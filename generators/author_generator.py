#!/usr/bin/env python3
"""
Author Component Generator

Generates author information content using local JSON data.
"""

import logging
from typing import Dict, Optional
from generators.component_generators import StaticComponentGenerator

logger = logging.getLogger(__name__)

class AuthorComponentGenerator(StaticComponentGenerator):
    """Generator for author components using local author data"""
    
    def __init__(self):
        super().__init__("author")
    
    def _generate_static_content(self, material_name: str, material_data: Dict,
                                author_info: Optional[Dict] = None,
                                frontmatter_data: Optional[Dict] = None,
                                schema_fields: Optional[Dict] = None) -> str:
        """Generate author component content using author system"""
        try:
            from run import get_author_by_id
            from components.author.generator import create_author_content_from_data
            
            # Get author ID from author_info or use default
            author_id = 1  # Default to Taiwan author
            if author_info and 'id' in author_info:
                author_id = author_info['id']
            
            # Get author data using existing system
            author = get_author_by_id(author_id)
            if not author:
                # Fallback author data
                author = {
                    "name": "Expert Author", 
                    "title": "Ph.D.", 
                    "country": "International", 
                    "expertise": "Materials Science and Laser Technology",
                    "image": "/images/author/default.jpg"
                }
                logger.warning(f"Author {author_id} not found, using fallback data")
            
            # Generate content using the existing template function
            content = create_author_content_from_data(material_name, author)
            logger.info(f"Generated author component for {material_name} using author {author.get('name', 'Unknown')}")
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating author component for {material_name}: {e}")
            raise

def create_author_generator():
    """Factory function to create an author generator"""
    return AuthorComponentGenerator()
