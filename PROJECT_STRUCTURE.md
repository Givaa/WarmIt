# 📁 WarmIt - Project Structure

Quick reference guide to navigate the codebase.

---

## 🗂️ Root Directory

```
warmit/
├── 📄 README.md                    # Main project documentation
├── 📄 CHANGELOG.md                 # Version history and changes
├── 📄 TODO.md                      # Roadmap and future features
├── 📄 PROJECT_STRUCTURE.md         # This file
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 pyproject.toml               # Python dependencies (Poetry)
├── 🔧 warmit.sh                    # Main startup script
│
├── 📂 src/warmit/                  # Main application code
├── 📂 dashboard/                   # Streamlit web dashboard
├── 📂 docker/                      # Docker configuration
├── 📂 scripts/                     # Utility scripts
├── 📂 config/                      # Configuration profiles
└── 📂 docs/                        # Documentation
```

---

## 📂 Application Code (`src/warmit/`)

### Core Modules

```
src/warmit/
├── 📄 __init__.py
├── 📄 main.py                      # FastAPI application entry point
├── 📄 config.py                    # Configuration management (Pydantic)
├── 📄 database.py                  # Database connection and session
├── 📄 tasks.py                     # Celery task definitions
│
├── 📂 models/                      # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── base.py                     # Base model with common fields
│   ├── account.py                  # Email account model
│   ├── campaign.py                 # Campaign model
│   ├── email.py                    # Email message model
│   └── metric.py                   # Metrics model
│
├── 📂 api/                         # FastAPI routes
│   ├── __init__.py
│   ├── accounts.py                 # Account CRUD endpoints
│   ├── campaigns.py                # Campaign CRUD endpoints
│   ├── metrics.py                  # Metrics endpoints
│   ├── test.py                     # Quick test endpoints
│   └── health.py                   # Health check endpoints
│
└── 📂 services/                    # Business logic
    ├── __init__.py
    ├── ai_generator.py             # 🔥 AI email generation (OpenRouter/Groq)
    ├── scheduler.py                # Campaign email scheduler
    ├── response_bot.py             # Auto-reply bot
    ├── domain_checker.py           # WHOIS/RDAP domain analysis
    ├── email_sender.py             # SMTP email sending
    ├── email_receiver.py           # IMAP email receiving
    ├── encryption.py               # 🔐 Password encryption (Fernet)
    ├── config_profiles.py          # 📋 Configuration profile manager
    └── rate_limit_tracker.py       # 💰 API rate limit tracking
```

### Key Files Explained

**`ai_generator.py`** (350 lines)
- Multiple AI provider support (OpenRouter, Groq, OpenAI)
- Automatic failover between providers
- Local template generation (42,875+ combinations)
- Retry logic with exponential backoff

**`encryption.py`** (128 lines)
- Fernet symmetric encryption for passwords
- Automatic encrypt on save, decrypt on load
- Global encryption service singleton
- Migration support

**`config_profiles.py`** (200 lines)
- Loads YAML configuration profiles
- Automatic profile selection based on scale
- Apply profile settings to environment
- Small/Medium/Large/Enterprise presets

**`rate_limit_tracker.py`** (330 lines)
- Real-time API request tracking
- RPM (requests per minute) and RPD (requests per day)
- Saturation forecasting
- Per-provider status tracking

---

## 📂 Dashboard (`dashboard/`)

```
dashboard/
├── 📄 app.py                       # Main Streamlit application
├── 📄 auth.py                      # 🔐 Authentication module
├── 📄 email_providers.py           # 20+ email provider configs
│
└── 📂 pages/                       # Dashboard pages (modular)
    ├── __init__.py
    └── api_costs.py                # 💰 API cost monitoring page
```

### Dashboard Pages

1. **📊 Dashboard** - Overview with metrics and charts
2. **📧 Accounts** - Manage sender/receiver accounts
3. **🎯 Campaigns** - Create and monitor campaigns
4. **📈 Analytics** - Historical data and trends
5. **➕ Add New** - Add accounts and create campaigns
6. **🧪 Quick Test** - Test emails immediately
7. **🧮 Estimate** - Resource estimation tool
8. **💰 API Costs** - Rate limit monitoring (NEW!)
9. **⚙️ Settings** - Change password, logout, about

---

## 📂 Configuration (`config/`)

```
config/
└── 📂 profiles/                    # Configuration presets
    ├── small.yaml                  # 1-10 accounts (2GB RAM, 1 CPU)
    ├── medium.yaml                 # 10-50 accounts (4GB RAM, 2 CPU)
    ├── large.yaml                  # 50-200 accounts (8GB RAM, 4 CPU)
    └── enterprise.yaml             # 200+ accounts (16GB RAM, 8 CPU)
```

Each profile includes:
- Resource limits (RAM, CPU, storage)
- Worker configuration (Celery workers, concurrency)
- Database pooling (connections, pool size)
- API rate limits (RPM, RPD per provider)
- Safety settings (bounce rate, auto-pause)
- Recommendations

