"""
Contaminants Data Loader - NEW ARCHITECTURE (December 11, 2025)

This module provides BaseDataLoader-based loading for contaminant pattern data.
Maintains backward compatibility with existing PatternDataLoader.

New Architecture:
- Inherits from shared.data.base_loader.BaseDataLoader
- Uses shared.cache.manager.CacheManager for caching
- Uses shared.utils.file_io for file operations
- Eliminates duplicate YAML loading code

Backward Compatibility:
- All existing PatternDataLoader methods remain available
- No breaking changes to existing code
- Gradual migration path

Usage (New):
    from domains.contaminants.data_loader_v2 import ContaminantsDataLoader
    
    loader = ContaminantsDataLoader()
    patterns = loader.load_patterns()
    pattern = loader.get_pattern('rust_oxidation')

Usage (Legacy - still works):
    from domains.contaminants.data_loader import PatternDataLoader
    
    loader = PatternDataLoader()
    pattern = loader.get_pattern('rust_oxidation')
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from shared.cache.manager import cache_manager
from shared.data.base_loader import BaseDataLoader

logger = logging.getLogger(__name__)

# Import author registry for author resolution
try:
    from data.authors.registry import resolve_author_for_generation
except ImportError:
    logger.warning("Could not import author registry - author resolution will be limited")
    resolve_author_for_generation = None


class ContaminantsDataLoader(BaseDataLoader):
    """
    Data loader for contaminants domain.
    
    Loads data from:
    - Contaminants.yaml: Pattern metadata, laser properties, safety data
    
    Features:
    - Thread-safe caching via CacheManager
    - Fail-fast validation
    - Author resolution
    - Specialized loaders for laser properties
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize contaminants data loader"""
        super().__init__(project_root)
        self.data_dir = self.project_root / 'data' / 'contaminants'
        
        # File paths
        self.contaminants_file = self.data_dir / 'Contaminants.yaml'
    
    def _get_data_file_path(self) -> Path:
        """Return path to primary data file (Contaminants.yaml)"""
        return self.contaminants_file
    
    def _validate_loaded_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate Contaminants.yaml structure.
        
        Args:
            data: Loaded YAML data
        
        Returns:
            True if valid structure
        """
        # Contaminants.yaml should have 'contamination_patterns' key
        return 'contamination_patterns' in data
    
    def load_patterns(self) -> Dict[str, Any]:
        """
        Load all contamination patterns from Contaminants.yaml.
        
        Returns:
            Dict mapping pattern_id to pattern data
            Example: {"rust_oxidation": {...}, "paint_coatings": {...}}
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        # Check cache first
        cached = cache_manager.get('contaminants', 'patterns')
        if cached:
            return cached
        
        # Load using base class method
        data = self._load_yaml_file(self.contaminants_file)
        patterns = data.get('contamination_patterns', {})
        
        # Cache for 1 hour
        cache_manager.set('contaminants', 'patterns', patterns, ttl=3600)
        
        return patterns
    
    def get_pattern(self, pattern_id: str, resolve_author: bool = True) -> Dict[str, Any]:
        """
        Get single contamination pattern by ID.
        
        Args:
            pattern_id: Pattern identifier (e.g., 'rust_oxidation')
            resolve_author: If True, resolve author ID to complete author object
        
        Returns:
            Pattern data dictionary
        
        Raises:
            ConfigurationError: If pattern not found
        """
        patterns = self.load_patterns()
        
        if pattern_id not in patterns:
            from shared.validation.errors import ConfigurationError
            available = list(patterns.keys())[:10]  # Show first 10
            raise ConfigurationError(
                f"Pattern '{pattern_id}' not found in Contaminants.yaml. "
                f"Available patterns (showing first 10): {available}"
            )
        
        pattern_data = patterns[pattern_id].copy()
        
        # Resolve author from registry if requested and available
        if resolve_author and resolve_author_for_generation and 'author' in pattern_data:
            try:
                author = resolve_author_for_generation(pattern_data)
                if author:
                    pattern_data['author'] = author
                    logger.debug(f"Resolved author for pattern '{pattern_id}'")
            except Exception as e:
                logger.warning(f"Could not resolve author for pattern '{pattern_id}': {e}")
        
        return pattern_data
    
    def get_pattern_metadata(self, pattern_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get pattern metadata (description, mechanism, environments).
        
        Args:
            pattern_id: Specific pattern (None = all patterns)
        
        Returns:
            Pattern metadata (excludes laser_properties)
        """
        patterns = self.load_patterns()
        
        if pattern_id is None:
            # Return metadata for all patterns
            return {
                pid: {
                    'pattern_id': pid,
                    'name': pdata.get('name', ''),
                    'description': pdata.get('description', ''),
                    'removal_mechanism': pdata.get('removal_mechanism', ''),
                    'common_environments': pdata.get('common_environments', []),
                    'valid_materials': pdata.get('valid_materials', [])
                }
                for pid, pdata in patterns.items()
            }
        else:
            # Return metadata for specific pattern
            pattern_data = self.get_pattern(pattern_id, resolve_author=False)
            return {
                'pattern_id': pattern_id,
                'name': pattern_data.get('name', ''),
                'description': pattern_data.get('description', ''),
                'removal_mechanism': pattern_data.get('removal_mechanism', ''),
                'common_environments': pattern_data.get('common_environments', []),
                'valid_materials': pattern_data.get('valid_materials', [])
            }
    
    def get_optical_properties(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get optical properties for a contamination pattern.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Dict with optical properties (absorptivity, reflectivity, etc.)
        
        Raises:
            ConfigurationError: If pattern or properties not found
        """
        pattern_data = self.get_pattern(pattern_id, resolve_author=False)
        
        from shared.validation.errors import ConfigurationError
        
        laser_props = pattern_data.get('laser_properties', {})
        if not laser_props:
            raise ConfigurationError(
                f"Pattern '{pattern_id}' has no laser_properties section"
            )
        
        optical = laser_props.get('optical_properties', {})
        if not optical:
            from shared.validation.errors import ConfigurationError
            raise ConfigurationError(
                f"Pattern '{pattern_id}' has no optical_properties in laser_properties"
            )
        
        return optical
    
    def get_laser_parameters(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get recommended laser parameters for a contamination pattern.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Dict with laser parameters (wavelengths, power, etc.)
        
        Raises:
            ConfigurationError: If pattern or parameters not found
        """
        pattern_data = self.get_pattern(pattern_id, resolve_author=False)
        
        laser_props = pattern_data.get('laser_properties', {})
        if not laser_props:
            from shared.validation.errors import ConfigurationError
            raise ConfigurationError(
                f"Pattern '{pattern_id}' has no laser_properties section"
            )
        
        params = laser_props.get('recommended_parameters', {})
        if not params:
            from shared.validation.errors import ConfigurationError
            raise ConfigurationError(
                f"Pattern '{pattern_id}' has no recommended_parameters in laser_properties"
            )
        
        return params
    
    def get_safety_data(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get safety considerations for a contamination pattern.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Dict with safety data (hazards, precautions, etc.)
        
        Raises:
            ConfigurationError: If pattern or safety data not found
        """
        pattern_data = self.get_pattern(pattern_id, resolve_author=False)
        
        laser_props = pattern_data.get('laser_properties', {})
        if not laser_props:
            from shared.validation.errors import ConfigurationError
            raise ConfigurationError(
                f"Pattern '{pattern_id}' has no laser_properties section"
            )
        
        safety = laser_props.get('safety_considerations', {})
        if not safety:
            from shared.validation.errors import ConfigurationError
            raise ConfigurationError(
                f"Pattern '{pattern_id}' has no safety_considerations in laser_properties"
            )
        
        return safety
    
    def get_patterns_for_material(self, material_name: str) -> List[Dict[str, Any]]:
        """
        Get all contamination patterns applicable to a material.
        
        Args:
            material_name: Material name (e.g., 'Steel', 'Aluminum')
        
        Returns:
            List of pattern data dicts
        """
        patterns = self.load_patterns()
        
        applicable = []
        for pattern_id, pattern_data in patterns.items():
            valid_materials = pattern_data.get('valid_materials', [])
            
            # Check if 'ALL' or material name in valid_materials
            if 'ALL' in valid_materials or material_name in valid_materials:
                pattern_with_id = pattern_data.copy()
                pattern_with_id['pattern_id'] = pattern_id
                applicable.append(pattern_with_id)
        
        return applicable
    
    def get_patterns_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all patterns in a category.
        
        Args:
            category: Category name (e.g., 'contamination', 'aging')
        
        Returns:
            List of pattern data dicts
        """
        patterns = self.load_patterns()
        
        matching = []
        for pattern_id, pattern_data in patterns.items():
            if pattern_data.get('category') == category:
                pattern_with_id = pattern_data.copy()
                pattern_with_id['pattern_id'] = pattern_id
                matching.append(pattern_with_id)
        
        return matching
    
    def get_all_pattern_ids(self) -> List[str]:
        """
        Get list of all pattern IDs.
        
        Returns:
            List of pattern identifiers
        """
        patterns = self.load_patterns()
        return list(patterns.keys())
    
    def validate_pattern_exists(self, pattern_id: str) -> bool:
        """
        Check if a pattern exists.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            True if pattern exists, False otherwise
        """
        patterns = self.load_patterns()
        return pattern_id in patterns


# Backward compatibility: Export alias for old name
PatternDataLoaderV2 = ContaminantsDataLoader
