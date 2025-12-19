"""
Emergency Response Library Enricher

Expands emergency_response relationships with full emergency procedures.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from export.enrichers.base import BaseLibraryEnricher


class EmergencyResponseEnricher(BaseLibraryEnricher):
    """Enricher for emergency response library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with emergency response library."""
        if library_file is None:
            library_file = Path(__file__).parent.parent.parent / 'data' / 'safety' / 'EmergencyResponseLibrary.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get emergency response template by ID."""
        templates = self.library_data.get('response_templates', {})
        
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
        Enrich emergency response relationship (typically single entry).
        
        Args:
            relationships: List of emergency_response relationships
            
        Returns:
            Enriched emergency response data (single template)
        """
        if not relationships:
            return {}
            
        # Usually only one emergency template per compound
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
