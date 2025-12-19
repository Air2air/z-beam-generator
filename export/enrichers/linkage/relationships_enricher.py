"""
Domain Linkages Enricher - Populate relationships field

Enricher that populates the relationships field using DomainLinkagesService.
This runs BEFORE the slug enricher so that slug can be added to the populated linkages.
"""

import logging
from typing import Any, Dict

from export.enrichers.base import BaseEnricher
from shared.services.relationships_service import DomainLinkagesService

logger = logging.getLogger(__name__)


class DomainLinkagesEnricher(BaseEnricher):
    """
    Populate relationships field from DomainLinkagesService.
    
    This enricher queries the centralized domain linkages service to get
    all related items (materials, contaminants, compounds, settings) for
    the current item.
    
    Must run BEFORE DomainLinkagesSlugEnricher so slug can be added.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize domain linkages enricher.
        
        Args:
            config: Configuration dict with 'domain' key (required)
        """
        super().__init__(config)
        
        # Domain is required
        if 'domain' not in config:
            raise ValueError("DomainLinkagesEnricher requires 'domain' in config")
        
        self.domain = config['domain']
        self.service = DomainLinkagesService()
        logger.info(f"Initialized DomainLinkagesEnricher for domain: {self.domain}")
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Populate relationships field.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with relationships populated
        """
        print(f"🔧 DomainLinkagesEnricher.enrich() called for {frontmatter.get('id', 'unknown')}")
        
        # Get item ID
        item_id = frontmatter.get('id')
        if not item_id:
            logger.warning("No 'id' field in frontmatter, skipping domain linkages enrichment")
            return frontmatter
        
        # Get linkages from service
        linkages = self.service.generate_linkages(item_id, self.domain)
        
        # Count entries
        total = sum(len(v) if isinstance(v, list) else 0 for v in linkages.values())
        print(f"   Populated {len(linkages)} linkage types, {total} total entries")
        
        # MERGE with existing relationships (preserve library relationships from source)
        existing_rels = frontmatter.get('relationships', {})
        if existing_rels:
            print(f"   ⚠️  Merging with {len(existing_rels)} existing relationship types: {list(existing_rels.keys())}")
            # Merge: linkages takes priority for overlapping keys, but existing preserved
            merged_rels = dict(existing_rels)
            merged_rels.update(linkages)
            frontmatter['relationships'] = merged_rels
        else:
            frontmatter['relationships'] = linkages
        
        logger.debug(f"Populated relationships for {item_id} in {self.domain}")
        
        return frontmatter
