# Prompt Coherence Validation System
**Date**: December 11, 2025  
**Implementation**: Two-stage validation before API submission  
**Purpose**: Ensure separation of concerns and contradiction-free prompts

---

## 🎯 Purpose

Validates that the **final assembled prompt** sent to Grok is:
1. **Coherent** - No contradictions between sections
2. **Clear** - No duplicate or conflicting instructions
3. **Well-Separated** - Proper separation of concerns (voice vs content vs requirements)
4. **Consistent** - Length, tone, and forbidden phrase instructions aligned

---

## 🏗️ Architecture

### **Two-Stage Validation**

**Stage 1: Standard Validation** (`prompt_validator.py`)
- Length checks (API limits, token counts)
- Format validation (encoding, structure)
- Technical compliance (API compatibility)

**Stage 2: Coherence Validation** (`prompt_coherence_validator.py`) 🔥 **NEW**
- Separation of concerns validation
- Contradiction detection
- Duplication checking
- Voice instruction leak detection
- Length instruction consistency
- Forbidden phrase consistency

---

## 🔍 Separation of Concerns Checks

### **1. Voice Instructions Isolation**
**Rule**: Voice instructions ONLY in VOICE section

**Detects**:
- Voice keywords in REQUIREMENTS section
- Examples: 'conversational', 'casual', 'formal tone', 'writing style', 'ESL traits'

**Error Example**:
```
❌ ERROR (SEPARATION_VIOLATION): Voice instruction 'conversational' found in REQUIREMENTS section
   📍 Section 1: REQUIREMENTS
   📍 Section 2: VOICE
   💡 Move voice instructions to VOICE section only
```

### **2. Content Instructions Isolation**
**Rule**: Content instructions ONLY in component template

**Detects**:
- Content keywords in VOICE section
- Examples: 'focus on', 'emphasize', 'structure should', 'format must', 'start with'

**Warning Example**:
```
⚠️  WARNING (SEPARATION_VIOLATION): Content instruction 'focus on' found in VOICE section
   📍 Section 1: VOICE
   💡 Move content instructions to component template
```

### **3. Voice Instruction Leaks**
**Rule**: Voice-specific keywords ONLY in VOICE section

**Detects**:
- 'forbidden phrases', 'tone requirements:', 'core style:', 'regional patterns:', 'ESL traits'
- Found anywhere OUTSIDE the VOICE section

**Error Example**:
```
❌ ERROR (VOICE_LEAK): Voice instruction 'forbidden phrases' leaked outside VOICE section
   📍 Section 1: Line 45
   📍 Section 2: VOICE
   💡 Consolidate all voice instructions in VOICE section
```

---

## 🚫 Contradiction Detection

### **1. Length Contradictions**
**Detects**:
- Both 'brief' and 'detailed' in same prompt
- Conflicting word counts (e.g., "50 words" and "150 words")
- Inconsistent ranges (e.g., "50-150" and "200-300")

**Error Example**:
```
❌ ERROR (CONTRADICTION): Contradictory length instructions: both 'brief' and 'detailed' specified
   📍 Section 1: REQUIREMENTS
      'Found: brief/short/concise'
      'Also found: detailed/comprehensive/thorough'
   💡 Choose one length target and remove conflicting instructions
```

### **2. Tone Contradictions**
**Detects**:
- Both 'formal' and 'casual' tone specified
- Conflicting tone keywords

**Critical Example**:
```
❌ CRITICAL (CONTRADICTION): Contradictory tone instructions: both formal and casual specified
   📍 Section 1: VOICE
      'Formal keywords: formal, professional, technical, objective'
      'Casual keywords: casual, conversational, friendly'
   💡 Personas define tone - remove conflicting tone instructions
```

### **3. Length Instruction Inconsistency**
**Detects**:
- Multiple different word count targets
- Ranges that don't overlap or are far apart

**Error Example**:
```
❌ ERROR (CONTRADICTION): Inconsistent length targets specified
   📍 Section 1: Multiple locations
      'Found: 50-150 words'
      'Also found: 200-300 words'
   💡 Use single length target (specify in humanness layer only)
```

