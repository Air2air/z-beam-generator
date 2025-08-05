"""
Tags generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Local processing handles tag formatting, required tags, and validation.
"""

import logging
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class TagsGenerator(BaseComponent):
    """Generator for article tags with strict validation and local formatting."""
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated tags with enhanced local formatting.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed tags
            
        Raises:
            ValueError: If content is invalid
        """
        # Parse tags from various formats
        raw_tags = self._parse_raw_tags(content)
        
        # Apply formatting rules
        processed_tags = self._format_tags(raw_tags)
        
        # Ensure required tags are present
        processed_tags = self._ensure_required_tags(processed_tags)
        
        # Get validation parameters
        min_tags = self.get_component_config("min_tags")
        max_tags = self.get_component_config("max_tags")
        
        # Validate tag count
        if min_tags > 0 and len(processed_tags) < min_tags:
            raise ValueError(f"Generated tags too few: {len(processed_tags)}, minimum required: {min_tags}")
        
        # Truncate to max_tags if needed
        if max_tags > 0 and len(processed_tags) > max_tags:
            processed_tags = processed_tags[:max_tags]
        
        # Format tags as comma-separated list
        return ', '.join(processed_tags) + '\n'
    
    def _parse_raw_tags(self, content: str) -> list:
        """Parse tags from various possible API response formats.
        
        Args:
            content: Raw API response
            
        Returns:
            list: Parsed tag list
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
        return [tag.strip() for tag in tag_lines if tag.strip()]
    
    def _format_tags(self, tags: list) -> list:
        """Apply formatting rules to tags.
        
        Args:
            tags: Raw tag list
            
        Returns:
            list: Formatted tag list
        """
        formatted = []
        for tag in tags:
            # Convert to title case
            tag = ' '.join(word.capitalize() for word in tag.split())
            
            # Limit to 2 words
            if len(tag.split()) > 2:
                tag = ' '.join(tag.split()[:2])
            
            # Add to formatted list if not empty
            if tag:
                formatted.append(tag)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(formatted))
    
    def _ensure_required_tags(self, tags: list) -> list:
        """Ensure required tags are present.
        
        Args:
            tags: Formatted tag list
            
        Returns:
            list: Tag list with required tags
        """
        # Start with provided tags (case-insensitive comparison)
        tag_lower_map = {tag.lower(): tag for tag in tags}
        result = list(tags)
        
        # Always include "Laser Cleaning"
        if "laser cleaning" not in tag_lower_map:
            result.insert(0, "Laser Cleaning")
        
        # Add material category if applicable
        if self.article_type == "material" and hasattr(self, "category"):
            category = self.category.capitalize()
            if category.lower() not in tag_lower_map:
                result.append(category)
        
        # Add author name as a tag
        author_name = self.author_data.get("author_name", "")
        if author_name and author_name.lower() not in tag_lower_map:
            result.append(author_name)
        
        # Add application type if applicable
        if self.article_type == "application":
            app_tag = "Surface Treatment"
            if app_tag.lower() not in tag_lower_map:
                result.append(app_tag)
        
        return result