# System Requirements

Complete guide for running WarmIt on Ubuntu/Linux systems.

---

## 🖥️ Operating System

### Supported
- **Ubuntu 20.04 LTS** or newer (Recommended: 22.04 LTS or 24.04 LTS)
- **Debian 11+**
- **CentOS/RHEL 8+**
- **Other Linux distributions** with Docker support

### Not Tested (but should work)
- Fedora
- Arch Linux
- OpenSUSE

---

## 📦 Required Software

### 1. Docker Engine
**Minimum Version**: 20.10+
**Recommended**: 24.0+

#### Install on Ubuntu:
```bash
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

#### Post-Installation (Run Docker without sudo):
```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Apply group changes (logout/login or run)
newgrp docker

# Verify
docker run hello-world
```

### 2. Docker Compose
**Minimum Version**: 2.0+
**Recommended**: 2.20+

Included with Docker Engine installation above. Verify:
```bash
docker compose version
# Should output: Docker Compose version v2.x.x
```

### 3. Git
```bash
sudo apt-get install -y git
git --version
```

### 4. curl & jq (for scripts)
```bash
sudo apt-get install -y curl jq
```

---

## 💾 Hardware Requirements

### Minimum (1-10 accounts)
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 20 GB free space
- **Network**: Stable internet connection

### Recommended (10-50 accounts)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 50 GB free space (SSD recommended)
- **Network**: 100 Mbps+ connection

### Enterprise (50+ accounts)
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 100+ GB SSD
- **Network**: 1 Gbps+ connection
- **Consider**: Multiple workers, load balancing

---

## 🔌 Network Requirements

### Ports
WarmIt uses the following ports:

| Port | Service | Required | Notes |
|------|---------|----------|-------|
| 8000 | API | Yes | FastAPI REST API |
| 8501 | Dashboard | Yes | Streamlit UI |
| 5432 | PostgreSQL | Internal | Docker network only |
| 6379 | Redis | Internal | Docker network only |

### Firewall Rules (UFW)
```bash
# Allow SSH (if remote)
sudo ufw allow 22/tcp

# Allow WarmIt services
sudo ufw allow 8000/tcp
sudo ufw allow 8501/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### Reverse Proxy (Optional)
For production, use Nginx or Caddy:
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

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🐍 Python Requirements (for development)

**Runtime**: Docker handles all Python dependencies
**Development**: Python 3.11+ (if running without Docker)

### Install Python 3.11 on Ubuntu:
```bash
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
```

### Install Poetry (optional, for development):
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
poetry --version
```

---

## 📊 Database Requirements

### PostgreSQL 16 (via Docker)
- Automatically managed by Docker Compose
- Data persisted in Docker volume
- No manual installation needed

### Backup Considerations
```bash
# Backup PostgreSQL data
docker compose -f docker/docker-compose.prod.yml exec postgres pg_dump -U warmit warmit > backup.sql

# Restore
docker compose -f docker/docker-compose.prod.yml exec -T postgres psql -U warmit warmit < backup.sql
```

---

## 🔐 Security Requirements

### SSL/TLS Certificates (Production)
Use Let's Encrypt with Certbot:
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d warmit.yourdomain.com
```

### Environment Variables
- Never commit `.env` files to git
- Use strong passwords (20+ characters)
- Rotate API keys regularly
- Use secret management tools for production

### System Updates
```bash
# Keep system updated
sudo apt-get update && sudo apt-get upgrade -y

# Enable automatic security updates
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## ✅ Pre-Installation Checklist

Run this script to verify your system:

```bash
#!/bin/bash
# save as: check_requirements.sh

echo "WarmIt - System Requirements Check"
echo "==================================="
echo ""

# Check OS
echo "OS: $(lsb_release -d | cut -f2)"
echo "Kernel: $(uname -r)"
echo ""

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker: $(docker --version)"
else
    echo "❌ Docker: Not installed"
fi

# Check Docker Compose
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose: $(docker compose version --short)"
else
    echo "❌ Docker Compose: Not installed"
fi

# Check Git
if command -v git &> /dev/null; then
    echo "✅ Git: $(git --version)"
else
    echo "❌ Git: Not installed"
fi

# Check curl
if command -v curl &> /dev/null; then
    echo "✅ curl: $(curl --version | head -1)"
else
    echo "❌ curl: Not installed"
fi

# Check jq
if command -v jq &> /dev/null; then
    echo "✅ jq: $(jq --version)"
else
    echo "⚠️  jq: Not installed (optional, for scripts)"
fi

echo ""

# Check CPU
echo "CPU Cores: $(nproc)"

# Check RAM
echo "RAM: $(free -h | awk '/^Mem:/ {print $2}')"

# Check Disk
echo "Disk Free: $(df -h / | awk 'NR==2 {print $4}')"

echo ""

# Check Docker daemon
if docker info &> /dev/null; then
    echo "✅ Docker daemon: Running"
else
    echo "❌ Docker daemon: Not running or no permissions"
    echo "   Try: sudo usermod -aG docker $USER && newgrp docker"
fi

echo ""
echo "Check complete!"
```

Run it:
```bash
chmod +x check_requirements.sh
./check_requirements.sh
```

---

## 🚀 Quick Install (Ubuntu 22.04 LTS)

Complete setup from scratch:

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install dependencies
sudo apt-get install -y git curl jq

# Clone WarmIt
git clone https://github.com/yourusername/warmit.git
cd warmit

# Configure
cp .env.example docker/.env
nano docker/.env  # Add API keys

# Start
./start.sh

# Done! Access:
# Dashboard: http://localhost:8501
# API: http://localhost:8000
```

---

## 🐛 Common Issues

### Docker Permission Denied
```bash
sudo usermod -aG docker $USER
newgrp docker
# Or logout and login again
```

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :8501

# Kill the process or change WarmIt ports in docker-compose.prod.yml
```

### Out of Disk Space
```bash
# Clean Docker
docker system prune -a --volumes

# Check disk usage
df -h
docker system df
```

### Docker Compose Not Found
```bash
# Install manually
sudo apt-get install docker-compose-plugin

# Or use old docker-compose v1
sudo apt-get install docker-compose
```

---

## 📱 Monitoring Requirements

### System Monitoring
```bash
# Install htop
sudo apt-get install -y htop

# Install netdata (optional)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

### Docker Monitoring
```bash
# View logs
docker compose -f docker/docker-compose.prod.yml logs -f

# View stats
docker stats

# View health
docker compose -f docker/docker-compose.prod.yml ps
```

---

## 🔄 Update Requirements

### Updating WarmIt
```bash
cd warmit
git pull
./start.sh restart
```

### Updating Docker
```bash
sudo apt-get update
sudo apt-get install --only-upgrade docker-ce docker-ce-cli containerd.io
```

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker compose -f docker/docker-compose.prod.yml logs`
2. Verify requirements: Run `check_requirements.sh`
3. Check [FAQ.md](FAQ.md)
4. Open issue on GitHub

---

**System requirements verified! Ready for production! 🚀**
