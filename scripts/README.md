# WarmIt - Scripts

Utility scripts for database migrations, resource estimation, and maintenance.

---

## 📋 Available Scripts

### 🧮 estimate_resources.py
Estimate infrastructure resources needed for email warming campaigns.

**Features:**
- Calculate RAM, CPU, storage requirements
- Estimate API usage and costs
- Generate docker-compose configuration
- Support for different scale profiles

**Usage:**
```bash
# Interactive mode
python scripts/estimate_resources.py

# With parameters
python scripts/estimate_resources.py --senders 50 --receivers 100 --weeks 6

# JSON output for automation
python scripts/estimate_resources.py --senders 50 --receivers 100 --json
```

**Also available in dashboard:** Go to "🧮 Estimate" page

---

### 🔄 migrate_add_names.py
Database migration to add first_name and last_name fields to accounts.

**Purpose:** Add personal name fields to account model for better email personalization

**Usage:**
```bash
# Set DATABASE_URL first
export DATABASE_URL="postgresql+asyncpg://user:pass@host/db"

python scripts/migrate_add_names.py
```

**What it does:**
1. Adds first_name column (VARCHAR 100, nullable)
2. Adds last_name column (VARCHAR 100, nullable)
3. Shows migration status

---

### 🔐 migrate_encrypt_passwords.py
Database migration to encrypt existing plaintext passwords.

**Purpose:** Migrate from plaintext to encrypted password storage using Fernet encryption

**Usage:**
```bash
# Set required environment variables
export DATABASE_URL="postgresql+asyncpg://user:pass@host/db"
export ENCRYPTION_KEY="your-fernet-key"

# Generate encryption key if needed
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

python scripts/migrate_encrypt_passwords.py
```

**What it does:**
1. Expands password column to VARCHAR(500)
2. Encrypts all plaintext passwords
3. Skips already encrypted passwords
4. Shows progress for each account

**Important:** Save your ENCRYPTION_KEY - you can't decrypt without it!

---

## 📂 migrations/
SQL migration scripts for database schema changes.

**Directory:** `scripts/migrations/`

**Purpose:** Version-controlled database migrations

**Available migrations:**
- `001_add_campaign_language.sql` - Adds language field to campaigns table

**Documentation:** See [migrations/README.md](migrations/README.md) for details

**How to apply:**
```bash
# Migrations are auto-applied on container startup
./warmit.sh restart

# Or apply manually
docker compose -f docker/docker-compose.prod.yml exec -T postgres \
  psql -U warmit -d warmit < scripts/migrations/XXX_migration.sql
```

---

### 🐕 watchdog.py
Container health monitoring service (runs inside Docker).

**Purpose:** Monitors health of all WarmIt containers and logs status

**Usage:**
```bash
# Usually run inside Docker container (see docker-compose.prod.yml)
python scripts/watchdog.py
```

**What it monitors:**
- Container running status
- Service health checks
- Automatic restarts
- Log aggregation

---

### 🖥️ cli.py
Command-line interface for WarmIt operations.

**Purpose:** CLI tool for managing WarmIt without dashboard

**Usage:**
```bash
python scripts/cli.py --help
```

---


## 🛠️ Manual Alternatives

Some scripts have been removed for simplicity. Here's how to do those tasks manually:

### Check Docker Space
**Old script:** `check-docker-space.sh`

**Manual alternative:**
```bash
# Show disk usage
docker system df

# Detailed breakdown
docker system df -v
```

---

### Cleanup Docker
**Old script:** `cleanup-docker.sh`

**Manual alternative:**
```bash
# Remove unused containers, networks, images (dangling)
docker system prune

# Remove ALL unused images (not just dangling)
docker system prune -a

# Remove volumes too (⚠️ WARNING: deletes data)
docker system prune -a --volumes

# Remove specific items
docker container prune   # Remove stopped containers
docker image prune -a    # Remove unused images
docker volume prune      # Remove unused volumes
docker network prune     # Remove unused networks
```

---

### Debug Container
**Old script:** `debug-container.sh`

**Manual alternative:**
```bash
# View logs
docker logs <container-name>
docker logs -f <container-name>              # Follow logs
docker logs --tail 100 <container-name>      # Last 100 lines

# Execute commands inside container
docker exec -it <container-name> bash        # Interactive shell
docker exec <container-name> ls -la /app     # List files
docker exec <container-name> env             # View environment variables
docker exec <container-name> ps aux          # Running processes

# Inspect container
docker inspect <container-name>              # Full container details
docker stats <container-name>                # Resource usage
docker top <container-name>                  # Running processes

# Copy files from container
docker cp <container-name>:/path/to/file ./local/path

# Check container status
docker ps                                    # Running containers
docker ps -a                                 # All containers (including stopped)
```

**Example debugging session:**
```bash
# 1. Check if container is running
docker ps | grep warmit-api

# 2. View recent logs
docker logs --tail 50 warmit-api

# 3. Check directory structure
docker exec warmit-api ls -la /app/src

# 4. Check Python can import modules
docker exec warmit-api python -c "import warmit; print('OK')"

# 5. Interactive debugging
docker exec -it warmit-api bash
cd /app
python
>>> import warmit
>>> # Test your code
```

---

### Development Mode
**Old script:** `run_dev.sh`

**Manual alternative:**
```bash
# Use the main warmit.sh script instead
./warmit.sh start

# Or run services manually
cd docker
docker-compose -f docker-compose.prod.yml up -d
```

---

### Setup
**Old script:** `setup.sh`

**Manual alternative:**
```bash
# 1. Copy environment file
cp .env.example docker/.env

# 2. Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 3. Edit docker/.env with your settings
nano docker/.env  # or vim, code, etc.

# 4. Start services
./warmit.sh start

# 5. Get admin password
docker logs warmit-dashboard | grep "Admin Password"
```

---

### Check Requirements
**Old script:** `check_requirements.sh`

**Manual alternative:**
Docker automatically handles dependencies via pyproject.toml and Dockerfile. If you need to check manually:

```bash
# Check installed packages in container
docker exec warmit-api pip list

# Check for outdated packages
docker exec warmit-api pip list --outdated

# Verify specific package
docker exec warmit-api pip show fastapi
```

---

### Fix Redis Warning
**Old script:** `fix-redis-warning.sh`

**Manual alternative:**
This was for a specific Redis warning. If you see Redis warnings in logs:

```bash
# Check Redis logs
docker logs warmit-redis

# Common fixes:
# 1. Increase memory limit in docker-compose.prod.yml:
#    redis:
#      mem_limit: 512m

# 2. Set Redis maxmemory policy:
docker exec warmit-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## 📝 Notes

**Running scripts:**
- Most scripts should be run from the project root directory
- Python scripts require proper environment variables (DATABASE_URL, ENCRYPTION_KEY, etc.)
- Migration scripts are one-time operations
- Always backup your database before running migrations

**Environment setup:**
```bash
# Load environment from docker/.env
export $(cat docker/.env | grep -v '^#' | xargs)

# Or set manually
export DATABASE_URL="postgresql+asyncpg://warmit:password@localhost:5432/warmit"
export ENCRYPTION_KEY="your-fernet-key"
```

**Best practices:**
- Use `./warmit.sh` for starting/stopping services (not individual scripts)
- Use dashboard for resource estimation (more user-friendly than CLI)
- Keep ENCRYPTION_KEY backed up securely
- Run migrations in a test environment first
- Monitor logs after running maintenance scripts

---

**Last Updated:** 2026-01-15
**WarmIt Version:** 0.2.1-dev (Multilingual Support)
