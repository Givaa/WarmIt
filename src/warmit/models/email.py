"""Email model for tracking sent/received emails."""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from warmit.models.base import Base, TimestampMixin


class EmailStatus(str, Enum):
    """Status of an email."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    FAILED = "failed"


class Email(Base, TimestampMixin):
    """Email tracking record."""

    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Relationships
    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    receiver_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    campaign_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Email content
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    in_reply_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    thread_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # Status tracking
    status: Mapped[EmailStatus] = mapped_column(
        SQLEnum(EmailStatus),
        default=EmailStatus.PENDING,
        nullable=False,
        index=True
    )
    is_warmup: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timing
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # AI generation metadata
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ai_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    sender: Mapped["Account"] = relationship(
        "Account",
        foreign_keys=[sender_id],
        back_populates="sent_emails"
    )
    receiver: Mapped["Account"] = relationship(
        "Account",
        foreign_keys=[receiver_id],
        back_populates="received_emails"
    )

    def __repr__(self) -> str:
        return f"<Email(id={self.id}, subject={self.subject[:30]}, status={self.status})>"
