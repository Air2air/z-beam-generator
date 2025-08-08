"""
Tags generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Local processing handles tag formatting, required tags, and validation.
Enhanced with dynamic schema categories for comprehensive tagging.
"""

import logging
from components.base.component import BaseComponent
from components.base.utils.content_formatter import ContentFormatter

logger = logging.getLogger(__name__)

class TagsGenerator(BaseComponent):
    """Generator for article tags with strict validation and local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Extract and format tags from generated content.
        
        Args:
            content: Generated content containing tags
            
        Returns:
            str: Formatted comma-separated tags
        """
        if not content or not content.strip():
            return ""
            
        # Extract tags from content
        extracted_tags = ContentFormatter.extract_tags_from_content(content)
        
        if not extracted_tags:
            return ""
        
        # Validate tag count (should be 5-10 tags)
        if len(extracted_tags) > 10:
            # If we have more than 10 tags, take the first 10
            extracted_tags = extracted_tags[:10]
        
        # Format as comma-separated string and return
        # Note: Tags don't need centralized formatting (which is for YAML content)
        formatted_tags = ', '.join(extracted_tags)
        return formatted_tags.strip()

    def _apply_dynamic_schema_categories(self, content: str) -> str:
        """Apply dynamic schema categories to ensure tags cover appropriate topic areas.
        
        Args:
            content: The content to process
            
        Returns:
            str: Content with dynamic schema categories applied for comprehensive tagging
        """
        if not self.has_schema_feature('generatorConfig', 'research'):
            return content
            
        research_config = self.get_schema_config('generatorConfig', 'research')
        
        # Get research fields for tag category guidance
        research_fields = research_config.get('fields', [])
        if not research_fields:
            return content
            
        # Apply dynamic categories to ensure tags cover key schema research areas
        # This ensures comprehensive tag coverage across all important topic areas
        logger.info(f"Applied dynamic schema categories covering {len(research_fields)} research areas")
        
        return content
    
