#!/usr/bin/env python3
"""
Author Component Generator

Simple component that generates author information markdown files
without requiring AI API calls. Uses the local authors.json data.
"""

import json
from pathlib import Path
from typing import Dict, Any


class AuthorGenerator:
    """Generate author component content from local JSON data"""
    
    def __init__(self):
        """Initialize the author generator"""
        self.authors_file = Path("components/author/authors.json")
        self.template_file = Path("validators/examples/author.md")
        
    def _load_authors(self) -> Dict[str, Any]:
        """Load authors data from JSON file"""
        try:
            with open(self.authors_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ Error loading authors data: {e}")
            return {"authors": []}
    
    def _load_template(self) -> str:
        """Load author template from master template file"""
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to hardcoded template if file not found
            return self._get_fallback_template()
    
    def _get_fallback_template(self) -> str:
        """Fallback template if master template file is not available"""
        return """{author_name}  
{author_title}  
{author_expertise}  
{author_country}  
{author_image}"""
    
    def get_author_by_id(self, author_id: int) -> Dict[str, Any]:
        """Get author data by ID"""
        authors_data = self._load_authors()
        for author in authors_data.get("authors", []):
            if author.get("id") == author_id:
                return author
        return {}
    
    def generate(self, material: str, author_id: int = 1) -> str:
        """Generate author component content"""
        author = self.get_author_by_id(author_id)
        
        if not author:
            return f"Author information not found for ID: {author_id}"
        
        # Load template and substitute variables
        template = self._load_template()
        return self._populate_template(template, material, author)
    
    def _populate_template(self, template: str, material: str, author: Dict[str, Any]) -> str:
        """Populate template with author data and material information"""
        return template.format(
            author_name=author.get('name', 'Unknown Author'),
            author_title=author.get('title', 'Ph.D.'),
            author_expertise=author.get('expertise', 'Materials Science and Laser Technology'),
            author_country=author.get('country', 'International'),
            author_image=author.get('image', '/images/author/default.jpg'),
            material=material
        )
    
    @staticmethod
    def _create_author_template(material: str, author: Dict[str, Any]) -> str:
        """Create standardized author content template (legacy method for compatibility)"""
        # For backward compatibility, create a generator instance and use the template method
        generator = AuthorGenerator()
        template = generator._load_template()
        return generator._populate_template(template, material, author)
    
    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "author",
            "description": "Author information component",
            "version": "1.0.0",
            "requires_api": False,
            "type": "static"
        }


# Standalone functions for direct usage
def generate_author_content(material: str, author_id: int = 1) -> str:
    """Generate author content for a material (simplified interface)"""
    generator = AuthorGenerator()
    return generator.generate(material, author_id)


def create_author_content_from_data(material: str, author: Dict[str, Any]) -> str:
    """Create author content directly from author data (most efficient)"""
    return AuthorGenerator._create_author_template(material, author)


if __name__ == "__main__":
    # Test the generator
    generator = AuthorGenerator()
    test_content = generator.generate("Aluminum", 1)
    print("🧪 Author Component Test:")
    print("=" * 50)
    print(test_content)
