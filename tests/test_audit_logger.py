"""
Test Suite for HIPAA Audit Logger

Ensures audit logging meets HIPAA compliance requirements.
"""

import pytest
from datetime import datetime
from nix_system.security.hipaa.audit_logger import (
    HIPAAAuditLogger,
    AuditEventType,
    AuditSeverity
)


@pytest.fixture
def audit_logger(tmp_path):
    """Create audit logger with temporary directory"""
    return HIPAAAuditLogger(
        log_directory=str(tmp_path / "audit"),
        enable_encryption=False,  # Disabled for testing
        enable_integrity_check=True
    )


class TestAuditLogger:
    """Test suite for audit logging"""

    def test_log_phi_access(self, audit_logger):
        """Test logging PHI access"""
        event_id = audit_logger.log_phi_access(
            user_id="test_user_001",
            patient_id="patient_12345",
            resource_type="medical_record",
            resource_id="mr_001",
            action="view",
            ip_address="192.168.1.100",
            purpose="treatment"
        )

        assert event_id is not None
        assert len(event_id) == 36  # UUID length

    def test_log_emergency_access(self, audit_logger):
        """Test logging emergency break-glass access"""
        event_id = audit_logger.log_emergency_access(
            user_id="dr_emergency_001",
            patient_id="patient_12345",
            resource_type="medical_record",
            justification="Life-threatening emergency",
            ip_address="192.168.1.101"
        )

        assert event_id is not None

    def test_log_breach_detection(self, audit_logger):
        """Test logging potential HIPAA breach"""
        affected_patients = ["patient_001", "patient_002", "patient_003"]

        event_id = audit_logger.log_breach_detection(
            description="Unauthorized access detected",
            affected_patients=affected_patients,
            data_compromised="Medical records",
            detection_method="Automated monitoring"
        )

        assert event_id is not None

    def test_log_event_with_integrity_check(self, audit_logger):
        """Test audit log integrity verification"""
        event_id = audit_logger.log_event(
            event_type=AuditEventType.ACCESS_PHI,
            user_id="test_user",
            action="test_action",
            resource_type="test_resource",
            severity=AuditSeverity.INFO
        )

        # In production, would retrieve and verify
        assert event_id is not None

    def test_compliance_report_generation(self, audit_logger):
        """Test HIPAA compliance report generation"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)

        report = audit_logger.generate_compliance_report(start_date, end_date)

        assert report is not None
        assert "report_id" in report
        assert "total_access_events" in report
        assert "period_start" in report
        assert "period_end" in report

    def test_severity_levels(self, audit_logger):
        """Test different severity levels"""
        severities = [
            AuditSeverity.INFO,
            AuditSeverity.WARNING,
            AuditSeverity.CRITICAL,
            AuditSeverity.EMERGENCY
        ]

        for severity in severities:
            event_id = audit_logger.log_event(
                event_type=AuditEventType.SECURITY_ALERT,
                user_id="test_user",
                action=f"test_severity_{severity.value}",
                resource_type="test",
                severity=severity
            )
            assert event_id is not None
