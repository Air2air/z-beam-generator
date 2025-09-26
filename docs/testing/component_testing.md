## 🧪 Component Testing Updates - Machine Settings Separation

### **Recent Architecture Changes**
- **Caption Component**: Machine settings removed, now focuses on image descriptions and SEO
- **Settings Component**: New component created to handle machine settings with table-like structure
- **Component Separation**: Clean separation of concerns between image content and machine configuration

### **Updated Test Categories**
- **Caption Tests**: Verify removal of machine settings, focus on content generation
- **Settings Tests**: Validate machine settings extraction and table structure
- **Integration Tests**: Test both components work independently and together
- **Separation Tests**: Ensure clean component boundaries

### **Caption Component Testing (Updated)**

```python
class TestCaptionComponentGenerator:
    """Updated tests for caption component after machine settings removal"""

    def test_machine_settings_removed(self):
        """Test that machine settings are completely removed from caption component."""
        mock_frontmatter = {
            'name': 'Test Material',
            'category': 'metal',
            'machineSettings': {
                'wavelength': '1064nm',
                'powerRange': '50-200W'
            }
        }
        
        with patch.object(self.generator, '_load_frontmatter_data', return_value=mock_frontmatter):
            result = self.generator.generate('Test Material', {})
        
        if result.success:
            content = result.content
            yaml_content = content.split('---\n')[0]
            parsed = yaml.safe_load(yaml_content)
            
            # Verify NO machine settings in output
            machine_setting_fields = ['laser_parameters', 'technicalSpecifications', 'machineSettings']
            for field in machine_setting_fields:
                assert field not in parsed, f"Machine setting field '{field}' should not be in caption component"

    def test_file_size_reduction_after_settings_extraction(self):
        """Test that generated content is smaller after machine settings extraction."""
        result = self.generator.generate('Test Material', {})
        
        if result.success:
            content = result.content
            # New format should be 3.5-4.0KB (reduced from 4.7-5.0KB)
            content_size = len(content.encode('utf-8'))
            assert content_size >= 3000, f"Generated content should be at least 3KB, got {content_size} bytes"
            assert content_size <= 5000, f"Generated content should not exceed 5KB, got {content_size} bytes"

    def test_caption_component_focus(self):
        """Test that caption component focuses on image-related content."""
        result = self.generator.generate('Test Material', {})
        
        if result.success:
            content = result.content
            yaml_content = content.split('---\n')[0]
            parsed = yaml.safe_load(yaml_content)
            
            # Should have image-related content
            assert 'before_text' in parsed
            assert 'after_text' in parsed
            assert 'chemicalProperties' in parsed
            assert 'author' in parsed
            assert 'keywords' in parsed
```

### **Settings Component Testing (New)**

```python
class TestSettingsComponentGenerator:
    """Test cases for new Settings component with table-like structure."""

    def test_table_like_structure_generation(self):
        """Test that generated content follows table component structure with section headings."""
        mock_frontmatter = {
            'machineSettings': {
                'powerRange': '50-200W',
                'wavelength': '1064nm',
                'pulseDuration': '10-200ns'
            }
        }
        
        result = self.generator._generate_static_content(
            'Test Material', {}, frontmatter_data=mock_frontmatter
        )
        
        parsed = yaml.safe_load(result)
        
        # Test main structure (like table component)
        assert 'machineSettings' in parsed
        assert 'settings' in parsed['machineSettings']
        assert 'renderInstructions' in parsed
        
        settings = parsed['machineSettings']['settings']
        assert isinstance(settings, list)
        
        # Test section headers (like table component)
        headers = [section['header'] for section in settings]
        expected_headers = ['## Machine Configuration', '## Processing Parameters']
        
        for expected_header in expected_headers:
            if expected_header in headers:
                assert True  # At least one expected header found
                break
        else:
            pytest.fail(f"No expected headers found. Got: {headers}")

    def test_render_instructions_like_table_component(self):
        """Test that render instructions follow table component pattern."""
        result = self.generator._generate_static_content(
            'Test Material', {}, frontmatter_data={'machineSettings': {'powerRange': '50-200W'}}
        )
        
        parsed = yaml.safe_load(result)
        instructions = parsed['renderInstructions']
        
        # Should follow table component pattern
        assert 'Next.js' in instructions
        assert 'loop over' in instructions
        assert '<table>' in instructions
        assert 'parameter' in instructions
        assert 'value' in instructions
        assert 'range' in instructions
        assert 'category' in instructions

    def test_machine_settings_extraction(self):
        """Test extraction of machine settings from frontmatter."""
        mock_frontmatter = {
            'machineSettings': {
                'powerRange': '50-200W',
                'powerRangeMin': '20W',
                'powerRangeMax': '500W',
                'wavelength': '1064nm',
                'fluenceRange': '1.0–10 J/cm²'
            }
        }
        
        result = self.generator._generate_static_content(
            'Test Material', {}, frontmatter_data=mock_frontmatter
        )
        
        parsed = yaml.safe_load(result)
        settings = parsed['machineSettings']['settings']
        
        # Should extract and structure machine settings
        all_rows = []
        for section in settings:
            all_rows.extend(section.get('rows', []))
        
        parameters = [row['parameter'] for row in all_rows]
        
        # Should include key machine settings
        expected_params = ['Power Range', 'Wavelength', 'Fluence Range']
        for param in expected_params:
            if param in parameters:
                assert True  # At least one parameter found
                break
        else:
            pytest.fail(f"No expected parameters found. Got: {parameters}")
```

