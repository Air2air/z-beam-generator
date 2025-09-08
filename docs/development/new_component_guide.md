# 🔧 New Component Development Guide

## **Purpose**
This guide provides a step-by-step blueprint for AI assistants to add new components to the Z-Beam Generator system. It ensures consistency, proper integration, and adherence to established patterns.

## 📋 Requirements

### **Prerequisites**
- [ ] Understand the component architecture ([Component Standards](../COMPONENT_STANDARDS.md))
- [ ] Review the base generator class ([Generator Base Blueprint](../components/generator_base.md))
- [ ] Identify the component's purpose and requirements
- [ ] Determine API dependencies and data sources

### **Required Skills**
- Python 3.8+ development
- YAML configuration files
- API integration patterns
- Unit testing with pytest
- Error handling patterns

## 🏗️ Architecture Planning

### **Step 1: Define Component Requirements**

```yaml
# Example component specification
component:
  name: "new_component"
  type: "metadata"  # content, metadata, structure, presentation
  api_provider: "deepseek"  # none, deepseek, gemini, etc.
  ai_detection: false  # true if content quality matters
  dependencies:
    - "frontmatter"  # Components this one depends on
  output_format: "markdown"  # markdown, json, yaml, html
  real_time_updates: false  # true for long-running components
```

### **Step 2: Plan Directory Structure**

```
components/{component_name}/
├── __init__.py                    # Package initialization
├── generator.py                  # Main generator class
├── mock_generator.py             # Mock for testing
├── validator.py                  # Input/output validation
├── prompt.yaml                   # Component prompts/configuration
├── example_{component}.md        # Usage example
├── README.md                     # Component documentation
└── testing/
    └── test_{component}.py       # Unit tests
```

### **Step 3: Design API Integration**

```python
# Choose appropriate API client pattern
if component_config['api_provider'] == 'deepseek':
    from api.deepseek import DeepSeekAPIClient
elif component_config['api_provider'] == 'gemini':
    from api.gemini import GeminiAPIClient
else:
    # Static generation - no API needed
    pass
```

## 🔧 Implementation Steps

### **Step 4: Create Base Files**

#### **`__init__.py`**
```python
"""
{Component Name} component for Z-Beam Generator.

This component generates {brief description}.
"""

from .generator import {ComponentName}Generator
from .validator import {ComponentName}Validator

__all__ = ['{ComponentName}Generator', '{ComponentName}Validator']
```

#### **`generator.py`**
```python
from components.base import ComponentGenerator, ComponentResult
from typing import Dict, Any, Optional
import time

class {ComponentName}Generator(ComponentGenerator):
    """Generator for {component_name} component"""

    def __init__(self, material_name: str, **kwargs):
        super().__init__(material_name, **kwargs)
        self.validator = {ComponentName}Validator()
        # Initialize API client if needed
        # self.api_client = APIClient() if needs_api else None

    def get_component_type(self) -> str:
        return "{component_name}"

    def validate_inputs(self, **kwargs) -> bool:
        """Validate component-specific inputs"""
        # Implement validation logic
        required_fields = ['material_data']  # Add your requirements
        return all(field in kwargs for field in required_fields)

    def generate(self, **kwargs) -> ComponentResult:
        """Generate {component_name} content"""
        try:
            # Validate inputs
            if not self.validate_inputs(**kwargs):
                return self.handle_error(ValueError("Invalid inputs"))

            # Extract parameters
            material_data = kwargs.get('material_data', {})

            # Generate content
            content = self._generate_content(material_data)

            # Return success result
            return self.create_success_result(
                content=content,
                metadata={{
                    'material': self.material_name,
                    'generation_method': 'static'  # or 'api'
                }}
            )

        except Exception as e:
            return self.handle_error(e)

    def _generate_content(self, material_data: Dict[str, Any]) -> str:
        """Implementation-specific content generation"""
        # Your generation logic here
        return f"Generated {self.get_component_type()} for {material_data.get('name', 'unknown')}"
```

#### **`validator.py`**
```python
from typing import Dict, Any, List

class {ComponentName}Validator:
    """Validation logic for {component_name} component"""

    def validate_input(self, material_data: Dict[str, Any]) -> List[str]:
        """Validate input data and return list of errors"""
        errors = []

        # Required field validation
        required_fields = ['name', 'category']
        for field in required_fields:
            if field not in material_data:
                errors.append(f"Missing required field: {field}")

        # Data type validation
        if 'name' in material_data and not isinstance(material_data['name'], str):
            errors.append("Field 'name' must be a string")

        return errors

    def validate_output(self, content: str) -> List[str]:
        """Validate generated content"""
        errors = []

        if not content or len(content.strip()) == 0:
            errors.append("Generated content is empty")

        if len(content) < 10:  # Minimum length check
            errors.append("Generated content is too short")

        return errors
```

