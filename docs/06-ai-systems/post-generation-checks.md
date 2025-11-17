# Post-Generation Integrity Checks

**Date**: November 16, 2025  
**Status**: Production Implementation  
**Version**: 1.0

---

## Overview

Post-generation integrity checks verify that all generation outputs are properly logged to the learning database and that the system's feedback loop is functioning correctly. These checks run automatically after every caption, subtitle, and FAQ generation.

---

## Purpose

Ensures the self-learning system remains operational by verifying:
1. Detection results are logged to database
2. Generation parameters are stored for learning
3. Sweet spot recommendations are updated
4. Subjective evaluations are recorded

---

## Architecture

### Location
- **Module**: `processing/integrity/integrity_checker.py`
- **Method**: `IntegrityChecker.run_post_generation_checks()`
- **Integration**: `shared/commands/generation.py` (all handlers)

### Flow
```
Generation Complete
    ↓
Post-Generation Integrity Check
    ↓
├─ Check 1: Database Exists
├─ Check 2: Detection Logged
├─ Check 3: Parameters Logged  
├─ Check 4: Sweet Spot Updated
└─ Check 5: Subjective Evaluation Logged
    ↓
Report Results to User
```

---

## Checks Performed

### 1. Database Exists
**Purpose**: Verify winston_feedback.db is accessible  
**Status**: FAIL if database not found  
**Action**: Generation data cannot be stored without database

```python
# Expected path
db_path = Path('data/winston_feedback.db')

# Result
✅ PASS: Database found at data/winston_feedback.db
❌ FAIL: Winston feedback database not found
```

### 2. Detection Result Logged
**Purpose**: Verify Winston AI detection was logged  
**Status**: FAIL if no detection found for material/component  
**Data Logged**:
- Human score
- AI score  
- Success/failure status
- Timestamp

```python
# Query
SELECT id, timestamp, human_score, ai_score, success
FROM detection_results
WHERE material = ? AND component_type = ?
ORDER BY timestamp DESC
LIMIT 1

# Result
✅ PASS: Detection result #410 logged (human: 98.0%, AI: 2.0%)
❌ FAIL: No detection result found for Brass/caption
```

### 3. Generation Parameters Logged
**Purpose**: Verify all generation parameters were stored  
**Status**: WARN if parameters not logged  
**Data Logged**:
- Temperature
- Frequency penalty
- Presence penalty
- All 14 modular parameters
- Full JSON snapshot

```python
# Query
SELECT id, temperature, frequency_penalty, presence_penalty, param_hash
FROM generation_parameters
WHERE detection_result_id = ?

# Result
✅ PASS: Generation parameters #331 logged (temp: 0.640, freq: 0.150, pres: 0.100)
⚠️  WARN: No generation parameters logged for detection #410
```

### 4. Sweet Spot Table Updated
**Purpose**: Verify sweet spot recommendations exist or are accumulating data  
**Status**: PASS if < 5 samples (not enough data yet)  
**Threshold**: 5 successful generations required before sweet spot calculated

```python
# Query
SELECT sample_count, confidence_level, last_updated, avg_human_score
FROM sweet_spot_recommendations
WHERE material = ? AND component_type = ?

# Results
✅ PASS: Sweet spot exists: 12 samples, high confidence, avg score 85.3%
✅ PASS: Sweet spot not yet calculated (only 3 samples, need 5+ for sweet spot)
⚠️  WARN: Sweet spot not found despite 8 samples - may need manual update
```

### 5. Subjective Evaluation Logged
**Purpose**: Verify content quality evaluation was stored  
**Status**: WARN if using rule-based fallback (Claude API unavailable)  
**Data Logged**:
- Overall score (0-10)
- 6 dimension scores
- Quality gate pass/fail
- Claude API availability flag

```python
# Query
SELECT id, overall_score, passes_quality_gate, has_claude_api, timestamp
FROM subjective_evaluations
WHERE topic = ? AND component_type = ?
ORDER BY timestamp DESC
LIMIT 1

# Results
✅ PASS: Subjective evaluation #50 logged: 7.4/10 (PASS)
⚠️  WARN: Subjective evaluation #50 logged: 7.4/10 (PASS) (rule-based fallback)
⚠️  WARN: No subjective evaluation found for Brass/caption
```

---

## Integration Points

### Caption Generation
**File**: `shared/commands/generation.py`
**Function**: `handle_caption_generation()`
**Location**: After "Caption generation complete!" message

