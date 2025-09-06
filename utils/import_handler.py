#!/usr/bin/env python3
"""
Enhanced Import Error Handling

This module provides robust error handling for import failures
and graceful degradation when modules are missing.
"""

import logging
import importlib
from typing import Any, Optional, Dict, List, Callable
from functools import wraps

logger = logging.getLogger(__name__)


class ImportErrorHandler:
    """
    Enhanced import error handler with fallback strategies.

    Features:
    - Graceful import failure handling
    - Fallback module loading
    - Dependency validation
    - Import retry mechanisms
    """

    def __init__(self):
        self.failed_imports: Dict[str, str] = {}
        self.fallbacks: Dict[str, Dict[str, Any]] = {}

    def register_fallback(self, module_name: str, fallback_module: Any) -> None:
        """Register a fallback module for when the primary import fails."""
        self.fallbacks[module_name] = fallback_module
        logger.debug(f"Registered fallback for {module_name}")

    def safe_import(self, module_name: str, fallback: Any = None) -> Optional[Any]:
        """
        Safely import a module with error handling.

        Args:
            module_name: The module to import
            fallback: Optional fallback if import fails

        Returns:
            Imported module or fallback
        """
        try:
            module = importlib.import_module(module_name)
            logger.debug(f"Successfully imported {module_name}")
            return module
        except ImportError as e:
            error_msg = f"Failed to import {module_name}: {e}"
            self.failed_imports[module_name] = error_msg
            logger.warning(error_msg)

            # Try fallback
            if fallback:
                logger.info(f"Using fallback for {module_name}")
                return fallback

            # Try registered fallback
            if module_name in self.fallbacks:
                logger.info(f"Using registered fallback for {module_name}")
                return self.fallbacks[module_name]

            return None

    def validate_dependencies(self, dependencies: List[str]) -> Dict[str, bool]:
        """
        Validate that all required dependencies are available.

        Args:
            dependencies: List of module names to check

        Returns:
            Dict mapping module names to availability status
        """
        results = {}
        for dep in dependencies:
            try:
                importlib.import_module(dep)
                results[dep] = True
                logger.debug(f"Dependency {dep} is available")
            except ImportError as e:
                results[dep] = False
                self.failed_imports[dep] = str(e)
                logger.warning(f"Dependency {dep} is missing: {e}")

        return results

    def get_import_report(self) -> Dict[str, Any]:
        """Get a report of import successes and failures."""
        return {
            'failed_imports': self.failed_imports.copy(),
            'total_failed': len(self.failed_imports),
            'total_attempted': len(self.failed_imports) + len([m for m in self.fallbacks.keys() if m not in self.failed_imports])
        }


# Global import handler instance
import_handler = ImportErrorHandler()


def with_import_fallback(fallback_module: Any):
    """Decorator to provide import fallback for functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ImportError as e:
                logger.warning(f"Import error in {func.__name__}: {e}")
                logger.info(f"Using fallback for {func.__name__}")
                # Try to call the same function on the fallback module
                if hasattr(fallback_module, func.__name__):
                    fallback_func = getattr(fallback_module, func.__name__)
                    return fallback_func(*args, **kwargs)
                else:
                    raise e
        return wrapper
    return decorator


def create_mock_module(**attributes) -> Any:
    """Create a mock module with specified attributes."""
    import types
    module = types.ModuleType("mock_module")

    for name, value in attributes.items():
        setattr(module, name, value)

    return module


def setup_component_fallbacks():
    """Setup common component fallbacks."""
    # Mock component generator
    mock_generator = create_mock_module(
        generate=lambda *args, **kwargs: {
            'component_type': 'mock',
            'content': 'Mock content - component not available',
            'success': False,
            'error': 'Component module not found'
        }
    )

    # Register fallbacks for common components
    common_components = [
        'components.author.generator',
        'components.table.generator',
        'components.frontmatter.generator',
        'components.badgesymbol.generator',
        'components.jsonld.generator',
        'components.metatags.generator',
        'components.propertiestable.generator',
        'components.tags.generator',
        'components.bullets.generator',
        'components.caption.generator',
        'components.text.generator'
    ]

    for component in common_components:
        import_handler.register_fallback(component, mock_generator)


def validate_critical_imports() -> bool:
    """Validate that critical imports are working."""
    critical_modules = [
        'generators.component_generators',
        'utils.component_base',
        'api.client_manager',
        'optimizer.ai_detection.service',
        'run'
    ]

    results = import_handler.validate_dependencies(critical_modules)

    failed_count = sum(1 for status in results.values() if not status)
    total_count = len(results)

    if failed_count > 0:
        logger.error(f"Critical import validation failed: {failed_count}/{total_count} modules failed")
        for module, status in results.items():
            if not status:
                logger.error(f"  - {module}: {import_handler.failed_imports.get(module, 'Unknown error')}")
        return False
    else:
        logger.info(f"Critical import validation passed: {total_count}/{total_count} modules available")
        return True


# Initialize fallbacks on import
setup_component_fallbacks()


__all__ = [
    'ImportErrorHandler',
    'import_handler',
    'with_import_fallback',
    'create_mock_module',
    'setup_component_fallbacks',
    'validate_critical_imports',
]
