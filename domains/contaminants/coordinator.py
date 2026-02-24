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
    
    def _create_data_loader(self):
        """
        Create contaminants data loader.
        
        Note: Contaminants use load_contaminants_data() function, not class-based loader.
        Returns None since data loading is handled via _load_contaminants_data().
        """
        return None
    
    def _get_item_data(self, item_id: str) -> Dict:
        """Get contaminant data from Contaminants.yaml"""
        contaminants_data = self._load_domain_data()
        if item_id not in contaminants_data['contaminants']:
            raise ValueError(f"Contaminant '{item_id}' not found in Contaminants.yaml")
        return contaminants_data['contaminants'][item_id]
    
    def _save_content(self, item_id: str, component_type: str, content: str, author_id: Optional[int] = None) -> None:
        """Save content to Contaminants.yaml - handled by QualityEvaluatedGenerator"""
        # Note: QualityEvaluatedGenerator already saves to Contaminants.yaml
        # This method exists to satisfy abstract base class
        pass
    
    def generate_contaminant_content(
        self,
        contaminant_id: str,
        component_type: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content for a specific contaminant and component type.
        Alias for generate_content() with contaminants-specific naming.
        """
        return self.generate_content(contaminant_id, component_type, force_regenerate)

    def generate_all_components_for_contaminant(
        self,
        contaminant_id: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate all component types for a contaminant.
        Delegates to base generate_all_components() using prompt-directory discovery.
        """
        return self.generate_all_components(contaminant_id, force_regenerate)
    
    def get_contaminant_data(self, contaminant_id: str) -> Optional[Dict[str, Any]]:
        """Get contaminant data for context."""
        try:
            return self._get_item_data(contaminant_id)
        except ValueError:
            return None
    
    def _load_contaminants_data(self) -> Dict:
        """Load contaminants data - wrapper for _load_domain_data for backwards compatibility"""
        data = self._load_domain_data()

        # Backward compatibility: legacy callers/tests expect contamination_patterns
        if 'contamination_patterns' not in data and 'contaminants' in data:
            data['contamination_patterns'] = data['contaminants']

        return data
    
    def list_contaminants(self) -> list:
        """Get list of all contaminant IDs."""
        contaminants_data = self._load_contaminants_data()
        return list(contaminants_data['contaminants'].keys())
