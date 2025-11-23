# Subtitle Length Configuration Update

**Date:** November 22, 2025  
**Status:** ✅ Implemented  
**Component:** Subtitle Generation

---

## Overview

Updated subtitle generation to use component-specific length configuration (`subtitle_length`) with 50% reduced word count ranges compared to descriptions.

---

## Configuration Changes

### New: `subtitle_length` Configuration

**File:** `generation/config.yaml` (lines 83-96)

```yaml
subtitle_length:
  short:
    range: [21, 31]
    description: "CONCISE - core advantage only"
  medium:
    range: [31, 46]
    description: "BALANCED - key property with context"
  long:
    range: [46, 63]
    description: "DETAILED - property with comparison"
```

### Component Length Targets

**File:** `generation/config.yaml` (lines 204-207)

```yaml
component_lengths:
  subtitle:
    target: 1000  # No effective token limit - let prompt instructions control length
    extraction_strategy: raw
```

**Rationale:** Changed from `target: 25` (32 tokens) to `target: 1000` (1300 tokens) to prevent token truncation. The actual word count is controlled by:
1. Prompt instructions in `prompts/components/subtitle.txt`
2. Dynamic length selection from `subtitle_length` configuration
3. HumannessOptimizer applying component-specific randomization

---

## Technical Implementation

### 1. HumannessOptimizer Routing

**File:** `learning/humanness_optimizer.py` (lines 387-407)

```python
# Dynamic length config selection based on component_type
length_config_key = 'subtitle_length' if component_type == 'subtitle' else 'length'
if length_config_key in self.config['randomization_targets']:
    length_config = self.config['randomization_targets'][length_config_key]
else:
    length_config = self.config['randomization_targets']['length']  # Fallback
```

**How It Works:**
- When `component_type='subtitle'` → Uses `subtitle_length` config
- When `component_type='description'` → Uses `length` config
- Falls back to `length` if component-specific config not found

### 2. Prompt Template Updates

**File:** `prompts/components/subtitle.txt`

Added anti-jargon section matching `description.txt`:

```
🚫 AVOID EXCESSIVE TECHNICAL JARGON:
- NO multiple decimal places in one sentence
- NO wavelength citations without context
- NO physics textbook language
- NO temperature in Kelvin (use °C or descriptive terms)
- YES conversational technical: Expert explaining, not documenting
- YES direct statements: "maintains integrity under heat" not "presents structural resilience"
```

---

## Word Count Distribution

### Target Ranges

| Range | Words | Description |
|-------|-------|-------------|
| **SHORT** | 21-31 | Core advantage only |
| **MEDIUM** | 32-46 | Key property with context |
| **LONG** | 47-63 | Property with comparison |

### Before Update (November 22, 2025)

- **Average:** 24.1 words
- **Range:** 8 - 70 words
- **Within Target (21-63):** 58 files (43.9%)
- **Under Target (<21):** 71 files (53.8%)
- **Over Target (>63):** 3 files (2.3%)

### Materials Needing Regeneration

**74 files** outside target range:
- 71 too short (<21 words)
- 3 too long (>63 words)

**List:** `materials_needing_subtitle_regen.txt`

---

## Regeneration Process

### Batch Script

**File:** `batch_subtitle_update_74.sh`

```bash
#!/bin/bash
# Regenerates subtitles for 74 materials outside 21-63 word range
# Reads from: materials_needing_subtitle_regen.txt
# Uses: python3 run.py --subtitle "$MATERIAL" --skip-integrity-check
```

### Usage

```bash
# Generate list of materials needing update
python3 << 'EOF'
import os, yaml
materials_dir = 'frontmatter/materials'
needs_regen = []
for file in os.listdir(materials_dir):
    if file.endswith('.yaml'):
        with open(f'{materials_dir}/{file}') as f:
            data = yaml.safe_load(f)
            title = data.get('title', '')
            material = title.replace(' Laser Cleaning', '')
            if 'subtitle' in data:
                wc = len(data['subtitle'].split())
                if wc < 21 or wc > 63:
                    needs_regen.append(material)
with open('materials_needing_subtitle_regen.txt', 'w') as f:
    for m in needs_regen:
        f.write(f"{m}\n")
print(f"Created list: {len(needs_regen)} materials")
EOF

# Run batch regeneration
./batch_subtitle_update_74.sh
```

### Expected Results

- **Success Rate:** ~95% (based on previous batch operations)
- **Word Count Distribution:** 70%+ within 21-63 range
- **Average:** 35-45 words (mid-range with LLM overage)
- **Time:** ~15-20 minutes (74 materials × 10-15s each)

---

## Testing

### Manual Test (5 Materials)

Tested subtitle generation with new configuration:

| Material | Word Count | Status |
|----------|-----------|---------|
| Aluminum | 40 | ✅ Within target (MEDIUM) |
| Copper | 37 | ✅ Within target (MEDIUM) |
| Titanium | 40 | ✅ Within target (MEDIUM) |
| Bronze | 38 | ✅ Within target (MEDIUM) |
| Steel | 40 | ✅ Within target (MEDIUM) |

