"""
Unit Extraction Utility for MinUnit/MaxUnit Field Population

This module provides comprehensive unit extraction from material property ranges
to populate the MinUnit/MaxUnit fields required by the frontmatter schema.

Schema Requirements:
- 10 properties with complete Min/Max/MinUnit/MaxUnit field sets (40 total fields)
- Unit extraction from category ranges like "0.53 g/cm³" → "g/cm³"
- Consistent unit format validation and normalization
"""

import logging
import re
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class UnitExtractor:
    """Extract and normalize units from material property range strings."""
    
    # Unit normalization mappings
    UNIT_NORMALIZATIONS = {
        # Common variations to standard forms
        'g/cc': 'g/cm³',
        'g/cubic cm': 'g/cm³',
        'kg/m3': 'kg/m³',
        'kg/cubic m': 'kg/m³',
        'degrees C': '°C',
        'deg C': '°C',
        'celsius': '°C',
        'fahrenheit': '°F',
        'deg F': '°F',
        'microns': 'μm',
        'micrometers': 'μm',
        'nanometers': 'nm',
        'millimeters': 'mm',
        'centimeters': 'cm',
        'meters': 'm',
        'watts': 'W',
        'kilowatts': 'kW',
        'megawatts': 'MW',
        'hertz': 'Hz',
        'kilohertz': 'kHz',
        'megahertz': 'MHz',
        'gigahertz': 'GHz',
        'pascals': 'Pa',
        'kilopascals': 'kPa',
        'megapascals': 'MPa',
        'gigapascals': 'GPa',
        'percent': '%',
        'percentage': '%',
    }
    
    # Unit extraction patterns (in order of specificity)
    UNIT_PATTERNS = [
        # Most complex units first (with dots and special chars)
        r'[\d.-]+\s*([a-zA-Z]+/[a-zA-Z]+·[a-zA-Z]+)',           # J/g·K, W/m·K
        r'[\d.-]+\s*([μ][a-zA-Z]+/[a-zA-Z]+·[a-zA-Z]+)',       # μm/m·K
        r'[\d.-]+\s*([a-zA-Z]+/[a-zA-Z]+[³²])',                # g/cm³, units with superscript
        r'[\d.-]+\s*([a-zA-Z²³]+/[a-zA-Z]+)',                  # mm²/s, units with superscript prefix
        r'[\d.-]+\s*([a-zA-Z]+[³²])',                          # cm³, m²
        r'[\d.-]+\s*([a-zA-Z]+/[a-zA-Z]+)',                    # J/g, mm/s, W/m
        r'[\d.-]+\s*([μ][a-zA-Z]+/[a-zA-Z]+)',                 # μm/m
        r'[\d.-]+\s*([μ][a-zA-Z]+)',                           # μm, μs
        r'[\d.-]+\s*([°][CF])',                                # °C, °F
        r'[\d.-]+\s*([a-zA-Z]+⁻¹)',                           # cm⁻¹
        r'[\d.-]+\s*([a-zA-Z]+)',                              # MPa, Hz, HB, HV
        r'[\d.-]+\s*(%)',                                      # %
    ]
    
    def __init__(self):
        """Initialize unit extractor with compiled patterns."""
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) 
                                for pattern in self.UNIT_PATTERNS]
    
    def extract_unit(self, value_string: str) -> Optional[str]:
        """
        Extract unit from a value string like "0.53 g/cm³".
        
        Args:
            value_string: String containing numeric value and unit
            
        Returns:
            Extracted and normalized unit string, or None if no unit found
        """
        if not value_string or not isinstance(value_string, str):
            return None
        
        # Try each pattern in order of specificity
        for pattern in self.compiled_patterns:
            match = pattern.search(value_string)
            if match:
                unit = match.group(1)
                
                # Normalize unit if mapping exists
                normalized_unit = self.UNIT_NORMALIZATIONS.get(unit.lower(), unit)
                
                logger.debug(f"Extracted unit '{unit}' → '{normalized_unit}' from '{value_string}'")
                return normalized_unit
        
        logger.warning(f"No unit found in value string: '{value_string}'")
        return None
    
    def extract_min_max_units(self, range_data: Dict) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract MinUnit and MaxUnit from range data dictionary.
        
        Args:
            range_data: Dictionary with 'min' and 'max' keys containing value strings
            
        Returns:
            Tuple of (min_unit, max_unit) or (None, None) if extraction fails
        """
        if not isinstance(range_data, dict):
            return None, None
        
        min_unit = None
        max_unit = None
        
        if 'min' in range_data:
            min_unit = self.extract_unit(range_data['min'])
        
        if 'max' in range_data:
            max_unit = self.extract_unit(range_data['max'])
        
        # Validate consistency
        if min_unit and max_unit and min_unit != max_unit:
            logger.warning(f"Unit mismatch: min='{min_unit}' vs max='{max_unit}' in {range_data}")
        
        return min_unit, max_unit
    
    def extract_unit_from_range(self, range_data: Dict) -> Optional[str]:
        """
        Extract a single unit from range data, preferring consistent units.
        
        Args:
            range_data: Dictionary with 'min' and 'max' keys containing value strings
            
        Returns:
            Single unit string, or None if no unit found
        """
        if not isinstance(range_data, dict):
            return None
        
        min_unit, max_unit = self.extract_min_max_units(range_data)
        
        # Return consistent unit
        if min_unit and max_unit:
            if min_unit == max_unit:
                return min_unit
            else:
                # Units don't match, prefer min_unit but log warning
                logger.warning(f"Unit mismatch: min='{min_unit}' vs max='{max_unit}', using min unit")
                return min_unit
        
        # Return whichever unit we found
        return min_unit or max_unit
    
    def validate_unit_consistency(self, units: Dict[str, str]) -> bool:
        """
        Validate that MinUnit and MaxUnit are consistent for a property.
        
        Args:
            units: Dictionary with 'minUnit' and 'maxUnit' keys
            
        Returns:
            True if units are consistent or one is missing, False if mismatched
        """
        min_unit = units.get('minUnit')
        max_unit = units.get('maxUnit')
        
        if not min_unit or not max_unit:
            return True  # Allow missing units
        
        return min_unit == max_unit


# Global instance for easy access
unit_extractor = UnitExtractor()


if __name__ == "__main__":
    # Test unit extraction
    test_cases = [
        "0.53 g/cm³",
        "22.59 g/cm³",
        "70 MPa",
        "2000 MPa",
        "6.3 W/m·K",
        "429 W/m·K",
        "-38.8°C",
        "3422°C",
        "5 HB",
        "500 HV",
        "70 GPa",
        "411 GPa",
        "0.02 cm⁻¹",
        "100 cm⁻¹",
        "5%",
        "98%",
        "4.2 mm²/s",
        "174 mm²/s",
        "0.5 μm/m·K",
        "29.1 μm/m·K",
        "0.128 J/g·K",
        "0.904 J/g·K"
    ]
    
    print("=== UNIT EXTRACTION TESTING ===")
    extractor = UnitExtractor()
    
    for test_case in test_cases:
        unit = extractor.extract_unit(test_case)
        print(f"'{test_case}' → '{unit}'")
    
    print("\n=== RANGE UNIT EXTRACTION TESTING ===")
    test_ranges = [
        {"min": "1 W", "max": "10000 W"},
        {"min": "1 fs", "max": "1000000000 ns"},  # Unit mismatch case
        {"min": "0.1 J/cm²", "max": "100 J/cm²"},
        {"min": "0.01 mm", "max": "50 mm"},
    ]
    
    for range_data in test_ranges:
        single_unit = extractor.extract_unit_from_range(range_data)
        min_unit, max_unit = extractor.extract_min_max_units(range_data)
        print(f"{range_data} → single_unit='{single_unit}' (min='{min_unit}', max='{max_unit}')")
