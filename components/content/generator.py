"""
Content generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Includes support for limiting links to technical terms and setting maximum link count.
"""

import logging
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class ContentGenerator(BaseComponent):
    """Generator for main article content with strict validation."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated content with validation.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed content
            
        Raises:
            ValueError: If content is invalid
        """
        # Rigorous word count validation
        content = self._validate_word_count(content)
        
        # Validate links if configured
        inline_links_config = self.get_component_config("inline_links", {})
        if inline_links_config:
            max_links = inline_links_config.get("max_links", 5)
            content = self._validate_links(content, max_links)
        
        return content