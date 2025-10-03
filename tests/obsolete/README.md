# Obsolete Tests Archive

**Created**: 2025-10-02 15:06:20
**Reason**: Test cleanup for fail-fast architecture compliance

## Why These Tests Are Obsolete

These tests have been moved here because they:

1. **Test code that no longer exists** (chemical_fallback, old optimizers)
2. **Provide redundant coverage** (multiple tests for same functionality)
3. **Test legacy/outdated systems** (pre-flattening structure, old validation)
4. **Are over-engineered** (841+ lines for file validation)

## Categories

### chemical_fallback/
Tests for chemical fallback system that was removed. The fail-fast architecture 
explicitly avoids fallback mechanisms.

**Files**: 3 tests
**Total Lines**: ~1,165 lines

### ai_detection_optimizer/
Tests for AI detection optimization services that don't exist in current codebase.
Optimizer orchestration was simplified.

**Files**: 8 tests
**Total Lines**: ~800+ lines

### legacy_redundant/
Legacy tests and redundant coverage. Example: 5 different caption tests when
one comprehensive test would suffice.

**Files**: 5 tests
**Total Lines**: ~1,500+ lines

### over_engineered/
Tests that are too large/complex for what they validate. Candidates for 
rewriting as simpler tests.

**Files**: 2 tests
**Total Lines**: ~1,451 lines

### potentially_obsolete/
Tests that might be obsolete but need review before permanent removal.

**Files**: 5 tests

## What Remains

After cleanup, the essential test suite focuses on:

- **Unit tests**: Component functionality (materials.py, pipeline_integration.py)
- **Integration tests**: Component interactions, API integration
- **E2E tests**: Full workflow validation
- **Validation tests**: Data integrity, format compliance

## Restoration

If any test is needed:

```bash
# Move back from obsolete
mv tests/obsolete/[category]/test_name.py tests/[original_location]/

# Or reference for historical context
cat tests/obsolete/[category]/test_name.py
```

## Next Steps

1. **Review**: Confirm these tests are truly obsolete
2. **Extract Value**: If any tests have useful patterns, extract them
3. **Delete**: After 30 days, consider permanent removal
4. **Simplify**: Rewrite over-engineered tests as minimal essential tests

---

**Total Tests Moved**: 23
**Space Saved**: ~5,000+ lines of obsolete test code
**Active Tests Remaining**: ~70-80 essential tests

See `docs/development/TESTING.md` for current testing strategy.
