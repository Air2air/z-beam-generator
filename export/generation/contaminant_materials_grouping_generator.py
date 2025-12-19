"""
Contaminant Materials Grouping Generator
=========================================

Groups flat materials lists in contaminants by category.

Purpose:
- Transform flat materials arrays into semantic groups (metals, woods, plastics, etc.)
- Improves frontend UX for browsing 40-100+ materials
- Runs AFTER DomainLinkagesGenerator creates relationships.materials

Architecture Note:
- This is a GENERATOR not an ENRICHER
- Generators run after enrichers, so this can access the generated relationships
- Only processes contaminants domain

Created: December 19, 2025
Part of: Change 4 - Group Contaminants Relationships
"""

from typing import Dict, Any
from export.generation.base import BaseGenerator
from export.enrichers.grouping.contaminant_materials_grouping_enricher import ContaminantMaterialsGroupingEnricher
import logging

logger = logging.getLogger(__name__)


class ContaminantMaterialsGroupingGenerator(BaseGenerator):
    """Group contaminant materials into semantic categories."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize generator (reuses enricher logic)."""
        super().__init__(config)
        # Reuse enricher logic
        self.enricher = ContaminantMaterialsGroupingEnricher(config)
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Group materials in relationships by category.
        
        Args:
            frontmatter: Frontmatter dict with relationships.materials
        
        Returns:
            Frontmatter with grouped materials
        """
        # Delegate to enricher (it has all the logic)
        return self.enricher.enrich(frontmatter)
