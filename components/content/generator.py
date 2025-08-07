"""
Content generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Enhanced with local formatting and validation for links, sections, and headings.
"""

import logging
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class ContentGenerator(BaseComponent):
    """Generator for main article content with strict validation and local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated content using centralized formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed content
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate word count using base component method
        content = self._validate_word_count(content)
        
        # Apply centralized formatting
        content = self.apply_centralized_formatting(content)
        
                # Validate links using base component method
        inline_links_config = self.get_component_config("inline_links", {})
        if inline_links_config:
            max_links = inline_links_config.get("max_links", 5)
            content = self._validate_links(content, max_links)
        
        return content