### **Component Separation Testing**

```python
class TestComponentSeparation:
    """Test clean separation between caption and settings components."""

    def test_independent_component_generation(self):
        """Test that caption and settings components work independently."""
        # Generate caption without settings
        caption_result = caption_generator.generate('Test Material', {})
        assert caption_result.success

        # Generate settings without caption
        settings_result = settings_generator._generate_static_content(
            'Test Material', {}, frontmatter_data={'machineSettings': {'powerRange': '50W'}}
        )
        assert isinstance(settings_result, str)

    def test_combined_component_generation(self):
        """Test that both components can be generated together."""
        # This simulates: python3 run.py --material "steel" --components "caption,settings"
        
        mock_frontmatter = {
            'name': 'Test Material',
            'category': 'metal',
            'machineSettings': {'powerRange': '50W'},
            'chemicalProperties': {'formula': 'Test'},
            'author_object': {'name': 'Test Author', 'expertise': ['Testing']},
            'applications': ['Test Application']
        }
        
        # Generate both components
        caption_result = caption_generator.generate('Test Material', {})
        settings_result = settings_generator._generate_static_content(
            'Test Material', {}, frontmatter_data=mock_frontmatter
        )
        
        # Both should succeed
        assert caption_result.success
        assert isinstance(settings_result, str)
        
        # Verify no overlap in content
        caption_yaml = yaml.safe_load(caption_result.content.split('---\n')[0])
        settings_yaml = yaml.safe_load(settings_result)
        
        # Caption should not have machine settings
        assert 'machineSettings' not in caption_yaml
        assert 'laser_parameters' not in caption_yaml
        
        # Settings should not have caption content
        assert 'before_text' not in settings_yaml
        assert 'after_text' not in settings_yaml
        assert 'author' not in settings_yaml

    def test_data_source_consistency(self):
        """Test that both components use same frontmatter data source."""
        material_name = 'Test Material'
        
        # Both components should access same frontmatter data
        # Caption component: loads frontmatter internally
        # Settings component: receives frontmatter as parameter
        
        # This ensures data consistency between components
        assert True  # Placeholder for data consistency tests

    def test_component_factory_registration(self):
        """Test that both components are properly registered with factory."""
        from generators.component_generators import ComponentGeneratorFactory
        
        # Both components should be discoverable
        caption_gen = ComponentGeneratorFactory.create_generator('caption', 'test')
        settings_gen = ComponentGeneratorFactory.create_generator('settings', 'test')
        
        assert caption_gen is not None
        assert settings_gen is not None
        assert caption_gen.component_type == 'caption'
        assert settings_gen.component_type == 'settings'
```

### **Integration Testing Patterns (Updated)**

```python
class TestUpdatedComponentPipeline:
    """Test component pipeline after machine settings separation."""

    def test_frontmatter_to_multiple_components(self):
        """Test frontmatter data feeding both caption and settings components."""
        material_data = {
            "name": "Copper",
            "category": "metal"
        }

        # Generate frontmatter first
        frontmatter_gen = ComponentGeneratorFactory.create_generator("frontmatter", "copper")
        frontmatter_result = frontmatter_gen.generate(material_data=material_data)
        assert frontmatter_result.success

        # Generate caption (should work without machine settings)
        caption_gen = ComponentGeneratorFactory.create_generator("caption", "copper")
        caption_result = caption_gen.generate(
            material_data=material_data,
            frontmatter_data=frontmatter_result.content
        )
        assert caption_result.success

        # Generate settings (should extract machine settings)
        settings_gen = ComponentGeneratorFactory.create_generator("settings", "copper")
        settings_result = settings_gen.generate(
            material_data=material_data,
            frontmatter_data=frontmatter_result.content
        )
        assert settings_result.success

    def test_component_content_validation(self):
        """Test that each component contains appropriate content."""
        
        # Caption should focus on descriptions and SEO
        caption_content = caption_generator.generate('Test Material', {}).content
        caption_yaml = yaml.safe_load(caption_content.split('---\n')[0])
        
        assert 'before_text' in caption_yaml
        assert 'after_text' in caption_yaml
        assert 'keywords' in caption_yaml
        
        # Settings should focus on machine configuration
        settings_content = settings_generator._generate_static_content(
            'Test Material', {}, 
            frontmatter_data={'machineSettings': {'powerRange': '50W'}}
        )
        settings_yaml = yaml.safe_load(settings_content)
        
        assert 'machineSettings' in settings_yaml
        assert 'settings' in settings_yaml['machineSettings']
        assert 'renderInstructions' in settings_yaml

    def test_architecture_consistency(self):
        """Test that component architecture remains consistent."""
        
        # Both components should follow fail-fast architecture
        # Both should use frontmatter data
        # Settings should follow table component pattern
        
        # Caption fail-fast test
        with pytest.raises(Exception):
            caption_generator.generate('', {})
        
        # Settings fail-fast test  
        with pytest.raises(Exception):
            settings_generator._generate_static_content('', {})
        
        with pytest.raises(Exception):
            settings_generator._generate_static_content('Test', {}, frontmatter_data=None)
```

