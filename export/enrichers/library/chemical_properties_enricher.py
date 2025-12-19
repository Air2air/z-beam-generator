"""
Chemical Properties Library Enricher

Expands chemical_properties relationships with full physical/chemical data.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from export.enrichers.base import BaseLibraryEnricher


class ChemicalPropertiesEnricher(BaseLibraryEnricher):
    """Enricher for chemical properties library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with chemical properties library."""
        if library_file is None:
            library_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'compounds' / 'ChemicalProperties.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get chemical property set by ID."""
        properties = self.library_data.get('chemical_properties', {})
        
        # Handle both dict (O(1)) and list (O(n)) structures
        if isinstance(properties, dict):
            return properties.get(entry_id)
        else:
            for prop in properties:
                if prop.get('id') == entry_id:
                    return prop
        
        return None
    
    def enrich(self, relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enrich chemical properties relationship (typically single entry).
        
        Args:
            relationships: List of chemical_properties relationships
            
        Returns:
            Enriched chemical properties data (single set)
        """
        if not relationships:
            return {}
            
        # Usually only one chemical property set per compound
        rel = relationships[0]
        
        entry_id = rel.get('id')
        if not entry_id:
            return {}
            
        # Get base properties
        props = self.get_entry(entry_id)
        if not props:
            return {}
            
        # Apply overrides
        overrides = rel.get('overrides', {})
        if overrides:
            props = self.apply_overrides(props, overrides)
            
        return props