#### **`prompt.yaml`**
```yaml
# {Component Name} Component Configuration
component:
  name: "{component_name}"
  description: "Brief description of what this component generates"
  version: "1.0.0"

generation:
  method: "static"  # or "api"
  api_provider: "none"  # or "deepseek", "gemini", etc.
  ai_detection: false

prompts:
  system: |
    You are a technical content generator specializing in {domain}.
    Generate {component_type} content that is accurate, professional, and useful.

  user_template: |
    Generate {component_type} for the following material:

    Material: {{material_name}}
    Category: {{material_category}}
    Properties: {{material_properties}}

    Requirements:
    - {specific requirements}
    - {formatting guidelines}
    - {quality standards}

output:
  format: "markdown"
  min_length: 50
  max_length: 500
```

### **Step 5: Create Mock for Testing**

#### **`mock_generator.py`**
```python
from components.base import ComponentResult
from .generator import {ComponentName}Generator
from typing import Dict, Any
import time

class Mock{ComponentName}Generator({ComponentName}Generator):
    """Mock implementation for testing {component_name} component"""

    def _generate_content(self, material_data: Dict[str, Any]) -> str:
        """Return mock content for testing"""
        material_name = material_data.get('name', 'Unknown Material')

        return f"""# Mock {self.get_component_type().title()} for {material_name}

This is mock content generated for testing purposes.

## Material Information
- **Name**: {material_name}
- **Category**: {material_data.get('category', 'Unknown')}
- **Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Mock Content
This component would generate actual {self.get_component_type()} content here.
For testing purposes, this mock content is returned instead.

## Testing Notes
- Component type: {self.get_component_type()}
- Material: {self.material_name}
- Generation time: Mock implementation
"""

    def generate_with_error(self, error_type: str = "general") -> ComponentResult:
        """Generate a mock error for testing error handling"""
        if error_type == "validation":
            return self.handle_error(ValueError("Mock validation error"))
        elif error_type == "api":
            return self.handle_error(ConnectionError("Mock API error"))
        else:
            return self.handle_error(RuntimeError("Mock general error"))
```

## 🧪 Testing Implementation

### **Step 6: Create Unit Tests**

#### **`testing/test_{component}.py`**
```python
import pytest
from components.{component_name}.generator import {ComponentName}Generator
from components.{component_name}.mock_generator import Mock{ComponentName}Generator
from components.{component_name}.validator import {ComponentName}Validator

class Test{ComponentName}Generator:

    @pytest.fixture
    def generator(self):
        return {ComponentName}Generator("test_material")

    @pytest.fixture
    def mock_generator(self):
        return Mock{ComponentName}Generator("test_material")

    @pytest.fixture
    def validator(self):
        return {ComponentName}Validator()

    def test_component_type(self, generator):
        """Test component type identification"""
        assert generator.get_component_type() == "{component_name}"

    def test_successful_generation(self, mock_generator):
        """Test successful content generation"""
        material_data = {
            "name": "Test Material",
            "category": "test_category",
            "properties": ["test_property"]
        }

        result = mock_generator.generate(material_data=material_data)

        assert result.success is True
        assert result.component_type == "{component_name}"
        assert "Test Material" in result.content
        assert result.generation_time > 0

    def test_input_validation_failure(self, generator):
        """Test input validation"""
        result = generator.generate()  # Missing required inputs

        assert result.success is False
        assert "Invalid inputs" in result.error_message

    def test_error_handling(self, mock_generator):
        """Test error handling"""
        result = mock_generator.generate_with_error("general")

        assert result.success is False
        assert result.error_message is not None
        assert "Mock general error" in result.error_message

    def test_validator_functionality(self, validator):
        """Test input validation"""
        # Valid input
        valid_data = {"name": "Test", "category": "Metal"}
        errors = validator.validate_input(valid_data)
        assert len(errors) == 0

        # Invalid input
        invalid_data = {}  # Missing required fields
        errors = validator.validate_input(invalid_data)
        assert len(errors) > 0
        assert "Missing required field" in errors[0]

class Test{ComponentName}Integration:
    """Integration tests for {component_name} component"""

    def test_end_to_end_generation(self, mock_generator):
        """Test complete generation workflow"""
        material_data = {
            "name": "Integration Test Material",
            "category": "integration_test"
        }

        result = mock_generator.generate(material_data=material_data)

        assert result.success is True
        assert len(result.content) > 100  # Substantial content
        assert result.metadata['material'] == "test_material"
```

## 🔧 Integration Steps

### **Step 7: Register Component**

#### **Update Component Factory**
```python
# In generators/component_generators.py
from components.{component_name}.generator import {ComponentName}Generator

class ComponentGeneratorFactory:
    """Factory for creating component generators"""

    _generators = {{
        # ... existing generators ...
        "{component_name}": {ComponentName}Generator,
    }}

    @classmethod
    def create_generator(cls, component_type: str, material_name: str, **kwargs):
        """Create appropriate generator for component type"""
        generator_class = cls._generators.get(component_type)
        if not generator_class:
            raise ValueError(f"Unknown component type: {component_type}")

        return generator_class(material_name, **kwargs)
```

#### **Update Main Configuration**
```python
# In run.py or main configuration
COMPONENT_TYPES = [
    # ... existing components ...
    "{component_name}",
]

# Component configuration
COMPONENT_CONFIG = {{
    # ... existing config ...
    "{component_name}": {{
        "api_provider": "none",  # or appropriate API
        "ai_detection": False,
        "dependencies": [],  # Add dependencies if any
    }},
}}
```

