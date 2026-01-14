# WarmIt - FAQ & Troubleshooting

## Frequently Asked Questions

### General

**Q: Cos'è l'email warming?**
A: L'email warming è il processo di costruire gradualmente la reputazione di un indirizzo email o dominio inviando un volume crescente di email nel tempo. Questo aiuta a evitare che le tue email finiscano nello spam.

**Q: Quanto tempo ci vuole per riscaldare un account?**
A: Dipende dall'età del dominio:
- Domini nuovi (< 30 giorni): 6-8 settimane
- Domini moderatamente nuovi (30-180 giorni): 4-6 settimane
- Domini stabiliti (> 180 giorni): 2-4 settimane

**Q: Posso usare WarmIt con Gmail gratuito?**
A: Sì, ma devi usare le App Password e abilitare IMAP nelle impostazioni. Gmail gratuito ha un limite di 500 email/giorno.

**Q: WarmIt funziona con qualsiasi provider email?**
A: Sì, funziona con qualsiasi provider che supporti SMTP e IMAP (Gmail, Outlook, Yahoo, domini custom, etc.).

**Q: È sicuro? Le mie credenziali sono protette?**
A: Le credenziali sono salvate nel database. In produzione, dovresti:
- Usare variabili d'ambiente per credenziali sensibili
- Criptare il database
- Usare HTTPS per l'API
- Limitare l'accesso alla rete

### Setup & Configuration

**Q: Come ottengo una API key per OpenRouter/Groq?**
A:
- OpenRouter: https://openrouter.ai - Registrati e copia l'API key
- Groq: https://console.groq.com - Registrati e crea una API key
Entrambi offrono tier gratuiti generosi.

**Q: Come creo una Gmail App Password?**
A:
1. Vai su https://myaccount.google.com/security
2. Abilita 2-Step Verification
3. Vai su "App passwords"
4. Genera una nuova password per "Mail"
5. Usa quella password in WarmIt

**Q: Quanti account sender dovrei usare?**
A: Inizia con 2-3 account sender. Puoi aggiungerne altri man mano che il sistema è stabile.

**Q: Quanti account receiver servono?**
A: Almeno 2-3 receiver account. Più ne hai, più naturale appare il traffico.

### Email Sending

**Q: Perché le mie email non vengono inviate?**
A: Controlla:
1. Credenziali corrette (usa App Password per Gmail)
2. IMAP abilitato
3. Firewall non blocca porte 587 (SMTP) e 993 (IMAP)
4. Account non bloccato dal provider
5. Logs: `tail -f logs/celery-worker.log`

**Q: Come posso testare l'invio senza aspettare lo scheduler?**
A: Usa l'endpoint manuale:
```bash
curl -X POST http://localhost:8000/api/campaigns/1/process
```

**Q: Il bounce rate è alto, cosa faccio?**
A:
1. Verifica DNS records (SPF, DKIM, DMARC)
2. Controlla che i receiver accounts esistano
3. Riduci il volume giornaliero
4. Pausa la campagna temporaneamente

**Q: Come distribuisco gli invii durante il giorno?**
A: WarmIt automaticamente invia ogni 2 ore. Puoi modificare la frequenza in `src/warmit/tasks/__init__.py`.

### AI & Content

**Q: Le email generate dall'AI sembrano spam?**
A: L'AI è configurata per generare email naturali e conversazionali. Usa temperature alta (0.8) e varia topics/tone per massima naturalezza.

**Q: Posso personalizzare i contenuti generati?**
A: Sì, modifica `src/warmit/services/ai_generator.py`:
- Aggiungi topics in `TOPICS`
- Modifica tones in `TONES`
- Cambia i prompt templates

**Q: Cosa succede se l'API AI fallisce?**
A: WarmIt ha un fallback system che usa template predefiniti per continuare a inviare.

**Q: I modelli gratuiti sono sufficienti?**
A: Sì! Llama 3.3 70B (gratuito su OpenRouter) è ottimo per generare email naturali.

### Monitoring & Metrics

**Q: Come monitoro il progresso?**
A: Usa il CLI o l'API:
```bash
# CLI
poetry run python scripts/cli.py stats
poetry run python scripts/cli.py campaigns

# API
curl http://localhost:8000/api/metrics/system
```

**Q: Cosa indica un buon open rate?**
A: Per warmup emails tra account controllati, punta a 70-90% open rate.

**Q: Come so quando il warming è completo?**
A: La campagna si completa automaticamente dopo il numero di settimane configurato. Indicatori di successo:
- Open rate > 70%
- Bounce rate < 2%
- Reply rate > 50%
- Nessuna segnalazione spam

### Database & Performance

