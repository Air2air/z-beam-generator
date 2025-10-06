# Voice Profile Cleanup Plan

## Objective
Remove ALL signature phrases, emotives, and cultural references from voice profiles per VOICE_RULES.md. Keep ONLY structural and grammatical patterns.

## Profiles to Clean

### 1. Taiwan (`voice/profiles/taiwan.yaml`)
**Status:** Partially updated, needs cleanup

**Remove:**
- [ ] Signature phrases section (lines containing catchphrases)
- [ ] Emotive descriptors: "interesting", "worth mentioning", "very important"
- [ ] Personal observations: "we can see", "I observe"
- [ ] Conversational markers: "let me explain", "simply put"

**Keep:**
- [x] Article omission patterns
- [x] Topic-comment structure  
- [x] Preposition variations
- [x] "Very" overuse pattern (grammatical, not emotive)
- [x] Measurement-first word order

### 2. Italy (`voice/profiles/italy.yaml`)
**Status:** Updated but contains emotives

**Remove:**
- [ ] Signature phrases: "what strikes one", "truly remarkable", "quite beautiful"
- [ ] Aesthetic appreciation: "beautiful", "elegant", "quality"
- [ ] Emotive intensifiers: "truly", "really", "quite", "particularly"
- [ ] Cultural references: if any remain
- [ ] Personal engagement: "one can see", "what strikes"

**Keep:**
- [x] Word order inversion patterns
- [x] Emphatic pronoun repetition
- [x] Infinitive without subject
- [x] Object fronting
- [x] Preposition from Italian ("different of")
- [x] Article with abstractions patterns

### 3. Indonesia (`voice/profiles/indonesia.yaml`)
**Status:** Original profile, full cleanup needed

**Remove:**
- [ ] ALL signature phrases
- [ ] Environmental/sustainability content references
- [ ] Practical/accessibility emotional markers
- [ ] Cultural values or characteristics
- [ ] Any emotive vocabulary

**Keep:**
- [ ] Repetition for emphasis pattern
- [ ] Simplified clause structure
- [ ] Direct cause-effect patterns
- [ ] Preposition simplification
- [ ] Reduced article complexity
- [ ] Progressive aspect patterns

### 4. USA (`voice/profiles/united_states.yaml`)
**Status:** Original profile, full cleanup needed

**Remove:**
- [ ] ALL signature phrases
- [ ] Innovation/business context references
- [ ] Confidence/optimism markers
- [ ] ROI or performance emotives
- [ ] Cultural characteristics

**Keep:**
- [ ] Direct assertion patterns
- [ ] Active voice preference
- [ ] Shorter sentence structures
- [ ] Present perfect usage patterns
- [ ] Phrasal verb preference
- [ ] Results-oriented structure

## Cleanup Template

### Section 1: Remove Completely
```yaml
# DELETE THESE SECTIONS:
signature_phrases: [...]
cultural_values: [...]
cultural_communication: [...]  # If it contains non-structural content
aesthetic_appreciation: [...]
personal_engagement: [...]
```

### Section 2: Clean Vocabulary
```yaml
# BEFORE:
vocabulary_patterns:
  preferred_terms:
    - "remarkable"
    - "truly exceptional"
    - "beautiful"
    - "one can see"

# AFTER:
vocabulary_patterns:
  neutral_terms:
    - "shows"
    - "indicates"
    - "demonstrates"
    - "measures"
```

### Section 3: Keep Grammar Only
```yaml
# KEEP - This is structural:
grammar_characteristics:
  noticeable_patterns:
    - "Article omission (Surface shows vs The surface shows)"
    - "Word order inversion for emphasis"
    - "Preposition from L1 (depends of vs depends on)"
```

### Section 4: Clean Examples
```yaml
# BEFORE:
example_patterns:
  before_caption:
    - "What strikes one is the remarkable contamination..."

# AFTER:
example_patterns:
  before_caption:
    - "The contamination layer shows thickness 15-25 micrometers."
```

## Implementation Steps

1. **Taiwan Profile**
   - Remove conversational markers
   - Replace "interesting"/"worth mentioning" with neutral structure
   - Keep grammatical patterns only
   - Update examples to be purely technical

2. **Italy Profile**
   - Remove ALL aesthetic vocabulary
   - Delete "strikes one", "beautiful", "elegant", "quality"
   - Keep only structural inversions and pronoun patterns
   - Eliminate personal engagement phrases

3. **Indonesia Profile**
   - Strip environmental context references
   - Remove practical/accessibility emotional content
   - Keep repetition and simplification patterns
   - Update to pure structural description

4. **USA Profile**
   - Remove innovation/business language
   - Delete confidence markers
   - Keep active voice and phrasal verb patterns
   - Focus on structural directness only

## Validation Criteria

Each cleaned profile must:
- [ ] Contain ZERO signature phrases
- [ ] Contain ZERO emotive words (remarkable, beautiful, etc.)
- [ ] Contain ZERO cultural references
- [ ] Contain ONLY grammatical and structural patterns
- [ ] Have examples showing ONLY technical observations
- [ ] Pass YAML validation
- [ ] Generate content without personality markers

## Testing

After cleanup:
```bash
# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('voice/profiles/PROFILE.yaml'))"

# Test generation
python3 -c "
from voice.orchestrator import VoiceOrchestrator
voice = VoiceOrchestrator(country='COUNTRY')
instructions = voice.get_voice_instructions(context='caption_generation')
# Check instructions for emotives
"
```

## Timeline

- Taiwan cleanup: 30 minutes
- Italy cleanup: 30 minutes  
- Indonesia cleanup: 45 minutes (more complex)
- USA cleanup: 45 minutes (more complex)
- Testing: 30 minutes
- **Total: ~3 hours**

---

**Next Action:** Clean Taiwan profile first (already partially updated), then Italy, Indonesia, USA.
