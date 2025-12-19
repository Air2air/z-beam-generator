"""
Material Properties Library Enricher

Expands material_properties relationships with full property sets.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from export.enrichers.base import BaseLibraryEnricher


class MaterialPropertiesEnricher(BaseLibraryEnricher):
    """Enricher for material properties library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with material properties library."""
        if library_file is None:
            library_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'materials' / 'MaterialPropertyLibrary.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get property set by ID."""
        property_sets = self.library_data.get('material_properties', {})
        
        # Handle dict-based library (O(1) lookup)
        if isinstance(property_sets, dict):
            return property_sets.get(entry_id)
        
        # Handle legacy list-based library (O(n) lookup)
        for prop_set in property_sets:
            if prop_set.get('id') == entry_id:
                return prop_set
                
        return None
    
    def enrich(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich material properties relationships.
        
        Args:
            relationships: List of material_properties relationships
            
        Returns:
            List of enriched property sets
        """
        enriched = []
        
        for rel in relationships:
            entry_id = rel.get('id')
            if not entry_id:
                continue
                
            # Get base property set
            props = self.get_entry(entry_id)
            if not props:
                continue
                
            # Apply overrides
            overrides = rel.get('overrides', {})
            if overrides:
                props = self.apply_overrides(props, overrides)
                
            enriched.append(props)
            
        return enriched
