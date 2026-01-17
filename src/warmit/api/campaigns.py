"""Campaign management API endpoints."""

from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from warmit.database import get_session
from warmit.models.campaign import Campaign, CampaignStatus
from warmit.models.account import Account
from warmit.models.email import Email, EmailStatus
from warmit.services.scheduler import WarmupScheduler


router = APIRouter()


async def sync_campaign_stats(session: AsyncSession, campaign: Campaign) -> Campaign:
    """
    Synchronize campaign statistics from the Email table.

    This ensures stats are always accurate even if counters get out of sync.
    """
    # Count total emails sent for this campaign
    result = await session.execute(
        select(func.count(Email.id))
        .where(Email.campaign_id == campaign.id)
        .where(Email.status == EmailStatus.SENT)
    )
    campaign.total_emails_sent = result.scalar() or 0

    # Count opened emails
    result = await session.execute(
        select(func.count(Email.id))
        .where(Email.campaign_id == campaign.id)
        .where(Email.opened_at.isnot(None))
    )
    campaign.total_emails_opened = result.scalar() or 0

    # Count replied emails
    result = await session.execute(
        select(func.count(Email.id))
        .where(Email.campaign_id == campaign.id)
        .where(Email.replied_at.isnot(None))
    )
    campaign.total_emails_replied = result.scalar() or 0

    # Count bounced emails
    result = await session.execute(
        select(func.count(Email.id))
        .where(Email.campaign_id == campaign.id)
        .where(Email.status == EmailStatus.BOUNCED)
    )
    campaign.total_emails_bounced = result.scalar() or 0

    # Count emails sent today
    today = date.today()
    result = await session.execute(
        select(func.count(Email.id))
        .where(Email.campaign_id == campaign.id)
        .where(Email.status == EmailStatus.SENT)
        .where(func.date(Email.sent_at) == today)
    )
    campaign.emails_sent_today = result.scalar() or 0

    return campaign


# Pydantic schemas
class CampaignCreate(BaseModel):
    """Schema for creating a campaign."""

    name: str
    sender_account_ids: list[int]
    receiver_account_ids: list[int]
    duration_weeks: Optional[int] = None
    language: str = "en"  # Language for email generation ("en" or "it")


class CampaignResponse(BaseModel):
    """Schema for campaign response."""

    id: int
    name: str
    sender_account_ids: list[int]
    receiver_account_ids: list[int]
    status: CampaignStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    duration_weeks: int
    current_week: int
    emails_sent_today: int
    target_emails_today: int
    total_emails_sent: int
    total_emails_opened: int
    total_emails_replied: int
    total_emails_bounced: int
    open_rate: float
    reply_rate: float
    bounce_rate: float
    progress_percentage: float
    language: str
    next_send_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignStatusUpdate(BaseModel):
    """Schema for updating campaign status."""

    status: CampaignStatus


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    campaign_data: CampaignCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create and start a new warming campaign.

    This endpoint creates a warming campaign that progressively increases email volume
    based on domain age and best practices.
    """
    if not campaign_data.sender_account_ids:
        raise HTTPException(status_code=400, detail="At least one sender account required")

    if not campaign_data.receiver_account_ids:
        raise HTTPException(status_code=400, detail="At least one receiver account required")

    scheduler = WarmupScheduler(session)

    try:
        campaign = await scheduler.start_campaign(
            name=campaign_data.name,
            sender_account_ids=campaign_data.sender_account_ids,
            receiver_account_ids=campaign_data.receiver_account_ids,
            duration_weeks=campaign_data.duration_weeks,
            language=campaign_data.language,
        )
        return campaign

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[CampaignResponse])
async def list_campaigns(
    status: Optional[CampaignStatus] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    List all campaigns.

    Optional filter:
    - status: Filter by campaign status (pending/active/paused/completed/failed)
    """
    query = select(Campaign)

    if status:
        query = query.where(Campaign.status == status)

    result = await session.execute(query)
    campaigns = result.scalars().all()

    # Sync stats from Email table to ensure accuracy
    for campaign in campaigns:
        await sync_campaign_stats(session, campaign)

    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a specific campaign by ID."""
    result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Sync stats from Email table to ensure accuracy
    await sync_campaign_stats(session, campaign)

    return campaign


@router.patch("/{campaign_id}/status", response_model=CampaignResponse)
async def update_campaign_status(
    campaign_id: int,
    status_update: CampaignStatusUpdate,
    session: AsyncSession = Depends(get_session),
):
    """
    Update campaign status.

    Allowed transitions:
    - ACTIVE -> PAUSED
    - PAUSED -> ACTIVE
    - Any -> COMPLETED (manual completion)
    """
    result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Validate status transition
    if campaign.status == CampaignStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot modify completed campaign")

    campaign.status = status_update.status

    if status_update.status == CampaignStatus.COMPLETED:
        campaign.end_date = datetime.now()

    await session.commit()
    await session.refresh(campaign)

    return campaign


@router.post("/{campaign_id}/process")
async def process_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """
    Manually trigger campaign processing for the current day.

    This bypasses the scheduled send time and sends immediately.
    Useful for testing. In production, scheduled sends are triggered by a cron job.
    """
    result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    scheduler = WarmupScheduler(session)
    # Use force=True to bypass next_send_time check for manual sends
    emails_sent = await scheduler.process_campaign(campaign, force=True)

    return {
        "campaign_id": campaign_id,
        "emails_sent": emails_sent,
        "emails_sent_today": campaign.emails_sent_today,
        "target_emails_today": campaign.target_emails_today,
    }


@router.get("/{campaign_id}/sender-stats")
async def get_campaign_sender_stats(
    campaign_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get detailed statistics for each sender in a campaign.

    Returns per-sender metrics including emails sent, open rates, bounce rates, etc.
    """
    from sqlalchemy import func
    from warmit.models.email import Email, EmailStatus

    # Get campaign
    result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get sender accounts
    result = await session.execute(
        select(Account).where(Account.id.in_(campaign.sender_account_ids))
    )
    senders = result.scalars().all()

    sender_stats = []

    for sender in senders:
        # Count emails sent by this sender in this campaign
        emails_sent_result = await session.execute(
            select(func.count(Email.id))
            .where(Email.sender_id == sender.id)
            .where(Email.campaign_id == campaign_id)
        )
        emails_sent = emails_sent_result.scalar() or 0

        # Count opened emails
        emails_opened_result = await session.execute(
            select(func.count(Email.id))
            .where(Email.sender_id == sender.id)
            .where(Email.campaign_id == campaign_id)
            .where(Email.opened_at.isnot(None))
        )
        emails_opened = emails_opened_result.scalar() or 0

        # Count replied emails
        emails_replied_result = await session.execute(
            select(func.count(Email.id))
            .where(Email.sender_id == sender.id)
            .where(Email.campaign_id == campaign_id)
            .where(Email.replied_at.isnot(None))
        )
        emails_replied = emails_replied_result.scalar() or 0

        # Count bounced emails
        emails_bounced_result = await session.execute(
            select(func.count(Email.id))
            .where(Email.sender_id == sender.id)
            .where(Email.campaign_id == campaign_id)
            .where(Email.status == EmailStatus.BOUNCED)
        )
        emails_bounced = emails_bounced_result.scalar() or 0

        # Calculate rates
        open_rate = (emails_opened / emails_sent * 100) if emails_sent > 0 else 0
        reply_rate = (emails_replied / emails_sent * 100) if emails_sent > 0 else 0
        bounce_rate = (emails_bounced / emails_sent * 100) if emails_sent > 0 else 0

        sender_stats.append({
            "sender_id": sender.id,
            "sender_email": sender.email,
            "sender_name": sender.full_name,
            "domain": sender.domain,
            "domain_age_days": sender.domain_age_days,
            "status": sender.status.value,
            "emails_sent": emails_sent,
            "emails_opened": emails_opened,
            "emails_replied": emails_replied,
            "emails_bounced": emails_bounced,
            "open_rate": round(open_rate, 2),
            "reply_rate": round(reply_rate, 2),
            "bounce_rate": round(bounce_rate, 2),
            "total_sent_overall": sender.total_sent,
            "bounce_rate_overall": round(sender.bounce_rate * 100, 2),
        })

    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "sender_stats": sender_stats,
    }


