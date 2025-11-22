# Subjective Evaluation Policy - Six Comprehensive Dimensions

**Status**: MANDATORY (November 22, 2025)  
**Owner**: AI Quality Systems  
**Grade**: A+ (100/100) - Comprehensive human realism evaluation

---

## 📋 Overview

Subjective evaluation provides comprehensive human realism assessment using **6 dimensions** that cover all aspects of AI detection, from voice authenticity to technical jargon overload.

**Purpose**: Catch AI-generated content that passes Winston detection but exhibits subtle non-human patterns like academic tone, formulaic structures, or excessive technical precision.

---

## 🎯 Six Comprehensive Dimensions

### 1. **Voice Authenticity** (0-10)
**Question**: Could a real human expert have this exact voice?

**Evaluation Criteria**:
- 9-10: Convincingly human quirks
- 7-8: Subtle authenticity
- 5-6: Generic competence
- 3-4: Template-like
- 0-2: Algorithmic

**Detects**: Generic AI voice, lack of personality, template-driven writing

---

### 2. **Tonal Consistency** (0-10)
**Question**: Natural expert voice OR artificial consistency?

**Evaluation Criteria**:
- 9-10: Genuine human variation
- 7-8: Believable steadiness
- 5-6: Too perfect
- 3-4: Mechanical
- 0-2: Robotic

**Detects**: Algorithmic perfection, unnatural consistency, mechanical tone

---

### 3. **Technical Accessibility** (0-10) 🔥 **NEW (Nov 22, 2025)**
**Question**: Practical guidance vs academic documentation?

**Evaluation Criteria**:
- 9-10: Expert explaining naturally
- 7-8: Mostly practical
- 5-6: Some jargon overload
- 3-4: Textbook-like
- 0-2: Physics paper

**Detects**: 
- Excessive decimal places (0.95, 0.06, 933.47)
- Wavelength citations ("at 1064 nm")
- Temperature in Kelvin (933.47 K)
- Physics textbook language
- Property bombardment without practical application

---

### 4. **Natural Imperfection** (0-10) 🔥 **NEW (Nov 22, 2025)**
**Question**: Human quirks vs algorithmic perfection?

**Evaluation Criteria**:
- 9-10: Genuine human variability
- 7-8: Some natural flow
- 5-6: Suspiciously polished
- 3-4: Too symmetric
- 0-2: Machine perfect

**Detects**:
- Perfect parallel structures
- Balanced sentence lengths
- Symmetry obsession
- Algorithmic polish

---

### 5. **Conversational Flow** (0-10) 🔥 **NEW (Nov 22, 2025)**
**Question**: Natural thinking vs template structure?

**Evaluation Criteria**:
- 9-10: Unpredictable human flow
- 7-8: Mostly natural
- 5-6: Some formulaic patterns
- 3-4: Template-driven
- 0-2: Algorithmic structure

**Detects**:
- Formulaic organization
- Template-driven structure
- Predictable patterns
- Mechanical transitions

---

### 6. **Overall Realism** (0-10)
**Question**: Would you bet $1000 this was written by a human?

**Evaluation Criteria**:
- 9-10: Absolutely human
- 7-8: Probably human (MINIMUM THRESHOLD)
- 5-6: Uncertain
- 3-4: Likely AI
- 0-2: Obviously synthetic

**Primary Quality Gate**: This is the main pass/fail score

---

## 🚨 Four Detection Categories

### 1. **Technical Jargon Issues** 🔥 **NEW (Nov 22, 2025)**
Detects academic/textbook tone that reads like physics papers:

**Examples**:
- Multiple decimal places: "0.95 reflectivity, 0.06 absorption, 933.47 K melting point"
- Wavelength citations: "at 1064 nm", "532 nm laser"
- Temperature in Kelvin: "933.47 K" instead of "660°C"
- Scientific paper language: "presents a primary challenge", "requires precise control"
- Property bombardment: Listing specs without practical use

**Action**: INSTANT REJECTION if detected

---

### 2. **AI Patterns Found**
Detects algorithmic writing patterns:

**Examples**:
- Perfect parallel structures
- Balanced sentence lengths
- Transitional overuse: "Additionally", "Furthermore", "Moreover"
- Abstract noun stacking: "optimization of precision enhancement"
- Hedge words: "various", "numerous", "range of"
- Generic intensifiers: "highly", "extremely", "significantly"
- Corporate passive voice: "is achieved", "can be obtained"

**Action**: Lower scores, may REJECT if severe

---

### 3. **Theatrical Phrases Found**
Detects promotional/marketing language:

**Examples**:
- "presents a unique challenge"
- "critical pitfall"
- "offers significant benefits"
- "When it comes to..."
- "can provide"

**Action**: Lower scores, may REJECT if multiple found

---

### 4. **Formulaic Structures** 🔥 **NEW (Nov 22, 2025)**
Detects template-driven organization:

**Examples**:
- Three items in identical format
- Symmetry obsession (perfectly balanced paragraphs)
- Opening pattern repetition (sentences starting same way)
- Template-driven structure (challenge → solution → importance)

**Action**: Lower Natural Imperfection and Conversational Flow scores

---

## 📊 Evaluation Response Format

