# Scoring Normalization Issues - November 20, 2025

## 🚨 **CRITICAL ISSUE FOUND**

The system has **inconsistent score normalization** between components, causing the sweet spot analyzer to fail.

---

## 📊 **Current State Analysis**

### Database Actual Values
```sql
SELECT MIN(human_score), MAX(human_score), AVG(human_score) FROM detection_results;
-- Result: 0.0 | 7.67 | 0.42
```

**Finding**: Database contains MIXED formats:
- Some records: `human_score=7.67` (0-100 scale, raw Winston format)
- Many records: `human_score=1.0` (0-1.0 scale, normalized)
- Many records: `human_score=0.0` (failures/skipped)

---

## 🔍 **Root Cause Analysis**

### 1. Winston API Output (`shared/api/client.py`)
```python
def detect_ai_content(self, text: str) -> Dict[str, Any]:
    # Winston returns 'score' (0-100 human percentage)
    human_score = data.get('score', 0)  # 0-100
    ai_score = (100 - human_score) / 100.0  # 0-1.0 normalized
    
    return {
        'human_score': human_score,  # ❌ 0-100 scale
        'ai_score': ai_score,         # ✅ 0-1.0 normalized
    }
```

### 2. Database Storage (`postprocessing/detection/winston_feedback_db.py`)
```python
def log_detection(...):
    cursor.execute("""
        INSERT INTO detection_results 
        (human_score, ai_score, composite_quality_score, ...)
        VALUES (?, ?, ?, ...)
    """, (
        winston_result.get('human_score', 0),  # ❌ Stores 0-100 directly
        winston_result.get('ai_score', 1.0),   # ✅ Stores 0-1.0
        composite_quality_score                # ❓ Unknown scale
    ))
```

### 3. Sweet Spot Analyzer (`learning/sweet_spot_analyzer.py`)
```python
query = """
    SELECT ... 
    FROM generation_parameters gp
    JOIN detection_results dr ON gp.detection_result_id = dr.id
    WHERE COALESCE(dr.composite_quality_score, dr.human_score) >= ?
      AND dr.success = 1
"""
params = [self.success_threshold]  # ❌ Was 80.0 (0-100 scale)
```

### 4. Composite Scorer (`postprocessing/evaluation/composite_scorer.py`)
```python
def calculate_composite_score(
    self,
    winston_human_score: float,      # ✅ 0-100 expected
    subjective_overall_score: float, # ✅ 0-10 expected (normalized to 0-100)
    readability_score: float         # ✅ 0-100 expected
) -> Dict[str, Any]:
    # Returns composite_score: 0-100 ❌ But database expects 0-1.0!
```

---

## 🎯 **The Problem**

### Sweet Spot Query Failure
```python
# generation.py line 157
analyzer = SweetSpotAnalyzer(db_path, min_samples=5, success_threshold=80.0)
```

**With threshold=80.0:**
```sql
WHERE COALESCE(dr.composite_quality_score, dr.human_score) >= 80.0
```
- If `human_score` is 0-100: Expects ≥80% (works)
- If `human_score` is 0-1.0: Expects ≥8000% (IMPOSSIBLE)
- **Result**: 0 samples found (should be 22+)

**After fix (threshold=0.80):**
```sql
WHERE COALESCE(dr.composite_quality_score, dr.human_score) >= 0.80
```
- If `human_score` is 0-100: Expects ≥0.80% (too low!)
- If `human_score` is 0-1.0: Expects ≥80% (CORRECT)
- **Result**: 22 samples found ✅

---

## 🔧 **Immediate Fix Applied**

**File**: `shared/commands/generation.py`
```python
# OLD (BROKEN)
analyzer = SweetSpotAnalyzer(db_path, min_samples=5, success_threshold=80.0)

# NEW (FIXED)
analyzer = SweetSpotAnalyzer(db_path, min_samples=5, success_threshold=0.80)
```

**Status**: ✅ Fixes sweet spot analyzer for normalized scores (0-1.0)

---

## ⚠️ **Remaining Issues**

### 1. Inconsistent Database Values
**Problem**: Database contains BOTH formats (0-100 AND 0-1.0)
**Impact**: 
- Sweet spot analyzer gets mixed data
- Calculations may be incorrect
- Historical data comparison is unreliable

