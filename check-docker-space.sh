#!/bin/bash
# Check Docker disk usage and provide cleanup commands

echo "======================================"
echo "🔍 Docker Disk Usage Analysis"
echo "======================================"
echo ""

echo "📊 Overall Docker disk usage:"
docker system df
echo ""

echo "======================================"
echo "📦 Detailed breakdown:"
echo "======================================"
echo ""

echo "🖼️  Docker Images:"
docker system df -v | grep -A 100 "Images space usage:" | head -20
echo ""

echo "📦 Docker Containers:"
docker ps -a --format "table {{.Names}}\t{{.Size}}"
echo ""

echo "💾 Docker Volumes:"
docker volume ls -q | xargs docker volume inspect --format '{{.Name}}: {{.Mountpoint}}' 2>/dev/null
echo ""

echo "======================================"
echo "💽 System Disk Usage:"
echo "======================================"
df -h / | awk 'NR==1 || /\/$/'
echo ""

echo "======================================"
echo "🧹 Cleanup Recommendations:"
echo "======================================"
echo ""
echo "1. Remove all stopped containers, unused networks, dangling images:"
echo "   docker system prune -a"
echo ""
echo "2. Remove all unused volumes (⚠️  WARNING: This deletes data!):"
echo "   docker volume prune"
echo ""
echo "3. Remove everything and start fresh (⚠️  DANGEROUS!):"
echo "   docker system prune -a --volumes"
echo ""
echo "4. Remove only WarmIt images to rebuild:"
echo "   docker images | grep warmit | awk '{print \$3}' | xargs docker rmi -f"
echo ""
echo "5. Check large Docker files:"
echo "   du -sh ~/Library/Containers/com.docker.docker/Data 2>/dev/null || echo 'Docker Desktop data location varies'"
echo ""

echo "======================================"
echo "📝 WarmIt specific images:"
echo "======================================"
docker images | grep -E "warmit|REPOSITORY"
