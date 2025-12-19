"""
Author Enricher - Expand author field with full profile data

Enricher that expands minimal author data (just ID) with full author profile
from Authors.yaml including name, country, credentials, expertise, etc.

This ensures frontmatter has rich author data for:
- Schema.org Person markup
- SEO author attribution  
- Display in UI components
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class AuthorEnricher(BaseEnricher):
    """
    Expand author field with full profile from Authors.yaml.
    
    Transforms:
        author:
          id: 1
    
    Into:
        author:
          id: 1
          name: Yi-Chun Lin
          country: Taiwan
          title: Ph.D.
          jobTitle: Senior Materials Research Scientist
          expertise: [...]
          credentials: [...]
          ... (all fields from Authors.yaml)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize author enricher.
        
        Args:
            config: Configuration dict (no specific keys required)
        """
        super().__init__(config)
        
        # Path to Authors.yaml
        self.authors_file = Path('data/authors/Authors.yaml')
        
        # Lazy-loaded authors data
        self._authors_data: Optional[Dict] = None
    
    def _load_authors(self) -> Dict:
        """Load authors data from Authors.yaml"""
        if self._authors_data is None:
            if not self.authors_file.exists():
                raise FileNotFoundError(f"Authors file not found: {self.authors_file}")
            
            with open(self.authors_file, 'r', encoding='utf-8') as f:
                self._authors_data = yaml.safe_load(f)
            
            logger.info(f"Loaded {len(self._authors_data.get('authors', {}))} authors from {self.authors_file}")
        
        return self._authors_data
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expand author field with full profile data.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with expanded author field
        """
        # Check if author field exists
        if 'author' not in frontmatter:
            logger.debug("No author field in frontmatter")
            return frontmatter
        
        author = frontmatter['author']
        
        # Check if author is already expanded (has more than just id)
        if not isinstance(author, dict):
            logger.warning(f"Author field is not a dict: {type(author)}")
            return frontmatter
        
        author_id = author.get('id')
        if not author_id:
            logger.warning("Author dict has no 'id' field")
            return frontmatter
        
        # Check if author is fully expanded (has key fields beyond basic info)
        # Basic fields: id, name, country, country_display, title
        # Complete fields should include: credentials, email, image, url
        required_complete_fields = ['credentials', 'email', 'image', 'url']
        if all(field in author for field in required_complete_fields):
            logger.debug(f"Author {author_id} already fully expanded")
            return frontmatter
        
        # Load authors data
        authors_data = self._load_authors()
        authors = authors_data.get('authors', {})
        
        # Get full author profile (Authors.yaml uses integer keys)
        author_profile = authors.get(author_id)  # Use integer ID directly
        if not author_profile:
            logger.warning(f"Author ID {author_id} not found in Authors.yaml")
            return frontmatter
        
        # Expand author with all fields from profile
        # Preserve any existing fields (like id)
        expanded_author = dict(author)  # Start with existing fields
        expanded_author.update(author_profile)  # Add all profile fields
        
        frontmatter['author'] = expanded_author
        
        logger.debug(f"Expanded author {author_id} ({author_profile.get('name')})")
        
        return frontmatter
