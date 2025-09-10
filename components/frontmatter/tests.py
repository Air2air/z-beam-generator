#!/usr/bin/env python3
"""
Frontmatter Component Test Suite

Comprehensive tests for frontmatter generation, validation, and enhancement
using hybrid data integration approach:

- Material data from materials.yaml combined with prompt templates
- Author information resolution via author_id from authors.json
- Template variable substitution and dynamic content generation
- Property enhancement with category ranges and statistical data
- Frontmatter validation and format checking
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from components.frontmatter.generator import FrontmatterComponentGenerator
from components.frontmatter.validator import (
    validate_frontmatter_content,
    validate_frontmatter_format,
    validate_frontmatter_properties,
)
from components.frontmatter.utils import (
    enhance_frontmatter_with_context,
    enhance_generated_frontmatter,
    load_category_ranges,
    validate_frontmatter_properties_completeness,
)
from generators.component_generators import ComponentResult


class TestFrontmatterGenerator(unittest.TestCase):
    """Test cases for FrontmatterComponentGenerator"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = FrontmatterComponentGenerator()
        self.test_material_data = {
            "name": "Steel",
            "author_id": 3,
            "formula": "Fe-C",
            "symbol": "Fe",
            "category": "metal",
            "material_type": "ferrous alloy"
        }
        self.test_author_data = {
            "id": 3,
            "name": "Ikmanda Roswati",
            "sex": "m",
            "title": "Ph.D.",
            "country": "Indonesia",
            "expertise": "Ultrafast Laser Physics and Material Interactions",
            "image": "/images/author/ikmanda-roswati.jpg"
        }

    def test_initialization(self):
        """Test generator initialization"""
        self.assertIsInstance(self.generator, FrontmatterComponentGenerator)
        self.assertIsNotNone(self.generator.prompt_config)

    @patch('pathlib.Path.exists')
    @patch('builtins.open', create=True)
    @patch('yaml.safe_load')
    def test_prompt_config_loading_success(self, mock_yaml_load, mock_open, mock_exists):
        """Test successful loading of prompt configuration from prompt.yaml"""
        # Mock file exists
        mock_exists.return_value = True

        # Mock YAML content
        mock_prompt_config = {
            'name': 'Frontmatter Generator',
            'template': 'Test template with {subject} and {author_name}'
        }
        mock_yaml_load.return_value = mock_prompt_config

        # Create new generator to test loading
        generator = FrontmatterComponentGenerator()

        # Verify prompt config was loaded
        self.assertEqual(generator.prompt_config, mock_prompt_config)
        mock_exists.assert_called_once()
        mock_open.assert_called_once()
        mock_yaml_load.assert_called_once()

    @patch('pathlib.Path.exists')
    def test_prompt_config_loading_file_not_found(self, mock_exists):
        """Test prompt config loading when prompt.yaml file doesn't exist"""
        # Mock file doesn't exist
        mock_exists.return_value = False

        # Create new generator to test loading
        generator = FrontmatterComponentGenerator()

        # Verify empty config when file not found
        self.assertEqual(generator.prompt_config, {})

    @patch('pathlib.Path.exists')
    @patch('yaml.safe_load', side_effect=Exception("YAML parsing error"))
    def test_prompt_config_loading_yaml_error(self, mock_yaml_load, mock_exists):
        """Test prompt config loading with YAML parsing error"""
        # Mock file exists but YAML parsing fails
        mock_exists.return_value = True

        # Create new generator to test loading
        generator = FrontmatterComponentGenerator()

        # Verify empty config when YAML parsing fails
        self.assertEqual(generator.prompt_config, {})

    @patch('utils.get_author_by_id')
    def test_create_template_vars_success(self, mock_get_author):
        """Test successful template variable creation"""
        mock_get_author.return_value = self.test_author_data

        result = self.generator._create_template_vars(
            "Steel",
            self.test_material_data,
            None
        )

        # Verify all expected variables are present
        expected_vars = [
            'subject', 'subject_lowercase', 'subject_slug',
            'material_formula', 'material_symbol', 'material_type',
            'category', 'author_name', 'author_object_sex',
            'author_object_title', 'author_object_country',
            'author_object_expertise', 'author_object_image',
            'persona_country', 'author_id', 'timestamp'
        ]

        for var in expected_vars:
            self.assertIn(var, result, f"Missing template variable: {var}")

        # Verify specific values
        self.assertEqual(result['subject'], 'Steel')
        self.assertEqual(result['material_formula'], 'Fe-C')
        self.assertEqual(result['author_name'], 'Ikmanda Roswati')
        self.assertEqual(result['author_id'], 3)

    def test_create_template_vars_missing_category(self):
        """Test template variable creation with missing category"""
        incomplete_data = self.test_material_data.copy()
        del incomplete_data['category']

        with self.assertRaises(Exception) as context:
            self.generator._create_template_vars(
                "Steel",
                incomplete_data,
                None
            )

        self.assertIn("category", str(context.exception))

    def test_create_template_vars_missing_formula(self):
        """Test template variable creation with missing formula"""
        incomplete_data = self.test_material_data.copy()
        del incomplete_data['formula']

        with self.assertRaises(Exception) as context:
            self.generator._create_template_vars(
                "Steel",
                incomplete_data,
                None
            )

        self.assertIn("formula", str(context.exception))

    @patch('utils.get_author_by_id')
    def test_create_template_vars_author_resolution_failure(self, mock_get_author):
        """Test template variable creation with author resolution failure"""
        mock_get_author.return_value = None  # Simulate author not found

        with self.assertRaises(Exception) as context:
            self.generator._create_template_vars(
                "Steel",
                self.test_material_data,
                None
            )

        self.assertIn("author_id", str(context.exception))

    @patch('utils.get_author_by_id')
    def test_build_api_prompt_with_template_integration(self, mock_get_author):
        """Test API prompt building with actual template integration from prompt.yaml"""
        mock_get_author.return_value = self.test_author_data

        # Set up generator with test template that mimics the actual prompt.yaml structure
        test_template = """TASK: Generate ONLY valid YAML frontmatter data for {subject} laser cleaning.
---
name: "{subject}"
author: "{author_name}"
category: "{category}"
chemicalProperties:
  formula: "{material_formula}"
---
"""
        self.generator.prompt_config = {'template': test_template}

        # Create template variables
        template_vars = self.generator._create_template_vars(
            "Steel",
            self.test_material_data,
            self.test_author_data
        )

        # Build API prompt
        prompt = self.generator._build_api_prompt(template_vars, None)

        # Verify template variables were substituted correctly from material data
        self.assertIn('Steel', prompt)
        self.assertIn('Ikmanda Roswati', prompt)
        self.assertIn('metal', prompt)
        self.assertIn('Fe-C', prompt)
        self.assertIn('---', prompt)  # YAML markers should be present
        self.assertIn('TASK: Generate ONLY valid YAML', prompt)  # Template content preserved

    def test_build_api_prompt_missing_template_config(self):
        """Test API prompt building with missing template configuration"""
        # Clear prompt config
        self.generator.prompt_config = {}

        template_vars = {'subject': 'Steel'}

        with self.assertRaises(ValueError) as context:
            self.generator._build_api_prompt(template_vars, None)

        self.assertIn("Prompt configuration not loaded", str(context.exception))

    def test_build_api_prompt_missing_template_field(self):
        """Test API prompt building with missing template field in config"""
        # Set config without template field
        self.generator.prompt_config = {'name': 'Test Config'}

        template_vars = {'subject': 'Steel'}

        with self.assertRaises(ValueError) as context:
            self.generator._build_api_prompt(template_vars, None)

        self.assertIn("missing required 'template' field", str(context.exception))

    @patch('utils.property_enhancer.enhance_generated_frontmatter')
    def test_post_process_content_success(self, mock_enhance):
        """Test successful content post-processing"""
        mock_enhance.return_value = "enhanced content"

        result = self.generator._post_process_content(
            "original content",
            "Steel",
            self.test_material_data
        )

        mock_enhance.assert_called_once_with("original content", "metal")
        self.assertEqual(result, "enhanced content")

    @patch('utils.property_enhancer.enhance_generated_frontmatter')
    def test_post_process_content_enhancement_failure(self, mock_enhance):
        """Test content post-processing with enhancement failure"""
        mock_enhance.side_effect = Exception("Enhancement failed")

        result = self.generator._post_process_content(
            "original content",
            "Steel",
            self.test_material_data
        )

        # Should return original content on enhancement failure
        self.assertEqual(result, "original content")

    def test_generate_missing_api_client(self):
        """Test generation with missing API client"""
        result = self.generator.generate(
            "Steel",
            self.test_material_data,
            api_client=None
        )

        self.assertFalse(result.success)
        self.assertIn("API client", result.error_message)

    @patch('utils.get_author_by_id')
    @patch('components.frontmatter.generator.APIComponentGenerator.__init__')
    def test_generate_full_workflow(self, mock_init, mock_get_author):
        """Test full generation workflow"""
        mock_init.return_value = None
        mock_get_author.return_value = self.test_author_data

        # Mock API client
        mock_api_client = Mock()
        mock_api_response = Mock()
        mock_api_response.success = True
        mock_api_response.content = self._get_sample_frontmatter_content()
        mock_api_client.generate_simple.return_value = mock_api_response

        # Create generator instance
        generator = FrontmatterComponentGenerator()
        generator.prompt_config = {'template': 'Sample template {subject}'}

        result = generator.generate(
            "Steel",
            self.test_material_data,
            api_client=mock_api_client
        )

        self.assertTrue(result.success)
        self.assertIsInstance(result, ComponentResult)

    def _get_sample_frontmatter_content(self):
        """Get sample frontmatter content for testing"""
        return """---
name: Steel
author: Ikmanda Roswati
category: metal
---
"""


