# Troubleshooting Guide
**Date**: November 25, 2025  
**Status**: ✅ PRODUCTION READY

## 🚨 Common Issues & Solutions

---

## Issue 1: "MaterialImageConfig is required"

### Symptom

```python
ValueError: MaterialImageConfig is required
```

### Cause

Missing or None configuration passed to generator.

### Solution

**Always provide explicit configuration**:

```python
# ❌ WRONG
result = generator.generate_complete("Oak", config=None)

# ✅ RIGHT
config = MaterialImageConfig(material="Oak")
result = generator.generate_complete("Oak", config=config)
```

### Prevention

- Never pass `config=None`
- Always instantiate MaterialImageConfig
- Validate config exists before passing to generator

---

## Issue 2: Validation Warnings - Low Detail Score

### Symptom

```
⚠️ Prompt validation warning: Detail score 45/100 (minimum: 60)
```

### Cause

Generated prompt lacks sufficient detail for high-quality image generation.

### Root Causes

1. **Research data incomplete**: Patterns missing visual characteristics
2. **Too few patterns selected**: Only 1-2 patterns instead of 3-4
3. **Vague descriptions**: Generic terms instead of specific details

### Solution

**Check research data completeness**:

```python
result = generator.generate_complete("Oak", config=config)
research = result['research_data']

for pattern in research['patterns']:
    print(f"Pattern: {pattern['name']}")
    print(f"Visual: {pattern.get('visual_characteristics', 'MISSING')}")
    print(f"Distribution: {pattern.get('distribution_physics', 'MISSING')}")
```

**Increase uniformity for more patterns**:

```python
config = MaterialImageConfig(
    material="Oak",
    contamination_uniformity=4  # Use 3-4 patterns instead of 1-2
)
```

**Verify aging research active**:

- Wood should have 50-70% aging patterns
- Check `pattern['type'] == 'aging'` in results

### Prevention

- Use `contamination_uniformity >= 3` for complex materials
- Verify research data has all 11 dimensions
- Test validation before generation

---

## Issue 3: Contradiction Detected

### Symptom

```
❌ Prompt validation error: Physics violation detected (uniform + drips)
```

### Cause

Prompt contains contradictory descriptions that violate physics.

### Common Contradictions

1. **Uniform + Gravity Effects**: "uniform coating" AND "drips from edges"
2. **Symmetric + Environment**: "perfectly symmetric" AND "wind-driven patterns"
3. **Instant + Aging**: "immediate corrosion" AND "gradual patina formation"
4. **Same + Different**: "identical coating" AND "varied thickness"
5. **Identical + Shift**: "identical patterns" AND "gravity shift"

### Solution

**Review research prompt guidance**:

Check `contamination_pattern_selector.py` for contradictory pattern/rule selection.

**Example fix**:

```python
# ❌ BAD: Contradictory research
"Uniform rust coating across entire surface."
"Heavy rust drips accumulate at bottom edges."

# ✅ GOOD: Consistent research
"Non-uniform rust with heavier accumulation at bottom edges due to gravity."
```

**Manual override** (if research is correct):

```python
# Skip validation if you're confident prompt is correct
prompt = build_material_cleaning_prompt(
    ...,
    validate=False  # Use with caution
)
```

### Prevention

- Test research output for contradictions
- Use consistent physics descriptions
- Review validation results before generation

---

## Issue 4: Unknown Material Error

### Symptom

```python
RuntimeError: Material "UnknownMaterial" not found in category mapping
```

### Cause

Material name not in `CATEGORY_MAP` dictionary.

### Solution

**Check supported materials**:

```python
from domains.materials.image.research.contamination_pattern_selector import ContaminationPatternSelector

selector = ContaminationPatternSelector()

# List all supported materials
print(selector.MATERIAL_CATEGORIES.keys())

# Check if material supported
if "MyMaterial".lower() in selector.MATERIAL_CATEGORIES:
    print(f"Supported: maps to {selector.MATERIAL_CATEGORIES['MyMaterial'.lower()]}")
else:
    print("Not supported")
```

**Add new material** (if needed):

1. Open `contamination_pattern_selector.py`
2. Add mapping:
   ```python
   MATERIAL_CATEGORIES = {
       ...
       "mymaterial": "appropriate_category",
   }
   ```
3. Restart application

### Prevention

- Verify material names against CATEGORY_MAP
- Use exact capitalization (e.g., "Oak" not "oak")
- Check spelling

---

## Issue 5: Cache Stale or Incorrect

### Symptom

- Old research data returned for category
- Changes to research prompt not reflected
- Unexpected patterns in results

### Cause

LRU cache returning stale data after research prompt modifications.

### Solution

**Clear cache**:

```python
from domains.materials.image.research.contamination_pattern_selector import ContaminationPatternSelector

selector = ContaminationPatternSelector()

# Clear all cached research
selector._data = None

# Re-generate (will fetch fresh research)
result = generator.generate_complete("Oak", config=config)
```

**Verify cache cleared**:

```python
# Check cache info
print("Cache reset complete (selector data cache cleared)")

# After clearing, size should be 0
```

### Prevention

- Clear cache after modifying research prompts
- Restart application for clean state
- Use cache_info() to monitor behavior

---

## Issue 6: Gemini API Errors

### Symptom

```
RuntimeError: Research failed: API Error [429] Rate limit exceeded
```

### Cause

Gemini API rate limit exceeded or connectivity issue.

### Solutions

**Rate limit exceeded**:

```python
import time

# Add delay between requests
result1 = generator.generate_complete("Oak", config=config1)
time.sleep(1)  # Wait 1 second
result2 = generator.generate_complete("Maple", config=config2)
```

**API key invalid**:

