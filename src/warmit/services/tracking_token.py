"""Secure HMAC token generation and validation for email tracking.

This module provides cryptographically signed tokens for tracking URLs,
preventing unauthorized access to tracking endpoints.

Developed with ❤️ by Givaa
https://github.com/Givaa
"""

import hmac
import hashlib
import time
import os
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def _get_tracking_secret() -> str:
    """Get tracking secret from environment.

    Returns:
        Secret key for HMAC signing
    """
    secret = os.getenv("TRACKING_SECRET_KEY", "")
    if not secret:
        logger.warning(
            "TRACKING_SECRET_KEY not set! Using fallback. "
            "This is insecure for production!"
        )
        # Fallback for development - NOT secure for production
        return "warmit-dev-secret-change-in-production"
    return secret


# Token expiry in days (typical campaign duration)
TOKEN_EXPIRY_DAYS = 30


def generate_tracking_token(email_id: int) -> Tuple[str, int]:
    """Generate HMAC token for tracking URL.

    The token is generated using HMAC-SHA256 with the email_id and
    current timestamp. It's truncated to 32 characters for shorter URLs.

    Args:
        email_id: The email ID to generate token for

    Returns:
        Tuple of (token, timestamp)
    """
    secret = _get_tracking_secret()
    timestamp = int(time.time())
    message = f"{email_id}:{timestamp}"

    token = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()[:32]  # Truncated for shorter URLs

    return token, timestamp


def validate_tracking_token(
    email_id: int,
    token: str,
    timestamp: int
) -> bool:
    """Validate HMAC tracking token.

    Checks that:
    1. Token is not expired (within TOKEN_EXPIRY_DAYS)
    2. Token matches expected HMAC signature

    Args:
        email_id: The email ID from the URL
        token: The token from the URL
        timestamp: The timestamp from the URL

    Returns:
        True if token is valid and not expired, False otherwise
    """
    # Check expiry
    current_time = time.time()
    token_age_seconds = current_time - timestamp

    if token_age_seconds > TOKEN_EXPIRY_DAYS * 86400:
        logger.debug(f"Token expired for email {email_id} (age: {token_age_seconds/86400:.1f} days)")
        return False

    if token_age_seconds < 0:
        # Token from the future - suspicious
        logger.warning(f"Token has future timestamp for email {email_id}")
        return False

    # Regenerate expected token and compare
    secret = _get_tracking_secret()
    message = f"{email_id}:{timestamp}"

    expected = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()[:32]

    # Use constant-time comparison to prevent timing attacks
    is_valid = hmac.compare_digest(token, expected)

    if not is_valid:
        logger.debug(f"Invalid token for email {email_id}")

    return is_valid


def generate_tracking_url(base_url: str, email_id: int) -> str:
    """Generate complete tracking URL with signed token.

    Args:
        base_url: Base URL for tracking (e.g., "http://example.com")
        email_id: The email ID to track

    Returns:
        Complete tracking URL with token and timestamp
    """
    token, timestamp = generate_tracking_token(email_id)
    return f"{base_url}/track/open/{email_id}?token={token}&ts={timestamp}"


def is_token_required() -> bool:
    """Check if token validation is enabled.

    Token validation is enabled when TRACKING_SECRET_KEY is set.
    This allows backwards compatibility during migration.

    Returns:
        True if tokens should be validated
    """
    secret = os.getenv("TRACKING_SECRET_KEY", "")
    return bool(secret)
