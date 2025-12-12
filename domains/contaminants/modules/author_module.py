"""
AuthorModule - Enrich author data from registry for contaminants

Handles: Author data enrichment from author registry

Architecture:
- Contaminants.yaml only has author.id
- Full author data retrieved from data.authors.registry
- Fail-fast on invalid author ID
"""

import logging
from typing import Dict, Optional


class AuthorModule:
    """Enrich author data for contaminant frontmatter"""
    
    def __init__(self):
        """Initialize author module"""
        self.logger = logging.getLogger(__name__)
    
    def generate(self, contaminant_data: Dict) -> Optional[Dict]:
        """
        Enrich author data from registry
        
        Args:
            contaminant_data: Contaminant data from Contaminants.yaml
            
        Returns:
            Full author dictionary from registry or None if not present
            
        Raises:
            KeyError: If author ID is invalid
        """
        self.logger.info("Enriching author data from registry")
        
        # Extract author field
        author_field = contaminant_data.get('author')
        
        if not author_field:
            self.logger.warning("No author field in contaminant data")
            return None
        
        # Get author ID (handle both dict and direct ID)
        if isinstance(author_field, dict):
            author_id = author_field.get('id')
        else:
            author_id = author_field
        
        if not author_id:
            self.logger.warning("No author ID found")
            return None
        
        # Get full author data from registry
        from data.authors.registry import get_author
        
        try:
            author_data = get_author(author_id)
            self.logger.info(
                f"✅ Enriched author: {author_data.get('name')} (ID: {author_id})"
            )
            return author_data.copy()
        except KeyError:
            self.logger.error(f"❌ Invalid author ID {author_id}")
            raise