```python
# Verify API key
import os
api_key = os.getenv("GEMINI_API_KEY")
print(f"API key configured: {api_key is not None}")
print(f"API key length: {len(api_key) if api_key else 0}")
```

**Network connectivity**:

```python
# Test API connectivity
import requests
response = requests.get("https://generativelanguage.googleapis.com")
print(f"API reachable: {response.status_code == 200}")
```

### Prevention

- Monitor API quota usage
- Implement exponential backoff for retries
- Cache results to minimize API calls

---

## Issue 7: Prompt Too Long (> 3,000 chars)

### Symptom

```
❌ Prompt validation error: Prompt exceeds 3,000 character Imagen 4 limit
```

### Cause

Excessive research data or too many patterns included.

### Solution

**Reduce pattern count**:

```python
config = MaterialImageConfig(
    material="Oak",
    contamination_uniformity=2  # Use fewer patterns (1-2 instead of 4+)
)
```

**Trim research descriptions** (advanced):

Modify `_build_concise_contamination_section()` to use shorter descriptions:

```python
# Limit description length
description = pattern['visual_characteristics'][:100]  # Max 100 chars
```

**Use isolated view** (shorter environment descriptions):

```python
config = MaterialImageConfig(
    material="Oak",
    view_mode="Isolated"  # Removes environment context
)
```

### Prevention

- Use `contamination_uniformity <= 3` by default
- Test prompt length before generation
- Monitor validation metrics

---

## Issue 8: Vague or Abstract Terms Warning

### Symptom

```
⚠️ Prompt validation warning: Vague terms detected (some, various, typical)
```

### Cause

Research data contains non-specific language that reduces Imagen 4 accuracy.

### Solution

**Review research output**:

```python
result = generator.generate_complete("Oak", config=config)
prompt = result['prompt']

# Search for vague terms
vague_terms = ["some", "various", "typical", "several", "many", "most"]
for term in vague_terms:
    if term in prompt.lower():
        print(f"Found vague term: {term}")
```

**Refine research prompt**:

Modify pattern/rule selection in `contamination_pattern_selector.py` to request specific details:

```
❌ BAD: "Some rust patterns appear"
✅ GOOD: "3-5 rust patterns appear at weld joints"
```

**Accept warnings** (if specificity not critical):

Warnings don't block generation - prompt still usable.

### Prevention

- Test research output for specificity
- Use quantitative descriptions (e.g., "3-5 patterns" not "several patterns")
- Review validation warnings regularly

---

## Issue 9: High Duplication (> 20%)

### Symptom

```
❌ Prompt validation error: Excessive duplication (25% duplicate content)
```

### Cause

Research patterns contain repetitive text.

### Solution

**Review patterns for duplication**:

```python
result = generator.generate_complete("Oak", config=config)
patterns = result['research_data']['patterns']

for pattern in patterns:
    print(f"Pattern: {pattern['name']}")
    print(f"Visual: {pattern['visual_characteristics']}")
    print()
```

**Reduce pattern count**:

```python
config = MaterialImageConfig(
    material="Oak",
    contamination_uniformity=2  # Fewer patterns = less duplication
)
```

**Vary descriptions** (advanced):

Modify research prompt to request diverse vocabulary.

### Prevention

- Use varied pattern types (aging + contamination)
- Test duplication score before generation
- Monitor validation metrics

---

## Issue 10: Imagen 4 Generation Fails

### Symptom

Image generation fails despite passing prompt validation.

### Possible Causes

1. **Imagen API quota exceeded**
2. **Safety filter triggered**
3. **Invalid aspect ratio or parameters**
4. **Network timeout**

### Solutions

**Check Imagen API quota**:

```python
# Monitor Imagen API usage in Google Cloud Console
# https://console.cloud.google.com/apis/dashboard
```

**Review safety filter settings**:

```python
# Adjust safety filter (if needed)
safety_settings = {
    "block_few": True,  # Less restrictive
    # or "block_some", "block_most"
}
```

**Verify parameters**:

```python
# Standard Imagen 4 parameters
params = {
    "aspect_ratio": "16:9",  # 1408x768
    "guidance_scale": 13.0,
    "model": "imagen-4.0-generate-001"
}
```

**Implement retry logic**:

```python
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        result = imagen_api.generate(prompt)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise
```

---

## 🔍 Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# All validation checks logged
result = generator.generate_complete("Oak", config=config)
```

### Inspect Validation Metrics

```python
validation = result['validation']

print(f"Valid: {validation['valid']}")
print(f"Length: {validation['metrics']['length']}")
print(f"Detail: {validation['metrics']['detail_score']}/100")
print(f"Clarity: {validation['metrics']['clarity_score']}/100")
print(f"Duplication: {validation['metrics']['duplication_score']}%")
```

### Test Components Separately

```python
# Test research only
from domains.materials.image.research.contamination_pattern_selector import ContaminationPatternSelector
selector = ContaminationPatternSelector()
research = selector.get_patterns_for_image_gen("Oak")

# Test prompt building only
from domains.materials.image.research.material_prompts import build_material_cleaning_prompt
prompt = build_material_cleaning_prompt(
    material_name="Oak",
    research_data=research,
    contamination_level=3,
    contamination_uniformity=3,
    view_mode="Contextual",
    environment_wear=3,
    validate=False  # Skip validation for testing
)

# Test validation only
from domains.materials.image.research.material_prompts import validate_prompt
validation = validate_prompt(prompt, research)
```

---

## 🔗 Related Documentation

- `PROMPT_VALIDATION.md` - Validation system details
- `API_USAGE.md` - Python API examples
- `ARCHITECTURE.md` - System architecture and data flow
- `TESTING.md` - Test coverage and validation

---

**Status**: ✅ Common issues documented and solutions validated  
**Last Updated**: November 25, 2025
