# Testing Guide

Comprehensive guide to the Z-Beam Generator test framework, test organization, and testing strategies.

## Overview

The testing system validates:
- ✅ Data integrity (materials.yaml, Categories.yaml)
- ✅ Component generation (frontmatter, text, caption, tags)
- ✅ API connectivity and error handling
- ✅ Validation and quality control
- ✅ Integration between components

## Test Organization

```
tests/
├── unit/                          # Unit tests (fast, isolated)
│   ├── test_materials_loading.py
│   ├── test_validation_rules.py
│   └── test_data_structures.py
│
├── integration/                   # Integration tests (components working together)
│   ├── test_frontmatter_pipeline.py
│   ├── test_api_integration.py
│   └── test_component_interaction.py
│
├── e2e/                           # End-to-end tests (full workflows)
│   ├── test_single_material_generation.py
│   └── test_batch_operations.py
│
├── fixtures/                      # Test data and mocks
│   ├── sample_materials.yaml
│   ├── expected_outputs/
│   └── mocks/
│
└── validation/                    # Validation-specific tests
    ├── test_materials_validation.py
    ├── test_fail_fast_validation.py
    └── test_quality_scoring.py
```

## Running Tests

### Quick Test Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_materials_loading.py

# Run tests matching pattern
pytest -k "frontmatter"

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html

# Run fast tests only (skip slow E2E)
pytest -m "not slow"
```

### Test Categories

```bash
# Unit tests only (fast, < 1 minute)
pytest tests/unit/

# Integration tests (moderate, 2-5 minutes)
pytest tests/integration/

# End-to-end tests (slow, 5-15 minutes)
pytest tests/e2e/

# Validation tests
pytest tests/validation/
```

## Key Test Files

### Data Validation Tests

**`tests/test_materials_yaml.py`**
- Validates materials.yaml structure
- Checks flattened format compliance
- Verifies all 121 materials exist
- Confirms category embedding

**`tests/validation/test_fail_fast_validation.py`**
- Tests fail-fast architecture
- Ensures no mock APIs in production
- Validates error handling
- Confirms explicit configuration

### Component Tests

**`tests/frontmatter/test_frontmatter_generator.py`**
- Tests frontmatter generation
- Validates simple string applications
- Checks camelCase caption format
- Confirms tags generation

**`tests/integration/test_caption_frontmatter_integration.py`**
- Tests caption integration with frontmatter
- Validates camelCase format
- Checks required caption fields

### API Tests

**`tests/test_api_connectivity_validation.py`**
- Tests API connectivity
- Validates API keys
- Checks error handling
- Confirms timeout behavior

## Writing New Tests

### Unit Test Template

```python
"""
Test module for [component/feature name].
"""
import pytest
from pathlib import Path

def test_basic_functionality():
    """Test basic [feature] functionality."""
    # Arrange
    input_data = {"test": "data"}
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result is not None
    assert "expected_key" in result


def test_error_handling():
    """Test [feature] handles errors properly."""
    with pytest.raises(ValueError, match="Expected error message"):
        function_under_test(invalid_input)


@pytest.mark.slow
def test_slow_operation():
    """Test that takes > 5 seconds (marked as slow)."""
    # Long-running test code
    pass
```

### Integration Test Template

```python
"""
Integration test for [components] working together.
"""
import pytest
import yaml
from pathlib import Path

@pytest.fixture
def sample_material():
    """Provide sample material data for testing."""
    return {
        "name": "TestMaterial",
        "category": "metal",
        "properties": {"density": 2.7}
    }


def test_component_integration(sample_material):
    """Test [component A] integrates with [component B]."""
    # Arrange
    component_a = ComponentA(sample_material)
    component_b = ComponentB()
    
    # Act
    result = component_b.process(component_a.generate())
    
    # Assert
    assert result is not None
    assert result.is_valid()
```

### E2E Test Template

```python
"""
End-to-end test for [workflow].
"""
import pytest
import subprocess
from pathlib import Path

