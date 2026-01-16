"""Application configuration using Pydantic settings."""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    database_url: str = "sqlite+aiosqlite:///./warmit.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AI Configuration
    ai_provider: Literal["openrouter", "groq", "openai"] = "openrouter"
    openrouter_api_key: str = ""
    openrouter_api_key_2: str = ""  # Fallback OpenRouter key
    openrouter_api_key_3: str = ""  # 3rd OpenRouter key
    groq_api_key: str = ""
    groq_api_key_2: str = ""  # Fallback Groq key
    openai_api_key: str = ""
    ai_model: str = "meta-llama/llama-3.3-70b-instruct:free"

    # Fallback models for different providers
    groq_model: str = "llama-3.3-70b-versatile"
    openai_model: str = "gpt-4o-mini"

    # Application
    debug: bool = False
    log_level: str = "INFO"

    # Email Warming Configuration
    min_emails_per_day: int = 5
    max_emails_per_day: int = 100
    warmup_duration_weeks: int = 6
    response_delay_min_hours: int = 1
    response_delay_max_hours: int = 6

    # Safety Settings
    max_bounce_rate: float = 0.05
    auto_pause_on_high_bounce: bool = True

    # Tracking
    api_base_url: str = "http://localhost:8000"  # Base URL for tracking pixels

    @property
    def ai_api_key(self) -> str:
        """Get the appropriate API key based on provider."""
        if self.ai_provider == "openrouter":
            return self.openrouter_api_key
        elif self.ai_provider == "groq":
            return self.groq_api_key
        elif self.ai_provider == "openai":
            return self.openai_api_key
        return ""

    @property
    def ai_base_url(self) -> str:
        """Get the base URL for the AI provider."""
        if self.ai_provider == "openrouter":
            return "https://openrouter.ai/api/v1"
        elif self.ai_provider == "groq":
            return "https://api.groq.com/openai/v1"
        elif self.ai_provider == "openai":
            return "https://api.openai.com/v1"
        return ""

    def _is_valid_api_key(self, key: str) -> bool:
        """Check if an API key is valid (not empty or placeholder)."""
        if not key or not key.strip():
            return False
        # Reject placeholder values
        invalid_patterns = ["your_", "change_this", "example", "placeholder", "xxx"]
        key_lower = key.lower()
        return not any(pattern in key_lower for pattern in invalid_patterns)

    def get_all_api_configs(self) -> list[dict[str, str]]:
        """
        Get all available API configurations in priority order.
        Returns list of dicts with 'provider', 'api_key', 'base_url', 'model'.
        Only includes valid API keys (not empty or placeholders).
        """
        configs = []

        # OpenRouter keys
        if self._is_valid_api_key(self.openrouter_api_key):
            configs.append({
                "provider": "openrouter_1",
                "api_key": self.openrouter_api_key,
                "base_url": "https://openrouter.ai/api/v1",
                "model": self.ai_model,
            })
        if self._is_valid_api_key(self.openrouter_api_key_2):
            configs.append({
                "provider": "openrouter_2",
                "api_key": self.openrouter_api_key_2,
                "base_url": "https://openrouter.ai/api/v1",
                "model": self.ai_model,
            })
        if self._is_valid_api_key(self.openrouter_api_key_3):
            configs.append({
                "provider": "openrouter_3",
                "api_key": self.openrouter_api_key_3,
                "base_url": "https://openrouter.ai/api/v1",
                "model": self.ai_model,
            })

        # Groq keys
        if self._is_valid_api_key(self.groq_api_key):
            configs.append({
                "provider": "groq_1",
                "api_key": self.groq_api_key,
                "base_url": "https://api.groq.com/openai/v1",
                "model": self.groq_model,
            })
        if self._is_valid_api_key(self.groq_api_key_2):
            configs.append({
                "provider": "groq_2",
                "api_key": self.groq_api_key_2,
                "base_url": "https://api.groq.com/openai/v1",
                "model": self.groq_model,
            })

        # OpenAI key
        if self._is_valid_api_key(self.openai_api_key):
            configs.append({
                "provider": "openai_1",
                "api_key": self.openai_api_key,
                "base_url": "https://api.openai.com/v1",
                "model": self.openai_model,
            })

        return configs


# Global settings instance
settings = Settings()
