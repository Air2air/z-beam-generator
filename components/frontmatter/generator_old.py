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

import logging

from components.base.component import BaseComponent
from components.base.utils.validation import validate_category_consistency
from components.base.utils.slug_utils import SlugUtils
from components.base.utils.content_formatter import ContentFormatter
from components.base.image_handler import ImageHandler

logger = logging.getLogger(__name__)

class FrontmatterGenerator(BaseComponent):
    """Generator for article frontmatter with robust validation and auto-recovery."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/frontmatter/prompt.yaml"
    
    def _get_base_data(self) -> dict:
        """Get base data for the prompt template."""
        data = super()._get_base_data()
        
        # Add subject-name-with-hyphens to support the image URL formatting
        data['subject-name-with-hyphens'] = SlugUtils.create_subject_slug(self.subject)
        
        return data
    
    def _ensure_schema_structure(self, parsed: dict) -> dict:
        """Ensure the frontmatter follows the schema structure for the article type.
        
        Args:
            parsed: The parsed frontmatter data
            
        Returns:
            dict: The frontmatter with enforced schema structure
        """
        if not self.has_schema_feature('generatorConfig'):
            logger.warning(f"No generatorConfig found for article type: {self.article_type}")
            return parsed
            
        config = self.get_schema_config('generatorConfig')
        
        # Add required fields if missing
        if 'requiredFields' in config:
            for field in config['requiredFields']:
                if field not in parsed:
                    # Add default values for missing required fields
                    if field == 'name':
                        parsed[field] = self.subject
                    elif field == 'category':
                        parsed[field] = getattr(self, 'category', 'material')
                    elif field == 'author':
                        parsed[field] = self.author_data.get('author_name', 'Unknown')
        
        # Ensure proper schema structure
        if 'fieldMapping' in config:
            field_mapping = config['fieldMapping']
            for schema_field, content_field in field_mapping.items():
                if content_field in parsed:
                    # Move content to proper schema field if different
                    if schema_field != content_field:
                        parsed[schema_field] = parsed.pop(content_field)
        
        return parsed
    
    def _component_specific_processing(self, content: str) -> str:
        """Process frontmatter with centralized structured content processing."""
        return self._process_structured_content(content, output_format="yaml")
    
    def _extract_content_from_text(self, content: str) -> dict:
        """Extract structured data from any text format using utility.
        
        This method delegates to ContentFormatter for text extraction.
        
        Args:
            content: Raw text content from AI
            
        Returns:
            dict: Structured data extracted from text
        """
        return ContentFormatter.extract_structured_data_from_text(content, self.subject)

    def _extract_yaml_content(self, content: str) -> str:
        """Extract clean YAML content from various AI response formats.
        
        Args:
            content: Raw AI response content
            
        Returns:
            str: Clean YAML content
        """
        # First try to extract content between frontmatter markers
        yaml_content = ContentFormatter.extract_content_between_markers(content, '---')
        
        # If no markers found, use the general YAML extraction method
        if yaml_content == content:
            yaml_content = ContentFormatter.extract_yaml_content(content)
        
        # Make sure we don't have trailing --- markers that would create multiple YAML documents
        yaml_content = yaml_content.strip()
        if yaml_content.endswith('---'):
            yaml_content = yaml_content[:-3].strip()
        
        return yaml_content

    def _sanitize_content(self, content: str) -> str:
        """Remove malformed content and standardize image URLs using utility."""
        # First preprocess to remove problematic formatting
        content = ContentFormatter.preprocess_ai_content(content)
        # Then apply frontmatter-specific sanitization
        return ContentFormatter.sanitize_frontmatter_content(content)
    
    def validate_category_consistency(self, content: str) -> bool:
        """Validates category consistency in frontmatter.
        
        Args:
            content: Frontmatter content
            
        Returns:
            bool: True if consistent
        """
        category = getattr(self, 'category', None)
        if not category:
            return True
            
        return validate_category_consistency(content, category, self.article_type, self.subject)
    
    def _process_response(self, response_data):
        """Process the raw response data from the AI model."""
        # Let the base class process the response first
        data = super()._process_response(response_data)
        
        # Process image URLs in case they bypass component_specific_processing
        data = ImageHandler.process_image_data(data, self.subject)
        data = ImageHandler.add_missing_images(data, self.subject)
        
        return data
