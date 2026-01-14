# WarmIt - Project Summary

## Overview

**WarmIt** è un tool sofisticato per il riscaldamento automatizzato di caselle email, progettato per migliorare la deliverability e ridurre la probabilità che le email finiscano nello spam.

## Caratteristiche Principali

### 🔥 Core Features

1. **Domain Age Analysis**
   - Controllo automatico età dominio via WHOIS/RDAP
   - Raccomandazioni personalizzate basate su età dominio
   - Calcolo automatico durata warming ottimale

2. **AI-Powered Content Generation**
   - Generazione email naturali e conversazionali
   - Supporto OpenRouter (30+ modelli gratuiti) e Groq
   - Varietà di topics, tones e stili
   - Fallback system per resilienza

3. **Progressive Volume Scheduling**
   - Aumento graduale volume email basato su best practices
   - Schedule personalizzati per nuovi vs established domains
   - Distribuzione invii su 8-12 ore (comportamento umano)
   - Safety features: auto-pause su high bounce rate

4. **Automated Response System**
   - Bot automatico che legge inbox dei receiver accounts
   - Risposta intelligente con AI
   - Delay casuali per simulare comportamento umano
   - Thread tracking e gestione conversazioni

5. **Multi-Account Management**
   - Gestione multipli sender e receiver accounts
   - Supporto tutti i provider (Gmail, Outlook, custom domains)
   - Test automatici connessione SMTP/IMAP
   - Status tracking per ogni account

6. **Campaign Management**
   - Creazione e gestione campagne warming
   - Progress tracking in tempo reale
   - Metriche dettagliate (open rate, reply rate, bounce rate)
   - Controlli pause/resume

7. **Comprehensive Metrics**
   - Dashboard metriche sistema
   - Statistiche per account e campagna
   - Tracking giornaliero
   - Grafici e trend analysis

### 🏗️ Architettura

