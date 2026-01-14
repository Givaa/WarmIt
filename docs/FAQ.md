# WarmIt - FAQ & Troubleshooting

## Frequently Asked Questions

### General

**Q: What is email warming?**
A: Email warming is the process of gradually building the reputation of an email address or domain by sending an increasing volume of emails over time. This helps prevent your emails from landing in spam.

**Q: How long does it take to warm up an account?**
A: It depends on the domain age:
- New domains (< 30 days): 6-8 weeks
- Moderately new domains (30-180 days): 4-6 weeks
- Established domains (> 180 days): 2-4 weeks

**Q: Can I use WarmIt with free Gmail?**
A: Yes, but you must use App Passwords and enable IMAP in settings. Free Gmail has a limit of 500 emails/day.

**Q: Does WarmIt work with any email provider?**
A: Yes, it works with any provider that supports SMTP and IMAP (Gmail, Outlook, Yahoo, custom domains, etc.).

**Q: Is it secure? Are my credentials protected?**
A: Credentials are stored in the database. In production, you should:
- Use environment variables for sensitive credentials
- Encrypt the database
- Use HTTPS for the API
- Limit network access

### Setup & Configuration

**Q: How do I get an API key for OpenRouter/Groq?**
A:
- OpenRouter: https://openrouter.ai - Sign up and copy the API key
- Groq: https://console.groq.com - Sign up and create an API key
Both offer generous free tiers.

**Q: How do I create a Gmail App Password?**
A:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to "App passwords"
4. Generate a new password for "Mail"
5. Use that password in WarmIt

**Q: How many sender accounts should I use?**
A: Start with 2-3 sender accounts. You can add more as the system stabilizes.

**Q: How many receiver accounts do I need?**
A: At least 2-3 receiver accounts. The more you have, the more natural the traffic appears.

### Email Sending

**Q: Why aren't my emails being sent?**
A: Check:
1. Correct credentials (use App Password for Gmail)
2. IMAP enabled
3. Firewall not blocking ports 587 (SMTP) and 993 (IMAP)
4. Account not blocked by provider
5. Logs: `tail -f logs/celery-worker.log`

**Q: How can I test sending without waiting for the scheduler?**
A: Use the manual endpoint:
```bash
curl -X POST http://localhost:8000/api/campaigns/1/process
```

**Q: The bounce rate is high, what do I do?**
A:
1. Verify DNS records (SPF, DKIM, DMARC)
2. Check that receiver accounts exist
3. Reduce daily volume
4. Pause the campaign temporarily

**Q: How are sends distributed throughout the day?**
A: WarmIt automatically sends every 2 hours. You can modify the frequency in `src/warmit/tasks/__init__.py`.

### AI & Content

**Q: Do AI-generated emails look like spam?**
A: The AI is configured to generate natural and conversational emails. It uses high temperature (0.8) and varies topics/tone for maximum naturalness.

**Q: Can I customize the generated content?**
A: Yes, modify `src/warmit/services/ai_generator.py`:
- Add topics in `TOPICS`
- Modify tones in `TONES`
- Change prompt templates

**Q: What happens if the AI API fails?**
A: WarmIt has a fallback system that uses predefined templates to continue sending.

**Q: Are free models sufficient?**
A: Yes! Llama 3.3 70B (free on OpenRouter) is excellent for generating natural emails.

### Monitoring & Metrics

**Q: How do I monitor progress?**
A: Use the CLI or API:
```bash
# CLI
poetry run python scripts/cli.py stats
poetry run python scripts/cli.py campaigns

# API
curl http://localhost:8000/api/metrics/system
```

**Q: What indicates a good open rate?**
A: For warmup emails between controlled accounts, aim for 70-90% open rate.

**Q: How do I know when warming is complete?**
A: The campaign completes automatically after the configured number of weeks. Success indicators:
- Open rate > 70%
- Bounce rate < 2%
- Reply rate > 50%
- No spam reports

### Database & Performance

**Q: Is SQLite sufficient for production?**
A: SQLite is fine for 1-10 accounts. For more accounts or high traffic, use PostgreSQL:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/warmit
```

**Q: How do I backup the database?**
A:
```bash
# SQLite
cp warmit.db warmit_backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump warmit > warmit_backup_$(date +%Y%m%d).sql
```

**Q: How many emails can WarmIt handle?**
A: With proper setup:
- SQLite: 100-500 emails/day
- PostgreSQL: 10,000+ emails/day

### Automation

**Q: How do I make WarmIt start automatically at boot?**
A: Use systemd (Linux) or launchd (macOS). Example in USAGE.md.

**Q: Can I change the sending frequency?**
A: Yes, modify `beat_schedule` in `src/warmit/tasks/__init__.py`:
```python
"process-campaigns": {
    "task": "warmit.tasks.warming.process_campaigns",
    "schedule": 3600.0,  # Every hour instead of every 2 hours
}
```

**Q: How does the response bot work?**
A: Every 30 minutes:
1. Checks inbox of receiver accounts
2. Reads unread emails from sender accounts
3. Generates response with AI
4. Sends response with random delay
5. Marks email as read

### Troubleshooting

**Q: Redis connection refused**
A:
```bash
# Start Redis
redis-server

# Verify it's running
redis-cli ping
# Should respond: PONG
```

**Q: Celery worker won't start**
A: Check:
```bash
# Verify Redis
redis-cli ping

# Check logs
poetry run celery -A warmit.tasks worker --loglevel=debug

# Reinstall dependencies
poetry install
```

**Q: ModuleNotFoundError: No module named 'warmit'**
A: Add src to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**Q: SSL/TLS errors with SMTP/IMAP**
A: Try changing settings:
```json
{
  "smtp_use_tls": true,  // or false
  "imap_use_ssl": true   // or false
}
```

**Q: API responding slowly**
A:
- Use PostgreSQL instead of SQLite
- Add database indexes
- Increase Celery workers
- Use Redis cache

**Q: Emails going to spam even after warming**
A:
1. Verify DNS records:
   ```bash
   dig TXT yourdomain.com
   dig TXT _dmarc.yourdomain.com
   ```
2. Check SPF: `v=spf1 include:_spf.google.com ~all`
3. Enable DKIM in Google Admin Console
4. Add DMARC: `v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com`
5. Slower warming
6. Less "spammy" content

### Production Deployment

**Q: How do I deploy to production?**
A: Options:
1. Docker Compose (simplest)
2. Kubernetes (scalable)
3. VPS with systemd
4. PaaS (Heroku, Railway, etc.)

**Q: What are security best practices?**
A:
- Use HTTPS for API (nginx + Let's Encrypt)
- Encrypt database with LUKS or encryption at rest
- Use secrets manager (Vault, AWS Secrets Manager)
- Limit access with firewall
- Monitor logs for suspicious activity
- Regular automatic backups

**Q: How do I scale to handle more accounts?**
A:
1. Switch to PostgreSQL
2. Add more Celery workers
3. Use Redis Cluster
4. Distribute workers across multiple machines
5. Load balancer for API

## Support

Didn't find an answer to your question?

- GitHub Issues: https://github.com/yourusername/warmit/issues
- Email: support@yourdomain.com
- Documentation: https://github.com/yourusername/warmit

## Contributing

Want to improve WarmIt?

1. Fork the repository
2. Create a branch for your feature
3. Make changes
4. Submit a Pull Request

We appreciate contributions of:
- Bug fixes
- New features
- Documentation
- Tests
- Translations
