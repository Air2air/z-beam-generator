"""
Contaminant Appearance Library Enricher

Expands contaminant_appearance relationships with full visual characteristics.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from export.enrichers.base import BaseLibraryEnricher


class ContaminantAppearanceEnricher(BaseLibraryEnricher):
    """Enricher for contaminant appearance library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with contaminant appearance library."""
        if library_file is None:
            library_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'contaminants' / 'Contaminants.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get appearance pattern by ID."""
        patterns = self.library_data.get('contaminant_appearance', [])
        
        for pattern in patterns:
            if pattern.get('id') == entry_id:
                return pattern
                
        return None
    
    def enrich(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich contaminant appearance relationships.
        
        Args:
            relationships: List of contaminant_appearance relationships
            
        Returns:
            List of enriched appearance patterns
        """
        enriched = []
        
        for rel in relationships:
            entry_id = rel.get('id')
            if not entry_id:
                continue
                
            # Get base appearance pattern
            pattern = self.get_entry(entry_id)
            if not pattern:
                continue
                
            # Apply overrides
            overrides = rel.get('overrides', {})
            if overrides:
                pattern = self.apply_overrides(pattern, overrides)
                
            enriched.append(pattern)
            
        return enriched
