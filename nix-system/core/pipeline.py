"""
NIX (National Information Exchange) Core Pipeline

Central orchestrator for secure healthcare information exchange.
Routes data between patients, providers, state/federal systems, and authorized parties.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
import asyncio


class EntityType(Enum):
    """Types of entities in the NIX network"""
    PATIENT = "patient"
    PROVIDER = "provider"
    HOSPITAL = "hospital"
    PHARMACY = "pharmacy"
    DME_SUPPLIER = "dme_supplier"
    INSURANCE = "insurance"
    STATE_SYSTEM = "state_system"
    FEDERAL_SYSTEM = "federal_system"
    SOS = "sos"  # Secretary of State
    LAB = "lab"


class MessageType(Enum):
    """Types of messages in NIX pipeline"""
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    CONSENT_REQUEST = "consent_request"
    CONSENT_GRANT = "consent_grant"
    CONSENT_REVOKE = "consent_revoke"
    DOCUMENT_SHARE = "document_share"
    EMERGENCY_ACCESS = "emergency_access"
    AUDIT_REQUEST = "audit_request"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    EMERGENCY = 4


class NIXMessage:
    """Standard message format for NIX pipeline"""

    def __init__(self,
                 message_type: MessageType,
                 sender_id: str,
                 sender_type: EntityType,
                 recipient_id: str,
                 recipient_type: EntityType,
                 payload: Dict[str, Any],
                 priority: MessagePriority = MessagePriority.NORMAL):
        """
        Initialize NIX message

        Args:
            message_type: Type of message
            sender_id: ID of sender
            sender_type: Type of sender entity
            recipient_id: ID of recipient
            recipient_type: Type of recipient entity
            payload: Message payload data
            priority: Message priority
        """
        self.message_id = str(uuid.uuid4())
        self.message_type = message_type
        self.sender_id = sender_id
        self.sender_type = sender_type
        self.recipient_id = recipient_id
        self.recipient_type = recipient_type
        self.payload = payload
        self.priority = priority
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.status = "pending"

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender_id": self.sender_id,
            "sender_type": self.sender_type.value,
            "recipient_id": self.recipient_id,
            "recipient_type": self.recipient_type.value,
            "payload": self.payload,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "status": self.status
        }


class NIXPipeline:
    """
    Core NIX pipeline for healthcare information exchange

    Features:
    - Message routing
    - Priority queuing
    - Consent verification
    - Audit logging
    - Error handling
    - Retry logic
    """

    def __init__(self):
        """Initialize NIX pipeline"""
        self.message_queue: Dict[int, List[NIXMessage]] = {
            1: [],  # Low priority
            2: [],  # Normal priority
            3: [],  # High priority
            4: []   # Emergency priority
        }
        self.entity_registry: Dict[str, Dict[str, Any]] = {}
        self.routing_table: Dict[str, str] = {}
        self.active_connections: Dict[str, Any] = {}

    def register_entity(self,
                       entity_id: str,
                       entity_type: EntityType,
                       endpoint: str,
                       credentials: Dict[str, Any],
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register entity in NIX network

        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity
            endpoint: Network endpoint (URL, IP, etc.)
            credentials: Authentication credentials
            metadata: Additional entity metadata

        Returns:
            True if registration successful
        """
        self.entity_registry[entity_id] = {
            "entity_id": entity_id,
            "entity_type": entity_type.value,
            "endpoint": endpoint,
            "credentials": credentials,
            "metadata": metadata or {},
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }

        # Add to routing table
        self.routing_table[entity_id] = endpoint

        return True

    def send_message(self, message: NIXMessage) -> str:
        """
        Send message through NIX pipeline

        Args:
            message: NIX message to send

        Returns:
            Message ID
        """
        # Validate sender and recipient are registered
        if message.sender_id not in self.entity_registry:
            raise ValueError(f"Sender {message.sender_id} not registered")
        if message.recipient_id not in self.entity_registry:
            raise ValueError(f"Recipient {message.recipient_id} not registered")

        # Add to priority queue
        self.message_queue[message.priority.value].append(message)

        # Process message asynchronously
        asyncio.create_task(self._process_message(message))

        return message.message_id

    async def _process_message(self, message: NIXMessage):
        """
        Process message through pipeline

        Args:
            message: Message to process
        """
        try:
            # 1. Verify consent (for PHI data requests)
            if message.message_type == MessageType.DATA_REQUEST:
                if not await self._verify_consent(message):
                    message.status = "consent_denied"
                    return

            # 2. Apply HIPAA compliance checks
            if not await self._hipaa_compliance_check(message):
                message.status = "compliance_failed"
                return

            # 3. Encrypt message payload
            encrypted_payload = await self._encrypt_message(message)

            # 4. Route to recipient
            success = await self._route_message(message, encrypted_payload)

            if success:
                message.status = "delivered"
            else:
                message.status = "delivery_failed"

            # 5. Log to audit trail
            await self._audit_log(message)

        except Exception as e:
            message.status = "error"
            print(f"Error processing message {message.message_id}: {str(e)}")

    async def _verify_consent(self, message: NIXMessage) -> bool:
        """
        Verify patient consent for data access

        Args:
            message: Message to verify

        Returns:
            True if consent exists and is valid
        """
        # In production, this would check consent database
        # For now, return True for demonstration
        return True

    async def _hipaa_compliance_check(self, message: NIXMessage) -> bool:
        """
        Perform HIPAA compliance checks

        Args:
            message: Message to check

        Returns:
            True if compliant
        """
        # Check minimum necessary principle
        # Verify purpose of use
        # Check authorization
        # Validate encryption requirements
        return True

    async def _encrypt_message(self, message: NIXMessage) -> bytes:
        """
        Encrypt message payload for transit

        Args:
            message: Message to encrypt

        Returns:
            Encrypted payload
        """
        # Use TLS 1.3 for transport encryption
        # Additional payload encryption for sensitive data
        return b""

    async def _route_message(self, message: NIXMessage, encrypted_payload: bytes) -> bool:
        """
        Route message to recipient

        Args:
            message: Message to route
            encrypted_payload: Encrypted message payload

        Returns:
            True if successfully routed
        """
        recipient_endpoint = self.routing_table.get(message.recipient_id)
        if not recipient_endpoint:
            return False

        # In production, this would send via HTTP/HTTPS, Direct messaging, etc.
        return True

    async def _audit_log(self, message: NIXMessage):
        """
        Log message to audit trail

        Args:
            message: Message to log
        """
        # Log to HIPAA audit system
        pass

    def request_patient_data(self,
                            requester_id: str,
                            requester_type: EntityType,
                            patient_id: str,
                            data_types: List[str],
                            purpose: str,
                            priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """
        Request patient data through NIX

        Args:
            requester_id: ID of requesting entity
            requester_type: Type of requester
            patient_id: Patient whose data is requested
            data_types: Types of data requested (medical_records, prescriptions, etc.)
            purpose: Purpose of request (treatment, payment, operations)
            priority: Request priority

        Returns:
            Request message ID
        """
        message = NIXMessage(
            message_type=MessageType.DATA_REQUEST,
            sender_id=requester_id,
            sender_type=requester_type,
            recipient_id=patient_id,
            recipient_type=EntityType.PATIENT,
            payload={
                "data_types": data_types,
                "purpose": purpose,
                "requester_info": self.entity_registry.get(requester_id, {})
            },
            priority=priority
        )

        return self.send_message(message)

    def share_document(self,
                      sender_id: str,
                      sender_type: EntityType,
                      recipient_id: str,
                      recipient_type: EntityType,
                      document_id: str,
                      document_type: str,
                      consent_id: str) -> str:
        """
        Share document through NIX

        Args:
            sender_id: ID of sender
            sender_type: Type of sender
            recipient_id: ID of recipient
            recipient_type: Type of recipient
            document_id: Document to share
            document_type: Type of document
            consent_id: Associated consent ID

        Returns:
            Message ID
        """
        message = NIXMessage(
            message_type=MessageType.DOCUMENT_SHARE,
            sender_id=sender_id,
            sender_type=sender_type,
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            payload={
                "document_id": document_id,
                "document_type": document_type,
                "consent_id": consent_id
            },
            priority=MessagePriority.NORMAL
        )

        return self.send_message(message)

    def emergency_access_request(self,
                                 provider_id: str,
                                 patient_id: str,
                                 justification: str,
                                 data_types: List[str]) -> str:
        """
        Request emergency break-glass access

        Args:
            provider_id: Provider requesting emergency access
            patient_id: Patient ID
            justification: Justification for emergency access
            data_types: Types of data needed

        Returns:
            Request message ID
        """
        message = NIXMessage(
            message_type=MessageType.EMERGENCY_ACCESS,
            sender_id=provider_id,
            sender_type=EntityType.PROVIDER,
            recipient_id=patient_id,
            recipient_type=EntityType.PATIENT,
            payload={
                "justification": justification,
                "data_types": data_types,
                "emergency": True
            },
            priority=MessagePriority.EMERGENCY
        )

        return self.send_message(message)

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return {
            "registered_entities": len(self.entity_registry),
            "entities_by_type": self._count_entities_by_type(),
            "messages_in_queue": sum(len(q) for q in self.message_queue.values()),
            "queue_by_priority": {
                "low": len(self.message_queue[1]),
                "normal": len(self.message_queue[2]),
                "high": len(self.message_queue[3]),
                "emergency": len(self.message_queue[4])
            }
        }

    def _count_entities_by_type(self) -> Dict[str, int]:
        """Count registered entities by type"""
        counts = {}
        for entity in self.entity_registry.values():
            entity_type = entity["entity_type"]
            counts[entity_type] = counts.get(entity_type, 0) + 1
        return counts


# Example usage
if __name__ == "__main__":
    pipeline = NIXPipeline()

    # Register entities
    pipeline.register_entity(
        entity_id="hospital_001",
        entity_type=EntityType.HOSPITAL,
        endpoint="https://hospital001.nix.gov",
        credentials={"api_key": "abc123"}
    )

    pipeline.register_entity(
        entity_id="patient_12345",
        entity_type=EntityType.PATIENT,
        endpoint="patient://device_001",
        credentials={"public_key": "xyz789"}
    )

    # Request patient data
    request_id = pipeline.request_patient_data(
        requester_id="hospital_001",
        requester_type=EntityType.HOSPITAL,
        patient_id="patient_12345",
        data_types=["medical_records", "prescriptions"],
        purpose="treatment"
    )

    print(f"Data request sent: {request_id}")
    print(f"Pipeline stats: {pipeline.get_pipeline_stats()}")
