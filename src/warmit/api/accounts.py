"""Account management API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from warmit.database import get_session
from warmit.models.account import Account, AccountType, AccountStatus
from warmit.services.domain_checker import DomainChecker
from warmit.services.email_service import EmailService
from datetime import datetime, timezone


router = APIRouter()


# Pydantic schemas
class AccountCreate(BaseModel):
    """Schema for creating an account."""

    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    type: AccountType
    smtp_host: str
    smtp_port: int = 587
    smtp_use_tls: bool = True
    imap_host: str
    imap_port: int = 993
    imap_use_ssl: bool = True
    password: str


class AccountUpdate(BaseModel):
    """Schema for updating an account."""

    status: Optional[AccountStatus] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    imap_host: Optional[str] = None
    imap_port: Optional[int] = None
    password: Optional[str] = None


class AccountResponse(BaseModel):
    """Schema for account response."""

    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    type: AccountType
    status: AccountStatus
    domain: Optional[str]
    domain_age_days: Optional[int]
    current_daily_limit: int
    total_sent: int
    total_received: int
    total_opened: int
    total_replied: int
    total_bounced: int
    bounce_rate: float
    open_rate: float
    reply_rate: float
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=AccountResponse, status_code=201)
async def create_account(
    account_data: AccountCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new email account.

    This endpoint creates a new email account for warming (sender) or receiving (receiver).
    It automatically checks the domain age for sender accounts.
    """
    # Check if account already exists
    result = await session.execute(
        select(Account).where(Account.email == account_data.email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Account already exists")

    # Test connection
    test_results = await EmailService.test_connection(
        smtp_host=account_data.smtp_host,
        smtp_port=account_data.smtp_port,
        imap_host=account_data.imap_host,
        imap_port=account_data.imap_port,
        username=account_data.email,
        password=account_data.password,
        smtp_use_tls=account_data.smtp_use_tls,
        imap_use_ssl=account_data.imap_use_ssl,
    )

    if not test_results["smtp"] or not test_results["imap"]:
        raise HTTPException(
            status_code=400,
            detail=f"Connection test failed: SMTP={test_results['smtp']}, IMAP={test_results['imap']}",
        )

    # Create account
    account = Account(
        email=account_data.email,
        first_name=account_data.first_name,
        last_name=account_data.last_name,
        type=account_data.type,
        status=AccountStatus.ACTIVE,
        smtp_host=account_data.smtp_host,
        smtp_port=account_data.smtp_port,
        smtp_use_tls=account_data.smtp_use_tls,
        imap_host=account_data.imap_host,
        imap_port=account_data.imap_port,
        imap_use_ssl=account_data.imap_use_ssl,
        password=account_data.password,
    )

    # Extract domain from email for all accounts
    domain = account_data.email.split('@')[1] if '@' in account_data.email else None
    account.domain = domain

    # Check domain age only for sender accounts
    if account_data.type == AccountType.SENDER:
        domain_info = await DomainChecker.check_domain(account_data.email)
        account.domain_age_days = domain_info.age_days
        account.domain_checked_at = datetime.now(timezone.utc)
        account.current_daily_limit = domain_info.initial_daily_limit

    session.add(account)
    await session.commit()
    await session.refresh(account)

    return account


@router.get("", response_model=list[AccountResponse])
async def list_accounts(
    type: Optional[AccountType] = None,
    status: Optional[AccountStatus] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    List all email accounts.

    Optional filters:
    - type: Filter by account type (sender/receiver)
    - status: Filter by account status (active/paused/disabled/error)
    """
    query = select(Account)

    if type:
        query = query.where(Account.type == type)
    if status:
        query = query.where(Account.status == status)

    result = await session.execute(query)
    accounts = result.scalars().all()

    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a specific account by ID."""
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    update_data: AccountUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update an account."""
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Update fields
    if update_data.status is not None:
        account.status = update_data.status
    if update_data.smtp_host is not None:
        account.smtp_host = update_data.smtp_host
    if update_data.smtp_port is not None:
        account.smtp_port = update_data.smtp_port
    if update_data.imap_host is not None:
        account.imap_host = update_data.imap_host
    if update_data.imap_port is not None:
        account.imap_port = update_data.imap_port
    if update_data.password is not None:
        account.password = update_data.password

    await session.commit()
    await session.refresh(account)

    return account


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete an account."""
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    await session.delete(account)
    await session.commit()

    return None


@router.post("/{account_id}/check-domain")
async def check_domain(
    account_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Re-check domain age for an account."""
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    domain_info = await DomainChecker.check_domain(account.email)
    account.domain = domain_info.domain
    account.domain_age_days = domain_info.age_days
    account.domain_checked_at = datetime.now(timezone.utc)

    await session.commit()

    return {
        "domain": domain_info.domain,
        "age_days": domain_info.age_days,
        "is_new_domain": domain_info.is_new_domain,
        "warmup_weeks_recommended": domain_info.warmup_weeks_recommended,
        "initial_daily_limit": domain_info.initial_daily_limit,
    }
