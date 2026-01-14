"""Tests for domain checker service."""

import pytest
from warmit.services.domain_checker import DomainChecker, DomainInfo


class TestDomainChecker:
    """Test domain checker functionality."""

    def test_extract_domain(self):
        """Test domain extraction from email."""
        assert DomainChecker.extract_domain("test@example.com") == "example.com"
        assert DomainChecker.extract_domain("user@subdomain.example.com") == "subdomain.example.com"
        assert DomainChecker.extract_domain("example.com") == "example.com"

    @pytest.mark.asyncio
    async def test_check_domain_google(self):
        """Test checking a well-known domain."""
        domain_info = await DomainChecker.check_domain("test@google.com")

        assert domain_info.domain == "google.com"
        assert domain_info.age_days is not None
        assert domain_info.age_days > 365 * 20  # Google is old!
        assert not domain_info.is_new_domain
        assert domain_info.warmup_weeks_recommended == 2  # Established domain

    def test_domain_info_recommendations(self):
        """Test domain info recommendations."""
        # New domain (< 30 days)
        new_domain = DomainInfo(domain="new.com", age_days=15)
        assert new_domain.is_new_domain
        assert new_domain.warmup_weeks_recommended == 8
        assert new_domain.initial_daily_limit == 3

        # Moderately new (90-180 days)
        mid_domain = DomainInfo(domain="mid.com", age_days=120)
        assert not mid_domain.is_new_domain
        assert mid_domain.warmup_weeks_recommended == 4
        assert mid_domain.initial_daily_limit == 10

        # Established (> 180 days)
        old_domain = DomainInfo(domain="old.com", age_days=365)
        assert not old_domain.is_new_domain
        assert old_domain.warmup_weeks_recommended == 2
        assert old_domain.initial_daily_limit == 20

    def test_calculate_warmup_schedule(self):
        """Test warmup schedule calculation."""
        # New domain
        new_domain = DomainInfo(domain="new.com", age_days=15)
        schedule = DomainChecker.calculate_warmup_schedule(new_domain)

        assert len(schedule) == 8  # 8 weeks for new domain
        assert schedule[1] == 3  # Week 1 starts at 3
        assert schedule[8] > schedule[1]  # Progressive increase

        # Established domain
        old_domain = DomainInfo(domain="old.com", age_days=365)
        schedule = DomainChecker.calculate_warmup_schedule(old_domain)

        assert len(schedule) == 2  # Only 2 weeks needed
        assert schedule[1] == 20  # Start higher
