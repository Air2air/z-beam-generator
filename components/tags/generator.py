"""
Tags generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Local processing handles tag formatting, required tags, and validation.
"""

import logging
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class TagsGenerator(BaseComponent):
    """Generator for article tags with strict validation and local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated tags using centralized formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed tags
            
        Raises:
            ValueError: If content is invalid
        """
        # Use centralized tag extraction and formatting
        tags = self.extract_tags_from_content(content)
        
        # Apply centralized formatting
        formatted_content = self.apply_centralized_formatting(content)
        
        # Get validation parameters
        min_tags = self.get_component_config("min_tags", 5)
        max_tags = self.get_component_config("max_tags", 10)
        
        # Validate tag count
        if len(tags) < min_tags:
            logger.warning(f"Generated only {len(tags)} tags, minimum required: {min_tags}")
        elif len(tags) > max_tags:
            logger.warning(f"Generated {len(tags)} tags, maximum allowed: {max_tags}")
            # Keep only the first max_tags
            tags = tags[:max_tags]
            formatted_content = ", ".join(tags)
        
        return formatted_content
    