**Q: SQLite è sufficiente per produzione?**
A: SQLite va bene per 1-10 account. Per più account o traffico alto, usa PostgreSQL:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/warmit
```

**Q: Come faccio backup del database?**
A:
```bash
# SQLite
cp warmit.db warmit_backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump warmit > warmit_backup_$(date +%Y%m%d).sql
```

**Q: Quante email può gestire WarmIt?**
A: Con setup corretto:
- SQLite: 100-500 email/giorno
- PostgreSQL: 10,000+ email/giorno

### Automation

**Q: Come faccio a far partire WarmIt automaticamente all'avvio?**
A: Usa systemd (Linux) o launchd (macOS). Esempio in USAGE.md.

**Q: Posso cambiare la frequenza di invio?**
A: Sì, modifica `beat_schedule` in `src/warmit/tasks/__init__.py`:
```python
"process-campaigns": {
    "task": "warmit.tasks.warming.process_campaigns",
    "schedule": 3600.0,  # Ogni ora invece di ogni 2 ore
}
```

**Q: Come funziona il response bot?**
A: Ogni 30 minuti:
1. Controlla inbox dei receiver accounts
2. Legge email non lette dai sender accounts
3. Genera risposta con AI
4. Invia risposta con delay casuale
5. Marca email come letta

### Troubleshooting

**Q: Redis connection refused**
A:
```bash
# Avvia Redis
redis-server

# Verifica sia running
redis-cli ping
# Dovrebbe rispondere: PONG
```

**Q: Celery worker non si avvia**
A: Controlla:
```bash
# Verifica Redis
redis-cli ping

# Controlla logs
poetry run celery -A warmit.tasks worker --loglevel=debug

# Reinstalla dipendenze
poetry install
```

**Q: ModuleNotFoundError: No module named 'warmit'**
A: Aggiungi src al PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**Q: SSL/TLS errors con SMTP/IMAP**
A: Prova a cambiare le impostazioni:
```json
{
  "smtp_use_tls": true,  // o false
  "imap_use_ssl": true   // o false
}
```

**Q: API risponde lentamente**
A:
- Usa PostgreSQL invece di SQLite
- Aggiungi indici al database
- Aumenta worker Celery
- Usa Redis cache

**Q: Email finiscono in spam anche dopo warming**
A:
1. Verifica DNS records:
   ```bash
   dig TXT yourdomain.com
   dig TXT _dmarc.yourdomain.com
   ```
2. Controlla SPF: `v=spf1 include:_spf.google.com ~all`
3. Abilita DKIM in Google Admin Console
4. Aggiungi DMARC: `v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com`
5. Warming più lento
6. Content meno "spammy"

### Production Deployment

**Q: Come faccio deploy in produzione?**
A: Opzioni:
1. Docker Compose (più semplice)
2. Kubernetes (scalabile)
3. VPS con systemd
4. PaaS (Heroku, Railway, etc.)

**Q: Quali sono le best practices di sicurezza?**
A:
- Usa HTTPS per l'API (nginx + Let's Encrypt)
- Cripta database con LUKS o encryption at rest
- Usa secrets manager (Vault, AWS Secrets Manager)
- Limita accesso con firewall
- Monitora logs per attività sospette
- Backup regolari automatici

**Q: Come scalo per gestire più account?**
A:
1. Passa a PostgreSQL
2. Aggiungi più Celery workers
3. Usa Redis Cluster
4. Distribuisci worker su più macchine
5. Load balancer per API

### Legal & Compliance

**Q: È legale usare WarmIt?**
A: Sì, purché:
- Usi account che possiedi
- Non invii spam
- Rispetti CAN-SPAM Act e GDPR
- Non violi TOS del provider email

**Q: Posso usarlo per cold email campaigns?**
A: WarmIt è progettato per WARMING, non per campagne cold. Dopo il warming, usa tool dedicati per cold email che rispettino le leggi anti-spam.

**Q: Devo informare i destinatari?**
A: Durante il warming, invii solo tra account che controlli, quindi no. Per campagne reali, devi sempre:
- Avere consenso (opt-in)
- Fornire modo di unsubscribe
- Includere indirizzo fisico
- Rispettare GDPR

## Support

Non hai trovato risposta alla tua domanda?

- GitHub Issues: https://github.com/yourusername/warmit/issues
- Email: support@yourdomain.com
- Documentation: https://github.com/yourusername/warmit

## Contribuire

Vuoi migliorare WarmIt?

1. Fork il repository
2. Crea un branch per la tua feature
3. Fai le modifiche
4. Invia una Pull Request

Apprezziamo contributi di:
- Bug fixes
- Nuove feature
- Documentazione
- Test
- Traduzioni
