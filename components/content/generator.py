"""
Content generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from typing import Dict, Any
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
        # Strict validation - no fallbacks
        data = self._prepare_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for content generation with strict validation.
        
        Returns:
            Dict[str, Any]: Validated data for generation
            
        Raises:
            ValueError: If required data is missing
        """
        data = super()._prepare_data()
        
        # Get component configuration
        component_config = self.get_component_config()
        
        # Validate required configuration
        required_config = ["min_words", "max_words"]
        for key in required_config:
            if key not in component_config:
                raise ValueError(f"Required config '{key}' missing for content component")
        
        data.update({
            "min_words": component_config["min_words"],
            "max_words": component_config["max_words"]
        })
        
        return data
    
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
        
        # Basic validation - ensure minimum content length
        word_count = len(content.split())
        min_words = self.get_component_config("min_words")
        
        if word_count < min_words:
            raise ValueError(f"Generated content too short: {word_count} words, minimum required: {min_words}")
        
        return content.strip()