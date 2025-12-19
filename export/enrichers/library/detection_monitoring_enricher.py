"""
Detection and Monitoring Library Enricher

Expands detection_monitoring relationships with full sensor/method data.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from export.enrichers.base import BaseLibraryEnricher


class DetectionMonitoringEnricher(BaseLibraryEnricher):
    """Enricher for detection and monitoring library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with detection monitoring library."""
        if library_file is None:
            library_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'monitoring' / 'DetectionMonitoring.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get monitoring method profile by ID."""
        methods = self.library_data.get('detection_monitoring', {})
        
        # Handle both dict (O(1)) and list (O(n)) structures
        if isinstance(methods, dict):
            return methods.get(entry_id)
        else:
            for method in methods:
                if method.get('id') == entry_id:
                    return method
        
        return None
    
    def enrich(self, relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enrich detection monitoring relationship (typically single entry).
        
        Args:
            relationships: List of detection_monitoring relationships
            
        Returns:
            Enriched monitoring data (single profile)
        """
        if not relationships:
            return {}
            
        # Usually only one monitoring profile per compound
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
