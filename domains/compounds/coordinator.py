"""
Compounds Domain Coordinator
Orchestrates content generation for hazardous compound safety profiles.

REFACTORED (December 24, 2025):
Now extends DomainCoordinator to eliminate duplication.
"""

import logging
from typing import Any, Dict, Optional

from shared.domain.base_coordinator import DomainCoordinator

logger = logging.getLogger(__name__)


class CompoundCoordinator(DomainCoordinator):
    """
    Coordinates content generation for the compounds domain.
    
    Extends DomainCoordinator to provide:
    - QualityEvaluatedGenerator initialization
    - Winston client integration
    - SubjectiveEvaluator setup
    - Domain config loading
    
    Domain-specific responsibilities:
    - Load compounds data via CompoundDataLoader
    - Save generated content to Compounds.yaml
    - Handle batch compound generation
    """
    
    @property
    def domain_name(self) -> str:
        """Return domain name for config loading"""
        return "compounds"
    
    def _create_data_loader(self):
        """Compounds load data via _load_domain_data() in the base class."""
        return None

    def _get_item_data(self, item_id: str) -> Dict:
        """Get compound data from Compounds.yaml."""
        compounds_data = self._load_domain_data()
        if item_id not in compounds_data['compounds']:
            raise ValueError(f"Compound not found: {item_id}")
        return compounds_data['compounds'][item_id]
    
    def _save_content(self, item_id: str, component_type: str, content: str, author_id: Optional[int] = None) -> None:
        """Save content to Compounds.yaml - handled by QualityEvaluatedGenerator"""
        # Note: QualityEvaluatedGenerator already saves to Compounds.yaml
        # This method exists to satisfy abstract base class
        pass
    
    def generate_compound_content(
        self,
        compound_id: str,
        component_type: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content for a specific compound and component type.
        Alias for generate_content() with compounds-specific naming.
        """
        return self.generate_content(compound_id, component_type, force_regenerate)

    def generate_all_components_for_compound(
        self,
        compound_id: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate all component types for a compound.
        Delegates to base generate_all_components() using prompt-directory discovery.
        """
        return self.generate_all_components(compound_id, force_regenerate)

    def get_compound_data(self, compound_id: str) -> Optional[Dict[str, Any]]:
        """Get compound data for context."""
        try:
            return self._get_item_data(compound_id)
        except ValueError:
            return None

    def list_compounds(self) -> list:
        """Get list of all compound IDs."""
        return list(self._load_domain_data()['compounds'].keys())
