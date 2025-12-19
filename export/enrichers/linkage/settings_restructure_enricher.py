"""
Settings Restructure Enricher - Move machine_settings into relationships

Transforms settings frontmatter from flat structure to grouped relationships:
- machine_settings (root) → relationships.machine_settings

Created: December 19, 2025
Purpose: Normalize settings structure to match compounds/materials pattern
Pattern: Following CompoundRestructureEnricher architecture
"""

import logging
from typing import Dict, Any

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class SettingsRestructureEnricher(BaseEnricher):
    """
    Restructure settings frontmatter by moving machine_settings into relationships.
    
    BEFORE:
    ```yaml
    id: Aluminum
    machine_settings:
      powerRange: {...}
      wavelength: {...}
    relationships:
      related_materials: [...]
    ```
    
    AFTER:
    ```yaml
    id: Aluminum
    relationships:
      machine_settings:
        powerRange: {...}
        wavelength: {...}
      related_materials: [...]
    ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize settings restructure enricher."""
        super().__init__(config)
        logger.info("Initialized SettingsRestructureEnricher")
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Move machine_settings into relationships section.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Restructured frontmatter with machine_settings in relationships
        """
        # Initialize relationships if missing
        if 'relationships' not in frontmatter:
            frontmatter['relationships'] = {}
        
        # Move machine_settings if it exists at root
        if 'machine_settings' in frontmatter:
            frontmatter['relationships']['machine_settings'] = frontmatter.pop('machine_settings')
            logger.debug(f"Moved machine_settings into relationships")
        
        return frontmatter
