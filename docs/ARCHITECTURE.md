# WarmIt Architecture

## Overview

WarmIt is a microservices-based email warming system built with Python, FastAPI, and Celery, orchestrated via Docker Compose.

```
┌─────────────┐     ┌──────────┐     ┌────────────┐
│  Dashboard  │────▶│   API    │────▶│ PostgreSQL │
│ (Streamlit) │     │ (FastAPI)│     │  Database  │
│   :8501     │     │  :8000   │     │   :5432    │
└─────────────┘     └────┬─────┘     └────────────┘
                         │
                         ├──────────┬────────────┐
                         ▼          ▼            ▼
                    ┌─────────┐ ┌────────┐ ┌──────────┐
                    │  Redis  │ │ Worker │ │ Watchdog │
                    │  :6379  │ │(Celery)│ │ Monitor  │
                    └─────────┘ └────────┘ └──────────┘
                         │          ▲
                         └──────────┘
                            Beat
                         (Scheduler)
```

## Components

### 1. API (FastAPI)
**Port:** 8000
**Container:** `warmit-api`
**Purpose:** REST API for managing accounts, campaigns, and metrics

**Endpoints:**
- `/health` - Health check
- `/accounts` - Email account management
- `/campaigns` - Warming campaign management
- `/metrics` - Performance metrics
- `/docs` - Interactive API documentation

**Key Features:**
- Async request handling
- Pydantic validation
- SQLAlchemy ORM
- Auto-generated OpenAPI docs

### 2. Dashboard (Streamlit)
**Port:** 8501
**Container:** `warmit-dashboard`
**Purpose:** Web UI for monitoring and management

**Features:**
- Real-time metrics visualization
- Campaign management interface
- Account status monitoring
- Interactive charts (Plotly)

**Tech:**
- Streamlit for UI
- Pandas for data processing
- Plotly for visualization

### 3. Worker (Celery)
**Container:** `warmit-worker`
**Purpose:** Asynchronous task execution

**Tasks:**
- Send warming emails
- Fetch and process responses
- Generate AI content
- Update metrics

**Configuration:**
- Concurrency: 4 workers
- Max tasks per child: 1000
- Auto-restart on failure

### 4. Beat (Celery Beat)
**Container:** `warmit-beat`
**Purpose:** Task scheduler

**Schedules:**
- Daily email sending (based on campaign schedule)
- Response checking (every 15 minutes)
- Metric updates (every 5 minutes)
- Health checks (every 30 minutes)

### 5. Watchdog
**Container:** `warmit-watchdog`
**Purpose:** System monitoring and auto-recovery

**Monitors:**
- Worker health
- Queue length
- Failed tasks
- API availability

**Actions:**
- Restart failed workers
- Clear stuck tasks
- Alert on critical issues
- Log system metrics

### 6. PostgreSQL
**Port:** 5432
**Container:** `warmit-postgres`
**Purpose:** Primary data storage

**Tables:**
- `accounts` - Email accounts
- `campaigns` - Warming campaigns
- `emails` - Sent/received emails
- `metrics` - Performance data

**Features:**
- Persistent volume
- Auto-backup
- Connection pooling

### 7. Redis
**Port:** 6379
**Container:** `warmit-redis`
**Purpose:** Task queue and cache

**Usage:**
- Celery message broker
- Task result backend
- Session cache
- Rate limiting

**Configuration:**
- Persistence: AOF + RDB
- Max memory: 512MB
- Eviction: allkeys-lru

### 8. Dozzle (Logs Viewer)
**Port:** 8888
**Container:** `warmit-logs`
**Purpose:** Web-based log aggregation

**Features:**
- Real-time log streaming
- Multi-container view
- Search and filter
- No data persistence (read-only)

## Data Flow

### Email Sending Flow
```
1. Beat triggers daily schedule
2. Beat creates "send_emails" task → Redis queue
3. Worker picks up task
4. Worker fetches campaign config from PostgreSQL
5. Worker generates AI content (OpenRouter/Groq)
6. Worker sends email via SMTP
7. Worker logs result to PostgreSQL
8. Worker updates metrics
```

### Response Processing Flow
```
1. Beat triggers response check
2. Beat creates "check_responses" task → Redis queue
3. Worker picks up task
4. Worker connects to IMAP
5. Worker fetches unread emails
6. Worker identifies warming emails (by Message-ID)
7. Worker generates AI response
8. Worker sends reply
9. Worker marks original as read
10. Worker updates engagement metrics
```

### Health Monitoring Flow
```
1. Watchdog runs every 5 minutes
2. Checks worker health via Celery inspect
3. Checks API health via HTTP request
4. Checks Redis connectivity
5. Checks PostgreSQL connectivity
6. If unhealthy: attempts restart
7. Logs status to PostgreSQL
```

## Communication

### Internal (Docker Network)
- Dashboard → API: `http://api:8000`
- API → PostgreSQL: `postgresql://postgres:5432`
- API → Redis: `redis://redis:6379`
- Worker → API: `http://api:8000`
- Worker → PostgreSQL: Direct connection
- Worker → Redis: Direct connection

### External (Host Machine)
- Dashboard: `http://localhost:8501`
- API: `http://localhost:8000`
- Logs: `http://localhost:8888`
- PostgreSQL: `localhost:5432` (if exposed)
- Redis: `localhost:6379` (if exposed)

## File Structure

