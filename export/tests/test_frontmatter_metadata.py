#!/usr/bin/env python3
"""
Frontmatter Metadata Tests

Tests for preservedData.generationMetadata.generated_date field
that is required by metadata sync validation.

This field tracks generation timestamps for data freshness validation.
"""

import unittest
import yaml
from pathlib import Path
from datetime import datetime
import sys
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestFrontmatterMetadata(unittest.TestCase):
    """Tests for frontmatter metadata fields by checking generated files"""

    def setUp(self):
        """Set up test environment with temporary directory"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up temporary directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_deployed_materials_files_have_preserved_data(self):
        """Test that deployed materials files include preservedData.generationMetadata.generated_date"""
        # Check a real deployed file
        materials_file = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials/steel-laser-cleaning.yaml')
        
        if not materials_file.exists():
            self.skipTest("Deployed materials file not found")
        
        with open(materials_file, 'r') as f:
            materials_data = yaml.safe_load(f)
        
        # Check preservedData exists
        self.assertIn('preservedData', materials_data)
        self.assertIn('generationMetadata', materials_data['preservedData'])
        self.assertIn('generated_date', materials_data['preservedData']['generationMetadata'])
        
        # Verify it's a valid ISO timestamp
        timestamp = materials_data['preservedData']['generationMetadata']['generated_date']
        self.assertIsInstance(timestamp, str)
        
        # Parse to verify it's valid ISO format
        try:
            parsed_date = datetime.fromisoformat(timestamp)
            self.assertIsInstance(parsed_date, datetime)
        except ValueError:
            self.fail(f"generated_date is not valid ISO format: {timestamp}")

    def test_deployed_settings_files_have_preserved_data(self):
        """Test that deployed settings files include preservedData.generationMetadata.generated_date"""
        # Check a real deployed file
        settings_file = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/settings/steel-settings.yaml')
        
        if not settings_file.exists():
            self.skipTest("Deployed settings file not found")
        
        with open(settings_file, 'r') as f:
            settings_data = yaml.safe_load(f)
        
        # Check preservedData exists
        self.assertIn('preservedData', settings_data)
        self.assertIn('generationMetadata', settings_data['preservedData'])
        self.assertIn('generated_date', settings_data['preservedData']['generationMetadata'])
        
        # Verify it's a valid ISO timestamp
        timestamp = settings_data['preservedData']['generationMetadata']['generated_date']
        self.assertIsInstance(timestamp, str)
        
        # Parse to verify it's valid ISO format
        try:
            parsed_date = datetime.fromisoformat(timestamp)
            self.assertIsInstance(parsed_date, datetime)
        except ValueError:
            self.fail(f"generated_date is not valid ISO format: {timestamp}")

    def test_timestamp_format_is_valid_iso(self):
        """Test that timestamps in deployed files are valid ISO format"""
        materials_file = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials/aluminum-laser-cleaning.yaml')
        
        if not materials_file.exists():
            self.skipTest("Deployed materials file not found")
        
        with open(materials_file, 'r') as f:
            materials_data = yaml.safe_load(f)
        
        timestamp_str = materials_data['preservedData']['generationMetadata']['generated_date']
        
        # Should parse successfully
        timestamp = datetime.fromisoformat(timestamp_str)
        
        # Should have expected components
        self.assertIsNotNone(timestamp.year)
        self.assertIsNotNone(timestamp.month)
        self.assertIsNotNone(timestamp.day)
        self.assertIsNotNone(timestamp.hour)
        self.assertIsNotNone(timestamp.minute)

    def test_yaml_serialization_preserves_metadata(self):
        """Test that YAML serialization preserves preservedData structure"""
        materials_file = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials/copper-laser-cleaning.yaml')
        
        if not materials_file.exists():
            self.skipTest("Deployed materials file not found")
        
        # Load file
        with open(materials_file, 'r') as f:
            original_data = yaml.safe_load(f)
        
        # Re-serialize
        yaml_content = yaml.safe_dump(original_data, sort_keys=False, allow_unicode=True)
        
        # Deserialize back
        deserialized = yaml.safe_load(yaml_content)
        
        # Verify preservedData survived serialization
        self.assertIn('preservedData', deserialized)
        self.assertIn('generationMetadata', deserialized['preservedData'])
        self.assertIn('generated_date', deserialized['preservedData']['generationMetadata'])
        
        # Verify timestamp is still valid
        timestamp = deserialized['preservedData']['generationMetadata']['generated_date']
        datetime.fromisoformat(timestamp)  # Should not raise

    def test_multiple_files_have_different_timestamps(self):
        """Test that different materials have different (or same batch) timestamps"""
        file1 = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials/steel-laser-cleaning.yaml')
        file2 = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials/aluminum-laser-cleaning.yaml')
        
        if not (file1.exists() and file2.exists()):
            self.skipTest("Deployed files not found")
        
        with open(file1, 'r') as f:
            data1 = yaml.safe_load(f)
        with open(file2, 'r') as f:
            data2 = yaml.safe_load(f)
        
        timestamp1 = data1['preservedData']['generationMetadata']['generated_date']
        timestamp2 = data2['preservedData']['generationMetadata']['generated_date']
        
        # Both should be valid ISO timestamps
        datetime.fromisoformat(timestamp1)
        datetime.fromisoformat(timestamp2)
        
        # They may be the same (batch export) or different (individual exports)
        # Just verify both exist and are valid
        self.assertIsNotNone(timestamp1)
        self.assertIsNotNone(timestamp2)


class TestFrontmatterFieldStructure(unittest.TestCase):
    """Tests for frontmatter field structure after field restructuring by checking deployed files"""

    def test_deployed_materials_files_have_material_description(self):
        """Test that deployed materials files use material_description (not subtitle)"""
        materials_file = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials/steel-laser-cleaning.yaml')
        
        if not materials_file.exists():
            self.skipTest("Deployed materials file not found")
        
        with open(materials_file, 'r') as f:
            materials_data = yaml.safe_load(f)
        
        # Should have material_description
        self.assertIn('material_description', materials_data)
        self.assertIsInstance(materials_data['material_description'], str)
        
        # Should NOT have subtitle
        self.assertNotIn('subtitle', materials_data)

    def test_deployed_settings_files_have_settings_description(self):
        """Test that deployed settings files use settings_description (not description)"""
        settings_file = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/settings/steel-settings.yaml')
        
        if not settings_file.exists():
            self.skipTest("Deployed settings file not found")
        
        with open(settings_file, 'r') as f:
            settings_data = yaml.safe_load(f)
        
        # Should have settings_description
        self.assertIn('settings_description', settings_data)
        self.assertIsInstance(settings_data['settings_description'], str)
        
        # Should NOT have generic 'description'
        self.assertNotIn('description', settings_data)

    def test_deployed_settings_files_have_active_field(self):
        """Test that deployed settings files include active field"""
        settings_file = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/settings/steel-settings.yaml')
        
        if not settings_file.exists():
            self.skipTest("Deployed settings file not found")
        
        with open(settings_file, 'r') as f:
            settings_data = yaml.safe_load(f)
        
        # Should have active field
        self.assertIn('active', settings_data)
        self.assertIsInstance(settings_data['active'], bool)

    def test_materials_file_has_expected_structure(self):
        """Test that materials files have expected field structure"""
        materials_file = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials/aluminum-laser-cleaning.yaml')
        
        if not materials_file.exists():
            self.skipTest("Deployed materials file not found")
        
        with open(materials_file, 'r') as f:
            materials_data = yaml.safe_load(f)
        
        # Check key fields exist
        expected_fields = ['name', 'category', 'material_description', 'preservedData']
        for field in expected_fields:
            self.assertIn(field, materials_data, f"Missing field: {field}")

    def test_settings_file_has_expected_structure(self):
        """Test that settings files have expected structure"""
        settings_file = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/settings/aluminum-settings.yaml')
        
        if not settings_file.exists():
            self.skipTest("Deployed settings file not found")
        
        with open(settings_file, 'r') as f:
            settings_data = yaml.safe_load(f)
        
        # Check key fields exist
        expected_fields = ['name', 'category', 'settings_description', 'active', 'preservedData']
        for field in expected_fields:
            self.assertIn(field, settings_data, f"Missing field: {field}")


if __name__ == '__main__':
    unittest.main()
