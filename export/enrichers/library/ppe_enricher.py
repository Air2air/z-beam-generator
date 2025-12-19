"""
PPE Requirements Library Enricher

Expands ppe_requirements relationships with full PPE templates.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from export.enrichers.base import BaseLibraryEnricher


class PPELibraryEnricher(BaseLibraryEnricher):
    """Enricher for PPE requirements library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with PPE library."""
        if library_file is None:
            library_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'safety' / 'PPELibrary.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get PPE template by ID."""
        templates = self.library_data.get('ppe_templates', {})
        
        # Handle both dict (O(1)) and list (O(n)) structures
        if isinstance(templates, dict):
            return templates.get(entry_id)
        else:
            for template in templates:
                if template.get('id') == entry_id:
                    return template
        
        return None
    
    def enrich(self, relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enrich PPE requirements relationship (typically single entry).
        
        Args:
            relationships: List of ppe_requirements relationships
            
        Returns:
            Enriched PPE data (single template)
        """
        if not relationships:
            return {}
            
        # Usually only one PPE template per compound
        rel = relationships[0]
        
        entry_id = rel.get('id')
        if not entry_id:
            return {}
            
        # Get base template
        template = self.get_entry(entry_id)
        if not template:
            return {}
            
        # Apply overrides
        overrides = rel.get('overrides', {})
        if overrides:
            template = self.apply_overrides(template, overrides)
            
        return template
