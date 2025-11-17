# Realism Metrics Implementation - November 16, 2025

## 🎯 Objective
Implement structured realism feedback system to enable parameter learning for content realism (in addition to existing Winston AI detection optimization).

## ✅ Completed Work

### 1. Updated Grok Evaluation Prompt
**File**: `processing/subjective/evaluator.py` (Lines 158-188)

Added structured **Realism Analysis** section to Grok prompt requesting:
```
**Realism Analysis**:
- AI Tendencies Detected: [comma-separated list]
  - formulaic_phrasing
  - unnatural_transitions
  - excessive_enthusiasm
  - rigid_structure
  - overly_polished
  - mechanical_tone
  - repetitive_patterns
  - forced_transitions
  - artificial_symmetry
  - generic_language
  - none
- Realism Score (0-10): X (10=perfectly human, 0=obviously AI)
- Voice Authenticity (0-10): X (natural conversational flow)
- Tonal Consistency (0-10): X (genuine variations without jarring shifts)
```

**Impact**: Grok now returns machine-readable realism data instead of only free-form narrative.

---

### 2. Updated SubjectiveEvaluationResult Dataclass
**File**: `processing/subjective/evaluator.py` (Lines 41-51)

Added 4 new optional fields:
```python
@dataclass
class SubjectiveEvaluationResult:
    # ... existing fields ...
    narrative_assessment: Optional[str] = None
    
    # NEW: Realism metrics
    realism_score: Optional[float] = None  # 0-10 scale
    voice_authenticity: Optional[float] = None  # 0-10 scale
    tonal_consistency: Optional[float] = None  # 0-10 scale
    ai_tendencies: Optional[List[str]] = None  # List of detected AI patterns
    
    raw_response: Optional[str] = None
```

**Impact**: Evaluation results can now store structured realism metrics.

---

### 3. Implemented Realism Metrics Parser
**File**: `processing/subjective/evaluator.py` (Lines 291-343)

Added parsing logic in `_parse_claude_response()` to extract:

```python
# Extract realism analysis metrics
for i, line in enumerate(lines):
    if '**Realism Analysis**' in line or 'Realism Analysis:' in line:
        # Parse AI Tendencies (comma-separated list)
        if 'AI Tendencies Detected:' in line_text:
            tendencies_str = line_text.split(':', 1)[1].strip()
            tendencies_str = tendencies_str.strip('[]')
            if tendencies_str and tendencies_str.lower() != 'none':
                ai_tendencies = [t.strip() for t in tendencies_str.split(',')]
        
        # Parse Realism Score (X/10 or X format)
        if 'Realism Score' in line_text:
            score_str = line_text.split(':', 1)[1].strip().split('/')[0]
            realism_score = float(score_str)
        
        # Parse Voice Authenticity
        if 'Voice Authenticity' in line_text:
            score_str = line_text.split(':', 1)[1].strip().split('/')[0]
            voice_authenticity = float(score_str)
        
        # Parse Tonal Consistency
        if 'Tonal Consistency' in line_text:
            score_str = line_text.split(':', 1)[1].strip().split('/')[0]
            tonal_consistency = float(score_str)
```

**Impact**: Structured realism data now extracted from Grok response and populated in result object.

---

### 4. Updated Database Schema
**File**: `processing/detection/winston_feedback_db.py` (Lines 151-155)

Added 4 new columns to `subjective_evaluations` table:
```sql
CREATE TABLE IF NOT EXISTS subjective_evaluations (
    ...
    narrative_assessment TEXT,
    realism_score REAL,
    voice_authenticity REAL,
    tonal_consistency REAL,
    ai_tendencies TEXT,  -- JSON array of detected patterns
    author_id INTEGER,
    ...
);
```

**Impact**: Database can now store realism metrics alongside existing evaluation data.

---

### 5. Updated Database Logging
**File**: `processing/detection/winston_feedback_db.py` (Lines 572-611)

Updated `log_subjective_evaluation()` INSERT statement:
```python
INSERT INTO subjective_evaluations
(timestamp, topic, component_type, domain, generated_text,
 overall_score, clarity_score, professionalism_score,
 technical_accuracy_score, human_likeness_score,
 engagement_score, jargon_free_score,
 passes_quality_gate, quality_threshold, evaluation_time_ms,
 strengths, weaknesses, recommendations,
 author_id, attempt_number, has_claude_api, narrative_assessment,
 realism_score, voice_authenticity, tonal_consistency, ai_tendencies)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```

Added to VALUES tuple:
```python
evaluation_result.realism_score,
evaluation_result.voice_authenticity,
evaluation_result.tonal_consistency,
json.dumps(evaluation_result.ai_tendencies) if evaluation_result.ai_tendencies else None
```

**Impact**: Realism metrics now persisted to database for learning system access.

---

