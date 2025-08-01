"""
Tags generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class TagsGenerator(BaseComponent):
    """Generator for article tags with strict validation."""
    
    def generate(self) -> str:
        """Generate tags content with strict validation.
        
        Returns:
            str: The generated tags
            
        Raises:
            ValueError: If generation fails
        """
        # Use base class schema-driven data preparation
        data = self.get_template_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated tags.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed tags
            
        Raises:
            ValueError: If content is invalid
        """
        if not content or not content.strip():
            raise ValueError("API returned empty or invalid tags")
        
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
        
        if len(processed_tags) < min_tags:
            raise ValueError(f"Generated {len(processed_tags)} tags, minimum required: {min_tags}")
        
        if len(processed_tags) > max_tags:
            # Truncate to max_tags
            processed_tags = processed_tags[:max_tags]
        
        # Format tags as metatags for HTML head
        formatted_output = "<!-- Metatags for HTML head -->\n"
        formatted_output += '<meta name="keywords" content="' + ', '.join(processed_tags) + '">\n\n'
        
        # Add tags in user-friendly format
        formatted_output += "<!-- Tags for display -->\n"
        formatted_output += ', '.join(processed_tags) + '\n'
        
        return formatted_output