#!/usr/bin/env python3
"""
Comprehensive tests for the enhanced category ranges database.
Tests all Phase 1 & 2 property ranges across all material categories.
"""

import unittest
import sys
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.property_enhancer import load_category_ranges


class TestCategoryRanges(unittest.TestCase):
    """Test suite for category ranges database."""

    def setUp(self):
        """Set up test fixtures."""
        self.ranges = load_category_ranges()
        self.expected_categories = [
            'metal', 'ceramic', 'composite', 'glass', 
            'stone', 'masonry', 'wood', 'semiconductor'
        ]
        self.expected_properties = [
            # Original 6 properties
            'density', 'tensileStrength', 'thermalConductivity', 
            'meltingPoint', 'hardness', 'youngsModulus',
            # Phase 1 & 2 properties (5 new)
            'laserAbsorption', 'laserReflectivity', 'thermalDiffusivity',
            'thermalExpansion', 'specificHeat'
        ]

    def test_database_loads_successfully(self):
        """Test that the category ranges database loads without errors."""
        self.assertIsInstance(self.ranges, dict)
        self.assertGreater(len(self.ranges), 0, "Category ranges should not be empty")

    def test_all_categories_present(self):
        """Test that all expected material categories are present."""
        for category in self.expected_categories:
            self.assertIn(category, self.ranges, f"Category '{category}' missing from database")

    def test_all_properties_present_in_all_categories(self):
        """Test that all 11 properties are present in every category."""
        for category in self.expected_categories:
            category_props = self.ranges[category]
            for prop in self.expected_properties:
                self.assertIn(prop, category_props, 
                            f"Property '{prop}' missing from category '{category}'")

    def test_property_structure_validity(self):
        """Test that each property has valid min/max structure."""
        for category_name, category_data in self.ranges.items():
            for prop_name, prop_data in category_data.items():
                with self.subTest(category=category_name, property=prop_name):
                    self.assertIsInstance(prop_data, dict, 
                                        f"{category_name}.{prop_name} should be a dictionary")
                    self.assertIn('min', prop_data, 
                                f"{category_name}.{prop_name} missing 'min' key")
                    self.assertIn('max', prop_data, 
                                f"{category_name}.{prop_name} missing 'max' key")
                    self.assertIsInstance(prop_data['min'], str, 
                                        f"{category_name}.{prop_name}.min should be string")
                    self.assertIsInstance(prop_data['max'], str, 
                                        f"{category_name}.{prop_name}.max should be string")
                    self.assertNotEqual(prop_data['min'], '', 
                                      f"{category_name}.{prop_name}.min should not be empty")
                    self.assertNotEqual(prop_data['max'], '', 
                                      f"{category_name}.{prop_name}.max should not be empty")

    def test_original_property_units(self):
        """Test that original 6 properties have expected units."""
        expected_units = {
            'density': ['g/cm³'],
            'tensileStrength': ['MPa'],
            'thermalConductivity': ['W/m·K'],
            'meltingPoint': ['°C'],
            'hardness': ['HV', 'HB', 'HRC'],
            'youngsModulus': ['GPa']
        }
        
        for category_name, category_data in self.ranges.items():
            for prop_name, expected_unit_list in expected_units.items():
                with self.subTest(category=category_name, property=prop_name):
                    prop_data = category_data[prop_name]
                    min_val = prop_data['min']
                    max_val = prop_data['max']
                    
                    # Check that at least one expected unit is present
                    min_has_unit = any(unit in min_val for unit in expected_unit_list)
                    max_has_unit = any(unit in max_val for unit in expected_unit_list)
                    
                    self.assertTrue(min_has_unit, 
                                  f"{category_name}.{prop_name}.min '{min_val}' missing expected units {expected_unit_list}")
                    self.assertTrue(max_has_unit, 
                                  f"{category_name}.{prop_name}.max '{max_val}' missing expected units {expected_unit_list}")

    def test_new_property_units(self):
        """Test that Phase 1 & 2 properties have expected units."""
        expected_units = {
            'laserAbsorption': ['cm⁻¹'],
            'laserReflectivity': ['%'],
            'thermalDiffusivity': ['mm²/s'],
            'thermalExpansion': ['µm/m·K'],
            'specificHeat': ['J/g·K']
        }
        
        for category_name, category_data in self.ranges.items():
            for prop_name, expected_unit_list in expected_units.items():
                with self.subTest(category=category_name, property=prop_name):
                    prop_data = category_data[prop_name]
                    min_val = prop_data['min']
                    max_val = prop_data['max']
                    
                    # Check that expected units are present
                    min_has_unit = any(unit in min_val for unit in expected_unit_list)
                    max_has_unit = any(unit in max_val for unit in expected_unit_list)
                    
                    self.assertTrue(min_has_unit, 
                                  f"{category_name}.{prop_name}.min '{min_val}' missing expected units {expected_unit_list}")
                    self.assertTrue(max_has_unit, 
                                  f"{category_name}.{prop_name}.max '{max_val}' missing expected units {expected_unit_list}")

    def test_numeric_values_extractable(self):
        """Test that numeric values can be extracted from all ranges."""
        from utils.percentile_calculator import extract_numeric_value
        
        for category_name, category_data in self.ranges.items():
            for prop_name, prop_data in category_data.items():
                with self.subTest(category=category_name, property=prop_name):
                    min_val = prop_data['min']
                    max_val = prop_data['max']
                    
                    # Should be able to extract numeric values
                    min_numeric = extract_numeric_value(min_val)
                    max_numeric = extract_numeric_value(max_val)
                    
                    self.assertIsInstance(min_numeric, (int, float), 
                                        f"Could not extract numeric value from {category_name}.{prop_name}.min: '{min_val}'")
                    self.assertIsInstance(max_numeric, (int, float), 
                                        f"Could not extract numeric value from {category_name}.{prop_name}.max: '{max_val}'")
                    self.assertGreaterEqual(max_numeric, min_numeric, 
                                          f"{category_name}.{prop_name}: max ({max_numeric}) should be >= min ({min_numeric})")

    def test_metal_category_realistic_ranges(self):
        """Test that metal category has realistic property ranges."""
        metal = self.ranges['metal']
        
        # Test original properties
        self.assertIn('0.5', metal['density']['min'])  # Lithium
        self.assertIn('22.6', metal['density']['max'])  # Osmium
        
        self.assertIn('-39', metal['meltingPoint']['min'])  # Mercury
        self.assertIn('3422', metal['meltingPoint']['max'])  # Tungsten
        
        # Test new laser properties
        self.assertIn('0.02', metal['laserAbsorption']['min'])  # Highly reflective
        self.assertIn('100', metal['laserAbsorption']['max'])  # Dark/oxidized
        
        self.assertIn('5%', metal['laserReflectivity']['min'])  # Oxidized
        self.assertIn('98%', metal['laserReflectivity']['max'])  # Polished
        
        # Test new thermal properties
        self.assertIn('4', metal['thermalDiffusivity']['min'])  # Stainless steel
        self.assertIn('174', metal['thermalDiffusivity']['max'])  # Silver
        
        self.assertIn('0.5', metal['thermalExpansion']['min'])  # Low expansion alloys
        self.assertIn('29', metal['thermalExpansion']['max'])  # High expansion metals

    def test_ceramic_category_characteristics(self):
        """Test that ceramic category has appropriate characteristics."""
        ceramic = self.ranges['ceramic']
        
        # Ceramics should have high hardness ranges
        self.assertIn('2500', ceramic['hardness']['max'])  # Should have very high hardness
        
        # Ceramics should have low thermal expansion (generally)
        self.assertIn('0.5', ceramic['thermalExpansion']['min'])  # Quartz ceramics
        
        # Ceramics can have very low or very high thermal conductivity
        self.assertIn('0.5', ceramic['thermalConductivity']['min'])  # Insulating
        self.assertIn('200', ceramic['thermalConductivity']['max'])  # Silicon carbide

    def test_wood_category_characteristics(self):
        """Test that wood category has appropriate characteristics."""
        wood = self.ranges['wood']
        
        # Wood should have low density range
        self.assertIn('0.1', wood['density']['min'])  # Balsa
        self.assertIn('1.3', wood['density']['max'])  # Dense hardwood
        
        # Wood should have relatively low melting point (decomposition)
        self.assertIn('250', wood['meltingPoint']['min'])  # Decomposition start
        self.assertIn('500', wood['meltingPoint']['max'])  # Complete pyrolysis
        
        # Wood should have high laser absorption (organic material)
        self.assertIn('5', wood['laserAbsorption']['min'])  # Light woods
        self.assertIn('100', wood['laserAbsorption']['max'])  # Dark woods
        
        # Wood should have high specific heat (especially when wet)
        self.assertIn('2.5', wood['specificHeat']['max'])  # Green/wet wood

    def test_semiconductor_category_characteristics(self):
        """Test that semiconductor category has appropriate characteristics."""
        semiconductor = self.ranges['semiconductor']
        
        # Semiconductors should have high hardness
        self.assertIn('900', semiconductor['hardness']['min'])  # Silicon
        self.assertIn('2800', semiconductor['hardness']['max'])  # Silicon carbide
        
        # Semiconductors can have extreme thermal conductivity range
        self.assertIn('1.5', semiconductor['thermalConductivity']['min'])  # Low-k materials
        self.assertIn('490', semiconductor['thermalConductivity']['max'])  # Silicon carbide
        
        # Semiconductors should have very high Young's modulus
        self.assertIn('130', semiconductor['youngsModulus']['min'])  # Silicon
        self.assertIn('450', semiconductor['youngsModulus']['max'])  # Silicon carbide

    def test_laser_properties_consistency(self):
        """Test that laser properties are consistent across categories."""
        for category_name, category_data in self.ranges.items():
            with self.subTest(category=category_name):
                # Laser absorption and reflectivity should be inversely related conceptually
                absorption_min = extract_numeric_value(category_data['laserAbsorption']['min'])
                absorption_max = extract_numeric_value(category_data['laserAbsorption']['max'])
                
                reflectivity_min = extract_numeric_value(category_data['laserReflectivity']['min'])
                reflectivity_max = extract_numeric_value(category_data['laserReflectivity']['max'])
                
                # Basic sanity checks
                self.assertGreater(absorption_max, absorption_min, 
                                 f"{category_name}: absorption max should be > min")
                self.assertGreater(reflectivity_max, reflectivity_min, 
                                 f"{category_name}: reflectivity max should be > min")
                
                # Reflectivity should be percentage (0-100%)
                self.assertGreaterEqual(reflectivity_min, 0, 
                                      f"{category_name}: reflectivity min should be >= 0%")
                self.assertLessEqual(reflectivity_max, 100, 
                                   f"{category_name}: reflectivity max should be <= 100%")

    def test_thermal_properties_consistency(self):
        """Test that thermal properties are physically consistent."""
        from utils.percentile_calculator import extract_numeric_value
        
        for category_name, category_data in self.ranges.items():
            with self.subTest(category=category_name):
                # Thermal diffusivity should be positive
                diffusivity_min = extract_numeric_value(category_data['thermalDiffusivity']['min'])
                diffusivity_max = extract_numeric_value(category_data['thermalDiffusivity']['max'])
                
                self.assertGreater(diffusivity_min, 0, 
                                 f"{category_name}: thermal diffusivity min should be > 0")
                self.assertGreater(diffusivity_max, diffusivity_min, 
                                 f"{category_name}: thermal diffusivity max should be > min")
                
                # Thermal expansion should be positive
                expansion_min = extract_numeric_value(category_data['thermalExpansion']['min'])
                expansion_max = extract_numeric_value(category_data['thermalExpansion']['max'])
                
                self.assertGreater(expansion_min, 0, 
                                 f"{category_name}: thermal expansion min should be > 0")
                self.assertGreater(expansion_max, expansion_min, 
                                 f"{category_name}: thermal expansion max should be > min")
                
                # Specific heat should be positive and reasonable
                specific_heat_min = extract_numeric_value(category_data['specificHeat']['min'])
                specific_heat_max = extract_numeric_value(category_data['specificHeat']['max'])
                
                self.assertGreater(specific_heat_min, 0, 
                                 f"{category_name}: specific heat min should be > 0")
                self.assertGreater(specific_heat_max, specific_heat_min, 
                                 f"{category_name}: specific heat max should be > min")
                self.assertLess(specific_heat_max, 10, 
                              f"{category_name}: specific heat max should be reasonable (< 10 J/g·K)")