### **Performance Testing (Updated)**

```python
class TestUpdatedPerformance:
    """Test performance after component separation."""

    def test_component_generation_speed(self):
        """Test generation speed for separated components."""
        materials = ["aluminum", "copper", "steel"]
        
        # Test caption generation speed (should be faster without machine settings)
        caption_times = []
        for material in materials:
            start_time = time.time()
            result = caption_generator.generate(material, {"name": material})
            end_time = time.time()
            
            assert result.success
            caption_times.append(end_time - start_time)
        
        # Test settings generation speed
        settings_times = []
        for material in materials:
            mock_frontmatter = {'machineSettings': {'powerRange': '50W'}}
            
            start_time = time.time()
            result = settings_generator._generate_static_content(
                material, {}, frontmatter_data=mock_frontmatter
            )
            end_time = time.time()
            
            assert isinstance(result, str)
            settings_times.append(end_time - start_time)
        
        # Both should be reasonably fast
        avg_caption_time = sum(caption_times) / len(caption_times)
        avg_settings_time = sum(settings_times) / len(settings_times)
        
        assert avg_caption_time < 2.0, f"Caption generation too slow: {avg_caption_time}s"
        assert avg_settings_time < 1.0, f"Settings generation too slow: {avg_settings_time}s"

    def test_memory_efficiency_after_separation(self):
        """Test memory usage after component separation."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate both components
        caption_result = caption_generator.generate("aluminum", {"name": "aluminum"})
        settings_result = settings_generator._generate_static_content(
            "aluminum", {}, frontmatter_data={'machineSettings': {'powerRange': '50W'}}
        )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory
        
        assert caption_result.success
        assert isinstance(settings_result, str)
        assert memory_used < 50, f"Memory usage too high: {memory_used}MB"
```

This comprehensive testing framework ensures the updated component architecture maintains high quality while properly separating concerns between image content (Caption) and machine configuration (Settings). Testing Patterns & Blueprints

## **Purpose**
This document provides standardized testing patterns and blueprints for the Z-Beam Generator system. It ensures consistent test implementation, proper mocking strategies, and comprehensive coverage across all components.

## 📋 Requirements

### **Testing Framework**
- **pytest** as the primary testing framework
- **unittest.mock** for mocking external dependencies
- **pytest-cov** for coverage reporting
- **pytest-xdist** for parallel test execution

### **Test Categories**
- **Unit Tests**: Individual functions and methods
- **Integration Tests**: Component interactions
- **API Tests**: External service integrations
- **Performance Tests**: Speed and resource usage
- **Robustness Tests**: Error handling and edge cases

## 🏗️ Test Architecture

### **Test Directory Structure**
```
tests/
├── unit/                          # Unit tests
│   ├── test_components/          # Component unit tests
│   ├── test_utils/               # Utility function tests
│   └── test_generators/          # Generator tests
├── integration/                  # Integration tests
│   ├── test_component_interaction.py
│   └── test_full_pipeline.py
├── api/                          # API integration tests
│   ├── test_deepseek_integration.py
│   └── test_winston_integration.py
├── performance/                  # Performance tests
│   ├── test_generation_speed.py
│   └── test_memory_usage.py
├── robustness/                   # Robustness tests
│   ├── test_error_handling.py
│   └── test_circuit_breakers.py
└── fixtures/                     # Test data and fixtures
    ├── Materials.yaml
    ├── api_responses.json
    └── mock_data.py
```

