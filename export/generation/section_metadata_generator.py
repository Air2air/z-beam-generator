"""
Section Metadata Generator - Wraps SectionMetadataEnricher as a generator

This allows section metadata wrapping to run AFTER RelationshipsGenerator
populates relationship fields in the generators phase.

Created: December 22, 2025
Purpose: Enable section metadata to wrap dynamically generated relationships
"""

import logging
from typing import Any, Dict

# MIGRATION NOTE (Dec 29, 2025): SectionMetadataEnricher functionality moved to UniversalContentGenerator
# This generator is now deprecated - use universal_content_generator task system instead
# from export.enrichers.metadata.section_metadata_enricher import SectionMetadataEnricher
from export.generation.base import BaseGenerator

logger = logging.getLogger(__name__)


class SectionMetadataGenerator(BaseGenerator):
    """
    DEPRECATED: Section metadata now handled by UniversalContentGenerator.
    This generator returns frontmatter unchanged for backwards compatibility.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize generator."""
        super().__init__(config)
        logger.warning("SectionMetadataGenerator deprecated - use UniversalContentGenerator instead")
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pass through - functionality moved to UniversalContentGenerator.
        
        Args:
            frontmatter: Frontmatter dict
        
        Returns:
            Unchanged frontmatter
        """
        logger.debug("SectionMetadataGenerator pass-through (deprecated)")
        return frontmatter
