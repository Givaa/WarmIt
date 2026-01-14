# WarmIt - Production Deployment Guide

Guida completa per deployment production-ready con failsafe e monitoring automatico.

## 🚀 Quick Start (Un Comando Solo!)

```bash
# 1. Configura API key
cp .env.example .env
nano .env  # Aggiungi OPENROUTER_API_KEY o GROQ_API_KEY

# 2. Avvia tutto!
./start.sh
```

**È tutto!** WarmIt sarà accessibile su:
- 📊 Dashboard: http://localhost:8501
- 🔌 API: http://localhost:8000
- 📖 Docs: http://localhost:8000/docs

## 🛡️ Failsafe Features

### Auto-Restart Policies

Tutti i servizi hanno `restart: always`:
- **API**: Si riavvia automaticamente se crasha
- **Worker**: Riprende task automaticamente
- **Beat**: Mantiene schedule anche dopo restart
- **Redis**: Persiste dati su disco
- **PostgreSQL**: Backup automatici transazioni
- **Dashboard**: Always available
- **Watchdog**: Monitora e recupera errori

### Health Checks

Health check ogni 30-60 secondi:
- **API**: HTTP health endpoint
- **Worker**: Celery ping
- **Beat**: PID file check
- **Redis**: Redis PING
- **PostgreSQL**: pg_isready
- **Dashboard**: Streamlit health

Se un servizio fallisce 3 health check consecutivi, Docker lo riavvia automaticamente.

### Watchdog Monitoring

Sistema autonomo che:
- Controlla tutti i servizi ogni 5 minuti
- Rileva problemi prima che diventino critici
- Trigger auto-recovery automatico
- Logging dettagliato
- Cooldown 1 ora tra recovery

### Resource Limits

Limiti per prevenire crash di memoria:
```yaml
API:     1GB RAM, 1 CPU
Worker:  2GB RAM, 2 CPU
Beat:    512MB RAM, 0.5 CPU
```

### Log Rotation

Automatic log rotation:
- Max 50MB per log file
- Max 5 file rotati
- Previene disk full

## 📋 Requisiti

### Sistema Minimo
- **RAM**: 4GB (8GB raccomandato)
- **CPU**: 2 cores (4 raccomandato)
- **Disk**: 20GB (SSD raccomandato)
- **OS**: Linux, macOS, Windows con WSL2

### Software
- Docker 20.10+
- Docker Compose v2+
- Bash (per script)

## 🔧 Configurazione

### 1. Environment Variables

File `.env` essenziali:

```bash
# AI Provider (REQUIRED)
AI_PROVIDER=openrouter  # o groq
OPENROUTER_API_KEY=sk-or-v1-xxxxx
# O
GROQ_API_KEY=gsk_xxxxx

# Database (REQUIRED)
POSTGRES_PASSWORD=your_secure_password_here

# Optional
AI_MODEL=meta-llama/llama-3.3-70b-instruct:free
LOG_LEVEL=INFO
DEBUG=false
```

### 2. Performance Tuning

Per carichi alti, modifica `docker-compose.prod.yml`:

```yaml
# Aumenta workers
worker:
  command: celery -A warmit.tasks worker --concurrency=8  # invece di 4

# Aumenta memoria
api:
  deploy:
    resources:
      limits:
        memory: 2G  # invece di 1G
```

### 3. Network Configuration

Per accesso remoto, modifica ports:

```yaml
api:
  ports:
    - "0.0.0.0:8000:8000"  # Esponi su tutte le interfacce

dashboard:
  ports:
    - "0.0.0.0:8501:8501"
```

⚠️ **Security Warning**: Usa nginx reverse proxy e HTTPS in produzione!

## 🎯 Comandi Essenziali

### Gestione Base

```bash
# Start (prima volta o dopo stop)
./start.sh

# Restart (mantiene containers)
./start.sh restart

# Stop (mantiene dati)
./start.sh stop

# Remove containers (mantiene dati)
./start.sh down

# Reset completo (CANCELLA TUTTO)
./start.sh reset
```

