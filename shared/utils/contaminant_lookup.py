"""
Material-Contaminant Lookup Helpers (Hybrid Approach)

Provides O(1) lookup functions for querying contamination relationships
in both directions using the hybrid cached architecture.

Usage:
    from shared.utils.contaminant_lookup import (
        get_contaminants_for_material,
        get_materials_for_contaminant,
        is_contaminant_valid_for_material
    )
    
    # O(1) lookup: What contaminants affect Aluminum?
    contaminants = get_contaminants_for_material('Aluminum')
    # Returns: ['aluminum-oxidation', 'anodizing-defects', ...]
    
    # O(1) lookup: What materials can have rust?
    materials = get_materials_for_contaminant('rust-oxidation')
    # Returns: ['Steel', 'Iron', 'Cast Iron']
    
    # O(1) check: Can Aluminum have rust?
    valid = is_contaminant_valid_for_material('rust-oxidation', 'Aluminum')
    # Returns: False

Architecture:
    - Contaminants.yaml: SOURCE OF TRUTH (edit manually)
    - Materials.yaml: CACHED DATA (run sync script after changes)
    - This module: Fast O(1) lookups using cached data

Author: AI Assistant
Date: November 26, 2025
"""

from pathlib import Path
from typing import List, Optional, Tuple

import yaml

# Cache for loaded data
_materials_cache = None
_contaminants_cache = None


def _load_materials():
    """Load Materials.yaml with caching."""
    global _materials_cache
    
    if _materials_cache is None:
        materials_file = Path(__file__).parent.parent.parent / 'data' / 'materials' / 'Materials.yaml'
        with open(materials_file, 'r', encoding='utf-8') as f:
            _materials_cache = yaml.safe_load(f)
    
    return _materials_cache


def _load_contaminants():
    """Load Contaminants.yaml with caching."""
    global _contaminants_cache
    
    if _contaminants_cache is None:
        contaminants_file = Path(__file__).parent.parent.parent / 'data' / 'contaminants' / 'Contaminants.yaml'
        with open(contaminants_file, 'r', encoding='utf-8') as f:
            _contaminants_cache = yaml.safe_load(f)
    
    return _contaminants_cache


def get_contaminants_for_material(
    material_name: str,
    include_prohibited: bool = False
) -> List[str]:
    """
    Get all contamination patterns that can affect a material.
    
    Uses cached data from Materials.yaml for O(1) lookup.
    
    Args:
        material_name: Material name (e.g., 'Aluminum', 'Steel')
        include_prohibited: If True, also return prohibited contaminants
    
    Returns:
        List of contamination pattern IDs
        
    Example:
        >>> get_contaminants_for_material('Aluminum')
        ['aluminum-oxidation', 'anodizing-defects', 'anti-seize', ...]
        
        >>> get_contaminants_for_material('Aluminum', include_prohibited=True)
        (['aluminum-oxidation', ...], ['rust-oxidation', ...])
    """
    materials_data = _load_materials()
    materials = materials_data.get('materials', {})
    
    material = materials.get(material_name, {})
    valid = material.get('common_contaminants', [])
    
    if include_prohibited:
        prohibited = material.get('prohibited_contaminants', [])
        return valid, prohibited
    
    return valid


def get_materials_for_contaminant(
    contaminant_id: str,
    include_prohibited: bool = False
) -> List[str]:
    """
    Get all materials that can be affected by a contamination pattern.
    
    Uses source data from Contaminants.yaml for O(1) lookup.
    
    Args:
        contaminant_id: Contamination pattern ID (e.g., 'rust-oxidation')
        include_prohibited: If True, also return prohibited materials
    
    Returns:
        List of material names
        
    Example:
        >>> get_materials_for_contaminant('rust-oxidation')
        ['Steel', 'Iron', 'Cast Iron', 'Carbon Steel', 'Wrought Iron']
        
        >>> get_materials_for_contaminant('rust-oxidation', include_prohibited=True)
        (['Steel', ...], ['Aluminum', 'Copper', ...])
    """
    contaminants_data = _load_contaminants()
    patterns = contaminants_data.get('contamination_patterns', {})
    
    pattern = patterns.get(contaminant_id, {})
    valid = pattern.get('valid_materials', [])
    
    if include_prohibited:
        prohibited = pattern.get('prohibited_materials', [])
        return valid, prohibited
    
    return valid


