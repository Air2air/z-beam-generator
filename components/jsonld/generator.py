#!/usr/bin/env python3
"""
JSON-LD Component Generator

Generates JSON-LD structured data using frontmatter extraction.
Integrated with the modular component architecture.
"""

import sys
from pathlib import Path
from typing import Dict
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import after path setup
try:
    from generators.component_generators import FrontmatterComponentGenerator, ComponentResult
except ImportError:
    # Fallback if running standalone
    class FrontmatterComponentGenerator:
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


class JsonldComponentGenerator(FrontmatterComponentGenerator):
    """Generator for JSON-LD components using frontmatter data"""
    
    def __init__(self):
        super().__init__("jsonld")
    
    def _extract_from_frontmatter(self, material_name: str, frontmatter_data: Dict) -> str:
        """Generate JSON-LD structured data from frontmatter using schema and example"""
        
        # Load example file to understand the expected format
        try:
            example_path = Path(__file__).parent / "example_jsonld.md"
            example_fields = {}
            if example_path.exists():
                with open(example_path, 'r', encoding='utf-8') as f:
                    example_content = f.read()
                    example_fields = self._parse_example_json_ld(example_content)
        except Exception:
            example_fields = {}
        
        # Load schema to understand expected structure  
        try:
            schema_path = Path(__file__).parent.parent.parent / "schemas" / "material.json"
            schema_structure = {}
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    # Extract relevant properties for JSON-LD
                    material_profile = schema.get('materialProfile', {}).get('profile', {})
                    schema_structure = {
                        'basic': material_profile.get('basicInfo', {}),
                        'chemical': material_profile.get('chemicalProperties', {}),
                        'physical': material_profile.get('physicalProperties', {}),
                        'technical': material_profile.get('technicalSpecifications', {})
                    }
        except Exception:
            schema_structure = {}
        
        # Extract values dynamically
        if example_fields:
            # Use example structure as template
            jsonld_data = self._build_from_example(frontmatter_data, example_fields, material_name)
        elif schema_structure:
            # Use schema structure
            jsonld_data = self._build_from_schema(frontmatter_data, schema_structure, material_name)
        else:
            # Fallback to hardcoded structure
            jsonld_data = self._build_fallback_jsonld(frontmatter_data, material_name)
        
        # Format as proper JSON-LD script tag
        json_content = json.dumps(jsonld_data, indent=2)
        return f'<script type="application/ld+json">\n{json_content}\n</script>'
    
    def _parse_example_json_ld(self, example_content: str) -> Dict:
        """Parse example file to extract JSON-LD structure"""
        try:
            # Look for JSON-LD script tags
            if '<script type="application/ld+json">' in example_content:
                start_tag = '<script type="application/ld+json">'
                end_tag = '</script>'
                start_idx = example_content.find(start_tag) + len(start_tag)
                end_idx = example_content.find(end_tag, start_idx)
                if start_idx > 0 and end_idx > start_idx:
                    json_str = example_content[start_idx:end_idx].strip()
                    return json.loads(json_str)
        except Exception:
            pass
        return {}
    
    def _build_from_example(self, frontmatter_data: Dict, example_structure: Dict, material_name: str) -> Dict:
        """Build JSON-LD using example structure as template"""
        result = {}
        
        for key, example_value in example_structure.items():
            if key in ['@context', '@type']:
                result[key] = example_value
            elif key == 'name':
                result[key] = self._get_field(frontmatter_data, ['title', 'name'], material_name)
            elif key == 'description':
                result[key] = self._get_field(frontmatter_data, ['description'], f"Technical specifications and properties for {material_name}")
            elif key == 'category':
                result[key] = self._get_field(frontmatter_data, ['category', 'type'], 'Material')
            elif isinstance(example_value, dict):
                result[key] = self._build_nested_structure(frontmatter_data, example_value, key)
            elif isinstance(example_value, list):
                result[key] = self._build_properties_array(frontmatter_data, example_value)
            else:
                # Try to extract similar field from frontmatter
                result[key] = self._get_field(frontmatter_data, [key], str(example_value))
        
        return result
    
    def _build_from_schema(self, frontmatter_data: Dict, schema_structure: Dict, material_name: str) -> Dict:
        """Build JSON-LD using schema structure"""
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Material",
            "name": self._get_field(frontmatter_data, ['title', 'name'], material_name),
            "description": self._get_field(frontmatter_data, ['description'], f"Technical specifications and properties for {material_name}"),
            "category": self._get_field(frontmatter_data, ['category', 'type'], 'Material')
        }
        
        # Add chemical composition if available
        if 'chemical' in schema_structure:
            chem_props = schema_structure['chemical'].get('properties', {})
            if chem_props:
                jsonld["chemicalComposition"] = {
                    "@type": "ChemicalSubstance",
                    "molecularFormula": self._get_field(frontmatter_data, ['chemicalProperties.formula', 'formula'], 'N/A'),
                    "identifier": self._get_field(frontmatter_data, ['chemicalProperties.symbol', 'symbol'], material_name[:3].upper())
                }
        
        # Add properties array
        properties = []
        for section_name, section_data in schema_structure.items():
            if section_name != 'basic' and isinstance(section_data, dict):
                section_props = section_data.get('properties', {})
                for prop_name, prop_config in section_props.items():
                    prop_value = self._get_field(frontmatter_data, [f'{section_name}Properties.{prop_name}', prop_name], 'N/A')
                    properties.append({
                        "@type": "PropertyValue",
                        "name": prop_config.get('title', prop_name.title()),
                        "value": prop_value
                    })
        
        if properties:
            jsonld["properties"] = properties
        
        return jsonld
    
    def _build_fallback_jsonld(self, frontmatter_data: Dict, material_name: str) -> Dict:
        """Build fallback JSON-LD structure"""
        # Extract basic material information
        title = frontmatter_data.get('title', material_name)
        description = frontmatter_data.get('description', f"Technical specifications and properties for {material_name}")
        category = frontmatter_data.get('category', 'Material')
        
        # Extract chemical properties
        chem_props = frontmatter_data.get('chemicalProperties', {})
        formula = chem_props.get('formula', 'N/A')
        symbol = chem_props.get('symbol', material_name[:3].upper())
        
        # Extract physical properties
        properties = frontmatter_data.get('properties', {})
        density = properties.get('density', 'N/A')
        melting_point = properties.get('meltingPoint', 'N/A')
        thermal_conductivity = properties.get('thermalConductivity', 'N/A')
        
        # Extract technical specifications
        tech_specs = frontmatter_data.get('technicalSpecifications', {})
        tensile_strength = tech_specs.get('tensileStrength', 'N/A') if tech_specs else 'N/A'
        
        # Build JSON-LD structure
        return {
            "@context": "https://schema.org",
            "@type": "Material",
            "name": title,
            "description": description,
            "category": category,
            "chemicalComposition": {
                "@type": "ChemicalSubstance",
                "molecularFormula": formula,
                "identifier": symbol
            },
            "properties": [
                {
                    "@type": "PropertyValue",
                    "name": "Density",
                    "value": density
                },
                {
                    "@type": "PropertyValue", 
                    "name": "Melting Point",
                    "value": melting_point
                },
                {
                    "@type": "PropertyValue",
                    "name": "Thermal Conductivity", 
                    "value": thermal_conductivity
                },
                {
                    "@type": "PropertyValue",
                    "name": "Tensile Strength",
                    "value": tensile_strength
                }
            ]
        }
    
    def _build_nested_structure(self, frontmatter_data: Dict, example_structure: Dict, parent_key: str) -> Dict:
        """Build nested dictionary structure"""
        result = {}
        for key, example_value in example_structure.items():
            if key in ['@type']:
                result[key] = example_value
            else:
                field_path = f"{parent_key}.{key}" if parent_key != 'chemicalComposition' else f"chemicalProperties.{key}"
                result[key] = self._get_field(frontmatter_data, [field_path, key], str(example_value))
        return result
    
    def _build_properties_array(self, frontmatter_data: Dict, example_array: list) -> list:
        """Build properties array from example structure"""
        if not example_array:
            return []
        
        # Use first item as template
        template = example_array[0] if isinstance(example_array[0], dict) else {}
        
        properties = []
        # Look for common property sections
        for section_name in ['physicalProperties', 'technicalSpecifications', 'properties']:
            section_data = frontmatter_data.get(section_name, {})
            if isinstance(section_data, dict):
                for prop_name, prop_value in section_data.items():
                    properties.append({
                        "@type": template.get("@type", "PropertyValue"),
                        "name": prop_name.replace('_', ' ').title(),
                        "value": str(prop_value)
                    })
        
        return properties if properties else [template]
    
    def _get_field(self, data: Dict, paths: list, default: str = "") -> str:
        """Extract field using dot notation paths with fallback"""
        for path in paths:
            if '.' in path:
                # Handle nested path
                keys = path.split('.')
                current = data
                try:
                    for key in keys:
                        current = current[key]
                    if current is not None:
                        return str(current)
                except (KeyError, TypeError):
                    continue
            else:
                # Handle direct key
                value = data.get(path)
                if value is not None:
                    return str(value)
        return default
