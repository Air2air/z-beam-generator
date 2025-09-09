#!/usr/bin/env python3
"""
Robust Import Manager

Provides safe imports with fallback mechanisms and clear error messages.
Handles missing dependencies and provides graceful degradation.
"""

import importlib
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class ImportManager:
    """
    Robust import management with fallback mechanisms.

    Features:
    - Safe imports with clear error messages
    - Fallback mechanisms for missing components
    - Graceful degradation
    - Dependency validation
    """

    _import_cache: Dict[str, Any] = {}
    _failed_imports: Dict[str, str] = {}

    @classmethod
    def safe_import(cls, module_path: str, fallback: Any = None) -> Optional[Any]:
        """
        Safely import a module with fallback.

        Args:
            module_path: Module path to import
            fallback: Fallback value if import fails

        Returns:
            Imported module or fallback
        """
        if module_path in cls._import_cache:
            return cls._import_cache[module_path]

        if module_path in cls._failed_imports:
            logger.debug(
                f"Using cached failure for {module_path}: {cls._failed_imports[module_path]}"
            )
            return fallback

        try:
            module = importlib.import_module(module_path)
            cls._import_cache[module_path] = module
            logger.debug(f"Successfully imported {module_path}")
            return module
        except ImportError as e:
            error_msg = f"Failed to import {module_path}: {e}"
            cls._failed_imports[module_path] = error_msg
            logger.warning(error_msg)
            return fallback
        except Exception as e:
            error_msg = f"Unexpected error importing {module_path}: {e}"
            cls._failed_imports[module_path] = error_msg
            logger.error(error_msg)
            return fallback

    @classmethod
    def safe_import_class(
        cls, module_path: str, class_name: str, fallback: Any = None
    ) -> Optional[Type]:
        """
        Safely import a class from a module.

        Args:
            module_path: Module path
            class_name: Class name to import
            fallback: Fallback class if import fails

        Returns:
            Imported class or fallback
        """
        cache_key = f"{module_path}.{class_name}"

        if cache_key in cls._import_cache:
            return cls._import_cache[cache_key]

        if cache_key in cls._failed_imports:
            return fallback

        try:
            module = importlib.import_module(module_path)
            class_obj = getattr(module, class_name)
            cls._import_cache[cache_key] = class_obj
            logger.debug(f"Successfully imported {cache_key}")
            return class_obj
        except (ImportError, AttributeError) as e:
            error_msg = f"Failed to import {cache_key}: {e}"
            cls._failed_imports[cache_key] = error_msg
            logger.warning(error_msg)
            return fallback
        except Exception as e:
            error_msg = f"Unexpected error importing {cache_key}: {e}"
            cls._failed_imports[cache_key] = error_msg
            logger.error(error_msg)
            return fallback

    @classmethod
    def get_import_errors(cls) -> Dict[str, str]:
        """Get all import errors that occurred."""
        return cls._failed_imports.copy()

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the import cache."""
        cls._import_cache.clear()
        cls._failed_imports.clear()
        logger.info("Import cache cleared")


def validate_dependencies() -> Dict[str, Any]:
    """
    Validate all critical dependencies and report status.

    Returns:
        Dictionary with validation results
    """
    results = {"critical": {}, "optional": {}, "missing": [], "warnings": []}

    # Critical dependencies
    critical_deps = [
        ("yaml", "PyYAML for configuration files"),
        ("pathlib", "Path handling (built-in)"),
        ("typing", "Type hints (built-in)"),
    ]

    for module, description in critical_deps:
        try:
            importlib.import_module(module)
            results["critical"][module] = f"✅ {description}"
        except ImportError:
            results["critical"][module] = f"❌ {description}"
            results["missing"].append(module)

    # Optional dependencies
    optional_deps = [
        ("requests", "HTTP requests"),
        ("aiohttp", "Async HTTP requests"),
        ("pytest", "Testing framework"),
    ]

    for module, description in optional_deps:
        try:
            importlib.import_module(module)
            results["optional"][module] = f"✅ {description}"
        except ImportError:
            results["optional"][module] = f"⚠️  {description} (optional)"
            results["warnings"].append(f"Missing optional dependency: {module}")

    return results


def setup_python_path():
    """Ensure project root is in Python path."""
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        logger.debug(f"Added to Python path: {project_root}")


# Initialize on import
setup_python_path()


__all__ = [
    "ImportManager",
    "validate_dependencies",
    "setup_python_path",
]
