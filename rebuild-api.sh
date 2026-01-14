#!/bin/bash
# Quick rebuild script for API container after code changes

set -e

echo "🔧 Rebuilding WarmIt API container..."
echo ""

cd docker

# Stop and remove old API container
echo "⏹️  Stopping old API container..."
docker stop warmit-api 2>/dev/null || true
docker rm warmit-api 2>/dev/null || true

# Rebuild API image
echo "🔨 Building new API image..."
docker compose build --no-cache api

# Start all services
echo "🚀 Starting services..."
docker compose up -d

# Wait for API to be healthy
echo ""
echo "⏳ Waiting for API to be healthy..."
for i in {1..30}; do
    if docker inspect warmit-api --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
        echo "✅ API is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API failed to become healthy"
        echo ""
        echo "Check logs with:"
        echo "  docker logs warmit-api"
        exit 1
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "✅ Rebuild complete!"
echo ""
echo "View logs: docker logs -f warmit-api"