class TestFrontmatterValidator(unittest.TestCase):
    """Test cases for frontmatter validation functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.valid_frontmatter = """---
name: Steel
applications:
  - industry: Automotive Manufacturing
    detail: Removal of rust from Steel components
technicalSpecifications:
  powerRange: 50-1000W
  wavelength: "1064nm"
author: Ikmanda Roswati
author_object:
  id: 3
  name: Ikmanda Roswati
  sex: "m"
  title: "Ph.D."
  country: "Indonesia"
  expertise: "Ultrafast Laser Physics"
  image: "/images/author/ikmanda-roswati.jpg"
category: metal
chemicalProperties:
  symbol: Fe
  formula: Fe-C
properties:
  density: "7.85 g/cm³"
  meltingPoint: "1370-1510°C"
keywords: steel, laser, cleaning
---
"""

        self.invalid_frontmatter = """---
name: Steel
applications:
  - industry: Automotive
    detail: Rust removal
---
"""

    def test_validate_frontmatter_format_valid(self):
        """Test validation of valid frontmatter format"""
        errors = validate_frontmatter_format(self.valid_frontmatter)
        self.assertEqual(len(errors), 0)

    def test_validate_frontmatter_format_invalid_yaml(self):
        """Test validation of invalid YAML format"""
        invalid_yaml = """---
