#!/bin/bash
# Debug script to check container structure

echo "======================================"
echo "🔍 WarmIt Container Debugging"
echo "======================================"
echo ""

if [ -z "$1" ]; then
    echo "Usage: ./debug-container.sh <container-name>"
    echo ""
    echo "Available containers:"
    docker ps -a --filter "name=warmit" --format "  - {{.Names}}"
    echo ""
    echo "Example: ./debug-container.sh warmit-api"
    exit 1
fi

CONTAINER=$1

echo "🐳 Container: $CONTAINER"
echo ""

if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "❌ Container $CONTAINER not found"
    exit 1
fi

echo "📦 Container Status:"
docker ps -a --filter "name=$CONTAINER" --format "table {{.Names}}\t{{.Status}}\t{{.State}}"
echo ""

echo "📂 Directory structure in /app:"
docker exec $CONTAINER ls -la /app 2>/dev/null || echo "Container not running or cannot execute commands"
echo ""

echo "📂 Python module structure:"
docker exec $CONTAINER find /app -name "*.py" -type f 2>/dev/null | head -20 || echo "Cannot list files"
echo ""

echo "🐍 Python path:"
docker exec $CONTAINER python -c "import sys; print('\n'.join(sys.path))" 2>/dev/null || echo "Cannot check Python path"
echo ""

echo "🔍 Check if warmit module exists:"
docker exec $CONTAINER python -c "import warmit; print('✅ Module found')" 2>/dev/null || echo "❌ Module NOT found"
echo ""

echo "📋 Last 30 lines of logs:"
docker logs $CONTAINER --tail 30
echo ""

echo "======================================"
echo "Image information:"
docker inspect $CONTAINER --format='Image: {{.Config.Image}}' 2>/dev/null
docker inspect $CONTAINER --format='Created: {{.Created}}' 2>/dev/null
echo ""

echo "To rebuild this container:"
echo "  cd docker"
echo "  docker compose build --no-cache $CONTAINER"
echo "  docker compose up -d $CONTAINER"
