# Docker Configuration

This directory contains all Docker-related files for WarmIt production deployment.

## Files Structure

```
docker/
├── docker-compose.yml          # Main compose file (symlink to prod)
├── docker-compose.prod.yml     # Production configuration (actual file)
├── Dockerfile                  # Main app image (API, Worker, Beat, Watchdog)
├── Dockerfile.dashboard        # Streamlit dashboard image
├── .env                        # Environment variables (create from .env.example)
└── README.md                   # This file
```

## Services

WarmIt runs 8 Docker containers in production:

| Service | Port | Description |
|---------|------|-------------|
| **api** | 8000 | FastAPI REST API |
| **worker** | - | Celery worker for email tasks |
| **beat** | - | Celery beat scheduler |
| **dashboard** | 8501 | Streamlit web dashboard |
| **watchdog** | - | Health monitoring service |
| **logs** | 8888 | Dozzle web-based log viewer |
| **postgres** | 5432 | PostgreSQL database |
| **redis** | 6379 | Redis for Celery |

## Quick Start

```bash
# From project root
./start.sh

# Access services
open http://localhost:8501    # Dashboard
open http://localhost:8888    # Logs viewer
open http://localhost:8000/docs  # API docs
```

## Web-Based Log Viewer

**Dozzle** provides a modern web interface to view all container logs in real-time.

**Access:** http://localhost:8888

**Features:**
- Real-time log streaming
- Search and filter logs
- Multi-container view
- Auto-refresh
- Dark mode
- No authentication required (local only)

**Usage:**
1. Open http://localhost:8888
2. Select container from dropdown (warmit-api, warmit-worker, etc.)
3. View real-time logs
4. Use search bar to filter
5. Click "Download" to export logs

**Why Dozzle?**
- ✅ No need for `docker compose logs` commands
- ✅ Browser-based, accessible from any device on network
- ✅ Better than terminal for long-running sessions
- ✅ Search and filter capabilities
- ✅ Lightweight (only 256MB RAM)

## Configuration

### Environment Variables

Copy `.env.example` to `docker/.env` and configure:

```bash
# Required
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Database
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql+asyncpg://warmit:password@postgres:5432/warmit

# Redis
REDIS_URL=redis://redis:6379/0
```

### Production Features

All services include:
- ✅ **Health checks**: Every 30-60s
- ✅ **Auto-restart**: On failure
- ✅ **Resource limits**: CPU and memory
- ✅ **Log rotation**: Max 50MB per service
- ✅ **Data persistence**: Volumes for postgres/redis

## Commands

### Start/Stop

```bash
./start.sh              # Start all services
./start.sh restart      # Restart all services
./start.sh stop         # Stop all services
./start.sh down         # Stop and remove containers
./start.sh reset        # Delete all data (WARNING!)
```

### View Status

```bash
cd docker
docker compose ps       # Service status
docker compose logs -f  # All logs
docker compose logs -f api     # API logs only
docker compose logs -f worker  # Worker logs only
```

**Or use web interface:** http://localhost:8888

### Scale Services

```bash
# Scale workers for high volume
cd docker
docker compose up -d --scale worker=3
```

### Manual Operations

```bash
cd docker

# Restart specific service
docker compose restart api

# View resource usage
docker stats

# Execute command in container
docker compose exec api bash
docker compose exec postgres psql -U warmit

# View specific logs
docker compose logs --tail=100 worker
```

## Port Reference

| Port | Service | Protocol | Notes |
|------|---------|----------|-------|
| 8000 | API | HTTP | REST API endpoints |
| 8501 | Dashboard | HTTP | Streamlit UI |
| 8888 | Logs | HTTP | Dozzle log viewer |
| 5432 | PostgreSQL | TCP | Database (internal) |
| 6379 | Redis | TCP | Cache/Queue (internal) |

**Firewall Configuration:**
- Allow 8000, 8501, 8888 for web access
- 5432, 6379 are container-to-container only

## Data Persistence

Docker volumes store persistent data:

```bash
# List volumes
docker volume ls | grep warmit

# Backup database
docker compose exec postgres pg_dump -U warmit warmit > backup.sql

# Restore database
docker compose exec -T postgres psql -U warmit warmit < backup.sql

# Backup Redis (if needed)
docker compose exec redis redis-cli SAVE
```

## Troubleshooting

### Services not starting

```bash
# Check logs via web
open http://localhost:8888

# Or via terminal
cd docker
docker compose logs api
docker compose logs worker
```

### High memory usage

```bash
# Check resource usage
docker stats

# Restart specific service
docker compose restart worker
```

### Database issues

```bash
# Check PostgreSQL
docker compose exec postgres psql -U warmit -c "SELECT version();"

# View database logs
docker compose logs postgres
```

### Network issues

```bash
# Check network
docker network inspect warmit-network

# Recreate network
docker compose down
docker compose up -d
```

### Reset everything

```bash
# Complete reset (deletes ALL data)
./start.sh reset

# Then start fresh
./start.sh
```

## Production Deployment

### Ubuntu/Linux Server

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# 2. Clone repository
git clone <repo-url> warmit
cd warmit

# 3. Configure
cp .env.example docker/.env
nano docker/.env  # Add API keys

# 4. Start
./start.sh
```

### Nginx Reverse Proxy (Optional)

```nginx
# /etc/nginx/sites-available/warmit
server {
    listen 80;
    server_name warmit.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /logs {
        proxy_pass http://localhost:8888;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

## Updates

```bash
# Pull latest changes
git pull

# Rebuild and restart
cd docker
docker compose build
docker compose up -d

# Or use script
./start.sh restart
```

## Monitoring

### Web Interfaces
- **Dashboard**: http://localhost:8501 - Campaign metrics
- **Logs**: http://localhost:8888 - Real-time logs
- **API Docs**: http://localhost:8000/docs - API testing

### Health Checks

All services have health checks:
- API: `curl http://localhost:8000/health`
- Dashboard: `curl http://localhost:8501/_stcore/health`
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`

### Resource Limits

| Service | CPU Limit | Memory Limit | Notes |
|---------|-----------|--------------|-------|
| api | 1.0 | 1GB | Main API |
| worker | 2.0 | 2GB | Email processing |
| beat | 0.5 | 512MB | Scheduler |
| dashboard | 1.0 | 1GB | Streamlit |
| watchdog | - | - | Monitoring |
| logs | 0.5 | 256MB | Log viewer |
| postgres | - | - | Database |
| redis | - | 512MB | Cache |

## Security Notes

- ⚠️ Change default passwords in `docker/.env`
- ⚠️ Use firewall to restrict port access
- ⚠️ Don't expose 5432, 6379 publicly
- ⚠️ Use Nginx with SSL for production
- ⚠️ Keep Docker and images updated

## Support

For issues or questions, see main [README.md](../README.md) and [docs/](../docs/)
