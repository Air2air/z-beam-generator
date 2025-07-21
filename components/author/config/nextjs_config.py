"""Next.js configuration hints for different authors."""

from typing import Dict, Any, Optional
from ..author_service import AuthorService
from .country_styles import get_country_style

# Initialize author service
author_service = AuthorService()

def get_nextjs_config(author_id: int) -> Dict[str, Any]:
    """Get Next.js configuration for an author based on their country."""
    # Get author data
    author = author_service.get_author_by_id(author_id)
    if not author:
        # Default config if author not found
        return {
            "template": "usa",
            "contentColumns": 1,
            "tableOfContents": True
        }
    
    # Get country from author data
    country = author.get("country", "usa").lower()
    
    # Get country style
    country_style = get_country_style(country)
    
    # Base configs for different author types
    BASE_CONFIGS = {
        # Scientific authors (Evelyn)
        1: {
            "contentColumns": 1,
            "tableOfContents": True,
            "authorBox": {
                "position": "top",
                "showCredentials": True
            },
            "citations": True
        },
        
        # Practical authors (Mario)
        2: {
            "contentColumns": 2,
            "tableOfContents": False,
            "authorBox": {
                "position": "bottom",
                "showSpecialties": True
            },
            "applicationExamples": True
        },
        
        # Industry authors (Todd, Ikmanda)
        3: {
            "contentColumns": 1,
            "tableOfContents": True,
            "authorBox": {
                "position": "sidebar",
                "showSpecialties": True
            },
            "industryStandards": True
        }
    }
    
    # Get base config for author type (defaulting to type 3 if not found)
    author_type_id = author.get("id", 3)
    base_config = BASE_CONFIGS.get(author_type_id, BASE_CONFIGS[3])
    
    # Combine with country-specific template
    config = {
        "template": country_style["template"],
        **base_config
    }
    
    return config