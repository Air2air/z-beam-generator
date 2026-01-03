"""
Material Applications Library Enricher

Expands material_applications relationships with full application details.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from export.enrichers.base import BaseLibraryEnricher


class MaterialApplicationsEnricher(BaseLibraryEnricher):
    """Enricher for material applications library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with material applications library."""
        if library_file is None:
            library_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'materials' / 'MaterialApplications.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get application by ID."""
        applications = self.library_data.get('material_applications', {})
        
        # Handle dict-based library (O(1) lookup)
        if isinstance(applications, dict):
            return applications.get(entry_id)
        
        # Handle legacy list-based library (O(n) lookup)
        for app in applications:
            if app.get('id') == entry_id:
                return app
                
        return None
    
    def enrich(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich material applications relationships.
        
        Args:
            relationships: List of material_applications relationships
            
        Returns:
            List of enriched application data
        """
        enriched = []
        
        for rel in relationships:
            entry_id = rel.get('id')
            if not entry_id:
                continue
                
            # Get base application
            app = self.get_entry(entry_id)
            if not app:
                continue
                
            # Apply overrides
            overrides = rel.get('overrides', {})
            if overrides:
                app = self.apply_overrides(app, overrides)
                
            enriched.append(app)
            
        return enriched
