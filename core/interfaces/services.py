"""
Service interfaces for the article generation system.
These interfaces define the contracts that implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from config.global_config import get_config
from core.domain.models import (
    GenerationRequest,
    GenerationContext,
    GenerationResult,
    AIScore,
    SectionConfig,
    PromptTemplate,
    TemperatureConfig,
)


class IContentService(ABC):
    """Interface for content generation services."""

    @abstractmethod
    def generate_content(
        self, request: GenerationRequest, context: GenerationContext
    ) -> GenerationResult:
        """Generate content based on the request and context."""
        pass


class IDetectionService(ABC):
    """Interface for AI detection services."""

    @abstractmethod
    def detect_ai_likelihood(
        self,
        content: str,
        context: GenerationContext,
        iteration: int = 1,
        temperature: Optional[float] = None,  # Use get_config().get_detection_temperature() if None
        timeout: Optional[int] = None,  # Use get_config().get_api_timeout() if None
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> AIScore:
        """Detect AI-like characteristics in content."""
        pass

    @abstractmethod
    def detect_human_likelihood(
        self,
        content: str,
        context: GenerationContext,
        iteration: int = 1,
        temperature: float = None,  # Will use get_config().get_detection_temperature()
        timeout: int = None,  # Will use get_config().get_api_timeout()
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> AIScore:
        """Detect Natural Voice characteristics in content."""
        pass

    @abstractmethod
    def detect_ai_patterns(
        self,
        content: str,
        context: GenerationContext,
        iteration: int = 1,
        temperature: float = None,  # Will use get_config().get_detection_temperature()
        timeout: int = None,  # Will use get_config().get_api_timeout()
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> AIScore:
        """Detect AI-generated patterns in content (new method)."""
        pass

    @abstractmethod
    def detect_natural_voice_authenticity(
        self,
        content: str,
        context: GenerationContext,
        iteration: int = 1,
        temperature: float = None,  # Will use get_config().get_detection_temperature()
        timeout: int = None,  # Will use get_config().get_api_timeout()
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> AIScore:
        """Detect Natural Voice authenticity in content (new method)."""
        pass

    @abstractmethod
    def run_comprehensive_detection(
        self,
        content: str,
        context: GenerationContext,
        ai_threshold: int,
        natural_voice_threshold: int,
        iteration: int = 1,
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> Dict[str, Any]:
        """Run comprehensive detection with both AI and Natural Voice analysis."""
        pass


class IAPIClient(ABC):
    """Interface for AI API clients."""

    @abstractmethod
    def call_api(
        self,
        prompt: str,
        model: str = None,
        temperature: float = None,  # Will use get_config().get_content_temperature()
        max_tokens: int = 3000,
        timeout: int = None,  # Will use get_config().get_api_timeout()
    ) -> str:
        """Call the AI API with the given parameters."""
        pass

    @abstractmethod
    def call_ai_api(
        self,
        prompt: str,
        model: str = None,
        temperature: float = None,  # Will use get_config().get_content_temperature()
        max_tokens: int = 3000,
        timeout: int = None,  # Will use get_config().get_api_timeout()
    ) -> str:
        """Legacy method name for backward compatibility."""
        pass


class IPromptRepository(ABC):
    """Interface for prompt storage and retrieval."""

    @abstractmethod
    def get_prompt(self, name: str, category: str = None) -> Optional[PromptTemplate]:
        """Get a prompt template by name and optional category."""
        pass

    @abstractmethod
    def list_prompts(self, category: str = None) -> List[str]:
        """List available prompt names, optionally filtered by category."""
        pass

    @abstractmethod
    def get_sections_config(self) -> Dict[str, SectionConfig]:
        """Get all section configurations."""
        pass

    @abstractmethod
    def get_section_config(self, section_name: str) -> Optional[SectionConfig]:
        """Get configuration for a specific section."""
        pass


class IPromptManager(ABC):
    """Interface for prompt management and loading."""

    @abstractmethod
    def load_prompt(self, filename: str, category: str = None) -> str:
        """Load a prompt from file."""
        pass

    @abstractmethod
    def get_prompt_content(self, prompt_name: str, category: str = None) -> str:
        """Get prompt content by name."""
        pass


class IContentGenerator(ABC):
    """Interface for content generation."""

    @abstractmethod
    def generate_section_content(
        self,
        section_name: str,
        material: str,
        generation_context: Dict[str, Any],
        api_client: IAPIClient,
        prompt_manager: IPromptManager,
        ai_detection_threshold: int,
        human_detection_threshold: int,
        iterations_per_section: int = None,  # Will use get_config().get_iterations_per_section()
        temperature: float = None,  # Will use get_config().get_content_temperature()
        timeout: int = None,  # Will use get_config().get_api_timeout()
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> Dict[str, Any]:
        """Generate content for a specific section."""
        pass


class IArticleGenerator(ABC):
    """Interface for article generation."""

    @abstractmethod
    def generate_article(
        self,
        config: Any,
        ai_detection_threshold: int,
        human_detection_threshold: int,
        iterations_per_section: int = None,  # Will use get_config().get_iterations_per_section()
        force_regenerate: bool = False,
        max_article_words: int = None,  # Will use get_config().get_max_article_words()
        api_timeout: int = None,  # Will use get_config().get_api_timeout()
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> Any:
        """Generate a complete article."""
        pass


class IWordBudgetManager(ABC):
    """Interface for managing word budgets across sections."""

    @abstractmethod
    def allocate_budget(self, total_words: int, sections: List[str]) -> Dict[str, int]:
        """Allocate word budget across sections."""
        pass

    @abstractmethod
    def get_section_budget(self, section_name: str) -> int:
        """Get the word budget for a specific section."""
        pass

    @abstractmethod
    def update_usage(self, section_name: str, words_used: int) -> None:
        """Update the word usage for a section."""
        pass

    @abstractmethod
    def get_remaining_budget(self, section_name: str) -> int:
        """Get the remaining word budget for a section."""
        pass


class IMetadataGenerator(ABC):
    """Interface for metadata generation."""

    @abstractmethod
    def generate_metadata(
        self, content: str, config: Any, context: GenerationContext
    ) -> Dict[str, Any]:
        """Generate metadata for the article."""
        pass


class IFileManager(ABC):
    """Interface for file operations."""

    @abstractmethod
    def write_file(self, filepath: str, content: str) -> bool:
        """Write content to a file."""
        pass

    @abstractmethod
    def read_file(self, filepath: str) -> str:
        """Read content from a file."""
        pass

    @abstractmethod
    def file_exists(self, filepath: str) -> bool:
        """Check if a file exists."""
        pass


class ICacheManager(ABC):
    """Interface for cache management."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set a value in cache."""
        pass

    @abstractmethod
    def invalidate(self, key: str) -> None:
        """Invalidate a cache entry."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass


class ICacheRepository(ABC):
    """Interface for cache repository operations."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set a value in cache."""
        pass

    @abstractmethod
    def invalidate(self, key: str) -> None:
        """Invalidate a cache entry."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass
