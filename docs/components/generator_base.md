# 🎯 Component Generator Base Blueprint

## **Purpose**
The ComponentGenerator base class provides the foundation for all content generation components in the Z-Beam system. It establishes consistent patterns for component development, error handling, validation, and result management.

## 📋 Requirements

### **Dependencies**
- Python 3.8+
- `pathlib.Path` for file operations
- `typing` module for type hints
- `dataclasses` for result objects

### **Prerequisites**
- Component must inherit from `ComponentGenerator`
- Component must implement `generate()` method
- Component must return `ComponentResult` objects

## 🏗️ Architecture

### **Class Hierarchy**
```
ComponentGenerator (Abstract Base)
├── generate() -> ComponentResult
├── validate_inputs() -> bool
├── get_component_type() -> str
└── handle_error() -> ComponentResult

ComponentResult (Data Class)
├── component_type: str
├── content: str
├── success: bool
├── error_message: Optional[str]
├── metadata: Dict[str, Any]
└── generation_time: float
```

### **Key Design Patterns**
- **Template Method**: Base class defines workflow, subclasses implement specifics
- **Factory Pattern**: Component creation through factory methods
- **Result Object**: Structured return values with success/error states
- **Fail-Fast**: Immediate validation and error reporting

## 🔧 Implementation

### **Base Class Structure**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import time

@dataclass
class ComponentResult:
    """Standardized result object for all component operations"""
    component_type: str
    content: str = ""
    success: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    generation_time: float = 0.0

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ComponentGenerator(ABC):
    """Abstract base class for all component generators"""

    def __init__(self, material_name: str, **kwargs):
        self.material_name = material_name
        self.start_time = time.time()
        self._validate_initialization()

    def _validate_initialization(self):
        """Validate that component is properly initialized"""
        if not self.material_name:
            raise ValueError("Material name is required")

    @abstractmethod
    def generate(self, **kwargs) -> ComponentResult:
        """Main generation method - must be implemented by subclasses"""
        pass

    @abstractmethod
    def get_component_type(self) -> str:
        """Return the component type identifier"""
        pass

    def validate_inputs(self, **kwargs) -> bool:
        """Validate input parameters - override in subclasses"""
        return True

    def handle_error(self, error: Exception, **kwargs) -> ComponentResult:
        """Standard error handling - can be overridden"""
        generation_time = time.time() - self.start_time

        return ComponentResult(
            component_type=self.get_component_type(),
            content="",
            success=False,
            error_message=str(error),
            metadata={"error_type": type(error).__name__},
            generation_time=generation_time
        )

    def create_success_result(self, content: str, **metadata) -> ComponentResult:
        """Helper method to create successful results"""
        generation_time = time.time() - self.start_time

        return ComponentResult(
            component_type=self.get_component_type(),
            content=content,
            success=True,
            metadata=metadata,
            generation_time=generation_time
        )
```

### **Implementation Example**

```python
class TextComponentGenerator(ComponentGenerator):
    """Example implementation of a text component generator"""

    def get_component_type(self) -> str:
        return "text"

    def validate_inputs(self, **kwargs) -> bool:
        """Validate text generation inputs"""
        required_fields = ['material_data', 'author_info']
        for field in required_fields:
            if field not in kwargs:
                return False
        return True

    def generate(self, **kwargs) -> ComponentResult:
        """Generate text content"""
        try:
            # Validate inputs first
            if not self.validate_inputs(**kwargs):
                return self.handle_error(
                    ValueError("Missing required input fields")
                )

            # Extract parameters
            material_data = kwargs['material_data']
            author_info = kwargs['author_info']

            # Generate content (implementation specific)
            content = self._generate_text_content(material_data, author_info)

            # Return success result
            return self.create_success_result(
                content=content,
                word_count=len(content.split()),
                material=material_data.get('name', 'unknown')
            )

        except Exception as e:
            return self.handle_error(e)

    def _generate_text_content(self, material_data: Dict, author_info: Dict) -> str:
        """Implementation-specific content generation logic"""
        # Your generation logic here
        return f"Generated content for {material_data.get('name', 'material')}"
```

## 🧪 Testing

### **Unit Test Pattern**

```python
import pytest
from components.base import ComponentGenerator, ComponentResult

class TestComponentGenerator:

    def test_successful_generation(self):
        """Test successful component generation"""
        generator = TextComponentGenerator("aluminum")

        result = generator.generate(
            material_data={"name": "Aluminum", "category": "metal"},
            author_info={"name": "Test Author"}
        )

        assert result.success is True
        assert result.component_type == "text"
        assert result.content is not None
        assert result.generation_time > 0

    def test_input_validation_failure(self):
        """Test input validation failure"""
        generator = TextComponentGenerator("aluminum")

        result = generator.generate()  # Missing required inputs

        assert result.success is False
        assert "Missing required input fields" in result.error_message

    def test_error_handling(self):
        """Test error handling"""
        generator = TextComponentGenerator("aluminum")

        # Simulate an error in generation
        result = generator.generate(
            material_data={"name": "Aluminum"},
            author_info={"name": "Test Author"},
            simulate_error=True
        )

        assert result.success is False
        assert result.error_message is not None
        assert result.generation_time > 0
```

### **Mock Implementation Pattern**

```python
class MockTextComponentGenerator(ComponentGenerator):
    """Mock implementation for testing"""

    def get_component_type(self) -> str:
        return "text"

    def generate(self, **kwargs) -> ComponentResult:
        """Mock generation - returns predictable results"""
        if kwargs.get('simulate_error', False):
            raise ValueError("Simulated error for testing")

        return self.create_success_result(
            content="Mock generated content",
            word_count=3,
            material=self.material_name
        )
```

## 📊 Monitoring

### **Performance Metrics**
- **Generation Time**: Track time from initialization to result
- **Success Rate**: Percentage of successful generations
- **Error Patterns**: Common failure modes and frequencies
- **Resource Usage**: Memory and CPU utilization

### **Health Checks**
```python
def health_check_component(generator_class: type) -> Dict[str, Any]:
    """Health check for component generators"""
    try:
        # Test instantiation
        generator = generator_class("test_material")

        # Test basic generation
        result = generator.generate(test_data=True)

        return {
            "status": "healthy" if result.success else "degraded",
            "generation_time": result.generation_time,
            "component_type": generator.get_component_type(),
            "last_check": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": time.time()
        }
```

## 🔄 Maintenance

### **Update Procedures**
1. **Weekly**: Review error patterns and performance metrics
2. **Monthly**: Update base class with new common functionality
3. **Quarterly**: Major architecture changes and refactoring

### **Extension Points**
- **New Result Fields**: Add to `ComponentResult` dataclass
- **Common Validation**: Add to base `validate_inputs()` method
- **Shared Utilities**: Add helper methods to base class
- **Monitoring Hooks**: Add performance tracking methods

### **Migration Guide**
When updating existing components to use the new base class:

1. **Inherit from ComponentGenerator**
2. **Implement required abstract methods**
3. **Update return types to ComponentResult**
4. **Add input validation**
5. **Update error handling**
6. **Add unit tests**

## 📚 Related Documentation

- **[Component Standards](../COMPONENT_STANDARDS.md)** - Overall component development standards
- **[Error Handling Patterns](../development/error_handling.md)** - Error management patterns
- **[Testing Patterns](../testing/component_testing.md)** - Component testing approaches
- **[Factory Pattern](../development/factory_patterns.md)** - Component factory implementation</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/docs/components/generator_base.md
