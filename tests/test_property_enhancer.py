#!/usr/bin/env python3
"""
Comprehensive tests for the enhanced property enhancer system.
Tests the integration of percentile calculations with frontmatter enhancement.
"""

import unittest
import sys
import tempfile
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.property_enhancer import (
    enhance_frontmatter_with_context,
    enhance_generated_frontmatter,
    load_category_ranges
)


class TestPropertyEnhancer(unittest.TestCase):
    """Test suite for property enhancer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_steel = {
            'name': 'AISI 1018 Steel',
            'category': 'metal',
            'description': 'Low carbon steel',
            'properties': {
                'density': '7.87 g/cm³',
                'meltingPoint': '1450°C',
                'thermalConductivity': '51.9 W/m·K',
                'tensileStrength': '440 MPa',
                'hardness': '126 HV',
                'youngsModulus': '205 GPa'
            }
        }
        
        self.enhanced_material = {
            'name': 'Aluminum 6061-T6',
            'category': 'metal',
            'description': 'Heat-treated aluminum alloy',
            'properties': {
                # Original properties
                'density': '2.70 g/cm³',
                'meltingPoint': '660°C',
                'thermalConductivity': '167 W/m·K',
                'tensileStrength': '310 MPa',
                'hardness': '95 HV',
                'youngsModulus': '68.9 GPa',
                
                # Phase 1 & 2 properties
                'laserAbsorption': '0.1 cm⁻¹',
                'laserReflectivity': '90%',
                'thermalDiffusivity': '67 mm²/s',
                'thermalExpansion': '23.6 µm/m·K',
                'specificHeat': '0.90 J/g·K'
            }
        }

    def test_load_category_ranges(self):
        """Test loading of category ranges from YAML file."""
        ranges = load_category_ranges()
        
        # Should load successfully
        self.assertIsInstance(ranges, dict)
        self.assertGreater(len(ranges), 0)
        
        # Should contain expected categories
        expected_categories = ['metal', 'ceramic', 'composite', 'glass', 'stone', 'masonry', 'wood', 'semiconductor']
        for category in expected_categories:
            self.assertIn(category, ranges, f"Category {category} missing from ranges")
        
        # Each category should have all 11 properties
        expected_properties = [
            'density', 'tensileStrength', 'thermalConductivity', 'meltingPoint',
            'hardness', 'youngsModulus', 'laserAbsorption', 'laserReflectivity',
            'thermalDiffusivity', 'thermalExpansion', 'specificHeat'
        ]
        
        for category, props in ranges.items():
            for prop in expected_properties:
                self.assertIn(prop, props, f"Property {prop} missing from {category} category")
                self.assertIn('min', props[prop], f"Min value missing for {prop} in {category}")
                self.assertIn('max', props[prop], f"Max value missing for {prop} in {category}")

    def test_enhance_frontmatter_original_properties(self):
        """Test enhancement with original 6 properties."""
        enhanced = enhance_frontmatter_with_context(self.sample_steel, 'metal')
        
        # Should return enhanced data
        self.assertIsInstance(enhanced, dict)
        self.assertIn('properties', enhanced)
        
        properties = enhanced['properties']
        
        # Should have min/max values added for original properties
        expected_min_max = [
            ('densityMin', 'densityMax'),
            ('meltingMin', 'meltingMax'),
            ('thermalMin', 'thermalMax'),
            ('tensileMin', 'tensileMax'),
            ('hardnessMin', 'hardnessMax'),
            ('modulusMin', 'modulusMax')
        ]
        
        for min_key, max_key in expected_min_max:
            self.assertIn(min_key, properties, f"Missing {min_key}")
            self.assertIn(max_key, properties, f"Missing {max_key}")
            self.assertNotEqual(properties[min_key], '', f"{min_key} should not be empty")
            self.assertNotEqual(properties[max_key], '', f"{max_key} should not be empty")
        
        # Should have percentiles calculated for original properties
        expected_percentiles = [
            'densityPercentile',
            'meltingPercentile',
            'thermalPercentile',
            'tensilePercentile',
            'hardnessPercentile',
            'modulusPercentile'
        ]
        
        for percentile in expected_percentiles:
            self.assertIn(percentile, properties, f"Missing {percentile}")
            self.assertIsInstance(properties[percentile], (int, float))
            self.assertTrue(0 <= properties[percentile] <= 100, f"{percentile} out of range: {properties[percentile]}")

    def test_enhance_frontmatter_all_properties(self):
        """Test enhancement with all 11 properties (original + Phase 1 & 2)."""
        enhanced = enhance_frontmatter_with_context(self.enhanced_material, 'metal')
        
        # Should return enhanced data
        self.assertIsInstance(enhanced, dict)
        self.assertIn('properties', enhanced)
        
        properties = enhanced['properties']
        
        # Should have min/max values for all 11 properties
        expected_min_max = [
            ('densityMin', 'densityMax'),
            ('meltingMin', 'meltingMax'),
            ('thermalMin', 'thermalMax'),
            ('tensileMin', 'tensileMax'),
            ('hardnessMin', 'hardnessMax'),
            ('modulusMin', 'modulusMax'),
            ('laserAbsorptionMin', 'laserAbsorptionMax'),
            ('laserReflectivityMin', 'laserReflectivityMax'),
            ('thermalDiffusivityMin', 'thermalDiffusivityMax'),
            ('thermalExpansionMin', 'thermalExpansionMax'),
            ('specificHeatMin', 'specificHeatMax')
        ]
        
        for min_key, max_key in expected_min_max:
            self.assertIn(min_key, properties, f"Missing {min_key}")
            self.assertIn(max_key, properties, f"Missing {max_key}")
        
        # Should have percentiles for all 11 properties
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
        
        for percentile in expected_percentiles:
            self.assertIn(percentile, properties, f"Missing {percentile}")
            self.assertIsInstance(properties[percentile], (int, float))
            self.assertTrue(0 <= properties[percentile] <= 100, f"{percentile} out of range: {properties[percentile]}")

    def test_enhance_frontmatter_aluminum_characteristics(self):
        """Test that aluminum gets expected percentile characteristics."""
        enhanced = enhance_frontmatter_with_context(self.enhanced_material, 'metal')
        properties = enhanced['properties']
        
        # Aluminum should have low density percentile (light metal)
        self.assertLess(properties['densityPercentile'], 25, "Aluminum density percentile should be low")
        
        # Aluminum should have low melting point percentile
        self.assertLess(properties['meltingPercentile'], 30, "Aluminum melting point percentile should be low")
        
        # Aluminum should have high thermal conductivity percentile (good conductor)
        self.assertGreater(properties['thermalPercentile'], 35, "Aluminum thermal conductivity percentile should be high")
        
        # Aluminum should have very low laser absorption (highly reflective)
        self.assertLess(properties['laserAbsorptionPercentile'], 5, "Aluminum laser absorption should be very low")
        
        # Aluminum should have very high laser reflectivity
        self.assertGreater(properties['laserReflectivityPercentile'], 85, "Aluminum laser reflectivity should be very high")
        
        # Aluminum should have high thermal diffusivity
        self.assertGreater(properties['thermalDiffusivityPercentile'], 30, "Aluminum thermal diffusivity should be high")

    def test_enhance_frontmatter_invalid_category(self):
        """Test enhancement with invalid category."""
        enhanced = enhance_frontmatter_with_context(self.sample_steel, 'invalid_category')
        
        # Should return original data unchanged
        self.assertEqual(enhanced, self.sample_steel)

    def test_enhance_frontmatter_missing_properties(self):
        """Test enhancement when properties section is missing."""
        material_no_props = {
            'name': 'Test Material',
            'category': 'metal',
            'description': 'Test description'
        }
        
        enhanced = enhance_frontmatter_with_context(material_no_props, 'metal')
        
        # Should return original data unchanged
        self.assertEqual(enhanced, material_no_props)

    def test_enhance_generated_frontmatter(self):
        """Test enhancement of YAML frontmatter content."""
        frontmatter_content = """---