## 📊 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Generation                                                │
│    python3 run.py --caption "Aluminum"                       │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Global Evaluation (after generation)                      │
│    shared/commands/global_evaluation.py                      │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Grok Evaluation (with enhanced prompt)                    │
│    processing/subjective/evaluator.py                        │
│    → Returns structured realism metrics                      │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Parse Realism Metrics                                     │
│    _parse_claude_response()                                  │
│    → Extracts AI tendencies list + 3 scores                  │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Store in Database                                         │
│    processing/detection/winston_feedback_db.py               │
│    → subjective_evaluations table                            │
│    → Columns: realism_score, voice_authenticity,             │
│               tonal_consistency, ai_tendencies               │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. NEXT: RealismOptimizer                                    │
│    processing/learning/realism_optimizer.py (TODO)           │
│    → Analyzes ai_tendencies                                  │
│    → Suggests parameter adjustments                          │
│    → Learns from retry outcomes                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Next Steps (TODO)

### 1. Create RealismOptimizer Class
**New File**: `processing/learning/realism_optimizer.py`

```python
class RealismOptimizer:
    """Optimizes parameters to improve realism scores."""
    
    def analyze_ai_tendencies(self, tendencies: List[str]) -> Dict[str, float]:
        """Map AI tendencies to parameter adjustments."""
        # formulaic_phrasing → increase temperature
        # unnatural_transitions → decrease structural_predictability
        # excessive_enthusiasm → reduce emotional_tone
        # etc.
        pass
    
    def suggest_parameters(self, current_params, realism_issues) -> Dict:
        """Return adjusted parameters to fix realism issues."""
        pass
    
    def learn_from_outcome(self, adjustments, outcome_improved):
        """Update learning table with success/failure."""
        pass
```

### 2. Create Realism Learning Database Table
```sql
CREATE TABLE IF NOT EXISTS realism_learning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    material TEXT NOT NULL,
    component_type TEXT NOT NULL,
    
    -- Original state
    original_realism_score REAL,
    detected_ai_tendencies TEXT,  -- JSON array
    original_parameters TEXT,  -- JSON object
    
    -- Adjustment made
    parameter_adjustments TEXT,  -- JSON object
    adjustment_rationale TEXT,
    
    -- Outcome
    new_realism_score REAL,
    improvement REAL,  -- new_score - original_score
    success BOOLEAN,  -- improvement > 0
    
    -- Metadata
    subjective_evaluation_id INTEGER,
    FOREIGN KEY (subjective_evaluation_id) REFERENCES subjective_evaluations(id)
);
```

### 3. Implement Dual-Objective Scoring
**Modify**: `materials/unified_generator.py` generation retry loop

```python
# Current: Only Winston score optimization
if winston_score >= threshold:
    accept_generation()

# NEW: Dual-objective optimization
combined_score = (winston_score * 0.4) + (realism_score * 0.6)
if combined_score >= threshold:
    accept_generation()
else:
    # Get parameter adjustments from RealismOptimizer
    adjustments = realism_optimizer.suggest_parameters(
        current_params,
        evaluation.ai_tendencies
    )
    # Retry with adjusted parameters
```

### 4. Integration Testing
- Generate caption with realism evaluation
- Verify realism metrics in database
- Trigger parameter adjustment on low realism score
- Verify retry with adjusted parameters
- Confirm realism improvement tracked in learning table

### 5. Batch Testing
Update `scripts/batch_caption_test.py` to display:
- Realism Score (0-10)
- Voice Authenticity (0-10)
- Tonal Consistency (0-10)
- AI Tendencies Detected (list)
- Combined Score (Winston 40% + Realism 60%)

---

## 🚀 Expected Outcomes

### Current Problem
- Parameter optimization → High Winston scores (95%+)
- But text sounds unrealistic, overly polished, mechanical

### Solution After Implementation
- Dual optimization → High Winston scores + High realism scores
- Text beats AI detection AND sounds genuinely human
- Learning system continuously improves both objectives

### Key Insight
Winston optimization answers: "Does it look like AI?"
Realism optimization answers: "Does it SOUND human?"

Both are required for truly effective human-like content generation.

---

## 📝 Files Modified

1. ✅ `processing/subjective/evaluator.py` - Prompt, dataclass, parser
2. ✅ `processing/detection/winston_feedback_db.py` - Schema, logging
3. ⏳ `processing/learning/realism_optimizer.py` - TODO: Create
4. ⏳ `materials/unified_generator.py` - TODO: Integrate dual-objective
5. ⏳ `scripts/batch_caption_test.py` - TODO: Display realism metrics

---

## 🔍 Validation Commands

```bash
# Test single caption with realism evaluation
python3 run.py --caption "Aluminum"

# Check database for realism metrics
sqlite3 data/winston_feedback.db "SELECT realism_score, voice_authenticity, tonal_consistency, ai_tendencies FROM subjective_evaluations ORDER BY id DESC LIMIT 1;"

# Run batch test (after RealismOptimizer implemented)
python3 scripts/batch_caption_test.py

# View learning data (after learning table created)
sqlite3 data/winston_feedback.db "SELECT * FROM realism_learning ORDER BY timestamp DESC LIMIT 5;"
```

---

## ✨ Summary

**Completed**: Structured realism metrics infrastructure (Grok prompt, dataclass, parser, database schema)

**Next**: Create RealismOptimizer to use this data for parameter learning

**Impact**: Enables dual-objective optimization to produce content that is BOTH undetectable by AI detection AND genuinely human-sounding.

The foundation is now in place to solve the core problem: high AI detection scores producing unrealistic text.
