"""
BaseDataLoader - Abstract base class for all data loaders.

This module provides standardized YAML loading with caching, validation,
and fail-fast error handling. All domain data loaders should inherit from this.

Key features:
- Thread-safe caching
- Standardized error handling
- Path resolution
- Validation hooks
- Automatic cache invalidation

Author: Z-Beam Development Team
Date: December 11, 2025
"""

import logging
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from shared.exceptions import ConfigurationError, ValidationError

logger = logging.getLogger(__name__)


class BaseDataLoader(ABC):
    """
    Abstract base class for all data loaders.
    
    Provides:
    - Standardized YAML loading with caching
    - Path resolution
    - Fail-fast error handling
    - Validation hooks
    - Thread-safe operations
    
    Usage:
        class MaterialsDataLoader(BaseDataLoader):
            def _get_data_file_path(self) -> Path:
                return self.project_root / 'data' / 'materials' / 'Materials.yaml'
            
            def _validate_loaded_data(self, data: Dict[str, Any]) -> bool:
                return 'materials' in data
            
            def load_materials(self) -> Dict[str, Any]:
                filepath = self._get_data_file_path()
                data = self._load_yaml_file(filepath)
                return data.get('materials', {})
    """
    
    # Class-level cache shared across instances
    _cache: Dict[str, Any] = {}
    _cache_lock = threading.Lock()
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize data loader.
        
        Args:
            project_root: Root directory of project. If None, auto-detected.
        
        Raises:
            ConfigurationError: If project root cannot be determined
        """
        if project_root is None:
            # Auto-detect project root
            current_file = Path(__file__).resolve()
            # Go up from shared/data/base_loader.py to project root
            self.project_root = current_file.parent.parent.parent
        else:
            self.project_root = project_root
        
        # Validate project structure
        self._validate_project_structure()
    
    @abstractmethod
    def _get_data_file_path(self) -> Path:
        """
        Return path to main data file.
        
        Must be implemented by subclasses.
        
        Returns:
            Path to data file
        
        Example:
            return self.project_root / 'data' / 'materials' / 'Materials.yaml'
        """
        pass
    
    @abstractmethod
    def _validate_loaded_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate loaded data structure.
        
        Must be implemented by subclasses.
        
        Args:
            data: Loaded YAML data
        
        Returns:
            True if valid, False otherwise
        
        Example:
            return 'materials' in data or 'categories' in data
        """
        pass

    @abstractmethod
    def _get_cache_domain(self) -> str:
        """
        Return the cache_manager domain string for this loader.

        Must be implemented by subclasses.

        Returns:
            Domain name used as cache_manager namespace (e.g., 'materials')

        Example:
            return 'materials'
        """
        pass

    def _load_with_cache(
        self,
        cache_key: str,
        filepath: Path,
        extractor=None,
        ttl: int = 3600,
    ):
        """
        Load YAML file with cache_manager caching (no schema validation).

        Use for secondary data files where domain validation is not required.
        For primary domain files that need schema validation, call
        _load_yaml_file() directly then cache_manager manually.

        Args:
            cache_key: Key for cache_manager storage
            filepath: Path to YAML file
            extractor: Optional callable(data) -> result. If None, returns raw data.
            ttl: Cache time-to-live in seconds (default 1 hour)

        Returns:
            Cached or freshly loaded data
        """
        from shared.cache.manager import cache_manager
        from shared.utils.file_io import read_yaml_file

        cached = cache_manager.get(self._get_cache_domain(), cache_key)
        if cached:
            return cached

        data = read_yaml_file(filepath)
        result = extractor(data) if extractor is not None else data
        cache_manager.set(self._get_cache_domain(), cache_key, result, ttl=ttl)
        return result

    def _validate_project_structure(self):
        """
        Validate project structure on initialization.
        
        Ensures data directory exists.
        
        Raises:
            ConfigurationError: If project structure is invalid
        """
        data_dir = self.project_root / 'data'
        if not data_dir.exists():
            raise ConfigurationError(
                f"Project data directory not found: {data_dir}\n"
                f"Project root: {self.project_root}"
            )
    
    def _load_yaml_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Load YAML file with caching and error handling.
        
        Thread-safe, fail-fast on errors.
        
        Args:
            filepath: Path to YAML file
        
        Returns:
            Loaded data dictionary
        
        Raises:
            ConfigurationError: If file not found or invalid YAML
            ValidationError: If data fails validation
        """
        cache_key = str(filepath)
        
        # Check cache first (thread-safe)
        with self._cache_lock:
            if cache_key in self._cache:
                logger.debug(f"Cache hit: {filepath.name}")
                return self._cache[cache_key]
        
        logger.debug(f"Loading {filepath.name}...")
        
        # Validate file existence
        if not filepath.exists():
            raise ConfigurationError(
                f"Required data file not found: {filepath}\n"
                f"Expected location: {filepath.absolute()}"
            )
        
        # Load YAML with error handling
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if data is None:
                raise ConfigurationError(f"Empty YAML file: {filepath}")
            
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in {filepath}:\n{str(e)}\n"
                f"File must be valid YAML format."
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load {filepath}: {str(e)}"
            )
        
        # Validate data structure
        if not self._validate_loaded_data(data):
            raise ValidationError(
                message=f"Invalid data structure in {filepath}",
                fix="Check file format matches expected schema",
                context={"filepath": str(filepath)}
            )
        
        # Cache the result (thread-safe)
        with self._cache_lock:
            self._cache[cache_key] = data
        
        logger.debug(f"✅ Loaded and cached: {filepath.name}")
        return data
    
    def clear_cache(self, filepath: Optional[Path] = None):
        """
        Clear cached data from both internal _cache and cache_manager.

        Args:
            filepath: Specific file to clear from _cache. If None, clears all
                      _cache entries and the full cache_manager domain.
        """
        from shared.cache.manager import cache_manager

        with self._cache_lock:
            if filepath is None:
                # Clear entire _cache
                count = len(self._cache)
                self._cache.clear()
                logger.info(f"Cleared {count} cached files")
                # Also clear the domain's cache_manager entries
                cache_manager.invalidate(self._get_cache_domain())
                logger.info(f"Cleared cache_manager domain: {self._get_cache_domain()}")
            else:
                # Clear specific file from _cache only
                cache_key = str(filepath)
                if cache_key in self._cache:
                    del self._cache[cache_key]
                    logger.info(f"Cleared cache: {filepath.name}")
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache size and keys
        """
        with cls._cache_lock:
            return {
                'size': len(cls._cache),
                'keys': list(cls._cache.keys())
            }
