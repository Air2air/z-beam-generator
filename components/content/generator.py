"""
Content generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from components.base.enhanced_component import EnhancedBaseComponent

logger = logging.getLogger(__name__)

class ContentGenerator(EnhancedBaseComponent):
    """Generator for main article content with strict validation."""
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated content.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed content
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate and clean input
        content = self._validate_non_empty(content, "API returned empty or invalid content")
        
        # Strip any markdown code blocks that might have been added
        clean_content = self._strip_markdown_code_blocks(content)
        
        # Rigorous word count validation
        word_count = len(clean_content.split())
        min_words = self.get_component_config("min_words")
        max_words = self.get_component_config("max_words")
        
        if word_count < min_words:
            raise ValueError(f"Generated content too short: {word_count} words, minimum required: {min_words}")
        
        if word_count > max_words:
            raise ValueError(f"Generated content too long: {word_count} words, maximum allowed: {max_words}")
        
        return clean_content