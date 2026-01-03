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

import logging
from typing import Any, Dict

# MIGRATION NOTE (Dec 29, 2025): ContaminantMaterialsGroupingEnricher moved to UniversalContentGenerator
# from export.enrichers.grouping.contaminant_materials_grouping_enricher import (
#     ContaminantMaterialsGroupingEnricher,
# )
from export.generation.base import BaseGenerator

logger = logging.getLogger(__name__)


class ContaminantMaterialsGroupingGenerator(BaseGenerator):
    """
    DEPRECATED: Material grouping now handled by UniversalContentGenerator.
    This generator returns frontmatter unchanged for backwards compatibility.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize generator."""
        super().__init__(config)
        logger.warning("ContaminantMaterialsGroupingGenerator deprecated - use UniversalContentGenerator")
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pass through - functionality moved to UniversalContentGenerator.
        
        Args:
            frontmatter: Frontmatter dict
        
        Returns:
            Unchanged frontmatter
        """
        logger.debug("ContaminantMaterialsGroupingGenerator pass-through (deprecated)")
        return frontmatter
