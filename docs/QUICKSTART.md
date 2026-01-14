# WarmIt - Quick Start Guide

Quick guide to get started with WarmIt right away!

## Setup in 5 Minutes

### 1. Prerequisites

```bash
# Verify Python 3.11+
python3 --version

# Install Poetry (if you don't have it)
curl -sSL https://install.python-poetry.org | python3 -

# Install Redis
# macOS:
brew install redis

# Ubuntu/Debian:
sudo apt-get install redis-server
```

### 2. Project Setup

```bash
# Clone or navigate to directory
cd WarmIt

# Run automatic setup
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. Configure API Key

Choose a free AI provider:

**Option A: OpenRouter (Recommended)**
1. Go to https://openrouter.ai
2. Sign up and get API key
3. Edit `.env`:
```bash
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
AI_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

**Option B: Groq**
1. Go to https://console.groq.com
2. Sign up and create API key
3. Edit `.env`:
```bash
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your-key-here
AI_MODEL=llama-3.3-70b-versatile
```

### 4. Start Services

```bash
# Easy way - all in one
make dev

# Or manually in separate terminals:
# Terminal 1:
redis-server

# Terminal 2:
make api

# Terminal 3:
make worker

# Terminal 4:
make beat
```

### 5. Verify Installation

```bash
# Check API
curl http://localhost:8000/health

# Should respond:
# {"status":"healthy"}
```

## First Warming

### 1. Add Gmail Account

First, create a [Gmail App Password](https://myaccount.google.com/apppasswords):
- Go to Google Account → Security
- Enable 2-Step Verification
- Create App Password for "Mail"

Then add the account:

```bash
# Sender (account to warm up)
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-sender@gmail.com",
    "type": "sender",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_use_tls": true,
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "imap_use_ssl": true,
    "password": "your-app-password"
  }'
```

```bash
# Receiver (account that responds)
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-receiver@gmail.com",
    "type": "receiver",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_use_tls": true,
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "imap_use_ssl": true,
    "password": "another-app-password"
  }'
```

### 2. Create Campaign

```bash
curl -X POST http://localhost:8000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "First Campaign",
    "sender_account_ids": [1],
    "receiver_account_ids": [2],
    "duration_weeks": 4
  }'
```

### 3. Start Warming (Manual Test)

```bash
# Send first emails (normally automatic)
curl -X POST http://localhost:8000/api/campaigns/1/process
```

### 4. Monitor Progress

```bash
# Via CLI
make cli stats
make cli campaigns

# Via API
curl http://localhost:8000/api/metrics/system
curl http://localhost:8000/api/campaigns/1
```

## API Dashboard

Open in browser: **http://localhost:8000/docs**

Here you'll find:
- Interactive Swagger documentation
- Test endpoints directly
- Complete data schema

## Useful Commands

### Via Makefile

```bash
make help       # List commands
make setup      # Initial setup
make dev        # Start everything
make test       # Run tests
make format     # Format code
make lint       # Lint code
make clean      # Clean temporary files
```

### Via CLI

```bash
# System statistics
poetry run python scripts/cli.py stats

# List accounts
poetry run python scripts/cli.py accounts

# List campaigns
poetry run python scripts/cli.py campaigns

# Verify domain
poetry run python scripts/cli.py check-domain example@domain.com

# Initialize DB
poetry run python scripts/cli.py init-db
```

### Via API

```bash
# List all accounts
curl http://localhost:8000/api/accounts

# Account details
curl http://localhost:8000/api/accounts/1

# Account metrics
curl http://localhost:8000/api/metrics/accounts/1

# Pause campaign
curl -X PATCH http://localhost:8000/api/campaigns/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "paused"}'
```

## Best Practices

1. **Start Slow**
   - 1-2 sender accounts
   - 2-3 receiver accounts
   - Monitor first days

2. **Verify DNS**
   ```bash
   # SPF
   dig TXT yourdomain.com

   # DKIM (if custom domain)
   # Configure in Google Admin Console

   # DMARC
   dig TXT _dmarc.yourdomain.com
   ```

3. **Monitor Metrics**
   - Bounce rate < 5%
   - Open rate > 70%
   - Reply rate > 50%

4. **Gradual Approach**
   - Don't skip weeks
   - Maintain consistent volume
   - No long pauses

## Quick Troubleshooting

### Redis won't connect
```bash
redis-server
redis-cli ping  # Must respond PONG
```

### Celery won't start
```bash
# Reinstall
poetry install

# Direct test
poetry run celery -A warmit.tasks worker --loglevel=debug
```

### Emails not sending
```bash
# Verify credentials
# For Gmail use App Password, not regular password

# Enable IMAP in Gmail:
# Settings → Forwarding and POP/IMAP → Enable IMAP

# Test connection
curl -X POST http://localhost:8000/api/accounts/1/check-domain
```

### Slow API
```bash
# Use PostgreSQL instead of SQLite
# Modify in .env:
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/warmit
```

## Next Steps

1. **Read complete documentation**
   - [USAGE.md](USAGE.md) - Detailed guide
   - [FAQ.md](FAQ.md) - Frequently asked questions
   - [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Technical overview

2. **Explore examples**
   ```bash
   chmod +x examples/api_examples.sh
   ./examples/api_examples.sh
   ```

3. **Customize configuration**
   - Modify schedule in `src/warmit/tasks/__init__.py`
   - Customize AI topics in `src/warmit/services/ai_generator.py`
   - Adjust limits in `.env`

4. **Production deployment**
   - Setup Docker: `docker-compose up -d`
   - Configure HTTPS with nginx
   - Setup automatic backups

## Support

Having problems?

1. Check [FAQ.md](FAQ.md)
2. Verify logs: `tail -f logs/celery-worker.log`
3. Open issue on GitHub
4. Email: support@yourdomain.com

## Success!

If you see this, you're ready:
- API responding on http://localhost:8000
- Redis connected
- Celery worker running
- Accounts configured
- Campaign active

**Warming is now automatic!**

Emails will be sent every 2 hours and responses will be automatic every 30 minutes.

Monitor progress with:
```bash
make cli campaigns
```

Happy warming!
