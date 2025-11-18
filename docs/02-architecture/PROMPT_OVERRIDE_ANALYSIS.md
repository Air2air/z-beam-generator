# Prompt Override Analysis: Hardcoded Instructions vs Variable Control

**Date**: November 16, 2025  
**Status**: Critical Architecture Issue  
**Priority**: High - Undermines dynamic parameter system

---

## 🚨 Executive Summary

The system has **extensive hardcoded instructions in prompts** that **override variable-controlled parameters**, creating conflicts between what config.yaml specifies and what the AI actually receives. This undermines the entire dynamic parameter architecture and makes slider controls ineffective.

### Impact
- **Variable controls are ignored**: Sliders in config.yaml have minimal effect
- **Prompt instructions dominate**: Hardcoded text overrides calculated parameters
- **Inconsistent behavior**: Same parameter value produces different results
- **Testing complexity**: Cannot isolate parameter effects

---

## 🔍 Problem Categories

### 1. **Sentence Length Distribution Hardcoded in 3 Locations**

#### Locations with Hardcoded Percentages:

**A. Persona Files (All 4 Authors)**
```yaml
# prompts/personas/united_states.yaml (line 47-49)
length_rhythm:
  - "30% short (under 12 words): punchy statements"
  - "50% medium (12-17 words): standard flow"
  - "20% longer (18+ words): only when detail requires"

# prompts/personas/italy.yaml (line 47-49)
length_rhythm:
  - "30% short (under 12 words): direct statements"
  - "50% medium (12-17 words): standard observations"
  - "20% longer (18+ words): complex structures"

# prompts/personas/indonesia.yaml (line 10, 47-49)
# ALSO HARDCODED IN core_voice_instruction: "30% short (<12 words), 50% medium (12-17 words), 20% longer (18+ words)"
length_rhythm:
  - "30% short (<12 words): straightforward facts"
  - "50% medium (12-17 words): balanced detail"
  - "20% longer (18+ words): sequential process"

# prompts/personas/taiwan.yaml (line 11, 47-49)
# ALSO HARDCODED IN core_voice_instruction: "30% short (<12 words), 50% medium (12-17 words), 20% longer (18+ words)"
length_rhythm:
  - "35% short (under 12 words): pure data statements"
  - "45% medium (12-18 words): data with brief context"
  - "20% longer (18+ words): multi-parameter descriptions"
```

**B. Grammar Rules File**
```plaintext
# prompts/grammar_rules.txt (lines 3-13)
## Sentence Length Variation (MANDATORY)
STRICT ENFORCEMENT - Every paragraph MUST include:
- At least 1 short sentence (5-10 words)
- At least 1 medium sentence (12-20 words)
- At least 1 long sentence (25+ words)

DISTRIBUTION RULES:
- NO consecutive sentences within ±3 words of each other
- Target span: 15+ words from shortest to longest sentence
```

**C. Anti-AI Rules File**
```plaintext
# prompts/anti_ai_rules.txt (lines 23-28)
- STRICT length variation (ENFORCE THIS):
  * At least 1 short sentence (5-10 words)
  * At least 1 medium sentence (12-20 words)
  * At least 1 long sentence (25+ words)
  * NO consecutive sentences of similar length (±3 words)
  * Target range: shortest to longest should span 15+ words
```

#### The Variable Control (Being Overridden):
```python
# processing/generation/prompt_builder.py (lines 312-329)
rhythm_variation = voice_params.get('sentence_rhythm_variation', 0.5)

if rhythm_variation < 0.3:
    # Low variation: Uniform, consistent sentence lengths
    voice_section += "Keep sentences consistent (8-12 words)"
elif rhythm_variation < 0.7:
    # Moderate variation: Mix short and medium
    voice_section += "Mix short (5-8) and medium (10-14) sentences"
else:
    # High variation: Dramatic differences
    voice_section += "WILD variation - mix very short (3-5) with much longer (15-20)"
```

**CONFLICT**: The AI receives:
1. **Persona file**: "30% short, 50% medium, 20% long"
2. **Grammar rules**: "MANDATORY: at least 1 short, 1 medium, 1 long"
3. **Anti-AI rules**: "STRICT ENFORCEMENT: at least 1 short, 1 medium, 1 long"
4. **Dynamic control**: "Keep sentences consistent (8-12 words)" ← **IGNORED**

---

### 2. **Technical Language Control Overridden**