```
┌─────────────────────────────────────────────────────────┐
│                      WarmIt System                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐               │
│  │   FastAPI    │◄────►│   Database   │               │
│  │   REST API   │      │ SQLite/PgSQL │               │
│  └──────┬───────┘      └──────────────┘               │
│         │                                               │
│         │              ┌──────────────┐                │
│         └─────────────►│    Redis     │◄───────┐      │
│                        └──────────────┘        │      │
│                                                 │      │
│  ┌──────────────┐      ┌──────────────┐       │      │
│  │Celery Worker │◄────►│ Celery Beat  │───────┘      │
│  │  (Tasks)     │      │ (Scheduler)  │              │
│  └──────┬───────┘      └──────────────┘              │
│         │                                              │
│         ▼                                              │
│  ┌─────────────────────────────────────────────┐     │
│  │           Services Layer                    │     │
│  ├─────────────────────────────────────────────┤     │
│  │ • DomainChecker  • AIGenerator             │     │
│  │ • EmailService   • WarmupScheduler         │     │
│  │ • ResponseBot                               │     │
│  └─────────────────────────────────────────────┘     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 📦 Tech Stack

**Backend:**
- Python 3.11+
- FastAPI (API framework)
- SQLAlchemy (ORM)
- Celery (task queue)
- Redis (message broker)

**Email:**
- aiosmtplib (async SMTP)
- aioimap (async IMAP)
- email standard library

**AI:**
- OpenAI SDK (compatible con OpenRouter/Groq)
- Supporto multiple providers

**Tools:**
- Typer + Rich (CLI)
- pytest (testing)
- Black + Ruff (code quality)
- Poetry (dependency management)

## Project Structure

```
WarmIt/
├── src/warmit/
│   ├── api/                    # FastAPI routes
│   │   ├── accounts.py         # Account management
│   │   ├── campaigns.py        # Campaign management
│   │   └── metrics.py          # Metrics & statistics
│   ├── models/                 # Database models
│   │   ├── account.py          # Email accounts
│   │   ├── campaign.py         # Warming campaigns
│   │   ├── email.py            # Email tracking
│   │   └── metric.py           # Daily metrics
│   ├── services/               # Business logic
│   │   ├── domain_checker.py  # WHOIS/RDAP
│   │   ├── ai_generator.py    # AI content generation
│   │   ├── email_service.py   # SMTP/IMAP
│   │   ├── scheduler.py        # Warming scheduler
│   │   └── response_bot.py    # Auto-reply bot
│   ├── tasks/                  # Celery tasks
│   │   ├── warming.py          # Campaign processing
│   │   └── response.py         # Response processing
│   ├── config.py               # Settings
│   ├── database.py             # DB connection
│   └── main.py                 # FastAPI app
├── scripts/
│   ├── setup.sh                # Initial setup
│   ├── run_dev.sh              # Development startup
│   └── cli.py                  # CLI tool
├── tests/                      # Test suite
├── examples/                   # Usage examples
├── docs/                       # Documentation
├── docker-compose.yml          # Docker setup
├── Dockerfile                  # Container image
├── Makefile                    # Build commands
└── pyproject.toml             # Dependencies
```

## Warming Strategy

### Schedule Progressivo

**Domini Nuovi (< 30 giorni):**
```
Week 1: 3 emails/day
Week 2: 5 emails/day
Week 3: 8 emails/day
Week 4: 13 emails/day
Week 5: 18 emails/day
Week 6: 23 emails/day
Week 7: 33 emails/day
Week 8+: 43 emails/day
```

**Domini Stabiliti (> 180 giorni):**
```
Week 1: 20 emails/day
Week 2+: 50 emails/day
```

### Best Practices Implementate

1. ✅ Start lento con volume basso
2. ✅ Aumento progressivo (no salti)
3. ✅ Distribuzione temporale (8-12 ore)
4. ✅ Contenuti vari e naturali
5. ✅ Conversazioni bidirezionali
6. ✅ Delay casuali tra invii
7. ✅ Response timing umano (1-6 ore)
8. ✅ Monitoring bounce rate
9. ✅ Auto-pause su problemi
10. ✅ Tracking metriche dettagliate

## API Endpoints

### Accounts
- `POST /api/accounts` - Crea account
- `GET /api/accounts` - Lista accounts
- `GET /api/accounts/{id}` - Dettagli account
- `PATCH /api/accounts/{id}` - Modifica account
- `DELETE /api/accounts/{id}` - Elimina account
- `POST /api/accounts/{id}/check-domain` - Verifica dominio

### Campaigns
- `POST /api/campaigns` - Crea campagna
- `GET /api/campaigns` - Lista campagne
- `GET /api/campaigns/{id}` - Dettagli campagna
- `PATCH /api/campaigns/{id}/status` - Modifica status
- `POST /api/campaigns/{id}/process` - Trigger manuale
- `DELETE /api/campaigns/{id}` - Elimina campagna

### Metrics
- `GET /api/metrics/accounts/{id}` - Metriche account
- `GET /api/metrics/system` - Metriche sistema
- `GET /api/metrics/daily` - Metriche giornaliere

## Automation

### Celery Tasks (Scheduled)

1. **process_campaigns** (ogni 2 ore, 8am-8pm)
   - Processa tutte le campagne attive
   - Invia email secondo schedule
   - Aggiorna statistiche

2. **process_responses** (ogni 30 minuti)
   - Legge inbox receiver accounts
   - Genera e invia risposte
   - Marca email come lette

3. **reset_daily_counters** (mezzanotte)
   - Reset contatori giornalieri
   - Prepara nuovo giorno

4. **update_metrics** (23:59)
   - Aggiorna metriche giornaliere
   - Calcola tassi
   - Archivia statistiche

## Security Features

1. **Connection Validation**
   - Test SMTP/IMAP prima di salvare account
   - Verifica credenziali

2. **Error Handling**
   - Retry logic per failures
   - Fallback per AI generation
   - Graceful degradation

3. **Safety Limits**
   - Max bounce rate (5%)
   - Auto-pause su problemi
   - Rate limiting

4. **Data Protection**
   - Database isolation
   - Environment variables per secrets
   - Logging sicuro (no passwords)

## Performance

### Capacità
- SQLite: 100-500 emails/giorno
- PostgreSQL: 10,000+ emails/giorno
- Scalabile orizzontalmente con multiple workers

### Ottimizzazioni
- Async I/O (SMTP/IMAP)
- Connection pooling
- Background tasks (Celery)
- Distributed processing

## Future Enhancements

### Planned Features
- [ ] Web dashboard UI
- [ ] Email template editor
- [ ] A/B testing support
- [ ] Spam score checking
- [ ] IP rotation support
- [ ] Webhook notifications
- [ ] Multi-language support
- [ ] Export reports (PDF/CSV)
- [ ] Integration con ESP (SendGrid, etc.)
- [ ] Machine learning per optimal timing

### Possible Integrations
- Zapier/Make.com
- Slack notifications
- Prometheus metrics
- Grafana dashboards
- Stripe billing

## Deployment Options

1. **Development** (locale)
   ```bash
   ./scripts/run_dev.sh
   ```

2. **Docker Compose** (più semplice)
   ```bash
   docker-compose up -d
   ```

3. **Kubernetes** (scalabile)
   - Helm charts (coming soon)

4. **VPS/Cloud** (manual)
   - systemd services
   - nginx reverse proxy
   - Let's Encrypt SSL

## Testing

```bash
# Run tests
make test

# Run with coverage
poetry run pytest --cov=warmit --cov-report=html

# Lint code
make lint

# Format code
make format
```

## Documentation

- [README.md](README.md) - Overview e quick start
- [USAGE.md](USAGE.md) - Guida completa utilizzo
- [FAQ.md](FAQ.md) - Domande frequenti
- [API Docs](http://localhost:8000/docs) - Swagger UI interattiva

## Contributing

Contributions are welcome! Areas:
- Bug fixes
- Feature development
- Documentation improvements
- Testing
- Translations

## License

MIT License - See [LICENSE](LICENSE) for details

## Credits

Built with:
- FastAPI by Sebastián Ramírez
- SQLAlchemy by Mike Bayer
- Celery by Ask Solem
- Python community

AI providers:
- OpenRouter (https://openrouter.ai)
- Groq (https://groq.com)

## Contact

- GitHub: https://github.com/yourusername/warmit
- Issues: https://github.com/yourusername/warmit/issues
- Email: support@yourdomain.com

---

**Made with ❤️ by Giovanni Rapa**

**Version:** 0.1.0
**Status:** Beta
**Last Updated:** 2026-01-14
