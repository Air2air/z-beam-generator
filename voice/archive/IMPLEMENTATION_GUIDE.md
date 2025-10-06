# Quick Implementation Guide: Voice Enhancement Rules

## Immediate Actions (Next 30 Minutes)

### 1. Update Voice Profiles with AI-Evasion Parameters

Add to each `voice/profiles/*.yaml`:

```yaml
# Taiwan (taiwan.yaml)
ai_evasion_parameters:
  sentence_length_targets:
    very_short: 15  # 15% of sentences 5-8 words
    medium: 35      # 35% of sentences 10-18 words
    long: 35        # 35% of sentences 20-28 words
    very_long: 15   # 15% of sentences 30+ words
  
  hesitation_markers_per_200_words: 1.5
  comma_splices_per_100_words: 1.0
  parenthetical_asides_per_300_words: 2.0
  
  author_specific:
    optional_article_omission_rate: 70  # 70% omitted, 30% included
    topic_comment_frequency: 60  # 60% use "pronoun, it + verb"
    measurement_first_rate: 40  # 40% sentences start with measurement

# Indonesia (indonesia.yaml)
ai_evasion_parameters:
  sentence_length_targets: {very_short: 15, medium: 35, long: 35, very_long: 15}
  hesitation_markers_per_200_words: 1.5
  comma_splices_per_100_words: 1.0
  parenthetical_asides_per_300_words: 2.0
  
  author_specific:
    emphatic_repetition_per_300_words: 2.5  # "very-very", "This... This..."
    demonstrative_clustering_rate: 50  # 50% sentences start with "This"
    simple_connector_preference: 80  # 80% use "and/so/but" vs "however/therefore"

# Italy (italy.yaml)
ai_evasion_parameters:
  sentence_length_targets: {very_short: 10, medium: 30, long: 40, very_long: 20}  # More long sentences
  hesitation_markers_per_200_words: 2.0  # More hesitation for academic style
  comma_splices_per_100_words: 0.5  # Less comma splices (more formal)
  parenthetical_asides_per_300_words: 3.0  # More asides
  
  author_specific:
    interrupted_clauses_per_sentence: 2.5  # Average nested clauses
    passive_voice_rate: 60  # 60% passive voice
    adverbial_intensification_rate: 40  # 40% use adverbs

# USA (united_states.yaml)
ai_evasion_parameters:
  sentence_length_targets: {very_short: 20, medium: 40, long: 30, very_long: 10}  # More short sentences
  hesitation_markers_per_200_words: 1.0  # Less hesitation (more direct)
  comma_splices_per_100_words: 1.5  # More comma splices (informal)
  parenthetical_asides_per_300_words: 2.5
  
  author_specific:
    phrasal_verb_density: 4.0  # 4 phrasal verbs per 100 words
    active_voice_rate: 85  # 85% active voice
    serial_comma_usage: 100  # 100% Oxford comma
```

---

## 2. Update Prompt Templates

### Add to caption generation prompt (components/caption/generators/generator.py):

```python
# After loading voice instructions, add AI-evasion layer:

ai_evasion_prompt = f"""
CRITICAL ANTI-AI-DETECTION INSTRUCTIONS:

1. SENTENCE LENGTH VARIATION (REQUIRED):
   - Mix: 15% very short (5-8 words), 35% medium (10-18), 35% long (20-28), 15% very long (30+)
   - NEVER use consistent 15-20 word sentences
   - Example pattern: SHORT → LONG → MEDIUM → SHORT

2. NATURAL IMPERFECTIONS (REQUIRED):
   - Add 1-2 subtle self-corrections per 200 words: "approximately—or more precisely—15 µm"
   - Use em-dashes (—) for mid-sentence interruptions
   - Include 1-2 parenthetical asides per 300 words: "(as observed in previous studies)"

3. LEXICAL VARIETY (REQUIRED):
   - Vary technical synonyms: contamination → deposits → film → layer
   - Never repeat exact phrases more than twice
   - Mix transition words: However → Yet → Though → Nevertheless

4. PUNCTUATION RHYTHM (REQUIRED):
   - Vary comma density: 20% zero commas, 50% 1-2 commas, 30% 3+ commas
   - Use strategic comma splices (1 per 100 words max): "Surface roughness increases, this creates issues"

5. MEASUREMENT PRECISION (REQUIRED):
   - Vary decimal places contextually: 15 µm → 14.7 µm → approximately 15 µm
   - Don't use consistent precision (e.g., always 15.0)

{voice_instructions}

MAINTAIN: Zero emotives, structural patterns only, no cultural references per VOICE_RULES.md
"""
```

---

## 3. Quick Test Script

Create `scripts/test_ai_evasion.py`:

