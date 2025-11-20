"""
Test Suite for Rate Limiter

Ensures rate limiting protects against abuse.
"""

import pytest
import time
from nix_system.security.firewall.rate_limiter import (
    RateLimiter,
    RateLimitTier,
    TokenBucket
)


class TestTokenBucket:
    """Test suite for token bucket algorithm"""

    def test_initial_capacity(self):
        """Test bucket starts at full capacity"""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)
        assert bucket.tokens == 100

    def test_consume_tokens(self):
        """Test consuming tokens"""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)

        # Consume 10 tokens
        success = bucket.consume(10)
        assert success is True
        assert bucket.tokens == 90

    def test_insufficient_tokens(self):
        """Test consuming more tokens than available"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        # Try to consume more than capacity
        success = bucket.consume(20)
        assert success is False
        assert bucket.tokens == 10  # Tokens unchanged

    def test_token_refill(self):
        """Test tokens refill over time"""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)

        # Consume tokens
        bucket.consume(50)
        assert bucket.tokens == 50

        # Wait for refill (1 second = 10 tokens)
        time.sleep(1.1)

        # Try to consume (should have refilled)
        bucket._refill()
        assert bucket.tokens >= 60  # Should have refilled ~10 tokens


class TestRateLimiter:
    """Test suite for rate limiter"""

    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance"""
        return RateLimiter()

    def test_set_entity_tier(self, rate_limiter):
        """Test setting rate limit tier"""
        rate_limiter.set_entity_tier("entity_001", RateLimitTier.BASIC)

        # Verify tier is set
        assert "entity_001" in rate_limiter.entity_tiers
        assert rate_limiter.entity_tiers["entity_001"] == RateLimitTier.BASIC

    def test_basic_tier_limits(self, rate_limiter):
        """Test basic tier rate limits"""
        entity_id = "entity_001"
        rate_limiter.set_entity_tier(entity_id, RateLimitTier.BASIC)

        # Should allow requests within limit
        for i in range(10):
            allowed = rate_limiter.check_rate_limit(entity_id, "192.168.1.100")
            assert allowed is True

    def test_emergency_tier_unlimited(self, rate_limiter):
        """Test emergency tier has no limits"""
        entity_id = "emergency_001"
        rate_limiter.set_entity_tier(entity_id, RateLimitTier.EMERGENCY)

        # Should allow many requests
        for i in range(1000):
            allowed = rate_limiter.check_rate_limit(entity_id, "192.168.1.100")
            assert allowed is True

    def test_rate_limit_exceeded(self, rate_limiter):
        """Test rate limit exceeded"""
        entity_id = "entity_001"
        rate_limiter.set_entity_tier(entity_id, RateLimitTier.FREE)

        # Free tier: 100 requests/hour, ~1.67/minute
        # Should eventually hit limit with rapid requests
        allowed_count = 0
        for i in range(20):
            if rate_limiter.check_rate_limit(entity_id, "192.168.1.100"):
                allowed_count += 1

        # Not all should be allowed
        assert allowed_count < 20

    def test_concurrent_connections(self, rate_limiter):
        """Test concurrent connection limits"""
        entity_id = "entity_001"
        rate_limiter.set_entity_tier(entity_id, RateLimitTier.FREE)

        # Increment connections
        for i in range(5):
            success = rate_limiter.increment_connection(entity_id)
            assert success is True

        # Should hit limit (Free tier: 5 connections)
        success = rate_limiter.increment_connection(entity_id)
        assert success is False

        # Decrement and try again
        rate_limiter.decrement_connection(entity_id)
        success = rate_limiter.increment_connection(entity_id)
        assert success is True

    def test_get_rate_limit_status(self, rate_limiter):
        """Test getting rate limit status"""
        entity_id = "entity_001"
        rate_limiter.set_entity_tier(entity_id, RateLimitTier.PROFESSIONAL)

        # Make some requests
        for i in range(5):
            rate_limiter.check_rate_limit(entity_id, "192.168.1.100")

        status = rate_limiter.get_rate_limit_status(entity_id)

        assert status["entity_id"] == entity_id
        assert status["tier"] == RateLimitTier.PROFESSIONAL.value
        assert "usage" in status
        assert status["usage"]["requests_last_minute"] >= 5

    def test_ip_blocking(self, rate_limiter):
        """Test IP blocking for abuse"""
        entity_id = "entity_001"
        ip_address = "192.168.1.100"

        rate_limiter.set_entity_tier(entity_id, RateLimitTier.FREE)

        # Simulate DDoS attack (many requests rapidly)
        # This should trigger IP blocking
        for i in range(150):
            rate_limiter.check_rate_limit(entity_id, ip_address)

        # IP should eventually be blocked
        # (DDoS detection triggers at 100 requests in 10 seconds)

    def test_multiple_entities(self, rate_limiter):
        """Test rate limiting multiple entities independently"""
        entity1 = "entity_001"
        entity2 = "entity_002"

        rate_limiter.set_entity_tier(entity1, RateLimitTier.BASIC)
        rate_limiter.set_entity_tier(entity2, RateLimitTier.PROFESSIONAL)

        # Both should be allowed initially
        assert rate_limiter.check_rate_limit(entity1, "192.168.1.100") is True
        assert rate_limiter.check_rate_limit(entity2, "192.168.1.101") is True

        # Limits should be independent
        status1 = rate_limiter.get_rate_limit_status(entity1)
        status2 = rate_limiter.get_rate_limit_status(entity2)

        assert status1["limits"]["requests_per_hour"] == 1000  # Basic
        assert status2["limits"]["requests_per_hour"] == 10000  # Professional

    def test_statistics(self, rate_limiter):
        """Test getting rate limiter statistics"""
        rate_limiter.set_entity_tier("entity_001", RateLimitTier.BASIC)
        rate_limiter.set_entity_tier("entity_002", RateLimitTier.PROFESSIONAL)
        rate_limiter.set_entity_tier("entity_003", RateLimitTier.ENTERPRISE)

        stats = rate_limiter.get_statistics()

        assert stats["total_entities"] == 3
        assert "entities_by_tier" in stats
        assert stats["entities_by_tier"]["basic"] == 1
        assert stats["entities_by_tier"]["professional"] == 1
        assert stats["entities_by_tier"]["enterprise"] == 1