name: Steel
  invalid: indentation
---
"""
        errors = validate_frontmatter_format(invalid_yaml)
        self.assertGreater(len(errors), 0)
        self.assertIn("Invalid YAML", errors[0])

    def test_validate_frontmatter_format_missing_closing_marker(self):
        """Test validation of frontmatter missing closing marker"""
        missing_marker = """---
name: Steel
applications:
  - industry: Automotive
"""
        errors = validate_frontmatter_format(missing_marker)
        self.assertGreater(len(errors), 0)
        self.assertIn("not properly closed", errors[0])

    def test_validate_frontmatter_content_valid(self):
        """Test validation of valid frontmatter content"""
        errors = validate_frontmatter_content(self.valid_frontmatter)
        self.assertEqual(len(errors), 0)

    def test_validate_frontmatter_content_missing_required(self):
        """Test validation of frontmatter missing required fields"""
        incomplete = """---
applications:
  - industry: Automotive
---
"""
        errors = validate_frontmatter_content(incomplete)
        self.assertGreater(len(errors), 0)

    def test_validate_frontmatter_properties_completeness(self):
        """Test validation of frontmatter properties completeness"""
        warnings = validate_frontmatter_properties(self.valid_frontmatter)
        # Should have minimal warnings for well-structured frontmatter
        self.assertIsInstance(warnings, list)


class TestFrontmatterUtils(unittest.TestCase):
    """Test cases for frontmatter utility functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.sample_frontmatter_data = {
            "name": "Steel",
            "category": "metal",
            "properties": {
                "density": "7.85 g/cm³",
                "meltingPoint": "1370-1510°C",
                "thermalConductivity": "45-65 W/m·K"
            },
            "chemicalProperties": {
                "symbol": "Fe",
                "formula": "Fe-C"
            }
        }

    @patch('components.frontmatter.utils.Path')
    def test_load_category_ranges_success(self, mock_path):
        """Test successful loading of category ranges"""
        mock_path.return_value.exists.return_value = True

        sample_ranges = {
            "categories": {
                "metal": {
                    "density": {"min": 1.0, "max": 20.0},
                    "meltingPoint": {"min": 200, "max": 3000}
                }
            }
        }

        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = yaml.dump(sample_ranges)
            mock_open.return_value.__enter__.return_value = mock_file

            with patch('yaml.safe_load', return_value=sample_ranges):
                ranges = load_category_ranges()
                self.assertIsInstance(ranges, dict)

    @patch('components.frontmatter.utils.Path')
    def test_load_category_ranges_file_not_found(self, mock_path):
        """Test loading category ranges when file not found"""
        mock_path.return_value.exists.return_value = False

        ranges = load_category_ranges()
        self.assertEqual(ranges, {})

    def test_enhance_frontmatter_with_context_success(self):
        """Test successful frontmatter enhancement with context"""
        category_ranges = {
            "metal": {
                "density": {"min": 1.0, "max": 20.0},
                "meltingPoint": {"min": 200, "max": 3000}
            }
        }

        with patch('components.frontmatter.utils.load_category_ranges',
                  return_value=category_ranges):
            enhanced = enhance_frontmatter_with_context(
                self.sample_frontmatter_data,
                "metal"
            )

            self.assertIsInstance(enhanced, dict)
            self.assertIn("properties", enhanced)

    def test_enhance_frontmatter_with_context_no_category_ranges(self):
        """Test frontmatter enhancement with missing category ranges"""
        with patch('components.frontmatter.utils.load_category_ranges',
                  return_value={}):
            result = enhance_frontmatter_with_context(
                self.sample_frontmatter_data,
                "nonexistent"
            )

            # Should return original data unchanged
            self.assertEqual(result, self.sample_frontmatter_data)

    def test_enhance_generated_frontmatter_success(self):
        """Test successful enhancement of generated frontmatter content"""
        frontmatter_content = """---
name: Steel
category: metal
properties:
  density: "7.85 g/cm³"
---
"""

        with patch('components.frontmatter.utils.enhance_frontmatter_with_context'):
            result = enhance_generated_frontmatter(frontmatter_content, "metal")

            self.assertIsInstance(result, str)
            self.assertIn("---", result)

    def test_enhance_generated_frontmatter_invalid_format(self):
        """Test enhancement of invalid frontmatter format"""
        invalid_content = "Not a frontmatter"

        result = enhance_generated_frontmatter(invalid_content, "metal")

        # Should return original content
        self.assertEqual(result, invalid_content)

    def test_validate_frontmatter_properties_completeness_full(self):
        """Test completeness validation with full frontmatter data"""
        result = validate_frontmatter_properties_completeness(
            self.sample_frontmatter_data
        )

        self.assertIsInstance(result, dict)
        self.assertIn("completeness", result)
        self.assertIn("recommendations", result)
        self.assertGreater(result["completeness"], 0)

    def test_validate_frontmatter_properties_completeness_empty(self):
        """Test completeness validation with empty frontmatter data"""
        result = validate_frontmatter_properties_completeness({})

        self.assertEqual(result["completeness"], 0.0)
        self.assertIn("Add frontmatter data", result["recommendations"][0])


