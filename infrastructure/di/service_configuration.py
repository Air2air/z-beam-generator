"""
Service container configuration for the modern architecture.
"""

from infrastructure.di import ModernServiceContainer
from infrastructure.configuration import ConfigProvider, get_config_provider
from infrastructure.api.client import APIClient
from infrastructure.storage.modern_repositories import ModernFileContentRepository, ModernFilePromptRepository

# Application services
from application.services.content_services import ContentService, DetectionService
from application.commands.content_generation import ContentGenerationHandler

# Core interfaces
from domain.simple_repositories import (
    ISimpleContentRepository, 
    ISimplePromptRepository,
    ISimpleContentService,
    ISimpleDetectionService
)
from core.interfaces.services import IAPIClient


def configure_modern_services(container: ModernServiceContainer) -> None:
    """Configure all services for the modern architecture."""
    
    # Configuration provider (singleton) - direct instance
    config_provider = get_config_provider()
    container.register_singleton(
        ConfigProvider,
        factory=lambda: config_provider
    )
    
    # Infrastructure services - direct instances
    container.register_singleton(
        ISimpleContentRepository,
        factory=lambda: ModernFileContentRepository("output")
    )
    
    container.register_singleton(
        ISimplePromptRepository,
        factory=lambda: ModernFilePromptRepository("prompts")
    )
    
    # API Client factory - creates instances per provider
    def create_api_client() -> IAPIClient:
        # Use the GlobalConfigManager to get provider and API key
        from config.global_config import GlobalConfigManager
        config_manager = GlobalConfigManager.get_instance()
        provider = config_manager.get_generator_provider()
        
        # Get API key from environment through config manager - NO HARDCODING!
        try:
            api_key = config_manager.get_api_key(provider)
        except ValueError as e:
            print(f"⚠️ Warning: {e}")
            # For training/testing, fall back to TEST provider
            provider = "TEST"
            api_key = config_manager.get_api_key(provider)
        
        print(f"Creating API client with provider: {provider}")
        return APIClient(provider, api_key)
    
    container.register_transient(
        IAPIClient,
        factory=create_api_client
    )
    
    # Create shared instances for services
    content_repo = ModernFileContentRepository("output")
    prompt_repo = ModernFilePromptRepository("prompts")
    
    # Application services - avoid resolve calls in factory
    def create_content_service() -> ISimpleContentService:
        return ContentService(
            create_api_client(),
            prompt_repo,
            config_provider
        )
    
    def create_detection_service() -> ISimpleDetectionService:
        return DetectionService(
            create_api_client(),
            prompt_repo,
            config_provider
        )
    
    container.register_scoped(
        ISimpleContentService,
        factory=create_content_service
    )
    
    container.register_scoped(
        ISimpleDetectionService,
        factory=create_detection_service
    )
    
    # Command handlers
    def create_content_handler() -> ContentGenerationHandler:
        return ContentGenerationHandler(
            create_content_service(),
            create_detection_service(),
            content_repo,
            prompt_repo,
            config_provider
        )
    
    container.register_scoped(
        ContentGenerationHandler,
        factory=create_content_handler
    )


def get_configured_container() -> ModernServiceContainer:
    """Get a fully configured service container."""
    container = ModernServiceContainer()
    configure_modern_services(container)
    return container
