"""Metrics model for tracking daily statistics."""

from datetime import date
from sqlalchemy import Integer, Float, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from warmit.models.base import Base, TimestampMixin


class Metric(Base, TimestampMixin):
    """Daily metrics for an account."""

    __tablename__ = "metrics"
    __table_args__ = (
        UniqueConstraint("account_id", "date", name="uix_account_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Relationship
    account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Date for these metrics
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Email counts
    emails_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    emails_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    emails_opened: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    emails_replied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    emails_bounced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    emails_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Calculated rates
    open_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reply_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    bounce_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationship
    account: Mapped["Account"] = relationship("Account", back_populates="metrics")

    def calculate_rates(self) -> None:
        """Calculate and update rates based on counts."""
        if self.emails_sent > 0:
            self.open_rate = self.emails_opened / self.emails_sent
            self.bounce_rate = self.emails_bounced / self.emails_sent
        else:
            self.open_rate = 0.0
            self.bounce_rate = 0.0

        if self.emails_received > 0:
            self.reply_rate = self.emails_replied / self.emails_received
        else:
            self.reply_rate = 0.0

    def __repr__(self) -> str:
        return (
            f"<Metric(account_id={self.account_id}, date={self.date}, "
            f"sent={self.emails_sent}, open_rate={self.open_rate:.2%})>"
        )
