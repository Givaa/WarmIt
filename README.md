# WarmIt 🔥

**Enterprise-grade email warming tool with AI-powered content generation and failsafe architecture.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

> **Warm up email accounts progressively to achieve 95%+ inbox placement rate**

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/Givaa/warmit.git
cd warmit

# 2. Start (it will guide you through configuration)
./start.sh

# The script will:
# - Create docker/.env from template
# - Prompt you to add your API key
# - Start all services automatically
```

**First time setup:**
1. Run `./start.sh`
2. Edit `docker/.env` when prompted
3. Add your OpenRouter or Groq API key
4. Press Enter to continue

**That's it!** ✨

**Access:**
- 📊 Dashboard: http://localhost:8501
- 📝 Logs (Web): http://localhost:8888
- 🔌 API: http://localhost:8000
- 📖 Docs: http://localhost:8000/docs

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

### Core
- ✅ Multi-account warming
- ✅ AI content generation (OpenRouter/Groq)
- ✅ Progressive volume scheduling
- ✅ Auto-response system
- ✅ Domain age analysis
- ✅ **Auto-configuration for 20+ email providers**

### Enterprise
- ✅ Web dashboard (Streamlit)
- ✅ Auto-restart on failure
- ✅ Health monitoring (30s checks)
- ✅ Watchdog auto-recovery (5min)
- ✅ Resource limits & log rotation
- ✅ Data persistence (PostgreSQL + Redis)

### Analytics
- ✅ Real-time metrics
- ✅ Interactive charts (Plotly)
- ✅ Per-account tracking
- ✅ 30-day history
- ✅ Open/Reply/Bounce rates

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

## 📖 Documentation

| Doc | Description |
|-----|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design & components |
| [FAQ](docs/FAQ.md) | Troubleshooting & common issues |

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
./start.sh          # Start all services
./start.sh restart  # Restart
./start.sh stop     # Stop (keep data)
./start.sh down     # Remove containers

# View logs
docker compose -f docker/docker-compose.prod.yml logs -f

# Check health
curl http://localhost:8000/health/detailed | jq
```

---

## 🏗️ Architecture

```
Dashboard (8501) ──► API (8000) ──► PostgreSQL
                        │
                        ├──► Redis ◄──► Celery Worker
                        │                    │
                        └──► Watchdog ◄──────┘
```

**Tech:** Python 3.11, FastAPI, Streamlit, Celery, PostgreSQL, Redis, Docker

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

- [Quick Start Guide](docs/QUICKSTART.md) - Detailed setup instructions
- [Architecture](docs/ARCHITECTURE.md) - System architecture and components
- [System Requirements](docs/SYSTEM_REQUIREMENTS.md) - Hardware and software requirements
- [FAQ](docs/FAQ.md) - Frequently asked questions
- [Utility Scripts](scripts/README.md) - Maintenance and debugging tools

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [Celery](https://docs.celeryq.dev/)
- [OpenRouter](https://openrouter.ai)
- [Groq](https://groq.com)

---

<p align="center">
  <strong>⭐ Star this repo if you find it useful!</strong><br/>
  Made with ❤️ by <a href="https://github.com/Givaa">Givaa</a>
</p>
