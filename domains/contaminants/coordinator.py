"""
Contaminants Domain Coordinator
Orchestrates content generation for contamination pattern removal profiles.

Created: December 26, 2025
Extends DomainCoordinator base class to provide unified generation architecture.
"""

import logging
from typing import Any, Dict, Optional

from shared.domain.base_coordinator import DomainCoordinator

logger = logging.getLogger(__name__)


class ContaminantCoordinator(DomainCoordinator):
    """
    Coordinates content generation for the contaminants domain.
    
    Extends DomainCoordinator to provide:
    - QualityEvaluatedGenerator initialization
    - Winston client integration
    - SubjectiveEvaluator setup
    - Domain config loading
    
    Domain-specific responsibilities:
    - Load contaminants data from Contaminants.yaml
    - Save generated content to Contaminants.yaml
    - Handle batch contaminant generation
    """
    
    @property
    def domain_name(self) -> str:
        """Return domain name for config loading"""
        return "contaminants"

    def _load_contaminants_data(self) -> Dict[str, Any]:
        """Load contaminants data with legacy key compatibility."""
        data = self._load_domain_data()

        contaminants = data.get('contaminants')
        contamination_patterns = data.get('contamination_patterns')

        if contaminants is None and contamination_patterns is not None:
            data['contaminants'] = contamination_patterns
        elif contamination_patterns is None and contaminants is not None:
            data['contamination_patterns'] = contaminants

        return data

    def list_contaminants(self) -> list:
        """Get list of all contaminant IDs."""
        data = self._load_contaminants_data()
        return list(data.get('contaminants', {}).keys())

    def get_contaminant_data(self, contaminant_id: str) -> Optional[Dict[str, Any]]:
        """Get contaminant data for context."""
        try:
            return self._get_item_data(contaminant_id)
        except ValueError:
            return None

    def generate_contaminant_content(
        self,
        contaminant_id: str,
        component_type: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """Legacy wrapper around generate_content()."""
        return self.generate_content(contaminant_id, component_type, force_regenerate)
