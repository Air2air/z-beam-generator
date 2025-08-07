"""
Metatags generator for Z-Beam Generator.

Generates Next.js compatible meta tags in YAML frontmatter format.
Enhanced with local formatting and validation.
"""

import logging
import yaml
from components.base.component import BaseComponent
from components.metatags.validation import validate_article_specific_fields

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
        """Process the generated metatags using centralized formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Validated and formatted metatags
            
        Raises:
            ValueError: If content is invalid
        """
        try:
            # Use centralized base component method
            yaml_content = self.extract_yaml_content(content)
                
            # Parse the YAML content
            parsed = yaml.safe_load(yaml_content)
            if not isinstance(parsed, dict):
                raise ValueError("Metatags must be a valid YAML dictionary")
            
            # Validate fields based on article type
            validate_article_specific_fields(self.article_type, getattr(self, 'category', None), parsed)
            
            # Apply centralized formatting - delegate ALL formatting to BaseComponent
            formatted_content = self.apply_centralized_formatting(content, parsed)
            
            with open("logs/metatags_yaml.log", "a") as f:
                f.write(f"Subject: {self.subject}\n")
                f.write(f"Formatted content:\n{formatted_content}\n")
                f.write("-" * 80 + "\n")
                
            return f"---\n{formatted_content}---"
            
        except Exception as e:
            # Log the error
            logger.error(f"Error processing metatags: {e}")
            with open("logs/metatags_error.log", "a") as f:
                f.write(f"Subject: {self.subject}\n")
                f.write(f"Error: {e}\n")
                f.write(f"Content causing error:\n{content}\n")
                f.write("-" * 80 + "\n")
            raise ValueError(f"Metatags generation failed: {e}")