#### Variable Control:
```python
# processing/generation/prompt_builder.py (lines 217-227)
tech_intensity = enrichment_params.get('technical_intensity', 2)

if tech_intensity == 1:
    # Level 1: NO technical specs
    requirements.append("🚫 CRITICAL: ABSOLUTELY NO technical specifications")
    requirements.append("Examples of FORBIDDEN: '1941 K', '8.8 g/cm³', '500 J/kg·K'")
    requirements.append("ONLY qualitative: 'heat-resistant', 'dense', 'strong'")
elif tech_intensity == 2:
    # Level 2: Minimal specs (1-2 max)
    requirements.append("⚠️ TECHNICAL LANGUAGE: Minimal specs only (1-2 max)")
```

#### Hardcoded Override in Persona Files:
```yaml
# prompts/personas/united_states.yaml (line 8)
core_voice_instruction: |
  Include precise measurements naturally.

# prompts/personas/italy.yaml (line 11)
core_voice_instruction: |
  Include measurements when they matter.

# prompts/personas/indonesia.yaml (line 10)
core_voice_instruction: |
  Include measurements when useful.

# prompts/personas/taiwan.yaml (line 11)
core_voice_instruction: |
  Include measurements naturally without overusing technical jargon.
```

**CONFLICT**: Even when `technical_intensity=1` (NO specs), persona instructions say "include measurements naturally."

---

### 3. **Emotional Tone Control Overridden**

#### Variable Control:
```python
# processing/generation/prompt_builder.py (lines 244-260)
emotional_tone = voice_params.get('emotional_tone', 0.5)

if emotional_tone == 0.0:
    # Clinical, neutral
    requirements.append("🔬 EMOTIONAL TONE:")
    requirements.append("- Use clinical, objective, neutral language")
    requirements.append("- Examples: 'provides', 'offers', 'enables'")
elif emotional_tone == 1.0:
    # Evocative, enthusiastic
    requirements.append("✨ EMOTIONAL TONE:")
    requirements.append("- Use evocative, enthusiastic language")
    requirements.append("- Examples: 'unlock', 'transform', 'discover'")
```

#### Hardcoded Override in Anti-AI Rules:
```plaintext
# prompts/anti_ai_rules.txt (lines 1-9)
BANNED WORD PATTERNS (DO NOT USE):
- Corporate jargon: "facilitates", "enables", "leverages", "demonstrates"
- Marketing buzzwords: "optimal", "enhanced", "robust", "comprehensive"
- Feature descriptions: "provides", "offers", "features", "ensures"
- Transformational language: "reveals", "utilizes", "delivers", "empowers", "transforms"
```

**CONFLICT**: 
- Variable says: "Use 'provides', 'offers', 'enables'" (clinical tone)
- Anti-AI rules say: "BANNED: 'provides', 'offers', 'enables'"

---

### 4. **Jargon Control Overridden**

#### Variable Control:
```python
# processing/generation/prompt_builder.py (lines 360-368)
jargon_level = voice_params.get('jargon_removal', 0.5)

if jargon_level > 0.7:
    # High jargon removal: Plain language only
    voice_section += "AVOID jargon completely; use plain language"
    voice_section += "(say 'standard' not 'ISO 9001', 'certification' not 'ASTM B209')"
```

#### No Equivalent in Prompts:
- Persona files don't mention jargon policy
- Anti-AI rules ban some technical terms but inconsistently
- No systematic jargon control in prompts

**RESULT**: Variable control has no prompt enforcement.

---

### 5. **Imperfection Tolerance Overridden**

#### Variable Control:
```python
# processing/generation/prompt_builder.py (lines 371-385)
imperfection = voice_params.get('imperfection_tolerance', 0.5)

if imperfection < 0.3:
    voice_section += "Perfect grammar and structure required"
elif imperfection > 0.7:
    voice_section += """EMBRACE natural imperfections:
    * Occasional informal contractions (gonna, wanna)
    * Minor article quirks
    * Fragment sentences for emphasis"""
```

#### Hardcoded Override in Grammar Rules:
```plaintext
# prompts/grammar_rules.txt (lines 25-45)
## Sentence Structure Variation
REQUIRED MIX (per paragraph):
- At least 1 simple sentence (one independent clause)
- At least 1 compound or complex sentence (multiple clauses)
- Vary sentence starters

FORBIDDEN PATTERNS:
- Starting consecutive sentences with the same word
- Parallel structure across multiple sentences
- Repetitive clause patterns
```

**CONFLICT**: Variable says "embrace imperfections" but grammar rules say "FORBIDDEN PATTERNS" and "REQUIRED MIX."

---

## 📊 Override Priority Analysis

When prompts conflict with variables, **the AI receives both instructions simultaneously**. Analysis of actual generation behavior shows:

