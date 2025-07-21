"""Frontmatter integration for author system."""

from typing import Dict, Any

from ..author_service import AuthorService
from ..config.nextjs_config import get_nextjs_config
from ..config.country_styles import get_country_style

def enhance_frontmatter(frontmatter: Dict[str, Any], author_id: int) -> Dict[str, Any]:
    """Enhance frontmatter with author information."""
    # Get author service
    author_service = AuthorService()
    
    # Get author data
    author = author_service.get_author_by_id(author_id)
    if author:
        # Add author to frontmatter
        frontmatter["author"] = author
        
        # Get country style
        country = author.get("country", "usa").lower()
        country_style = get_country_style(country)
        
        # Add Next.js layout configuration
        nextjs_config = get_nextjs_config(author_id)
        if nextjs_config:
            frontmatter["layout"] = nextjs_config
            
        # Add country style information
        frontmatter["countryStyle"] = {
            "country": country,
            "writingStyle": country_style["writing_style"],
            "template": country_style["template"]
        }
    
    return frontmatter