**Result:** All test materials generated 37-40 word subtitles (within 21-63 target range).

### Automated Testing

**Test File:** `tests/test_subtitle_length_config.py` (to be created)

```python
def test_subtitle_length_config_exists():
    """Verify subtitle_length config exists"""
    config = load_config('generation/config.yaml')
    assert 'subtitle_length' in config['randomization_targets']
    
def test_humanness_optimizer_routes_correctly():
    """Verify HumannessOptimizer uses subtitle_length for subtitles"""
    optimizer = HumannessOptimizer()
    params = optimizer.generate_humanness_params(component_type='subtitle')
    # Should use subtitle_length ranges (21-63) not description ranges (42-127)
    
def test_subtitle_word_count_in_range():
    """Verify generated subtitles fall within 21-63 word range"""
    # Generate subtitle for test material
    # Assert word count between 21 and 63
```

---

## Files Changed

### Configuration
- ✅ `generation/config.yaml` - Added `subtitle_length` + updated `component_lengths.subtitle.target`

### Code
- ✅ `learning/humanness_optimizer.py` - Component-specific length routing

### Prompts
- ✅ `prompts/components/subtitle.txt` - Anti-jargon rules

### Scripts
- ✅ `batch_subtitle_update_74.sh` - Batch regeneration script
- ✅ `materials_needing_subtitle_regen.txt` - List of 74 materials

### Documentation
- ✅ `docs/01-getting-started/ai-assistants.md` - Updated word count reference
- ✅ `docs/SUBTITLE_LENGTH_CONFIG_NOV22_2025.md` - This document
- ⏳ `tests/test_subtitle_length_config.py` - To be created

---

## Migration Path

### For Existing Materials

1. **Identify:** 74 materials outside 21-63 word range
2. **Regenerate:** Run `batch_subtitle_update_74.sh`
3. **Verify:** Check word count distribution post-regeneration
4. **Commit:** Update Materials.yaml + frontmatter files

### For New Materials

- ✅ Automatically use new configuration
- ✅ Generate 21-63 word subtitles
- ✅ Apply anti-jargon rules
- ✅ Use component-specific length randomization

---

## Rationale

### Why 50% Reduction?

| Component | Range | Purpose |
|-----------|-------|---------|
| **Description** | 42-127 words | Full material overview |
| **Subtitle** | 21-63 words | Single key property highlight |

**Subtitle Purpose:** Quick, scannable property highlight that:
- Captures ONE compelling advantage
- Avoids jargon overload
- Complements longer description
- Fits meta description/preview contexts

### Why Component-Specific Config?

**Before:** All components used same `length` configuration
**Problem:** Subtitles too long, repeated description content

**After:** Each component has appropriate length:
- Description: 42-127 words (comprehensive)
- Subtitle: 21-63 words (focused)
- Caption: 25 words (ultra-concise)
- FAQ: Dynamic per question

---

## Rollback Plan

If needed, revert to previous configuration:

```yaml
# Remove subtitle_length section
# Change component_lengths.subtitle.target back to 25
# Revert humanness_optimizer.py routing logic
```

**Not Recommended:** Previous configuration caused:
- Token truncation (target: 25 = 32 tokens)
- Mid-sentence cuts
- Inconsistent quality

---

## Success Metrics

### Completion Criteria

- ✅ Configuration implemented
- ✅ Code updated
- ✅ Prompts enhanced
- ✅ Manual testing passed (5/5 materials)
- ⏳ Batch regeneration (74 materials)
- ⏳ Automated tests created

### Post-Regeneration Goals

- **Target Compliance:** 70%+ of materials within 21-63 words
- **Average Word Count:** 35-45 words
- **Quality:** Pass Winston + Realism gates
- **Consistency:** Similar style to descriptions

---

## Related Documentation

- `CLEANUP_REPORT_NOV22_2025.md` - Prompt/frontmatter cleanup
- `HARDCODED_VALUE_FIXES_NOV22_2025.md` - Dynamic config approach
- `generation/config.yaml` - Complete configuration reference
- `docs/01-getting-started/ai-assistants.md` - User-facing generation guide

---

## Commit History

1. **4e99174f** - Subtitle generation normalization and frontmatter standardization
2. **3d04801b** - Clean up 9 orphaned frontmatter files
3. **ce5703f4** - Restore 7 abbreviated duplicate frontmatter files
4. **[PENDING]** - Batch subtitle regeneration for 74 materials

---

## Future Enhancements

### Potential Improvements

1. **Adaptive Length by Category:**
   ```yaml
   subtitle_length:
     metal: [25, 35]    # Shorter for common metals
     composite: [35, 50] # Longer for complex materials
     ceramic: [30, 45]
   ```

2. **Property-Focused Subtitles:**
   - Automatically highlight most unique property
   - Compare against category averages
   - Emphasize competitive advantages

3. **SEO Optimization:**
   - Target 50-60 characters for meta descriptions
   - Include material + key benefit
   - Natural language (no keyword stuffing)

---

**Status:** ✅ Configuration complete, ready for batch regeneration