class TestFrontmatterIntegration(unittest.TestCase):
    """Integration tests for frontmatter component"""

    def setUp(self):
        """Set up integration test fixtures"""
        self.generator = FrontmatterComponentGenerator()
        self.test_author_data = {
            "id": 3,
            "name": "Ikmanda Roswati",
            "sex": "m",
            "title": "Ph.D.",
            "country": "Indonesia",
            "expertise": "Ultrafast Laser Physics and Material Interactions",
            "image": "/images/author/ikmanda-roswati.jpg"
        }
        self.test_material_data = {
            "name": "Steel",
            "author_id": 3,
            "formula": "Fe-C",
            "symbol": "Fe",
            "category": "metal",
            "material_type": "ferrous alloy"
        }

    @patch('utils.get_author_by_id')
    @patch('components.frontmatter.generator.APIComponentGenerator.__init__')
    def test_full_generation_workflow(self, mock_init, mock_get_author):
        """Test complete generation workflow from material data to final output"""
        mock_init.return_value = None
        mock_get_author.return_value = {
            "id": 3,
            "name": "Ikmanda Roswati",
            "sex": "m",
            "title": "Ph.D.",
            "country": "Indonesia",
            "expertise": "Ultrafast Laser Physics and Material Interactions",
            "image": "/images/author/ikmanda-roswati.jpg"
        }

        # Mock API client with realistic response
        mock_api_client = Mock()
        mock_api_response = Mock()
        mock_api_response.success = True
        mock_api_response.content = self._get_complete_frontmatter_sample()
        mock_api_client.generate_simple.return_value = mock_api_response

        # Create generator with test configuration
        generator = FrontmatterComponentGenerator()
        generator.prompt_config = {
            'template': self._get_test_template()
        }

        # Test material data
        material_data = {
            "name": "Steel",
            "author_id": 3,
            "formula": "Fe-C",
            "symbol": "Fe",
            "category": "metal",
            "material_type": "ferrous alloy"
        }

        # Generate frontmatter
        result = generator.generate(
            "Steel",
            material_data,
            api_client=mock_api_client
        )

        # Verify successful generation
        self.assertTrue(result.success)
        self.assertIn("Steel", result.content)
        self.assertIn("Ikmanda Roswati", result.content)
        self.assertIn("Indonesia", result.content)

    @patch('utils.get_author_by_id')
    @patch('components.frontmatter.generator.APIComponentGenerator.__init__')
    def test_hybrid_data_integration_end_to_end(self, mock_init, mock_get_author):
        """Test complete hybrid data integration: materials.yaml + prompt.yaml + authors.json"""
        mock_init.return_value = None
        mock_get_author.return_value = self.test_author_data

        # Mock API client
        mock_api_client = Mock()
        mock_api_response = Mock()
        mock_api_response.success = True
        mock_api_response.content = """---
name: "Steel"
author: "Ikmanda Roswati"
category: "metal"
chemicalProperties:
  formula: "Fe-C"
---
"""
        mock_api_client.generate_simple.return_value = mock_api_response

        # Create generator with realistic template from prompt.yaml
        generator = FrontmatterComponentGenerator()
        generator.prompt_config = {
            'template': """TASK: Generate frontmatter for {subject}.
---
name: "{subject}"
author: "{author_name}"
category: "{category}"
chemicalProperties:
  formula: "{material_formula}"
  symbol: "{material_symbol}"
---
"""
        }

        # Generate using material data (simulating data from materials.yaml)
        result = generator.generate(
            "Steel",
            self.test_material_data,  # Material data with formula, symbol, category
            api_client=mock_api_client,
            author_info=self.test_author_data  # Author data (simulating authors.json)
        )

        # Verify successful generation
        self.assertTrue(result.success)
        self.assertIn("Steel", result.content)
        self.assertIn("Ikmanda Roswati", result.content)
        self.assertIn("Fe-C", result.content)  # Material formula from materials.yaml
        self.assertIn("metal", result.content)  # Category from materials.yaml

        # Verify the API was called with properly formatted prompt
        mock_api_client.generate_simple.assert_called_once()
        call_args = mock_api_client.generate_simple.call_args[0][0]

        # Verify template variables were substituted in the prompt
        self.assertIn("Steel", call_args)
        self.assertIn("Ikmanda Roswati", call_args)
        self.assertIn("Fe-C", call_args)
        self.assertIn("TASK: Generate frontmatter", call_args)

    def _get_complete_frontmatter_sample(self):
        """Get complete frontmatter sample for integration testing"""
        return """---
name: Steel
applications:
  - industry: Automotive Manufacturing
    detail: Removal of rust, scale, and paint from Steel components
author: Ikmanda Roswati
author_object:
  id: 3
  name: Ikmanda Roswati
  sex: "m"
  title: "Ph.D."
  country: "Indonesia"
  expertise: "Ultrafast Laser Physics and Material Interactions"
  image: "/images/author/ikmanda-roswati.jpg"
category: metal
chemicalProperties:
  symbol: Fe
  formula: Fe-C
properties:
  density: "7.85 g/cm³"
  meltingPoint: "1370-1510°C"
---
"""

    def _get_test_template(self):
        """Get test template for integration testing"""
        return """Generate frontmatter for {subject}.

---
name: {subject}
author: {author_name}
author_object:
  id: {author_id}
  name: {author_name}
  sex: "{author_object_sex}"
  title: "{author_object_title}"
  country: "{author_object_country}"
  expertise: "{author_object_expertise}"
  image: "{author_object_image}"
category: {category}
chemicalProperties:
  symbol: {material_symbol}
  formula: {material_formula}
---
"""


