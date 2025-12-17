#!/usr/bin/env python3
"""
Compound Lookup Service for Default Safety Data

PURPOSE: Provide default concentration_range and hazard_class values
         from Compounds.yaml for produces_compounds enrichment.

USAGE:
    from export.contaminants.compound_lookup import get_compound_defaults
    
    defaults = get_compound_defaults('iron-oxide')
    # Returns: {'concentration_range': '5.0 mg/m³', 'hazard_class': 'irritant'}
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Global cache for compounds data
_COMPOUNDS_CACHE: Optional[Dict] = None


def _load_compounds() -> Dict:
    """Load Compounds.yaml and cache it."""
    global _COMPOUNDS_CACHE
    
    if _COMPOUNDS_CACHE is None:
        compounds_path = Path(__file__).resolve().parents[2] / "data" / "compounds" / "Compounds.yaml"
        
        try:
            with open(compounds_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                _COMPOUNDS_CACHE = data.get('compounds', {})
                logger.debug(f"✅ Loaded {len(_COMPOUNDS_CACHE)} compounds")
        except Exception as e:
            logger.error(f"❌ Failed to load Compounds.yaml: {e}")
            _COMPOUNDS_CACHE = {}
    
    return _COMPOUNDS_CACHE


def get_compound_defaults(compound_id: str) -> Dict[str, str]:
    """
    Get default concentration_range and hazard_class for a compound.
    
    Args:
        compound_id: Compound ID (e.g., 'iron-oxide', 'carbon-monoxide')
    
    Returns:
        Dict with 'concentration_range' and 'hazard_class' if available
        Empty dict if compound not found or fields missing
    
    Example:
        >>> get_compound_defaults('iron-oxide')
        {'concentration_range': '5.0 mg/m³', 'hazard_class': 'irritant'}
        
        >>> get_compound_defaults('unknown-compound')
        {}
    """
    compounds = _load_compounds()
    
    if compound_id not in compounds:
        logger.debug(f"⚠️  Compound '{compound_id}' not found in Compounds.yaml")
        return {}
    
    compound_data = compounds[compound_id]
    result = {}
    
    # Extract concentration_range from typical_concentration_range
    if 'typical_concentration_range' in compound_data:
        result['concentration_range'] = compound_data['typical_concentration_range']
    
    # Extract hazard_class
    if 'hazard_class' in compound_data:
        result['hazard_class'] = compound_data['hazard_class']
    
    if result:
        logger.debug(f"✓ Found defaults for {compound_id}: {result}")
    else:
        logger.debug(f"⚠️  No hazard_class or typical_concentration_range for {compound_id}")
    
    return result


def normalize_compound_name(name: str) -> str:
    """
    Normalize compound name to ID format for lookup.
    
    Args:
        name: Compound name (e.g., 'Iron Oxide', 'Carbon Monoxide (CO)')
    
    Returns:
        Normalized ID (e.g., 'iron-oxide', 'carbon-monoxide')
    
    Examples:
        >>> normalize_compound_name('Iron Oxide')
        'iron-oxide'
        
        >>> normalize_compound_name('Carbon Monoxide (CO)')
        'carbon-monoxide'
        
        >>> normalize_compound_name('Nitrogen Oxides (NOx)')
        'nitrogen-oxides'
    """
    # Remove parenthetical suffixes (e.g., "(CO)", "(NOx)")
    if '(' in name:
        name = name.split('(')[0].strip()
    
    # Convert to lowercase and replace spaces/underscores with hyphens
    normalized = name.lower().replace(' ', '-').replace('_', '-')
    
    # Remove multiple consecutive hyphens
    while '--' in normalized:
        normalized = normalized.replace('--', '-')
    
    return normalized.strip('-')


def enrich_compound_with_defaults(compound: Dict) -> Dict:
    """
    Enrich a produces_compounds entry with default values from Compounds.yaml.
    
    Adds concentration_range and hazard_class if:
    - Fields are missing in the compound dict
    - Default values are available in Compounds.yaml
    
    Args:
        compound: Compound dict from produces_compounds array
    
    Returns:
        Enriched compound dict (original dict is NOT modified)
    
    Example:
        >>> compound = {'id': 'iron-oxide', 'title': 'Iron Oxide'}
        >>> enriched = enrich_compound_with_defaults(compound)
        >>> 'concentration_range' in enriched
        True
    """
    # Create a copy to avoid modifying original
    enriched = compound.copy()
    
    # Skip if both fields already present
    if 'concentration_range' in enriched and 'hazard_class' in enriched:
        return enriched
    
    # Get compound ID for lookup
    compound_id = enriched.get('id')
    if not compound_id:
        # Try to derive from title
        title = enriched.get('title', '')
        if title:
            compound_id = normalize_compound_name(title)
        else:
            logger.warning(f"⚠️  Compound missing both 'id' and 'title' - cannot enrich")
            return enriched
    
    # Remove -compound suffix if present (linkage IDs use this format)
    if compound_id.endswith('-compound'):
        compound_id = compound_id[:-9]  # Remove last 9 characters (-compound)
    
    # Get defaults from Compounds.yaml
    defaults = get_compound_defaults(compound_id)
    
    if not defaults:
        logger.debug(f"⚠️  No defaults available for {compound_id}")
        return enriched
    
    # Add missing fields
    added_fields = []
    
    if 'concentration_range' not in enriched and 'concentration_range' in defaults:
        enriched['concentration_range'] = defaults['concentration_range']
        added_fields.append('concentration_range')
    
    if 'hazard_class' not in enriched and 'hazard_class' in defaults:
        enriched['hazard_class'] = defaults['hazard_class']
        added_fields.append('hazard_class')
    
    if added_fields:
        logger.debug(f"✓ Added {', '.join(added_fields)} to {compound_id}")
    
    return enriched


def enrich_produces_compounds(produces_compounds: list) -> list:
    """
    Enrich all compounds in produces_compounds array with default values.
    
    Args:
        produces_compounds: List of compound dicts
    
    Returns:
        List of enriched compound dicts (original list is NOT modified)
    
    Example:
        >>> compounds = [
        ...     {'id': 'iron-oxide', 'title': 'Iron Oxide'},
        ...     {'id': 'carbon-monoxide', 'title': 'Carbon Monoxide'}
        ... ]
        >>> enriched = enrich_produces_compounds(compounds)
        >>> len(enriched)
        2
        >>> 'concentration_range' in enriched[0]
        True
    """
    if not produces_compounds:
        return []
    
    enriched_list = []
    for compound in produces_compounds:
        enriched = enrich_compound_with_defaults(compound)
        enriched_list.append(enriched)
    
    return enriched_list


if __name__ == "__main__":
    # Test the lookup service
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    
    print("=" * 80)
    print("COMPOUND LOOKUP SERVICE TEST")
    print("=" * 80)
    print()
    
    # Test individual lookups
    test_compounds = [
        'iron-oxide',
        'carbon-monoxide',
        'nitrogen-oxides',
        'chromium-vi',
        'unknown-compound'
    ]
    
    for compound_id in test_compounds:
        defaults = get_compound_defaults(compound_id)
        if defaults:
            print(f"✓ {compound_id}:")
            print(f"  concentration_range: {defaults.get('concentration_range', 'N/A')}")
            print(f"  hazard_class: {defaults.get('hazard_class', 'N/A')}")
        else:
            print(f"✗ {compound_id}: No defaults found")
        print()
    
    # Test normalization
    print("=" * 80)
    print("NAME NORMALIZATION TEST")
    print("=" * 80)
    print()
    
    test_names = [
        'Iron Oxide',
        'Carbon Monoxide (CO)',
        'Nitrogen Oxides (NOx)',
        'Chromium VI',
        'Polycyclic Aromatic Hydrocarbons (PAHs)'
    ]
    
    for name in test_names:
        normalized = normalize_compound_name(name)
        defaults = get_compound_defaults(normalized)
        status = "✓" if defaults else "✗"
        print(f"{status} '{name}' → '{normalized}' → {len(defaults)} fields")
    
    print()
    print("=" * 80)
