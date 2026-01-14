# Multi-Account Setup Guide

Guida completa per configurare warming con multipli account sender e receiver.

## 🎯 Scenario Ideale

**10 Sender (da scaldare) + 10 Receiver (risponditori) = Setup Ottimale**

### Vantaggi

✅ **Distribuzione Naturale**: Email distribuite su multipli receiver
✅ **Scalabilità**: Aggiungi sender/receiver senza limiti
✅ **Resilienza**: Se 1 account ha problemi, gli altri continuano
✅ **Efficienza**: Warming parallelo di multipli domini
✅ **Realismo**: Simula organizzazione con più utenti

---

## 📊 Matematica del Warming

### Esempio: 10 Sender + 10 Receiver

**Settimana 1** (5 email/giorno per sender):
```
10 sender × 5 email/giorno = 50 email totali/giorno
50 email ÷ 10 receiver = ~5 email/receiver/giorno

✅ Carico bilanciato automaticamente
✅ Nessun receiver sovraccarico
✅ Pattern naturale distribuito
```

**Settimana 4** (25 email/giorno per sender):
```
10 sender × 25 email/giorno = 250 email totali/giorno
250 email ÷ 10 receiver = ~25 email/receiver/giorno

✅ Ancora gestibile
✅ Distribuzione automatica
✅ High engagement
```

### Scalabilità

| Sender | Receiver | Email/Day (Week 1) | Email/Day (Week 6) |
|--------|----------|--------------------|--------------------|
| 5 | 5 | 25 | 250 |
| 10 | 10 | 50 | 500 |
| 20 | 15 | 100 | 1,000 |
| 50 | 30 | 250 | 2,500 |

---

## 🛠️ Setup Methods

> **📘 Guida Provider Italiani**: Per configurazione dettagliata di Gmail, Outlook e Libero, vedi [PROVIDER_SETUP_IT.md](PROVIDER_SETUP_IT.md)

### Metodo 1: Dashboard (Consigliato)

**Vantaggi**: Visuale, semplice, no script

#### Step 1: Aggiungi Tutti i SENDER

```
1. Apri http://localhost:8501
2. Vai su "Add New" → "Add Account"
3. Per ogni sender:
   - Email: vendite@tuodominio.com
   - Type: sender
   - SMTP/IMAP config
   - Password
   - [Add Account]
4. Ripeti 10 volte
```

#### Step 2: Aggiungi Tutti i RECEIVER

```
1. "Add New" → "Add Account"
2. Per ogni receiver:
   - Email: warmup1@gmail.com
   - Type: receiver
   - SMTP: smtp.gmail.com
   - IMAP: imap.gmail.com
   - Password: [App Password Gmail]
   - [Add Account]
3. Ripeti 10 volte
```

#### Step 3: Crea Campagna

```
1. "Add New" → "Create Campaign"
2. Name: "Warming Completo 2026"
3. Sender Accounts: ✅ Select all 10
4. Receiver Accounts: ✅ Select all 10
5. Duration: 6 weeks
6. [Create Campaign]
```

**Done!** 🎉

---

### Metodo 2: Script Automatico

**Vantaggi**: Veloce, ripetibile, bulk import

#### Usa lo Script Fornito

```bash
cd examples/
chmod +x setup_multi_accounts.sh
./setup_multi_accounts.sh
```

**Lo script:**
1. Aggiunge 10 sender
2. Aggiunge 10 receiver (chiede password per ognuno)
3. Crea campagna automaticamente

#### Personalizza lo Script

Modifica `setup_multi_accounts.sh`:

```bash
# Cambia questi array con i tuoi account
SENDERS=(
    "tuo1@domain.com"
    "tuo2@domain.com"
    # ... aggiungi i tuoi
)

SENDER_SMTP_HOST="smtp.tuodomain.com"
SENDER_PASSWORD="password_comune"  # O chiedi per ognuno

RECEIVERS=(
    "warmup1@gmail.com"
    "warmup2@outlook.com"
    # ... aggiungi i tuoi
)
```

---

### Metodo 3: CSV Import (Futuro)

**Prossima versione:** Import da CSV/Excel
```csv
email,type,smtp_host,smtp_port,imap_host,imap_port,password
vendite@domain.com,sender,smtp.domain.com,587,imap.domain.com,993,pass1
info@domain.com,sender,smtp.domain.com,587,imap.domain.com,993,pass2
```

---

## 🎨 Patterns di Utilizzo

### Pattern 1: Stesso Dominio

**Scenario**: Warming multipli account su stesso dominio

