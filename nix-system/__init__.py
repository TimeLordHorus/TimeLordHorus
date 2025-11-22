"""
NIX - National Information Exchange System

HIPAA-compliant medical records information subsystem for secure
healthcare information exchange.
"""

__version__ = "1.0.0"
__author__ = "NIX Development Team"
__license__ = "Proprietary"

# Export main components
from nix_system.core.pipeline import NIXPipeline
from nix_system.security.hipaa.audit_logger import HIPAAAuditLogger
from nix_system.security.encryption.aes_encryption import AESEncryption
from nix_system.storage.client_storage import ClientStorageSystem
from nix_system.tracking.provenance import DocumentProvenance
from nix_system.consent.consent_engine import ConsentEngine

__all__ = [
    "NIXPipeline",
    "HIPAAAuditLogger",
    "AESEncryption",
    "ClientStorageSystem",
    "DocumentProvenance",
    "ConsentEngine",
]
