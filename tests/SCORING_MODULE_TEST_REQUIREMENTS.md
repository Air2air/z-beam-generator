# Test Requirements for Scoring Module

## Dependencies

The Scoring Module requires scientific computing libraries:

```bash
pip install -r requirements.txt
```

**Required packages**:
- `numpy>=1.24.0` - Array operations and statistical calculations
- `scipy>=1.11.0` - Statistical functions (spearmanr, pearsonr, bootstrap)
- `pytest>=7.4.0` - Test framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-cov>=4.1.0` - Coverage reporting

## Test Suites

### CompositeScorer Tests
**File**: `tests/test_composite_scorer.py`  
**Coverage**: 32 comprehensive tests

```bash
# Run all composite scorer tests
pytest tests/test_composite_scorer.py -v

# Run with coverage
pytest tests/test_composite_scorer.py --cov=postprocessing.evaluation.composite_scorer --cov-report=html
```

**Test Categories**:
1. Initialization (default weights, custom weights, validation)
2. All dimensions present (perfect/mixed/low scores)
3. Missing dimensions (subjective/readability/both)
4. Weight redistribution logic
5. Validation (range checks for all dimensions)
6. Convenience methods (database result objects)
7. Score interpretation (5 quality levels)
8. Edge cases (zeros, boundaries, rounding)

### GranularParameterCorrelator Tests
**Status**: Tests to be created

**Required test coverage**:
1. Correlation analysis with sufficient data (30+ samples)
2. Correlation analysis with insufficient data (<30 samples)
3. Statistical significance filtering (p-value < 0.05)
4. Correlation strength interpretation (very_strong to negligible)
5. Confidence interval calculation via bootstrap
6. Relationship type detection (linear, polynomial, logarithmic)
7. Optimal range identification
8. Sensitivity calculation
9. Parameter interaction detection
10. Adjustment recommendation generation

**Test file location**: `tests/test_granular_correlator.py`

## Database Requirements

Tests require a test database with sample data:

**Required tables**:
- `detection_results` (with composite_quality_score, subjective_evaluation_id)
- `generation_parameters` (with all 20+ parameters)
- `subjective_evaluations` (with generation_parameters_id)

**Sample data requirements**:
- Minimum 30 samples per parameter for reliable correlation
- Mix of high/medium/low quality scores
- Parameter variation across valid ranges
- Complete foreign key linking

## Running All Tests

```bash
# All scoring module tests
pytest tests/test_composite_scorer.py tests/test_granular_correlator.py -v

# With coverage report
pytest tests/test_composite_scorer.py tests/test_granular_correlator.py \
    --cov=postprocessing.evaluation --cov=learning \
    --cov-report=html --cov-report=term

# Quick smoke test
pytest tests/test_composite_scorer.py::TestCompositeScorer::test_default_initialization -v
```

## Continuous Integration

The scoring module tests should be included in CI/CD:

```yaml
# .github/workflows/tests.yml
- name: Install dependencies
  run: pip install -r requirements.txt

- name: Run scoring module tests
  run: |
    pytest tests/test_composite_scorer.py -v
    pytest tests/test_granular_correlator.py -v
```

## Known Issues

1. **Import errors**: Ensure numpy and scipy are installed before running tests
2. **Database not found**: GranularParameterCorrelator tests require `data/z-beam.db`
3. **Insufficient data**: Correlation tests may be skipped if <30 samples available
4. **Floating point precision**: Some tests use `round()` for comparison (±0.001 tolerance)

## Test Data Generation

To generate test data for correlation analysis:

```python
# scripts/generate_test_correlation_data.py
import sqlite3
import numpy as np

db_path = 'data/z-beam.db'
conn = sqlite3.connect(db_path)

# Generate 100 samples with realistic parameter distributions
for i in range(100):
    # Random parameters
    temperature = np.random.uniform(0.5, 1.5)
    frequency_penalty = np.random.uniform(0.0, 0.5)
    
    # Simulated quality score (with realistic correlation)
    composite_score = (
        50 + 
        (temperature - 1.0) * 20 +  # Temperature has positive correlation
        frequency_penalty * -30 +    # Frequency penalty negative
        np.random.normal(0, 5)       # Random noise
    )
    composite_score = np.clip(composite_score, 0, 100)
    
    # Insert into database...
```

## Documentation Tests

Documentation should include:

1. **README examples work**: All code examples in SCORING_MODULE_README.md should execute
2. **Import paths correct**: All import statements match actual module structure
3. **Parameter ranges match**: PARAMETER_RANGES in correlator matches actual config
4. **API examples current**: Usage examples reflect current API signatures

**Validation command**:
```bash
# Extract and test all code blocks from README
python scripts/test_readme_examples.py postprocessing/evaluation/SCORING_MODULE_README.md
```
