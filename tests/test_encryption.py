"""
Test Suite for AES Encryption

Ensures encryption meets HIPAA security requirements.
"""

import pytest
from nix_system.security.encryption.aes_encryption import AESEncryption, RSAEncryption


class TestAESEncryption:
    """Test suite for AES-256-GCM encryption"""

    def test_key_generation(self):
        """Test encryption key generation"""
        key = AESEncryption.generate_key()
        assert len(key) == 32  # 256 bits

    def test_encrypt_decrypt_string(self):
        """Test string encryption and decryption"""
        aes = AESEncryption()
        plaintext = "Patient: John Doe, SSN: 123-45-6789"

        # Encrypt
        encrypted = aes.encrypt_string(plaintext)
        assert encrypted != plaintext
        assert len(encrypted) > 0

        # Decrypt
        decrypted = aes.decrypt_string(encrypted)
        assert decrypted == plaintext

    def test_encrypt_decrypt_bytes(self):
        """Test bytes encryption and decryption"""
        aes = AESEncryption()
        plaintext = b"Protected Health Information"

        # Encrypt
        ciphertext, iv, auth_tag = aes.encrypt(plaintext)
        assert ciphertext != plaintext
        assert len(iv) == 12  # GCM nonce size
        assert len(auth_tag) == 16  # GCM tag size

        # Decrypt
        decrypted = aes.decrypt(ciphertext, iv, auth_tag)
        assert decrypted == plaintext

    def test_authenticated_encryption(self):
        """Test authenticated encryption with additional data"""
        aes = AESEncryption()
        plaintext = b"Medical Record Data"
        associated_data = b"patient_12345"

        # Encrypt with associated data
        ciphertext, iv, auth_tag = aes.encrypt(plaintext, associated_data)

        # Decrypt with same associated data (should succeed)
        decrypted = aes.decrypt(ciphertext, iv, auth_tag, associated_data)
        assert decrypted == plaintext

    def test_tamper_detection(self):
        """Test that tampering is detected"""
        aes = AESEncryption()
        plaintext = b"Critical PHI Data"

        ciphertext, iv, auth_tag = aes.encrypt(plaintext)

        # Tamper with ciphertext
        tampered_ciphertext = bytes([b ^ 0xFF for b in ciphertext])

        # Attempt to decrypt tampered data (should fail)
        with pytest.raises(Exception):
            aes.decrypt(tampered_ciphertext, iv, auth_tag)

    def test_key_derivation(self):
        """Test PBKDF2 key derivation"""
        password = "StrongPassword123!"
        salt = b"unique_salt_value"

        # Derive key
        key1 = AESEncryption.derive_key(password, salt)
        assert len(key1) == 32

        # Same password and salt should produce same key
        key2 = AESEncryption.derive_key(password, salt)
        assert key1 == key2

        # Different salt should produce different key
        different_salt = b"different_salt"
        key3 = AESEncryption.derive_key(password, different_salt)
        assert key1 != key3


class TestRSAEncryption:
    """Test suite for RSA-4096 encryption"""

    def test_key_pair_generation(self):
        """Test RSA key pair generation"""
        private_key, public_key = RSAEncryption.generate_key_pair()
        assert private_key is not None
        assert public_key is not None

    def test_encrypt_decrypt(self):
        """Test RSA encryption and decryption"""
        private_key, public_key = RSAEncryption.generate_key_pair()
        rsa = RSAEncryption(private_key, public_key)

        # Encrypt small data (like AES key)
        plaintext = b"AES-256 Encryption Key Data"
        ciphertext = rsa.encrypt_with_public_key(plaintext, public_key)
        assert ciphertext != plaintext

        # Decrypt
        decrypted = rsa.decrypt_with_private_key(ciphertext)
        assert decrypted == plaintext

    def test_key_export(self):
        """Test PEM key export"""
        private_key, public_key = RSAEncryption.generate_key_pair()
        rsa = RSAEncryption(private_key, public_key)

        # Export public key
        public_pem = rsa.export_public_key_pem()
        assert b"BEGIN PUBLIC KEY" in public_pem

        # Export private key
        private_pem = rsa.export_private_key_pem()
        assert b"BEGIN PRIVATE KEY" in private_pem

        # Export encrypted private key
        password = b"encryption_password"
        encrypted_pem = rsa.export_private_key_pem(password)
        assert b"BEGIN ENCRYPTED PRIVATE KEY" in encrypted_pem
