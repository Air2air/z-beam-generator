#!/usr/bin/env python3
"""
Laser Property Helpers

Utility functions for laser-specific property operations:
- Value extraction from strings with wavelength context
- Unit normalization for laser properties
- Property type classification
- Physics validation (optical properties)
- Range parsing for fluence, scan speed, etc.

Author: Z-Beam Generator
Date: November 25, 2025
"""

import re
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def extract_wavelength_value(value_str: str) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """
    Extract numeric value, unit, and wavelength from laser property string.
    
    Examples:
        "0.85 at 1064nm" → (0.85, "dimensionless", "1064nm")
        "5.2 J/cm² (532nm)" → (5.2, "J/cm²", "532nm")
        "2500 W" → (2500.0, "W", None)
        "0.45 ± 0.05 at 355nm" → (0.45, "dimensionless", "355nm")
        "10-15 μm" → (12.5, "μm", None)  # midpoint of range
    
    Args:
        value_str: String containing value, optional unit, optional wavelength
    
    Returns:
        (value, unit, wavelength) tuple
        - value: Numeric value (None if cannot parse)
        - unit: Unit string (None if dimensionless)
        - wavelength: Wavelength string (None if not specified)
    """
    if not value_str or not isinstance(value_str, str):
        return (None, None, None)
    
    value_str = value_str.strip()
    
    # Extract wavelength if present
    wavelength = None
    wavelength_patterns = [
        r'\((\d+(?:\.\d+)?)\s*nm\)',  # (1064nm)
        r'at\s+(\d+(?:\.\d+)?)\s*nm',  # at 1064nm
        r'@\s*(\d+(?:\.\d+)?)\s*nm'    # @1064nm
    ]
    
    for pattern in wavelength_patterns:
        match = re.search(pattern, value_str, re.IGNORECASE)
        if match:
            wavelength = f"{match.group(1)}nm"
            # Remove wavelength from string for value extraction
            value_str = re.sub(pattern, '', value_str, flags=re.IGNORECASE).strip()
            break
    
    # Extract numeric value (handle ranges and uncertainties)
    value = None
    
    # Range: "10-15" or "10 - 15"
    range_match = re.search(r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)', value_str)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        value = (low + high) / 2.0  # Use midpoint
    else:
        # Uncertainty: "0.45 ± 0.05" or "0.45 +/- 0.05"
        uncertainty_match = re.search(r'(\d+(?:\.\d+)?)\s*[±+/-]+\s*\d+(?:\.\d+)?', value_str)
        if uncertainty_match:
            value = float(uncertainty_match.group(1))
        else:
            # Simple number: "0.85" or "2500"
            number_match = re.search(r'(\d+(?:\.\d+)?)', value_str)
            if number_match:
                value = float(number_match.group(1))
    
    # Extract unit (everything after the number that's not wavelength)
    unit = None
    if value is not None:
        # Remove the number from string
        remaining = re.sub(r'\d+(?:\.\d+)?', '', value_str, count=1).strip()
        # Remove uncertainty notation
        remaining = re.sub(r'[±+/-]+\s*\d+(?:\.\d+)?', '', remaining).strip()
        
        if remaining:
            # Clean up common unit patterns
            remaining = remaining.replace('at', '').replace('(', '').replace(')', '').strip()
            if remaining:
                unit = remaining
    
    # Default to dimensionless if no unit found
    if unit is None and value is not None:
        unit = "dimensionless"
    
    return (value, unit, wavelength)


def normalize_laser_unit(unit: str, property_type: str) -> str:
    """
    Normalize laser-specific units to standard forms.
    
    Property types: optical, thermal, energy, power, speed, length, temperature
    
    Examples:
        unit="mJ/cm2", property_type="energy" → "J/cm²"
        unit="watts", property_type="power" → "W"
        unit="microns", property_type="length" → "μm"
        unit="deg C", property_type="temperature" → "°C"
    
    Args:
        unit: Unit string (possibly non-standard)
        property_type: Type of property for context
    
    Returns:
        Normalized unit string
    """
    if not unit:
        return "dimensionless"
    
    unit = unit.strip().lower()
    
    # Energy density (fluence)
    if property_type == "energy":
        if unit in ["mj/cm2", "mj/cm^2", "millijoules/cm2"]:
            return "J/cm²"
        if unit in ["j/cm2", "j/cm^2", "joules/cm2"]:
            return "J/cm²"
        if unit in ["j/m2", "j/m^2"]:
            return "J/m²"
    
    # Power
    elif property_type == "power":
        if unit in ["watts", "watt"]:
            return "W"
        if unit in ["kw", "kilowatts"]:
            return "kW"
        if unit in ["mw", "milliwatts"]:
            return "mW"
        if unit in ["w/cm2", "w/cm^2"]:
            return "W/cm²"
    
    # Speed
    elif property_type == "speed":
        if unit in ["mm/s", "mm/sec", "millimeters/second"]:
            return "mm/s"
        if unit in ["m/s", "m/sec", "meters/second"]:
            return "m/s"
        if unit in ["cm/s", "cm/sec"]:
            return "cm/s"
    
    # Length
    elif property_type == "length":
        if unit in ["microns", "micrometer", "micrometers", "um", "µm"]:
            return "μm"
        if unit in ["nm", "nanometers", "nanometer"]:
            return "nm"
        if unit in ["mm", "millimeters", "millimeter"]:
            return "mm"
    
    # Temperature
    elif property_type == "temperature":
        if unit in ["deg c", "degrees c", "celsius", "degc", "°c"]:
            return "°C"
        if unit in ["deg k", "degrees k", "kelvin", "k"]:
            return "K"
        if unit in ["deg f", "degrees f", "fahrenheit", "degf", "°f"]:
            return "°F"
    
    # Time
    elif property_type == "time":
        if unit in ["ns", "nanoseconds", "nanosecond"]:
            return "ns"
        if unit in ["ps", "picoseconds", "picosecond"]:
            return "ps"
        if unit in ["fs", "femtoseconds", "femtosecond"]:
            return "fs"
        if unit in ["µs", "us", "microseconds", "microsecond"]:
            return "μs"
    
    # If no match, return cleaned version
    return unit.replace("^2", "²").replace("deg", "°")


