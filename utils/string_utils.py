"""
String manipulation utilities for consistent text handling.
"""

import re
from typing import Optional

class StringUtils:
    """String manipulation utilities."""
    
    @staticmethod
    def create_slug(text: str) -> str:
        """Create a URL-friendly slug from text.
        
        Args:
            text: Text to convert to slug
            
        Returns:
            Slug string
        """
        # Convert to lowercase and replace spaces with hyphens
        slug = text.lower().strip().replace(' ', '-')
        
        # Remove special characters
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading and trailing hyphens
        slug = slug.strip('-')
        
        # Return a default if slug is empty
        return slug or 'untitled'
    
    @staticmethod
    def format_title(key: str) -> str:
        """Convert a camelCase or snake_case key to Title Case.
        
        Args:
            key: String in camelCase or snake_case
            
        Returns:
            String in Title Case
        """
        # Handle camelCase
        if any(c.isupper() for c in key):
            title = re.sub(r'([A-Z])', r' \1', key).strip()
            # Special cases
            title = title.replace(" I D", " ID")
            title = title.replace(" U R L", " URL")
        else:
            # Handle snake_case
            title = key.replace('_', ' ')
        
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in title.split())
    
    @staticmethod
    def extract_frontmatter(content: str) -> Optional[str]:
        """Extract YAML content between frontmatter delimiters.
        
        Args:
            content: Text containing frontmatter
            
        Returns:
            YAML content or None if not found
        """
        if not content:
            return None
            
        frontmatter_match = re.search(r'---\s*(.*?)\s*---', content, re.DOTALL)
        if frontmatter_match:
            return frontmatter_match.group(1).strip()
            
        return None