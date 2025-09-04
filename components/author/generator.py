#!/usr/bin/env python3
"""
Author Component Generator

Generates author information content using local JSON data.
Integrated with the modular component architecture.
"""

import logging
import sys
import json
from pathlib import Path
from typing import Dict, Optional, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import after path setup
try:
    from generators.component_generators import APIComponentGenerator, ComponentResult
except ImportError:
    # Fallback if running standalone
    class APIComponentGenerator:
        def __init__(self, component_type): 
            self.component_type = component_type
        def generate(self, *args, **kwargs):
            raise NotImplementedError("Base class method")
    
    class ComponentResult:
        def __init__(self, component_type, content, success, error_message=None):
            self.component_type = component_type
            self.content = content
            self.success = success
            self.error_message = error_message

logger = logging.getLogger(__name__)

class AuthorComponentGenerator(APIComponentGenerator):
    """Generator for author components using local author data"""
    
    def __init__(self):
        super().__init__("author")
    
    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Generate author component content using author system"""
        try:
            from run import get_author_by_id
            
            # Determine author ID to use
            if author_info and 'id' in author_info:
                author_id = author_info['id']
            else:
                # Use first author as default
                author_id = 1
                
            # Get author data
            author_data = get_author_by_id(author_id)
            if not author_data:
                return ComponentResult(
                    component_type="author",
                    content="",
                    success=False,
                    error_message=f"Author with ID {author_id} not found"
                )
            
            # Generate author content
            author_name = author_data.get('name', 'Unknown Author')
            author_title = author_data.get('title', 'Expert')
            author_expertise = author_data.get('expertise', 'Technical Expert')
            country = author_data.get('country', 'International')
            
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
            
            return ComponentResult(
                component_type="author",
                content=content,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error generating author content: {e}")
            return ComponentResult(
                component_type="author",
                content="",
                success=False,
                error_message=str(e)
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
        """Legacy generate method"""
        author_info = {'id': author_id}
        material_data = {'name': material}
        
        # Call the correct method from AuthorComponentGenerator
        result = self.generator.generate(material, material_data, author_info=author_info)
        
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
            "type": "static"
        }
    
    @staticmethod
    def _create_author_template(material: str, author: Dict[str, Any]) -> str:
        """Create standardized author content template (legacy method for compatibility)"""
        # Use the provided author data directly instead of loading from JSON
        author_name = author.get('name', 'Unknown Author')
        author_title = author.get('title', 'Expert')
        author_expertise = author.get('expertise', 'Technical Expert')
        country = author.get('country', 'International')
        
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
