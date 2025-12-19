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

from shared.validation.errors import ConfigurationError, ValidationError

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
                f"Invalid data structure in {filepath}\n"
                f"Failed validation check."
            )
        
        # Cache the result (thread-safe)
        with self._cache_lock:
            self._cache[cache_key] = data
        
        logger.debug(f"✅ Loaded and cached: {filepath.name}")
        return data
    
    def clear_cache(self, filepath: Optional[Path] = None):
        """
        Clear cached data.
        
        Args:
            filepath: Specific file to clear. If None, clears all cache.
        """
        with self._cache_lock:
            if filepath is None:
                # Clear entire cache
                count = len(self._cache)
                self._cache.clear()
                logger.info(f"Cleared {count} cached files")
            else:
                # Clear specific file
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
