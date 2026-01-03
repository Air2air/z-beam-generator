"""
Field Cleanup Enricher - Removes redundant and unused fields from frontmatter.

Purpose:
- Remove redundant fields from relationship items (category, subcategory, slug)
- Remove unused fields (typical_context when "general")
- **Remove empty items arrays** (Dec 23, 2025) - Prevents null/empty relationship sections
- Clean up data across all domains

Target fields for removal:
- category (duplicated in URL)
- subcategory (duplicated in URL)
- slug (duplicated in id)
- typical_context (when value is "general")
- Empty items arrays (prevents display issues)
"""

from typing import Any, Dict, List

from export.enrichers.base import BaseEnricher


class FieldCleanupEnricher(BaseEnricher):
    """Remove redundant and unused fields from relationship items."""
    
    REDUNDANT_FIELDS = ['category', 'subcategory', 'slug']
    
    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove redundant fields from all relationship items and remove empty items arrays."""
        if 'relationships' not in data:
            return data
        
        relationships = data['relationships']
        sections_to_remove = []
        
        # Debug logging
        item_id = data.get('id', 'unknown')
        
        # Clean all relationship sections
        for section_key, section_value in relationships.items():
            # Debug specific compound
            if item_id == 'metal-vapors-mixed' and section_key == 'exposure_limits':
                print(f"  [DEBUG] {item_id}.{section_key}:")
                print(f"    Type: {type(section_value)}")
                print(f"    Is dict: {isinstance(section_value, dict)}")
                if isinstance(section_value, dict):
                    print(f"    Keys: {section_value.keys()}")
                    print(f"    Has items: {'items' in section_value}")
                    print(f"    Has presentation: {'presentation' in section_value}")
            
            if isinstance(section_value, dict):
                # Handle grouped structure (e.g., materials.groups.metals.items)
                if 'groups' in section_value:
                    for group_key, group_value in section_value['groups'].items():
                        if isinstance(group_value, dict) and 'items' in group_value:
                            group_value['items'] = self._clean_items(group_value['items'])
                
                # Handle direct items (e.g., compounds.items)
                elif 'items' in section_value:
                    # Clean items
                    section_value['items'] = self._clean_items(section_value['items'])
                    
                    # Remove section if items array is now empty
                    if not section_value['items']:
                        sections_to_remove.append(section_key)
                        print(f"  [FieldCleanup] {item_id}: Removing {section_key} (empty items)")
                
                # Remove section if it has presentation but no items field
                # (This happens when items was removed from source)
                elif 'presentation' in section_value and 'items' not in section_value:
                    sections_to_remove.append(section_key)
                    print(f"  [FieldCleanup] {item_id}: Removing {section_key} (no items field)")
            
            # Handle flat array (old pattern)
            elif isinstance(section_value, list):
                relationships[section_key] = self._clean_items(section_value)
                
                # Remove section if list is empty
                if not relationships[section_key]:
                    sections_to_remove.append(section_key)
        
        # Remove empty sections
        for section_key in sections_to_remove:
            del relationships[section_key]
        
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
