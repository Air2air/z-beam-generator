#!/usr/bin/env python3
"""
Robust Path Manager

Centralized path management to eliminate hardcoded paths and CWD dependencies.
Provides consistent path resolution across the entire codebase.
"""

import logging
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
    def get_preferred_existing_path(
        cls, *relative_paths: Union[str, Path], must_exist: bool = True
    ) -> Path:
        """Return the first existing project-relative path from a preferred list."""
        if not cls._initialized:
            cls.initialize()

        candidates = [cls._project_root / Path(path) for path in relative_paths]
        for candidate in candidates:
            if candidate.exists():
                return candidate

        if must_exist:
            joined = ", ".join(str(candidate) for candidate in candidates)
            raise FileNotFoundError(f"None of the candidate paths exist: {joined}")

        return candidates[0]

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
    def get_governance_dir(cls) -> Path:
        """Get the Grok-first governance directory path."""
        return cls.get_preferred_existing_path("governance", ".github")

    @classmethod
    def get_aggregates_dir(cls) -> Path:
        """Get the canonical aggregate YAML directory path."""
        return cls.get_preferred_existing_path("aggregates", "data")

    @classmethod
    def get_aggregate_file(cls, filename: str, *legacy_parts: str) -> Path:
        """Get an aggregate YAML file, preferring the new canonical location."""
        candidates = [Path("aggregates") / filename]
        if legacy_parts:
            candidates.append(Path(*legacy_parts))
        return cls.get_preferred_existing_path(*candidates)

    @classmethod
    def get_voice_profiles_dir(cls) -> Path:
        """Get the canonical voice profiles directory, with legacy fallback."""
        return cls.get_preferred_existing_path("voices", "shared/voice/profiles")

    @classmethod
    def get_config_dir(cls) -> Path:
        """Get config directory path."""
        return cls.get_path("config")

    @classmethod
    def get_materials_file(cls) -> Path:
        """Get materials YAML file path."""
        return cls.get_aggregate_file("Materials.yaml", "data", "materials", "Materials.yaml")

    @classmethod
    def get_contaminants_file(cls) -> Path:
        """Get contaminants YAML file path."""
        return cls.get_aggregate_file("contaminants.yaml", "data", "contaminants", "contaminants.yaml")

    @classmethod
    def get_compounds_file(cls) -> Path:
        """Get compounds YAML file path."""
        return cls.get_aggregate_file("Compounds.yaml", "data", "compounds", "Compounds.yaml")

    @classmethod
    def get_settings_file(cls) -> Path:
        """Get settings YAML file path."""
        return cls.get_aggregate_file("Settings.yaml", "data", "settings", "Settings.yaml")

    @classmethod
    def get_applications_file(cls) -> Path:
        """Get applications YAML file path."""
        return cls.get_aggregate_file("Applications.yaml", "data", "applications", "Applications.yaml")

    @classmethod
    def get_authors_file(cls) -> Path:
        """Get authors YAML file path."""
        return cls.get_aggregate_file("Authors.yaml", "data", "authors", "Authors.yaml")

    @classmethod
    def get_api_keys_file(cls) -> Path:
        """Get API keys file path."""
        return cls.get_path("config", "api_keys.py")

    @classmethod
    def get_component_output_dir(cls, component_type: str) -> Path:
        """Get output directory for a specific component type."""
        return cls.ensure_directory("content", "components", component_type)


# NOTE: PathManager uses lazy initialization - no need to initialize on import
# The class will auto-initialize on first use


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
