# Processing Pipeline Testing

## Test Suite Location

The main test suite is located at:
- **Local**: `tests/test_processing_pipeline.py` (may be in .gitignore)
- **This directory**: Reference documentation and helpers

## Running Tests

```bash
# Run all processing pipeline tests
pytest tests/test_processing_pipeline.py -v

# Run specific test class
pytest tests/test_processing_pipeline.py::TestComponentRegistry -v

# Run with coverage
pytest tests/test_processing_pipeline.py --cov=processing --cov-report=html
```

## Test Coverage

- ✅ **ComponentRegistry**: Spec retrieval, registration, listing
- ✅ **DomainContext**: Domain factories, context retrieval
- ✅ **PromptBuilder**: Unified prompts, spec-driven building, failure adjustment
- ✅ **AuthorVoiceStore**: Profile loading, ESL trait extraction
- ✅ **DataEnricher**: Fact fetching, prompt formatting
- ✅ **AIDetectorEnsemble**: Pattern detection, batch processing
- ✅ **ReadabilityValidator**: Flesch scoring, improvement suggestions
- ✅ **Integration**: End-to-end workflows

## Test Files

Main test file location (may be gitignored):
```
tests/test_processing_pipeline.py  # 400+ lines, 35+ tests
```

## Writing New Tests

```python
from processing.generation.component_specs import ComponentRegistry

def test_custom_component():
    """Test custom component registration"""
    from processing.generation.component_specs import ComponentSpec
    
    spec = ComponentSpec(
        name='test_type',
        default_length=50,
        format_rules='Test format',
        focus_areas='Test focus',
        style_notes='Test style'
    )
    
    ComponentRegistry.register(spec)
    retrieved = ComponentRegistry.get_spec('test_type')
    assert retrieved.name == 'test_type'
```

## CI/CD Integration

Tests should be run as part of continuous integration:

```yaml
# .github/workflows/test.yml
- name: Run processing pipeline tests
  run: pytest tests/test_processing_pipeline.py -v
```

## Manual Testing

For manual testing of the pipeline:

```bash
# Test subtitle generation
python3 processing/test_pipeline.py

# Test specific material
from processing.orchestrator import Orchestrator
from shared.api.grok_client import GrokClient

orch = Orchestrator(GrokClient())
result = orch.generate("Aluminum", "subtitle", 2)
print(result)
```

## Expected Results

All tests should pass with:
- **ComponentRegistry**: 100% coverage
- **DomainContext**: 100% coverage
- **PromptBuilder**: 95%+ coverage
- **Integration**: 80%+ coverage

## Troubleshooting

### Import Errors

```python
# Ensure project root in path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Missing Dependencies

```bash
pip install pytest pytest-cov
pip install textstat  # For readability tests
```

### Gitignore Issues

Test files matching `test_*.py` are gitignored by default.
See `.gitignore` line 60.

To track test files, either:
1. Rename to `processing_tests.py`
2. Or use `git add -f tests/test_processing_pipeline.py`
3. Or modify .gitignore pattern

---

**Note**: Main test suite at `tests/test_processing_pipeline.py` contains complete test coverage.
Check your local workspace for the actual test file (may not be in git due to .gitignore).
