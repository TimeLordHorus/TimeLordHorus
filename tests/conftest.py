"""
Pytest configuration and shared fixtures
"""

import pytest
import os
from datetime import datetime


@pytest.fixture(scope="session")
def test_encryption_key():
    """Generate test encryption key"""
    from nix_system.security.encryption.aes_encryption import AESEncryption
    return AESEncryption.generate_key()


@pytest.fixture(scope="function")
def temp_log_dir(tmp_path):
    """Create temporary log directory"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return str(log_dir)


@pytest.fixture(scope="function")
def test_patient():
    """Create test patient data"""
    return {
        "patient_id": "test_patient_001",
        "first_name": "Test",
        "last_name": "Patient",
        "date_of_birth": "1980-01-01",
        "ssn": "123-45-6789"
    }


@pytest.fixture(scope="function")
def test_provider():
    """Create test provider data"""
    return {
        "provider_id": "test_provider_001",
        "name": "Dr. Test Provider",
        "npi": "1234567890",
        "specialty": "Internal Medicine"
    }


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment before each test"""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"

    yield

    # Cleanup after test
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
