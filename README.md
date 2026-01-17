# WarmIt 🔥

**Enterprise-grade email warming tool with AI-powered content generation and failsafe architecture.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

> **Warm up email accounts progressively to achieve 95%+ inbox placement rate**

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Clone
git clone https://github.com/Givaa/warmit.git
cd warmit

# 2. Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 3. Configure environment
cp .env.example docker/.env
# Edit docker/.env:
# - Add your API keys (OpenRouter/Groq)
# - Add ENCRYPTION_KEY from step 2

# 4. Start services
./warmit.sh start

# 5. Get admin password
docker logs warmit-dashboard | grep "Admin Password"
```

**That's it!** ✨

**Access:**
- 📊 **Dashboard:** http://localhost (via Nginx on port 80)
- 📝 **Logs:** http://localhost:8888 (localhost only)
- 🔌 **API:** Internal only (secured behind Nginx)
- 📖 **API Docs:** Not exposed (security)

**Management:**
```bash
./warmit.sh help      # Show help menu
./warmit.sh start     # Start all services
./warmit.sh stop      # Stop all services
./warmit.sh restart   # Restart all services
./warmit.sh down      # Stop and remove containers
./warmit.sh reset     # ⚠️  Delete all data (use with caution!)
```

### Windows Users

WarmIt works on Windows with **Git Bash** (included with [Git for Windows](https://git-scm.com/download/win)):

```bash
# Open Git Bash terminal, then:
cd /c/path/to/warmit
bash warmit.sh start
```

**Requirements:**
- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows/)
- [Git for Windows](https://git-scm.com/download/win) (includes Git Bash)
- Python 3.11+ (for encryption key generation)

---

## ✨ What is WarmIt?

WarmIt progressively warms email accounts to build sender reputation and achieve inbox placement. Perfect for:

- 🆕 New domains (< 30 days old)
- 📧 Cold email campaigns
- 🔄 Domain reputation recovery
- 📈 Improving deliverability rates

### The Problem

- New domains → Spam folder
- Sudden high volume → Blocked
- No engagement history → Low reputation

### The Solution

WarmIt automatically:
1. Checks domain age
2. Creates optimal warming schedule (2-8 weeks)
3. Generates natural AI conversations
4. Auto-responds to build engagement
5. Monitors and recovers from issues

**Result:** 95%+ inbox placement 📨✅

---

## 🎯 Key Features

### 🔥 Core Email Warming
- ✅ Multi-account warming (unlimited scale)
- ✅ AI content generation (OpenRouter/Groq/OpenAI)
- ✅ Multiple API keys with automatic fallback
- ✅ Local template generation (42,875+ combinations)
- ✅ Progressive volume scheduling (5 → 80 emails/day)
- ✅ Auto-response system with human-like timing
- ✅ Domain age analysis (WHOIS/RDAP)
- ✅ **Auto-configuration for 20+ email providers**

### 🔐 Security & Infrastructure
- ✅ **Dashboard authentication** (auto-generated passwords)
- ✅ **Database encryption** (Fernet, automatic encrypt/decrypt)
- ✅ PostgreSQL default (production-ready)
- ✅ Secure credential storage
- ✅ Password change UI
- ✅ Session-based auth

### 📊 Planning & Monitoring
- ✅ **Resource estimation tool** (CLI + Dashboard)
- ✅ **Dynamic configuration profiles** (Small/Medium/Large/Enterprise)
- ✅ **API cost & rate limit dashboard** (real-time tracking)
- ✅ Saturation forecasting (know when limits will be hit)
- ✅ Docker Compose config generator
- ✅ Optimization recommendations

### 🏢 Enterprise Features
- ✅ Web dashboard (Streamlit)
- ✅ Auto-restart on failure
- ✅ Health monitoring (30s checks)
- ✅ Watchdog auto-recovery (5min)
- ✅ Resource limits & log rotation
- ✅ Data persistence (PostgreSQL + Redis)
- ✅ Multi-worker support (Celery)

### 📈 Analytics
- ✅ Real-time metrics
- ✅ Interactive charts (Plotly)
- ✅ Per-account tracking
- ✅ Per-campaign tracking
- ✅ 30-day history
- ✅ Open/Reply/Bounce rates
- ✅ API usage tracking

---

## 📧 Email Provider Auto-Configuration

**No more searching for SMTP settings!** Just type your email and everything auto-fills:

```
Type: mario@libero.it
↓ Auto-detects Libero Mail
SMTP: smtp.libero.it:587 ✓
IMAP: imapmail.libero.it:993 ✓
```

**Supported providers (20+):**
- 🇮🇹 Italian: Libero, Virgilio, Aruba, TIM, Fastweb, Tiscali
- 🌍 International: Gmail, Outlook, Yahoo, iCloud, AOL, ProtonMail, Zoho

**How it works:**
1. Dashboard → "Add Account"
2. Select provider from dropdown OR let it auto-detect
3. Enter email → settings auto-fill ✨
4. Shows helpful notes (e.g., "Gmail needs App Password")
5. All fields editable for custom configs

**Example notes shown:**
- **Gmail**: "Use App Password. Enable 2FA first, then create in Google Account settings"
- **Aruba**: "Port 465 with SSL (not 587 TLS). For PEC use pec.aruba.it"
- **Yahoo**: "Generate App Password in Account Security"

---

## 📊 Warming Strategy

| Week | New Domain | Mid-Age | Established |
|------|------------|---------|-------------|
| 1 | 3/day | 5/day | 20/day |
| 2 | 5/day | 10/day | 50/day |
| 3 | 8/day | 15/day | 50/day |
| 4 | 13/day | 25/day | - |
| 5 | 18/day | 35/day | - |
| 6+ | 23-43/day | 50/day | - |

**Automatically adjusted based on domain age!**

---

## 🛡️ Failsafe Features

- **Auto-restart**: All services restart on crash
- **Health checks**: Every 30s via Docker
- **Watchdog**: Auto-recovery every 5min
- **Resource limits**: Prevents OOM crashes
- **Log rotation**: Automatic cleanup
- **Data persistence**: Survives restarts

**Can run for months without manual intervention!**

---

## 🎯 Management

```bash
./warmit.sh          # Start all services
./warmit.sh restart  # Restart
./warmit.sh stop     # Stop (keep data)
./warmit.sh down     # Remove containers
./warmit.sh logs     # View all logs
./warmit.sh status   # Check service status
./warmit.sh health   # Check API health
./warmit.sh db-shell # Open PostgreSQL shell
```

---

## 🏗️ Architecture

```
Internet
    │
    ▼
