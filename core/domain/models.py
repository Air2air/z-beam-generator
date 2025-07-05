"""
Domain models for the Z-Beam generator.
These represent the core business entities and value objects.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


def _get_config_value(config_method_name, default_value):
    """Helper to safely get config values with fallback."""
    try:
        from config.global_config import get_config
        config = get_config()
        return getattr(config, config_method_name)()
    except Exception:
        return default_value


@dataclass(frozen=True)
class TemperatureConfig:
    """Configuration for temperature settings in different contexts.

    Temperature controls randomness/creativity in AI responses:
    - Low (0.1-0.3): Predictable, consistent, analytical
    - Medium (0.4-0.7): Balanced creativity and consistency
    - High (0.8+): Creative, varied, potentially less focused
    """

    content_temp: float = None  # For generating article content
    detection_temp: float = None  # For detection analysis
    improvement_temp: float = None  # For improvement iterations
    summary_temp: float = None  # For summary generation
    metadata_temp: float = None  # For structured metadata

    def __post_init__(self):
        # Set default values from config if not provided
        if self.content_temp is None:
            object.__setattr__(
                self,
                "content_temp",
                _get_config_value('get_content_temperature', 0.6),
            )
        if self.detection_temp is None:
            object.__setattr__(
                self,
                "detection_temp",
                _get_config_value('get_detection_temperature', 0.3),
            )
        if self.improvement_temp is None:
            object.__setattr__(
                self,
                "improvement_temp",
                _get_config_value('get_improvement_temperature', 0.7),
            )
        if self.summary_temp is None:
            object.__setattr__(
                self,
                "summary_temp",
                _get_config_value('get_summary_temperature', 0.4),
            )
        if self.metadata_temp is None:
            object.__setattr__(
                self,
                "metadata_temp",
                _get_config_value('get_metadata_temperature', 0.2),
            )

        # Validate all temperatures are in valid range
        for name, value in [
            ("content_temp", self.content_temp),
            ("detection_temp", self.detection_temp),
            ("improvement_temp", self.improvement_temp),
            ("summary_temp", self.summary_temp),
            ("metadata_temp", self.metadata_temp),
        ]:
            if not 0.0 <= value <= 2.0:
                raise ValueError(
                    f"Temperature {name} must be between 0.0 and 2.0, got {value}"
                )

    @classmethod
    def from_legacy_config(cls, content_temp: float, detection_temp: float = None):
        """Create from legacy config values."""
        detection_temp = (
            detection_temp if detection_temp is not None else min(0.3, content_temp)
        )
        return cls(content_temp=content_temp, detection_temp=detection_temp)

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            "content_temp": self.content_temp,
            "detection_temp": self.detection_temp,
            "improvement_temp": self.improvement_temp,
            "summary_temp": self.summary_temp,
            "metadata_temp": self.metadata_temp,
        }


class DetectionResult(Enum):
    """Result of AI/human detection analysis."""

    PASS = "pass"
    FAIL = "fail"
    THRESHOLD_MET = "threshold_met"


class ProviderType(Enum):
    """Supported AI providers."""

    GEMINI = "GEMINI"
    XAI = "XAI"
    DEEPSEEK = "DEEPSEEK"


class SectionType(Enum):
    """Types of content sections."""

    TEXT = "text"
    TABLE = "table"
    CHART = "chart"
    LIST = "list"
    COMPARISON = "comparison"


@dataclass(frozen=True)
class AIScore:
    """Result of AI detection analysis."""

    score: int
    feedback: str
    iteration: int
    detection_type: str  # "ai" or "human"

    def __post_init__(self):
        if not 0 <= self.score <= 100:
            raise ValueError(f"Score must be between 0-100, got {self.score}")
        if self.iteration < 1:
            raise ValueError(f"Iteration must be >= 1, got {self.iteration}")


@dataclass(frozen=True)
class SectionConfig:
    """Configuration for a content section."""

    name: str
    ai_detect: bool
    prompt_file: str
    section_type: SectionType
    generate: bool = True
    order: int = 0

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Section name cannot be empty")
        if not self.prompt_file.strip():
            raise ValueError("Prompt file cannot be empty")


@dataclass
class GenerationRequest:
    """Request for content generation."""

    material: str
    sections: List[str]
    provider: ProviderType
    model: str
    ai_detection_threshold: int
    human_detection_threshold: int
    iterations_per_section: int = None  # Will use get_config().get_iterations_per_section()
    temperature: float = None  # Legacy field, will use config
    max_tokens: int = 6144
    force_regenerate: bool = False
    api_timeout: int = None  # Will use get_config().get_api_timeout()
    detection_temperature: float = None  # Legacy field, will use config
    temperature_config: Optional[TemperatureConfig] = None

    def __post_init__(self):
        # Set defaults from config if not provided
        if self.iterations_per_section is None:
            self.iterations_per_section = _get_config_value('get_iterations_per_section', 3)
        if self.temperature is None:
            self.temperature = _get_config_value('get_content_temperature', 1.0)
        if self.api_timeout is None:
            self.api_timeout = _get_config_value('get_api_timeout', 60)
        if self.detection_temperature is None:
            self.detection_temperature = _get_config_value('get_detection_temperature', 0.3)
            
        if not self.material.strip():
            raise ValueError("Material cannot be empty")
        if not self.sections:
            raise ValueError("At least one section must be specified")
        if not 0 <= self.ai_detection_threshold <= 100:
            raise ValueError("AI detection threshold must be 0-100")
        if not 0 <= self.human_detection_threshold <= 100:
            raise ValueError("Human detection threshold must be 0-100")
        if self.iterations_per_section < 1:
            raise ValueError("Iterations per section must be >= 1")

        # Create temperature_config if not provided (from legacy fields)
        if self.temperature_config is None:
            self.temperature_config = TemperatureConfig.from_legacy_config(
                content_temp=self.temperature, detection_temp=self.detection_temperature
            )


@dataclass
@dataclass
class GenerationContext:
    """Context for content generation including variables and metadata."""

    material: str
    content_type: str
    variables: Dict[str, Any] = field(default_factory=dict)
    material_details: Optional[Dict[str, Any]] = None
    article_data: Optional[Dict[str, Any]] = None
    cache_data: Optional[Dict[str, Any]] = None

    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a variable with optional default."""
        return self.variables.get(key, default)

    def set_variable(self, key: str, value: Any) -> None:
        """Set a variable in the context."""
        self.variables[key] = value


