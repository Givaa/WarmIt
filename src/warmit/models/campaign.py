"""Campaign model for warming campaigns."""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from warmit.models.base import Base, TimestampMixin


class CampaignStatus(str, Enum):
    """Status of a warming campaign."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class Campaign(Base, TimestampMixin):
    """Warming campaign configuration and tracking."""

    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Campaign configuration
    sender_account_ids: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    receiver_account_ids: Mapped[list[int]] = mapped_column(JSON, nullable=False)

    # Status and timing
    status: Mapped[CampaignStatus] = mapped_column(
        SQLEnum(CampaignStatus),
        default=CampaignStatus.PENDING,
        nullable=False
    )
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_weeks: Mapped[int] = mapped_column(Integer, default=6, nullable=False)

    # Progress tracking
    current_week: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    emails_sent_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    target_emails_today: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    last_email_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Statistics
    total_emails_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_emails_opened: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_emails_replied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_emails_bounced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Settings
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    @property
    def open_rate(self) -> float:
        """Calculate campaign open rate."""
        if self.total_emails_sent == 0:
            return 0.0
        return self.total_emails_opened / self.total_emails_sent

    @property
    def reply_rate(self) -> float:
        """Calculate campaign reply rate."""
        if self.total_emails_sent == 0:
            return 0.0
        return self.total_emails_replied / self.total_emails_sent

    @property
    def bounce_rate(self) -> float:
        """Calculate campaign bounce rate."""
        if self.total_emails_sent == 0:
            return 0.0
        return self.total_emails_bounced / self.total_emails_sent

    @property
    def progress_percentage(self) -> float:
        """Calculate campaign progress percentage."""
        total_weeks = self.duration_weeks
        if total_weeks == 0:
            return 0.0
        return (self.current_week / total_weeks) * 100

    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, name={self.name}, status={self.status})>"
