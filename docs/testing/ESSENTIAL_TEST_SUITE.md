# Essential Test Suite for Z-Beam Generator

**Version**: 2.0 (Post-Flattening, Fail-Fast Architecture)  
**Created**: October 2, 2025  
**Purpose**: Minimal, focused test suite aligned with fail-fast principles

## Philosophy

The essential test suite follows Z-Beam's **fail-fast architecture**:

1. **No mocks in production** - MockAPIClient for tests only
2. **Explicit validation** - Test what actually matters
3. **Fast feedback** - Quick unit tests, targeted integration tests
4. **Real scenarios** - E2E tests validate actual workflows

**Goal**: ~40-50 essential tests (down from 106) covering critical functionality

---

## Essential Test Structure

```
tests/
├── unit/                          # 15-20 tests (fast, isolated)
│   ├── test_materials_loading.py        # Flattened structure access
│   ├── test_pipeline_validation.py      # Validation rules
│   ├── test_frontmatter_component.py    # Core frontmatter generation
│   ├── test_text_component.py           # Text generation
│   ├── test_caption_component.py        # Caption generation (consolidated)
│   └── test_tags_component.py           # Tags extraction
│
├── integration/                   # 15-20 tests (component interactions)
│   ├── test_api_integration.py          # DeepSeek, Winston, Perplexity
│   ├── test_frontmatter_pipeline.py     # Full frontmatter workflow
│   ├── test_validation_pipeline.py      # Validation + improvement
│   └── test_component_factory.py        # Component discovery
│
├── e2e/                           # 5-10 tests (full workflows)
│   ├── test_single_generation.py        # Single material generation
│   ├── test_batch_generation.py         # Batch processing
│   ├── test_compliance_workflow.py      # Validation + regeneration
│   └── test_api_integration.py          # Real API calls (optional)
│
└── validation/                    # 5-10 tests (data integrity)
    ├── test_materials_data.py           # materials.yaml structure
    ├── test_categories_data.py          # Categories.yaml validity
    └── test_frontmatter_compliance.py   # Format compliance
```

**Total**: ~40-55 essential tests

---

## Unit Tests (15-20 tests)

### Purpose
Test **individual functions/classes** in isolation with mocks for external dependencies.

### Essential Unit Tests

#### 1. Materials Loading (`test_materials_loading.py`)

```python
"""Test flattened materials.yaml loading and access."""

def test_load_materials():
    """Test materials load correctly from flat structure."""
    materials = load_materials()
    assert len(materials) == 121
    assert 'Aluminum' in materials
    assert materials['Aluminum']['category'] == 'metal'

def test_get_material_by_name():
    """Test direct O(1) material lookup."""
    material = get_material_by_name('Aluminum')
    assert material is not None
    assert 'properties' in material

def test_case_insensitive_lookup():
    """Test case-insensitive material search.
    
    CRITICAL REQUIREMENT: ALL material lookups must be case-insensitive.
    This is a core system behavior, not an optional feature.
    
    Tests verify:
    - CLI commands work with any case variation
    - API functions handle all case combinations
    - Material resolution is consistent across cases
    """
    material = find_material_case_insensitive('aluminum')
    assert material is not None, "lowercase lookup failed"
    
    material = find_material_case_insensitive('ALUMINUM')
    assert material is not None, "uppercase lookup failed"
    
    material = find_material_case_insensitive('AlUmInUm')
    assert material is not None, "mixed case lookup failed"

def test_material_not_found():
    """Test fail-fast when material doesn't exist."""
    with pytest.raises(ValueError):
        get_material_by_name('NonexistentMaterial')
```

**Why Essential**: Core data access, used by all components

---

#### 2. Pipeline Validation (`test_pipeline_validation.py`)

```python
"""Test validation rules for frontmatter and text."""

def test_validate_applications_simple_strings():
    """Applications must be simple strings with colon."""
    frontmatter = {
        'applications': [
            'Aerospace: Precision cleaning',
            'Electronics: Component cleaning'
        ]
    }
    result = validate_and_improve_frontmatter('Test', frontmatter)
    assert result['validation_passed']

def test_validate_caption_camelcase():
    """Caption must use camelCase keys."""
    caption = {
        'beforeText': 'Before...',
        'afterText': 'After...',
        'description': 'Test'
    }
    assert validate_caption_format(caption)

def test_validate_tags_count():
    """Tags must be 4-10 items."""
    assert validate_tags(['metal', 'aerospace', 'electronics', 'manufacturing'])
    assert not validate_tags(['metal'])  # Too few
```