---

## 📂 Docker (`docker/`)

```
docker/
├── 📄 Dockerfile                   # Main application image
├── 📄 Dockerfile.dashboard         # Dashboard image
├── 📄 docker-compose.prod.yml      # Production deployment
├── 📄 .env                         # Environment variables (gitignored)
│
└── 📂 logs/                        # Container logs (gitignored)
```

### Services in docker-compose

1. **postgres** - PostgreSQL database
2. **redis** - Redis cache/queue
3. **api** - FastAPI application
4. **worker** - Celery worker
5. **beat** - Celery beat scheduler
6. **dashboard** - Streamlit dashboard
7. **watchdog** - Health monitoring
8. **logs** - Dozzle log viewer

---

## 📂 Scripts (`scripts/`)

```
scripts/
├── 📄 migrate_add_names.py         # Database migration (add first/last names)
├── 📄 migrate_encrypt_passwords.py # Database migration (encrypt passwords)
├── 📄 estimate_resources.py        # 🧮 Resource estimation CLI tool
├── 📄 watchdog.py                  # Container health monitoring
```

---

## 📂 Documentation (`docs/`)

```
docs/
├── 📄 README.md                            # Documentation index
├── 📄 SECURITY_SETUP.md                    # 🔐 Security guide
└── 📄 RESOURCE_ESTIMATION.md               # 🧮 Resource planning guide
```

---

## 🔑 Key Files by Feature

### Authentication & Security
- `dashboard/auth.py` - Dashboard login/password management
- `src/warmit/services/encryption.py` - Database encryption
- `scripts/migrate_encrypt_passwords.py` - Encrypt existing data
- `dashboard/.auth` - Hashed admin password (gitignored)

### AI Email Generation
- `src/warmit/services/ai_generator.py` - Main AI service
- Multiple provider support + local fallback
- Template library with 42,875+ combinations

### Resource Planning
- `scripts/estimate_resources.py` - CLI estimation tool
- `dashboard/app.py` (line 956+) - Dashboard page
- `config/profiles/*.yaml` - Configuration presets

### API Rate Limiting
- `src/warmit/services/rate_limit_tracker.py` - Tracking service
- `dashboard/pages/api_costs.py` - Monitoring dashboard
- Real-time RPM/RPD tracking with forecasting

### Configuration Profiles
- `config/profiles/*.yaml` - YAML profile definitions
- `src/warmit/services/config_profiles.py` - Profile manager
- Automatic selection based on deployment scale

---

## 🎯 Common Tasks & Files

**Add a new email provider:**
- Edit `dashboard/email_providers.py`
- Add provider config with SMTP/IMAP settings

**Add a new dashboard page:**
- Create `dashboard/pages/your_page.py`
- Import and call `render_your_page()` in `dashboard/app.py`

**Add a new API endpoint:**
- Create route in `src/warmit/api/your_endpoint.py`
- Register router in `src/warmit/main.py`

**Add a new Celery task:**
- Define task in `src/warmit/tasks.py`
- Configure schedule in `tasks.py` celery beat schedule

**Modify database schema:**
- Edit model in `src/warmit/models/`
- Create migration script in `scripts/migrate_*.py`

**Add a new configuration profile:**
- Create `config/profiles/your_profile.yaml`
- Follow existing profile structure
- Will be auto-loaded by `config_profiles.py`

---

## 📝 Code Statistics

**Total Lines of Code:** ~15,000+

**By Module:**
- `src/warmit/` - ~8,000 lines
- `dashboard/` - ~2,500 lines
- `scripts/` - ~1,500 lines
- `config/` - ~400 lines
- `docs/` - ~3,000 lines

**New in v0.2.0:**
- Authentication: ~430 lines
- Encryption: ~230 lines
- Configuration Profiles: ~600 lines
- Rate Limit Tracking: ~610 lines
- Resource Estimation: ~730 lines

**Total Added:** ~2,600 lines

---

## 🔍 Finding Your Way Around

**Looking for:**
- 🔐 **Security features?** → `dashboard/auth.py`, `src/warmit/services/encryption.py`
- 🤖 **AI generation?** → `src/warmit/services/ai_generator.py`
- 📊 **Metrics/analytics?** → `src/warmit/api/metrics.py`, `src/warmit/models/metric.py`
- ⚙️ **Configuration?** → `config/profiles/`, `src/warmit/config.py`
- 📧 **Email sending?** → `src/warmit/services/email_sender.py`
- 🎯 **Campaign logic?** → `src/warmit/services/scheduler.py`
- 💰 **Rate limits?** → `src/warmit/services/rate_limit_tracker.py`
- 📱 **Dashboard UI?** → `dashboard/app.py`, `dashboard/pages/`
- 🐳 **Docker setup?** → `docker/docker-compose.prod.yml`
- 📚 **Documentation?** → `docs/README.md`

---

**Last Updated:** 2026-01-15
**Version:** 0.2.0-dev
