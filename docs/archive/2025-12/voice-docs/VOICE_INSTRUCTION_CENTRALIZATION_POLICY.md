# Voice Instruction Centralization Policy

**Created**: December 6, 2025  
**Status**: MANDATORY - Grade F violation if not followed  
**Enforcement**: Automated tests in `tests/test_voice_centralization_policy.py`

---

## 🎯 Core Principle

**ALL voice, tone, and style instructions MUST exist ONLY in persona files.**

**Zero tolerance** for voice instructions in:
- ❌ Domain prompt templates (`domains/*/prompts/*.txt`)
- ❌ Generation code (`generation/**/*.py`, `processing/**/*.py`)
- ❌ Configuration files (`config.yaml`, domain-specific configs)
- ❌ Shared templates outside persona directory

**Single source of truth**: `shared/voice/profiles/*.yaml`

---

## 🚨 Critical Problem Solved

**Issue Discovered**: December 6, 2025
- Domain prompts contained contradictory voice instructions
- `description.txt` said: "NO conversational tone"
- Persona files said: "conversational professional English"
- LLM (Grok-4-fast) received conflicting instructions → ignored both
- Result: All 4 authors produced identical forbidden phrases ("you'll want to")

**Root Cause**: Voice instructions scattered across multiple files creating architectural conflicts.

---

## ✅ What IS Allowed