### **Step 8: Add to Test Suite**

#### **Update Unified Tests**
```python
# In run_unified_tests.py
def test_{component_name}_component():
    """Test {component_name} component generation"""
    generator = {ComponentName}Generator("aluminum")

    result = generator.generate(material_data={{"name": "Aluminum"}})

    assert result.success is True
    assert result.component_type == "{component_name}"
    print(f"✅ {ComponentName} component test passed")
```

## 📊 Monitoring Setup

### **Step 9: Add Health Checks**

```python
# In utils/health_monitor.py
def check_{component_name}_health() -> Dict[str, Any]:
    """Health check for {component_name} component"""
    try:
        generator = {ComponentName}Generator("health_check_material")
        result = generator.generate(material_data={{"name": "Health Check"}})

        return {{
            "component": "{component_name}",
            "status": "healthy" if result.success else "degraded",
            "response_time": result.generation_time,
            "timestamp": time.time()
        }}
    except Exception as e:
        return {{
            "component": "{component_name}",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }}
```

### **Step 10: Add Performance Monitoring**

```python
# In utils/performance_monitor.py
def monitor_{component_name}_performance():
    """Monitor {component_name} component performance"""
    # Track generation times, success rates, error patterns
    metrics = {{
        "component": "{component_name}",
        "avg_generation_time": calculate_average_generation_time(),
        "success_rate": calculate_success_rate(),
        "error_rate": calculate_error_rate(),
        "peak_memory_usage": get_peak_memory_usage()
    }}

    return metrics
```

## 📚 Documentation

### **Step 11: Create Component Documentation**

#### **`README.md`**
```markdown
# {Component Name} Component

## Overview
Brief description of what this component generates and its purpose in the system.

## Configuration
```yaml
# Component configuration in main config
{component_name}:
  api_provider: "none"
  ai_detection: false
  dependencies: []
```

## Usage
```python
from components.{component_name}.generator import {ComponentName}Generator

generator = {ComponentName}Generator("material_name")
result = generator.generate(material_data={{"name": "Material"}})

if result.success:
    print(result.content)
else:
    print(f"Error: {result.error_message}")
```

## Dependencies
- List of components this depends on
- Required data structures
- API requirements

## Output Format
Description of the output format and structure.

## Testing
```bash
# Run component tests
python -m pytest components/{component_name}/testing/

# Run with mock data
python -c "from components.{component_name}.mock_generator import Mock{ComponentName}Generator; print('Mock test passed')"
```
```

#### **`example_{component}.md`**
```markdown
# Example {Component Name} Output

This file shows an example of the output generated by the {component_name} component.

## Generated Content

[Actual example content would go here]

## Metadata
- **Component**: {component_name}
- **Material**: Example Material
- **Generated**: 2025-01-08
- **Word Count**: 150
```

## ✅ Validation Checklist

### **Pre-Implementation**
- [ ] Component requirements defined
- [ ] API dependencies identified
- [ ] Directory structure planned
- [ ] Integration points identified

### **Implementation**
- [ ] Base files created (`__init__.py`, `generator.py`, `validator.py`)
- [ ] Mock generator implemented
- [ ] Unit tests written
- [ ] Component factory updated
- [ ] Configuration updated

### **Testing**
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Mock generator works
- [ ] Error handling tested

### **Documentation**
- [ ] README.md created
- [ ] Example output provided
- [ ] Usage examples documented
- [ ] Configuration documented

### **Integration**
- [ ] Component registered in factory
- [ ] Added to unified test suite
- [ ] Health checks implemented
- [ ] Performance monitoring added

## 🔄 Maintenance

### **Regular Tasks**
- [ ] Monitor performance metrics
- [ ] Review error patterns
- [ ] Update test cases as needed
- [ ] Refresh example outputs

### **Update Procedures**
- [ ] Minor updates: Update version in `prompt.yaml`
- [ ] Major updates: Update documentation and examples
- [ ] Breaking changes: Update integration tests

## 📞 Support

For questions about this component:
1. Check this README first
2. Review the base generator blueprint
3. Look at existing component implementations
4. Run the test suite for examples

---

**Component Status**: 🟢 Ready for production use
**Last Updated**: 2025-01-08
**Version**: 1.0.0
```

## 🎯 Success Criteria

### **Component is Complete When:**
- [ ] All files created and implemented
- [ ] Unit tests pass (100% coverage for core functionality)
- [ ] Integration tests pass
- [ ] Documentation is complete and accurate
- [ ] Component works in unified test suite
- [ ] Health checks are green
- [ ] Performance monitoring is active

### **Component is Production-Ready When:**
- [ ] Used successfully in at least 3 different materials
- [ ] No critical bugs reported in 30 days
- [ ] Performance metrics are within acceptable ranges
- [ ] Documentation is up-to-date and accurate
- [ ] Integration with other components is smooth

This guide ensures that new components are consistently implemented, properly tested, and well-documented, maintaining the high quality standards of the Z-Beam Generator system.</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/docs/development/new_component_guide.md
