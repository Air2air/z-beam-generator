"""Author utilities for managing article authors."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_author_by_id(author_id: str) -> Optional[Dict[str, Any]]:
    """Get author information by ID."""
    try:
        authors_file = Path("authors/authors.json")
        
        if not authors_file.exists():
            logger.warning("Authors file not found")
            return None
        
        with open(authors_file, 'r') as f:
            authors_data = json.load(f)
        
        author = authors_data.get(author_id)
        
        if author:
            logger.info(f"Author {author_id} found: {author.get('name', 'Unknown')}")
        else:
            logger.warning(f"Author {author_id} not found")
        
        return author
        
    except Exception as e:
        logger.error(f"Error loading author {author_id}: {e}")
        return None

def list_authors() -> Dict[str, Any]:
    """List all available authors."""
    try:
        authors_file = Path("authors/authors.json")
        
        if not authors_file.exists():
            return {}
        
        with open(authors_file, 'r') as f:
            return json.load(f)
            
    except Exception as e:
        logger.error(f"Error loading authors: {e}")
        return {}