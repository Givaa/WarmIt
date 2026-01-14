#!/bin/bash

# WarmIt - System Requirements Check Script
# Verifies all prerequisites for running WarmIt on Linux/Ubuntu

set +e  # Don't exit on errors

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔥 WarmIt - System Requirements Check${NC}"
echo "======================================"
echo ""

ERRORS=0
WARNINGS=0

# Check OS
echo -e "${BLUE}System Information:${NC}"
if command -v lsb_release &> /dev/null; then
    echo "  OS: $(lsb_release -d | cut -f2)"
else
    echo "  OS: $(uname -s) $(uname -r)"
fi
echo "  Kernel: $(uname -r)"
echo "  Architecture: $(uname -m)"
echo ""

# Check Docker
echo -e "${BLUE}Required Software:${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
    echo -e "  ${GREEN}✅ Docker${NC}: $DOCKER_VERSION"

    # Check Docker daemon
    if docker info &> /dev/null 2>&1; then
        echo -e "     ${GREEN}✅ Docker daemon running${NC}"
    else
        echo -e "     ${RED}❌ Docker daemon not running or permission denied${NC}"
        echo "        Try: sudo usermod -aG docker \$USER && newgrp docker"
        ((ERRORS++))
    fi
else
    echo -e "  ${RED}❌ Docker: Not installed${NC}"
    echo "     Install: curl -fsSL https://get.docker.com | sh"
    ((ERRORS++))
fi

# Check Docker Compose
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "installed")
    echo -e "  ${GREEN}✅ Docker Compose${NC}: $COMPOSE_VERSION"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | awk '{print $3}' | tr -d ',')
    echo -e "  ${GREEN}✅ Docker Compose (v1)${NC}: $COMPOSE_VERSION"
    echo -e "     ${YELLOW}⚠️  Consider upgrading to Docker Compose v2${NC}"
    ((WARNINGS++))
else
    echo -e "  ${RED}❌ Docker Compose: Not installed${NC}"
    echo "     Install: sudo apt-get install docker-compose-plugin"
    ((ERRORS++))
fi

# Check Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    echo -e "  ${GREEN}✅ Git${NC}: $GIT_VERSION"
else
    echo -e "  ${RED}❌ Git: Not installed${NC}"
    echo "     Install: sudo apt-get install git"
    ((ERRORS++))
fi

# Check curl
if command -v curl &> /dev/null; then
    CURL_VERSION=$(curl --version | head -1 | awk '{print $2}')
    echo -e "  ${GREEN}✅ curl${NC}: $CURL_VERSION"
else
    echo -e "  ${RED}❌ curl: Not installed${NC}"
    echo "     Install: sudo apt-get install curl"
    ((ERRORS++))
fi

# Check jq (optional but recommended)
if command -v jq &> /dev/null; then
    JQ_VERSION=$(jq --version | tr -d 'jq-')
    echo -e "  ${GREEN}✅ jq${NC}: $JQ_VERSION"
else
    echo -e "  ${YELLOW}⚠️  jq: Not installed (optional, for scripts)${NC}"
    echo "     Install: sudo apt-get install jq"
    ((WARNINGS++))
fi

echo ""

# Check Hardware
echo -e "${BLUE}Hardware Resources:${NC}"

# CPU
CPU_CORES=$(nproc)
if [ "$CPU_CORES" -ge 4 ]; then
    echo -e "  ${GREEN}✅ CPU Cores${NC}: $CPU_CORES (Excellent)"
elif [ "$CPU_CORES" -ge 2 ]; then
    echo -e "  ${GREEN}✅ CPU Cores${NC}: $CPU_CORES (Adequate)"
else
    echo -e "  ${YELLOW}⚠️  CPU Cores${NC}: $CPU_CORES (May be slow)"
    ((WARNINGS++))
fi