```python
# Run post-generation integrity check
print("🔍 Running post-generation integrity check...")
from processing.integrity import IntegrityChecker
checker = IntegrityChecker()
post_results = checker.run_post_generation_checks(
    material=material_name,
    component_type='caption'
)

# Print results
post_pass = sum(1 for r in post_results if r.status.value == 'PASS')
post_warn = sum(1 for r in post_results if r.status.value == 'WARN')
post_fail = sum(1 for r in post_results if r.status.value == 'FAIL')

print(f"   {post_pass} passed, {post_warn} warnings, {post_fail} failed")

for result in post_results:
    icon = {"FAIL": "❌", "WARN": "⚠️", "PASS": "✅"}[result.status.value]
    print(f"   {icon} {result.check_name}: {result.message}")
```

### Subtitle Generation
**File**: `shared/commands/generation.py`
**Function**: `handle_subtitle_generation()`
**Integration**: Same pattern as caption generation

### FAQ Generation
**File**: `shared/commands/generation.py`
**Function**: `handle_faq_generation()`
**Integration**: Same pattern as caption generation

---

## Expected Output

### Successful Generation
```
✨ Caption generation complete!

🔍 Running post-generation integrity check...
   5 passed, 0 warnings, 0 failed
   ✅ Post-Gen: Database Exists: Database found at data/winston_feedback.db
   ✅ Post-Gen: Detection Logged: Detection result #410 logged (human: 98.0%, AI: 2.0%)
   ✅ Post-Gen: Parameters Logged: Generation parameters #331 logged (temp: 0.640, freq: 0.150, pres: 0.100)
   ✅ Post-Gen: Sweet Spot Updated: Sweet spot exists: 12 samples, high confidence, avg score 85.3%
   ✅ Post-Gen: Subjective Evaluation Logged: Subjective evaluation #50 logged: 7.4/10 (PASS)
```

### Early Material (< 5 samples)
```
🔍 Running post-generation integrity check...
   5 passed, 0 warnings, 0 failed
   ✅ Post-Gen: Database Exists: Database found at data/winston_feedback.db
   ✅ Post-Gen: Detection Logged: Detection result #1 logged (human: 45.2%, AI: 54.8%)
   ✅ Post-Gen: Parameters Logged: Generation parameters #1 logged (temp: 0.700, freq: 0.200, pres: 0.150)
   ✅ Post-Gen: Sweet Spot Updated: Sweet spot not yet calculated (only 1 samples, need 5+ for sweet spot)
   ✅ Post-Gen: Subjective Evaluation Logged: Subjective evaluation #1 logged: 8.2/10 (PASS)
```

### With Warnings
```
🔍 Running post-generation integrity check...
   3 passed, 2 warnings, 0 failed
   ✅ Post-Gen: Database Exists: Database found at data/winston_feedback.db
   ✅ Post-Gen: Detection Logged: Detection result #410 logged (human: 98.0%, AI: 2.0%)
   ⚠️  Post-Gen: Parameters Logged: No generation parameters logged for detection #410
   ✅ Post-Gen: Sweet Spot Updated: Sweet spot exists: 12 samples, high confidence, avg score 85.3%
   ⚠️  Post-Gen: Subjective Evaluation Logged: Subjective evaluation #50 logged: 7.4/10 (PASS) (rule-based fallback)
```

### With Failures
```
🔍 Running post-generation integrity check...
   1 passed, 0 warnings, 1 failed
   ✅ Post-Gen: Database Exists: Database found at data/winston_feedback.db
   ❌ Post-Gen: Detection Logged: No detection result found for Steel/caption
```

---

## Troubleshooting

### Database Not Found
**Symptom**: `❌ Post-Gen: Database Exists: Winston feedback database not found`  
**Cause**: winston_feedback.db was deleted or moved  
**Solution**: Database will be recreated on next generation with Winston integration

### No Detection Logged
**Symptom**: `❌ Post-Gen: Detection Logged: No detection result found`  
**Cause**: Winston API integration failed or was skipped  
**Solution**: Check Winston API configuration in .env (WINSTON_API_KEY)

### Parameters Not Logged
**Symptom**: `⚠️  Post-Gen: Parameters Logged: No generation parameters logged`  
**Cause**: Parameter logging failed in DynamicGenerator  
**Solution**: Check generator.py for parameter logging integration