### Monitoring

```bash
# Status servizi
docker-compose -f docker-compose.prod.yml ps

# Logs real-time
docker-compose -f docker-compose.prod.yml logs -f

# Logs specifici
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f worker
docker-compose -f docker-compose.prod.yml logs -f watchdog

# Health check manuale
curl http://localhost:8000/health/detailed | jq

# Recovery manuale
curl -X POST http://localhost:8000/health/recover
```

### Troubleshooting

```bash
# Rebuild dopo modifiche codice
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Restart singolo servizio
docker-compose -f docker-compose.prod.yml restart api

# Accesso shell container
docker exec -it warmit-api bash
docker exec -it warmit-worker bash

# Database access
docker exec -it warmit-postgres psql -U warmit -d warmit

# Redis access
docker exec -it warmit-redis redis-cli
```

## 💾 Backup & Recovery

### Backup Automatico Database

Crea cron job:

```bash
# Backup giornaliero alle 2 AM
0 2 * * * docker exec warmit-postgres pg_dump -U warmit warmit > /backups/warmit_$(date +\%Y\%m\%d).sql
```

### Backup Manuale

```bash
# Database
docker exec warmit-postgres pg_dump -U warmit warmit > warmit_backup.sql

# Redis
docker exec warmit-redis redis-cli SAVE
docker cp warmit-redis:/data/dump.rdb ./redis_backup.rdb

# Volumes
docker run --rm -v warmit_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_data.tar.gz /data
```

### Restore

```bash
# Database
cat warmit_backup.sql | docker exec -i warmit-postgres psql -U warmit warmit

# Redis
docker cp redis_backup.rdb warmit-redis:/data/dump.rdb
docker-compose -f docker-compose.prod.yml restart redis
```

## 📊 Monitoring Dashboard

### Dashboard Features

- ✅ Real-time system metrics
- ✅ Account management
- ✅ Campaign monitoring
- ✅ Analytics & charts
- ✅ One-click controls
- ✅ Auto-refresh every 30s

### Dashboard Endpoints

Dashboard accede a questi endpoint API:
- `GET /health` - Basic health
- `GET /health/detailed` - Full health report
- `GET /api/accounts` - Account list
- `GET /api/campaigns` - Campaign list
- `GET /api/metrics/system` - System metrics
- `POST /api/accounts` - Add account
- `POST /api/campaigns` - Create campaign

## 🔒 Security Best Practices

### 1. Environment Variables

```bash
# Genera password sicura
openssl rand -base64 32

# Usa in .env
POSTGRES_PASSWORD=tua_password_generata
```

### 2. Firewall Rules

```bash
# Permetti solo localhost
ufw allow from 127.0.0.1 to any port 8000
ufw allow from 127.0.0.1 to any port 8501

# O permetti IP specifico
ufw allow from 192.168.1.0/24 to any port 8000
```

### 3. Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name warmit.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name warmit.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/warmit.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/warmit.yourdomain.com/privkey.pem;

    # Dashboard
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. SSL/TLS

```bash
# Usa Let's Encrypt
sudo certbot --nginx -d warmit.yourdomain.com
```

## 🚨 Troubleshooting

### Servizio non si avvia

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs service_name

# Check health
docker inspect warmit-api | grep Health

# Manual test
docker exec -it warmit-api curl http://localhost:8000/health
```

### High Memory Usage

```bash
# Check usage
docker stats

# Restart worker (clear cache)
docker-compose -f docker-compose.prod.yml restart worker

# Reduce concurrency in docker-compose.prod.yml
worker:
  command: celery -A warmit.tasks worker --concurrency=2
```

### Database Connection Errors

```bash
# Check PostgreSQL
docker exec warmit-postgres pg_isready -U warmit

