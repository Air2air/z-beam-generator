"""Integration between author system and content components."""

import logging
from typing import Dict, Any, Optional

from components.style.style_service import StyleService

logger = logging.getLogger(__name__)

class AuthorComponentIntegration:
    """Handles integration between the author system and content components."""
    
    @staticmethod
    def enhance_prompt_with_author_style(prompt: str, author: Dict[str, Any], params: Dict[str, Any] = None) -> str:
        """Enhance a component prompt with author-specific styling.
        
        Args:
            prompt: Original prompt
            author: Author data
            params: Additional parameters
            
        Returns:
            Enhanced prompt
        """
        if not params:
            params = {}
            
        try:
            # Use the new StyleService to enhance the prompt
            style_service = StyleService()
            enhanced_prompt = style_service.enhance_prompt_for_author(prompt, author, params)
            return enhanced_prompt
        except Exception as e:
            logger.error(f"Error enhancing prompt with author style: {e}")
            return prompt  # Return the original prompt if enhancement fails
    
    @staticmethod
    def get_author_specific_params(author: Dict[str, Any], component_type: str) -> Dict[str, Any]:
        """Get author-specific parameters for a component.
        
        Args:
            author: Author data
            component_type: Component type
            
        Returns:
            Author-specific parameters
        """
        # This will be handled by the LayoutService instead
        return {}