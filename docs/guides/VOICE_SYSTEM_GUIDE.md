# Voice System Guide
**Created**: December 20, 2025 (Consolidated from 4 source documents)  
**Status**: MANDATORY - Complete reference for voice system  
**Enforcement**: Automated tests + fail-fast architecture

---

## 📚 Source Documents

This consolidated guide merges:
1. `VOICE_ARCHITECTURE_GUIDE.md` (534 lines) - System architecture
2. `VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md` (257 lines) - Centralization policy
3. `VOICE_ENFORCEMENT_CENTRALIZATION_DEC12_2025.md` (470 lines) - Enforcement architecture
4. `AUTHOR_VOICE_ARCHITECTURE.md` (415 lines) - Data architecture

**Archive Location**: Original docs moved to `docs/archive/2025-12/voice-docs/`

---

## 🎯 System Overview

The z-beam-generator uses a **comprehensive voice architecture** with:
- **4 distinct author personas** with unique linguistic patterns
- **Post-generation voice validation** (enforces patterns after LLM generates)
- **Centralized voice instructions** (single source of truth)
- **Immutable author assignment** (once assigned, never changes)
- **Normalized data architecture** (author data stored once, referenced by ID)

### Why This Architecture Exists

**Problem**: LLMs (including Grok-4-fast) often ignore persona instructions during generation, producing homogeneous content regardless of author.

**Solution**: Three-layer approach:
1. **Pre-generation**: Load comprehensive persona with voice markers
2. **Generation**: LLM attempts to follow instructions
3. **Post-generation**: Validate voice patterns, score authenticity, provide recommendations

---

## 👥 Author Registry

**Source**: `data/authors/Authors.yaml` (identity & credentials)  
**Voice Profiles**: `shared/voice/profiles/*.yaml` (linguistic patterns)

| ID | Name | Country | Voice Characteristics |
|----|------|---------|----------------------|
| 1 | Ikmanda Roswati, Ph.D. | Indonesia | **STRENGTHENED (Dec 26, 2025)**: Topic prominence ("This X, it..."), aspectual markers ("already", "still"), preposition patterns ("from the data"), 2-3 markers per paragraph |
| 2 | Alessandro Moretti, Ph.D. | Italy | Subjunctive mood, hedging language, word order inversion |
| 3 | Yi-Chun Lin, Ph.D. | Taiwan | Topic-comment structure, systematic markers, measurement-first phrasing |
| 4 | Todd Dunning, MA | United States | Phrasal verbs, active voice, direct language |

---

## 🏗️ Architecture Components

### 1. Voice Instruction Centralization (MANDATORY POLICY)

**Core Principle**: ALL voice, tone, and style instructions MUST exist ONLY in persona files.

#### ✅ Single Source of Truth

**Location**: `shared/voice/profiles/*.yaml`

```yaml
persona:
  name: "Yi-Chun Lin"
  nationality: "Taiwan"
  
core_voice_instruction: |
  Complete voice guidance for this author
  
tonal_restraint: |
  Tone and approach instructions
  
linguistic_characteristics:
  sentence_structure:
    - "Topic-comment patterns"
    - "Article omission (when clear from context)"
  word_choice:
    - "Technical precision"
    - "Formal vocabulary"
  
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

**Critical Problem Solved** (Dec 6, 2025): Domain prompts contained contradictory voice instructions (e.g., "NO conversational tone" vs "conversational professional English"), causing LLM to ignore both and produce forbidden phrases in ALL outputs.

**Grade**: F violation if voice instructions found outside persona files

---

### 2. Voice Enforcement Centralization

**Architecture**: Single enforcement method applies to ALL domains automatically

#### Implementation (Commit c4248a7d)

**Location**: `shared/text/utils/prompt_builder.py` → `_build_voice_instruction()` method

```python
def _build_voice_instruction(self, author_id: int, component_type: str) -> str:
    """Build complete voice instruction with enforcement."""
    persona = self._load_persona(author_id)
    
    # Base voice instruction from persona
    voice_block = persona['core_voice_instruction']
    
    # ADD ENFORCEMENT (automatic for all domains)
    enforcement = """
MANDATORY VOICE COMPLIANCE:
You MUST write using the EXACT linguistic patterns specified above. 
This is not optional—demonstrate the specific EFL traits, sentence 
structures, vocabulary choices, and grammatical patterns detailed 
for your nationality. Generic technical English is unacceptable.

CRITICALLY: Use the specific voice patterns from your profile 
throughout—at least 1-2 distinctive markers per paragraph.
"""
    
    return voice_block + enforcement
