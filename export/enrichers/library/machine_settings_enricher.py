"""
Machine Settings Library Enricher

Expands machine_settings relationships with full preset configurations.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from export.enrichers.base import BaseLibraryEnricher


class MachineSettingsEnricher(BaseLibraryEnricher):
    """Enricher for machine settings library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with machine settings library."""
        if library_file is None:
            library_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'machine' / 'MachineSettings.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get machine preset by ID."""
        presets = self.library_data.get('machine_presets', [])
        
        for preset in presets:
            if preset.get('id') == entry_id:
                return preset
                
        return None
    
    def enrich(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich machine settings relationships.
        
        Args:
            relationships: List of machine_settings relationships
            
        Returns:
            List of enriched machine presets
        """
        enriched = []
        
        for rel in relationships:
            entry_id = rel.get('id')
            if not entry_id:
                continue
                
            # Get base preset
            preset = self.get_entry(entry_id)
            if not preset:
                continue
                
            # Apply overrides
            overrides = rel.get('overrides', {})
            if overrides:
                preset = self.apply_overrides(preset, overrides)
                
            enriched.append(preset)
            
        return enriched
