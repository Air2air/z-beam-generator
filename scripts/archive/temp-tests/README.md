# Temporary Test Files

Ad-hoc test scripts created during development and debugging.

## Purpose

These are temporary, exploratory test files used during feature development. They are not part of the formal test suite (tests/ directory) and may not follow standard test conventions.

## Files

- Various `test_*.py` files: Experimental tests for specific features
- `temp_ai_detection.py`: Testing AI detection algorithms

## Usage

```bash
# From repository root
python scripts/temp-tests/test_example.py
```

## Status

- **Not in version control**: These files are typically .gitignored
- **Not maintained**: May break as code evolves
- **For reference only**: Review formal tests in tests/ directory for maintained test coverage

## Migration Path

If any test proves valuable:
1. Refactor to pytest format
2. Move to appropriate tests/ subdirectory
3. Add to CI/CD pipeline
4. Remove from temp-tests/
