# Voice Architecture Guide

**Created**: December 12, 2025 (Consolidated from 3 source documents)  
**Status**: MANDATORY - Complete reference for voice system architecture  
**Enforcement**: Automated tests + fail-fast architecture

---

## 📚 Document Sources

This consolidated guide combines:
1. **VOICE_VALIDATION_SYSTEM.md** (21 KB) - Voice validation architecture
2. **AUTHOR_ASSIGNMENT_POLICY.md** (3.2 KB) - Author assignment rules
3. **VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md** (7.9 KB) - Voice centralization policy

**Archive Location**: `docs/archive/2025-12/voice-migrations/` and `voice-analysis/`

---

## 🎯 System Overview

The z-beam-generator uses a **comprehensive voice architecture** with:
- **4 distinct author personas** with unique linguistic patterns
- **Post-generation voice validation** (enforces patterns after LLM generates)
- **Centralized voice instructions** (single source of truth)
- **Immutable author assignment** (once assigned, never changes)

### Why This Architecture Exists

**Problem**: LLMs (including Grok-4-fast) often ignore persona instructions during generation, producing homogeneous content regardless of author.

**Solution**: Three-layer approach:
1. **Pre-generation**: Load comprehensive persona with voice markers
2. **Generation**: LLM attempts to follow instructions
3. **Post-generation**: Validate voice patterns, score authenticity, provide recommendations

---

## 👥 Author Registry (Authoritative)

**Source**: `shared/voice/profiles/*.yaml`

| ID | Name | Country | Voice Characteristics |
|----|------|---------|----------------------|
| 1 | Ikmanda Roswati, Ph.D. | Indonesia | Passive constructions, formal tone, demonstrative clusters |
| 2 | Alessandro Moretti, Ph.D. | Italy | Subjunctive mood, hedging language, word order inversion |
| 3 | Yi-Chun Lin, Ph.D. | Taiwan | Topic-comment structure, systematic markers, measurement-first phrasing |
| 4 | Todd Dunning, MA | United States | Phrasal verbs, active voice, direct language |

---

## 🏗️ Architecture Components

### 1. Centralized Voice Instructions (MANDATORY POLICY)

**Core Principle**: ALL voice, tone, and style instructions MUST exist ONLY in persona files.

#### ✅ Single Source of Truth

`shared/voice/profiles/*.yaml` - ONLY location for voice instructions:
```yaml
core_voice_instruction: |
  Complete voice guidance for this author
  
tonal_restraint: |
  Tone and approach instructions
  
linguistic_characteristics:
  - Sentence structure patterns
  - Preferred constructions
  
forbidden:
  direct_address:
    - "you", "your", "you'll"
  conversational_filler:
    - "basically", "actually", "literally"
  theatrical:
    - "crucial", "critical", "essential"
```

#### ❌ Zero Tolerance Violations

**FORBIDDEN in domain prompts** (`domains/*/prompts/*.txt`):
```
❌ "Write in conversational professional English"
❌ "Use active voice (75%)"
❌ "NO conversational tone"
❌ "Mix sentence lengths naturally"
```

**ALLOWED in domain prompts**:
```
✅ Task description ("Write a paragraph describing...")
✅ Content strategy ("Lead with most important consideration")
✅ Structure requirements ("Single paragraph, 5-7 sentences")
✅ Length targets ("80-120 words")
✅ {voice_instruction} placeholder (populated from persona)
```

**Critical Problem Solved**: Domain prompts previously contained contradictory voice instructions (e.g., "NO conversational tone" vs "conversational professional English"), causing LLM to ignore both and produce forbidden phrases in ALL outputs.

---

### 2. Author Assignment & Immutability (MANDATORY POLICY)

**Core Principle**: Once an author is assigned to content, it NEVER changes.

#### Assignment Rules

**Rule 1: NO Author Fallbacks**
```python
# ❌ PROHIBITED
author_id = material_data.get('author', {}).get('id', 2)  # NO DEFAULT

# ✅ REQUIRED
from data.authors.registry import resolve_author_for_generation
author_info = resolve_author_for_generation(material_data)  # Fails if missing
```

**Rule 2: Random Assignment for New Materials**
```python
import random
author_id = random.randint(1, 4)
material_data['author'] = {'id': author_id, 'name': get_author_name(author_id)}
```

