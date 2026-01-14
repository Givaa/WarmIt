# Configurazione Provider Italiani

Guida completa per configurare Gmail, Outlook e Libero come receiver accounts.

---

## 📧 Gmail

### Perché Gmail?
- ✅ Provider più usato al mondo (40%+ market share)
- ✅ Filtri anti-spam più sofisticati
- ✅ Se passi Gmail, passi quasi tutto
- ✅ Ottimo per testare deliverability

### Configurazione

**IMPORTANTE**: Gmail richiede "App Password" per applicazioni esterne.

#### Step 1: Abilita 2FA
1. Vai su https://myaccount.google.com/security
2. Clicca su "Verifica in due passaggi"
3. Segui la procedura guidata

#### Step 2: Genera App Password
1. Vai su https://myaccount.google.com/apppasswords
2. Seleziona "Mail" come app
3. Seleziona "Altro" come dispositivo
4. Inserisci "WarmIt" come nome
5. Clicca "Genera"
6. **Copia la password di 16 caratteri** (es: `abcd efgh ijkl mnop`)

#### Step 3: Configurazione WarmIt

```json
{
  "email": "warmup1@gmail.com",
  "type": "receiver",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_use_tls": true,
  "imap_host": "imap.gmail.com",
  "imap_port": 993,
  "imap_use_ssl": true,
  "password": "abcd efgh ijkl mnop"  // App Password
}
```

### Troubleshooting Gmail

#### Errore: "Username and password not accepted"
- ✅ Verifica che 2FA sia attivo
- ✅ Usa App Password, non la password normale
- ✅ Copia l'App Password senza spazi

#### Errore: "Too many login attempts"
- ✅ Aspetta 15 minuti
- ✅ Verifica che non ci siano altre app che usano lo stesso account

#### Limiti Gmail
- 📊 500 email/day per account gratuito
- 📊 2,000 email/day per Google Workspace
- ⏱️ Max 100 destinatari per email

---

## 📧 Outlook / Hotmail

### Perché Outlook?
- ✅ Secondo provider più usato
- ✅ Molto usato in ambito aziendale (Microsoft 365)
- ✅ Filtri diversi da Gmail
- ✅ Importante per B2B

### Configurazione

**BUONA NOTIZIA**: Outlook non richiede App Password per SMTP/IMAP base.

#### Step 1: Verifica Impostazioni Account
1. Vai su https://outlook.live.com
2. Settings → View all Outlook settings
3. Mail → Sync email
4. Verifica che "POP and IMAP" sia abilitato

#### Step 2: (Opzionale) App Password per 2FA
Se hai 2FA attivo:
1. Vai su https://account.microsoft.com/security
2. Security → Advanced security options
3. App passwords → Create new app password
4. Copia la password generata

#### Step 3: Configurazione WarmIt

```json
{
  "email": "warmup6@outlook.com",
  "type": "receiver",
  "smtp_host": "smtp-mail.outlook.com",
  "smtp_port": 587,
  "smtp_use_tls": true,
  "imap_host": "outlook.office365.com",
  "imap_port": 993,
  "imap_use_ssl": true,
  "password": "tua_password_normale"  // O App Password se 2FA
}
```

### Domini Supportati
- outlook.com
- outlook.it
- hotmail.com
- hotmail.it
- live.com
- live.it

**Tutti usano la stessa configurazione SMTP/IMAP!**

### Troubleshooting Outlook

#### Errore: "Mailbox unavailable"
- ✅ Verifica che IMAP sia abilitato nelle impostazioni
- ✅ Prova ad accedere via web per sbloccare l'account

#### Errore: "Authentication failed"
- ✅ Se hai 2FA, usa App Password
- ✅ Verifica username (deve essere email completa)

#### Limiti Outlook
- 📊 300 email/day per account gratuito
- 📊 10,000 email/day per Microsoft 365
- ⏱️ Max 100 destinatari per email

---

## 📧 Libero

### Perché Libero?
- ✅ Provider italiano più diffuso
- ✅ Ottimo se i tuoi clienti sono in Italia
- ✅ Comportamento diverso dai provider USA
- ✅ Aggiunge realismo al pattern

### Configurazione

**NOTA**: Libero ha configurazioni diverse per mail.libero.it e posta.libero.it.

#### Step 1: Verifica Tipo Account
- **mail.libero.it**: Webmail classica
- **posta.libero.it**: Nuova interfaccia

#### Step 2: Configurazione WarmIt

**Per account Libero Mail classici:**
```json
{
  "email": "warmup9@libero.it",
  "type": "receiver",
  "smtp_host": "smtp.libero.it",
  "smtp_port": 587,
  "smtp_use_tls": true,
  "imap_host": "imap.libero.it",
  "imap_port": 993,
  "imap_use_ssl": true,
  "password": "tua_password"
}
```

**Per account business (se hai Libero Business):**
```json
{
  "smtp_host": "smtps.libero.it",
  "smtp_port": 465,
  "smtp_use_tls": false,
  "smtp_use_ssl": true
}
```

### Troubleshooting Libero

