"""
URL Generator - Generate URL fields from slug and category hierarchy

Populates 'url' and 'canonical_url' fields in source YAML data.

Dependencies: slug

Example:
    materials:
      aluminum-laser-cleaning:
        slug: "aluminum-laser-cleaning"
        category: "metal"
        url: "/materials/metal/aluminum-laser-cleaning"  # ← Generated
        canonical_url: "https://www.z-beam.com/materials/metal/aluminum-laser-cleaning"  # ← Generated
"""

import logging
from typing import Dict, Any, List

from scripts.generators.base_generator import BaseGenerator

logger = logging.getLogger(__name__)


class URLGenerator(BaseGenerator):
    """
    Generate URL fields from slug and category hierarchy.
    
    Builds relative and canonical URLs based on:
    - Domain (materials, contaminants, etc.)
    - Category (if present)
    - Subcategory (if present)
    - Slug
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize URL generator.
        
        Args:
            config: Config with 'domain' key
        """
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://www.z-beam.com')
    
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate URL fields for all items.
        
        Args:
            data: Domain data dict
        
        Returns:
            Data with url and canonical_url fields populated
        """
        count = 0
        for item_id, item_data in data.items():
            if not isinstance(item_data, dict):
                continue
            
            # Skip if already has URL
            if 'url' in item_data and 'canonical_url' in item_data:
                continue
            
            # Build URL path
            slug = item_data.get('slug', item_id)
            category = item_data.get('category', '')
            subcategory = item_data.get('subcategory', '')
            
            path_parts = [self.domain]
            if category:
                path_parts.append(category.lower())
            if subcategory:
                path_parts.append(subcategory.lower())
            path_parts.append(slug)
            
            # Generate URLs
            url = '/' + '/'.join(path_parts)
            canonical_url = self.base_url + url
            
            item_data['url'] = url
            item_data['canonical_url'] = canonical_url
            count += 1
        
        self._log_progress(f"Generated URLs for {count} items", count)
        return data
    
    def get_generated_fields(self) -> List[str]:
        """Return list of generated fields"""
        return ['url', 'canonical_url']
    
    def get_dependencies(self) -> List[str]:
        """Depends on slug field"""
        return ['slug']
    
    def validate_dependencies(self, data: Dict[str, Any]) -> bool:
        """Check that slug exists for all items"""
        return all(
            'slug' in item 
            for item in data.values() 
            if isinstance(item, dict)
        )
