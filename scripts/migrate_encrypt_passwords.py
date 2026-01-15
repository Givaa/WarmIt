#!/usr/bin/env python3
"""
Migration script to encrypt existing passwords in accounts table.

This script:
1. Expands password column size (255 -> 500 chars) to accommodate encrypted data
2. Encrypts all existing plaintext passwords
3. Safe to run multiple times (won't re-encrypt already encrypted passwords)

IMPORTANT: Set ENCRYPTION_KEY environment variable before running!
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from warmit.database import engine
from warmit.services.encryption import encrypt_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate():
    """Encrypt existing passwords in accounts table."""
    logger.info("=" * 80)
    logger.info("🔐 Starting password encryption migration")
    logger.info("=" * 80)

    # Check if encryption key is set
    if not os.getenv("ENCRYPTION_KEY"):
        logger.error("❌ ENCRYPTION_KEY not set in environment!")
        logger.error("⚠️  Please set ENCRYPTION_KEY in your .env file before running migration.")
        logger.error("⚠️  You can generate a key with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
        return

    logger.info(f"✅ ENCRYPTION_KEY found: {os.getenv('ENCRYPTION_KEY')[:20]}...")

    async with engine.begin() as conn:
        # Step 1: Expand password column size
        logger.info("\n📝 Step 1: Expanding password column size...")
        try:
            # Try PostgreSQL syntax first
            await conn.execute(
                text("ALTER TABLE accounts ALTER COLUMN password TYPE VARCHAR(500);")
            )
            logger.info("✅ Column resized (PostgreSQL)")
        except Exception as e:
            # PostgreSQL failed, try SQLite
            logger.info(f"PostgreSQL syntax failed ({e}), trying SQLite approach...")

            # SQLite doesn't support ALTER COLUMN TYPE directly
            # We'll handle this differently - just log warning
            logger.warning("⚠️  SQLite detected - column resize not needed (SQLite is flexible with VARCHAR sizes)")

        # Step 2: Fetch all accounts
        logger.info("\n📊 Step 2: Fetching existing accounts...")
        result = await conn.execute(
            text("SELECT id, email, password FROM accounts;")
        )
        accounts = result.fetchall()

        logger.info(f"📧 Found {len(accounts)} accounts to process")

        if len(accounts) == 0:
            logger.info("✅ No accounts to migrate")
            return

        # Step 3: Encrypt passwords
        logger.info("\n🔐 Step 3: Encrypting passwords...")
        encrypted_count = 0
        skipped_count = 0

        for account_id, email, password in accounts:
            # Check if already encrypted (Fernet ciphertext starts with 'gAAAAA' when base64 encoded)
            if password.startswith('gAAAAA'):
                logger.info(f"  ⏭️  {email}: Already encrypted, skipping")
                skipped_count += 1
                continue

            # Encrypt the password
            encrypted_password = encrypt_password(password)

            # Update in database
            await conn.execute(
                text("UPDATE accounts SET password = :encrypted WHERE id = :id"),
                {"encrypted": encrypted_password, "id": account_id}
            )

            logger.info(f"  ✅ {email}: Password encrypted")
            encrypted_count += 1

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("🎉 Migration completed successfully!")
        logger.info("=" * 80)
        logger.info(f"✅ Encrypted: {encrypted_count} passwords")
        logger.info(f"⏭️  Skipped: {skipped_count} passwords (already encrypted)")
        logger.info(f"📊 Total: {len(accounts)} accounts")
        logger.info("=" * 80)

        if encrypted_count > 0:
            logger.info("\n⚠️  IMPORTANT:")
            logger.info("   - Keep your ENCRYPTION_KEY safe and backed up!")
            logger.info("   - Without the key, encrypted passwords cannot be recovered!")
            logger.info("   - Add ENCRYPTION_KEY to your .env file for production use")


if __name__ == "__main__":
    asyncio.run(migrate())
