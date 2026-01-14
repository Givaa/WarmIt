#!/bin/bash
# Safe Docker cleanup script for WarmIt

set -e

echo "======================================"
echo "🧹 WarmIt Docker Cleanup"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Check disk space before
echo "💽 Disk space BEFORE cleanup:"
df -h / | awk 'NR==1 || /\/$/'
echo ""

DOCKER_BEFORE=$(docker system df | grep "Total" | awk '{print $4}')
echo "🐋 Docker space usage BEFORE: $DOCKER_BEFORE"
echo ""

echo "======================================"
echo "Step 1: Stop and remove WarmIt containers"
echo "======================================"
cd "$PROJECT_ROOT/docker"
docker compose down
echo -e "${GREEN}✅ Containers stopped and removed${NC}"
echo ""

echo "======================================"
echo "Step 2: Remove dangling images"
echo "======================================"
DANGLING=$(docker images -f "dangling=true" -q | wc -l | xargs)
if [ "$DANGLING" -gt 0 ]; then
    docker image prune -f
    echo -e "${GREEN}✅ Removed $DANGLING dangling images${NC}"
else
    echo -e "${YELLOW}ℹ️  No dangling images to remove${NC}"
fi
echo ""

echo "======================================"
echo "Step 3: Remove old WarmIt images"
echo "======================================"
WARMIT_IMAGES=$(docker images | grep warmit | wc -l | xargs)
if [ "$WARMIT_IMAGES" -gt 0 ]; then
    docker images | grep warmit | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || true
    echo -e "${GREEN}✅ Removed WarmIt images${NC}"
else
    echo -e "${YELLOW}ℹ️  No WarmIt images to remove${NC}"
fi
echo ""

echo "======================================"
echo "Step 4: Remove unused build cache"
echo "======================================"
docker builder prune -f
echo -e "${GREEN}✅ Build cache cleared${NC}"
echo ""

echo "======================================"
echo "Step 5: Remove stopped containers"
echo "======================================"
docker container prune -f
echo -e "${GREEN}✅ Stopped containers removed${NC}"
echo ""

echo "======================================"
echo "Optional: Remove unused volumes?"
echo "======================================"
echo -e "${RED}⚠️  WARNING: This will delete database data!${NC}"
read -p "Remove volumes? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker volume prune -f
    echo -e "${GREEN}✅ Volumes removed${NC}"
else
    echo -e "${YELLOW}ℹ️  Volumes kept${NC}"
fi
echo ""

echo "======================================"
echo "📊 Cleanup Results"
echo "======================================"

DOCKER_AFTER=$(docker system df | grep "Total" | awk '{print $4}')
echo "🐋 Docker space usage AFTER: $DOCKER_AFTER"
echo ""

echo "💽 Disk space AFTER cleanup:"
df -h / | awk 'NR==1 || /\/$/'
echo ""

echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo ""
echo "To rebuild WarmIt:"
echo "  ./scripts/force-rebuild.sh"
echo ""
echo "Or manually:"
echo "  cd docker"
echo "  docker compose build --no-cache"
echo "  docker compose up -d"