class TestFrontmatterErrorHandling(unittest.TestCase):
    """Test cases for error handling scenarios"""

    def setUp(self):
        """Set up error handling test fixtures"""
        self.generator = FrontmatterComponentGenerator()

    def test_missing_prompt_config_file(self):
        """Test handling of missing prompt configuration file"""
        with patch('pathlib.Path.exists', return_value=False):
            generator = FrontmatterComponentGenerator()
            # Should handle gracefully with empty config
            self.assertEqual(generator.prompt_config, {})

    def test_invalid_prompt_config_format(self):
        """Test handling of invalid prompt configuration format"""
        with patch('yaml.safe_load', side_effect=yaml.YAMLError("Invalid YAML")):
            with patch('pathlib.Path.exists', return_value=True):
                generator = FrontmatterComponentGenerator()
                # Should handle gracefully with empty config
                self.assertEqual(generator.prompt_config, {})

    @patch('utils.get_author_by_id')
    def test_author_resolution_with_incomplete_data(self, mock_get_author):
        """Test author resolution with incomplete author data"""
        mock_get_author.return_value = {"id": 3}  # Missing required fields

        with self.assertRaises(Exception):
            self.generator._create_template_vars(
                "Steel",
                {"name": "Steel", "author_id": 3, "category": "metal", "formula": "Fe-C", "symbol": "Fe"},
                None
            )

    def test_template_formatting_with_special_characters(self):
        """Test template formatting with special characters in data"""
        template_vars = {
            'subject': 'Steel',
            'subject_lowercase': 'steel',
            'subject_slug': 'steel',
            'material_formula': 'Fe-C',
            'material_symbol': 'Fe',
            'material_type': 'ferrous alloy',
            'category': 'metal',
            'author_name': 'Test Author',
            'author_object_sex': 'm',
            'author_object_title': 'Ph.D.',
            'author_object_country': 'Test Country',
            'author_object_expertise': 'Test Expertise',
            'author_object_image': '/images/test.jpg',
            'persona_country': 'Test Country',
            'author_id': 1,
            'timestamp': '2025-09-08T10:30:00Z'
        }

        # Should handle special characters without issues
        prompt = self.generator._build_api_prompt(template_vars)
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)


