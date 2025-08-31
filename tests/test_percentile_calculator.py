#!/usr/bin/env python3
"""
Comprehensive tests for the enhanced percentile calculator system.
Tests all new functionality implemented for Phase 1 & 2 properties.
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.percentile_calculator import (
    extract_numeric_value,
    calculate_percentile,
    calculate_property_percentiles
)


class TestPercentileCalculator(unittest.TestCase):
    """Test suite for percentile calculator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_category_ranges = {
            'metal': {
                'density': {'min': '0.5 g/cm³', 'max': '22.6 g/cm³'},
                'meltingPoint': {'min': '-39°C', 'max': '3422°C'},
                'thermalConductivity': {'min': '8 W/m·K', 'max': '429 W/m·K'},
                'tensileStrength': {'min': '70 MPa', 'max': '2000 MPa'},
                'hardness': {'min': '5 HB', 'max': '500 HV'},
                'youngsModulus': {'min': '70 GPa', 'max': '411 GPa'},
                'laserAbsorption': {'min': '0.02 cm⁻¹', 'max': '100 cm⁻¹'},
                'laserReflectivity': {'min': '5%', 'max': '98%'},
                'thermalDiffusivity': {'min': '4 mm²/s', 'max': '174 mm²/s'},
                'thermalExpansion': {'min': '0.5 µm/m·K', 'max': '29 µm/m·K'},
                'specificHeat': {'min': '0.13 J/g·K', 'max': '0.90 J/g·K'}
            }
        }

    def test_extract_numeric_value_original_units(self):
        """Test numeric extraction for original 6 property units."""
        test_cases = [
            ("7.85 g/cm³", 7.85),
            ("1500°C", 1500.0),
            ("50 W/m·K", 50.0),
            ("400 MPa", 400.0),
            ("150 HV", 150.0),
            ("200 GPa", 200.0)
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = extract_numeric_value(input_value)
                self.assertAlmostEqual(result, expected, places=2)

    def test_extract_numeric_value_new_units(self):
        """Test numeric extraction for Phase 1 & 2 property units."""
        test_cases = [
            # Laser-specific units
            ("0.02 cm⁻¹", 0.02),
            ("100 cm⁻¹", 100.0),
            ("98%", 98.0),
            ("5%", 5.0),
            
            # Thermal property units
            ("174 mm²/s", 174.0),
            ("4 mm²/s", 4.0),
            ("29 µm/m·K", 29.0),
            ("0.5 µm/m·K", 0.5),
            ("0.90 J/g·K", 0.90),
            ("0.13 J/g·K", 0.13),
            
            # Scientific notation
            ("1.5e-3 cm⁻¹", 0.0015),
            ("2.5E+2 mm²/s", 250.0)
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = extract_numeric_value(input_value)
                self.assertAlmostEqual(result, expected, places=4)

    def test_extract_numeric_value_ranges(self):
        """Test numeric extraction for range values."""
        test_cases = [
            ("50-100 MPa", 75.0),  # Average of range
            ("10-20 cm⁻¹", 15.0),
            ("0.1-0.5 J/g·K", 0.3)
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = extract_numeric_value(input_value)
                self.assertAlmostEqual(result, expected, places=2)

    def test_extract_numeric_value_edge_cases(self):
        """Test numeric extraction for edge cases."""
        test_cases = [
            ("N/A", 0.0),
            ("", 0.0),
            ("NULL", 0.0),
            ("na", 0.0),
            (None, 0.0)
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = extract_numeric_value(str(input_value) if input_value else "")
                self.assertEqual(result, expected)

    def test_calculate_percentile_original_properties(self):
        """Test percentile calculation for original 6 properties."""
        test_cases = [
            # (value, min, max, expected_percentile)
            ("7.85 g/cm³", "0.5 g/cm³", "22.6 g/cm³", 33.3),  # Steel density
            ("1500°C", "-39°C", "3422°C", 43.2),  # Steel melting point
            ("50 W/m·K", "8 W/m·K", "429 W/m·K", 10.0),  # Steel thermal conductivity
            ("400 MPa", "70 MPa", "2000 MPa", 17.1),  # Steel tensile strength
            ("200 GPa", "70 GPa", "411 GPa", 38.1)  # Steel Young's modulus
        ]
        
        for value, min_val, max_val, expected in test_cases:
            with self.subTest(value=value):
                result = calculate_percentile(value, min_val, max_val)
                self.assertAlmostEqual(result, expected, places=1)

    def test_calculate_percentile_new_properties(self):
        """Test percentile calculation for Phase 1 & 2 properties."""
        test_cases = [
            # Laser-specific properties
            ("10 cm⁻¹", "0.02 cm⁻¹", "100 cm⁻¹", 10.0),  # Moderate absorption
            ("90%", "5%", "98%", 91.4),  # High reflectivity
            
            # Thermal properties
            ("15 mm²/s", "4 mm²/s", "174 mm²/s", 6.5),  # Low diffusivity
            ("12 µm/m·K", "0.5 µm/m·K", "29 µm/m·K", 40.4),  # Moderate expansion
            ("0.46 J/g·K", "0.13 J/g·K", "0.90 J/g·K", 42.9)  # Moderate specific heat
        ]
        
        for value, min_val, max_val, expected in test_cases:
            with self.subTest(value=value):
                result = calculate_percentile(value, min_val, max_val)
                self.assertAlmostEqual(result, expected, places=1)

    def test_calculate_percentile_edge_cases(self):
        """Test percentile calculation edge cases."""
        # Value at minimum
        result = calculate_percentile("5%", "5%", "98%")
        self.assertEqual(result, 0.0)
        
        # Value at maximum
        result = calculate_percentile("98%", "5%", "98%")
        self.assertEqual(result, 100.0)
        
        # Value below minimum
        result = calculate_percentile("1%", "5%", "98%")
        self.assertEqual(result, 0.0)
        
        # Value above maximum
        result = calculate_percentile("99%", "5%", "98%")
        self.assertEqual(result, 100.0)
        
        # Min equals max
        result = calculate_percentile("50", "50", "50")
        self.assertEqual(result, 50.0)

    def test_calculate_property_percentiles_complete_material(self):
        """Test percentile calculation for a complete material with all 11 properties."""
        properties = {
            # Original properties
            'density': '7.85 g/cm³',
            'densityMin': '0.5 g/cm³',
            'densityMax': '22.6 g/cm³',
            'meltingPoint': '1500°C',
            'meltingMin': '-39°C',
            'meltingMax': '3422°C',
            'thermalConductivity': '50 W/m·K',
            'thermalMin': '8 W/m·K',
            'thermalMax': '429 W/m·K',
            'tensileStrength': '400 MPa',
            'tensileMin': '70 MPa',
            'tensileMax': '2000 MPa',
            'hardness': '150 HV',
            'hardnessMin': '5 HB',
            'hardnessMax': '500 HV',
            'youngsModulus': '200 GPa',
            'modulusMin': '70 GPa',
            'modulusMax': '411 GPa',
            
            # New properties
            'laserAbsorption': '10 cm⁻¹',
            'laserAbsorptionMin': '0.02 cm⁻¹',
            'laserAbsorptionMax': '100 cm⁻¹',
            'laserReflectivity': '20%',
            'laserReflectivityMin': '5%',
            'laserReflectivityMax': '98%',
            'thermalDiffusivity': '15 mm²/s',
            'thermalDiffusivityMin': '4 mm²/s',
            'thermalDiffusivityMax': '174 mm²/s',
            'thermalExpansion': '12 µm/m·K',
            'thermalExpansionMin': '0.5 µm/m·K',
            'thermalExpansionMax': '29 µm/m·K',
            'specificHeat': '0.46 J/g·K',
            'specificHeatMin': '0.13 J/g·K',
            'specificHeatMax': '0.90 J/g·K'
        }
        
        enhanced = calculate_property_percentiles(properties, self.test_category_ranges, 'metal')
        
        # Check that all 11 percentiles were calculated
        expected_percentiles = [
            'densityPercentile',
            'meltingPercentile',
            'thermalPercentile',
            'tensilePercentile',
            'hardnessPercentile',
            'modulusPercentile',
            'laserAbsorptionPercentile',
            'laserReflectivityPercentile',
            'thermalDiffusivityPercentile',
            'thermalExpansionPercentile',
            'specificHeatPercentile'
        ]
        
        for percentile_key in expected_percentiles:
            with self.subTest(percentile=percentile_key):
                self.assertIn(percentile_key, enhanced)
                self.assertIsInstance(enhanced[percentile_key], (int, float))
                self.assertTrue(0 <= enhanced[percentile_key] <= 100)

    def test_calculate_property_percentiles_partial_material(self):
        """Test percentile calculation when some properties are missing."""
        properties = {
            'density': '7.85 g/cm³',
            'densityMin': '0.5 g/cm³',
            'densityMax': '22.6 g/cm³',
            'laserAbsorption': '10 cm⁻¹',
            'laserAbsorptionMin': '0.02 cm⁻¹',
            'laserAbsorptionMax': '100 cm⁻¹'
        }
        
        enhanced = calculate_property_percentiles(properties, self.test_category_ranges, 'metal')
        
        # Should calculate percentiles for properties that have all required values
        self.assertIn('densityPercentile', enhanced)
        self.assertIn('laserAbsorptionPercentile', enhanced)
        
        # Should not calculate percentiles for missing properties
        self.assertNotIn('meltingPercentile', enhanced)
        self.assertNotIn('thermalPercentile', enhanced)

    def test_calculate_property_percentiles_invalid_category(self):
        """Test percentile calculation with invalid category."""
        properties = {
            'density': '7.85 g/cm³',
            'densityMin': '0.5 g/cm³',
            'densityMax': '22.6 g/cm³'
        }
        
        enhanced = calculate_property_percentiles(properties, self.test_category_ranges, 'invalid')
        
        # Should return original properties unchanged
        self.assertEqual(enhanced, properties)


class TestPercentileCalculatorIntegration(unittest.TestCase):
    """Integration tests for percentile calculator with real data."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_category_ranges = {
            'metal': {
                'density': {'min': '0.5 g/cm³', 'max': '22.6 g/cm³'},
                'meltingPoint': {'min': '-39°C', 'max': '3422°C'},
                'thermalConductivity': {'min': '8 W/m·K', 'max': '429 W/m·K'},
                'tensileStrength': {'min': '70 MPa', 'max': '2000 MPa'},
                'hardness': {'min': '5 HB', 'max': '500 HV'},
                'youngsModulus': {'min': '70 GPa', 'max': '411 GPa'},
                'laserAbsorption': {'min': '0.02 cm⁻¹', 'max': '100 cm⁻¹'},
                'laserReflectivity': {'min': '5%', 'max': '98%'},
                'thermalDiffusivity': {'min': '4 mm²/s', 'max': '174 mm²/s'},
                'thermalExpansion': {'min': '0.5 µm/m·K', 'max': '29 µm/m·K'},
                'specificHeat': {'min': '0.13 J/g·K', 'max': '0.90 J/g·K'}
            }
        }
    
    def test_aluminum_percentiles(self):
        """Test percentile calculations for aluminum with realistic values."""
        aluminum_properties = {
            'density': '2.70 g/cm³',
            'densityMin': '0.5 g/cm³',
            'densityMax': '22.6 g/cm³',
            'meltingPoint': '660°C',
            'meltingMin': '-39°C',
            'meltingMax': '3422°C',
            'thermalConductivity': '237 W/m·K',
            'thermalMin': '8 W/m·K',
            'thermalMax': '429 W/m·K',
            'laserAbsorption': '0.1 cm⁻¹',  # Highly reflective
            'laserAbsorptionMin': '0.02 cm⁻¹',
            'laserAbsorptionMax': '100 cm⁻¹',
            'laserReflectivity': '90%',  # High reflectivity
            'laserReflectivityMin': '5%',
            'laserReflectivityMax': '98%',
            'thermalDiffusivity': '97 mm²/s',  # High thermal diffusivity
            'thermalDiffusivityMin': '4 mm²/s',
            'thermalDiffusivityMax': '174 mm²/s'
        }
        
        enhanced = calculate_property_percentiles(aluminum_properties, 
                                                 {'metal': self.test_category_ranges['metal']}, 'metal')
        
        # Aluminum should have low density percentile (light metal)
        self.assertLess(enhanced['densityPercentile'], 25)
        
        # Aluminum should have low melting point percentile
        self.assertLess(enhanced['meltingPercentile'], 30)
        
        # Aluminum should have high thermal conductivity percentile (good conductor)
        self.assertGreater(enhanced['thermalPercentile'], 50)
        
        # Aluminum should have very low laser absorption (highly reflective)
        self.assertLess(enhanced['laserAbsorptionPercentile'], 5)
        
        # Aluminum should have very high laser reflectivity
        self.assertGreater(enhanced['laserReflectivityPercentile'], 85)
        
        # Aluminum should have high thermal diffusivity percentile
        self.assertGreater(enhanced['thermalDiffusivityPercentile'], 50)

    def test_stainless_steel_percentiles(self):
        """Test percentile calculations for stainless steel with realistic values."""
        steel_properties = {
            'density': '8.00 g/cm³',
            'densityMin': '0.5 g/cm³',
            'densityMax': '22.6 g/cm³',
            'thermalConductivity': '16.2 W/m·K',  # Poor conductor
            'thermalMin': '8 W/m·K',
            'thermalMax': '429 W/m·K',
            'laserAbsorption': '15 cm⁻¹',  # Moderate absorption
            'laserAbsorptionMin': '0.02 cm⁻¹',
            'laserAbsorptionMax': '100 cm⁻¹',
            'thermalDiffusivity': '4.2 mm²/s',  # Low thermal diffusivity
            'thermalDiffusivityMin': '4 mm²/s',
            'thermalDiffusivityMax': '174 mm²/s',
            'specificHeat': '0.50 J/g·K',
            'specificHeatMin': '0.13 J/g·K',
            'specificHeatMax': '0.90 J/g·K'
        }
        
        enhanced = calculate_property_percentiles(steel_properties, 
                                                 {'metal': self.test_category_ranges['metal']}, 'metal')
        
        # Stainless steel should have moderate density percentile
        self.assertTrue(25 <= enhanced['densityPercentile'] <= 45)
        
        # Stainless steel should have low thermal conductivity percentile (poor conductor)
        self.assertLess(enhanced['thermalPercentile'], 20)
        
        # Stainless steel should have moderate laser absorption
        self.assertTrue(10 <= enhanced['laserAbsorptionPercentile'] <= 25)
        
        # Stainless steel should have very low thermal diffusivity percentile
        self.assertLess(enhanced['thermalDiffusivityPercentile'], 10)
        
        # Stainless steel should have moderate specific heat percentile
        self.assertTrue(35 <= enhanced['specificHeatPercentile'] <= 65)


if __name__ == '__main__':
    unittest.main(verbosity=2)