@dataclass
class GenerationResult:
    """Result of content generation."""

    content: str
    ai_score: Optional[AIScore] = None
    human_score: Optional[AIScore] = None
    threshold_met: bool = False
    iterations_completed: int = 0
    metadata: Optional[Dict[str, Any]] = None

    @property
    def final_ai_score(self) -> Optional[int]:
        """Get the final AI detection score."""
        return self.ai_score.score if self.ai_score else None

    @property
    def final_human_score(self) -> Optional[int]:
        """Get the final human detection score."""
        return self.human_score.score if self.human_score else None


@dataclass
class ArticleMetadata:
    """Metadata for generated articles."""

    title: str
    material: str
    file_name: str
    provider: ProviderType
    model: str
    author: str
    temperature: float
    publish_date: str
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    description: Optional[str] = None
    image_url: Optional[str] = None

    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert to YAML frontmatter dictionary."""
        return {
            "title": self.title,
            "nameShort": self.material,
            "description": self.description,
            "publishedAt": self.publish_date,
            "authors": [self.author],
            "tags": self.tags,
            "keywords": self.keywords,
            "image": self.image_url,
        }


@dataclass
class PromptTemplate:
    """A prompt template with metadata."""

    name: str
    category: str
    content: str
    variables: List[str] = field(default_factory=list)

    def format(self, **kwargs) -> str:
        """Format the template with provided variables."""
        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable {e} for prompt {self.name}")


@dataclass
class CacheEntry:
    """Cache entry for generated content."""

    key: str
    content: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self, max_age_seconds: float) -> bool:
        """Check if the cache entry is expired."""
        import time

        return (time.time() - self.timestamp) > max_age_seconds
        """Convert to dictionary for serialization."""
        return {
            "content_generation": self.content_generation,
            "detection": self.detection,
            "improvement": self.improvement,
        }