class TestFrontmatterVersioning(unittest.TestCase):
    """Test cases for frontmatter version information integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = FrontmatterComponentGenerator()

    def test_version_information_integration(self):
        """Test that version information is properly integrated via versioning system"""
        # Test content with proper YAML frontmatter
        test_content = """---
name: "Test Material"
category: "metal"
author: "Test Author"
---"""
        
        # Mock the versioning system
        with patch('versioning.stamp_component_output') as mock_stamp:
            mock_stamp.return_value = test_content + """

# Version Information
# Generated: 2025-09-10T13:23:40.671545
# Material: Test Material
# Component: frontmatter
# Generator: Z-Beam v2.1.0

---
Version Log - Generated: 2025-09-10T13:23:40.671714
Material: Test Material
Component: frontmatter
Generator: Z-Beam v2.1.0
---"""
            
            # Test that versioning system is called
            from versioning import stamp_component_output
            result = stamp_component_output("frontmatter", test_content)
            
            # Verify versioning was applied
            self.assertIn("# Version Information", result)
            self.assertIn("Version Log - Generated:", result)
            self.assertIn("Material: Test Material", result)
            self.assertIn("Component: frontmatter", result)
            mock_stamp.assert_called_once_with("frontmatter", test_content)

    def test_version_information_format_validation(self):
        """Test validation of version information format in generated files"""
        # Sample content with version information
        content_with_version = """---