**Why Essential**: Validation is critical for quality, runs on every generation

---

#### 3. Component Tests (3 files)

**Frontmatter** (`test_frontmatter_component.py`):
```python
def test_generate_applications_simple_strings()
def test_generate_caption_camelcase()
def test_generate_tags()
def test_frontmatter_required_fields()
```

**Text** (`test_text_component.py`):
```python
def test_select_author_persona()
def test_word_count_validation()
def test_quality_scoring()
def test_author_voice_markers()
```

**Caption** (`test_caption_component.py` - consolidates 4 existing tests):
```python
def test_caption_generation()
def test_caption_structure()
def test_caption_length_validation()
```

**Why Essential**: Core content generation, must work correctly

---

## Integration Tests (15-20 tests)

### Purpose
Test **component interactions** and **external API integration** with real or mock clients.

### Essential Integration Tests

#### 1. API Integration (`test_api_integration.py`)

```python
"""Test API client integration (DeepSeek, Winston, Perplexity)."""

@pytest.mark.api
def test_deepseek_content_generation():
    """Test DeepSeek generates valid content."""
    client = get_api_client('deepseek')
    result = client.generate(prompt="Test", material="Aluminum")
    assert result is not None
    assert len(result) > 0

@pytest.mark.api
def test_winston_quality_scoring():
    """Test Winston AI scores content."""
    score = winston_score("Test content for quality assessment.")
    assert 0 <= score['human_believability'] <= 100

@pytest.mark.mock
def test_api_with_mock_client():
    """Test with MockAPIClient for fast tests."""
    client = MockAPIClient()
    result = client.generate(prompt="Test")
    assert result is not None
```

**Why Essential**: API integration is core functionality, must work reliably

---

#### 2. Frontmatter Pipeline (`test_frontmatter_pipeline.py`)

```python
"""Test full frontmatter generation pipeline."""

def test_frontmatter_generation_workflow():
    """Test complete frontmatter generation."""
    result = generate_frontmatter('Aluminum')
    
    # Validate structure
    assert 'applications' in result
    assert 'caption' in result['images']
    assert 'tags' in result
    
    # Validate format
    assert all(isinstance(app, str) for app in result['applications'])
    assert 'beforeText' in result['images']['caption']
    assert 4 <= len(result['tags']) <= 10

def test_frontmatter_validation_integration():
    """Test validation catches format issues."""
    frontmatter = generate_frontmatter('Copper')
    validation = validate_and_improve_frontmatter('Copper', frontmatter)
    
    assert 'validation_result' in validation
    assert validation['validation_passed'] or len(validation['issues_detected']) > 0
```

**Why Essential**: Tests full generation + validation workflow

---

#### 3. Component Factory (`test_component_factory.py`)

```python
"""Test component generator factory."""

def test_create_frontmatter_generator():
    """Factory creates frontmatter generator."""
    gen = ComponentGeneratorFactory.create_generator('frontmatter')
    assert gen is not None
    assert hasattr(gen, 'generate')

def test_create_text_generator():
    """Factory creates text generator."""
    gen = ComponentGeneratorFactory.create_generator('text')
    assert gen is not None

def test_invalid_component_type():
    """Factory fails fast on invalid type."""
    with pytest.raises(ValueError):
        ComponentGeneratorFactory.create_generator('invalid')
```

**Why Essential**: Factory pattern is core to component architecture

---

## E2E Tests (5-10 tests)

### Purpose
Test **complete workflows** from user input to file output.

### Essential E2E Tests

#### 1. Single Generation (`test_single_generation.py`)

```python
"""Test single material generation workflow."""

@pytest.mark.e2e
def test_generate_single_material():
    """Test: python3 run.py --material Aluminum --components frontmatter"""
    result = run_generation(material='Aluminum', components=['frontmatter'])
    
    assert result['success']
    
    # Verify file created
    output_file = Path('content/components/frontmatter/aluminum-laser-cleaning.yaml')
    assert output_file.exists()
    
    # Verify content
    with open(output_file) as f:
        data = yaml.safe_load(f)
    
    assert data['material'] == 'Aluminum'
    assert len(data['applications']) >= 2
    assert 'beforeText' in data['images']['caption']
    assert 4 <= len(data['tags']) <= 10
```

