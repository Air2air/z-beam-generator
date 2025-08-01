"""
Content generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class ContentGenerator(BaseComponent):
    """Generator for main article content with strict validation."""
    
    def generate(self) -> str:
        """Generate main article content with strict validation.
        
        Returns:
            str: The generated content
            
        Raises:
            ValueError: If generation fails
        """
        # Use base class schema-driven data preparation
        data = self.get_template_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated content.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed content
            
        Raises:
            ValueError: If content is invalid
        """
        if not content or not content.strip():
            raise ValueError("API returned empty or invalid content")
        
        # Strip any markdown code blocks that might have been added
        clean_content = content.strip()
        
        # Rigorous word count validation
        word_count = len(clean_content.split())
        min_words = self.get_component_config("min_words")
        max_words = self.get_component_config("max_words")
        
        if word_count < min_words:
            raise ValueError(f"Generated content too short: {word_count} words, minimum required: {min_words}")
        
        if word_count > max_words:
            raise ValueError(f"Generated content too long: {word_count} words, maximum allowed: {max_words}")
        
        return clean_content