# Generic Learning Architecture Proposal

**Date**: November 16, 2025  
**Status**: Draft  
**Goal**: Ensure learning database is truly generic and subjective evaluations contribute to learning

---

## Problem Statement

### Current Issues

1. **Sweet Spot Table Mismatch**
   - Table has `material` and `component_type` columns (specific)
   - But sweet_spot_analyzer does GENERIC learning (ignores those parameters)
   - This creates confusion: "Is learning specific or generic?"

2. **Subjective Evaluations Isolated**
   - Subjective evaluations score content quality (0-10 scale)
   - Winston detection scores AI-likeness (0-100% human scale)
   - These aren't integrated - subjective scores don't contribute to parameter learning

3. **Duplicate Scoring Systems**
   - Winston API: `human_score` (0.0-1.0, where higher = more human)
   - Subjective eval: `overall_score` (0-10, where higher = better quality)
   - Sweet spot analyzer: Only uses `human_score` for learning
   - No unified "quality" metric

---

## Proposed Solution

### 1. Make Sweet Spot Table Truly Generic

**Option A: Remove material/component columns (RECOMMENDED)**

```sql
CREATE TABLE IF NOT EXISTS sweet_spot_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_updated TEXT NOT NULL,
    scope TEXT DEFAULT 'global',  -- 'global', 'component_type', 'material'
    scope_value TEXT DEFAULT NULL,  -- NULL for global, or specific value
    
    -- Sweet spot parameter ranges
    temperature_min REAL,
    temperature_max REAL,
    temperature_median REAL,
    ...
    
    -- Statistics
    sample_count INTEGER NOT NULL,
    max_human_score REAL NOT NULL,
    avg_human_score REAL NOT NULL,
    confidence_level TEXT NOT NULL,
    
    -- Correlations and recommendations
    parameter_correlations TEXT,
    recommendations TEXT,
    
    UNIQUE(scope, scope_value)
);
```

**Benefits**:
- Default scope='global', scope_value=NULL for generic learning
- Can optionally filter by component_type or material if needed
- Clear semantic: "This learning is for X scope"
- Backward compatible: Can migrate existing data to 'global' scope

**Option B: Keep columns but make them optional**
- Set `material='*'` and `component_type='*'` for generic learning
- Less clear semantically

### 2. Unified Quality Scoring System

**Create a composite quality score** that combines:
1. Winston human score (AI detection)
2. Subjective evaluation score (content quality)
3. Optional: Readability score

```python
def calculate_composite_quality_score(
    human_score: float,  # 0.0-1.0 from Winston
    subjective_score: Optional[float] = None,  # 0-10 from subjective eval
    readability_score: Optional[float] = None  # 0-100
) -> float:
    """
    Calculate composite quality score (0-100 scale).
    
    Weights:
    - Human score (AI detection): 60% 
    - Subjective evaluation: 30%
    - Readability: 10%
    
    If subjective/readability missing, redistribute weight to human_score.
    """
    weights = {
        'human': 0.6,
        'subjective': 0.3,
        'readability': 0.1
    }
    
    # Normalize all to 0-100 scale
    scores = {
        'human': human_score * 100
    }
    
    if subjective_score is not None:
        scores['subjective'] = (subjective_score / 10) * 100
    else:
        # Redistribute subjective weight to human
        weights['human'] += weights['subjective']
        weights['subjective'] = 0
    
    if readability_score is not None:
        scores['readability'] = readability_score
    else:
        # Redistribute readability weight to human
        weights['human'] += weights['readability']
        weights['readability'] = 0
    
    composite = sum(
        scores.get(metric, 0) * weight 
        for metric, weight in weights.items()
    )
    
    return composite
```

### 3. Integrate Subjective Evaluations into Learning

**Add `composite_quality_score` to detection_results table**:

```sql
ALTER TABLE detection_results ADD COLUMN composite_quality_score REAL;
```

**Update sweet_spot_analyzer to use composite scores**:

```python
# In sweet_spot_analyzer.py
query = """
    SELECT 
        gp.*,
        dr.human_score,
        dr.composite_quality_score,
        COALESCE(dr.composite_quality_score, dr.human_score * 100) as quality_score,
        dr.material,
        dr.component_type
    FROM generation_parameters gp
    JOIN detection_results dr ON gp.detection_result_id = dr.id
    WHERE quality_score >= ?  -- Use composite or fallback to human_score
      AND dr.success = 1
    ORDER BY quality_score DESC
"""
```

**Link subjective evaluations to detection results**:

