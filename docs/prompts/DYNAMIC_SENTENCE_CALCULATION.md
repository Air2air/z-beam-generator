## Dynamic Sentence Count Calculation

**Last Updated**: November 14, 2025  
**Status**: ✅ ACTIVE

---

## Overview

The Z-Beam Generator uses **dynamic sentence count calculation** based on author voice and grammar norms rather than hardcoded sentence counts. This allows natural variation between authors while respecting country-specific writing patterns.

---

## Key Principles

### 1. No Hardcoded Sentence Counts
- ❌ **FORBIDDEN**: `min_sentences: 5-7` in persona files
- ✅ **REQUIRED**: `grammar_norms` with `avg_words_per_sentence`
- Sentence counts calculated at runtime based on word count target

### 2. Grammar Norms by Country
Each author has grammar norms that reflect their country's writing patterns:

| Country | Avg Words/Sentence | Distribution | Writing Style |
|---------|-------------------|--------------|---------------|
| **United States** | 16 | 30% short, 50% medium, 20% long | Direct, concise |
| **Italy** | 18 | 20% short, 50% medium, 30% long | Formal, structured |
| **Indonesia** | 17 | 25% short, 55% medium, 20% long | Clear, cause-effect |
| **Taiwan** | 15 | 35% short, 45% medium, 20% long | Data-focused, precise |

### 3. Dynamic Calculation
Sentence counts determined by:
```
base_sentences = word_count ÷ avg_words_per_sentence
min_sentences = floor(base_sentences - 1)
max_sentences = ceil(base_sentences + 1)
```

---

## Grammar Norms Structure

### In Persona Files (`prompts/personas/*.yaml`)

```yaml
# Grammar Norms: American English (direct, concise sentences)
grammar_norms:
  avg_words_per_sentence: 16  # American technical writing: 14-20 words average
  sentence_length_distribution:  # Target percentages for variety
    short: 0.30   # <12 words: punchy, direct
    medium: 0.50  # 12-18 words: standard flow
    long: 0.20    # 19+ words: detailed explanations
  preferred_punctuation: [".", "—"]  # Period for clarity, em-dash for emphasis
  compound_sentence_ratio: 0.25  # 25% sentences use coordinating conjunctions
```

### Required Fields
1. **`avg_words_per_sentence`**: Integer (12-20 typical range)
2. **`sentence_length_distribution`**: Dict with `short`, `medium`, `long` (must sum to 1.0)
3. **`preferred_punctuation`**: List of strings (punctuation preferences)
4. **`compound_sentence_ratio`**: Float 0.0-1.0 (percentage of compound sentences)

---

## Implementation

### SentenceCalculator Module
Location: `processing/generation/sentence_calculator.py`

Key methods:
- `calculate_sentence_target(word_count, grammar_norms)` → (min, max, guidance)
- `get_sentence_guidance(word_count, grammar_norms)` → natural language string
- `validate_sentence_count(text, word_count, grammar_norms)` → (bool, message)

### Integration with PromptBuilder
Location: `processing/generation/prompt_builder.py`

The prompt builder now:
1. Extracts `grammar_norms` from voice profile
2. Calculates dynamic sentence target using `SentenceCalculator`
3. Includes guidance in prompt: "Target 5-7 sentences (avg 16 words/sentence). Mix: 2 short (<12w), 3 medium (12-18w), 1-2 long (19+w)"

---

## Examples

### Subtitle (15 words)
**American English** (16 avg):
- Target: **2 sentences** (floor(15/16-1)=2, ceil(15/16+1)=2)
- Distribution: 1-2 short sentences

**Italian English** (18 avg):
- Target: **2 sentences** (floor(15/18-1)=2, ceil(15/18+1)=2)
- Distribution: 1-2 short sentences

### Caption (100 words)
**American English** (16 avg):
- Base: 100/16 = 6.25 sentences
- Target: **5-8 sentences**
- Distribution: 2 short, 3 medium, 1-2 long

**Italian English** (18 avg):
- Base: 100/18 = 5.56 sentences
- Target: **4-7 sentences**
- Distribution: 1 short, 3 medium, 1-2 long (more long sentences)

**Taiwanese English** (15 avg):
- Base: 100/15 = 6.67 sentences
- Target: **5-8 sentences**
- Distribution: 2 short, 3 medium, 1-2 long (more short sentences)

---

## Testing

### Test Suite
Location: `tests/test_dynamic_sentence_calculation.py`

**Critical Tests**:
1. ✅ Sentence counts vary by author for same word count
2. ✅ Grammar norms present in all persona files
3. ✅ No hardcoded `min_sentences` anywhere
4. ✅ Distribution percentages sum to 1.0
5. ✅ Validation works correctly

### Running Tests
```bash
pytest tests/test_dynamic_sentence_calculation.py -v
```

---

## Configuration

### Word Count Ranges
Defined in `processing/config.yaml`:

```yaml
component_lengths:
  subtitle:
    default: 15
  caption:
    default: 25  
  description:
    default: 150
  faq:
    default: 100
  troubleshooter:
    default: 120
```

These are combined with `length_variation_range` slider (1-3) to create actual ranges:
- **Level 1**: ±10% variation
- **Level 2**: ±20% variation
- **Level 3**: ±40% variation

---

## Migration from Hardcoded Counts

### Before (❌ DEPRECATED)
```yaml
generation_constraints:
  caption: {min_sentences: 5-7, min_words: 95, length_variation: true}
```

### After (✅ CURRENT)
```yaml
# Grammar Norms: American English
grammar_norms:
  avg_words_per_sentence: 16
  sentence_length_distribution:
    short: 0.30
    medium: 0.50
    long: 0.20
  preferred_punctuation: [".", "—"]
  compound_sentence_ratio: 0.25

generation_constraints:
  caption: {min_words: 95, length_variation: true}  # Sentences calculated dynamically
```

---

## Benefits

1. **Natural Variation**: Sentence counts vary naturally by author voice
2. **Grammar Authenticity**: Respects country-specific writing patterns
3. **Flexible**: Adapts to any word count without manual updates
4. **Maintainable**: Single source of truth (grammar norms) instead of scattered counts
5. **Testable**: Clear validation that counts follow norms

---

## Troubleshooting

### Problem: Sentences still hardcoded
**Solution**: Run `pytest tests/test_dynamic_sentence_calculation.py::TestGrammarNormsIntegrity::test_no_hardcoded_sentence_counts_in_personas`

### Problem: Grammar norms missing
**Solution**: Run `pytest tests/test_dynamic_sentence_calculation.py::TestGrammarNormsIntegrity::test_grammar_norms_present_in_all_personas`

### Problem: All authors have same sentence count
**Solution**: Check `avg_words_per_sentence` differs between countries in persona files

---

## Future Enhancements

1. **Sentence complexity scoring** based on compound_sentence_ratio
2. **Punctuation preference enforcement** in validation
3. **Dynamic distribution adjustment** based on content type
4. **Cross-language grammar norms** for non-English content
