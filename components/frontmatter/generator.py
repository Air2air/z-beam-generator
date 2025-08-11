"""
Frontmatter generator for Z-Beam Generator.

Simplified implementation using base class utilities for all formatting.
"""

import logging
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class FrontmatterGenerator(BaseComponent):
    """Generator for article frontmatter using base class utilities for all formatting."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/frontmatter/prompt.yaml"
