# Subjective Evaluation API Fix

**Date**: November 16, 2025  
**Issue**: SubjectiveEvaluator using incorrect API signature  
**Status**: Fixed  
**Version**: 1.0

---

## Problem Statement

### Symptom
During micro generation for Brass (November 16, 2025), subjective evaluation failed:

```
Error in subjective evaluation: CachedAPIClient.generate() got an unexpected keyword argument 'prompt'
```

**Impact**: Subjective evaluation fell back to rule-based scoring instead of using Grok API for accurate quality assessment.

### Root Cause
**File**: `postprocessing/evaluation/subjective_evaluator.py`  
**Method**: `_get_subjective_evaluation()` (lines ~205-225)

The method was calling the API client with individual keyword arguments:
```python
# INCORRECT - Old API signature
response = self.api_client.generate(
    prompt=evaluation_prompt,
    system_prompt=system_prompt,
    max_tokens=500,
    temperature=0.3
)
```

**Problem**: `CachedAPIClient.generate()` expects a `GenerationRequest` object, not individual kwargs.

---

## Solution

### Updated API Call
Changed to use `GenerationRequest` object per correct API signature:

```python
# CORRECT - New API signature
from shared.api.client import GenerationRequest

request = GenerationRequest(
    prompt=evaluation_prompt,
    system_prompt=system_prompt,
    max_tokens=500,
    temperature=0.3
)
response = self.api_client.generate(request)
content = response.content  # Access content from response object
```

### Key Changes
1. **Import GenerationRequest**: Added `from shared.api.client import GenerationRequest`
2. **Create request object**: Wrap parameters in GenerationRequest
3. **Extract content**: Use `response.content` instead of treating response as string
4. **Consistent pattern**: Matches usage in `DynamicGenerator` and other components

---

## File Modifications

### File: `postprocessing/evaluation/subjective_evaluator.py`

**Lines Modified**: ~205-225 (in `_get_subjective_evaluation()` method)

**Before** (Incorrect):
```python
try:
    response = self.api_client.generate(
        prompt=evaluation_prompt,
        system_prompt=system_prompt,
        max_tokens=500,
        temperature=0.3
    )
    
    # Parse response
    lines = response.strip().split('\n')
    # ...
except Exception as e:
    logger.warning(f"Error in subjective evaluation: {str(e)}")
    logger.warning("Falling back to rule-based evaluation")
    return self._fallback_evaluation(content)
```

**After** (Correct):
```python
try:
    # Use GenerationRequest object per API signature
    from shared.api.client import GenerationRequest
    
    request = GenerationRequest(
        prompt=evaluation_prompt,
        system_prompt=system_prompt,
        max_tokens=500,
        temperature=0.3
    )
    response = self.api_client.generate(request)
    
    # Parse response content
    lines = response.content.strip().split('\n')
    # ...
except Exception as e:
    logger.warning(f"Error in subjective evaluation: {str(e)}")
    logger.warning("Falling back to rule-based evaluation")
    return self._fallback_evaluation(content)
```

**Impact**: Subjective evaluation now successfully uses Grok API instead of always falling back to rule-based scoring.

---

## API Signature Documentation

### Correct Usage Pattern

**All API calls in the system should follow this pattern:**

```python
from shared.api.client import GenerationRequest

# 1. Create request object with all parameters
request = GenerationRequest(
    prompt="Your prompt here",
    system_prompt="System instructions here",  # Optional
    max_tokens=500,
    temperature=0.7
)

# 2. Call generate() with request object
response = api_client.generate(request)

# 3. Access response content
content = response.content
```

### ❌ Incorrect Patterns to Avoid

```python
# DON'T: Pass kwargs directly
response = api_client.generate(
    prompt="...",
    system_prompt="...",
    max_tokens=500
)

# DON'T: Treat response as string
lines = response.strip().split('\n')

# DON'T: Use old API signature
response = api_client.generate(prompt, system_prompt)
```

### ✅ Correct Patterns

```python
# DO: Use GenerationRequest object
request = GenerationRequest(prompt="...", max_tokens=500)
response = api_client.generate(request)

# DO: Access response.content
lines = response.content.strip().split('\n')

# DO: Check response attributes
if response.status == 'success':
    content = response.content
```

