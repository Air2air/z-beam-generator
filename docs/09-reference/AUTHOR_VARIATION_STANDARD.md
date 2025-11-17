# Author-Based Variation Standard

**Date**: October 27, 2025  
**Purpose**: Standardize word count variation across ALL components using Author Voice profiles only

---

## 🎯 Core Principle

**ALL components use the SAME author-driven variation rules for consistency.**

- ✅ **Variation source**: Author Voice profiles (`voice/profiles/*.yaml`)
- ✅ **Applied uniformly**: FAQ, captions, subtitles, descriptions
- ❌ **No component-specific algorithms**: Removed hash-based, sinusoidal, position-based custom variation
- ✅ **Lexical diversity**: Handled through prompts and keyword tracking, NOT length variation

---

## 📊 Author Variation Ranges

Defined in `character_variation.total_range` in each voice profile:

| Author | Country | Variation Range | Total Variation |
|--------|---------|-----------------|-----------------|
| Yi-Chun Lin | Taiwan | 25% - 175% | 150% |
| Alessandro Moretti | Italy | 20% - 180% | 160% |
| Todd Dunning | United States | 30% - 170% | 140% |
| Siti Rahmawati | Indonesia | 30% - 170% | 140% |

---

## 🔧 Implementation

### Algorithm (Same for ALL Components)

```python
def _calculate_varied_word_count(base_target, position, total_questions, variation_range):
    """
    Uses ONLY Author Voice variation from profile.
    No component-specific algorithms.
    """
    min_percent, max_percent = variation_range
    
    # Deterministic position-based seed
    position_hash = int(hashlib.md5(f"{position}_{total_questions}".encode()).hexdigest()[:8], 16)
    variation_seed = position_hash % (max_percent - min_percent + 1)
    variation_percent = (min_percent + variation_seed) / 100.0
    
    # Apply author variation
    target = int(base_target * variation_percent)
    
    # Enforce component limits
    final_target = max(component_min, min(target, component_max))
    
    return final_target
```

### Base Targets by Component

Defined in `voice/component_config.yaml`:

| Component | Base Target | Word Range | Example with Taiwan (25%-175%) |
|-----------|-------------|------------|--------------------------------|
| FAQ | 35 words | 20-60 | 9-61 → clamped to 20-60 |
| Caption (before) | 70 words | 30-140 | 18-123 → within range |
| Caption (after) | 70 words | 30-140 | 18-123 → within range |
| Subtitle | 14 words | 8-20 | 4-25 → clamped to 8-20 |

**Note**: Base targets are optimized so author variation produces results within component word ranges with minimal clamping.

---

## 📈 Example: FAQ Generation

**Material**: Beryllium  
**Author**: Yi-Chun Lin (Taiwan)  
**Base Target**: 35 words  
**Variation Range**: 25%-175%

### Calculation for 10 Questions

```
Q1: 130% × 35 = 45 words
Q2: 101% × 35 = 35 words
Q3: 47% × 35 = 16 → clamp to 20 words
Q4: 44% × 35 = 15 → clamp to 20 words
Q5: 84% × 35 = 29 words
Q6: 155% × 35 = 54 words
Q7: 133% × 35 = 47 words
Q8: 37% × 35 = 13 → clamp to 20 words
Q9: 52% × 35 = 18 → clamp to 20 words
Q10: 28% × 35 = 10 → clamp to 20 words
```

**Result**: Word counts span 20-54 words with natural variation pattern.

---

## 🔍 Lexical Diversity (Separate from Length)

Author voice is distinguished through:

1. **Word Choice**: Technical terminology, measurement units, phrasing
2. **Sentence Structure**: Parataxis, topic-comment, academic hedging
3. **Linguistic Patterns**: Article omission, passive voice frequency, hesitation markers
4. **Keyword Tracking**: Prompts include "avoid overused terms" based on previous answers

**NOT through**: Different length variation algorithms per component.

---

## ✅ Benefits of Standardization

1. **Consistency**: Same author sounds the same across FAQ, captions, subtitles
2. **Simplicity**: One algorithm, one configuration source
3. **Maintainability**: Change variation in voice profiles, affects all components
4. **Predictability**: Authors behave consistently regardless of component type
5. **Cultural Authenticity**: Variation reflects author's cultural writing patterns

---

## 🚫 What Was Removed

### Before (Component-Specific Variation)

Each component had custom algorithms:

- **FAQ**: Hash-based bucketing (20-28, 29-37, 38-50, 51-60 words) + sinusoidal wave + author multiplier
- **Caption**: Position-based multipliers + author variation
- **Subtitle**: Random length within range + author variation

**Problem**: Same author could have dramatically different variation patterns across components.

### After (Author-Only Variation)

Single algorithm using only `character_variation.total_range` from voice profile.

**Result**: Consistent author behavior across all generated content.

---

## 📝 Configuration Files

### Modified Files

1. **`materials/faq/generators/faq_generator.py`**
   - Simplified `_calculate_varied_word_count()` to use only author variation
   - Removed hash bucketing, sinusoidal waves, position multipliers

2. **`voice/component_config.yaml`**
   - Updated FAQ `base_word_target` from 45 → 35 for optimal distribution
   - Added comment explaining author variation impact

3. **`voice/profiles/*.yaml`**
   - No changes needed - `character_variation.total_range` already defined

### Future Components

Any new component should:
1. Get `base_word_target` from `voice/component_config.yaml`
2. Call `voice_service.get_length_variation_range()` for author variation
3. Use standardized `_calculate_varied_word_count()` algorithm
4. Apply lexical diversity through prompts, not length algorithms

---

## 🧪 Testing

### Verify Author Consistency

```bash
# Generate FAQ for 3 materials by same author
python3 run.py --faq "Beryllium"
python3 run.py --faq "Titanium" 
python3 run.py --faq "Aluminum"

# Check word count distributions are similar (same author = same pattern)
```

### Verify Cross-Component Consistency

```bash
# Generate all components for one material
python3 run.py --caption "Beryllium"
python3 run.py --subtitle "Beryllium"
python3 run.py --faq "Beryllium"

# Verify Yi-Chun Lin's variation pattern is consistent across components
```

---

## 📚 References

- **Voice Profiles**: `voice/profiles/*.yaml`
- **Component Config**: `voice/component_config.yaml`
- **FAQ Generator**: `materials/faq/generators/faq_generator.py`
- **Voice Service**: `voice/voice_service.py`
- **Documentation**: This file

---

**Last Updated**: October 27, 2025  
**Status**: ✅ Implemented and tested