### Persona Files (`shared/voice/profiles/*.yaml`)
**ONLY location for voice instructions:**
- ✅ `core_voice_instruction` - Complete voice guidance
- ✅ `tonal_restraint` - Tone and approach
- ✅ `linguistic_characteristics` - Writing style patterns
- ✅ `forbidden.direct_address` - Prohibited phrases (you, your, you'll)
- ✅ `forbidden.conversational_filler` - Prohibited casual language
- ✅ `forbidden.theatrical` - Prohibited dramatic language
- ✅ `style_patterns` - Sentence structure and rhythm guidance

### Domain Prompts (`domains/*/prompts/*.txt`)
**Technical instructions ONLY:**
- ✅ Task description ("Write a paragraph describing...")
- ✅ Content strategy ("Lead with most important consideration")
- ✅ Structure requirements ("Single paragraph, 5-7 sentences")
- ✅ Length targets ("80-120 words")
- ✅ Forbidden patterns (generic advice, lists, questions)
- ✅ Context-specific terminology ("laser cleaning" not "machining")
- ✅ `{voice_instruction}` placeholder (populated from persona)

### Generation Code
**Mechanism ONLY:**
- ✅ Load persona file
- ✅ Render `{voice_instruction}` placeholder
- ✅ Pass complete persona to prompt builder
- ✅ Technical parameter application (temperature, penalties)

---

## ❌ What is FORBIDDEN

### Voice Instruction Violations (Grade F)

**Domain Prompts - FORBIDDEN**:
```
❌ "Write in conversational professional English"
❌ "Use active voice (75%)"
❌ "MANDATORY VOICE COMPLIANCE: NO direct address"
❌ "NO conversational tone"
❌ "Write like you're explaining to a colleague"
❌ "Use active voice and conversational tone"
❌ "Mix sentence lengths naturally"
```

**Generation Code - FORBIDDEN**:
```python
❌ system_prompt = "Write in conversational style..."
❌ prompt += "\nUse active voice and direct phrasing"
❌ voice_style = "conversational" if component == "faq" else "formal"
```

**Config Files - FORBIDDEN**:
```yaml
❌ voice_style: conversational
❌ tone: professional_conversational
❌ forbidden_phrases: ["you", "your", "you'll"]
```

---

## 📋 Compliance Checklist

Before ANY content generation work:

- [ ] **Personas**: All voice instructions in `shared/voice/profiles/*.yaml`
- [ ] **Domain prompts**: ONLY `{voice_instruction}` placeholder, no voice rules
- [ ] **Generation code**: ONLY loads persona, no voice instructions
- [ ] **Config files**: ONLY technical parameters, no voice guidance
- [ ] **Tests**: Verify zero voice instructions outside personas

---

## 🔧 Migration Guide

### Removing Voice Instructions from Domain Prompts

**BEFORE** (description.txt - WRONG):
```
VOICE STYLE:
{voice_instruction}

MANDATORY VOICE COMPLIANCE:
- NO direct address: Never use "you", "your", "you'll"
- NO conversational tone: Professional technical documentation only
```

**AFTER** (description.txt - CORRECT):
```
VOICE STYLE:
{voice_instruction}

[All voice rules removed - handled by persona]
```

**BEFORE** (component_summary.txt - WRONG):
```
=== VOICE STYLE ===
Write in conversational professional English. Use active voice (75%).
```

**AFTER** (component_summary.txt - CORRECT):
```
VOICE STYLE:
{voice_instruction}

[All voice guidance removed - handled by persona]
```

---

## 🎯 Benefits

1. **No Conflicts**: Single source of truth prevents contradictory instructions
2. **Voice Distinctiveness**: Each author's unique voice unimpaired by domain overrides
3. **Maintainability**: Voice changes in ONE place (persona file)
4. **Testability**: Can verify voice compliance against single authoritative source
5. **LLM Clarity**: No confused instructions → better generation quality

---

## 📊 Enforcement

### Automated Tests
File: `tests/test_voice_centralization_policy.py`

**Checks**:
1. ✅ Domain prompts contain ONLY `{voice_instruction}` placeholder
2. ✅ Domain prompts have ZERO voice instruction keywords
3. ✅ Generation code has ZERO hardcoded voice instructions
4. ✅ Config files have ZERO voice/tone settings

**Keywords Flagged**:
- "conversational tone", "active voice", "professional style"
- "Write like", "tone:", "voice style"
- "MANDATORY VOICE", "forbidden phrases"
- Any `forbidden.` lists outside persona files

### Manual Review
**Before PR merge, verify**:
- [ ] `grep -r "conversational tone" domains/*/prompts/*.txt` → No matches
- [ ] `grep -r "MANDATORY VOICE" domains/*/prompts/*.txt` → No matches
- [ ] `grep -r "active voice" domains/*/prompts/*.txt` → No matches
- [ ] All voice guidance exists in `shared/voice/profiles/*.yaml`

---

## 🚫 Grade F Violations

**Automatic Grade F** if:
1. Voice instructions added to domain prompts
2. Voice instructions hardcoded in generation code
3. Persona overrides created in domain-specific configs
4. Contradictory voice rules introduced anywhere

**Recovery**: Remove all violations, regenerate content, verify quality.

---

## 📚 Related Policies

- **Prompt Purity Policy**: `PROMPT_PURITY_POLICY.md` (no hardcoded prompts in code)
- **Template-Only Policy**: `TEMPLATE_ONLY_POLICY.md` (templates determine content)
- **Content Instruction Policy**: `CONTENT_INSTRUCTION_POLICY.md` (content rules in prompts/)
- **Author Assignment Immutability**: `copilot-instructions.md` Rule #11 (author never changes)

---

## 🎓 Example: Correct Architecture

### Persona File (Source of Truth)
`shared/voice/profiles/indonesia.yaml`:
```yaml
core_voice_instruction: |
  Write in conversational professional English: Use active voice (75%) with 
  straightforward, natural phrasing. Write like explaining results to a team 
  member, not documenting for archives. Use practical verbs ("clears", "removes").

forbidden:
  direct_address: ["you", "your", "you'll", "you should", "you need to"]
  conversational_filler: ["Well,", "So,", "Now,", "just", "simply"]
```

### Domain Prompt (Technical Instructions Only)
`domains/settings/prompts/description.txt`:
```
You are {author} from {country}, writing practical operational guidance.

VOICE STYLE:
{voice_instruction}

TASK: Write a concise paragraph describing key considerations. Target 80-120 words.

STRUCTURE:
- Single paragraph, 5-7 sentences
- Lead with most important operational consideration
[etc - NO voice instructions]
```

### Generation Code (Mechanism Only)
```python
persona = PersonaLoader.load(author_id)
voice_instruction = persona['core_voice_instruction']
prompt = template.render(voice_instruction=voice_instruction)
# NO voice logic in code
```

---

## 🔄 Version History

- **1.0.0** (Dec 6, 2025): Initial policy - voice centralization mandatory
- Migration: Remove voice instructions from 3 domain prompt files
- Enforcement: Tests prevent future violations

---

**Compliance**: MANDATORY  
**Grade**: F violation if not followed  
**Priority**: TIER 1 - System-breaking (creates conflicting instructions)
