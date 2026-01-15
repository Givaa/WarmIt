"""Encryption service for sensitive data in database."""

import os
from cryptography.fernet import Fernet
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EncryptionService:
    """Handle encryption/decryption of sensitive data using Fernet (symmetric encryption)."""

    def __init__(self):
        """Initialize encryption service with key from environment."""
        # Get encryption key from environment variable
        encryption_key = os.getenv("ENCRYPTION_KEY")

        if not encryption_key:
            logger.warning("⚠️  ENCRYPTION_KEY not set! Generating a new key...")
            logger.warning("⚠️  Add this to your .env file to persist encryption:")
            encryption_key = Fernet.generate_key().decode()
            logger.warning(f"ENCRYPTION_KEY={encryption_key}")
            logger.warning("⚠️  Without setting this key, you won't be able to decrypt existing data after restart!")

        # Convert string key to bytes if needed
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()

        try:
            self.cipher = Fernet(encryption_key)
            logger.info("✅ Encryption service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize encryption: {e}")
            logger.error("⚠️  Data encryption will be disabled!")
            self.cipher = None

    def encrypt(self, plaintext: str) -> Optional[str]:
        """Encrypt a string.

        Args:
            plaintext: String to encrypt

        Returns:
            Encrypted string (base64 encoded) or None if encryption fails
        """
        if not self.cipher:
            logger.warning("Encryption not available, storing plaintext")
            return plaintext

        if not plaintext:
            return plaintext

        try:
            # Convert string to bytes, encrypt, and return as string
            encrypted_bytes = self.cipher.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return plaintext  # Fallback to plaintext if encryption fails

    def decrypt(self, ciphertext: str) -> Optional[str]:
        """Decrypt a string.

        Args:
            ciphertext: Encrypted string (base64 encoded)

        Returns:
            Decrypted plaintext string or None if decryption fails
        """
        if not self.cipher:
            logger.warning("Encryption not available, returning as-is")
            return ciphertext

        if not ciphertext:
            return ciphertext

        try:
            # Convert string to bytes, decrypt, and return as string
            decrypted_bytes = self.cipher.decrypt(ciphertext.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            # If decryption fails, it might be plaintext (backwards compatibility)
            logger.debug(f"Decryption failed (might be plaintext): {e}")
            return ciphertext


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get or create global encryption service instance.

    Returns:
        EncryptionService instance
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


def encrypt_password(password: str) -> str:
    """Encrypt a password.

    Args:
        password: Plain text password

    Returns:
        Encrypted password
    """
    service = get_encryption_service()
    return service.encrypt(password) or password


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt a password.

    Args:
        encrypted_password: Encrypted password

    Returns:
        Decrypted password
    """
    service = get_encryption_service()
    return service.decrypt(encrypted_password) or encrypted_password
