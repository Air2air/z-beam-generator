#!/usr/bin/env python3
"""
Centralized Component Registry

This module provides centralized access to all component generators,
preventing import path issues and providing a single point of access
for all components in the system.
"""

from typing import Dict, Type, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Component Registry
COMPONENT_REGISTRY: Dict[str, Type[Any]] = {}


def register_component(name: str, component_class: Type[Any]) -> None:
    """Register a component in the central registry."""
    COMPONENT_REGISTRY[name] = component_class
    logger.debug(f"Registered component: {name}")


def get_component(name: str) -> Optional[Type[Any]]:
    """Get a component from the registry."""
    return COMPONENT_REGISTRY.get(name)


def list_components() -> list[str]:
    """List all registered components."""
    return list(COMPONENT_REGISTRY.keys())


# Lazy import and registration of components
def _load_components():
    """Load and register all available components."""
    components_to_load = [
        ('author', 'components.author.generator', 'AuthorComponentGenerator'),
        ('badgesymbol', 'components.badgesymbol.generator', 'BadgesymbolComponentGenerator'),
        ('bullets', 'components.bullets.generator', 'BulletsComponentGenerator'),
        ('caption', 'components.caption.generator', 'CaptionComponentGenerator'),
        ('frontmatter', 'components.frontmatter.generator', 'FrontmatterComponentGenerator'),
        ('jsonld', 'components.jsonld.generator', 'JsonldComponentGenerator'),
        ('metatags', 'components.metatags.generator', 'MetatagsComponentGenerator'),
        ('propertiestable', 'components.propertiestable.generator', 'PropertiestableComponentGenerator'),
        ('table', 'components.table.generator', 'TableComponentGenerator'),
        ('tags', 'components.tags.generator', 'TagsComponentGenerator'),
        ('text', 'components.text.generator', 'TextComponentGenerator'),
    ]

    for component_name, module_path, class_name in components_to_load:
        try:
            module = __import__(module_path, fromlist=[class_name])
            component_class = getattr(module, class_name)
            register_component(component_name, component_class)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Failed to load component {component_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading component {component_name}: {e}")


# Load components on module import
_load_components()


# Convenience functions for common operations
def create_component(component_type: str, *args, **kwargs):
    """Create a component instance."""
    component_class = get_component(component_type)
    if component_class:
        return component_class(*args, **kwargs)
    else:
        raise ValueError(f"Unknown component type: {component_type}")


def get_component_info(component_type: str) -> Optional[Dict[str, Any]]:
    """Get information about a component."""
    component_class = get_component(component_type)
    if component_class:
        return {
            'name': component_type,
            'class': component_class,
            'module': component_class.__module__,
            'doc': component_class.__doc__ or "",
        }
    return None


# Export commonly used classes and functions
__all__ = [
    'COMPONENT_REGISTRY',
    'register_component',
    'get_component',
    'list_components',
    'create_component',
    'get_component_info',
]
