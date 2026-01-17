"""Automated email response bot."""

import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from warmit.models.account import Account, AccountStatus, AccountType
from warmit.models.email import Email, EmailStatus
from warmit.models.campaign import Campaign
from warmit.services.email_service import EmailService, EmailMessage
from warmit.services.ai_generator import AIGenerator
from warmit.services.tracking_token import generate_tracking_url
from warmit.config import settings


logger = logging.getLogger(__name__)


class ResponseBot:
    """Automated bot that reads and responds to emails."""

    def __init__(self, session: AsyncSession):
        """
        Initialize response bot.

        Args:
            session: Database session
        """
        self.session = session
        self.email_service = EmailService()
        self.ai_generator = AIGenerator()

    async def process_receiver_account(self, account: Account) -> int:
        """
        Process unread emails for a receiver account.

        Args:
            account: Receiver account to process

        Returns:
            Number of emails processed
        """
        if account.type != AccountType.RECEIVER:
            logger.warning(f"Account {account.email} is not a receiver account")
            return 0

        if account.status != AccountStatus.ACTIVE:
            logger.info(f"Account {account.email} is not active, skipping")
            return 0

        logger.info(f"Processing receiver account: {account.email}")

        # Fetch unread emails (decrypt password for IMAP)
        unread_emails = await self.email_service.fetch_unread_emails(
            imap_host=account.imap_host,
            imap_port=account.imap_port,
            username=account.email,
            password=account.get_password(),
            use_ssl=account.imap_use_ssl,
        )

        if not unread_emails:
            logger.info(f"No unread emails for {account.email}")
            return 0

        processed_count = 0
        emails_to_mark_unread = []  # Track emails we didn't respond to

        for email_data in unread_emails:
            try:
                # Check if we should respond to this email
                if await self._should_respond(email_data):
                    # Simulate human delay before responding
                    await self._simulate_human_delay()

                    # Generate and send response
                    success = await self._respond_to_email(account, email_data)

                    if success:
                        processed_count += 1
                        # Email stays as \Seen since we responded
                    else:
                        # Failed to respond, mark for unread restoration
                        if "imap_id" in email_data:
                            emails_to_mark_unread.append(email_data["imap_id"])
                else:
                    # Decided not to respond (15% chance), mark for unread restoration
                    if "imap_id" in email_data:
                        emails_to_mark_unread.append(email_data["imap_id"])

            except Exception as e:
                logger.error(f"Failed to process email: {e}")
                continue

        # Re-mark emails as unread if we didn't respond to them
        # This is needed because RFC822 fetch automatically marks as \Seen
        if emails_to_mark_unread:
            try:
                import aioimaplib
                imap = aioimaplib.IMAP4_SSL(account.imap_host, account.imap_port) if account.imap_use_ssl else aioimaplib.IMAP4(account.imap_host, account.imap_port)
                await imap.wait_hello_from_server()
                await imap.login(account.email, account.get_password())
                await imap.select("INBOX")

                for imap_id in emails_to_mark_unread:
                    await imap.store(imap_id, "-FLAGS", "(\\Seen)")
                    logger.debug(f"Re-marked email {imap_id} as unread")

                await imap.logout()
                logger.info(f"Re-marked {len(emails_to_mark_unread)} emails as unread")
            except Exception as e:
                logger.error(f"Failed to re-mark emails as unread: {e}")

        # Update account statistics
        account.total_received += len(unread_emails)
        account.total_replied += processed_count
        await self.session.commit()

        logger.info(
            f"Processed {processed_count}/{len(unread_emails)} emails for {account.email}"
        )

        return processed_count

    async def process_all_receivers(self) -> dict[str, int]:
        """
        Process all active receiver accounts.

        Returns:
            Dictionary mapping account emails to number of emails processed
        """
        # Get all active receiver accounts
        result = await self.session.execute(
            select(Account).where(
                Account.type == AccountType.RECEIVER,
                Account.status == AccountStatus.ACTIVE,
            )
        )
        receivers = result.scalars().all()

        logger.info(f"Processing {len(receivers)} receiver accounts")

        results = {}
        for receiver in receivers:
            count = await self.process_receiver_account(receiver)
            results[receiver.email] = count

        return results

    async def _should_respond(self, email_data: dict) -> bool:
        """
        Determine if we should respond to this email.

        Args:
            email_data: Email data dictionary

        Returns:
            True if should respond, False otherwise
        """
        # Check if this is a warmup email (from our sender accounts)
        sender_email = email_data.get("from", "")
        logger.debug(f"Checking if should respond to email from: {sender_email}")

        # Extract email address from "Name <email>" format
        if "<" in sender_email:
            sender_email = sender_email.split("<")[1].split(">")[0]

        sender_email = sender_email.strip().lower()
        logger.debug(f"Extracted sender email: {sender_email}")

        # Check if sender is one of our warmup accounts (case-insensitive)
        result = await self.session.execute(
            select(Account).where(
                func.lower(Account.email) == sender_email,
                Account.type == AccountType.SENDER,
            )
        )
        sender_account = result.scalar_one_or_none()

        # Only respond to emails from our warmup sender accounts
        if sender_account:
            # Respond to 80-90% of emails to simulate human behavior
            should_respond = random.random() < 0.85
            logger.info(f"Email from warmup sender {sender_email}, responding: {should_respond}")
            return should_respond
        else:
            logger.debug(f"Email from {sender_email} is not from a warmup sender account, skipping")

        return False

    async def _respond_to_email(self, account: Account, email_data: dict) -> bool:
        """
        Generate and send response to an email.

        Args:
            account: Receiver account
            email_data: Email data dictionary

        Returns:
            True if response sent successfully, False otherwise
        """
        try:
            # Extract sender
            sender_email = email_data.get("from", "")
            if "<" in sender_email:
                sender_email = sender_email.split("<")[1].split(">")[0]

            # Get sender account
            result = await self.session.execute(
                select(Account).where(Account.email == sender_email)
            )
            sender_account = result.scalar_one_or_none()

            if not sender_account:
                logger.warning(f"Sender account not found: {sender_email}")
                return False

            # Find the campaign this email belongs to
            # Get all campaigns and filter in Python since JSON operator is tricky
            result = await self.session.execute(
                select(Campaign).where(Campaign.status == "active").order_by(Campaign.created_at.desc())
            )
            campaigns = result.scalars().all()

            # Find matching campaign
            campaign = None
            for c in campaigns:
                if sender_account.id in c.sender_account_ids and account.id in c.receiver_account_ids:
                    campaign = c
                    break

            # Use campaign language if available, default to "en"
            language = campaign.language if campaign else "en"

            # Generate reply content with receiver's name and campaign language
            original_subject = email_data.get("subject", "")
            original_body = email_data.get("body", "")

            reply_content = await self.ai_generator.generate_email(
                is_reply=True,
                previous_content=f"Subject: {original_subject}\n\n{original_body}",
                sender_name=account.full_name,
                language=language,  # type: ignore
            )

            # Create temporary message for message_id
            temp_reply = EmailMessage(
                sender=account.email,
                receiver=sender_email,
                subject=reply_content.subject if not original_subject.startswith("Re:") else original_subject,
                body=reply_content.body,
                in_reply_to=email_data.get("message_id"),
                references=email_data.get("references") or email_data.get("message_id"),
            )

            # Create email record FIRST to get ID for tracking
            email_record = Email(
                sender_id=account.id,
                receiver_id=sender_account.id,
                subject=reply_content.subject,
                body=reply_content.body,
                message_id=temp_reply.message_id,
                in_reply_to=email_data.get("message_id"),
                thread_id=email_data.get("message_id"),
                status=EmailStatus.PENDING,
                is_warmup=True,
                ai_generated=True,
                ai_prompt=reply_content.prompt,
                ai_model=reply_content.model,
            )
            self.session.add(email_record)
            await self.session.flush()  # Get ID without committing

            # Build tracking URL with signed token
            tracking_url = generate_tracking_url(settings.api_base_url, email_record.id)

            # Create reply message with tracking pixel
            reply_message = EmailMessage(
                sender=account.email,
                receiver=sender_email,
                subject=reply_content.subject if not original_subject.startswith("Re:") else original_subject,
                body=reply_content.body,
                in_reply_to=email_data.get("message_id"),
                references=email_data.get("references") or email_data.get("message_id"),
                tracking_url=tracking_url,
            )

            # Send reply (decrypt password for SMTP)
            success = await self.email_service.send_email(
                smtp_host=account.smtp_host,
                smtp_port=account.smtp_port,
                username=account.email,
                password=account.get_password(),
                message=reply_message,
                use_tls=account.smtp_use_tls,
            )

            if success:
                # Update status to SENT
                email_record.status = EmailStatus.SENT
                email_record.sent_at = datetime.now(timezone.utc)

                logger.debug(f"Reply {email_record.id} sent with tracking URL: {tracking_url}")

                # Update original email status
                result = await self.session.execute(
                    select(Email).where(Email.message_id == email_data.get("message_id"))
                )
                original_email = result.scalar_one_or_none()
                if original_email:
                    original_email.status = EmailStatus.REPLIED
                    original_email.replied_at = datetime.now(timezone.utc)

                await self.session.commit()

                logger.info(f"Sent reply from {account.email} to {sender_email}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to respond to email: {e}")
            return False

    async def _simulate_human_delay(self) -> None:
        """Simulate human response delay (configurable range)."""
        min_hours = settings.response_delay_min_hours
        max_hours = settings.response_delay_max_hours

        # In practice, we won't actually delay in production
        # This is just for logging/tracking purposes
        delay_hours = random.uniform(min_hours, max_hours)
        logger.info(f"Simulating human delay: {delay_hours:.1f} hours")

        # For development/testing, you might want to use a shorter delay
        # await asyncio.sleep(delay_seconds)
