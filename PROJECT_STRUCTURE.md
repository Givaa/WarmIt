# WarmIt - Project Structure

## 📁 Directory Layout

```
WarmIt/
│
├── 📄 README.md                    # Main documentation
├── 📄 LICENSE                      # MIT License
├── 📄 CHANGELOG.md                 # Version history
├── 📄 CONTRIBUTING.md              # Contributing guidelines
├── 📄 Makefile                     # Development commands
├── 📄 pyproject.toml               # Python dependencies
├── 📄 .env.example                 # Environment template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 start.sh                     # 🚀 One-click production startup
│
├── 📁 src/warmit/                  # Main application
│   ├── 📄 __init__.py
│   ├── 📄 main.py                  # FastAPI application
│   ├── 📄 config.py                # Configuration management
│   ├── 📄 database.py              # Database connection
│   │
│   ├── 📁 api/                     # REST API routes
│   │   ├── 📄 __init__.py
│   │   ├── 📄 accounts.py          # Account endpoints
│   │   ├── 📄 campaigns.py         # Campaign endpoints
│   │   └── 📄 metrics.py           # Metrics endpoints
│   │
│   ├── 📁 models/                  # Database models
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base.py              # Base model
│   │   ├── 📄 account.py           # Account model
│   │   ├── 📄 campaign.py          # Campaign model
│   │   ├── 📄 email.py             # Email tracking model
│   │   └── 📄 metric.py            # Metrics model
│   │
│   ├── 📁 services/                # Business logic
│   │   ├── 📄 __init__.py
│   │   ├── 📄 domain_checker.py    # WHOIS/RDAP checker
│   │   ├── 📄 ai_generator.py      # AI content generation
│   │   ├── 📄 email_service.py     # SMTP/IMAP service
│   │   ├── 📄 scheduler.py         # Warming scheduler
│   │   ├── 📄 response_bot.py      # Auto-response bot
│   │   └── 📄 health_monitor.py    # Health monitoring
│   │
│   ├── 📁 tasks/                   # Celery tasks
│   │   ├── 📄 __init__.py          # Celery app
│   │   ├── 📄 warming.py           # Warming tasks
│   │   └── 📄 response.py          # Response tasks
│   │
│   └── 📁 utils/                   # Utilities
│       └── 📄 __init__.py
│
├── 📁 dashboard/                   # Streamlit web UI
│   └── 📄 app.py                   # Dashboard application
│
├── 📁 scripts/                     # Utility scripts
│   ├── 📄 setup.sh                 # Initial setup
│   ├── 📄 run_dev.sh               # Development runner
│   ├── 📄 cli.py                   # CLI tool
│   └── 📄 watchdog.py              # Monitoring service
│
├── 📁 tests/                       # Test suite
│   ├── 📄 __init__.py
│   └── 📄 test_domain_checker.py
│
├── 📁 docker/                      # Docker configuration
│   ├── 📄 docker-compose.yml       # Development compose
│   ├── 📄 docker-compose.prod.yml  # Production compose
│   ├── 📄 Dockerfile               # Main Dockerfile
│   └── 📄 Dockerfile.dashboard     # Dashboard Dockerfile
│
├── 📁 docs/                        # Documentation
│   ├── 📄 QUICKSTART.md            # 5-minute guide
│   ├── 📄 PRODUCTION.md            # Production deployment
│   ├── 📄 USAGE.md                 # Usage guide
│   ├── 📄 FAQ.md                   # FAQ & troubleshooting
│   ├── 📄 FEATURES.md              # Feature highlights
│   └── 📄 PROJECT_SUMMARY.md       # Technical overview
│
├── 📁 examples/                    # Usage examples
│   └── 📄 api_examples.sh          # API request examples
│
├── 📁 .github/                     # GitHub configuration
│   ├── 📁 ISSUE_TEMPLATE/
│   │   ├── 📄 bug_report.md
│   │   └── 📄 feature_request.md
│   └── 📄 pull_request_template.md
│
├── 📁 alembic/                     # Database migrations
│   ├── 📄 env.py
│   └── 📁 versions/
│
└── 📁 logs/                        # Application logs (created at runtime)
```

## 🎯 Key Files Explained

### Root Level

| File | Purpose |
|------|---------|
| `start.sh` | **Production startup** - One command to start everything |
| `README.md` | Main documentation and entry point |
| `pyproject.toml` | Python dependencies and project config |
| `.env.example` | Environment variables template |
| `Makefile` | Development shortcuts |

### Source Code (`src/warmit/`)

