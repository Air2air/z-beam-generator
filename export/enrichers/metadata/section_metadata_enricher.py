"""
Section Metadata Enricher - Adds display metadata to relationship sections.

This enricher wraps relationship arrays with presentation metadata:
- presentation: Display variant (card, list, table, etc.)
- items: Array of relationship items

Example transformation:
    Before:
        relationships:
          produces_compounds:
            - id: pahs-compound
              frequency: common
    
    After:
        relationships:
          produces_compounds:
            presentation: card
            items:
              - id: pahs-compound
                frequency: common

Compatible with Card Restructure (December 2025).
Migrated from _section structure to presentation structure.
"""

import logging
from typing import Dict, Any, List, Optional

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class SectionMetadataEnricher(BaseEnricher):
    """
    Enricher that adds presentation metadata wrappers to relationship fields.
    
    Configuration (in export/config/{domain}.yaml):
        - type: section_metadata
          module: export.enrichers.metadata.section_metadata_enricher
          class: SectionMetadataEnricher
          sections:
            produces_compounds:
              presentation: "card"
            produced_from_contaminants:
              presentation: "list"
    
    This enricher should run LATE in the pipeline (after all relationship
    enrichment is complete) so we're wrapping fully-enriched relationship data.
    
    Compatible with Card Restructure (December 2025) - uses 'presentation' key.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enricher.
        
        Args:
            config: Enricher config dict with 'sections' key
        """
        super().__init__(config)
        self.section_configs = config.get('sections', {})
        logger.info(f"Initialized SectionMetadataEnricher with {len(self.section_configs)} section configs")
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add section metadata wrappers to relationship fields.
        
        Args:
            frontmatter: Frontmatter dictionary
        
        Returns:
            Frontmatter with section metadata wrappers added
        """
        if 'relationships' not in frontmatter:
            return frontmatter
        
        relationships = frontmatter['relationships']
        if not isinstance(relationships, dict):
            return frontmatter
        
        item_id = frontmatter.get('id', 'unknown')
        wrapped_count = 0
        
        # Process each relationship field
        for field_name, field_data in list(relationships.items()):
            # Skip if no section config for this field
            if field_name not in self.section_configs:
                continue
            
            # Skip if already wrapped (has presentation key)
            if isinstance(field_data, dict) and 'presentation' in field_data:
                continue
            
            # Skip if data is not a list
            if not isinstance(field_data, list):
                continue
            
            # Get section config
            section_config = self.section_configs[field_name]
            
            # Create wrapper structure with presentation (new format)
            # Include empty lists for consistency
            wrapped_data = {
                'presentation': section_config.get('presentation', 'card'),
                'items': field_data
            }
            
            # Replace relationship field with wrapped version
            relationships[field_name] = wrapped_data
            wrapped_count += 1
            
            logger.debug(f"Wrapped {field_name} for {item_id} with presentation='{wrapped_data['presentation']}'")
        
        if wrapped_count > 0:
            logger.info(f"Added presentation metadata to {wrapped_count} relationship fields in {item_id}")
        
        return frontmatter
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate enricher configuration.
        
        Args:
            config: Enricher config dict
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if 'sections' not in config:
            errors.append("SectionMetadataEnricher requires 'sections' key in config")
            return errors
        
        sections = config['sections']
        if not isinstance(sections, dict):
            errors.append("'sections' must be a dictionary")
            return errors
        
        # Validate each section config
        for field_name, section_config in sections.items():
            if not isinstance(section_config, dict):
                errors.append(f"Section config for '{field_name}' must be a dictionary")
                continue
            
            # Title is required
            if 'title' not in section_config:
                errors.append(f"Section config for '{field_name}' missing required 'title' field")
            
            # Validate variant if provided
            valid_variants = ['relationship', 'info', 'grid', 'safety', 'default']
            if 'variant' in section_config and section_config['variant'] not in valid_variants:
                errors.append(
                    f"Section config for '{field_name}' has invalid variant '{section_config['variant']}'. "
                    f"Must be one of: {', '.join(valid_variants)}"
                )
            
            # Validate order if provided
            if 'order' in section_config and not isinstance(section_config['order'], int):
                errors.append(f"Section config for '{field_name}' has non-integer 'order' value")
        
        return errors
