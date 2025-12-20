# Prompt Chain Separation of Concerns Policy
**Date**: December 14, 2025  
**Status**: MANDATORY - Strict enforcement  
**Grade**: F violation if any overlap occurs

---

## 🎯 Core Principle

**Each layer in the prompt chain must be completely DRY (Don't Repeat Yourself) and specific to its concern.**

NO overlap between layers. NO duplication of instructions. NO contradictions.

---

## 📋 The Four Layers

### **Layer 1: Component Length Configuration** (`generation/config.yaml`)
**Purpose**: Define BASE word count targets (technical configuration)

**ONLY Contains**:
- Base word count numbers: `description: 100`
- Extraction strategies: `extraction_strategy: raw`
- Technical settings ONLY

**FORBIDDEN**:
- ❌ Content instructions ("describe formation and behavior")
- ❌ Voice instructions ("use topic-comment structures")
- ❌ Style guidance ("be conversational")
- ❌ Formatting requirements ("use 2 paragraphs")

**Example**:
```yaml
component_lengths:
  description: 100        # Base target (variation applied separately)
  micro: 80
  faq: 50
```

---

### **Layer 2: Domain Prompts** (`domains/*/prompts/*.txt`)
**Purpose**: Define WHAT content to generate (subject matter ONLY)

**ONLY Contains**:
- Content requirements (topics to cover)
- Domain-specific context
- What information to include
- Placeholder: `{voice_instruction}`

**FORBIDDEN**:
- ❌ Length specifications ("90-110 words", "2-3 sentences")
- ❌ Voice instructions ("use EFL patterns", "vary sentence length")
- ❌ Style guidance ("be formal", "use technical tone")
- ❌ Structural variation ("alternate short/long sentences")

**Example**:
```plaintext
CONTENT REQUIREMENTS (WHAT to say):
Describe this contamination pattern covering:
1. What it is and how it forms
2. Unique characteristics
3. Behavior on different materials
4. Key challenges for removal

{voice_instruction}
```

---

### **Layer 3: Voice Profiles** (`shared/voice/profiles/*.yaml`)
**Purpose**: Define HOW to write (voice characteristics ONLY)

**ONLY Contains**:
- Linguistic patterns (topic-comment, article omission, etc.)
- Vocabulary preferences (connectors, markers)
- Tonal characteristics (formal, systematic)
- Grammar norms (parataxis, stative verbs)

**FORBIDDEN**:
- ❌ Content requirements ("describe formation process")
- ❌ Length targets ("90-110 words", "13-19 words per sentence")
- ❌ Structural variation patterns (handled by humanness)
- ❌ Word count distributions ("25% short, 50% medium")

**Example**:
```yaml
core_voice_instruction: |
  Formulate formal English: Balance active/passive for clarity.
  Embed Mandarin EFL traits (1-2 per paragraph):
  - Topic-comment word order
  - Selective article omission
  - Temporal sequence markers
  - Aspect markers ("already", "still")
  
  Use paratactic chaining ("and", "thus", "so").
  Prefer stative verbs and noun-heavy constructions.
```

---

### **Layer 4: Humanness Layer** (`learning/humanness_optimizer.py`)
**Purpose**: Provide STRUCTURAL variation (rhythm & diversity ONLY)

**ONLY Contains**:
- Sentence rhythm patterns (mixed cadence, balanced)
- Opening strategies (direct, context-setting, challenge-first)
- Structural approaches (problem-focused, formation process)
- Anti-AI pattern breaking (vary openings, mix lengths)

**FORBIDDEN**:
- ❌ Content requirements ("describe removal challenges")
- ❌ Voice characteristics ("use EFL patterns")
- ❌ Exact length targets ("must be 100 words")
- ❌ Tonal guidance ("be formal", "be systematic")

**Example**:
```
STRUCTURAL VARIATION (rhythm ONLY):
- Opening: Challenge-First (state main problem first)
- Rhythm: MIXED CADENCE (alternate short and long sentences)
- NO content instructions - structure only
```

---

## 🚫 Common Violations

### ❌ Violation 1: Length in Multiple Layers
```
generation/config.yaml: description: 100
domain prompt: LENGTH: 90-110 words
voice profile: Vary lengths: 25% short (<11 words), 50% medium (11-17)
```
**Impact**: AI receives 3+ conflicting length targets → confusion → rigid output

**Fix**: Length target ONLY in `generation/config.yaml`, variation applied automatically

---

### ❌ Violation 2: Content in Voice Profiles
```yaml
# voice profile
voice_examples:
  - "Describe formation process then removal challenges"
```
**Impact**: Voice profile defining WHAT to say (domain prompt's job)

**Fix**: Voice examples show HOW to write, not WHAT to write about

---

### ❌ Violation 3: Voice in Domain Prompts
```plaintext
# domain prompt
STYLE: Use topic-comment structures and article omission
```
**Impact**: Domain prompt defining HOW to write (voice profile's job)

**Fix**: Remove ALL voice/style instructions, use `{voice_instruction}` placeholder

---

### ❌ Violation 4: Content in Humanness Layer
```python
# humanness layer
opening = "Explain how contamination forms and removal methods"
```
**Impact**: Structural layer defining WHAT to say (domain prompt's job)

**Fix**: Humanness only defines STRUCTURE ("challenge-first opening"), not content

---

## ✅ Correct Flow

```
1. generation/config.yaml
   ↓ Base: description = 100 words
   
2. Length calculator applies variation
   ↓ Range: 30-170 words (±70%)
   
3. Domain prompt receives calculated range
   ↓ "Target: 30-170 words" + content requirements
   
4. Voice profile applied
   ↓ Voice characteristics: EFL patterns, connectors, tone
   
5. Humanness layer adds variation
   ↓ Structural diversity: rhythm, opening, approach
   
6. Final prompt sent to LLM
   ↓ Complete instructions with NO contradictions
```

---

## 📊 Verification Checklist

Before ANY prompt/configuration change:

- [ ] **Layer 1 (config.yaml)**: Only base numbers and technical settings?
- [ ] **Layer 2 (domain prompts)**: Only content requirements (WHAT to say)?
- [ ] **Layer 3 (voice profiles)**: Only voice characteristics (HOW to say)?
- [ ] **Layer 4 (humanness)**: Only structural variation (rhythm, openings)?
- [ ] **No overlap**: Each instruction appears in exactly ONE layer?
- [ ] **No contradictions**: No conflicting instructions across layers?

---

## 🎯 Benefits

1. ✅ **No AI confusion** - Clear, non-contradictory instructions
2. ✅ **DRY principle** - Each concern defined once, in right place
3. ✅ **Easy maintenance** - Change length → edit config ONLY
4. ✅ **Quality improvement** - AI produces natural, varied output
5. ✅ **Debugging easier** - Know exactly where to look for issues

---

## 🚨 Enforcement

**Grade**: F violation if ANY of these occur:
- Length specifications in domain prompts or voice profiles
- Content requirements in voice profiles or humanness layer
- Voice instructions in domain prompts or config files
- Multiple layers defining same aspect (e.g., sentence length)

**Validation**: Automated tests check for overlap
**Code Review**: Mandatory check before merging prompt changes

---

**Status**: MANDATORY (December 14, 2025)  
**Compliance**: 100% required for all prompt chain components
