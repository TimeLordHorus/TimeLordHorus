"""
Consent Management Engine

Implements granular consent management for patient data sharing.
Compliant with HIPAA Privacy Rule § 164.508 (Authorizations).
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field


class ConsentType(Enum):
    """Types of consent"""
    TREATMENT = "treatment"
    PAYMENT = "payment"
    OPERATIONS = "operations"
    RESEARCH = "research"
    MARKETING = "marketing"
    DISCLOSURE = "disclosure"
    EMERGENCY = "emergency"


class ConsentStatus(Enum):
    """Consent status"""
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    DENIED = "denied"


class DataCategory(Enum):
    """Categories of health data"""
    MEDICAL_RECORDS = "medical_records"
    PRESCRIPTIONS = "prescriptions"
    DIAGNOSES = "diagnoses"
    LAB_RESULTS = "lab_results"
    IMAGING = "imaging"
    CHART_NOTES = "chart_notes"
    BIRTH_CERTIFICATE = "birth_certificate"
    IMMUNIZATIONS = "immunizations"
    MENTAL_HEALTH = "mental_health"
    SUBSTANCE_ABUSE = "substance_abuse"
    GENETIC_INFO = "genetic_info"
    HIV_STATUS = "hiv_status"


@dataclass
class ConsentScope:
    """Defines scope of consent"""
    data_categories: List[DataCategory]
    specific_documents: List[str] = field(default_factory=list)
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    exclude_categories: List[DataCategory] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_categories": [c.value for c in self.data_categories],
            "specific_documents": self.specific_documents,
            "date_range_start": self.date_range_start,
            "date_range_end": self.date_range_end,
            "exclude_categories": [c.value for c in self.exclude_categories]
        }


@dataclass
class ConsentRecord:
    """Patient consent record"""
    consent_id: str
    patient_id: str
    recipient_id: str
    recipient_name: str
    recipient_type: str  # provider, hospital, pharmacy, etc.

    consent_type: ConsentType
    scope: ConsentScope

    purpose: str
    status: ConsentStatus

    granted_at: str
    effective_date: str
    expiration_date: Optional[str]

    # Permissions
    can_view: bool = True
    can_copy: bool = False
    can_print: bool = False
    can_export: bool = False
    can_share: bool = False

    # Audit
    granted_by: str  # patient_id or authorized representative
    authorization_method: str  # electronic_signature, written, verbal
    signature_data: Optional[str] = None

    # Revocation
    revoked_at: Optional[str] = None
    revoked_by: Optional[str] = None
    revocation_reason: Optional[str] = None

    # Metadata
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "consent_id": self.consent_id,
            "patient_id": self.patient_id,
            "recipient_id": self.recipient_id,
            "recipient_name": self.recipient_name,
            "recipient_type": self.recipient_type,
            "consent_type": self.consent_type.value,
            "scope": self.scope.to_dict(),
            "purpose": self.purpose,
            "status": self.status.value,
            "granted_at": self.granted_at,
            "effective_date": self.effective_date,
            "expiration_date": self.expiration_date,
            "permissions": {
                "can_view": self.can_view,
                "can_copy": self.can_copy,
                "can_print": self.can_print,
                "can_export": self.can_export,
                "can_share": self.can_share
            },
            "granted_by": self.granted_by,
            "authorization_method": self.authorization_method,
            "revoked_at": self.revoked_at,
            "revoked_by": self.revoked_by,
            "revocation_reason": self.revocation_reason,
            "notes": self.notes,
            "metadata": self.metadata
        }


class ConsentEngine:
    """
    Manages patient consent for data sharing

    Features:
    - Granular consent management
    - Expiration tracking
    - Consent verification
    - Revocation handling
    - Audit trail
    """

    def __init__(self):
        """Initialize consent engine"""
        self.consents: Dict[str, ConsentRecord] = {}
        self.patient_consents: Dict[str, List[str]] = {}  # patient_id -> consent_ids
        self.recipient_consents: Dict[str, List[str]] = {}  # recipient_id -> consent_ids

    def grant_consent(self,
                     patient_id: str,
                     recipient_id: str,
                     recipient_name: str,
                     recipient_type: str,
                     consent_type: ConsentType,
                     scope: ConsentScope,
                     purpose: str,
                     duration_days: Optional[int] = None,
                     can_view: bool = True,
                     can_copy: bool = False,
                     can_print: bool = False,
                     can_export: bool = False,
                     can_share: bool = False,
                     granted_by: Optional[str] = None,
                     authorization_method: str = "electronic_signature",
                     signature_data: Optional[str] = None) -> ConsentRecord:
        """
        Grant patient consent

        Args:
            patient_id: Patient granting consent
            recipient_id: Entity receiving consent
            recipient_name: Name of recipient
            recipient_type: Type of recipient
            consent_type: Type of consent
            scope: Scope of consent (data categories, etc.)
            purpose: Purpose of data access
            duration_days: Number of days consent is valid (None = indefinite)
            can_view: Allow viewing data
            can_copy: Allow copying data
            can_print: Allow printing data
            can_export: Allow exporting data
            can_share: Allow sharing data with others
            granted_by: Who granted consent (patient or representative)
            authorization_method: How consent was authorized
            signature_data: Digital signature data

        Returns:
            ConsentRecord
        """
        consent_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Calculate expiration date
        expiration_date = None
        if duration_days:
            expiration = datetime.now(timezone.utc) + timedelta(days=duration_days)
            expiration_date = expiration.isoformat()

        consent = ConsentRecord(
            consent_id=consent_id,
            patient_id=patient_id,
            recipient_id=recipient_id,
            recipient_name=recipient_name,
            recipient_type=recipient_type,
            consent_type=consent_type,
            scope=scope,
            purpose=purpose,
            status=ConsentStatus.ACTIVE,
            granted_at=timestamp,
            effective_date=timestamp,
            expiration_date=expiration_date,
            can_view=can_view,
            can_copy=can_copy,
            can_print=can_print,
            can_export=can_export,
            can_share=can_share,
            granted_by=granted_by or patient_id,
            authorization_method=authorization_method,
            signature_data=signature_data
        )

        # Store consent
        self.consents[consent_id] = consent

        # Index by patient
        if patient_id not in self.patient_consents:
            self.patient_consents[patient_id] = []
        self.patient_consents[patient_id].append(consent_id)

        # Index by recipient
        if recipient_id not in self.recipient_consents:
            self.recipient_consents[recipient_id] = []
        self.recipient_consents[recipient_id].append(consent_id)

        return consent

    def verify_consent(self,
                      patient_id: str,
                      recipient_id: str,
                      data_category: DataCategory,
                      action: str = "view") -> bool:
        """
        Verify if recipient has valid consent for action

        Args:
            patient_id: Patient ID
            recipient_id: Recipient ID
            data_category: Category of data being accessed
            action: Action being performed (view, copy, print, export, share)

        Returns:
            True if consent is valid
        """
        # Get all consents for patient
        consent_ids = self.patient_consents.get(patient_id, [])

        for consent_id in consent_ids:
            consent = self.consents.get(consent_id)
            if not consent:
                continue

            # Check recipient matches
            if consent.recipient_id != recipient_id:
                continue

            # Check status
            if consent.status != ConsentStatus.ACTIVE:
                continue

            # Check expiration
            if consent.expiration_date:
                expiration = datetime.fromisoformat(consent.expiration_date)
                if datetime.now(timezone.utc) > expiration:
                    # Auto-expire consent
                    consent.status = ConsentStatus.EXPIRED
                    continue

            # Check data category is in scope
            if data_category not in consent.scope.data_categories:
                continue

            # Check excluded categories
            if data_category in consent.scope.exclude_categories:
                continue

            # Check permission for action
            permission_map = {
                "view": consent.can_view,
                "copy": consent.can_copy,
                "print": consent.can_print,
                "export": consent.can_export,
                "share": consent.can_share
            }

            if permission_map.get(action, False):
                return True

        return False

    def revoke_consent(self,
                      consent_id: str,
                      revoked_by: str,
                      reason: Optional[str] = None) -> bool:
        """
        Revoke patient consent

        Args:
            consent_id: Consent to revoke
            revoked_by: Who is revoking (patient or representative)
            reason: Reason for revocation

        Returns:
            True if successfully revoked
        """
        consent = self.consents.get(consent_id)
        if not consent:
            return False

        if consent.status != ConsentStatus.ACTIVE:
            return False

        # Revoke consent
        consent.status = ConsentStatus.REVOKED
        consent.revoked_at = datetime.now(timezone.utc).isoformat()
        consent.revoked_by = revoked_by
        consent.revocation_reason = reason

        return True

    def get_patient_consents(self, patient_id: str,
                           active_only: bool = True) -> List[ConsentRecord]:
        """
        Get all consents for patient

        Args:
            patient_id: Patient ID
            active_only: Return only active consents

        Returns:
            List of consent records
        """
        consent_ids = self.patient_consents.get(patient_id, [])
        consents = [self.consents[cid] for cid in consent_ids if cid in self.consents]

        if active_only:
            consents = [c for c in consents if c.status == ConsentStatus.ACTIVE]

        return consents

    def get_recipient_consents(self, recipient_id: str) -> List[ConsentRecord]:
        """
        Get all consents granted to recipient

        Args:
            recipient_id: Recipient ID

        Returns:
            List of consent records
        """
        consent_ids = self.recipient_consents.get(recipient_id, [])
        return [self.consents[cid] for cid in consent_ids if cid in self.consents]

    def get_consent_summary(self, patient_id: str) -> Dict[str, Any]:
        """
        Get summary of patient consents

        Args:
            patient_id: Patient ID

        Returns:
            Consent summary
        """
        all_consents = self.get_patient_consents(patient_id, active_only=False)
        active_consents = [c for c in all_consents if c.status == ConsentStatus.ACTIVE]

        return {
            "patient_id": patient_id,
            "total_consents": len(all_consents),
            "active_consents": len(active_consents),
            "expired_consents": len([c for c in all_consents if c.status == ConsentStatus.EXPIRED]),
            "revoked_consents": len([c for c in all_consents if c.status == ConsentStatus.REVOKED]),
            "consents_by_type": self._count_by_type(all_consents),
            "active_recipients": list(set(c.recipient_id for c in active_consents))
        }

    def _count_by_type(self, consents: List[ConsentRecord]) -> Dict[str, int]:
        """Count consents by type"""
        counts = {}
        for consent in consents:
            consent_type = consent.consent_type.value
            counts[consent_type] = counts.get(consent_type, 0) + 1
        return counts


# Example usage
if __name__ == "__main__":
    engine = ConsentEngine()

    # Grant consent for treatment
    scope = ConsentScope(
        data_categories=[
            DataCategory.MEDICAL_RECORDS,
            DataCategory.PRESCRIPTIONS,
            DataCategory.LAB_RESULTS
        ]
    )

    consent = engine.grant_consent(
        patient_id="patient_12345",
        recipient_id="dr_smith_001",
        recipient_name="Dr. John Smith",
        recipient_type="provider",
        consent_type=ConsentType.TREATMENT,
        scope=scope,
        purpose="Ongoing treatment for diabetes",
        duration_days=365,
        can_view=True,
        can_copy=True
    )

    print(f"Consent granted: {consent.consent_id}")

    # Verify consent
    has_consent = engine.verify_consent(
        patient_id="patient_12345",
        recipient_id="dr_smith_001",
        data_category=DataCategory.MEDICAL_RECORDS,
        action="view"
    )

    print(f"Has consent to view medical records: {has_consent}")

    # Get summary
    summary = engine.get_consent_summary("patient_12345")
    print(f"Consent summary: {summary}")
