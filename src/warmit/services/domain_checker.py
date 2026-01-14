"""Domain age and reputation checker using WHOIS/RDAP."""

import re
import logging
from datetime import datetime, timezone
from typing import Optional
import whois
from email.utils import parseaddr


logger = logging.getLogger(__name__)


class DomainInfo:
    """Domain information container."""

    def __init__(
        self,
        domain: str,
        creation_date: Optional[datetime] = None,
        age_days: Optional[int] = None,
        registrar: Optional[str] = None,
        status: Optional[list[str]] = None,
    ):
        self.domain = domain
        self.creation_date = creation_date
        self.age_days = age_days
        self.registrar = registrar
        self.status = status or []

    @property
    def is_new_domain(self) -> bool:
        """Check if domain is less than 30 days old."""
        if self.age_days is None:
            return False
        return self.age_days < 30

    @property
    def warmup_weeks_recommended(self) -> int:
        """Recommend warming duration based on domain age."""
        if self.age_days is None:
            return 6  # Default to 6 weeks

        if self.age_days < 30:
            return 8  # Very new domain
        elif self.age_days < 90:
            return 6  # New domain
        elif self.age_days < 180:
            return 4  # Moderately new
        else:
            return 2  # Established domain

    @property
    def initial_daily_limit(self) -> int:
        """Recommend initial daily email limit based on domain age."""
        if self.age_days is None:
            return 5

        if self.age_days < 30:
            return 3  # Very conservative for brand new domains
        elif self.age_days < 90:
            return 5  # Conservative
        elif self.age_days < 180:
            return 10  # Moderate
        else:
            return 20  # More aggressive for established domains

    def __repr__(self) -> str:
        return (
            f"<DomainInfo(domain={self.domain}, age_days={self.age_days}, "
            f"recommended_warmup_weeks={self.warmup_weeks_recommended})>"
        )


class DomainChecker:
    """Check domain age and provide warming recommendations."""

    @staticmethod
    def extract_domain(email: str) -> str:
        """
        Extract domain from email address.

        Args:
            email: Email address

        Returns:
            Domain name
        """
        _, addr = parseaddr(email)
        if "@" in addr:
            return addr.split("@")[1].lower()
        return email.lower()

    @staticmethod
    async def check_domain(email_or_domain: str) -> DomainInfo:
        """
        Check domain age and information using WHOIS.

        Args:
            email_or_domain: Email address or domain name

        Returns:
            DomainInfo object with domain information

        Raises:
            ValueError: If domain lookup fails
        """
        # Extract domain if email address provided
        if "@" in email_or_domain:
            domain = DomainChecker.extract_domain(email_or_domain)
        else:
            domain = email_or_domain.lower()

        logger.info(f"Checking domain: {domain}")

        try:
            # Query WHOIS
            w = whois.whois(domain)

            # Extract creation date
            creation_date = None
            if w.creation_date:
                # Handle both single datetime and list of datetimes
                if isinstance(w.creation_date, list):
                    creation_date = w.creation_date[0]
                else:
                    creation_date = w.creation_date

                # Ensure timezone aware
                if creation_date and creation_date.tzinfo is None:
                    creation_date = creation_date.replace(tzinfo=timezone.utc)

            # Calculate age in days
            age_days = None
            if creation_date:
                now = datetime.now(timezone.utc)
                age_days = (now - creation_date).days

            # Extract registrar
            registrar = w.registrar if hasattr(w, "registrar") else None

            # Extract status
            status = []
            if hasattr(w, "status"):
                if isinstance(w.status, list):
                    status = w.status
                elif isinstance(w.status, str):
                    status = [w.status]

            domain_info = DomainInfo(
                domain=domain,
                creation_date=creation_date,
                age_days=age_days,
                registrar=registrar,
                status=status,
            )

            logger.info(
                f"Domain check successful: {domain} - Age: {age_days} days, "
                f"Recommended warmup: {domain_info.warmup_weeks_recommended} weeks"
            )

            return domain_info

        except Exception as e:
            logger.error(f"Failed to check domain {domain}: {e}")
            # Return default info on failure
            return DomainInfo(
                domain=domain,
                creation_date=None,
                age_days=None,
                registrar=None,
                status=[],
            )

    @staticmethod
    def calculate_warmup_schedule(domain_info: DomainInfo) -> dict[int, int]:
        """
        Calculate email volume schedule for warming period.

        Args:
            domain_info: Domain information

        Returns:
            Dictionary mapping week number to daily email limit
        """
        weeks = domain_info.warmup_weeks_recommended
        initial_limit = domain_info.initial_daily_limit

        schedule = {}

        # Progressive increase based on domain age
        if domain_info.age_days and domain_info.age_days < 30:
            # Very conservative for new domains
            schedule = {
                1: initial_limit,  # 3-5
                2: initial_limit + 2,  # 5-7
                3: initial_limit + 5,  # 8-10
                4: initial_limit + 10,  # 13-15
                5: initial_limit + 15,  # 18-20
                6: initial_limit + 20,  # 23-25
                7: initial_limit + 30,  # 33-35
                8: initial_limit + 40,  # 43-45
            }
        elif domain_info.age_days and domain_info.age_days < 90:
            # Standard warming curve
            schedule = {
                1: 5,
                2: 10,
                3: 15,
                4: 25,
                5: 35,
                6: 50,
            }
        elif domain_info.age_days and domain_info.age_days < 180:
            # Faster warmup for moderately aged domains
            schedule = {
                1: 10,
                2: 20,
                3: 35,
                4: 50,
            }
        else:
            # Quick warmup for established domains
            schedule = {
                1: 20,
                2: 50,
            }

        # Return only the weeks needed
        return {week: limit for week, limit in schedule.items() if week <= weeks}
