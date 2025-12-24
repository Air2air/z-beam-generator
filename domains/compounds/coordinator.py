"""
Compounds Domain Coordinator
Orchestrates content generation for hazardous compound safety profiles.

REFACTORED (December 24, 2025):
Now extends UniversalDomainCoordinator to eliminate duplication.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from shared.domain.base_coordinator import UniversalDomainCoordinator
from domains.compounds.data_loader import CompoundDataLoader

logger = logging.getLogger(__name__)


class CompoundCoordinator(UniversalDomainCoordinator):
    """
    Coordinates content generation for the compounds domain.
    
    Extends UniversalDomainCoordinator to provide:
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
        """Create compounds data loader"""
        return CompoundDataLoader()
    
    def _get_item_data(self, item_id: str) -> Dict:
        """Get compound data from Compounds.yaml"""
        compound = self.data_loader.get_compound(item_id)
        if not compound:
            raise ValueError(f"Compound not found: {item_id}")
        return compound
    
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
        
        Wrapper for universal generate_content method with compounds-specific naming.
        
        Args:
            compound_id: Compound identifier (e.g., "formaldehyde")
            component_type: Type of content to generate (e.g., "description")
            force_regenerate: Whether to regenerate even if content exists
            
        Returns:
            Dict with generation results (see UniversalDomainCoordinator.generate_content)
        """
        return self.generate_content(compound_id, component_type, force_regenerate)
    
    def generate_all_components_for_compound(
        self,
        compound_id: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate all enabled component types for a compound.
        
        Args:
            compound_id: Compound identifier
            force_regenerate: Whether to regenerate existing content
            
        Returns:
            Dict with results for each component type
        """
        results = {}
        enabled_types = [
            comp_type for comp_type, config in self.domain_config['component_types'].items()
            if config.get('enabled', True)
        ]
        
        logger.info(
            f"Generating {len(enabled_types)} component types for {compound_id}: "
            f"{enabled_types}"
        )
        
        for component_type in enabled_types:
            try:
                result = self.generate_compound_content(
                    compound_id=compound_id,
                    component_type=component_type,
                    force_regenerate=force_regenerate
                )
                results[component_type] = result
            except Exception as e:
                logger.error(
                    f"Failed to generate {component_type} for {compound_id}: {e}"
                )
                results[component_type] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    def get_compound_data(self, compound_id: str) -> Optional[Dict[str, Any]]:
        """Get compound data for context."""
        return self.data_loader.get_compound(compound_id)
    
    def list_compounds(self) -> list:
        """Get list of all compound IDs."""
        return self.data_loader.list_compound_ids()
