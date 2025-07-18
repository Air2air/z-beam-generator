import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Loads configuration files for content generation."""
    
    @staticmethod
    def load_prompt_template() -> str:
        """Load the main content prompt template."""
        # Simple default template
        return """Write an article about {subject} for a {article_type} article.
Use {min_words} to {max_words} words divided into approximately {paragraphs} paragraphs.
Use these sections: {sections}

{section_prompts}

Use this context information:
{frontmatter_context}
"""
    
    @staticmethod
    def load_section_prompts() -> Dict[str, str]:
        """Load section-specific prompts."""
        # Default section prompts
        return {
            "overview": "Write an overview about {subject}",
            "applications": "Describe the applications of {subject}",
            "technicalSpecifications": "Provide technical specifications for {subject}",
            "challenges": "Discuss challenges related to {subject}",
            "benefits": "Explain the benefits of {subject}"
        }