```
SENDER (10):           DOMAIN
├── vendite@           ├── tuodominio.com
├── info@              ├── tuodominio.com
├── supporto@          ├── tuodominio.com
├── marketing@         ├── tuodominio.com
└── ...                └── tuodominio.com

RECEIVER (10):         PROVIDER
├── warmup1@           ├── gmail.com
├── warmup2@           ├── gmail.com
├── warmup3@           ├── outlook.com
├── warmup4@           ├── yahoo.com
└── ...                └── (mix)
```

**Vantaggi:**
- Warm domain reputation globalmente
- Tutti i sender beneficiano
- Setup SMTP/IMAP uguale per tutti

**SMTP Config (uguale per tutti):**
```json
{
  "smtp_host": "smtp.tuodominio.com",
  "smtp_port": 587,
  "imap_host": "imap.tuodominio.com",
  "imap_port": 993
}
```

---

### Pattern 2: Domini Multipli

**Scenario**: Warming account su domini diversi

```
SENDER (10):           DOMAIN
├── sales@             ├── company1.com
├── info@              ├── company1.com
├── support@           ├── company2.com
├── contact@           ├── company2.com
├── hello@             ├── company3.com
└── ...                └── (vari)

RECEIVER (10): Stessi per tutti!
├── warmup1@gmail.com
├── warmup2@outlook.com
└── ...
```

**Vantaggi:**
- Warm multipli domini contemporaneamente
- Receiver pool condiviso
- Efficiente uso risorse

**Setup:** SMTP/IMAP diverso per ogni dominio

---

### Pattern 3: Scaling Graduale

**Scenario**: Inizi piccolo, scali progressivamente

```
Week 1-2:
  2 sender + 3 receiver

Week 3-4:
  5 sender + 5 receiver  (aggiungi durante warming)

Week 5-6:
  10 sender + 10 receiver  (aggiungi ancora)
```

**Vantaggi:**
- Start cauto
- Validi sistema prima
- Scali su successo

---

## 🔧 Best Practices

### Ratio Sender:Receiver

| Sender | Receiver Min | Receiver Opt | Note |
|--------|--------------|--------------|------|
| 1 | 2 | 3-5 | Sufficiente |
| 5 | 5 | 8-10 | Bilanciato |
| 10 | 10 | 15-20 | Ideale |
| 20+ | 15+ | 25-30 | Enterprise |

**Regola empirica**: `Receiver ≥ Sender` (minimo 1:1)

### Diversificazione Receiver

**Buona diversificazione:**
```
40% Gmail (warmup1-4@gmail.com)
30% Outlook (warmup5-7@outlook.com)
20% Yahoo (warmup8-9@yahoo.com)
10% Altri (warmup10@proton.me)
```

**Perché?**
- Simula destinatari reali
- ESP diversi = pattern naturale
- Nessun provider dominante

### Password Management

**Opzione A: Password Comune**
```bash
# Stessa password per tutti i sender dello stesso dominio
SENDER_PASSWORD="SecurePass123!"

# Pro: Setup veloce
# Contro: Meno sicuro
```

**Opzione B: Password Individuali**
```bash
# Password diversa per ogni account
vendite@domain.com    → VenPass123!
info@domain.com       → InfoPass456!

# Pro: Più sicuro
# Contro: Setup più lungo
```

**Opzione C: Password Manager**
```bash
# Usa 1Password, Bitwarden, etc.
# Genera password uniche
# Salva in vault

# Pro: Massima sicurezza
# Contro: Richiede integrazione
```

### Naming Convention

**SENDER (produzione):**
```
vendite@domain.com
info@domain.com
supporto@domain.com
```

**RECEIVER (warming):**
```
warmup1@gmail.com
warmup2@gmail.com
warmup-company-01@outlook.com
```

**Perché "warmup" nel nome?**
- Riconoscimento immediato
- Evita confusione con account reali
- Facile gestione bulk

---

## 📊 Monitoring Multi-Account

### Dashboard Overview

```
Dashboard → Overview

ACCOUNTS
├── Senders:    10 active
├── Receivers:  10 active
└── Total:      20 accounts

CAMPAIGNS
├── Active:     1
├── Progress:   Week 3/6 (50%)
└── Status:     🟢 Healthy

TODAY'S ACTIVITY
├── Sent:       150/250
├── Open Rate:  87%
└── Reply Rate: 82%
```

### Per-Account View

```
Dashboard → Accounts → Filter: Sender

vendite@domain.com      ✅ Active
├── Sent: 75
├── Open: 87%
├── Bounce: 0.5%
└── Status: 🟢 Healthy

info@domain.com         ✅ Active
├── Sent: 73
├── Open: 85%
├── Bounce: 1.2%
└── Status: 🟢 Healthy

...
```