```
**Overall Realism (0-10)**: X
**Voice Authenticity (0-10)**: X
**Tonal Consistency (0-10)**: X
**Technical Accessibility (0-10)**: X
**Natural Imperfection (0-10)**: X
**Conversational Flow (0-10)**: X

**Reasoning** (2-3 sentences covering all dimensions):

**Technical Jargon Issues**: [list specific examples or "none"]
**AI Patterns Found**: [list or "none"]
**Theatrical Phrases Found**: [quotes or "none"]
**Formulaic Structures**: [describe or "none"]

**Pass/Fail**: [PASS if ≥{realism_threshold}, FAIL if <{realism_threshold}]
```

---

## 🔧 Implementation

### Template File
**Location**: `prompts/evaluation/subjective_quality.txt`

Contains:
- 6 dimension evaluation criteria
- Technical jargon detection rules (INSTANT REJECTION)
- AI pattern detection
- Formulaic structure detection
- Response format specification

### Parser
**Location**: `postprocessing/evaluation/subjective_evaluator.py`

**Method**: `_parse_claude_response()`

Parses:
- 6 dimension scores (float 0-10)
- Technical jargon issues (list)
- AI patterns (list)
- Theatrical phrases (list)
- Formulaic structures (list)
- Pass/fail status

### Result Object
**Class**: `SubjectiveEvaluationResult`

**Fields**:
```python
realism_score: float  # Overall Realism (primary gate)
voice_authenticity: float
tonal_consistency: float
technical_accessibility: float  # NEW
natural_imperfection: float  # NEW
conversational_flow: float  # NEW
technical_jargon_issues: List[str]  # NEW
formulaic_structures: List[str]  # NEW
ai_tendencies: List[str]
passes_quality_gate: bool
```

---

## ✅ Quality Thresholds

### Pass/Fail Gate
**Primary Score**: Overall Realism ≥ 7.0/10

**Secondary Requirements**:
- Technical Accessibility ≥ 5.0 (prevent academic tone)
- Natural Imperfection ≥ 5.0 (prevent algorithmic perfection)
- Conversational Flow ≥ 5.0 (prevent template structure)

**Instant Rejection Triggers**:
- Technical Jargon Issues detected (academic tone)
- Multiple Theatrical Phrases (3+)
- Severe AI Patterns (formulaic, robotic)

---

## 🧪 Testing

### Test File
**Location**: `tests/test_subjective_evaluation_six_dimensions.py`

**Coverage**:
1. ✅ All 6 dimensions parsed from response
2. ✅ Technical jargon detection and parsing
3. ✅ Formulaic structures detection and parsing
4. ✅ All 4 detection categories present
5. ✅ Clean content passes all dimensions
6. ✅ Technical Accessibility dimension critical
7. ✅ Response format includes all fields
8. ✅ Evaluation criteria includes jargon detection

### Running Tests
```bash
pytest tests/test_subjective_evaluation_six_dimensions.py -v
```

---

## 📚 Related Documentation

- **Prompt Template**: `prompts/evaluation/subjective_quality.txt`
- **Description Prompt**: `prompts/components/description.txt` (jargon avoidance)
- **Parser Implementation**: `postprocessing/evaluation/subjective_evaluator.py`
- **Quality Gates**: `docs/06-ai-systems/QUALITY_GATE_POLICY.md`
- **Terminal Logging**: `docs/08-development/TERMINAL_LOGGING_POLICY.md`

---

## 🔄 Change History

### November 22, 2025 - Six Comprehensive Dimensions
- **Status**: MANDATORY enforcement
- **Dimensions**: Expanded from 3 to 6
- **New Dimensions**: Technical Accessibility, Natural Imperfection, Conversational Flow
- **New Detection**: Technical Jargon Issues, Formulaic Structures
- **Tests**: test_subjective_evaluation_six_dimensions.py created
- **Grade**: A+ (100/100) - Comprehensive implementation

**Before**: 3 dimensions (Voice, Tone, Realism)
**After**: 6 dimensions covering all human realism aspects

**Impact**: Catches academic tone, jargon overload, formulaic patterns that previously passed

---

## 🎯 Examples

### ❌ FAIL - Technical Jargon Overload
```
Content: "Aluminum's high reflectivity of 0.95 and low laser absorption 
of 0.06 at 1064 nm present a primary challenge for laser cleaning. 
Its low melting point of 933.47 K requires precise control."

Scores:
- Overall Realism: 4.0/10
- Technical Accessibility: 2.0/10 (CRITICAL FAIL)

Issues Detected:
- Technical Jargon: Multiple decimals (0.95, 0.06, 933.47), wavelength (1064 nm), Kelvin
- Theatrical Phrases: "presents a primary challenge"

Result: FAIL (academic tone, physics paper language)
```

### ✅ PASS - Natural Expert Voice
```
Content: "Copper tends to heat up fast, so you'll want to dial back 
the power a bit. Start around 80W and watch how it responds - 
the surface should clean up nicely without any discoloration."

Scores:
- Overall Realism: 9.0/10
- Technical Accessibility: 9.5/10 (EXCELLENT)
- Natural Imperfection: 9.0/10
- Conversational Flow: 9.0/10

Issues Detected: none

Result: PASS (natural expert explaining, practical guidance)
```

---

**REMEMBER**: The goal is to catch content that reads like it came from a machine, not a human expert. All 6 dimensions work together to provide comprehensive human realism evaluation.
