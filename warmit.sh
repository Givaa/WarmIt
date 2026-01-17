#!/bin/bash

# WarmIt - One-Click Production Startup Script
# This script starts WarmIt in production mode with all failsafe features
#
# Developed with ❤️ by Givaa
# https://github.com/Givaa

set -e

echo "🔥🔥🔥 WarmIt Production Startup 🔥🔥🔥"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker/docker-compose.prod.yml"
ENV_FILE="docker/.env"
ENV_EXAMPLE=".env.example"

# Cross-platform function to get env value (works on Windows/Git Bash, macOS, Linux)
# Usage: get_env_value "VAR_NAME" "/path/to/file"
get_env_value() {
    local var_name="$1"
    local file="$2"
    local value=""
    if grep -q "^${var_name}=" "$file" 2>/dev/null; then
        value=$(grep "^${var_name}=" "$file" | head -1)
        value="${value#*=}"           # Remove everything before =
        value="${value%%#*}"          # Remove comments
        value="${value//[[:space:]]/}" # Remove whitespace
        value="${value//\"/}"         # Remove double quotes
        value="${value//\'/}"         # Remove single quotes
    fi
    echo "$value"
}

# Check if Docker is running (needed for all commands)
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    echo ""
    echo "Please start Docker and try again:"
    echo "  - macOS: Open Docker Desktop"
    echo "  - Linux: sudo systemctl start docker"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Check if docker-compose or docker compose is available
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo -e "${RED}❌ Error: docker-compose not found${NC}"
    echo ""
    echo "Please install docker-compose:"
    echo "  https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ docker-compose found${NC}"
echo ""

# Show help menu
show_help() {
    echo "🔥 WarmIt - Production Startup Script"
    echo ""
    echo "Usage: ./warmit.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  (no command)    Start WarmIt in production mode (default)"
    echo "  start           Start WarmIt in production mode"
    echo "  restart         Restart all services"
    echo "  stop            Stop all services (keep containers)"
    echo "  down            Stop and remove all containers (keep data)"
    echo "  reset           Delete EVERYTHING (containers, volumes, data)"
    echo "  status          Show service status"
    echo "  logs [service]  Show logs (api, worker, dashboard, postgres, redis)"
    echo "  db-shell        Open PostgreSQL interactive shell"
    echo "  health          Check API health status"
    echo "  password        Get/generate admin password"
    echo "  help            Show this help menu"
    echo ""
    echo "Examples:"
    echo "  ./warmit.sh              # Start services"
    echo "  ./warmit.sh restart      # Restart services"
    echo "  ./warmit.sh stop         # Stop services"
    echo "  ./warmit.sh logs api     # View API logs"
    echo "  ./warmit.sh db-shell     # Open database shell"
    echo "  ./warmit.sh reset        # Delete all data (use with caution!)"
    echo ""
    echo "Access URLs (after starting):"
    echo "  Dashboard:  http://localhost (via Nginx)"
    echo "  Logs:       http://localhost:8888 (localhost only)"
    echo "  API:        Internal only (not exposed)"
    echo "  Tracking:   http://localhost/track/* (signed URLs only)"
    echo ""
    echo "Made with  by Givaa - https://github.com/Givaa"
}

