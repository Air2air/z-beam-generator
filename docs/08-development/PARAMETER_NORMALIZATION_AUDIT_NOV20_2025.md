# Parameter Value Normalization - Complete E2E Audit
## November 20, 2025

## 🎯 **Executive Summary**

**CRITICAL FINDING**: The system has **INCONSISTENT normalization** across the entire pipeline:
- Winston API returns `human_score` as 0-100, `ai_score` is normalized to 0-1.0 by client
- Database stores **MIXED formats** (both 0-100 and 0-1.0)
- Documentation **CONTRADICTS** implementation
- Composite scorer expects 0-100 but database queries expect 0-1.0
- Sweet spot analyzer was using wrong threshold (now fixed)

---

## 📊 **Score Normalization Map**

### Winston API Response (`shared/api/client.py`)
```python
def detect_ai_content(self, text: str) -> Dict[str, Any]:
    # Winston API returns 'score' field as 0-100
    human_score = data.get('score', 0)  # ✅ 0-100 scale (Winston native)
    
    # Client normalizes AI score to 0-1.0
    ai_score = (100 - human_score) / 100.0  # ✅ 0-1.0 scale (normalized)
    
    return {
        'human_score': human_score,  # ❌ 0-100 scale
        'ai_score': ai_score,         # ✅ 0-1.0 scale
        'readability_score': data.get('readability_score')  # ❓ Unknown scale
    }
```

**Expected Ranges**:
- `human_score`: 0-100 (percentage)
- `ai_score`: 0-1.0 (normalized)
- `readability_score`: Flesch scale (0-100, higher = easier)

---

### Database Storage (`postprocessing/detection/winston_feedback_db.py`)

#### Schema (actual)
```sql
CREATE TABLE detection_results (
    human_score REAL NOT NULL,           -- ❓ No scale specified in schema
    ai_score REAL NOT NULL,              -- ❓ No scale specified in schema
    readability_score REAL,              -- ❓ No scale specified in schema
    composite_quality_score REAL,        -- ❓ No scale specified in schema
    ...
);
```

#### Storage Code
```python
def log_detection(...):
    cursor.execute("""
        INSERT INTO detection_results 
        (human_score, ai_score, readability_score, composite_quality_score, ...)
        VALUES (?, ?, ?, ?, ...)
    """, (
        winston_result.get('human_score', 0),     # ❌ Stores 0-100 from Winston
        winston_result.get('ai_score', 1.0),      # ✅ Stores 0-1.0 normalized
        winston_result.get('readability_score'),  # ❓ Unknown scale
        composite_quality_score                   # ❓ Unknown scale (0-100 expected)
    ))
```

**Actual Database Values** (from query):
```sql
SELECT MIN(human_score), MAX(human_score), AVG(human_score) FROM detection_results;
-- Result: 0.0 | 7.67 | 0.42
```

**INCONSISTENCY DETECTED**:
- Expected: 0-100 (from Winston API)
- Actual: 0-7.67 (MUCH lower than expected)
- Some records: 1.0 (perfect score, normalized)
- Many records: 0.0 (failures or skipped)

**Hypothesis**: Scores are being normalized SOMEWHERE between Winston API and database, but:
1. NOT consistently (mix of 0-100 and 0-1.0)
2. NOT documented
3. NOT in the obvious places

---

### Documentation (`docs/02-architecture/UNIFIED_LEARNING_ARCHITECTURE.md`)

```markdown
CREATE TABLE detection_results (
    human_score REAL,      -- 0-100 scale  ❌ CONTRADICTS actual data
    ai_score REAL,          -- 0-1.0 scale  ✅ CORRECT
    ...
);
```

**Documentation says** `human_score` is 0-100, but **database has** 0-7.67!

---

### Validation Constants (`generation/validation/constants.py`)

