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
│
├── 📂 models/                      # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── base.py                     # Base model with common fields
│   ├── account.py                  # Email account model
│   ├── campaign.py                 # Campaign model (with language support)
│   ├── email.py                    # Email message model
│   └── metric.py                   # Metrics model
│
├── 📂 api/                         # FastAPI routes
│   ├── __init__.py
│   ├── accounts.py                 # Account CRUD endpoints
│   ├── campaigns.py                # Campaign CRUD endpoints (multilingual)
│   ├── metrics.py                  # Metrics endpoints
│   └── test.py                     # Quick test endpoints (multilingual)
│
├── 📂 services/                    # Business logic
│   ├── __init__.py
│   ├── ai_generator.py             # 🔥 AI email generation (EN/IT, OpenRouter/Groq)
│   ├── scheduler.py                # Campaign email scheduler (multilingual)
│   ├── response_bot.py             # Auto-reply bot (multilingual)
│   ├── domain_checker.py           # WHOIS/RDAP domain analysis
│   ├── email_service.py            # SMTP/IMAP email service (multipart emails)
│   ├── encryption.py               # 🔐 Password encryption (Fernet)
│   ├── config_profiles.py          # 📋 Configuration profile manager
│   ├── rate_limit_tracker.py       # 💰 API rate limit tracking
│   └── health_monitor.py           # 🏥 System health monitoring
│
├── 📂 tasks/                       # Celery background tasks
│   ├── __init__.py
│   ├── warming.py                  # Warming campaign tasks
│   └── response.py                 # Response bot tasks
│
└── 📂 utils/                       # Utility functions
    └── __init__.py
```

### Key Files Explained

**`ai_generator.py`** (~600 lines)
- **NEW:** Bilingual support (English & Italian)
- Multiple AI provider support (OpenRouter, Groq, OpenAI)
- Automatic failover between providers
- Local template generation (42,875+ combinations per language)
- Retry logic with exponential backoff
- Language-specific templates for emails and replies

**`email_service.py`** (~355 lines)
- **NEW:** Multipart email support (HTML + plain text)
- SMTP email sending with TLS/SSL support
- IMAP email receiving and parsing
- Connection testing
- Mark emails as read

**`scheduler.py`** (~388 lines)
- **NEW:** Campaign language support
- Progressive email warmup
- Domain age-based duration calculation
- Daily target calculation
- Bounce rate monitoring

**`response_bot.py`** (~281 lines)
- **NEW:** Multilingual auto-replies
- Campaign language detection
- IMAP email fetching
- Intelligent reply generation
- Human-like delay simulation

**`encryption.py`** (~128 lines)
- Fernet symmetric encryption for passwords
- Automatic encrypt on save, decrypt on load
- Global encryption service singleton
- Migration support

**`config_profiles.py`** (~200 lines)
- Loads YAML configuration profiles
- Automatic profile selection based on scale
- Apply profile settings to environment
- Small/Medium/Large/Enterprise presets

**`rate_limit_tracker.py`** (~330 lines)
- Real-time API request tracking
- RPM (requests per minute) and RPD (requests per day)
- Saturation forecasting
- Per-provider status tracking

**`health_monitor.py`** (~250 lines)
- Database, Redis, API health checks
- Auto-recovery mechanisms
- Detailed health reporting
- Service status monitoring

---

## 📂 Dashboard (`dashboard/`)

```
dashboard/
├── 📄 app.py                       # Main Streamlit application (multilingual UI)
├── 📄 auth.py                      # 🔐 Authentication module
└── 📄 email_providers.py           # 20+ email provider configs
```

### Dashboard Pages

1. **📊 Dashboard** - Overview with metrics and charts
2. **📧 Accounts** - Manage sender/receiver accounts
3. **🎯 Campaigns** - Create and monitor campaigns (with language selector 🇬🇧🇮🇹)
4. **📈 Analytics** - Historical data and trends
5. **➕ Add New** - Add accounts and create campaigns
6. **🧪 Quick Test** - Test emails immediately (multilingual)
7. **🧮 Estimate** - Resource estimation tool
8. **⚙️ Settings** - Change password, logout, about

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
├── 📄 docker-compose.yml           # Development deployment
├── 📄 .env                         # Environment variables (gitignored)
│
└── 📂 logs/                        # Container logs (gitignored)
```

### Services in docker-compose

1. **postgres** - PostgreSQL database
2. **redis** - Redis cache/queue
3. **api** - FastAPI application
4. **worker** - Celery worker (email processing)
5. **beat** - Celery beat scheduler (cron jobs)
6. **dashboard** - Streamlit dashboard
7. **watchdog** - Health monitoring service
8. **logs** - Dozzle log viewer (web UI)

---

## 📂 Scripts (`scripts/`)

```
scripts/
├── 📄 README.md                    # Scripts documentation
├── 📄 cli.py                       # Command-line interface
├── 📄 migrate_add_names.py         # Database migration (add first/last names)
├── 📄 migrate_encrypt_passwords.py # Database migration (encrypt passwords)
├── 📄 estimate_resources.py        # 🧮 Resource estimation CLI tool
├── 📄 watchdog.py                  # Container health monitoring
│
└── 📂 migrations/                  # Database migrations
    ├── README.md                   # Migration documentation
    └── 001_add_campaign_language.sql  # Add language field to campaigns
```

