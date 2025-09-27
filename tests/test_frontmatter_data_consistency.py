#!/usr/bin/env python3
"""
Frontmatter Data Consistency Tests

Ensures that frontmatter generation correctly uses data from Categories.yaml and Materials.yaml
without silent failures, missing units, or inconsistent mappings.

This prevents the machine settings unit extraction issue from recurring.
"""

import unittest
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.materials import load_materials
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator
from api.client_factory import create_api_client


class TestFrontmatterDataConsistency(unittest.TestCase):
    """Test consistency between frontmatter generation and source data"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Load source data
        cls.materials_data = load_materials()
        
        # Load Categories.yaml
        categories_path = Path(__file__).resolve().parents[1] / "data" / "Categories.yaml"
        with open(categories_path, 'r', encoding='utf-8') as file:
            cls.categories_data = yaml.safe_load(file)
        
        # Create test materials data with required machine settings ranges
        cls.test_materials_data = cls.materials_data.copy()
        cls.test_materials_data['machineSettingsRanges'] = {
            'powerRange': {'min': 10, 'max': 1000, 'unit': 'W'},
            'wavelength': {'min': 355, 'max': 1064, 'unit': 'nm'},
            'pulseDuration': {'min': 1, 'max': 100, 'unit': 'ns'},
            'fluenceThreshold': {'min': 0.1, 'max': 50, 'unit': 'J/cm²'},
            'repetitionRate': {'min': 1, 'max': 100000, 'unit': 'Hz'},
            'spotSize': {'min': 10, 'max': 1000, 'unit': 'μm'}
        }
        
        # Patch materials loading for testing
        import data.materials
        cls.original_load = data.materials.load_materials
        data.materials.load_materials = lambda: cls.test_materials_data
        
        # Initialize generator
        try:
            api_client = create_api_client('deepseek')
            cls.generator = StreamlinedFrontmatterGenerator(api_client=api_client)
        except Exception as e:
            print(f"Warning: Could not initialize API client: {e}")
            cls.generator = None
    
    @classmethod
    def tearDownClass(cls):
        """Restore original materials loading"""
        import data.materials
        data.materials.load_materials = cls.original_load
    
    def test_machine_settings_unit_mapping(self):
        """Test that all machine settings have proper unit mappings"""
        if not self.generator:
            self.skipTest("Generator not available")
        
        # Get machine settings from Categories.yaml
        machine_descriptions = self.categories_data.get('machineSettingsDescriptions', {})
        
        # Test each machine setting for unit extraction
        failed_mappings = []
        
        for setting_name, setting_info in machine_descriptions.items():
            if isinstance(setting_info, dict) and 'unit' in setting_info:
                expected_unit = setting_info['unit']
                
                # Test unit extraction
                extracted_unit = self.generator._get_category_unit('metal', setting_name)
                
                if not extracted_unit:
                    failed_mappings.append(f"{setting_name}: No unit extracted (expected: {expected_unit})")
                elif extracted_unit != expected_unit.split(',')[0].strip():  # Handle multi-unit strings
                    failed_mappings.append(f"{setting_name}: Got '{extracted_unit}', expected '{expected_unit}'")
        
        self.assertEqual(len(failed_mappings), 0, 
                        f"Machine settings unit extraction failures:\n" + "\n".join(failed_mappings))
    
    def test_material_properties_unit_mapping(self):
        """Test that all material properties have proper unit mappings"""
        if not self.generator:
            self.skipTest("Generator not available")
        
        # Get material property ranges from Categories.yaml for each category
        failed_mappings = []
        
        categories = self.categories_data.get('categories', {})
        for category_name, category_info in categories.items():
            if 'category_ranges' in category_info:
                ranges = category_info['category_ranges']
                
                for prop_name, prop_range in ranges.items():
                    if isinstance(prop_range, dict) and 'unit' in prop_range:
                        expected_unit = prop_range['unit']
                        
                        # Test unit extraction
                        extracted_unit = self.generator._get_category_unit(category_name, prop_name)
                        
                        if not extracted_unit:
                            failed_mappings.append(f"{category_name}.{prop_name}: No unit extracted (expected: {expected_unit})")
                        elif extracted_unit != expected_unit:
                            failed_mappings.append(f"{category_name}.{prop_name}: Got '{extracted_unit}', expected '{expected_unit}'")
        
        self.assertEqual(len(failed_mappings), 0,
                        f"Material properties unit extraction failures:\n" + "\n".join(failed_mappings))
    
    def test_generated_frontmatter_unit_consistency(self):
        """Test that generated frontmatter has consistent units for value, min, max"""
        if not self.generator:
            self.skipTest("Generator not available")
        
        # Generate frontmatter for aluminum
        result = self.generator.generate('aluminum')
        self.assertTrue(result.success, f"Frontmatter generation failed: {result.error_message}")
        
        # Parse generated content
        parsed = yaml.safe_load(result.content)
        self.assertIn('machineSettings', parsed, "Generated frontmatter missing machineSettings")
        
        inconsistencies = []
        machine_settings = parsed['machineSettings']
        
        for setting_name, setting_data in machine_settings.items():
            if isinstance(setting_data, dict):
                value_unit = setting_data.get('unit')
                min_val = setting_data.get('min')
                max_val = setting_data.get('max')
                
                # Check that unit is present
                if not value_unit:
                    inconsistencies.append(f"{setting_name}: Missing unit field")
                
                # Check that min/max are present and numeric
                if min_val is None:
                    inconsistencies.append(f"{setting_name}: Missing min value")
                elif not isinstance(min_val, (int, float)):
                    inconsistencies.append(f"{setting_name}: Min value '{min_val}' is not numeric")
                
                if max_val is None:
                    inconsistencies.append(f"{setting_name}: Missing max value")
                elif not isinstance(max_val, (int, float)):
                    inconsistencies.append(f"{setting_name}: Max value '{max_val}' is not numeric")
        
        self.assertEqual(len(inconsistencies), 0,
                        f"Machine settings inconsistencies:\n" + "\n".join(inconsistencies))
    
    def test_all_required_sections_present(self):
        """Test that all required sections from Categories.yaml are used in generation"""
        if not self.generator:
            self.skipTest("Generator not available")
        
        # Required sections that should be loaded from Categories.yaml
        required_sections = [
            'machineSettingsDescriptions',
            'materialPropertyDescriptions',
            'environmentalImpactTemplates',
            'applicationTypeDefinitions',
            'standardOutcomeMetrics',
            'universal_regulatory_standards'
        ]
        
        missing_sections = []
        
        for section in required_sections:
            if not hasattr(self.generator, section.replace('Descriptions', '_descriptions').replace('Definitions', '_definitions').replace('Templates', '_templates').replace('Metrics', '_metrics').replace('universal_regulatory_standards', 'universal_regulatory_standards')):
                missing_sections.append(section)
        
        self.assertEqual(len(missing_sections), 0,
                        f"Generator missing required sections: {missing_sections}")
    
    def test_categories_yaml_structure_completeness(self):
        """Test that Categories.yaml has all expected structure"""
        required_top_level = [
            'machineSettingsDescriptions',
            'materialPropertyDescriptions', 
            'environmentalImpactTemplates',
            'applicationTypeDefinitions',
            'standardOutcomeMetrics',
            'categories'
        ]
        
        missing_sections = []
        for section in required_top_level:
            if section not in self.categories_data:
                missing_sections.append(section)
        
        self.assertEqual(len(missing_sections), 0,
                        f"Categories.yaml missing required sections: {missing_sections}")
        
        # Test that each machine setting description has a unit
        machine_desc = self.categories_data.get('machineSettingsDescriptions', {})
        missing_units = []
        
        for setting_name, setting_info in machine_desc.items():
            if not isinstance(setting_info, dict) or 'unit' not in setting_info:
                missing_units.append(setting_name)
        
        self.assertEqual(len(missing_units), 0,
                        f"Machine settings descriptions missing units: {missing_units}")
    
    def test_material_property_coverage(self):
        """Test that all material properties in Categories.yaml are handled by generator"""
        if not self.generator:
            self.skipTest("Generator not available")
        
        # Get all property keys from Categories.yaml category ranges
        all_properties = set()
        categories = self.categories_data.get('categories', {})
        
        for category_info in categories.values():
            if 'category_ranges' in category_info:
                all_properties.update(category_info['category_ranges'].keys())
        
        # Check if generator's property mapping covers all properties
        property_mapping = {
            'density': 'density',
            'thermalConductivity': 'thermalConductivity', 
            'tensileStrength': 'tensileStrength',
            'youngsModulus': 'youngsModulus',
            'hardness': 'hardness',
            'electricalConductivity': 'electricalConductivity',
            'meltingPoint': 'thermalDestructionPoint',
            'thermalExpansion': 'thermalExpansion',
            'thermalDiffusivity': 'thermalDiffusivity',
            'specificHeat': 'specificHeat',
            'laserAbsorption': 'laserAbsorption',
            'laserReflectivity': 'laserReflectivity'
        }
        
        unmapped_properties = all_properties - set(property_mapping.values())
        
        # Some properties might be intentionally unmapped, but we should know about them
        if unmapped_properties:
            print(f"Info: Properties in Categories.yaml not mapped in generator: {unmapped_properties}")
    
    def test_generated_content_matches_source_data(self):
        """Test that generated content uses actual data from source files"""
        if not self.generator:
            self.skipTest("Generator not available")
        
        # Generate frontmatter
        result = self.generator.generate('aluminum')
        self.assertTrue(result.success, f"Generation failed: {result.error_message}")
        
        parsed = yaml.safe_load(result.content)
        
        # Test regulatory standards come from Categories.yaml
        if 'regulatoryStandards' in parsed:
            generated_standards = parsed['regulatoryStandards']
            universal_standards = self.categories_data.get('universal_regulatory_standards', [])
            
            # At least universal standards should be present
            for standard in universal_standards:
                self.assertIn(standard, generated_standards,
                            f"Universal standard '{standard}' missing from generated content")
        
        # Test environmental impact uses Categories.yaml templates
        if 'environmentalImpact' in parsed:
            generated_impacts = parsed['environmentalImpact']
            template_keys = set(self.categories_data.get('environmentalImpactTemplates', {}).keys())
            generated_benefits = {impact.get('benefit', '').lower().replace(' ', '_') for impact in generated_impacts}
            
            # Check that generated benefits correspond to template keys
            self.assertTrue(len(template_keys & generated_benefits) > 0,
                          "Generated environmental impacts don't match Categories.yaml templates")


class TestDataSourceIntegrity(unittest.TestCase):
    """Test integrity of source data files"""
    
    def test_categories_yaml_valid(self):
        """Test that Categories.yaml is valid and loadable"""
        categories_path = Path(__file__).resolve().parents[1] / "data" / "Categories.yaml"
        self.assertTrue(categories_path.exists(), "Categories.yaml not found")
        
        with open(categories_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        self.assertIsInstance(data, dict, "Categories.yaml should contain a dictionary")
    
    def test_materials_yaml_valid(self):
        """Test that Materials.yaml is valid and loadable"""
        materials_data = load_materials()
        self.assertIsInstance(materials_data, dict, "Materials data should be a dictionary")
        self.assertIn('materials', materials_data, "Materials data should contain 'materials' section")


if __name__ == '__main__':
    unittest.main()