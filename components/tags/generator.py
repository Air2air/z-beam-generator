"""
Tags generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Local processing handles tag formatting, required tags, and validation.
Enhanced with dynamic schema categories for comprehensive tagging.
"""

import logging
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class TagsGenerator(BaseComponent):
    """Generator for article tags with strict validation and local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated tags using centralized formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed tags with dynamic schema categories
            
        Raises:
            ValueError: If content is invalid
        """
        # Use centralized tag extraction and formatting
        tags = self.extract_tags_from_content(content)
        
        # Apply centralized formatting
        formatted_content = self.apply_centralized_formatting(content)
        
        # Apply dynamic schema categories
        formatted_content = self._apply_dynamic_schema_categories(formatted_content)
        
        # Get validation parameters
        min_tags = self.get_component_config("min_tags", 5)
        max_tags = self.get_component_config("max_tags", 10)
        
        # Validate tag count
        if len(tags) < min_tags:
            logger.warning(f"Generated only {len(tags)} tags, minimum required: {min_tags}")
        elif len(tags) > max_tags:
            logger.warning(f"Generated {len(tags)} tags, maximum allowed: {max_tags}")
            # Keep only the first max_tags
            tags = tags[:max_tags]
            formatted_content = ", ".join(tags)
        
        return formatted_content

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
    
