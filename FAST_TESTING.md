# Fast Test Configuration

## Quick Test Commands

### Fast Unit Tests Only (recommended for development)
```bash
pytest tests/unit/ --no-cov --disable-warnings -x --tb=line
```

### Fast Integration Tests
```bash
pytest tests/integration/ --no-cov --disable-warnings --tb=line -m "not slow"
```

### Fast Smoke Tests
```bash
pytest -m smoke --no-cov --disable-warnings --tb=line
```

### Full Test Suite (for CI)
```bash
pytest --ignore=backups/ --ignore=scripts/test_*
```

## Speed Optimizations

1. **Disable Coverage for Development**
   - Coverage adds 30-50% overhead
   - Only use for final validation

2. **Skip Slow Tests During Development**
   - Use `-m "not slow"` to skip e2e tests
   - Use `-m "not e2e"` to skip end-to-end tests

3. **Fail Fast During Development**
   - Use `-x` to stop on first failure
   - Use `--maxfail=3` to stop after few failures

4. **Reduce Test Scope**
   - Test specific modules: `pytest tests/unit/test_specific.py`
   - Test specific functions: `pytest -k "test_function_name"`

5. **Exclude Problem Directories**
   - Add `--ignore=backups/` to skip archived tests
   - Add `--ignore=scripts/` to skip integration scripts

## Current Performance Issues

- 7 collection errors from missing modules
- 697 test items being collected (too many)
- Coverage reporting enabled by default
- Parallel execution overhead for small test suite
- Backup directories being scanned

## Recommended pytest.ini Changes

For faster development, consider a minimal pytest.ini:

```ini
[tool:pytest]
testpaths = tests/unit tests/integration
addopts = --strict-markers --tb=short --disable-warnings -x
markers =
    unit: Unit tests
    integration: Integration tests  
    slow: Slow tests
    smoke: Smoke tests
norecursedirs = .git __pycache__ backups archive node_modules
```