#!/usr/bin/env python3
"""Caption Component Generator"""

import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from generators.component_generators import StaticComponentGenerator
from utils.config_loader import load_yaml_config

class CaptionComponentGenerator(StaticComponentGenerator):
    def __init__(self):
        super().__init__("caption")

    def _load_frontmatter_data(self, material_name: str) -> Dict:
        """Load frontmatter data for the material"""
        content_dir = Path("content/components/frontmatter")
        
        potential_paths = [
            content_dir / f"{material_name.lower()}.yaml",
            content_dir / f"{material_name.lower().replace(' ', '-')}.yaml",
            content_dir / f"{material_name.lower().replace('_', '-')}.yaml",
            content_dir / f"{material_name.lower()}-laser-cleaning.yaml"
        ]
        
        for path in potential_paths:
            if path.exists():
                try:
                    return load_yaml_config(str(path))
                except Exception as e:
                    print(f"Warning: Could not load frontmatter from {path}: {e}")
                    continue
        
        return {}

    def _generate_static_content(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        timestamp = datetime.datetime.now().isoformat() + "Z"
        
        # Use provided frontmatter_data or try to load it
        if not frontmatter_data:
            frontmatter_data = self._load_frontmatter_data(material_name)
        
        # Generate enhanced content if frontmatter is available
        if frontmatter_data:
            author = frontmatter_data.get('author_object', {}).get('name', 'Dr. Research Specialist')
            category = frontmatter_data.get('category', 'metal')
            
            # Generate more detailed content
            before_text = f"Initial surface examination reveals significant contamination deposits across the {material_name.lower()} substrate. Microscopic analysis shows surface oxidation and environmental deposits requiring precision laser treatment."
            after_text = f"Post-laser cleaning analysis demonstrates remarkable surface restoration through comprehensive laser processing. The {material_name.lower()} substrate now exhibits pristine surface characteristics with minimal thermal effects."
            
        else:
            # Basic content without frontmatter
            before_text = f"Initial examination of {material_name.lower()} surface shows contamination requiring treatment."
            after_text = f"Post-cleaning analysis shows successful surface restoration on {material_name.lower()}."
            author = "Dr. Research Specialist"
            category = "metal"
        
        return f"""---
before_text: |
  {before_text}

after_text: |
  {after_text}

processing:
  frontmatter_available: {bool(frontmatter_data)}

generation:
  generated: "{timestamp}"

author: "{author}"

seo:
  title: "{material_name.title()} Surface Laser Cleaning Analysis"
  description: "Microscopic analysis of {material_name.lower()} surface before and after precision laser cleaning"

chemical_properties:
  materialType: "{category}"

---
Material: "{material_name.lower()}"
Component: caption
Generated: {timestamp}
Generator: Z-Beam v1.0.0
---"""

class CaptionGenerator:
    def __init__(self):
        self.generator = CaptionComponentGenerator()

    def generate(self, material: str, material_data: Dict = None) -> str:
        return self.generator._generate_static_content(material, Path("."), material_data)

def generate_caption_content(material: str, material_data: Dict = None) -> str:
    generator = CaptionGenerator()
    return generator.generate(material, material_data)