**Solution Options**:
1. **Migrate old data** - Convert all 0-100 scores to 0-1.0
2. **Add normalization layer** - Detect and normalize at query time
3. **Document mixed format** - Accept it and handle both

### 2. Composite Score Storage Scale
**Problem**: `composite_scorer` returns 0-100, but database expects 0-1.0
**Evidence**: Database shows `composite_quality_score=1.0` (not 100.0)
**Impact**: If composite score is stored as 0-100, it breaks sweet spot queries

**Need to verify**: Where is composite_quality_score normalized before storage?

### 3. Missing Composite Scores
**Problem**: Most records have `composite_quality_score=NULL`
**Query**: `SELECT COUNT(*) FROM detection_results WHERE composite_quality_score IS NOT NULL;`
**Impact**: Sweet spot falls back to `human_score` (mixed format)

---

## 📋 **Recommended Actions**

### Priority 1: Standardize Database Format (0-1.0)
```python
# Option A: Normalize at storage time
human_score_normalized = winston_result.get('human_score', 0) / 100.0
ai_score_normalized = winston_result.get('ai_score', 1.0)  # Already normalized
composite_normalized = composite_score / 100.0 if composite_score else None

# Option B: Migration script
UPDATE detection_results 
SET human_score = human_score / 100.0 
WHERE human_score > 1.0;
```

### Priority 2: Add Validation
```python
def log_detection(...):
    # Validate ranges before storage
    if not 0.0 <= human_score <= 1.0:
        raise ValueError(f"human_score must be 0-1.0, got {human_score}")
    if not 0.0 <= ai_score <= 1.0:
        raise ValueError(f"ai_score must be 0-1.0, got {ai_score}")
```

### Priority 3: Document Expected Ranges
Create `docs/08-development/SCORE_NORMALIZATION_STANDARD.md`:
```markdown
# Score Normalization Standard

ALL scores stored in database MUST use 0-1.0 scale:
- human_score: 0.0 (0% human) to 1.0 (100% human)
- ai_score: 0.0 (0% AI) to 1.0 (100% AI)
- composite_quality_score: 0.0 (worst) to 1.0 (best)
- readability_score: 0.0 (worst) to 1.0 (best)

Conversion from Winston API (0-100):
- normalized = winston_raw / 100.0
```

---

## 🧪 **Testing Required**

1. **Query all records** and check for out-of-range values:
```sql
SELECT COUNT(*) FROM detection_results WHERE human_score > 1.0;
SELECT COUNT(*) FROM detection_results WHERE ai_score > 1.0;
SELECT COUNT(*) FROM detection_results WHERE composite_quality_score > 1.0;
```

2. **Test sweet spot with both formats**:
```python
# Test with normalized threshold
analyzer = SweetSpotAnalyzer(db_path, success_threshold=0.80)
results = analyzer.get_sweet_spot_ranges()
# Should find 22+ samples

# Test with raw threshold (should fail on normalized data)
analyzer = SweetSpotAnalyzer(db_path, success_threshold=80.0)
results = analyzer.get_sweet_spot_ranges()
# Should find 0 samples
```

3. **Verify composite score storage**:
```python
# Generate content and check what gets stored
python3 run.py --caption "TestMaterial" --skip-integrity-check
# Then query: SELECT composite_quality_score FROM detection_results ORDER BY id DESC LIMIT 1;
# Expected: 0.0-1.0, not 0-100
```

---

## 📌 **Status**

- ✅ **Sweet spot threshold fixed** (0.80 instead of 80.0)
- ⚠️ **Database inconsistency identified** (mixed 0-100 and 0-1.0 formats)
- ❓ **Composite score normalization** (needs verification)
- 🔄 **Migration strategy** (to be determined)

---

## 📅 **Next Steps**

1. Run database queries to assess extent of inconsistency
2. Decide on normalization strategy (migrate vs. handle both)
3. Update all database write operations to normalize scores
4. Add validation at storage layer
5. Create comprehensive test suite for score normalization
6. Document standard in system architecture

---

**Date**: November 20, 2025
**Issue**: Scoring normalization inconsistency
**Fix Applied**: Sweet spot threshold normalized to 0-1.0 scale
**Status**: Partial fix, full solution pending
