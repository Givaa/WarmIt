# Database Migrations

This directory contains SQL migration scripts for WarmIt database schema changes.

## Migration Files

### 001_add_campaign_language.sql
**Date:** 2026-01-15
**Version:** v0.2.1
**Description:** Adds `language` column to `campaigns` table for multilingual email support

**Changes:**
- Adds `language VARCHAR(10) NOT NULL DEFAULT 'en'` column
- Supports "en" (English) and "it" (Italian)
- Automatically applied on container startup

**How to apply manually:**
```bash
docker compose -f docker/docker-compose.prod.yml exec -T postgres psql -U warmit -d warmit < scripts/migrations/001_add_campaign_language.sql
```

---

## Migration Guidelines

### Creating a New Migration

1. **Naming Convention:**
   ```
   XXX_descriptive_name.sql
   ```
   - `XXX` = sequential number (001, 002, 003, etc.)
   - Use underscores for spaces
   - Keep it concise but descriptive

2. **File Structure:**
   ```sql
   -- Migration: Brief title
   -- Created: YYYY-MM-DD
   -- Description: What this migration does

   -- Your SQL commands here
   ALTER TABLE ...;

   -- Add comments for documentation
   COMMENT ON COLUMN table.column IS 'Description';
   ```

3. **Best Practices:**
   - Always use `IF NOT EXISTS` or `IF EXISTS` when possible
   - Add comments to document changes
   - Use default values when adding NOT NULL columns
   - Test migrations on a copy of production data first
   - Keep migrations idempotent (safe to run multiple times)

### Applying Migrations

**Automatic (Recommended):**
- Migrations are automatically applied when services restart
- The database initialization process runs `create_all()` which updates schema

**Manual Application:**
```bash
# Apply a specific migration
docker compose -f docker/docker-compose.prod.yml exec -T postgres \
  psql -U warmit -d warmit < scripts/migrations/XXX_migration_name.sql

# Or use psql interactively
docker compose -f docker/docker-compose.prod.yml exec postgres \
  psql -U warmit -d warmit
```

### Rollback Strategy

Currently, WarmIt does not use a formal migration framework like Alembic. To rollback a migration:

1. **Create a reverse migration:**
   ```sql
   -- Migration: Rollback XXX_migration_name
   -- Created: YYYY-MM-DD
   -- Description: Reverses changes from migration XXX

   ALTER TABLE campaigns DROP COLUMN IF EXISTS language;
   ```

2. **Apply the rollback:**
   ```bash
   docker compose -f docker/docker-compose.prod.yml exec -T postgres \
     psql -U warmit -d warmit < scripts/migrations/XXX_rollback.sql
   ```

---

## Migration History

| ID | Name | Date | Description |
|----|------|------|-------------|
| 001 | add_campaign_language | 2026-01-15 | Add language support for campaigns (EN/IT) |
| 002 | add_next_send_time | 2026-01-16 | Add scheduling fields for random email timing |

---

## Future Improvements

For production systems with frequent schema changes, consider:
- Implementing Alembic for version-controlled migrations
- Adding migration status tracking table
- Automated migration testing
- Migration rollback automation

---

**Last Updated:** 2026-01-15
