"""
AES-256 Encryption Module for HIPAA Compliance

Implements NIST-approved encryption for PHI/PII at rest and in transit.
Compliant with HIPAA Security Rule § 164.312(a)(2)(iv) and § 164.312(e)(2)(ii)
"""

import os
import base64
import hashlib
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import secrets


class AESEncryption:
    """
    AES-256-GCM encryption for HIPAA-compliant data protection

    Features:
    - AES-256-GCM authenticated encryption
    - Unique IV for each encryption operation
    - PBKDF2 key derivation
    - Integrity verification via GCM authentication tags
    """

    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize AES encryption

        Args:
            master_key: 32-byte master encryption key (generates if not provided)
        """
        if master_key is None:
            self.master_key = self.generate_key()
        else:
            if len(master_key) != 32:
                raise ValueError("Master key must be 32 bytes for AES-256")
            self.master_key = master_key

    @staticmethod
    def generate_key() -> bytes:
        """Generate cryptographically secure 256-bit encryption key"""
        return secrets.token_bytes(32)

    @staticmethod
    def derive_key(password: str, salt: bytes, iterations: int = 600000) -> bytes:
        """
        Derive encryption key from password using PBKDF2

        Args:
            password: User password
            salt: Cryptographic salt (must be unique per user)
            iterations: PBKDF2 iterations (600k recommended by OWASP 2023)

        Returns:
            32-byte derived key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def encrypt(self, plaintext: bytes, associated_data: Optional[bytes] = None) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt data using AES-256-GCM

        Args:
            plaintext: Data to encrypt
            associated_data: Additional authenticated data (not encrypted but authenticated)

        Returns:
            Tuple of (ciphertext, iv, auth_tag)
        """
        # Generate unique 96-bit IV (nonce) for GCM
        iv = os.urandom(12)

        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Add associated data if provided
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)

        # Encrypt
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Get authentication tag
        auth_tag = encryptor.tag

        return ciphertext, iv, auth_tag

    def decrypt(self, ciphertext: bytes, iv: bytes, auth_tag: bytes,
                associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt data using AES-256-GCM

        Args:
            ciphertext: Encrypted data
            iv: Initialization vector used during encryption
            auth_tag: Authentication tag for integrity verification
            associated_data: Additional authenticated data (must match encryption)

        Returns:
            Decrypted plaintext

        Raises:
            cryptography.exceptions.InvalidTag: If authentication fails (tampered data)
        """
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv, auth_tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Add associated data if provided
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)

        # Decrypt and verify
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext

    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt string and return base64-encoded result

        Args:
            plaintext: String to encrypt

        Returns:
            Base64-encoded encrypted data (format: base64(iv + auth_tag + ciphertext))
        """
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext, iv, auth_tag = self.encrypt(plaintext_bytes)

        # Combine iv + auth_tag + ciphertext
        encrypted_data = iv + auth_tag + ciphertext

        # Return base64-encoded
        return base64.b64encode(encrypted_data).decode('utf-8')

    def decrypt_string(self, encrypted_b64: str) -> str:
        """
        Decrypt base64-encoded encrypted string

        Args:
            encrypted_b64: Base64-encoded encrypted data

        Returns:
            Decrypted string
        """
        # Decode base64
        encrypted_data = base64.b64decode(encrypted_b64)

        # Extract components (iv: 12 bytes, tag: 16 bytes, rest: ciphertext)
        iv = encrypted_data[:12]
        auth_tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]

        # Decrypt
        plaintext_bytes = self.decrypt(ciphertext, iv, auth_tag)

        return plaintext_bytes.decode('utf-8')

    def encrypt_file(self, input_path: str, output_path: str,
                     chunk_size: int = 64 * 1024) -> None:
        """
        Encrypt large file in chunks

        Args:
            input_path: Path to plaintext file
            output_path: Path to encrypted output file
            chunk_size: Size of chunks to process (64KB default)
        """
        # Generate unique IV
        iv = os.urandom(12)

        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            # Write IV first
            outfile.write(iv)

            # Encrypt file in chunks
            while True:
                chunk = infile.read(chunk_size)
                if not chunk:
                    break
                encrypted_chunk = encryptor.update(chunk)
                outfile.write(encrypted_chunk)

            # Finalize and write auth tag
            outfile.write(encryptor.finalize())
            outfile.write(encryptor.tag)

    def decrypt_file(self, input_path: str, output_path: str,
                     chunk_size: int = 64 * 1024) -> None:
        """
        Decrypt large file in chunks

        Args:
            input_path: Path to encrypted file
            output_path: Path to decrypted output file
            chunk_size: Size of chunks to process (64KB default)
        """
        with open(input_path, 'rb') as infile:
            # Read IV (first 12 bytes)
            iv = infile.read(12)

            # Read entire encrypted content to get auth tag
            encrypted_content = infile.read()

        # Extract auth tag (last 16 bytes)
        auth_tag = encrypted_content[-16:]
        ciphertext = encrypted_content[:-16]

        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv, auth_tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Decrypt and write
        with open(output_path, 'wb') as outfile:
            # Process in chunks
            for i in range(0, len(ciphertext), chunk_size):
                chunk = ciphertext[i:i + chunk_size]
                decrypted_chunk = decryptor.update(chunk)
                outfile.write(decrypted_chunk)

            # Finalize
            outfile.write(decryptor.finalize())


class RSAEncryption:
    """
    RSA-4096 asymmetric encryption for key exchange and digital signatures
    """

    def __init__(self, private_key: Optional[rsa.RSAPrivateKey] = None,
                 public_key: Optional[rsa.RSAPublicKey] = None):
        """
        Initialize RSA encryption

        Args:
            private_key: RSA private key
            public_key: RSA public key
        """
        self.private_key = private_key
        self.public_key = public_key

    @staticmethod
    def generate_key_pair() -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """Generate RSA-4096 key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key

    def encrypt_with_public_key(self, plaintext: bytes, public_key: rsa.RSAPublicKey) -> bytes:
        """Encrypt data with RSA public key (for small data like AES keys)"""
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    def decrypt_with_private_key(self, ciphertext: bytes) -> bytes:
        """Decrypt data with RSA private key"""
        if not self.private_key:
            raise ValueError("Private key not available")

        plaintext = self.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext

    def export_public_key_pem(self) -> bytes:
        """Export public key in PEM format"""
        if not self.public_key:
            raise ValueError("Public key not available")

        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def export_private_key_pem(self, password: Optional[bytes] = None) -> bytes:
        """Export private key in PEM format (optionally encrypted)"""
        if not self.private_key:
            raise ValueError("Private key not available")

        encryption = serialization.NoEncryption()
        if password:
            encryption = serialization.BestAvailableEncryption(password)

        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )


# Example usage
if __name__ == "__main__":
    # AES encryption example
    aes = AESEncryption()

    # Encrypt PHI
    phi_data = "Patient: John Doe, DOB: 1980-01-01, SSN: 123-45-6789"
    encrypted = aes.encrypt_string(phi_data)
    print(f"Encrypted: {encrypted[:50]}...")

    # Decrypt
    decrypted = aes.decrypt_string(encrypted)
    print(f"Decrypted: {decrypted}")

    # RSA key pair generation
    private_key, public_key = RSAEncryption.generate_key_pair()
    print(f"\nGenerated RSA-4096 key pair")
