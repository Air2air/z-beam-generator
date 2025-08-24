#!/usr/bin/env python3
"""
Badge Symbol Generator

Generates standardized badge symbol tables by extracting data from frontmatter.
This is a static component that doesn't require API calls.
"""

from typing import Dict, Any, Optional


class BadgeSymbolGenerator:
    """Generates badge symbol tables from frontmatter data"""
    
    def __init__(self):
        self.component_info = {
            "name": "Badge Symbol",
            "description": "Generates standardized badge symbol tables from frontmatter data",
            "version": "1.0.0",
            "type": "static"
        }
    
    def generate_content(self, material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate badge symbol content from frontmatter data"""
        if not frontmatter_data:
            return self._generate_fallback_content(material_name)
        
        # Extract values for badge symbol
        symbol = self._get_field(frontmatter_data, ['chemicalProperties.symbol', 'symbol'], material_name[:2].upper())
        material_type = self._get_field(frontmatter_data, ['chemicalProperties.materialType', 'materialType', 'category'], 'material')
        
        # Create frontmatter section only
        frontmatter = f'---\nsymbol: "{symbol}"\nmaterialType: "{material_type.lower()}"\n---'
        
        return frontmatter
    
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
    
    def _generate_fallback_content(self, material_name: str) -> str:
        """Generate basic content when no frontmatter available"""
        symbol = material_name[:2].upper() if material_name else "MA"
        return f'---\nsymbol: "{symbol}"\nmaterialType: "material"\n---'


# Static functions for compatibility
def create_badge_symbol_template(material_name: str) -> str:
    """Create badge symbol template for a material"""
    generator = BadgeSymbolGenerator()
    return generator.generate_content(material_name)


def generate_badge_symbol_content(material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate badge symbol content from material name and optional frontmatter"""
    generator = BadgeSymbolGenerator()
    return generator.generate_content(material_name, frontmatter_data)
