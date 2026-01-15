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

# Handle commands that don't need .env validation
if [ "$1" == "restart" ]; then
    echo -e "${BLUE}Restarting WarmIt...${NC}"
    $DOCKER_COMPOSE -f $COMPOSE_FILE restart
    echo ""
    echo -e "${GREEN}✅ WarmIt restarted!${NC}"
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

# For start command (default), validate .env and API keys
# Check if .env exists in docker/ directory
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: docker/.env file not found${NC}"
    echo ""

    # Check if we have .env.example
    if [ -f "$ENV_EXAMPLE" ]; then
        echo "Creating docker/.env from .env.example..."
        cp "$ENV_EXAMPLE" "$ENV_FILE"

        # Update for production
        sed -i.bak 's|sqlite+aiosqlite:///./warmit.db|postgresql+asyncpg://warmit:warmit_secure_password_2026@postgres:5432/warmit|g' "$ENV_FILE"
        sed -i.bak 's|redis://localhost:6379/0|redis://redis:6379/0|g' "$ENV_FILE"
        sed -i.bak 's|DEBUG=true|DEBUG=false|g' "$ENV_FILE"
        # Ensure POSTGRES_PASSWORD matches DATABASE_URL
        sed -i.bak 's|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=warmit_secure_password_2026|g' "$ENV_FILE"
        rm -f "${ENV_FILE}.bak"

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
        
        # Add missing keys
        if ! grep -q "OPENROUTER_API_KEY_2" "$ENV_FILE"; then
            echo "" >> "$ENV_FILE"
            echo "# Multiple API keys for fallback (v0.2.0+)" >> "$ENV_FILE"
            echo "OPENROUTER_API_KEY_2=  # Optional: 2nd OpenRouter key for fallback" >> "$ENV_FILE"
            echo "OPENROUTER_API_KEY_3=  # Optional: 3rd OpenRouter key for fallback" >> "$ENV_FILE"
            echo "GROQ_API_KEY_2=  # Optional: 2nd Groq key for fallback" >> "$ENV_FILE"
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
ENCRYPTION_KEY=$(grep "^ENCRYPTION_KEY=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' "'"'"'' | sed 's/#.*//')

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

    # Add to .env file
    echo "" >> "$ENV_FILE"
    echo "# Auto-generated encryption key (DO NOT CHANGE OR LOSE THIS!)" >> "$ENV_FILE"
    echo "ENCRYPTION_KEY=$GENERATED_KEY" >> "$ENV_FILE"

    echo ""
    echo -e "${GREEN}✅ Encryption key generated and saved to docker/.env${NC}"
    echo ""
    echo -e "${YELLOW}🔑 Your encryption key: $GENERATED_KEY${NC}"
    echo ""
    echo -e "${RED}⚠️  IMPORTANT: This key is now saved in docker/.env${NC}"
    echo -e "${RED}⚠️  DO NOT LOSE THIS KEY or you won't be able to decrypt your passwords!${NC}"
    echo -e "${RED}⚠️  DO NOT CHANGE THIS KEY or existing passwords will become unreadable!${NC}"
    echo ""
    read -p "Press Enter to continue..."
else
    echo -e "${GREEN}✅ Encryption key configured${NC}"
fi

# Verify API key is configured
AI_PROVIDER=$(grep "^AI_PROVIDER=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' "'"'"'' | sed 's/#.*//')

if [ "$AI_PROVIDER" = "openrouter" ]; then
    # Check OpenRouter key
    OPENROUTER_KEY=$(grep "^OPENROUTER_API_KEY=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' "'"'"'' | sed 's/#.*//')
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
    GROQ_KEY=$(grep "^GROQ_API_KEY=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d ' "'"'"'' | sed 's/#.*//')
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

# Wait for API to be healthy
echo ""
echo "Waiting for API to be healthy..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API is healthy!${NC}"
        break
    fi
    echo -n "."
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo ""
    echo -e "${RED}❌ API failed to start. Check logs:${NC}"
    echo "  $DOCKER_COMPOSE -f $COMPOSE_FILE logs api"
    exit 1
fi

# Success!
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 WarmIt is now running! 🎉${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo "  📊 Dashboard:  http://0.0.0.0:8501"
echo "  📝 Logs (Web): http://localhost:8888"
echo "  🔌 API:        http://localhost:8000"
echo "  📖 API Docs:   http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  Service status:      $DOCKER_COMPOSE -f $COMPOSE_FILE ps"
echo "  Restart:             ./warmit.sh restart"
echo "  Stop:                ./warmit.sh stop"
echo "  Remove containers:   ./warmit.sh down"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Open dashboard: http://localhost:8501"
echo "  2. Add your email accounts"
echo "  3. Create a warming campaign"
echo "  4. Monitor progress!"
echo ""
echo -e "${GREEN}Happy warming! 🔥${NC}"
echo ""
