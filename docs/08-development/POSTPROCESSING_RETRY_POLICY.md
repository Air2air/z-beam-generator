# Postprocessing Retry-Until-Requirements-Met Policy

**Status**: 🔥 MANDATORY (December 14, 2025)  
**Grade**: Policy violation = Grade F  
**Enforcement**: Automated tests in `tests/test_postprocessing_retry_policy.py`

---

## 🎯 Policy Statement

**The postprocessing system MUST retry content regeneration until quality requirements are met OR maximum attempts are exhausted.**

Single-attempt regeneration that gives up when quality is still poor is **Grade F policy violation**.

---

## 📋 Requirements

### 1. Maximum Attempts
- **Constant**: `MAX_REGENERATION_ATTEMPTS = 5`
- **Location**: `shared/commands/postprocess.py`
- **Behavior**: System tries up to 5 times to generate acceptable content

### 2. Stop Conditions (Either Triggers Stop)
- ✅ **Requirements Met**: Quality score ≥ threshold AND readability pass AND zero AI patterns
- ✅ **Max Attempts Exhausted**: Tried `MAX_REGENERATION_ATTEMPTS` times

### 3. Best Version Tracking
- System tracks quality score for each attempt
- If all attempts fail, returns **highest quality version** (not last attempt)
- Result dict includes `best_quality_score` field

### 4. Attempt Reporting
- Result dict must include `attempts` field showing how many tries were made
- Terminal output shows attempt number during processing

---

## 🔍 Quality Requirements (All Must Pass)

For an attempt to be considered "requirements met":

```python
requirements_met = (
    readability.get('status') == 'pass' AND
    len(ai_patterns) == 0 AND
    quality_score >= QUALITY_THRESHOLD (60/100)
)
```

---

## 📊 Implementation Example

```python
# CORRECT: Retry loop until requirements met
best_quality_score = 0
best_content = None

for attempt in range(1, MAX_REGENERATION_ATTEMPTS + 1):
    result = generator.generate(item_name, component_type)
    
    quality_score = evaluate_quality(result.content)
    
    # Track best
    if quality_score > best_quality_score:
        best_quality_score = quality_score
        best_content = result.content
    
    # Check if requirements met
    if meets_all_requirements(result.content, quality_score):
        print(f"✅ REQUIREMENTS MET on attempt {attempt}!")
        break
    else:
        print(f"⚠️ Attempt {attempt} below threshold, retrying...")

return best_content
```

```python
# WRONG: Single attempt then give up
result = generator.generate(item_name, component_type)

if quality_score < threshold:
    print("⚠️ No improvement, keeping original")  # ❌ POLICY VIOLATION
    return original
```

---

## 🧪 Test Requirements

All implementations must pass these tests:

### Test 1: Stops When Requirements Met
- **Given**: Attempts 1-2 fail, attempt 3 passes
- **Expected**: Stops at attempt 3, reports `attempts=3`
- **Test**: `test_retries_until_requirements_met()`

### Test 2: Exhausts All Attempts
- **Given**: All 5 attempts fail quality checks
- **Expected**: Tries all 5, reports `attempts=5`
- **Test**: `test_exhausts_all_attempts_when_requirements_never_met()`

### Test 3: Tracks Best Version
- **Given**: 5 attempts with scores [45, 50, 58, 52, 48]
- **Expected**: Returns attempt 3 (score 58), includes `best_quality_score=58`
- **Test**: `test_tracks_best_version_across_attempts()`

### Test 4: Policy Documented
- **Expected**: Module docstring mentions "MANDATORY RETRY POLICY"
- **Test**: `test_policy_documented_in_module_docstring()`

---

## 📖 Result Dictionary Schema

Successful regeneration result:

```python
{
    'item': 'gasket-material',
    'field': 'description',
    'action': 'REGENERATED',
    'improved': True,  # or False
    'attempts': 3,  # How many tries before success/giving up
    'best_quality_score': 75,  # Highest score achieved
    'old_quality': {
        'readability': 'fail',
        'ai_patterns': 3
    },
    'new_quality': {
        'readability': 'pass',
        'ai_patterns': 0
    }
}
```

