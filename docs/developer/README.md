# 👨‍💻 Developer Documentation

Complete technical reference for WarmIt email warming platform.

---

## 📖 Table of Contents

### Architecture & Design
- [Architecture Overview](ARCHITECTURE.md) - System design and component interaction
- [Database Schema](DATABASE_SCHEMA.md) - Complete database model reference
- [API Reference](API_REFERENCE.md) - All API endpoints with examples
- [Task System](TASK_SYSTEM.md) - Celery tasks and scheduling

### Core Components
- [Models Reference](MODELS.md) - SQLAlchemy models (Account, Campaign, Email, Metric)
- [Services Reference](SERVICES.md) - Business logic services
- [Email Service](EMAIL_SERVICE.md) - SMTP/IMAP operations
- [AI Generator](AI_GENERATOR.md) - Content generation system
- [Response Bot](RESPONSE_BOT.md) - Automated reply system

### Development Guides
- [Setup Development Environment](DEVELOPMENT_SETUP.md) - Local development guide
- [Testing Guide](TESTING.md) - Writing and running tests
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute
- [Code Style](CODE_STYLE.md) - Coding standards and best practices

### Workflows & Flows
- [Email Warming Flow](flows/WARMING_FLOW.md) - Complete warming process
- [Response Flow](flows/RESPONSE_FLOW.md) - Auto-response mechanism
- [Tracking Flow](flows/TRACKING_FLOW.md) - Open/click tracking
- [Bounce Detection Flow](flows/BOUNCE_FLOW.md) - Bounce handling

---

## 🚀 Quick Reference

### Key Classes

| Class | Location | Purpose |
|-------|----------|---------|
| `Account` | `models/account.py` | Email account configuration |
| `Campaign` | `models/campaign.py` | Warming campaign settings |
| `Email` | `models/email.py` | Email record tracking |
| `Metric` | `models/metric.py` | Daily statistics |
| `EmailService` | `services/email_service.py` | SMTP/IMAP operations |
| `AIGenerator` | `services/ai_generator.py` | Content generation |
| `ResponseBot` | `services/response_bot.py` | Auto-reply logic |
| `WarmupScheduler` | `services/scheduler.py` | Campaign execution |
| `BounceDetector` | `services/bounce_detector.py` | Bounce detection |

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/accounts/` | POST | Create account |
| `/campaigns/` | POST | Create campaign |
| `/campaigns/{id}/start` | POST | Start campaign |
| `/track/open/{email_id}` | GET | Track email open |
| `/webhooks/bounce` | POST | Handle bounce webhook |
| `/health/detailed` | GET | System health check |

### Key Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| `process_campaigns` | Every 2 hours | Send warming emails |
| `process_responses` | Every 15 min | Check and respond to emails |
| `detect_bounces` | Every 30 min | Check for bounced emails |
| `reset_daily_counters` | Daily at 00:00 | Reset campaign counters |
| `update_metrics` | Daily at 23:00 | Update daily statistics |

### Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `TZ` | `Europe/Rome` | Timezone for all services |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `DATABASE_URL` | - | PostgreSQL connection string |
| `REDIS_URL` | - | Redis connection string |
| `AI_PROVIDER` | `openrouter` | AI provider (openrouter/groq) |

> **Note:** All Docker services use `Europe/Rome` timezone by default. Celery tasks and logs display local time.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Dashboard                            │
│                    (Streamlit - Port 8501)                   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP REST API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI Server                        │
│                        (Port 8000)                           │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Accounts │  │Campaigns │  │ Tracking │  │  Health  │   │
│  │   API    │  │   API    │  │   API    │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────┬────────────┬────────────┬────────────┬───────────┘
           │            │            │            │
           ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Services Layer                          │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   Email    │  │    AI      │  │  Response  │           │
│  │  Service   │  │ Generator  │  │    Bot     │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Warmup    │  │   Bounce   │  │   Domain   │           │
│  │ Scheduler  │  │  Detector  │  │  Checker   │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└──────────┬────────────────────────────────────┬─────────────┘
           │                                    │
           ▼                                    ▼
┌──────────────────────┐            ┌──────────────────────┐
│     PostgreSQL       │            │    Redis + Celery    │
│   (Main Database)    │            │   (Task Queue)       │
│                      │            │                      │
│  • accounts          │            │  ┌───────────────┐  │
│  • campaigns         │            │  │ Celery Worker │  │
│  • emails            │            │  └───────────────┘  │
│  • metrics           │            │  ┌───────────────┐  │
│                      │            │  │  Celery Beat  │  │
└──────────────────────┘            │  └───────────────┘  │
                                    └──────────────────────┘
```

---

## 🔄 Core Workflows

### 1. Email Warming Workflow

```
[Celery Beat Scheduler]
        ↓
[process_campaigns task] (every 2 hours)
        ↓
[WarmupScheduler.process_all_campaigns()]
        ↓
For each active campaign:
    ↓
    [Check if should send now] (based on next_send_time)
    ↓
    [Calculate daily target] (progressive: 5→10→15→25→35→50)
    ↓
    [Generate AI content] (AIGenerator)
    ↓
    [Send emails] (EmailService)
    ↓
    [Record in database] (Email record with tracking pixel)
    ↓
    [Update statistics] (sender.total_sent++)
    ↓
    [Schedule next send time] (random 2-10 min delay)
```

