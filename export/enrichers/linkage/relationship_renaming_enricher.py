"""
Relationship Renaming Enricher - Standardizes relationship section names.

Purpose:
- Rename relationships for consistency across domains
- Remove "related_" prefix (redundant)
- Use clear, descriptive names for specific relationships

Naming conventions:
- Simple nouns for basic relationships: materials, contaminants
- Descriptive prefixes only when clarifying role: source_, affected_
- Never use "related_" prefix

Domain-specific mappings:
- Contaminants: related_materials → materials
- Compounds: produced_by_contaminants → source_contaminants
- Compounds: found_on_materials → affected_materials  
- Settings: related_materials → materials, related_contaminants → contaminants
- Materials: Already correct (uses "contaminants")
"""

from typing import Any, Dict

from export.enrichers.base import BaseEnricher


class RelationshipRenamingEnricher(BaseEnricher):
    """Standardize relationship section names across domains."""
    
    # Domain-specific rename mappings
    RENAME_MAPS = {
        'contaminants': {
            'related_materials': 'materials',
            'related_contaminants': 'contaminants'
        },
        'compounds': {
            'produced_by_contaminants': 'source_contaminants',
            'found_on_materials': 'affected_materials',
            'related_materials': 'materials'
        },
        'settings': {
            'related_materials': 'materials',
            'related_contaminants': 'contaminants'
        }
        # Materials already uses "contaminants" - no changes needed
    }
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.domain = config.get('domain')
    
    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Rename relationship sections based on domain."""
        if 'relationships' not in data:
            return data
        
        # Get rename map for this domain
        rename_map = self.RENAME_MAPS.get(self.domain, {})
        if not rename_map:
            return data
        
        relationships = data['relationships']
        
        # Apply renames
        for old_name, new_name in rename_map.items():
            if old_name in relationships:
                relationships[new_name] = relationships.pop(old_name)
        
        return data
