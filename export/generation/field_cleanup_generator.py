"""
Field Cleanup Generator
=======================

Removes redundant fields from relationship items after all enrichments/groupings complete.

Purpose:
- Remove category, subcategory (redundant with URL)
- Remove slug (duplicates id)
- Remove typical_context when value is "general"

Architecture Note:
- This is a GENERATOR not an ENRICHER
- Generators run AFTER enrichers, so this cleans up the final structure
- Reuses FieldCleanupEnricher logic

Created: December 19, 2025
Part of: Changes 2 & 5 - Remove redundant fields
"""

import logging
from typing import Any, Dict

# MIGRATION NOTE (Dec 29, 2025): FieldCleanupEnricher moved to UniversalContentGenerator
# from export.enrichers.cleanup.field_cleanup_enricher import FieldCleanupEnricher
from export.generation.base import BaseGenerator

logger = logging.getLogger(__name__)


class FieldCleanupGenerator(BaseGenerator):
    """
    DEPRECATED: Field cleanup now handled by UniversalContentGenerator.
    This generator returns frontmatter unchanged for backwards compatibility.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize generator."""
        super().__init__(config)
        logger.warning("FieldCleanupGenerator deprecated - use UniversalContentGenerator instead")
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pass through - functionality moved to UniversalContentGenerator.
        
        Args:
            frontmatter: Frontmatter dict
        
        Returns:
            Unchanged frontmatter
        """
        logger.debug("FieldCleanupGenerator pass-through (deprecated)")
        return frontmatter
        return self.enricher.enrich(frontmatter)