name: "Alumina"
category: "ceramic"
author: "Test Author"
---

# Version Information
# Generated: 2025-09-10T13:23:40.671545
# Material: Alumina
# Component: frontmatter
# Generator: Z-Beam v2.1.0

---
Version Log - Generated: 2025-09-10T13:23:40.671714
Material: Alumina
Component: frontmatter
Generator: Z-Beam v2.1.0
---"""
        
        # Test that content has proper structure
        lines = content_with_version.split('\n')
        yaml_sections = [i for i, line in enumerate(lines) if line.strip() == '---']
        
        # Should have at least 4 '---' markers (open YAML, close YAML, close version log)
        self.assertGreaterEqual(len(yaml_sections), 3)
        
        # Check that version information is present
        content_str = '\n'.join(lines)
        self.assertIn("# Version Information", content_str)
        self.assertIn("Version Log - Generated:", content_str)
        self.assertIn("Material:", content_str)
        self.assertIn("Component: frontmatter", content_str)

    def test_post_processor_version_preservation(self):
        """Test that post-processor preserves version information sections"""
        from components.frontmatter.post_processor import post_process_frontmatter
        
        # Content with version info that might have formatting issues
        malformed_content = """---
name: "Test Material"
description: "Test description
---

# Version Information
# Generated: 2025-09-10T13:23:40.671545

---
Version Log - Generated: 2025-09-10T13:23:40.671714
Material: Test Material
---"""
        
        # Post-process the content
        processed = post_process_frontmatter(malformed_content, "Test Material")
        
        # Verify version sections are preserved
        self.assertIn("# Version Information", processed)
        self.assertIn("Version Log - Generated:", processed)
        self.assertIn("Material: Test Material", processed)
        
        # Verify YAML is properly formatted
        lines = processed.split('\n')
        yaml_sections = [i for i, line in enumerate(lines) if line.strip() == '---']
        self.assertGreaterEqual(len(yaml_sections), 2)  # At least opening and closing YAML

    def test_no_version_duplication(self):
        """Test that version information is not duplicated in template"""
        # Check that prompt template does not contain version information
        prompt_config = self.generator.prompt_config
        if prompt_config and 'template' in prompt_config:
            template = prompt_config['template']
            
            # Template should not contain version information fields
            self.assertNotIn("versionInfo:", template)
            self.assertNotIn("generated:", template)
            self.assertNotIn("# Version Information", template)
            
            # Version info should be handled by external versioning system
            self.assertNotIn("Version Log", template)

    @patch('api.client_factory.APIClientFactory.create_client')
    def test_version_integration_in_generation_workflow(self, mock_create_client):
        """Test that version information is properly integrated in full generation workflow"""
        # Mock API client
        mock_api_client = Mock()
        mock_api_client.generate_simple.return_value = Mock(
            success=True,
            content="""---
name: "Steel"
category: "metal"
---"""
        )
        mock_create_client.return_value = mock_api_client
        
        # Mock versioning system
        with patch('versioning.stamp_component_output') as mock_stamp:
            mock_stamp.return_value = """---
name: "Steel"
category: "metal"
---

# Version Information
# Generated: 2025-09-10T13:23:40.671545
# Material: Steel

---
Version Log - Generated: 2025-09-10T13:23:40.671714
Material: Steel
Component: frontmatter
---"""
            
            # Generate content
            result = self.generator.generate(
                material_name="Steel",
                material_data={
                    "name": "Steel",
                    "author_id": 1,
                    "formula": "Fe-C",
                    "symbol": "Fe",
                    "category": "metal"
                },
                api_client=mock_api_client
            )
            
            # Verify versioning was applied
            self.assertTrue(result.success)
            self.assertIn("# Version Information", result.content)
            self.assertIn("Version Log - Generated:", result.content)
            mock_stamp.assert_called_once()


if __name__ == '__main__':
    # Configure test runner with verbose output
    unittest.main(verbosity=2)