"""Style service for managing voice, tone and writing style."""

import importlib
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class StyleService:
    """Core service for managing writing styles and voice."""
    
    def __init__(self):
        """Initialize the style service."""
        self.styles_cache = {}
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    
    def get_style_for_country(self, country: str) -> Dict[str, Any]:
        """Get style characteristics for a specific country.
        
        Args:
            country: Country code or name (e.g., 'taiwan', 'usa')
            
        Returns:
            Dictionary with style characteristics
        """
        # Normalize country name to lowercase
        country_lower = country.lower()
        
        # Check cache first
        if country_lower in self.styles_cache:
            return self.styles_cache[country_lower]
        
        # Try to load country style
        try:
            # Import the country style module dynamically
            module_name = f"components.style.templates.{country_lower}_template"
            country_module = importlib.import_module(module_name)
            
            # Get style characteristics
            if hasattr(country_module, 'get_style_characteristics'):
                style = country_module.get_style_characteristics()
                self.styles_cache[country_lower] = style
                return style
            else:
                logger.warning(f"No style characteristics found for country: {country}")
        except (ImportError, AttributeError) as e:
            logger.warning(f"Failed to load style for country {country}: {str(e)}")
        
        # Fall back to US style if country not found
        if country_lower != "usa":
            return self.get_style_for_country("usa")
        
        # Default style if everything fails
        return {
            "writing_style": "clear and direct",
            "paragraph_structure": "logical progression",
            "terminology": "technical but accessible",
            "cultural_references": "international standards",
            "template": "usa"
        }
    
    def enhance_prompt_for_author(self, prompt: str, author: Dict[str, Any], params: Dict[str, Any]) -> str:
        """Enhance a prompt with author-specific style elements."""
        from components.style.prompt_enhancer import enhance_prompt
        
        # Get country from author
        country = author.get("country", "usa").lower()
        
        # Get word count from params with fallbacks
        if "max_word_count" not in params and "author_id" in params:
            # Try to get from content_word_count array if available
            author_id = params.get("author_id")
            word_counts = params.get("content_word_count", [400, 250, 500, 600])
            try:
                author_index = int(author_id) - 1
                if 0 <= author_index < len(word_counts):
                    params["max_word_count"] = word_counts[author_index]
            except (ValueError, TypeError, IndexError):
                pass
        
        # Enhance the prompt with style-specific elements
        return enhance_prompt(prompt, country, author, params)