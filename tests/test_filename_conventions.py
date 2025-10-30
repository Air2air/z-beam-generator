#!/usr/bin/env python3
"""
Test filename conventions for Z-Beam Generator.

This test suite validates that:
1. Material names with spaces are properly converted to hyphenated filenames
2. All generated files follow the consistent naming pattern
3. The filename generation logic is working correctly across all components

Based on docs/DATA_SOURCES.md File Naming Conventions section.
"""

import unittest
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup to resolve module
from commands.research import generate_safe_filename  # noqa: E402


class TestFilenameConventions(unittest.TestCase):
    """Test that filename conventions are properly applied."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_materials = [
            "Stainless Steel",
            "Carbon Steel", 
            "Cast Iron",
            "Aluminum 6061",
            "Ti-6Al-4V",
            "Inconel 625",
            "Brass C360"
        ]
        
    def test_space_to_hyphen_conversion(self):
        """Test that spaces in material names are converted to hyphens."""
        test_cases = [
            ("Stainless Steel", "stainless-steel"),
            ("Carbon Steel", "carbon-steel"),
            ("Cast Iron", "cast-iron"),
            ("Aluminum 6061", "aluminum-6061"),
            ("Brass C360", "brass-c360")
        ]
        
        for material_name, expected_safe_name in test_cases:
            with self.subTest(material=material_name):
                safe_name = generate_safe_filename(material_name)
                self.assertEqual(safe_name, expected_safe_name)
                
    def test_special_characters_handling(self):
        """Test that special characters are properly handled in filenames."""
        test_cases = [
            ("Ti-6Al-4V", "ti-6al-4v"),
            ("Inconel 625", "inconel-625"),
            ("AISI 304", "aisi-304"),
            ("A36 Steel", "a36-steel")
        ]
        
        for material_name, expected_safe_name in test_cases:
            with self.subTest(material=material_name):
                safe_name = generate_safe_filename(material_name)
                self.assertEqual(safe_name, expected_safe_name)
                
    def test_filename_patterns(self):
        """Test that complete filename patterns are correctly generated."""
        material = "Stainless Steel"
        safe_name = generate_safe_filename(material)
        
        # Test various file patterns
        expected_patterns = {
            'frontmatter': f"{safe_name}-laser-cleaning.yaml",
            'markdown': f"{safe_name}-laser-cleaning.md",
            'image_hero': f"/images/{safe_name}-laser-cleaning-hero.jpg",
            'image_micro': f"/images/{safe_name}-laser-cleaning-micro.jpg"
        }
        
        # Verify patterns match expected format
        self.assertEqual(expected_patterns['frontmatter'], "stainless-steel-laser-cleaning.yaml")
        self.assertEqual(expected_patterns['markdown'], "stainless-steel-laser-cleaning.md")
        self.assertEqual(expected_patterns['image_hero'], "/images/stainless-steel-laser-cleaning-hero.jpg")
        self.assertEqual(expected_patterns['image_micro'], "/images/stainless-steel-laser-cleaning-micro.jpg")
        
    def test_case_normalization(self):
        """Test that uppercase material names are normalized to lowercase."""
        test_cases = [
            ("STAINLESS STEEL", "stainless-steel"),
            ("ALUMINUM", "aluminum"),
            ("CARBON STEEL", "carbon-steel"),
            ("Ti-6Al-4V", "ti-6al-4v")
        ]
        
        for material_name, expected_safe_name in test_cases:
            with self.subTest(material=material_name):
                safe_name = generate_safe_filename(material_name)
                self.assertEqual(safe_name, expected_safe_name)
                
    def test_consistent_filename_generation(self):
        """Test that filename generation is consistent across calls."""
        material = "Stainless Steel"
        
        # Generate filename multiple times
        filenames = [generate_safe_filename(material) for _ in range(5)]
        
        # All should be identical
        self.assertTrue(all(fn == filenames[0] for fn in filenames))
        self.assertEqual(filenames[0], "stainless-steel")
        
    def test_no_double_hyphens(self):
        """Test that multiple spaces don't create double hyphens."""
        test_cases = [
            ("Stainless  Steel", "stainless-steel"),  # Double space
            ("Carbon   Steel", "carbon-steel"),      # Triple space
            ("Cast    Iron", "cast-iron")           # Quad space
        ]
        
        for material_name, expected_safe_name in test_cases:
            with self.subTest(material=material_name):
                safe_name = generate_safe_filename(material_name)
                self.assertEqual(safe_name, expected_safe_name)
                # Ensure no double hyphens
                self.assertNotIn("--", safe_name)


class TestFilenameConventionsIntegration(unittest.TestCase):
    """Integration tests for filename conventions across the system."""
    
    def test_image_url_generation(self):
        """Test that image URLs follow hyphenated naming convention."""
        # This test validates the pattern used in image generation
        material = "Stainless Steel"
        safe_name = generate_safe_filename(material)
        
        hero_url = f"/images/{safe_name}-laser-cleaning-hero.jpg"
        micro_url = f"/images/{safe_name}-laser-cleaning-micro.jpg"
        
        self.assertEqual(hero_url, "/images/stainless-steel-laser-cleaning-hero.jpg")
        self.assertEqual(micro_url, "/images/stainless-steel-laser-cleaning-micro.jpg")
        
    def test_frontmatter_filename_generation(self):
        """Test that frontmatter files use hyphenated naming."""
        material = "Stainless Steel"
        safe_name = generate_safe_filename(material)
        
        frontmatter_filename = f"{safe_name}-laser-cleaning.yaml"
        self.assertEqual(frontmatter_filename, "stainless-steel-laser-cleaning.yaml")
        
    def test_markdown_filename_generation(self):
        """Test that markdown files use hyphenated naming."""
        material = "Stainless Steel"
        safe_name = generate_safe_filename(material)
        
        markdown_filename = f"{safe_name}-laser-cleaning.md"
        self.assertEqual(markdown_filename, "stainless-steel-laser-cleaning.md")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)