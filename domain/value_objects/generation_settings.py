"""
Value objects for generation settings in the Z-Beam domain.
These encapsulate configuration and behavior settings for content generation.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class Provider(Enum):
    """Enumeration of supported AI providers."""
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    XAI = "xai"
    ANTHROPIC = "anthropic"


class DetectionMode(Enum):
    """Enumeration of detection modes."""
    COMPREHENSIVE = "comprehensive"  # Both AI and human detection
    AI_ONLY = "ai_only"             # Only AI detection
    HUMAN_ONLY = "human_only"       # Only human-like detection
    DISABLED = "disabled"           # No detection


@dataclass(frozen=True)
class TemperatureSettings:
    """Value object for temperature configuration across different operations."""
    
    content_generation: float
    ai_detection: float
    human_detection: float
    improvement: float
    summary: float
    metadata: float
    
    def __post_init__(self):
        """Validate temperature settings."""
        temperatures = [
            self.content_generation,
            self.ai_detection,
            self.human_detection,
            self.improvement,
            self.summary,
            self.metadata
        ]
        
        for temp in temperatures:
            if not 0.0 <= temp <= 2.0:
                raise ValueError(f"Temperature {temp} must be between 0.0 and 2.0")
    
    def get_for_operation(self, operation: str) -> float:
        """Get temperature for a specific operation."""
        operation_map = {
            "content": self.content_generation,
            "ai_detection": self.ai_detection,
            "human_detection": self.human_detection,
            "improvement": self.improvement,
            "summary": self.summary,
            "metadata": self.metadata,
        }
        return operation_map.get(operation, self.content_generation)


@dataclass(frozen=True)
class ThresholdSettings:
    """Value object for detection thresholds."""
    
    ai_threshold: float  # Maximum acceptable AI-like score (0-100)
    human_threshold: float  # Minimum acceptable human-like score (0-100)
    confidence_threshold: float = 0.8  # Minimum confidence for decisions
    
    def __post_init__(self):
        """Validate threshold settings."""
        if not 0 <= self.ai_threshold <= 100:
            raise ValueError("AI threshold must be between 0 and 100")
        
        if not 0 <= self.human_threshold <= 100:
            raise ValueError("Human threshold must be between 0 and 100")
        
        if not 0 <= self.confidence_threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0 and 1")
    
    def passes_ai_threshold(self, ai_score: float) -> bool:
        """Check if an AI score passes the threshold."""
        return ai_score <= self.ai_threshold
    
    def passes_human_threshold(self, human_score: float) -> bool:
        """Check if a human score passes the threshold."""
        return human_score >= self.human_threshold
    
    def passes_both_thresholds(self, ai_score: float, human_score: float) -> bool:
        """Check if both thresholds are satisfied."""
        return self.passes_ai_threshold(ai_score) and self.passes_human_threshold(human_score)


@dataclass(frozen=True)
class APISettings:
    """Value object for API configuration."""
    
    provider: Provider
    model: Optional[str] = None
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    max_tokens: int = 3000
    
    def __post_init__(self):
        """Validate API settings."""
        if self.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")
        
        if self.retry_delay_seconds < 0:
            raise ValueError("Retry delay cannot be negative")
        
        if self.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
    
    def get_provider_name(self) -> str:
        """Get the provider name as string."""
        return self.provider.value
    
    def should_retry(self, attempt: int) -> bool:
        """Check if a retry should be attempted."""
        return attempt <= self.max_retries


@dataclass(frozen=True)
class GenerationSettings:
    """Value object encapsulating all generation settings."""
    
    temperature_settings: TemperatureSettings
    threshold_settings: ThresholdSettings
    api_settings: APISettings
    detection_mode: DetectionMode = DetectionMode.COMPREHENSIVE
    max_iterations_per_section: int = 5
    enable_caching: bool = True
    enable_logging: bool = True
    debug_mode: bool = False
    custom_settings: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate generation settings."""
        if self.max_iterations_per_section <= 0:
            raise ValueError("Max iterations per section must be positive")
    
    def get_temperature_for_operation(self, operation: str) -> float:
        """Get temperature setting for a specific operation."""
        return self.temperature_settings.get_for_operation(operation)
    
    def should_run_ai_detection(self) -> bool:
        """Check if AI detection should be run."""
        return self.detection_mode in [DetectionMode.COMPREHENSIVE, DetectionMode.AI_ONLY]
    
    def should_run_human_detection(self) -> bool:
        """Check if human detection should be run."""
        return self.detection_mode in [DetectionMode.COMPREHENSIVE, DetectionMode.HUMAN_ONLY]
    
    def should_run_detection(self) -> bool:
        """Check if any detection should be run."""
        return self.detection_mode != DetectionMode.DISABLED
    
    def get_custom_setting(self, key: str, default=None):
        """Get a custom setting value."""
        if not self.custom_settings:
            return default
        return self.custom_settings.get(key, default)
    
    def with_custom_setting(self, key: str, value: Any) -> 'GenerationSettings':
        """Create a new instance with an additional custom setting."""
        current_custom = self.custom_settings or {}
        new_custom = {**current_custom, key: value}
        
        # Create new instance with updated custom settings
        return GenerationSettings(
            temperature_settings=self.temperature_settings,
            threshold_settings=self.threshold_settings,
            api_settings=self.api_settings,
            detection_mode=self.detection_mode,
            max_iterations_per_section=self.max_iterations_per_section,
            enable_caching=self.enable_caching,
            enable_logging=self.enable_logging,
            debug_mode=self.debug_mode,
            custom_settings=new_custom
        )
    
    @classmethod
    def create_default(cls, provider: Provider = Provider.GEMINI) -> 'GenerationSettings':
        """Create default generation settings."""
        temperature_settings = TemperatureSettings(
            content_generation=0.6,
            ai_detection=0.3,
            human_detection=0.3,
            improvement=0.7,
            summary=0.4,
            metadata=0.2
        )
        
        threshold_settings = ThresholdSettings(
            ai_threshold=25.0,
            human_threshold=25.0,
            confidence_threshold=0.8
        )
        
        api_settings = APISettings(
            provider=provider,
            timeout_seconds=30,
            max_retries=3,
            max_tokens=3000
        )
        
        return cls(
            temperature_settings=temperature_settings,
            threshold_settings=threshold_settings,
            api_settings=api_settings,
            detection_mode=DetectionMode.COMPREHENSIVE,
            max_iterations_per_section=5,
            enable_caching=True,
            enable_logging=True,
            debug_mode=False
        )
