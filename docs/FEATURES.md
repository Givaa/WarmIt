# WarmIt - Feature Highlights

## 📊 Web Dashboard

### Overview Page
![Dashboard Overview](docs/images/dashboard-overview.png)

**Features:**
- Real-time system metrics
- Active campaigns status
- Email activity charts
- Account health overview
- Auto-refresh every 30 seconds

### Accounts Management
![Accounts](docs/images/dashboard-accounts.png)

**Features:**
- Add/edit/delete accounts
- SMTP/IMAP connection testing
- Domain age checking
- Status control (pause/resume)
- Bounce rate monitoring
- Bulk operations

### Campaign Management
![Campaigns](docs/images/dashboard-campaigns.png)

**Features:**
- Create warming campaigns
- Progress tracking
- Real-time metrics
- Manual email triggers
- Pause/resume controls
- Week-by-week breakdown

### Analytics
![Analytics](docs/images/dashboard-analytics.png)

**Features:**
- Interactive Plotly charts
- Email volume trends
- Open/reply/bounce rates
- 7/14/30/60/90 day views
- Export data (coming soon)

## 🛡️ Failsafe System

### Auto-Restart
Every service has `restart: always`:
```yaml
services:
  api:
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**What this means:**
- Service crashes? Restarts in 3s
- Container killed? Starts again
- Server reboots? All services come back up
- Zero manual intervention needed

### Health Checks

**Every service is monitored:**

| Service | Check Method | Interval | Action on Failure |
|---------|--------------|----------|-------------------|
| API | HTTP /health | 30s | Restart after 3 fails |
| Worker | Celery ping | 60s | Restart after 3 fails |
| Beat | PID file | 60s | Restart after 3 fails |
| Redis | PING command | 10s | Restart after 3 fails |
| PostgreSQL | pg_isready | 10s | Restart after 3 fails |
| Dashboard | HTTP health | 30s | Restart after 3 fails |

### Watchdog Monitoring

**Autonomous monitoring system:**

```
┌──────────────────────────────────────┐
│         Watchdog Service             │
│  (Checks every 5 minutes)            │
└─────────────┬────────────────────────┘
              │
              ├─► Check API health
              ├─► Check Database
              ├─► Check Redis
              ├─► Check Celery workers
              ├─► Check account status
              │
              ├─► Detect issues
              │
              └─► Auto-recovery
                  (if needed)
```

**Recovery Actions:**
1. Resume paused accounts with good metrics
2. Reset error accounts
3. Clear stuck tasks
4. Restart failed services
5. Log all actions

**Cooldown Period:**
- 1 hour between recovery attempts
- Prevents recovery loops
- Manual override available

### Resource Limits

**Prevents memory/CPU exhaustion:**

```yaml
API:
  limits:
    cpus: '1.0'
    memory: 1G
  reservations:
    cpus: '0.5'
    memory: 512M

Worker:
  limits:
    cpus: '2.0'
    memory: 2G
  reservations:
    cpus: '1.0'
    memory: 1G
```

**Benefits:**
- No OOM (Out of Memory) kills
- Predictable performance
- Fair resource sharing
- Easy capacity planning

### Log Management

**Automatic rotation:**
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "50m"   # Max 50MB per file
    max-file: "5"      # Keep 5 files
```

**Result:**
- Max 250MB logs per service
- Prevents disk full
- Easy log analysis
- Automatic cleanup

## 🎯 Smart Warming

### Domain-Based Strategy

**Automatic optimization based on domain age:**

```python
if domain_age < 30 days:
    duration = 8 weeks
    start = 3 emails/day

elif domain_age < 90 days:
    duration = 6 weeks
    start = 5 emails/day

elif domain_age < 180 days:
    duration = 4 weeks
    start = 10 emails/day

else:  # Established domain
    duration = 2 weeks
    start = 20 emails/day
```

### Progressive Volume

**Week-by-week increase:**

| Week | New Domain | Mid Domain | Established |
|------|------------|------------|-------------|
| 1 | 3/day | 5/day | 20/day |
| 2 | 5/day | 10/day | 50/day |
| 3 | 8/day | 15/day | 50/day |
| 4 | 13/day | 25/day | 50/day |
| 5 | 18/day | 35/day | - |
| 6 | 23/day | 50/day | - |
| 7 | 33/day | - | - |
| 8+ | 43/day | - | - |

### Human-Like Behavior

**Randomization:**
- ✅ Email content (15+ topics, 5+ tones)
- ✅ Send times (distributed over 8-12 hours)
- ✅ Intervals between emails (30s - 2min)
- ✅ Response times (1-6 hours)
- ✅ Reply rate (80-90%)

## 🤖 AI Content Generation

### Free AI Providers