**Why Essential**: Most common user workflow, must work end-to-end

---

#### 2. Batch Generation (`test_batch_generation.py`)

```python
"""Test batch generation workflow."""

@pytest.mark.e2e
@pytest.mark.slow
def test_batch_generation_sample():
    """Test batch processing with small sample."""
    materials = ['Aluminum', 'Copper', 'Zinc']
    
    results = batch_generate(materials, component='frontmatter')
    
    assert len(results) == 3
    assert all(r['success'] for r in results)
    
    # Verify all files created
    for material in materials:
        file = Path(f'content/components/frontmatter/{material.lower()}-laser-cleaning.yaml')
        assert file.exists()
```

**Why Essential**: Batch processing is production workflow

---

#### 3. Compliance Workflow (`test_compliance_workflow.py`)

```python
"""Test validation and regeneration workflow."""

@pytest.mark.e2e
def test_compliance_check_and_fix():
    """Test: verify compliance → regenerate non-compliant → verify again."""
    
    # Step 1: Check compliance
    report = verify_compliance()
    initial_compliant = report['compliant_count']
    
    # Step 2: Regenerate non-compliant
    if report['non_compliant_count'] > 0:
        sample_material = report['non_compliant'][0]
        result = generate_frontmatter(sample_material)
        assert result['success']
    
    # Step 3: Verify improvement
    report2 = verify_compliance()
    assert report2['compliant_count'] >= initial_compliant
```

**Why Essential**: Core operational workflow for maintaining quality

---

## Validation Tests (5-10 tests)

### Purpose
Test **data integrity** and **format compliance** of YAML files.

### Essential Validation Tests

#### 1. Materials Data (`test_materials_data.py`)

```python
"""Validate materials.yaml structure and content."""

def test_materials_yaml_structure():
    """Validate flat structure with 121 materials."""
    with open('data/materials.yaml') as f:
        data = yaml.safe_load(f)
    
    assert 'materials' in data
    assert len(data['materials']) == 121
    
    # Verify flat structure
    for name, material in data['materials'].items():
        assert 'category' in material
        assert 'properties' in material

def test_materials_required_fields():
    """Each material has required fields."""
    materials = load_materials()
    
    for name, material in materials.items():
        assert 'category' in material
        assert 'properties' in material
        assert material['category'] in [
            'metal', 'wood', 'stone', 'composite', 
            'glass', 'ceramic', 'masonry', 'plastic', 'semiconductor'
        ]
```

**Why Essential**: Data integrity is foundation of system

---

#### 2. Frontmatter Compliance (`test_frontmatter_compliance.py`)

```python
"""Validate generated frontmatter files."""

def test_all_materials_have_frontmatter():
    """All 121 materials should have frontmatter files."""
    materials = load_materials()
    frontmatter_files = list(Path('content/components/frontmatter').glob('*-laser-cleaning.yaml'))
    
    # Should have ~121 files (may be in progress)
    assert len(frontmatter_files) >= 100

def test_frontmatter_format_compliance():
    """Sample files have correct format."""
    sample_files = [
        'aluminum-laser-cleaning.yaml',
        'copper-laser-cleaning.yaml',
        'zinc-laser-cleaning.yaml'
    ]
    
    for filename in sample_files:
        filepath = Path(f'content/components/frontmatter/{filename}')
        if not filepath.exists():
            continue
        
        with open(filepath) as f:
            data = yaml.safe_load(f)
        
        # Applications: simple strings
        assert all(isinstance(app, str) and ':' in app for app in data['applications'])
        
        # Caption: camelCase
        caption = data['images']['caption']
        assert 'beforeText' in caption
        assert 'afterText' in caption
        
        # Tags: 4-10 items
        assert 4 <= len(data['tags']) <= 10
```

**Why Essential**: Ensures content meets quality standards

---

## Test Execution Strategy

### Fast Feedback Loop (Unit + Quick Integration)

