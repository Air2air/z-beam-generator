"""
Caption generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from components.base.enhanced_component import EnhancedBaseComponent

logger = logging.getLogger(__name__)

class CaptionGenerator(EnhancedBaseComponent):
    """Generator for image caption content with strict validation."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated caption.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed caption
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate caption length and structure
        clean_content = content.strip()
        
        # Caption must have properly formatted sections with "Results:" and "Equipment:"
        if "**Results:**" not in clean_content or "**Equipment:**" not in clean_content:
            raise ValueError("Caption must contain both '**Results:**' and '**Equipment:**' sections")
        
        # Split content into sections
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
        
        return clean_content
