#!/bin/bash
# Force complete rebuild of WarmIt - Use this after Dockerfile changes

set -e

echo "======================================"
echo "🔨 Force Rebuild WarmIt"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT/docker"

echo -e "${YELLOW}⏹️  Step 1: Stopping all containers...${NC}"
docker compose down
echo -e "${GREEN}✅ Stopped${NC}"
echo ""

echo -e "${YELLOW}🗑️  Step 2: Removing old WarmIt images...${NC}"
docker images | grep warmit | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
echo -e "${GREEN}✅ Old images removed${NC}"
echo ""

echo -e "${YELLOW}🧹 Step 3: Clearing build cache...${NC}"
docker builder prune -f
echo -e "${GREEN}✅ Cache cleared${NC}"
echo ""

echo -e "${BLUE}🔨 Step 4: Building fresh images (no cache)...${NC}"
echo "This will take 3-5 minutes..."
docker compose build --no-cache --progress=plain
echo -e "${GREEN}✅ Build complete${NC}"
echo ""

echo -e "${BLUE}🚀 Step 5: Starting services...${NC}"
docker compose up -d
echo -e "${GREEN}✅ Services started${NC}"
echo ""

echo -e "${BLUE}⏳ Step 6: Waiting for API to be healthy...${NC}"
for i in {1..60}; do
    if docker inspect warmit-api --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo -e "${GREEN}✅ API is healthy!${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}❌ API failed to become healthy after 2 minutes${NC}"
        echo ""
        echo "Checking logs..."
        docker logs warmit-api --tail 30
        exit 1
    fi
    echo -n "."
    sleep 2
done

echo ""
echo -e "${GREEN}======================================"
echo "✅ Rebuild Complete!"
echo "======================================${NC}"
echo ""
echo -e "${BLUE}Service Status:${NC}"
docker compose ps
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo "  📊 Dashboard:  http://localhost:8501"
echo "  📝 Logs (Web): http://localhost:8888"
echo "  🔌 API:        http://localhost:8000"
echo "  📖 API Docs:   http://localhost:8000/docs"
echo ""
echo -e "${GREEN}Happy warming! 🔥${NC}"
