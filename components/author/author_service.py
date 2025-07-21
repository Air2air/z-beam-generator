"""Service for managing author data."""

import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AuthorService:
    """Core service for author data."""
    
    def __init__(self):
        """Initialize the author service."""
        self.authors_file = os.path.join(os.path.dirname(__file__), "authors.json")
    
    def get_authors(self) -> List[Dict[str, Any]]:
        """Get all authors."""
        # Reload data each time for fresh loading
        return self._load_authors()
    
    def get_author_by_id(self, author_id: int) -> Optional[Dict[str, Any]]:
        """Get author by ID."""
        authors = self._load_authors()
        for author in authors:
            if author.get("id") == author_id:
                return author
        logger.warning(f"Author with ID {author_id} not found")
        return None
    
    def get_author_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get author by slug."""
        authors = self._load_authors()
        for author in authors:
            if author.get("slug") == slug:
                return author
        logger.warning(f"Author with slug '{slug}' not found")
        return None
    
    def _load_authors(self) -> List[Dict[str, Any]]:
        """Load authors from JSON file."""
        try:
            with open(self.authors_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load authors: {str(e)}")
            return []