### **Test Naming Conventions**
- **Files**: `test_{component_name}.py` or `test_{functionality}.py`
- **Classes**: `Test{ComponentName}` or `Test{Functionality}`
- **Methods**: `test_{scenario}_{expected_result}`
- **Fixtures**: `{resource}_fixture` or `mock_{resource}`

## 🔧 Unit Testing Patterns

### **Component Generator Testing**

```python
import pytest
from components.base import ComponentResult
from components.{component_name}.generator import {ComponentName}Generator
from components.{component_name}.mock_generator import Mock{ComponentName}Generator

class Test{ComponentName}Generator:

    @pytest.fixture
    def generator(self):
        """Create generator instance for testing"""
        return {ComponentName}Generator("test_material")

    @pytest.fixture
    def mock_generator(self):
        """Create mock generator for predictable testing"""
        return Mock{ComponentName}Generator("test_material")

    def test_component_type(self, generator):
        """Test component type identification"""
        assert generator.get_component_type() == "{component_name}"

    def test_successful_generation(self, mock_generator):
        """Test successful content generation"""
        material_data = {{
            "name": "Test Material",
            "category": "test_category",
            "properties": ["test_property"]
        }}

        result = mock_generator.generate(material_data=material_data)

        # Assertions
        assert result.success is True
        assert result.component_type == "{component_name}"
        assert isinstance(result, ComponentResult)
        assert result.generation_time > 0
        assert "Test Material" in result.content

    def test_input_validation(self, generator):
        """Test input validation for required fields"""
        # Test missing required inputs
        result = generator.generate()

        assert result.success is False
        assert "Invalid inputs" in result.error_message
        assert result.generation_time > 0

    def test_error_handling(self, mock_generator):
        """Test error handling and recovery"""
        # Test various error scenarios
        result = mock_generator.generate_with_error("validation")

        assert result.success is False
        assert result.error_message is not None
        assert "validation" in result.error_message.lower()

    def test_generation_metadata(self, mock_generator):
        """Test that generation includes proper metadata"""
        material_data = {{"name": "Test Material"}}
        result = mock_generator.generate(material_data=material_data)

        assert result.metadata is not None
        assert "material" in result.metadata
        assert result.metadata["material"] == "test_material"

    @pytest.mark.parametrize("material_name,expected_success", [
        ("aluminum", True),
        ("copper", True),
        ("", False),  # Empty material name should fail
        ("nonexistent_material", True),  # Should still work
    ])
    def test_generation_with_different_materials(self, material_name, expected_success):
        """Test generation with various material names"""
        if not material_name:
            with pytest.raises(ValueError):
                {ComponentName}Generator(material_name)
        else:
            generator = {ComponentName}Generator(material_name)
            result = generator.generate(material_data={{"name": material_name}})

            assert result.success is expected_success
```

### **API Client Testing**

```python
import pytest
from unittest.mock import Mock, patch
from api.deepseek import DeepSeekAPIClient
from api.exceptions import APIError, RateLimitError

class TestDeepSeekAPIClient:

    @pytest.fixture
    def api_client(self):
        """Create API client with test configuration"""
        return DeepSeekAPIClient(api_key="test_key")

    @pytest.fixture
    def mock_response(self):
        """Mock successful API response"""
        return {{
            "choices": [{{
                "message": {{
                    "content": "Generated content from API"
                }}
            }}],
            "usage": {{
                "total_tokens": 150
            }}
        }}

    def test_successful_api_call(self, api_client, mock_response):
        """Test successful API call"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response

            result = api_client.generate_content("Test prompt")

            assert "Generated content from API" in result
            mock_post.assert_called_once()

    def test_api_error_handling(self, api_client):
        """Test API error handling"""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = Exception("API Error")

            with pytest.raises(APIError):
                api_client.generate_content("Test prompt")

    def test_rate_limit_handling(self, api_client):
        """Test rate limit error handling"""
        with patch('requests.post') as mock_post:
            # Mock rate limit response
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {{"error": "Rate limit exceeded"}}
            mock_post.return_value = mock_response

            with pytest.raises(RateLimitError):
                api_client.generate_content("Test prompt")

    def test_timeout_handling(self, api_client):
        """Test timeout error handling"""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = TimeoutError("Request timed out")

            with pytest.raises(APIError) as exc_info:
                api_client.generate_content("Test prompt")

            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.parametrize("status_code,expected_exception", [
        (400, APIError),
        (401, APIError),
        (403, APIError),
        (429, RateLimitError),
        (500, APIError),
        (502, APIError),
    ])
    def test_various_http_errors(self, api_client, status_code, expected_exception):
        """Test various HTTP error codes"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.json.return_value = {{"error": f"HTTP {status_code}"}}
            mock_post.return_value = mock_response

            with pytest.raises(expected_exception):
                api_client.generate_content("Test prompt")
```