### Sweet Spot Not Updated
**Symptom**: `⚠️  Post-Gen: Sweet Spot Updated: Sweet spot not found despite X samples`  
**Cause**: Sweet spot calculation didn't run or failed  
**Solution**: Manually trigger sweet spot update:
```python
from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
db = WinstonFeedbackDatabase('data/winston_feedback.db')
# Sweet spot calculation happens automatically on upsert
```

### No Subjective Evaluation
**Symptom**: `⚠️  Post-Gen: Subjective Evaluation Logged: No subjective evaluation found`  
**Cause**: Subjective evaluation was skipped or failed  
**Solution**: Check Grok API configuration and SubjectiveEvaluator integration

---

## Manual Verification

### Check Database Contents
```bash
# Total detection results
sqlite3 data/winston_feedback.db "SELECT COUNT(*) FROM detection_results"

# Recent detections
sqlite3 data/winston_feedback.db "SELECT material, component_type, human_score, timestamp FROM detection_results ORDER BY timestamp DESC LIMIT 10"

# Parameter storage
sqlite3 data/winston_feedback.db "SELECT COUNT(*) FROM generation_parameters"

# Sweet spot status
sqlite3 data/winston_feedback.db "SELECT material, component_type, sample_count, confidence_level FROM sweet_spot_recommendations"

# Subjective evaluations
sqlite3 data/winston_feedback.db "SELECT topic, component_type, overall_score, has_claude_api FROM subjective_evaluations ORDER BY timestamp DESC LIMIT 10"
```

### Verify Specific Material
```bash
# Check if material has complete data
python3 << 'EOF'
from processing.integrity import IntegrityChecker
checker = IntegrityChecker()
results = checker.run_post_generation_checks('Aluminum', 'caption')
for r in results:
    print(f"{r.status.value}: {r.check_name} - {r.message}")
EOF
```

---

## Testing

### Unit Tests
**File**: `tests/test_integrity_checker.py`
**Coverage**: Post-generation check methods

```python
def test_post_generation_checks_database_exists():
    """Verify database existence check"""
    
def test_post_generation_checks_detection_logged():
    """Verify detection result logging check"""
    
def test_post_generation_checks_parameters_logged():
    """Verify parameter storage check"""
    
def test_post_generation_checks_sweet_spot_updated():
    """Verify sweet spot calculation check"""
    
def test_post_generation_checks_subjective_evaluation_logged():
    """Verify subjective evaluation storage check"""
```

### Integration Tests
**File**: `tests/integration/test_generation_workflow.py`

```python
def test_caption_generation_with_post_checks():
    """Full caption generation with post-generation checks"""
    # Generate caption
    # Verify post-generation checks run
    # Confirm all data logged
    
def test_post_generation_checks_after_failure():
    """Post-checks behavior after generation failure"""
    # Trigger generation failure
    # Verify checks still run
    # Confirm partial data logged
```

---

## Metrics & Monitoring

### Key Metrics
- **Detection Logging Rate**: % of generations with logged detection
- **Parameter Storage Rate**: % of generations with logged parameters
- **Sweet Spot Coverage**: % of materials with sweet spot data
- **Evaluation Success Rate**: % of evaluations using Claude API vs fallback

### Dashboard Queries
```sql
-- Detection logging rate
SELECT 
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM detection_results) as detection_rate
FROM detection_results 
WHERE id IN (SELECT detection_result_id FROM generation_parameters);

-- Sweet spot coverage
SELECT 
    COUNT(DISTINCT material || '/' || component_type) as with_sweet_spot,
    (SELECT COUNT(DISTINCT material || '/' || component_type) FROM detection_results) as total_combos
FROM sweet_spot_recommendations;

-- Evaluation API usage
SELECT 
    has_claude_api,
    COUNT(*) as count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM subjective_evaluations) as percentage
FROM subjective_evaluations
GROUP BY has_claude_api;
```

---

## Related Documentation

- **E2E Requirements**: `docs/system/E2E_SYSTEM_REQUIREMENTS.md` - Requirement #2 (Self-Learning)
- **Integrity Checker**: `processing/integrity/README.md` - Full integrity check documentation
- **Winston Learning**: `docs/winston/WINSTON_LEARNING_SYSTEM.md` - Learning system architecture
- **Database Schema**: `processing/detection/winston_feedback_db.py` - Database structure
- **Sweet Spot**: `docs/system/SWEET_SPOT_RECOMMENDATIONS.md` - Sweet spot calculation

---

## Version History

- **1.0** (November 16, 2025): Initial implementation
  - Added run_post_generation_checks() method
  - Integrated into all generation commands
  - 5 checks: database, detection, parameters, sweet spot, evaluation
