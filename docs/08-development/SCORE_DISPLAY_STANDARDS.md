# Score Display Standards

**Purpose**: Prevent score inversion bugs and ensure consistent score representation  
**Date**: November 17, 2025  
**Status**: ✅ Enforced via `shared/validation/score_validator.py`

---

## 🎯 The Problem

**Score inversions** occur when displaying the wrong score type or scale:

### Historical Examples:

**Example 1: Test Script Display (Nov 17, 2025)**
```python
# WRONG - Displayed ai_score as "human score"
winston = result.get('ai_score', 'N/A')  # Gets 0.05
print(f"Winston: {winston:.1f}% human")   # Shows "0.1% human" ❌

# CORRECT - Display human_score
human = result.get('human_score', 0.0)    # Gets 95.0
print(f"Winston: {human:.1f}% human")     # Shows "95.0% human" ✅
```

**Impact**: User sees "0% success" when actually 95% successful

**Example 2: API Response Handling**
```python
# Winston API returns
{
    'score': 95.0,        # Human score (0-100)
    'ai_score': 0.05      # AI score (0-1.0)
}

# WRONG - Using wrong field
display_score = response['ai_score']      # 0.05
print(f"{display_score}% human")          # Shows "0.05% human" ❌

# CORRECT - Use human score
display_score = response['score']         # 95.0
print(f"{display_score:.1f}% human")     # Shows "95.0% human" ✅
```

---

## 📏 Standard Score Scales

### Winston Detection Scores

| Score Type | Range | Meaning | Display Format |
|------------|-------|---------|----------------|
| `human_score` | 0-100 | Percentage human-written | `{score:.1f}% human` |
| `ai_score` | 0.0-1.0 | Probability AI-generated | Internal only, don't display |

**Conversion:**
```python
ai_score = (100 - human_score) / 100.0
human_score = (1.0 - ai_score) * 100.0
```

### Subjective Evaluation Scores

| Score Type | Range | Meaning | Display Format |
|------------|-------|---------|----------------|
| `overall_score` | 0-10 | Overall quality rating | `{score:.1f}/10` |
| `clarity_score` | 0-10 | Clarity dimension | `{score:.1f}/10` |
| `human_likeness_score` | 0-10 | Human-like writing | `{score:.1f}/10` |
| (other dimensions) | 0-10 | Various dimensions | `{score:.1f}/10` |

### Composite Scores (Future)

| Score Type | Range | Meaning | Display Format |
|------------|-------|---------|----------------|
| `composite_quality` | 0-100 | Winston (60%) + Subjective (30%) + Readability (10%) | `{score:.1f}/100` |

---

## ✅ Validation Rules

### Enforced by `@validate_scores` Decorator

**1. Range Validation**
```python
# human_score must be 0-100
if not (0 <= human_score <= 100):
    raise ScoreValidationError("Invalid human_score: {score}")

# ai_score must be 0-1.0
if not (0 <= ai_score <= 1.0):
    raise ScoreValidationError("Invalid ai_score: {score}")

# subjective scores must be 0-10
if not (0 <= overall_score <= 10):
    raise ScoreValidationError("Invalid overall_score: {score}")
```

**2. Consistency Validation**
```python
# If both present, they must be inverses
expected_ai = (100 - human_score) / 100.0
if abs(ai_score - expected_ai) > 0.01:
    raise ScoreValidationError(
        f"Score mismatch: human={human_score}% but ai={ai_score:.3f}"
    )
```

**3. Type Validation**
```python
# All scores must be numeric
if not isinstance(score, (int, float)):
    raise ScoreValidationError(
        f"Score must be numeric, got {type(score).__name__}"
    )
```

---

## 🔧 Implementation Standards

### 1. Function Return Values

**ALWAYS return human_score for display:**

```python
@validate_scores
def generate(self, identifier, component_type):
    # ... generation logic ...
    
    winston_response = api.detect(text)
    
    return {
        'success': True,
        'human_score': winston_response['score'],  # 0-100 scale ✅
        'ai_score': winston_response['ai_score'],  # 0-1.0 scale (internal)
        'text': text
    }
```

