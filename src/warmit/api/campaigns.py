"""Campaign management API endpoints."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from warmit.database import get_session
from warmit.models.campaign import Campaign, CampaignStatus
from warmit.services.scheduler import WarmupScheduler


router = APIRouter()


# Pydantic schemas
class CampaignCreate(BaseModel):
    """Schema for creating a campaign."""

    name: str
    sender_account_ids: list[int]
    receiver_account_ids: list[int]
    duration_weeks: Optional[int] = None


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

    This is useful for testing. In production, this should be triggered by a cron job.
    """
    result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    scheduler = WarmupScheduler(session)
    emails_sent = await scheduler.process_campaign(campaign)

    return {
        "campaign_id": campaign_id,
        "emails_sent": emails_sent,
        "emails_sent_today": campaign.emails_sent_today,
        "target_emails_today": campaign.target_emails_today,
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
