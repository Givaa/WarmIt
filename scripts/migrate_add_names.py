#!/usr/bin/env python3
"""
Migration script to add first_name and last_name fields to accounts table.

This script adds the new fields if they don't already exist.
Safe to run multiple times.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from warmit.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate():
    """Add first_name and last_name columns to accounts table."""
    logger.info("Starting migration: Adding first_name and last_name to accounts")

    async with engine.begin() as conn:
        # Check if columns already exist
        try:
            # Try to add the columns - PostgreSQL
            await conn.execute(
                text(
                    """
                    ALTER TABLE accounts
                    ADD COLUMN IF NOT EXISTS first_name VARCHAR(100),
                    ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);
                    """
                )
            )
            logger.info("✅ Migration completed successfully (PostgreSQL)")
        except Exception as e:
            # If PostgreSQL syntax fails, try SQLite
            logger.info(f"PostgreSQL syntax failed, trying SQLite: {e}")
            try:
                # Check if column exists in SQLite
                result = await conn.execute(text("PRAGMA table_info(accounts);"))
                columns = [row[1] for row in result]

                if "first_name" not in columns:
                    await conn.execute(
                        text("ALTER TABLE accounts ADD COLUMN first_name VARCHAR(100);")
                    )
                    logger.info("✅ Added first_name column")
                else:
                    logger.info("ℹ️  first_name column already exists")

                if "last_name" not in columns:
                    await conn.execute(
                        text("ALTER TABLE accounts ADD COLUMN last_name VARCHAR(100);")
                    )
                    logger.info("✅ Added last_name column")
                else:
                    logger.info("ℹ️  last_name column already exists")

                logger.info("✅ Migration completed successfully (SQLite)")

            except Exception as e2:
                logger.error(f"❌ Migration failed: {e2}")
                raise


if __name__ == "__main__":
    asyncio.run(migrate())
