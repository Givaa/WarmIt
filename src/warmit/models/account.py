"""Email account model."""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Integer, Boolean, Enum as SQLEnum, DateTime, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from warmit.models.base import Base, TimestampMixin


class AccountType(str, Enum):
    """Type of email account."""
    SENDER = "sender"  # Account to be warmed up
    RECEIVER = "receiver"  # Account that receives and responds


class AccountStatus(str, Enum):
    """Status of email account."""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    ERROR = "error"


class Account(Base, TimestampMixin):
    """Email account configuration."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # Personal information
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Account type and status
    type: Mapped[AccountType] = mapped_column(SQLEnum(AccountType), nullable=False)
    status: Mapped[AccountStatus] = mapped_column(
        SQLEnum(AccountStatus),
        default=AccountStatus.ACTIVE,
        nullable=False
    )

    # SMTP Configuration
    smtp_host: Mapped[str] = mapped_column(String(255), nullable=False)
    smtp_port: Mapped[int] = mapped_column(Integer, default=587, nullable=False)
    smtp_use_tls: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # IMAP Configuration
    imap_host: Mapped[str] = mapped_column(String(255), nullable=False)
    imap_port: Mapped[int] = mapped_column(Integer, default=993, nullable=False)
    imap_use_ssl: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Credentials (encrypted at rest)
    # Note: This column stores encrypted passwords. Use _plaintext_password for in-memory plaintext.
    password: Mapped[str] = mapped_column(String(500), nullable=False)  # Increased size for encrypted data

    # Domain information
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    domain_age_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    domain_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Warming configuration
    current_daily_limit: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    warmup_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Statistics
    total_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_opened: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_replied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_bounced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    sent_emails: Mapped[list["Email"]] = relationship(
        "Email",
        foreign_keys="Email.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan"
    )
    received_emails: Mapped[list["Email"]] = relationship(
        "Email",
        foreign_keys="Email.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan"
    )
    metrics: Mapped[list["Metric"]] = relationship(
        "Metric",
        back_populates="account",
        cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        """Get full name or email username as fallback."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            # Fallback to email username
            return self.email.split('@')[0].replace('.', ' ').replace('_', ' ').title()

    @property
    def bounce_rate(self) -> float:
        """Calculate bounce rate."""
        if self.total_sent == 0:
            return 0.0
        return self.total_bounced / self.total_sent

    @property
    def open_rate(self) -> float:
        """Calculate open rate."""
        if self.total_sent == 0:
            return 0.0
        return self.total_opened / self.total_sent

    @property
    def reply_rate(self) -> float:
        """Calculate reply rate."""
        if self.total_received == 0:
            return 0.0
        return self.total_replied / self.total_received

    def get_password(self) -> str:
        """Get decrypted password.

        Returns:
            Plain text password
        """
        # If we have a cached plaintext password from the load event, use it
        if hasattr(self, '_plaintext_password') and self._plaintext_password:
            return self._plaintext_password

        # Otherwise, decrypt from the encrypted password field
        from warmit.services.encryption import decrypt_password
        decrypted = decrypt_password(self.password)
        self._plaintext_password = decrypted
        return decrypted

    def set_password(self, plaintext_password: str) -> None:
        """Set password (will be encrypted).

        Args:
            plaintext_password: Plain text password to encrypt and store
        """
        from warmit.services.encryption import encrypt_password
        self.password = encrypt_password(plaintext_password)

    def __repr__(self) -> str:
        return f"<Account(email={self.email}, type={self.type}, status={self.status})>"


# SQLAlchemy events for automatic encryption/decryption
@event.listens_for(Account, "before_insert")
@event.listens_for(Account, "before_update")
def encrypt_password_on_save(mapper, connection, target):
    """Encrypt password before saving to database."""
    from warmit.services.encryption import encrypt_password

    # Check if password looks like plaintext (not already encrypted)
    # Fernet encrypted strings start with 'gAAAAA' when base64 encoded
    if target.password and not target.password.startswith('gAAAAA'):
        target.password = encrypt_password(target.password)


@event.listens_for(Account, "load")
def decrypt_password_on_load(target, context):
    """Decrypt password after loading from database."""
    from warmit.services.encryption import decrypt_password

    # Decrypt password on load
    if target.password:
        decrypted = decrypt_password(target.password)
        # Store decrypted password in a private attribute for in-memory use
        target._plaintext_password = decrypted
