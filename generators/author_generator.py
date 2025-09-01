#!/usr/bin/env python3
"""
Author Component Generator

Generates author information content using local JSON data.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)

class AuthorComponentGenerator(APIComponentGenerator):
    """Generator for author components using local author data"""
    
    def __init__(self):
        super().__init__("author")
    
    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Generate author component content using local author data"""
        try:
            from run import get_author_by_id
            
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
            
            # Generate author content using local data
            content = self._create_author_content(material_name, author)
            logger.info(f"Generated author component for {material_name} using author {author.get('name', 'Unknown')}")
            
            return ComponentResult(
                component_type="author",
                content=content,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error generating author component for {material_name}: {e}")
            return ComponentResult(
                component_type="author",
                content="",
                success=False,
                error_message=str(e)
            )
    
    def _create_author_content(self, material_name: str, author: Dict) -> str:
        """Create author content from author data"""
        name = author.get('name', 'Expert Author')
        title = author.get('title', 'Ph.D.')
        country = author.get('country', 'International')
        expertise = author.get('expertise', 'Materials Science')
        image_path = author.get('image', '/images/author/default.jpg')
        
        content = f"""**{name}, {title}**
*{expertise}*
*{country}*

![{name}]({image_path})

Expert analysis of {material_name} laser cleaning applications, providing technical insights based on extensive research in materials processing and laser technology."""
        
        return content

def create_author_generator():
    """Factory function to create an author generator"""
    return AuthorComponentGenerator()
