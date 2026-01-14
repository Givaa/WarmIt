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
        )
        self.session.add(campaign)

        # Update sender accounts
        for sender in senders:
            if not sender.warmup_start_date:
                sender.warmup_start_date = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(campaign)

        logger.info(
            f"Started campaign '{name}' with {len(senders)} senders "
            f"and {len(receivers)} receivers for {duration_weeks} weeks"
        )

        return campaign

    async def process_campaign(self, campaign: Campaign) -> int:
        """
        Process a campaign for the current day.

        Args:
            campaign: Campaign to process

        Returns:
            Number of emails sent
        """
        if campaign.status != CampaignStatus.ACTIVE:
            logger.info(f"Campaign {campaign.id} is not active")
            return 0

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
            logger.info(
                f"Campaign {campaign.id} already sent {campaign.emails_sent_today}/{target_today} today"
            )
            return 0

        # Send emails
        emails_to_send = target_today - campaign.emails_sent_today
        emails_sent = await self._send_warmup_emails(campaign, emails_to_send)

        # Update campaign stats
        campaign.emails_sent_today += emails_sent
        campaign.total_emails_sent += emails_sent
        campaign.last_email_sent_at = datetime.now(timezone.utc)

        await self.session.commit()

        logger.info(
            f"Campaign {campaign.id}: Sent {emails_sent} emails "
            f"({campaign.emails_sent_today}/{target_today} today)"
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
        Calculate daily email target based on current week.

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

        sent_count = 0

        # Distribute emails across senders
        emails_per_sender = count // len(senders)
        remainder = count % len(senders)

        for i, sender in enumerate(senders):
            # Calculate how many to send for this sender
            sender_count = emails_per_sender
            if i < remainder:
                sender_count += 1

            # Check bounce rate
            if sender.bounce_rate > settings.max_bounce_rate:
                logger.warning(
                    f"Sender {sender.email} has high bounce rate ({sender.bounce_rate:.2%}), skipping"
                )
                if settings.auto_pause_on_high_bounce:
                    sender.status = AccountStatus.PAUSED
                    await self.session.commit()
                continue

            # Send emails
            for _ in range(sender_count):
                # Pick random receiver
                receiver = random.choice(receivers)

                # Generate email content
                content = await self.ai_generator.generate_email()

                # Create message
                message = EmailMessage(
                    sender=sender.email,
                    receiver=receiver.email,
                    subject=content.subject,
                    body=content.body,
                )

                # Send email
                success = await self.email_service.send_email(
                    smtp_host=sender.smtp_host,
                    smtp_port=sender.smtp_port,
                    username=sender.email,
                    password=sender.password,
                    message=message,
                    use_tls=sender.smtp_use_tls,
                )

                if success:
                    # Record in database
                    email_record = Email(
                        sender_id=sender.id,
                        receiver_id=receiver.id,
                        campaign_id=campaign.id,
                        subject=content.subject,
                        body=content.body,
                        message_id=message.message_id,
                        status=EmailStatus.SENT,
                        is_warmup=True,
                        ai_generated=True,
                        ai_prompt=content.prompt,
                        ai_model=content.model,
                        sent_at=datetime.now(timezone.utc),
                    )
                    self.session.add(email_record)

                    # Update sender stats
                    sender.total_sent += 1
                    sent_count += 1

                    # Add small delay between emails (human-like behavior)
                    import asyncio
                    await asyncio.sleep(random.uniform(30, 120))  # 30s - 2min

                else:
                    # Record failure
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
