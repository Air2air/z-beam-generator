"""
Laser Parameters Library Enricher

Expands laser_parameters relationships with full parameter specifications.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from export.enrichers.base import BaseLibraryEnricher


class LaserParametersEnricher(BaseLibraryEnricher):
    """Enricher for laser parameters library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with laser parameters library."""
        if library_file is None:
            library_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'laser' / 'LaserParameters.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get laser parameter set by ID."""
        parameter_sets = self.library_data.get('laser_parameter_sets', [])
        
        for param_set in parameter_sets:
            if param_set.get('id') == entry_id:
                return param_set
                
        return None
    
    def enrich(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich laser parameters relationships.
        
        Args:
            relationships: List of laser_parameters relationships
            
        Returns:
            List of enriched parameter sets
        """
        enriched = []
        
        for rel in relationships:
            entry_id = rel.get('id')
            if not entry_id:
                continue
                
            # Get base parameter set
            params = self.get_entry(entry_id)
            if not params:
                continue
                
            # Apply overrides
            overrides = rel.get('overrides', {})
            if overrides:
                params = self.apply_overrides(params, overrides)
                
            # Add relationship context
            if 'material_specific_notes' in rel:
                params['material_notes'] = rel['material_specific_notes']
                
            enriched.append(params)
            
        return enriched