def classify_laser_property(prop_name: str) -> str:
    """
    Classify laser property by type.
    
    Returns: optical | thermal | removal | layer | parameter | safety | selectivity | unknown
    
    Examples:
        "absorption_coefficient" → "optical"
        "ablation_threshold" → "thermal"
        "removal_efficiency" → "removal"
        "fluence_range" → "parameter"
        "fume_composition" → "safety"
    
    Args:
        prop_name: Property name
    
    Returns:
        Property category string
    """
    prop_name = prop_name.lower().strip()
    
    # Optical properties
    OPTICAL_PROPERTIES = {
        'absorption_coefficient', 'absorption', 'absorptivity',
        'reflectivity', 'reflectance', 'reflection',
        'transmittance', 'transmission', 'transmissivity',
        'refractive_index', 'refraction',
        'extinction_coefficient', 'extinction',
        'penetration_depth', 'optical_depth'
    }
    
    # Thermal properties
    THERMAL_PROPERTIES = {
        'ablation_threshold', 'ablation_temp', 'ablation_temperature',
        'decomposition_temperature', 'decomposition_temp',
        'vaporization_temperature', 'vaporization_temp',
        'thermal_conductivity', 'thermal_diffusivity',
        'specific_heat_capacity', 'heat_capacity',
        'melting_point', 'melting_temperature',
        'thermal_expansion'
    }
    
    # Removal characteristics
    REMOVAL_PROPERTIES = {
        'removal_mechanism', 'removal_mode',
        'removal_efficiency', 'removal_rate',
        'surface_quality', 'surface_roughness',
        'byproducts', 'byproduct_composition',
        'cleaning_efficiency', 'ablation_rate'
    }
    
    # Layer properties
    LAYER_PROPERTIES = {
        'typical_thickness', 'thickness_range', 'layer_thickness',
        'adhesion_strength', 'adhesion',
        'hardness', 'layer_hardness',
        'porosity', 'layer_porosity'
    }
    
    # Laser parameters
    PARAMETER_PROPERTIES = {
        'recommended_wavelength', 'optimal_wavelength', 'wavelength',
        'fluence_range', 'fluence', 'energy_density',
        'scan_speed_range', 'scan_speed', 'scanning_speed',
        'pulse_duration', 'pulse_width',
        'repetition_rate', 'rep_rate', 'frequency',
        'spot_size', 'beam_diameter',
        'overlap_percentage', 'overlap', 'line_overlap',
        'number_of_passes', 'passes'
    }
    
    # Safety data
    SAFETY_PROPERTIES = {
        'fume_composition', 'fumes', 'vapor_composition',
        'exposure_limits', 'exposure_limit', 'osha_limit', 'pel', 'tlv',
        'ventilation_requirements', 'ventilation',
        'ppe_requirements', 'ppe', 'protective_equipment',
        'hazard_classification', 'hazard_class', 'ghs_classification'
    }
    
    # Selectivity ratios
    SELECTIVITY_PROPERTIES = {
        'selectivity_ratio', 'selectivity', 'absorption_ratio',
        'contrast_ratio', 'substrate_ratio'
    }
    
    # Check each category
    if any(keyword in prop_name for keyword in OPTICAL_PROPERTIES):
        return 'optical'
    elif any(keyword in prop_name for keyword in THERMAL_PROPERTIES):
        return 'thermal'
    elif any(keyword in prop_name for keyword in REMOVAL_PROPERTIES):
        return 'removal'
    elif any(keyword in prop_name for keyword in LAYER_PROPERTIES):
        return 'layer'
    elif any(keyword in prop_name for keyword in PARAMETER_PROPERTIES):
        return 'parameter'
    elif any(keyword in prop_name for keyword in SAFETY_PROPERTIES):
        return 'safety'
    elif any(keyword in prop_name for keyword in SELECTIVITY_PROPERTIES):
        return 'selectivity'
    else:
        return 'unknown'


