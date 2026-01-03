"""
Material Category Enricher for Settings

Looks up category and subcategory from Materials.yaml based on the material name
and adds them to settings frontmatter for hierarchical path construction.

Created: December 19, 2025
Purpose: Add category/subcategory to settings for proper full_path generation
"""

import logging
from pathlib import Path
from typing import Any, Dict

import yaml

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class MaterialCategoryEnricher(BaseEnricher):
    """
    Add material category/subcategory to settings frontmatter.
    
    Settings are per-material but don't include category information.
    This enricher looks up the material in Materials.yaml and copies
    its category and subcategory fields to settings frontmatter.
    
    This enables proper hierarchical paths like:
    /settings/metal/non-ferrous/aluminum-settings
    
    instead of flat:
    /settings/aluminum-settings
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enricher.
        
        Args:
            config: Enricher config with optional 'materials_file' key
        """
        super().__init__(config)
        
        # Load Materials.yaml
        materials_file = config.get('materials_file', 'data/materials/Materials.yaml')
        self.materials_path = Path(materials_file)
        
        if not self.materials_path.exists():
            raise FileNotFoundError(f"Materials file not found: {self.materials_path}")
        
        with open(self.materials_path, 'r') as f:
            data = yaml.safe_load(f)
            self.materials = data.get('materials', {})
        
        logger.info(f"MaterialCategoryEnricher initialized with {len(self.materials)} materials")
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add category and subcategory from Materials.yaml.
        
        Args:
            frontmatter: Settings frontmatter dict
        
        Returns:
            Frontmatter with category and subcategory fields added
        """
        # Get material name from frontmatter
        material_name = frontmatter.get('name')
        if not material_name:
            logger.warning("Settings frontmatter missing 'name' field")
            return frontmatter
        
        # Try to find matching material (case-insensitive)
        # Settings name might be "Aluminum" but material slug is "aluminum-laser-cleaning"
        material_data = None
        for mat_id, mat_data in self.materials.items():
            mat_display_name = mat_data.get('name', '')
            if mat_display_name.lower() == material_name.lower():
                material_data = mat_data
                break
        
        if not material_data:
            logger.warning(f"Material '{material_name}' not found in Materials.yaml")
            return frontmatter
        
        # Copy category and subcategory
        if 'category' in material_data:
            frontmatter['category'] = material_data['category']
            logger.debug(f"Added category: {material_data['category']}")
        
        if 'subcategory' in material_data:
            frontmatter['subcategory'] = material_data['subcategory']
            logger.debug(f"Added subcategory: {material_data['subcategory']}")
        
        return frontmatter
