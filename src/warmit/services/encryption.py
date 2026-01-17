"""Encryption service for sensitive data in database.

SECURITY: This service NEVER falls back to plaintext storage.
If encryption is not available, operations will fail safely.

Developed with ❤️ by Givaa
https://github.com/Givaa
"""

import os
from cryptography.fernet import Fernet
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Raised when encryption/decryption fails and no fallback is safe."""
    pass


class EncryptionService:
    """Handle encryption/decryption of sensitive data using Fernet (symmetric encryption).

    SECURITY: This service will NOT fall back to plaintext storage.
    If ENCRYPTION_KEY is not set, encryption operations will raise an error.
    """

    def __init__(self, require_key: bool = True):
        """Initialize encryption service with key from environment.

        Args:
            require_key: If True, raise error if ENCRYPTION_KEY not set (default: True)
        """
        self.cipher = None
        self._key_available = False

        encryption_key = os.getenv("ENCRYPTION_KEY")

        if not encryption_key:
            if require_key:
                logger.error("❌ ENCRYPTION_KEY not set!")
                logger.error("   Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
                logger.error("   Add ENCRYPTION_KEY=<your_key> to your .env file")
                # Don't raise here, but self.cipher will be None
                # Operations will fail safely
            return

        # Convert string key to bytes if needed
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()

        try:
            self.cipher = Fernet(encryption_key)
            self._key_available = True
            logger.info("✅ Encryption service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize encryption with provided key: {e}")
            # cipher remains None - operations will fail safely

    @property
    def is_available(self) -> bool:
        """Check if encryption is properly configured."""
        return self._key_available and self.cipher is not None

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string.

        SECURITY: Will raise EncryptionError if encryption not available.
        Never falls back to plaintext storage.

        Args:
            plaintext: String to encrypt

        Returns:
            Encrypted string (base64 encoded)

        Raises:
            EncryptionError: If encryption is not available
        """
        if not plaintext:
            return plaintext

        if not self.cipher:
            raise EncryptionError(
                "ENCRYPTION_KEY not configured. Cannot store sensitive data. "
                "Set ENCRYPTION_KEY in your .env file."
            )

        try:
            encrypted_bytes = self.cipher.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {e}")

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string.

        Args:
            ciphertext: Encrypted string (base64 encoded)

        Returns:
            Decrypted plaintext string

        Note:
            For backwards compatibility, if decryption fails and the string
            doesn't look like a Fernet token, it's assumed to be plaintext.
        """
        if not ciphertext:
            return ciphertext

        # Fernet tokens always start with 'gAAAAA' when base64 encoded
        is_likely_encrypted = ciphertext.startswith('gAAAAA')

        if not self.cipher:
            if is_likely_encrypted:
                raise EncryptionError(
                    "Cannot decrypt: ENCRYPTION_KEY not configured but data appears encrypted."
                )
            # Assume plaintext for backwards compatibility
            logger.warning("Encryption not available, assuming plaintext data")
            return ciphertext

        try:
            decrypted_bytes = self.cipher.decrypt(ciphertext.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            if is_likely_encrypted:
                # This was definitely encrypted but failed - wrong key?
                raise EncryptionError(
                    f"Decryption failed (wrong key?): {e}"
                )
            # Might be legacy plaintext - return as-is for backwards compat
            logger.debug(f"Decryption failed, assuming plaintext: {e}")
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