# Handle help command
if [ "$1" == "help" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
    exit 0
fi

# Handle commands that don't need .env validation
if [ "$1" == "restart" ]; then
    echo -e "${BLUE}Restarting WarmIt...${NC}"
    $DOCKER_COMPOSE -f $COMPOSE_FILE restart
    echo ""
    echo -e "${GREEN}✅ WarmIt restarted!${NC}"
    exit 0
fi

if [ "$1" == "status" ]; then
    echo -e "${BLUE}WarmIt Service Status:${NC}"
    echo ""
    $DOCKER_COMPOSE -f $COMPOSE_FILE ps
    exit 0
fi

if [ "$1" == "logs" ]; then
    SERVICE="$2"
    if [ -z "$SERVICE" ]; then
        echo -e "${BLUE}Showing all logs (Ctrl+C to exit)...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f --tail=100
    else
        echo -e "${BLUE}Showing $SERVICE logs (Ctrl+C to exit)...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f --tail=100 "$SERVICE"
    fi
    exit 0
fi

if [ "$1" == "db-shell" ]; then
    echo -e "${BLUE}Opening PostgreSQL shell...${NC}"
    echo -e "${YELLOW}Useful commands:${NC}"
    echo "  \\dt                    - List all tables"
    echo "  \\d accounts            - Describe accounts table"
    echo "  SELECT * FROM accounts; - View all accounts"
    echo "  \\q                     - Quit"
    echo ""
    docker exec -it warmit-postgres psql -U warmit -d warmit
    exit 0
fi

if [ "$1" == "password" ]; then
    echo -e "${BLUE}Getting admin password...${NC}"
    echo ""
    # Check if dashboard container is running
    if ! docker ps --format '{{.Names}}' | grep -q warmit-dashboard; then
        echo -e "${RED}❌ Dashboard container is not running${NC}"
        echo "Start WarmIt first: ./warmit.sh start"
        exit 1
    fi
    # Generate/get password
    docker exec warmit-dashboard python3 -c "
import sys
sys.path.insert(0, '/app')
from dashboard.auth import get_or_create_password
hash, is_new = get_or_create_password()
if not is_new:
    print()
    print('=' * 60)
    print('Password already set. To reset:')
    print('  1. docker exec warmit-dashboard rm /app/dashboard/.auth')
    print('  2. ./warmit.sh password')
    print('=' * 60)
"
    exit 0
fi

if [ "$1" == "health" ]; then
    echo -e "${BLUE}Checking WarmIt health...${NC}"
    echo ""

    # Check if Nginx is responding (public entry point)
    if curl -f -s http://localhost/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Nginx (public gateway) is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Nginx not responding on port 80${NC}"
    fi

    # Check internal API health via docker exec
    if docker exec warmit-api curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API is healthy${NC}"
        echo ""
        echo "Detailed health:"
        docker exec warmit-api curl -s http://localhost:8000/health/detailed 2>/dev/null | python3 -m json.tool 2>/dev/null || docker exec warmit-api curl -s http://localhost:8000/health/detailed
    else
        echo -e "${RED}❌ API is not responding${NC}"
        echo ""
        echo "Check if services are running: ./warmit.sh status"
    fi
    exit 0
fi

if [ "$1" == "stop" ]; then
    echo -e "${YELLOW}Stopping WarmIt...${NC}"
    $DOCKER_COMPOSE -f $COMPOSE_FILE stop
    echo ""
    echo -e "${GREEN}✅ WarmIt stopped${NC}"
    exit 0
fi

if [ "$1" == "down" ]; then
    echo -e "${RED}Stopping and removing all containers...${NC}"
    read -p "Are you sure? This will remove all containers but keep data (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $DOCKER_COMPOSE -f $COMPOSE_FILE down
        echo -e "${GREEN}✅ Containers removed${NC}"
    fi
    exit 0
fi

if [ "$1" == "reset" ]; then
    echo -e "${RED}⚠️  DANGER: This will DELETE ALL DATA!${NC}"
    echo "This includes:"
    echo "  - All email accounts"
    echo "  - All campaigns"
    echo "  - All metrics and history"
    echo "  - Database and Redis data (including volumes)"
    echo "  - All Docker containers and networks"
    echo ""
    read -p "Are you ABSOLUTELY SURE? Type 'DELETE' to confirm: " -r
    echo
    if [[ $REPLY == "DELETE" ]]; then
        echo "Stopping and removing containers..."
        $DOCKER_COMPOSE -f $COMPOSE_FILE down -v

        echo ""
        echo -e "${GREEN}✅ All data deleted (containers, volumes, networks)${NC}"
        echo ""
        echo "To start fresh, run: ./warmit.sh"
    else
        echo "Cancelled"
    fi
    exit 0
fi

# Handle explicit start command (same as default/no command)
if [ "$1" == "start" ]; then
    # Just continue to the normal startup flow
    echo -e "${BLUE}Starting WarmIt...${NC}"
    echo ""
fi

# Show error for unknown commands
if [ -n "$1" ] && [ "$1" != "start" ]; then
    echo -e "${RED}❌ Error: Unknown command '$1'${NC}"
    echo ""
    show_help
    exit 1
fi

# For start command (default), validate .env and API keys
# Check if .env exists in docker/ directory
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: docker/.env file not found${NC}"
    echo ""

    # Check if we have .env.example
    if [ -f "$ENV_EXAMPLE" ]; then
        echo "Creating docker/.env from .env.example..."
        cp "$ENV_EXAMPLE" "$ENV_FILE"

        # Update for production (cross-platform without sed -i)
        TEMP_FILE="${ENV_FILE}.tmp"
        while IFS= read -r line || [ -n "$line" ]; do
            # Replace SQLite with PostgreSQL
            if [[ "$line" == *"sqlite+aiosqlite:///./warmit.db"* ]]; then
                line="${line//sqlite+aiosqlite:\/\/.\\/warmit.db/postgresql+asyncpg:\/\/warmit:warmit_secure_password_2026@postgres:5432\/warmit}"
            fi
            # Replace localhost Redis with Docker Redis
            if [[ "$line" == *"redis://localhost:6379/0"* ]]; then
                line="${line//redis:\/\/localhost:6379\/0/redis:\/\/redis:6379\/0}"
            fi
            # Set DEBUG to false
            if [[ "$line" == "DEBUG=true" ]]; then
                line="DEBUG=false"
            fi
            # Set POSTGRES_PASSWORD
            if [[ "$line" == POSTGRES_PASSWORD=* ]]; then
                line="POSTGRES_PASSWORD=warmit_secure_password_2026"
            fi
            echo "$line"
        done < "$ENV_FILE" > "$TEMP_FILE"
        mv "$TEMP_FILE" "$ENV_FILE"

        echo -e "${GREEN}✅ Created docker/.env${NC}"
    else
        echo -e "${RED}❌ Error: .env.example not found${NC}"
        exit 1
    fi

    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Please edit docker/.env and add your API keys!${NC}"
    echo ""
    echo "Required configuration:"
    echo "  1. Generate encryption key:"
    echo "     python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    echo "  2. Add ENCRYPTION_KEY to docker/.env"
    echo "  3. Choose AI provider: AI_PROVIDER (openrouter or groq)"
    echo "  4. Add API keys (supports multiple for failover):"
    echo "     OPENROUTER_API_KEY=sk-or-v1-xxxxx"
    echo "     OPENROUTER_API_KEY_2=sk-or-v1-xxxxx  # Optional"
    echo "     OPENROUTER_API_KEY_3=sk-or-v1-xxxxx  # Optional"
    echo "     GROQ_API_KEY=gsk_xxxxx"
    echo "     GROQ_API_KEY_2=gsk_xxxxx  # Optional"
    echo "  5. Set secure password: POSTGRES_PASSWORD=your_secure_password"
    echo ""
    echo "Edit with: nano docker/.env"
    echo ""
    read -p "Press Enter after editing docker/.env, or Ctrl+C to exit..."
else
    # docker/.env exists - check if it needs updating for v0.2.0
    if ! grep -q "OPENROUTER_API_KEY_2" "$ENV_FILE"; then
        echo -e "${YELLOW}⚠️  Updating docker/.env with new v0.2.0 configuration...${NC}"
        
        # Backup old .env
        cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        
        # Add missing keys (comments on separate lines to avoid parsing issues)
        if ! grep -q "OPENROUTER_API_KEY_2" "$ENV_FILE"; then
            echo "" >> "$ENV_FILE"
            echo "# Multiple API keys for fallback (v0.2.0+)" >> "$ENV_FILE"
            echo "# Optional: Add additional API keys for automatic failover" >> "$ENV_FILE"
            echo "OPENROUTER_API_KEY_2=" >> "$ENV_FILE"
            echo "OPENROUTER_API_KEY_3=" >> "$ENV_FILE"
            echo "GROQ_API_KEY_2=" >> "$ENV_FILE"
        fi

        if ! grep -q "ENCRYPTION_KEY" "$ENV_FILE"; then
            echo "" >> "$ENV_FILE"
            echo "# Security - Encryption Key for sensitive data (v0.2.0+)" >> "$ENV_FILE"
            echo "# Generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"" >> "$ENV_FILE"
            echo "ENCRYPTION_KEY=" >> "$ENV_FILE"
        fi
        
        echo -e "${GREEN}✅ docker/.env updated! Backup saved.${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  IMPORTANT: Generate and add ENCRYPTION_KEY to docker/.env!${NC}"
        echo "Run: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        echo ""
        read -p "Press Enter after adding ENCRYPTION_KEY, or Ctrl+C to exit..."
    fi
fi

# Verify ENCRYPTION_KEY is configured (CRITICAL for data security)
# Extract value after = and trim whitespace (cross-platform compatible)
ENCRYPTION_KEY=""
if grep -q "^ENCRYPTION_KEY=" "$ENV_FILE" 2>/dev/null; then
    # Get the line, extract after =, remove quotes and whitespace
    ENCRYPTION_KEY=$(grep "^ENCRYPTION_KEY=" "$ENV_FILE" | head -1)
    ENCRYPTION_KEY="${ENCRYPTION_KEY#*=}"  # Remove everything before =
    ENCRYPTION_KEY="${ENCRYPTION_KEY%%#*}"  # Remove comments
    ENCRYPTION_KEY="${ENCRYPTION_KEY//[[:space:]]/}"  # Remove whitespace
    ENCRYPTION_KEY="${ENCRYPTION_KEY//\"/}"  # Remove double quotes
    ENCRYPTION_KEY="${ENCRYPTION_KEY//\'/}"  # Remove single quotes
fi

# Check if key is empty or placeholder
if [ -z "$ENCRYPTION_KEY" ] || [ "$ENCRYPTION_KEY" = "your_encryption_key_here" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  ENCRYPTION_KEY not configured - generating one now...${NC}"
    echo ""

    # Generate encryption key using Docker with pip install
    echo "Generating secure encryption key using Docker..."
    GENERATED_KEY=$(docker run --rm python:3.11-slim bash -c "pip install -q cryptography && python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"" 2>/dev/null)

    if [ -z "$GENERATED_KEY" ]; then
        echo -e "${RED}❌ Failed to generate encryption key with Docker${NC}"
        echo ""
        echo "Trying alternative method (OpenSSL)..."

        # Fallback: Generate a base64-encoded 32-byte key using OpenSSL (compatible with Fernet)
        GENERATED_KEY=$(openssl rand -base64 32 2>/dev/null)

        if [ -z "$GENERATED_KEY" ]; then
            echo -e "${RED}❌ Failed to generate encryption key${NC}"
            echo ""
            echo "Please add ENCRYPTION_KEY manually to docker/.env"
            echo "You can generate one at: https://fernet-generator.fly.dev/"
            echo "Or run: docker run --rm python:3.11-slim bash -c 'pip install cryptography && python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"'"
            exit 1
        fi
    fi

    # Update or add ENCRYPTION_KEY in .env file (cross-platform without sed -i)
    if grep -q "^ENCRYPTION_KEY=" "$ENV_FILE"; then
        # Create temp file, replace the line, then move back
        TEMP_FILE="${ENV_FILE}.tmp"
        while IFS= read -r line || [ -n "$line" ]; do
            if [[ "$line" == ENCRYPTION_KEY=* ]]; then
                echo "ENCRYPTION_KEY=$GENERATED_KEY"
            else
                echo "$line"
            fi
        done < "$ENV_FILE" > "$TEMP_FILE"
        mv "$TEMP_FILE" "$ENV_FILE"
    else
        # Add new ENCRYPTION_KEY
        echo "" >> "$ENV_FILE"
        echo "# Auto-generated encryption key (DO NOT CHANGE OR LOSE THIS!)" >> "$ENV_FILE"
        echo "ENCRYPTION_KEY=$GENERATED_KEY" >> "$ENV_FILE"
    fi

    echo ""
    echo -e "${GREEN}✅ Encryption key generated and saved to docker/.env${NC}"
    echo ""
    echo -e "${YELLOW}Your encryption key: $GENERATED_KEY${NC}"
    echo ""
    echo -e "${RED}IMPORTANT: This key is now saved in docker/.env${NC}"
    echo -e "${RED}DO NOT LOSE THIS KEY or you won't be able to decrypt your passwords!${NC}"
    echo -e "${RED}DO NOT CHANGE THIS KEY or existing passwords will become unreadable!${NC}"
    echo ""
    read -p "Press Enter to continue..."
else
    echo -e "${GREEN}✅ Encryption key configured${NC}"
fi

# Verify TRACKING_SECRET_KEY is configured (for secure email tracking)
TRACKING_SECRET_KEY=""
if grep -q "^TRACKING_SECRET_KEY=" "$ENV_FILE" 2>/dev/null; then
    TRACKING_SECRET_KEY=$(grep "^TRACKING_SECRET_KEY=" "$ENV_FILE" | head -1)
    TRACKING_SECRET_KEY="${TRACKING_SECRET_KEY#*=}"
    TRACKING_SECRET_KEY="${TRACKING_SECRET_KEY%%#*}"
    TRACKING_SECRET_KEY="${TRACKING_SECRET_KEY//[[:space:]]/}"
    TRACKING_SECRET_KEY="${TRACKING_SECRET_KEY//\"/}"
    TRACKING_SECRET_KEY="${TRACKING_SECRET_KEY//\'/}"
fi

if [ -z "$TRACKING_SECRET_KEY" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  TRACKING_SECRET_KEY not configured - generating one now...${NC}"
    echo ""

    # Generate tracking secret key using OpenSSL (cross-platform)
    echo "Generating secure tracking secret key..."
    GENERATED_TRACKING_KEY=$(openssl rand -hex 32 2>/dev/null)

    if [ -z "$GENERATED_TRACKING_KEY" ]; then
        # Fallback: use /dev/urandom on Unix or PowerShell on Windows
        if [ -f /dev/urandom ]; then
            GENERATED_TRACKING_KEY=$(head -c 32 /dev/urandom | xxd -p | tr -d '\n' 2>/dev/null)
        fi
    fi

    if [ -z "$GENERATED_TRACKING_KEY" ]; then
        echo -e "${YELLOW}⚠️  Could not auto-generate tracking key${NC}"
        echo "Please add TRACKING_SECRET_KEY manually to docker/.env"
        echo "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
    else
        # Add TRACKING_SECRET_KEY to .env file
        if grep -q "^TRACKING_SECRET_KEY=" "$ENV_FILE"; then
            # Update existing line
            TEMP_FILE="${ENV_FILE}.tmp"
            while IFS= read -r line || [ -n "$line" ]; do
                if [[ "$line" == TRACKING_SECRET_KEY=* ]]; then
                    echo "TRACKING_SECRET_KEY=$GENERATED_TRACKING_KEY"
                else
                    echo "$line"
                fi
            done < "$ENV_FILE" > "$TEMP_FILE"
            mv "$TEMP_FILE" "$ENV_FILE"
        else
            # Add new line
            echo "" >> "$ENV_FILE"
            echo "# Auto-generated tracking secret key for secure email tracking (v1.0.2+)" >> "$ENV_FILE"
            echo "TRACKING_SECRET_KEY=$GENERATED_TRACKING_KEY" >> "$ENV_FILE"
        fi

        echo ""
        echo -e "${GREEN}✅ Tracking secret key generated and saved to docker/.env${NC}"
        echo ""
        echo -e "${YELLOW}Your tracking secret key: $GENERATED_TRACKING_KEY${NC}"
        echo ""
    fi
else
    echo -e "${GREEN}✅ Tracking secret key configured${NC}"
fi

# Verify API key is configured
AI_PROVIDER=$(get_env_value "AI_PROVIDER" "$ENV_FILE")

if [ "$AI_PROVIDER" = "openrouter" ]; then
    # Check OpenRouter key
    OPENROUTER_KEY=$(get_env_value "OPENROUTER_API_KEY" "$ENV_FILE")
    if [ -z "$OPENROUTER_KEY" ] || echo "$OPENROUTER_KEY" | grep -q "your_openrouter_key_here"; then
        echo ""
        echo -e "${YELLOW}⚠️  Warning: OpenRouter API key not configured${NC}"
        echo "Please add your OpenRouter API key in docker/.env:"
        echo "  OPENROUTER_API_KEY=sk-or-v1-xxxxx"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
elif [ "$AI_PROVIDER" = "groq" ]; then
    # Check Groq key
    GROQ_KEY=$(get_env_value "GROQ_API_KEY" "$ENV_FILE")
    if [ -z "$GROQ_KEY" ] || echo "$GROQ_KEY" | grep -q "your_groq_key_here"; then
        echo ""
        echo -e "${YELLOW}⚠️  Warning: Groq API key not configured${NC}"
        echo "Please add your Groq API key in docker/.env:"
        echo "  GROQ_API_KEY=gsk_xxxxx"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo ""
    echo -e "${YELLOW}⚠️  Warning: AI_PROVIDER not set or invalid${NC}"
    echo "Please set AI_PROVIDER in docker/.env to 'openrouter' or 'groq'"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✅ Configuration file found${NC}"
echo ""

# Start WarmIt
echo -e "${BLUE}Starting WarmIt...${NC}"
echo ""
echo "This may take a few minutes on first run (downloading images)"
echo ""

# Pull base images (redis, postgres, dozzle)
echo "Pulling base images (Redis, PostgreSQL, Dozzle)..."
$DOCKER_COMPOSE -f $COMPOSE_FILE pull redis postgres logs 2>&1 | grep -v "Pulling" | head -5 || true

# Build custom images
echo ""
echo "Building WarmIt custom images (API, Worker, Dashboard)..."
echo "This may take 2-5 minutes depending on your system..."
$DOCKER_COMPOSE -f $COMPOSE_FILE build

# Start services
echo ""
echo "Starting services..."
$DOCKER_COMPOSE -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be ready..."
sleep 5

# Check service status
echo ""
echo -e "${BLUE}Service Status:${NC}"
$DOCKER_COMPOSE -f $COMPOSE_FILE ps

# Wait for Nginx (gateway) to be healthy
echo ""
echo "Waiting for services to be healthy..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    # Check Nginx (public gateway) - dashboard accessible
    if curl -f -s http://localhost/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Nginx gateway is healthy!${NC}"
        break
    fi
    echo -n "."
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Nginx not ready yet, checking internal API...${NC}"

    # Try internal API check
    if docker exec warmit-api curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API is healthy (Nginx may still be starting)${NC}"
    else
        echo -e "${RED}❌ Services failed to start. Check logs:${NC}"
        echo "  $DOCKER_COMPOSE -f $COMPOSE_FILE logs api"
        echo "  $DOCKER_COMPOSE -f $COMPOSE_FILE logs nginx"
        exit 1
    fi
fi

# Success!
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 WarmIt is now running! 🎉${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo "  📊 Dashboard:  http://localhost (via Nginx on port 80)"
echo "  📝 Logs:       http://localhost:8888 (localhost only - use SSH tunnel remotely)"
echo "  🔒 API:        Internal only (not publicly exposed)"
echo "  📧 Tracking:   http://localhost/track/* (HMAC signed URLs)"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  Service status:      $DOCKER_COMPOSE -f $COMPOSE_FILE ps"
echo "  Restart:             ./warmit.sh restart"
echo "  Stop:                ./warmit.sh stop"
echo "  Remove containers:   ./warmit.sh down"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Get admin password: docker logs warmit-dashboard | grep Password"
echo "  2. Open dashboard: http://localhost"
echo "  3. Login with generated password"
echo "  4. Add your email accounts"
echo "  5. Create a warming campaign"
echo "  6. Monitor progress!"
echo ""
echo -e "${GREEN}Happy warming! 🔥${NC}"
echo ""
echo -e "\033[2mMade with ❤️  by Givaa\033[0m"
