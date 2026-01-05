"""
Contaminants Domain Coordinator
Orchestrates content generation for contamination pattern removal profiles.

Created: December 26, 2025
Extends DomainCoordinator base class to provide unified generation architecture.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional
import yaml

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
        if item_id not in contaminants_data['contamination_patterns']:
            raise ValueError(f"Contaminant '{item_id}' not found in Contaminants.yaml")
        return contaminants_data['contamination_patterns'][item_id]
    
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
        
        Wrapper for universal generate_content method with contaminants-specific naming.
        
        Args:
            contaminant_id: Contaminant identifier (e.g., "rust", "oil-spill")
            component_type: Type of content to generate (e.g., "description")
            force_regenerate: Whether to regenerate even if content exists
            
        Returns:
            Dict with generation results (see DomainCoordinator.generate_content)
        """
        return self.generate_content(contaminant_id, component_type, force_regenerate)
    
    def generate_all_components_for_contaminant(
        self,
        contaminant_id: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate all enabled component types for a contaminant.
        
        Args:
            contaminant_id: Contaminant identifier
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
            f"Generating {len(enabled_types)} component types for {contaminant_id}: "
            f"{enabled_types}"
        )
        
        for component_type in enabled_types:
            try:
                result = self.generate_contaminant_content(
                    contaminant_id=contaminant_id,
                    component_type=component_type,
                    force_regenerate=force_regenerate
                )
                results[component_type] = result
            except Exception as e:
                logger.error(
                    f"Failed to generate {component_type} for {contaminant_id}: {e}"
                )
                results[component_type] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    def get_contaminant_data(self, contaminant_id: str) -> Optional[Dict[str, Any]]:
        """Get contaminant data for context."""
        try:
            return self._get_item_data(contaminant_id)
        except ValueError:
            return None
    
    def _load_contaminants_data(self) -> Dict:
        """Load contaminants data - wrapper for _load_domain_data for backwards compatibility"""
        return self._load_domain_data()
    
    def list_contaminants(self) -> list:
        """Get list of all contaminant IDs."""
        contaminants_data = self._load_contaminants_data()
        return list(contaminants_data['contamination_patterns'].keys())
