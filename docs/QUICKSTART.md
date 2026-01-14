# WarmIt - Quick Start Guide

Guida rapida per iniziare subito con WarmIt!

## 🚀 Setup in 5 Minuti

### 1. Prerequisiti

```bash
# Verifica Python 3.11+
python3 --version

# Installa Poetry (se non l'hai)
curl -sSL https://install.python-poetry.org | python3 -

# Installa Redis
# macOS:
brew install redis

# Ubuntu/Debian:
sudo apt-get install redis-server
```

### 2. Setup Progetto

```bash
# Clone o vai nella directory
cd WarmIt

# Esegui setup automatico
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. Configura API Key

Scegli un provider AI gratuito:

**Opzione A: OpenRouter (Raccomandato)**
1. Vai su https://openrouter.ai
2. Registrati e ottieni API key
3. Modifica `.env`:
```bash
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
AI_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

**Opzione B: Groq**
1. Vai su https://console.groq.com
2. Registrati e crea API key
3. Modifica `.env`:
```bash
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your-key-here
AI_MODEL=llama-3.3-70b-versatile
```

### 4. Avvia Servizi

```bash
# Modo facile - tutto in uno
make dev

# Oppure manualmente in terminali separati:
# Terminal 1:
redis-server

# Terminal 2:
make api

# Terminal 3:
make worker

# Terminal 4:
make beat
```

### 5. Verifica Installazione

```bash
# Check API
curl http://localhost:8000/health

# Dovrebbe rispondere:
# {"status":"healthy"}
```

## 📧 Primo Warming

### 1. Aggiungi Account Gmail

Prima, crea una [App Password Gmail](https://myaccount.google.com/apppasswords):
- Vai su Google Account → Security
- Abilita 2-Step Verification
- Crea App Password per "Mail"

Poi aggiungi l'account:

```bash
# Sender (account da riscaldare)
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tuo-sender@gmail.com",
    "type": "sender",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_use_tls": true,
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "imap_use_ssl": true,
    "password": "la-tua-app-password"
  }'
```

```bash
# Receiver (account che risponde)
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tuo-receiver@gmail.com",
    "type": "receiver",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_use_tls": true,
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "imap_use_ssl": true,
    "password": "altra-app-password"
  }'
```

### 2. Crea Campagna

```bash
curl -X POST http://localhost:8000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prima Campagna",
    "sender_account_ids": [1],
    "receiver_account_ids": [2],
    "duration_weeks": 4
  }'
```

### 3. Avvia Warming (Test Manuale)

```bash
# Invia prime email (normalmente automatico)
curl -X POST http://localhost:8000/api/campaigns/1/process
```

### 4. Monitora Progresso

```bash
# Via CLI
make cli stats
make cli campaigns

# Via API
curl http://localhost:8000/api/metrics/system
curl http://localhost:8000/api/campaigns/1
```

## 📊 Dashboard API

Apri nel browser: **http://localhost:8000/docs**

Qui trovi:
- Documentazione interattiva Swagger
- Test endpoint direttamente
- Schema dati completo

## 🔧 Comandi Utili

### Via Makefile

```bash
make help       # Lista comandi
make setup      # Setup iniziale
make dev        # Avvia tutto
make test       # Run tests
make format     # Formatta codice
make lint       # Lint codice
make clean      # Pulisci temporanei
```

### Via CLI

```bash
# Statistiche sistema
poetry run python scripts/cli.py stats

# Lista accounts
poetry run python scripts/cli.py accounts

# Lista campagne
poetry run python scripts/cli.py campaigns

# Verifica dominio
poetry run python scripts/cli.py check-domain esempio@domain.com

# Inizializza DB
poetry run python scripts/cli.py init-db
```

### Via API

```bash
# Lista tutti gli accounts
curl http://localhost:8000/api/accounts

# Dettagli account
curl http://localhost:8000/api/accounts/1

# Metriche account
curl http://localhost:8000/api/metrics/accounts/1

# Pausa campagna
curl -X PATCH http://localhost:8000/api/campaigns/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "paused"}'
```

## 🎯 Best Practices

1. **Inizia Piano**
   - 1-2 sender accounts
   - 2-3 receiver accounts
   - Monitora primi giorni

2. **Verifica DNS**
   ```bash
   # SPF
   dig TXT tuodominio.com

   # DKIM (se custom domain)
   # Configura in Google Admin Console

   # DMARC
   dig TXT _dmarc.tuodominio.com
   ```

3. **Monitora Metriche**
   - Bounce rate < 5%
   - Open rate > 70%
   - Reply rate > 50%

4. **Gradualità**
   - Non saltare settimane
   - Mantieni volume costante
   - No pause lunghe

## ❌ Troubleshooting Rapido

### Redis non si connette
```bash
redis-server
redis-cli ping  # Deve rispondere PONG
```

### Celery non parte
```bash
# Reinstalla
poetry install

# Test diretto
poetry run celery -A warmit.tasks worker --loglevel=debug
```

### Email non si inviano
```bash
# Verifica credenziali
# Per Gmail usa App Password, non password normale

# Abilita IMAP in Gmail:
# Settings → Forwarding and POP/IMAP → Enable IMAP

# Test connessione
curl -X POST http://localhost:8000/api/accounts/1/check-domain
```

### API lenta
```bash
# Usa PostgreSQL invece di SQLite
# Modifica in .env:
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/warmit
```

## 📚 Prossimi Passi

1. **Leggi la documentazione completa**
   - [USAGE.md](USAGE.md) - Guida dettagliata
   - [FAQ.md](FAQ.md) - Domande frequenti
   - [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Overview tecnico

2. **Esplora esempi**
   ```bash
   chmod +x examples/api_examples.sh
   ./examples/api_examples.sh
   ```

3. **Personalizza configurazione**
   - Modifica schedule in `src/warmit/tasks/__init__.py`
   - Personalizza topics AI in `src/warmit/services/ai_generator.py`
   - Adatta limiti in `.env`

4. **Production deployment**
   - Setup Docker: `docker-compose up -d`
   - Configura HTTPS con nginx
   - Setup backup automatici

## 🆘 Supporto

Hai problemi?

1. Controlla [FAQ.md](FAQ.md)
2. Verifica logs: `tail -f logs/celery-worker.log`
3. Apri issue su GitHub
4. Email: support@yourdomain.com

## 🎉 Successo!

Se vedi questo, sei pronto:
- ✅ API risponde su http://localhost:8000
- ✅ Redis connesso
- ✅ Celery worker running
- ✅ Account configurati
- ✅ Campagna attiva

**Il warming è ora automatico!**

Le email verranno inviate ogni 2 ore e le risposte saranno automatiche ogni 30 minuti.

Monitora il progresso con:
```bash
make cli campaigns
```

Buon warming! 🔥