**NEVER return only ai_score for display:**

```python
# WRONG - Requires conversion by caller
return {
    'success': True,
    'ai_score': 0.05  # Caller must convert ❌
}

# CORRECT - Both scores provided
return {
    'success': True,
    'human_score': 95.0,   # Ready for display ✅
    'ai_score': 0.05       # For internal logic ✅
}
```

### 2. Display Formatting

**User-Facing Displays:**

```python
# Winston scores - ALWAYS show human_score
print(f"✅ SUCCESS: {result['human_score']:.1f}% human")
print(f"Winston Detection: {result['human_score']:.1f}% human-written")

# Subjective scores - Use 0-10 scale
print(f"Overall Quality: {result['overall_score']:.1f}/10")
print(f"Clarity: {result['clarity_score']:.1f}/10")
```

**Internal Logic:**

```python
# Use ai_score for thresholds
if result['ai_score'] <= 0.30:  # 70% human threshold
    print("Passes acceptance threshold")

# Or use human_score
if result['human_score'] >= 70:
    print("Passes acceptance threshold")
```

### 3. Test Script Requirements

**All test scripts MUST:**

1. **Display human_score** (not ai_score)
2. **Convert if needed** before display
3. **Validate score ranges** in assertions

```python
# Test script example
def test_generation():
    result = orchestrator.generate("TestMaterial", "caption")
    
    # Get human_score for display
    if 'human_score' in result:
        human = result['human_score']
    elif 'ai_score' in result:
        # Convert if only ai_score present
        human = (1.0 - result['ai_score']) * 100.0
    else:
        human = 'N/A'
    
    # Display correctly
    print(f"Winston: {human:.1f}% human")
    
    # Validate range
    if isinstance(human, (int, float)):
        assert 0 <= human <= 100, f"Invalid human_score: {human}"
```

### 4. Database Storage

**Store BOTH scores:**

```sql
CREATE TABLE detection_results (
    id INTEGER PRIMARY KEY,
    human_score REAL NOT NULL,  -- 0-100 scale for display
    ai_score REAL NOT NULL,     -- 0-1.0 scale for logic
    -- ... other columns
);
```

**Query patterns:**

```python
# For display - use human_score
cursor.execute("""
    SELECT material, human_score
    FROM detection_results
    WHERE success = 1
    ORDER BY human_score DESC
""")

# For logic - use ai_score
cursor.execute("""
    SELECT material, ai_score
    FROM detection_results
    WHERE ai_score <= 0.30  -- 70% human threshold
    ORDER BY ai_score ASC
""")
```

---

## 🧪 Testing Standards

### Unit Tests for Score Validation

**File**: `tests/test_score_validation.py`

```python
import pytest
from shared.validation.score_validator import (
    validate_scores,
    ScoreValidationError,
    convert_ai_to_human_score,
    convert_human_to_ai_score
)

def test_valid_scores():
    """Valid scores should pass"""
    @validate_scores
    def mock_generate():
        return {
            'success': True,
            'human_score': 95.0,
            'ai_score': 0.05
        }
    
    result = mock_generate()
    assert result['human_score'] == 95.0

def test_inverted_scores_detected():
    """Score inversion should raise error"""
    @validate_scores
    def mock_generate():
        return {
            'success': True,
            'human_score': 95.0,
            'ai_score': 0.95  # WRONG - Should be 0.05
        }
    
    with pytest.raises(ScoreValidationError, match="Score mismatch"):
        mock_generate()

def test_out_of_range_human_score():
    """Out of range human_score should raise error"""
    @validate_scores
    def mock_generate():
        return {
            'success': True,
            'human_score': 150.0  # Out of range
        }
    
    with pytest.raises(ScoreValidationError, match="Invalid human_score"):
        mock_generate()

def test_score_conversion():
    """Score conversion should be accurate"""
    # AI to human
    human = convert_ai_to_human_score(0.05)
    assert human == 95.0
    
    # Human to AI
    ai = convert_human_to_ai_score(95.0)
    assert ai == 0.05
```

### Integration Tests

**File**: `tests/test_score_consistency.py`