### Campaign Metrics

```
Dashboard → Campaigns → "Warming Completo 2026"

Progress: ████████░░ 80% (Week 5/6)

METRICS
├── Total Sent:     3,500 emails
├── Avg Open:       86%
├── Avg Reply:      81%
├── Avg Bounce:     1.3%
└── Health:         🟢 Excellent

PER SENDER
├── All 10 active
├── 0 paused
├── 0 errors
└── Average daily: 25 emails
```

---

## 🚨 Troubleshooting

### Alcuni Sender Non Inviano

**Causa**: Bounce rate alto o errori SMTP

**Soluzione:**
```bash
# Check account status
Dashboard → Accounts → Filter: Error

# Fix account
1. Verifica password
2. Check SMTP/IMAP config
3. Test connection
4. Resume account
```

### Alcuni Receiver Non Rispondono

**Causa**: IMAP non funziona o password sbagliata

**Soluzione:**
```bash
# Check logs
docker compose -f docker/docker-compose.prod.yml logs worker | grep receiver

# Verifica inbox manualmente
# Fix password/IMAP config
# Restart worker
```

### Distribuzione Non Bilanciata

**Causa**: Casualità del sistema

**Soluzione:**
- ✅ Normale: Piccole variazioni sono OK
- ✅ Nel lungo periodo si bilancia
- ❌ Se molto sbilanciata: check logs

---

## 💡 Tips & Tricks

### Tip 1: Staging Before Production

```
1. Setup 2 sender + 2 receiver (test)
2. Run 1 week
3. Verify tutto funziona
4. Scale to 10 + 10
```

### Tip 2: Batch Adding

```
# Aggiungi 5 sender, check
# Poi altri 5
# Invece di tutti e 10 insieme
```

### Tip 3: Gradual Campaign Start

```
# Campagna 1: 5 sender + 5 receiver
# Dopo 2 settimane:
# Campagna 2: altri 5 sender + stessi receiver
```

### Tip 4: Shared Receiver Pool

```
# Crea pool grande di receiver
RECEIVERS: 20 account

# Usa per multiple campagne
Campagna A: 10 sender → 20 receiver
Campagna B: 5 sender → stessi 20 receiver

✅ Massima efficienza
```

---

## 📈 Scaling Beyond 10+10

### 20 Sender + 15 Receiver

**Setup:**
```
Week 1: 20 × 5 = 100 emails/day
Week 6: 20 × 50 = 1,000 emails/day

Receiver load: 50-70 email/day
✅ Gestibile
```

**Resources:**
```yaml
worker:
  command: celery worker --concurrency=8
  resources:
    memory: 4G
    cpus: '4.0'
```

### 50+ Sender

**Multi-Campaign Strategy:**
```
Campaign 1: Sender 1-25  → Receiver Pool A
Campaign 2: Sender 26-50 → Receiver Pool B

O

Campaign 1: Tutti 50 sender → 30 receiver pool
```

**Infrastructure:**
```yaml
# Scale workers
worker:
  deploy:
    replicas: 2  # 2 worker containers

# More CPU/RAM
resources:
  memory: 8G
  cpus: '8.0'
```

---

## ✅ Checklist Multi-Account

Prima di iniziare:

- [ ] Hai almeno 2-3 receiver per ogni sender
- [ ] App Password create per Gmail accounts
- [ ] SMTP/IMAP credentials corrette
- [ ] DNS records (SPF/DKIM/DMARC) configurati
- [ ] Docker running
- [ ] WarmIt started (`./start.sh`)
- [ ] Dashboard accessible (http://localhost:8501)

Setup completato:

- [ ] Tutti i sender aggiunti e active
- [ ] Tutti i receiver aggiunti e active
- [ ] Campagna creata
- [ ] Status: Active
- [ ] Prime email inviate
- [ ] Check logs per errori
- [ ] Monitor dashboard giornalmente

---

## 🎓 Real-World Example

**Azienda con 10 persone nel team vendite:**

```
SETUP
├── 10 account email aziendali (sender)
├── 10 account Gmail personali (receiver)
└── 1 campagna di 6 settimane

RISULTATI DOPO 6 SETTIMANE
├── 3,500 email inviate
├── 87% open rate
├── 83% reply rate
├── 1.2% bounce rate
├── ✅ Domain reputation eccellente
└── ✅ Pronto per cold email campaign

TEMPO RISPARMIATO
├── Warming manuale: 40+ ore
├── WarmIt automatico: 15 minuti setup
└── ROI: 160x
```

---

**Ready to warm 10+ accounts? Let's go! 🔥**

Per domande: [FAQ.md](FAQ.md)
