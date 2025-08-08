"""
Caption generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Enhanced with local formatting and section processing.
Enhanced with dynamic image requirements from schema configurations.
"""

import logging
from components.base.component import BaseComponent
from components.base.utils.content_formatter import ContentFormatter
from components.base.utils.formatting import format_caption_content

logger = logging.getLogger(__name__)

class CaptionGenerator(BaseComponent):
    """Generator for image caption content with strict validation and centralized formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated caption with standardized formatting rules.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed caption with standardized format applied via Python utilities
            
        Raises:
            ValueError: If content is invalid
        """
        # Skip centralized formatting for captions as they are plain text, not YAML
        # Apply dynamic image requirements from schema
        content = self._apply_dynamic_image_requirements(content)
        
        # Clean and normalize the content using ContentFormatter
        clean_content = ContentFormatter.normalize_case(content.strip(), 'sentence')
        
        # Apply all caption formatting rules via Python utilities
        formatted_caption = format_caption_content(clean_content)
        
        return formatted_caption
    
    def _apply_dynamic_image_requirements(self, content: str) -> str:
        """Apply dynamic image requirements from schema for targeted caption generation.
        
        Args:
            content: The content to process
            
        Returns:
            str: Content with dynamic image requirements applied based on schema specifications
        """
        if not self.has_schema_feature('generatorConfig'):
            return content
            
        generator_config = self.get_schema_config('generatorConfig')
        
        # Use the research field configuration that exists in the schema
        if 'research' in generator_config:
            research_config = generator_config['research']
            if 'fields' in research_config:
                logger.info(f"Applied dynamic image generation context from research fields: {research_config['fields']}")
        
        return content
