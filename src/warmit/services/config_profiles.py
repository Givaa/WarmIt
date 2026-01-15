"""Configuration profile management for dynamic scaling."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProfileConfig:
    """Configuration profile data."""

    name: str
    description: str
    max_senders: int
    max_receivers: int
    resources: Dict[str, Any]
    email_volume: Dict[str, Any]
    workers: Dict[str, Any]
    database: Dict[str, Any]
    safety: Dict[str, Any]
    api_limits: Dict[str, Any]
    monitoring: Dict[str, Any]
    recommendations: list[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProfileConfig":
        """Create ProfileConfig from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            max_senders=data["max_senders"],
            max_receivers=data["max_receivers"],
            resources=data["resources"],
            email_volume=data["email_volume"],
            workers=data["workers"],
            database=data["database"],
            safety=data["safety"],
            api_limits=data["api_limits"],
            monitoring=data["monitoring"],
            recommendations=data["recommendations"],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "max_senders": self.max_senders,
            "max_receivers": self.max_receivers,
            "resources": self.resources,
            "email_volume": self.email_volume,
            "workers": self.workers,
            "database": self.database,
            "safety": self.safety,
            "api_limits": self.api_limits,
            "monitoring": self.monitoring,
            "recommendations": self.recommendations,
        }


class ConfigProfileManager:
    """Manage configuration profiles for different deployment scales."""

    def __init__(self):
        """Initialize profile manager."""
        self.profiles_dir = Path(__file__).parent.parent.parent.parent / "config" / "profiles"
        self.profiles: Dict[str, ProfileConfig] = {}
        self._load_profiles()

    def _load_profiles(self):
        """Load all profile YAML files."""
        if not self.profiles_dir.exists():
            logger.warning(f"Profiles directory not found: {self.profiles_dir}")
            return

        for profile_file in self.profiles_dir.glob("*.yaml"):
            try:
                with open(profile_file, 'r') as f:
                    data = yaml.safe_load(f)
                    profile = ProfileConfig.from_dict(data)
                    self.profiles[profile.name] = profile
                    logger.info(f"Loaded profile: {profile.name}")
            except Exception as e:
                logger.error(f"Failed to load profile {profile_file}: {e}")

    def get_profile(self, name: str) -> Optional[ProfileConfig]:
        """Get profile by name.

        Args:
            name: Profile name (small, medium, large, enterprise)

        Returns:
            ProfileConfig or None if not found
        """
        return self.profiles.get(name.lower())

    def get_recommended_profile(self, num_senders: int) -> Optional[ProfileConfig]:
        """Get recommended profile based on number of senders.

        Args:
            num_senders: Number of sender accounts

        Returns:
            Recommended ProfileConfig
        """
        if num_senders <= 10:
            return self.get_profile("small")
        elif num_senders <= 50:
            return self.get_profile("medium")
        elif num_senders <= 200:
            return self.get_profile("large")
        else:
            return self.get_profile("enterprise")

    def list_profiles(self) -> list[str]:
        """List all available profile names."""
        return list(self.profiles.keys())

    def get_all_profiles(self) -> Dict[str, ProfileConfig]:
        """Get all loaded profiles."""
        return self.profiles

    def apply_profile(self, profile_name: str, env_vars: Dict[str, str]) -> Dict[str, str]:
        """Apply profile settings to environment variables.

        Args:
            profile_name: Profile to apply
            env_vars: Current environment variables

        Returns:
            Updated environment variables
        """
        profile = self.get_profile(profile_name)
        if not profile:
            logger.error(f"Profile not found: {profile_name}")
            return env_vars

        # Update env vars with profile settings
        updated = env_vars.copy()

        # Email volume
        updated["MIN_EMAILS_PER_DAY"] = str(profile.email_volume["min_emails_per_day"])
        updated["MAX_EMAILS_PER_DAY"] = str(profile.email_volume["max_emails_per_day"])
        updated["WARMUP_DURATION_WEEKS"] = str(profile.email_volume["warmup_duration_weeks"])
        updated["RESPONSE_DELAY_MIN_HOURS"] = str(profile.email_volume["response_delay_min_hours"])
        updated["RESPONSE_DELAY_MAX_HOURS"] = str(profile.email_volume["response_delay_max_hours"])

        # Safety
        updated["MAX_BOUNCE_RATE"] = str(profile.safety["max_bounce_rate"])
        updated["AUTO_PAUSE_ON_HIGH_BOUNCE"] = str(profile.safety["auto_pause_on_high_bounce"]).lower()

        # Workers (for docker-compose)
        updated["CELERY_WORKERS"] = str(profile.workers["celery_workers"])
        updated["CELERY_CONCURRENCY"] = str(profile.workers["celery_concurrency"])

        # Database
        updated["DB_POOL_SIZE"] = str(profile.database["pool_size"])
        updated["DB_MAX_OVERFLOW"] = str(profile.database["max_overflow"])

        logger.info(f"Applied profile '{profile_name}' to configuration")

        return updated


# Global profile manager instance
_profile_manager: Optional[ConfigProfileManager] = None


def get_profile_manager() -> ConfigProfileManager:
    """Get or create global profile manager instance.

    Returns:
        ConfigProfileManager instance
    """
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ConfigProfileManager()
    return _profile_manager


def get_current_profile(num_senders: int) -> Optional[ProfileConfig]:
    """Get recommended profile for current deployment.

    Args:
        num_senders: Number of sender accounts

    Returns:
        Recommended ProfileConfig
    """
    manager = get_profile_manager()
    return manager.get_recommended_profile(num_senders)
