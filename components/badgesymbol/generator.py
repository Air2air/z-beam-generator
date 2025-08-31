#!/usr/bin/env python3
"""
Badge Symbol Generator

Generates standardized badge symbol tables by extracting data from frontmatter.
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


class BadgeSymbolComponentGenerator(StaticComponentGenerator):
    """Generator for badge symbol components using frontmatter data"""
    
    def __init__(self):
        super().__init__("badgesymbol")
        self.component_info = {
            "name": "Badge Symbol",
            "description": "Generates standardized badge symbol tables from frontmatter data",
            "version": "2.0.0",  # Updated version
            "type": "static"
        }
    
    def _generate_static_content(self, material_name: str, material_data: Dict,
                                author_info: Optional[Dict] = None,
                                frontmatter_data: Optional[Dict] = None,
                                schema_fields: Optional[Dict] = None) -> str:
        """Generate badge symbol component content from frontmatter data"""
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


# Legacy compatibility class
class BadgeSymbolGenerator:
    """Legacy badge symbol generator for backward compatibility"""
    
    def __init__(self):
        self.generator = BadgeSymbolComponentGenerator()
        self.component_info = {
            "name": "Badge Symbol",
            "description": "Generates standardized badge symbol tables from frontmatter data",
            "version": "2.0.0",  # Updated version
            "type": "static"
        }
    
    def generate_content(self, material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None) -> str:
        """Legacy generate_content method"""
        material_data = {'name': material_name}
        return self.generator._generate_static_content(material_name, material_data, 
                                                     frontmatter_data=frontmatter_data)


# Static functions for compatibility
def create_badge_symbol_template(material_name: str) -> str:
    """Create badge symbol template for a material"""
    generator = BadgeSymbolGenerator()
    return generator.generate_content(material_name)


def generate_badge_symbol_content(material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate badge symbol content from material name and optional frontmatter"""
    generator = BadgeSymbolGenerator()
    return generator.generate_content(material_name, frontmatter_data)
