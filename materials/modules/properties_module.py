"""
PropertiesModule - Extract materialProperties with ranges from Categories.yaml

Handles: materialProperties dictionary with min/max ranges

Architecture:
- Extract properties from Materials.yaml
- Apply min/max ranges from Categories.yaml
- Separate qualitative properties to materialCharacteristics
- Fail-fast if category ranges not defined
"""

import logging
from typing import Dict
import yaml
from pathlib import Path


class PropertiesModule:
    """Extract and format materialProperties for frontmatter"""
    
    def __init__(self, categories_yaml_path: str = "data/Categories.yaml"):
        """
        Initialize properties module
        
        Args:
            categories_yaml_path: Path to Categories.yaml
        """
        self.logger = logging.getLogger(__name__)
        self.categories_yaml_path = categories_yaml_path
        self._categories_data = None
    
    @property
    def categories_data(self) -> Dict:
        """Lazy-load categories data"""
        if self._categories_data is None:
            path = Path(self.categories_yaml_path)
            
            if not path.exists():
                raise FileNotFoundError(f"Categories.yaml not found: {path}")
            
            with open(path, 'r') as f:
                self._categories_data = yaml.safe_load(f)
            
            self.logger.debug("Loaded Categories.yaml")
        
        return self._categories_data
    
    def generate(self, material_name: str, material_data: Dict) -> Dict:
        """
        Extract materialProperties with ranges
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            
        Returns:
            Dictionary with property categories (Physical, Optical, etc.)
            Each property has: {value, unit, min, max, confidence}
            
        Raises:
            ValueError: If category not found or data invalid
        """
        self.logger.info(f"Generating properties for {material_name}")
        
        # Get category
        category = material_data.get('category', '').lower()
        if not category:
            raise ValueError(f"Category missing for {material_name}")
        
        # Get properties from material data
        if 'materialProperties' not in material_data:
            self.logger.warning(f"No materialProperties for {material_name}")
            return {}
        
        properties = material_data['materialProperties']
        
        # Apply ranges from Categories.yaml
        properties_with_ranges = self._apply_ranges(
            properties, 
            category, 
            material_name
        )
        
        self.logger.info(f"✅ Generated properties for {material_name}")
        return properties_with_ranges
    
    def _apply_ranges(
        self, 
        properties: Dict, 
        category: str, 
        material_name: str
    ) -> Dict:
        """
        Apply min/max ranges from Categories.yaml
        
        Data Architecture Rule:
        - Min/max ONLY from Categories.yaml
        - NEVER from Materials.yaml
        - Fail-fast if category not defined
        """
        # Get category ranges
        categories = self.categories_data.get('categories', {})
        
        if category not in categories:
            raise ValueError(
                f"Category '{category}' not defined in Categories.yaml "
                f"(material: {material_name})"
            )
        
        category_props = categories[category].get('materialProperties', {})
        
        # Apply ranges to each property
        result = {}
        
        for prop_category, props_dict in properties.items():
            result[prop_category] = {}
            
            # Handle dict properties
            if not isinstance(props_dict, dict):
                # Non-dict value at category level - copy as-is
                result[prop_category] = props_dict
                continue
            
            for prop_name, prop_value in props_dict.items():
                # Handle non-dict property values (strings, floats, etc.)
                if not isinstance(prop_value, dict):
                    # Convert simple values to dict format
                    if isinstance(prop_value, (int, float)):
                        result[prop_category][prop_name] = {
                            'value': prop_value,
                            'unit': '',
                            'confidence': 1.0
                        }
                    else:
                        # Strings, etc. - copy as-is
                        result[prop_category][prop_name] = prop_value
                    continue
                
                # Get range from Categories.yaml
                if prop_name in category_props:
                    range_data = category_props[prop_name]
                    
                    # Build property with ranges
                    result[prop_category][prop_name] = {
                        'value': prop_value.get('value'),
                        'unit': prop_value.get('unit', ''),
                        'min': range_data.get('min'),
                        'max': range_data.get('max'),
                        'confidence': prop_value.get('confidence', 1.0)
                    }
                else:
                    # Property not in category ranges - copy as-is
                    # This handles custom properties gracefully
                    result[prop_category][prop_name] = prop_value
                    
                    self.logger.debug(
                        f"Property '{prop_name}' not in category ranges, "
                        f"using value as-is"
                    )
        
        return result


# Backward compatibility
class PropertiesGenerator(PropertiesModule):
    """Alias for backward compatibility"""
    pass
