# 📦 Models Reference

Complete reference for all SQLAlchemy models in WarmIt.

**Location:** `src/warmit/models/`

---

## Table of Contents

- [Account Model](#account-model)
- [Campaign Model](#campaign-model)
- [Email Model](#email-model)
- [Metric Model](#metric-model)
- [Base Models](#base-models)

---

## Account Model

**File:** `src/warmit/models/account.py`

Represents an email account (sender or receiver) with SMTP/IMAP configuration.

### Class Definition

```python
class Account(Base, TimestampMixin):
    """Email account configuration."""

    __tablename__ = "accounts"
```

### Fields

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | Integer | No | Primary key |
| `email` | String(255) | No | Email address (unique, indexed) |
| `first_name` | String(100) | Yes | First name for personalization |
| `last_name` | String(100) | Yes | Last name for personalization |
| `type` | AccountType | No | `sender` or `receiver` |
| `status` | AccountStatus | No | `active`, `paused`, `disabled`, `error` |
| **SMTP Configuration** |
| `smtp_host` | String(255) | No | SMTP server hostname |
| `smtp_port` | Integer | No | SMTP port (default: 587) |
| `smtp_use_tls` | Boolean | No | Use STARTTLS (default: True) |
| **IMAP Configuration** |
| `imap_host` | String(255) | No | IMAP server hostname |
| `imap_port` | Integer | No | IMAP port (default: 993) |
| `imap_use_ssl` | Boolean | No | Use SSL (default: True) |
| **Credentials** |
| `password` | String(500) | No | Encrypted password (Fernet) |
| **Domain Information** |
| `domain` | String(255) | Yes | Domain name |
| `domain_age_days` | Integer | Yes | Domain age in days |
| `domain_checked_at` | DateTime | Yes | When domain was checked |
| **Warming Configuration** |
| `current_daily_limit` | Integer | No | Current sending limit (default: 5) |
| `warmup_start_date` | DateTime | Yes | When warming started |
| **Statistics** |
| `total_sent` | Integer | No | Total emails sent (default: 0) |
| `total_received` | Integer | No | Total emails received (default: 0) |
| `total_opened` | Integer | No | Total emails opened (default: 0) |
| `total_replied` | Integer | No | Total replies sent (default: 0) |
| `total_bounced` | Integer | No | Total bounces (default: 0) |
| **Timestamps (from TimestampMixin)** |
| `created_at` | DateTime | No | Account creation time |
| `updated_at` | DateTime | No | Last update time |

### Enums

```python
class AccountType(str, Enum):
    """Type of email account."""
    SENDER = "sender"      # Account to be warmed up
    RECEIVER = "receiver"  # Account that receives and responds

class AccountStatus(str, Enum):
    """Status of email account."""
    ACTIVE = "active"      # Account is active
    PAUSED = "paused"      # Temporarily paused
    DISABLED = "disabled"  # Disabled by user
    ERROR = "error"        # Has errors
```

### Relationships

```python
# Emails sent by this account
sent_emails: Mapped[list[Email]] = relationship(
    "Email",
    foreign_keys="Email.sender_id",
    back_populates="sender",
    cascade="all, delete-orphan"
)

# Emails received by this account
received_emails: Mapped[list[Email]] = relationship(
    "Email",
    foreign_keys="Email.receiver_id",
    back_populates="receiver",
    cascade="all, delete-orphan"
)

# Daily metrics for this account
metrics: Mapped[list[Metric]] = relationship(
    "Metric",
    back_populates="account",
    cascade="all, delete-orphan"
)
```

### Properties

#### `full_name`

Returns the full name or email username as fallback.

```python
@property
def full_name(self) -> str:
    """Get full name or email username as fallback."""
    if self.first_name and self.last_name:
        return f"{self.first_name} {self.last_name}"
    elif self.first_name:
        return self.first_name
    else:
        # Fallback to email username
        return self.email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
```

**Example:**
```python
account.first_name = "Mario"
account.last_name = "Rossi"
print(account.full_name)  # "Mario Rossi"

account2.email = "john.doe@example.com"
print(account2.full_name)  # "John Doe" (from email)
```

#### `bounce_rate`

Calculates the bounce rate as a percentage.

```python
@property
def bounce_rate(self) -> float:
    """Calculate bounce rate."""
    if self.total_sent == 0:
        return 0.0
    return self.total_bounced / self.total_sent
```

**Example:**
```python
account.total_sent = 100
account.total_bounced = 5
print(account.bounce_rate)  # 0.05 (5%)
```

#### `open_rate`

Calculates the open rate as a percentage.

```python
@property
def open_rate(self) -> float:
    """Calculate open rate."""
    if self.total_sent == 0:
        return 0.0
    return self.total_opened / self.total_sent
```

#### `reply_rate`

Calculates the reply rate as a percentage.

```python
@property
def reply_rate(self) -> float:
    """Calculate reply rate."""
    if self.total_received == 0:
        return 0.0
    return self.total_replied / self.total_received
```

### Methods

#### `get_password()`

Retrieves the decrypted password.

```python
def get_password(self) -> str:
    """
    Get decrypted password.

    Returns:
        Plain text password
    """
    if hasattr(self, '_plaintext_password') and self._plaintext_password:
        return self._plaintext_password

    from warmit.services.encryption import decrypt_password
    decrypted = decrypt_password(self.password)
    self._plaintext_password = decrypted
    return decrypted
```

**Usage:**
```python
account = session.query(Account).first()
password = account.get_password()  # Returns decrypted password
```

#### `set_password(plaintext_password)`

Sets and encrypts the password.

```python
def set_password(self, plaintext_password: str) -> None:
    """
    Set password (will be encrypted).

    Args:
        plaintext_password: Plain text password to encrypt and store
    """
    from warmit.services.encryption import encrypt_password
    self.password = encrypt_password(plaintext_password)
```

**Usage:**
```python
account = Account(email="test@example.com", ...)
account.set_password("my_secure_password")
# password field now contains encrypted version
```

### SQLAlchemy Events

#### Auto-Encryption on Save

```python
@event.listens_for(Account, "before_insert")
@event.listens_for(Account, "before_update")
def encrypt_password_on_save(mapper, connection, target):
    """Encrypt password before saving to database."""
    from warmit.services.encryption import encrypt_password

    # Check if password looks like plaintext (not already encrypted)
    if target.password and not target.password.startswith('gAAAAA'):
        target.password = encrypt_password(target.password)
```

#### Auto-Decryption on Load

```python
@event.listens_for(Account, "load")
def decrypt_password_on_load(target, context):
    """Decrypt password after loading from database."""
    from warmit.services.encryption import decrypt_password

    if target.password:
        decrypted = decrypt_password(target.password)
        target._plaintext_password = decrypted
```

### Example Usage

```python
from warmit.models.account import Account, AccountType, AccountStatus

# Create sender account
sender = Account(
    email="sender@gmail.com",
    first_name="John",
    last_name="Doe",
    type=AccountType.SENDER,
    status=AccountStatus.ACTIVE,
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_use_tls=True,
    imap_host="imap.gmail.com",
    imap_port=993,
    imap_use_ssl=True,
)
sender.set_password("app_password_here")

# Add to session and commit
session.add(sender)
await session.commit()

# Retrieve and use
account = await session.get(Account, sender_id)
password = account.get_password()  # Decrypted automatically
print(f"Full name: {account.full_name}")
print(f"Bounce rate: {account.bounce_rate:.2%}")
```

---

## Campaign Model

**File:** `src/warmit/models/campaign.py`

Represents a warming campaign with multiple senders and receivers.

### Class Definition

```python
class Campaign(Base, TimestampMixin):
    """Warming campaign configuration and tracking."""

    __tablename__ = "campaigns"
```

### Fields

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | Integer | No | Primary key |
| `name` | String(255) | No | Campaign name |
| **Configuration** |
| `sender_account_ids` | JSON (List[int]) | No | List of sender account IDs |
| `receiver_account_ids` | JSON (List[int]) | No | List of receiver account IDs |
| `status` | CampaignStatus | No | Campaign status |
| `start_date` | DateTime | Yes | Campaign start time |
| `end_date` | DateTime | Yes | Campaign end time |
| `duration_weeks` | Integer | No | Duration in weeks (default: 6) |
| `language` | String(10) | No | Email language ("en" or "it") |
| **Progress Tracking** |
| `current_week` | Integer | No | Current week number (default: 0) |
| `emails_sent_today` | Integer | No | Emails sent today (default: 0) |
| `target_emails_today` | Integer | No | Target for today (default: 5) |
| `last_email_sent_at` | DateTime | Yes | Last email send time |
| `next_send_time` | DateTime | Yes | Next scheduled send |
| **Statistics** |
| `total_emails_sent` | Integer | No | Total emails sent (default: 0) |
| `total_emails_opened` | Integer | No | Total emails opened (default: 0) |
| `total_emails_replied` | Integer | No | Total replies (default: 0) |
| `total_emails_bounced` | Integer | No | Total bounces (default: 0) |
| **Settings** |
| `settings` | JSON (dict) | Yes | Additional settings |
| **Timestamps** |
| `created_at` | DateTime | No | Campaign creation time |
| `updated_at` | DateTime | No | Last update time |

### Enums

```python
class CampaignStatus(str, Enum):
    """Status of a warming campaign."""
    PENDING = "pending"      # Not yet started
    ACTIVE = "active"        # Currently running
    PAUSED = "paused"        # Temporarily paused
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"        # Failed due to errors
```

### Properties

#### `open_rate`

```python
@property
def open_rate(self) -> float:
    """Calculate campaign open rate."""
    if self.total_emails_sent == 0:
        return 0.0
    return self.total_emails_opened / self.total_emails_sent
```

#### `reply_rate`

```python
@property
def reply_rate(self) -> float:
    """Calculate campaign reply rate."""
    if self.total_emails_sent == 0:
        return 0.0
    return self.total_emails_replied / self.total_emails_sent
```

#### `bounce_rate`

```python
@property
def bounce_rate(self) -> float:
    """Calculate campaign bounce rate."""
    if self.total_emails_sent == 0:
        return 0.0
    return self.total_emails_bounced / self.total_emails_sent
```

#### `progress_percentage`

```python
@property
def progress_percentage(self) -> float:
    """Calculate campaign progress percentage."""
    total_weeks = self.duration_weeks
    if total_weeks == 0:
        return 0.0
    return (self.current_week / total_weeks) * 100
```

### Example Usage

```python
from warmit.models.campaign import Campaign, CampaignStatus

# Create campaign
campaign = Campaign(
    name="Q1 2026 Warming",
    sender_account_ids=[1, 2, 3],  # 3 senders
    receiver_account_ids=[10, 11, 12, 13, 14],  # 5 receivers
    status=CampaignStatus.ACTIVE,
    duration_weeks=6,
    language="en",
    current_week=1,
    target_emails_today=15,  # 5 per sender
)

session.add(campaign)
await session.commit()

# Check progress
print(f"Progress: {campaign.progress_percentage:.1f}%")
print(f"Open rate: {campaign.open_rate:.2%}")
print(f"Reply rate: {campaign.reply_rate:.2%}")
```

---

## Email Model

**File:** `src/warmit/models/email.py`

Represents an individual email sent/received.

### Class Definition

```python
class Email(Base, TimestampMixin):
    """Email record for tracking."""

    __tablename__ = "emails"
```

### Fields

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | Integer | No | Primary key |
| `sender_id` | Integer | No | FK to Account (sender) |
| `receiver_id` | Integer | No | FK to Account (receiver) |
| `campaign_id` | Integer | Yes | FK to Campaign |
| **Email Content** |
| `message_id` | String(255) | Yes | Email Message-ID header (unique) |
| `subject` | String(500) | No | Email subject |
| `body` | Text | No | Email body |
| `in_reply_to` | String(255) | Yes | In-Reply-To header |
| `references` | Text | Yes | References header |
| **Status & Tracking** |
| `status` | EmailStatus | No | Email status |
| `is_warmup` | Boolean | No | Is warming email (default: True) |
| `sent_at` | DateTime | Yes | Send timestamp |
| `opened_at` | DateTime | Yes | First open timestamp |
| `bounced_at` | DateTime | Yes | Bounce timestamp |
| **AI Generation** |
| `ai_generated` | Boolean | No | Generated by AI (default: False) |
| `ai_model` | String(100) | Yes | AI model used |
| `ai_prompt` | Text | Yes | Prompt used |
| **Timestamps** |
| `created_at` | DateTime | No | Record creation time |
| `updated_at` | DateTime | No | Last update time |

### Enums

```python
class EmailStatus(str, Enum):
    """Status of an email."""
    PENDING = "pending"  # Queued but not sent
    SENT = "sent"        # Successfully sent
    BOUNCED = "bounced"  # Bounced/failed
```

### Relationships

```python
# Sender account
sender: Mapped[Account] = relationship(
    "Account",
    foreign_keys=[sender_id],
    back_populates="sent_emails"
)

# Receiver account
receiver: Mapped[Account] = relationship(
    "Account",
    foreign_keys=[receiver_id],
    back_populates="received_emails"
)

# Campaign (optional)
campaign: Mapped[Optional[Campaign]] = relationship(
    "Campaign"
)
```

### Example Usage

```python
from warmit.models.email import Email, EmailStatus

# Create email record
email = Email(
    sender_id=1,
    receiver_id=10,
    campaign_id=5,
    message_id="<unique-id@example.com>",
    subject="Interesting article about productivity",
    body="Hi! I found this article...",
    status=EmailStatus.SENT,
    is_warmup=True,
    ai_generated=True,
    ai_model="meta-llama/llama-3.3-70b-instruct",
    ai_prompt="Generate casual email about productivity tips",
)

session.add(email)
await session.commit()

# Later: track open
email.opened_at = datetime.now(timezone.utc)
email.sender.total_opened += 1
await session.commit()
```

---

## Metric Model

**File:** `src/warmit/models/metric.py`

Daily statistics snapshot for each account.

### Fields

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | Integer | No | Primary key |
| `account_id` | Integer | No | FK to Account |
| `date` | Date | No | Metric date (unique with account_id) |
| **Counts** |
| `emails_sent` | Integer | No | Emails sent (default: 0) |
| `emails_received` | Integer | No | Emails received (default: 0) |
| `emails_opened` | Integer | No | Emails opened (default: 0) |
| `emails_replied` | Integer | No | Replies sent (default: 0) |
| `emails_bounced` | Integer | No | Bounces (default: 0) |
| **Rates** |
| `open_rate` | Float | No | Open rate (default: 0.0) |
| `reply_rate` | Float | No | Reply rate (default: 0.0) |
| `bounce_rate` | Float | No | Bounce rate (default: 0.0) |
| **Timestamps** |
| `created_at` | DateTime | No | Record creation time |
| `updated_at` | DateTime | No | Last update time |

### Methods

#### `calculate_rates()`

```python
def calculate_rates(self) -> None:
    """Calculate all rate metrics."""
    # Open rate
    if self.emails_sent > 0:
        self.open_rate = self.emails_opened / self.emails_sent
    else:
        self.open_rate = 0.0

    # Reply rate
    if self.emails_received > 0:
        self.reply_rate = self.emails_replied / self.emails_received
    else:
        self.reply_rate = 0.0

    # Bounce rate
    if self.emails_sent > 0:
        self.bounce_rate = self.emails_bounced / self.emails_sent
    else:
        self.bounce_rate = 0.0
```

### Example Usage

```python
from warmit.models.metric import Metric
from datetime import date

# Create daily metric
metric = Metric(
    account_id=1,
    date=date.today(),
    emails_sent=50,
    emails_opened=45,
    emails_replied=10,
    emails_bounced=1,
)
metric.calculate_rates()

session.add(metric)
await session.commit()

print(f"Open rate: {metric.open_rate:.2%}")    # 90%
print(f"Reply rate: {metric.reply_rate:.2%}")  # 20%
print(f"Bounce rate: {metric.bounce_rate:.2%}") # 2%
```

---

## Base Models

**File:** `src/warmit/models/base.py`

### Base

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all models."""
    pass
```

### TimestampMixin

Adds automatic timestamp fields to models.

```python
from sqlalchemy import DateTime, func

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
```

**Usage:**
```python
class MyModel(Base, TimestampMixin):
    """My model with automatic timestamps."""
    __tablename__ = "my_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    # created_at and updated_at added automatically
```

---

## Common Queries

### Get All Active Senders

```python
from sqlalchemy import select
from warmit.models.account import Account, AccountType, AccountStatus

result = await session.execute(
    select(Account).where(
        Account.type == AccountType.SENDER,
        Account.status == AccountStatus.ACTIVE
    )
)
senders = result.scalars().all()
```

### Get Campaign with Accounts

```python
from sqlalchemy.orm import selectinload

result = await session.execute(
    select(Campaign)
    .where(Campaign.id == campaign_id)
)
campaign = result.scalar_one()

# Get sender accounts
sender_result = await session.execute(
    select(Account).where(Account.id.in_(campaign.sender_account_ids))
)
senders = sender_result.scalars().all()
```

### Get Recent Emails with Tracking

```python
from datetime import datetime, timedelta

week_ago = datetime.now(timezone.utc) - timedelta(days=7)

result = await session.execute(
    select(Email)
    .options(
        selectinload(Email.sender),
        selectinload(Email.receiver)
    )
    .where(Email.sent_at >= week_ago)
    .order_by(Email.sent_at.desc())
)
recent_emails = result.scalars().all()

for email in recent_emails:
    print(f"{email.sender.email} → {email.receiver.email}")
    print(f"Opened: {'Yes' if email.opened_at else 'No'}")
```

---

**Last Updated:** 2026-01-17
**Version:** 1.0.0
