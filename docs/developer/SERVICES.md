# 🔧 Services Reference

Complete reference for all business logic services in WarmIt.

**Location:** `src/warmit/services/`

---

## Table of Contents

- [EmailService](#emailservice) - SMTP/IMAP operations
- [AIGenerator](#aigenerator) - Content generation
- [ResponseBot](#responsebot) - Auto-reply system
- [WarmupScheduler](#warmupscheduler) - Campaign execution
- [BounceDetector](#bouncedetector) - Bounce detection
- [DomainChecker](#domainchecker) - Domain age verification
- [HealthMonitor](#healthmonitor) - System health checks
- [RateLimitTracker](#ratelimittracker) - API rate limiting
- [EncryptionService](#encryptionservice) - Database encryption
- [TrackingTokenService](#trackingtokenservice) - HMAC tracking tokens
- [RateLimitMiddleware](#ratelimitmiddleware) - HTTP rate limiting

---

## EmailService

**File:** `src/warmit/services/email_service.py`

Handles all SMTP and IMAP email operations.

### Class: `EmailMessage`

Container for email messages.

```python
class EmailMessage:
    """Email message container."""

    def __init__(
        self,
        sender: str,
        receiver: str,
        subject: str,
        body: str,
        message_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
        tracking_url: Optional[str] = None,
    ):
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.body = body
        self.message_id = message_id or make_msgid()
        self.in_reply_to = in_reply_to
        self.references = references
        self.tracking_url = tracking_url
```

#### Method: `to_mime()`

Converts EmailMessage to MIME format.

```python
def to_mime(self) -> MIMEMultipart:
    """
    Convert to MIME message.

    Returns:
        MIMEMultipart message ready to send

    Note:
        - Creates multipart/alternative with text and HTML parts
        - Adds tracking pixel if tracking_url provided
        - Preserves In-Reply-To and References headers for threading
    """
```

**Example:**
```python
msg = EmailMessage(
    sender="sender@example.com",
    receiver="receiver@example.com",
    subject="Test Email",
    body="Hello!\n\nThis is a test.",
    tracking_url="https://api.example.com/track/open/123"
)

mime_msg = msg.to_mime()
# Ready to send via SMTP
```

### Class: `EmailService`

Main service for email operations.

#### Method: `send_email()`

Sends an email via SMTP.

```python
@staticmethod
async def send_email(
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
        smtp_host: SMTP server hostname (e.g., "smtp.gmail.com")
        smtp_port: SMTP server port (587 for STARTTLS, 465 for SSL)
        username: SMTP username (usually email address)
        password: SMTP password (use App Password for Gmail/Outlook)
        message: EmailMessage object to send
        use_tls: Whether to use STARTTLS (True) or direct SSL (False)

    Returns:
        True if email sent successfully, False otherwise

    Note:
        - Port 465: Direct SSL connection (use_tls parameter ignored)
        - Port 587: STARTTLS if use_tls=True
        - Automatically handles connection type based on port
    """
```

**Port Handling:**
```python
if smtp_port == 465:
    # SSL/TLS direct connection (implicit TLS)
    await aiosmtplib.send(
        mime_msg,
        hostname=smtp_host,
        port=smtp_port,
        username=username,
        password=password,
        use_tls=True,      # Enable TLS wrapper
        start_tls=False,   # Don't use STARTTLS
    )
else:
    # Port 587 or other: use STARTTLS if use_tls=True
    await aiosmtplib.send(
        mime_msg,
        hostname=smtp_host,
        port=smtp_port,
        username=username,
        password=password,
        use_tls=False,     # Don't wrap connection in TLS
        start_tls=use_tls, # Use STARTTLS instead
    )
```

**Example:**
```python
from warmit.services.email_service import EmailService, EmailMessage

service = EmailService()

# Gmail example (port 587, STARTTLS)
msg = EmailMessage(
    sender="sender@gmail.com",
    receiver="receiver@example.com",
    subject="Test",
    body="Hello!"
)

success = await service.send_email(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    username="sender@gmail.com",
    password="app_password_here",
    message=msg,
    use_tls=True  # Use STARTTLS
)

# Libero example (port 465, SSL)
success = await service.send_email(
    smtp_host="smtp.libero.it",
    smtp_port=465,
    username="sender@libero.it",
    password="password_here",
    message=msg,
    use_tls=False  # Port 465 uses SSL automatically
)
```

#### Method: `fetch_unread_emails()`

Fetches unread emails from IMAP server.

```python
@staticmethod
async def fetch_unread_emails(
    imap_host: str,
    imap_port: int,
    username: str,
    password: str,
    use_ssl: bool = True,
    limit: int = 50,
) -> list[dict]:
    """
    Fetch unread emails from IMAP server.

    Args:
        imap_host: IMAP server hostname (e.g., "imap.gmail.com")
        imap_port: IMAP server port (usually 993)
        username: IMAP username (usually email address)
        password: IMAP password
        use_ssl: Whether to use SSL (default: True)
        limit: Maximum number of emails to fetch

    Returns:
        List of email dictionaries with fields:
            - message_id: Email Message-ID
            - subject: Email subject
            - from: Sender email
            - to: Recipient email
            - date: Send date
            - in_reply_to: In-Reply-To header
            - references: References header
            - body: Plain text body
            - imap_id: IMAP message ID (for re-marking as unread)

    Note:
        - Searches for UNSEEN emails
        - Uses RFC822 fetch (marks as \\Seen)
        - Response bot re-marks as unread if not responding
    """
```

**Example:**
```python
emails = await service.fetch_unread_emails(
    imap_host="imap.gmail.com",
    imap_port=993,
    username="receiver@gmail.com",
    password="app_password",
    use_ssl=True,
    limit=20
)

for email in emails:
    print(f"From: {email['from']}")
    print(f"Subject: {email['subject']}")
    print(f"Body: {email['body'][:100]}...")
    print(f"IMAP ID: {email['imap_id']}")
```

#### Static Method: `_extract_body()`

Extracts plain text body from email message.

```python
@staticmethod
def _extract_body(email_message) -> str:
    """
    Extract plain text body from email message.

    Args:
        email_message: Parsed email.message object

    Returns:
        Plain text body content

    Note:
        - Handles multipart messages
        - Extracts first text/plain part
        - Returns empty string if no text part found
    """
```

---

## AIGenerator

**File:** `src/warmit/services/ai_generator.py`

Generates email content using AI providers with automatic fallback.

### Class Definition

```python
class AIGenerator:
    """AI-powered email content generator with multi-provider fallback."""

    def __init__(self):
        self.providers = self._load_providers()
        self.fallback_generator = LocalFallbackGenerator()
```

### Method: `generate_email()`

Generates email content with automatic provider fallback.

```python
async def generate_email(
    self,
    sender_name: str,
    language: str = "en",
    is_reply: bool = False,
    original_subject: Optional[str] = None,
    original_body: Optional[str] = None,
) -> EmailContent:
    """
    Generate email content using AI with fallback chain.

    Args:
        sender_name: Name of the sender (for personalization)
        language: Language code ("en" or "it")
        is_reply: Whether this is a reply to another email
        original_subject: Subject of email being replied to
        original_body: Body of email being replied to

    Returns:
        EmailContent with subject, body, prompt, model used

    Fallback Chain:
        1. Try all configured AI providers (OpenRouter, Groq, OpenAI)
        2. If all fail, use local template generator
        3. Never fails - always returns content

    Example:
        >>> generator = AIGenerator()
        >>> content = await generator.generate_email(
        ...     sender_name="Mario Rossi",
        ...     language="it",
        ...     is_reply=False
        ... )
        >>> print(content.subject)
        "Consigli di produttività"
        >>> print(content.model)
        "meta-llama/llama-3.3-70b-instruct"
    """
```

**Provider Selection Logic:**
```python
# Try each provider in order
for provider_config in self.providers:
    try:
        # Check rate limits
        if await self.rate_tracker.can_make_request(provider_name):
            # Try generation
            content = await self._generate_with_provider(
                provider_config,
                prompt
            )

            # Record success
            await self.rate_tracker.record_success(provider_name)
            return content

    except Exception as e:
        # Try next provider
        continue

# All providers failed - use local fallback
return self.fallback_generator.generate(language, is_reply)
```

### Method: `_generate_with_provider()`

Generates content with a specific AI provider.

```python
async def _generate_with_provider(
    self,
    provider_config: dict,
    prompt: str,
    max_retries: int = 1,
) -> EmailContent:
    """
    Generate content with specific provider.

    Args:
        provider_config: Provider configuration dict with:
            - name: Provider name
            - api_key: API key
            - base_url: API base URL
            - model: Model name
        prompt: Generation prompt
        max_retries: Maximum retry attempts

    Returns:
        EmailContent object

    Raises:
        Exception if generation fails after all retries
    """
```

**Example:**
```python
# Initialize generator
generator = AIGenerator()

# Generate initial email
content = await generator.generate_email(
    sender_name="John Doe",
    language="en",
    is_reply=False
)
print(f"Subject: {content.subject}")
print(f"Body: {content.body}")
print(f"Model: {content.model}")

# Generate reply
reply_content = await generator.generate_email(
    sender_name="Jane Smith",
    language="en",
    is_reply=True,
    original_subject="Tips for productivity",
    original_body="I found this interesting article..."
)
print(f"Reply Subject: {reply_content.subject}")  # "Re: Tips for productivity"
```

### Local Fallback Generator

When all AI providers fail, uses local template generation.

```python
class LocalFallbackGenerator:
    """Local template-based email generator."""

    def generate(
        self,
        language: str = "en",
        is_reply: bool = False
    ) -> EmailContent:
        """
        Generate email from local templates.

        Combinations:
            - 42,875+ unique email combinations
            - Random topic selection
            - Template-based generation
            - No API required

        Returns:
            EmailContent with model="local_fallback"
        """
```

---

## ResponseBot

**File:** `src/warmit/services/response_bot.py`

Handles automatic responses to incoming emails.

### Class Definition

```python
class ResponseBot:
    """Automated email response bot for receiver accounts."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.email_service = EmailService()
        self.ai_generator = AIGenerator()
```

### Method: `process_all_receivers()`

Processes all receiver accounts.

```python
async def process_all_receivers(self) -> dict[int, int]:
    """
    Process all active receiver accounts.

    Returns:
        Dictionary mapping account_id to number of emails processed

    Workflow:
        1. Get all active receiver accounts
        2. For each account:
           - Fetch unread emails
           - Decide whether to respond (85% probability)
           - Generate and send reply OR mark as unread
        3. Update statistics

    Example:
        >>> bot = ResponseBot(session)
        >>> results = await bot.process_all_receivers()
        >>> print(results)
        {1: 3, 2: 5, 3: 0}  # Account 1: 3 emails, Account 2: 5, Account 3: 0
    """
```

### Method: `process_receiver()`

Processes single receiver account.

```python
async def process_receiver(self, account: Account) -> int:
    """
    Process emails for a single receiver account.

    Args:
        account: Receiver Account object

    Returns:
        Number of emails processed (replied to)

    Workflow:
        1. Fetch unread emails via IMAP
        2. For each email:
           a. Decide if should respond (85% probability)
           b. If YES:
              - Generate reply with AI
              - Send via SMTP
              - Email stays as \\Seen
           c. If NO:
              - Mark as unread again (STORE -FLAGS \\Seen)
        3. Update account.total_replied counter

    Note:
        - Uses RFC822 fetch (marks as \\Seen initially)
        - Re-marks as unread if not responding
        - This prevents inbox from filling up with unread emails
    """
```

**Response Decision Logic:**
```python
async def _should_respond(self, email_data: dict) -> bool:
    """
    Decide whether to respond to email.

    Args:
        email_data: Email dictionary from fetch_unread_emails()

    Returns:
        True if should respond (85% probability), False otherwise

    Logic:
        - 85% chance to respond
        - 15% chance to ignore (simulates realistic engagement)
        - Random delay between checks (human-like behavior)
    """
    return random.random() < 0.85  # 85% response rate
```

**Unread Restoration:**
```python
# Re-mark emails as unread if we didn't respond
if emails_to_mark_unread:
    try:
        imap = aioimaplib.IMAP4_SSL(account.imap_host, account.imap_port)
        await imap.wait_hello_from_server()
        await imap.login(account.email, account.get_password())
        await imap.select("INBOX")

        for imap_id in emails_to_mark_unread:
            await imap.store(imap_id, "-FLAGS", "(\\Seen)")
            logger.debug(f"Re-marked email {imap_id} as unread")

        await imap.logout()
    except Exception as e:
        logger.error(f"Failed to re-mark emails as unread: {e}")
```

### Method: `_respond_to_email()`

Generates and sends reply to an email.

```python
async def _respond_to_email(
    self,
    account: Account,
    email_data: dict
) -> bool:
    """
    Generate and send reply to email.

    Args:
        account: Receiver Account object
        email_data: Email dictionary with subject, body, message_id, etc.

    Returns:
        True if reply sent successfully, False otherwise

    Workflow:
        1. Extract original email details
        2. Find associated campaign
        3. Generate reply with AI (using campaign language)
        4. Build reply message with proper threading headers
        5. Send via SMTP
        6. Record in database as Email record
        7. Update campaign statistics

    Threading Headers:
        - In-Reply-To: original message_id
        - References: original references + original message_id
        - Subject: "Re: " + original subject
    """
```

**Example:**
```python
from warmit.services.response_bot import ResponseBot

# Initialize bot
async with async_session_maker() as session:
    bot = ResponseBot(session)

    # Process all receivers
    results = await bot.process_all_receivers()

    for account_id, count in results.items():
        print(f"Account {account_id}: processed {count} emails")

    # Or process specific account
    account = await session.get(Account, receiver_id)
    count = await bot.process_receiver(account)
    print(f"Processed {count} emails for {account.email}")
```

---

## WarmupScheduler

**File:** `src/warmit/services/scheduler.py`

Manages email warming campaigns and progressive sending.

### Class Definition

```python
class WarmupScheduler:
    """Scheduler for progressive email warming campaigns."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.email_service = EmailService()
        self.ai_generator = AIGenerator()
```

### Method: `start_campaign()`

Creates and starts a new warming campaign.

```python
async def start_campaign(
    self,
    name: str,
    sender_account_ids: list[int],
    receiver_account_ids: list[int],
    duration_weeks: Optional[int] = None,
    language: str = "en",
) -> Campaign:
    """
    Start a new warming campaign.

    Args:
        name: Campaign name
        sender_account_ids: List of sender account IDs to warm up
        receiver_account_ids: List of receiver account IDs
        duration_weeks: Optional custom duration, otherwise calculated from domain age
        language: Email language ("en" or "it")

    Returns:
        Created Campaign object

    Workflow:
        1. Validate accounts exist
        2. Check domain ages (WHOIS/RDAP)
        3. Calculate optimal duration (2-8 weeks based on domain age)
        4. Create campaign with status=ACTIVE
        5. Set initial next_send_time (random time today)
        6. Update sender warmup_start_date

    Raises:
        ValueError: If accounts not found
    """
```

**Duration Calculation:**
```python
async def _calculate_optimal_duration(self, senders: list[Account]) -> int:
    """
    Calculate optimal warmup duration based on sender domain ages.

    Logic:
        - New domain (< 30 days): 8 weeks
        - Young domain (30-90 days): 6 weeks
        - Moderate domain (90-180 days): 4 weeks
        - Established domain (180+ days): 2 weeks

    Returns:
        Duration in weeks (2-8)
    """
```

### Method: `process_all_campaigns()`

Processes all active campaigns.

```python
async def process_all_campaigns(self) -> dict[int, int]:
    """
    Process all active warming campaigns.

    Returns:
        Dictionary mapping campaign_id to emails sent

    Workflow:
        1. Get all campaigns with status=ACTIVE
        2. For each campaign:
           - Call process_campaign()
        3. Return results

    Called by:
        Celery task: warmit.tasks.warming.process_campaigns
        Schedule: Every 2 hours
    """
```

### Method: `process_campaign()`

Processes a single campaign.

```python
async def process_campaign(self, campaign: Campaign) -> int:
    """
    Process a single warming campaign.

    Args:
        campaign: Campaign object to process

    Returns:
        Number of emails sent

    Workflow:
        1. Check if should send now (next_send_time passed)
        2. Check if reached daily target (emails_sent_today)
        3. Calculate how many to send
        4. Send emails via _send_warmup_emails()
        5. Update campaign counters
        6. Schedule next send time

    Next Send Time Logic:
        - If completed today's target: Schedule for tomorrow
        - Otherwise: Schedule for later today (30+ min from now)
    """
```

### Method: `_calculate_daily_target()`

Calculates daily email target based on campaign week.

```python
async def _calculate_daily_target(self, campaign: Campaign) -> int:
    """
    Calculate daily email target based on current week and domain ages.

    Progressive Schedule (per sender):
        Week 1: 5 emails/day
        Week 2: 10 emails/day
        Week 3: 15 emails/day
        Week 4: 25 emails/day
        Week 5: 35 emails/day
        Week 6+: 50 emails/day

    Domain Age Constraint (Week 1 only):
        - Very new domain (< 30 days): limit to 3/day
        - New domain (30-90 days): limit to 5/day
        - Moderate (90-180 days): limit to 10/day
        - Established (180+ days): no limit

    Scaling:
        Total target = base_target * num_senders

    Returns:
        Total daily target across all senders

    Example:
        Campaign with 3 senders, Week 1, established domains:
        base_target = 5
        total_target = 5 * 3 = 15 emails/day
    """
```

### Method: `_send_warmup_emails()`

Sends warming emails for a campaign.

```python
async def _send_warmup_emails(self, campaign: Campaign, count: int) -> int:
    """
    Send warmup emails for a campaign.

    Args:
        campaign: Campaign object
        count: Number of emails to send

    Returns:
        Number of emails successfully sent

    Workflow:
        1. Get sender and receiver accounts
        2. Distribute count across senders evenly
        3. Check each sender's bounce rate
        4. Randomize send order
        5. For each email:
           a. Select random receiver
           b. Generate AI content (with sender's name)
           c. Create Email record in DB (to get ID)
           d. Build tracking pixel URL
           e. Send via SMTP
           f. Update statistics
           g. Wait 2-10 minutes (production delay)
        6. Commit all changes

    Bounce Rate Protection:
        - If sender.bounce_rate > max_bounce_rate:
          - Skip sender
          - Optionally pause account (auto_pause_on_high_bounce)
    """
```

**Email Distribution Logic:**
```python
# Distribute emails across senders
emails_per_sender = count // len(senders)
remainder = count % len(senders)

# Example: count=7, senders=3
# emails_per_sender = 2
# remainder = 1
# Allocation: [2, 2, 3]

sender_allocations = []
for i, sender in enumerate(senders):
    sender_count = emails_per_sender
    if i < remainder:
        sender_count += 1

    for _ in range(sender_count):
        sender_allocations.append(sender)

# Randomize order
random.shuffle(sender_allocations)
```

**Example:**
```python
from warmit.services.scheduler import WarmupScheduler

async with async_session_maker() as session:
    scheduler = WarmupScheduler(session)

    # Start new campaign
    campaign = await scheduler.start_campaign(
        name="Q1 2026 Warming",
        sender_account_ids=[1, 2, 3],
        receiver_account_ids=[10, 11, 12, 13, 14],
        language="en"
    )

    # Process campaign (send emails)
    emails_sent = await scheduler.process_campaign(campaign)
    print(f"Sent {emails_sent} emails")

    # Process all campaigns
    results = await scheduler.process_all_campaigns()
    print(f"Total sent: {sum(results.values())}")
```

---

## BounceDetector

**File:** `src/warmit/services/bounce_detector.py`

Detects bounced emails in sender inboxes.

### Method: `process_all_senders()`

Checks all sender accounts for bounce notifications.

```python
async def process_all_senders(self) -> dict[int, int]:
    """
    Process all active sender accounts for bounces.

    Returns:
        Dictionary mapping account_id to bounces detected

    Workflow:
        1. Get all active sender accounts
        2. For each sender:
           - Check inbox for bounce notifications
           - Parse bounce messages
           - Update Email records
           - Update statistics
    """
```

---

## Common Usage Patterns

### Sending Email with Tracking

```python
from warmit.services.email_service import EmailService, EmailMessage

# Create message with tracking pixel
message = EmailMessage(
    sender="sender@example.com",
    receiver="receiver@example.com",
    subject="Test Email",
    body="Hello!",
    tracking_url="https://api.example.com/track/open/123"
)

# Send
service = EmailService()
success = await service.send_email(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    username="sender@example.com",
    password="app_password",
    message=message,
    use_tls=True
)
```

### Generating AI Content

```python
from warmit.services.ai_generator import AIGenerator

generator = AIGenerator()

# Generate email
content = await generator.generate_email(
    sender_name="Mario Rossi",
    language="it",
    is_reply=False
)

# Generate reply
reply = await generator.generate_email(
    sender_name="Luca Verdi",
    language="it",
    is_reply=True,
    original_subject=content.subject,
    original_body=content.body
)
```

### Running Response Bot

```python
from warmit.services.response_bot import ResponseBot

async with async_session_maker() as session:
    bot = ResponseBot(session)

    # Process all receivers
    results = await bot.process_all_receivers()

    total = sum(results.values())
    print(f"Processed {total} emails across {len(results)} accounts")
```

---

## EncryptionService

**File:** `src/warmit/services/encryption.py`

Handles encryption/decryption of sensitive data (email passwords) using Fernet symmetric encryption.

### Class Definition

```python
class EncryptionService:
    """Handle encryption/decryption of sensitive data using Fernet."""

    def __init__(self, require_key: bool = True):
        """
        Initialize encryption service.

        Args:
            require_key: If True, log error if ENCRYPTION_KEY not set

        Note:
            - Reads ENCRYPTION_KEY from environment
            - If not set, encryption operations will raise EncryptionError
            - NEVER falls back to plaintext storage
        """
```

### Method: `encrypt()`

```python
def encrypt(self, plaintext: str) -> str:
    """
    Encrypt a string.

    Args:
        plaintext: String to encrypt

    Returns:
        Encrypted string (base64 encoded Fernet token)

    Raises:
        EncryptionError: If ENCRYPTION_KEY not configured

    Note:
        - NEVER falls back to plaintext
        - Empty strings are returned as-is
    """
```

### Method: `decrypt()`

```python
def decrypt(self, ciphertext: str) -> str:
    """
    Decrypt a string.

    Args:
        ciphertext: Encrypted string

    Returns:
        Decrypted plaintext

    Raises:
        EncryptionError: If data appears encrypted but key not configured

    Note:
        - Detects Fernet tokens by 'gAAAAA' prefix
        - For backwards compatibility, non-encrypted strings returned as-is
    """
```

**Example:**
```python
from warmit.services.encryption import get_encryption_service

service = get_encryption_service()

# Encrypt password
encrypted = service.encrypt("my_secret_password")
# Output: "gAAAAABk..."

# Decrypt password
decrypted = service.decrypt(encrypted)
# Output: "my_secret_password"
```

---

## TrackingTokenService

**File:** `src/warmit/services/tracking_token.py`

Generates and validates HMAC-SHA256 tokens for secure email tracking URLs.

### Function: `generate_tracking_token()`

```python
def generate_tracking_token(email_id: int) -> Tuple[str, int]:
    """
    Generate HMAC token for tracking URL.

    Args:
        email_id: Database ID of the email

    Returns:
        Tuple of (token, timestamp)

    Note:
        - Token is HMAC-SHA256 of "email_id:timestamp"
        - Truncated to 32 chars for shorter URLs
        - Requires TRACKING_SECRET_KEY in environment
    """
```

### Function: `validate_tracking_token()`

```python
def validate_tracking_token(email_id: int, token: str, timestamp: int) -> bool:
    """
    Validate tracking token.

    Args:
        email_id: Email ID from URL
        token: Token from URL
        timestamp: Timestamp from URL

    Returns:
        True if valid and not expired, False otherwise

    Note:
        - Tokens expire after 30 days
        - Uses constant-time comparison (hmac.compare_digest)
    """
```

### Function: `generate_tracking_url()`

```python
def generate_tracking_url(email_id: int, base_url: str) -> str:
    """
    Generate complete tracking URL with token.

    Args:
        email_id: Database ID of the email
        base_url: API base URL (e.g., "https://warmit.example.com")

    Returns:
        Complete tracking URL with token and timestamp

    Example:
        >>> generate_tracking_url(123, "https://warmit.example.com")
        "https://warmit.example.com/track/open/123?token=a1b2c3...&ts=1705484400"
    """
```

---

## RateLimitMiddleware

**File:** `src/warmit/middleware/rate_limit.py`

FastAPI middleware for protecting API endpoints from abuse.

### Class Definition

```python
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""
```

### Rate Limits

| Endpoint Type | Max Requests | Window |
|---------------|--------------|--------|
| `/auth/*`, `/login/*` | 5 | 5 minutes |
| `/password/*` | 3 | 5 minutes |
| `/api/*` | 100 | 1 minute |
| `/track/*` | 500 | 1 minute |
| Default | 60 | 1 minute |

### Response Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 60
```

### Rate Limit Exceeded Response

```json
HTTP 429 Too Many Requests
Retry-After: 45

{
    "detail": "Rate limit exceeded. Please retry after 45 seconds."
}
```

**Example:**
```python
# In main.py
from warmit.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware)
```

---

**Last Updated:** 2026-01-17
**Version:** 1.0.3