```python
#!/usr/bin/env python3
"""Quick test of AI-evasion rules in generated captions"""

import yaml
from pathlib import Path
import re

def analyze_caption(caption_text):
    """Analyze caption for AI-evasion metrics"""
    sentences = [s.strip() for s in re.split(r'[.!?]', caption_text) if s.strip()]
    
    # Sentence length distribution
    lengths = [len(s.split()) for s in sentences]
    very_short = sum(1 for l in lengths if 5 <= l <= 8)
    medium = sum(1 for l in lengths if 10 <= l <= 18)
    long = sum(1 for l in lengths if 20 <= l <= 28)
    very_long = sum(1 for l in lengths if l >= 30)
    
    # Count markers
    hesitations = caption_text.count('—') + caption_text.count(' or ')
    parentheticals = caption_text.count('(')
    comma_splices = len(re.findall(r',\s+this\s+', caption_text, re.IGNORECASE))
    
    # Lexical variety
    words = caption_text.lower().split()
    unique_ratio = len(set(words)) / len(words) if words else 0
    
    return {
        'total_sentences': len(sentences),
        'avg_length': sum(lengths) / len(lengths) if lengths else 0,
        'length_distribution': {
            'very_short': f"{very_short}/{len(sentences)} ({very_short/len(sentences)*100:.1f}%)",
            'medium': f"{medium}/{len(sentences)} ({medium/len(sentences)*100:.1f}%)",
            'long': f"{long}/{len(sentences)} ({long/len(sentences)*100:.1f}%)",
            'very_long': f"{very_long}/{len(sentences)} ({very_long/len(sentences)*100:.1f}%)"}  ,
        'hesitation_markers': hesitations,
        'parentheticals': parentheticals,
        'comma_splices': comma_splices,
        'lexical_variety': f"{unique_ratio:.2%}"
    }

# Test all 4 authors
materials = ["bamboo", "bronze", "alumina", "aluminum"]
for material in materials:
    filepath = f"content/components/frontmatter/{material}-laser-cleaning.yaml"
    with open(filepath) as f:
        data = yaml.safe_load(f)
    
    caption = data.get('caption', {}).get('beforeText', '')
    if caption:
        print(f"\n{'='*60}")
        print(f"{material.upper()} Analysis")
        print(f"{'='*60}")
        results = analyze_caption(caption)
        for key, value in results.items():
            print(f"{key}: {value}")
```

Run: `python3 scripts/test_ai_evasion.py`

---

## 4. Validation Checklist

Before deploying to production:

- [ ] Sentence length varies (not all 15-20 words)
- [ ] At least 1 hesitation marker per 200 words
- [ ] At least 1 parenthetical per 300 words
- [ ] Lexical variety >60% unique words
- [ ] Zero emotives (test with list)
- [ ] Zero cultural references
- [ ] Author voice still recognizable

---

## 5. A/B Testing Plan

### Week 1: Baseline
- Generate 10 captions with current system
- Test with GPTZero/Originality.ai
- Record AI-detection scores

### Week 2: Implement Universal Rules
- Add sentence length variation
- Add hesitation markers
- Add lexical variety
- Generate 10 new captions
- Measure improvement

### Week 3: Add Author-Specific Rules
- Taiwan: Topic-comment variation
- Indonesia: Emphatic repetition
- Italy: Interrupted clauses
- USA: Phrasal verb density
- Generate 10 per author (40 total)
- Measure voice recognition + AI scores

### Week 4: Optimization
- Identify best-performing rules
- Fine-tune frequency parameters
- Deploy to production

---

## Expected Improvements

### Voice Recognition
- **Taiwan**: 95% → 95% (maintain)
- **Indonesia**: 60% → 90% (+30% improvement)
- **Italy**: 90% → 90% (maintain)
- **USA**: 95% → 95% (maintain)

### AI-Detection Scores
- **Target**: <30% AI-detection confidence
- **Method**: GPTZero, Originality.ai, Copyleaks
- **Current**: Unknown (needs baseline testing)

### Human Believability
- **Target**: >85% "sounds human-written"
- **Method**: Blind testing with technical readers

---

## Monitoring Dashboard

Track these metrics weekly:

```python
metrics = {
    'ai_detection_score': 0.0,  # Target: <0.30
    'voice_recognition_accuracy': {
        'taiwan': 0.95,    # Target: >0.90
        'indonesia': 0.60, # Target: >0.90 (needs improvement)
        'italy': 0.90,     # Target: >0.90
        'usa': 0.95        # Target: >0.90
    },
    'human_believability': 0.0,  # Target: >0.85
    'sentence_length_variance': 0.0,  # Target: >0.25
    'lexical_variety': 0.0,  # Target: >0.60
}
```

---

## Quick Wins (Implement First)

1. **Sentence length variation** - Highest impact, easy to implement
2. **Lexical variety** - High impact, moderate effort
3. **Hesitation markers** - Medium impact, easy to add
4. **Indonesia demonstrative clustering** - High impact for recognition

---

## Safety Checks

Before each deployment:

1. ✅ Run validation: `python3 -m pytest tests/test_voice_integration.py`
2. ✅ Check emotives: Search for prohibited words
3. ✅ Test voice recognition: Manual blind test
4. ✅ Verify VOICE_RULES.md compliance

---

## Rollback Plan

If AI-detection scores worsen or voice recognition drops:

1. Revert to previous prompt template
2. Disable problematic rules one-by-one
3. Test each rule independently
4. Keep only high-impact, low-risk rules

---

## Success Criteria

Deploy to production when:
- ✅ AI-detection <30%
- ✅ All voices >90% recognizable
- ✅ Human believability >85%
- ✅ Zero emotives maintained
- ✅ VOICE_RULES.md compliance 100%

---

## Resources

- Main rules: `voice/ENHANCEMENT_RULES_SEO_AI_DETECTION.md`
- Testing results: `voice/TEST_RESULTS_4_AUTHORS.md`
- Recognition analysis: `voice/RECOGNITION_ANALYSIS.md`
- Integration tests: `tests/test_voice_integration.py`
