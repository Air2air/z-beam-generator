"""
Property Access Helpers

Simplifies access to nested and pattern-specific properties in Materials.yaml
while preserving the sophisticated multi-pattern architecture.

Supports 4 property patterns:
1. Simple: {value: 123, unit: 'GPa'}
2. Nested: {point: {value: 1357, unit: 'K'}, type: 'melting'}
3. Pulse-specific: {nanosecond: {min: 2.0, max: 8.0, unit: 'J/cm²'}}
4. Wavelength-specific: {at_1064nm: {min: 85, max: 98, unit: '%'}}

Usage:
    from utils.property_helpers import PropertyAccessor
    
    # Simple property access
    value = PropertyAccessor.get_value(material['properties']['density'])
    
    # Nested thermal destruction
    temp = PropertyAccessor.get_thermal_destruction_point(material)
    
    # Pulse-specific ablation
    threshold = PropertyAccessor.get_value(
        material['properties']['ablationThreshold'],
        pulse_type='femtosecond'
    )
    
    # Category range access
    range_data = PropertyAccessor.get_category_range(
        categories_data, 'metal', 'density'
    )
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path


class PropertyAccessor:
    """Helper methods for accessing material properties with pattern awareness"""
    
    # Pulse duration types for ablation threshold
    PULSE_TYPES = ['nanosecond', 'picosecond', 'femtosecond']
    
    # Wavelength keys for reflectivity
    WAVELENGTH_KEYS = ['at_1064nm', 'at_532nm', 'at_355nm', 'at_10640nm']
    
    @staticmethod
    def get_value(prop_data: Any, 
                  pulse_type: str = 'nanosecond',
                  wavelength: str = '1064nm',
                  return_range: bool = False) -> Optional[float]:
        """
        Universal property value getter with pattern detection.
        
        Automatically detects and handles:
        - Simple values: {value: 123}
        - Nested structures: {point: {value: 123}}
        - Pulse-specific: {nanosecond: {min: 2.0, max: 8.0}}
        - Wavelength-specific: {at_1064nm: {min: 85, max: 98}}
        
        Args:
            prop_data: Property data dictionary or numeric value
            pulse_type: Pulse duration type ('nanosecond', 'picosecond', 'femtosecond')
            wavelength: Wavelength for reflectivity ('1064nm', '532nm', '355nm', '10640nm')
            return_range: If True, return (min, max) tuple for range-based properties
            
        Returns:
            Single numeric value (average if range), or None if not found
            If return_range=True, returns (min, max) tuple for range-based properties
        """
        # Direct numeric value
        if isinstance(prop_data, (int, float)):
            return float(prop_data)
        
        if not isinstance(prop_data, dict):
            return None
        
        # Direct value field
        if 'value' in prop_data:
            return float(prop_data['value'])
        
        # Nested point structure (thermalDestruction)
        if 'point' in prop_data and isinstance(prop_data['point'], dict):
            point_data = prop_data['point']
            if 'value' in point_data:
                return float(point_data['value'])
        
        # Pulse-specific (ablationThreshold)
        if pulse_type in prop_data:
            pulse_data = prop_data[pulse_type]
            if isinstance(pulse_data, dict):
                min_val = pulse_data.get('min')
                max_val = pulse_data.get('max')
                if return_range and min_val is not None and max_val is not None:
                    return (float(min_val), float(max_val))
                if min_val is not None and max_val is not None:
                    return (float(min_val) + float(max_val)) / 2
                return float(min_val or max_val or 0)
        
        # Wavelength-specific (reflectivity)
        wl_key = f'at_{wavelength}'
        if wl_key in prop_data:
            wl_data = prop_data[wl_key]
            if isinstance(wl_data, dict):
                min_val = wl_data.get('min')
                max_val = wl_data.get('max')
                if return_range and min_val is not None and max_val is not None:
                    return (float(min_val), float(max_val))
                if min_val is not None and max_val is not None:
                    return (float(min_val) + float(max_val)) / 2
                return float(min_val or max_val or 0)
        
        # Fallback to min/max average
        min_val = prop_data.get('min')
        max_val = prop_data.get('max')
        if return_range and min_val is not None and max_val is not None:
            return (float(min_val), float(max_val))
        if min_val is not None and max_val is not None:
            return (float(min_val) + float(max_val)) / 2
        
        return None
    
    @staticmethod
    def get_thermal_destruction_point(material: Dict) -> Optional[float]:
        """
        Get thermalDestruction.point.value safely.
        
        Args:
            material: Material data dictionary
            
        Returns:
            Thermal destruction temperature in K, or None
            
        Example:
            >>> temp = PropertyAccessor.get_thermal_destruction_point(copper)
            >>> print(f"Melting point: {temp} K")
        """
        try:
            return float(material['properties']['thermalDestruction']['point']['value'])
        except (KeyError, TypeError, ValueError):
            return None
    
    @staticmethod
    def get_thermal_destruction_type(material: Dict) -> Optional[str]:
        """
        Get thermalDestruction.type safely.
        
        Args:
            material: Material data dictionary
            
        Returns:
            Destruction type ('melting', 'thermal_shock', 'carbonization', etc.)
            
        Example:
            >>> dtype = PropertyAccessor.get_thermal_destruction_type(copper)
            >>> print(f"Destruction mechanism: {dtype}")
        """
        try:
            return material['properties']['thermalDestruction']['type']
        except (KeyError, TypeError):
            return None
    
    @staticmethod
    def get_ablation_threshold(material: Dict, 
                               pulse_type: str = 'nanosecond',
                               return_range: bool = False) -> Optional[Any]:
        """
        Get ablation threshold for specific pulse duration.
        
        Args:
            material: Material data dictionary
            pulse_type: Pulse duration ('nanosecond', 'picosecond', 'femtosecond')
            return_range: If True, return (min, max) tuple
            
        Returns:
            Threshold value in J/cm², (min, max) tuple if return_range=True, or None
            
        Example:
            >>> threshold = PropertyAccessor.get_ablation_threshold(steel, 'femtosecond')
            >>> print(f"Femtosecond ablation: {threshold} J/cm²")
        """
        try:
            ablation_data = material['properties']['ablationThreshold']
            return PropertyAccessor.get_value(
                ablation_data, 
                pulse_type=pulse_type,
                return_range=return_range
            )
        except (KeyError, TypeError):
            return None
    
    @staticmethod
    def get_reflectivity(material: Dict,
                        wavelength: str = '1064nm',
                        return_range: bool = False) -> Optional[Any]:
        """
        Get reflectivity for specific wavelength.
        
        Args:
            material: Material data dictionary
            wavelength: Wavelength ('1064nm', '532nm', '355nm', '10640nm')
            return_range: If True, return (min, max) tuple
            
        Returns:
            Reflectivity percentage, (min, max) tuple if return_range=True, or None
            
        Example:
            >>> refl = PropertyAccessor.get_reflectivity(aluminum, '532nm')
            >>> print(f"Green laser reflectivity: {refl}%")
        """
        try:
            refl_data = material['properties']['reflectivity']
            return PropertyAccessor.get_value(
                refl_data,
                wavelength=wavelength,
                return_range=return_range
            )
        except (KeyError, TypeError):
            return None
    
    @staticmethod
    def get_category_range(categories: Dict, 
                          category: str, 
                          property_name: str) -> Optional[Dict]:
        """
        Get category range for a property with nested support.
        
        Args:
            categories: Categories data dictionary
            category: Category name (case-insensitive)
            property_name: Property name
            
        Returns:
            Dictionary with min, max, unit, or None
            
        Example:
            >>> range_data = PropertyAccessor.get_category_range(
            ...     categories, 'metal', 'density'
            ... )
            >>> print(f"Metal density range: {range_data['min']}-{range_data['max']} {range_data['unit']}")
        """
        try:
            cat_data = categories.get('categories', categories)
            
            # Find category (case-insensitive)
            cat_ranges = None
            for cat_name, cat_info in cat_data.items():
                if cat_name.lower() == category.lower():
                    cat_ranges = cat_info.get('category_ranges', {})
                    break
            
            if not cat_ranges:
                return None
            
            range_data = cat_ranges.get(property_name)
            
            # Handle nested thermalDestruction
            if property_name == 'thermalDestruction' and isinstance(range_data, dict):
                if 'point' in range_data:
                    return range_data['point']
            
            return range_data
        except (KeyError, TypeError, AttributeError):
            return None
    
    @staticmethod
    def detect_property_pattern(prop_data: Any) -> str:
        """
        Detect which property pattern is used.
        
        Args:
            prop_data: Property data dictionary
            
        Returns:
            Pattern type: 'pulse-specific', 'wavelength-specific', 'nested', 
                         'simple', or 'unknown'
            
        Example:
            >>> pattern = PropertyAccessor.detect_property_pattern(
            ...     material['properties']['ablationThreshold']
            ... )
            >>> print(f"Pattern type: {pattern}")
        """
        if not isinstance(prop_data, dict):
            return 'simple'
        
        # Check for pulse-specific
        if any(pulse in prop_data for pulse in PropertyAccessor.PULSE_TYPES):
            return 'pulse-specific'
        
        # Check for wavelength-specific
        if any(wl in prop_data for wl in PropertyAccessor.WAVELENGTH_KEYS):
            return 'wavelength-specific'
        
        # Check for nested structure
        if 'point' in prop_data and isinstance(prop_data['point'], dict):
            return 'nested'
        
        # Check for simple value
        if 'value' in prop_data:
            return 'simple'
        
        return 'unknown'
    
    @staticmethod
    def get_property_safely(material: Dict, property_name: str, **kwargs) -> Optional[Any]:
        """
        Get any property value safely with automatic pattern detection.
        
        Args:
            material: Material data dictionary
            property_name: Property name to retrieve
            **kwargs: Additional arguments for get_value (pulse_type, wavelength, return_range)
            
        Returns:
            Property value or None
            
        Example:
            >>> density = PropertyAccessor.get_property_safely(copper, 'density')
            >>> temp = PropertyAccessor.get_property_safely(copper, 'thermalDestruction')
        """
        try:
            prop_data = material['properties'].get(property_name)
            if prop_data is None:
                return None
            
            # Special handling for thermalDestruction
            if property_name == 'thermalDestruction':
                return PropertyAccessor.get_thermal_destruction_point(material)
            
            return PropertyAccessor.get_value(prop_data, **kwargs)
        except (KeyError, TypeError):
            return None
    
    @staticmethod
    def get_all_property_values(material: Dict, 
                               pulse_type: str = 'nanosecond',
                               wavelength: str = '1064nm') -> Dict[str, Any]:
        """
        Get all property values from a material as a flat dictionary.
        
        Args:
            material: Material data dictionary
            pulse_type: Default pulse type for ablation
            wavelength: Default wavelength for reflectivity
            
        Returns:
            Dictionary mapping property names to values
            
        Example:
            >>> values = PropertyAccessor.get_all_property_values(copper)
            >>> for prop, val in values.items():
            ...     print(f"{prop}: {val}")
        """
        result = {}
        properties = material.get('properties', {})
        
        for prop_name, prop_data in properties.items():
            value = PropertyAccessor.get_value(
                prop_data,
                pulse_type=pulse_type,
                wavelength=wavelength
            )
            if value is not None:
                result[prop_name] = value
        
        return result


class CategoryHelper:
    """Helper methods for working with category data"""
    
    @staticmethod
    def get_all_categories(categories_data: Dict) -> List[str]:
        """Get list of all category names"""
        cat_data = categories_data.get('categories', categories_data)
        return list(cat_data.keys())
    
    @staticmethod
    def get_category_info(categories_data: Dict, category: str) -> Optional[Dict]:
        """Get full category information"""
        cat_data = categories_data.get('categories', categories_data)
        for cat_name, cat_info in cat_data.items():
            if cat_name.lower() == category.lower():
                return cat_info
        return None
    
    @staticmethod
    def get_all_properties_in_category(categories_data: Dict, 
                                      category: str) -> List[str]:
        """Get list of all properties defined for a category"""
        cat_info = CategoryHelper.get_category_info(categories_data, category)
        if cat_info and 'category_ranges' in cat_info:
            return list(cat_info['category_ranges'].keys())
        return []
    
    @staticmethod
    def is_value_in_range(value: Any, min_val: Any, max_val: Any) -> bool:
        """
        Check if a value falls within min/max range.
        
        Args:
            value: Value to check
            min_val: Minimum allowed value (None = no minimum)
            max_val: Maximum allowed value (None = no maximum)
            
        Returns:
            True if value is in range, False otherwise
            
        Example:
            >>> in_range = CategoryHelper.is_value_in_range(8.96, 0.53, 22.6)
            >>> print(f"Copper density in metal range: {in_range}")
        """
        if value is None:
            return True  # Null values are acceptable
        
        if min_val is None and max_val is None:
            return True  # No range defined
        
        try:
            num_value = float(value)
            if min_val is not None:
                if num_value < float(min_val):
                    return False
            if max_val is not None:
                if num_value > float(max_val):
                    return False
            return True
        except (ValueError, TypeError):
            return True  # Can't validate non-numeric


# Convenience functions for common operations
def get_material_property(material: Dict, property_name: str, **kwargs) -> Optional[Any]:
    """Shortcut for PropertyAccessor.get_property_safely"""
    return PropertyAccessor.get_property_safely(material, property_name, **kwargs)


def get_category_range(categories: Dict, category: str, property_name: str) -> Optional[Dict]:
    """Shortcut for PropertyAccessor.get_category_range"""
    return PropertyAccessor.get_category_range(categories, category, property_name)


def is_in_range(value: Any, min_val: Any, max_val: Any) -> bool:
    """Shortcut for CategoryHelper.is_value_in_range"""
    return CategoryHelper.is_value_in_range(value, min_val, max_val)