**Rule 3: Immutability**
- Author stored in Materials.yaml, Settings.yaml, etc. under `author.id` field
- Generator reads existing author ID from data file
- If no author assigned (new material), randomly assign once, then persist
- **NEVER re-randomize** on regeneration

#### Separation of Concerns

| Component | Responsibility |
|-----------|----------------|
| **Author Personas** (`shared/voice/profiles/*.yaml`) | Define voice characteristics per author |
| **Humanness Optimizer** (`learning/humanness_optimizer.py`) | Structural variation ONLY (rhythm, opening) |
| **Domain Config** (`domains/*/config.yaml`) | Structural randomization (rhythms, structures) NOT voice |

**Grade**: F violation if voice/author changes on regeneration

---

### 3. Voice Validation System (Post-Generation)

**Purpose**: Enforce voice patterns after generation to address LLM non-compliance.

#### Three-Layer Quality Analysis

```
┌─────────────────────────────────────────────────────────────┐
│                    QualityAnalyzer                          │
│              (Unified Quality Assessment)                    │
│                                                              │
│  ┌────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │  AI Pattern    │  │ Voice            │  │ Structural   ││
│  │  Detection     │  │ Authenticity     │  │ Quality      ││
│  │                │  │                  │  │              ││
│  │ • Grammar      │  │ • Language       │  │ • Sentence   ││
│  │ • Phrasing     │  │   detection      │  │   variation  ││
│  │ • Repetition   │  │ • Translation    │  │ • Rhythm     ││
│  │ • Statistical  │  │   artifacts      │  │ • Complexity ││
│  │   patterns     │  │ • Linguistic     │  │   variation  ││
│  │                │  │   patterns       │  │              ││
│  └────────────────┘  └──────────────────┘  └──────────────┘│
│                                                              │
│  Result: Overall Score (0-100) + Recommendations            │
└─────────────────────────────────────────────────────────────┘
```

#### VoicePostProcessor (`shared/voice/post_processor.py`)

**Core Methods**:

##### `detect_language(text)` → Dict
Detects if text is in English or another language.
```python
Returns:
{
    'language': str,      # 'english', 'indonesian', 'italian', etc.
    'confidence': float,  # 0-1
    'indicators': List[str]  # Words that triggered detection
}
```

##### `detect_translation_artifacts(text)` → Dict
Identifies translation artifacts indicating poor voice application.
```python
Detects:
- Reduplication: "very-very", "clean-clean" (Indonesian-style)
- Excessive conjunctions: "then...then...then"
- Repetitive sentence starters

Returns:
{
    'has_artifacts': bool,
    'artifact_count': int,
    'patterns_found': List[Dict],
    'severity': str  # 'none', 'minor', 'moderate', 'severe'
}
```

##### `detect_linguistic_patterns(text, author)` → Dict
Detects country-specific linguistic patterns.

**USA (Todd Dunning)**:
- Phrasal verbs: "set up", "carry out", "figure out"
- Active voice dominance (75%+)
- American spelling: "color", "analyze"

**Taiwan (Yi-Chun Lin)**:
- Topic-comment structure: "Material properties, these determine..."
- Article omissions: "Surface becomes contaminated"
- Systematic markers: "firstly", "specifically"

**Italy (Alessandro Moretti)**:
- Subjunctive influence: "it seems", "would appear"
- Word order inversion: adjectives before nouns
- Emphatic pronouns

**Indonesia (Ikmanda Roswati)**:
- Passive constructions: "is formed", "are used"
- Demonstrative clusters: "this material", "these properties"
- Serial verbs, paratactic structure

```python
Returns:
{
    'pattern_score': float (0-100),
    'patterns_found': List[str],
    'pattern_quality': str,  # 'authentic', 'weak', 'absent'
    'linguistic_issues': List[str]
}
```

##### `score_voice_authenticity(text, author, voice_indicators, mode)` → Dict
Scores voice authenticity based on linguistic patterns.

**Modes**:
- `strict`: Requires strong pattern presence (70%+ score)
- `moderate`: Accepts weak patterns (40%+ score)
- `lenient`: Accepts minimal patterns (20%+ score)

```python
Returns:
{
    'authenticity_score': float (0-100),
    'authenticity_level': str,  # 'strong', 'moderate', 'weak', 'absent'
    'pattern_count': int,
    'recommendations': List[str]
}
```

---

## 🧪 Testing & Verification

