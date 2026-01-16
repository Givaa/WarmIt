"""Email warming scheduler with progressive volume increase."""

import logging
import random
from datetime import datetime, date, timedelta, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from warmit.models.account import Account, AccountStatus, AccountType
from warmit.models.campaign import Campaign, CampaignStatus
from warmit.models.email import Email, EmailStatus
from warmit.models.metric import Metric
from warmit.services.email_service import EmailService, EmailMessage
from warmit.services.ai_generator import AIGenerator
from warmit.services.domain_checker import DomainChecker
from warmit.config import settings


logger = logging.getLogger(__name__)


class WarmupScheduler:
    """Scheduler for progressive email warming campaigns."""

    def __init__(self, session: AsyncSession):
        """
        Initialize warmup scheduler.

        Args:
            session: Database session
        """
        self.session = session
        self.email_service = EmailService()
        self.ai_generator = AIGenerator()

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

        Returns:
            Created campaign
        """
        # Validate accounts exist
        result = await self.session.execute(
            select(Account).where(Account.id.in_(sender_account_ids))
        )
        senders = result.scalars().all()

        result = await self.session.execute(
            select(Account).where(Account.id.in_(receiver_account_ids))
        )
        receivers = result.scalars().all()

        if len(senders) != len(sender_account_ids):
            raise ValueError("Some sender accounts not found")
        if len(receivers) != len(receiver_account_ids):
            raise ValueError("Some receiver accounts not found")

        # Check domain ages and determine duration
        if not duration_weeks:
            duration_weeks = await self._calculate_optimal_duration(senders)

        # Create campaign
        campaign = Campaign(
            name=name,
            sender_account_ids=sender_account_ids,
            receiver_account_ids=receiver_account_ids,
            status=CampaignStatus.ACTIVE,
            start_date=datetime.now(timezone.utc),
            duration_weeks=duration_weeks,
            current_week=1,
            language=language,
        )
        self.session.add(campaign)

        # Update sender accounts
        for sender in senders:
            if not sender.warmup_start_date:
                sender.warmup_start_date = datetime.now(timezone.utc)

        # Set initial next_send_time to a random time today
        campaign.next_send_time = self._calculate_random_send_time()

        await self.session.commit()
        await self.session.refresh(campaign)

        logger.info(
            f"Started campaign '{name}' with {len(senders)} senders "
            f"and {len(receivers)} receivers for {duration_weeks} weeks"
        )
        logger.info(f"Next send scheduled for: {campaign.next_send_time}")

        return campaign

    async def process_campaign(self, campaign: Campaign, force: bool = False) -> int:
        """
        Process a campaign for the current day.

        Args:
            campaign: Campaign to process
            force: If True, bypass the next_send_time check (for manual "Send Now")

        Returns:
            Number of emails sent
        """
        if campaign.status != CampaignStatus.ACTIVE:
            logger.info(f"Campaign {campaign.id} is not active")
            return 0

        # Check if it's time to send (only if next_send_time is set and not forced)
        if not force:
            now = datetime.now(timezone.utc)
            if campaign.next_send_time and campaign.next_send_time > now:
                logger.info(
                    f"Campaign {campaign.id}: Not yet time to send. "
                    f"Next send at {campaign.next_send_time}"
                )
                return 0
        else:
            logger.info(f"Campaign {campaign.id}: Manual send (forced), bypassing schedule")

        # Update current week
        weeks_elapsed = (
            datetime.now(timezone.utc) - campaign.start_date
        ).days // 7 + 1
        campaign.current_week = min(weeks_elapsed, campaign.duration_weeks)

        # Check if campaign is complete
        if campaign.current_week > campaign.duration_weeks:
            campaign.status = CampaignStatus.COMPLETED
            campaign.end_date = datetime.now(timezone.utc)
            await self.session.commit()
            logger.info(f"Campaign {campaign.id} completed")
            return 0

        # Calculate target emails for today
        target_today = await self._calculate_daily_target(campaign)
        campaign.target_emails_today = target_today

        # Check if we've already sent enough today
        if campaign.emails_sent_today >= target_today:
            # Schedule next send for tomorrow
            campaign.next_send_time = self._calculate_random_send_time(completed_today=True)
            await self.session.commit()
            logger.info(
                f"Campaign {campaign.id} already sent {campaign.emails_sent_today}/{target_today} today. "
                f"Next send scheduled for {campaign.next_send_time}"
            )
            return 0

        # Calculate how many emails to send in this batch
        # Send in small batches distributed throughout the day (max 3 per batch)
        emails_remaining = target_today - campaign.emails_sent_today
        batch_size = min(3, emails_remaining)

        # Send emails
        emails_sent = await self._send_warmup_emails(campaign, batch_size)

        # Update campaign stats
        campaign.emails_sent_today += emails_sent
        campaign.total_emails_sent += emails_sent
        campaign.last_email_sent_at = datetime.now(timezone.utc)

        # Calculate next send time
        completed_for_today = campaign.emails_sent_today >= target_today
        campaign.next_send_time = self._calculate_random_send_time(completed_today=completed_for_today)

        await self.session.commit()

        logger.info(
            f"Campaign {campaign.id}: Sent {emails_sent} emails "
            f"({campaign.emails_sent_today}/{target_today} today). "
            f"Next send scheduled for {campaign.next_send_time}"
        )

        return emails_sent

    async def process_all_campaigns(self) -> dict[int, int]:
        """
        Process all active campaigns.

        Returns:
            Dictionary mapping campaign IDs to emails sent
        """
        result = await self.session.execute(
            select(Campaign).where(Campaign.status == CampaignStatus.ACTIVE)
        )
        campaigns = result.scalars().all()

        logger.info(f"Processing {len(campaigns)} active campaigns")

        results = {}
        for campaign in campaigns:
            emails_sent = await self.process_campaign(campaign)
            results[campaign.id] = emails_sent

        return results

    async def reset_daily_counters(self) -> None:
        """Reset daily email counters for all campaigns."""
        result = await self.session.execute(
            select(Campaign).where(Campaign.status == CampaignStatus.ACTIVE)
        )
        campaigns = result.scalars().all()

        for campaign in campaigns:
            campaign.emails_sent_today = 0

        await self.session.commit()
        logger.info("Reset daily counters for all campaigns")

    async def _calculate_optimal_duration(self, senders: list[Account]) -> int:
        """Calculate optimal warmup duration based on sender domain ages."""
        max_duration = settings.warmup_duration_weeks

        for sender in senders:
            # Check domain age if not already checked
            if not sender.domain_age_days:
                domain_info = await DomainChecker.check_domain(sender.email)
                sender.domain = domain_info.domain
                sender.domain_age_days = domain_info.age_days
                sender.domain_checked_at = datetime.now(timezone.utc)

                # Use recommended duration
                recommended = domain_info.warmup_weeks_recommended
                max_duration = max(max_duration, recommended)

        await self.session.commit()
        return max_duration

    async def _calculate_daily_target(self, campaign: Campaign) -> int:
        """
        Calculate daily email target based on current week and domain ages.

        Takes into account the youngest domain to avoid overloading new domains.

        Args:
            campaign: Campaign to calculate for

        Returns:
            Number of emails to send today
        """
        week = campaign.current_week

        # Progressive schedule based on best practices
        if week == 1:
            base_target = 5
        elif week == 2:
            base_target = 10
        elif week == 3:
            base_target = 15
        elif week == 4:
            base_target = 25
        elif week == 5:
            base_target = 35
        elif week >= 6:
            base_target = 50
        else:
            base_target = 5

        # Get sender accounts to check domain ages
        result = await self.session.execute(
            select(Account).where(Account.id.in_(campaign.sender_account_ids))
        )
        senders = list(result.scalars().all())

        # Find the youngest domain (most conservative limit)
        min_age_days = None
        for sender in senders:
            if sender.domain_age_days is not None:
                if min_age_days is None or sender.domain_age_days < min_age_days:
                    min_age_days = sender.domain_age_days

        # Apply domain age constraint for week 1 only (most critical period)
        if week == 1 and min_age_days is not None:
            # Get recommended initial limit based on youngest domain
            if min_age_days < 30:
                # Very new domain - be extra conservative
                domain_limit = 3
            elif min_age_days < 90:
                # New domain - conservative
                domain_limit = 5
            elif min_age_days < 180:
                # Moderately new - moderate
                domain_limit = 10
            else:
                # Established domain - normal progression
                domain_limit = base_target

            # Use the more conservative limit
            base_target = min(base_target, domain_limit)
            logger.info(
                f"Campaign {campaign.id}: Youngest domain is {min_age_days} days old, "
                f"limiting week 1 to {base_target} emails/sender"
            )

        # Scale by number of sender accounts
        num_senders = len(campaign.sender_account_ids)
        total_target = base_target * num_senders

        # Cap at configured maximum
        return min(total_target, settings.max_emails_per_day * num_senders)

    async def _send_warmup_emails(self, campaign: Campaign, count: int) -> int:
        """
        Send warmup emails for a campaign.

        Args:
            campaign: Campaign to send for
            count: Number of emails to send

        Returns:
            Number of emails successfully sent
        """
        # Get sender and receiver accounts
        result = await self.session.execute(
            select(Account).where(Account.id.in_(campaign.sender_account_ids))
        )
        senders = list(result.scalars().all())

        result = await self.session.execute(
            select(Account).where(Account.id.in_(campaign.receiver_account_ids))
        )
        receivers = list(result.scalars().all())

        if not senders or not receivers:
            logger.error("No sender or receiver accounts found")
            return 0

        logger.info(f"Campaign {campaign.id}: {len(senders)} senders, {len(receivers)} receivers, target count={count}")

        sent_count = 0

        # Distribute emails across senders
        emails_per_sender = count // len(senders)
        remainder = count % len(senders)
        logger.info(f"Campaign {campaign.id}: emails_per_sender={emails_per_sender}, remainder={remainder}")

        # Create a list of (sender, count) tuples
        sender_allocations = []
        for i, sender in enumerate(senders):
            # Calculate how many to send for this sender
            sender_count = emails_per_sender
            if i < remainder:
                sender_count += 1

            logger.info(f"Campaign {campaign.id}: Sender {i} ({sender.email}): allocated {sender_count} emails, bounce_rate={sender.bounce_rate:.2%}")

            # Check bounce rate
            if sender.bounce_rate > settings.max_bounce_rate:
                logger.warning(
                    f"Sender {sender.email} has high bounce rate ({sender.bounce_rate:.2%}), skipping"
                )
                if settings.auto_pause_on_high_bounce:
                    sender.status = AccountStatus.PAUSED
                    await self.session.commit()
                continue

            # Add to allocations
            for _ in range(sender_count):
                sender_allocations.append(sender)

        # Randomize the order to avoid same sender sending consecutively
        random.shuffle(sender_allocations)

        logger.info(f"Campaign {campaign.id}: Will send {len(sender_allocations)} emails in randomized order")

        # Send emails in randomized order
        for idx, sender in enumerate(sender_allocations, 1):
            logger.info(f"Campaign {campaign.id}: Processing email {idx}/{len(sender_allocations)}")
            # Pick random receiver
            receiver = random.choice(receivers)

            # Generate email content with sender's name and campaign language
            content = await self.ai_generator.generate_email(
                sender_name=sender.full_name,
                language=campaign.language  # type: ignore
            )

            # Create temporary message for message_id
            temp_message = EmailMessage(
                sender=sender.email,
                receiver=receiver.email,
                subject=content.subject,
                body=content.body,
            )

            # Create email record FIRST to get ID for tracking
            email_record = Email(
                sender_id=sender.id,
                receiver_id=receiver.id,
                campaign_id=campaign.id,
                subject=content.subject,
                body=content.body,
                message_id=temp_message.message_id,
                status=EmailStatus.PENDING,
                is_warmup=True,
                ai_generated=True,
                ai_prompt=content.prompt,
                ai_model=content.model,
            )
            self.session.add(email_record)
            await self.session.flush()  # Get ID without committing

            # Build tracking URL
            tracking_url = f"{settings.api_base_url}/track/open/{email_record.id}"

            # Create message with tracking pixel
            message = EmailMessage(
                sender=sender.email,
                receiver=receiver.email,
                subject=content.subject,
                body=content.body,
                message_id=temp_message.message_id,
                tracking_url=tracking_url,
            )

            # Send email (decrypt password for SMTP)
            success = await self.email_service.send_email(
                smtp_host=sender.smtp_host,
                smtp_port=sender.smtp_port,
                username=sender.email,
                password=sender.get_password(),
                message=message,
                use_tls=sender.smtp_use_tls,
            )

            if success:
                # Update status to SENT
                email_record.status = EmailStatus.SENT
                email_record.sent_at = datetime.now(timezone.utc)

                # Update sender stats
                sender.total_sent += 1
                sent_count += 1

                logger.debug(f"Email {email_record.id} sent with tracking URL: {tracking_url}")

                # Add delay between emails (human-like behavior)
                # Longer delays make the pattern less suspicious
                import asyncio
                # Production delays: 2-10 minutes between emails
                await asyncio.sleep(random.uniform(120, 600))  # 2-10 minutes

            else:
                # Mark as failed
                email_record.status = EmailStatus.BOUNCED
                sender.total_bounced += 1

        await self.session.commit()
        return sent_count

    async def update_metrics(self) -> None:
        """Update daily metrics for all accounts."""
        today = date.today()

        # Get all accounts
        result = await self.session.execute(select(Account))
        accounts = result.scalars().all()

        for account in accounts:
            # Get or create metric for today
            result = await self.session.execute(
                select(Metric).where(
                    Metric.account_id == account.id,
                    Metric.date == today,
                )
            )
            metric = result.scalar_one_or_none()

            if not metric:
                metric = Metric(account_id=account.id, date=today)
                self.session.add(metric)

            # Update counts from account
            metric.emails_sent = account.total_sent
            metric.emails_received = account.total_received
            metric.emails_opened = account.total_opened
            metric.emails_replied = account.total_replied
            metric.emails_bounced = account.total_bounced

            # Calculate rates
            metric.calculate_rates()

        await self.session.commit()
        logger.info(f"Updated metrics for {len(accounts)} accounts")

    def _calculate_random_send_time(self, completed_today: bool = False) -> datetime:
        """
        Calculate a random send time within business hours.

        Args:
            completed_today: If True, schedule for tomorrow. If False, try to schedule later today.

        Returns random time between 9 AM and 6 PM local time (converted to UTC).
        """
        now = datetime.now(timezone.utc)

        # Define business hours (9 AM to 6 PM)
        start_hour = 9
        end_hour = 18

        # If we've completed today's target, schedule for tomorrow
        if completed_today:
            # Schedule for tomorrow at a random time
            random_hour = random.randint(start_hour, end_hour - 1)
            random_minute = random.randint(0, 59)
            random_second = random.randint(0, 59)

            send_time = now.replace(
                hour=random_hour,
                minute=random_minute,
                second=random_second,
                microsecond=0
            )
            send_time += timedelta(days=1)
        else:
            # Try to schedule later today (at least 30 minutes from now, up to end of business hours)
            min_wait_minutes = 30
            latest_today = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
            earliest_next = now + timedelta(minutes=min_wait_minutes)

            # If we're past business hours or too close to end, schedule for tomorrow
            if earliest_next >= latest_today:
                random_hour = random.randint(start_hour, end_hour - 1)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)

                send_time = now.replace(
                    hour=random_hour,
                    minute=random_minute,
                    second=random_second,
                    microsecond=0
                )
                send_time += timedelta(days=1)
            else:
                # Schedule randomly between 30 minutes from now and end of business hours
                time_range_seconds = int((latest_today - earliest_next).total_seconds())
                random_offset_seconds = random.randint(0, time_range_seconds)
                send_time = earliest_next + timedelta(seconds=random_offset_seconds)

        return send_time

    def _calculate_random_reply_time(self, original_send_time: datetime) -> datetime:
        """
        Calculate a random reply time within same day as original email.

        Reply is scheduled 2-8 hours after the original email, but within the same day.
        """
        # Random delay between 2 and 8 hours
        min_delay_hours = 2
        max_delay_hours = 8

        delay_hours = random.uniform(min_delay_hours, max_delay_hours)
        reply_time = original_send_time + timedelta(hours=delay_hours)

        # Ensure reply is within the same day (before midnight)
        end_of_day = original_send_time.replace(hour=23, minute=59, second=59)
        if reply_time > end_of_day:
            # Schedule earlier in the day if would go past midnight
            reply_time = original_send_time + timedelta(
                hours=random.uniform(min_delay_hours, min(max_delay_hours, (end_of_day - original_send_time).seconds / 3600))
            )

        return reply_time
