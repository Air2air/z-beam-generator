# Size-Aware Prompt Compression Policy

**Status**: ✅ IMPLEMENTED (December 12, 2025)  
**Location**: `generation/core/generator.py`, `learning/humanness_optimizer.py`  
**Purpose**: Automatically compress humanness layer when base prompt exceeds size threshold

---

## Problem Statement

**Root Cause**: Full humanness optimization layer is ~9,000 characters (67% of total prompt). Combined with base prompt (author, task, voice, requirements), total prompts frequently exceeded the 8,000 character API limit for Grok text generation.

**Impact**:
- Prompts: 12,000+ chars (51% over limit)
- API rejection of oversized prompts
- Generation failures for small components (descriptions, captions)

**Example**:
```
Base prompt:        2,983 chars (author + voice + task)
Full humanness:     9,074 chars (randomization + patterns + examples)
TOTAL:             12,057 chars ❌ EXCEEDS 8,000 limit
```

---

## Solution: Size-Aware Compression

### Architecture

Generator automatically compresses humanness layer based on base prompt size:

```python
# In generation/core/generator.py

SIZE_THRESHOLD = 2000  # Chars

if base_size > SIZE_THRESHOLD:
    # Use COMPRESSED humanness (~800 chars)
    final_humanness = optimizer.generate_compressed_humanness(
        component_type, strictness_level=1
    )
else:
    # Use FULL humanness (~9,000 chars)
    final_humanness = humanness_layer
```

### Compression Strategy

**Compressed humanness retains**:
1. **Critical opening patterns** - Most important for AI detection avoidance
2. **Forbidden phrases** - Top 10 most critical violations
3. **Core voice requirements** - Essential conversational markers
4. **Structural diversity rules** - Randomization mandates
5. **RANDOMIZE directives** - Prevent repetition

**Compressed humanness removes**:
- Verbose examples ("Example from passing sample...")
- Statistical analysis ("Analyzed 327 generations...")
- Detailed explanations of each pattern
- Redundant warnings
- Multiple examples per rule

### Size Comparison

| Version | Size | Percentage | Use Case |
|---------|------|------------|----------|
| Full humanness | ~9,000 chars | 100% | Small base prompts (<2,000 chars) |
| Compressed humanness | ~800 chars | 9% | Large base prompts (>2,000 chars) |

**Compression ratio**: 91% reduction (9,000 → 800 chars)

---

## Implementation Details

### 1. Method: `generate_compressed_humanness()`

**Location**: `learning/humanness_optimizer.py`

**Purpose**: Generate essential humanness instructions without verbose content

**Returns**: Compressed humanness layer (~800 chars)

**Sections**:
```
=== HUMANNESS LAYER (COMPRESSED) ===

🚨 OPENING RULE:
Start with: 'When cleaning [X], you'll want...' OR 'The key with [X] is...'
❌ NEVER: '[Material]'s...' or '[Material] has...'

✅ VOICE: Direct technician explaining to colleague
Use: 'you must', 'watch for', 'be careful with', 'We've found'
❌ AVOID: Encyclopedia tone, passive observation, formal comparisons

❌ FORBIDDEN PHRASES:
'presents a challenge', 'zaps away', 'game-changing', 'quick zap',
'changes everything', 'primary concern', 'stands out among', ...

📐 STRUCTURE: Vary approach - problem/contrast/process/experience
Mix short (5-10w) and long (20-30w) sentences randomly

🎲 RANDOMIZE: Opening pattern, voice style, property order, warning placement
NO TWO OUTPUTS SHOULD BE SIMILAR

=== END COMPRESSED LAYER ===
```

### 2. Generator Integration

**Location**: `generation/core/generator.py` (lines ~245-290)

**Process**:
1. Build base prompt WITHOUT humanness (measure size)
2. Check base size against SIZE_THRESHOLD (2,000 chars)
3. If base > 2,000: Use compressed humanness (~800 chars)
4. If base < 2,000: Use full humanness (~9,000 chars)
5. Rebuild prompt with appropriate humanness
6. Log sizes (base, humanness, total)

**Terminal Output**:
```
📦 Base prompt 2,983 chars > 2,000 - using COMPRESSED humanness
📊 Final prompt: 3,800 chars (base: 2,983, humanness: 814)
```

---

## Results

### Before Compression

```
Base prompt:        2,983 chars
Full humanness:     9,074 chars
TOTAL:             12,057 chars ❌ EXCEEDS 8,000 limit
Status:             CRITICAL validation failure
API Result:         Rejected (over limit)
```

### After Compression

```
Base prompt:        2,983 chars  
Compressed humanness: 814 chars
TOTAL:              3,797 chars ✅ UNDER 8,000 limit
Status:             Valid (3 suggestions only)
API Result:         Success
```

**Reduction**: 12,057 → 3,797 chars (68% reduction)

---

## Quality Impact

### Retained Quality Elements