@router.get("/{campaign_id}/receiver-stats")
async def get_campaign_receiver_stats(
    campaign_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get detailed statistics for each receiver in a campaign.

    Returns per-receiver metrics including emails received, replies sent, etc.
    """
    from sqlalchemy import func
    from warmit.models.email import Email, EmailStatus

    # Get campaign
    result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get receiver accounts
    result = await session.execute(
        select(Account).where(Account.id.in_(campaign.receiver_account_ids))
    )
    receivers = result.scalars().all()

    receiver_stats = []

    for receiver in receivers:
        # Count emails received by this receiver in this campaign
        emails_received_result = await session.execute(
            select(func.count(Email.id))
            .where(Email.receiver_id == receiver.id)
            .where(Email.campaign_id == campaign_id)
        )
        emails_received = emails_received_result.scalar() or 0

        # Count emails opened by this receiver
        emails_opened_result = await session.execute(
            select(func.count(Email.id))
            .where(Email.receiver_id == receiver.id)
            .where(Email.campaign_id == campaign_id)
            .where(Email.opened_at.isnot(None))
        )
        emails_opened = emails_opened_result.scalar() or 0

        # Count replies sent by this receiver
        replies_sent_result = await session.execute(
            select(func.count(Email.id))
            .where(Email.receiver_id == receiver.id)
            .where(Email.campaign_id == campaign_id)
            .where(Email.replied_at.isnot(None))
        )
        replies_sent = replies_sent_result.scalar() or 0

        # Count bounced emails to this receiver
        emails_bounced_result = await session.execute(
            select(func.count(Email.id))
            .where(Email.receiver_id == receiver.id)
            .where(Email.campaign_id == campaign_id)
            .where(Email.status == EmailStatus.BOUNCED)
        )
        emails_bounced = emails_bounced_result.scalar() or 0

        # Calculate rates
        open_rate = (emails_opened / emails_received * 100) if emails_received > 0 else 0
        reply_rate = (replies_sent / emails_received * 100) if emails_received > 0 else 0
        bounce_rate = (emails_bounced / emails_received * 100) if emails_received > 0 else 0

        receiver_stats.append({
            "receiver_id": receiver.id,
            "receiver_email": receiver.email,
            "receiver_name": receiver.full_name,
            "domain": receiver.domain,
            "status": receiver.status.value,
            "emails_received": emails_received,
            "emails_opened": emails_opened,
            "replies_sent": replies_sent,
            "emails_bounced": emails_bounced,
            "open_rate": round(open_rate, 2),
            "reply_rate": round(reply_rate, 2),
            "bounce_rate": round(bounce_rate, 2),
        })

    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "receiver_stats": receiver_stats,
    }


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a campaign."""
    result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    await session.delete(campaign)
    await session.commit()

    return None