#### Errore: "Connection refused"
- ✅ Verifica di usare `smtp.libero.it` (non smtps)
- ✅ Porta 587 con TLS (non 465)
- ✅ Alcuni account Libero limitano SMTP/IMAP esterni

#### Errore: "Relay access denied"
- ✅ Accedi via webmail almeno una volta
- ✅ Verifica che SMTP/IMAP siano abilitati nel tuo piano

#### Limiti Libero
- 📊 100-200 email/day per account gratuito
- 📊 500+ email/day per account Premium
- ⏱️ Rate limit più aggressivi dei provider USA
- ⚠️ Alcuni account free potrebbero non supportare SMTP/IMAP

### Domini Supportati
- libero.it
- inwind.it
- iol.it
- blu.it
- giallo.it

---

## 📧 Aruba (Domini Personalizzati)

### Perché Aruba?
- ✅ Hosting italiano più diffuso
- ✅ Ottimo per domini custom aziendali
- ✅ Configurazione SMTP/IMAP standard
- ✅ Perfetto per sender accounts

### Configurazione

**NOTA**: Aruba supporta sia porta 587 (TLS) che 465 (SSL). Consigliamo 587.

#### Verifica Configurazione
1. Accedi al pannello Aruba
2. Email → Gestione → Configurazione
3. Verifica che IMAP/SMTP siano attivi

#### Configurazione WarmIt

**Per domini hosted su Aruba:**
```json
{
  "email": "vendite@tuodominio.com",
  "type": "sender",
  "smtp_host": "smtp.tuodominio.com",
  "smtp_port": 587,
  "smtp_use_tls": true,
  "imap_host": "imap.tuodominio.com",
  "imap_port": 993,
  "imap_use_ssl": true,
  "password": "tua_password"
}
```

**Alternativa con porta 465 (SSL):**
```json
{
  "smtp_host": "smtps.tuodominio.com",
  "smtp_port": 465,
  "smtp_use_tls": false,
  "smtp_use_ssl": true
}
```

### Configurazioni Comuni Aruba

| Tipo | SMTP | IMAP | Note |
|------|------|------|------|
| Domini Custom | smtp.tuodominio.com:587 | imap.tuodominio.com:993 | Raccomandato |
| Domini Custom (SSL) | smtps.tuodominio.com:465 | imaps.tuodominio.com:993 | Alternativa |
| Email Aruba | smtp.aruba.it:587 | imap.aruba.it:993 | Solo per @aruba.it |

### Troubleshooting Aruba

#### Errore: "Authentication failed"
- ✅ Verifica username (deve essere email completa: `vendite@tuodominio.com`)
- ✅ Controlla che SMTP/IMAP siano abilitati nel pannello
- ✅ Verifica di non avere autenticazione a 2 fattori attiva

#### Errore: "Connection refused"
- ✅ Prova entrambe le porte (587 e 465)
- ✅ Verifica DNS: `smtp.tuodominio.com` deve puntare ai server Aruba
- ✅ Controlla firewall/antivirus

#### Errore: "Relay access denied"
- ✅ Usa sempre la stessa email per autenticazione e invio
- ✅ Verifica che il dominio sia attivo e configurato correttamente

#### Limiti Aruba
- 📊 Dipende dal piano hosting
- 📊 Piani base: 100-200 email/ora
- 📊 Piani business: 500+ email/ora
- ⏱️ Rate limit variabile per piano

### Domini Multipli su Aruba

Se hai più domini hosted su Aruba:
```bash
SENDERS=(
    "vendite@azienda1.com"    # smtp.azienda1.com
    "info@azienda2.com"        # smtp.azienda2.com
    "support@azienda3.com"     # smtp.azienda3.com
)

# Lo script auto-rileva il dominio e configura smtp.dominio.com
```

### Best Practices Aruba

1. **Usa sempre TLS (porta 587)** invece di SSL (porta 465)
2. **Verifica SPF/DKIM/DMARC** nel pannello Aruba
3. **Monitora i limiti** del tuo piano hosting
4. **Backup configurazione** prima di modificare impostazioni
5. **Test connessione** prima di iniziare warming

---

## 🎯 Distribuzione Consigliata

### Setup Ottimale Italiano

**Caso tipico: Domini aziendali Aruba + Receiver misti**

```
SENDERS (10 - da scaldare)
├── vendite@tuodominio.com      [Aruba]
├── info@tuodominio.com          [Aruba]
├── supporto@tuodominio.com      [Aruba]
├── marketing@tuodominio.com     [Aruba]
├── ... (altri account aziendali)

RECEIVERS (10 - risponditori)
├── warmup1@gmail.com            [Gmail - 40%]
├── warmup2@gmail.com
├── warmup3@gmail.com
├── warmup4@gmail.com
├── warmup5@outlook.com          [Outlook - 30%]
├── warmup6@outlook.it
├── warmup7@hotmail.com
├── warmup8@libero.it            [Libero - 20%]
├── warmup9@libero.it
└── warmup10@yahoo.it            [Yahoo - 10%]
```

### Perché questa distribuzione?

| Sender | Provider | Motivo |
|--------|----------|--------|
| Aruba | Domini custom | Caselle aziendali da scaldare |