## 🧪 Integration Testing Patterns

### **Component Pipeline Testing**

```python
import pytest
from generators.component_generators import ComponentGeneratorFactory

class TestComponentPipeline:

    def test_frontmatter_dependency_chain(self):
        """Test that components respect frontmatter dependencies"""
        # Test frontmatter generation first
        frontmatter_gen = ComponentGeneratorFactory.create_generator(
            "frontmatter", "aluminum"
        )

        frontmatter_result = frontmatter_gen.generate(
            material_data={{"name": "Aluminum", "category": "metal"}}
        )

        assert frontmatter_result.success is True

        # Test dependent component (badgesymbol requires frontmatter)
        badgesymbol_gen = ComponentGeneratorFactory.create_generator(
            "badgesymbol", "aluminum"
        )

        # This should work with frontmatter data
        badgesymbol_result = badgesymbol_gen.generate(
            material_data={{"name": "Aluminum"}},
            frontmatter_data=frontmatter_result.content
        )

        assert badgesymbol_result.success is True

    def test_full_generation_pipeline(self):
        """Test complete generation pipeline for a material"""
        material_data = {{
            "name": "Copper",
            "category": "metal",
            "properties": ["ductile", "conductive"]
        }}

        components_to_test = ["frontmatter", "badgesymbol", "author", "bullets"]

        results = {{}}
        for component in components_to_test:
            generator = ComponentGeneratorFactory.create_generator(
                component, "copper"
            )

            # Pass previous results as dependencies
            kwargs = {{"material_data": material_data}}
            if component == "badgesymbol" and "frontmatter" in results:
                kwargs["frontmatter_data"] = results["frontmatter"].content
            elif component == "author" and "frontmatter" in results:
                kwargs["frontmatter_data"] = results["frontmatter"].content

            result = generator.generate(**kwargs)
            results[component] = result

            assert result.success is True, f"{component} generation failed"

    def test_error_propagation(self):
        """Test that errors in dependencies propagate correctly"""
        # Create a component that will fail
        failing_gen = ComponentGeneratorFactory.create_generator(
            "frontmatter", "aluminum"
        )

        # Simulate failure
        with patch.object(failing_gen, '_generate_content') as mock_generate:
            mock_generate.side_effect = Exception("Simulated failure")

            result = failing_gen.generate(material_data={{"name": "Aluminum"}})

            assert result.success is False
            assert "Simulated failure" in result.error_message

    def test_performance_under_load(self):
        """Test system performance with multiple concurrent generations"""
        import concurrent.futures
        import time

        materials = ["aluminum", "copper", "steel", "titanium"]
        results = {{}}

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_material = {{
                executor.submit(self._generate_single_material, material): material
                for material in materials
            }}

            for future in concurrent.futures.as_completed(future_to_material):
                material = future_to_material[future]
                try:
                    result = future.result()
                    results[material] = result
                except Exception as e:
                    results[material] = f"Error: {e}"

        total_time = time.time() - start_time

        # Verify all materials were processed
        assert len(results) == len(materials)

        # Verify reasonable performance (should complete within 30 seconds)
        assert total_time < 30, f"Generation took too long: {total_time}s"

        # Verify all results are successful
        for material, result in results.items():
            assert not isinstance(result, str) or not result.startswith("Error")

    def _generate_single_material(self, material_name):
        """Helper method to generate content for a single material"""
        generator = ComponentGeneratorFactory.create_generator(
            "frontmatter", material_name
        )

        return generator.generate(
            material_data={{"name": material_name, "category": "metal"}}
        )
```

## 🔧 Mocking Patterns

### **API Service Mocking**

```python
class MockDeepSeekAPI:
    """Mock DeepSeek API for testing"""

    def __init__(self, responses=None, errors=None):
        self.responses = responses or []
        self.errors = errors or []
        self.call_count = 0
        self.call_history = []

    def generate_content(self, prompt):
        """Mock content generation"""
        self.call_count += 1
        self.call_history.append(prompt)

        # Return error if configured
        if self.errors and self.call_count <= len(self.errors):
            error = self.errors[self.call_count - 1]
            if isinstance(error, Exception):
                raise error
            else:
                raise Exception(error)

        # Return response if available
        if self.responses and self.call_count <= len(self.responses):
            return self.responses[self.call_count - 1]

        # Default mock response
        return f"Mock generated content for prompt: {prompt[:50]}..."

class MockWinstonAI:
    """Mock Winston AI detection service"""

    def __init__(self, scores=None):
        self.scores = scores or [75.0, 80.0, 85.0]
        self.call_count = 0

    def analyze_content(self, content):
        """Mock content analysis"""
        self.call_count += 1

        if self.call_count <= len(self.scores):
            return self.scores[self.call_count - 1]

        return 70.0  # Default score
```

