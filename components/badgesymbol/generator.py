#!/usr/bin/env python3
"""
Badge Symbol Generator

Generates standardized badge symbol tables by extracting data from frontmatter.
Integrated with the modular component architecture.
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Any
import json
import yaml

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


class BadgesymbolComponentGenerator(FrontmatterComponentGenerator):
    """Generator for badge symbol components using frontmatter data - NO API CALLS"""
    
    def __init__(self):
        super().__init__("badgesymbol")
    
    def _extract_from_frontmatter(self, material_name: str, frontmatter_data: Dict) -> str:
        """Generate badge symbol component content from frontmatter data using schema and example"""
        
        # Load example file to understand the expected format
        try:
            example_path = Path(__file__).parent / "example_badgesymbol.md"
            example_fields = {}
            if example_path.exists():
                with open(example_path, 'r', encoding='utf-8') as f:
                    example_content = f.read()
                    example_fields = self._parse_example_frontmatter(example_content)
        except Exception:
            example_fields = {}
        
        # Load schema to understand expected structure  
        try:
            schema_path = Path(__file__).parent.parent.parent / "schemas" / "material.json"
            schema_fields = {}
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    chem_props = schema.get('materialProfile', {}).get('profile', {}).get('chemicalProperties', {}).get('properties', {})
                    if chem_props:
                        schema_fields = {
                            'symbol': chem_props.get('symbol', {}),
                            'materialType': chem_props.get('materialType', {})
                        }
        except Exception:
            schema_fields = {}
        
        # Extract values dynamically
        frontmatter_output = {}
        
        # Priority 1: Use example fields if available
        if example_fields:
            for field_name, example_value in example_fields.items():
                extracted_value = self._extract_field_value(frontmatter_data, field_name, material_name)
                frontmatter_output[field_name] = extracted_value
        # Priority 2: Use schema fields
        elif schema_fields:
            for field_name in schema_fields.keys():
                extracted_value = self._extract_field_value(frontmatter_data, field_name, material_name)
                frontmatter_output[field_name] = extracted_value
        # FAIL-FAST: No fallback allowed - system must have required schema or example
        else:
            raise Exception(f"No schema or example provided for badge symbol generation of {material_name} - fail-fast architecture requires explicit configuration")
        
        # Build frontmatter YAML
        yaml_lines = ['---']
        for key, value in frontmatter_output.items():
            yaml_lines.append(f'{key}: "{value}"')
        yaml_lines.append('---')
        
        return '\n'.join(yaml_lines)
    
    def _parse_example_frontmatter(self, example_content: str) -> Dict[str, str]:
        """Parse example file to extract frontmatter fields"""
        try:
            if example_content.startswith('---'):
                parts = example_content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter_yaml = parts[1].strip()
                    return yaml.safe_load(frontmatter_yaml) or {}
        except Exception:
            pass
        return {}
    
    def _extract_field_value(self, frontmatter_data: Dict, field_name: str, material_name: str) -> str:
        """Extract field value using multiple potential paths"""
        
        # Define field extraction paths
        field_paths = {
            'symbol': ['chemicalProperties.symbol', 'symbol', 'chemicalFormula'],
            'materialType': ['chemicalProperties.materialType', 'materialType', 'category', 'type']
        }
        
        paths = field_paths.get(field_name, [field_name])
        
        for path in paths:
            value = self._get_field(frontmatter_data, [path], None)
            if value and value != 'None':
                # Apply field-specific processing
                if field_name == 'symbol' and len(value) > 4:
                    # Truncate long symbols
                    return value[:4].upper()
                elif field_name == 'materialType':
                    return value.lower()
                return value
        
        # Generate fallback values
        if field_name == 'symbol':
            return material_name[:2].upper()
        elif field_name == 'materialType':
            return 'material'
        
        return field_name
    
    def _get_field(self, data: Dict[str, Any], paths: list, default: str) -> str:
        """Get field value from nested dict using dot notation paths"""
        for path in paths:
            value = data
            for key in path.split('.'):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break
            if value is not None:
                return str(value)
        return default


# Legacy compatibility class
class BadgeSymbolGenerator:
    """Legacy badge symbol generator for backward compatibility"""
    
    def __init__(self):
        self.generator = BadgesymbolComponentGenerator()
        self.component_info = {
            "name": "Badge Symbol",
            "description": "Generates standardized badge symbol tables from frontmatter data",
            "version": "2.0.0",  # Updated version
            "type": "static"
        }
    
    def generate_content(self, material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None) -> str:
        """Legacy generate_content method"""
        result = self.generator.generate(material_name, {}, frontmatter_data=frontmatter_data or {})
        return result.content if hasattr(result, 'content') else str(result)


# Static functions for compatibility
def create_badge_symbol_template(material_name: str) -> str:
    """Create badge symbol template for a material"""
    generator = BadgeSymbolGenerator()
    return generator.generate_content(material_name)


def generate_badge_symbol_content(material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate badge symbol content from material name and optional frontmatter"""
    generator = BadgeSymbolGenerator()
    return generator.generate_content(material_name, frontmatter_data)
