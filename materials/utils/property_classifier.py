"""Property Classification System

Automated property classification based on property_system.yaml registry.
Eliminates manual classification, reduces errors, ensures consistency.

Usage:
    from materials.utils.property_classifier import PropertyClassifier
    
    classifier = PropertyClassifier()
    
    # Check if property is qualitative
    if classifier.is_qualitative('crystallineStructure'):
        # Handle as qualitative
    
    # Get property metadata
    info = classifier.get_property_info('density')
    print(info['type'])  # 'quantitative'
    print(info['typical_units'])  # ['g/cm³', 'kg/m³']
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class PropertyInfo:
    """Property metadata from registry"""
    name: str
    type: str  # 'quantitative', 'qualitative', 'quantitative_nested'
    category: str
    unit_required: bool
    range_required: bool
    typical_units: List[str] = None
    allowed_values: List[str] = None
    description: str = ""
    measurement_context: str = ""
    nested_structure: bool = False
    fields: Dict[str, Any] = None


class PropertyClassifier:
    """Automated property classification from registry"""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize classifier with property registry.
        
        Args:
            registry_path: Path to property_system.yaml (auto-detects if None)
        """
        if registry_path is None:
            # Auto-detect from project structure
            registry_path = Path(__file__).parent.parent / 'data' / 'categories' / 'property_system.yaml'
        
        if not registry_path.exists():
            raise FileNotFoundError(f"Property registry not found: {registry_path}")
        
        with open(registry_path, 'r', encoding='utf-8') as f:
            self.registry = yaml.safe_load(f)
        
        self.properties = self.registry.get('propertyDefinitions', {})
        self.rules = self.registry.get('classificationRules', {})
        self.mappings = self.registry.get('legacyPropertyMappings', {})
    
    def is_qualitative(self, property_name: str) -> bool:
        """
        Check if property is qualitative (descriptive, no numerical range).
        
        Args:
            property_name: Name of the property
            
        Returns:
            True if qualitative, False if quantitative
        """
        prop_info = self.properties.get(property_name, {})
        return prop_info.get('type') == 'qualitative'
    
    def is_quantitative(self, property_name: str) -> bool:
        """
        Check if property is quantitative (numerical with ranges).
        
        Args:
            property_name: Name of the property
            
        Returns:
            True if quantitative, False if qualitative
        """
        prop_info = self.properties.get(property_name, {})
        prop_type = prop_info.get('type', '')
        return prop_type in ['quantitative', 'quantitative_nested']
    
    def requires_range(self, property_name: str) -> bool:
        """
        Check if property requires min/max range values.
        
        Args:
            property_name: Name of the property
            
        Returns:
            True if ranges required, False otherwise
        """
        prop_info = self.properties.get(property_name, {})
        return prop_info.get('range_required', False)
    
    def requires_unit(self, property_name: str) -> bool:
        """
        Check if property requires unit specification.
        
        Args:
            property_name: Name of the property
            
        Returns:
            True if unit required, False otherwise
        """
        prop_info = self.properties.get(property_name, {})
        return prop_info.get('unit_required', False)
    
    def get_property_info(self, property_name: str) -> Optional[PropertyInfo]:
        """
        Get complete property metadata.
        
        Args:
            property_name: Name of the property
            
        Returns:
            PropertyInfo object or None if not found
        """
        prop_data = self.properties.get(property_name)
        if not prop_data:
            return None
        
        return PropertyInfo(
            name=property_name,
            type=prop_data.get('type', 'quantitative'),
            category=prop_data.get('category', 'unknown'),
            unit_required=prop_data.get('unit_required', True),
            range_required=prop_data.get('range_required', True),
            typical_units=prop_data.get('typical_units', []),
            allowed_values=prop_data.get('allowed_values', []),
            description=prop_data.get('description', ''),
            measurement_context=prop_data.get('measurement_context', ''),
            nested_structure=prop_data.get('nested_structure', False),
            fields=prop_data.get('fields', {})
        )
    
    def get_frontmatter_section(self, property_name: str) -> str:
        """
        Determine which frontmatter section property belongs in.
        
        Args:
            property_name: Name of the property
            
        Returns:
            'materialProperties' or 'materialCharacteristics'
        """
        prop_info = self.properties.get(property_name, {})
        prop_type = prop_info.get('type', 'quantitative')
        
        if prop_type == 'qualitative':
            return 'materialCharacteristics'
        return 'materialProperties'
    
    def validate_property_value(self, property_name: str, value: Any) -> bool:
        """
        Validate property value against allowed values (for qualitative).
        
        Args:
            property_name: Name of the property
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        prop_info = self.properties.get(property_name, {})
        
        # Quantitative properties - just check if numeric
        if prop_info.get('type') in ['quantitative', 'quantitative_nested']:
            return isinstance(value, (int, float))
        
        # Qualitative properties - check against allowed values
        allowed = prop_info.get('allowed_values', [])
        if not allowed:
            # No restrictions - any string value allowed
            return isinstance(value, str)
        
        return value in allowed
    
    def get_legacy_mapping(self, old_property_name: str) -> Optional[Dict[str, str]]:
        """
        Get migration info for legacy property names.
        
        Args:
            old_property_name: Old property name
            
        Returns:
            Dict with new_property, new_type, migration_note
        """
        return self.mappings.get(old_property_name)
    
    def list_properties_by_type(self, prop_type: str) -> List[str]:
        """
        List all properties of a given type.
        
        Args:
            prop_type: 'quantitative', 'qualitative', or 'quantitative_nested'
            
        Returns:
            List of property names
        """
        return [
            name for name, info in self.properties.items()
            if info.get('type') == prop_type
        ]
    
    def list_properties_by_category(self, category: str) -> List[str]:
        """
        List all properties in a category.
        
        Args:
            category: Category name (thermal, mechanical, optical_laser, etc.)
            
        Returns:
            List of property names
        """
        return [
            name for name, info in self.properties.items()
            if info.get('category') == category
        ]


# Global classifier instance for convenience
_classifier_instance = None

def get_classifier() -> PropertyClassifier:
    """Get global PropertyClassifier instance (singleton)"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = PropertyClassifier()
    return _classifier_instance