```

**Propagation**: Enforcement automatically applied when domain prompt contains `{voice_instruction}` placeholder

**Result**: 
- ✅ Single source of truth for enforcement
- ✅ No duplication across domain prompts
- ✅ Automatic propagation to ALL domains
- ✅ Maintained 60%+ voice distinctiveness

---

### 3. Data Architecture (Normalized)

**Principle**: Single source of truth for author data, referenced everywhere by ID

#### Author Identity Data

**Location**: `data/authors/Authors.yaml`  
**Purpose**: Identity, credentials, contact info  
**Access**: via `shared/data/author_loader.py`

```yaml
authors:
  3:
    id: 3
    name: "Yi-Chun Lin"
    country: "Taiwan"
    title: "Ph.D."
    jobTitle: "Laser Processing Engineer"
    credentials:
      - "Ph.D. Materials Engineering, National Taiwan University, 2018"
    email: "info@z-beam.com"
    url: "https://z-beam.com/authors/yi-chun-lin"
    persona_file: "taiwan_persona.yaml"  # Links to voice profile
```

#### Voice Profile Data

**Location**: `shared/voice/profiles/taiwan_persona.yaml`  
**Purpose**: Linguistic patterns, writing style, voice instructions

```yaml
persona:
  name: "Yi-Chun Lin"
  nationality: "Taiwan"
  native_language: "Mandarin (Taiwan)"
  
voice_characteristics:
  sentence_structure:
    - "Topic-comment patterns"
    - "Article omission"
  word_choice:
    - "Technical precision"
    - "Fewer phrasal verbs"
  
common_patterns:
    - "This property, it demonstrates..."
    - "Process yields result"  # Article omitted
