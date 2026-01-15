# Campaign Resource Estimator

Estimate required resources (RAM, CPU, storage, API calls, costs) for WarmIt email warming campaigns.

## 🚀 Quick Start

### CLI Usage

```bash
python scripts/estimate_resources.py --senders 100 --receivers 100 --weeks 6
```

### Dashboard Usage

1. Navigate to http://localhost:8501
2. Click **"🧮 Estimate"** in sidebar
3. Enter campaign parameters
4. Click **"Calculate Estimate"**

## 📋 CLI Options

```bash
python scripts/estimate_resources.py [OPTIONS]

Options:
  --senders INT     Number of sender accounts (required)
  --receivers INT   Number of receiver accounts (required)
  --weeks INT       Campaign duration in weeks (default: 6)
  --json           Output as JSON format
  -h, --help       Show help message
```

## 💡 Examples

### Small Campaign (10 accounts)
```bash
python scripts/estimate_resources.py --senders 10 --receivers 10 --weeks 6
```

**Output:**
```
=" * 80
🔥 WARMIT - CAMPAIGN RESOURCE ESTIMATION
=" * 80

📊 CAMPAIGN PARAMETERS
  Sender Accounts:    10
  Receiver Accounts:  10
  Duration:           6 weeks

📧 EMAIL VOLUME
  Total Emails:       3,360
  Avg per Day:        80
  Avg per Week:       560
  Peak per Day:       80 (week 6)

💾 RESOURCE REQUIREMENTS
  RAM (Minimum):      2,666 MB (2.6 GB)
  RAM (Recommended):  3,999 MB (3.9 GB)
  CPU (Minimum):      0.6 cores
  CPU (Recommended):  0.9 cores
  Storage:            91 MB (0.09 GB)

🗄️  DATABASE
  Connections Needed: 10
  Pool Size:          20

⚙️  WORKERS
  Celery Workers:     2
  Concurrency:        4

🔌 API USAGE
  Total API Calls:    6,720
  Calls per Day:      160
  Estimated Cost:     $0.00 (using free tier)

📋 RECOMMENDATION
  Configuration:      SMALL

✅ No warnings - configuration looks good!
```

### Medium Campaign (50 accounts)
```bash
python scripts/estimate_resources.py --senders 50 --receivers 50 --weeks 8
```

### Large Campaign (200 accounts)
```bash
python scripts/estimate_resources.py --senders 200 --receivers 200 --weeks 10
```

### Enterprise Campaign (500 accounts)
```bash
python scripts/estimate_resources.py --senders 500 --receivers 500 --weeks 12
```

### JSON Output (for automation)
```bash
python scripts/estimate_resources.py --senders 100 --receivers 100 --weeks 6 --json > estimate.json
```

**Output:**
```json
{
  "campaign": {
    "senders": 100,
    "receivers": 100,
    "duration_weeks": 6
  },
  "email_volume": {
    "total_emails": 33600,
    "per_day_avg": 800,
    "per_week_avg": 5600,
    "peak_per_day": 800
  },
  "resources": {
    "ram_mb_minimum": 4266,
    "ram_mb_recommended": 6399,
    "cpu_cores_minimum": 1.3,
    "cpu_cores_recommended": 1.95,
    "storage_mb": 850,
    "storage_gb": 0.83
  },
  ...
}
```

## 📊 What Gets Estimated

### Email Volume
- **Total emails** over campaign duration
- **Average per day/week**
- **Peak volume** (final week)
- Based on progressive warming: 5 → 10 → 20 → 40 → 60 → 80 emails/sender/day

### Resource Requirements
- **RAM:** Base system + accounts + workers + services
- **CPU:** Based on email processing load
- **Storage:** Emails + accounts + metrics + overhead

### Infrastructure
- **Database connections:** Based on worker count
- **Connection pool size:** With safety overhead
- **Celery workers:** Auto-calculated from load
- **Worker concurrency:** Optimized for throughput

