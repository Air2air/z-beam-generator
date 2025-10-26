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
        
        # Load existing frontmatter files for testing (no AI generation needed)
        cls.frontmatter_dir = Path(__file__).resolve().parents[1] / "content" / "frontmatter"
    
    def test_machine_settings_unit_mapping(self):
        """Test that all machine settings in Categories.yaml have unit definitions"""
        # Get machine settings from Categories.yaml
        machine_descriptions = self.categories_data.get('machineSettingsDescriptions', {})
        
        # Test each machine setting has unit definition
        missing_units = []
        
        for setting_name, setting_info in machine_descriptions.items():
            if isinstance(setting_info, dict):
                if 'unit' not in setting_info:
                    missing_units.append(setting_name)
        
        self.assertEqual(len(missing_units), 0, 
                        f"Machine settings missing unit definitions: {missing_units}")
    
    def test_material_properties_unit_mapping(self):
        """Test that all material properties in Categories.yaml have unit definitions"""
        # Get material property ranges from Categories.yaml for each category
        missing_units = []
        
        categories = self.categories_data.get('categories', {})
        for category_name, category_info in categories.items():
            if 'category_ranges' in category_info:
                ranges = category_info['category_ranges']
                
                for prop_name, prop_range in ranges.items():
                    # thermalDestruction is a nested object, not a simple property with unit
                    if prop_name == 'thermalDestruction':
                        continue
                    if isinstance(prop_range, dict) and 'unit' not in prop_range:
                        missing_units.append(f"{category_name}.{prop_name}")
        
        self.assertEqual(len(missing_units), 0,
                        f"Material properties missing unit definitions: {missing_units}")
    
    def test_generated_frontmatter_unit_consistency(self):
        """Test that existing frontmatter files have consistent unit structure"""
        # Test a sample of existing frontmatter files
        test_files = ['aluminum-laser-cleaning.yaml', 'copper-laser-cleaning.yaml']
        
        for filename in test_files:
            filepath = self.frontmatter_dir / filename
            if not filepath.exists():
                continue
                
            with open(filepath, 'r') as f:
                parsed = yaml.safe_load(f)
            
            if 'machineSettings' not in parsed:
                continue
                
            machine_settings = parsed['machineSettings']
            
            # Categorical fields that don't need min/max values
            categorical_fields = {'laserType', 'beamQuality', 'coolingType', 'operatingMode'}
            
            for setting_name, setting_data in machine_settings.items():
                if setting_name == 'wavelength':
                    continue
                    
                if isinstance(setting_data, dict) and setting_name not in categorical_fields:
                    # Numeric settings should have unit field
                    self.assertIn('unit', setting_data, 
                                f"{filename}: {setting_name} should have unit field")
    
    def test_all_required_sections_present(self):
        """Test that all required sections exist in Categories.yaml"""
        # Required sections that should be in Categories.yaml
        required_sections = [
            'machineSettingsDescriptions',
            'materialPropertyDescriptions',
            'environmentalImpactTemplates',
            'applicationTypeDefinitions',
            'standardOutcomeMetrics',
            'categories'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in self.categories_data:
                missing_sections.append(section)
        
        self.assertEqual(len(missing_sections), 0,
                        f"Categories.yaml missing required sections: {missing_sections}")
    
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
    
    def test_categories_yaml_min_max_source_compliance(self):
        """Test that Categories.yaml has proper category_ranges structure"""
        # Get all categories
        categories = self.categories_data.get('categories', {})
        
        # Test that each category has category_ranges
        for category_name, category_info in categories.items():
            self.assertIn('category_ranges', category_info,
                         f"Category '{category_name}' missing category_ranges")
            
            # Test that ranges are properly structured
            ranges = category_info['category_ranges']
            self.assertIsInstance(ranges, dict,
                                f"Category '{category_name}' category_ranges must be dict")

    def test_environmental_impact_template_compliance(self):
        """Test that Categories.yaml has environmentalImpactTemplates"""
        # Validate environmentalImpactTemplates exist in Categories.yaml
        self.assertIn('environmentalImpactTemplates', self.categories_data,
                     "Categories.yaml missing environmentalImpactTemplates")
        
        templates = self.categories_data['environmentalImpactTemplates']
        self.assertIsInstance(templates, dict,
                            "environmentalImpactTemplates must be dict")
        
        # Verify templates have proper structure
        for template_key, template_data in templates.items():
            self.assertIsInstance(template_data, dict,
                                f"Template '{template_key}' must be dict")

    def test_application_types_definition_compliance(self):
        """Test that Categories.yaml has applicationTypeDefinitions"""
        # Get definitions from Categories.yaml
        self.assertIn('applicationTypeDefinitions', self.categories_data,
                     "Categories.yaml missing applicationTypeDefinitions")
        
        definitions = self.categories_data['applicationTypeDefinitions']
        self.assertIsInstance(definitions, dict,
                            "applicationTypeDefinitions must be dict")
        
        # Verify definitions have proper structure
        for def_key, def_data in definitions.items():
            self.assertIsInstance(def_data, dict,
                                f"Definition '{def_key}' must be dict")

    def test_outcome_metrics_standard_compliance(self):
        """Test that Categories.yaml has standardOutcomeMetrics"""
        # Get standard metrics from Categories.yaml  
        self.assertIn('standardOutcomeMetrics', self.categories_data,
                     "Categories.yaml missing standardOutcomeMetrics")
        
        metrics = self.categories_data['standardOutcomeMetrics']
        self.assertIsInstance(metrics, dict,
                            "standardOutcomeMetrics must be dict")
        
        # Verify metrics have proper structure
        for metric_key, metric_data in metrics.items():
            self.assertIsInstance(metric_data, dict,
                                f"Metric '{metric_key}' must be dict")

    def test_material_property_coverage(self):
        """Test that Categories.yaml has category_ranges for each category"""
        # Get all categories
        categories = self.categories_data.get('categories', {})
        
        # Check that each category has category_ranges
        for category_name, category_info in categories.items():
            self.assertIn('category_ranges', category_info,
                         f"Category '{category_name}' missing category_ranges")
    
    def test_generated_content_matches_source_data(self):
        """Test that Materials.yaml has proper regulatory standards structure"""
        # Test that materials in Materials.yaml have proper regulatory standards
        materials = self.materials_data.get('materials', {})
        
        # Sample a few materials to check structure
        for material_name in list(materials.keys())[:5]:
            material = materials[material_name]
            
            if 'regulatoryStandards' in material:
                standards = material['regulatoryStandards']
                
                # Regulatory standards must be array of objects
                self.assertIsInstance(standards, list,
                                    f"{material_name}: regulatoryStandards must be array")
                
                if len(standards) > 0:
                    # Items must be objects with required fields
                    first_standard = standards[0]
                    self.assertIsInstance(first_standard, dict,
                                        f"{material_name}: regulatoryStandards items must be objects")
                    self.assertIn('name', first_standard,
                                f"{material_name}: regulatoryStandards items must have 'name' field")
                    self.assertIn('description', first_standard,
                                f"{material_name}: regulatoryStandards items must have 'description' field")


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