class TestCategoryRangesIntegration(unittest.TestCase):
    """Integration tests for category ranges with real calculations."""

    def test_realistic_material_percentiles(self):
        """Test percentile calculations with realistic material data across categories."""
        from utils.percentile_calculator import calculate_percentile
        
        ranges = load_category_ranges()
        
        # Test materials with known characteristics
        test_materials = [
            {
                'category': 'metal',
                'material': 'Aluminum',
                'properties': {
                    'density': '2.70 g/cm³',  # Should be low percentile (light metal)
                    'thermalConductivity': '237 W/m·K',  # Should be high percentile (good conductor)
                    'laserReflectivity': '90%'  # Should be high percentile (reflective)
                }
            },
            {
                'category': 'ceramic',
                'material': 'Alumina',
                'properties': {
                    'hardness': '1500 HV',  # Should be high percentile (very hard)
                    'thermalConductivity': '30 W/m·K',  # Should be moderate percentile
                    'thermalExpansion': '8 µm/m·K'  # Should be moderate percentile
                }
            },
            {
                'category': 'wood',
                'material': 'Oak',
                'properties': {
                    'density': '0.75 g/cm³',  # Should be moderate percentile
                    'laserAbsorption': '50 cm⁻¹',  # Should be moderate percentile
                    'specificHeat': '1.7 J/g·K'  # Should be moderate-high percentile
                }
            }
        ]
        
        for test_case in test_materials:
            category = test_case['category']
            category_ranges = ranges[category]
            
            for prop_name, prop_value in test_case['properties'].items():
                with self.subTest(category=category, material=test_case['material'], property=prop_name):
                    prop_ranges = category_ranges[prop_name]
                    min_val = prop_ranges['min']
                    max_val = prop_ranges['max']
                    
                    percentile = calculate_percentile(prop_value, min_val, max_val)
                    
                    # Percentile should be valid
                    self.assertTrue(0 <= percentile <= 100, 
                                  f"{category} {prop_name} percentile {percentile} out of range")
                    
                    # Test specific expectations
                    if category == 'metal' and prop_name == 'density' and 'Aluminum' in test_case['material']:
                        self.assertLess(percentile, 50, "Aluminum should have low density percentile")
                    
                    if category == 'metal' and prop_name == 'thermalConductivity' and 'Aluminum' in test_case['material']:
                        self.assertGreater(percentile, 50, "Aluminum should have high thermal conductivity percentile")
                    
                    if category == 'ceramic' and prop_name == 'hardness':
                        self.assertGreaterEqual(percentile, 50, "Ceramics should have high hardness percentile")


def extract_numeric_value(value_str):
    """Helper function to extract numeric values (imported locally to avoid circular imports)."""
    from utils.percentile_calculator import extract_numeric_value as calc_extract
    return calc_extract(value_str)


if __name__ == '__main__':
    unittest.main(verbosity=2)
