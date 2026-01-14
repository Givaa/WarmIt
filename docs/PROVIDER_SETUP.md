# Email Provider Configuration Guide

Complete guide to configure Gmail, Outlook, and Libero as receiver accounts.

---

## Gmail

### Why Gmail?
- Most used provider worldwide (40%+ market share)
- Most sophisticated anti-spam filters
- If you pass Gmail, you pass almost everything
- Excellent for testing deliverability

### Configuration

**IMPORTANT**: Gmail requires App Passwords for external applications.

#### Step 1: Enable 2FA
1. Go to https://myaccount.google.com/security
2. Click on "2-Step Verification"
3. Follow the guided procedure

#### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" as app
3. Select "Other" as device
4. Enter "WarmIt" as name
5. Click "Generate"
6. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

#### Step 3: WarmIt Configuration

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

#### Error: "Username and password not accepted"
- Verify that 2FA is active
- Use App Password, not your regular password
- Copy the App Password without spaces

#### Error: "Too many login attempts"
- Wait 15 minutes
- Verify that no other apps are using the same account

#### Gmail Limits
- 500 emails/day for free accounts
- 2,000 emails/day for Google Workspace
- Max 100 recipients per email

---

## Outlook / Hotmail

### Why Outlook?
- Second most used provider
- Heavily used in business environments (Microsoft 365)
- Different filters from Gmail
- Important for B2B

### Configuration

**GOOD NEWS**: Outlook doesn't require App Passwords for basic SMTP/IMAP.

#### Step 1: Verify Account Settings
1. Go to https://outlook.live.com
2. Settings → View all Outlook settings
3. Mail → Sync email
4. Verify that "POP and IMAP" is enabled

#### Step 2: (Optional) App Password for 2FA
If you have 2FA enabled:
1. Go to https://account.microsoft.com/security
2. Security → Advanced security options
3. App passwords → Create new app password
4. Copy the generated password

#### Step 3: WarmIt Configuration

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
  "password": "your_normal_password"  // Or App Password if 2FA
}
```

### Supported Domains
- outlook.com
- outlook.it
- hotmail.com
- hotmail.it
- live.com
- live.it

**All use the same SMTP/IMAP configuration!**

### Troubleshooting Outlook

#### Error: "Mailbox unavailable"
- Verify that IMAP is enabled in settings
- Try logging in via web to unlock the account

#### Error: "Authentication failed"
- If you have 2FA, use App Password
- Verify username (must be full email)

#### Outlook Limits
- 300 emails/day for free accounts
- 10,000 emails/day for Microsoft 365
- Max 100 recipients per email

---

## Libero

### Why Libero?
- Most popular Italian provider
- Great if your customers are in Italy
- Different behavior from US providers
- Adds realism to the pattern

### Configuration

**NOTE**: Libero has different configurations for mail.libero.it and posta.libero.it.

#### Step 1: Verify Account Type
- **mail.libero.it**: Classic webmail
- **posta.libero.it**: New interface

#### Step 2: WarmIt Configuration

**For classic Libero Mail accounts:**
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
  "password": "your_password"
}
```

**For business accounts (if you have Libero Business):**
```json
{
  "smtp_host": "smtps.libero.it",
  "smtp_port": 465,
  "smtp_use_tls": false,
  "smtp_use_ssl": true
}
```

### Troubleshooting Libero

#### Error: "Connection refused"
- Verify you're using `smtp.libero.it` (not smtps)
- Port 587 with TLS (not 465)
- Some Libero accounts limit external SMTP/IMAP

#### Error: "Relay access denied"
- Log in via webmail at least once
- Verify that SMTP/IMAP are enabled in your plan

#### Libero Limits
- 100-200 emails/day for free accounts
- 500+ emails/day for Premium accounts
- More aggressive rate limits than US providers
- Some free accounts might not support SMTP/IMAP

### Supported Domains
- libero.it
- inwind.it
- iol.it
- blu.it
- giallo.it

---

## Aruba (Custom Domains)

### Why Aruba?
- Most popular Italian hosting provider
- Great for custom business domains
- Standard SMTP/IMAP configuration
- Perfect for sender accounts

### Configuration

**NOTE**: Aruba supports both port 587 (TLS) and 465 (SSL). We recommend 587.

#### Verify Configuration
1. Access Aruba control panel
2. Email → Management → Configuration
3. Verify that IMAP/SMTP are active

#### WarmIt Configuration

**For domains hosted on Aruba:**
```json
{
  "email": "sales@yourdomain.com",
  "type": "sender",
  "smtp_host": "smtp.yourdomain.com",
  "smtp_port": 587,
  "smtp_use_tls": true,
  "imap_host": "imap.yourdomain.com",
  "imap_port": 993,
  "imap_use_ssl": true,
  "password": "your_password"
}
```

**Alternative with port 465 (SSL):**
```json
{
  "smtp_host": "smtps.yourdomain.com",
  "smtp_port": 465,
  "smtp_use_tls": false,
  "smtp_use_ssl": true
}
```

### Common Aruba Configurations

| Type | SMTP | IMAP | Notes |
|------|------|------|------|
| Custom Domains | smtp.yourdomain.com:587 | imap.yourdomain.com:993 | Recommended |
| Custom Domains (SSL) | smtps.yourdomain.com:465 | imaps.yourdomain.com:993 | Alternative |
| Aruba Email | smtp.aruba.it:587 | imap.aruba.it:993 | Only for @aruba.it |

### Troubleshooting Aruba

#### Error: "Authentication failed"
- Verify username (must be full email: `sales@yourdomain.com`)
- Check that SMTP/IMAP are enabled in control panel
- Verify you don't have 2FA enabled