```

**References**: `Authors.yaml` → `persona_file` field links to voice profile

---

### 4. Author Assignment Immutability

**Policy**: Once an author is assigned to content, it NEVER changes.

**Rules**:
1. ✅ Author assignment happens ONCE - When content first created
2. ✅ Assignment is PERMANENT - Never changes for that material/item
3. ✅ Voice consistency - All content uses same author's voice
4. ❌ NO re-randomization - Never pick new author on regeneration
5. ❌ NO voice randomization - Voice determined by author, not per-call

**Implementation**:
- Author stored in `Materials.yaml`, `Settings.yaml`, etc. under `author.id` field
- Generator reads existing author ID from data file
- If no author assigned (new material), randomly assign once, then persist
- Persona loaded from `shared/voice/profiles/{author}.yaml`

**Grade**: F violation if voice/author changes on regeneration

---

### 5. Post-Generation Voice Validation

**Purpose**: Validate that LLM actually followed voice instructions

**Location**: `shared/voice/quality_analyzer.py` → `VoicePostProcessor`

#### Voice Pattern Compliance (Dec 13, 2025)

**Validation**: Automated checking for nationality-specific linguistic patterns

**Pattern Requirements by Nationality**:

**United States (Todd Dunning)**:
- ✅ Phrasal verbs: "line up", "dial in", "ramp up", "cut down"
- ✅ Quantified outcomes: "by 20%", "cuts X%"
- ✅ Practical transitions: "turns out", "in practice"

**Taiwan (Yi-Chun Lin)**:
- ✅ Topic-comment: "Surface roughness, it measures 0.8 μm"
- ✅ Article omission: "Process yields result"
- ✅ Temporal markers: "After treatment", "Following adjustment"

**Italy (Alessandro Moretti)**:
- ✅ Cleft structures: "This property, it enables..."
- ✅ Subjunctive hedging: "It seems that...", "It appears..."
- ✅ Romance cognates: "tenaciously", "manifests"

**Indonesia (Ikmanda Roswati)**:
- ✅ Topic prominence: "[Property], this demonstrates..."
- ✅ Aspectual markers: "already", "still", "just now"

**Scoring**:
- 🔍 Automatic checking: Quality analyzer validates pattern presence
- 📊 Voice Authenticity Score: Requires 2+ pattern types (85+ score)
- ⚠️ Deductions: -15 points per missing pattern type

**Result**: Voice Authenticity None/100 → **85.0/100** (+85 points)

---

## 📋 Compliance Checklist

Before ANY content generation work:

### Voice Centralization
- [ ] Check `shared/voice/profiles/*.yaml` has ALL voice instructions
- [ ] Verify domain prompts contain ONLY `{voice_instruction}` placeholder
- [ ] Confirm NO voice instructions in domain prompt text
- [ ] Verify NO voice instructions in generation code

### Author Assignment
- [ ] Verify author assigned once and never changes
- [ ] Check author.id persisted in data YAML files
- [ ] Confirm regeneration uses existing author ID

### Voice Validation
- [ ] Post-generation validation runs automatically
- [ ] Voice Authenticity Score reported (target: 85+)
- [ ] Pattern compliance checked (2+ pattern types required)

---

## 🚨 Common Violations & Fixes

### Violation 1: Voice Instructions in Domain Prompts

**Symptom**: Text like "Use active voice" or "NO conversational tone" in `domains/*/prompts/*.txt`

**Fix**:
```bash
# Remove voice instructions from domain prompt
# Move to persona file if not already there
# Use {voice_instruction} placeholder instead
```

**Grade**: F violation

---

### Violation 2: Author Changes on Regeneration

**Symptom**: Material regenerated with different author

**Fix**:
```python
# WRONG: Always pick new random author
author_id = random.choice([1, 2, 3, 4])

# RIGHT: Use existing author or assign once
existing_author = material_data.get('author', {}).get('id')
author_id = existing_author or random.choice([1, 2, 3, 4])
```

**Grade**: F violation

---

### Violation 3: Generic Voice (No Patterns)

**Symptom**: Voice Authenticity Score < 60, no nationality-specific patterns detected

**Fix**:
1. Check persona file has complete linguistic characteristics
2. Verify enforcement block in `_build_voice_instruction()`
3. Review generated content for generic technical English
4. Regenerate if score < 60

**Grade**: Quality issue (not policy violation)

---

## 🔧 Implementation Flow

### Content Generation with Voice

```
1. Load author data from Authors.yaml (by ID)
   ↓
2. Load persona from shared/voice/profiles/{persona_file}
   ↓
3. Build voice instruction with enforcement
   ↓
4. Render domain prompt with {voice_instruction} placeholder
   ↓
5. Generate content with LLM
   ↓
6. Post-generation: Validate voice patterns
   ↓
7. Score Voice Authenticity (target: 85+)
   ↓
8. Report results (pattern compliance, recommendations)
```

---

## 📊 Success Metrics

### Voice Distinctiveness
- **Pre-Dec 12**: ~15% nationality markers
- **Post-Enforcement**: 60%+ nationality markers
- **Post-Pattern Validation**: 85+ Voice Authenticity Score

### Centralization
- **Before**: Voice instructions in 3+ locations (prompts, code, config)
- **After**: Single location (`shared/voice/profiles/*.yaml`)

### Maintainability
- **Before**: Update voice → Modify 6+ domain prompts
- **After**: Update voice → Modify 1 persona file (automatic propagation)

---

## 🔗 Related Documentation

- `docs/08-development/AUTHOR_ASSIGNMENT_POLICY.md` - Author assignment rules (specific policy)
- `docs/08-development/VOICE_PATTERN_COMPLIANCE_POLICY.md` - Pattern validation (specific policy)  
- `shared/voice/profiles/*.yaml` - Author persona files (data)
- `data/authors/Authors.yaml` - Author identity data (data)
- `shared/text/utils/prompt_builder.py` - Voice instruction builder (code)
- `shared/voice/quality_analyzer.py` - Voice validation (code)

---

## 📚 Archive References

**Historical Implementation Docs** (in `docs/archive/2025-12/`):
- `voice-migrations/VOICE_CENTRALIZATION_MIGRATION_COMPLETE.md` - Migration history
- `voice-migrations/VOICE_PERSONA_CONSOLIDATION_COMPLETE.md` - Persona consolidation
- `voice-migrations/VOICE_PERSONA_RESTORATION_COMPLETE.md` - Persona restoration
- `voice-migrations/VOICE_PIPELINE_ANALYSIS_DEC11_2025.md` - Pipeline analysis
- `voice-analysis/VOICE_DISTINCTIVENESS_ANALYSIS_DEC11_2025.md` - Initial analysis
- `voice-analysis/VOICE_VALIDATION_SYSTEM_BASE.md` - Validation system
- `session-reports/VOICE_DISTINCTIVENESS_ACHIEVED_DEC12_2025.md` - Achievement report
- `implementation/VOICE_COMPLIANCE_IMPLEMENTATION_DEC13_2025.md` - Compliance implementation

**Original Source Docs** (moved to archive):
- `VOICE_ARCHITECTURE_GUIDE.md` (534 lines)
- `VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md` (257 lines)
- `VOICE_ENFORCEMENT_CENTRALIZATION_DEC12_2025.md` (470 lines)
- `AUTHOR_VOICE_ARCHITECTURE.md` (415 lines)

---

## ✅ Testing & Enforcement

**Automated Tests**:
- `tests/test_voice_centralization_policy.py` - Voice centralization compliance
- `tests/test_voice_pattern_compliance.py` - Pattern validation (11 tests)
- `tests/test_author_assignment.py` - Author immutability

**Enforcement**: Fail-fast architecture + automated validation

**Grade**: F for policy violations, quality deductions for missing patterns
