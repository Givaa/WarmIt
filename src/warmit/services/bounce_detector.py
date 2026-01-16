"""Bounce detection service for identifying email delivery failures."""

import logging
import re
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from warmit.models.email import Email, EmailStatus
from warmit.models.account import Account, AccountType
from warmit.services.email_service import EmailService


logger = logging.getLogger(__name__)


class BounceDetector:
    """Service for detecting and processing email bounces."""

    # Patterns that indicate bounce/delivery failure
    BOUNCE_SUBJECT_PATTERNS = [
        r"delivery\s+status\s+notification",
        r"undelivered\s+mail",
        r"returned\s+mail",
        r"mail\s+delivery\s+(failed|failure)",
        r"undeliverable",
        r"mailer-daemon",
        r"delivery\s+failure",
        r"message\s+not\s+delivered",
    ]

    # Compile patterns for efficiency
    BOUNCE_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in BOUNCE_SUBJECT_PATTERNS]

    def __init__(self, session: AsyncSession):
        self.session = session
        self.email_service = EmailService()

    @classmethod
    def is_bounce_message(cls, subject: str, sender: str) -> bool:
        """
        Determine if an email is a bounce notification.

        Args:
            subject: Email subject line
            sender: Sender email address

        Returns:
            True if this appears to be a bounce message
        """
        # Check sender
        sender_lower = sender.lower()
        if any(keyword in sender_lower for keyword in ["mailer-daemon", "postmaster", "noreply"]):
            return True

        # Check subject patterns
        for pattern in cls.BOUNCE_PATTERNS:
            if pattern.search(subject):
                return True

        return False

    async def process_sender_bounces(self, account: Account) -> int:
        """
        Check a sender account for bounce notifications and process them.

        Args:
            account: Sender account to check

        Returns:
            Number of bounces detected
        """
        if account.type != AccountType.SENDER:
            logger.warning(f"Account {account.email} is not a sender account")
            return 0

        logger.info(f"Checking {account.email} for bounce notifications")

        # Fetch unread emails
        unread_emails = await self.email_service.fetch_unread_emails(
            imap_host=account.imap_host,
            imap_port=account.imap_port,
            username=account.email,
            password=account.get_password(),
            use_ssl=account.imap_use_ssl,
        )

        if not unread_emails:
            logger.debug(f"No unread emails for {account.email}")
            return 0

        bounce_count = 0

        for email_data in unread_emails:
            try:
                subject = email_data.get("subject", "")
                sender = email_data.get("from", "")
                body = email_data.get("body", "")

                # Check if this is a bounce message
                if self.is_bounce_message(subject, sender):
                    logger.warning(f"Bounce detected: {subject} from {sender}")

                    # Try to find the original email
                    # Bounce messages usually quote the original message ID or recipient
                    original_email = await self._find_bounced_email(account, body)

                    if original_email:
                        # Mark as bounced
                        original_email.status = EmailStatus.BOUNCED
                        original_email.bounced_at = datetime.now(timezone.utc)

                        # Update sender stats
                        account.total_bounced += 1

                        bounce_count += 1

                        logger.info(
                            f"Marked email {original_email.id} as bounced: "
                            f"{account.email} → {original_email.receiver.email if original_email.receiver else 'unknown'}"
                        )
                    else:
                        logger.warning(f"Could not find original email for bounce from {sender}")

                    # Mark bounce notification as read
                    await self.email_service.mark_as_read(
                        imap_host=account.imap_host,
                        imap_port=account.imap_port,
                        username=account.email,
                        password=account.get_password(),
                        message_id=email_data.get("message_id"),
                        use_ssl=account.imap_use_ssl,
                    )

            except Exception as e:
                logger.error(f"Error processing potential bounce: {e}")
                continue

        if bounce_count > 0:
            await self.session.commit()
            logger.info(f"Processed {bounce_count} bounces for {account.email}")

        return bounce_count

    async def _find_bounced_email(self, sender_account: Account, bounce_body: str) -> Email | None:
        """
        Try to find the original email that bounced.

        Args:
            sender_account: The sender account that received the bounce
            bounce_body: Body of the bounce notification

        Returns:
            The original Email record if found, None otherwise
        """
        # Try to extract recipient email from bounce body
        # Common patterns: "to: email@domain.com" or "<email@domain.com>"
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        potential_recipients = re.findall(email_pattern, bounce_body)

        if not potential_recipients:
            return None

        # Try each potential recipient
        for recipient_email in potential_recipients:
            # Skip if it's the sender's own email
            if recipient_email.lower() == sender_account.email.lower():
                continue

            # Look for recent sent email to this recipient
            result = await self.session.execute(
                select(Email)
                .where(
                    Email.sender_id == sender_account.id,
                    Email.status == EmailStatus.SENT,
                )
                .order_by(Email.sent_at.desc())
                .limit(10)  # Check last 10 sent emails
            )
            recent_emails = result.scalars().all()

            for email in recent_emails:
                if email.receiver and email.receiver.email.lower() == recipient_email.lower():
                    return email

        return None

    async def process_all_senders(self) -> dict[str, int]:
        """
        Process bounce detection for all active sender accounts.

        Returns:
            Dictionary mapping account emails to number of bounces detected
        """
        # Get all active sender accounts
        result = await self.session.execute(
            select(Account).where(
                Account.type == AccountType.SENDER,
                Account.status.in_(["active", "paused"]),  # Check both active and paused
            )
        )
        senders = result.scalars().all()

        logger.info(f"Processing bounce detection for {len(senders)} sender accounts")

        results = {}
        for sender in senders:
            count = await self.process_sender_bounces(sender)
            results[sender.email] = count

        return results
