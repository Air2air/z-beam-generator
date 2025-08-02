"""
Tags generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from components.base.enhanced_component import EnhancedBaseComponent

logger = logging.getLogger(__name__)

class TagsGenerator(EnhancedBaseComponent):
    """Generator for article tags with strict validation."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated tags.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed tags
            
        Raises:
            ValueError: If content is invalid
        """
        # Normalize input: handle comma-separated lists or line-by-line formats
        lines = content.strip().split('\n')
        tag_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Handle comma-separated tags on one line
            if ',' in line:
                tag_lines.extend([tag.strip() for tag in line.split(',') if tag.strip()])
            else:
                tag_lines.append(line)
        
        # Convert tags to standardized format
        processed_tags = [tag.strip() for tag in tag_lines if tag.strip()]
        
        min_tags = self.get_component_config("min_tags")
        max_tags = self.get_component_config("max_tags")
        
        # Validate line count using the utility function
        processed_tags = self._validate_line_count(
            processed_tags, 
            min_tags, 
            max_tags,
            "Generated tags"
        )
        
        # Format tags as comma-separated list
        return ', '.join(processed_tags) + '\n'