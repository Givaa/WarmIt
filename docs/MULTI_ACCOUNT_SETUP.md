# Multi-Account Setup Guide

Complete guide for configuring warming with multiple sender and receiver accounts.

## Ideal Scenario

**10 Senders (to warm up) + 10 Receivers (responders) = Optimal Setup**

### Advantages

**Natural Distribution**: Emails distributed across multiple receivers
**Scalability**: Add senders/receivers without limits
**Resilience**: If 1 account has problems, others continue
**Efficiency**: Parallel warming of multiple domains
**Realism**: Simulates organization with multiple users

---

## Warming Mathematics

### Example: 10 Senders + 10 Receivers

**Week 1** (5 emails/day per sender):
```
10 senders × 5 emails/day = 50 total emails/day
50 emails ÷ 10 receivers = ~5 emails/receiver/day

Automatically balanced load
No receiver overload
Natural distributed pattern
```

**Week 4** (25 emails/day per sender):
```
10 senders × 25 emails/day = 250 total emails/day
250 emails ÷ 10 receivers = ~25 emails/receiver/day

Still manageable
Automatic distribution
High engagement
```

### Scalability

| Senders | Receivers | Emails/Day (Week 1) | Emails/Day (Week 6) |
|---------|-----------|---------------------|---------------------|
| 5 | 5 | 25 | 250 |
| 10 | 10 | 50 | 500 |
| 20 | 15 | 100 | 1,000 |
| 50 | 30 | 250 | 2,500 |

---

## Setup Methods

> **Italian Provider Guide**: For detailed configuration of Gmail, Outlook and Libero, see [PROVIDER_SETUP.md](PROVIDER_SETUP.md)

### Method 1: Dashboard (Recommended)

**Advantages**: Visual, simple, no scripts

#### Step 1: Add All SENDERS

```
1. Open http://localhost:8501
2. Go to "Add New" → "Add Account"
3. For each sender:
   - Email: sales@yourdomain.com
   - Type: sender
   - SMTP/IMAP config
   - Password
   - [Add Account]
4. Repeat 10 times
```

#### Step 2: Add All RECEIVERS

```
1. "Add New" → "Add Account"
2. For each receiver:
   - Email: warmup1@gmail.com
   - Type: receiver
   - SMTP: smtp.gmail.com
   - IMAP: imap.gmail.com
   - Password: [Gmail App Password]
   - [Add Account]
3. Repeat 10 times
```

#### Step 3: Create Campaign

```
1. "Add New" → "Create Campaign"
2. Name: "Complete Warming 2026"
3. Sender Accounts: Select all 10
4. Receiver Accounts: Select all 10
5. Duration: 6 weeks
6. [Create Campaign]
```

**Done!**

---

### Method 2: Automatic Script

**Advantages**: Fast, repeatable, bulk import

#### Use Provided Script

```bash
cd examples/
chmod +x setup_multi_accounts.sh
./setup_multi_accounts.sh
```

**The script:**
1. Adds 10 senders
2. Adds 10 receivers (asks password for each)
3. Creates campaign automatically

#### Customize the Script

Modify `setup_multi_accounts.sh`:

```bash
# Change these arrays with your accounts
SENDERS=(
    "your1@domain.com"
    "your2@domain.com"
    # ... add yours
)

SENDER_SMTP_HOST="smtp.yourdomain.com"
SENDER_PASSWORD="common_password"  # Or ask for each

RECEIVERS=(
    "warmup1@gmail.com"
    "warmup2@outlook.com"
    # ... add yours
)
```

---

### Method 3: CSV Import (Future)

**Next version:** Import from CSV/Excel
```csv
email,type,smtp_host,smtp_port,imap_host,imap_port,password
sales@domain.com,sender,smtp.domain.com,587,imap.domain.com,993,pass1
info@domain.com,sender,smtp.domain.com,587,imap.domain.com,993,pass2
```

---

## Usage Patterns

### Pattern 1: Same Domain

**Scenario**: Warming multiple accounts on same domain

