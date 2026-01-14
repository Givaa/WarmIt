# Ubuntu Quick Start Guide

Complete step-by-step guide to get WarmIt running on Ubuntu in 10 minutes.

## Prerequisites

- Ubuntu 20.04+ (fresh install is fine)
- Internet connection
- Sudo access

---

## 1. Install Docker (2 minutes)

```bash
# One-command install
curl -fsSL https://get.docker.com | sudo sh

# Add your user to docker group (no need for sudo)
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Verify
docker --version
docker compose version
```

**Expected output:**
```
Docker version 24.0.x
Docker Compose version v2.x.x
```

---

## 2. Clone WarmIt (30 seconds)

```bash
cd ~
git clone https://github.com/Givaa/warmit.git
cd warmit
```

---

## 3. Get API Key (1 minute)

Choose one provider:

### Option A: OpenRouter (Recommended - Free tier available)
1. Go to https://openrouter.ai/
2. Sign up
3. Get API key: https://openrouter.ai/keys
4. Copy the key: `sk-or-v1-xxxxx`

### Option B: Groq (Fast, free)
1. Go to https://console.groq.com/
2. Sign up
3. Get API key
4. Copy the key: `gsk-xxxxx`

---

## 4. Start WarmIt (1 minute)

```bash
chmod +x start.sh
./start.sh
```

**What happens:**
1. Script creates `docker/.env` from template
2. Prompts you to add API key
3. Press Ctrl+C, edit file, then re-run

**Edit configuration:**
```bash
nano docker/.env
```

**Add your API key:**
```bash
# For OpenRouter
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxx  # ← Add your key here

# OR for Groq
AI_PROVIDER=groq
GROQ_API_KEY=gsk-xxxxx  # ← Add your key here
```

**Save:** `Ctrl+X`, then `Y`, then `Enter`

**Start again:**
```bash
./start.sh
```

**Wait 2-3 minutes** for services to start.

---

## 5. Access Web Interfaces

### Dashboard (Main UI)
```bash
# Ubuntu Desktop
firefox http://localhost:8501

# Ubuntu Server (SSH tunnel)
# On your local machine:
ssh -L 8501:localhost:8501 user@server-ip
# Then open: http://localhost:8501
```

### Logs Viewer (Dozzle)
```bash
# View all logs in browser
open http://localhost:8888
```

**Features:**
- Real-time log streaming
- Search and filter
- Multi-container view
- No terminal commands needed!

### API Documentation
```bash
open http://localhost:8000/docs
```

---

## 6. Quick Test (5 minutes)

### Test System Health

```bash
# Check all services are running
cd ~/warmit/docker
docker compose ps

# Expected: All services "Up" and "healthy"
```

### Test API

```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Test Dashboard

Open http://localhost:8501 - you should see the WarmIt dashboard

---

## 7. Add Email Accounts

### Via Web Dashboard (Easiest)

1. Open http://localhost:8501
2. Go to "Add New" → "Add Account"
3. Add 1 sender (your business email)
4. Add 1 receiver (Gmail with App Password)
5. Create campaign
6. Done!

### Via Script (Faster for multiple accounts)

```bash
cd ~/warmit/examples
nano setup_multi_accounts.sh

# Edit SENDERS and RECEIVERS arrays
# Then run:
chmod +x setup_multi_accounts.sh
./setup_multi_accounts.sh
```

---

## Common Issues & Solutions

### Port Already in Use

```bash
# Check what's using port 8501
sudo lsof -i :8501

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

### Docker Permission Denied

```bash
# You need to logout/login after adding user to docker group
# Or use:
newgrp docker

# Verify you're in docker group
groups | grep docker
```

### Services Not Starting

```bash
# View logs in browser
open http://localhost:8888

# Or terminal
cd ~/warmit/docker
docker compose logs api
docker compose logs worker
```

### API Key Not Working

```bash
# Check .env file
cat ~/warmit/docker/.env | grep API_KEY

# Make sure no spaces, correct format
# Restart services
cd ~/warmit
./start.sh restart
```

---

## Useful Commands