✅ **AI Detection Avoidance**: Critical opening patterns preserved  
✅ **Voice Consistency**: Core conversational markers intact  
✅ **Forbidden Phrase Filtering**: Top 10 violations included  
✅ **Structural Diversity**: Randomization mandates present  

### Trade-offs

⚠️ **Reduced Guidance**: Fewer examples and explanations  
⚠️ **Less Context**: Statistical analysis removed  
⚠️ **Minimal Redundancy**: Single warning per rule (vs multiple)  

**Assessment**: Compressed humanness maintains essential quality gates while sacrificing verbose guidance. For small components (30-80 word descriptions), this trade-off is acceptable.

---

## Configuration

### Size Threshold

**Current**: `SIZE_THRESHOLD = 2000` chars

**Rationale**:
- Typical base prompt: 2,500-3,000 chars
- Compressed humanness: ~800 chars
- Total with compression: 3,300-3,800 chars
- Safety margin: 52-63% below API limit

**Adjustment**:
```python
# In generation/core/generator.py (line ~252)
SIZE_THRESHOLD = 2000  # Lower = more compression, Higher = more full humanness
```

### API Limit

**Current**: 8,000 chars (Grok text API)

**Hard limit**: Cannot be exceeded  
**Enforcement**: Automatic compression prevents violations

---

## Testing

### Test Suite

**File**: `tests/test_compressed_humanness.py`

**Coverage**:
1. ✅ Compressed humanness method exists
2. ✅ Generates non-empty content
3. ✅ Compressed significantly smaller than full (9:1 ratio)
4. ✅ Contains all critical sections
5. ✅ Has clear start/end markers
6. ✅ Strictness level validation (1-5)
7. ✅ Removes verbose examples
8. ✅ Preserves forbidden phrases
9. ✅ SIZE_THRESHOLD correctly configured
10. ✅ Typical prompt stays under API limit
11. ✅ Large prompt stays under API limit

**Run Tests**:
```bash
pytest tests/test_compressed_humanness.py -v
```

### Manual Verification

```bash
# Test compressed humanness output
python3 -c "
from learning.humanness_optimizer import HumannessOptimizer
optimizer = HumannessOptimizer(winston_db_path='z-beam.db')
compressed = optimizer.generate_compressed_humanness('description', 1)
print(f'Size: {len(compressed)} chars')
print(compressed)
"

# Test in generation context
python3 run.py --contaminant "adhesive-residue" --description
# Watch for: "📦 using COMPRESSED humanness" message
```

---

## When Compression Applies

### Compressed Humanness Used

✅ Small components (descriptions, captions, micros)  
✅ Complex persona profiles (long voice instructions)  
✅ Rich context (many facts, detailed requirements)  
✅ Base prompt > 2,000 chars  

### Full Humanness Used

✅ Large components (FAQs, articles)  
✅ Minimal persona profiles  
✅ Simple context  
✅ Base prompt < 2,000 chars  

---

## Maintenance

### Monitoring

Watch for:
- Prompts still exceeding 8,000 chars (compression insufficient)
- Quality degradation with compressed humanness
- False positives (compression when full would fit)

### Adjustment Guidelines

**If prompts still too large**:
1. Lower SIZE_THRESHOLD (2000 → 1500)
2. Compress humanness further (remove more content)
3. Compress persona files (reduce voice instructions)

**If quality suffers**:
1. Raise SIZE_THRESHOLD (2000 → 2500)
2. Add essential content back to compressed version
3. Implement two-tier compression (normal + aggressive)

---

## Integration with Other Policies

### Prompt Validation Policy

- Compressed prompts validated same as full prompts
- Size validation enforced (8,000 char limit)
- Quality checks run on compressed humanness

### Prompt Purity Policy

- Compression happens in `humanness_optimizer.py` ONLY
- Generator calls compression method (doesn't modify instructions)
- No hardcoded humanness text in generator

### Fail-Fast Architecture

- If compression still exceeds limit → optimization attempted
- If optimization fails → logged but generation proceeds
- No silent failures or defaults

---

## Future Enhancements

### Potential Improvements

1. **Two-tier compression**:
   - Normal compressed: ~800 chars (current)
   - Aggressive compressed: ~400 chars (future)

2. **Component-specific compression**:
   - Descriptions: Aggressive compression
   - FAQs: Normal compression
   - Articles: No compression

3. **Dynamic compression ratio**:
   - Calculate exact space available
   - Compress to fit precisely

4. **Cached compressed versions**:
   - Pre-generate compressed humanness for common components
   - Avoid regeneration overhead

---

## References

- **Implementation**: `generation/core/generator.py` (lines 245-290)
- **Compression Method**: `learning/humanness_optimizer.py::generate_compressed_humanness()`
- **Tests**: `tests/test_compressed_humanness.py`
- **Related Policy**: `docs/08-development/PROMPT_VALIDATION_POLICY.md`

---

## Changelog

**December 12, 2025**: Initial implementation
- Added `generate_compressed_humanness()` method
- Integrated size-aware decision in generator
- Created comprehensive test suite
- Documented policy and architecture
