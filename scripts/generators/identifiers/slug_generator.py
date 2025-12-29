"""
Slug Generator - Generate slug fields from item IDs

Populates 'slug' field in source YAML data.
Slug is typically the item ID (already slugified).

Dependencies: None (base generator, runs first)

Example:
    materials:
      aluminum-laser-cleaning:
        name: "Aluminum"
        slug: "aluminum-laser-cleaning"  # ← Generated
"""

import logging
from typing import Dict, Any, List

from scripts.generators.base_generator import BaseGenerator

logger = logging.getLogger(__name__)


class SlugGenerator(BaseGenerator):
    """
    Generate slug fields from item IDs.
    
    Slug is the URL-friendly identifier for an item.
    In most cases, slug = item_id (already slugified).
    """
    
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate slug fields for all items.
        
        Args:
            data: Domain data dict
        
        Returns:
            Data with slug fields populated
        """
        count = 0
        for item_id, item_data in data.items():
            if not isinstance(item_data, dict):
                continue
            
            # Only generate if missing
            if 'slug' not in item_data:
                item_data['slug'] = item_id
                count += 1
        
        self._log_progress(f"Generated slugs for {count} items", count)
        return data
    
    def get_generated_fields(self) -> List[str]:
        """Return list of generated fields"""
        return ['slug']
    
    def get_dependencies(self) -> List[str]:
        """No dependencies (base generator)"""
        return []