def validate_optical_physics(optical_props: Dict[str, Any], tolerance: float = 0.05) -> Tuple[bool, str]:
    """
    Validate optical properties meet physics constraint: absorption + reflection + transmission ≈ 1.0
    
    Args:
        optical_props: Dictionary with 'absorption_coefficient', 'reflectivity', 'transmittance'
        tolerance: Allowed deviation (default 5%)
    
    Returns:
        (is_valid, error_message) tuple
    
    Examples:
        >>> props = {'absorption_coefficient': 0.7, 'reflectivity': 0.25, 'transmittance': 0.05}
        >>> validate_optical_physics(props)
        (True, "")
        
        >>> props = {'absorption_coefficient': 0.7, 'reflectivity': 0.5, 'transmittance': 0.1}
        >>> validate_optical_physics(props)
        (False, "Sum is 1.30 (should be 1.00 ± 0.05)")
    """
    # Extract values (handle nested structures)
    absorption = None
    reflection = None
    transmission = None
    
    # Handle both direct values and nested {'value': X} structures
    for key in ['absorption_coefficient', 'absorption', 'absorptivity']:
        if key in optical_props:
            val = optical_props[key]
            absorption = val.get('value', val) if isinstance(val, dict) else val
            break
    
    for key in ['reflectivity', 'reflectance', 'reflection']:
        if key in optical_props:
            val = optical_props[key]
            reflection = val.get('value', val) if isinstance(val, dict) else val
            break
    
    for key in ['transmittance', 'transmission', 'transmissivity']:
        if key in optical_props:
            val = optical_props[key]
            transmission = val.get('value', val) if isinstance(val, dict) else val
            break
    
    # Need at least 2 values to validate
    values = [v for v in [absorption, reflection, transmission] if v is not None]
    if len(values) < 2:
        return (True, "Insufficient data for validation")
    
    # Calculate sum
    total = sum(values)
    
    # Check constraint: total ≈ 1.0
    expected = 1.0
    if abs(total - expected) > tolerance:
        return (
            False,
            f"Sum is {total:.2f} (should be {expected:.2f} ± {tolerance:.2f})"
        )
    
    return (True, "")


def parse_fluence_range(fluence_str: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Parse fluence range string into min, max, unit.
    
    Examples:
        "0.5-5.0 J/cm²" → (0.5, 5.0, "J/cm²")
        "2-8 J/cm2" → (2.0, 8.0, "J/cm²")
        "5.2 J/cm²" → (5.2, 5.2, "J/cm²")  # Single value
    
    Args:
        fluence_str: Fluence range string
    
    Returns:
        (min_value, max_value, unit) tuple
    """
    if not fluence_str or not isinstance(fluence_str, str):
        return (None, None, None)
    
    fluence_str = fluence_str.strip()
    
    # Extract unit
    unit = None
    unit_patterns = [
        r'(J/cm[²2])',
        r'(mJ/cm[²2])',
        r'(J/m[²2])'
    ]
    
    for pattern in unit_patterns:
        match = re.search(pattern, fluence_str, re.IGNORECASE)
        if match:
            unit = normalize_laser_unit(match.group(1), 'energy')
            break
    
    # Extract range
    range_match = re.search(r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)', fluence_str)
    if range_match:
        min_val = float(range_match.group(1))
        max_val = float(range_match.group(2))
        return (min_val, max_val, unit)
    
    # Single value
    number_match = re.search(r'(\d+(?:\.\d+)?)', fluence_str)
    if number_match:
        value = float(number_match.group(1))
        return (value, value, unit)
    
    return (None, None, unit)


def parse_speed_range(speed_str: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Parse scan speed range string into min, max, unit.
    
    Examples:
        "100-500 mm/s" → (100.0, 500.0, "mm/s")
        "10-50 mm/sec" → (10.0, 50.0, "mm/s")
        "250 mm/s" → (250.0, 250.0, "mm/s")  # Single value
    
    Args:
        speed_str: Speed range string
    
    Returns:
        (min_value, max_value, unit) tuple
    """
    if not speed_str or not isinstance(speed_str, str):
        return (None, None, None)
    
    speed_str = speed_str.strip()
    
    # Extract unit
    unit = None
    unit_patterns = [
        r'(mm/s(?:ec)?)',
        r'(m/s(?:ec)?)',
        r'(cm/s(?:ec)?)'
    ]
    
    for pattern in unit_patterns:
        match = re.search(pattern, speed_str, re.IGNORECASE)
        if match:
            unit = normalize_laser_unit(match.group(1), 'speed')
            break
    
    # Extract range
    range_match = re.search(r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)', speed_str)
    if range_match:
        min_val = float(range_match.group(1))
        max_val = float(range_match.group(2))
        return (min_val, max_val, unit)
    
    # Single value
    number_match = re.search(r'(\d+(?:\.\d+)?)', speed_str)
    if number_match:
        value = float(number_match.group(1))
        return (value, value, unit)
    
    return (None, None, unit)
