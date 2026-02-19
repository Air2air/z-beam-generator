"""
Scale Mapper Utility
====================

Provides consistent normalization of integer slider values (1-10 scale) 
to decimal factors (0.0-1.0 range) for use in dynamic parameter calculations.

All sliders in the system use a 1-10 integer scale where:
- 1 = minimum (maps to 0.0)
- 10 = maximum (maps to 1.0)

This utility ensures consistent mapping throughout the codebase.
"""

from typing import List


def normalize_slider(value: int, min_val: int = 1, max_val: int = 10) -> float:
    """
    Normalize a single slider value to 0.0-1.0 range.
    
    Args:
        value: Integer slider value (typically 1-10)
        min_val: Minimum slider value (default: 1)
        max_val: Maximum slider value (default: 10)
    
    Returns:
        Normalized float between 0.0 and 1.0
    
    Examples:
        >>> normalize_slider(1)   # Returns 0.0
        >>> normalize_slider(5)   # Returns 0.444...
        >>> normalize_slider(10)  # Returns 1.0
    """
    if value < min_val:
        value = min_val
    if value > max_val:
        value = max_val
    
    return (value - min_val) / (max_val - min_val)


def normalize_sliders(values: List[int], min_val: int = 1, max_val: int = 10) -> float:
    """
    Normalize multiple slider values to combined 0.0-1.0 factor.
    
    Takes the average of normalized individual sliders.
    
    Args:
        values: List of integer slider values
        min_val: Minimum slider value (default: 1)
        max_val: Maximum slider value (default: 10)
    
    Returns:
        Combined normalized float between 0.0 and 1.0
    
    Examples:
        >>> normalize_sliders([1, 1, 1])      # Returns 0.0
        >>> normalize_sliders([5, 5, 5])      # Returns 0.444...
        >>> normalize_sliders([10, 10, 10])   # Returns 1.0
        >>> normalize_sliders([8, 5, 8])      # Returns 0.630...
    """
    if not values:
        raise ValueError("normalize_sliders requires at least one slider value")
    
    normalized = [normalize_slider(v, min_val, max_val) for v in values]
    return sum(normalized) / len(normalized)


def map_to_range(factor: float, min_output: float, max_output: float) -> float:
    """
    Map a normalized factor (0.0-1.0) to a target output range.
    
    Args:
        factor: Normalized factor between 0.0 and 1.0
        min_output: Minimum output value
        max_output: Maximum output value
    
    Returns:
        Value scaled to output range
    
    Examples:
        >>> map_to_range(0.0, 0.3, 1.0)   # Returns 0.3
        >>> map_to_range(0.5, 0.3, 1.0)   # Returns 0.65
        >>> map_to_range(1.0, 0.3, 1.0)   # Returns 1.0
        >>> map_to_range(0.7, 0.0, 2.0)   # Returns 1.4
    """
    return min_output + (factor * (max_output - min_output))


def slider_to_range(value: int, min_output: float, max_output: float, 
                    min_val: int = 1, max_val: int = 10) -> float:
    """
    Direct mapping from slider value to output range (convenience function).
    
    Combines normalize_slider() and map_to_range() in one call.
    
    Args:
        value: Integer slider value
        min_output: Minimum output value
        max_output: Maximum output value
        min_val: Minimum slider value (default: 1)
        max_val: Maximum slider value (default: 10)
    
    Returns:
        Value scaled to output range
    
    Examples:
        >>> slider_to_range(1, 0.3, 1.0)    # Returns 0.3 (min temp)
        >>> slider_to_range(10, 0.3, 1.0)   # Returns 1.0 (max temp)
        >>> slider_to_range(5, 0.0, 2.0)    # Returns ~0.89 (mid penalty)
    """
    factor = normalize_slider(value, min_val, max_val)
    return map_to_range(factor, min_output, max_output)


def sliders_to_range(values: List[int], min_output: float, max_output: float,
                     min_val: int = 1, max_val: int = 10) -> float:
    """
    Direct mapping from multiple sliders to output range (convenience function).
    
    Combines normalize_sliders() and map_to_range() in one call.
    
    Args:
        values: List of integer slider values
        min_output: Minimum output value
        max_output: Maximum output value
        min_val: Minimum slider value (default: 1)
        max_val: Maximum slider value (default: 10)
    
    Returns:
        Value scaled to output range
    
    Examples:
        >>> sliders_to_range([8, 5, 8], 0.0, 2.0)   # Returns ~1.26 (combined penalty)
        >>> sliders_to_range([1, 1, 1], 0.3, 1.0)   # Returns 0.3 (min temp)
    """
    factor = normalize_sliders(values, min_val, max_val)
    return map_to_range(factor, min_output, max_output)


# Convenience functions for common use cases

def penalty_from_sliders(values: List[int]) -> float:
    """
    Calculate API penalty (0.0-2.0) from slider values.
    
    Common use case for frequency_penalty and presence_penalty.
    
    Args:
        values: List of slider values (1-10 scale)
    
    Returns:
        Penalty value between 0.0 and 2.0
    """
    return sliders_to_range(values, 0.0, 2.0)


def temperature_from_sliders(values: List[int]) -> float:
    """
    Calculate temperature (0.3-1.0) from slider values.
    
    Common use case for API temperature parameter.
    
    Args:
        values: List of slider values (1-10 scale)
    
    Returns:
        Temperature value between 0.3 and 1.0
    """
    return sliders_to_range(values, 0.3, 1.0)