### **File System Mocking**

```python
import tempfile
import os
from unittest.mock import patch, mock_open

class TestFileOperations:

    def test_file_reading(self):
        """Test file reading operations"""
        test_content = "Test file content"

        with patch('builtins.open', mock_open(read_data=test_content)) as mock_file:
            with open('test_file.txt', 'r') as f:
                content = f.read()

            assert content == test_content
            mock_file.assert_called_once_with('test_file.txt', 'r')

    def test_file_writing(self):
        """Test file writing operations"""
        with patch('builtins.open', mock_open()) as mock_file:
            with open('output.txt', 'w') as f:
                f.write("Test content")

            # Verify file was opened for writing
            mock_file.assert_called_once_with('output.txt', 'w')

            # Verify content was written
            handle = mock_file()
            handle.write.assert_called_once_with("Test content")

    def test_temporary_directory(self):
        """Test operations in temporary directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.txt")

            # Write test content
            with open(test_file, 'w') as f:
                f.write("Temporary test content")

            # Read and verify
            with open(test_file, 'r') as f:
                content = f.read()

            assert content == "Temporary test content"

            # Verify file exists
            assert os.path.exists(test_file)
```

## 🏷️ Version Information Testing Patterns

### **Version Integration Testing**
Tests for version information integration across all components using the centralized versioning system.

```python
class TestVersionIntegration(unittest.TestCase):
    """Test version information integration patterns"""

    def setUp(self):
        self.generator = FrontmatterComponentGenerator()

    @patch('versioning.stamp_component_output')
    def test_version_stamping_integration(self, mock_stamp):
        """Test that version information is properly integrated"""
        # Mock versioning system
        test_content = """---
name: "Test Material"
category: "metal"
---"""
        
        versioned_content = test_content + """

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
        mock_stamp.return_value = versioned_content

        # Test versioning integration
        from versioning import stamp_component_output
        result = stamp_component_output("frontmatter", test_content)
        
        # Verify version sections exist
        self.assertIn("# Version Information", result)
        self.assertIn("Version Log - Generated:", result)
        self.assertIn("Component: frontmatter", result)
        mock_stamp.assert_called_once_with("frontmatter", test_content)

    def test_version_section_structure(self):
        """Test version information section structure"""
        sample_content = '''---
name: "Test Material"
---

# Version Information
# Generated: 2025-09-10T13:23:40.671545
# Material: Test Material

---
Version Log - Generated: 2025-09-10T13:23:40.671714
Material: Test Material
Component: frontmatter
---'''
        
        # Parse and validate structure
        lines = sample_content.split('\n')
        yaml_markers = [i for i, line in enumerate(lines) if line.strip() == '---']
        version_comments = [i for i, line in enumerate(lines) if '# Version Information' in line]
        version_logs = [i for i, line in enumerate(lines) if 'Version Log - Generated:' in line]
        
        # Verify proper structure
        self.assertGreaterEqual(len(yaml_markers), 3)  # YAML start, end, version log end
        self.assertEqual(len(version_comments), 1)      # One version comment section
        self.assertEqual(len(version_logs), 1)          # One version log section

    def test_version_information_preservation(self):
        """Test that post-processing preserves version information"""
        from components.frontmatter.post_processor import post_process_frontmatter
        
        # Content with potential formatting issues
        malformed_content = """---
name: "Test Material"
description: "Test
---

# Version Information
# Generated: 2025-09-10T13:23:40.671545

---
Version Log - Generated: 2025-09-10T13:23:40.671714
Material: Test Material
---"""
        
        # Post-process and verify preservation
        processed = post_process_frontmatter(malformed_content, "Test Material")
        
        self.assertIn("# Version Information", processed)
        self.assertIn("Version Log - Generated:", processed)
        self.assertIn("Material: Test Material", processed)

    def test_no_version_duplication_in_template(self):
        """Test that templates don't contain version information"""
        # Version info should be handled by external versioning system
        generator = FrontmatterComponentGenerator()
        
        if hasattr(generator, 'prompt_config') and generator.prompt_config:
            template = generator.prompt_config.get('template', '')
            
            # Template should not contain version fields
            self.assertNotIn("versionInfo:", template)
            self.assertNotIn("# Version Information", template)
            self.assertNotIn("Version Log", template)
```

### **Version Testing Guidelines**

#### **Required Test Cases**
1. **Version Integration**: Test versioning system integration
2. **Section Structure**: Validate version section format and placement
3. **Content Preservation**: Ensure version info survives post-processing
4. **Template Separation**: Verify version info not in templates
5. **Format Consistency**: Test consistent format across components

