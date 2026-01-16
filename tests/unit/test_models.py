"""Unit tests for database models."""

import pytest
from datetime import datetime, timezone

from warmit.models.account import Account, AccountType, AccountStatus
from warmit.models.campaign import Campaign, CampaignStatus
from warmit.models.email import Email, EmailStatus


class TestAccountModel:
    """Test Account model."""

    @pytest.mark.asyncio
    async def test_create_account(self, db_session):
        """Test creating an account."""
        account = Account(
            email="test@example.com",
            type=AccountType.SENDER,
            status=AccountStatus.ACTIVE,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_use_tls=True,
            imap_host="imap.example.com",
            imap_port=993,
            imap_use_ssl=True,
            password="test_password",
        )
        db_session.add(account)
        await db_session.commit()

        assert account.id is not None
        assert account.email == "test@example.com"
        assert account.type == AccountType.SENDER
        assert account.status == AccountStatus.ACTIVE

    def test_full_name_with_names(self, sender_account):
        """Test full_name property with first and last name."""
        assert sender_account.full_name == "John Doe"

    @pytest.mark.asyncio
    async def test_full_name_from_email(self, db_session):
        """Test full_name property fallback to email."""
        account = Account(
            email="john.doe@example.com",
            type=AccountType.SENDER,
            status=AccountStatus.ACTIVE,
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_use_tls=True,
            imap_host="imap.example.com",
            imap_port=993,
            imap_use_ssl=True,
            password="test",
        )
        db_session.add(account)
        await db_session.commit()

        assert account.full_name == "John Doe"

    def test_bounce_rate_calculation(self, sender_account):
        """Test bounce rate calculation."""
        sender_account.total_sent = 100
        sender_account.total_bounced = 5

        assert sender_account.bounce_rate == 0.05

    def test_bounce_rate_zero_sent(self, sender_account):
        """Test bounce rate when no emails sent."""
        sender_account.total_sent = 0
        sender_account.total_bounced = 0

        assert sender_account.bounce_rate == 0.0

    def test_open_rate_calculation(self, sender_account):
        """Test open rate calculation."""
        sender_account.total_sent = 100
        sender_account.total_opened = 85

        assert sender_account.open_rate == 0.85

    def test_reply_rate_calculation(self, receiver_account):
        """Test reply rate calculation."""
        receiver_account.total_received = 50
        receiver_account.total_replied = 40

        assert receiver_account.reply_rate == 0.8


class TestCampaignModel:
    """Test Campaign model."""

    @pytest.mark.asyncio
    async def test_create_campaign(self, db_session):
        """Test creating a campaign."""
        campaign = Campaign(
            name="Test Campaign",
            sender_account_ids=[1, 2],
            receiver_account_ids=[10, 11, 12],
            status=CampaignStatus.ACTIVE,
            duration_weeks=6,
            language="en",
        )
        db_session.add(campaign)
        await db_session.commit()

        assert campaign.id is not None
        assert campaign.name == "Test Campaign"
        assert len(campaign.sender_account_ids) == 2
        assert len(campaign.receiver_account_ids) == 3

    def test_open_rate_calculation(self, campaign):
        """Test campaign open rate calculation."""
        campaign.total_emails_sent = 100
        campaign.total_emails_opened = 90

        assert campaign.open_rate == 0.9

    def test_reply_rate_calculation(self, campaign):
        """Test campaign reply rate calculation."""
        campaign.total_emails_sent = 100
        campaign.total_emails_replied = 20

        assert campaign.reply_rate == 0.2

    def test_bounce_rate_calculation(self, campaign):
        """Test campaign bounce rate calculation."""
        campaign.total_emails_sent = 100
        campaign.total_emails_bounced = 3

        assert campaign.bounce_rate == 0.03

    def test_progress_percentage(self, campaign):
        """Test campaign progress calculation."""
        campaign.duration_weeks = 6
        campaign.current_week = 3

        assert campaign.progress_percentage == 50.0


class TestEmailModel:
    """Test Email model."""

    @pytest.mark.asyncio
    async def test_create_email(
        self, db_session, sender_account, receiver_account, campaign
    ):
        """Test creating an email."""
        email = Email(
            sender_id=sender_account.id,
            receiver_id=receiver_account.id,
            campaign_id=campaign.id,
            message_id="<unique@example.com>",
            subject="Test Subject",
            body="Test body content",
            status=EmailStatus.SENT,
            is_warmup=True,
        )
        db_session.add(email)
        await db_session.commit()

        assert email.id is not None
        assert email.sender_id == sender_account.id
        assert email.receiver_id == receiver_account.id
        assert email.status == EmailStatus.SENT

    @pytest.mark.asyncio
    async def test_email_relationships(self, email, sender_account, receiver_account):
        """Test email relationships with accounts."""
        assert email.sender.email == sender_account.email
        assert email.receiver.email == receiver_account.email

    def test_email_status_enum(self):
        """Test email status enum values."""
        assert EmailStatus.PENDING == "pending"
        assert EmailStatus.SENT == "sent"
        assert EmailStatus.BOUNCED == "bounced"