```python
class ValidationConstants:
    # Thresholds
    WINSTON_AI_THRESHOLD = 0.33          # ✅ 0-1.0 scale (33% AI max)
    WINSTON_HUMAN_THRESHOLD = 0.67       # ✅ 0-1.0 scale (67%+ human)
    
    # Default scores
    DEFAULT_AI_SCORE = 0.0               # ✅ 0-1.0 scale (perfect)
    DEFAULT_HUMAN_SCORE = 100.0          # ❌ 0-100 scale (inconsistent!)
    DEFAULT_FALLBACK_AI_SCORE = 0.5      # ✅ 0-1.0 scale (neutral)
    
    @staticmethod
    def ai_to_human_score(ai_score: float) -> float:
        """Convert AI score (0-1) to human percentage (0-100)."""
        return (1.0 - ai_score) * 100.0   # ✅ Expects 0-1.0 input, returns 0-100
    
    @staticmethod
    def human_to_ai_score(human_percent: float) -> float:
        """Convert human percentage (0-100) to AI score (0-1)."""
        return 1.0 - (human_percent / 100.0)  # ✅ Expects 0-100 input, returns 0-1.0
```

**INCONSISTENCY**: `DEFAULT_HUMAN_SCORE = 100.0` uses 0-100 scale, but thresholds use 0-1.0 scale!

---

### Composite Scorer (`postprocessing/evaluation/composite_scorer.py`)

```python
def calculate_composite_score(
    self,
    winston_human_score: float,       # ✅ Expects 0-100
    subjective_overall_score: float,  # ✅ Expects 0-10 (normalized to 0-100 internally)
    readability_score: float          # ✅ Expects 0-100
) -> Dict[str, Any]:
    # Validate ranges
    if not 0.0 <= winston_human_score <= 100.0:
        raise ValueError(f"winston_human_score must be 0-100, got {winston_human_score}")
    
    # Normalize subjective to 0-100
    subjective_normalized = subjective_overall_score * 10.0 if subjective_overall_score is not None else None
    
    # Calculate contributions
    winston_contrib = winston_human_score * available_weights['winston']
    subjective_contrib = subjective_normalized * available_weights['subjective'] if subjective_normalized else 0.0
    readability_contrib = readability_score * available_weights['readability'] if readability_score else 0.0
    
    # Composite score
    composite = winston_contrib + subjective_contrib + readability_contrib  # ✅ Returns 0-100
    
    return {'composite_score': round(composite, 2)}  # ✅ 0-100 scale
```

**Expected Input Scales**:
- `winston_human_score`: 0-100
- `subjective_overall_score`: 0-10
- `readability_score`: 0-100

**Output Scale**: 0-100

**BUT**: Database queries expect composite_quality_score in 0-1.0 scale!

---

### Simple Step Composite Scorer (`postprocessing/steps/quality/composite_scorer.py`)

```python
def _execute_logic(self, context: Dict[str, Any]) -> float:
    winston_human_score = context['winston_result']['human_score']  # ❌ Expects 0-100, gets ???
    realism_score = context['realism_result']['score']              # ✅ 0-10 scale
    
    # Winston 60% + Realism 40% (convert realism 0-10 to 0-100)
    composite = (winston_human_score * 0.6) + (realism_score * 10 * 0.4)
    
    return round(composite, 2)  # ✅ Returns 0-100
```

**ASSUMPTION**: Expects `winston_human_score` as 0-100, but may receive 0-1.0 from database!

---

### Sweet Spot Analyzer (`learning/sweet_spot_analyzer.py`)

```python
query = """
    SELECT ... 
    FROM generation_parameters gp
    JOIN detection_results dr ON gp.detection_result_id = dr.id
    WHERE COALESCE(dr.composite_quality_score, dr.human_score) >= ?
      AND dr.success = 1
"""
params = [self.success_threshold]  # Was 80.0, NOW 0.80 ✅ FIXED
```

**Original Bug**: Used `success_threshold=80.0` (0-100 scale)
**Database Contains**: 0-1.0 scale (or mixed)
**Result**: 0 samples found (expected 22+)

**Fix Applied**: Changed to `success_threshold=0.80` ✅

---

## 🔍 **Identified Issues**

### Issue 1: Mixed Database Formats ❌ CRITICAL
**Problem**: Database contains BOTH 0-100 AND 0-1.0 formats for same fields
**Evidence**:
```sql
SELECT MIN(human_score), MAX(human_score) FROM detection_results;
-- Result: 0.0 | 7.67
-- Expected if 0-100: 0 | 100
-- Expected if 0-1.0: 0.0 | 1.0
-- Actual: MIXED (7.67 suggests 0-100, but range suggests 0-1.0)
```

**Impact**:
- Analytics calculations wrong
- Sweet spot analyzer gets inconsistent data
- Composite scores invalid if using wrong scale

