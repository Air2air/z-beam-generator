# Component Structure Standards

## 📁 Standard Component Directory Structure

Every component should follow this consistent structure:

```
components/{component_name}/
├── __init__.py                 # Package initialization
├── generator.py               # Main component generator
├── mock_generator.py          # Mock generator for testing
├── post_processor.py          # Post-processing utilities
├── validator.py               # Component validation
├── prompt.yaml               # Component prompts/configuration
├── example_{component}.md    # Example output
├── README.md                 # Component documentation
└── testing/                  # Component-specific tests
    └── test_{component}.py
```

## 📋 Required Files for All Components

### Core Files (Required)
- `__init__.py` - Package initialization
- `generator.py` - Main generation logic
- `validator.py` - Input/output validation
- `prompt.yaml` - Prompts and configuration
- `example_{component}.md` - Usage example

### Testing Files (Required)
- `mock_generator.py` - Mock implementation for testing
- `testing/test_{component}.py` - Component unit tests

### Hybrid Component Testing Rule

**For hybrid data components** (components that combine API-generated content with static source data):

- ✅ **API data fields**: Can use mock API clients for testing
- ✅ **Static source data**: Must be used and tested without mocking
- ✅ **Data validation**: Static data must be validated against real schemas
- ✅ **Integration testing**: Test both mocked API and real static data together

**Example Implementation:**
```python
def test_hybrid_component():
    """Test hybrid component with mock API but real static data."""
    # Use mock API for generated content
    mock_client = get_mock_api_client()

    # Use REAL static data source
    static_data = load_static_data_from_file("Materials.yaml")

    result = component.generate(
        material_name="Steel",
        static_data=static_data,  # Real data, no mocking
        api_client=mock_client    # Mock API for generated fields
    )

    # Validate integration
    assert result.success
    assert static_data_integrity(static_data, result)
    assert api_content_quality(result.generated_content)
```

### Documentation (Required)
- `README.md` - Component documentation

### Optional Files
- `post_processor.py` - Post-processing utilities
- `utils.py` - Component-specific utilities
- `calculator.py` - Calculation utilities (if needed)

## 🔧 Component File Standards

### generator.py
- Must inherit from ComponentGenerator base class
- Must implement `generate()` method
- Must include comprehensive error handling
- Must validate inputs and fail-fast on invalid data

### validator.py
- Must validate component inputs and outputs
- Must provide clear error messages
- Must handle edge cases gracefully

### README.md
- Must include component description
- Must document configuration options
- Must provide usage examples
- Must list dependencies and requirements

## ✅ Compliance Checklist

- [ ] Standard directory structure
- [ ] All required files present
- [ ] Consistent naming conventions
- [ ] Proper documentation
- [ ] Unit tests implemented
- [ ] Mock generator for testing</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/docs/COMPONENT_STANDARDS.md
