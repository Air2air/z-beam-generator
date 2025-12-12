# Z-Beam Generator Test Suite

Comprehensive testing framework for the Z-Beam laser cleaning content generation system.

## Overview

This test suite provides extensive coverage for the Z-Beam generator components with a focus on:
- **Fail-fast architecture validation**
- **Component integration testing**
- **Error handling and edge cases**
- **API client dependency management**
- **Content quality assurance**
- **API configuration centralization validation**
- **Performance regression prevention**

## Recent Test Additions (September 2025)

### API Configuration Centralization Tests
- **`test_api_centralization.py`**: Validates that all API configurations are properly centralized in `run.py`
- **`test_api_timeout_fixes.py`**: Ensures API timeout issues are resolved with optimized parameters

### Key Test Coverage
- ✅ Single source of truth for API configurations
- ✅ Elimination of duplicate API_PROVIDERS definitions
- ✅ Conservative parameter validation (max_tokens=4000, temperature=0.1)
- ✅ Timeout configuration verification
- ✅ Large prompt handling capability
- ✅ Real-world scenario validation (Steel material generation)

## Test Structure

### Test Categories

- **Unit Tests**: Individual component functionality
- **Integration Tests**: Component interactions and data flow
- **System Tests**: End-to-end content generation workflows
- **Quality Tests**: Code style, security, and performance
- **Configuration Tests**: API configuration centralization and optimization
- **Performance Regression Tests**: Parameter optimization validation

### Test Organization

```
tests/
├── test_api_centralization.py        # API configuration centralization tests
├── test_api_timeout_fixes.py         # API parameter optimization tests
├── test_content_comprehensive.py     # Enhanced content component testing
├── test_frontmatter_component.py     # Frontmatter component tests
├── test_content_component.py         # Content component interface tests
├── test_author_component.py          # Author component tests
├── test_tags_component.py            # Tags component tests
├── test_metatags_component.py        # Metatags component tests
├── test_badgesymbol_component.py     # Badgesymbol component tests
├── test_propertiestable_component.py # Propertiestable component tests
├── component_test_template.py        # Standardized test template
└── conftest.py                       # Test fixtures and configuration
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_content_comprehensive.py

# Run API centralization tests
pytest tests/test_api_centralization.py -v

# Run API timeout optimization tests  
pytest tests/test_api_timeout_fixes.py -v

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=components --cov-report=html
```

### Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

### Parallel Execution

```bash
# Run tests in parallel
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

## Test Configuration

### pytest.ini Settings

- **Test Discovery**: `tests/` and `components/` directories
- **Markers**: unit, integration, slow, mock, real_api
- **Coverage**: HTML and terminal reports
- **Parallel**: Disabled by default (enable with `-n auto`)

### Environment Variables

```bash
# Test configuration
TEST_USE_MOCK_API=true
TEST_MOCK_DELAY=0.01
TEST_API_PROVIDER=grok
TEST_RUN_SLOW=false
TEST_PARALLEL=false
```

## Component Test Patterns

### Hybrid Component Testing Rule

**For hybrid data components** (components that combine API-generated content with static source data):

- ✅ **API data fields**: Can use mock API clients for testing
- ✅ **Static source data**: Must be used and tested without mocking
- ✅ **Data validation**: Static data must be validated against real schemas
- ✅ **Integration testing**: Test both mocked API and real static data together

**Example Test Pattern:**
```python
def test_hybrid_component_with_mixed_mocking():
    """Test hybrid component using mock API but real static data."""
    # Mock API for generated content
    mock_client = get_mock_api_client("deepseek")

    # Use REAL static data (no mocking)
    static_data = load_static_data_from_yaml("Materials.yaml")

    result = generate_hybrid_component(
        material_name="Steel",
        static_data=static_data,  # Real data, no mocking
        api_client=mock_client    # Mock API for generated fields
    )

    # Validate both parts work correctly
    assert result.success
    assert validate_static_data_integrity(static_data, result)
    assert validate_api_generated_content(result.generated_content)
```

### API-Based Components

```python
def test_component_fail_fast_no_api_client():
    """Test fail-fast behavior when no API client is provided."""
    generator = get_generator()

    result = generator.generate(material_name="Test", ...)
    assert not result.success
    assert "API client" in result.error_message.lower()
```

### Frontmatter-Based Components

```python
def test_component_with_frontmatter_data():
    """Test component generation with valid frontmatter data."""
    generator = get_generator()

    frontmatter_data = {"title": "Test", "category": "metal"}
    result = generator.generate(..., frontmatter_data=frontmatter_data)
    assert result.success
    assert len(result.content) > 0
```

### Static Components

```python
def test_component_static_generation():
    """Test static component generation without API."""
    generator = get_generator()

    result = generator.generate(..., api_client=None)
    assert result.success  # Static components don't require API
    assert result.component_type == "component_name"