# Check connections
docker exec warmit-postgres psql -U warmit -c "SELECT count(*) FROM pg_stat_activity;"

# Restart database
docker-compose -f docker-compose.prod.yml restart postgres
```

### Redis Connection Errors

```bash
# Check Redis
docker exec warmit-redis redis-cli ping

# Check memory
docker exec warmit-redis redis-cli INFO memory

# Clear cache
docker exec warmit-redis redis-cli FLUSHALL
```

### Worker not processing tasks

```bash
# Check worker status
docker exec warmit-worker celery -A warmit.tasks inspect active

# Check queue
docker exec warmit-redis redis-cli LLEN celery

# Restart worker
docker-compose -f docker-compose.prod.yml restart worker
```

## 📈 Performance Optimization

### For High Volume (100+ accounts)

```yaml
# docker-compose.prod.yml modifications
worker:
  command: celery -A warmit.tasks worker --concurrency=8 --prefetch-multiplier=1
  deploy:
    replicas: 2  # Multiple workers
    resources:
      limits:
        memory: 4G
        cpus: '4.0'

api:
  command: uvicorn warmit.main:app --host 0.0.0.0 --port 8000 --workers 4
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '2.0'
```

### Database Optimization

```sql
-- In PostgreSQL
CREATE INDEX idx_emails_sent_at ON emails(sent_at);
CREATE INDEX idx_emails_status ON emails(status);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_campaigns_status ON campaigns(status);
```

## 🔄 Update & Maintenance

### Update WarmIt

```bash
# Stop services
./start.sh stop

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
./start.sh
```

### Database Migrations

```bash
# Generate migration
docker exec warmit-api alembic revision --autogenerate -m "description"

# Apply migration
docker exec warmit-api alembic upgrade head
```

### Cleanup

```bash
# Remove old images
docker image prune -a

# Remove old volumes (CAUTION!)
docker volume prune

# Clear logs older than 7 days
find ./logs -name "*.log" -mtime +7 -delete
```

## 📞 Support & Monitoring

### Health Dashboard

Access: http://localhost:8000/health/detailed

Response example:
```json
{
  "overall_status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "celery_workers": {"status": "healthy", "workers": 1},
    "system_resources": {"status": "healthy", "cpu_percent": 25.3}
  }
}
```

### Metrics Tracking

Built-in metrics:
- Email volume (sent/opened/replied)
- Open rates, reply rates, bounce rates
- Account health
- Campaign progress
- System resources

### Alerts (Manual Setup)

Example alert script:

```bash
#!/bin/bash
# check_warmit.sh

STATUS=$(curl -s http://localhost:8000/health/detailed | jq -r '.overall_status')

if [ "$STATUS" != "healthy" ]; then
    # Send alert (email, Slack, etc.)
    echo "WarmIt unhealthy!" | mail -s "WarmIt Alert" admin@example.com
fi
```

Add to crontab:
```bash
*/5 * * * * /path/to/check_warmit.sh
```

## 🎓 Best Practices

1. **Always use ./start.sh** - Non usare docker-compose direttamente
2. **Monitor dashboard** - Controlla almeno una volta al giorno
3. **Backup regolari** - Setup backup automatici
4. **Update mensili** - Aggiorna codice e dipendenze
5. **Resource monitoring** - Usa `docker stats` periodicamente
6. **Log review** - Controlla logs per errori
7. **Bounce rate** - Mantieni sotto 2%
8. **Gradual scaling** - Non aggiungere troppi account subito

## 📚 Additional Resources

- [README.md](README.md) - Overview
- [QUICKSTART.md](QUICKSTART.md) - 5 minute setup
- [USAGE.md](USAGE.md) - Complete usage guide
- [FAQ.md](FAQ.md) - Common questions
- API Docs: http://localhost:8000/docs

---

**Production Ready! 🚀**

Con questa configurazione, WarmIt può girare stabile per mesi senza interventi manuali!