```python
def test_unified_orchestrator_scores():
    """UnifiedOrchestrator should return valid scores"""
    orchestrator = UnifiedOrchestrator(api_client=test_client)
    result = orchestrator.generate("TestMaterial", "caption")
    
    # Should have human_score
    assert 'human_score' in result
    assert 0 <= result['human_score'] <= 100
    
    # Should have ai_score
    assert 'ai_score' in result
    assert 0 <= result['ai_score'] <= 1.0
    
    # Should be consistent
    expected_ai = (100 - result['human_score']) / 100.0
    assert abs(result['ai_score'] - expected_ai) < 0.01

def test_winston_api_response():
    """Winston API response should have correct format"""
    client = APIClientFactory.create_client('winston')
    response = client.detect_ai("Test content")
    
    # Should have human score (0-100)
    assert 'human_score' in response
    assert 0 <= response['human_score'] <= 100
    
    # Should have ai_score (0-1.0)
    assert 'ai_score' in response
    assert 0 <= response['ai_score'] <= 1.0
```

---

## 🚨 Common Mistakes to Avoid

### Mistake 1: Displaying ai_score as percentage

```python
# WRONG
print(f"Winston: {ai_score}% human")  # Shows 0.05% ❌

# CORRECT
print(f"Winston: {human_score:.1f}% human")  # Shows 95.0% ✅
```

### Mistake 2: Using wrong scale for logic

```python
# WRONG - Comparing different scales
if human_score <= 0.30:  # Comparing 95 to 0.30 ❌
    print("Fails threshold")

# CORRECT - Use ai_score for 0-1.0 thresholds
if ai_score <= 0.30:  # Comparing 0.05 to 0.30 ✅
    print("Passes threshold")

# OR - Use human_score with 0-100 threshold
if human_score >= 70:  # Comparing 95 to 70 ✅
    print("Passes threshold")
```

### Mistake 3: Not validating before display

```python
# WRONG - No validation
def generate():
    return {'human_score': 150.0}  # Invalid, but no error ❌

# CORRECT - Decorator validates
@validate_scores
def generate():
    return {'human_score': 150.0}  # Raises ScoreValidationError ✅
```

### Mistake 4: Assuming scores are always present

```python
# WRONG - Assumes human_score exists
score = result['human_score']  # KeyError if missing ❌
print(f"{score}% human")

# CORRECT - Handle missing scores
score = result.get('human_score', 'N/A')
if isinstance(score, (int, float)):
    print(f"{score:.1f}% human")
else:
    print(f"Score: {score}")
```

---

## 📖 Quick Reference

### Score Type Cheat Sheet

```python
# DISPLAY TO USER
human_score: 95.0    →  "95.0% human"
overall_score: 8.5   →  "8.5/10"

# INTERNAL LOGIC
ai_score: 0.05       →  if ai_score <= 0.30: pass
ai_threshold: 0.30   →  70% human threshold

# CONVERSIONS
ai_score = (100 - human_score) / 100.0
human_score = (1.0 - ai_score) * 100.0
```

### When to Use Which Score

| Use Case | Use This Score | Format |
|----------|----------------|--------|
| Display to user | `human_score` | `{score:.1f}% human` |
| Display quality rating | `overall_score` | `{score:.1f}/10` |
| Threshold comparison (0-1.0) | `ai_score` | `if ai_score <= 0.30:` |
| Threshold comparison (0-100) | `human_score` | `if human_score >= 70:` |
| Database queries (sorting best) | `human_score DESC` | Higher is better |
| Database queries (sorting best) | `ai_score ASC` | Lower is better |

---

## 🎯 Summary

**Golden Rules:**
1. ✅ **Always display human_score** (0-100) to users
2. ✅ **Store both scores** in database
3. ✅ **Use @validate_scores** on all generation functions
4. ✅ **Convert before display** if only ai_score available
5. ✅ **Test score consistency** in integration tests
6. ❌ **Never display ai_score** as percentage
7. ❌ **Never mix scales** in comparisons

**Enforcement**: Runtime validation via `@validate_scores` decorator catches inversions before they reach users.