**OpenRouter (Recommended):**
- 30+ free models
- Llama 3.3 70B included
- 1M+ tokens/month free tier
- Best for variety

**Groq:**
- Ultra-fast inference
- 14,400 requests/day free
- Llama 3.3 70B
- Best for speed

### Content Variety

**15+ Topics:**
- Tech news & innovations
- Productivity tips
- Industry insights
- Business strategies
- Personal development
- Health & wellness
- Travel experiences
- Book recommendations
- And more...

**5+ Tones:**
- Friendly & casual
- Professional & informative
- Enthusiastic & energetic
- Thoughtful & reflective
- Humorous & light-hearted

**Result:**
- Every email unique
- Natural conversations
- No spam patterns
- High engagement

### Fallback System

If AI fails:
```python
def generate_fallback_email():
    topic = random.choice(TOPICS)
    return f"""
    Hi,

    Hope you're doing well! I was thinking about {topic}
    and wanted to share a quick thought with you.

    Would love to hear your perspective on this when
    you have a moment.

    Best regards
    """
```

**Never stops sending!**

## 📈 Metrics & Analytics

### Real-Time Tracking

**Account Metrics:**
- Total sent/received
- Open rate %
- Reply rate %
- Bounce rate %
- Current daily limit
- Domain age

**Campaign Metrics:**
- Progress % (week/duration)
- Emails sent today/target
- Total emails sent
- Open/reply/bounce rates
- Last email sent time

**System Metrics:**
- Total accounts (active/paused)
- Active campaigns
- Emails sent today
- Average rates across all accounts

### Historical Data

**Daily metrics stored:**
- Date
- Emails sent/received/opened/replied/bounced
- Calculated rates
- 30+ day history
- Plotly interactive charts

### Health Reports

**Detailed health endpoint:**
```json
{
  "overall_status": "healthy",
  "timestamp": "2026-01-14T10:30:00Z",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection OK"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection OK"
    },
    "celery_workers": {
      "status": "healthy",
      "workers": 1,
      "message": "1 workers active"
    },
    "system_resources": {
      "status": "healthy",
      "cpu_percent": 25.3,
      "memory_percent": 45.2,
      "disk_percent": 15.8
    },
    "email_accounts": {
      "status": "healthy",
      "total_accounts": 5,
      "active_accounts": 5,
      "high_bounce_accounts": 0
    }
  }
}
```

## 🔒 Security Features

### Connection Validation
- ✅ SMTP/IMAP tested before saving
- ✅ Credentials validated
- ✅ Connection timeouts
- ✅ Error handling

### Data Protection
- ✅ Database encryption (production)
- ✅ Environment variables for secrets
- ✅ No plaintext passwords in logs
- ✅ Secure Docker networking

### Safety Limits
- ✅ Max bounce rate (5%)
- ✅ Auto-pause on high bounces
- ✅ Rate limiting
- ✅ Resource constraints

### Monitoring
- ✅ Failed login attempts logged
- ✅ Unusual activity detection
- ✅ Health check alerts
- ✅ Recovery action logs

## 🚀 Performance

### Scalability

**Single server capacity:**
- 10-50 accounts: Easy
- 50-100 accounts: Comfortable
- 100-500 accounts: Possible (tune resources)
- 500+ accounts: Multi-server setup

**Optimization tips:**
```yaml
# High volume config
worker:
  command: celery -A warmit.tasks worker --concurrency=8
  deploy:
    replicas: 2
    resources:
      limits:
        memory: 4G
        cpus: '4.0'

api:
  command: uvicorn warmit.main:app --workers 4
```

### Database Performance

**Built-in indexes:**
- ✅ emails(sent_at)
- ✅ emails(status)
- ✅ accounts(status)
- ✅ campaigns(status)
- ✅ metrics(account_id, date)

**Result:**
- Fast queries
- Efficient joins
- Quick dashboard loads

### Caching

**Redis usage:**
- Task queue
- Result backend
- Session storage
- Cache layer (future)

**Benefits:**
- Fast task distribution
- Reliable delivery
- No task loss

## 🎁 Bonus Features

### CLI Tool
```bash
# Beautiful CLI with Rich
poetry run python scripts/cli.py stats
poetry run python scripts/cli.py accounts
poetry run python scripts/cli.py campaigns
poetry run python scripts/cli.py check-domain email@domain.com
```

### API Documentation
- Auto-generated Swagger UI
- Interactive testing
- Request/response examples
- Authentication docs (future)

### Docker Compose
- One-command deployment
- All services configured
- Volume persistence
- Network isolation

### Makefile
```bash
make dev      # Development mode
make test     # Run tests
make format   # Format code
make lint     # Lint code
```

---

**Production-ready, failsafe, and beautiful! 🔥**
