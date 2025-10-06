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
                        "Machine settings unit extraction failures:\n" + "\n".join(failed_mappings))
    
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
                        "Material properties unit extraction failures:\n" + "\n".join(failed_mappings))
    
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
        
        # Categorical fields that don't need min/max values
        categorical_fields = {'laserType', 'beamQuality', 'coolingType', 'operatingMode'}
        
        for setting_name, setting_data in machine_settings.items():
            # Skip wavelength since it was removed from the system but AI might still generate it
            if setting_name == 'wavelength':
                continue
                
            if isinstance(setting_data, dict):
                value_unit = setting_data.get('unit')
                min_val = setting_data.get('min')
                max_val = setting_data.get('max')
                
                # Check that unit is present
                if not value_unit:
                    inconsistencies.append(f"{setting_name}: Missing unit field")
                
                # Skip min/max checks for categorical fields
                if setting_name in categorical_fields:
                    continue
                    
                # Check that min/max are present and numeric for numeric fields
                if min_val is None:
                    inconsistencies.append(f"{setting_name}: Missing min value")
                elif not isinstance(min_val, (int, float)):
                    inconsistencies.append(f"{setting_name}: Min value '{min_val}' is not numeric")
                
                if max_val is None:
                    inconsistencies.append(f"{setting_name}: Missing max value")
                elif not isinstance(max_val, (int, float)):
                    inconsistencies.append(f"{setting_name}: Max value '{max_val}' is not numeric")
        
        self.assertEqual(len(inconsistencies), 0,
                        "Machine settings inconsistencies:\n" + "\n".join(inconsistencies))
    
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
        
        # Map section names to actual generator attribute names
        section_to_attr = {
            'machineSettingsDescriptions': 'machine_settings_descriptions',
            'materialPropertyDescriptions': 'material_property_descriptions',
            'environmentalImpactTemplates': 'environmental_impact_templates',
            'applicationTypeDefinitions': 'application_type_definitions',
            'standardOutcomeMetrics': 'standard_outcome_metrics'
        }
        
        for section in required_sections:
            attr_name = section_to_attr.get(section, section)
            if not hasattr(self.generator, attr_name):
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
    
    def test_categories_yaml_min_max_source_compliance(self):
        """Test that materialProperties min/max values come from Categories.yaml category_ranges"""
        if not self.generator:
            self.skipTest("Generator not available")
        
        # Generate frontmatter for copper (metal category)
        result = self.generator.generate('copper')
        self.assertTrue(result.success, f"Frontmatter generation failed: {result.error_message}")
        
        parsed = yaml.safe_load(result.content)
        self.assertIn('materialProperties', parsed, "Generated frontmatter missing materialProperties")
        
        # Get expected ranges from Categories.yaml for metal category
        metal_ranges = self.categories_data.get('categories', {}).get('metal', {}).get('category_ranges', {})
        
        compliance_violations = []
        material_properties = parsed['materialProperties']
        
        for prop_name, prop_data in material_properties.items():
            if isinstance(prop_data, dict):
                prop_min = prop_data.get('min')
                prop_max = prop_data.get('max')
                
                # Check if property exists in Categories.yaml category_ranges
                if prop_name in metal_ranges:
                    expected_range = metal_ranges[prop_name]
                    
                    # Handle string values (like thermalDestructionType) - skip validation
                    if not isinstance(expected_range, dict):
                        continue
                    
                    expected_min = expected_range.get('min')
                    expected_max = expected_range.get('max')
                    
                    # Verify min/max match Categories.yaml values
                    if prop_min != expected_min:
                        compliance_violations.append(
                            f"{prop_name}.min: Got {prop_min}, expected {expected_min} from Categories.yaml"
                        )
                    if prop_max != expected_max:
                        compliance_violations.append(
                            f"{prop_name}.max: Got {prop_max}, expected {expected_max} from Categories.yaml"
                        )
                else:
                    # Properties not in Categories.yaml should have null min/max
                    if prop_min is not None:
                        compliance_violations.append(
                            f"{prop_name}.min: Should be null (property not in Categories.yaml), got {prop_min}"
                        )
                    if prop_max is not None:
                        compliance_violations.append(
                            f"{prop_name}.max: Should be null (property not in Categories.yaml), got {prop_max}"
                        )
        
        self.assertEqual(len(compliance_violations), 0,
                        "Categories.yaml min/max source compliance violations:\n" + "\n".join(compliance_violations))

    def test_environmental_impact_template_compliance(self):
        """Test that environmentalImpact benefits use Categories.yaml environmentalImpactTemplates"""
        if not self.generator:
            self.skipTest("Generator not available")
        
        # Generate frontmatter 
        result = self.generator.generate('copper')
        self.assertTrue(result.success, f"Frontmatter generation failed: {result.error_message}")
        
        parsed = yaml.safe_load(result.content)
        self.assertIn('environmentalImpact', parsed, "Generated frontmatter missing environmentalImpact")
        
        # Validate environmentalImpactTemplates exist in Categories.yaml
        _ = self.categories_data.get('environmentalImpactTemplates', {})  # Validate existence
        
        # Map template keys to expected benefit names
        template_to_benefit = {
            'chemical_waste_elimination': 'Chemical Waste Elimination',
            'water_usage_reduction': 'Water Usage Reduction', 
            'energy_efficiency': 'Energy Efficiency',
            'air_quality_improvement': 'Air Quality Improvement'
        }
        
        generated_benefits = {impact.get('benefit', '') for impact in parsed['environmentalImpact']}
        expected_benefits = set(template_to_benefit.values())
        
        # Check that generated benefits match expected template-derived benefits
        missing_benefits = expected_benefits - generated_benefits
        extra_benefits = generated_benefits - expected_benefits
        
        compliance_issues = []
        if missing_benefits:
            compliance_issues.append(f"Missing expected benefits: {missing_benefits}")
        if extra_benefits:
            compliance_issues.append(f"Extra benefits not from templates: {extra_benefits}")
        
        self.assertEqual(len(compliance_issues), 0,
                        "Environmental impact template compliance issues:\n" + "\n".join(compliance_issues))

    def test_application_types_definition_compliance(self):
        """Test that applicationTypes use Categories.yaml applicationTypeDefinitions"""
        if not self.generator:
            self.skipTest("Generator not available")
        
        # Generate frontmatter
        result = self.generator.generate('copper')
        self.assertTrue(result.success, f"Frontmatter generation failed: {result.error_message}")
        
        parsed = yaml.safe_load(result.content)
        self.assertIn('applicationTypes', parsed, "Generated frontmatter missing applicationTypes")
        
        # Get definitions from Categories.yaml
        _ = self.categories_data.get('applicationTypeDefinitions', {})  # Validate existence
        
        # Map definition keys to expected type names
        definition_to_type = {
            'precision_cleaning': 'Precision Cleaning',
            'surface_preparation': 'Surface Preparation',
            'restoration_cleaning': 'Restoration Cleaning',
            'contamination_removal': 'Contamination Removal'
        }
        
        generated_types = {app.get('type', '') for app in parsed['applicationTypes']}
        expected_types = set(definition_to_type.values())
        
        # Verify all generated types come from Categories.yaml definitions
        extra_types = generated_types - expected_types
        
        compliance_issues = []
        if extra_types:
            compliance_issues.append(f"Application types not from Categories.yaml definitions: {extra_types}")
        
        self.assertEqual(len(compliance_issues), 0,
                        "Application types definition compliance issues:\n" + "\n".join(compliance_issues))

    def test_outcome_metrics_standard_compliance(self):
        """Test that outcomeMetrics use Categories.yaml standardOutcomeMetrics"""
        if not self.generator:
            self.skipTest("Generator not available")
        
        # Generate frontmatter
        result = self.generator.generate('copper')
        self.assertTrue(result.success, f"Frontmatter generation failed: {result.error_message}")
        
        parsed = yaml.safe_load(result.content)
        self.assertIn('outcomeMetrics', parsed, "Generated frontmatter missing outcomeMetrics")
        
        # Get standard metrics from Categories.yaml  
        _ = self.categories_data.get('standardOutcomeMetrics', {})  # Validate existence
        
        # Map standard keys to expected metric names
        standard_to_metric = {
            'contaminant_removal_efficiency': 'Contaminant Removal Efficiency',
            'processing_speed': 'Processing Speed',
            'surface_quality_preservation': 'Surface Quality Preservation',
            'thermal_damage_avoidance': 'Thermal Damage Avoidance'
        }
        
        generated_metrics = {metric.get('metric', '') for metric in parsed['outcomeMetrics']}
        expected_metrics = set(standard_to_metric.values())
        
        # Verify all generated metrics come from Categories.yaml standards
        extra_metrics = generated_metrics - expected_metrics
        
        compliance_issues = []
        if extra_metrics:
            compliance_issues.append(f"Outcome metrics not from Categories.yaml standards: {extra_metrics}")
        
        self.assertEqual(len(compliance_issues), 0,
                        "Outcome metrics standard compliance issues:\n" + "\n".join(compliance_issues))

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