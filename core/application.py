"""
Service registration and application bootstrap.
"""

from typing import Optional
from core.container import ServiceContainer
from core.interfaces.services import (
    IContentGenerator,
    IDetectionService,
    IAPIClient,
    IPromptRepository,
    ICacheRepository,
)

# Add prompt optimization interfaces
from generator.core.interfaces.prompt_optimization import (
    IPromptPerformanceRepository,
    IPromptSelectionStrategy,
    IPromptOptimizationService,
)
from generator.core.services.content_service import ContentGenerationService
from generator.core.services.detection_service import DetectionService

# Add prompt optimization services
from generator.core.services.prompt_optimization_service import (
    PromptOptimizationService,
)
from generator.core.services.prompt_selection_strategies import (
    PerformanceBasedSelectionStrategy,
)
from generator.infrastructure.storage.prompt_performance_repository import (
    FilePromptPerformanceRepository,
)
from generator.infrastructure.api.client import APIClient
from generator.infrastructure.storage.repositories import (
    FileCacheRepository,
)
from generator.infrastructure.storage.enhanced_json_prompt_repository import (
    EnhancedJsonPromptRepository,
)
from generator.config.enhanced_settings import get_settings
from generator.modules.logger import get_logger

logger = get_logger("application")


def configure_services(container: ServiceContainer) -> None:
    """Configure all services in the dependency injection container."""
    settings = get_settings()

    # Register repositories
    container.register_factory(
        IPromptRepository,
        lambda: EnhancedJsonPromptRepository(settings.paths.prompts_dir),
    )

    container.register_factory(
        ICacheRepository, lambda: FileCacheRepository(settings.paths.cache_dir)
    )

    # Register prompt performance repository
    container.register_factory(
        IPromptPerformanceRepository,
        lambda: FilePromptPerformanceRepository(
            str(settings.paths.cache_dir / "prompt_performance.json")
        ),
    )

    # Register prompt selection strategies
    container.register_factory(
        IPromptSelectionStrategy,
        lambda: PerformanceBasedSelectionStrategy(),  # Default strategy
    )

    # Register prompt optimization service
    def prompt_optimization_service_factory():
        performance_repo = container.get(IPromptPerformanceRepository)
        selection_strategy = container.get(IPromptSelectionStrategy)
        return PromptOptimizationService(performance_repo, selection_strategy)

    container.register_factory(
        IPromptOptimizationService, prompt_optimization_service_factory
    )

    # Register API client factory (will be created per request based on provider)
    def api_client_factory():
        # Use detection_provider from settings if available, otherwise fallback to generator_provider
        provider = None  # No hardcoded fallback - must be configured

        # Try to get provider from settings
        try:
            if hasattr(settings, "detection_provider") and settings.detection_provider:
                provider = settings.detection_provider
            elif (
                hasattr(settings, "generator_provider") and settings.generator_provider
            ):
                provider = settings.generator_provider
        except AttributeError:
            # Fallback to default provider if attributes don't exist
            pass

        provider = provider.upper()

        # Get the appropriate API key based on provider
        api_key = None
        if provider == "GEMINI":
            api_key = settings.api.gemini_api_key
        elif provider == "DEEPSEEK":
            api_key = settings.api.deepseek_api_key
        elif provider == "XAI":
            api_key = settings.api.anthropic_api_key

        if not api_key:
            raise ValueError(f"No API key configured for provider: {provider}")

        return APIClient(provider, api_key)

    container.register_factory(IAPIClient, api_client_factory)

    # Register detection service
    def detection_service_factory():
        api_client = container.get(IAPIClient)
        prompt_repo = container.get(IPromptRepository)
        return DetectionService(api_client, prompt_repo)

    container.register_factory(IDetectionService, detection_service_factory)

    # Register content generation service
    def content_service_factory():
        api_client = container.get(IAPIClient)
        detection_service = container.get(IDetectionService)
        prompt_repo = container.get(IPromptRepository)
        return ContentGenerationService(api_client, detection_service, prompt_repo)

    container.register_factory(IContentGenerator, content_service_factory)

    # Services configured


def create_api_client(provider: str, api_key: str) -> APIClient:
    """Create an API client for a specific provider."""
    return APIClient(provider, api_key)


def validate_application_setup() -> bool:
    """Validate that the application is properly set up."""
    settings = get_settings()
    errors = settings.validate_setup()

    if errors:
        logger.error("Application setup validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        return False

    logger.info("Application setup validation passed")
    return True


class Application:
    """Main application class that orchestrates the entire system."""

    def __init__(self):
        self.container = ServiceContainer()
        self.settings = get_settings()

    def initialize(self) -> bool:
        """Initialize the application."""
        try:
            logger.info("Initializing Z-Beam Generator application...")

            # Validate setup
            if not validate_application_setup():
                return False

            # Configure services
            configure_services(self.container)

            # Ensure required directories exist
            self._ensure_directories()

            logger.info("Application initialization completed successfully")
            return True

        except Exception as e:
            logger.error(f"Application initialization failed: {str(e)}")
            return False

    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.settings.paths.cache_dir,
            self.settings.paths.output_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")

    def get_content_generator(self, provider: str, api_key: str) -> IContentGenerator:
        """Get a content generator configured for a specific provider."""
        # Create provider-specific API client
        api_client = create_api_client(provider, api_key)

        # Get other services from container
        detection_service = self.container.get(IDetectionService)
        prompt_repo = self.container.get(IPromptRepository)

        # Create content service with provider-specific API client
        return ContentGenerationService(api_client, detection_service, prompt_repo)

    def get_prompt_optimization_service(self) -> IPromptOptimizationService:
        """Get the prompt optimization service."""
        return self.container.get(IPromptOptimizationService)

    def shutdown(self) -> None:
        """Shutdown the application cleanly."""
        logger.info("Shutting down application...")
        # Clean up resources if needed
        if self.settings.cache.auto_cleanup:
            try:
                cache_repo = self.container.get(ICacheRepository)
                deleted = cache_repo.clear_expired(self.settings.cache.max_age_seconds)
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} expired cache entries")
            except Exception as e:
                logger.warning(f"Failed to clean up cache during shutdown: {str(e)}")


# Global application instance
_app: Optional[Application] = None


def get_app() -> Application:
    """Get the global application instance."""
    global _app
    if _app is None:
        _app = Application()
        _app.initialize()
    return _app