### Test Suite: `tests/test_example_free_voice_distinctiveness.py`

**11 tests covering**:
1. **Voice marker detection** (4 tests - one per author)
   - Taiwan: Topic-comment structure
   - Italy: Subjunctive/hedging
   - USA: Phrasal verbs
   - Indonesia: Passive constructions

2. **Vocabulary diversity** (1 test)
   - <40% vocabulary overlap across authors

3. **Template independence** (1 test)
   - No repetitive structural patterns

4. **Cross-domain reusability** (2 tests)
   - Materials and contaminants use same system

5. **Architecture validation** (3 tests)
   - Voice ≥30% of prompt
   - Zero hardcoded examples
   - Voice-dominant architecture

### Test Contaminants (4 items, all authors represented)

| Contaminant | Author | ID | Voice Markers |
|-------------|--------|----|----|
| adhesive-residue | Yi-Chun Lin (Taiwan) | 3 | Topic-comment |
| aluminum-oxidation | Alessandro Moretti (Italy) | 2 | Subjunctive |
| copper-patina | Todd Dunning (USA) | 4 | Phrasal verbs |
| rust-oxidation | Ikmanda Roswati (Indonesia) | 1 | Passive voice |

---

## 📊 Voice Validation Pipeline

### Generation Flow

```
1. Load Material/Item Data
   ├─→ Read author.id from data file
   └─→ FAIL if author missing (no fallback)

2. Load Persona
   ├─→ Read shared/voice/profiles/{country}.yaml
   ├─→ Extract core_voice_instruction (full text)
   └─→ Prepare {voice_instruction} placeholder

3. Build Prompt
   ├─→ Load domain template (domains/*/prompts/*.txt)
   ├─→ Render {voice_instruction} with persona text
   ├─→ Add facts, context (NO voice instructions here)
   └─→ Final prompt: 35% voice, 65% technical

4. Generate Content
   ├─→ Call LLM (Grok, Claude, etc.)
   ├─→ Apply temperature/penalties from dynamic config
   └─→ Receive generated text

5. Post-Generation Validation
   ├─→ VoicePostProcessor.detect_language(text)
   ├─→ VoicePostProcessor.detect_translation_artifacts(text)
   ├─→ VoicePostProcessor.detect_linguistic_patterns(text, author)
   ├─→ VoicePostProcessor.score_voice_authenticity(text, author)
   └─→ QualityAnalyzer.analyze_quality(text) → Overall score

6. Learning & Feedback
   ├─→ Log attempt to database (Winston, Realism, Voice scores)
   ├─→ If voice score low: Add to feedback for next attempt
   ├─→ Parameter adjustments (temp, penalties)
   └─→ Save to Materials.yaml (preserves author.id)
```

---

## 🎯 Quality Gates

### Voice Validation Thresholds

**Strict Mode** (production):
- Voice authenticity: ≥70/100
- Language: Must be English
- Translation artifacts: Severity ≤ minor
- Linguistic patterns: ≥5 patterns detected

**Moderate Mode** (development):
- Voice authenticity: ≥40/100
- Language: Must be English
- Translation artifacts: Severity ≤ moderate
- Linguistic patterns: ≥3 patterns detected

**Lenient Mode** (testing):
- Voice authenticity: ≥20/100
- Language: Must be English
- Translation artifacts: Severity ≤ severe
- Linguistic patterns: ≥1 pattern detected

### Overall Quality Score

Composite from:
- **AI Pattern Detection** (30%): Grammar, phrasing, repetition
- **Voice Authenticity** (40%): Linguistic patterns, author markers
- **Structural Quality** (30%): Sentence variation, rhythm, complexity

**Minimum score**: 60/100 for production content

---

## 🔧 Implementation Examples

### Correct Author Loading

```python
# ✅ CORRECT - Fail-fast, no fallbacks
from data.authors.registry import resolve_author_for_generation

def generate_content(material_name: str):
    material_data = load_material(material_name)
    
    # Fails with clear error if author missing
    author_info = resolve_author_for_generation(material_data)
    
    # Load persona from single source of truth
    persona = load_persona(author_info['id'])
    
    # Generate with voice instructions
    result = generator.generate(
        material_name=material_name,
        author_id=author_info['id'],
        persona=persona
    )
    
    return result
```

### Voice Validation Example