| Directory | Purpose |
|-----------|---------|
| `api/` | FastAPI REST endpoints |
| `models/` | SQLAlchemy database models |
| `services/` | Business logic and core features |
| `tasks/` | Celery background tasks |
| `utils/` | Helper functions and utilities |

### Key Services

| Service | File | Purpose |
|---------|------|---------|
| **Domain Checker** | `services/domain_checker.py` | WHOIS/RDAP analysis |
| **AI Generator** | `services/ai_generator.py` | Content generation |
| **Email Service** | `services/email_service.py` | SMTP/IMAP operations |
| **Scheduler** | `services/scheduler.py` | Warming schedule logic |
| **Response Bot** | `services/response_bot.py` | Auto-reply system |
| **Health Monitor** | `services/health_monitor.py` | System health checks |

### Frontend

| File | Purpose |
|------|---------|
| `dashboard/app.py` | Streamlit web interface (500+ lines) |

### Deployment

| File | Purpose |
|------|---------|
| `docker/docker-compose.prod.yml` | Production Docker setup |
| `docker/Dockerfile` | API/Worker container |
| `docker/Dockerfile.dashboard` | Dashboard container |

### Documentation

| File | Purpose |
|------|---------|
| `docs/QUICKSTART.md` | 5-minute setup guide |
| `docs/PRODUCTION.md` | Production deployment |
| `docs/USAGE.md` | Complete usage guide |
| `docs/FAQ.md` | Troubleshooting |
| `docs/FEATURES.md` | Feature list |

## 🔧 Configuration Files

### Environment (`.env`)
```bash
# AI Provider
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Database
DATABASE_URL=postgresql+asyncpg://...
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_URL=redis://redis:6379/0
```

### Python (`pyproject.toml`)
- Dependencies (Poetry format)
- Black/Ruff configuration
- MyPy settings
- Build configuration

### Docker (`docker/docker-compose.prod.yml`)
- 7 services (API, Worker, Beat, Dashboard, Watchdog, Redis, PostgreSQL)
- Health checks
- Restart policies
- Resource limits
- Volume mounts

## 📊 Data Flow

```
User → Dashboard (8501) → API (8000) → Database (PostgreSQL)
                            ↓
                         Redis ← Celery Worker
                            ↓
                         SMTP/IMAP (Email Providers)
                            ↑
                         Watchdog (Monitoring)
```

## 🗂️ Database Schema

| Table | Purpose |
|-------|---------|
| `accounts` | Email accounts (sender/receiver) |
| `campaigns` | Warming campaigns |
| `emails` | Email tracking records |
| `metrics` | Daily statistics |

## 🔄 Task Queue

| Task | Schedule | Purpose |
|------|----------|---------|
| `process_campaigns` | Every 2 hours | Send warming emails |
| `process_responses` | Every 30 min | Handle received emails |
| `reset_daily_counters` | Midnight | Reset daily limits |
| `update_metrics` | 11:59 PM | Update statistics |

## 🚀 Startup Flow

### Production (`./start.sh`)
```
1. Check Docker
2. Check .env
3. Pull images
4. Build custom images
5. Start services (docker compose up -d)
6. Wait for health checks
7. Display access URLs
```

### Development (`make dev`)
```
1. Start Redis
2. Start PostgreSQL
3. Start API (uvicorn)
4. Start Celery worker
5. Start Celery beat
6. Start Dashboard (streamlit)
```

## 📦 Dependencies

### Core
- FastAPI - Web framework
- SQLAlchemy - ORM
- Celery - Task queue
- Redis - Message broker
- PostgreSQL - Database

### Services
- aiosmtplib - Async SMTP
- aioimap - Async IMAP
- python-whois - Domain checking
- openai - AI integration

### UI
- Streamlit - Dashboard
- Plotly - Charts

### Development
- pytest - Testing
- black - Formatting
- ruff - Linting
- mypy - Type checking

## 🔐 Security

| Aspect | Implementation |
|--------|----------------|
| Secrets | Environment variables |
| Database | Encrypted connections |
| API | CORS configured |
| Docker | Isolated networks |
| Logs | No passwords logged |

## 📈 Scalability

### Horizontal Scaling
- Multiple Celery workers
- API worker processes
- Database read replicas

### Vertical Scaling
- Increase resource limits
- More CPU/RAM per container

## 🎓 Learning Path

1. **Start Here**: README.md
2. **Quick Setup**: docs/QUICKSTART.md
3. **Core Code**: src/warmit/services/
4. **API**: src/warmit/api/
5. **Dashboard**: dashboard/app.py
6. **Tasks**: src/warmit/tasks/
7. **Production**: docs/PRODUCTION.md

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style
- Testing
- Pull request process

---

**Well-organized and ready for scale! 🚀**
