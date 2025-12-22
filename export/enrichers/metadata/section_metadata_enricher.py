"""
Section Metadata Enricher - Adds display metadata to relationship sections.

This enricher wraps relationship arrays with section metadata:
- title: Section heading text
- description: Section description
- order: Render order
- variant: Display style
- icon: Icon identifier

Example transformation:
    Before:
        relationships:
          produces_compounds:
            - id: pahs-compound
              frequency: common
    
    After:
        relationships:
          produces_compounds:
            _section:
              title: "Compounds Produced"
              description: "Hazardous compounds released during laser cleaning"
              order: 2
              variant: "relationship"
              icon: "flask"
            items:
              - id: pahs-compound
                frequency: common

Part of Relationship Normalization V2 implementation.
"""

import logging
from typing import Dict, Any, List, Optional

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class SectionMetadataEnricher(BaseEnricher):
    """
    Enricher that adds section metadata wrappers to relationship fields.
    
    Configuration (in export/config/{domain}.yaml):
        - type: section_metadata
          module: export.enrichers.metadata.section_metadata_enricher
          class: SectionMetadataEnricher
          sections:
            produces_compounds:
              title: "Compounds Produced"
              description: "Hazardous compounds released during laser cleaning"
              order: 2
              variant: "relationship"
              icon: "flask"
            produced_from_contaminants:
              title: "Contaminant Sources"
              description: "Contaminants that produce this compound"
              order: 1
              variant: "relationship"
              icon: "droplet"
    
    This enricher should run LATE in the pipeline (after all relationship
    enrichment is complete) so we're wrapping fully-enriched relationship data.
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
            
            # Skip if already wrapped (has _section key)
            if isinstance(field_data, dict) and '_section' in field_data:
                continue
            
            # Skip if data is not a list or empty
            if not isinstance(field_data, list) or len(field_data) == 0:
                continue
            
            # Get section config
            section_config = self.section_configs[field_name]
            
            # Create wrapper structure
            wrapped_data = {
                '_section': {
                    'title': section_config.get('title', field_name.replace('_', ' ').title()),
                    'description': section_config.get('description', ''),
                    'order': section_config.get('order', 999),
                    'variant': section_config.get('variant', 'relationship'),
                    'icon': section_config.get('icon', '')
                },
                'items': field_data
            }
            
            # Remove empty description/icon if not provided
            if not wrapped_data['_section']['description']:
                del wrapped_data['_section']['description']
            if not wrapped_data['_section']['icon']:
                del wrapped_data['_section']['icon']
            
            # Replace relationship field with wrapped version
            relationships[field_name] = wrapped_data
            wrapped_count += 1
            
            logger.debug(f"Wrapped {field_name} for {item_id} with section metadata")
        
        if wrapped_count > 0:
            logger.info(f"Added section metadata to {wrapped_count} relationship fields in {item_id}")
        
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
