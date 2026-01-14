"""
Author Data Loader
Centralized loading of normalized author data
"""

from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

import yaml


class AuthorLoader:
    """Loads and caches author data from Authors.yaml"""
    
    def __init__(self, authors_file: str = "data/authors/Authors.yaml"):
        self.authors_file = Path(authors_file)
        self._authors_cache: Optional[Dict] = None
    
    @lru_cache(maxsize=1)
    def load_all_authors(self) -> Dict[int, Dict]:
        """Load all authors from Authors.yaml"""
        if not self.authors_file.exists():
            raise FileNotFoundError(
                f"Authors file not found: {self.authors_file}\n"
                "Run consolidation script to create normalized author data."
            )
        
        with open(self.authors_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return data['authors']
    
    def get_author_by_id(self, author_id: int) -> Dict:
        """
        Get full author object by ID
        
        Args:
            author_id: Author ID (1-4)
            
        Returns:
            Full author dictionary with all fields
            
        Raises:
            KeyError: If author_id not found
        """
        authors = self.load_all_authors()
        
        if author_id not in authors:
            raise KeyError(
                f"Author ID {author_id} not found. "
                f"Available IDs: {list(authors.keys())}"
            )
        
        return authors[author_id]
    
    def hydrate_author_reference(self, author_ref: any) -> Dict:
        """
        Convert author reference to full author object
        
        Handles both old format (full object) and new format (just ID)
        
        Args:
            author_ref: Either author_id (int) or full author dict
            
        Returns:
            Full author dictionary
        """
        # New format: just an ID
        if isinstance(author_ref, int):
            return self.get_author_by_id(author_ref)
        
        # Old format: full object with 'id' field
        if isinstance(author_ref, dict) and 'id' in author_ref:
            author_id = author_ref['id']
            return self.get_author_by_id(author_id)
        
        # Fallback: return as-is (for backwards compatibility)
        return author_ref


# Global instance for easy importing
_author_loader = AuthorLoader()

def load_all_authors() -> Dict[int, Dict]:
    """Convenience function: Load all authors"""
    return _author_loader.load_all_authors()

def get_author(author_id: int) -> Dict:
    """Convenience function: Get author by ID"""
    return _author_loader.get_author_by_id(author_id)

def hydrate_author(author_ref: any) -> Dict:
    """Convenience function: Hydrate author reference to full object"""
    return _author_loader.hydrate_author_reference(author_ref)
