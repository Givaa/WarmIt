"""API rate limit tracking and monitoring system."""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitInfo:
    """Rate limit information for an API provider."""

    provider: str  # openrouter, groq, openai

    # Limits
    rpm_limit: int  # requests per minute
    rpd_limit: int  # requests per day

    # Current usage
    requests_this_minute: int = 0
    requests_today: int = 0

    # Timestamps
    minute_reset_time: float = field(default_factory=time.time)
    day_reset_time: float = field(default_factory=lambda: time.time())

    # Historical tracking (last 60 minutes)
    hourly_history: deque = field(default_factory=lambda: deque(maxlen=60))

    # Status
    is_exhausted: bool = False
    last_request_time: float = 0.0

    def utilization_rpm(self) -> float:
        """Get current RPM utilization percentage (0-100)."""
        if self.rpm_limit == 0:
            return 0.0
        return (self.requests_this_minute / self.rpm_limit) * 100

    def utilization_rpd(self) -> float:
        """Get current RPD utilization percentage (0-100)."""
        if self.rpd_limit == 0:
            return 0.0
        return (self.requests_today / self.rpd_limit) * 100

    def remaining_rpm(self) -> int:
        """Get remaining requests this minute."""
        return max(0, self.rpm_limit - self.requests_this_minute)

    def remaining_rpd(self) -> int:
        """Get remaining requests today."""
        return max(0, self.rpd_limit - self.requests_today)

    def time_until_rpm_reset(self) -> float:
        """Get seconds until RPM resets."""
        return max(0, self.minute_reset_time - time.time())

    def time_until_rpd_reset(self) -> float:
        """Get seconds until RPD resets."""
        return max(0, self.day_reset_time - time.time())

    def estimated_saturation_time(self, requests_per_hour: float) -> Optional[float]:
        """Estimate when rate limit will be exhausted.

        Args:
            requests_per_hour: Current request rate per hour

        Returns:
            Hours until saturation, or None if not on track to saturate
        """
        if requests_per_hour == 0:
            return None

        # Calculate based on daily limit
        remaining = self.remaining_rpd()
        if remaining == 0:
            return 0.0

        hours_until_saturation = remaining / requests_per_hour

        # If saturation is beyond today, return None
        if hours_until_saturation > 24:
            return None

        return hours_until_saturation


