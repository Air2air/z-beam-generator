"""
Breadcrumb Generator - Generate breadcrumb navigation arrays

Populates 'breadcrumb' and 'full_path' fields in source YAML data.

Dependencies: url

Example:
    materials:
      aluminum-laser-cleaning:
        url: "/materials/metal/aluminum-laser-cleaning"
        breadcrumb:  # ← Generated
          - label: "Home"
            href: "/"
          - label: "Materials"
            href: "/materials"
          - label: "Metal"
            href: "/materials/metal"
          - label: "Aluminum"
            href: "/materials/metal/aluminum-laser-cleaning"
        full_path: "/materials/metal/aluminum-laser-cleaning"  # ← Generated
"""

import logging
from typing import Dict, Any, List

from scripts.generators.base_generator import BaseGenerator

logger = logging.getLogger(__name__)


class BreadcrumbGenerator(BaseGenerator):
    """
    Generate breadcrumb navigation arrays.
    
    Creates hierarchical navigation:
    Home → Domain → Category → Subcategory → Item
    """
    
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate breadcrumb fields for all items.
        
        Args:
            data: Domain data dict
        
        Returns:
            Data with breadcrumb and full_path fields populated
        """
        count = 0
        for item_id, item_data in data.items():
            if not isinstance(item_data, dict):
                continue
            
            # Skip if already has breadcrumb
            if 'breadcrumb' in item_data:
                continue
            
            # Build breadcrumb array
            breadcrumb = [{"label": "Home", "href": "/"}]
            
            # Add domain level
            domain_label = self.domain.capitalize()
            breadcrumb.append({
                "label": domain_label,
                "href": f"/{self.domain}"
            })
            
            # Add category level
            category = item_data.get('category', '')
            if category:
                category_label = category.replace('-', ' ').replace('_', ' ').title()
                breadcrumb.append({
                    "label": category_label,
                    "href": f"/{self.domain}/{category.lower()}"
                })
            
            # Add subcategory level (if present)
            subcategory = item_data.get('subcategory', '')
            if subcategory:
                subcategory_label = subcategory.replace('-', ' ').replace('_', ' ').title()
                breadcrumb.append({
                    "label": subcategory_label,
                    "href": f"/{self.domain}/{category.lower()}/{subcategory.lower()}"
                })
            
            # Add current item
            name = item_data.get('name', '')
            url = item_data.get('url', '')
            
            if name and url:
                breadcrumb.append({
                    "label": name,
                    "href": url
                })
                
                item_data['breadcrumb'] = breadcrumb
                item_data['full_path'] = url
                count += 1
        
        self._log_progress(f"Generated breadcrumbs for {count} items", count)
        return data
    
    def get_generated_fields(self) -> List[str]:
        """Return list of generated fields"""
        return ['breadcrumb', 'full_path']
    
    def get_dependencies(self) -> List[str]:
        """Depends on url field"""
        return ['url']
    
    def validate_dependencies(self, data: Dict[str, Any]) -> bool:
        """Check that url exists for all items"""
        return all(
            'url' in item 
            for item in data.values() 
            if isinstance(item, dict)
        )
