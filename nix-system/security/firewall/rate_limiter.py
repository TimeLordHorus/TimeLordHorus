"""
Rate Limiting and DDoS Protection

Implements rate limiting to protect against abuse and DDoS attacks.
"""

import time
from typing import Dict, Optional, List
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum


class RateLimitTier(Enum):
    """Rate limit tiers for different entity types"""
    FREE = "free"  # 100 req/hour
    BASIC = "basic"  # 1,000 req/hour
    PROFESSIONAL = "professional"  # 10,000 req/hour
    ENTERPRISE = "enterprise"  # 100,000 req/hour
    EMERGENCY = "emergency"  # Unlimited


class RateLimitConfig:
    """Rate limit configuration by tier"""
    LIMITS = {
        RateLimitTier.FREE: {
            "requests_per_hour": 100,
            "requests_per_minute": 10,
            "concurrent_connections": 5
        },
        RateLimitTier.BASIC: {
            "requests_per_hour": 1000,
            "requests_per_minute": 100,
            "concurrent_connections": 20
        },
        RateLimitTier.PROFESSIONAL: {
            "requests_per_hour": 10000,
            "requests_per_minute": 500,
            "concurrent_connections": 100
        },
        RateLimitTier.ENTERPRISE: {
            "requests_per_hour": 100000,
            "requests_per_minute": 2000,
            "concurrent_connections": 500
        },
        RateLimitTier.EMERGENCY: {
            "requests_per_hour": float('inf'),
            "requests_per_minute": float('inf'),
            "concurrent_connections": float('inf')
        }
    }


