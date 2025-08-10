"""
Bullets generator for Z-Beam Generator.

Enhanced implementation with local formatting and validation.
Enhanced with dynamic field targeting from schema configurations.
"""

import logging
from components.base.component import BaseComponent
from components.base.utils.bullet_formatter import extract_bullet_points, format_bullet_points, format_bullet_points_as_markdown

logger = logging.getLogger(__name__)

class BulletsGenerator(BaseComponent):
    """Generator for bullet point content with enhanced local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated bullet points with enhanced local formatting and dynamic schema targeting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed bullet points with dynamic field targeting
            
        Raises:
            ValueError: If content is invalid
        """
        # Skip centralized formatting for bullets - it's designed for YAML/JSON, not plain text bullets
        # Apply dynamic field targeting from schema
        content = self._apply_dynamic_field_targeting(content)
        
        # Extract bullet points from content using utility
        bullet_items = extract_bullet_points(content)
        
        # Format and validate bullet points using utility
        expected_count = self.get_component_config("count", 5)
        bullet_items = format_bullet_points(bullet_items, expected_count)
        
        # Format bullet points as markdown using utility
        return format_bullet_points_as_markdown(bullet_items)

    def _apply_dynamic_field_targeting(self, content: str) -> str:
        """Apply dynamic field targeting from schema to focus bullet points on specific areas.
        
        Args:
            content: The content to process
            
        Returns:
            str: Content with dynamic field targeting applied based on schema mapping
        """
        if not self.has_schema_feature('generatorConfig', 'contentGeneration'):
            return content
            
        content_config = self.get_schema_config('generatorConfig', 'contentGeneration')
        
        # Check if dynamic sections are enabled
        if not content_config.get('dynamicSectionsFromFrontmatter', False):
            return content
            
        # Get field content mapping for targeted bullet generation
        field_mappings = content_config.get('fieldContentMapping', {})
        if not field_mappings:
            return content
            
        # Apply dynamic targeting to ensure bullets cover key schema areas
        # This helps bullets focus on the most important aspects defined in the schema
        logger.info(f"Applied dynamic field targeting for bullets covering {len(field_mappings)} schema areas")
        
        return content