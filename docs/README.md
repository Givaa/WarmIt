# 📚 WarmIt Documentation

Complete documentation for WarmIt email warming platform.

---

## 📖 Table of Contents

### Getting Started
- [Main README](../README.md) - Project overview and quick start
- [Security Setup Guide](SECURITY_SETUP.md) - Authentication & encryption setup
- [Resource Estimation](RESOURCE_ESTIMATION.md) - Planning campaigns and infrastructure

### Setup Guides
- [API Keys Setup](setup/API_KEYS.md) - Configure AI providers (OpenRouter/Groq/OpenAI)
- [Tracking Setup](setup/TRACKING_SETUP.md) - Email tracking pixel configuration

### Configuration
- [Environment Variables](../.env.example) - All configuration options
- [Configuration Profiles](../config/profiles/) - Small/Medium/Large/Enterprise presets
- [Docker Compose](../docker/docker-compose.prod.yml) - Production deployment

### Developer Documentation
- [Developer Guide](developer/README.md) - Complete developer reference
- [Models Reference](developer/MODELS.md) - SQLAlchemy models documentation
- [Services Reference](developer/SERVICES.md) - Business logic services
- [API Reference](developer/API_REFERENCE.md) - REST API endpoints *(coming soon)*
- [Task System](developer/TASK_SYSTEM.md) - Celery tasks *(coming soon)*

### Project Documentation
- [Project Structure](PROJECT_STRUCTURE.md) - Complete codebase map
- [Changelog](changelog/CHANGELOG.md) - All changes and versions
- [Changelog v0.2.2](changelog/CHANGELOG_v0.2.2.md) - Latest version changes
- [TODO](TODO.md) - Roadmap and future features
- [Implementation Notes](guides/IMPLEMENTATION_NOTES.md) - Technical implementation details
- [Upgrade Guide v0.2.2](guides/UPGRADE_TO_v0.2.2.md) - Migration instructions
- [Scripts Documentation](../scripts/README.md) - Utility scripts guide

---

## 🚀 Quick Links

### Common Tasks

**Setup & Installation:**
```bash
# Clone repo
git clone https://github.com/yourusername/warmit.git
cd warmit

# Setup environment
cp .env.example docker/.env
# Edit docker/.env with your settings

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Add to docker/.env as ENCRYPTION_KEY

# Start services
./warmit.sh start

# Check dashboard logs for admin password
docker logs warmit-dashboard | grep "Admin Password"

# Open dashboard
open http://localhost:8501
```

**Add Accounts:**
1. Login to dashboard
2. Go to "➕ Add New" → "Add Account"
3. Select provider or use auto-detect
4. Fill in email and password (use App Password for Gmail/Yahoo)
5. Click "Add Account"

**Create Campaign:**
1. Go to "➕ Add New" → "Create Campaign"
2. Select sender and receiver accounts
3. Set duration (default 6 weeks)
4. Click "Create Campaign"

**Estimate Resources:**
1. Go to "🧮 Estimate"
2. Enter number of senders/receivers/weeks
3. View resource requirements and docker-compose config
4. Use presets for quick estimates

**Monitor API Usage:**
1. Go to "💰 API Costs"
2. View real-time rate limit status
3. Check saturation forecasts
4. Get optimization recommendations

---

## 📋 Documentation Index

### Core Concepts

**Email Warming:**
- Progressive volume increase (5 → 80 emails/day over 6 weeks)
- Human-like timing with randomization
- Automated replies between accounts
- Domain reputation building

**AI Generation:**
- Multiple provider support (OpenRouter, Groq, OpenAI)
- Automatic fallback chain
- Local template generation
- 42,875+ unique combinations

**Security:**
- Dashboard authentication with auto-generated passwords
- Database encryption (Fernet)
- Password hashing (SHA-256 + salt)
- Secure credential storage

**Infrastructure:**
- PostgreSQL for production reliability
- Redis for task queue
- Celery for async processing
- Docker Compose for easy deployment

**Monitoring:**
- Real-time API rate limit tracking
- Resource usage estimation
- Campaign progress tracking
- Performance analytics

---

## 🎯 Feature Guides

### 1. Security Setup
See: [SECURITY_SETUP.md](SECURITY_SETUP.md)

- Generate encryption key
- Set up dashboard authentication
- Migrate existing databases
- Best practices

### 2. Resource Estimation
See: [RESOURCE_ESTIMATION.md](RESOURCE_ESTIMATION.md)