class TokenBucket:
    """
    Token bucket algorithm for rate limiting

    Allows bursts while maintaining average rate
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket

        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens consumed, False if insufficient
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        """Refill bucket based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        refill_amount = elapsed * self.refill_rate

        self.tokens = min(self.capacity, self.tokens + refill_amount)
        self.last_refill = now

    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get wait time until tokens available

        Args:
            tokens: Number of tokens needed

        Returns:
            Wait time in seconds
        """
        self._refill()

        if self.tokens >= tokens:
            return 0.0

        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


class RateLimiter:
    """
    Comprehensive rate limiting system

    Features:
    - Per-entity rate limiting
    - Multiple time windows (minute, hour)
    - Token bucket algorithm
    - IP-based limiting
    - DDoS detection
    """

    def __init__(self):
        """Initialize rate limiter"""
        self.entity_tiers: Dict[str, RateLimitTier] = {}
        self.entity_buckets: Dict[str, TokenBucket] = {}
        self.request_history: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Dict[str, float] = {}  # IP -> unblock_time
        self.connection_counts: Dict[str, int] = defaultdict(int)

    def set_entity_tier(self, entity_id: str, tier: RateLimitTier):
        """
        Set rate limit tier for entity

        Args:
            entity_id: Entity ID
            tier: Rate limit tier
        """
        self.entity_tiers[entity_id] = tier

        # Create token bucket
        limits = RateLimitConfig.LIMITS[tier]
        capacity = limits["requests_per_minute"]
        refill_rate = capacity / 60.0  # tokens per second

        self.entity_buckets[entity_id] = TokenBucket(capacity, refill_rate)

    def check_rate_limit(self, entity_id: str, ip_address: str) -> bool:
        """
        Check if request is within rate limits

        Args:
            entity_id: Entity making request
            ip_address: IP address

        Returns:
            True if within limits, False if exceeded
        """
        # Check if IP is blocked
        if self._is_ip_blocked(ip_address):
            return False

        # Get entity tier
        tier = self.entity_tiers.get(entity_id, RateLimitTier.FREE)

        # Emergency tier has no limits
        if tier == RateLimitTier.EMERGENCY:
            return True

        # Check token bucket
        bucket = self.entity_buckets.get(entity_id)
        if not bucket:
            self.set_entity_tier(entity_id, tier)
            bucket = self.entity_buckets[entity_id]

        if not bucket.consume():
            return False

        # Check hourly limit
        if not self._check_hourly_limit(entity_id, tier):
            return False

        # Check for DDoS patterns
        if self._detect_ddos(entity_id, ip_address):
            self._block_ip(ip_address, duration_minutes=60)
            return False

        # Record request
        self._record_request(entity_id)

        return True

    def increment_connection(self, entity_id: str) -> bool:
        """
        Increment concurrent connection count

        Args:
            entity_id: Entity ID

        Returns:
            True if within limit, False if exceeded
        """
        tier = self.entity_tiers.get(entity_id, RateLimitTier.FREE)
        max_connections = RateLimitConfig.LIMITS[tier]["concurrent_connections"]

        if self.connection_counts[entity_id] >= max_connections:
            return False

        self.connection_counts[entity_id] += 1
        return True

    def decrement_connection(self, entity_id: str):
        """Decrement concurrent connection count"""
        if self.connection_counts[entity_id] > 0:
            self.connection_counts[entity_id] -= 1

    def get_rate_limit_status(self, entity_id: str) -> Dict[str, any]:
        """
        Get rate limit status for entity

        Args:
            entity_id: Entity ID

        Returns:
            Rate limit status information
        """
        tier = self.entity_tiers.get(entity_id, RateLimitTier.FREE)
        limits = RateLimitConfig.LIMITS[tier]
        bucket = self.entity_buckets.get(entity_id)

        # Count recent requests
        now = time.time()
        history = self.request_history[entity_id]
        requests_last_hour = len([t for t in history if now - t < 3600])
        requests_last_minute = len([t for t in history if now - t < 60])

        return {
            "entity_id": entity_id,
            "tier": tier.value,
            "limits": limits,
            "usage": {
                "requests_last_hour": requests_last_hour,
                "requests_last_minute": requests_last_minute,
                "concurrent_connections": self.connection_counts[entity_id],
                "tokens_available": bucket.tokens if bucket else 0
            },
            "retry_after": bucket.get_wait_time() if bucket else 0
        }

    def _check_hourly_limit(self, entity_id: str, tier: RateLimitTier) -> bool:
        """Check hourly request limit"""
        hourly_limit = RateLimitConfig.LIMITS[tier]["requests_per_hour"]

        now = time.time()
        history = self.request_history[entity_id]

        # Remove requests older than 1 hour
        history = [t for t in history if now - t < 3600]
        self.request_history[entity_id] = history

        return len(history) < hourly_limit

    def _detect_ddos(self, entity_id: str, ip_address: str) -> bool:
        """
        Detect potential DDoS attack

        Args:
            entity_id: Entity ID
            ip_address: IP address

        Returns:
            True if DDoS pattern detected
        """
        now = time.time()
        history = self.request_history[entity_id]

        # Check for suspicious patterns
        # 1. Too many requests in short time
        recent_requests = [t for t in history if now - t < 10]
        if len(recent_requests) > 100:  # 100 requests in 10 seconds
            return True

        # 2. Consistent high-frequency requests
        requests_last_minute = [t for t in history if now - t < 60]
        if len(requests_last_minute) > 500:
            return True

        return False

    def _block_ip(self, ip_address: str, duration_minutes: int = 60):
        """
        Block IP address

        Args:
            ip_address: IP to block
            duration_minutes: Block duration in minutes
        """
        unblock_time = time.time() + (duration_minutes * 60)
        self.blocked_ips[ip_address] = unblock_time

    def _is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        if ip_address not in self.blocked_ips:
            return False

        unblock_time = self.blocked_ips[ip_address]
        if time.time() >= unblock_time:
            # Unblock IP
            del self.blocked_ips[ip_address]
            return False

        return True

    def _record_request(self, entity_id: str):
        """Record request timestamp"""
        self.request_history[entity_id].append(time.time())

        # Keep only last hour of history
        now = time.time()
        self.request_history[entity_id] = [
            t for t in self.request_history[entity_id]
            if now - t < 3600
        ]

    def get_statistics(self) -> Dict[str, any]:
        """Get rate limiter statistics"""
        return {
            "total_entities": len(self.entity_tiers),
            "entities_by_tier": self._count_by_tier(),
            "blocked_ips": len(self.blocked_ips),
            "active_connections": sum(self.connection_counts.values())
        }

    def _count_by_tier(self) -> Dict[str, int]:
        """Count entities by tier"""
        counts = defaultdict(int)
        for tier in self.entity_tiers.values():
            counts[tier.value] += 1
        return dict(counts)


# Example usage
if __name__ == "__main__":
    limiter = RateLimiter()

    # Set entity tiers
    limiter.set_entity_tier("hospital_001", RateLimitTier.ENTERPRISE)
    limiter.set_entity_tier("patient_12345", RateLimitTier.BASIC)

    # Check rate limit
    allowed = limiter.check_rate_limit("hospital_001", "192.168.1.100")
    print(f"Request allowed: {allowed}")

    # Get status
    status = limiter.get_rate_limit_status("hospital_001")
    print(f"Rate limit status: {status}")

    # Get statistics
    stats = limiter.get_statistics()
    print(f"Statistics: {stats}")