class RateLimitTracker:
    """Track API rate limits across multiple providers."""

    # Default rate limits (free tier)
    DEFAULT_LIMITS = {
        "openrouter": {
            "rpm": 20,
            "rpd": 50,  # Assumes <$10 credits
        },
        "groq": {
            "rpm": 30,  # Conservative estimate
            "rpd": 1000,  # Conservative estimate
        },
        "openai": {
            "rpm": 60,  # Free tier estimate
            "rpd": 200,  # Free tier estimate
        },
    }

    def __init__(self):
        """Initialize rate limit tracker."""
        self.providers: Dict[str, RateLimitInfo] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all providers with default limits."""
        for provider, limits in self.DEFAULT_LIMITS.items():
            self.providers[provider] = RateLimitInfo(
                provider=provider,
                rpm_limit=limits["rpm"],
                rpd_limit=limits["rpd"],
                minute_reset_time=time.time() + 60,
                day_reset_time=time.time() + 86400,  # 24 hours
            )

    def set_provider_limits(self, provider: str, rpm: int, rpd: int):
        """Override default limits for a provider.

        Args:
            provider: Provider name
            rpm: Requests per minute limit
            rpd: Requests per day limit
        """
        if provider in self.providers:
            self.providers[provider].rpm_limit = rpm
            self.providers[provider].rpd_limit = rpd
            logger.info(f"Updated {provider} limits: {rpm} RPM, {rpd} RPD")

    def record_request(self, provider: str) -> bool:
        """Record an API request.

        Args:
            provider: Provider name

        Returns:
            True if request allowed, False if rate limited
        """
        if provider not in self.providers:
            logger.warning(f"Unknown provider: {provider}")
            return True

        info = self.providers[provider]
        current_time = time.time()

        # Check if we need to reset counters
        self._check_resets(provider)

        # Check if rate limited
        if info.requests_this_minute >= info.rpm_limit:
            logger.warning(f"{provider}: RPM limit reached ({info.rpm_limit})")
            info.is_exhausted = True
            return False

        if info.requests_today >= info.rpd_limit:
            logger.warning(f"{provider}: RPD limit reached ({info.rpd_limit})")
            info.is_exhausted = True
            return False

        # Record request
        info.requests_this_minute += 1
        info.requests_today += 1
        info.last_request_time = current_time
        info.is_exhausted = False

        # Add to hourly history
        info.hourly_history.append(current_time)

        return True

    def _check_resets(self, provider: str):
        """Check and perform counter resets if needed.

        Args:
            provider: Provider name
        """
        info = self.providers[provider]
        current_time = time.time()

        # Reset minute counter
        if current_time >= info.minute_reset_time:
            info.requests_this_minute = 0
            info.minute_reset_time = current_time + 60
            info.is_exhausted = False
            logger.debug(f"{provider}: RPM counter reset")

        # Reset daily counter
        if current_time >= info.day_reset_time:
            info.requests_today = 0
            info.day_reset_time = current_time + 86400
            info.is_exhausted = False
            logger.info(f"{provider}: RPD counter reset")

    def can_make_request(self, provider: str) -> Tuple[bool, str]:
        """Check if a request can be made.

        Args:
            provider: Provider name

        Returns:
            Tuple of (can_make_request, reason_if_not)
        """
        if provider not in self.providers:
            return True, ""

        self._check_resets(provider)

        info = self.providers[provider]

        if info.requests_this_minute >= info.rpm_limit:
            wait_time = int(info.time_until_rpm_reset())
            return False, f"RPM limit reached. Wait {wait_time}s."

        if info.requests_today >= info.rpd_limit:
            wait_time = int(info.time_until_rpd_reset() / 3600)
            return False, f"Daily limit reached. Wait {wait_time}h."

        return True, ""

    def get_provider_status(self, provider: str) -> Optional[RateLimitInfo]:
        """Get current status for a provider.

        Args:
            provider: Provider name

        Returns:
            RateLimitInfo or None
        """
        self._check_resets(provider)
        return self.providers.get(provider)

    def get_all_statuses(self) -> Dict[str, RateLimitInfo]:
        """Get status for all providers."""
        for provider in self.providers:
            self._check_resets(provider)
        return self.providers.copy()

    def get_request_rate(self, provider: str) -> float:
        """Get current request rate (requests per hour).

        Args:
            provider: Provider name

        Returns:
            Requests per hour
        """
        if provider not in self.providers:
            return 0.0

        info = self.providers[provider]

        # Count requests in last hour
        current_time = time.time()
        hour_ago = current_time - 3600

        recent_requests = sum(1 for t in info.hourly_history if t >= hour_ago)

        return float(recent_requests)

    def get_saturation_forecast(self, provider: str) -> Optional[datetime]:
        """Forecast when provider will hit daily limit.

        Args:
            provider: Provider name

        Returns:
            Estimated saturation datetime, or None if not on track to saturate
        """
        if provider not in self.providers:
            return None

        info = self.providers[provider]
        request_rate = self.get_request_rate(provider)

        hours_until = info.estimated_saturation_time(request_rate)

        if hours_until is None:
            return None

        return datetime.now() + timedelta(hours=hours_until)

    def reset_provider(self, provider: str):
        """Manually reset a provider's counters.

        Args:
            provider: Provider name
        """
        if provider in self.providers:
            info = self.providers[provider]
            info.requests_this_minute = 0
            info.requests_today = 0
            info.minute_reset_time = time.time() + 60
            info.day_reset_time = time.time() + 86400
            info.is_exhausted = False
            logger.info(f"Manually reset {provider} counters")


# Global rate limit tracker
_rate_limit_tracker: Optional[RateLimitTracker] = None


def get_rate_limit_tracker() -> RateLimitTracker:
    """Get or create global rate limit tracker.

    Returns:
        RateLimitTracker instance
    """
    global _rate_limit_tracker
    if _rate_limit_tracker is None:
        _rate_limit_tracker = RateLimitTracker()
    return _rate_limit_tracker


def record_api_request(provider: str) -> bool:
    """Record an API request (convenience function).

    Args:
        provider: Provider name

    Returns:
        True if allowed, False if rate limited
    """
    tracker = get_rate_limit_tracker()
    return tracker.record_request(provider)


def check_rate_limit(provider: str) -> Tuple[bool, str]:
    """Check if API request is allowed (convenience function).

    Args:
        provider: Provider name

    Returns:
        Tuple of (allowed, reason_if_not)
    """
    tracker = get_rate_limit_tracker()
    return tracker.can_make_request(provider)
