# Testing Documentation

Comprehensive testing documentation for the Z-Beam Generator system.

## Overview

- **[TESTING_OVERVIEW.md](TESTING_OVERVIEW.md)** - General testing strategy and guidelines
- **[ESSENTIAL_TEST_SUITE.md](ESSENTIAL_TEST_SUITE.md)** - Essential tests that must pass

## Detailed Testing Guides

- **[component_testing.md](component_testing.md)** - Component testing patterns and examples (48 KB)
- **[api_testing.md](api_testing.md)** - API testing methodology and diagnostics (41 KB)

## Quick Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_component.py

# Run with coverage
pytest --cov=components --cov-report=html

# Run only fast tests
pytest -m "not slow"
```

## Test Organization

Tests are organized by component:
- `tests/test_caption/` - Caption component tests
- `tests/test_frontmatter/` - Frontmatter component tests
- `tests/test_voice/` - Voice system tests
- `tests/test_validation/` - Validation tests
- `tests/test_data/` - Data architecture tests

## See Also

- [Component Documentation](../components/) - Component-specific testing details
- [API Error Handling](../api/ERROR_HANDLING.md) - API testing and diagnostics
