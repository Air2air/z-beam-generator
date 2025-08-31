#!/usr/bin/env python3
"""
Properties Table Generator

Generates standardized properties tables by extracting data from frontmatter.
Integrated with the modular component architecture.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import after path setup
try:
    from generators.component_generators import StaticComponentGenerator
except ImportError:
    # Fallback if running standalone
    class StaticComponentGenerator:
        def __init__(self, component_type): 
            self.component_type = component_type
        def _generate_static_content(self, *args, **kwargs):
            raise NotImplementedError("Base class method")


class PropertiesTableComponentGenerator(StaticComponentGenerator):
    """Generator for properties table components using frontmatter data"""
    
    def __init__(self):
        super().__init__("propertiestable")
        self.component_info = {
            "name": "Properties Table",
            "description": "Generates standardized properties tables from frontmatter data",
            "version": "2.0.0",  # Updated version
            "type": "static"
        }
    
    def _generate_static_content(self, material_name: str, material_data: Dict,
                                author_info: Optional[Dict] = None,
                                frontmatter_data: Optional[Dict] = None,
                                schema_fields: Optional[Dict] = None) -> str:
        """Generate properties table component content from frontmatter data"""
        if not frontmatter_data:
            return self._generate_fallback_table(material_name)
        
        # Build the properties table
        table = "| Property | Value |\n|----------|-------|\n"
        
        # Add chemical properties if available
        chem_props = frontmatter_data.get('chemicalProperties', {})
        if chem_props:
            if 'formula' in chem_props:
                table += f"| Chemical Formula | {chem_props['formula']} |\n"
            if 'symbol' in chem_props:
                table += f"| Material Symbol | {chem_props['symbol']} |\n"
            if 'materialType' in chem_props:
                table += f"| Material Type | {chem_props['materialType']} |\n"
        
        # Add physical properties
        properties = frontmatter_data.get('properties', {})
        if properties:
            if 'density' in properties:
                table += f"| Density | {properties['density']} |\n"
            if 'meltingPoint' in properties:
                table += f"| Melting Point | {properties['meltingPoint']} |\n"
            if 'thermalConductivity' in properties:
                table += f"| Thermal Conductivity | {properties['thermalConductivity']} |\n"
        
        # Add technical specifications
        tech_specs = frontmatter_data.get('technicalSpecifications', {})
        if tech_specs and hasattr(tech_specs, 'get'):
            if 'tensileStrength' in tech_specs:
                table += f"| Tensile Strength | {tech_specs['tensileStrength']} |\n"
        
        return table
    
    def _generate_fallback_table(self, material_name: str) -> str:
        """Generate basic table when no frontmatter available"""
        return f"""| Property | Value |
|----------|-------|
| Material | {material_name} |
| Type | Material |
| Status | Properties not available |"""


# Legacy compatibility class
class PropertiesTableGenerator:
    """Legacy properties table generator for backward compatibility"""
    
    def __init__(self):
        self.generator = PropertiesTableComponentGenerator()
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
