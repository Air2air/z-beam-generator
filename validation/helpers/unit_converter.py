#!/usr/bin/env python3
"""
Unit Converter for Property Validation

Provides unit normalization for property validation to ensure
accurate range checking across different unit representations.

Per GROK_INSTRUCTIONS.md:
- Fail-fast on unknown units
- No silent conversions or fallbacks
- Explicit conversion rules only
"""

from typing import Tuple, Optional


class UnitConversionError(Exception):
    """Raised when unit conversion fails"""
    pass


class UnitConverter:
    """
    Unit converter for material properties.
    
    Converts property values to normalized units before validation.
    This prevents false positives when comparing values in different units.
    
    Example:
        electricalConductivity: 37,700,000 S/m = 37.7 MS/m
        Without conversion: 37,700,000 > 70 (FAIL - incorrect)
        With conversion: 37.7 > 70 (PASS - correct)
    """
    
    # Define conversion factors to normalized units
    # Format: {property_name: {normalized_unit: {source_unit: factor}}}
    CONVERSION_RULES = {
        'electricalConductivity': {
            'MS/m': {  # Normalized unit: MegaSiemens/meter
                'MS/m': 1.0,
                'S/m': 1e-6,  # 1 S/m = 0.000001 MS/m
                '×10⁷ S/m': 10.0,  # 1×10⁷ S/m = 10 MS/m
                '% IACS': 0.581,  # 100% IACS = 58.1 MS/m (copper standard)
            }
        },
        'electricalResistivity': {
            'Ω·m': {  # Normalized unit: Ohm-meter
                'Ω·m': 1.0,
                'ohm·m': 1.0,
                'Ω⋅m': 1.0,
            }
        },
        'thermalConductivity': {
            'W/(m·K)': {  # Normalized unit: Watts per meter-Kelvin
                'W/(m·K)': 1.0,
                'W/m·K': 1.0,
                'W/mK': 1.0,
            }
        },
        'thermalExpansion': {
            '10⁻⁶/K': {  # Normalized unit: parts per million per Kelvin
                '10⁻⁶/K': 1.0,
                'μm/m·°C': 1.0,  # Same scale
                'ppm/K': 1.0,
                'ppm/°C': 1.0,
            }
        },
        'density': {
            'g/cm³': {  # Normalized unit: grams per cubic centimeter
                'g/cm³': 1.0,
                'g/cc': 1.0,
                'kg/m³': 0.001,  # 1 kg/m³ = 0.001 g/cm³
            }
        },
        'hardness': {
            'GPa': {  # Normalized unit: GigaPascals (for Vickers hardness)
                'GPa': 1.0,
                'MPa': 0.001,  # 1 MPa = 0.001 GPa
                'HV': 0.0098,  # Approximate: HV to GPa conversion
                'Mohs': None,  # Mohs is non-linear - handle separately
            }
        },
        'youngsModulus': {
            'GPa': {
                'GPa': 1.0,
                'MPa': 0.001,
                'Pa': 1e-9,
            }
        },
        'tensileStrength': {
            'MPa': {
                'MPa': 1.0,
                'GPa': 1000.0,
                'Pa': 1e-6,
            }
        },
        'specificHeat': {
            'J/(kg·K)': {
                'J/(kg·K)': 1.0,
                'J/kg·K': 1.0,
                'J/kgK': 1.0,
            }
        },
        'thermalDiffusivity': {
            'mm²/s': {
                'mm²/s': 1.0,
                'm²/s': 1000000.0,  # 1 m²/s = 1,000,000 mm²/s
                'cm²/s': 100.0,  # 1 cm²/s = 100 mm²/s
            }
        },
    }
    
    @classmethod
    def normalize(cls, property_name: str, value: float, unit: str) -> Tuple[float, str]:
        """
        Normalize a property value to its standard unit.
        
        Args:
            property_name: Name of the property (e.g., 'electricalConductivity')
            value: The property value
            unit: The current unit
            
        Returns:
            Tuple of (normalized_value, normalized_unit)
            
        Raises:
            UnitConversionError: If conversion fails or unit is unknown
            
        Example:
            >>> UnitConverter.normalize('electricalConductivity', 37700000.0, 'S/m')
            (37.7, 'MS/m')
        """
        if property_name not in cls.CONVERSION_RULES:
            # No conversion rules - return as-is (property doesn't need normalization)
            return value, unit
        
        property_rules = cls.CONVERSION_RULES[property_name]
        normalized_unit = list(property_rules.keys())[0]  # First key is normalized unit
        
        if unit not in property_rules[normalized_unit]:
            raise UnitConversionError(
                f"Unknown unit '{unit}' for property '{property_name}'. "
                f"Expected one of: {list(property_rules[normalized_unit].keys())}"
            )
        
        conversion_factor = property_rules[normalized_unit][unit]
        
        if conversion_factor is None:
            raise UnitConversionError(
                f"Cannot convert unit '{unit}' for property '{property_name}' - "
                f"non-linear scale (e.g., Mohs hardness)"
            )
        
        normalized_value = value * conversion_factor
        return normalized_value, normalized_unit
    
    @classmethod
    def get_normalized_unit(cls, property_name: str) -> Optional[str]:
        """
        Get the normalized unit for a property.
        
        Args:
            property_name: Name of the property
            
        Returns:
            The normalized unit string, or None if property has no conversion rules
        """
        if property_name not in cls.CONVERSION_RULES:
            return None
        
        property_rules = cls.CONVERSION_RULES[property_name]
        return list(property_rules.keys())[0]
    
    @classmethod
    def is_convertible(cls, property_name: str, unit: str) -> bool:
        """
        Check if a unit can be converted for a property.
        
        Args:
            property_name: Name of the property
            unit: Unit to check
            
        Returns:
            True if convertible, False otherwise
        """
        if property_name not in cls.CONVERSION_RULES:
            return True  # No rules means no conversion needed
        
        property_rules = cls.CONVERSION_RULES[property_name]
        normalized_unit = list(property_rules.keys())[0]
        
        if unit not in property_rules[normalized_unit]:
            return False
        
        return property_rules[normalized_unit][unit] is not None