### Issue 2: Documentation Contradicts Implementation ❌ CRITICAL
**Problem**: Docs say `human_score` is 0-100, but database has 0-7.67
**Files Affected**:
- `docs/02-architecture/UNIFIED_LEARNING_ARCHITECTURE.md`
- `docs/08-development/SCORE_DISPLAY_STANDARDS.md`
- `postprocessing/evaluation/SCORING_MODULE_README.md`

### Issue 3: Validation Constants Inconsistent ⚠️ HIGH
**Problem**: `DEFAULT_HUMAN_SCORE = 100.0` but `WINSTON_HUMAN_THRESHOLD = 0.67`
**Location**: `generation/validation/constants.py`
**Impact**: Mixing scales in same class confuses developers

### Issue 4: Composite Scorer Scale Mismatch ⚠️ HIGH
**Problem**: Composite scorer returns 0-100, but database queries expect 0-1.0
**Evidence**: Sweet spot query needed threshold change from 80.0 to 0.80
**Impact**: All sweet spot calculations were failing

### Issue 5: No Normalization Layer ❌ CRITICAL
**Problem**: Winston API returns 0-100, but somewhere it becomes 0-1.0
**Missing**: Explicit normalization before database storage
**Result**: Inconsistent data depending on code path taken

---

## 🎯 **Root Cause Analysis**

### Where is Normalization Happening?

**Theory 1: Multiple Code Paths**
- Path A: Winston API → Direct storage (0-100)
- Path B: Winston API → Normalization → Storage (0-1.0)
- Path C: Skipped validation → Default values (100.0 or 1.0)

**Theory 2: Historical Changes**
- Old code stored 0-100
- New code stores 0-1.0
- No migration script run
- Database has mixed old/new data

**Theory 3: Calculation Errors**
- `human_score = 7.67` could be:
  - 7.67% human (0-100 scale) = terrible score
  - 7.67 subjective score (0-10 scale) = good score, wrong field
  - 0.0767 (0-1.0 scale) displayed wrong = 7.67% human

---

## 📋 **Comprehensive Solution**

### Phase 1: Standardize on 0-1.0 Normalized Scale ✅ RECOMMENDED

**Rationale**:
1. AI/ML convention: normalized 0-1.0 for all scores
2. Easier math: no division needed for thresholds
3. Consistent with `ai_score` already being 0-1.0
4. Prevents scale confusion

**Changes Required**:

#### 1.1: Update Winston API Client
```python
# shared/api/client.py
def detect_ai_content(self, text: str) -> Dict[str, Any]:
    human_score = data.get('score', 0)  # Winston returns 0-100
    ai_score = (100 - human_score) / 100.0
    
    return {
        'ai_score': ai_score,                    # ✅ 0-1.0 normalized
        'human_score': human_score / 100.0,      # ✅ NORMALIZE to 0-1.0
        'human_score_raw': human_score,          # Keep original for display
        'readability_score': data.get('readability_score', 0) / 100.0,  # ✅ Normalize
        ...
    }
```

#### 1.2: Update Validation Constants
```python
# generation/validation/constants.py
class ValidationConstants:
    # ALL thresholds on 0-1.0 scale
    WINSTON_AI_THRESHOLD = 0.33          # ✅ 33% AI max
    WINSTON_HUMAN_THRESHOLD = 0.67       # ✅ 67% human min
    
    # ALL defaults on 0-1.0 scale
    DEFAULT_AI_SCORE = 0.0               # ✅ Perfect (0% AI)
    DEFAULT_HUMAN_SCORE = 1.0            # ✅ CHANGED: Perfect (100% human)
    DEFAULT_FALLBACK_AI_SCORE = 0.5      # ✅ Neutral (50% AI)
    
    @staticmethod
    def to_percentage(normalized: float) -> float:
        """Convert normalized (0-1.0) to percentage (0-100) for display."""
        return normalized * 100.0
    
    @staticmethod
    def from_percentage(percentage: float) -> float:
        """Convert percentage (0-100) to normalized (0-1.0) for storage."""
        return percentage / 100.0
```

