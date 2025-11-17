# Subjective Evaluation Integration Requirements

**Last Updated**: November 16, 2025  
**Module**: `processing/subjective/`

---

## 🎯 Core Requirement

**Subjective evaluation MUST run generically for ALL component types during generation.**

This is not optional. Every content generation command (caption, subtitle, FAQ, description, etc.) must invoke subjective evaluation as the final quality check.

---

## 📋 Integration Checklist

When adding a new component type, you MUST:

### 1. ✅ Add Subjective Evaluation to Generation Handler

```python
def handle_YOUR_component_generation(material_name: str, skip_integrity_check: bool = False):
    """Generate YOUR_component for a material."""
    
    # ... generation logic ...
    
    # ✅ REQUIRED: Run Subjective evaluation as final quality check
    print("🤖 Running subjective content evaluation...")
    from shared.commands.subjective_evaluation_helper import evaluate_after_generation
    from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
    from processing.config.config_loader import get_config
    
    try:
        # Initialize feedback database
        config = get_config()
        db_path = config.config.get('winston_feedback_db_path')
        feedback_db = None
        if db_path:
            feedback_db = WinstonFeedbackDatabase(db_path)
        
        # Initialize Grok API client
        from shared.api.client_factory import create_api_client
        grok_client = create_api_client('grok')
        
        # Evaluate generated content
        evaluation = evaluate_after_generation(
            content=generated_text,
            topic=material_name,
            component_type='YOUR_component',  # ⚠️ Use actual component type
            domain='materials',
            api_client=grok_client,
            feedback_db=feedback_db,
            verbose=False
        )
        
        if evaluation:
            print(f"   Overall Quality Score: {evaluation.overall_score:.1f}/10")
            print(f"   Quality Gate: {'✅ PASS' if evaluation.passes_quality_gate else '❌ FAIL'}")
            
            # Display narrative assessment if available
            if evaluation.narrative_assessment:
                print()
                print("   📝 Assessment:")
                print(f"      {evaluation.narrative_assessment}")
            
            print()
            print("   📊 Quality Dimensions:")
            for score in evaluation.dimension_scores:
                status = "✅" if score.score >= 7.0 else "⚠️"
                print(f"      {status} {score.dimension.value.replace('_', ' ').title()}: {score.score:.1f}/10")
            print()
    except Exception as e:
        print(f"   ⚠️  Subjective evaluation unavailable: {e}")
        print()
```

### 2. ✅ Ensure component_type is Passed Correctly

The `component_type` parameter MUST match the actual component being generated:
- `'caption'` for captions
- `'subtitle'` for subtitles
- `'faq'` for FAQs
- `'description'` for descriptions
- etc.

**Do NOT** hardcode or default to a generic value.

### 3. ✅ Store Results in Database

The `evaluate_after_generation()` function automatically stores results in the `subjective_evaluations` table when `feedback_db` is provided. This enables:
- Historical tracking of quality trends
- Parameter learning and optimization
- Narrative assessment retrieval for reports

### 4. ✅ Add Tests

Create integration tests to verify subjective evaluation runs:

```python
def test_YOUR_component_generation_uses_subjective_evaluation():
    """Verify YOUR_component generation calls subjective evaluation."""
    from pathlib import Path
    generation_file = Path("shared/commands/generation.py")
    content = generation_file.read_text()
    
    assert "handle_YOUR_component_generation" in content
    assert "evaluate_after_generation" in content or "SubjectiveEvaluationHelper" in content
```

Add this to `tests/test_subjective_evaluation_integration.py`.

---

## 📊 Database Schema

Subjective evaluations are stored with these fields:

```sql
CREATE TABLE subjective_evaluations (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    topic TEXT,                    -- Material name or subject
    component_type TEXT,           -- 'caption', 'subtitle', 'faq', etc.
    overall_score REAL,            -- 0-10 overall quality
    clarity_score REAL,            -- 6 dimension scores
    professionalism_score REAL,
    technical_accuracy_score REAL,
    human_likeness_score REAL,
    engagement_score REAL,
    jargon_free_score REAL,
    narrative_assessment TEXT,     -- Paragraph-form evaluation
    strengths TEXT,                -- JSON array
    weaknesses TEXT,               -- JSON array
    recommendations TEXT,          -- JSON array
    passes_quality_gate INTEGER,   -- Boolean
    evaluation_time_ms INTEGER
);
```

---

## 🔍 Verification

### Automated Tests

Run the integration test suite:

```bash
pytest tests/test_subjective_evaluation_integration.py -v
```

Tests verify:
- ✅ All component handlers call subjective evaluation
- ✅ `SubjectiveEvaluationResult` includes `narrative_assessment`
- ✅ Database has `narrative_assessment` column
- ✅ Grok prompt requests narrative assessment
- ✅ Batch tests display narrative assessment

### Manual Verification

Generate content and check for evaluation output:

```bash
python3 run.py --caption "MaterialName"
# Should see: "🤖 Running subjective content evaluation..."
# Should see: Quality scores and narrative assessment

python3 run.py --subtitle "MaterialName"
# Should also see subjective evaluation

python3 run.py --faq "MaterialName"
# Should also see subjective evaluation
```

### Database Verification

Check that evaluations are being logged:

```bash
sqlite3 processing/detection/winston_feedback.db \
  "SELECT topic, component_type, overall_score, narrative_assessment 
   FROM subjective_evaluations 
   ORDER BY timestamp DESC LIMIT 5;"
```

---

## ⚠️ Common Mistakes

### ❌ DON'T: Skip subjective evaluation for "simple" components
Every component needs quality assessment, regardless of complexity.

### ❌ DON'T: Hardcode component_type
```python
# BAD
evaluate_after_generation(
    content=text,
    component_type='caption',  # ❌ Wrong if generating subtitle!
    ...
)
```

### ❌ DON'T: Silently fail without logging
```python
# BAD
try:
    evaluation = evaluate_after_generation(...)
except:
    pass  # ❌ User has no visibility into failure
```

### ✅ DO: Pass correct component_type
```python
# GOOD
evaluate_after_generation(
    content=subtitle_text,
    component_type='subtitle',  # ✅ Matches what's being generated
    ...
)
```

### ✅ DO: Show informative errors
```python
# GOOD
try:
    evaluation = evaluate_after_generation(...)
except Exception as e:
    print(f"   ⚠️  Subjective evaluation unavailable: {e}")
    # Generation continues but user is informed
```

---

## 📚 Related Documentation

- **Subjective Module README**: `processing/subjective/README.md`
- **Evaluation Helper**: `shared/commands/subjective_evaluation_helper.py`
- **Database Schema**: `processing/detection/winston_feedback_db.py`
- **Integration Tests**: `tests/test_subjective_evaluation_integration.py`
- **Narrative Assessment**: See Grok prompt in `processing/subjective/evaluator.py`

---

## 🔄 Future Components

When adding new component types (e.g., `description`, `use_case`, `technical_specs`):

1. ✅ Follow the integration checklist above
2. ✅ Add test to `test_subjective_evaluation_integration.py`
3. ✅ Update this documentation with the new component type
4. ✅ Verify database logging works
5. ✅ Ensure batch tests include the new component

**No exceptions.** All content must be evaluated.
