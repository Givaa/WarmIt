"""Authentication module for WarmIt Dashboard."""

import hashlib
import secrets
import os
from pathlib import Path
from typing import Optional, Tuple
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Auth file locations
AUTH_FILE = Path(__file__).parent / ".auth"
SESSION_FILE = Path(__file__).parent / ".sessions"
ENV_FILE = Path(__file__).parent.parent / "docker" / ".env"

# Session duration (7 days)
SESSION_DURATION = timedelta(days=7)


def generate_password(length: int = 16) -> str:
    """Generate a secure random password.

    Args:
        length: Length of password (default 16)

    Returns:
        Secure random password with alphanumeric + special chars
    """
    # Use letters, digits, and safe special characters
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*-_=+"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt.

    Args:
        password: Plain text password

    Returns:
        Hashed password in format: salt$hash
    """
    # Generate random salt (32 bytes = 64 hex chars)
    salt = secrets.token_hex(32)

    # Hash password with salt
    pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()

    # Return in format: salt$hash
    return f"{salt}${pwd_hash}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash.

    Args:
        password: Plain text password to verify
        hashed: Hashed password in format: salt$hash

    Returns:
        True if password matches, False otherwise
    """
    try:
        salt, pwd_hash = hashed.split('$')
        # Hash the provided password with the same salt
        new_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        return new_hash == pwd_hash
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def get_or_create_password() -> Tuple[str, bool]:
    """Get existing password or create a new one.

    Returns:
        Tuple of (password_hash, is_new)
        - password_hash: The hashed password
        - is_new: True if password was just generated, False if existing
    """
    # Check if auth file exists
    if AUTH_FILE.exists():
        try:
            with open(AUTH_FILE, 'r') as f:
                password_hash = f.read().strip()
                if password_hash:
                    logger.info("✅ Using existing admin password")
                    return password_hash, False
        except Exception as e:
            logger.error(f"Error reading auth file: {e}")

    # Generate new password
    logger.info("🔐 No existing password found, generating new admin password...")
    password = generate_password(16)
    password_hash = hash_password(password)

    # Save to file
    try:
        AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(AUTH_FILE, 'w') as f:
            f.write(password_hash)

        # Set secure permissions (owner read/write only)
        AUTH_FILE.chmod(0o600)

        logger.info("=" * 80)
        logger.info("⚠️  ADMIN PASSWORD GENERATED - SAVE THIS PASSWORD!")
        logger.info("=" * 80)
        logger.info(f"🔑 Admin Password: {password}")
        logger.info("=" * 80)
        logger.info("⚠️  This password will only be shown ONCE at first startup!")
        logger.info("⚠️  Save it somewhere safe!")
        logger.info("=" * 80)

        # Also log to a file for safety
        log_file = Path(__file__).parent / "first_run_password.txt"
        with open(log_file, 'w') as f:
            f.write(f"WarmIt Admin Password (Generated at startup)\n")
            f.write(f"=" * 60 + "\n")
            f.write(f"Password: {password}\n")
            f.write(f"=" * 60 + "\n")
            f.write(f"This file will be automatically deleted after first successful login.\n")
        log_file.chmod(0o600)

        logger.info(f"💾 Password also saved temporarily to: {log_file}")
        logger.info("   (This file will be deleted after first successful login)")

        return password_hash, True

    except Exception as e:
        logger.error(f"Failed to save password: {e}")
        raise


def change_password(old_password: str, new_password: str) -> Tuple[bool, str]:
    """Change the admin password.

    Args:
        old_password: Current password
        new_password: New password to set

    Returns:
        Tuple of (success, message)
    """
    # Verify old password
    if not AUTH_FILE.exists():
        return False, "No password set. This should not happen."

    try:
        with open(AUTH_FILE, 'r') as f:
            current_hash = f.read().strip()

        if not verify_password(old_password, current_hash):
            return False, "Current password is incorrect"

        # Validate new password
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters"

        # Hash and save new password
        new_hash = hash_password(new_password)
        with open(AUTH_FILE, 'w') as f:
            f.write(new_hash)

        logger.info("✅ Admin password changed successfully")
        return True, "Password changed successfully"

    except Exception as e:
        logger.error(f"Error changing password: {e}")
        return False, f"Error: {str(e)}"


def delete_first_run_file():
    """Delete the temporary password file after first login."""
    log_file = Path(__file__).parent / "first_run_password.txt"
    if log_file.exists():
        try:
            log_file.unlink()
            logger.info("🗑️  Deleted temporary password file")
        except Exception as e:
            logger.error(f"Error deleting temporary password file: {e}")


def check_auth(password: str) -> bool:
    """Check if provided password is correct.

    Args:
        password: Password to check

    Returns:
        True if password is correct, False otherwise
    """
    password_hash, is_new = get_or_create_password()

    result = verify_password(password, password_hash)

    # Delete temp password file on first successful login
    if result:
        delete_first_run_file()

    return result


def create_session_token() -> str:
    """Create a new session token.

    Returns:
        Secure random session token
    """
    return secrets.token_urlsafe(32)


def save_session(token: str) -> None:
    """Save a session token with expiry.

    Args:
        token: Session token to save
    """
    try:
        # Load existing sessions
        sessions = load_sessions()

        # Add new session with expiry
        expiry = (datetime.now() + SESSION_DURATION).isoformat()
        sessions[token] = expiry

        # Save to file
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSION_FILE, 'w') as f:
            json.dump(sessions, f)
        SESSION_FILE.chmod(0o600)

    except Exception as e:
        logger.error(f"Error saving session: {e}")


def load_sessions() -> dict:
    """Load all valid sessions from file.

    Returns:
        Dictionary of valid session tokens and their expiry times
    """
    if not SESSION_FILE.exists():
        return {}

    try:
        with open(SESSION_FILE, 'r') as f:
            sessions = json.load(f)

        # Filter out expired sessions
        now = datetime.now()
        valid_sessions = {
            token: expiry
            for token, expiry in sessions.items()
            if datetime.fromisoformat(expiry) > now
        }

        # Save cleaned sessions back if any were removed
        if len(valid_sessions) != len(sessions):
            with open(SESSION_FILE, 'w') as f:
                json.dump(valid_sessions, f)

        return valid_sessions

    except Exception as e:
        logger.error(f"Error loading sessions: {e}")
        return {}


def validate_session(token: Optional[str]) -> bool:
    """Check if a session token is valid.

    Args:
        token: Session token to validate

    Returns:
        True if session is valid, False otherwise
    """
    if not token:
        return False

    sessions = load_sessions()
    return token in sessions


def delete_session(token: Optional[str]) -> None:
    """Delete a session token.

    Args:
        token: Session token to delete
    """
    if not token:
        return

    try:
        sessions = load_sessions()
        if token in sessions:
            del sessions[token]

            with open(SESSION_FILE, 'w') as f:
                json.dump(sessions, f)

            logger.info("🔒 Session logged out")

    except Exception as e:
        logger.error(f"Error deleting session: {e}")
