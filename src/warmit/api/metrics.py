"""Metrics and statistics API endpoints."""

from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from warmit.database import get_session
from warmit.models.account import Account
from warmit.models.metric import Metric
from warmit.models.email import Email, EmailStatus


router = APIRouter()


# Pydantic schemas
class MetricResponse(BaseModel):
    """Schema for metric response."""

    date: date
    emails_sent: int
    emails_received: int
    emails_opened: int
    emails_replied: int
    emails_bounced: int
    open_rate: float
    reply_rate: float
    bounce_rate: float

    class Config:
        from_attributes = True


class AccountMetrics(BaseModel):
    """Schema for account metrics summary."""

    account_id: int
    email: str
    total_sent: int
    total_received: int
    total_opened: int
    total_replied: int
    total_bounced: int
    open_rate: float
    reply_rate: float
    bounce_rate: float
    current_daily_limit: int
    daily_metrics: list[MetricResponse]


class SystemMetrics(BaseModel):
    """Schema for system-wide metrics."""

    total_accounts: int
    active_accounts: int
    total_campaigns: int
    active_campaigns: int
    total_emails_sent: int
    total_emails_received: int
    emails_sent_today: int
    average_open_rate: float
    average_reply_rate: float
    average_bounce_rate: float


@router.get("/accounts/{account_id}", response_model=AccountMetrics)
async def get_account_metrics(
    account_id: int,
    days: int = 30,
    session: AsyncSession = Depends(get_session),
):
    """
    Get metrics for a specific account.

    Args:
        account_id: Account ID
        days: Number of days of history to include (default: 30)
    """
    # Get account
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Get daily metrics
    start_date = date.today() - timedelta(days=days)
    result = await session.execute(
        select(Metric)
        .where(Metric.account_id == account_id, Metric.date >= start_date)
        .order_by(Metric.date.desc())
    )
    daily_metrics = result.scalars().all()

    return AccountMetrics(
        account_id=account.id,
        email=account.email,
        total_sent=account.total_sent,
        total_received=account.total_received,
        total_opened=account.total_opened,
        total_replied=account.total_replied,
        total_bounced=account.total_bounced,
        open_rate=account.open_rate,
        reply_rate=account.reply_rate,
        bounce_rate=account.bounce_rate,
        current_daily_limit=account.current_daily_limit,
        daily_metrics=[
            MetricResponse(
                date=m.date,
                emails_sent=m.emails_sent,
                emails_received=m.emails_received,
                emails_opened=m.emails_opened,
                emails_replied=m.emails_replied,
                emails_bounced=m.emails_bounced,
                open_rate=m.open_rate,
                reply_rate=m.reply_rate,
                bounce_rate=m.bounce_rate,
            )
            for m in daily_metrics
        ],
    )


@router.get("/system", response_model=SystemMetrics)
async def get_system_metrics(
    session: AsyncSession = Depends(get_session),
):
    """
    Get system-wide metrics.

    Provides an overview of all accounts, campaigns, and email statistics.
    """
    from warmit.models.campaign import Campaign, CampaignStatus
    from warmit.models.account import AccountStatus

    # Count accounts
    result = await session.execute(select(func.count(Account.id)))
    total_accounts = result.scalar_one()

    result = await session.execute(
        select(func.count(Account.id)).where(Account.status == AccountStatus.ACTIVE)
    )
    active_accounts = result.scalar_one()

    # Count campaigns
    result = await session.execute(select(func.count(Campaign.id)))
    total_campaigns = result.scalar_one()

    result = await session.execute(
        select(func.count(Campaign.id)).where(Campaign.status == CampaignStatus.ACTIVE)
    )
    active_campaigns = result.scalar_one()

    # Email statistics
    result = await session.execute(select(func.sum(Account.total_sent)))
    total_sent = result.scalar_one() or 0

    result = await session.execute(select(func.sum(Account.total_received)))
    total_received = result.scalar_one() or 0

    # Today's emails
    today = date.today()
    result = await session.execute(
        select(func.count(Email.id)).where(
            func.date(Email.sent_at) == today,
            Email.status == EmailStatus.SENT,
        )
    )
    emails_sent_today = result.scalar_one()

    # Average rates - calculate from database columns, not @property methods
    # Open rate = total_opened / total_sent
    result = await session.execute(
        select(func.sum(Account.total_opened), func.sum(Account.total_sent))
    )
    row = result.one()
    total_opened = row[0] or 0
    total_sent_for_open = row[1] or 0
    avg_open_rate = total_opened / total_sent_for_open if total_sent_for_open > 0 else 0.0

    # Reply rate = total_replied / total_received
    result = await session.execute(
        select(func.sum(Account.total_replied), func.sum(Account.total_received))
    )
    row = result.one()
    total_replied = row[0] or 0
    total_received_for_reply = row[1] or 0
    avg_reply_rate = total_replied / total_received_for_reply if total_received_for_reply > 0 else 0.0

    # Bounce rate = total_bounced / total_sent
    result = await session.execute(
        select(func.sum(Account.total_bounced), func.sum(Account.total_sent))
    )
    row = result.one()
    total_bounced = row[0] or 0
    total_sent_for_bounce = row[1] or 0
    avg_bounce_rate = total_bounced / total_sent_for_bounce if total_sent_for_bounce > 0 else 0.0

    return SystemMetrics(
        total_accounts=total_accounts,
        active_accounts=active_accounts,
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        total_emails_sent=total_sent,
        total_emails_received=total_received,
        emails_sent_today=emails_sent_today,
        average_open_rate=float(avg_open_rate),
        average_reply_rate=float(avg_reply_rate),
        average_bounce_rate=float(avg_bounce_rate),
    )


@router.get("/daily", response_model=list[MetricResponse])
async def get_daily_metrics(
    days: int = 30,
    session: AsyncSession = Depends(get_session),
):
    """
    Get aggregated daily metrics across all accounts.

    Args:
        days: Number of days of history to include (default: 30)
    """
    start_date = date.today() - timedelta(days=days)

    result = await session.execute(
        select(
            Metric.date,
            func.sum(Metric.emails_sent).label("emails_sent"),
            func.sum(Metric.emails_received).label("emails_received"),
            func.sum(Metric.emails_opened).label("emails_opened"),
            func.sum(Metric.emails_replied).label("emails_replied"),
            func.sum(Metric.emails_bounced).label("emails_bounced"),
        )
        .where(Metric.date >= start_date)
        .group_by(Metric.date)
        .order_by(Metric.date.desc())
    )

    metrics = []
    for row in result:
        sent = row.emails_sent or 0
        received = row.emails_received or 0
        opened = row.emails_opened or 0
        replied = row.emails_replied or 0
        bounced = row.emails_bounced or 0

        metrics.append(
            MetricResponse(
                date=row.date,
                emails_sent=sent,
                emails_received=received,
                emails_opened=opened,
                emails_replied=replied,
                emails_bounced=bounced,
                open_rate=opened / sent if sent > 0 else 0.0,
                reply_rate=replied / received if received > 0 else 0.0,
                bounce_rate=bounced / sent if sent > 0 else 0.0,
            )
        )

    return metrics
