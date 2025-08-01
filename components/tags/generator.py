"""
Tags generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from components.base.enhanced_component import EnhancedBaseComponent

logger = logging.getLogger(__name__)

class TagsGenerator(EnhancedBaseComponent):
    """Generator for article tags with strict validation."""
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated tags.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed tags
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate and clean input
        content = self._validate_non_empty(content, "API returned empty or invalid tags")
        
        # Validate tag format and count
        lines = content.strip().split('\n')
        # Normalize input: handle comma-separated lists or line-by-line formats
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
        
        # Validate line count using the base method
        processed_tags = self._validate_line_count(
            processed_tags, 
            min_tags, 
            max_tags,
            "Generated"
        )
        
        # Format tags as comma-separated list
        return ', '.join(processed_tags) + '\n'