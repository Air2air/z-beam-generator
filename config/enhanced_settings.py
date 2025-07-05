"""
Type-safe configuration using Pydantic.
"""

from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional, List
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()


class APISettings(BaseSettings):
    """API configuration settings."""

    gemini_api_key: Optional[str] = Field(None, env="GEMINI_API_KEY")
    xai_api_key: Optional[str] = Field(None, env="XAI_API_KEY")
    deepseek_api_key: Optional[str] = Field(None, env="DEEPSEEK_API_KEY")

    @field_validator("gemini_api_key", "xai_api_key", "deepseek_api_key", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        provider_lower = provider.lower()
        if provider_lower == "gemini":
            return self.gemini_api_key
        elif provider_lower == "xai":
            return self.xai_api_key
        elif provider_lower == "deepseek":
            return self.deepseek_api_key
        return None


class GenerationSettings(BaseSettings):
    """Content generation settings."""

    default_temperature: float = Field(1.0, ge=0.0, le=2.0)
    default_ai_threshold: int = Field(25, ge=0, le=100)
    default_human_threshold: int = Field(25, ge=0, le=100)
    max_iterations_per_section: int = Field(5, ge=1, le=10)
    default_max_tokens: int = Field(6144, ge=100, le=8192)

    model_config = ConfigDict(env_prefix="GEN_")


class PathSettings(BaseSettings):
    """File path settings."""

    prompts_dir: Path = Field(default_factory=lambda: Path("generator/prompts"))
    cache_dir: Path = Field(default_factory=lambda: Path("generator/cache"))
    output_dir: Path = Field(default_factory=lambda: Path("app/(materials)/posts"))
    authors_dir: Path = Field(default_factory=lambda: Path("generator/authors"))

    @field_validator(
        "prompts_dir", "cache_dir", "output_dir", "authors_dir", mode="before"
    )
    @classmethod
    def resolve_path(cls, v):
        if isinstance(v, str):
            return Path(v).resolve()
        return v

    model_config = ConfigDict(env_prefix="PATH_")


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    log_level: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    log_file: Optional[Path] = Field(None)
    log_rotation: bool = Field(True)
    max_log_size_mb: int = Field(10, ge=1, le=100)
    backup_count: int = Field(5, ge=1, le=20)

    model_config = ConfigDict(env_prefix="LOG_")


class CacheSettings(BaseSettings):
    """Cache configuration."""

    enabled: bool = Field(True)
    max_age_hours: int = Field(24, ge=1, le=168)  # 1 hour to 1 week
    auto_cleanup: bool = Field(True)

    @property
    def max_age_seconds(self) -> float:
        """Get max age in seconds."""
        return self.max_age_hours * 3600

    model_config = ConfigDict(env_prefix="CACHE_")


class AppSettings(BaseSettings):
    """Main application settings."""

    api: APISettings = APISettings()
    generation: GenerationSettings = GenerationSettings()
    paths: PathSettings = PathSettings()
    logging: LoggingSettings = LoggingSettings()
    cache: CacheSettings = CacheSettings()

    # Global settings
    environment: str = Field(
        "development", pattern="^(development|staging|production)$"
    )
    debug: bool = Field(False)

    model_config = ConfigDict(env_file=".env", env_nested_delimiter="__", extra="allow")

    @field_validator("debug", mode="before")
    @classmethod
    def set_debug_from_env(cls, v, info):
        """Set debug mode based on environment."""
        if (
            info
            and hasattr(info, "data")
            and info.data.get("environment") == "development"
        ):
            return True
        return v

    def validate_setup(self) -> List[str]:
        """Validate the complete setup and return any errors."""
        errors = []

        # Check required directories
        for dir_name, dir_path in [
            ("prompts", self.paths.prompts_dir),
            ("cache", self.paths.cache_dir),
            ("output", self.paths.output_dir),
            ("authors", self.paths.authors_dir),
        ]:
            if not dir_path.exists():
                errors.append(f"{dir_name} directory does not exist: {dir_path}")

        # Check API keys
        if not any(
            [self.api.gemini_api_key, self.api.xai_api_key, self.api.deepseek_api_key]
        ):
            errors.append("At least one API key must be configured")

        return errors


# Global settings instance
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


def reload_settings() -> AppSettings:
    """Reload settings from environment."""
    global _settings
    _settings = AppSettings()
    return _settings