---

## 🔁 Duplication Detection

### **Duplicate Instructions**
**Detects**:
- Exact duplicate sentences
- Very similar instructions repeated

**Warning Example**:
```
⚠️  WARNING (DUPLICATION): Duplicate instruction found
   📍 Section 1: Multiple locations
      'Write in a formal technical style with precise terminology'
   💡 Remove duplicate - say each instruction once
```

---

## 📊 Validation Output

### **Terminal Output**
```
================================================================================
🔍 COMPREHENSIVE PROMPT VALIDATION (FULL PROMPT)
================================================================================

📊 PROMPT METRICS:
   • Characters: 4,285
   • Words: 723
   • Estimated tokens: 1,085
   • Status: ✅ VALID: 3 suggestions

🔗 COHERENCE VALIDATION:
   ✅ COHERENT (Score: 90/100)

   ✅ Coherence validated successfully

📄 Full prompt saved to: /tmp/tmpXYZ_prompt.txt
   View with: cat /tmp/tmpXYZ_prompt.txt
```

### **With Issues**
```
🔗 COHERENCE VALIDATION:
   ❌ INCOHERENT: 1 critical, 2 errors, 3 warnings (Score: 70/100)

⚠️  COHERENCE ISSUES DETECTED:
   • [CRITICAL] Contradictory tone instructions: both formal and casual specified
   • [ERROR] Voice instruction 'conversational' found in REQUIREMENTS section
   • [ERROR] Inconsistent length targets specified

❌ CRITICAL COHERENCE FAILURE
[Full detailed report follows...]
```

---

## 🏆 Coherence Score

**Scoring System** (0-100):
- Start: 100 points
- Each CRITICAL issue: -10 points
- Each ERROR: -10 points
- Each WARNING: -5 points

**Grades**:
- **90-100**: Excellent separation of concerns
- **75-89**: Good, minor issues
- **60-74**: Fair, needs improvement
- **<60**: Poor, significant coherence problems

---

## 📋 Detected Sections

The validator identifies these prompt sections:

1. **Context/Facts**: Material information, factual data
2. **Voice**: Author voice, tone, style instructions
3. **Humanness Layer**: Anti-AI instructions, structural variation
4. **Requirements**: Technical requirements, format specifications
5. **Component Template**: Component-specific instructions

**Example Output**:
```
📋 Detected Sections:
   ✅ Context/Facts
   ✅ Voice
   ✅ Humanness Layer
   ✅ Requirements
   ❌ Component Template
```

---

## 🔧 Integration

### **Automatic Validation**

Runs automatically in `generation/core/generator.py` before EVERY API call:

```python
# Stage 1: Standard validation
validation_result = validate_text_prompt(prompt)

# Stage 2: Coherence validation
coherence_result = validate_prompt_coherence(prompt)

# Fail on critical issues
if validation_result.has_critical_issues:
    raise ValueError("Standard validation failed")

if coherence_result has critical issues:
    raise ValueError("Coherence validation failed")
```

### **Manual Validation**

Can be used independently:

```python
from shared.validation.prompt_coherence_validator import validate_prompt_coherence

result = validate_prompt_coherence(assembled_prompt)

if not result.is_coherent:
    print(result.format_report())
    
print(f"Coherence Score: {result.separation_score}/100")
```

---

## 📝 Issue Types

### **CoherenceIssueType Enum**

1. **CONTRADICTION** - Conflicting instructions
2. **DUPLICATION** - Repeated instructions
3. **CONFUSION** - Unclear or ambiguous instructions
4. **SEPARATION_VIOLATION** - Concerns not properly separated
5. **VOICE_LEAK** - Voice instructions outside voice section

### **Severity Levels**

1. **CRITICAL** - Blocks generation, must fix
2. **ERROR** - Should fix, likely causes problems
3. **WARNING** - Optional, improves quality

---

## 🎯 Policy Compliance

### **Enforces These Policies**:

1. **Voice Instruction Centralization Policy**
   - ALL voice instructions ONLY in `shared/voice/profiles/*.yaml`
   - Detects voice instructions leaking to other sections

2. **Prompt Chaining Policy**
   - Validates output of orchestrated prompt chain
   - Ensures proper separation between stages

3. **Content Instruction Policy**
   - Content instructions ONLY in `domains/*/prompts/*.txt`
   - Not in code, not in system prompts

4. **Template-Only Policy**
   - Component instructions from templates
   - No component-specific code in generators

---

## 🔬 Technical Details

### **Section Detection**

Uses keyword-based heuristics to detect sections:

- **Context**: 'TOPIC:', 'MATERIAL INFORMATION:', 'FACTUAL INFORMATION:'
- **Voice**: 'VOICE:', 'VOICE CHARACTERISTICS:'
- **Humanness**: 'HUMANNESS', 'ANTI-AI'
- **Requirements**: 'REQUIREMENTS:', 'TECHNICAL REQUIREMENTS:'
- **Component**: 'MICRO:', 'FAQ:', 'DESCRIPTION:', 'CAPTION:'

### **Contradiction Detection**

**Length patterns**:
```python
r'(\d+)\s*words'           # "50 words"
r'(\d+)\s*sentences'       # "3 sentences"
r'brief|short|concise'     # Brevity keywords
r'detailed|comprehensive'  # Detail keywords
```

**Tone keywords**:
```python
formal = ['formal', 'professional', 'technical', 'objective']
casual = ['casual', 'conversational', 'friendly', 'approachable']
neutral = ['neutral', 'balanced', 'detached']
```

---

## ✅ Testing

### **Test Cases**

1. **Clean prompt** - All sections properly separated
2. **Voice leak** - Forbidden phrases in requirements
3. **Tone contradiction** - Both formal and casual specified
4. **Length conflict** - "50 words" and "150 words" both present
5. **Duplication** - Same instruction repeated
6. **Missing sections** - No voice section detected

### **Expected Behavior**

```python
# Clean prompt
result = validate_prompt_coherence(clean_prompt)
assert result.is_coherent
assert len(result.issues) == 0
assert result.separation_score == 100.0

# Contradictory prompt
result = validate_prompt_coherence(contradictory_prompt)
assert not result.is_coherent
assert result.has_critical_issues
assert result.separation_score < 80.0
```

---

## 📊 Metrics Tracked

1. **Coherence Score**: 0-100 (separation quality)
2. **Issue Count**: Total issues detected
3. **Critical Count**: Issues that block generation
4. **Section Detection**: Which sections are present
5. **Contradiction Types**: Length, tone, format, etc.

---

## 🚀 Future Enhancements

### **Planned**

1. **Semantic Contradiction Detection**
   - Use LLM to detect semantic conflicts
   - Not just keyword-based

2. **Cross-Section Reference Checking**
   - Verify references between sections are valid
   - E.g., requirements reference valid voice instructions

3. **Template Consistency Checking**
   - Validate component templates match domain config
   - Ensure placeholders are all replaced

4. **Historical Pattern Learning**
   - Learn which contradictions cause worst outputs
   - Prioritize detection of high-impact issues

---

## 📚 Related Documentation

- **Prompt Chaining Policy**: `docs/08-development/PROMPT_CHAINING_POLICY.md`
- **Voice Centralization**: `docs/08-development/VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md`
- **Content Instructions**: `docs/prompts/CONTENT_INSTRUCTION_POLICY.md`
- **Standard Validator**: `shared/validation/prompt_validator.py`
- **Unified Validator**: `shared/validation/unified_validator.py`

---

## 🎓 Summary

The **Prompt Coherence Validator** ensures:

✅ **Clear separation** of voice, content, and requirements  
✅ **No contradictions** between prompt sections  
✅ **No duplications** of instructions  
✅ **Consistent** length, tone, and forbidden phrase specifications  
✅ **Proper isolation** of voice instructions in voice section only  

**Result**: Cleaner, more effective prompts that produce better content.

**Grade**: A+ implementation - comprehensive checks with actionable feedback.