```
SENDER (10):           DOMAIN
├── sales@             ├── yourdomain.com
├── info@              ├── yourdomain.com
├── support@           ├── yourdomain.com
├── marketing@         ├── yourdomain.com
└── ...                └── yourdomain.com

RECEIVER (10):         PROVIDER
├── warmup1@           ├── gmail.com
├── warmup2@           ├── gmail.com
├── warmup3@           ├── outlook.com
├── warmup4@           ├── yahoo.com
└── ...                └── (mix)
```

**Advantages:**
- Warm domain reputation globally
- All senders benefit
- Same SMTP/IMAP setup for all

**SMTP Config (same for all):**
```json
{
  "smtp_host": "smtp.yourdomain.com",
  "smtp_port": 587,
  "imap_host": "imap.yourdomain.com",
  "imap_port": 993
}
```

---

### Pattern 2: Multiple Domains

**Scenario**: Warming accounts on different domains

```
SENDER (10):           DOMAIN
├── sales@             ├── company1.com
├── info@              ├── company1.com
├── support@           ├── company2.com
├── contact@           ├── company2.com
├── hello@             ├── company3.com
└── ...                └── (various)

RECEIVER (10): Same for all!
├── warmup1@gmail.com
├── warmup2@outlook.com
└── ...
```

**Advantages:**
- Warm multiple domains simultaneously
- Shared receiver pool
- Efficient resource usage

**Setup:** Different SMTP/IMAP for each domain

---

### Pattern 3: Gradual Scaling

**Scenario**: Start small, scale progressively

```
Week 1-2:
  2 senders + 3 receivers

Week 3-4:
  5 senders + 5 receivers  (add during warming)

Week 5-6:
  10 senders + 10 receivers  (add more)
```

**Advantages:**
- Cautious start
- Validate system first
- Scale on success

---

## Best Practices

### Sender:Receiver Ratio

| Senders | Min Receivers | Optimal Receivers | Notes |
|---------|---------------|-------------------|-------|
| 1 | 2 | 3-5 | Sufficient |
| 5 | 5 | 8-10 | Balanced |
| 10 | 10 | 15-20 | Ideal |
| 20+ | 15+ | 25-30 | Enterprise |

**Rule of thumb**: `Receivers ≥ Senders` (minimum 1:1)

### Receiver Diversification

**Good diversification:**
```
40% Gmail (warmup1-4@gmail.com)
30% Outlook (warmup5-7@outlook.com)
20% Yahoo (warmup8-9@yahoo.com)
10% Others (warmup10@proton.me)
```

**Why?**
- Simulates real recipients
- Different ESPs = natural pattern
- No dominant provider

### Password Management

**Option A: Common Password**
```bash
# Same password for all senders on same domain
SENDER_PASSWORD="SecurePass123!"

# Pro: Fast setup
# Con: Less secure
```

**Option B: Individual Passwords**
```bash
# Different password for each account
sales@domain.com    → SalesPass123!
info@domain.com     → InfoPass456!

# Pro: More secure
# Con: Longer setup
```

**Option C: Password Manager**
```bash
# Use 1Password, Bitwarden, etc.
# Generate unique passwords
# Save in vault

# Pro: Maximum security
# Con: Requires integration
```

### Naming Convention

**SENDER (production):**
```
sales@domain.com
info@domain.com
support@domain.com
```

**RECEIVER (warming):**
```
warmup1@gmail.com
warmup2@gmail.com
warmup-company-01@outlook.com
```

**Why "warmup" in the name?**
- Immediate recognition
- Avoid confusion with real accounts
- Easy bulk management

---

## Multi-Account Monitoring

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
└── Status:     Healthy

TODAY'S ACTIVITY
├── Sent:       150/250
├── Open Rate:  87%
└── Reply Rate: 82%
```

### Per-Account View

```
Dashboard → Accounts → Filter: Sender

sales@domain.com        Active
├── Sent: 75
├── Open: 87%
├── Bounce: 0.5%
└── Status: Healthy

info@domain.com         Active
├── Sent: 73
├── Open: 85%
├── Bounce: 1.2%
└── Status: Healthy

