"""
Health Effects Library Enricher

Expands health_effects relationships with full toxicology data.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from export.enrichers.base import BaseLibraryEnricher


class HealthEffectsEnricher(BaseLibraryEnricher):
    """Enricher for health effects library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with health effects library."""
        if library_file is None:
            library_file = Path(__file__).parent.parent.parent / 'data' / 'safety' / 'HealthEffects.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get health effects profile by ID."""
        profiles = self.library_data.get('health_effects', {})
        
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
        Enrich health effects relationship (typically single entry).
        
        Args:
            relationships: List of health_effects relationships
            
        Returns:
            Enriched health effects data (single profile)
        """
        if not relationships:
            return {}
            
        # Usually only one health effects profile per compound
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