┌─────────────────────────────────────┐
│        Nginx (port 80/443)          │
├─────────────────────────────────────┤
│ /              → Dashboard (8501)   │  ← Protected by login
│ /track/*       → API (8000)         │  ← Requires valid HMAC token
│ /api/*         → BLOCKED            │  ← Not accessible
└─────────────────────────────────────┘
    │                    │
    ▼                    ▼
Dashboard ──► API ──► PostgreSQL
              │
              ├──► Redis ◄──► Celery Worker
              │                    │
              └──► Watchdog ◄──────┘

Logs (Dozzle) → localhost:8888 (local only)
```

**Tech:** Python 3.11, FastAPI, Streamlit, Celery, PostgreSQL, Redis, Nginx, Docker

---

## 📈 Performance

| Accounts | Emails/Day | RAM | CPU |
|----------|------------|-----|-----|
| 1-10 | 100-500 | 4GB | 2 cores |
| 10-50 | 500-2.5K | 8GB | 4 cores |
| 50-100 | 2.5-5K | 16GB | 8 cores |
| 100+ | 5K+ | 32GB+ | 16+ cores |

---

## 📚 Documentation

**Getting Started:**
- 📖 [Complete Documentation Index](docs/README.md) - All guides in one place
- 🔐 [Security Setup Guide](docs/SECURITY_SETUP.md) - Authentication & encryption
- 🧮 [Resource Estimation](docs/RESOURCE_ESTIMATION.md) - Campaign planning tool

**Setup Guides:**
- 🔑 [API Keys Setup](docs/setup/API_KEYS.md) - Configure AI providers
- 📊 [Tracking Setup](docs/setup/TRACKING_SETUP.md) - Email tracking configuration

**Project Documentation:**
- 🗺️ [Project Structure](docs/PROJECT_STRUCTURE.md) - Complete codebase map
- 📋 [Changelog](docs/changelog/CHANGELOG.md) - Version history and changes
- 📝 [TODO](docs/TODO.md) - Roadmap and future features
- 🔧 [Implementation Notes](docs/guides/IMPLEMENTATION_NOTES.md) - Technical details
- ⬆️ [Upgrade Guide v0.2.2](docs/guides/UPGRADE_TO_v0.2.2.md) - Migration instructions

**Configuration:**
- ⚙️ [Environment Variables](.env.example) - All configuration options
- 📋 [Configuration Profiles](config/profiles/) - Small/Medium/Large/Enterprise presets
- 🐳 [Docker Compose](docker/docker-compose.prod.yml) - Production deployment
- 🔧 [Scripts Documentation](scripts/README.md) - Utility scripts guide

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Last Updated:** 2026-01-17 | **Version:** 1.0.3
