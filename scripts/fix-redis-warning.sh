#!/bin/bash
# Fix Redis memory overcommit warning on host system

echo "Fixing Redis memory overcommit warning..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script needs sudo privileges to modify system settings."
    echo "Run with: sudo ./scripts/fix-redis-warning.sh"
    exit 1
fi

# Set overcommit_memory to 1
echo "Setting vm.overcommit_memory = 1..."
sysctl vm.overcommit_memory=1

# Make it persistent across reboots
if ! grep -q "vm.overcommit_memory" /etc/sysctl.conf; then
    echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf
    echo "✅ Setting added to /etc/sysctl.conf (persistent across reboots)"
else
    echo "✅ Setting already exists in /etc/sysctl.conf"
fi

echo ""
echo "✅ Redis memory overcommit warning fixed!"
echo ""
echo "What this does:"
echo "  - Allows Redis to allocate memory even if physical RAM is low"
echo "  - Prevents Redis from failing when system memory is overcommitted"
echo "  - Safe for Redis workloads (Redis manages its own memory)"
echo ""
echo "Restart Redis container to apply: docker restart warmit-redis"
