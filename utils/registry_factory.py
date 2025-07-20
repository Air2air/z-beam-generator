"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO CACHING: Do not cache registry instances by default
2. CACHING CONTROL: Allow explicit control over caching behavior
3. UNIFIED ACCESS: Provide a single point of access for all registry types
4. DYNAMIC IMPORTS: Use dynamic imports to avoid circular dependencies
"""

import logging
from typing import Any, Dict, Optional, Type

logger = logging.getLogger(__name__)

class RegistryFactory:
    """Factory for creating registry instances with caching control."""
    
    _instances = {}  # Type-level cache for when caching is requested
    
    @classmethod
    def reset_cache(cls) -> None:
        """Reset the registry instance cache."""
        cls._instances.clear()
    
    @classmethod
    def create_registry(cls, registry_type: str, use_cache: bool = False, **kwargs) -> Any:
        """Create a registry instance of the specified type.
        
        Args:
            registry_type: Type of registry to create
            use_cache: Whether to cache/reuse instances
            **kwargs: Additional arguments for registry constructor
            
        Returns:
            Registry instance or None if type is invalid
        """
        # Check cache first if enabled
        cache_key = f"{registry_type}:{str(kwargs)}"
        if use_cache and cache_key in cls._instances:
            return cls._instances[cache_key]
        
        # Import on demand to avoid circular imports
        if registry_type == 'schema':
            from utils.registries import SchemaRegistry
            registry = SchemaRegistry(**kwargs)
        elif registry_type == 'component':
            from utils.registries import ComponentRegistry
            registry = ComponentRegistry(**kwargs)
        elif registry_type == 'prompt':
            from utils.registries import PromptRegistry
            registry = PromptRegistry(**kwargs)
        elif registry_type == 'config':
            from utils.registries import ConfigRegistry
            registry = ConfigRegistry(**kwargs)
        else:
            logger.error(f"Invalid registry type: {registry_type}")
            return None
        
        # Store in cache if requested
        if use_cache:
            cls._instances[cache_key] = registry
            
        return registry
    
    @classmethod
    def schema_registry(cls, use_cache: bool = False, **kwargs) -> Any:
        """Get a schema registry instance."""
        return cls.create_registry('schema', use_cache, **kwargs)
    
    @classmethod
    def component_registry(cls, use_cache: bool = False, **kwargs) -> Any:
        """Get a component registry instance."""
        return cls.create_registry('component', use_cache, **kwargs)
    
    @classmethod
    def prompt_registry(cls, use_cache: bool = False, **kwargs) -> Any:
        """Get a prompt registry instance."""
        return cls.create_registry('prompt', use_cache, **kwargs)
    
    @classmethod
    def config_registry(cls, use_cache: bool = False, **kwargs) -> Any:
        """Get a config registry instance."""
        return cls.create_registry('config', use_cache, **kwargs)