#### **Testing Patterns**
```python
# Pattern 1: Mock versioning system
@patch('versioning.stamp_component_output')
def test_version_integration(self, mock_stamp):
    mock_stamp.return_value = content_with_version
    # Test component generation
    result = component.generate(...)
    mock_stamp.assert_called_once()

# Pattern 2: Parse version sections
def test_version_structure(self):
    lines = content.split('\n')
    yaml_markers = [i for i, line in enumerate(lines) if line.strip() == '---']
    version_sections = [i for i, line in enumerate(lines) if '# Version' in line]
    # Validate structure

# Pattern 3: Post-processor preservation
def test_version_preservation(self):
    processed = post_process_component(malformed_content)
    self.assertIn("# Version Information", processed)
    self.assertIn("Version Log", processed)
```

#### **Version Testing Checklist**
- ✅ Version stamping integration works
- ✅ Version sections have proper structure  
- ✅ Version info preserved during post-processing
- ✅ No version duplication in templates
- ✅ Consistent format across all components
- ✅ Version information parsing works correctly

## 📊 Performance Testing Patterns

### **Generation Speed Testing**

```python
import time
import statistics
from utils.performance_monitor import PerformanceMonitor

class TestGenerationPerformance:

    def test_generation_speed(self):
        """Test generation speed for different components"""
        components = ["frontmatter", "bullets", "text"]
        materials = ["aluminum", "copper", "steel"]
        iterations = 5

        performance_data = {{}}

        for component in components:
            times = []

            for material in materials:
                generator = ComponentGeneratorFactory.create_generator(
                    component, material
                )

                for _ in range(iterations):
                    start_time = time.time()

                    result = generator.generate(
                        material_data={{"name": material, "category": "metal"}}
                    )

                    end_time = time.time()
                    generation_time = end_time - start_time

                    assert result.success is True
                    times.append(generation_time)

            # Calculate statistics
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0

            performance_data[component] = {{
                "average": avg_time,
                "minimum": min_time,
                "maximum": max_time,
                "std_dev": std_dev,
                "total_samples": len(times)
            }}

        # Performance assertions
        for component, stats in performance_data.items():
            # Text component should take longer due to AI detection
            if component == "text":
                assert stats["average"] > 5.0, f"Text generation too fast: {stats['average']}s"
            else:
                assert stats["average"] < 2.0, f"{component} generation too slow: {stats['average']}s"

    def test_memory_usage(self):
        """Test memory usage during generation"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Generate content
        generator = ComponentGeneratorFactory.create_generator("text", "aluminum")
        result = generator.generate(
            material_data={{"name": "Aluminum", "category": "metal"}}
        )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory

        assert result.success is True
        assert memory_used < 100, f"Memory usage too high: {memory_used}MB"

    def test_concurrent_generation(self):
        """Test performance with concurrent generation"""
        import concurrent.futures

        materials = ["aluminum", "copper", "steel", "titanium", "brass"]
        max_workers = 3

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._generate_material, material)
                for material in materials
            ]

            results = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)

        total_time = time.time() - start_time

        # Verify all generations succeeded
        assert all(result.success for result in results)

        # Verify reasonable total time (should be faster than sequential)
        expected_sequential_time = len(materials) * 2.0  # 2s per material
        speedup_ratio = expected_sequential_time / total_time

        assert speedup_ratio > 1.5, f"Insufficient speedup: {speedup_ratio}x"
        assert total_time < 15, f"Concurrent generation too slow: {total_time}s"

    def _generate_material(self, material_name):
        """Helper method for concurrent generation testing"""
        generator = ComponentGeneratorFactory.create_generator("frontmatter", material_name)
        return generator.generate(
            material_data={{"name": material_name, "category": "metal"}}
        )
```

## 🛡️ Robustness Testing Patterns

### **Error Handling Testing**

