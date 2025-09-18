#!/usr/bin/env python3
"""
Enhanced Component Generator Factory

This module provides an enhanced factory pattern for component generators
that integrates with the centralized component registry and provides
better error handling, caching, and extensibility.
"""

import importlib
import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class ComponentGeneratorFactory:
    """
    Enhanced factory for creating component generators.

    Features:
    - Integration with centralized component registry
    - Lazy loading and caching
    - Better error handling
    - Support for both static and API generators
    - Extensible registration system
    """

    _generators: Dict[str, Type[Any]] = {}
    _instances: Dict[str, Any] = {}

    @classmethod
    def register_generator(
        cls, component_type: str, generator_class: Type[Any]
    ) -> None:
        """Register a generator class for a component type."""
        cls._generators[component_type] = generator_class
        logger.debug(
            f"Registered generator for {component_type}: {generator_class.__name__}"
        )

    @classmethod
    def unregister_generator(cls, component_type: str) -> None:
        """Unregister a generator for a component type."""
        if component_type in cls._generators:
            del cls._generators[component_type]
            # Also remove from instances cache
            if component_type in cls._instances:
                del cls._instances[component_type]
            logger.debug(f"Unregistered generator for {component_type}")

    @classmethod
    @lru_cache(maxsize=32)
    def create_generator(cls, component_type: str, **kwargs) -> Optional[Any]:
        """
        Create a generator instance for the specified component type.

        Args:
            component_type: The type of component generator to create
            **kwargs: Additional arguments to pass to the generator constructor

        Returns:
            Generator instance or None if creation fails
        """
        try:
            # First try to get from centralized registry
            try:
                import components

                if component_type in components.list_components():
                    generator = components.create_component(component_type)
                    logger.info(
                        f"Created {component_type} generator from centralized registry"
                    )
                    return generator
            except ImportError:
                logger.warning(
                    "Centralized component registry not available, falling back to direct imports"
                )

            # Fallback to registered generators
            if component_type in cls._generators:
                generator_class = cls._generators[component_type]
                generator = generator_class(**kwargs)
                logger.info(f"Created {component_type} generator from factory registry")
                return generator

            # Try dynamic import from components directory
            generator = cls._create_generator_from_components(component_type, **kwargs)
            if generator:
                return generator

            # Try dynamic import from generators directory
            generator = cls._create_generator_from_generators(component_type, **kwargs)
            if generator:
                return generator

            logger.error(f"No generator found for component type: {component_type}")
            from utils.ai.loud_errors import component_failure

            component_failure(
                "component_generator_factory",
                f"No generator found for component type: {component_type}",
                component_type=component_type,
            )
            return None

        except Exception as e:
            from utils.ai.loud_errors import component_failure

            component_failure(
                "component_generator_factory",
                f"Error creating generator for {component_type}: {e}",
                component_type=component_type,
            )
            logger.error(f"Error creating generator for {component_type}: {e}")
            return None

    @classmethod
    def _create_generator_from_components(
        cls, component_type: str, **kwargs
    ) -> Optional[Any]:
        """Try to create generator from components directory."""
        try:
            module_path = f"components.{component_type}.generator"
            class_name = f"{component_type.title()}ComponentGenerator"

            module = importlib.import_module(module_path)
            generator_class = getattr(module, class_name)

            generator = generator_class(**kwargs)
            logger.info(
                f"Created {component_type} generator from components.{component_type}.generator"
            )
            return generator

        except (ImportError, AttributeError) as e:
            logger.debug(
                f"Could not create {component_type} generator from components: {e}"
            )
            return None

    @classmethod
    def _create_generator_from_generators(
        cls, component_type: str, **kwargs
    ) -> Optional[Any]:
        """Try to create generator from generators directory."""
        try:
            module_path = f"generators.{component_type}_generator"
            class_name = f"{component_type.title()}ComponentGenerator"

            module = importlib.import_module(module_path)
            generator_class = getattr(module, class_name)

            generator = generator_class(**kwargs)
            logger.info(
                f"Created {component_type} generator from generators.{component_type}_generator"
            )
            return generator

        except (ImportError, AttributeError) as e:
            logger.debug(
                f"Could not create {component_type} generator from generators: {e}"
            )
            return None

    @classmethod
    def get_available_generators(cls) -> List[str]:
        """Get list of all available generator types."""
        available = set()

        # Add from centralized registry
        try:
            import components

            available.update(components.list_components())
        except ImportError:
            pass

        # Add from factory registry
        available.update(cls._generators.keys())

        # Add from components directory
        try:
            from pathlib import Path

            components_dir = Path("components")
            if components_dir.exists():
                for item in components_dir.iterdir():
                    if item.is_dir() and not item.name.startswith("__"):
                        generator_file = item / "generator.py"
                        if generator_file.exists():
                            available.add(item.name)
        except Exception:
            pass

        # Add from generators directory
        try:
            from pathlib import Path

            generators_dir = Path("generators")
            if generators_dir.exists():
                for item in generators_dir.glob("*_generator.py"):
                    component_name = item.stem.replace("_generator", "")
                    available.add(component_name)
        except Exception:
            pass

        return sorted(list(available))

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the generator creation cache."""
        cls.create_generator.cache_clear()
        cls._instances.clear()
        logger.info("Generator factory cache cleared")

    @classmethod
    def preload_generators(cls, component_types: List[str]) -> None:
        """Preload generators for better performance."""
        for component_type in component_types:
            try:
                generator = cls.create_generator(component_type)
                if generator:
                    cls._instances[component_type] = generator
                    logger.info(f"Preloaded generator for {component_type}")
            except Exception as e:
                logger.warning(f"Failed to preload generator for {component_type}: {e}")


# Convenience functions
def create_generator(component_type: str, **kwargs) -> Optional[Any]:
    """Convenience function to create a generator."""
    return ComponentGeneratorFactory.create_generator(component_type, **kwargs)


def get_available_generators() -> List[str]:
    """Convenience function to get available generators."""
    return ComponentGeneratorFactory.get_available_generators()


def register_generator(component_type: str, generator_class: Type[Any]) -> None:
    """Convenience function to register a generator."""
    ComponentGeneratorFactory.register_generator(component_type, generator_class)


# Auto-register known generators on import
def _auto_register_generators():
    """Automatically register known generators."""
    known_generators = {
        "author": ("generators.author_generator", "AuthorComponentGenerator"),
        "bullets": ("generators.bullets_generator", "BulletsComponentGenerator"),
        "table": ("generators.table_generator", "TableComponentGenerator"),
    }

    for component_type, (module_path, class_name) in known_generators.items():
        try:
            module = importlib.import_module(module_path)
            generator_class = getattr(module, class_name)
            register_generator(component_type, generator_class)
            logger.debug(f"Auto-registered {component_type} generator")
        except (ImportError, AttributeError) as e:
            logger.debug(f"Could not auto-register {component_type} generator: {e}")


# Initialize auto-registration
_auto_register_generators()


__all__ = [
    "ComponentGeneratorFactory",
    "create_generator",
    "get_available_generators",
    "register_generator",
]
