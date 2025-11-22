"""
Test Suite for Consent Management

Ensures consent management meets HIPAA requirements.
"""

import pytest
from datetime import datetime, timedelta
from nix_system.consent.consent_engine import (
    ConsentEngine,
    ConsentType,
    ConsentStatus,
    DataCategory,
    ConsentScope
)


@pytest.fixture
def consent_engine():
    """Create consent engine instance"""
    return ConsentEngine()


class TestConsentEngine:
    """Test suite for consent management"""

    def test_grant_consent(self, consent_engine):
        """Test granting patient consent"""
        scope = ConsentScope(
            data_categories=[
                DataCategory.MEDICAL_RECORDS,
                DataCategory.PRESCRIPTIONS
            ]
        )

        consent = consent_engine.grant_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            recipient_name="Dr. John Smith",
            recipient_type="provider",
            consent_type=ConsentType.TREATMENT,
            scope=scope,
            purpose="Ongoing diabetes treatment",
            duration_days=365,
            can_view=True,
            can_copy=True
        )

        assert consent.consent_id is not None
        assert consent.status == ConsentStatus.ACTIVE
        assert consent.patient_id == "patient_12345"
        assert consent.recipient_id == "dr_smith_001"

    def test_verify_consent_valid(self, consent_engine):
        """Test verifying valid consent"""
        scope = ConsentScope(
            data_categories=[DataCategory.MEDICAL_RECORDS]
        )

        consent_engine.grant_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            recipient_name="Dr. Smith",
            recipient_type="provider",
            consent_type=ConsentType.TREATMENT,
            scope=scope,
            purpose="Treatment",
            can_view=True
        )

        # Verify consent exists
        has_consent = consent_engine.verify_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            data_category=DataCategory.MEDICAL_RECORDS,
            action="view"
        )

        assert has_consent is True

    def test_verify_consent_invalid(self, consent_engine):
        """Test verifying invalid consent"""
        # No consent granted
        has_consent = consent_engine.verify_consent(
            patient_id="patient_12345",
            recipient_id="unauthorized_user",
            data_category=DataCategory.MEDICAL_RECORDS,
            action="view"
        )

        assert has_consent is False

    def test_verify_consent_wrong_data_category(self, consent_engine):
        """Test consent verification for wrong data category"""
        scope = ConsentScope(
            data_categories=[DataCategory.PRESCRIPTIONS]
        )

        consent_engine.grant_consent(
            patient_id="patient_12345",
            recipient_id="pharmacy_001",
            recipient_name="Main Pharmacy",
            recipient_type="pharmacy",
            consent_type=ConsentType.TREATMENT,
            scope=scope,
            purpose="Fill prescriptions",
            can_view=True
        )

        # Try to access different category
        has_consent = consent_engine.verify_consent(
            patient_id="patient_12345",
            recipient_id="pharmacy_001",
            data_category=DataCategory.MEDICAL_RECORDS,  # Different category
            action="view"
        )

        assert has_consent is False

    def test_verify_consent_insufficient_permission(self, consent_engine):
        """Test consent with insufficient permissions"""
        scope = ConsentScope(
            data_categories=[DataCategory.MEDICAL_RECORDS]
        )

        consent_engine.grant_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            recipient_name="Dr. Smith",
            recipient_type="provider",
            consent_type=ConsentType.TREATMENT,
            scope=scope,
            purpose="View only",
            can_view=True,
            can_copy=False  # Cannot copy
        )

        # Can view
        can_view = consent_engine.verify_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            data_category=DataCategory.MEDICAL_RECORDS,
            action="view"
        )
        assert can_view is True

        # Cannot copy
        can_copy = consent_engine.verify_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            data_category=DataCategory.MEDICAL_RECORDS,
            action="copy"
        )
        assert can_copy is False

    def test_revoke_consent(self, consent_engine):
        """Test revoking patient consent"""
        scope = ConsentScope(
            data_categories=[DataCategory.MEDICAL_RECORDS]
        )

        consent = consent_engine.grant_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            recipient_name="Dr. Smith",
            recipient_type="provider",
            consent_type=ConsentType.TREATMENT,
            scope=scope,
            purpose="Treatment"
        )

        # Revoke consent
        revoked = consent_engine.revoke_consent(
            consent_id=consent.consent_id,
            revoked_by="patient_12345",
            reason="No longer treating with this provider"
        )

        assert revoked is True
        assert consent.status == ConsentStatus.REVOKED
        assert consent.revoked_at is not None

        # Verify consent no longer valid
        has_consent = consent_engine.verify_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            data_category=DataCategory.MEDICAL_RECORDS,
            action="view"
        )
        assert has_consent is False

    def test_get_patient_consents(self, consent_engine):
        """Test retrieving patient consents"""
        scope = ConsentScope(
            data_categories=[DataCategory.MEDICAL_RECORDS]
        )

        # Grant multiple consents
        consent_engine.grant_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            recipient_name="Dr. Smith",
            recipient_type="provider",
            consent_type=ConsentType.TREATMENT,
            scope=scope,
            purpose="Treatment"
        )

        consent_engine.grant_consent(
            patient_id="patient_12345",
            recipient_id="pharmacy_001",
            recipient_name="Main Pharmacy",
            recipient_type="pharmacy",
            consent_type=ConsentType.TREATMENT,
            scope=scope,
            purpose="Prescriptions"
        )

        # Get all active consents
        consents = consent_engine.get_patient_consents("patient_12345", active_only=True)
        assert len(consents) == 2

    def test_consent_summary(self, consent_engine):
        """Test generating consent summary"""
        scope = ConsentScope(
            data_categories=[DataCategory.MEDICAL_RECORDS]
        )

        consent_engine.grant_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            recipient_name="Dr. Smith",
            recipient_type="provider",
            consent_type=ConsentType.TREATMENT,
            scope=scope,
            purpose="Treatment"
        )

        summary = consent_engine.get_consent_summary("patient_12345")

        assert summary["patient_id"] == "patient_12345"
        assert summary["total_consents"] == 1
        assert summary["active_consents"] == 1
        assert "dr_smith_001" in summary["active_recipients"]

    def test_excluded_categories(self, consent_engine):
        """Test consent with excluded data categories"""
        scope = ConsentScope(
            data_categories=[
                DataCategory.MEDICAL_RECORDS,
                DataCategory.PRESCRIPTIONS,
                DataCategory.LAB_RESULTS
            ],
            exclude_categories=[
                DataCategory.MENTAL_HEALTH,
                DataCategory.SUBSTANCE_ABUSE
            ]
        )

        consent_engine.grant_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            recipient_name="Dr. Smith",
            recipient_type="provider",
            consent_type=ConsentType.TREATMENT,
            scope=scope,
            purpose="General treatment",
            can_view=True
        )

        # Can access medical records
        assert consent_engine.verify_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            data_category=DataCategory.MEDICAL_RECORDS,
            action="view"
        ) is True

        # Cannot access mental health (excluded)
        assert consent_engine.verify_consent(
            patient_id="patient_12345",
            recipient_id="dr_smith_001",
            data_category=DataCategory.MENTAL_HEALTH,
            action="view"
        ) is False
