"""
Environmental Impact Library Enricher

Expands environmental_impact relationships with full environmental data.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from export.enrichers.base import BaseLibraryEnricher


class EnvironmentalImpactEnricher(BaseLibraryEnricher):
    """Enricher for environmental impact library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with environmental impact library."""
        if library_file is None:
            library_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'environmental' / 'EnvironmentalImpact.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get environmental profile by ID."""
        profiles = self.library_data.get('environmental_impact', {})
        
        # Handle both dict (O(1)) and list (O(n)) structures
        if isinstance(profiles, dict):
            return profiles.get(entry_id)
        else:
            for profile in profiles:
                if profile.get('id') == entry_id:
                    return profile
        
        return None
    
    def enrich(self, relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enrich environmental impact relationship (typically single entry).
        
        Args:
            relationships: List of environmental_impact relationships
            
        Returns:
            Enriched environmental data (single profile)
        """
        if not relationships:
            return {}
            
        # Usually only one environmental profile per compound
        rel = relationships[0]
        
        entry_id = rel.get('id')
        if not entry_id:
            return {}
            
        # Get base profile
        profile = self.get_entry(entry_id)
        if not profile:
            return {}
            
        # Apply overrides
        overrides = rel.get('overrides', {})
        if overrides:
            profile = self.apply_overrides(profile, overrides)
            
        return profile