...
```

### Campaign Metrics

```
Dashboard → Campaigns → "Complete Warming 2026"

Progress: ████████░░ 80% (Week 5/6)

METRICS
├── Total Sent:     3,500 emails
├── Avg Open:       86%
├── Avg Reply:      81%
├── Avg Bounce:     1.3%
└── Health:         Excellent

PER SENDER
├── All 10 active
├── 0 paused
├── 0 errors
└── Average daily: 25 emails
```

---

## Troubleshooting

### Some Senders Not Sending

**Cause**: High bounce rate or SMTP errors

**Solution:**
```bash
# Check account status
Dashboard → Accounts → Filter: Error

# Fix account
1. Verify password
2. Check SMTP/IMAP config
3. Test connection
4. Resume account
```

### Some Receivers Not Responding

**Cause**: IMAP not working or wrong password

**Solution:**
```bash
# Check logs
docker compose -f docker/docker-compose.prod.yml logs worker | grep receiver

# Verify inbox manually
# Fix password/IMAP config
# Restart worker
```

### Unbalanced Distribution

**Cause**: System randomness

**Solution:**
- Normal: Small variations are OK
- In the long term it balances out
- If very unbalanced: check logs

---

## Tips & Tricks

### Tip 1: Staging Before Production

```
1. Setup 2 senders + 2 receivers (test)
2. Run 1 week
3. Verify everything works
4. Scale to 10 + 10
```

### Tip 2: Batch Adding

```
# Add 5 senders, check
# Then another 5
# Instead of all 10 together
```

### Tip 3: Gradual Campaign Start

```
# Campaign 1: 5 senders + 5 receivers
# After 2 weeks:
# Campaign 2: another 5 senders + same receivers
```

### Tip 4: Shared Receiver Pool

```
# Create large receiver pool
RECEIVERS: 20 accounts

# Use for multiple campaigns
Campaign A: 10 senders → 20 receivers
Campaign B: 5 senders → same 20 receivers

Maximum efficiency
```

---

## Scaling Beyond 10+10

### 20 Senders + 15 Receivers

**Setup:**
```
Week 1: 20 × 5 = 100 emails/day
Week 6: 20 × 50 = 1,000 emails/day

Receiver load: 50-70 emails/day
Manageable
```

**Resources:**
```yaml
worker:
  command: celery worker --concurrency=8
  resources:
    memory: 4G
    cpus: '4.0'
```

### 50+ Senders

**Multi-Campaign Strategy:**
```
Campaign 1: Senders 1-25  → Receiver Pool A
Campaign 2: Senders 26-50 → Receiver Pool B

OR

Campaign 1: All 50 senders → 30 receiver pool
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

## Multi-Account Checklist

Before starting:

- [ ] Have at least 2-3 receivers for each sender
- [ ] App Passwords created for Gmail accounts
- [ ] SMTP/IMAP credentials correct
- [ ] DNS records (SPF/DKIM/DMARC) configured
- [ ] Docker running
- [ ] WarmIt started (`./start.sh`)
- [ ] Dashboard accessible (http://localhost:8501)

Setup completed:

- [ ] All senders added and active
- [ ] All receivers added and active
- [ ] Campaign created
- [ ] Status: Active
- [ ] First emails sent
- [ ] Check logs for errors
- [ ] Monitor dashboard daily

---

## Real-World Example

**Company with 10 people in sales team:**

```
SETUP
├── 10 business email accounts (senders)
├── 10 personal Gmail accounts (receivers)
└── 1 campaign of 6 weeks

RESULTS AFTER 6 WEEKS
├── 3,500 emails sent
├── 87% open rate
├── 83% reply rate
├── 1.2% bounce rate
├── Excellent domain reputation
└── Ready for cold email campaign

TIME SAVED
├── Manual warming: 40+ hours
├── WarmIt automatic: 15 minutes setup
└── ROI: 160x
```

---

**Ready to warm 10+ accounts? Let's go!**

For questions: [FAQ.md](FAQ.md)
