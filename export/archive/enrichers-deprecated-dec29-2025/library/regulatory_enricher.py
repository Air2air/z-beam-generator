"""
Regulatory Standards Library Enricher

Expands regulatory_standards relationships with full standard details.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from export.enrichers.base import BaseLibraryEnricher


class RegulatoryStandardsEnricher(BaseLibraryEnricher):
    """Enricher for regulatory standards library."""
    
    def __init__(self, library_file: Optional[Path] = None):
        """Initialize with regulatory standards library."""
        if library_file is None:
            # Navigate from export/enrichers/library/ to project root, then to data/regulatory/
            library_file = Path(__file__).parent.parent.parent.parent / 'data' / 'regulatory' / 'RegulatoryStandards.yaml'
        super().__init__(library_file)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get regulatory standard by ID."""
        standards = self.library_data.get('regulatory_standards', {})
        
        # Handle dict-based library (O(1) lookup)
        if isinstance(standards, dict):
            return standards.get(entry_id)
        
        # Handle legacy list-based library (O(n) lookup)
        for standard in standards:
            if standard.get('id') == entry_id:
                return standard
                
        return None
    
    def enrich(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich regulatory standards relationships.
        
        Args:
            relationships: List of regulatory_standards relationships
            
        Returns:
            List of enriched standard data
        """
        enriched = []
        
        for rel in relationships:
            entry_id = rel.get('id')
            if not entry_id:
                continue
                
            # Get base standard
            standard = self.get_entry(entry_id)
            if not standard:
                continue
                
            # Apply overrides if present
            overrides = rel.get('overrides', {})
            if overrides:
                standard = self.apply_overrides(standard, overrides)
                
            # Add relationship-specific fields
            if 'applicability' in rel:
                standard['applicability_note'] = rel['applicability']
            if 'compliance_status' in rel:
                standard['material_compliance_status'] = rel['compliance_status']
                
            enriched.append(standard)
            
        return enriched