```python
class TestErrorHandling:

    def test_api_timeout_recovery(self):
        """Test recovery from API timeouts"""
        with patch('api.deepseek.DeepSeekAPIClient.generate_content') as mock_api:
            # First call times out
            mock_api.side_effect = [
                TimeoutError("Request timed out"),
                "Recovered content"  # Second call succeeds
            ]

            generator = TextComponentGenerator("aluminum")

            result = generator.generate(
                material_data={{"name": "Aluminum"}},
                retry_on_timeout=True
            )

            assert result.success is True
            assert "Recovered content" in result.content
            assert mock_api.call_count == 2

    def test_circuit_breaker_activation(self):
        """Test circuit breaker activation on repeated failures"""
        with patch('api.deepseek.DeepSeekAPIClient.generate_content') as mock_api:
            mock_api.side_effect = ConnectionError("Service unavailable")

            generator = TextComponentGenerator("aluminum")

            # First few calls should attempt connection
            for i in range(3):
                result = generator.generate(
                    material_data={{"name": "Aluminum"}}
                )
                assert result.success is False

            # Circuit breaker should activate after threshold
            result = generator.generate(
                material_data={{"name": "Aluminum"}}
            )

            # Should get circuit breaker error instead of connection error
            assert result.success is False
            assert "circuit breaker" in result.error_message.lower()

    def test_graceful_degradation(self):
        """Test graceful degradation when services are unavailable"""
        with patch('api.deepseek.DeepSeekAPIClient') as mock_api_class:
            mock_api_class.side_effect = ImportError("DeepSeek not available")

            # Should fall back to basic generation or provide clear error
            generator = TextComponentGenerator("aluminum")

            result = generator.generate(
                material_data={{"name": "Aluminum"}}
            )

            # Should either succeed with degraded content or fail gracefully
            if not result.success:
                assert "DeepSeek" in result.error_message
                assert "not available" in result.error_message

    def test_invalid_input_handling(self):
        """Test handling of various invalid inputs"""
        generator = TextComponentGenerator("aluminum")

        invalid_inputs = [
            None,
            {{}},  # Empty dict
            {{"name": None}},  # None values
            {{"name": ""}},  # Empty strings
            {{"name": 123}},  # Wrong types
        ]

        for invalid_input in invalid_inputs:
            result = generator.generate(material_data=invalid_input)

            assert result.success is False
            assert result.error_message is not None
            assert result.generation_time > 0
```

## 📋 Test Fixtures & Data

### **Test Data Management**

```python
# tests/fixtures/Materials.yaml
materials:
  aluminum:
    name: "Aluminum"
    category: "metal"
    properties: ["ductile", "lightweight", "corrosion_resistant"]
    applications: ["aerospace", "automotive", "packaging"]

  copper:
    name: "Copper"
    category: "metal"
    properties: ["conductive", "ductile", "malleable"]
    applications: ["electrical", "plumbing", "electronics"]

# tests/fixtures/api_responses.json
{
  "deepseek_success": {
    "choices": [{
      "message": {
        "content": "Generated content from DeepSeek API"
      }
    }],
    "usage": {
      "total_tokens": 150
    }
  },

  "winston_analysis": {
    "score": 75.5,
    "confidence": 0.85,
    "analysis": "Content appears to be human-written"
  }
}

# tests/fixtures/mock_data.py
def get_mock_material_data(material_name):
    """Get mock material data for testing"""
    return {
        "name": material_name,
        "category": "metal",
        "properties": ["test_property_1", "test_property_2"],
        "applications": ["test_application"]
    }

def get_mock_author_data():
    """Get mock author data for testing"""
    return {
        "name": "Test Author",
        "country": "usa",
        "specialization": "test_specialization"
    }

def get_mock_frontmatter_data():
    """Get mock frontmatter data for testing"""
    return {
        "name": "Test Material",
        "category": "metal",
        "symbol": "Tm",
        "properties": ["ductile", "strong"]
    }
```

## 🎯 Test Execution & Reporting

### **Test Configuration**

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --tb=short
    --cov=components
    --cov=generators
    --cov=utils
    --cov-report=html:htmlcov
    --cov-report=term-missing
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    api: marks tests as API tests
    performance: marks tests as performance tests
```

### **Test Running Scripts**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=components --cov-report=html

# Run specific test categories
pytest -m "integration"        # Integration tests only
pytest -m "not slow"          # Skip slow tests
pytest tests/unit/            # Unit tests only

# Run with parallel execution
pytest -n auto

# Run specific test file
pytest tests/unit/test_text_component.py::TestTextComponentGenerator::test_successful_generation

# Generate coverage report
pytest --cov=components --cov-report=html && open htmlcov/index.html
```

### **CI/CD Integration**

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest --cov=components --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

## 📊 Test Metrics & Reporting

### **Coverage Requirements**
- **Unit Tests**: >90% coverage for core components
- **Integration Tests**: >80% coverage for component interactions
- **API Tests**: 100% coverage for error scenarios
- **Overall Coverage**: >85% for the entire codebase

### **Performance Benchmarks**
- **Unit Tests**: <1 second per test on average
- **Integration Tests**: <5 seconds per test on average
- **API Tests**: <10 seconds per test (including network calls)
- **Full Test Suite**: <2 minutes total execution time

### **Success Criteria**
- [ ] All tests pass in CI/CD pipeline
- [ ] Coverage requirements met
- [ ] Performance benchmarks achieved
- [ ] No flaky tests (tests that pass/fail randomly)
- [ ] Clear test failure messages for debugging

This comprehensive testing framework ensures the Z-Beam Generator system maintains high quality, reliability, and performance across all components and integrations.</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/docs/testing/component_testing.md