Failed after exhausting attempts:

```python
{
    'item': 'gasket-material',
    'field': 'description',
    'action': 'REGENERATED',  # Still saved best version
    'improved': False,  # Never met threshold
    'attempts': 5,  # Used all attempts
    'best_quality_score': 58,  # Best achieved (below 60 threshold)
    ...
}
```

---

## 🚨 Anti-Patterns (Grade F Violations)

### ❌ Single Attempt Then Give Up
```python
result = generator.generate(...)
if result.quality < threshold:
    return keep_original()  # VIOLATION: Didn't retry
```

### ❌ Not Tracking Best Version
```python
for attempt in range(5):
    result = generator.generate(...)
    # VIOLATION: No tracking of best version
    if result.quality >= threshold:
        return result

return last_result  # VIOLATION: Should return BEST, not LAST
```

### ❌ No Attempt Count Reporting
```python
return {
    'improved': False,
    # VIOLATION: Missing 'attempts' field
}
```

---

## 🎯 Rationale

**Problem**: Previous implementation tried once, saw no improvement, and gave up. This meant low-quality content stayed in system despite multiple generation attempts being available.

**Solution**: Mandatory retry loop ensures system makes every reasonable effort to meet quality requirements before accepting defeat.

**Benefits**:
1. Higher success rate - multiple chances to generate good content
2. Better quality - keeps best version even if none are perfect
3. Transparency - users see how many attempts were made
4. Deterministic - clear max attempts prevent infinite loops

---

## 🎓 Learning Integration (December 14, 2025)

**CRITICAL**: All retry attempts MUST be logged to learning database with session tracking.

### Session Tracking Requirements

1. **Generate Session ID**: Create unique UUID at start of retry loop
   ```python
   retry_session_id = str(uuid.uuid4())
   ```

2. **Pass to Generator**: Include in all `generate()` calls
   ```python
   result = generator.generate(
       material_name=item,
       component_type=field,
       retry_session_id=retry_session_id,
       is_retry=(attempt > 1)
   )
   ```

3. **Database Fields**: Learning database must track:
   - `retry_session_id` - Groups all attempts from same session
   - `is_retry` - Marks retry attempts (False for attempt 1, True for 2+)

### Learning Analysis Enabled

With retry tracking, the system can now:
- Calculate success rate by attempt number
- Analyze parameter drift (temp 0.7 → 0.85 → 1.0)
- Track quality progression within session
- Learn optimal retry strategies from historical data
- Identify which parameters correlate with retry success

**Implementation**: See `RETRY_LEARNING_INTEGRATION_DEC14_2025.md`

---

## 📚 Related Policies

- **Core Principle #0**: Universal Text Processing Pipeline
- **Data Storage Policy**: Dual-write requirement (save to data + frontmatter)
- **Quality Gates**: Winston 69%+, Realism 7.0+, Readability pass
- **Voice Pattern Compliance**: Author-specific linguistic patterns
- **Learning Integration**: Retry session tracking for analysis (Dec 14, 2025)

---

## ✅ Compliance Checklist

Before claiming postprocessing is complete:

- [ ] `MAX_REGENERATION_ATTEMPTS` constant defined (value: 5)
- [ ] Retry loop implemented (for attempt in range...)
- [ ] Best version tracking (best_quality_score variable)
- [ ] Stop condition: requirements met OR max attempts
- [ ] Result includes `attempts` field
- [ ] Result includes `best_quality_score` field
- [ ] All 4 tests passing in `test_postprocessing_retry_policy.py`
- [ ] Module docstring mentions "MANDATORY RETRY POLICY"
- [ ] Terminal output shows attempt numbers
- [ ] **Learning Integration** (Dec 14, 2025):
  - [ ] Session ID generated (uuid.uuid4())
  - [ ] Session ID passed to all generate() calls
  - [ ] is_retry flag set correctly (False for attempt 1, True for 2+)
  - [ ] Database tracks retry_session_id and is_retry
  - [ ] All attempts logged (not overwritten)
  - [ ] Tests passing in `test_retry_learning_integration.py`

---

**Grade**: Mandatory compliance - violations = Grade F
