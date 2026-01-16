"""Pytest configuration and fixtures for WarmIt tests."""

import asyncio
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from warmit.models.base import Base
from warmit.models.account import Account, AccountType, AccountStatus
from warmit.models.campaign import Campaign, CampaignStatus
from warmit.models.email import Email, EmailStatus


# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Database fixtures
@pytest.fixture(scope="function")
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=NullPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


# Model fixtures
@pytest.fixture
async def sender_account(db_session: AsyncSession) -> Account:
    """Create test sender account."""
    account = Account(
        email="sender@example.com",
        first_name="John",
        last_name="Doe",
        type=AccountType.SENDER,
        status=AccountStatus.ACTIVE,
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_use_tls=True,
        imap_host="imap.example.com",
        imap_port=993,
        imap_use_ssl=True,
        password="encrypted_password_here",
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def receiver_account(db_session: AsyncSession) -> Account:
    """Create test receiver account."""
    account = Account(
        email="receiver@example.com",
        first_name="Jane",
        last_name="Smith",
        type=AccountType.RECEIVER,
        status=AccountStatus.ACTIVE,
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_use_tls=True,
        imap_host="imap.example.com",
        imap_port=993,
        imap_use_ssl=True,
        password="encrypted_password_here",
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def campaign(
    db_session: AsyncSession,
    sender_account: Account,
    receiver_account: Account,
) -> Campaign:
    """Create test campaign."""
    campaign = Campaign(
        name="Test Campaign",
        sender_account_ids=[sender_account.id],
        receiver_account_ids=[receiver_account.id],
        status=CampaignStatus.ACTIVE,
        duration_weeks=6,
        current_week=1,
        language="en",
    )
    db_session.add(campaign)
    await db_session.commit()
    await db_session.refresh(campaign)
    return campaign


@pytest.fixture
async def email(
    db_session: AsyncSession,
    sender_account: Account,
    receiver_account: Account,
    campaign: Campaign,
) -> Email:
    """Create test email."""
    email = Email(
        sender_id=sender_account.id,
        receiver_id=receiver_account.id,
        campaign_id=campaign.id,
        message_id="<test@example.com>",
        subject="Test Email",
        body="This is a test email.",
        status=EmailStatus.SENT,
        is_warmup=True,
    )
    db_session.add(email)
    await db_session.commit()
    await db_session.refresh(email)
    return email
