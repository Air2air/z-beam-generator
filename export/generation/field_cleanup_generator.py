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

from typing import Dict, Any
from export.generation.base import BaseGenerator
from export.enrichers.cleanup.field_cleanup_enricher import FieldCleanupEnricher
import logging

logger = logging.getLogger(__name__)


class FieldCleanupGenerator(BaseGenerator):
    """Remove redundant fields from relationship items."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize generator (reuses enricher logic)."""
        super().__init__(config)
        # Reuse enricher logic
        self.enricher = FieldCleanupEnricher(config)
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up redundant fields in all relationship items.
        
        Args:
            frontmatter: Frontmatter dict with relationships
        
        Returns:
            Frontmatter with cleaned items
        """
        # Delegate to enricher (it has all the logic)
        return self.enricher.enrich(frontmatter)