```python
def link_subjective_to_detection(
    db: WinstonFeedbackDatabase,
    material: str,
    component_type: str,
    subjective_eval_id: int,
    detection_result_id: int
):
    """
    Link a subjective evaluation to its detection result and
    update the composite quality score.
    """
    # Get subjective evaluation score
    subjective_score = db.get_subjective_evaluation(subjective_eval_id)
    
    # Get detection result
    detection = db.get_detection_result(detection_result_id)
    
    # Calculate composite score
    composite = calculate_composite_quality_score(
        human_score=detection['human_score'],
        subjective_score=subjective_score['overall_score'],
        readability_score=detection.get('readability_score')
    )
    
    # Update detection result
    db.update_detection_composite_score(detection_result_id, composite)
```

---

## Implementation Plan

### Phase 1: Database Schema Updates
1. Add `composite_quality_score` column to `detection_results`
2. Add migration script to set `scope='global'`, `scope_value=NULL` for existing sweet spots
3. Update sweet_spot_recommendations table (Option A above)

### Phase 2: Scoring Integration
1. Implement `calculate_composite_quality_score()` function
2. Add `link_subjective_to_detection()` method to WinstonFeedbackDatabase
3. Update generation pipeline to link subjective evals after logging

### Phase 3: Analyzer Updates
1. Update `sweet_spot_analyzer.py` to use composite scores when available
2. Add fallback logic: use `human_score` if `composite_quality_score` is NULL
3. Update threshold parameter: `success_threshold` now applies to composite score (0-100)

### Phase 4: Verification
1. Run test generation with subjective evaluation
2. Verify composite score is calculated and stored
3. Verify sweet spot analyzer uses composite scores
4. Verify learning is truly generic (not material/component specific)

---

## Benefits

1. **True Generic Learning**: Sweet spot table semantics match analyzer behavior
2. **Unified Quality Metric**: Single score combines multiple quality dimensions
3. **Better Optimization**: Parameters optimized for both human-likeness AND content quality
4. **No Data Loss**: Subjective evaluations now contribute to parameter learning
5. **Backward Compatible**: Falls back to human_score if subjective eval unavailable

---

## Testing Strategy

```python
def test_generic_learning():
    """Verify learning is truly generic across materials/components."""
    db = WinstonFeedbackDatabase('data/winston_feedback.db')
    
    # Generate for multiple materials
    generate_caption("Aluminum")
    generate_caption("Steel")
    generate_subtitle("Titanium")
    
    # Get sweet spot
    analyzer = SweetSpotAnalyzer(db)
    sweet_spots = analyzer.get_sweet_spot_table(
        material=None,  # Should be generic
        component_type=None  # Should be generic
    )
    
    # Verify it's stored as global scope
    spots_db = db.get_sweet_spot_recommendations(scope='global')
    assert spots_db is not None
    assert spots_db['sample_count'] >= 3  # All generations contributed
    
def test_composite_scoring():
    """Verify composite quality score calculation."""
    # Case 1: Only human score
    score1 = calculate_composite_quality_score(human_score=0.95)
    assert score1 == 95.0  # 100% weight on human score
    
    # Case 2: Human + subjective
    score2 = calculate_composite_quality_score(
        human_score=0.90,  # 90% human
        subjective_score=8.5  # 8.5/10 quality
    )
    # 60% * 90 + 30% * 85 + 10% * 0 = 54 + 25.5 = 79.5
    assert 79 <= score2 <= 80
    
    # Case 3: All three
    score3 = calculate_composite_quality_score(
        human_score=0.92,
        subjective_score=9.0,
        readability_score=75.0
    )
    # 60% * 92 + 30% * 90 + 10% * 75 = 55.2 + 27 + 7.5 = 89.7
    assert 89 <= score3 <= 90
```

---

## Migration Path

### For Existing Installations

1. **Backup database**: `cp data/winston_feedback.db data/winston_feedback.db.backup`

2. **Run migration script**:
```bash
python3 scripts/migrations/migrate_to_generic_learning.py
```

3. **Verify migration**:
```bash
python3 scripts/migrations/verify_generic_learning.py
```

4. **Update codebase**: Deploy new code with composite scoring

5. **Rebuild sweet spots**: 
```bash
python3 scripts/winston/sweet_spot.py --rebuild --scope global
```

---

## Open Questions

1. **Weight distribution**: Are 60/30/10 the right weights for composite score?
2. **Threshold values**: Should success_threshold change from 80 (human%) to 70 (composite)?
3. **Backward compatibility**: How to handle old data without subjective evals?
4. **Performance**: Does adding composite score calculation slow down generation?

---

## Next Steps

1. ✅ Get approval on architecture direction
2. Create migration scripts
3. Implement Phase 1 (schema updates)
4. Test with sample data
5. Roll out to production