# RAM
if command -v free &> /dev/null; then
    RAM_TOTAL=$(free -g | awk '/^Mem:/ {print $2}')
    RAM_TOTAL_MB=$(free -m | awk '/^Mem:/ {print $2}')

    if [ "$RAM_TOTAL" -ge 8 ]; then
        echo -e "  ${GREEN}✅ RAM${NC}: ${RAM_TOTAL}GB (Excellent)"
    elif [ "$RAM_TOTAL" -ge 4 ]; then
        echo -e "  ${GREEN}✅ RAM${NC}: ${RAM_TOTAL}GB (Adequate)"
    elif [ "$RAM_TOTAL_MB" -ge 4000 ]; then
        echo -e "  ${GREEN}✅ RAM${NC}: ${RAM_TOTAL_MB}MB (Adequate)"
    else
        echo -e "  ${YELLOW}⚠️  RAM${NC}: ${RAM_TOTAL_MB}MB (May be insufficient)"
        echo "     Recommended: 4GB minimum"
        ((WARNINGS++))
    fi
fi

# Disk Space
if command -v df &> /dev/null; then
    DISK_FREE=$(df -BG / | awk 'NR==2 {print $4}' | tr -d 'G')

    if [ "$DISK_FREE" -ge 50 ]; then
        echo -e "  ${GREEN}✅ Disk Space${NC}: ${DISK_FREE}GB free (Excellent)"
    elif [ "$DISK_FREE" -ge 20 ]; then
        echo -e "  ${GREEN}✅ Disk Space${NC}: ${DISK_FREE}GB free (Adequate)"
    else
        echo -e "  ${YELLOW}⚠️  Disk Space${NC}: ${DISK_FREE}GB free (Low)"
        echo "     Recommended: 20GB minimum"
        ((WARNINGS++))
    fi
fi

echo ""

# Check Network
echo -e "${BLUE}Network:${NC}"

# Check internet connectivity
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo -e "  ${GREEN}✅ Internet connectivity${NC}"
else
    echo -e "  ${RED}❌ No internet connectivity${NC}"
    ((ERRORS++))
fi

# Check if ports are available
check_port() {
    local port=$1
    local service=$2

    if command -v ss &> /dev/null; then
        if ss -tuln | grep -q ":$port "; then
            echo -e "  ${YELLOW}⚠️  Port $port ($service)${NC}: In use"
            echo "     Check: sudo lsof -i :$port"
            ((WARNINGS++))
        else
            echo -e "  ${GREEN}✅ Port $port ($service)${NC}: Available"
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":$port "; then
            echo -e "  ${YELLOW}⚠️  Port $port ($service)${NC}: In use"
            ((WARNINGS++))
        else
            echo -e "  ${GREEN}✅ Port $port ($service)${NC}: Available"
        fi
    fi
}

check_port 8000 "API"
check_port 8501 "Dashboard"

echo ""

# Check Docker volumes
if docker info &> /dev/null 2>&1; then
    echo -e "${BLUE}Docker Status:${NC}"

    # Check Docker storage driver
    STORAGE_DRIVER=$(docker info 2>/dev/null | grep "Storage Driver" | awk '{print $3}')
    echo "  Storage Driver: $STORAGE_DRIVER"

    # Check existing WarmIt containers
    WARMIT_CONTAINERS=$(docker ps -a --filter "name=warmit" --format "{{.Names}}" 2>/dev/null | wc -l)
    if [ "$WARMIT_CONTAINERS" -gt 0 ]; then
        echo -e "  ${BLUE}Found $WARMIT_CONTAINERS WarmIt containers${NC}"
    fi

    # Check Docker disk usage
    if command -v docker &> /dev/null; then
        DOCKER_DISK=$(docker system df 2>/dev/null | grep "Total" | awk '{print $4}')
        if [ -n "$DOCKER_DISK" ]; then
            echo "  Docker disk usage: $DOCKER_DISK"
        fi
    fi

    echo ""
fi

# Summary
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Summary:${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All requirements met! System ready for WarmIt.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. git clone https://github.com/yourusername/warmit.git"
    echo "  2. cd warmit"
    echo "  3. ./start.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found${NC}"
    echo "System should work, but review warnings above."
    echo ""
    echo "You can proceed with:"
    echo "  ./start.sh"
    exit 0
else
    echo -e "${RED}❌ $ERRORS error(s) and $WARNINGS warning(s) found${NC}"
    echo "Please fix errors above before installing WarmIt."
    echo ""
    echo "Quick fix for Ubuntu/Debian:"
    echo "  curl -fsSL https://get.docker.com | sudo sh"
    echo "  sudo usermod -aG docker \$USER"
    echo "  sudo apt-get install -y git curl jq"
    echo "  newgrp docker  # Or logout/login"
    exit 1
fi
