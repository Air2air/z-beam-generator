"""
Caption generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class CaptionGenerator(BaseComponent):
    """Generator for image caption content with strict validation."""
    
    def generate(self) -> str:
        """Generate caption content with strict validation.
        
        Returns:
            str: The generated caption
            
        Raises:
            ValueError: If generation fails
        """
        # Strict validation - no fallbacks
        data = self._prepare_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for caption generation with strict validation.
        
        Returns:
            Dict[str, Any]: Validated data for generation
            
        Raises:
            ValueError: If required data is missing
        """
        data = super()._prepare_data()
        
        # Get component configuration
        component_config = self.get_component_config()
        
        # Validate required configuration
        required_config = ["results_word_count_max", "equipment_word_count_max"]
        for key in required_config:
            if key not in component_config:
                raise ValueError(f"Required config '{key}' missing for caption component")
        
        data.update({
            "results_word_count_max": component_config["results_word_count_max"],
            "equipment_word_count_max": component_config["equipment_word_count_max"]
        })
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated caption.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed caption
            
        Raises:
            ValueError: If content is invalid
        """
        if not content or not content.strip():
            raise ValueError("API returned empty or invalid caption")
        
        # Validate caption length
        word_count = len(content.strip().split())
        max_words = max(
            self.get_component_config("results_word_count_max"),
            self.get_component_config("equipment_word_count_max")
        )
        
        if word_count > max_words:
            raise ValueError(f"Caption too long: {word_count} words, maximum allowed: {max_words}")
        
        return content.strip()
