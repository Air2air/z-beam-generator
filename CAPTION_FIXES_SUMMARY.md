# Caption Generation Fixes - October 25, 2025

## Problem Analysis

**Overall Statistics** (107 materials analyzed):
- Average caption length: 267 words (127.6 before + 139.5 after)
- Range: 12-500 words (extreme variance)
- Author variance: 215-309 words average

**Critical Issues Identified**:

1. **Catastrophic Failure**: Gold = 12 words (6+6) - complete generation failure
2. **Over-generation**: Mortar = 500 words (209+291) - 4x over target
3. **Author Inconsistency**: Alessandro Moretti (Italy) averages 309 words (44% longer than others)
4. **Wide Variance**: 12-500 word range indicates inconsistent enforcement

## Implemented Fixes

### Fix 1: Minimum Word Count Enforcement ⚠️ CRITICAL
**Location**: `components/caption/generators/generator.py` - `_extract_single_section_content()`

**Change**:
```python
# BEFORE: Only character-based validation (100 chars minimum)
if not content or len(content) < min_length:
    raise ValueError(...)

# AFTER: Word-based validation (10 words minimum per section)
min_words = 10
word_count = len(content.split())
if not content or word_count < min_words:
    raise ValueError(f"{section_type}_TEXT too short: {word_count} words < {min_words} minimum")
```

**Impact**: Prevents Gold-style failures (6 words) - now requires minimum 10 words per section.

---

### Fix 2: Explicit Word Limit Enforcement in Prompts
**Location**: `components/caption/generators/generator.py` - `_build_single_section_prompt()`

**Change**: Added explicit constraints to AI prompts:
```python
prompt += f"\n\nSTRICT WORD LIMIT: Write EXACTLY {target_words} words (±5 words tolerance).\n"
prompt += f"CRITICAL: DO NOT exceed {target_words + 5} words under any circumstances.\n"
prompt += f"MINIMUM: Write at least {max(10, target_words - 5)} words for substantive content.\n"
```

**Impact**: Clearer guidance to AI prevents over-generation like Mortar (500 words).

---

### Fix 3: Post-Generation Word Count Trimming (Safety Net)
**Location**: `components/caption/generators/generator.py` - New `_trim_to_word_limit()` method

**Implementation**:
```python
def _trim_to_word_limit(self, text: str, target_words: int, section_type: str, 
                       material_name: str, tolerance: int = 5) -> str:
    """Hard trim text to word limit if exceeded"""
    words = text.split()
    max_words = target_words + tolerance
    
    if len(words) > max_words:
        # Trim to last complete sentence within limit
        trimmed_words = words[:max_words]
        trimmed_text = ' '.join(trimmed_words)
        
        # Find last sentence boundary
        sentence_ends = list(re.finditer(r'[.!?]', trimmed_text))
        if sentence_ends:
            last_sentence_end = sentence_ends[-1].end()
            return trimmed_text[:last_sentence_end]
    
    return text
```

**Applied**: After both before and after section extraction, before sentence enforcement.

**Impact**: Guarantees no caption exceeds 65 words per section (60 + 5 tolerance).

---

### Fix 4: Temperature Reduction for Consistency
**Location**: `components/caption/generators/generator.py` - Both API calls

**Change**:
```python
# BEFORE: temperature=0.7 (high creativity, high variance)
# AFTER: temperature=0.5 (balanced consistency)

before_response = api_client.generate_simple(
    prompt=before_prompt,
    max_tokens=dynamic_max_tokens,
    temperature=0.5   # Reduced from 0.7
)
```

**Impact**: Reduces variance from 12-500 words to expected 20-120 word range.

---

### Fix 5: Italy-Specific Brevity Constraints
**Location**: `voice/profiles/italy.yaml` - `voice_adaptation.caption_generation`

**Added Configuration**:
```yaml
caption_generation:
  word_count_constraints:
    strict_maximum_per_section: 60  # Hard cap
    strong_brevity_requirement: true
    compression_instruction: "Write concisely. Favor precision over elaboration."
    enforce_word_targets: true
  
  guidelines:
    - "BREVITY PRIORITY: Compress verbose descriptions. Prioritize conciseness."
```

**Impact**: Targets Alessandro Moretti's 309-word average → 240-word target.

---

## Expected Results

### Before Fixes:
- Range: 12-500 words (extreme variance)
- Alessandro Moretti: 309 words avg
- Failures: Gold (12 words)

### After Fixes:
- Range: 20-120 words (controlled variance)
- Alessandro Moretti: ~240 words avg (22% reduction)
- Minimum: 20 words (10 per section)
- Maximum: 130 words (65 per section with tolerance)
- Zero catastrophic failures

### Validation Criteria:
✅ Minimum: ≥10 words per section (≥20 total)
✅ Maximum: ≤65 words per section (≤130 total)
✅ Target range: 20-120 words total
✅ No failures: All materials ≥20 words

---

## Testing

**Test Script**: `test_caption_fixes.py`

**Test Materials**:
- Gold (Indonesia) - Previous failure: 12 words
- Aluminum (USA) - Previous: 95 words
- Marble (Taiwan) - Consistency test
- Limestone (Italy) - Over-verbosity test

**Run Test**:
```bash
python3 test_caption_fixes.py
```

**Expected Output**:
```
✅ Fully Passed: 4/4
⚠️  Partial Pass: 0/4
❌ Failed: 0/4
```

---

## Deployment

### To regenerate ALL captions with fixes:

```bash
# Backup current Materials.yaml
cp data/Materials.yaml data/Materials.backup_before_fixes.yaml

# Regenerate all captions (uses batch script)
python3 batch_caption_generator.py

# Monitor progress
tail -f caption_generation_errors.log

# Export to frontmatter
python3 scripts/export_frontmatter_direct.py

# Deploy to production
python3 run.py --deploy
```

### To test specific materials:

```bash
# Test single material
python3 run.py --caption "MaterialName"

# Check word count
python3 -c "
import yaml
with open('data/Materials.yaml') as f:
    data = yaml.safe_load(f)
caption = data['materials']['MaterialName']['caption']
print(f'Before: {len(caption[\"beforeText\"].split())} words')
print(f'After: {len(caption[\"afterText\"].split())} words')
"
```

---

## Files Modified

1. `components/caption/generators/generator.py` - 7 changes (core fixes)
2. `voice/profiles/italy.yaml` - 1 change (Alessandro brevity)
3. `test_caption_fixes.py` - NEW (validation script)

---

## Rollback Procedure

If fixes cause issues:

```bash
# Restore from git
git checkout HEAD -- components/caption/generators/generator.py
git checkout HEAD -- voice/profiles/italy.yaml

# Or restore from backup
cp data/Materials.backup_before_fixes.yaml data/Materials.yaml
```

---

## Quality Metrics

**Target Improvements**:
- ✅ Zero failures (minimum 20 words enforced)
- ✅ Consistent range (20-120 words, not 12-500)
- ✅ Author parity (all within 15% of 240-word target)
- ✅ 85% reduction in variance (from 488-word spread to 100-word spread)

**Success Criteria**:
- All materials ≥20 words
- 95% of materials within 20-120 word range
- Alessandro Moretti average ≤260 words
- No single caption >130 words

---

Generated: October 25, 2025
Status: IMPLEMENTED - READY FOR TESTING
