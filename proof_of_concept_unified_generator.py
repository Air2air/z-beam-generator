#!/usr/bin/env python3
"""
Proof of Concept: Unified Frontmatter Generator
Demonstrates how frontmatter can serve as the single source for all component outputs.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import yaml
import json

@dataclass
class UnifiedResult:
    """Result containing frontmatter and all derived outputs."""
    frontmatter: Dict[str, Any]
    derived_outputs: Dict[str, Any]
    success: bool
    errors: Optional[list] = None

class UnifiedFrontmatterGenerator:
    """
    Enhanced frontmatter generator that can derive all other component outputs
    from the core frontmatter data.
    """
    
    def __init__(self):
        self.frontmatter_generator = None  # Would be actual StreamlinedFrontmatterGenerator
    
    def generate_unified(self, material_name: str, output_formats: list = None) -> UnifiedResult:
        """
        Generate frontmatter and derive all requested component outputs.
        
        Args:
            material_name: Name of material to generate for
            output_formats: List of formats to generate (e.g., ['jsonld', 'metatags', 'table'])
        
        Returns:
            UnifiedResult with frontmatter and derived outputs
        """
        # Generate core frontmatter (existing functionality)
        frontmatter_data = self._generate_frontmatter(material_name)
        
        # Derive other component outputs
        derived_outputs = {}
        if output_formats:
            for format_name in output_formats:
                try:
                    derived_outputs[format_name] = self._derive_output(format_name, frontmatter_data)
                except Exception as e:
                    return UnifiedResult(
                        frontmatter=frontmatter_data,
                        derived_outputs=derived_outputs,
                        success=False,
                        errors=[f"Failed to derive {format_name}: {e}"]
                    )
        
        return UnifiedResult(
            frontmatter=frontmatter_data,
            derived_outputs=derived_outputs,
            success=True
        )
    
    def _generate_frontmatter(self, material_name: str) -> Dict[str, Any]:
        """Generate core frontmatter data (existing functionality)."""
        # This would use the existing StreamlinedFrontmatterGenerator
        return {
            "name": material_name,
            "category": "metal",  # Example
            "author": {"id": 1, "name": "Dr. Chen Wei-Ming"},
            "materialProperties": {"density": {"value": 2.7, "unit": "g/cm³"}},
            "machineSettings": {"powerRange": {"value": 50, "unit": "W"}},
            # ... all existing frontmatter fields
        }
    
    def _derive_output(self, format_name: str, frontmatter_data: Dict[str, Any]) -> Any:
        """Derive specific component output from frontmatter data."""
        derivation_methods = {
            'jsonld': self._derive_jsonld,
            'metatags': self._derive_metatags,
            'table': self._derive_table,
            'author': self._derive_author,
            'caption': self._derive_caption,
            'tags': self._derive_tags,
        }
        
        if format_name not in derivation_methods:
            raise ValueError(f"Unknown output format: {format_name}")
        
        return derivation_methods[format_name](frontmatter_data)
    
    def _derive_jsonld(self, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Derive JSON-LD structured data from frontmatter."""
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "name": f"{frontmatter_data['name']} Laser Cleaning",
            "author": {
                "@type": "Person",
                "name": frontmatter_data['author']['name']
            },
            "description": frontmatter_data.get('description', ''),
            # Derive full JSON-LD from frontmatter data
        }
    
    def _derive_metatags(self, frontmatter_data: Dict[str, Any]) -> Dict[str, str]:
        """Derive HTML metatags from frontmatter."""
        return {
            "title": f"{frontmatter_data['name']} Laser Cleaning Parameters",
            "description": frontmatter_data.get('description', ''),
            "keywords": f"{frontmatter_data['name']}, laser cleaning, {frontmatter_data.get('category', '')}",
            "author": frontmatter_data['author']['name'],
            # Derive all metatags from frontmatter data
        }
    
    def _derive_table(self, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Derive properties table from frontmatter."""
        properties = frontmatter_data.get('materialProperties', {})
        
        table_data = {
            "headers": ["Property", "Value", "Unit"],
            "rows": []
        }
        
        for prop_name, prop_data in properties.items():
            if isinstance(prop_data, dict) and 'value' in prop_data:
                table_data["rows"].append([
                    prop_name.replace('_', ' ').title(),
                    str(prop_data['value']),
                    prop_data.get('unit', '')
                ])
        
        return table_data
    
    def _derive_author(self, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Derive author information from frontmatter."""
        author_data = frontmatter_data.get('author', {})
        return {
            "bio": f"Content authored by {author_data.get('name', 'Unknown')}",
            "expertise": author_data.get('expertise', ''),
            "country": author_data.get('country', ''),
            # Full author component output derived from frontmatter
        }
    
    def _derive_caption(self, frontmatter_data: Dict[str, Any]) -> Dict[str, str]:
        """Derive image captions from frontmatter."""
        material_name = frontmatter_data['name']
        return {
            "before_text": f"{material_name} surface before laser cleaning treatment.",
            "after_text": f"{material_name} surface after laser cleaning, showing improved cleanliness.",
        }
    
    def _derive_tags(self, frontmatter_data: Dict[str, Any]) -> list:
        """Derive content tags from frontmatter."""
        tags = [
            frontmatter_data['name'].lower().replace(' ', '-'),
            frontmatter_data.get('category', '').lower(),
            'laser-cleaning',
            'surface-treatment',
        ]
        
        # Add author-based tags
        if 'author' in frontmatter_data:
            author_name = frontmatter_data['author'].get('name', '').lower()
            author_slug = author_name.replace(' ', '-').replace('.', '')
            tags.append(author_slug)
        
        return [tag for tag in tags if tag]  # Remove empty tags

# Example usage
def demo_unified_generation():
    """Demonstrate unified frontmatter generation."""
    generator = UnifiedFrontmatterGenerator()
    
    # Generate everything from frontmatter
    result = generator.generate_unified(
        material_name="Aluminum",
        output_formats=['jsonld', 'metatags', 'table', 'author', 'tags']
    )
    
    if result.success:
        print("✅ Unified generation successful!")
        print("📄 Frontmatter data:")
        print(yaml.dump(result.frontmatter, default_flow_style=False))
        
        print("🔄 Derived outputs:")
        for format_name, output_data in result.derived_outputs.items():
            print(f"\n{format_name.upper()}:")
            if isinstance(output_data, dict):
                print(json.dumps(output_data, indent=2))
            else:
                print(output_data)
    else:
        print("❌ Generation failed:")
        for error in result.errors:
            print(f"  - {error}")

if __name__ == "__main__":
    demo_unified_generation()