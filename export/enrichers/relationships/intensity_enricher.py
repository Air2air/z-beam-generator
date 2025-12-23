"""
Intensity Enricher for Relationship Items

Dynamically generates the 'intensity' field for relationship items during export.
Eliminates data redundancy by deriving intensity from existing fields
(severity, hazard_level, effectiveness, frequency) rather than storing it.

This follows the standard export enrichment pattern used for URLs, breadcrumbs, etc.
"""

from typing import Any, Dict, List, Optional
import logging
from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


# Intensity mapping for negative fields (severity, hazard)
NEGATIVE_INTENSITY_MAP = {
    'negligible': 'slightly_negative',
    'low': 'slightly_negative',
    'minimal': 'slightly_negative',
    'moderate': 'negative',
    'medium': 'negative',
    'high': 'very_negative',
    'extreme': 'very_negative',
    'critical': 'very_negative',
}

# Intensity mapping for positive fields (effectiveness)
POSITIVE_INTENSITY_MAP = {
    'poor': 'slightly_negative',
    'fair': 'slightly_positive',
    'moderate': 'slightly_positive',
    'medium': 'slightly_positive',
    'good': 'positive',
    'excellent': 'very_positive',
}

# Intensity mapping for frequency (context-dependent: rare contamination = good)
FREQUENCY_INTENSITY_MAP = {
    'rare': 'slightly_positive',      # Less contamination = better
    'occasional': 'slightly_negative',
    'common': 'negative',
    'very_common': 'very_negative',   # More contamination = worse
}


def determine_intensity(item: Dict[str, Any]) -> Optional[str]:
    """
    Determine consolidated intensity for a relationship item.
    
    Priority order:
    1. severity (negative scale - bad when high)
    2. hazard_level (negative scale - bad when high)
    3. effectiveness (positive scale - good when high)
    4. frequency (negative scale - common contamination = bad)
    
    Args:
        item: Relationship item dictionary
        
    Returns:
        Intensity string or None
        - very_negative: severe hazards, high severity
        - negative: moderate hazards
        - slightly_negative: minor issues, common frequency
        - slightly_positive: minor benefits, rare frequency
        - positive: good performance
        - very_positive: excellent results
    """
    # Check severity/hazard (negative scale)
    if 'severity' in item:
        value = str(item['severity']).lower()
        if value in NEGATIVE_INTENSITY_MAP:
            return NEGATIVE_INTENSITY_MAP[value]
    
    if 'hazard_level' in item:
        value = str(item['hazard_level']).lower()
        if value in NEGATIVE_INTENSITY_MAP:
            return NEGATIVE_INTENSITY_MAP[value]
    
    # Check effectiveness (positive scale)
    if 'effectiveness' in item:
        value = str(item['effectiveness']).lower()
        if value in POSITIVE_INTENSITY_MAP:
            return POSITIVE_INTENSITY_MAP[value]
    
    # Check frequency (negative scale - more contamination = worse)
    if 'frequency' in item:
        value = str(item['frequency']).lower()
        if value in FREQUENCY_INTENSITY_MAP:
            return FREQUENCY_INTENSITY_MAP[value]
    
    return None


def enrich_intensity(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add intensity field to all relationship items in the data.
    
    Args:
        data: Frontmatter data dictionary (any domain)
        
    Returns:
        Enriched data with intensity fields added
    """
    # Check for relationships section
    if 'relationships' not in data:
        return data
    
    relationships = data['relationships']
    if not isinstance(relationships, dict):
        return data
    
    # Process each relationship type
    for rel_type, rel_items in relationships.items():
        if not isinstance(rel_items, dict) or 'items' not in rel_items:
            continue
        
        items = rel_items['items']
        if not isinstance(items, list):
            continue
        
        # Add intensity to each item
        for item in items:
            if not isinstance(item, dict):
                continue
            
            # Skip if intensity already exists (should not happen in source)
            if 'intensity' in item:
                continue
            
            # Determine and add intensity
            intensity = determine_intensity(item)
            if intensity:
                item['intensity'] = intensity
    
    return data


class IntensityEnricher(BaseEnricher):
    """
    Enricher that adds intensity field to relationship items.
    
    This enricher dynamically derives intensity from legacy categorical fields
    (severity, hazard_level, effectiveness, frequency) during export.
    
    Architecture: Eliminates 50% data redundancy by deriving on-demand instead
                  of storing redundant fields in source data.
    
    Usage:
        enricher = IntensityEnricher(config)
        enriched_data = enricher.enrich(frontmatter_data)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enricher.
        
        Args:
            config: Enricher config dict
        """
        super().__init__(config)
        logger.info("Initialized IntensityEnricher")
    
    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich frontmatter data with intensity fields.
        
        Args:
            data: Frontmatter data dictionary
            
        Returns:
            Enriched data
        """
        return enrich_intensity(data)
    
    def can_enrich(self, data: Dict[str, Any]) -> bool:
        """
        Check if this enricher can process the given data.
        
        Args:
            data: Frontmatter data dictionary
            
        Returns:
            True if data has relationships section
        """
        return 'relationships' in data and isinstance(data.get('relationships'), dict)
