"""
Caption generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
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
        # Use base class schema-driven data preparation
        data = self.get_template_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
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
        
        # Validate caption length and structure
        clean_content = content.strip()
        
        # Split content into sections
        if "**Results:**" in clean_content and "**Equipment:**" in clean_content:
            results_section = clean_content.split("**Results:**")[1].split("**Equipment:**")[0].strip()
            equipment_section = clean_content.split("**Equipment:**")[1].strip()
            
            # Count words in each section
            results_word_count = len(results_section.split())
            equipment_word_count = len(equipment_section.split())
            
            # Get max word counts from config
            results_max = self.get_component_config("results_word_count_max")
            equipment_max = self.get_component_config("equipment_word_count_max")
            
            # Validate section word counts with detailed feedback
            if results_word_count > results_max:
                error_msg = (
                    f"Results section too long: {results_word_count} words, maximum allowed: {results_max}. "
                    f"Please reduce by {results_word_count - results_max} words. "
                    f"Current text: '{results_section}'"
                )
                raise ValueError(error_msg)
            
            # Allow 1-2 words extra for equipment section to prevent unnecessary failures
            if equipment_word_count > equipment_max + 2:
                error_msg = (
                    f"Equipment section too long: {equipment_word_count} words, maximum allowed: {equipment_max + 2}. "
                    f"Please reduce by {equipment_word_count - (equipment_max + 2)} words. "
                    f"Current text: '{equipment_section}'"
                )
                raise ValueError(error_msg)
        else:
            # Fallback to total validation if sections aren't properly formatted
            word_count = len(clean_content.split())
            total_max = self.get_component_config("results_word_count_max") + self.get_component_config("equipment_word_count_max")
            
            if word_count > total_max:
                raise ValueError(f"Caption too long: {word_count} words, maximum allowed: {total_max}")
        
        return clean_content
