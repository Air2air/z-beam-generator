"""Content integration for author system."""

from typing import Dict, Any

from ..styles.country_style import format_country_specific_prompt
from ..author_service import AuthorService

# Initialize author service
author_service = AuthorService()

def format_content_prompt(subject: str, author_id: int, params: Dict[str, Any] = None) -> str:
    """Format content prompt for an author with country-specific style."""
    params = params or {}
    
    # Get author data
    author = author_service.get_author_by_id(author_id)
    if not author:
        # Default prompt if author not found
        word_count = params.get("word_count", 400)
        paragraph_count = params.get("paragraphs", 3)
        return f"Write a technical article about {subject}. The article should be approximately {word_count} words, divided into {paragraph_count} paragraphs."
    
    # Format country-specific prompt
    return format_country_specific_prompt(subject, author, params)

def enhance_content(content: str, author_id: int, params: Dict[str, Any] = None) -> str:
    """Enhance content based on author style."""
    # For now, just return the content
    # In the future, this could apply country-specific formatting
    return content