### 2. Response Workflow

```
[Celery Beat Scheduler]
        ↓
[process_responses task] (every 15 min)
        ↓
[ResponseBot.process_all_receivers()]
        ↓
For each receiver account:
    ↓
    [Fetch unread emails] (IMAP)
    ↓
    [85% probability decision] (should respond?)
    ↓
    YES: [Generate reply] (AIGenerator)
         ↓
         [Send reply] (EmailService)
         ↓
         [Update stats] (receiver.total_replied++)
    ↓
    NO: [Mark as unread again] (IMAP STORE -FLAGS \\Seen)
```

### 3. Tracking Workflow

```
[Email client loads tracking pixel]
        ↓
[GET /track/open/{email_id}]
        ↓
[Find email in database] (eager load relationships)
        ↓
[Check if already opened] (email.opened_at)
        ↓
NO: [Record open] (email.opened_at = now)
    ↓
    [Update sender stats] (sender.total_opened++)
    ↓
[Return 1x1 transparent GIF]
```

---

## 📊 Data Models

### Core Entities

```python
Account
├── id: int (PK)
├── email: str (unique)
├── type: AccountType (sender/receiver)
├── smtp_host, smtp_port, smtp_use_tls
├── imap_host, imap_port, imap_use_ssl
├── password: str (encrypted with Fernet)
├── Statistics:
│   ├── total_sent: int
│   ├── total_received: int
│   ├── total_opened: int
│   ├── total_replied: int
│   └── total_bounced: int
└── Relationships:
    ├── sent_emails: List[Email]
    ├── received_emails: List[Email]
    └── metrics: List[Metric]

Campaign
├── id: int (PK)
├── name: str
├── sender_account_ids: List[int] (JSON)
├── receiver_account_ids: List[int] (JSON)
├── status: CampaignStatus
├── current_week: int
├── target_emails_today: int
├── emails_sent_today: int
├── next_send_time: datetime
└── Statistics:
    ├── total_emails_sent: int
    ├── total_emails_opened: int
    ├── total_emails_replied: int
    └── total_emails_bounced: int

Email
├── id: int (PK)
├── sender_id: int (FK -> Account)
├── receiver_id: int (FK -> Account)
├── campaign_id: int (FK -> Campaign)
├── message_id: str (unique)
├── subject: str
├── body: str
├── status: EmailStatus (pending/sent/bounced)
├── Timestamps:
│   ├── sent_at: datetime
│   ├── opened_at: datetime
│   └── bounced_at: datetime
└── AI Info:
    ├── ai_generated: bool
    ├── ai_model: str
    └── ai_prompt: str
```

---

## 🔧 Development Setup

### Prerequisites

```bash
# Python 3.11+
python --version

# Docker & Docker Compose
docker --version
docker compose version
```

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/warmit.git
cd warmit

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Setup environment
cp .env.example docker/.env
# Edit docker/.env with your settings

# 5. Start services
./warmit.sh start

# 6. Run tests
pytest

# 7. Code formatting
ruff check src/
ruff format src/
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_email_service.py

# Run with coverage
pytest --cov=warmit --cov-report=html

# Run specific test
pytest tests/test_email_service.py::test_send_email
```

---

## 📝 Code Style

### Conventions

- **PEP 8** compliance
- **Type hints** on all functions
- **Docstrings** (Google style) on all public methods
- **async/await** for I/O operations
- **Dependency injection** for testability

### Example Function

```python
async def send_email(
    self,
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    message: EmailMessage,
    use_tls: bool = True,
) -> bool:
    """
    Send an email via SMTP.

    Args:
        smtp_host: SMTP server hostname
        smtp_port: SMTP server port (587 for STARTTLS, 465 for SSL)
        username: SMTP username (usually email address)
        password: SMTP password (use App Password for Gmail/Outlook)
        message: EmailMessage object to send
        use_tls: Whether to use STARTTLS (True) or direct SSL (False)

    Returns:
        True if email sent successfully, False otherwise

    Example:
        >>> service = EmailService()
        >>> msg = EmailMessage(
        ...     sender="sender@example.com",
        ...     receiver="receiver@example.com",
        ...     subject="Test",
        ...     body="Hello!"
        ... )
        >>> success = await service.send_email(
        ...     smtp_host="smtp.gmail.com",
        ...     smtp_port=587,
        ...     username="sender@example.com",
        ...     password="app_password",
        ...     message=msg,
        ...     use_tls=True
        ... )
    """
    # Implementation...
```

---

## 🔗 Related Documentation

- [Main README](../../README.md) - Project overview
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Database Schema](DATABASE_SCHEMA.md) - Database structure
- [Architecture](ARCHITECTURE.md) - System architecture

---

**Last Updated:** 2026-01-17
**Documentation Version:** 1.0.0
