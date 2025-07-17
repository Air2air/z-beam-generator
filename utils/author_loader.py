"""Author data loading utilities."""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("z-beam")

def load_author(author_id: str) -> Dict[str, Any]:
    """Load author data by ID."""
    authors_path = "author/authors.json"
    
    if not Path(authors_path).exists():
        logger.warning(f"Authors file not found: {authors_path}")
        return {"id": author_id, "name": f"Author {author_id}"}
    
    try:
        with open(authors_path, 'r') as f:
            authors = json.load(f)
        
        author_id_int = int(author_id)
        for author in authors:
            if author.get("id") == author_id_int:
                logger.info(f"Found author: {author.get('name', 'Unknown')}")
                return author
        
        logger.warning(f"Author with ID {author_id} not found")
        return {"id": author_id, "name": f"Author {author_id}"}
    except Exception as e:
        logger.error(f"Failed to load author data: {e}")
        return {"id": author_id, "name": f"Author {author_id}"}