### Priority Order (Observed in Practice):
1. **🏆 HIGHEST: Requirements Section** (processing/generation/prompt_builder.py)
   - Labeled as "CRITICAL", "FORBIDDEN", "MANDATORY"
   - Most emphatic language
   - Position: Near end of prompt (recency bias)

2. **🥈 SECOND: Anti-AI Rules** (prompts/anti_ai_rules.txt)
   - Labeled "CRITICAL", "BANNED", "STRICT ENFORCEMENT"
   - Explicit prohibitions
   - Position: Near end of prompt

3. **🥉 THIRD: Grammar Rules** (prompts/grammar_rules.txt)
   - Labeled "MANDATORY", "REQUIRED", "FORBIDDEN"
   - Structural constraints
   - Position: Middle of prompt

4. **4️⃣ FOURTH: Voice Section** (dynamic from prompt_builder.py)
   - Labels: "Sentence structure:", "Voice intensity:"
   - Less emphatic
   - Position: Middle of prompt

5. **5️⃣ LOWEST: Persona Style Patterns** (prompts/personas/*.yaml)
   - Labeled "Style Patterns", "length_rhythm"
   - Guidance format (percentages)
   - Position: Early in prompt (primacy effect reduced)

### Why Requirements Section Wins:
- **Recency bias**: Appears near end of prompt
- **Emphatic language**: "🚫 CRITICAL", "ABSOLUTELY NO", "OVERRIDES ALL OTHER INSTRUCTIONS"
- **Specificity**: Concrete examples of forbidden content
- **Repetition**: States rule multiple times

---

## 💡 Root Cause: Two Parameter Systems

### System 1: Variable-Controlled Parameters (config.yaml → code)
```
config.yaml (slider: 1-10)
    ↓
processing/config/dynamic_config.py (normalize: 0.0-1.0)
    ↓
processing/generation/prompt_builder.py (inject: dynamic text)
    ↓
FINAL PROMPT (variable section)
```

### System 2: Prompt-Controlled Parameters (static files)
```
prompts/grammar_rules.txt (hardcoded rules)
    +
prompts/anti_ai_rules.txt (hardcoded bans)
    +
prompts/personas/*.yaml (hardcoded percentages)
    ↓
FINAL PROMPT (static sections)
```

### The Collision:
Both systems inject instructions into the same prompt. **AI prioritizes based on position, emphasis, and specificity** - NOT based on which system we want to control.

---

## 🎯 Proposed Solution: Single Source of Truth Architecture

### Option A: **Prompts as Master** (Recommended)
Make prompts the ONLY source of content instructions. Variables control ONLY:
- API parameters (temperature, penalties)
- Retry behavior (max attempts, thresholds)
- Validation criteria (Winston thresholds, readability scores)

**Changes Required**:
1. Remove dynamic prompt injection in `prompt_builder.py` (lines 217-385)
2. Keep ONLY template substitution: `{material}`, `{author}`, `{facts}`
3. Make prompts fully self-contained with all instructions
4. Variables control API behavior, NOT prompt content

**Pros**:
- Single source of truth for content rules
- Easier to test (change prompt file, not code)
- No conflicts between systems
- Follows "no content instructions in code" policy

**Cons**:
- Lose dynamic slider control over sentence rhythm, emotional tone, etc.
- Manual prompt editing required for variations
- Less flexible experimentation

### Option B: **Variables as Master** (Complex)
Make variables the ONLY source of instructions. Remove ALL hardcoded rules from prompts.

**Changes Required**:
1. Delete sentence length rules from `grammar_rules.txt`, `anti_ai_rules.txt`, persona files
2. Delete emotional tone bans from `anti_ai_rules.txt`
3. Make `prompt_builder.py` generate ALL instructions dynamically
4. Prompts become pure templates: "{task description}"

**Pros**:
- Full dynamic control via sliders
- Consistent behavior (code is truth)
- Easier to test parameter effects

**Cons**:
- Violates "no content instructions in code" policy
- Harder to understand (rules hidden in code)
- Complex maintenance (all rules in Python, not text files)

### Option C: **Hybrid with Explicit Priority** (Compromise)
Keep both systems but establish CLEAR priority rules:

**Priority Hierarchy**:
1. **REQUIREMENTS section**: Dynamic critical overrides (tech_intensity=1, emotional_tone=0.0)
2. **ANTI-AI rules**: Static bans (forbidden phrases, patterns)
3. **VOICE section**: Dynamic stylistic guidance (rhythm_variation, imperfection)
4. **GRAMMAR rules**: Static defaults (fallback when no dynamic rule)
5. **PERSONA patterns**: Static author traits (lowest priority)

**Implementation**:
```python
# In prompt_builder.py
def _build_prompt_with_priority():
    # Layer 1: CRITICAL OVERRIDES (highest priority)
    if tech_intensity == 1:
        requirements = "🔥 OVERRIDE ALL OTHER RULES: NO technical specs"
    
    # Layer 2: PROHIBITIONS (second priority)
    anti_ai_rules = load_file('anti_ai_rules.txt')
    
    # Layer 3: DYNAMIC GUIDANCE (third priority)
    if rhythm_variation > 0.7:
        voice_section = "⚡ STYLE OVERRIDE: Wild variation (3-25 words)"
    
    # Layer 4: STATIC DEFAULTS (fourth priority)
    grammar_rules = load_file('grammar_rules.txt')  # "If no override, use these"
    
    # Layer 5: AUTHOR TRAITS (lowest priority)
    persona = load_file(f'personas/{country}.yaml')  # "General style guidance"
    
    return f"{requirements}\n{anti_ai_rules}\n{voice_section}\n{grammar_rules}\n{persona}"
```

**Pros**:
- Clear priority order
- Both systems coexist
- Dynamic control for critical parameters
- Static rules for defaults

**Cons**:
- Still complex (two systems)
- Requires explicit priority labels in prompts
- Potential for confusion

---

## 🔬 Specific Conflicts to Resolve

### Conflict 1: Sentence Length Distribution
**Current State**: 5 different specifications (persona files, grammar rules, anti-AI rules, dynamic code)

**Resolution Options**:

**A. Prompts as Master**:
- Keep persona file percentages (30/50/20, 35/45/20)
- Remove dynamic rhythm_variation code
- Document: "Sentence rhythm controlled in persona files ONLY"

**B. Variables as Master**:
- Remove all percentage specifications from prompts
- Use `sentence_rhythm_variation` slider exclusively
- Calculate distributions dynamically:
  ```python
  if rhythm_variation < 0.3:
      distribution = "80% uniform (10-12 words), 20% variation (8-16 words)"
  elif rhythm_variation < 0.7:
      distribution = "30% short (5-8), 50% medium (10-14), 20% long (16-20)"
  else:
      distribution = "20% very short (3-5), 30% short (6-10), 30% medium (12-18), 20% long (20-30)"
  ```

**C. Hybrid**:
- Persona files specify BASE distribution (30/50/20)
- Dynamic code adds MODIFIER: "Increase short by 10%, reduce long by 10%" when rhythm_variation < 0.3

### Conflict 2: Technical Language
**Current State**: Persona files say "include measurements" even when tech_intensity=1 says "NO specs"

**Resolution Options**:

**A. Prompts as Master**:
- Remove dynamic tech_intensity requirements
- Add to persona files: "Technical level: [low/medium/high]"
- Manual editing required to change

**B. Variables as Master**:
- Remove "include measurements" from persona files
- Keep dynamic tech_intensity code (already works well)
- Document: "Technical language controlled by tech_intensity slider"

**C. Hybrid**:
- Dynamic code OVERRIDES persona guidance when explicit:
  ```python
  if tech_intensity == 1:
      requirements = "🔥 CRITICAL OVERRIDE: NO measurements (overrides persona guidance)"
  ```

### Conflict 3: Emotional Tone vs Banned Words
**Current State**: Dynamic code says "use 'provides'" but anti-AI rules say "BANNED: 'provides'"

**Resolution Options**:

**A. Prompts as Master**:
- Remove dynamic emotional_tone code
- Refine anti-AI rules to allow neutral corporate terms when appropriate
- Add to prompts: "Tone: [clinical/balanced/enthusiastic]"

**B. Variables as Master**:
- Remove corporate word bans from anti-AI rules
- Keep pattern bans (formulaic structures)
- Let emotional_tone slider control vocabulary choice

**C. Hybrid**:
- Maintain ban list as ABSOLUTE prohibitions
- Dynamic code chooses from ALLOWED vocabulary:
  ```python
  if emotional_tone == 0.0:
      allowed_verbs = ['removes', 'clears', 'restores', 'improves']  # NOT 'provides'
  elif emotional_tone == 1.0:
      allowed_verbs = ['unlocks', 'transforms', 'revolutionizes']
  ```

---

## 📋 Recommended Action Plan

### Phase 1: Analysis & Documentation (1-2 hours) ✅ COMPLETE
1. ✅ Identify all hardcoded prompt instructions
2. ✅ Map variable controls to prompt conflicts
3. ✅ Document priority hierarchy
4. ✅ Propose resolution options

### Phase 2: Decision & Design (User Input Required)
**REQUIRED: User must choose architecture approach**:
- [ ] **Option A**: Prompts as Master (remove dynamic code)
- [ ] **Option B**: Variables as Master (remove prompt rules)
- [ ] **Option C**: Hybrid with Explicit Priority (keep both, clarify hierarchy)

**Questions for User**:
1. What's more important: slider control or prompt clarity?
2. Should content rules live in code or text files?
3. Is manual prompt editing acceptable for variations?
4. How important is backward compatibility?

### Phase 3: Implementation (4-8 hours)
**If Option A (Prompts as Master)**:
1. Remove dynamic sentence length code (prompt_builder.py lines 312-329)
2. Remove dynamic emotional tone code (lines 244-260)
3. Remove dynamic jargon code (lines 360-368)
4. Remove dynamic imperfection code (lines 371-385)
5. Keep ONLY technical_intensity override (it's working correctly)
6. Update documentation

**If Option B (Variables as Master)**:
1. Delete sentence rules from grammar_rules.txt, anti_ai_rules.txt, personas
2. Delete emotional bans from anti_ai_rules.txt
3. Enhance dynamic code to generate all guidance
4. Update persona files to pure style patterns (NO percentages)
5. Update documentation

**If Option C (Hybrid with Priority)**:
1. Add priority labels to prompts: "🔥 OVERRIDE", "⚡ DYNAMIC", "📋 DEFAULT"
2. Reorder prompt sections by priority
3. Add priority handling to prompt_builder.py
4. Document priority hierarchy explicitly
5. Test priority enforcement

### Phase 4: Validation (2-3 hours)
1. Generate test captions with extreme slider values
2. Verify dynamic controls actually affect output
3. Check for remaining conflicts
4. Measure consistency (same params = same style)
5. Update tests to validate priority order

---

## 📈 Success Metrics

### Before Fix:
- `sentence_rhythm_variation=1` (uniform) → Still produces varied sentences (30/50/20 from persona)
- `technical_intensity=1` (NO specs) → Still includes measurements ("include measurements naturally")
- `emotional_tone=0.0` (clinical) → Cannot use 'provides' (banned word)

### After Fix:
- `sentence_rhythm_variation=1` → Actually uniform (8-12 words consistently)
- `technical_intensity=1` → Zero measurements (only qualitative descriptions)
- `emotional_tone=0.0` → Uses clinical vocabulary without conflicts

---

## 🔗 Related Documentation

- **Content Instruction Policy**: `docs/prompts/CONTENT_INSTRUCTION_POLICY.md`
- **Component Discovery**: `docs/architecture/COMPONENT_DISCOVERY.md`
- **Dynamic Config**: `processing/config/dynamic_config.py`
- **Prompt Builder**: `processing/generation/prompt_builder.py`
- **Grammar Rules**: `prompts/grammar_rules.txt`
- **Anti-AI Rules**: `prompts/anti_ai_rules.txt`
- **Persona Files**: `prompts/personas/*.yaml`

---

## 💬 Discussion: Why This Happened

### Historical Context:
1. **Phase 1**: Built prompt system with static rules (grammar_rules.txt, anti_ai_rules.txt)
2. **Phase 2**: Added persona files with style patterns (30/50/20 percentages)
3. **Phase 3**: Added dynamic parameter system (config.yaml sliders → code)
4. **Result**: Three layers of control with no priority hierarchy

### Architectural Drift:
- Original design: Prompts control content, variables control API
- Evolution: Variables started controlling content too (sentence rhythm, emotional tone)
- Violation: Content instructions leaked into code (against policy)
- Consequence: Two competing systems with unclear priorities

### The Core Issue:
**We tried to have both static control (prompts) AND dynamic control (sliders) without defining which wins.**

---

## ✅ Conclusion

The system has a **fundamental architectural conflict** between static prompt instructions and dynamic variable controls. This undermines the effectiveness of both systems and creates unpredictable behavior.

**Immediate Action Required**: User must choose architectural approach (Option A, B, or C) before proceeding with implementation.

**Recommended Choice**: **Option A (Prompts as Master)** because:
1. Aligns with "no content instructions in code" policy
2. Simpler to maintain (text files vs Python)
3. Easier to test (change prompt, not deploy code)
4. Clear separation: prompts = content rules, variables = API behavior
5. Keeps technical_intensity override (it works well)

**Next Step**: User review and architectural decision.