---

## 📂 Documentation (`docs/`)

```
docs/
├── 📄 README.md                    # Documentation index
├── 📄 SECURITY_SETUP.md            # 🔐 Security guide
└── 📄 RESOURCE_ESTIMATION.md       # 🧮 Resource planning guide
```

---

## 🔑 Key Files by Feature

### Multilingual Support (NEW in v0.2.1)
- `src/warmit/models/campaign.py` - Language field in Campaign model
- `src/warmit/services/ai_generator.py` - Bilingual templates (EN/IT)
- `src/warmit/services/scheduler.py` - Campaign language integration
- `src/warmit/services/response_bot.py` - Multilingual auto-replies
- `src/warmit/api/campaigns.py` - Language parameter in API
- `src/warmit/api/test.py` - Language parameter for quick tests
- `dashboard/app.py` - Language selectors (🇬🇧🇮🇹) in UI
- `scripts/migrations/001_add_campaign_language.sql` - DB migration

### Email Handling
- `src/warmit/services/email_service.py` - SMTP/IMAP service
- Multipart emails (HTML + plain text)
- Proper newline handling (no more `\n` in emails!)
- Connection testing and health checks

### Authentication & Security
- `dashboard/auth.py` - Dashboard login/password management
- `src/warmit/services/encryption.py` - Database encryption
- `scripts/migrate_encrypt_passwords.py` - Encrypt existing data
- `dashboard/.auth` - Hashed admin password (gitignored)

### AI Email Generation
- `src/warmit/services/ai_generator.py` - Main AI service
- Multiple provider support + local fallback
- Template library with 42,875+ combinations per language
- Bilingual support (English & Italian)

### Resource Planning
- `scripts/estimate_resources.py` - CLI estimation tool
- `dashboard/app.py` (Estimate page) - Dashboard page
- `config/profiles/*.yaml` - Configuration presets

### API Rate Limiting
- `src/warmit/services/rate_limit_tracker.py` - Tracking service
- Real-time RPM/RPD tracking with forecasting

### Configuration Profiles
- `config/profiles/*.yaml` - YAML profile definitions
- `src/warmit/services/config_profiles.py` - Profile manager
- Automatic selection based on deployment scale

### Health Monitoring
- `src/warmit/services/health_monitor.py` - System health checks
- `scripts/watchdog.py` - Container monitoring
- Auto-recovery mechanisms

---

## 🎯 Common Tasks & Files

**Add a new email provider:**
- Edit `dashboard/email_providers.py`
- Add provider config with SMTP/IMAP settings

**Add a new API endpoint:**
- Create route in `src/warmit/api/your_endpoint.py`
- Register router in `src/warmit/main.py`

**Add a new Celery task:**
- Define task in `src/warmit/tasks/your_task.py`
- Import in `src/warmit/tasks/__init__.py`

**Modify database schema:**
- Edit model in `src/warmit/models/`
- Create migration script in `scripts/migrations/`
- Apply migration manually or on next restart

**Add a new language:**
- Update `ai_generator.py` with new language templates
- Add language option in dashboard UI
- Update campaign model if needed

**Add a new configuration profile:**
- Create `config/profiles/your_profile.yaml`
- Follow existing profile structure
- Will be auto-loaded by `config_profiles.py`

---

## 📝 Code Statistics

**Total Lines of Code:** ~16,000+

**By Module:**
- `src/warmit/` - ~9,000 lines
- `dashboard/` - ~2,500 lines
- `scripts/` - ~1,500 lines
- `config/` - ~400 lines
- `docs/` - ~3,000 lines

**New in v0.2.1:**
- Multilingual support: ~800 lines
- Email service improvements: ~100 lines
- Database migrations: ~50 lines

---

## 🔍 Finding Your Way Around

**Looking for:**
- 🌐 **Multilingual support?** → `src/warmit/services/ai_generator.py`, `dashboard/app.py`
- 📧 **Email formatting?** → `src/warmit/services/email_service.py`
- 🔐 **Security features?** → `dashboard/auth.py`, `src/warmit/services/encryption.py`
- 🤖 **AI generation?** → `src/warmit/services/ai_generator.py`
- 📊 **Metrics/analytics?** → `src/warmit/api/metrics.py`, `src/warmit/models/metric.py`
- ⚙️ **Configuration?** → `config/profiles/`, `src/warmit/config.py`
- 🎯 **Campaign logic?** → `src/warmit/services/scheduler.py`
- 💰 **Rate limits?** → `src/warmit/services/rate_limit_tracker.py`
- 📱 **Dashboard UI?** → `dashboard/app.py`
- 🐳 **Docker setup?** → `docker/docker-compose.prod.yml`
- 🗄️ **Database migrations?** → `scripts/migrations/`
- 📚 **Documentation?** → `docs/README.md`

---

**Last Updated:** 2026-01-15
**Version:** 0.2.1-dev (Multilingual Support)