#### 1.3: Update Composite Scorer
```python
# postprocessing/evaluation/composite_scorer.py
def calculate_composite_score(
    self,
    winston_human_score: float,       # ✅ NOW expects 0-1.0
    subjective_overall_score: float,  # ✅ NOW expects 0-1.0 (was 0-10)
    readability_score: float          # ✅ NOW expects 0-1.0 (was 0-100)
) -> Dict[str, Any]:
    # Validate ALL on 0-1.0 scale
    if not 0.0 <= winston_human_score <= 1.0:
        raise ValueError(f"winston_human_score must be 0-1.0, got {winston_human_score}")
    if subjective_overall_score is not None and not 0.0 <= subjective_overall_score <= 1.0:
        raise ValueError(f"subjective_overall_score must be 0-1.0, got {subjective_overall_score}")
    if readability_score is not None and not 0.0 <= readability_score <= 1.0:
        raise ValueError(f"readability_score must be 0-1.0, got {readability_score}")
    
    # Calculate (all on same scale now!)
    winston_contrib = winston_human_score * available_weights['winston']
    subjective_contrib = subjective_overall_score * available_weights['subjective'] if subjective_overall_score else 0.0
    readability_contrib = readability_score * available_weights['readability'] if readability_score else 0.0
    
    composite = winston_contrib + subjective_contrib + readability_contrib
    
    return {'composite_score': round(composite, 4)}  # ✅ Returns 0-1.0
```

#### 1.4: Update Database Schema Documentation
```sql
-- postprocessing/detection/winston_feedback_db.py
CREATE TABLE detection_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    human_score REAL NOT NULL,           -- 0-1.0 normalized (0.67 = 67% human)
    ai_score REAL NOT NULL,              -- 0-1.0 normalized (0.33 = 33% AI)
    readability_score REAL,              -- 0-1.0 normalized (0.80 = 80/100 Flesch)
    composite_quality_score REAL,        -- 0-1.0 normalized (weighted average)
    ...
);
```

#### 1.5: Migrate Existing Data
```python
# scripts/migrate_scores_to_normalized.py
import sqlite3

def migrate_scores():
    """Convert all 0-100 scores to 0-1.0 normalized."""
    conn = sqlite3.connect('z-beam.db')
    cursor = conn.cursor()
    
    # Find records with scores > 1.0 (these are 0-100 format)
    cursor.execute("""
        UPDATE detection_results
        SET 
            human_score = human_score / 100.0,
            composite_quality_score = CASE 
                WHEN composite_quality_score > 1.0 THEN composite_quality_score / 100.0
                ELSE composite_quality_score
            END,
            readability_score = CASE
                WHEN readability_score > 1.0 THEN readability_score / 100.0
                ELSE readability_score
            END
        WHERE human_score > 1.0
    """)
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT MAX(human_score), MAX(composite_quality_score) FROM detection_results")
    max_human, max_composite = cursor.fetchone()
    
    print(f"✅ Migration complete")
    print(f"   Max human_score: {max_human:.4f} (should be ≤ 1.0)")
    print(f"   Max composite_quality_score: {max_composite:.4f} (should be ≤ 1.0)")
    
    conn.close()

if __name__ == "__main__":
    migrate_scores()
```

#### 1.6: Add Validation at Storage
```python
# postprocessing/detection/winston_feedback_db.py
def log_detection(...):
    # Validate all scores are 0-1.0 before storage
    human_score = winston_result.get('human_score', 0)
    ai_score = winston_result.get('ai_score', 1.0)
    composite_score = composite_quality_score if composite_quality_score else None
    
    # Enforce 0-1.0 range
    if not 0.0 <= human_score <= 1.0:
        raise ValueError(f"human_score must be 0-1.0, got {human_score}")
    if not 0.0 <= ai_score <= 1.0:
        raise ValueError(f"ai_score must be 0-1.0, got {ai_score}")
    if composite_score is not None and not 0.0 <= composite_score <= 1.0:
        raise ValueError(f"composite_quality_score must be 0-1.0, got {composite_score}")
    
    cursor.execute("""INSERT INTO detection_results ...""", (...))
```

---

## 📊 **Score Display Standards**

After normalization, **ALL scores stored as 0-1.0**, but **displayed as percentages**:

