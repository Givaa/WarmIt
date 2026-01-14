#!/bin/bash

# WarmIt - One-Click Production Startup Script
# This script starts WarmIt in production mode with all failsafe features

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
ENV_FILE=".env"

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo ""
    echo "Creating .env from example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env and add your API keys!${NC}"
    echo ""
    echo "Required configuration:"
    echo "  - AI_PROVIDER (openrouter or groq)"
    echo "  - OPENROUTER_API_KEY or GROQ_API_KEY"
    echo "  - POSTGRES_PASSWORD (set a strong password)"
    echo ""
    echo "After editing .env, run this script again."
    exit 1
fi

# Check if Docker is running
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

# Check for existing installation
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
    echo "  - Database and Redis data"
    echo ""
    read -p "Are you ABSOLUTELY SURE? Type 'DELETE' to confirm: " -r
    echo
    if [[ $REPLY == "DELETE" ]]; then
        echo "Stopping containers..."
        $DOCKER_COMPOSE -f $COMPOSE_FILE down -v
        echo -e "${GREEN}✅ All data deleted${NC}"
        echo ""
        echo "Run './start.sh' to start fresh"
    else
        echo "Cancelled"
    fi
    exit 0
fi

# Start WarmIt
echo -e "${BLUE}Starting WarmIt in production mode...${NC}"
echo ""
echo "This may take a few minutes on first run (downloading images)"
echo ""

# Pull latest images
echo "Pulling Docker images..."
$DOCKER_COMPOSE -f $COMPOSE_FILE pull

# Build custom images
echo ""
echo "Building WarmIt images..."
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
echo "  📊 Dashboard:  http://localhost:8501"
echo "  🔌 API:        http://localhost:8000"
echo "  📖 API Docs:   http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  View logs:           $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f"
echo "  View API logs:       $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f api"
echo "  View worker logs:    $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f worker"
echo "  Service status:      $DOCKER_COMPOSE -f $COMPOSE_FILE ps"
echo "  Restart:             ./start.sh restart"
echo "  Stop:                ./start.sh stop"
echo "  Remove containers:   ./start.sh down"
echo ""
echo -e "${BLUE}Features:${NC}"
echo "  ✅ Auto-restart on failure"
echo "  ✅ Health checks every 30s"
echo "  ✅ Watchdog monitoring (5min)"
echo "  ✅ Resource limits"
echo "  ✅ Log rotation"
echo "  ✅ Data persistence"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Open dashboard: http://localhost:8501"
echo "  2. Add your email accounts"
echo "  3. Create a warming campaign"
echo "  4. Monitor progress!"
echo ""
echo -e "${GREEN}Happy warming! 🔥${NC}"
