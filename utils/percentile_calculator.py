"""
Percentile calculation utilities for material properties.
Calculates where a property value sits within its category min/max range.
"""

import re
from typing import Union


def extract_numeric_value(value_str: str) -> float:
    """
    Extract numeric value from property strings like '2.3 g/cm³', '800 HV', '200 GPa'
    
    Args:
        value_str: String containing numeric value with units
        
    Returns:
        Extracted numeric value as float
    """
    if not value_str or value_str.upper() in ['N/A', 'NA', 'NULL', '']:
        return 0.0
    
    # Handle range values like "50-100 MPa" - take the average
    range_match = re.search(r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)', str(value_str))
    if range_match:
        min_val = float(range_match.group(1))
        max_val = float(range_match.group(2))
        return (min_val + max_val) / 2
    
    # Handle scientific notation and decimal values
    # Support units like: cm⁻¹, mm²/s, µm/m·K, J/g·K, %, etc.
    numeric_match = re.search(r'(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)', str(value_str))
    if numeric_match:
        return float(numeric_match.group(1))
    
    return 0.0


def calculate_percentile(value: Union[str, float], min_value: Union[str, float], max_value: Union[str, float]) -> float:
    """
    Calculate where a value sits within a min/max range as a percentage.
    
    Args:
        value: The actual property value (e.g., "2.3 g/cm³")
        min_value: Minimum value in category range (e.g., "1.8 g/cm³")
        max_value: Maximum value in category range (e.g., "6.0 g/cm³")
        
    Returns:
        Percentage (0-100) where the value sits within the range
        
    Examples:
        >>> calculate_percentile("2.3 g/cm³", "1.8 g/cm³", "6.0 g/cm³")
        11.9  # (2.3-1.8)/(6.0-1.8) * 100 = 11.9%
        
        >>> calculate_percentile("800 HV", "500 HV", "2500 HV")
        15.0  # (800-500)/(2500-500) * 100 = 15%
    """
    # Extract numeric values
    val = extract_numeric_value(value)
    min_val = extract_numeric_value(min_value)
    max_val = extract_numeric_value(max_value)
    
    # Handle edge cases
    if min_val == max_val:
        return 50.0  # Middle of range if no variation
    
    if val <= min_val:
        return 0.0
    
    if val >= max_val:
        return 100.0
    
    # Calculate percentile
    percentile = ((val - min_val) / (max_val - min_val)) * 100
    
    # Round to 1 decimal place
    return round(percentile, 1)


def calculate_property_percentiles(properties: dict, category_ranges: dict, category: str) -> dict:
    """
    Calculate percentiles for all properties that have min/max ranges.
    
    Args:
        properties: Dictionary containing property values
        category_ranges: Dictionary containing category range data
        category: Material category (e.g., 'metal', 'ceramic')
        
    Returns:
        Updated properties dictionary with percentile fields added
    """
    if not category_ranges or category not in category_ranges:
        return properties

    # Property mappings: (value_key, min_key, max_key, percentile_key)
    property_mappings = [
        # Original 6 properties
        ('density', 'densityMin', 'densityMax', 'densityPercentile'),
        ('meltingPoint', 'meltingMin', 'meltingMax', 'meltingPercentile'),
        ('thermalConductivity', 'thermalMin', 'thermalMax', 'thermalPercentile'),
        ('tensileStrength', 'tensileMin', 'tensileMax', 'tensilePercentile'),
        ('hardness', 'hardnessMin', 'hardnessMax', 'hardnessPercentile'),
        ('youngsModulus', 'modulusMin', 'modulusMax', 'modulusPercentile'),
        
        # Phase 1 & 2: Laser-specific and thermal properties
        ('laserAbsorption', 'laserAbsorptionMin', 'laserAbsorptionMax', 'laserAbsorptionPercentile'),
        ('laserReflectivity', 'laserReflectivityMin', 'laserReflectivityMax', 'laserReflectivityPercentile'),
        ('thermalDiffusivity', 'thermalDiffusivityMin', 'thermalDiffusivityMax', 'thermalDiffusivityPercentile'),
        ('thermalExpansion', 'thermalExpansionMin', 'thermalExpansionMax', 'thermalExpansionPercentile'),
        ('specificHeat', 'specificHeatMin', 'specificHeatMax', 'specificHeatPercentile'),
    ]
    
    for value_key, min_key, max_key, percentile_key in property_mappings:
        # Check if we have all required values
        if (value_key in properties and 
            min_key in properties and 
            max_key in properties):
            
            value = properties[value_key]
            min_val = properties[min_key]
            max_val = properties[max_key]
            
            # Calculate percentile
            percentile = calculate_percentile(value, min_val, max_val)
            properties[percentile_key] = percentile
    
    return properties


# Test the functions if run directly
if __name__ == "__main__":
    # Test numeric extraction
    test_cases = [
        ("2.3 g/cm³", 2.3),
        ("800 HV", 800.0),
        ("50-100 MPa", 75.0),
        ("1200°C", 1200.0),
        ("N/A", 0.0),
        ("150 GPa", 150.0),
        # New units for laser and thermal properties
        ("0.02 cm⁻¹", 0.02),
        ("98%", 98.0),
        ("174 mm²/s", 174.0),
        ("29 µm/m·K", 29.0),
        ("0.90 J/g·K", 0.90),
        ("1.5e-3 cm⁻¹", 1.5e-3)
    ]
    
    print("Testing numeric extraction:")
    for input_val, expected in test_cases:
        result = extract_numeric_value(input_val)
        print(f"  {input_val} -> {result} (expected: {expected})")
    
    print("\nTesting percentile calculation:")
    # Test percentile calculation
    percentile_tests = [
        ("2.3 g/cm³", "1.8 g/cm³", "6.0 g/cm³", 11.9),
        ("800 HV", "500 HV", "2500 HV", 15.0),
        ("200 GPa", "150 GPa", "400 GPa", 20.0)
    ]
    
    for value, min_val, max_val, expected in percentile_tests:
        result = calculate_percentile(value, min_val, max_val)
        print(f"  {value} in range [{min_val}, {max_val}] = {result}% (expected: {expected}%)")
