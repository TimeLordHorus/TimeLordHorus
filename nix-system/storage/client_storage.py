"""
Decentralized Client-Side Storage System

Implements secure, encrypted storage on patient devices with firewall protection.
Original medical records remain on patient's device; copies are tracked and encrypted.
"""

import os
import json
import sqlite3
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone
import hashlib

# Import from sibling modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from security.encryption.aes_encryption import AESEncryption
from tracking.provenance import DocumentProvenance, DeviceType, DocumentAction


class ClientStorageSystem:
    """
    Decentralized storage system for patient devices

    Features:
    - Encrypted local database
    - Original record storage
    - Firewall integration hooks
    - Offline-first capability
    - Sync management
    """

    def __init__(self, storage_path: str, device_id: str, encryption_key: bytes):
        """
        Initialize client storage system

        Args:
            storage_path: Path to local storage directory
            device_id: Unique device identifier
            encryption_key: Encryption key for data at rest
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.device_id = device_id
        self.encryption = AESEncryption(encryption_key)

        # Initialize encrypted database
        self.db_path = self.storage_path / "medical_records.db"
        self._initialize_database()

        # Initialize provenance tracking
        self.provenance = DocumentProvenance()

    def _initialize_database(self):
        """Initialize SQLite database for local storage"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Medical records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_records (
                record_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                record_type TEXT NOT NULL,
                content_encrypted BLOB NOT NULL,
                content_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_original INTEGER NOT NULL DEFAULT 1,
                sync_status TEXT DEFAULT 'local',
                metadata_encrypted BLOB,
                provenance_id TEXT
            )
        ''')

        # Prescriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prescriptions (
                prescription_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                provider_id TEXT NOT NULL,
                medication_name TEXT NOT NULL,
                dosage_encrypted BLOB NOT NULL,
                instructions_encrypted BLOB NOT NULL,
                prescribed_date TEXT NOT NULL,
                expiry_date TEXT,
                refills_remaining INTEGER,
                pharmacy_id TEXT,
                content_hash TEXT NOT NULL,
                metadata_encrypted BLOB
            )
        ''')

        # Diagnoses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnoses (
                diagnosis_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                provider_id TEXT NOT NULL,
                icd_code TEXT NOT NULL,
                diagnosis_encrypted BLOB NOT NULL,
                diagnosis_date TEXT NOT NULL,
                severity TEXT,
                status TEXT,
                content_hash TEXT NOT NULL,
                metadata_encrypted BLOB
            )
        ''')

        # Chart notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chart_notes (
                note_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                provider_id TEXT NOT NULL,
                note_type TEXT NOT NULL,
                content_encrypted BLOB NOT NULL,
                note_date TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                metadata_encrypted BLOB
            )
        ''')

        # Birth certificates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS birth_certificates (
                certificate_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                content_encrypted BLOB NOT NULL,
                issue_date TEXT NOT NULL,
                issuing_authority TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                metadata_encrypted BLOB
            )
        ''')

        # Consent records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consent_records (
                consent_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                recipient_type TEXT NOT NULL,
                document_ids TEXT NOT NULL,
                granted_at TEXT NOT NULL,
                expires_at TEXT,
                status TEXT NOT NULL,
                metadata_encrypted BLOB
            )
        ''')

        # Sync queue for offline changes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_queue (
                queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_type TEXT NOT NULL,
                record_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                synced INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

    def store_medical_record(self,
                            record_id: str,
                            patient_id: str,
                            record_type: str,
                            content: Dict[str, Any],
                            metadata: Optional[Dict[str, Any]] = None,
                            is_original: bool = True) -> str:
        """
        Store medical record on client device

        Args:
            record_id: Unique record identifier
            patient_id: Patient ID
            record_type: Type of medical record
            content: Record content (will be encrypted)
            metadata: Additional metadata
            is_original: True if this is the original record

        Returns:
            Content hash of stored record
        """
        # Serialize and encrypt content
        content_json = json.dumps(content)
        content_encrypted = self.encryption.encrypt_string(content_json)

        # Calculate content hash
        content_hash = hashlib.sha256(content_json.encode()).hexdigest()

        # Encrypt metadata if provided
        metadata_encrypted = None
        if metadata:
            metadata_json = json.dumps(metadata)
            metadata_encrypted = self.encryption.encrypt_string(metadata_json)

        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        timestamp = datetime.now(timezone.utc).isoformat()

        # Register with provenance tracking if original
        provenance_id = None
        if is_original:
            provenance_record = self.provenance.register_document(
                document_id=record_id,
                document_type=record_type,
                patient_id=patient_id,
                created_by=patient_id,
                device_id=self.device_id,
                device_type=DeviceType.CLIENT_DEVICE,
                initial_hash=content_hash,
                metadata=metadata
            )
            provenance_id = provenance_record.record_id

        cursor.execute('''
            INSERT OR REPLACE INTO medical_records
            (record_id, patient_id, record_type, content_encrypted, content_hash,
             created_at, updated_at, is_original, sync_status, metadata_encrypted, provenance_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (record_id, patient_id, record_type, content_encrypted, content_hash,
              timestamp, timestamp, 1 if is_original else 0, 'local', metadata_encrypted, provenance_id))

        conn.commit()
        conn.close()

        # Add to sync queue
        self._add_to_sync_queue('medical_records', record_id, 'create')

        return content_hash

    def retrieve_medical_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve and decrypt medical record

        Args:
            record_id: Record ID to retrieve

        Returns:
            Decrypted record content or None if not found
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            SELECT content_encrypted, metadata_encrypted, patient_id, record_type
            FROM medical_records
            WHERE record_id = ?
        ''', (record_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        content_encrypted, metadata_encrypted, patient_id, record_type = row

        # Decrypt content
        content_json = self.encryption.decrypt_string(content_encrypted)
        content = json.loads(content_json)

        # Decrypt metadata if present
        metadata = None
        if metadata_encrypted:
            metadata_json = self.encryption.decrypt_string(metadata_encrypted)
            metadata = json.loads(metadata_json)

        # Track access in provenance
        self.provenance.track_document_access(
            document_id=record_id,
            actor_id=patient_id,
            device_id=self.device_id,
            ip_address="127.0.0.1",
            action=DocumentAction.ACCESSED
        )

        return {
            "record_id": record_id,
            "patient_id": patient_id,
            "record_type": record_type,
            "content": content,
            "metadata": metadata
        }

    def store_prescription(self,
                          prescription_id: str,
                          patient_id: str,
                          provider_id: str,
                          medication_name: str,
                          dosage: str,
                          instructions: str,
                          prescribed_date: str,
                          expiry_date: Optional[str] = None,
                          refills: int = 0) -> str:
        """Store prescription record"""
        # Encrypt sensitive information
        dosage_encrypted = self.encryption.encrypt_string(dosage)
        instructions_encrypted = self.encryption.encrypt_string(instructions)

        # Calculate content hash
        content = f"{medication_name}:{dosage}:{instructions}"
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO prescriptions
            (prescription_id, patient_id, provider_id, medication_name,
             dosage_encrypted, instructions_encrypted, prescribed_date,
             expiry_date, refills_remaining, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (prescription_id, patient_id, provider_id, medication_name,
              dosage_encrypted, instructions_encrypted, prescribed_date,
              expiry_date, refills, content_hash))

        conn.commit()
        conn.close()

        return content_hash

    def grant_access_consent(self,
                            consent_id: str,
                            patient_id: str,
                            recipient_id: str,
                            recipient_type: str,
                            document_ids: List[str],
                            expires_at: Optional[str] = None) -> None:
        """
        Grant consent for another party to access documents

        Args:
            consent_id: Unique consent identifier
            patient_id: Patient granting consent
            recipient_id: ID of recipient (provider, organization, etc.)
            recipient_type: Type of recipient (provider, dme_supplier, etc.)
            document_ids: List of document IDs to grant access to
            expires_at: Optional expiration timestamp
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        document_ids_json = json.dumps(document_ids)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO consent_records
            (consent_id, patient_id, recipient_id, recipient_type,
             document_ids, granted_at, expires_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (consent_id, patient_id, recipient_id, recipient_type,
              document_ids_json, timestamp, expires_at, 'active'))

        conn.commit()
        conn.close()

    def get_active_consents(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all active consent grants for patient"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            SELECT consent_id, recipient_id, recipient_type, document_ids,
                   granted_at, expires_at
            FROM consent_records
            WHERE patient_id = ? AND status = 'active'
        ''', (patient_id,))

        consents = []
        for row in cursor.fetchall():
            consent_id, recipient_id, recipient_type, document_ids_json, granted_at, expires_at = row
            consents.append({
                "consent_id": consent_id,
                "recipient_id": recipient_id,
                "recipient_type": recipient_type,
                "document_ids": json.loads(document_ids_json),
                "granted_at": granted_at,
                "expires_at": expires_at
            })

        conn.close()
        return consents

    def _add_to_sync_queue(self, record_type: str, record_id: str, action: str):
        """Add operation to sync queue for later synchronization"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        timestamp = datetime.now(timezone.utc).isoformat()

        cursor.execute('''
            INSERT INTO sync_queue (record_type, record_id, action, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (record_type, record_id, action, timestamp))

        conn.commit()
        conn.close()

    def get_sync_queue(self) -> List[Dict[str, Any]]:
        """Get pending sync operations"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            SELECT queue_id, record_type, record_id, action, timestamp
            FROM sync_queue
            WHERE synced = 0
            ORDER BY queue_id ASC
        ''')

        queue = []
        for row in cursor.fetchall():
            queue_id, record_type, record_id, action, timestamp = row
            queue.append({
                "queue_id": queue_id,
                "record_type": record_type,
                "record_id": record_id,
                "action": action,
                "timestamp": timestamp
            })

        conn.close()
        return queue

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        stats = {}

        # Count records by type
        for table in ['medical_records', 'prescriptions', 'diagnoses', 'chart_notes', 'birth_certificates']:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            stats[table] = cursor.fetchone()[0]

        # Count pending sync operations
        cursor.execute('SELECT COUNT(*) FROM sync_queue WHERE synced = 0')
        stats['pending_sync'] = cursor.fetchone()[0]

        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    # Initialize client storage
    encryption_key = AESEncryption.generate_key()
    storage = ClientStorageSystem(
        storage_path="/secure/patient/storage",
        device_id="patient_device_001",
        encryption_key=encryption_key
    )

    # Store medical record
    record_hash = storage.store_medical_record(
        record_id="mr_001",
        patient_id="patient_12345",
        record_type="medical_history",
        content={
            "diagnosis": "Type 2 Diabetes",
            "date": "2024-01-15",
            "provider": "Dr. Smith"
        },
        is_original=True
    )

    print(f"Stored medical record with hash: {record_hash}")

    # Retrieve record
    record = storage.retrieve_medical_record("mr_001")
    print(f"Retrieved: {record}")

    # Storage stats
    stats = storage.get_storage_stats()
    print(f"Storage stats: {stats}")