```

## Test Fixtures

### Component Generators

```python
def get_generator():
    """Lazy initialization of component generator."""
    global _test_generator
    if _test_generator is None:
        _test_generator = ComponentGenerator()
    return _test_generator
```

### Test Data

```python
# Standard material data
material_data = {
    "name": "Aluminum",
    "subject": "Aluminum",
    "category": "metal",
    "data": {"formula": "Al"},
    "properties": {"chemicalFormula": "Al"}
}

# Author information
author_info = {"id": 1, "name": "Test Author", "country": "Taiwan"}
```

## CI/CD Integration

### GitHub Actions

The test suite is integrated with GitHub Actions for automated testing:

- **Multi-Python Support**: Tests run on Python 3.8-3.12
- **Coverage Reports**: Generated and uploaded to Codecov
- **Quality Checks**: Linting, formatting, and security scanning
- **Parallel Execution**: Optimized test performance

### Pre-commit Hooks

Code quality is enforced with pre-commit hooks:

```bash
# Install pre-commit hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

## Test Coverage

### Current Coverage

- **34 component tests** across 11 components
- **6 comprehensive content tests** with persona validation
- **62 total tests** with 100% component coverage

### Components Tested

✅ **Fully Tested:**
- text, frontmatter, content, author, tags, metatags, badgesymbol, propertiestable
- micro, bullets, table, jsonld (Phase 4 - Complete)

### Phase 4 Completion Summary

**Completed Components:**
- **micro** ( tests): API-based technical image micro generation
- **bullets** (10 tests): API-based technical bullet point generation
- **table** (11 tests): Static technical table generation
- **jsonld** (4 tests): Frontmatter-based JSON-LD structured data generation

**Test Statistics:**
- **Total Phase 4 Tests**: 34 tests
- **Test Pass Rate**: 100% (34/34)
- **Overall Coverage**: 11/11 components (100%)
- **Test Execution Time**: < 0.13s for all Phase 4 tests

## Quality Assurance

### Code Quality Tools

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting and style checking
- **mypy**: Type checking
- **bandit**: Security scanning

### Test Quality Metrics

- **Coverage Target**: >80% code coverage
- **Test Categories**: Unit, integration, system tests
- **Performance**: Parallel execution support
- **Reliability**: Fail-fast architecture validation

## Contributing

### Adding New Tests

1. **Follow the template**: Use `component_test_template.py` for new components
2. **Test all scenarios**: Success, failure, edge cases
3. **Use proper markers**: `@pytest.mark.unit`, `@pytest.mark.integration`
4. **Include documentation**: Clear test names and docstrings

### Test Naming Convention

```python
def test_component_scenario_expected_result():
    """Test description with expected behavior."""
```

### Example Test Addition

```python
def test_micro_generation_success():
    """Test successful micro generation with valid inputs."""
    generator = get_micro_generator()

    result = generator.generate(
        material_name="Aluminum",
        material_data=get_test_material_data(),
        api_client=get_mock_api_client()
    )

    assert result.success
    assert "micro" in result.content.lower()
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `PYTHONPATH` includes project root
2. **API Client Errors**: Use mock clients for isolated testing
3. **Coverage Issues**: Run `pytest --cov-report=html` for detailed reports
4. **Parallel Issues**: Disable with `pytest -n0` if tests interfere

### Debug Mode

```bash
# Run with debug output
pytest -v -s --tb=long

# Run specific failing test
pytest tests/test_specific.py::test_function -v

# Run with coverage details
pytest --cov=components --cov-report=term-missing
```

## Performance

### Test Execution Times

- **Unit Tests**: < 0.1s each
- **Integration Tests**: 0.1-1s each
- **System Tests**: 1-10s each
- **Full Suite**: < 30s with parallel execution

### Optimization Tips

1. **Use fixtures**: For expensive setup operations
2. **Mock external calls**: API calls, file I/O
3. **Parallel execution**: `pytest -n auto` for faster runs
4. **Selective testing**: `pytest -k "component_name"` for focused testing

## Security Testing

### Security Scan Integration

```bash
# Run security scans
bandit -r components/ generators/ utils/
safety check

# Include in CI/CD
# Automated security scanning on every PR
```

### API Key Management

- **Environment Variables**: API keys loaded from `.env`
- **Mock Clients**: Used for testing without real API calls
- **Fail-Fast**: System fails immediately if API keys missing

## Future Enhancements

### Planned Improvements

1. **Performance Testing**: Load testing and benchmarking
2. **Mutation Testing**: Test effectiveness validation
3. **Property-Based Testing**: Hypothesis framework integration
4. **Visual Testing**: UI component testing
5. **Contract Testing**: API integration validation

### Coverage Goals

- **Target Coverage**: 90%+ code coverage
- **Component Coverage**: 100% of components tested
- **Test Types**: Unit, integration, system, performance
- **Quality Gates**: All PRs must pass CI/CD pipeline