```python
# Post-generation validation
from shared.voice.post_processor import VoicePostProcessor

processor = VoicePostProcessor()

# Validate voice authenticity
validation = processor.score_voice_authenticity(
    text=generated_text,
    author={'id': 3, 'name': 'Yi-Chun Lin', 'country': 'Taiwan'},
    voice_indicators=persona['linguistic_characteristics'],
    mode='strict'
)

if validation['authenticity_score'] < 70:
    # Low voice score - provide feedback
    print(f"⚠️  Voice score: {validation['authenticity_score']}/100")
    print(f"   Patterns found: {validation['pattern_count']}")
    for rec in validation['recommendations']:
        print(f"   • {rec}")
    
    # Log for learning system
    log_voice_feedback(material_name, validation)
```

---

## 📈 Example-Free Architecture

**Voice Dominance**: Voice instructions now represent 35% of prompt (was 23%).

**How Achieved**:
1. **Removed examples**: No 300-char description examples in prompts
2. **Removed example_facts fallback**: No fallback text when facts empty
3. **Removed text fields from context**: Only category for classification

**Result**: Voice instructions can dominate, reducing template copying behavior.

---

## 🚨 Common Issues & Solutions

### Issue 1: Homogeneous Content Across Authors

**Symptom**: All 4 authors produce identical text with same forbidden phrases.

**Cause**: Voice instructions scattered across multiple files, creating conflicts that LLM ignores.

**Solution**: 
- ✅ Consolidate ALL voice instructions into personas/*.yaml
- ✅ Remove voice instructions from domain prompts
- ✅ Use only {voice_instruction} placeholder in prompts

### Issue 2: Translation Artifacts

**Symptom**: Text contains "very-very", "high-high" (Indonesian reduplication).

**Cause**: LLM applying Indonesian linguistic patterns to English content.

**Solution**:
- ✅ Post-generation detection catches this
- ✅ Provide feedback to learning system
- ✅ Adjust temperature/penalties for next attempt

### Issue 3: Weak Voice Markers

**Symptom**: Voice authenticity score <40/100, few linguistic patterns detected.

**Cause**: LLM ignoring persona instructions during generation.

**Solution**:
- ✅ Post-generation validation catches this
- ✅ Provide recommendations for improvement
- ✅ Consider switching LLM provider (Claude vs Grok)

### Issue 4: Author Changes on Regeneration

**Symptom**: Material has different author after regeneration.

**Cause**: Violation of immutability policy.

**Solution**:
- ✅ Verify author.id preserved in Materials.yaml
- ✅ Check no random re-assignment in generator
- ✅ Fail-fast if author missing (no fallback to random)

---

## 📚 Related Documentation

**Policies** (in docs/08-development/):
- `PROMPT_PURITY_POLICY.md` - No prompt text in code
- `TEMPLATE_ONLY_POLICY.md` - Only templates define content
- `EXAMPLE_FREE_ARCHITECTURE.md` - Voice-dominant prompts

**Architecture** (in docs/02-architecture/):
- `processing-pipeline.md` - Complete generation flow
- `DOMAIN_INDEPENDENCE_POLICY.md` - Cross-domain reusability

**Data** (in docs/05-data/):
- `DATA_STORAGE_POLICY.md` - Where author.id is stored

---

## ✅ Verification Checklist

Before deploying changes:

- [ ] All voice instructions in `shared/voice/profiles/*.yaml`
- [ ] No voice instructions in domain prompts
- [ ] No voice instructions in generation code
- [ ] Author assignment uses `resolve_author_for_generation()`
- [ ] No author fallbacks or defaults
- [ ] Post-generation validation active
- [ ] Test suite passing (11/11 tests)
- [ ] Example-free architecture maintained (voice ≥30%)

---

## 📊 Success Metrics

**Architecture**:
- ✅ Voice centralization: 100% compliant
- ✅ Author immutability: Enforced in pipeline
- ✅ Post-generation validation: Active and scoring

**Quality**:
- ⚠️ Voice distinctiveness: 0/100 (LLM ignores instructions)
- ✅ Detection system: Working (catches homogeneous content)
- ✅ Feedback system: Logging issues for improvement

**Recommendation**: Consider switching from Grok-4-fast to Claude or GPT-4 for better persona compliance.

---

**Last Updated**: December 12, 2025  
**Maintainer**: Voice System Team  
**Questions**: See root `DOCUMENTATION_MAP.md` for navigation