```bash
# View status
cd ~/warmit/docker
docker compose ps

# View logs (web interface)
open http://localhost:8888

# Restart all
cd ~/warmit
./start.sh restart

# Stop all
./start.sh stop

# View resource usage
docker stats

# Complete reset (deletes data)
./start.sh reset
```

---

## Access from Remote (Ubuntu Server)

### SSH Tunnel (Recommended)

On your local machine:
```bash
ssh -L 8501:localhost:8501 -L 8888:localhost:8888 user@server-ip
```

Then access:
- Dashboard: http://localhost:8501
- Logs: http://localhost:8888

### Firewall (Public Access)

**Warning:** Only if you trust your network!

```bash
# Allow ports
sudo ufw allow 8501/tcp
sudo ufw allow 8888/tcp
sudo ufw allow 8000/tcp

# Access from browser
http://<server-ip>:8501
http://<server-ip>:8888
```

### Nginx Reverse Proxy (Production)

See [docker/README.md](../docker/README.md) for Nginx configuration.

---

## Next Steps

### 1. Add Email Accounts

**Sender (Aruba/Custom Domain):**
- Email: sales@yourdomain.com
- SMTP: smtp.yourdomain.com:587
- IMAP: imap.yourdomain.com:993
- Password: your_email_password

**Receiver (Gmail):**
- Email: warmup1@gmail.com
- SMTP: smtp.gmail.com:587 (auto)
- IMAP: imap.gmail.com:993 (auto)
- Password: [Gmail App Password](https://myaccount.google.com/apppasswords)

See [PROVIDER_SETUP.md](PROVIDER_SETUP.md) for detailed provider configuration.

### 2. Create Campaign

- Duration: 6 weeks
- Select senders and receivers
- Click "Create Campaign"

### 3. Monitor

- Dashboard: http://localhost:8501
- Logs: http://localhost:8888
- Check metrics daily

### 4. Scale Up

After testing with 1-2 accounts, add more:
- 10 senders (business emails)
- 10 receivers (Gmail, Outlook, Libero)

See [MULTI_ACCOUNT_SETUP.md](MULTI_ACCOUNT_SETUP.md)

---

## Complete Example (Copy-Paste)

```bash
# Complete setup in 5 commands
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER && newgrp docker
git clone https://github.com/Givaa/warmit.git && cd warmit
nano docker/.env  # Add API key
./start.sh

# Access
firefox http://localhost:8501  # Dashboard
firefox http://localhost:8888  # Logs
```

---

## Performance Tuning

### Low-End VPS (1GB RAM)

```bash
# Edit docker/docker-compose.yml
# Reduce worker concurrency:
command: celery -A warmit.tasks worker --concurrency=2

# Restart
./start.sh restart
```

### High Volume (20+ senders)

```bash
# Scale workers
cd docker
docker compose up -d --scale worker=3

# Increase resources in docker-compose.yml
```

---

## Backup & Restore

### Backup

```bash
# Database
cd ~/warmit/docker
docker compose exec postgres pg_dump -U warmit warmit > ~/warmit-backup.sql

# Or full Docker volumes
docker volume ls | grep warmit
docker run --rm -v warmit_postgres_data:/data -v ~/backup:/backup alpine tar czf /backup/postgres-backup.tar.gz -C /data .
```

### Restore

```bash
cd ~/warmit/docker
docker compose exec -T postgres psql -U warmit warmit < ~/warmit-backup.sql
```

---

## System Requirements Check

Run the automated check:

```bash
cd ~/warmit
chmod +x scripts/check_requirements.sh
./scripts/check_requirements.sh
```

This verifies:
- Docker installation
- System resources (CPU, RAM, disk)
- Network connectivity
- Port availability

---

## Support

- Documentation: [README.md](../README.md)
- Provider Setup: [PROVIDER_SETUP.md](PROVIDER_SETUP.md)
- Multi-Account: [MULTI_ACCOUNT_SETUP.md](MULTI_ACCOUNT_SETUP.md)
- System Requirements: [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md)
- Docker Details: [docker/README.md](../docker/README.md)

---

**Ready to warm your emails? Let's go! 🔥**
