"""
Metatags generator for Z-Beam Generator.

Generates Next.js compatible meta tags in YAML frontmatter format.
Enhanced with local formatting and validation.
Enhanced with dynamic SEO requirements from schema configurations.
"""

import logging
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class MetatagsGenerator(BaseComponent):
    """Generator for Next.js compatible meta tags in YAML frontmatter format with enhanced local processing."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/metatags/prompt.yaml"
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated metatags using centralized processing with custom logging.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Validated and formatted metatags with dynamic requirements
            
        Raises:
            ValueError: If content is invalid
        """
        try:
            # Use centralized structured content processing
            formatted_content = self._process_structured_content(content, output_format="yaml")
            
            # Log the processed content for debugging
            with open("logs/metatags_yaml.log", "a") as f:
                f.write(f"Subject: {self.subject}\n")
                f.write(f"Formatted content:\n{formatted_content}\n")
                f.write("-" * 80 + "\n")
                
            return formatted_content
            
        except Exception as e:
            # Log the error
            logger.error(f"Error processing metatags: {e}")
            with open("logs/metatags_error.log", "a") as f:
                f.write(f"Subject: {self.subject}\n")
                f.write(f"Error: {e}\n")
                f.write(f"Content causing error:\n{content}\n")
                f.write("---\n")
            raise