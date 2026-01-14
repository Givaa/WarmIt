# Utility Scripts

Utility scripts for maintenance and debugging.

## Available Scripts

### 🔨 force-rebuild.sh
Force complete rebuild of all Docker images without cache.

**When to use:**
- After changing Dockerfiles
- When containers fail to start with "module not found" errors
- To ensure latest code changes are applied

**Usage:**
```bash
./scripts/force-rebuild.sh
```

### 🧹 cleanup-docker.sh
Clean up Docker resources (images, containers, cache) to free disk space.

**When to use:**
- "No space left on device" errors
- Before major rebuilds
- Regular maintenance

**Usage:**
```bash
./scripts/cleanup-docker.sh
```

### 🔍 check-docker-space.sh
Analyze Docker disk usage and show cleanup recommendations.

**Usage:**
```bash
./scripts/check-docker-space.sh
```

### 🐛 debug-container.sh
Debug a specific container to check its internal structure and logs.

**Usage:**
```bash
./scripts/debug-container.sh <container-name>

# Example
./scripts/debug-container.sh warmit-api
```

Shows:
- Container status
- Directory structure
- Python module paths
- Recent logs
- Image information

## Notes

- All scripts must be run from the project root directory
- The main `start.sh` script is in the project root for convenience
- These utility scripts are for advanced troubleshooting and maintenance
