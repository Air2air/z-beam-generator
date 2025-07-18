import logging
from ..utils.style_utils import format_section_prompt, get_standard_prompt_style

logger = logging.getLogger(__name__)

class SectionPromptBuilder:
    """Builds prompts for individual content sections."""
    
    @staticmethod
    def create_section_prompt(section, subject, section_data, words_per_section, randomize=False):
        """
        Create a prompt for a single content section with standardized formatting.
        
        Args:
            section: Dictionary with section info (id, title)
            subject: Main subject of the article
            section_data: Data/context for this section
            words_per_section: Target word count for the section
            randomize: Ignored (kept for backward compatibility)
        
        Returns:
            Formatted section prompt string
        """
        section_id = section.get("id", "")
        section_title = section.get("title", "")
        
        # Always use standard formatting (no randomization)
        return format_section_prompt(
            section_id=section_id,
            title=section_title,
            subject=subject,
            data=section_data,
            words=words_per_section
        )