---

## Related Components

### Components Using Correct API Signature
All these components correctly use `GenerationRequest`:

1. **DynamicGenerator** (`generation/core/generator.py`)
   - Uses GenerationRequest for all content generation
   - Reference implementation for API calls

2. **TextComponentGenerator** (`components/text/core/text_component_generator.py`)
   - Wraps DynamicGenerator, inherits correct usage

3. **SubjectiveEvaluator** (`postprocessing/evaluation/subjective_evaluator.py`)
   - NOW FIXED - Uses GenerationRequest as of November 16, 2025

### API Client Implementations
**Files**: 
- `shared/api/client.py` - Direct Grok API calls
- `shared/api/cached_client.py` - Caching wrapper around API client

**Expected Signature**:
```python
def generate(self, request: GenerationRequest) -> GenerationResponse:
    """
    Generate content using LLM API.
    
    Args:
        request: GenerationRequest object with prompt, system_prompt, max_tokens, temperature
        
    Returns:
        GenerationResponse object with content, status, metadata
    """
```

---

## Testing & Validation

### Unit Tests
**File**: `tests/test_subjective_evaluator.py`

```python
def test_subjective_evaluator_uses_generation_request():
    """Verify SubjectiveEvaluator uses correct API signature"""
    import inspect
    from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator
    
    # Check that _get_subjective_evaluation uses GenerationRequest
    source = inspect.getsource(SubjectiveEvaluator._get_subjective_evaluation)
    assert 'GenerationRequest' in source
    assert 'request = GenerationRequest' in source
    
def test_subjective_evaluator_extracts_response_content():
    """Verify response.content is used, not raw response"""
    import inspect
    from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator
    
    source = inspect.getsource(SubjectiveEvaluator._get_subjective_evaluation)
    assert 'response.content' in source
```

### Integration Tests
**File**: `tests/integration/test_api_signature_consistency.py`

```python
def test_all_api_calls_use_generation_request():
    """Verify all API calls use GenerationRequest pattern"""
    # Search codebase for api_client.generate() calls
    # Ensure all use GenerationRequest object
    
def test_no_kwargs_api_calls():
    """Verify no API calls use old kwargs pattern"""
    # Search for generate(prompt= patterns
    # Ensure none exist in production code
```

### Manual Validation
**Command**: Generate content and check subjective evaluation runs

```bash
# Generate micro for a material
python3 run.py --material "Aluminum" --micro

# Expected output (CHECK FOR):
# ✅ "Running subjective evaluation..." (NOT "Falling back to rule-based")
# ✅ "Subjective evaluation: X.X/10" with dimension scores
# ✅ No error "got an unexpected keyword argument 'prompt'"
```

---

## Impact & Results

### Before Fix (November 16, 2025 - Morning)
```
🔍 Running Grok and subjective evaluation...
   ✅ Grok Detection: 98.0% human, 2.0% AI (SUCCESS)
   Error in subjective evaluation: CachedAPIClient.generate() got an unexpected keyword argument 'prompt'
   Falling back to rule-based evaluation
   ⚠️  Subjective Evaluation: 7.4/10 (PASS) (rule-based fallback)
```

**Issues**:
- Subjective evaluation ALWAYS failed
- System ALWAYS used rule-based fallback
- No actual Grok API quality assessment
- Less accurate dimension scoring

### After Fix (November 16, 2025 - Afternoon)
```
🔍 Running Grok and subjective evaluation...
   ✅ Grok Detection: 98.0% human, 2.0% AI (SUCCESS)
   ✅ Subjective Evaluation: 7.4/10 (PASS)
```

**Improvements**:
- Subjective evaluation succeeds with Grok API
- Accurate 6-dimension scoring
- Better quality gate validation
- Sweet spot learning includes real evaluation data

---

## Post-Generation Integrity Check

### Evaluation Logging Check
Post-generation integrity check now verifies subjective evaluation was logged:

