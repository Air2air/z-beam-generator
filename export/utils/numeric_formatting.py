"""
Numeric Formatting Utilities

Provides consistent, readable numeric formatting for frontmatter exports.
See: docs/08-development/NUMERIC_FORMATTING_POLICY.md

Created: November 29, 2025
"""

from typing import Union, Optional


def format_numeric_value(value: Optional[float], unit: str = '') -> Optional[Union[int, float, str]]:
    """
    Format numeric value for human readability.
    
    Rules:
    - Very small (< 0.01): Scientific notation with 2 sig figs
    - Small (0.01-0.99): 2 decimal places max
    - Near whole (1-999): Whole or 1 decimal
    - Large (1000-999999): Whole numbers
    - Very large (≥ 1M): Scientific notation with 2 sig figs
    
    Args:
        value: Raw numeric value (can be None)
        unit: Unit string (for context, not currently used)
    
    Returns:
        Formatted value (int, float, or scientific notation string)
        Returns None if input is None
    
    Examples:
        >>> format_numeric_value(2.65e-08)
        '2.7e-08'
        >>> format_numeric_value(0.2744)
        0.27
        >>> format_numeric_value(933.47)
        933
        >>> format_numeric_value(37700000.0)
        '3.8e+07'
    """
    if value is None:
        return None
    
    # Handle non-numeric values
    if not isinstance(value, (int, float)):
        return value
    
    # Handle zero explicitly
    if value == 0:
        return 0
    
    abs_val = abs(value)
    
    # Rule 1: Very small numbers (< 0.01) - scientific notation
    if abs_val < 0.01 and abs_val > 0:
        # Use 2 significant figures
        formatted = f"{value:.2g}"
        return formatted
    
    # Rule 5: Very large numbers (≥ 1,000,000) - scientific notation
    if abs_val >= 1_000_000:
        # Use 2 significant figures
        formatted = f"{value:.2g}"
        return formatted
    
    # Rule 2: Small numbers (0.01 to 0.99) - 2 decimal places max
    if abs_val < 1:
        rounded = round(value, 2)
        # Return int if it's a whole number after rounding
        if rounded == int(rounded):
            return int(rounded)
        return rounded
    
    # Rule 3: Numbers 1 to 999 - whole or 1 decimal
    if abs_val < 1000:
        # For values >= 100, round to whole number (cleaner)
        if abs_val >= 100:
            return int(round(value))
        # For values 1-99, keep 1 decimal if meaningful
        rounded = round(value, 1)
        if rounded == int(rounded):
            return int(rounded)
        return rounded
    
    # Rule 4: Large numbers (1000 to 999999) - whole numbers
    return int(round(value))


def format_property_dict(prop_data: dict) -> dict:
    """
    Format all numeric values in a property dictionary.
    
    Applies formatting to 'value', 'min', and 'max' fields while
    preserving other fields like 'unit', 'description', etc.
    
    Args:
        prop_data: Property dictionary with potential numeric values
    
    Returns:
        Dictionary with formatted numeric values
    """
    if not isinstance(prop_data, dict):
        return prop_data
    
    formatted = prop_data.copy()
    
    # Format numeric fields
    for field in ['value', 'min', 'max']:
        if field in formatted and isinstance(formatted[field], (int, float)):
            formatted[field] = format_numeric_value(
                formatted[field], 
                formatted.get('unit', '')
            )
    
    return formatted


def format_machine_settings(settings: dict) -> dict:
    """
    Format all numeric values in machine settings.
    
    Args:
        settings: Machine settings dictionary with parameter subdicts
    
    Returns:
        Dictionary with all numeric values formatted
    """
    if not isinstance(settings, dict):
        return settings
    
    formatted = {}
    for param_name, param_data in settings.items():
        if isinstance(param_data, dict):
            formatted[param_name] = format_property_dict(param_data)
        else:
            formatted[param_name] = param_data
    
    return formatted


def format_material_properties(properties: dict) -> dict:
    """
    Format all numeric values in material properties.
    
    Handles nested structure: properties > categories > individual props
    
    Args:
        properties: Material properties dictionary (may be nested)
    
    Returns:
        Dictionary with all numeric values formatted
    """
    if not isinstance(properties, dict):
        return properties
    
    formatted = {}
    for key, value in properties.items():
        if isinstance(value, dict):
            # Check if this is a property dict (has 'value' field)
            if 'value' in value:
                formatted[key] = format_property_dict(value)
            else:
                # Nested category - recurse
                formatted[key] = format_material_properties(value)
        else:
            formatted[key] = value
    
    return formatted


# Convenience function for testing
def preview_formatting(value: float) -> str:
    """
    Preview how a value will be formatted.
    
    Args:
        value: Numeric value to format
    
    Returns:
        String showing before and after
    """
    formatted = format_numeric_value(value)
    return f"{value!r} → {formatted!r}"