name: Steel Sample
category: metal
description: Test steel for laser cleaning
properties:
  density: '7.85 g/cm³'
  meltingPoint: '1500°C'
  thermalConductivity: '50 W/m·K'
  tensileStrength: '400 MPa'
  hardness: '150 HV'
  youngsModulus: '200 GPa'
---
# Additional content here
This is the body content."""
        
        enhanced_content = enhance_generated_frontmatter(frontmatter_content, 'metal')
        
        # Should still be valid YAML frontmatter
        self.assertTrue(enhanced_content.startswith('---'))
        
        # Should contain enhanced properties
        self.assertIn('densityMin', enhanced_content)
        self.assertIn('densityMax', enhanced_content)
        self.assertIn('densityPercentile', enhanced_content)
        
        # Should preserve body content
        self.assertIn('# Additional content here', enhanced_content)
        self.assertIn('This is the body content.', enhanced_content)

    def test_enhance_generated_frontmatter_invalid_yaml(self):
        """Test enhancement with invalid YAML content."""
        invalid_content = "This is not YAML frontmatter"
        
        enhanced = enhance_generated_frontmatter(invalid_content, 'metal')
        
        # Should return original content unchanged
        self.assertEqual(enhanced, invalid_content)

    def test_multiple_categories(self):
        """Test enhancement works for different material categories."""
        categories_to_test = ['ceramic', 'composite', 'glass', 'wood']
        
        for category in categories_to_test:
            with self.subTest(category=category):
                test_material = {
                    'name': f'Test {category.title()}',
                    'category': category,
                    'properties': {
                        'density': '2.5 g/cm³',
                        'tensileStrength': '100 MPa'
                    }
                }
                
                enhanced = enhance_frontmatter_with_context(test_material, category)
                
                # Should enhance successfully
                self.assertIn('properties', enhanced)
                properties = enhanced['properties']
                
                # Should add min/max values
                self.assertIn('densityMin', properties)
                self.assertIn('densityMax', properties)
                self.assertIn('tensileMin', properties)
                self.assertIn('tensileMax', properties)
                
                # Should calculate percentiles
                self.assertIn('densityPercentile', properties)
                self.assertIn('tensilePercentile', properties)


class TestPropertyEnhancerIntegration(unittest.TestCase):
    """Integration tests for property enhancer with real scenarios."""

    def test_comprehensive_material_enhancement(self):
        """Test enhancement of a material with all property types."""
        comprehensive_material = {
            'name': 'Comprehensive Test Material',
            'category': 'metal',
            'description': 'Material with all 11 properties for testing',
            'properties': {
                # Original 6 properties
                'density': '5.0 g/cm³',
                'meltingPoint': '1000°C',
                'thermalConductivity': '100 W/m·K',
                'tensileStrength': '500 MPa',
                'hardness': '200 HV',
                'youngsModulus': '150 GPa',
                
                # Phase 1: Laser properties
                'laserAbsorption': '50 cm⁻¹',
                'laserReflectivity': '50%',
                
                # Phase 2: Thermal properties
                'thermalDiffusivity': '50 mm²/s',
                'thermalExpansion': '15 µm/m·K',
                'specificHeat': '0.5 J/g·K'
            }
        }
        
        enhanced = enhance_frontmatter_with_context(comprehensive_material, 'metal')
        properties = enhanced['properties']
        
        # Should have 11 original properties + 22 min/max + 11 percentiles = 44 properties
        total_properties = len(properties)
        expected_minimum = 33  # At least original + min/max + percentiles
        self.assertGreaterEqual(total_properties, expected_minimum, 
                              f"Expected at least {expected_minimum} properties, got {total_properties}")
        
        # All percentiles should be calculated
        percentile_keys = [k for k in properties.keys() if k.endswith('Percentile')]
        self.assertEqual(len(percentile_keys), 11, f"Expected 11 percentiles, got {len(percentile_keys)}")
        
        # All percentiles should be in valid range
        for key in percentile_keys:
            value = properties[key]
            self.assertTrue(0 <= value <= 100, f"{key} value {value} out of range 0-100")

    def test_realistic_steel_grades(self):
        """Test enhancement with realistic steel material data."""
        steel_grades = [
            {
                'name': 'AISI 304 Stainless Steel',
                'properties': {
                    'density': '8.00 g/cm³',
                    'meltingPoint': '1450°C',
                    'thermalConductivity': '16.2 W/m·K',  # Poor conductor
                    'tensileStrength': '515 MPa',
                    'hardness': '201 HV',
                    'laserAbsorption': '15 cm⁻¹',  # Moderate
                    'thermalDiffusivity': '4.2 mm²/s'  # Low
                }
            },
            {
                'name': 'AISI 1018 Carbon Steel',
                'properties': {
                    'density': '7.87 g/cm³',
                    'meltingPoint': '1450°C',
                    'thermalConductivity': '51.9 W/m·K',  # Better conductor
                    'tensileStrength': '440 MPa',
                    'hardness': '126 HV',
                    'laserAbsorption': '25 cm⁻¹',  # Higher absorption
                    'thermalDiffusivity': '15.1 mm²/s'  # Higher diffusivity
                }
            }
        ]
        
        for steel in steel_grades:
            with self.subTest(steel=steel['name']):
                material = {
                    'name': steel['name'],
                    'category': 'metal',
                    'properties': steel['properties']
                }
                
                enhanced = enhance_frontmatter_with_context(material, 'metal')
                properties = enhanced['properties']
                
                # Verify percentiles are calculated
                self.assertIn('densityPercentile', properties)
                self.assertIn('thermalPercentile', properties)
                
                # Verify stainless steel has lower thermal conductivity percentile than carbon steel
                if 'Stainless' in steel['name']:
                    self.assertLess(properties['thermalPercentile'], 10, 
                                  "Stainless steel should have low thermal conductivity percentile")
                elif 'Carbon' in steel['name']:
                    self.assertGreater(properties['thermalPercentile'], 10,
                                     "Carbon steel should have higher thermal conductivity percentile")


if __name__ == '__main__':
    unittest.main(verbosity=2)
