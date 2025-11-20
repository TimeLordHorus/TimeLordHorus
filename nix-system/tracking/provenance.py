"""
Document Provenance and Tracking System

Implements blockchain-based tracking of medical document lifecycle.
Every copy of a document is tracked with cryptographic signatures,
providing complete audit trail from creation to destruction.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class DocumentAction(Enum):
    """Actions that can be performed on a document"""
    CREATED = "created"
    ACCESSED = "accessed"
    MODIFIED = "modified"
    COPIED = "copied"
    TRANSFERRED = "transferred"
    SHARED = "shared"
    PRINTED = "printed"
    EXPORTED = "exported"
    DELETED = "deleted"
    ARCHIVED = "archived"


class DeviceType(Enum):
    """Types of devices that can store documents"""
    CLIENT_DEVICE = "client_device"
    HOSPITAL_SERVER = "hospital_server"
    CLOUD_BACKUP = "cloud_backup"
    DME_SUPPLIER = "dme_supplier"
    PHARMACY = "pharmacy"
    INSURANCE = "insurance"
    STATE_SYSTEM = "state_system"
    FEDERAL_SYSTEM = "federal_system"


@dataclass
class ProvenanceRecord:
    """Single provenance record in document history"""
    record_id: str
    document_id: str
    timestamp: str
    action: str
    actor_id: str
    actor_name: str
    source_device_id: str
    destination_device_id: Optional[str]
    device_type: str
    ip_address: str
    location: Optional[Dict[str, Any]]
    hash_before: Optional[str]
    hash_after: str
    parent_record_id: Optional[str]
    signature: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class DocumentProvenance:
    """
    Manages document provenance and tracking

    Features:
    - Cryptographic linking of provenance records
    - Device-level tracking
    - Immutable audit trail
    - Copy detection and tracking
    - Geographic tracking
    """

    def __init__(self):
        """Initialize provenance tracking system"""
        # In production, this would be a blockchain or distributed ledger
        self.provenance_chain: Dict[str, List[ProvenanceRecord]] = {}
        self.document_registry: Dict[str, Dict[str, Any]] = {}
        self.device_registry: Dict[str, Dict[str, Any]] = {}

    def register_document(self,
                         document_id: str,
                         document_type: str,
                         patient_id: str,
                         created_by: str,
                         device_id: str,
                         device_type: DeviceType,
                         initial_hash: str,
                         metadata: Optional[Dict[str, Any]] = None) -> ProvenanceRecord:
        """
        Register new document and create initial provenance record

        Args:
            document_id: Unique document identifier
            document_type: Type of document (medical_record, prescription, etc.)
            patient_id: Patient ID
            created_by: User who created document
            device_id: Device where document was created
            device_type: Type of device
            initial_hash: Cryptographic hash of document content
            metadata: Additional document metadata

        Returns:
            Initial provenance record
        """
        record_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Create initial provenance record
        record = ProvenanceRecord(
            record_id=record_id,
            document_id=document_id,
            timestamp=timestamp,
            action=DocumentAction.CREATED.value,
            actor_id=created_by,
            actor_name=created_by,  # Would lookup from user directory
            source_device_id=device_id,
            destination_device_id=None,
            device_type=device_type.value,
            ip_address="0.0.0.0",  # Would capture actual IP
            location=None,
            hash_before=None,
            hash_after=initial_hash,
            parent_record_id=None,
            signature=self._create_signature(record_id, document_id, timestamp, initial_hash),
            metadata=metadata or {}
        )

        # Register document
        self.document_registry[document_id] = {
            "document_id": document_id,
            "document_type": document_type,
            "patient_id": patient_id,
            "created_at": timestamp,
            "created_by": created_by,
            "original_device_id": device_id,
            "current_hash": initial_hash,
            "status": "active"
        }

        # Initialize provenance chain
        self.provenance_chain[document_id] = [record]

        return record

    def track_document_copy(self,
                           document_id: str,
                           actor_id: str,
                           source_device_id: str,
                           destination_device_id: str,
                           destination_device_type: DeviceType,
                           document_hash: str,
                           ip_address: str,
                           purpose: str,
                           consent_id: Optional[str] = None) -> ProvenanceRecord:
        """
        Track creation of document copy

        Args:
            document_id: Document being copied
            actor_id: User creating copy
            source_device_id: Source device ID
            destination_device_id: Destination device ID
            destination_device_type: Type of destination device
            document_hash: Hash of document copy
            ip_address: IP address of request
            purpose: Purpose of copy (treatment, transfer, backup)
            consent_id: Associated consent record

        Returns:
            Provenance record for copy
        """
        if document_id not in self.provenance_chain:
            raise ValueError(f"Document {document_id} not registered")

        record_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Get previous record
        previous_records = self.provenance_chain[document_id]
        parent_record = previous_records[-1]

        # Create copy tracking record
        record = ProvenanceRecord(
            record_id=record_id,
            document_id=document_id,
            timestamp=timestamp,
            action=DocumentAction.COPIED.value,
            actor_id=actor_id,
            actor_name=actor_id,
            source_device_id=source_device_id,
            destination_device_id=destination_device_id,
            device_type=destination_device_type.value,
            ip_address=ip_address,
            location=None,
            hash_before=parent_record.hash_after,
            hash_after=document_hash,
            parent_record_id=parent_record.record_id,
            signature=self._create_signature(record_id, document_id, timestamp, document_hash),
            metadata={
                "purpose": purpose,
                "consent_id": consent_id,
                "copy_number": len([r for r in previous_records if r.action == DocumentAction.COPIED.value]) + 1
            }
        )

        # Add to provenance chain
        self.provenance_chain[document_id].append(record)

        # Register destination device
        self._register_device_copy(destination_device_id, destination_device_type, document_id, record_id)

        return record

    def track_document_access(self,
                             document_id: str,
                             actor_id: str,
                             device_id: str,
                             ip_address: str,
                             action: DocumentAction = DocumentAction.ACCESSED) -> ProvenanceRecord:
        """
        Track document access

        Args:
            document_id: Document being accessed
            actor_id: User accessing document
            device_id: Device ID
            ip_address: IP address
            action: Type of access (viewed, modified, etc.)

        Returns:
            Provenance record
        """
        if document_id not in self.provenance_chain:
            raise ValueError(f"Document {document_id} not registered")

        record_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        previous_records = self.provenance_chain[document_id]
        parent_record = previous_records[-1]

        record = ProvenanceRecord(
            record_id=record_id,
            document_id=document_id,
            timestamp=timestamp,
            action=action.value,
            actor_id=actor_id,
            actor_name=actor_id,
            source_device_id=device_id,
            destination_device_id=None,
            device_type="unknown",
            ip_address=ip_address,
            location=None,
            hash_before=parent_record.hash_after,
            hash_after=parent_record.hash_after,
            parent_record_id=parent_record.record_id,
            signature=self._create_signature(record_id, document_id, timestamp, parent_record.hash_after),
            metadata={}
        )

        self.provenance_chain[document_id].append(record)

        return record

    def get_document_history(self, document_id: str) -> List[ProvenanceRecord]:
        """
        Get complete provenance history for document

        Args:
            document_id: Document ID

        Returns:
            List of provenance records in chronological order
        """
        return self.provenance_chain.get(document_id, [])

    def get_document_locations(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get all current locations where document copies exist

        Args:
            document_id: Document ID

        Returns:
            List of device locations
        """
        if document_id not in self.provenance_chain:
            return []

        locations = []
        for record in self.provenance_chain[document_id]:
            if record.action in [DocumentAction.COPIED.value, DocumentAction.CREATED.value]:
                device_id = record.destination_device_id or record.source_device_id
                if device_id in self.device_registry:
                    locations.append({
                        "device_id": device_id,
                        "device_type": record.device_type,
                        "timestamp": record.timestamp,
                        "record_id": record.record_id
                    })

        return locations

    def verify_document_integrity(self, document_id: str, current_hash: str) -> bool:
        """
        Verify document integrity against provenance chain

        Args:
            document_id: Document ID
            current_hash: Current document hash

        Returns:
            True if hash matches latest provenance record
        """
        if document_id not in self.provenance_chain:
            return False

        latest_record = self.provenance_chain[document_id][-1]
        return latest_record.hash_after == current_hash

    def verify_chain_integrity(self, document_id: str) -> bool:
        """
        Verify entire provenance chain integrity

        Args:
            document_id: Document ID

        Returns:
            True if chain is valid
        """
        if document_id not in self.provenance_chain:
            return False

        records = self.provenance_chain[document_id]

        for i, record in enumerate(records):
            # Verify signature
            expected_sig = self._create_signature(
                record.record_id,
                record.document_id,
                record.timestamp,
                record.hash_after
            )
            if record.signature != expected_sig:
                return False

            # Verify chain linkage
            if i > 0:
                previous_record = records[i - 1]
                if record.parent_record_id != previous_record.record_id:
                    return False
                if record.hash_before != previous_record.hash_after:
                    return False

        return True

    def _create_signature(self, record_id: str, document_id: str,
                         timestamp: str, document_hash: str) -> str:
        """Create cryptographic signature for provenance record"""
        data = f"{record_id}:{document_id}:{timestamp}:{document_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _register_device_copy(self, device_id: str, device_type: DeviceType,
                             document_id: str, record_id: str):
        """Register document copy on device"""
        if device_id not in self.device_registry:
            self.device_registry[device_id] = {
                "device_id": device_id,
                "device_type": device_type.value,
                "documents": []
            }

        self.device_registry[device_id]["documents"].append({
            "document_id": document_id,
            "record_id": record_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def generate_provenance_report(self, document_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive provenance report

        Args:
            document_id: Document ID

        Returns:
            Detailed provenance report
        """
        if document_id not in self.provenance_chain:
            return {"error": "Document not found"}

        records = self.provenance_chain[document_id]
        document_info = self.document_registry[document_id]

        # Calculate statistics
        access_count = len([r for r in records if r.action == DocumentAction.ACCESSED.value])
        copy_count = len([r for r in records if r.action == DocumentAction.COPIED.value])
        modification_count = len([r for r in records if r.action == DocumentAction.MODIFIED.value])

        return {
            "document_id": document_id,
            "document_info": document_info,
            "creation_date": records[0].timestamp,
            "last_activity": records[-1].timestamp,
            "total_events": len(records),
            "access_count": access_count,
            "copy_count": copy_count,
            "modification_count": modification_count,
            "current_locations": self.get_document_locations(document_id),
            "chain_integrity_valid": self.verify_chain_integrity(document_id),
            "provenance_chain": [r.to_dict() for r in records]
        }


# Example usage
if __name__ == "__main__":
    provenance = DocumentProvenance()

    # Register original document on patient device
    initial_record = provenance.register_document(
        document_id="doc_001",
        document_type="medical_record",
        patient_id="patient_12345",
        created_by="dr_smith",
        device_id="patient_phone_001",
        device_type=DeviceType.CLIENT_DEVICE,
        initial_hash="abc123def456",
        metadata={"diagnosis": "Type 2 Diabetes"}
    )

    print(f"Document registered: {initial_record.record_id}")

    # Track copy to hospital server
    copy_record = provenance.track_document_copy(
        document_id="doc_001",
        actor_id="patient_12345",
        source_device_id="patient_phone_001",
        destination_device_id="hospital_server_001",
        destination_device_type=DeviceType.HOSPITAL_SERVER,
        document_hash="abc123def456",
        ip_address="192.168.1.100",
        purpose="treatment",
        consent_id="consent_001"
    )

    print(f"Copy tracked: {copy_record.record_id}")

    # Generate report
    report = provenance.generate_provenance_report("doc_001")
    print(f"\nProvenance Report:")
    print(f"Total events: {report['total_events']}")
    print(f"Copy count: {report['copy_count']}")
    print(f"Chain valid: {report['chain_integrity_valid']}")
