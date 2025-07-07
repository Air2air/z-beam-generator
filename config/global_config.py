"""
Global Configuration Manager

Prevents hardcoding by providing centralized access to all configuration values.
All config values MUST come through this manager - NO HARDCODING ALLOWED!
"""

from typing import Any, Optional, Dict
from dataclasses import dataclass

# === EXCEPTIONS (merged from exceptions.py) ===
class ArticleGenerationError(Exception):
    """Base exception for article generation errors."""
    pass

class ConfigurationError(ArticleGenerationError):
    """Raised when there's a configuration-related error."""
    pass

class APIError(ArticleGenerationError):
    """Raised when there's an API-related error."""
    def __init__(self, message: str, provider: str = None, status_code: int = None):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code

class PromptError(ArticleGenerationError):
    """Raised when there's a prompt-related error."""
    pass

class ContentGenerationError(ArticleGenerationError):
    """Raised when content generation fails."""
    pass

class FileOperationError(ArticleGenerationError):
    """Raised when file operations fail."""
    pass

class GenerationError(ArticleGenerationError):
    """General generation process error."""
    pass

# Import logger when needed to avoid circular imports
def _get_logger():
    from modules.content_generator import get_logger
    return get_logger("global_config")


@dataclass
class TemperatureConfig:
    """Simple temperature configuration - consolidated from deleted domain model."""
    content_temp: float = 0.6
    detection_temp: float = 0.3
    improvement_temp: float = 0.7
    summary_temp: float = 0.4
    metadata_temp: float = 0.2
    
    def __post_init__(self):
        """Validate temperature values are in range 0.0-2.0."""
        for field_name in ['content_temp', 'detection_temp', 'improvement_temp', 'summary_temp', 'metadata_temp']:
            value = getattr(self, field_name)
            if not 0.0 <= value <= 2.0:
                raise ValueError(f"Temperature {field_name}={value} must be between 0.0 and 2.0")