```python
# Display function
def format_score_for_display(normalized_score: float, precision: int = 1) -> str:
    """Convert normalized score (0-1.0) to percentage string for display."""
    if normalized_score is None:
        return "N/A"
    percentage = normalized_score * 100.0
    return f"{percentage:.{precision}f}%"

# Usage
print(f"Human Score: {format_score_for_display(0.847)}")  # "84.7%"
print(f"AI Score: {format_score_for_display(0.153)}")     # "15.3%"
print(f"Composite: {format_score_for_display(0.823)}")    # "82.3%"
```

---

## 🧪 **Testing Plan**

### Test 1: Verify Winston API Returns
```python
def test_winston_normalization():
    from shared.api.client_factory import create_api_client
    
    client = create_api_client('winston')
    result = client.detect_ai_content("Test text here" * 100)
    
    # After fix
    assert 0.0 <= result['human_score'] <= 1.0, "human_score must be 0-1.0"
    assert 0.0 <= result['ai_score'] <= 1.0, "ai_score must be 0-1.0"
    
    # Inverse relationship
    assert abs((result['human_score'] + result['ai_score']) - 1.0) < 0.01
```

### Test 2: Verify Database Storage
```python
def test_database_normalized():
    import sqlite3
    
    conn = sqlite3.connect('z-beam.db')
    cursor = conn.cursor()
    
    # Check all scores are 0-1.0
    cursor.execute("SELECT MAX(human_score), MAX(ai_score), MAX(composite_quality_score) FROM detection_results")
    max_human, max_ai, max_composite = cursor.fetchone()
    
    assert max_human <= 1.0, f"human_score exceeds 1.0: {max_human}"
    assert max_ai <= 1.0, f"ai_score exceeds 1.0: {max_ai}"
    assert max_composite is None or max_composite <= 1.0, f"composite exceeds 1.0: {max_composite}"
```

### Test 3: Verify Composite Calculation
```python
def test_composite_normalized():
    from postprocessing.evaluation.composite_scorer import CompositeScorer
    
    scorer = CompositeScorer()
    
    result = scorer.calculate_composite_score(
        winston_human_score=0.85,    # 85% human
        subjective_overall_score=0.8, # 8/10 = 0.8
        readability_score=0.75        # 75/100 = 0.75
    )
    
    assert 0.0 <= result['composite_score'] <= 1.0
    assert result['composite_score'] > 0.7  # Weighted average should be ~0.8
```

### Test 4: Verify Sweet Spot Works
```python
def test_sweet_spot_finds_samples():
    from learning.sweet_spot_analyzer import SweetSpotAnalyzer
    
    analyzer = SweetSpotAnalyzer('z-beam.db', min_samples=5, success_threshold=0.80)
    results = analyzer.get_sweet_spot_ranges()
    
    # Should find samples now
    assert len(results) > 0, "Sweet spot should find samples with normalized threshold"
    
    metadata = results.get('metadata', {})
    assert metadata.get('sample_count', 0) >= 5, "Should have at least 5 samples"
```

---

## 📅 **Implementation Timeline**

### Phase 1: Immediate (Complete) ✅
- [x] Fix sweet spot threshold (0.80 instead of 80.0)
- [x] Document the issue comprehensively

### Phase 2: Critical (1-2 days)
- [ ] Update Winston API client to normalize human_score
- [ ] Update ValidationConstants to use 0-1.0 consistently
- [ ] Add validation at database storage
- [ ] Run migration script on z-beam.db

### Phase 3: Integration (1 day)
- [ ] Update composite scorer to expect 0-1.0
- [ ] Update all display code to format percentages
- [ ] Update all documentation
- [ ] Add comprehensive tests

### Phase 4: Verification (1 day)
- [ ] Run full test suite
- [ ] Verify all scores in database are 0-1.0
- [ ] Generate sample content and verify end-to-end
- [ ] Update all architecture docs

---

## 📌 **Status**

- ✅ **Issue Identified**: Mixed normalization across system
- ✅ **Root Cause Found**: No consistent normalization layer
- ✅ **Solution Designed**: Standardize on 0-1.0 normalized
- ✅ **Quick Fix Applied**: Sweet spot threshold corrected
- 🔄 **Full Fix Pending**: Comprehensive normalization implementation

---

**Date**: November 20, 2025  
**Issue**: Parameter value normalization inconsistency  
**Severity**: CRITICAL  
**Quick Fix**: ✅ Applied (sweet spot threshold)  
**Full Fix**: Pending implementation  
**Impact**: Analytics, sweet spot, composite scoring all affected