- CLI usage for automation
- Dashboard interactive estimator
- Configuration profiles
- Docker compose optimization

### 3. Configuration Profiles
Location: `config/profiles/`

**Profiles:**
- **Small** (1-10 accounts): 2GB RAM, 1 CPU, dev/test
- **Medium** (10-50 accounts): 4GB RAM, 2 CPU, small business
- **Large** (50-200 accounts): 8GB RAM, 4 CPU, enterprise
- **Enterprise** (200+ accounts): 16GB RAM, 8 CPU, large scale

Each profile includes:
- Resource limits (RAM, CPU, storage)
- Worker configuration (Celery workers, concurrency)
- Database pooling (connections, pool size)
- API rate limits (RPM, RPD)
- Safety settings (bounce rate, auto-pause)
- Recommendations specific to scale

### 4. API Rate Limiting
See: [API Costs Dashboard](../dashboard/pages/api_costs.py) implementation

**Rate Limits (Free Tier):**
- OpenRouter: 20 RPM, 50-1K RPD
- Groq: 30 RPM, ~1K RPD
- Automatic tracking and failover

**Monitoring:**
- Real-time utilization tracking
- Saturation forecasting
- Automatic provider switching
- Local fallback when exhausted

---

## 🔧 Technical Details

### Architecture

```
┌─────────────┐
│  Dashboard  │  (Streamlit, Port 8501)
│  (Web UI)   │
└──────┬──────┘
       │
       v
┌─────────────┐     ┌──────────┐     ┌───────────┐
│     API     │────▶│PostgreSQL│     │   Redis   │
│  (FastAPI)  │     │ (Database│◀────│  (Queue)  │
└──────┬──────┘     └──────────┘     └─────┬─────┘
       │                                     │
       v                                     v
┌─────────────┐                      ┌─────────────┐
│   Celery    │                      │   Celery    │
│   Worker    │                      │    Beat     │
│ (Async Jobs)│                      │ (Scheduler) │
└─────────────┘                      └─────────────┘
```

### Tech Stack

**Backend:**
- Python 3.11
- FastAPI (API framework)
- SQLAlchemy (ORM)
- Celery (task queue)
- Pydantic (validation)

**Frontend:**
- Streamlit (dashboard)
- Plotly (charts)
- Pandas (data processing)

**Infrastructure:**
- PostgreSQL 16 (database)
- Redis 7 (cache/queue)
- Docker & Docker Compose

**AI/ML:**
- OpenAI SDK (compatible with OpenRouter/Groq)
- Multiple provider support
- Local template fallback

**Email:**
- aiosmtplib (SMTP)
- aioimap (IMAP)
- Email validation
- WHOIS/RDAP integration

---

## 📊 Implementation Timeline

### Version 0.1.0 (2026-01-14)
- Initial release
- Core email warming functionality
- Dashboard and API
- Docker deployment

### Version 0.1.1 (2026-01-15 - Session 1)
- Renamed start.sh → warmit.sh
- Sender name integration in emails
- Multiple API keys with automatic fallback
- Local template generation (42,875+ combinations)
- Enhanced error handling

### Version 0.2.0 (2026-01-15 - Session 2)
- **Security:** Dashboard authentication + database encryption
- **Infrastructure:** PostgreSQL as default
- **Planning:** Resource estimation tool
- **Configuration:** Dynamic profiles (Small/Medium/Large/Enterprise)
- **Monitoring:** API cost & rate limit tracking dashboard

---

## 🐛 Troubleshooting

### Common Issues

**Problem:** Dashboard shows "API Offline"
**Solution:** Ensure API container is running: `docker ps | grep warmit-api`

**Problem:** "ENCRYPTION_KEY not set" warning
**Solution:** Generate key and add to `.env`:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Problem:** Cannot decrypt passwords
**Solution:** Check ENCRYPTION_KEY matches the one used to encrypt

**Problem:** Rate limit errors
**Solution:** Check "💰 API Costs" page, add more API keys, or upgrade to paid tier

**Problem:** High bounce rate
**Solution:** Reduce send volume, check email content, verify SMTP settings

### Logs

```bash
# View all logs
docker logs warmit-dashboard
docker logs warmit-api
docker logs warmit-worker

# Follow logs in real-time
docker logs -f warmit-api

# Web-based log viewer (Dozzle)
open http://localhost:8888
```

---

## 📄 License

See [LICENSE](../LICENSE) file for details.

---

**Last Updated:** 2026-01-15
**Documentation Version:** 0.2.0