class GlobalConfigManager:
    """
    Centralized configuration manager to prevent hardcoding.
    
    This is the SINGLE SOURCE OF TRUTH for all configuration values.
    If you need a config value, get it from here - DO NOT HARDCODING!
    """
    
    _instance: Optional['GlobalConfigManager'] = None
    _config: Dict[str, Any] = {}
    _provider_models: Dict[str, Any] = {}
    _temperature_config: Optional[TemperatureConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls, user_config: Dict[str, Any], provider_models: Dict[str, Any] = None) -> 'GlobalConfigManager':
        """Initialize the global config manager with user configuration and provider models."""
        instance = cls()
        instance._config = user_config.copy()
        instance._provider_models = provider_models or {}
        
        default_content_temp = instance._config.get("content_temp", 0.6)

        # Set intelligent defaults for optimization values if not provided
        optimization_defaults = {
            "ai_detection_threshold": 25,      # 25% max AI detection
            "natural_voice_threshold": 25,    # 25% max for natural voice
            "content_temp": default_content_temp,              # Default content creativity
            "detection_temp": 0.3,            # Low variance for detection
            "improvement_temp": 0.7,          # Higher creativity for improvements
            "summary_temp": 0.4,              # Moderate for summaries
            "metadata_temp": 0.2,             # Very consistent for metadata
            # Token limits compatible with DeepSeek API (max 8192)
            "max_content_tokens": 1500,       # Content generation
            "max_detection_tokens": 500,      # Detection responses  
            "max_metadata_tokens": 400,       # Metadata generation
            "max_api_tokens": 2000,           # Default API calls
            "max_small_response_tokens": 500, # Small responses
            "max_tiny_response_tokens": 50,   # Tiny responses 
            "max_large_response_tokens": 3000, # Large responses (reduced from 4000)
            "max_improvement_tokens": 4000,   # Content improvement (reduced from 8192)
        }
        
        # Apply defaults for missing optimization values
        for key, default_value in optimization_defaults.items():
            if key not in instance._config:
                instance._config[key] = default_value
        
        # Create temperature config from final settings
        instance._temperature_config = TemperatureConfig(
            content_temp=instance._config["content_temp"],
            detection_temp=instance._config["detection_temp"],
            improvement_temp=instance._config["improvement_temp"],
            summary_temp=instance._config["summary_temp"],
            metadata_temp=instance._config["metadata_temp"],
        )
        
        return instance
    
    @classmethod
    def get_instance(cls) -> 'GlobalConfigManager':
        """Get the global config manager instance."""
        if cls._instance is None:
            raise RuntimeError(
                "GlobalConfigManager not initialized! "
                "Call GlobalConfigManager.initialize(config) first."
            )
        return cls._instance
    
    # Core configuration getters
    def get_ai_detection_threshold(self) -> int:
        """Get AI detection threshold - NO HARDCODING!"""
        return self._config.get("ai_detection_threshold", 25)
    
    def get_natural_voice_threshold(self) -> int:
        """Get natural voice threshold - NO HARDCODING!"""
        return self._config.get("natural_voice_threshold", 25)
    
    def get_iterations_per_section(self) -> int:
        """Get iterations per section - NO HARDCODING!"""
        return self._config.get("iterations_per_section", 3)
    
    def get_max_article_words(self) -> int:
        """Get maximum article words - NO HARDCODING!"""
        return self._config.get("max_article_words", 1200)
    
    def get_api_timeout(self) -> int:
        """Get API timeout - NO HARDCODING!"""
        return self._config.get("api_timeout", 60)

    def get_overall_timeout(self) -> int:
        """Get overall operation timeout - NO HARDCODING!"""
        return self._config.get("overall_timeout", 300)

    # Basic configuration getters - NO HARDCODING!
    def get_material(self) -> str:
        """Get material from USER_CONFIG - NO HARDCODING!"""
        material = self._config.get("material")
        if not material:
            raise ConfigurationError(
                "Material not specified in USER_CONFIG. "
                "NO FALLBACKS - system must fail fast."
            )
        return material
    
    def get_generator_provider(self) -> str:
        """Get generator provider from USER_CONFIG - NO HARDCODING!"""
        provider = self._config.get("generator_provider")
        if not provider:
            raise ConfigurationError(
                "Generator provider not specified in USER_CONFIG. "
                "NO FALLBACKS - system must fail fast."
            )
        return provider
    
    def get_file_name(self) -> str:
        """Get file name from USER_CONFIG - NO HARDCODING!"""
        file_name = self._config.get("file_name")
        if not file_name:
            raise ConfigurationError(
                "File name not specified in USER_CONFIG. "
                "NO FALLBACKS - system must fail fast."
            )
        return file_name

    def get_temperature_config(self) -> TemperatureConfig:
        """Get temperature configuration - NO HARDCODING!"""
        if self._temperature_config is None:
            raise RuntimeError("Temperature config not initialized!")
        return self._temperature_config
    
    # Individual temperature getters
    def get_content_temperature(self) -> float:
        """Get content generation temperature - NO HARDCODING!"""
        return self.get_temperature_config().content_temp
    
    def get_detection_temperature(self) -> float:
        """Get detection temperature - NO HARDCODING!"""
        return self.get_temperature_config().detection_temp
    
    def get_improvement_temperature(self) -> float:
        """Get improvement temperature - NO HARDCODING!"""
        return self.get_temperature_config().improvement_temp
    
    def get_summary_temperature(self) -> float:
        """Get summary temperature - NO HARDCODING!"""
        return self.get_temperature_config().summary_temp
    
    def get_metadata_temperature(self) -> float:
        """Get metadata temperature - NO HARDCODING!"""
        return self.get_temperature_config().metadata_temp
    
    # Max tokens configuration - NO HARDCODING!
    def get_max_tokens(self) -> int:
        """Get max tokens per API request from USER_CONFIG - NO HARDCODING!"""
        return self._config.get("max_tokens", 4000)
    def get_max_content_tokens(self) -> int:
        """Get max tokens for content generation - NO HARDCODING!"""
        return self._config.get("max_content_tokens", 1500)
    
    def get_max_detection_tokens(self) -> int:
        """Get max tokens for detection responses - NO HARDCODING!"""
        return self._config.get("max_detection_tokens", 500)
    
    def get_max_metadata_tokens(self) -> int:
        """Get max tokens for metadata generation - NO HARDCODING!"""
        return self._config.get("max_metadata_tokens", 500)
    
    def get_max_api_tokens(self) -> int:
        """Get default max tokens for API calls - NO HARDCODING!"""
        return self._config.get("max_api_tokens", 3000)
    
    def get_max_small_response_tokens(self) -> int:
        """Get max tokens for small responses (research, etc.) - NO HARDCODING!"""
        return self._config.get("max_small_response_tokens", 500)
    
    def get_max_tiny_response_tokens(self) -> int:
        """Get max tokens for tiny responses (detection scores, etc.) - NO HARDCODING!"""
        return self._config.get("max_tiny_response_tokens", 50)
    
    def get_max_large_response_tokens(self) -> int:
        """Get max tokens for large responses (natural voice detection, etc.) - NO HARDCODING!"""
        return self._config.get("max_large_response_tokens", 3000)
    
    def get_max_improvement_tokens(self) -> int:
        """Get max tokens for content improvement - NO HARDCODING!"""
        return self._config.get("max_improvement_tokens", 4000)
    
    # Operation timeout configuration - NO HARDCODING!
    def get_prompt_selection_timeout(self) -> int:
        """Get timeout for prompt selection operations - NO HARDCODING!"""
        return self._config.get("prompt_selection_timeout", 10)
    
    # Detection threshold configuration - NO HARDCODING!
    def get_excellent_ai_threshold(self) -> int:
        """Get threshold for excellent AI detection scores - NO HARDCODING!"""
        return self._config.get("excellent_ai_threshold", 25)
    
    def get_low_natural_voice_threshold(self) -> int:
        """Get low threshold for natural voice detection - NO HARDCODING!"""
        return self._config.get("low_natural_voice_threshold", 15)
    
    def get_high_natural_voice_threshold(self) -> int:
        """Get high threshold for natural voice detection - NO HARDCODING!"""
        return self._config.get("high_natural_voice_threshold", 25)
    
    def get_voice_imbalance_threshold(self) -> int:
        """Get threshold for voice imbalance detection - NO HARDCODING!"""
        return self._config.get("voice_imbalance_threshold", 30)
    
    def get_score_balance_thresholds(self) -> Dict[str, int]:
        """Get all score balance thresholds - NO HARDCODING!"""
        return {
            "excellent_ai": self.get_excellent_ai_threshold(),
            "low_nv": self.get_low_natural_voice_threshold(),
            "high_nv": self.get_high_natural_voice_threshold(),
            "voice_imbalance": self.get_voice_imbalance_threshold()
        }
    
    # Content scoring thresholds - NO HARDCODING!
    def get_high_ai_score_threshold(self) -> int:
        """Get threshold for high AI scores - NO HARDCODING!"""
        return self._config.get("high_ai_score_threshold", 50)
    
    def get_low_quality_threshold(self) -> int:
        """Get threshold for low quality content - NO HARDCODING!"""
        return self._config.get("low_quality_threshold", 30)
    
    def get_moderate_quality_threshold(self) -> int:
        """Get threshold for moderate quality content - NO HARDCODING!"""
        return self._config.get("moderate_quality_threshold", 40)
    
    def get_very_high_score_threshold(self) -> int:
        """Get threshold for very high scores - NO HARDCODING!"""
        return self._config.get("very_high_score_threshold", 70)
    
    def get_content_scoring_thresholds(self) -> Dict[str, int]:
        """Get all content scoring thresholds - NO HARDCODING!"""
        return {
            "high_ai": self.get_high_ai_score_threshold(),
            "low_quality": self.get_low_quality_threshold(),
            "moderate_quality": self.get_moderate_quality_threshold(),
            "very_high": self.get_very_high_score_threshold()
        }
    
    # Provider configuration
    def get_generator_provider(self) -> str:
        """Get the generator provider."""
        provider = self._config.get("generator_provider")
        if not provider:
            raise ConfigurationError(
                "Generator provider not configured in USER_CONFIG. "
                "NO FALLBACKS - system must fail fast."
            )
        return provider
    
    def get_detection_provider(self) -> str:
        """Get detection provider - NO HARDCODING!"""
        return self._config.get("detection_provider", "DEEPSEEK")
    
    # === Content Generation Parameters ===
    
    def get_material(self) -> str:
        """Get the material for content generation."""
        material = self._config.get("material")
        if not material:
            raise ConfigurationError(
                "Material not configured in USER_CONFIG. "
                "NO FALLBACKS - system must fail fast."
            )
        return material
    
    def get_category(self) -> str:
        """Get the content category."""
        category = self._config.get("category")
        if not category:
            raise ConfigurationError(
                "Category not configured in USER_CONFIG. "
                "NO FALLBACKS - system must fail fast."
            )
        return category
    
    def get_filename(self) -> str:
        """Get the output filename."""
        filename = self._config.get("file_name")
        if not filename:
            raise ConfigurationError(
                "File name not configured in USER_CONFIG. "
                "NO FALLBACKS - system must fail fast."
            )
        return filename
    
    def get_author(self) -> str:
        """Get the author for content generation."""
        author = self._config.get("author")
        if not author:
            raise ConfigurationError(
                "Author not configured in USER_CONFIG. "
                "NO FALLBACKS - system must fail fast."
            )
        return author
    
    def get_generator_model(self) -> str:
        """Get the generator model from provider models."""
        provider = self.get_generator_provider()
        if provider not in self._provider_models:
            raise ConfigurationError(
                f"Provider '{provider}' not found in PROVIDER_MODELS. "
                "NO FALLBACKS - system must fail fast."
            )
        
        model = self._provider_models[provider].get("model")
        if not model:
            raise ConfigurationError(
                f"Model not configured for provider '{provider}'. "
                "NO FALLBACKS - system must fail fast."
            )
        return model

    def get_api_key_mappings(self) -> Dict[str, str]:
        """Get API key environment variable mappings."""
        mappings = self._config.get("api_key_mappings")
        if not mappings:
            raise ConfigurationError(
                "API key mappings not configured in USER_CONFIG. "
                "NO FALLBACKS - system must fail fast."
            )
        return mappings

    def get_api_keys(self) -> Dict[str, str]:
        """Get API keys from environment variables using configured mappings."""
        import os
        
        mappings = self.get_api_key_mappings()
        api_keys = {}
        
        for provider_key, env_var in mappings.items():
            api_key = os.environ.get(env_var)
            if api_key:
                api_keys[provider_key] = api_key
            else:
                # Use lazy logger import to avoid circular imports
                logger = _get_logger()
                logger.warning(f"API key not found in environment: {env_var}")
        
        return api_keys

    def get_generator_url_template(self) -> str:
        """Get the URL template for the generator provider."""
        provider = self.get_generator_provider()
        if provider not in self._provider_models:
            raise ConfigurationError(
                f"Provider '{provider}' not found in PROVIDER_MODELS. "
                "NO FALLBACKS - system must fail fast."
            )
        
        url_template = self._provider_models[provider].get("url_template")
        if not url_template:
            raise ConfigurationError(
                f"URL template not configured for provider '{provider}'. "
                "NO FALLBACKS - system must fail fast."
            )
        return url_template

    # Generic getter for any config value
    def get(self, key: str, default: Any = None) -> Any:
        """Get any configuration value - NO HARDCODING!"""
        return self._config.get(key, default)
    
    # Dynamic configuration updates (for training integration)
    def update_ai_detection_threshold(self, new_threshold: int) -> None:
        """Update AI detection threshold dynamically (e.g., from training insights)."""
        if not (0 <= new_threshold <= 100):
            raise ValueError(f"AI detection threshold must be 0-100, got {new_threshold}")
        self._config["ai_detection_threshold"] = new_threshold
        
    def update_natural_voice_threshold(self, new_threshold: int) -> None:
        """Update natural voice threshold dynamically (e.g., from training insights)."""
        if not (0 <= new_threshold <= 100):
            raise ValueError(f"Natural voice threshold must be 0-100, got {new_threshold}")
        self._config["natural_voice_threshold"] = new_threshold
        
    def update_temperature(self, temp_type: str, new_temp: float) -> None:
        """Update a specific temperature value dynamically."""
        if not (0.0 <= new_temp <= 2.0):
            raise ValueError(f"Temperature must be 0.0-2.0, got {new_temp}")
            
        temp_key = f"{temp_type}_temp"
        if temp_key not in ["content_temp", "detection_temp", "improvement_temp", "summary_temp", "metadata_temp"]:
            raise ValueError(f"Unknown temperature type: {temp_type}")
            
        self._config[temp_key] = new_temp
        
        # Rebuild temperature config
        self._temperature_config = TemperatureConfig(
            content_temp=self._config["content_temp"],
            detection_temp=self._config["detection_temp"],
            improvement_temp=self._config["improvement_temp"],
            summary_temp=self._config["summary_temp"],
            metadata_temp=self._config["metadata_temp"],
        )
        
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of current optimization settings."""
        return {
            "ai_detection_threshold": self.get_ai_detection_threshold(),
            "natural_voice_threshold": self.get_natural_voice_threshold(),
            "iterations_per_section": self.get_iterations_per_section(),
            "temperatures": {
                "content": self.get_content_temperature(),
                "detection": self.get_detection_temperature(),
                "improvement": self.get_improvement_temperature(),
                "summary": self.get_summary_temperature(),
                "metadata": self.get_metadata_temperature(),
            }
        }
    
    # Validation methods
    def validate_thresholds(self) -> None:
        """Validate that thresholds are reasonable."""
        ai_threshold = self.get_ai_detection_threshold()
        nv_threshold = self.get_natural_voice_threshold()
        
        if not (0 <= ai_threshold <= 100):
            raise ValueError(f"AI detection threshold must be 0-100, got {ai_threshold}")
        
        if not (0 <= nv_threshold <= 100):
            raise ValueError(f"Natural voice threshold must be 0-100, got {nv_threshold}")
    
    def validate_temperatures(self) -> None:
        """Validate that temperatures are reasonable."""
        temp_config = self.get_temperature_config()
        
        for temp_name, temp_value in [
            ("content_temp", temp_config.content_temp),
            ("detection_temp", temp_config.detection_temp),
            ("improvement_temp", temp_config.improvement_temp),
            ("summary_temp", temp_config.summary_temp),
            ("metadata_temp", temp_config.metadata_temp),
        ]:
            if not (0.0 <= temp_value <= 2.0):
                raise ValueError(f"{temp_name} must be 0.0-2.0, got {temp_value}")
    
    def validate_providers(self) -> None:
        """Validate that configured providers exist."""
        generator_provider = self.get_generator_provider()
        detection_provider = self.get_detection_provider()
        
        if not self.validate_provider(generator_provider):
            available = list(self._provider_models.keys())
            raise ValueError(f"Generator provider '{generator_provider}' not configured. Available: {available}")
        
        if not self.validate_provider(detection_provider):
            available = list(self._provider_models.keys())
            raise ValueError(f"Detection provider '{detection_provider}' not configured. Available: {available}")
    
    def validate_all(self) -> None:
        """Validate all configuration values."""
        self.validate_thresholds()
        self.validate_temperatures()
        self.validate_providers()

    # === Single-Pass Template Architecture Configuration ===
    
    def get_generator_version(self) -> str:
        """Get the current generator version."""
        return self._config.get("generator_version", "2.0.0-single-pass")
    
    def get_default_section_words(self) -> int:
        """Get default word target for sections."""
        return self._config.get("default_section_words", 150)
    
    def get_section_order(self) -> list:
        """Get the preferred order for assembling sections."""
        default_order = [
            "introduction",
            "technical_overview", 
            "applications",
            "safety_guidelines",
            "conclusion"
        ]
        return self._config.get("section_order", default_order)
    
    def get_supported_categories(self) -> list:
        """Get list of supported content categories."""
        default_categories = ["application", "author", "material", "region", "thesaurus"]
        return self._config.get("supported_categories", default_categories)
    
    def get_thesaurus_terms(self) -> list:
        """Get thesaurus terms for crosslinking."""
        default_terms = [
            "laser cleaning", "ablation", "surface preparation", "contaminant removal",
            "oxide removal", "rust removal", "paint stripping", "coating removal",
            "precision cleaning", "non-contact cleaning", "eco-friendly cleaning"
        ]
        return self._config.get("thesaurus_terms", default_terms)
    
    def get_content_quality_threshold(self) -> float:
        """Get minimum content quality threshold (0.0 to 1.0)."""
        return self._config.get("content_quality_threshold", 0.8)
    
    def get_technical_depth_level(self) -> str:
        """Get technical depth level for content."""
        return self._config.get("technical_depth_level", "intermediate")
    
    def get_retry_count(self) -> int:
        """Get API retry count."""
        return self._config.get("retry_count", 3)
    
    # === OPTIMIZATION MODE CONFIGURATION ===
    def get_optimization_mode(self) -> str:
        """Get optimization mode: speed_focused or quality_focused."""
        return self._config.get("optimization_mode", "speed_focused")
    
    def is_real_time_optimization_enabled(self) -> bool:
        """Check if real-time optimization during production is enabled."""
        return self._config.get("enable_real_time_optimization", False)
    
    def get_quality_retry_attempts(self) -> int:
        """Get number of retry attempts if quality is below threshold."""
        return self._config.get("quality_retry_attempts", 1)
    
    def is_section_scoring_enabled(self) -> bool:
        """Check if section-level scoring during generation is enabled."""
        return self._config.get("enable_section_scoring", False)
    
    def get_scoring_threshold_ai(self) -> int:
        """Get AI detection threshold for quality optimization."""
        return self._config.get("scoring_threshold_ai", 25)
    
    def get_scoring_threshold_nv(self) -> int:
        """Get natural voice threshold for quality optimization."""
        return self._config.get("scoring_threshold_nv", 20)
    
    def is_quality_focused_mode(self) -> bool:
        """Check if system is in quality-focused mode (slower but better)."""
        return self.get_optimization_mode() == "quality_focused"
    
    def is_speed_focused_mode(self) -> bool:
        """Check if system is in speed-focused mode (faster but simpler)."""
        return self.get_optimization_mode() == "speed_focused"


# Convenience function for getting the global config manager
def get_config() -> GlobalConfigManager:
    """Get the global configuration manager instance."""
    return GlobalConfigManager.get_instance()


# Decorator to ensure config is available
def requires_config(func):
    """Decorator to ensure global config is available before function execution."""
    def wrapper(*args, **kwargs):
        try:
            get_config()
        except RuntimeError:
            raise RuntimeError(
                f"Function {func.__name__} requires GlobalConfigManager to be initialized. "
                "Call GlobalConfigManager.initialize(config) first."
            )
        return func(*args, **kwargs)
    return wrapper