### API Usage
- **Total API calls:** 2 calls per email (send + reply)
- **Daily average:** For rate limit planning
- **Cost estimate:** Based on free tier (adjustable)

### Configuration Profiles
- **Small:** 1-10 accounts
- **Medium:** 10-50 accounts
- **Large:** 50-200 accounts
- **Enterprise:** 200+ accounts

## ⚠️ Warnings

The estimator provides warnings for:

- High RAM usage (>8GB recommended)
- High CPU usage (>4 cores)
- Large storage needs (>10GB)
- High API usage (>10,000 calls/day)
- Receiver/sender ratio issues
- Short duration for large campaigns

## 🐳 Docker Compose Integration

The estimator generates optimized resource limits:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '0.49'
          memory: 799M
        reservations:
          cpus: '0.33'
          memory: 533M

  worker:
    deploy:
      resources:
        limits:
          cpus: '0.98'
          memory: 1599M
        reservations:
          cpus: '0.65'
          memory: 1066M
```

## 🎯 Use Cases

### 1. Planning New Campaigns
Estimate resources **before** launching to ensure infrastructure is adequate.

### 2. Scaling Existing Deployments
Determine if you need to upgrade hardware for larger campaigns.

### 3. Cost Planning
Understand API usage and costs before committing to paid tiers.

### 4. Infrastructure Sizing
Size your VPS/cloud instance appropriately.

### 5. Budget Approval
Provide concrete numbers for budget proposals.

## 💰 Cost Estimation

**Free Tier (Default):**
- Uses OpenRouter/Groq free models
- Cost: $0.00
- Rate limits may apply

**Paid Tier (Manual adjustment):**
Edit `API_COST_PER_1K_CALLS` in script:
```python
API_COST_PER_1K_CALLS = 0.50  # $0.50 per 1K calls
```

Then costs will be calculated automatically.

## 🔄 Progressive Warming Schedule

The estimator uses WarmIt's standard warming progression:

| Week | Emails/Sender/Day |
|------|-------------------|
| 1    | 5                 |
| 2    | 10                |
| 3    | 20                |
| 4    | 40                |
| 5    | 60                |
| 6+   | 80                |

## 📚 Integration with CI/CD

```bash
#!/bin/bash
# Validate campaign feasibility before deployment

SENDERS=100
RECEIVERS=100
WEEKS=6

# Get estimate as JSON
ESTIMATE=$(python scripts/estimate_resources.py \
  --senders $SENDERS \
  --receivers $RECEIVERS \
  --weeks $WEEKS \
  --json)

# Extract recommended RAM (in MB)
RAM_NEEDED=$(echo $ESTIMATE | jq -r '.resources.ram_mb_recommended')

# Check if we have enough
AVAILABLE_RAM=8192  # 8GB

if [ $RAM_NEEDED -gt $AVAILABLE_RAM ]; then
  echo "❌ Insufficient RAM: need ${RAM_NEEDED}MB, have ${AVAILABLE_RAM}MB"
  exit 1
fi

echo "✅ Resources sufficient for campaign"
```

## 🛠️ Technical Details

**Calculation Factors:**
- Base RAM: 256MB system overhead
- RAM per sender: 50MB
- RAM per receiver: 30MB
- RAM per worker: 200MB
- CPU per 100 emails/day: 0.1 cores
- Storage per email: 5KB
- DB connections per worker: 5

**Overhead:**
- 50% RAM overhead recommended
- 50% CPU overhead recommended
- DB pool +10 connections safety margin

## 📝 Notes

- Estimates are **conservative** (include safety margins)
- Actual usage may vary based on email content and patterns
- Free API tier keeps costs at $0
- For production, use **PostgreSQL** (not SQLite)
- Monitor actual usage and adjust as needed

## 🔗 Related Documentation

- [TODO.md](../TODO.md) - Full feature roadmap
- [CHANGELOG.md](../CHANGELOG.md) - Version history
- [Security Setup](SECURITY_SETUP.md) - Authentication & encryption guide

---

**Need Help?** Check the main [README.md](../README.md) or open an issue.
