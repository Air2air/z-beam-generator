#!/usr/bin/env python3
"""
Pattern Property Cache

LRU cache for contamination pattern property lookups.
Mirrors CategoryPropertyCache architecture from Materials domain.

Optimizes performance for repeated pattern data access,
especially useful when iterating over all patterns or
accessing laser properties multiple times.

Author: Z-Beam Generator
Date: November 25, 2025
"""

import logging
from functools import lru_cache
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PatternPropertyCache:
    """
    LRU cache for contamination pattern property lookups.
    
    Provides cached access to pattern data to avoid repeated YAML parsing.
    Thread-safe via functools.lru_cache implementation.
    
    Usage:
        cache = PatternPropertyCache()
        
        # Get optical properties (cached)
        optical = cache.get_optical_properties('rust_oxidation')
        
        # Get specific wavelength (cached)
        optical_1064 = cache.get_optical_properties('rust_oxidation', '1064nm')
        
        # Clear cache when data changes
        cache.clear_cache()
    """
    
    def __init__(self, max_size: int = 128):
        """
        Initialize pattern property cache.
        
        Args:
            max_size: Maximum number of cached entries (LRU eviction)
        """
        self.max_size = max_size
        
        # Create LRU-cached methods
        self._get_pattern_data = lru_cache(maxsize=max_size)(
            self._get_pattern_data_impl
        )
        self._get_laser_properties = lru_cache(maxsize=max_size)(
            self._get_laser_properties_impl
        )
        
        logger.debug(f"PatternPropertyCache initialized (max_size={max_size})")
    
    def _get_pattern_data_impl(self, pattern_id: str) -> Dict[str, Any]:
        """
        Load pattern data (implementation - not cached directly).
        
        Args:
            pattern_id: Contamination pattern ID
        
        Returns:
            Complete pattern data from Contaminants.yaml
        """
        from domains.contaminants.loaders.data_loader_v2 import PatternDataLoader
        
        loader = PatternDataLoader()
        return loader.get_pattern(pattern_id)
    
    def _get_laser_properties_impl(
        self,
        pattern_id: str,
        property_type: str
    ) -> Dict[str, Any]:
        """
        Load laser properties (implementation - not cached directly).
        
        Args:
            pattern_id: Contamination pattern ID
            property_type: optical_properties | thermal_properties | removal_characteristics | etc.
        
        Returns:
            Laser property data
        """
        pattern_data = self._get_pattern_data(pattern_id)
        return pattern_data.get('laser_properties', {}).get(property_type, {})
    
    # Public API - Cached methods
    
    def get_pattern_data(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get complete pattern data (cached).
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Pattern data dictionary
        """
        return self._get_pattern_data(pattern_id)
    
    def get_optical_properties(
        self,
        pattern_id: str,
        wavelength: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get optical properties (cached) with optional wavelength filter.
        
        Args:
            pattern_id: Pattern identifier
            wavelength: Optional wavelength filter (e.g., '1064nm')
        
        Returns:
            Optical properties data
        """
        props = self._get_laser_properties(pattern_id, 'optical_properties')
        
        if wavelength:
            return props.get(wavelength, {})
        
        return props
    
    def get_thermal_properties(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get thermal properties (cached).
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Thermal properties data
        """
        return self._get_laser_properties(pattern_id, 'thermal_properties')
    
    def get_removal_characteristics(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get removal characteristics (cached).
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Removal characteristics data
        """
        return self._get_laser_properties(pattern_id, 'removal_characteristics')
    
    def get_layer_properties(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get layer properties (cached).
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Layer properties data
        """
        return self._get_laser_properties(pattern_id, 'layer_properties')
    
    def get_laser_parameters(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get laser parameters (cached).
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Laser parameters data
        """
        return self._get_laser_properties(pattern_id, 'laser_parameters')
    
    def get_safety_data(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get safety data (cached).
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Safety data
        """
        return self._get_laser_properties(pattern_id, 'safety_data')
    
    def get_selectivity_ratios(
        self,
        pattern_id: str,
        material: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get selectivity ratios (cached) with optional material filter.
        
        Args:
            pattern_id: Pattern identifier
            material: Optional substrate material filter
        
        Returns:
            Selectivity ratios data
        """
        ratios = self._get_laser_properties(pattern_id, 'selectivity_ratios')
        
        if material:
            return ratios.get(material, {})
        
        return ratios
    
    def get_pattern_metadata(self, pattern_id: str) -> Dict[str, Any]:
        """
        Get pattern metadata (cached) - excludes laser properties.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Pattern metadata (name, description, mechanism, etc.)
        """
        pattern = self._get_pattern_data(pattern_id)
        
        return {
            'pattern_id': pattern_id,
            'name': pattern.get('name', ''),
            'description': pattern.get('description', ''),
            'removal_mechanism': pattern.get('removal_mechanism', ''),
            'severity_levels': pattern.get('severity_levels', []),
            'typical_environments': pattern.get('typical_environments', []),
            'valid_materials': pattern.get('valid_materials', []),
            'prohibited_materials': pattern.get('prohibited_materials', [])
        }
    
    def get_applicable_materials(self, pattern_id: str) -> Dict[str, list]:
        """
        Get material applicability (cached).
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            {
                'valid_materials': [...],
                'prohibited_materials': [...]
            }
        """
        pattern = self._get_pattern_data(pattern_id)
        
        return {
            'valid_materials': pattern.get('valid_materials', []),
            'prohibited_materials': pattern.get('prohibited_materials', [])
        }
    
    # Cache management
    
    def clear_cache(self):
        """
        Clear all cached data.
        
        Should be called when Contaminants.yaml is modified
        to ensure fresh data is loaded.
        """
        self._get_pattern_data.cache_clear()
        self._get_laser_properties.cache_clear()
        logger.debug("PatternPropertyCache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            {
                'pattern_data': {...},  # LRU cache info
                'laser_properties': {...}  # LRU cache info
            }
        """
        return {
            'pattern_data': self._get_pattern_data.cache_info()._asdict(),
            'laser_properties': self._get_laser_properties.cache_info()._asdict()
        }


# Global cache instance for convenience
_global_cache = None


def get_global_cache() -> PatternPropertyCache:
    """
    Get global pattern property cache instance.
    
    Lazily creates cache on first access.
    
    Returns:
        Global PatternPropertyCache instance
    
    Example:
        >>> from domains.contaminants.utils.pattern_cache import get_global_cache
        >>> cache = get_global_cache()
        >>> optical = cache.get_optical_properties('rust_oxidation')
    """
    global _global_cache
    
    if _global_cache is None:
        _global_cache = PatternPropertyCache()
    
    return _global_cache


def clear_global_cache():
    """Clear the global cache instance"""
    global _global_cache
    
    if _global_cache is not None:
        _global_cache.clear_cache()
