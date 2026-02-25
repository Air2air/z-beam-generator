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
