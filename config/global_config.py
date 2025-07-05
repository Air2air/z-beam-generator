"""
Global Configuration Manager

Prevents hardcoding by providing centralized access to all configuration values.
All config values MUST come through this manager - NO HARDCODING ALLOWED!
"""

from typing import Any, Optional, Dict
from core.domain.models import TemperatureConfig


class GlobalConfigManager:
    """
    Centralized configuration manager to prevent hardcoding.
    
    This is the SINGLE SOURCE OF TRUTH for all configuration values.
    If you need a config value, get it from here - DO NOT HARDCODE!
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
        
        # Set intelligent defaults for optimization values if not provided
        optimization_defaults = {
            "ai_detection_threshold": 25,      # 25% max AI detection
            "natural_voice_threshold": 25,    # 25% max for natural voice
            "content_temp": 0.6,              # Balanced creativity for content
            "detection_temp": 0.3,            # Low variance for detection
            "improvement_temp": 0.7,          # Higher creativity for improvements
            "summary_temp": 0.4,              # Moderate for summaries
            "metadata_temp": 0.2,             # Very consistent for metadata
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
        return self._config.get("max_large_response_tokens", 4000)
    
    def get_max_improvement_tokens(self) -> int:
        """Get max tokens for content improvement - NO HARDCODING!"""
        return self._config.get("max_improvement_tokens", 8192)
    
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
        """Get generator provider - NO HARDCODING!"""
        return self._config.get("generator_provider", "DEEPSEEK")
    
    def get_detection_provider(self) -> str:
        """Get detection provider - NO HARDCODING!"""
        return self._config.get("detection_provider", "DEEPSEEK")
    
    # Material and content settings
    def get_material(self) -> str:
        """Get material - NO HARDCODING!"""
        return self._config.get("material", "Unknown")
    
    def get_category(self) -> str:
        """Get category - NO HARDCODING!"""
        return self._config.get("category", "Material")
    
    def get_file_name(self) -> str:
        """Get output file name - NO HARDCODING!"""
        return self._config.get("file_name", "output.mdx")
    
    def get_author(self) -> str:
        """Get author - NO HARDCODING!"""
        return self._config.get("author", "default_author.mdx")
    
    def get_force_regenerate(self) -> bool:
        """Get force regenerate flag - NO HARDCODING!"""
        return self._config.get("force_regenerate", True)
    
    # API Provider Configuration - NO HARDCODING!
    def get_available_providers(self) -> Dict[str, Any]:
        """Get all available providers and models - NO HARDCODING!"""
        return self._provider_models.copy()
    
    def get_provider_model(self, provider: str) -> str:
        """Get model name for a provider - NO HARDCODING!"""
        provider_config = self._provider_models.get(provider.upper(), {})
        return provider_config.get("model", "unknown-model")
    
    def get_provider_url(self, provider: str) -> str:
        """Get API URL template for a provider - NO HARDCODING!"""
        provider_config = self._provider_models.get(provider.upper(), {})
        return provider_config.get("url_template", "")
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get full configuration for a provider - NO HARDCODING!"""
        return self._provider_models.get(provider.upper(), {})
    
    def validate_provider(self, provider: str) -> bool:
        """Validate that a provider is configured - NO HARDCODING!"""
        return provider.upper() in self._provider_models
    
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