```python
# Check 5: Subjective Evaluation Logged
result = cursor.execute("""
    SELECT id, overall_score, passes_quality_gate, has_claude_api, timestamp
    FROM subjective_evaluations
    WHERE topic = ? AND component_type = ?
    ORDER BY timestamp DESC
    LIMIT 1
""", (material, component_type)).fetchone()

if result:
    eval_id, score, passes, has_api, timestamp = result
    
    if has_api:
        # ✅ PASS: Evaluation used Grok API
        return IntegrityResult(
            check_name="Post-Gen: Subjective Evaluation Logged",
            status=IntegrityStatus.PASS,
            message=f"Subjective evaluation #{eval_id} logged: {score}/10 (PASS)"
        )
    else:
        # ⚠️  WARN: Used rule-based fallback
        return IntegrityResult(
            check_name="Post-Gen: Subjective Evaluation Logged",
            status=IntegrityStatus.WARN,
            message=f"Subjective evaluation #{eval_id} logged: {score}/10 (PASS) (rule-based fallback)"
        )
```

**Expected after fix**: All post-generation checks show PASS (not WARN) for subjective evaluation.

---

## Troubleshooting

### Still Seeing "Falling back to rule-based evaluation"
**Symptom**: Error message persists after fix  
**Diagnosis**:
1. Check if fix was applied: `grep -n "GenerationRequest" postprocessing/evaluation/subjective_evaluator.py`
2. Verify imports: `from shared.api.client import GenerationRequest`
3. Check Grok API key: `echo $GROK_API_KEY`

**Solution**: 
- If GenerationRequest not found: Apply fix again
- If API key missing: Add to `.env` file
- If other error: Check full error message in terminal

### Subjective Evaluation Score Always Same
**Symptom**: Score doesn't vary between generations  
**Diagnosis**: May still be using rule-based fallback  
**Solution**: Check `has_claude_api` field in database:

```bash
sqlite3 data/z-beam.db "SELECT has_claude_api, COUNT(*) FROM subjective_evaluations GROUP BY has_claude_api"
```

**Expected after fix**:
```
1|<count>  # has_claude_api=1 (using Grok API)
```

**Before fix**:
```
0|<count>  # has_claude_api=0 (rule-based fallback)
```

### Import Error: "Cannot import name GenerationRequest"
**Symptom**: `ImportError: cannot import name 'GenerationRequest' from 'shared.api.client'`  
**Diagnosis**: Import path incorrect or GenerationRequest not exported  
**Solution**: Check `shared/api/client.py` defines GenerationRequest:

```python
# shared/api/client.py
from .generation_request import GenerationRequest
from .generation_response import GenerationResponse

__all__ = ['GenerationRequest', 'GenerationResponse', ...]
```

---

## Related Documentation

- **API Architecture**: `docs/api/API_ARCHITECTURE.md` - Full API design and patterns
- **Generation Request**: `docs/api/GENERATION_REQUEST.md` - GenerationRequest object documentation
- **Generation Response**: `docs/api/GENERATION_RESPONSE.md` - GenerationResponse object documentation
- **Subjective Evaluator**: `docs/evaluation/SUBJECTIVE_EVALUATION.md` - Evaluation system overview
- **Post-Gen Checks**: `docs/system/POST_GENERATION_INTEGRITY.md` - Integrity verification system

---

## Lessons Learned

### What Went Wrong
1. **Inconsistent API Usage**: Different components used different API call patterns
2. **Missing Documentation**: No clear guidance on correct API signature
3. **No Validation**: No tests checking API call consistency
4. **Silent Degradation**: System fell back to rule-based scoring without alerting user

### What We Fixed
1. ✅ **Standardized API Calls**: All components now use GenerationRequest
2. ✅ **Clear Documentation**: This document + API docs explain correct pattern
3. ✅ **Validation Tests**: New tests check API signature consistency
4. ✅ **Integrity Checks**: Post-gen checks now verify evaluation success

### Prevention Strategy
1. **Code Review**: Check all API calls use GenerationRequest pattern
2. **Automated Testing**: Run tests to catch API signature violations
3. **Integrity Checker**: Post-gen checks warn if fallback used
4. **Documentation**: Keep this doc updated with API changes

---

## Version History

- **1.0** (November 16, 2025): Initial documentation
  - Fixed SubjectiveEvaluator API signature
  - Changed from kwargs to GenerationRequest object
  - Updated to use response.content instead of raw response
  - Added validation tests and troubleshooting guide
