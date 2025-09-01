#!/usr/bin/env python3
"""
Properties Table Generator

Generates standardized properties tables by extracting data from frontmatter.
Integrated with the modular component architecture.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
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


class PropertiestableComponentGenerator(FrontmatterComponentGenerator):
    """Generator for properties table components using frontmatter data - NO API CALLS"""
    
    def __init__(self):
        super().__init__("propertiestable")
    
    def _extract_from_frontmatter(self, material_name: str, frontmatter_data: Dict) -> str:
        """Generate properties table component content from frontmatter data using material schema"""
        
        # Load schema to understand the expected structure
        try:
            schema_path = Path(__file__).parent.parent.parent / "schemas" / "material.json"
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    material_properties = schema.get('materialProfile', {}).get('profile', {}).get('properties', {}).get('properties', {})
            else:
                material_properties = {}
        except Exception:
            material_properties = {}
        
        # Load example file to understand the expected format
        try:
            example_path = Path(__file__).parent / "example_propertiestable.md"
            example_format = None
            if example_path.exists():
                with open(example_path, 'r', encoding='utf-8') as f:
                    example_content = f.read()
                    # Extract property names from example
                    example_format = self._parse_example_format(example_content)
        except Exception:
            example_format = None
        
        # Build the properties table dynamically
        table = "| Property | Value |\n|----------|-------|\n"
        
        # Use schema-defined properties or fallback to discovered properties
        properties_to_extract = []
        
        # Priority 1: Use schema-defined properties
        if material_properties:
            for prop_key, prop_info in material_properties.items():
                display_name = prop_info.get('description', prop_key.replace('_', ' ').title())
                properties_to_extract.append((prop_key, display_name))
        
        # Priority 2: Use example format if available
        elif example_format:
            properties_to_extract = example_format
        
        # Priority 3: Fallback to discovered properties from frontmatter
        else:
            # Discover properties from frontmatter structure
            properties_to_extract = self._discover_properties_from_frontmatter(frontmatter_data)
        
        # Extract values for each property
        for prop_key, display_name in properties_to_extract:
            value = self._get_property_value(frontmatter_data, prop_key)
            if value and value != 'N/A':
                table += f"| {display_name} | {value} |\n"
        
        return table
    
    def _parse_example_format(self, example_content: str) -> List[tuple]:
        """Parse example file to extract property format"""
        properties = []
        lines = example_content.split('\n')
        
        for line in lines:
            if '|' in line and not line.startswith('|--') and 'Property' not in line and 'Value' not in line:
                parts = [part.strip() for part in line.split('|') if part.strip()]
                if len(parts) >= 2:
                    property_name = parts[0]
                    # Convert display name to key (Formula -> formula, Thermal -> thermalConductivity, etc.)
                    property_key = self._display_name_to_key(property_name)
                    properties.append((property_key, property_name))
        
        return properties
    
    def _display_name_to_key(self, display_name: str) -> str:
        """Convert display name to frontmatter key"""
        name_mappings = {
            'Formula': 'chemicalProperties.formula',
            'Symbol': 'chemicalProperties.symbol', 
            'Category': 'category',
            'Density': 'properties.density',
            'Tensile': 'properties.tensileStrength',
            'Thermal': 'properties.thermalConductivity',
            'Chemical Formula': 'chemicalProperties.formula',
            'Material Symbol': 'chemicalProperties.symbol',
            'Material Type': 'chemicalProperties.materialType',
            'Melting Point': 'properties.meltingPoint'
        }
        
        return name_mappings.get(display_name, display_name.lower().replace(' ', '_'))
    
    def _discover_properties_from_frontmatter(self, frontmatter_data: Dict) -> List[tuple]:
        """Discover available properties from frontmatter structure"""
        properties = []
        
        # Chemical properties
        chem_props = frontmatter_data.get('chemicalProperties', {})
        if chem_props:
            if 'formula' in chem_props:
                properties.append(('chemicalProperties.formula', 'Chemical Formula'))
            if 'symbol' in chem_props:
                properties.append(('chemicalProperties.symbol', 'Material Symbol'))
            if 'materialType' in chem_props:
                properties.append(('chemicalProperties.materialType', 'Material Type'))
        
        # Physical properties
        props = frontmatter_data.get('properties', {})
        if props:
            prop_mappings = {
                'density': 'Density',
                'meltingPoint': 'Melting Point', 
                'thermalConductivity': 'Thermal Conductivity',
                'tensileStrength': 'Tensile Strength'
            }
            
            for key, display_name in prop_mappings.items():
                if key in props:
                    properties.append((f'properties.{key}', display_name))
        
        # Category
        if 'category' in frontmatter_data:
            properties.append(('category', 'Category'))
        
        return properties
    
    def _get_property_value(self, frontmatter_data: Dict, property_key: str) -> str:
        """Get property value using dot notation key"""
        try:
            if '.' in property_key:
                keys = property_key.split('.')
                value = frontmatter_data
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        return 'N/A'
                return str(value)
            else:
                return str(frontmatter_data.get(property_key, 'N/A'))
        except Exception:
            return 'N/A'


# Legacy compatibility class
class PropertiesTableGenerator:
    """Legacy properties table generator for backward compatibility"""
    
    def __init__(self):
        self.generator = PropertiestableComponentGenerator()
        self.component_info = {
            "name": "Properties Table",
            "description": "Generates standardized properties tables from frontmatter data",
            "version": "2.0.0",  # Updated version
            "type": "static"
        }
    
    def generate_content(self, material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate properties table from frontmatter data"""
        if not frontmatter_data:
            return self._generate_fallback_table(material_name)
        
        # Extract values with 8-character limit
        formula = self._get_field(frontmatter_data, ['chemicalProperties.formula', 'properties.chemicalFormula', 'formula'], 'N/A')
        symbol = self._get_field(frontmatter_data, ['chemicalProperties.symbol', 'symbol'], material_name[:3].upper())
        category = self._get_field(frontmatter_data, ['category'], 'Material').title()
        density = self._get_field(frontmatter_data, ['properties.density', 'chemicalProperties.density', 'density'], 'N/A')
        tensile = self._get_field(frontmatter_data, ['properties.tensileStrength', 'technicalSpecifications.tensileStrength'], 'N/A')
        thermal = self._get_field(frontmatter_data, ['properties.thermalConductivity', 'thermalProperties.conductivity'], 'N/A')
        
        # Extract min/max values for context (available for future enhancements)
        # density_min = self._get_field(frontmatter_data, ['properties.densityMin'], '')
        # density_max = self._get_field(frontmatter_data, ['properties.densityMax'], '')
        # tensile_min = self._get_field(frontmatter_data, ['properties.tensileMin'], '')
        # tensile_max = self._get_field(frontmatter_data, ['properties.tensileMax'], '')
        # thermal_min = self._get_field(frontmatter_data, ['properties.thermalMin'], '')
        # thermal_max = self._get_field(frontmatter_data, ['properties.thermalMax'], '')
        
        # Format values to 8 chars max
        formula = self._format_value(str(formula))
        symbol = self._format_value(str(symbol))
        category = self._format_value(self._abbreviate_category(str(category)))
        density = self._format_value(self._abbreviate_units(str(density)))
        tensile = self._format_value(self._abbreviate_units(str(tensile)))
        thermal = self._format_value(self._abbreviate_units(str(thermal)))
        
        return f"""| Property | Value |
|----------|-------|
| Formula | {formula} |
| Symbol | {symbol} |
| Category | {category} |
| Density | {density} |
| Tensile | {tensile} |
| Thermal | {thermal} |"""
    
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
    
    def _format_value(self, value: str) -> str:
        """Format value to max 8 characters"""
        if len(value) <= 8:
            return value
        return value[:7] + "…"
    
    def _abbreviate_type(self, material_type: str) -> str:
        """Abbreviate common material types"""
        # Convert to lowercase first for consistent matching (like badgesymbol)
        material_type_lower = material_type.lower()
        
        abbreviations = {
            'fiber-reinforced polymer': 'FRP',
            'carbon fiber reinforced polymer': 'CFRP', 
            'glass fiber reinforced polymer': 'GFRP',
            'stainless steel': 'SS',
            'cast iron': 'CI',
            'aluminum alloy': 'Al Alloy',
            'titanium alloy': 'Ti Alloy',
            'pure metal': 'Metal',
            'silicon carbide compound': 'SiC'
        }
        
        # Check for exact match with lowercase
        if material_type_lower in abbreviations:
            return abbreviations[material_type_lower]
        
        # For long material types, apply intelligent abbreviation
        if len(material_type) > 8:
            # Split on spaces and take first letters
            words = material_type.split()
            if len(words) > 1:
                abbrev = ''.join(word[0].upper() for word in words if word)
                if len(abbrev) <= 8:
                    return abbrev
        
        # Otherwise return title case, truncated if needed
        title_case = material_type.title()
        return title_case if len(title_case) <= 8 else title_case[:7] + "…"
    
    def _abbreviate_category(self, category: str) -> str:
        """Abbreviate common categories"""
        abbreviations = {
            'Composite': 'Composite',
            'Semiconductor': 'Semicond',
            'Ceramic': 'Ceramic', 
            'Metal': 'Metal',
            'Plastic': 'Plastic',
            'Glass': 'Glass',
            'Wood': 'Wood',
            'Stone': 'Stone',
            'Masonry': 'Masonry'
        }
        return abbreviations.get(category, category)
    
    def _abbreviate_units(self, value: str) -> str:
        """Abbreviate engineering units"""
        value = value.replace('Gigapascal', 'GPa').replace('Megapascal', 'MPa')
        value = value.replace('W/m·K', 'W/mK').replace('W/m-K', 'W/mK')
        value = value.replace('g/cm³', 'g/cm³').replace('kg/m³', 'kg/m³')
        value = value.replace(' to ', '-').replace(' ', '')
        return value
    
    def _generate_fallback_table(self, material_name: str) -> str:
        """Generate basic table when no frontmatter available"""
        symbol = material_name[:3].upper() if material_name else "MAT"
        return f"""| Property | Value |
|----------|-------|
| Formula | N/A |
| Symbol | {symbol} |
| Category | Material |
| Density | N/A |
| Tensile | N/A |
| Thermal | N/A |"""


# Static functions for compatibility
def create_properties_table_template(material_name: str) -> str:
    """Create properties table template for a material"""
    generator = PropertiesTableGenerator()
    return generator.generate_content(material_name)


def generate_properties_table_content(material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate properties table content from material name and optional frontmatter"""
    generator = PropertiesTableGenerator()
    return generator.generate_content(material_name, frontmatter_data)