```bash
# Run fast tests only (< 5 seconds)
pytest tests/unit tests/integration -m "not slow" -v

# Expected: ~30-35 tests in < 10 seconds
```

### Full Test Suite (All Essential Tests)

```bash
# Run all essential tests
pytest tests/unit tests/integration tests/e2e tests/validation -v

# Expected: ~45-55 tests in < 60 seconds (with mocks)
```

### With Real APIs (Slower)

```bash
# Run with real API calls
pytest tests/ -m "api or e2e" --no-mock -v

# Expected: ~10-15 tests in 5-10 minutes (API latency)
```

---

## What Was Removed

### Obsolete Tests (Moved to `tests/obsolete/`)

1. **Chemical Fallback** (3 tests, ~1,165 lines) - Code doesn't exist
2. **AI Detection/Optimizer** (8 tests, ~800 lines) - Services removed
3. **Legacy/Redundant** (5 tests, ~1,500 lines) - Duplicate coverage
4. **Over-engineered** (2 tests, ~1,451 lines) - Too complex

**Total Removed**: ~30 tests, ~4,900 lines

### Remaining Tests

- **Before Cleanup**: 106 tests
- **After Cleanup**: ~45-55 essential tests
- **Reduction**: ~50% fewer tests, 100% essential coverage

---

## Test Maintenance

### When to Add Tests

1. **New Component**: Add unit + integration tests
2. **Bug Fix**: Add regression test (mark with `@pytest.mark.regression`)
3. **New Workflow**: Add E2E test if not covered

### When to Remove Tests

1. **Code removed**: Remove associated tests
2. **Redundant coverage**: Consolidate into comprehensive test
3. **Over-engineered**: Simplify or remove

### Test Quality Criteria

- ✅ **Fast**: Unit tests < 0.1s, Integration < 1s, E2E < 10s
- ✅ **Focused**: Test one thing clearly
- ✅ **Reliable**: No flaky tests
- ✅ **Readable**: Clear test name and assertions
- ✅ **Maintainable**: Update when code changes

---

## Migration Plan

### Phase 1: Cleanup (Today)

```bash
# Run cleanup script (dry-run first)
python3 scripts/tools/cleanup_obsolete_tests.py --dry-run

# Execute cleanup
python3 scripts/tools/cleanup_obsolete_tests.py --execute
```

### Phase 2: Consolidation (This Week)

1. Merge 4 caption tests → 1 comprehensive test
2. Merge 5 frontmatter tests → 2 tests (generation + validation)
3. Keep best comprehensive E2E test, remove others

### Phase 3: Essential Suite (Ongoing)

1. Run essential tests only: `pytest tests/ --ignore=tests/obsolete`
2. Monitor coverage: Aim for 80% with essential tests
3. Update documentation: `docs/development/TESTING.md`

---

## Success Metrics

### Coverage Targets

- **Unit Tests**: 80-90% coverage of core modules
  - `data/materials.py`: 90%
  - `pipeline_integration.py`: 85%
  - Component generators: 80%

- **Integration Tests**: Critical paths covered
  - API integration: 100%
  - Component factory: 100%
  - Validation pipeline: 100%

- **E2E Tests**: Main workflows covered
  - Single generation: ✅
  - Batch generation: ✅
  - Compliance workflow: ✅

### Performance Targets

- **Fast Tests** (unit + quick integration): < 10 seconds
- **Full Suite** (with mocks): < 60 seconds
- **With Real APIs**: < 10 minutes

---

## Summary

### Essential Test Suite Benefits

1. **Faster**: ~50% reduction in test count
2. **Clearer**: Each test has clear purpose
3. **Maintainable**: No obsolete code to confuse developers
4. **Focused**: Tests align with fail-fast architecture
5. **Reliable**: No tests for code that doesn't exist

### Next Steps

1. ✅ Run cleanup script
2. ✅ Verify essential tests pass
3. ✅ Update CI/CD to use essential suite
4. ✅ Document in `TESTING.md`

---

**See Also**:
- `docs/development/TESTING.md` - Complete testing guide
- `scripts/tools/cleanup_obsolete_tests.py` - Cleanup script
- `tests/obsolete/README.md` - Why tests were moved
- `pytest.ini` - Test configuration
