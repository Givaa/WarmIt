# Docker Space Management for WarmIt

## Expected Disk Usage

### Docker Images
- **Base image** (`python:3.11-slim`): ~150 MB
- **WarmIt API/Worker** (after build): ~450-550 MB each
- **WarmIt Dashboard**: ~500-600 MB
- **Redis** (`redis:7-alpine`): ~30 MB
- **PostgreSQL** (`postgres:16-alpine`): ~240 MB
- **Dozzle** (`amir20/dozzle`): ~15 MB

**Total Images**: ~1.5-2 GB

### Docker Volumes (Data)
- **PostgreSQL data** (`postgres_data`): 100-500 MB (grows with campaigns/emails)
- **Redis data** (`redis_data`): 10-100 MB (temporary task queue data)
- **Logs** (`docker/logs`): 50-200 MB (rotated automatically)

**Total Volumes**: ~200 MB - 1 GB

### Build Cache
- **Docker build cache**: 500 MB - 2 GB (temporary layers during build)

**TOTAL EXPECTED**: 2-5 GB for a running WarmIt installation

## Quick Space Check

Run this script to check Docker disk usage:

```bash
./check-docker-space.sh
```

Or manually:

```bash
# Overall Docker usage
docker system df

# Detailed breakdown
docker system df -v

# System disk usage
df -h
```

## Cleanup Strategies

### 1. Safe Cleanup (Recommended)
Removes unused Docker resources without deleting data:

```bash
./cleanup-docker.sh
```

Or manually:

```bash
# Stop WarmIt
cd docker && docker compose down

# Remove dangling images
docker image prune -f

# Remove build cache
docker builder prune -f

# Remove stopped containers
docker container prune -f

# Rebuild
docker compose build --no-cache
docker compose up -d
```

**Space saved**: 500 MB - 2 GB

### 2. Full Cleanup (Destructive)
⚠️ **WARNING**: This deletes ALL Docker data including databases!

```bash
docker system prune -a --volumes
```

**Space saved**: 2-5 GB (everything)

### 3. WarmIt-Only Cleanup
Remove only WarmIt images and rebuild:

```bash
cd docker
docker compose down
docker images | grep warmit | awk '{print $3}' | xargs docker rmi -f
docker compose build --no-cache
docker compose up -d
```

**Space saved**: 1-2 GB

### 4. Remove Old Layers
If you've rebuilt multiple times, old layers accumulate:

```bash
docker builder prune -a -f
```

**Space saved**: 500 MB - 2 GB

## Optimized Dockerfile

The Dockerfile has been optimized to reduce image size:

1. **Multi-stage commands**: Combines apt, pip, and cleanup in one RUN statement
2. **Removes build dependencies**: `build-essential` removed after pip install
3. **Clears caches**: Removes apt lists and pip cache
4. **Slim base image**: Uses `python:3.11-slim` instead of full Python

**Before optimization**: ~650 MB per image
**After optimization**: ~450 MB per image
**Space saved**: ~200 MB per image × 4 images = **800 MB total**

## Preventing "No Space Left" Errors

### 1. Regular Cleanup Schedule

Add to crontab on Ubuntu server:

```bash
# Clean Docker weekly (Sundays at 3 AM)
0 3 * * 0 docker system prune -f >> /var/log/docker-cleanup.log 2>&1
```

### 2. Monitor Disk Usage

```bash
# Check every hour
watch -n 3600 df -h
```

### 3. Increase Disk Space (Ubuntu)

If you're on a cloud server (AWS, DigitalOcean, etc.):

```bash
# Check current size
df -h

# Resize disk from cloud provider dashboard
# Then expand filesystem:
sudo resize2fs /dev/sda1  # or your root partition
```

### 4. Move Docker Data Directory

If `/` is small but you have space on another partition:

```bash
# Stop Docker
sudo systemctl stop docker

# Move Docker data
sudo mv /var/lib/docker /mnt/large-partition/docker
sudo ln -s /mnt/large-partition/docker /var/lib/docker

# Start Docker
sudo systemctl start docker
```

## Log Rotation

WarmIt logs are automatically rotated by Docker:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "50m"  # Max 50MB per log file
    max-file: "5"    # Keep 5 files max
```

This prevents logs from filling disk.

## Quick Commands Reference

```bash
# Check space
./check-docker-space.sh
docker system df

# Safe cleanup
./cleanup-docker.sh
docker system prune -f

# Remove build cache
docker builder prune -f

# Remove old images
docker image prune -a -f

# Full cleanup (⚠️  DESTRUCTIVE)
docker system prune -a --volumes

# Rebuild WarmIt
cd docker
docker compose build --no-cache
docker compose up -d
```

## Troubleshooting

### "No space left on device" during build

```bash
# 1. Check space
df -h

# 2. Clean Docker
docker system prune -a -f
docker builder prune -a -f

# 3. If still failing, increase disk size or move Docker directory
```

### Docker images using too much space

```bash
# Remove all images and pull fresh
docker rmi $(docker images -q)
cd docker
docker compose pull
docker compose build --no-cache
```

### Volumes using too much space

```bash
# Check volume sizes
docker system df -v | grep -A 20 "Local Volumes"

# Remove unused volumes (⚠️  deletes data!)
docker volume prune -f
```

## Monitoring Best Practices

1. **Run space check weekly**: `./check-docker-space.sh`
2. **Clean build cache monthly**: `docker builder prune -f`
3. **Monitor logs**: Ensure log rotation is working
4. **Check volume growth**: Database should grow predictably with usage

## Expected Growth Over Time

- **Week 1**: 2-3 GB total
- **Month 1**: 3-4 GB (with campaign data)
- **Month 6**: 4-6 GB (with historical data)
- **Year 1**: 5-8 GB (with full history)

If growing faster, check:
- Log rotation working correctly
- Database not retaining unnecessary data
- No duplicate images accumulating
