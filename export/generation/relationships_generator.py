"""
Domain Linkages Generator
==========================

Generates relationships field using centralized DomainLinkagesService.

Replaces existing relationships (if present) with freshly generated
linkages from ExtractedLinkages.yaml, ensuring all entries have complete
Schema 5.0.0-compliant fields including 'slug'.

Part of Phase 2 Universal Exporter Architecture.
"""

from typing import Dict, Any
import logging
from export.generation.base import BaseGenerator
from shared.services.relationships_service import DomainLinkagesService

logger = logging.getLogger(__name__)


class DomainLinkagesGenerator(BaseGenerator):
    """
    Generate relationships from centralized associations.
    
    Workflow:
    1. Initialize DomainLinkagesService
    2. Extract item ID from frontmatter
    3. Call service.generate_linkages(item_id, domain)
    4. Replace frontmatter['relationships'] with generated linkages
    
    Ensures all linkage entries have:
    - id (shortened, no suffix)
    - slug (matches URL ending)
    - title
    - url
    - image
    - category/subcategory
    - frequency/severity/context
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize domain linkages generator.
        
        Args:
            config: Generator config with keys:
                - domain: Target domain ('materials', 'contaminants', 'compounds', 'settings')
                - output_field: Field name (default: 'relationships')
        """
        super().__init__(config)
        
        self.domain = config.get('domain')
        if not self.domain:
            raise ValueError("Missing required config key: 'domain'")
        
        self.output_field = config.get('output_field', 'relationships')
        
        # Initialize linkages service
        self.linkages_service = DomainLinkagesService()
        
        logger.debug(f"Initialized DomainLinkagesGenerator for {self.domain} domain")
    
    def generate(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate domain linkages from centralized associations.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with generated relationships field
        """
        # Extract item ID
        item_id = frontmatter.get('id')
        if not item_id:
            logger.warning(f"Frontmatter missing 'id' field, cannot generate linkages")
            return frontmatter
        
        # Generate linkages using centralized service
        try:
            linkages = self.linkages_service.generate_linkages(item_id, self.domain)
            
            if linkages:
                # MERGE with existing relationships instead of replacing
                # (Preserves technical fields moved by restructure enrichers)
                existing_relationships = frontmatter.get(self.output_field, {})
                merged_relationships = {**existing_relationships, **linkages}
                frontmatter[self.output_field] = merged_relationships
                
                # Count total linkage entries for logging
                total_entries = sum(len(v) if v else 0 for v in linkages.values())
                logger.debug(
                    f"Generated {total_entries} linkage entries for {item_id} "
                    f"({len(linkages)} linkage types)"
                )
            else:
                # No linkages found - preserve existing relationships if any
                if self.output_field not in frontmatter:
                    frontmatter[self.output_field] = {}
                logger.debug(f"No linkages found for {item_id}")
        
        except Exception as e:
            logger.error(f"Failed to generate linkages for {item_id}: {e}")
            # Set empty linkages on error to avoid breaking export
            frontmatter[self.output_field] = {}
        
        return frontmatter