def is_contaminant_valid_for_material(
    contaminant_id: str,
    material_name: str
) -> bool:
    """
    Check if a contamination pattern can affect a material.
    
    Fast O(1) check using cached data.
    
    Args:
        contaminant_id: Contamination pattern ID
        material_name: Material name
    
    Returns:
        True if contamination is valid for this material
        
    Example:
        >>> is_contaminant_valid_for_material('rust-oxidation', 'Steel')
        True
        
        >>> is_contaminant_valid_for_material('rust-oxidation', 'Aluminum')
        False
    """
    valid_materials = get_materials_for_contaminant(contaminant_id)
    return material_name in valid_materials


def get_contaminant_info(contaminant_id: str) -> Optional[dict]:
    """
    Get full contamination pattern data.
    
    Args:
        contaminant_id: Contamination pattern ID
    
    Returns:
        Pattern data dict or None if not found
        
    Example:
        >>> info = get_contaminant_info('rust-oxidation')
        >>> info['name']
        'Rust / Iron Oxide Formation'
        >>> info['laser_parameters']
        {...}
    """
    contaminants_data = _load_contaminants()
    patterns = contaminants_data.get('contamination_patterns', {})
    return patterns.get(contaminant_id)


def get_material_info(material_name: str) -> Optional[dict]:
    """
    Get full material data.
    
    Args:
        material_name: Material name
    
    Returns:
        Material data dict or None if not found
        
    Example:
        >>> info = get_material_info('Aluminum')
        >>> info['common_contaminants']
        ['aluminum-oxidation', ...]
    """
    materials_data = _load_materials()
    materials = materials_data.get('materials', {})
    return materials.get(material_name)


def clear_cache():
    """
    Clear cached data. Call after updating YAML files.
    
    Example:
        >>> # After running sync script
        >>> clear_cache()
        >>> contaminants = get_contaminants_for_material('Aluminum')
    """
    global _materials_cache, _contaminants_cache
    _materials_cache = None
    _contaminants_cache = None


def get_all_materials_with_contaminants() -> List[Tuple[str, int]]:
    """
    Get list of all materials that have contamination data.
    
    Returns:
        List of (material_name, contaminant_count) tuples, sorted by count
        
    Example:
        >>> materials = get_all_materials_with_contaminants()
        >>> materials[0]
        ('Steel', 44)
    """
    materials_data = _load_materials()
    materials = materials_data.get('materials', {})
    
    result = []
    for mat_name, mat_data in materials.items():
        contaminants = mat_data.get('common_contaminants', [])
        if contaminants:
            result.append((mat_name, len(contaminants)))
    
    return sorted(result, key=lambda x: -x[1])


def get_all_contaminants_with_materials() -> List[Tuple[str, str, int]]:
    """
    Get list of all contamination patterns with material counts.
    
    Returns:
        List of (pattern_id, name, material_count) tuples, sorted by count
        
    Example:
        >>> patterns = get_all_contaminants_with_materials()
        >>> patterns[0]
        ('environmental-dust', 'Environmental Dust Layer', 15)
    """
    contaminants_data = _load_contaminants()
    patterns = contaminants_data.get('contamination_patterns', {})
    
    result = []
    for pattern_id, pattern_data in patterns.items():
        name = pattern_data.get('name', pattern_id)
        materials = pattern_data.get('valid_materials', [])
        result.append((pattern_id, name, len(materials)))
    
    return sorted(result, key=lambda x: -x[2])