#### Error: "Connection refused"
- Try both ports (587 and 465)
- Verify DNS: `smtp.yourdomain.com` must point to Aruba servers
- Check firewall/antivirus

#### Error: "Relay access denied"
- Always use the same email for authentication and sending
- Verify that the domain is active and configured correctly

#### Aruba Limits
- Depends on hosting plan
- Basic plans: 100-200 emails/hour
- Business plans: 500+ emails/hour
- Variable rate limit per plan

### Multiple Domains on Aruba

If you have multiple domains hosted on Aruba:
```bash
SENDERS=(
    "sales@company1.com"    # smtp.company1.com
    "info@company2.com"     # smtp.company2.com
    "support@company3.com"  # smtp.company3.com
)

# The script auto-detects the domain and configures smtp.domain.com
```

### Aruba Best Practices

1. **Always use TLS (port 587)** instead of SSL (port 465)
2. **Verify SPF/DKIM/DMARC** in Aruba control panel
3. **Monitor limits** of your hosting plan
4. **Backup configuration** before modifying settings
5. **Test connection** before starting warming

---

## Recommended Distribution

### Optimal Italian Setup

**Typical case: Aruba business domains + mixed receivers**

```
SENDERS (10 - to warm up)
├── sales@yourdomain.com      [Aruba]
├── info@yourdomain.com       [Aruba]
├── support@yourdomain.com    [Aruba]
├── marketing@yourdomain.com  [Aruba]
├── ... (other business accounts)

RECEIVERS (10 - responders)
├── warmup1@gmail.com         [Gmail - 40%]
├── warmup2@gmail.com
├── warmup3@gmail.com
├── warmup4@gmail.com
├── warmup5@outlook.com       [Outlook - 30%]
├── warmup6@outlook.it
├── warmup7@hotmail.com
├── warmup8@libero.it         [Libero - 20%]
├── warmup9@libero.it
└── warmup10@yahoo.it         [Yahoo - 10%]
```

### Why this distribution?

| Sender | Provider | Reason |
|--------|----------|--------|
| Aruba | Custom domains | Business mailboxes to warm up |

| Receiver | % | Reason |
|----------|---|--------|
| Gmail | 40% | Market leader, strictest filters |
| Outlook | 30% | Heavily used B2B, Microsoft 365 |
| Libero | 20% | Italian provider, local pattern |
| Yahoo | 10% | Extra diversification |

**Advantages:**
- Simulates real Italian recipients
- Tests the 3 most used providers in Italy
- Natural and distributed pattern
- If it passes all 3, it passes everywhere

---

## Quick Setup with Script

Use the automatic script with optimal configuration:

```bash
cd examples/
chmod +x setup_multi_accounts.sh
./setup_multi_accounts.sh
```

The script:
- Adds 5 Gmail + 3 Outlook + 2 Libero automatically
- Requests password for each account
- Creates ready-to-use campaign
- Reminds to use App Passwords for Gmail

---

## Provider Monitoring

### Dashboard View

You can filter by provider in the dashboard:

```
Dashboard → Accounts → Filter: Email contains

Gmail:   @gmail.com     (5 accounts)
Outlook: @outlook.com   (3 accounts)
Libero:  @libero.it     (2 accounts)
```

### Metrics per Provider

```sql
-- Example query for provider statistics
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

## Important Warnings

### Gmail
- **ALWAYS use App Password**
- 2FA is required for App Password
- Each Gmail account counts towards the 500 emails/day limit

### Outlook
- Inactive accounts are disabled after 270 days
- Lower rate limits for new accounts
- Always use full email as username

### Libero
- **Stricter limits** compared to Gmail/Outlook
- Free accounts might not support IMAP/SMTP
- Consider Premium accounts for production
- More prone to temporary blocks

---

## Best Practices

### Account Creation

1. **Gmail**
   - Create 5 accounts with different names
   - Use different phone number for each account (or recovery email)
   - Enable 2FA immediately
   - Generate App Password right after creation

2. **Outlook**
   - Create 3 accounts (can use same phone)
   - Vary between outlook.com, outlook.it, hotmail.com
   - Enable IMAP in settings
   - (Optional) Enable 2FA for security

3. **Libero**
   - Create 2 Libero accounts
   - Log in via webmail at least once
   - Verify that SMTP/IMAP are active
   - Consider Premium if limits are too low

### Password Rotation

```bash
# Change passwords every 3-6 months for security
# Update in WarmIt:

curl -X PUT "http://localhost:8000/api/accounts/{account_id}" \
  -H "Content-Type: application/json" \
  -d '{"password": "new_password"}'
```

### Configuration Backup

Save configurations in a password manager:

```
Gmail Account 1
- Email: warmup1@gmail.com
- Password: (normal password)
- App Password: abcd efgh ijkl mnop
- Recovery: warmup1.recovery@outlook.com

Outlook Account 1
- Email: warmup6@outlook.com
- Password: (password)
- 2FA: (yes/no)

Libero Account 1
- Email: warmup9@libero.it
- Password: (password)
- Plan: Free/Premium
```

---

## Verify Configuration

Before starting warming, test each account:

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

## Useful Links

### Gmail
- App Passwords: https://myaccount.google.com/apppasswords
- Security Settings: https://myaccount.google.com/security
- IMAP Settings: https://support.google.com/mail/answer/7126229

### Outlook
- Account Settings: https://account.microsoft.com/security
- IMAP/SMTP Setup: https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353

### Libero
- Webmail: https://mail.libero.it
- Configuration: https://assistenza.libero.it/mail/
- Premium: https://abbonamenti.libero.it/

---

**Configuration complete! Now you're ready for warming!**
