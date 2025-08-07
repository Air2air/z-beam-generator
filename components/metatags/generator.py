"""
Metatags generator for Z-Beam Generator.

Generates Next.js compatible meta tags in YAML frontmatter format.
Enhanced with local formatting and validation.
Enhanced with dynamic SEO requirements from schema configurations.
"""

import logging
import yaml
from typing import Dict, Any
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
        """Process the generated metatags using centralized formatting and dynamic SEO requirements.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Validated and formatted metatags with dynamic requirements
            
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
            
            # Apply dynamic SEO requirements from schema
            parsed = self._apply_dynamic_seo_requirements(parsed)
            
            # Validate fields based on article type
            validate_article_specific_fields(self.article_type, getattr(self, 'category', None), parsed)
            
            # Apply centralized formatting - delegate ALL formatting to BaseComponent
            formatted_content = self.apply_centralized_formatting(content, parsed)
            
            with open("logs/metatags_yaml.log", "a") as f:
                f.write(f"Subject: {self.subject}\n")
                f.write(f"Formatted content:\n{formatted_content}\n")
                f.write("-" * 80 + "\n")
            
            
            # Add YAML frontmatter delimiters for consistency (following frontmatter pattern)
            if not formatted_content.startswith('---'):
                formatted_content = '---\n' + formatted_content
            if not formatted_content.endswith('---'):
                formatted_content = formatted_content.rstrip() + '\n---'
                
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

    def _apply_dynamic_seo_requirements(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Apply dynamic SEO requirements from schema for optimized metatag generation.
        
        Args:
            parsed: The parsed metatags data
            
        Returns:
            Dict: Enhanced metatags with dynamic SEO requirements applied
        """
        if not self.has_schema_feature('generatorConfig'):
            return parsed
            
        generator_config = self.get_schema_config('generatorConfig')
        
        # Check for SEO-specific requirements in schema
        if 'seoRequirements' in generator_config:
            seo_reqs = generator_config['seoRequirements']
            logger.info(f"Applied dynamic SEO requirements: {len(seo_reqs)} specifications")
        elif 'research' in generator_config:
            # Fallback to research fields for SEO content guidance
            research_config = generator_config['research']
            research_fields = research_config.get('fields', [])
            if research_fields:
                logger.info(f"Applied dynamic SEO guidance from {len(research_fields)} research fields")
        
        return parsed