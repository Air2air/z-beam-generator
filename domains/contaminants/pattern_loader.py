#!/usr/bin/env python3
"""
Pattern Data Loader with Caching

Unified loader for contamination pattern data from Contaminants.yaml.
Mirrors CategoryDataLoader architecture from Materials domain.

Features:
- Lazy loading for performance
- LRU caching for frequently accessed data
- Fail-fast validation per GROK_INSTRUCTIONS.md
- Thread-safe caching
- Specialized loaders for laser properties

Usage:
    loader = PatternDataLoader()
    
    # Load specific pattern
    rust_pattern = loader.get_pattern('rust_oxidation')
    
    # Load laser properties
    optical_props = loader.get_optical_properties('rust_oxidation')
    laser_params = loader.get_laser_parameters('rust_oxidation')
    safety = loader.get_safety_data('rust_oxidation')
    
    # Load all patterns
    all_patterns = loader.get_all_patterns()

Author: Z-Beam Generator
Date: November 25, 2025
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import threading

logger = logging.getLogger(__name__)

# Import author registry for author resolution
try:
    from data.authors.registry import resolve_author_for_generation
except ImportError:
    logger.warning("Could not import author registry - author resolution will be limited")
    resolve_author_for_generation = None


class ConfigurationError(Exception):
    """Raised when pattern data configuration is invalid"""
    pass


class PatternDataLoader:
    """
    Loader for contamination pattern data from Contaminants.yaml.
    
    Provides centralized access to pattern metadata, laser properties,
    safety data, and material applicability with LRU caching.
    """
    
    # Class-level cache lock for thread safety
    _cache_lock = threading.Lock()
    _instance_cache: Dict[str, Any] = {}
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the pattern data loader.
        
        Args:
            project_root: Path to project root. Auto-detected if not provided.
        """
        self.project_root = project_root or self._find_project_root()
        self.contaminants_data_dir = self.project_root / 'data' / 'contaminants'
        self.contaminants_file = self.contaminants_data_dir / 'Contaminants.yaml'
        
        if not self.contaminants_file.exists():
            raise ConfigurationError(
                f"Contaminants.yaml not found at: {self.contaminants_file}\n"
                f"Per GROK_INSTRUCTIONS.md: No fallbacks allowed."
            )
        
        logger.debug(f"PatternDataLoader using: {self.contaminants_file}")
    
    @staticmethod
    def _find_project_root() -> Path:
        """Find project root by looking for key markers"""
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            # Look for data/contaminants/Contaminants.yaml as marker
            if (parent / 'data' / 'contaminants' / 'Contaminants.yaml').exists():
                return parent
            # Fallback: Look for run.py (main entry point)
            if (parent / 'run.py').exists():
                return parent
        raise ConfigurationError(
            "Could not find project root (no data/contaminants/Contaminants.yaml or run.py found)"
        )
    
    def _load_yaml_file(self, filepath: Path) -> Dict[str, Any]:
        """Load and cache a YAML file"""
        cache_key = str(filepath)
        
        with self._cache_lock:
            if cache_key in self._instance_cache:
                return self._instance_cache[cache_key]
        
        if not filepath.exists():
            raise ConfigurationError(f"Required file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            with self._cache_lock:
                self._instance_cache[cache_key] = data
            
            return data
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {filepath}: {e}")
    
    def _load_contaminants_data(self) -> Dict[str, Any]:
        """Load complete Contaminants.yaml file"""
        return self._load_yaml_file(self.contaminants_file)
    
    def _get_key(self, key: str) -> Any:
        """Get a specific top-level key from Contaminants.yaml"""
        data = self._load_contaminants_data()
        
        if key not in data:
            raise ConfigurationError(f"Key '{key}' not found in {self.contaminants_file}")
        
        return data[key]
    
    # Public API - Pattern loaders
    
    def get_all_patterns(self) -> Dict[str, Any]:
        """
        Get all contamination patterns.
        
        Returns:
            Dict mapping pattern_id to pattern data
            Example: {"rust_oxidation": {...}, "paint_coatings": {...}}
        """
        return self._get_key('contamination_patterns')
    
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
        patterns = self.get_all_patterns()
        
        if pattern_id not in patterns:
            raise ConfigurationError(
                f"Pattern '{pattern_id}' not found in Contaminants.yaml. "
                f"Available: {list(patterns.keys())}"
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
        if pattern_id is None:
            patterns = self.get_all_patterns()
            return {
                pid: {
                    'pattern_id': pid,
                    'name': pdata.get('name', ''),
                    'description': pdata.get('description', ''),
                    'removal_mechanism': pdata.get('removal_mechanism', ''),
                    'severity_levels': pdata.get('severity_levels', []),
                    'typical_environments': pdata.get('typical_environments', []),
                    'valid_materials': pdata.get('valid_materials', []),
                    'prohibited_materials': pdata.get('prohibited_materials', [])
                }
                for pid, pdata in patterns.items()
            }
        
        pattern = self.get_pattern(pattern_id)
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
    
    # Laser properties loaders
    
    def get_optical_properties(
        self,
        pattern_id: Optional[str] = None,
        wavelength: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get optical properties for pattern(s).
        
        Args:
            pattern_id: Specific pattern (None = all patterns)
            wavelength: Filter by wavelength (e.g., '1064nm')
        
        Returns:
            Optical properties data
            
        Examples:
            # All patterns, all wavelengths
            all_optical = loader.get_optical_properties()
            
            # Specific pattern, all wavelengths
            rust_optical = loader.get_optical_properties('rust_oxidation')
            
            # Specific pattern, specific wavelength
            rust_1064 = loader.get_optical_properties('rust_oxidation', '1064nm')
        """
        if pattern_id is None:
            patterns = self.get_all_patterns()
            result = {}
            
            for pid, pdata in patterns.items():
                laser_props = pdata.get('laser_properties', {})
                optical = laser_props.get('optical_properties', {})
                
                if wavelength:
                    result[pid] = optical.get(wavelength, {})
                else:
                    result[pid] = optical
            
            return result
        
        pattern = self.get_pattern(pattern_id)
        laser_props = pattern.get('laser_properties', {})
        optical = laser_props.get('optical_properties', {})
        
        if wavelength:
            return optical.get(wavelength, {})
        
        return optical
    
    def get_thermal_properties(self, pattern_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get thermal properties for pattern(s).
        
        Args:
            pattern_id: Specific pattern (None = all patterns)
        
        Returns:
            Thermal properties data (ablation thresholds, decomposition temps, etc.)
        """
        if pattern_id is None:
            patterns = self.get_all_patterns()
            return {
                pid: pdata.get('laser_properties', {}).get('thermal_properties', {})
                for pid, pdata in patterns.items()
            }
        
        pattern = self.get_pattern(pattern_id)
        return pattern.get('laser_properties', {}).get('thermal_properties', {})
    
    def get_removal_characteristics(self, pattern_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get removal characteristics for pattern(s).
        
        Args:
            pattern_id: Specific pattern (None = all patterns)
        
        Returns:
            Removal characteristics (mechanism, efficiency, surface quality, byproducts)
        """
        if pattern_id is None:
            patterns = self.get_all_patterns()
            return {
                pid: pdata.get('laser_properties', {}).get('removal_characteristics', {})
                for pid, pdata in patterns.items()
            }
        
        pattern = self.get_pattern(pattern_id)
        return pattern.get('laser_properties', {}).get('removal_characteristics', {})
    
    def get_layer_properties(self, pattern_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get layer properties for pattern(s).
        
        Args:
            pattern_id: Specific pattern (None = all patterns)
        
        Returns:
            Layer properties (thickness ranges, penetration depth, adhesion)
        """
        if pattern_id is None:
            patterns = self.get_all_patterns()
            return {
                pid: pdata.get('laser_properties', {}).get('layer_properties', {})
                for pid, pdata in patterns.items()
            }
        
        pattern = self.get_pattern(pattern_id)
        return pattern.get('laser_properties', {}).get('layer_properties', {})
    
    def get_laser_parameters(self, pattern_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get recommended laser parameters for pattern(s).
        
        Args:
            pattern_id: Specific pattern (None = all patterns)
        
        Returns:
            Laser parameters (wavelength, fluence, scan speed, pulse duration, etc.)
        """
        if pattern_id is None:
            patterns = self.get_all_patterns()
            return {
                pid: pdata.get('laser_properties', {}).get('laser_parameters', {})
                for pid, pdata in patterns.items()
            }
        
        pattern = self.get_pattern(pattern_id)
        return pattern.get('laser_properties', {}).get('laser_parameters', {})
    
    def get_safety_data(self, pattern_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get safety requirements for pattern(s).
        
        Args:
            pattern_id: Specific pattern (None = all patterns)
        
        Returns:
            Safety data (fume composition, exposure limits, PPE, ventilation)
        """
        if pattern_id is None:
            patterns = self.get_all_patterns()
            return {
                pid: pdata.get('laser_properties', {}).get('safety_data', {})
                for pid, pdata in patterns.items()
            }
        
        pattern = self.get_pattern(pattern_id)
        return pattern.get('laser_properties', {}).get('safety_data', {})
    
    def get_selectivity_ratios(
        self,
        pattern_id: Optional[str] = None,
        material: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get selectivity ratios (contaminant/substrate absorption) for pattern(s).
        
        Args:
            pattern_id: Specific pattern (None = all patterns)
            material: Filter by substrate material
        
        Returns:
            Selectivity ratios data
        """
        if pattern_id is None:
            patterns = self.get_all_patterns()
            result = {}
            
            for pid, pdata in patterns.items():
                selectivity = pdata.get('laser_properties', {}).get('selectivity_ratios', {})
                
                if material:
                    result[pid] = selectivity.get(material, {})
                else:
                    result[pid] = selectivity
            
            return result
        
        pattern = self.get_pattern(pattern_id)
        selectivity = pattern.get('laser_properties', {}).get('selectivity_ratios', {})
        
        if material:
            return selectivity.get(material, {})
        
        return selectivity
    
    # Material applicability loaders
    
    def get_pattern_materials(self, pattern_id: str) -> Dict[str, List[str]]:
        """
        Get valid and prohibited materials for pattern.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            {
                'valid_materials': [...],
                'prohibited_materials': [...]
            }
        """
        pattern = self.get_pattern(pattern_id)
        return {
            'valid_materials': pattern.get('valid_materials', []),
            'prohibited_materials': pattern.get('prohibited_materials', [])
        }
    
    def get_patterns_for_material(self, material_name: str) -> Dict[str, List[str]]:
        """
        Get applicable patterns for a material.
        
        Args:
            material_name: Material name (e.g., 'Steel', 'Aluminum')
        
        Returns:
            {
                'valid_patterns': [...],  # Patterns that can treat this material
                'prohibited_patterns': [...]  # Patterns that cannot treat this material
            }
        """
        patterns = self.get_all_patterns()
        valid = []
        prohibited = []
        
        for pattern_id, pattern_data in patterns.items():
            if material_name in pattern_data.get('valid_materials', []):
                valid.append(pattern_id)
            elif material_name in pattern_data.get('prohibited_materials', []):
                prohibited.append(pattern_id)
        
        return {
            'valid_patterns': valid,
            'prohibited_patterns': prohibited
        }
    
    # Utility methods
    
    def get_pattern_ids(self) -> List[str]:
        """Get list of all pattern IDs"""
        return list(self.get_all_patterns().keys())
    
    def pattern_exists(self, pattern_id: str) -> bool:
        """Check if pattern exists"""
        try:
            self.get_pattern(pattern_id)
            return True
        except ConfigurationError:
            return False
    
    def has_laser_properties(self, pattern_id: str) -> bool:
        """Check if pattern has any laser properties defined"""
        pattern = self.get_pattern(pattern_id)
        return 'laser_properties' in pattern and bool(pattern['laser_properties'])
    
    def get_laser_property_coverage(self, pattern_id: str) -> Dict[str, bool]:
        """
        Check which laser properties are defined for pattern.
        
        Returns:
            {
                'optical_properties': True/False,
                'thermal_properties': True/False,
                'removal_characteristics': True/False,
                'layer_properties': True/False,
                'laser_parameters': True/False,
                'safety_data': True/False,
                'selectivity_ratios': True/False
            }
        """
        pattern = self.get_pattern(pattern_id)
        laser_props = pattern.get('laser_properties', {})
        
        return {
            'optical_properties': bool(laser_props.get('optical_properties')),
            'thermal_properties': bool(laser_props.get('thermal_properties')),
            'removal_characteristics': bool(laser_props.get('removal_characteristics')),
            'layer_properties': bool(laser_props.get('layer_properties')),
            'laser_parameters': bool(laser_props.get('laser_parameters')),
            'safety_data': bool(laser_props.get('safety_data')),
            'selectivity_ratios': bool(laser_props.get('selectivity_ratios'))
        }
    
    def clear_cache(self):
        """Clear the internal cache (useful for testing)"""
        with self._cache_lock:
            self._instance_cache.clear()
        logger.debug("PatternDataLoader cache cleared")


# Convenience functions for quick access

def load_pattern_data(pattern_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick access function to load pattern data.
    
    Args:
        pattern_id: Specific pattern ID (None = all patterns)
    
    Returns:
        Pattern data
    
    Example:
        >>> rust = load_pattern_data('rust_oxidation')
        >>> all_patterns = load_pattern_data()
    """
    loader = PatternDataLoader()
    
    if pattern_id is None:
        return loader.get_all_patterns()
    
    return loader.get_pattern(pattern_id)


def load_laser_properties(pattern_id: str, property_type: str) -> Dict[str, Any]:
    """
    Quick access to laser properties.
    
    Args:
        pattern_id: Pattern identifier
        property_type: One of: optical, thermal, removal, layer, parameters, safety, selectivity
    
    Returns:
        Laser property data
    
    Example:
        >>> optical = load_laser_properties('rust_oxidation', 'optical')
        >>> safety = load_laser_properties('rust_oxidation', 'safety')
    """
    loader = PatternDataLoader()
    
    method_map = {
        'optical': loader.get_optical_properties,
        'thermal': loader.get_thermal_properties,
        'removal': loader.get_removal_characteristics,
        'layer': loader.get_layer_properties,
        'parameters': loader.get_laser_parameters,
        'safety': loader.get_safety_data,
        'selectivity': loader.get_selectivity_ratios
    }
    
    if property_type not in method_map:
        raise ValueError(
            f"Invalid property_type '{property_type}'. "
            f"Options: {', '.join(method_map.keys())}"
        )
    
    return method_map[property_type](pattern_id)
