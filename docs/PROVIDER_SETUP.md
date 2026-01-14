# Email Provider Setup Guide

Complete guide for configuring Gmail, Outlook, Libero, and Aruba as receiver/sender accounts.

---

## 📧 Gmail

### Why Gmail?
- Most used provider worldwide (40%+ market share)
- Most sophisticated anti-spam filters
- If you pass Gmail, you pass almost everything
- Excellent for testing deliverability

### Configuration

**IMPORTANT**: Gmail requires "App Password" for external applications.

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
- Use App Password, not regular password
- Copy App Password without spaces

#### Error: "Too many login attempts"
- Wait 15 minutes
- Check no other apps are using the same account

#### Gmail Limits
- 500 emails/day for free account
- 2,000 emails/day for Google Workspace
- Max 100 recipients per email

---

## 📧 Outlook / Hotmail

### Why Outlook?
- Second most used provider
- Widely used in business (Microsoft 365)
- Different filters from Gmail
- Important for B2B

### Configuration

**GOOD NEWS**: Outlook doesn't require App Password for basic SMTP/IMAP.

#### Step 1: Verify Account Settings
1. Go to https://outlook.live.com
2. Settings → View all Outlook settings
3. Mail → Sync email
4. Verify "POP and IMAP" is enabled

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
  "password": "your_regular_password"  // Or App Password if 2FA
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
- Verify IMAP is enabled in settings
- Try logging in via web to unlock account

#### Error: "Authentication failed"
- If you have 2FA, use App Password
- Verify username (must be full email)

#### Outlook Limits
- 300 emails/day for free account
- 10,000 emails/day for Microsoft 365
- Max 100 recipients per email

---

## 📧 Libero

### Why Libero?
- Most popular Italian provider
- Great if your customers are in Italy
- Different behavior from US providers
- Adds realism to pattern

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
- Verify SMTP/IMAP are enabled in your plan

#### Libero Limits
- 100-200 emails/day for free account
- 500+ emails/day for Premium account
- More aggressive rate limits than US providers
- Some free accounts might not support SMTP/IMAP

### Supported Domains
- libero.it
- inwind.it
- iol.it
- blu.it
- giallo.it

---

## 📧 Aruba (Custom Domains)

### Why Aruba?
- Most popular Italian hosting provider
- Great for custom business domains
- Standard SMTP/IMAP configuration
- Perfect for sender accounts

### Configuration

**NOTE**: Aruba supports both port 587 (TLS) and 465 (SSL). We recommend 587.

#### Verify Configuration
1. Access Aruba panel
2. Email → Management → Configuration
3. Verify IMAP/SMTP are active

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
|------|------|------|-------|
| Custom Domains | smtp.yourdomain.com:587 | imap.yourdomain.com:993 | Recommended |
| Custom Domains (SSL) | smtps.yourdomain.com:465 | imaps.yourdomain.com:993 | Alternative |
| Aruba Email | smtp.aruba.it:587 | imap.aruba.it:993 | Only for @aruba.it |

### Troubleshooting Aruba

#### Error: "Authentication failed"
- Verify username (must be full email: `sales@yourdomain.com`)
- Check SMTP/IMAP are enabled in panel
- Verify 2-factor auth is not active

#### Error: "Connection refused"
- Try both ports (587 and 465)
- Verify DNS: `smtp.yourdomain.com` must point to Aruba servers
- Check firewall/antivirus

#### Error: "Relay access denied"
- Always use same email for authentication and sending
- Verify domain is active and correctly configured

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
    "info@company2.com"      # smtp.company2.com
    "support@company3.com"   # smtp.company3.com
)

# Script auto-detects domain and configures smtp.domain.com
```

### Aruba Best Practices

1. **Always use TLS (port 587)** instead of SSL (port 465)
2. **Verify SPF/DKIM/DMARC** in Aruba panel
3. **Monitor limits** of your hosting plan
4. **Backup configuration** before modifying settings
5. **Test connection** before starting warming

---

## 🎯 Recommended Distribution

### Optimal Setup

**Typical case: Business domains + Mixed receivers**

```
SENDERS (10 - to warm up)
├── sales@yourdomain.com      [Aruba/Custom]
├── info@yourdomain.com        [Aruba/Custom]
├── support@yourdomain.com     [Aruba/Custom]
├── marketing@yourdomain.com   [Aruba/Custom]
├── ... (other business accounts)

RECEIVERS (10 - responders)
├── warmup1@gmail.com          [Gmail - 40%]
├── warmup2@gmail.com
├── warmup3@gmail.com
├── warmup4@gmail.com
├── warmup5@outlook.com        [Outlook - 30%]
├── warmup6@outlook.it
├── warmup7@hotmail.com
├── warmup8@libero.it          [Libero - 20%]
├── warmup9@libero.it
└── warmup10@yahoo.it          [Yahoo - 10%]
```

### Why This Distribution?

| Sender | Provider | Reason |
|--------|----------|---------|
| Aruba/Custom | Custom domains | Business accounts to warm |

| Receiver | % | Reason |
|----------|---|---------|
| Gmail | 40% | Market leader, strictest filters |
| Outlook | 30% | Widely used B2B, Microsoft 365 |
| Libero | 20% | Italian provider, local pattern |
| Yahoo | 10% | Extra diversification |

**Advantages:**
- Simulates real recipients
- Tests major providers
- Natural distributed pattern
- If it passes all 3, it passes everywhere

---

## 🔧 Quick Setup

### Option 1: Dashboard Setup
1. Open http://localhost:8501
2. Add accounts one by one
3. Configure SMTP/IMAP for each
4. Create campaign

### Option 2: Automated Script
```bash
cd examples/
chmod +x setup_multi_accounts.sh

# Edit the script with your emails
nano setup_multi_accounts.sh

# Run
./setup_multi_accounts.sh
```

The script:
- Auto-detects provider from email domain
- Configures SMTP/IMAP automatically
- Shows Gmail App Password reminders
- Calculates distribution automatically

---

## 📊 Provider Monitoring

### Dashboard Filtering

```bash
Dashboard → Accounts → Filter by email

Gmail:   @gmail.com     (5 accounts)
Outlook: @outlook.com   (3 accounts)
Libero:  @libero.it     (2 accounts)
```

### Provider Metrics

Track performance per provider:
- Open rates
- Reply rates
- Bounce rates
- Delivery times

---

## 💡 Tips & Best Practices

### Gmail
- **ALWAYS use App Password**
- 2FA is required for App Password
- Each Gmail account counts toward 500 emails/day limit

### Outlook
- Inactive accounts disabled after 270 days
- Lower rate limits for new accounts
- Always use full email as username

### Libero
- **Stricter limits** than Gmail/Outlook
- Free accounts might not support IMAP/SMTP
- Consider Premium accounts for production
- More prone to temporary blocks

### Aruba/Custom Domains
- Verify SPF/DKIM/DMARC records
- Test connection before warming
- Monitor plan limits
- Keep backup of configuration

---

## 🔗 Useful Links

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

**Configuration complete! Ready for warming!**