@pytest.mark.slow
@pytest.mark.e2e
def test_full_generation_workflow():
    """Test complete material generation workflow."""
    # Arrange
    material = "TestMaterial"
    output_dir = Path("content/components/frontmatter")
    output_file = output_dir / f"{material.lower()}-laser-cleaning.yaml"
    
    # Clean up any existing file
    if output_file.exists():
        output_file.unlink()
    
    # Act - Run generation
    result = subprocess.run(
        ["python3", "run.py", "--material", material, "--components", "frontmatter"],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    # Assert - Check success
    assert result.returncode == 0, f"Generation failed: {result.stderr}"
    assert output_file.exists(), "Output file not created"
    
    # Assert - Validate content
    with open(output_file) as f:
        data = yaml.safe_load(f)
    
    assert "applications" in data
    assert isinstance(data["applications"], list)
    assert len(data["applications"]) >= 2
    assert "caption" in data
    assert "beforeText" in data["caption"]  # camelCase
    assert "tags" in data
    assert len(data["tags"]) >= 4
```

## Test Fixtures

### Common Fixtures

Located in `tests/conftest.py`:

```python
@pytest.fixture
def materials_data():
    """Load actual materials.yaml for testing."""
    from data.materials import load_materials
    return load_materials()


@pytest.fixture
def sample_frontmatter():
    """Provide sample frontmatter structure."""
    return {
        "name": "Aluminum",
        "category": "metal",
        "title": "Aluminum Laser Cleaning",
        "applications": [
            "Aerospace: Precision cleaning of components",
            "Manufacturing: Surface preparation"
        ],
        "caption": {
            "beforeText": "At 500x magnification...",
            "afterText": "Following laser cleaning...",
            "description": "Microscopic analysis...",
            "alt": "Aluminum surface before and after"
        },
        "tags": ["metal", "aerospace", "manufacturing"]
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
```

## Test Data

### Sample Materials

Located in `tests/fixtures/sample_materials.yaml`:

```yaml
materials:
  TestAluminum:
    category: metal
    properties:
      density: 2.7
      meltingPoint: 660
    applications:
      - "Aerospace: Testing applications"
      - "Manufacturing: Test cleaning"
```

### Expected Outputs

Located in `tests/fixtures/expected_outputs/`:

```
expected_outputs/
├── aluminum_frontmatter.yaml
├── copper_frontmatter.yaml
└── zinc_frontmatter.yaml
```

## Validation Tests

### Materials Validation

**Test**: `tests/validation/test_materials_validation.py`

Validates:
- All 121 materials present
- Flattened structure correct
- Categories embedded properly
- No missing required fields

### Frontmatter Compliance

**Test**: `tests/validation/test_frontmatter_compliance.py`

Validates:
- Simple string applications
- CamelCase caption format
- Tag arrays (4-10 items)
- Required fields present

### Fail-Fast Architecture

**Test**: `tests/validation/test_fail_fast_validation.py`

Validates:
- No mock APIs in production code
- No default fallback values
- Proper error messages
- Configuration validation

## Continuous Testing

### Pre-Commit Tests

Run before committing:
```bash
# Fast tests only
pytest tests/unit/ tests/validation/ -v

# Check test coverage
pytest --cov=. --cov-report=term-missing tests/unit/
```

### Pre-Push Tests

Run before pushing:
```bash
# All tests except slow E2E
pytest -v -m "not slow"

# Generate coverage report
pytest --cov=. --cov-report=html
```

### Pre-Deployment Tests

Run before deploying:
```bash
# All tests including E2E
pytest -v

# Validate all frontmatter files
python3 scripts/tools/verify_frontmatter_compliance.py

# Check API connectivity
python3 scripts/validation/check_api_status.py
```

## Test Coverage

### Current Coverage

```bash
# Generate coverage report
pytest --cov=. --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| data/materials.py | 90% | TBD |
| pipeline_integration.py | 85% | TBD |
| Component generators | 80% | TBD |
| API clients | 75% | TBD |

## Testing Best Practices

### DO ✅

1. **Write tests first** for new features (TDD)
2. **Test happy path and error cases**
3. **Use descriptive test names** that explain what's being tested
4. **Keep tests independent** (no test dependencies)
5. **Mock external services** in unit tests
6. **Use real APIs** in integration tests (with test keys)
7. **Mark slow tests** with `@pytest.mark.slow`
8. **Clean up test data** in teardown/fixtures

### DON'T ❌

1. **Don't commit failing tests** without marking as `xfail`
2. **Don't test implementation details** (test behavior)
3. **Don't use sleep()** for timing (use proper waiting)
4. **Don't share state** between tests
5. **Don't skip cleanup** even if test fails
6. **Don't hardcode paths** (use Path objects)
7. **Don't ignore warnings** (fix or suppress explicitly)

## Debugging Tests

### Run Single Test with Debug Output

```bash
# Run with print statements visible
pytest -s tests/unit/test_materials_loading.py::test_specific_function

# Run with debugger
pytest --pdb tests/unit/test_materials_loading.py

# Run with extra verbosity
pytest -vv tests/unit/test_materials_loading.py
```

### Common Test Issues

**1. Import Errors**
```
ImportError: No module named 'data'
```
**Solution**: Run from project root, not tests/ directory

**2. Fixture Not Found**
```
fixture 'materials_data' not found
```
**Solution**: Ensure fixtures defined in conftest.py

**3. API Timeouts**
```
Test timed out after 30 seconds
```
**Solution**: Increase timeout or mock API for unit tests

## Test Automation

### GitHub Actions (Future)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest -v -m "not slow"
```

### Pre-Commit Hooks (Future)

```.pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-fast
        name: Fast Unit Tests
        entry: pytest tests/unit/ -v
        language: system
        pass_filenames: false
```

## See Also

- [Contributing Guide](CONTRIBUTING.md) - Contribution guidelines
- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md) - System design
- [Validation Guide](../operations/VALIDATION.md) - Quality assurance
- [API Reference](API_REFERENCE.md) - Code documentation
