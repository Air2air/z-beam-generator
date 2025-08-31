#!/usr/bin/env python3
"""
Comprehensive validation tests for Frontmatter v5.0.0 architecture.

Tests the clear separation between imported materials data and AI-generated content
as defined in the v5.0.0 prompt architecture.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.frontmatter.validator import (
    validate_frontmatter_yaml,
    validate_frontmatter_content,
    validate_frontmatter_properties
)
from components.frontmatter.mock_generator import generate_mock_frontmatter


class TestFrontmatterV5Architecture(unittest.TestCase):
    """Test suite for Frontmatter v5.0.0 architecture validation."""

    def setUp(self):
        """Set up test fixtures."""
        # Valid frontmatter following v5.0.0 architecture
        self.valid_frontmatter = '''---
name: "AISI 1018 Steel"
description: "Technical overview of AISI 1018 steel for laser cleaning applications"
author: "Dr. Materials Expert"
keywords: "steel, metal, laser cleaning, AISI 1018, carbon steel"
category: "metal"
chemicalProperties:
  symbol: "Fe"
  formula: "Fe-C"
  materialType: "alloy"
properties:
  density: "7.87 g/cm³"
  meltingPoint: "1450°C"
  thermalConductivity: "51.9 W/m·K"
  laserType: "Fiber laser"
  wavelength: "1064nm"
  fluenceRange: "2.0-8.0 J/cm²"
composition:
- "Iron: 98.8%"
- "Carbon: 0.18%"
compatibility:
- "Metals"
- "Alloys"
regulatoryStandards: "ISO 11553 Safety of machinery - Laser processing machines"
images:
  hero:
    alt: "Steel surface laser cleaning demonstration"
    url: "/images/steel-laser-cleaning.jpg"
  micro:
    alt: "Microscopic view of cleaned steel surface"
    url: "/images/steel-micro-clean.jpg"
title: "Laser Cleaning AISI 1018 Steel - Technical Guide"
headline: "Comprehensive technical guide for laser cleaning metal steel"
environmentalImpact:
- benefit: "Chemical-free cleaning"
  description: "Eliminates need for toxic solvents"
subject: "AISI 1018 Steel"
article_type: "material"
---'''

        # Invalid frontmatter with common issues
        self.invalid_frontmatter = '''---
name: "Test Material"
description: "TBD - need to fill this out"
properties:
  density: "TODO: add density"
  meltingPoint: "[placeholder]"
---'''

    def test_valid_frontmatter_passes_all_validation(self):
        """Test that valid v5.0.0 frontmatter passes all validation."""
        yaml_errors = validate_frontmatter_yaml(self.valid_frontmatter)
        content_errors = validate_frontmatter_content(self.valid_frontmatter)
        property_warnings = validate_frontmatter_properties(self.valid_frontmatter)
        
        self.assertEqual(len(yaml_errors), 0, f"Valid frontmatter should pass YAML validation, got: {yaml_errors}")
        self.assertEqual(len(content_errors), 0, f"Valid frontmatter should pass content validation, got: {content_errors}")
        self.assertEqual(len(property_warnings), 0, f"Valid frontmatter should pass property validation, got: {property_warnings}")

    def test_invalid_frontmatter_fails_validation(self):
        """Test that invalid frontmatter with placeholders fails validation."""
        content_errors = validate_frontmatter_content(self.invalid_frontmatter)
        
        self.assertGreater(len(content_errors), 0, "Invalid frontmatter with placeholders should fail validation")
        self.assertTrue(any("placeholder" in error.lower() for error in content_errors), 
                       "Should detect placeholder content")

    def test_mock_generator_produces_valid_frontmatter(self):
        """Test that mock generator produces frontmatter that passes validation."""
        mock_frontmatter = generate_mock_frontmatter("Test Steel", "metal")
        
        yaml_errors = validate_frontmatter_yaml(mock_frontmatter)
        content_errors = validate_frontmatter_content(mock_frontmatter)
        
        self.assertEqual(len(yaml_errors), 0, f"Mock frontmatter should be valid YAML, got: {yaml_errors}")
        self.assertEqual(len(content_errors), 0, f"Mock frontmatter should pass content validation, got: {content_errors}")

    def test_required_v5_architecture_fields(self):
        """Test that frontmatter contains required fields per v5.0.0 architecture."""
        import yaml
        
        yaml_content = self.valid_frontmatter[3:self.valid_frontmatter.rfind('---')].strip()
        parsed = yaml.safe_load(yaml_content)
        
        # Core identification fields (AI generated)
        self.assertIn('name', parsed)
        self.assertIn('description', parsed)
        self.assertIn('author', parsed)
        self.assertIn('category', parsed)
        
        # Technical properties (AI generated with materials data context)
        self.assertIn('properties', parsed)
        self.assertIn('chemicalProperties', parsed)
        
        # Imported data fields (from materials list)
        properties = parsed['properties']
        self.assertIn('laserType', properties, "Should include laser parameters from materials list")
        self.assertIn('wavelength', properties, "Should include wavelength from materials list")
        self.assertIn('fluenceRange', properties, "Should include fluence from materials list")
        
        # AI-generated content
        self.assertIn('environmentalImpact', parsed, "Should include AI-generated environmental impact")
        self.assertIn('composition', parsed, "Should include AI-generated composition")

    def test_data_separation_validation(self):
        """Test validation of clear separation between imported and generated data."""
        # This tests the architectural principle that some data comes from materials list
        # and other data is AI-generated
        
        import yaml
        yaml_content = self.valid_frontmatter[3:self.valid_frontmatter.rfind('---')].strip()
        parsed = yaml.safe_load(yaml_content)
        
        # Imported data should be present (from materials list)
        properties = parsed['properties']
        imported_fields = ['wavelength', 'laserType', 'fluenceRange']
        for field in imported_fields:
            self.assertIn(field, properties, f"Should contain imported field: {field}")
        
        # AI-generated data should be present
        ai_generated_fields = ['environmentalImpact', 'composition', 'description']
        for field in ai_generated_fields:
            self.assertIn(field, parsed, f"Should contain AI-generated field: {field}")

    def test_yaml_structure_integrity(self):
        """Test YAML structure follows expected patterns."""
        # Test for common YAML issues our validator should catch
        
        bad_yaml_samples = [
            "---\n---\nname: Test",  # Multiple opening delimiters
            "---\nproperties: {}\n---",  # Empty object placeholders
            "---\nname: Test",  # Missing closing delimiter
        ]
        
        for bad_yaml in bad_yaml_samples:
            errors = validate_frontmatter_yaml(bad_yaml)
            self.assertGreater(len(errors), 0, f"Should detect errors in: {bad_yaml[:20]}...")

    def test_mock_generator_architecture_compliance(self):
        """Test that mock generator follows v5.0.0 architecture principles."""
        mock_content = generate_mock_frontmatter("Aluminum", "metal")
        
        import yaml
        yaml_content = mock_content[3:mock_content.rfind('---')].strip()
        parsed = yaml.safe_load(yaml_content)
        
        # Should contain both imported-style and AI-generated content
        self.assertIn('properties', parsed)
        self.assertIn('wavelength', parsed['properties'], "Mock should simulate imported laser data")
        self.assertIn('environmentalImpact', parsed, "Mock should simulate AI-generated content")
        
        # Validate realistic data types
        self.assertIsInstance(parsed['environmentalImpact'], list, "Environmental impact should be list")
        self.assertIsInstance(parsed['composition'], list, "Composition should be list")


if __name__ == '__main__':
    unittest.main()
