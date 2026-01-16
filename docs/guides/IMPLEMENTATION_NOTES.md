# Implementation Notes

## Email Scheduling System (v0.2.2+)

### Current Implementation

The system now supports scheduled email sending with random timing:

1. **Campaign Scheduling**
   - Campaigns have a `next_send_time` field that determines when the next batch of emails will be sent
   - Times are randomized within business hours (9 AM - 6 PM local time)
   - After sending, the next send time is automatically calculated for the following day

2. **Manual "Send Now" Override**
   - The "Send Now" button in the dashboard bypasses the scheduled time (uses `force=True`)
   - This is useful for testing and verification without waiting for the scheduled time
   - Manual sends still respect daily email limits and campaign status

3. **Database Schema**
   - `campaigns.next_send_time` - When the campaign should next send emails
   - `emails.scheduled_send_time` - When an individual email (reply) should be sent

### Known Limitations

**Reply Timing**: While the system calculates random reply times (2-8 hours after original email), replies are currently sent immediately due to the synchronous nature of the response_bot.

**To fully implement delayed replies**, you would need:

1. A background worker (Celery, RQ, or similar) to process scheduled emails
2. Modify `response_bot.py` to:
   - Store replies with `scheduled_send_time` but `status=PENDING`
   - NOT send them immediately
3. Create a worker that:
   - Queries `emails` where `status=PENDING` and `scheduled_send_time <= now()`
   - Sends those emails
   - Updates `status=SENT`

### Example Worker Implementation (Not Included)

```python
# workers/email_sender.py
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from warmit.models.email import Email, EmailStatus
from warmit.services.email_service import EmailService

async def process_scheduled_emails():
    \"\"\"Send emails that are scheduled for now or earlier.\"\"\"
    while True:
        # Query pending emails
        result = await session.execute(
            select(Email).where(
                Email.status == EmailStatus.PENDING,
                Email.scheduled_send_time <= datetime.now(timezone.utc)
            )
        )
        pending_emails = result.scalars().all()

        for email in pending_emails:
            # Send email logic here
            ...

        await asyncio.sleep(60)  # Check every minute
```

### Workaround for Current Version

The current implementation sends emails immediately but logs the intended send time. This provides natural-looking timing for outbound campaigns, though replies are instant.

For production use with delayed replies:
1. Implement the background worker as described above
2. Or use a cron job that runs every 5-10 minutes to send scheduled emails
3. Or integrate with a job queue system (Redis + RQ recommended)

---

**Last Updated:** 2026-01-16
**Version:** 0.2.2-dev
