"""
Section Metadata Generator - Wraps SectionMetadataEnricher as a generator

This allows section metadata wrapping to run AFTER RelationshipsGenerator
populates relationship fields in the generators phase.

Created: December 22, 2025
Purpose: Enable section metadata to wrap dynamically generated relationships
"""

import logging
from typing import Any, Dict

from export.enrichers.metadata.section_metadata_enricher import SectionMetadataEnricher

logger = logging.getLogger(__name__)


class SectionMetadataGenerator:
    """
    Generator wrapper for SectionMetadataEnricher.
    
    Runs in generators phase (after RelationshipsGenerator) to wrap
    relationship arrays with display metadata.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize generator with enricher.
        
        Args:
            config: Generator configuration (passed to enricher)
        """
        self.enricher = SectionMetadataEnricher(config)
        logger.info(f"Initialized SectionMetadataGenerator with {len(config.get('sections', {}))} sections")
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate section metadata by delegating to enricher.
        
        Args:
            frontmatter: Frontmatter dict with relationships to wrap
        
        Returns:
            Frontmatter with relationships wrapped in _section metadata
        """
        return self.enricher.enrich(frontmatter)
