#!/usr/bin/env python3
"""
Properties Table Generator

Generates standardized properties tables by extracting data from frontmatter.
This is a static component that doesn't require API calls.
"""

from typing import Dict, Any, Optional


class PropertiesTableGenerator:
    """Generates properties tables from frontmatter data"""
    
    def __init__(self):
        self.component_info = {
            "name": "Properties Table",
            "description": "Generates standardized properties tables from frontmatter data",
            "version": "1.1.0",
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
        material_type = self._get_field(frontmatter_data, ['chemicalProperties.materialType', 'materialType', 'type'], 'Unknown')
        tensile = self._get_field(frontmatter_data, ['properties.tensileStrength', 'technicalSpecifications.tensileStrength'], 'N/A')
        thermal = self._get_field(frontmatter_data, ['properties.thermalConductivity', 'thermalProperties.conductivity'], 'N/A')
        
        # Format values to 8 chars max
        formula = self._format_value(str(formula))
        symbol = self._format_value(str(symbol))
        category = self._format_value(self._abbreviate_category(str(category)))
        material_type = self._format_value(self._abbreviate_type(str(material_type)))
        tensile = self._format_value(self._abbreviate_units(str(tensile)))
        thermal = self._format_value(self._abbreviate_units(str(thermal)))
        
        return f"""| Property | Value |
|----------|-------|
| Chemical Formula | {formula} |
| Material Symbol | {symbol} |
| Category | {category} |
| Material Type | {material_type} |
| Tensile Strength | {tensile} |
| Thermal Conductivity | {thermal} |"""
    
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
        value = value.replace(' to ', '-').replace(' ', '')
        return value
    
    def _generate_fallback_table(self, material_name: str) -> str:
        """Generate basic table when no frontmatter available"""
        symbol = material_name[:3].upper() if material_name else "MAT"
        return f"""| Property | Value |
|----------|-------|
| Chemical Formula | N/A |
| Material Symbol | {symbol} |
| Category | Material |
| Material Type | Unknown |
| Tensile Strength | N/A |
| Thermal Conductivity | N/A |"""


# Static functions for compatibility
def create_properties_table_template(material_name: str) -> str:
    """Create properties table template for a material"""
    generator = PropertiesTableGenerator()
    return generator.generate_content(material_name)


def generate_properties_table_content(material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate properties table content from material name and optional frontmatter"""
    generator = PropertiesTableGenerator()
    return generator.generate_content(material_name, frontmatter_data)
