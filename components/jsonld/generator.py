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
from generators.component_generators import FrontmatterComponentGenerator, ComponentResult


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
                    if 'materialProfile' in schema and 'profile' in schema['materialProfile']:
                        material_profile = schema['materialProfile']['profile']
                        schema_structure = {
                            'basic': material_profile.get('basicInfo', {}),
                            'chemical': material_profile.get('chemicalProperties', {}),
                            'physical': material_profile.get('physicalProperties', {}),
                            'technical': material_profile.get('technicalSpecifications', {})
                        }
                    else:
                        raise Exception("Schema missing required 'materialProfile.profile' structure - fail-fast architecture requires complete schema")
            else:
                raise Exception(f"Required schema file missing: {schema_path} - fail-fast architecture requires complete schema configuration")
        except Exception as e:
            raise Exception(f"Failed to load schema: {e} - fail-fast architecture requires valid schema configuration")
        
        # Extract values dynamically
        if example_fields:
            # Use example structure as template
            jsonld_data = self._build_from_example(frontmatter_data, example_fields, material_name)
        elif schema_structure:
            # Use schema structure
            jsonld_data = self._build_from_schema(frontmatter_data, schema_structure, material_name)
        else:
            # FAIL-FAST: No fallback allowed - system must have required schema or example
            raise Exception(f"No schema or example provided for JSON-LD generation of {material_name} - fail-fast architecture requires explicit configuration")
        
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
                result[key] = self._get_field(frontmatter_data, ['title', 'name'], material_name)  # material_name as fallback for name
            elif key == 'description':
                result[key] = self._get_field(frontmatter_data, ['description'], f"Technical specifications and properties for {material_name}")  # Generated description as fallback
            elif key == 'category':
                if 'category' not in frontmatter_data and 'type' not in frontmatter_data:
                    raise Exception("Frontmatter data missing required 'category' or 'type' field - fail-fast architecture requires complete material information")
                result[key] = self._get_field(frontmatter_data, ['category', 'type'], None)  # No default - must exist
            elif isinstance(example_value, dict):
                result[key] = self._build_nested_structure(frontmatter_data, example_value, key)
            elif isinstance(example_value, list):
                result[key] = self._build_properties_array(frontmatter_data, example_value)
            else:
                # Try to extract similar field from frontmatter - allow defaults for optional fields
                result[key] = self._get_field(frontmatter_data, [key], str(example_value))
        
        return result
    
    def _build_from_schema(self, frontmatter_data: Dict, schema_structure: Dict, material_name: str) -> Dict:
        """Build JSON-LD using schema structure"""
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Material",
            "name": self._get_field(frontmatter_data, ['title', 'name'], material_name),  # material_name as fallback
            "description": self._get_field(frontmatter_data, ['description'], f"Technical specifications and properties for {material_name}"),  # Generated fallback
            "category": self._get_field(frontmatter_data, ['category', 'type'], None)  # No default - must exist
        }
        
        # Add chemical composition if available
        if 'chemical' in schema_structure:
            chem_props = schema_structure['chemical'].get('properties', {})
            if chem_props:
                # FAIL-FAST: Chemical properties must be available if schema defines them
                formula = self._get_field(frontmatter_data, ['chemicalProperties.formula', 'formula'], None)
                symbol = self._get_field(frontmatter_data, ['chemicalProperties.symbol', 'symbol'], None)
                if not formula:
                    raise Exception("Chemical formula required but not found in frontmatter data - fail-fast architecture requires complete chemical information")
                if not symbol:
                    raise Exception("Chemical symbol required but not found in frontmatter data - fail-fast architecture requires complete chemical information")
                
                jsonld["chemicalComposition"] = {
                    "@type": "ChemicalSubstance",
                    "molecularFormula": formula,  # Already validated above
                    "identifier": symbol  # Already validated above
                }
        
        # Add properties array
        properties = []
        for section_name, section_data in schema_structure.items():
            if section_name != 'basic' and isinstance(section_data, dict):
                if 'properties' not in section_data:
                    raise Exception(f"Schema section '{section_name}' missing required 'properties' field - fail-fast architecture requires complete schema")
                section_props = section_data['properties']
                for prop_name, prop_config in section_props.items():
                    prop_value = self._get_field(frontmatter_data, [f'{section_name}Properties.{prop_name}', prop_name], None)
                    if not prop_value:
                        raise Exception(f"Property '{prop_name}' required by schema but not found in frontmatter data - fail-fast architecture requires complete property information")
                    
                    # FAIL-FAST: Property config must have title
                    if 'title' not in prop_config:
                        raise Exception(f"Property config for '{prop_name}' missing required 'title' field - fail-fast architecture requires complete schema configuration")
                    
                    properties.append({
                        "@type": "PropertyValue",
                        "name": prop_config['title'],  # Already validated above
                        "value": prop_value  # Already validated above
                    })
        
        if properties:
            jsonld["properties"] = properties
        
        return jsonld
    

    
    def _build_nested_structure(self, frontmatter_data: Dict, example_structure: Dict, parent_key: str) -> Dict:
        """Build nested dictionary structure"""
        result = {}
        for key, example_value in example_structure.items():
            if key in ['@type']:
                result[key] = example_value
            else:
                field_path = f"{parent_key}.{key}" if parent_key != 'chemicalComposition' else f"chemicalProperties.{key}"
                result[key] = self._get_field(frontmatter_data, [field_path, key], str(example_value))  # Allow example_value as fallback for optional nested fields
        return result
    
    def _build_properties_array(self, frontmatter_data: Dict, example_array: list) -> list:
        """Build properties array from example structure"""
        if not example_array:
            return []
        
        # Use first item as template
        template = example_array[0] if isinstance(example_array[0], dict) else {}
        
        # FAIL-FAST: Template must have @type
        if not isinstance(template, dict) or '@type' not in template:
            raise Exception("Example array template missing required '@type' field - fail-fast architecture requires complete example structure")
        
        properties = []
        # Look for common property sections
        for section_name in ['physicalProperties', 'technicalSpecifications', 'properties']:
            if section_name not in frontmatter_data:
                continue  # Skip sections that don't exist
            section_data = frontmatter_data[section_name]
            if isinstance(section_data, dict):
                for prop_name, prop_value in section_data.items():
                    properties.append({
                        "@type": template["@type"],
                        "name": prop_name.replace('_', ' ').title(),
                        "value": str(prop_value)
                    })
        
        if not properties:
            raise Exception("No properties found in frontmatter data - fail-fast architecture requires at least one property for JSON-LD generation")
        
        return properties
    
    def _get_field(self, data: Dict, paths: list, default: str = None) -> str:
        """Extract field using dot notation paths - FAIL-FAST: default must be explicitly handled"""
        for path in paths:
            if '.' in path:
                # Handle nested path
                keys = path.split('.')
                current = data
                try:
                    for key in keys:
                        if key not in current:
                            continue
                        current = current[key]
                    if current is not None:
                        return str(current)
                except (KeyError, TypeError):
                    continue
            else:
                # Handle direct key
                if path in data and data[path] is not None:
                    return str(data[path])
        
        # FAIL-FAST: If no default provided, field must exist
        if default is None:
            raise Exception(f"Required field not found in data. Searched paths: {paths} - fail-fast architecture requires complete data")
        return default
