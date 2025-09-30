#!/usr/bin/env python3
"""
Author Component Generator

Generates author information in YAML format using frontmatter data only.
Noompatibility, no API calls - pure frontmatter extraction.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


from generators.component_generators import ComponentResult


class AuthorComponentGenerator:
    """Generator for author components using frontmatter data only"""

    def __init__(self):
        self.component_type = "author"
        # Load author lookup data
        authors_file = Path(__file__).parent / "authors.json"
        with open(authors_file, 'r') as f:
            self.authors_data = json.load(f)
        self.authors_lookup = {author["id"]: author for author in self.authors_data["authors"]}

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate author component content using frontmatter data only"""
        try:
            # Validate required data
            if not material_name:
                return self.create_error_result("Material name is required")
            
            if not frontmatter_data:
                return self.create_error_result("Frontmatter data is required - fail-fast architecture requires frontmatter author information")

            # Extract author data from frontmatter
            author_data = frontmatter_data.get("author")
            if not author_data:
                return self.create_error_result("No author found in frontmatter data")

            # Generate YAML content from frontmatter author data
            yaml_content = self._create_author_yaml(material_name, author_data)

            # Return clean YAML without versioning delimiters
            return ComponentResult(
                component_type="author", content=yaml_content, success=True
            )

        except Exception as e:
            return self.create_error_result(f"Content generation failed: {e}")

    def _create_author_yaml(self, material_name: str, author_data: Dict) -> str:
        """Create author content in YAML format from frontmatter author data"""
        
        # Validate required author fields - fail-fast architecture, no fallbacks
        required_fields = ["name", "title", "expertise", "country", "id", "image", "sex"]
        for field in required_fields:
            if field not in author_data:
                raise ValueError(f"Required author field '{field}' missing from frontmatter data - fail-fast architecture requires complete author information")
        
        # Extract author information - no fallback values
        author_title = author_data["title"]
        author_expertise = author_data["expertise"]
        country = author_data["country"]
        author_id = author_data["id"]
        image_url = author_data["image"]
        sex = author_data["sex"]

        # Look up author name from authors.json for profile text
        if author_id not in self.authors_lookup:
            raise ValueError(f"Author ID {author_id} not found in authors.json - fail-fast architecture requires valid author references")
        
        author_name = self.authors_lookup[author_id]["name"]
        first_name = author_name.split()[0]

        # Create structured author data
        author_structure = {
            "author": {
                "id": author_id,
                "name": author_name,
                "title": author_title,
                "expertise": author_expertise,
                "country": country,
                "sex": sex,
                "image": image_url,
                "profile": {
                    "description": f"{author_name} is a {author_expertise.lower()}{' based in ' + country if country else ''}. With extensive experience in laser processing and material science, {first_name} specializes in advanced laser cleaning applications and industrial material processing technologies.",
                    "expertiseAreas": [
                        "Laser cleaning systems and applications",
                        "Material science and processing", 
                        "Industrial automation and safety protocols",
                        "Technical consultation and process optimization"
                    ],
                    "contactNote": f"Contact {first_name} for expert consultation on laser cleaning applications for {material_name} and related materials."
                }
            },
            "materialContext": {
                "specialization": f"{material_name} laser cleaning applications"
            }
        }

        # Convert to clean YAML without delimiters
        yaml_output = yaml.dump(author_structure, default_flow_style=False, sort_keys=False, width=1000)
        return yaml_output.strip()

    def create_error_result(self, error_message: str) -> ComponentResult:
        """Create a ComponentResult for error cases"""
        return ComponentResult(
            component_type="author",
            content="",
            success=False,
            error_message=error_message,
        )


if __name__ == "__main__":
    # Test the generator
    print("🧪 Author Component Test:")
    print("=" * 50)
    
    # Sample frontmatter data
    test_frontmatter = {
        "author": {
            "id": 1,
            "title": "Ph.D.",
            "expertise": "Laser Materials Processing",
            "country": "Taiwan",
            "sex": "f",
            "image": "/images/author/yi-chun-lin.jpg"
        }
    }
    
    generator = AuthorComponentGenerator()
    result = generator.generate("Aluminum", {"name": "Aluminum"}, frontmatter_data=test_frontmatter)
    
    if result.success:
        print("✅ Generation successful")
        print(result.content)
    else:
        print("❌ Generation failed:", result.error_message)