```
WarmIt/
├── src/warmit/          # Main application code
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # Configuration
│   ├── database.py      # DB connection
│   ├── models/          # SQLAlchemy models
│   ├── api/             # FastAPI routes
│   ├── services/        # Business logic
│   │   ├── email_service.py
│   │   ├── ai_service.py
│   │   └── health_monitor.py
│   └── tasks/           # Celery tasks
│       ├── warming.py
│       └── response.py
├── dashboard/           # Streamlit dashboard
│   └── app.py
├── scripts/             # Utility scripts
│   ├── watchdog.py      # Monitoring script
│   └── ...
├── docker/              # Docker configuration
│   ├── .env             # Environment variables
│   ├── Dockerfile       # Main app image
│   ├── Dockerfile.dashboard
│   ├── docker-compose.yml → docker-compose.prod.yml
│   └── docker-compose.prod.yml
├── alembic/             # Database migrations
└── docs/                # Documentation
```

## Configuration

### Environment Variables (.env)

**AI Provider:**
- `AI_PROVIDER` - "openrouter" or "groq"
- `OPENROUTER_API_KEY` - OpenRouter API key
- `GROQ_API_KEY` - Groq API key

**Database:**
- `POSTGRES_PASSWORD` - Database password
- `DATABASE_URL` - Connection string (auto-generated)

**Redis:**
- `REDIS_URL` - Connection string (auto-generated)

**Logging:**
- `LOG_LEVEL` - INFO, DEBUG, WARNING, ERROR

### Docker Compose Configuration

**docker-compose.prod.yml:**
- Service definitions
- Network configuration
- Volume mounts
- Health checks
- Resource limits

**Key Features:**
- Auto-restart on failure
- Health checks every 30s
- Log rotation (max 50MB per service)
- Resource limits (CPU/RAM)
- Persistent volumes for data

## Scaling

### Horizontal Scaling

**Workers:**
```yaml
worker:
  deploy:
    replicas: 4
```

**API:**
```yaml
api:
  command: uvicorn warmit.main:app --workers 4
```

### Vertical Scaling

**Increase Resources:**
```yaml
worker:
  deploy:
    resources:
      limits:
        cpus: '4.0'
        memory: 4G
```

### Performance Tuning

**Redis:**
- Increase max memory for larger queues
- Adjust eviction policy based on usage

**PostgreSQL:**
- Tune connection pool size
- Add read replicas for heavy loads

**Celery:**
- Increase concurrency per worker
- Add more worker containers
- Tune task retry policies

## Monitoring

### Health Endpoints

**API Health:**
```bash
curl http://localhost:8000/health
```

**Detailed Health:**
```bash
curl http://localhost:8000/health/detailed
```

**Worker Health:**
```bash
docker exec warmit-worker celery -A warmit.tasks inspect ping
```

### Logs

**View all logs:**
```bash
docker compose -f docker/docker-compose.yml logs -f
```

**Specific service:**
```bash
docker logs -f warmit-api
```

**Web UI:**
```
http://localhost:8888
```

### Metrics

**Database:**
- Campaign stats via API `/metrics/campaigns`
- Account stats via API `/metrics/accounts`
- System health via `/health/detailed`

**Dashboard:**
- Real-time visualization at http://localhost:8501
- Export metrics as CSV

## Security

### Network Isolation
- All services on isolated Docker network
- Only necessary ports exposed to host
- Inter-service communication on private network

### Credentials
- Environment variables (not hardcoded)
- .env file (gitignored)
- No secrets in Docker images

### Best Practices
- Use strong PostgreSQL password
- Rotate API keys regularly
- Keep containers updated
- Monitor logs for suspicious activity

## Troubleshooting

### Common Issues

**1. Dashboard can't connect to API**
- Check API is healthy: `docker ps`
- Check environment variable: `docker exec warmit-dashboard env | grep API_BASE_URL`
- Should be: `API_BASE_URL=http://api:8000`

**2. Worker not processing tasks**
- Check Redis connection: `docker logs warmit-redis`
- Check worker logs: `docker logs warmit-worker`
- Inspect queue: `docker exec warmit-worker celery -A warmit.tasks inspect active`

**3. Database connection errors**
- Check PostgreSQL is running: `docker ps | grep postgres`
- Check connection string in .env
- Verify database exists: `docker exec warmit-postgres psql -U warmit -l`

**4. Out of memory**
- Check resource usage: `docker stats`
- Increase Docker memory limit
- Reduce worker concurrency
- Tune Redis max memory

### Debug Tools

**Container inspection:**
```bash
./scripts/debug-container.sh warmit-api
```

**Force rebuild:**
```bash
./scripts/force-rebuild.sh
```

**Check disk space:**
```bash
./scripts/check-docker-space.sh
```

**Cleanup:**
```bash
./scripts/cleanup-docker.sh
```

## Backup & Recovery

### Database Backup
```bash
docker exec warmit-postgres pg_dump -U warmit warmit > backup.sql
```

### Database Restore
```bash
docker exec -i warmit-postgres psql -U warmit warmit < backup.sql
```

### Volume Backup
```bash
docker run --rm -v warmit_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

## Development vs Production

### Development
- Single worker
- Debug logging
- Hot reload enabled
- Direct database access

### Production (Current)
- Multiple workers
- Info logging
- No hot reload
- Health checks enabled
- Auto-restart on failure
- Resource limits enforced
- Log rotation configured

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.11+ |
| API Framework | FastAPI | 0.115+ |
| Dashboard | Streamlit | 1.41+ |
| Task Queue | Celery | 5.4+ |
| Scheduler | Celery Beat | 5.4+ |
| Message Broker | Redis | 7+ |
| Database | PostgreSQL | 16+ |
| ORM | SQLAlchemy | 2.0+ |
| Container | Docker | 20.10+ |
| Orchestration | Docker Compose | 2.0+ |

## Next Steps

1. Read [QUICKSTART.md](QUICKSTART.md) for setup instructions
2. Review [FAQ.md](FAQ.md) for common questions
3. Check [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md) for hardware needs
4. Explore API docs at http://localhost:8000/docs after starting
