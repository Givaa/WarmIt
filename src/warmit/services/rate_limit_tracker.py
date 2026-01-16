"""API rate limit tracking and monitoring system with multi-key support.

Developed with ❤️ by Givaa
https://github.com/Givaa
"""

import time
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, field
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitInfo:
    """Rate limit information for an API key."""

    provider: str  # openrouter, groq, openai
    key_id: str  # Key identifier (e.g., "openrouter_1", "groq_2")

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


def _get_next_midnight_timestamp() -> float:
    """Calculate timestamp for next midnight (00:00:00).

    Returns:
        Unix timestamp for next midnight UTC
    """
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    # Get tomorrow's date at midnight
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return tomorrow.timestamp()


class RateLimitTracker:
    """Track API rate limits across multiple providers and API keys."""

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
        self.keys: Dict[str, RateLimitInfo] = {}
        self._initialize_keys_from_env()

    def _is_valid_api_key(self, key: str) -> bool:
        """Check if a string is a valid API key (not a placeholder or comment).

        Args:
            key: The key string to validate

        Returns:
            True if valid, False otherwise
        """
        if not key:
            return False

        # Skip comments (lines starting with #)
        if key.startswith("#"):
            return False

        # Common placeholder patterns to exclude
        placeholders = [
            "your_",
            "insert_",
            "add_your_",
            "put_your_",
            "paste_your_",
            "enter_your_",
            "replace_with_",
            "example_",
            "test_key",
            "dummy_",
            "placeholder",
            "xxx",
            "yyy",
            "zzz",
        ]

        key_lower = key.lower()
        for placeholder in placeholders:
            if placeholder in key_lower:
                return False

        return True

    def _initialize_keys_from_env(self):
        """Initialize API keys from environment variables."""
        # OpenRouter keys
        self._register_keys_for_provider("openrouter", "OPENROUTER_API_KEY")

        # Groq keys
        self._register_keys_for_provider("groq", "GROQ_API_KEY")

        # OpenAI keys
        self._register_keys_for_provider("openai", "OPENAI_API_KEY")

        logger.info(f"Initialized rate limit tracker with {len(self.keys)} API keys")

    def _register_keys_for_provider(self, provider: str, env_var_prefix: str):
        """Register all API keys for a provider from environment.

        Args:
            provider: Provider name (openrouter, groq, openai)
            env_var_prefix: Environment variable prefix (e.g., OPENROUTER_API_KEY)
        """
        if provider not in self.DEFAULT_LIMITS:
            logger.warning(f"No default limits for provider: {provider}")
            return

        limits = self.DEFAULT_LIMITS[provider]
        key_count = 0

        # Check main key
        main_key = os.getenv(env_var_prefix, "").strip()
        if main_key and self._is_valid_api_key(main_key):
            key_id = f"{provider}_1"
            self.keys[key_id] = RateLimitInfo(
                provider=provider,
                key_id=key_id,
                rpm_limit=limits["rpm"],
                rpd_limit=limits["rpd"],
                minute_reset_time=time.time() + 60,
                day_reset_time=_get_next_midnight_timestamp(),
            )
            key_count += 1
            logger.info(f"Registered {key_id}")

        # Check numbered keys (_2, _3, etc.)
        for i in range(2, 10):  # Support up to 9 keys per provider
            env_var = f"{env_var_prefix}_{i}"
            numbered_key = os.getenv(env_var, "").strip()
            if numbered_key and self._is_valid_api_key(numbered_key):
                key_id = f"{provider}_{i}"
                self.keys[key_id] = RateLimitInfo(
                    provider=provider,
                    key_id=key_id,
                    rpm_limit=limits["rpm"],
                    rpd_limit=limits["rpd"],
                    minute_reset_time=time.time() + 60,
                    day_reset_time=_get_next_midnight_timestamp(),
                )
                key_count += 1
                logger.info(f"Registered {key_id}")

        if key_count > 0:
            logger.info(f"Registered {key_count} API key(s) for {provider}")

    def set_key_limits(self, key_id: str, rpm: int, rpd: int):
        """Override default limits for a specific key.

        Args:
            key_id: Key identifier (e.g., "openrouter_1")
            rpm: Requests per minute limit
            rpd: Requests per day limit
        """
        if key_id in self.keys:
            self.keys[key_id].rpm_limit = rpm
            self.keys[key_id].rpd_limit = rpd
            logger.info(f"Updated {key_id} limits: {rpm} RPM, {rpd} RPD")

    def record_request(self, key_id: str) -> bool:
        """Record an API request for a specific key.

        Args:
            key_id: Key identifier (e.g., "openrouter_1")

        Returns:
            True if request allowed, False if rate limited
        """
        if key_id not in self.keys:
            logger.warning(f"Unknown key: {key_id}")
            return True

        info = self.keys[key_id]
        current_time = time.time()

        # Check if we need to reset counters
        self._check_resets(key_id)

        # Check if rate limited
        if info.requests_this_minute >= info.rpm_limit:
            logger.warning(f"{key_id}: RPM limit reached ({info.rpm_limit})")
            info.is_exhausted = True
            return False

        if info.requests_today >= info.rpd_limit:
            logger.warning(f"{key_id}: RPD limit reached ({info.rpd_limit})")
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

    def _check_resets(self, key_id: str):
        """Check and perform counter resets if needed.

        Args:
            key_id: Key identifier
        """
        if key_id not in self.keys:
            return

        info = self.keys[key_id]
        current_time = time.time()

        # Reset minute counter
        if current_time >= info.minute_reset_time:
            info.requests_this_minute = 0
            info.minute_reset_time = current_time + 60
            info.is_exhausted = False
            logger.debug(f"{key_id}: RPM counter reset")

        # Reset daily counter
        if current_time >= info.day_reset_time:
            info.requests_today = 0
            info.day_reset_time = _get_next_midnight_timestamp()
            info.is_exhausted = False
            logger.info(f"{key_id}: RPD counter reset")

    def can_make_request(self, key_id: str) -> Tuple[bool, str]:
        """Check if a request can be made with a specific key.

        Args:
            key_id: Key identifier

        Returns:
            Tuple of (can_make_request, reason_if_not)
        """
        if key_id not in self.keys:
            return True, ""

        self._check_resets(key_id)

        info = self.keys[key_id]

        if info.requests_this_minute >= info.rpm_limit:
            wait_time = int(info.time_until_rpm_reset())
            return False, f"RPM limit reached. Wait {wait_time}s."

        if info.requests_today >= info.rpd_limit:
            wait_time = int(info.time_until_rpd_reset() / 3600)
            return False, f"Daily limit reached. Wait {wait_time}h."

        return True, ""

    def get_available_key(self, provider: str) -> Optional[str]:
        """Get an available key for a provider.

        Selects the key with the most available quota.

        Args:
            provider: Provider name

        Returns:
            Key ID if available, None if all keys exhausted
        """
        provider_keys = [k for k in self.keys.keys() if k.startswith(provider)]

        if not provider_keys:
            return None

        # Find key with most remaining quota
        best_key = None
        best_remaining = -1

        for key_id in provider_keys:
            self._check_resets(key_id)
            can_use, _ = self.can_make_request(key_id)

            if can_use:
                info = self.keys[key_id]
                remaining = min(info.remaining_rpm(), info.remaining_rpd())

                if remaining > best_remaining:
                    best_remaining = remaining
                    best_key = key_id

        return best_key

    def get_key_status(self, key_id: str) -> Optional[RateLimitInfo]:
        """Get current status for a specific key.

        Args:
            key_id: Key identifier

        Returns:
            RateLimitInfo or None
        """
        if key_id in self.keys:
            self._check_resets(key_id)
        return self.keys.get(key_id)

    def get_provider_keys(self, provider: str) -> List[str]:
        """Get all keys for a provider.

        Args:
            provider: Provider name

        Returns:
            List of key IDs
        """
        return [k for k in self.keys.keys() if k.startswith(provider)]

    def get_provider_aggregate_status(self, provider: str) -> Dict[str, any]:
        """Get aggregated status for all keys of a provider.

        Args:
            provider: Provider name

        Returns:
            Dictionary with aggregated stats
        """
        provider_keys = self.get_provider_keys(provider)

        if not provider_keys:
            return {
                "provider": provider,
                "total_keys": 0,
                "total_rpm_limit": 0,
                "total_rpd_limit": 0,
                "total_requests_minute": 0,
                "total_requests_today": 0,
                "available_keys": 0,
            }

        total_rpm = 0
        total_rpd = 0
        total_req_minute = 0
        total_req_today = 0
        available = 0

        for key_id in provider_keys:
            self._check_resets(key_id)
            info = self.keys[key_id]

            total_rpm += info.rpm_limit
            total_rpd += info.rpd_limit
            total_req_minute += info.requests_this_minute
            total_req_today += info.requests_today

            can_use, _ = self.can_make_request(key_id)
            if can_use:
                available += 1

        return {
            "provider": provider,
            "total_keys": len(provider_keys),
            "total_rpm_limit": total_rpm,
            "total_rpd_limit": total_rpd,
            "total_requests_minute": total_req_minute,
            "total_requests_today": total_req_today,
            "available_keys": available,
            "utilization_rpm": (total_req_minute / total_rpm * 100) if total_rpm > 0 else 0,
            "utilization_rpd": (total_req_today / total_rpd * 100) if total_rpd > 0 else 0,
        }

    def get_all_statuses(self) -> Dict[str, RateLimitInfo]:
        """Get status for all keys."""
        for key_id in self.keys:
            self._check_resets(key_id)
        return self.keys.copy()

    def get_request_rate(self, key_id: str) -> float:
        """Get current request rate for a key (requests per hour).

        Args:
            key_id: Key identifier

        Returns:
            Requests per hour
        """
        if key_id not in self.keys:
            return 0.0

        info = self.keys[key_id]

        # Count requests in last hour
        current_time = time.time()
        hour_ago = current_time - 3600

        recent_requests = sum(1 for t in info.hourly_history if t >= hour_ago)

        return float(recent_requests)

    def get_saturation_forecast(self, key_id: str) -> Optional[datetime]:
        """Forecast when key will hit daily limit.

        Args:
            key_id: Key identifier

        Returns:
            Estimated saturation datetime, or None if not on track to saturate
        """
        if key_id not in self.keys:
            return None

        info = self.keys[key_id]
        request_rate = self.get_request_rate(key_id)

        hours_until = info.estimated_saturation_time(request_rate)

        if hours_until is None:
            return None

        return datetime.now() + timedelta(hours=hours_until)

    def reset_key(self, key_id: str):
        """Manually reset a key's counters.

        Args:
            key_id: Key identifier
        """
        if key_id in self.keys:
            info = self.keys[key_id]
            info.requests_this_minute = 0
            info.requests_today = 0
            info.minute_reset_time = time.time() + 60
            info.day_reset_time = _get_next_midnight_timestamp()
            info.is_exhausted = False
            logger.info(f"Manually reset {key_id} counters")


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


def record_api_request(key_id: str) -> bool:
    """Record an API request for a specific key (convenience function).

    Args:
        key_id: Key identifier (e.g., "openrouter_1")

    Returns:
        True if allowed, False if rate limited
    """
    tracker = get_rate_limit_tracker()
    return tracker.record_request(key_id)


def check_rate_limit(key_id: str) -> Tuple[bool, str]:
    """Check if API request is allowed for a specific key (convenience function).

    Args:
        key_id: Key identifier

    Returns:
        Tuple of (allowed, reason_if_not)
    """
    tracker = get_rate_limit_tracker()
    return tracker.can_make_request(key_id)


def get_available_key_for_provider(provider: str) -> Optional[str]:
    """Get an available key for a provider (convenience function).

    Args:
        provider: Provider name

    Returns:
        Key ID if available, None if all exhausted
    """
    tracker = get_rate_limit_tracker()
    return tracker.get_available_key(provider)