| Receiver | % | Motivo |
|----------|---|--------|
| Gmail | 40% | Market leader, filtri più severi |
| Outlook | 30% | Molto usato B2B, Microsoft 365 |
| Libero | 20% | Provider italiano, pattern locale |
| Yahoo | 10% | Diversificazione extra |

**Vantaggi:**
- ✅ Simula destinatari reali italiani
- ✅ Testa i 3 provider più usati in Italia
- ✅ Pattern naturale e distribuito
- ✅ Se passa su tutti e 3, passa ovunque

---

## 🔧 Setup Rapido con Script

Usa lo script automatico con la configurazione ottimale:

```bash
cd examples/
chmod +x setup_multi_accounts.sh
./setup_multi_accounts.sh
```

Lo script:
- ✅ Aggiunge 5 Gmail + 3 Outlook + 2 Libero automaticamente
- ✅ Richiede password per ogni account
- ✅ Crea campagna pronta all'uso
- ✅ Ricorda di usare App Password per Gmail

---

## 📊 Monitoraggio per Provider

### Dashboard View

Puoi filtrare per provider nella dashboard:

```
Dashboard → Accounts → Filter: Email contains

Gmail:   @gmail.com     (5 accounts)
Outlook: @outlook.com   (3 accounts)
Libero:  @libero.it     (2 accounts)
```

### Metrics per Provider

```sql
-- Query esempio per statistiche per provider
SELECT
  CASE
    WHEN email LIKE '%gmail.com' THEN 'Gmail'
    WHEN email LIKE '%outlook%' OR email LIKE '%hotmail%' THEN 'Outlook'
    WHEN email LIKE '%libero.it' THEN 'Libero'
  END as provider,
  COUNT(*) as accounts,
  AVG(open_rate) as avg_open_rate,
  AVG(reply_rate) as avg_reply_rate
FROM accounts
WHERE type = 'receiver'
GROUP BY provider;
```

---

## ⚠️ Attenzioni Importanti

### Gmail
- ⚠️ **SEMPRE usare App Password**
- ⚠️ 2FA è obbligatorio per App Password
- ⚠️ Ogni account Gmail conta verso i 500 email/day limit

### Outlook
- ⚠️ Account inattivi vengono disabilitati dopo 270 giorni
- ⚠️ Rate limit più bassi per account nuovi
- ⚠️ Usa sempre email completa come username

### Libero
- ⚠️ **Limiti più stretti** rispetto a Gmail/Outlook
- ⚠️ Account free potrebbero non supportare IMAP/SMTP
- ⚠️ Considera account Premium per produzione
- ⚠️ Più soggetto a blocchi temporanei

---

## 💡 Best Practices

### Creazione Account

1. **Gmail**
   - Crea 5 account con nomi diversi
   - Usa numero di telefono diverso per ogni account (o recovery email)
   - Attiva 2FA immediatamente
   - Genera App Password subito dopo creazione

2. **Outlook**
   - Crea 3 account (puoi usare stesso telefono)
   - Varia tra outlook.com, outlook.it, hotmail.com
   - Abilita IMAP nelle impostazioni
   - (Opzionale) Attiva 2FA per sicurezza

3. **Libero**
   - Crea 2 account Libero
   - Accedi via webmail almeno una volta
   - Verifica che SMTP/IMAP siano attivi
   - Considera Premium se limiti sono troppo bassi

### Rotazione Password

```bash
# Cambia password ogni 3-6 mesi per sicurezza
# Aggiorna in WarmIt:

curl -X PUT "http://localhost:8000/api/accounts/{account_id}" \
  -H "Content-Type: application/json" \
  -d '{"password": "nuova_password"}'
```

### Backup Configurazione

Salva le configurazioni in un password manager:

```
Gmail Account 1
- Email: warmup1@gmail.com
- Password: (password normale)
- App Password: abcd efgh ijkl mnop
- Recovery: warmup1.recovery@outlook.com

Outlook Account 1
- Email: warmup6@outlook.com
- Password: (password)
- 2FA: (sì/no)

Libero Account 1
- Email: warmup9@libero.it
- Password: (password)
- Piano: Free/Premium
```

---

## 🔍 Verificare Configurazione

Prima di iniziare il warming, testa ogni account:

```bash
# Test SMTP
curl -X POST "http://localhost:8000/api/accounts/test-connection" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "account_id_here",
    "test_type": "smtp"
  }'

# Test IMAP
curl -X POST "http://localhost:8000/api/accounts/test-connection" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "account_id_here",
    "test_type": "imap"
  }'
```

---

## 📚 Link Utili

### Gmail
- App Passwords: https://myaccount.google.com/apppasswords
- Security Settings: https://myaccount.google.com/security
- IMAP Settings: https://support.google.com/mail/answer/7126229

### Outlook
- Account Settings: https://account.microsoft.com/security
- IMAP/SMTP Setup: https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353

### Libero
- Webmail: https://mail.libero.it
- Configurazione: https://assistenza.libero.it/mail/
- Premium: https://abbonamenti.libero.it/

---

**Configurazione completata! Ora sei pronto per il warming! 🔥**
