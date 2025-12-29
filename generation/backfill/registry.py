"""
Backfill Generator Registry

Central registry for discovering and instantiating backfill generators.

Usage:
    # Register a generator
    BackfillRegistry.register('compound_linkage', CompoundLinkageBackfillGenerator)
    
    # Create generator from config
    config = {'type': 'compound_linkage', ...}
    generator = BackfillRegistry.create(config)
"""

from typing import Dict, Any, Type
from generation.backfill.base import BaseBackfillGenerator


class BackfillRegistry:
    """Registry for backfill generator discovery and instantiation."""
    
    _generators: Dict[str, Type[BaseBackfillGenerator]] = {}
    
    @classmethod
    def register(cls, name: str, generator_class: Type[BaseBackfillGenerator]) -> None:
        """
        Register a backfill generator.
        
        Args:
            name: Generator type name (e.g., 'compound_linkage')
            generator_class: Generator class
        """
        cls._generators[name] = generator_class
    
    @classmethod
    def create(cls, config: Dict[str, Any]) -> BaseBackfillGenerator:
        """
        Create backfill generator from config.
        
        Args:
            config: Generator config with 'type' key
        
        Returns:
            Instantiated generator
        
        Raises:
            KeyError: If generator type not registered
            ValueError: If config missing 'type' key
        """
        if 'type' not in config:
            raise ValueError("Generator config missing 'type' key")
        
        generator_type = config['type']
        
        if generator_type not in cls._generators:
            raise KeyError(f"Unknown generator type: {generator_type}")
        
        generator_class = cls._generators[generator_type]
        return generator_class(config)
    
    @classmethod
    def list_generators(cls) -> list:
        """
        List all registered generator types.
        
        Returns:
            List of generator type names
        """
        return list(cls._generators.keys())
