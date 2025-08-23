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
        
    def _load_authors(self) -> Dict[str, Any]:
        """Load authors data from JSON file"""
        try:
            with open(self.authors_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ Error loading authors data: {e}")
            return {"authors": []}
    
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
            return f"# Author Information\n\nAuthor information not found for ID: {author_id}"
        
        # Create author component content using template
        return self._create_author_template(material, author)
    
    @staticmethod
    def _create_author_template(material: str, author: Dict[str, Any]) -> str:
        """Create standardized author content template"""
        return f"""# Author Information

**{author.get('name', 'Unknown Author')}**, {author.get('title', 'Ph.D.')}

*{author.get('expertise', 'Materials Science and Laser Technology')}*

**Country**: {author.get('country', 'International')}

**Author Image**: `{author.get('image', 'public/images/author/default.jpg')}`

---

*This article on {material} laser cleaning was authored by {author.get('name', 'Unknown Author')}, a leading expert in materials science and laser technology from {author.get('country', 'International')}.*
"""
    
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
