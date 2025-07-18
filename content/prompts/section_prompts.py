import logging
from typing import Dict, Any

from ..randomizers.style_randomizer import StyleRandomizer

logger = logging.getLogger(__name__)

class SectionPromptBuilder:
    """Builds dynamic, randomized prompts for content sections with variable lengths."""
    
    @staticmethod
    def create_section_prompt(section: Dict[str, Any], subject: str, section_data: str, 
                            words_per_section: int, randomize: bool = True) -> str:
        """
        Create a prompt for a section with randomization including length variation.
        
        Args:
            section: Section metadata dictionary
            subject: The subject to write about
            section_data: Formatted data for this section
            words_per_section: Base target word count before randomization
            randomize: Whether to randomize prompt elements
            
        Returns:
            Formatted prompt for this section
        """
        section_id = section["id"]
        section_title = section["title"]
        
        # Base prompt structure
        prompt = f"## {section_title}\n\n"
        
        # Randomize the section length if randomization is enabled
        if randomize:
            # Apply significant randomization to section length
            actual_words = StyleRandomizer.randomize_word_count(words_per_section)
            
            # Record the actual length target in the section data for debugging
            section["target_length"] = actual_words
        else:
            actual_words = words_per_section
        
        # Add randomized style if requested
        if randomize:
            style = StyleRandomizer.get_style()
            prompt += f"Using a {style} style, "
            
            # Randomly determine if this section should be emphasized (lengthier/more detailed)
            if StyleRandomizer.should_emphasize_section():
                prompt += f"{StyleRandomizer.get_emphasis_instruction()} "
            
        # Get intro phrase (randomized if requested)
        if randomize:
            intro_phrase = StyleRandomizer.get_intro_phrase(section_id, subject)
        else:
            intro_phrase = f"Write about {subject} based on this information"
            
        prompt += f"{intro_phrase}:\n{section_data}\n\n"
        
        # Get conclusion guidance (randomized if requested)
        if randomize:
            conclusion = StyleRandomizer.get_conclusion_phrase(section_id)
        else:
            conclusion = "Provide comprehensive details and explain their significance."
            
        prompt += conclusion
        
        # Add word count guidance with highly variable targets
        if randomize:
            prompt += f"\n\n{StyleRandomizer.get_section_length_description(actual_words)}"
        else:
            prompt += f"\n\nWrite approximately {actual_words} words for this section."
        
        return prompt