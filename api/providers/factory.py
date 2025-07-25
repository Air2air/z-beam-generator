"""
API MODULE DIRECTIVES FOR AI ASSISTANTS:
1. LAZY LOADING: Only import provider modules when needed
2. ERROR HANDLING: Provide clear error messages for missing providers
3. PROVIDER REGISTRY: Use a registry to avoid hardcoding provider names
4. FALLBACK STRATEGY: Always have a fallback provider available
"""

import logging
import importlib
from typing import Dict, Any, Optional, Type
from api.errors import ProviderNotFoundError
from api.providers.base import BaseProvider

logger = logging.getLogger(__name__)

class ProviderFactory:
    """Factory for creating provider instances."""
    
    # Registry of provider class paths
    _provider_registry = {
        "deepseek": "api.providers.deepseek.DeepseekProvider",
        "anthropic": "api.providers.anthropic.AnthropicProvider",
        "openai": "api.providers.openai.OpenAIProvider",
        "fallback": "api.providers.fallback.FallbackProvider"
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_path: str) -> None:
        """Register a new provider.
        
        Args:
            name: Provider name
            provider_path: Fully qualified provider class path
        """
        cls._provider_registry[name.lower()] = provider_path
        logger.debug(f"Registered provider: {name} -> {provider_path}")
    
    @classmethod
    def create_provider(cls, provider_name: str, context: Optional[Dict[str, Any]] = None) -> BaseProvider:
        """Create provider instance.
        
        Args:
            provider_name: Name of the provider
            context: Context for the provider
            
        Returns:
            Provider instance
            
        Raises:
            ProviderNotFoundError: If the provider cannot be created
        """
        try:
            # Normalize provider name
            provider_name = provider_name.lower()
            
            # Check if provider is registered
            if provider_name not in cls._provider_registry:
                logger.warning(f"Unknown provider: {provider_name}, using fallback provider")
                provider_name = "fallback"
                
            # Get provider class path
            provider_path = cls._provider_registry[provider_name]
            
            # Import module and class dynamically
            module_path, class_name = provider_path.rsplit('.', 1)
            
            try:
                module = importlib.import_module(module_path)
                provider_class = getattr(module, class_name)
                return provider_class(context)
            except ImportError as e:
                logger.error(f"Provider module not found: {module_path}: {str(e)}")
                raise ProviderNotFoundError(f"Provider module not found: {module_path}")
                
            except AttributeError:
                logger.error(f"Provider class not found: {class_name} in {module_path}")
                raise ProviderNotFoundError(f"Provider class not found: {class_name} in {module_path}")
                
        except Exception as e:
            logger.error(f"Error creating provider {provider_name}: {str(e)}")
            
            # Try to create fallback provider as a last resort
            if provider_name != "fallback":
                logger.info("Attempting to create fallback provider")
                return cls.create_provider("fallback", context)
            else:
                raise ProviderNotFoundError(f"Failed to create provider and fallback provider: {str(e)}")