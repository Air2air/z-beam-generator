#!/usr/bin/env python3
"""
Robust Path Manager

Centralized path management to eliminate hardcoded paths and CWD dependencies.
Provides consistent path resolution across the entire codebase.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


class PathManager:
    """
    Centralized path management for the Z-Beam Generator.

    Features:
    - Automatic project root detection
    - Consistent path resolution
    - Platform-independent path handling
    - CWD independence
    """

    _project_root: Optional[Path] = None
    _initialized = False

    @classmethod
    def initialize(cls, project_root: Optional[Union[str, Path]] = None) -> None:
        """Initialize the path manager with project root."""
        if cls._initialized:
            return

        if project_root:
            cls._project_root = Path(project_root).resolve()
        else:
            # Auto-detect project root
            cls._project_root = cls._find_project_root()

        # Ensure project root exists
        if not cls._project_root or not cls._project_root.exists():
            raise RuntimeError(
                f"Could not determine project root. Tried: {cls._project_root}"
            )

        # Add project root to Python path
        project_root_str = str(cls._project_root)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)

        cls._initialized = True
        logger.info(f"PathManager initialized with root: {cls._project_root}")

    @classmethod
    def _find_project_root(cls) -> Optional[Path]:
        """Find project root by looking for key files/directories."""
        # Start from current file's directory
        current = Path(__file__).resolve().parent

        # Walk up directories looking for project markers
        for parent in [current] + list(current.parents):
            if (parent / "requirements.txt").exists() and (parent / "data").exists():
                return parent

        # Fallback: use current working directory
        cwd = Path.cwd()
        if (cwd / "requirements.txt").exists():
            return cwd

        return None

    @classmethod
    def get_project_root(cls) -> Path:
        """Get the project root directory."""
        if not cls._initialized:
            cls.initialize()
        return cls._project_root

    @classmethod
    def get_path(
        cls, *path_components: Union[str, Path], must_exist: bool = True
    ) -> Path:
        """
        Get a path relative to project root.

        Args:
            *path_components: Path components to join
            must_exist: Whether to raise error if path doesn't exist

        Returns:
            Absolute path
        """
        if not cls._initialized:
            cls.initialize()

        path = cls._project_root / Path(*path_components)

        if must_exist and not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        return path

    @classmethod
    def ensure_directory(cls, *path_components: Union[str, Path]) -> Path:
        """Ensure a directory exists, creating it if necessary."""
        path = cls.get_path(*path_components, must_exist=False)
        path.mkdir(parents=True, exist_ok=True)
        return path

    # Common path getters
    @classmethod
    def get_content_dir(cls) -> Path:
        """Get content directory path."""
        return cls.get_path("content")

    @classmethod
    def get_components_dir(cls) -> Path:
        """Get components directory path."""
        return cls.get_path("content", "components")

    @classmethod
    def get_data_dir(cls) -> Path:
        """Get data directory path."""
        return cls.get_path("data")

    @classmethod
    def get_config_dir(cls) -> Path:
        """Get config directory path."""
        return cls.get_path("config")

    @classmethod
    def get_materials_file(cls) -> Path:
        """Get materials YAML file path."""
        return cls.get_path("data", "materials.yaml")

    @classmethod
    def get_api_keys_file(cls) -> Path:
        """Get API keys file path."""
        return cls.get_path("config", "api_keys.py")

    @classmethod
    def get_component_output_dir(cls, component_type: str) -> Path:
        """Get output directory for a specific component type."""
        return cls.ensure_directory("content", "components", component_type)


# Initialize on import
PathManager.initialize()


def get_project_root() -> Path:
    """Convenience function to get project root."""
    return PathManager.get_project_root()


def get_path(*path_components: Union[str, Path], must_exist: bool = True) -> Path:
    """Convenience function for path resolution."""
    return PathManager.get_path(*path_components, must_exist=must_exist)


# Export common functions
__all__ = [
    "PathManager",
    "get_project_root",
    "get_path",
]
