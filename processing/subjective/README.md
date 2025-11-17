# Subjective Quality Assessment Module

**Purpose**: Comprehensive subjective quality evaluation and automated parameter tuning for generated content.

## Overview

The Subjective module provides three interconnected components for assessing and improving content quality:

1. **Evaluator** (`evaluator.py`): Grok AI 6-dimension quality assessment
2. **Validator** (`validator.py`): Lightweight pattern-based validation
3. **Parameter Tuner** (`parameter_tuner.py`): Automated parameter adjustment based on evaluation feedback

## Architecture

```
processing/subjective/
├── __init__.py              # Module exports
├── evaluator.py             # Grok AI multi-dimensional evaluation
├── validator.py             # Pattern validation rules
├── parameter_tuner.py       # Dimension-based parameter tuning
└── README.md                # This file
```

## Components

### 1. SubjectiveEvaluator (Grok AI Evaluation)

**Purpose**: Deep quality assessment using Grok AI across 6 dimensions.

**Dimensions**:
- Clarity (0-10)
- Professionalism (0-10)
- Technical Accuracy (0-10)
- Human-likeness (0-10)
- Engagement (0-10)
- Jargon-free (0-10)

**Output**:
- Overall score
- Dimension scores
- Strengths list
- Weaknesses list
- Recommendations list

**Usage**:
```python
from processing.subjective import SubjectiveEvaluator

evaluator = SubjectiveEvaluator(grok_client)
result = evaluator.evaluate(
    text="Generated caption...",
    material_name="Aluminum",
    component_type="caption"
)

print(f"Overall: {result['overall_score']}/10")
print(f"Clarity: {result['clarity_score']}/10")
```

**Database Storage**: Results stored in `subjective_evaluations` table via `WinstonFeedbackDatabase.log_subjective_evaluation()`.

### 2. SubjectiveValidator (Pattern Validation)

**Purpose**: Fast, rule-based validation for common issues.

**Checks**:
- Forbidden phrases ("click here", "contact us")
- Excessive punctuation (!!!, ???)
- ALL CAPS sections
- Marketing language
- Poor formatting

**Usage**:
```python
from processing.subjective import SubjectiveValidator

validator = SubjectiveValidator()
result = validator.validate(text="Generated caption...")

if result.passed:
    print("✅ Validation passed")
else:
    print(f"❌ {len(result.violations)} violations found")
    for v in result.violations:
        print(f"  - {v}")
```

**Performance**: Lightweight, runs in milliseconds. Use before expensive Grok AI evaluation.

### 3. SubjectiveParameterTuner (Automated Learning)

**Purpose**: Automatically adjust generation parameters based on evaluation dimension scores.

**Mapping Rules**:
- **Low Clarity** → Reduce temperature (simpler, clearer output)
- **Low Professionalism** → Increase presence_penalty (more formal)
- **Low Technical Accuracy** → Increase technical_depth slider
- **Low Human-likeness** → Reduce presence_penalty (more natural)
- **Low Engagement** → Increase temperature + conversational_tone
- **Low Jargon-free** → Reduce technical_depth (simpler language)

**Thresholds**:
- Score < 5.0 = Poor (large adjustment: 0.10 delta)
- Score < 7.0 = Below target (medium adjustment: 0.05 delta)
- Score >= 8.5 = Excellent (no adjustment)

**Usage**:
```python
from processing.subjective import SubjectiveParameterTuner

tuner = SubjectiveParameterTuner(feedback_db)

# Get evaluation from database
subjective_eval = feedback_db.get_latest_subjective_evaluation(
    material_name="Aluminum",
    component_type="caption"
)

# Current parameters
current_params = {
    'api': {'temperature': 1.0},
    'api_penalties': {'presence_penalty': 1.0},
    'voice': {'technical_depth': 50}
}

# Analyze and adjust
new_params, adjustments = tuner.analyze_and_adjust(
    subjective_eval, current_params
)

# Log adjustments
for adj in adjustments:
    print(f"🔧 {adj.parameter}: {adj.old_value} → {adj.new_value}")
    print(f"   Reason: {adj.reason}")
```

**Parameter Bounds**:
- Temperature: 0.5 - 1.5
- Penalties: 0.0 - 2.0
- Voice sliders: 0 - 100

## Integration Flow

```
Generate Content
     ↓
SubjectiveValidator (pattern check)
     ↓
SubjectiveEvaluator (Grok AI assessment)
     ↓
Store in Database
     ↓
SubjectiveParameterTuner (adjust parameters)
     ↓
Use adjusted parameters for next generation
```

## Testing

```bash
# Test individual components
pytest tests/test_subjective_evaluator.py
pytest tests/test_subjective_validator.py
pytest tests/test_subjective_parameter_tuner.py

# Test full integration
python3 run.py --batch-test
```

## Database Schema

**subjective_evaluations table**:
```sql
CREATE TABLE subjective_evaluations (
    id INTEGER PRIMARY KEY,
    material_name TEXT,
    component_type TEXT,
    overall_score REAL,
    clarity_score REAL,
    professionalism_score REAL,
    technical_accuracy_score REAL,
    human_likeness_score REAL,
    engagement_score REAL,
    jargon_free_score REAL,
    strengths TEXT,  -- JSON array
    weaknesses TEXT,  -- JSON array
    recommendations TEXT,  -- JSON array
    quality_gate_passed INTEGER,
    created_at TIMESTAMP
)
```

## Configuration

No configuration files needed - all thresholds and rules are defined in code:

- **Evaluator**: Uses Grok API client passed at initialization
- **Validator**: Rules hardcoded in `validator.py` (forbidden phrases, etc.)
- **Parameter Tuner**: Thresholds and adjustment magnitudes defined as class constants

## Performance Notes

- **Validator**: ~1-2ms per validation (negligible overhead)
- **Evaluator**: ~2-5s per evaluation (Grok API call)
- **Parameter Tuner**: <1ms per adjustment calculation

**Recommendation**: Run Validator first (cheap), then Evaluator only if validation passes.

## Future Enhancements

1. **Machine Learning Integration**: Train ML model on evaluation history to predict optimal parameters
2. **Author-Specific Tuning**: Adjust tuning rules based on author persona
3. **A/B Testing**: Compare parameter sets to find optimal configurations
4. **Feedback Loop**: Track parameter adjustment → quality improvement correlation
5. **Custom Rules**: Allow users to define custom validation patterns

## Related Documentation

- `docs/06-ai-systems/SUBJECTIVE_EVALUATION_LEARNING.md` - Learning system architecture
- `docs/04-operations/BATCH_TEST_REPORT_REQUIREMENTS.md` - Batch test reporting
- `processing/detection/winston_feedback_db.py` - Database storage

---

**Created**: November 16, 2025  
**Last Updated**: November 16, 2025
