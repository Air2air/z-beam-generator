#!/usr/bin/env python3
"""
Author Component Generator

Generates author information content using local JSON data.
Uses consolidated component base utilities for reduced code duplication.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from generators.component_generators import APIComponentGenerator
from utils.component_base import (
    ComponentResult,
    handle_generation_error,
    validate_required_fields,
)


class AuthorComponentGenerator(APIComponentGenerator):
    """Generator for author components using local author data"""

    def __init__(self):
        super().__init__("author")
        self.authors_file = Path(__file__).parent / "authors.json"

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate author component content using author system"""
        try:
            # Validate required data
            if not material_name:
                return self.create_error_result("Material name is required")

            # Determine author ID to use
            author_id = author_info.get("id", 1) if author_info else 1

            # Get author data
            author_data = self._get_author_by_id(author_id)
            if not author_data:
                return self.create_error_result(f"Author with ID {author_id} not found")

            # Generate content
            content = self._create_author_content(material_name, author_data)

            return ComponentResult(
                component_type="author", content=content, success=True
            )

        except Exception as e:
            return handle_generation_error("author", e, "content generation")

    def _get_author_by_id(self, author_id: int) -> Optional[Dict[str, Any]]:
        """Get author data by ID"""
        try:
            if not self.authors_file.exists():
                return None

            with open(self.authors_file, "r", encoding="utf-8") as f:
                authors_data = json.load(f)

            for author in authors_data.get("authors", []):
                if author.get("id") == author_id:
                    return author
            return None

        except Exception as e:
            self.logger.error(f"Error loading author data: {e}")
            return None

    def _create_author_content(self, material_name: str, author_data: Dict) -> str:
        """Create author content from author data"""
        author_name = author_data.get("name", "Unknown Author")
        author_title = author_data.get("title", "Expert")
        author_expertise = author_data.get("expertise", "Technical Expert")
        country = author_data.get("country", "International")

        content = f"""
## About the Author

**{author_name}**
*{author_title}*

{author_name} is a {author_expertise.lower()} based in {country}. With extensive experience in laser processing and material science, {author_name.split()[0]} specializes in advanced laser cleaning applications and industrial material processing technologies.

### Expertise Areas
- Laser cleaning systems and applications
- Material science and processing
- Industrial automation and safety protocols
- Technical consultation and process optimization

*Contact {author_name.split()[0]} for expert consultation on laser cleaning applications for {material_name} and related materials.*
""".strip()

        return content

    def create_error_result(self, error_message: str) -> ComponentResult:
        """Create a ComponentResult for error cases"""
        return ComponentResult(
            component_type="author",
            content="",
            success=False,
            error_message=error_message,
        )


# Legacy compatibility classes and functions
class AuthorGenerator:
    """Legacy author generator for backward compatibility"""

    def __init__(self):
        self.generator = AuthorComponentGenerator()
        self.authors_file = Path("components/author/authors.json")
        self.template_file = Path("components/author/example_author.md")

    def _load_authors(self) -> Dict[str, Any]:
        """Load authors data from JSON file"""
        try:
            with open(self.authors_file, "r", encoding="utf-8") as f:
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
        """Legacy generate method"""
        author_info = {"id": author_id}
        material_data = {"name": material}

        # Call the correct method from AuthorComponentGenerator
        result = self.generator.generate(
            material, material_data, author_info=author_info
        )

        if result.success:
            return result.content
        else:
            return f"Error generating author content: {result.error_message}"

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "author",
            "description": "Author information component",
            "version": "2.0.0",  # Updated version
            "requires_api": False,
            "type": "static",
        }

    @staticmethod
    def _create_author_template(material: str, author: Dict[str, Any]) -> str:
        """Create standardized author content template (legacy method for compatibility)"""
        # Use the provided author data directly instead of loading from JSON
        author_name = author.get("name", "Unknown Author")
        author_title = author.get("title", "Expert")
        author_expertise = author.get("expertise", "Technical Expert")
        country = author.get("country", "International")

        content = f"""
## About the Author

**{author_name}**
*{author_title}*

{author_name} is a {author_expertise.lower()} based in {country}. With extensive experience in laser processing and material science, {author_name.split()[0]} specializes in advanced laser cleaning applications and industrial material processing technologies.

### Expertise Areas
- Laser cleaning systems and applications
- Material science and processing
- Industrial automation and safety protocols
- Technical consultation and process optimization

*Contact {author_name.split()[0]} for expert consultation on laser cleaning applications for {material} and related materials.*
""".strip()

        return content


def generate_author_content(material: str, author_id: int = 1) -> str:
    """Legacy function for backward compatibility"""
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
