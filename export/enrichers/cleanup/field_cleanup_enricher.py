"""
Field Cleanup Enricher - Removes redundant and unused fields from frontmatter.

Purpose:
- Remove redundant fields from relationship items (category, subcategory, slug)
- Remove unused fields (typical_context when "general")
- Clean up data across all domains

Target fields for removal:
- category (duplicated in URL)
- subcategory (duplicated in URL)
- slug (duplicated in id)
- typical_context (when value is "general")
"""

from typing import Dict, Any, List
from export.enrichers.base import BaseEnricher


class FieldCleanupEnricher(BaseEnricher):
    """Remove redundant and unused fields from relationship items."""
    
    REDUNDANT_FIELDS = ['category', 'subcategory', 'slug']
    
    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove redundant fields from all relationship items."""
        if 'relationships' not in data:
            return data
        
        relationships = data['relationships']
        
        # Clean all relationship sections
        for section_key, section_value in relationships.items():
            if isinstance(section_value, dict):
                # Handle grouped structure (e.g., materials.groups.metals.items)
                if 'groups' in section_value:
                    for group_key, group_value in section_value['groups'].items():
                        if isinstance(group_value, dict) and 'items' in group_value:
                            group_value['items'] = self._clean_items(group_value['items'])
                
                # Handle direct items (e.g., compounds.items)
                elif 'items' in section_value:
                    section_value['items'] = self._clean_items(section_value['items'])
            
            # Handle flat array (old pattern)
            elif isinstance(section_value, list):
                relationships[section_key] = self._clean_items(section_value)
        
        return data
    
    def _clean_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove redundant fields from a list of items."""
        cleaned_items = []
        
        for item in items:
            if not isinstance(item, dict):
                cleaned_items.append(item)
                continue
            
            # Remove redundant fields
            cleaned_item = {k: v for k, v in item.items() 
                          if k not in self.REDUNDANT_FIELDS}
            
            # Remove typical_context if it's "general"
            if cleaned_item.get('typical_context') == 'general':
                cleaned_item.pop('typical_context', None)
            
            cleaned_items.append(cleaned_item)
        
        return cleaned_items
