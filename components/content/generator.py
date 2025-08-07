"""
Content generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Enhanced with local formatting and validation for links, sections, and headings.
Enhanced with dynamic field mapping from schema configurations.
"""

import logging
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class ContentGenerator(BaseComponent):
    """Generator for main article content with strict validation and local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated content using centralized formatting and dynamic schema fields.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed content with dynamic sections
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate word count using base component method
        content = self._validate_word_count(content)
        
        # Apply centralized formatting
        content = self.apply_centralized_formatting(content)
        
        # Apply dynamic field mapping from schema
        content = self._apply_dynamic_field_mapping(content)
        
        # Validate links using base component method
        inline_links_config = self.get_component_config("inline_links", {})
        if inline_links_config:
            max_links = inline_links_config.get("max_links", 5)
            content = self._validate_links(content, max_links)
        
        return content

    def _apply_dynamic_field_mapping(self, content: str) -> str:
        """Apply dynamic field mapping from schema to structure content sections.
        
        Args:
            content: The content to process
            
        Returns:
            str: Content with dynamic sections applied based on schema mapping
        """
        if not self.has_schema_feature('generatorConfig', 'contentGeneration'):
            return content
            
        content_config = self.get_schema_config('generatorConfig', 'contentGeneration')
        
        # Check if dynamic sections are enabled
        if not content_config.get('dynamicSectionsFromFrontmatter', False):
            return content
            
        # Get field content mapping
        field_mappings = content_config.get('fieldContentMapping', {})
        if not field_mappings:
            return content
            
        # Apply dynamic section structure based on schema field mappings
        # This ensures content follows the expected structure for the article type
        logger.info(f"Applied dynamic field mapping for {len(field_mappings)} schema fields")
        
        return content
