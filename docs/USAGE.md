# WarmIt - Usage Guide

Complete guide for using WarmIt to warm up your email accounts.

## Quick Start

### 1. Initial Setup

```bash
# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Edit .env with your API keys
nano .env
```

### 2. Configure AI Provider

Choose one of the free AI providers:

**Option A: OpenRouter (Recommended)**
```bash
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
AI_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

**Option B: Groq**
```bash
AI_PROVIDER=groq
GROQ_API_KEY=your_key_here
AI_MODEL=llama-3.3-70b-versatile
```

### 3. Start Services

```bash
# Easy way - runs all services
chmod +x scripts/run_dev.sh
./scripts/run_dev.sh

# Or manually:
redis-server  # Terminal 1
poetry run uvicorn warmit.main:app --reload  # Terminal 2
poetry run celery -A warmit.tasks worker --loglevel=info  # Terminal 3
poetry run celery -A warmit.tasks beat --loglevel=info  # Terminal 4
```

## Adding Email Accounts

### Add Sender Account (to be warmed)

```bash
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sender@yourdomain.com",
    "type": "sender",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_use_tls": true,
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "imap_use_ssl": true,
    "password": "your_app_password"
  }'
```

### Add Receiver Account (automated responder)

```bash
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "email": "receiver@yourotherdomain.com",
    "type": "receiver",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_use_tls": true,
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "imap_use_ssl": true,
    "password": "your_app_password"
  }'
```

**Important Notes:**
- For Gmail, use [App Passwords](https://support.google.com/accounts/answer/185833)
- Enable IMAP in Gmail settings
- Use real passwords, not your main account password

## Creating a Warming Campaign

```bash
curl -X POST http://localhost:8000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Warmup Campaign",
    "sender_account_ids": [1, 2],
    "receiver_account_ids": [3, 4],
    "duration_weeks": 6
  }'
```

**What happens:**
1. System checks domain age for each sender
2. Calculates optimal warming schedule
3. Starts sending emails progressively
4. Receiver accounts automatically respond

## Monitoring

### View API Documentation

Visit: http://localhost:8000/docs

### Use CLI

```bash
# View all accounts
poetry run python scripts/cli.py accounts

# View campaigns
poetry run python scripts/cli.py campaigns

# Check domain age
poetry run python scripts/cli.py check-domain sender@domain.com

# System statistics
poetry run python scripts/cli.py stats
```

### Check Metrics

```bash
# Get account metrics
curl http://localhost:8000/api/metrics/accounts/1

# Get system metrics
curl http://localhost:8000/api/metrics/system

# Get daily metrics
curl http://localhost:8000/api/metrics/daily?days=30
```

## Email Warming Schedule

WarmIt follows industry best practices:

### Standard Schedule (domains > 90 days)

| Week | Emails/Day per Account |
|------|------------------------|
| 1    | 5                      |
| 2    | 10                     |
| 3    | 15                     |
| 4    | 25                     |
| 5    | 35                     |
| 6+   | 50                     |

### New Domain Schedule (< 30 days)

| Week | Emails/Day per Account |
|------|------------------------|
| 1    | 3                      |
| 2    | 5                      |
| 3    | 8                      |
| 4    | 13                     |
| 5    | 18                     |
| 6    | 23                     |
| 7    | 33                     |
| 8+   | 43                     |

## Common Configurations

### Gmail

```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_use_tls": true,
  "imap_host": "imap.gmail.com",
  "imap_port": 993,
  "imap_use_ssl": true
}
```

### Outlook/Office 365

```json
{
  "smtp_host": "smtp.office365.com",
  "smtp_port": 587,
  "smtp_use_tls": true,
  "imap_host": "outlook.office365.com",
  "imap_port": 993,
  "imap_use_ssl": true
}
```

### Custom Domain (cPanel/Plesk)

```json
{
  "smtp_host": "mail.yourdomain.com",
  "smtp_port": 587,
  "smtp_use_tls": true,
  "imap_host": "mail.yourdomain.com",
  "imap_port": 993,
  "imap_use_ssl": true
}
```

## Automation Schedule

WarmIt automatically:

- **Every 2 hours**: Sends warmup emails (8am-8pm)
- **Every 30 minutes**: Checks for replies and responds
- **Midnight**: Resets daily counters
- **11:59 PM**: Updates metrics

You can customize these in [src/warmit/tasks/__init__.py](src/warmit/tasks/__init__.py)

## Safety Features

### Automatic Pause

Campaigns automatically pause if:
- Bounce rate exceeds 5%
- SMTP/IMAP connection fails repeatedly

### Manual Controls

```bash
# Pause campaign
curl -X PATCH http://localhost:8000/api/campaigns/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "paused"}'

# Resume campaign
curl -X PATCH http://localhost:8000/api/campaigns/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'

# Pause account
curl -X PATCH http://localhost:8000/api/accounts/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "paused"}'
```

## Best Practices

1. **Start Small**: Begin with 2-3 sender accounts
2. **Use Real Receivers**: Use accounts you control for receivers
3. **Monitor Daily**: Check bounce rates and metrics
4. **SPF/DKIM/DMARC**: Ensure proper DNS records
5. **Gradual Increase**: Don't rush the warmup process
6. **Consistent Volume**: Send regularly, avoid gaps
7. **Time Distribution**: Spread emails across 8-12 hours
8. **Mix Content**: AI generates varied topics and tones

## Troubleshooting

### High Bounce Rate

- Check DNS records (SPF, DKIM, DMARC)
- Verify receiver email addresses exist
- Slow down sending volume

### Emails Not Sending

```bash
# Check account connection
curl -X POST http://localhost:8000/api/accounts/1/check-domain

# View logs
tail -f logs/celery-worker.log
```

### AI Generation Fails

- Check API key in `.env`
- Verify API provider status
- Check rate limits

### Database Issues

```bash
# Reset database
poetry run python scripts/cli.py init-db
```

## Advanced Usage

### Custom Warmup Duration

```python
# Calculate based on domain age
domain_info = await DomainChecker.check_domain("email@domain.com")
print(f"Recommended: {domain_info.warmup_weeks_recommended} weeks")
```

### Manual Email Testing

```python
from warmit.services.email_service import EmailService, EmailMessage

message = EmailMessage(
    sender="sender@domain.com",
    receiver="receiver@domain.com",
    subject="Test",
    body="This is a test"
)

await EmailService.send_email(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    username="sender@domain.com",
    password="password",
    message=message
)
```

## Production Deployment

### Using Docker

```dockerfile
# Coming soon
```

### Using systemd

```ini
# /etc/systemd/system/warmit-api.service
[Unit]
Description=WarmIt API Server
After=network.target redis.service

[Service]
Type=simple
User=warmit
WorkingDirectory=/opt/warmit
ExecStart=/usr/local/bin/poetry run uvicorn warmit.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Support

- Issues: https://github.com/yourusername/warmit/issues
- Documentation: https://github.com/yourusername/warmit
- Email: support@yourdomain.com
