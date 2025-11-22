# Prompt Separation of Concerns - Architecture Guide
## November 20, 2025

## 🎯 **Overview**

This document defines the **correct separation of concerns** for all prompt templates in the system, ensuring maintainability, clarity, and architectural compliance.

---

## 📋 **Current Issues Found**

### **Issue 1: Prompts in Wrong Location**
- **Expected Location**: `prompts/components/*.txt`
- **Actual Location**: `domains/materials/prompts/*.txt`
- **Impact**: PromptBuilder can't find templates (line 126: `os.path.join('prompts', 'components', f'{component_type}.txt')`)
- **Evidence**: Empty AFTER section in generation report for Steel caption

### **Issue 2: Mixed Concerns in Templates**
Looking at `domains/materials/prompts/caption.txt`:
- ✅ **GOOD**: Voice instructions ("Write like you're explaining to a colleague")
- ✅ **GOOD**: Formatting rules ("NO labels like 'Before:', 'After:'")
- ⚠️ **MIXED**: Technical guidance embedded in template (should be dynamic from config)
- ⚠️ **MIXED**: Sentence guidance hardcoded (should use voice parameters)

---

## ✅ **Correct Separation of Concerns**

### **Layer 1: System-Level Prompts** (`prompts/system/`)
**Purpose**: Universal instructions that apply to ALL content generation

**Contents**:
- Professional writing standards
- General quality guidelines
- Universal anti-AI patterns
- Tone and style foundations

**Example** (`prompts/system/base.txt`):
```
You are a professional technical writer specializing in industrial laser cleaning content.

Write clear, factual, and technically accurate content.

Focus on:
- Technical accuracy and precision
- Professional tone
- Clear, direct language
- Natural, human-like writing style

Avoid:
- Marketing language or hype
- AI-typical phrases and patterns
- Repetitive structures
```

**Responsibility**: ✅ CORRECT - Universal standards

---

### **Layer 2: Component Templates** (`prompts/components/*.txt`)
**Purpose**: Component-specific content structure and requirements

**Contents**:
- Component structure (e.g., "two paragraphs", "single sentence", "Q&A format")
- Content strategy for THIS component type
- Formatting requirements specific to output format
- Component-specific banned patterns

**What SHOULD be here**:
```
TASK: Write two short paragraphs describing {material} at 1000x magnification.
- Paragraph 1: Contaminated surface before laser cleaning  
- Paragraph 2: Clean surface after laser treatment

FORMATTING:
- Complete sentences (no fragments)
- Separate the two paragraphs with ONE blank line
- NO labels like "Before:", "After:"

STRUCTURE REQUIREMENTS:
- Format: Direct declarative statement  
- NO questions
- End without period (concise statement)
```

**What should NOT be here**:
- ❌ Technical guidance (should be dynamically calculated from `voice_params` and `enrichment_params`)
- ❌ Sentence structure rules (should come from voice profile)
- ❌ Voice characteristics (should come from persona files)

**Current Violation in `caption.txt`**:
```
{technical_guidance}   ← CORRECT: Placeholder for dynamic insertion
{sentence_guidance}    ← CORRECT: Placeholder for dynamic insertion

# BUT the template itself has these sections which duplicate the placeholders
```

**Responsibility**: ✅ Structure, ❌ Voice/Technical (should be dynamic)

---

### **Layer 3: Voice Personas** (`prompts/personas/*.yaml`)
**Purpose**: Author-specific voice characteristics

**Contents**:
- Linguistic patterns (ESL traits, sentence structures)
- Grammar norms and preferences
- Regional language characteristics
- Component-specific sentence styles

**Example Structure**:
```yaml
id: 1
author: "Dr. Elena Kovač"
country: "Slovenia"

linguistic_characteristics:
  sentence_structure:
    patterns:
      - "Occasional present tense where native might use present perfect"
      - "Concrete subjects over abstract processes"

sentence_structure:
  caption:
    style: "Mix short (6-10 words) with medium (12-16 words)"
  subtitle:
    style: "Single declarative statement, 12-18 words"
```

**Responsibility**: ✅ CORRECT - Voice characteristics per author

---

### **Layer 4: Evaluation Prompts** (`prompts/evaluation/*.txt`)
**Purpose**: Quality assessment templates

**Contents**:
- Evaluation criteria
- Scoring rubrics
- Quality dimensions to assess

**Example** (`prompts/evaluation/subjective_quality.txt`):
```
Evaluate this content for:
1. Clarity
2. Technical Accuracy
3. Human-likeness
4. Professionalism

Return JSON with scores 0-10 for each dimension.
```

**Responsibility**: ✅ CORRECT - Evaluation criteria

---

### **Layer 5: Anti-AI Rules** (`prompts/rules/anti_ai_rules.txt`)
**Purpose**: Specific patterns to avoid for AI detection

**Contents**:
- Banned phrases ("facilitates", "leverages")
- Theatrical language to avoid
- Repetitive structures to prevent
- AI-typical patterns to eliminate

**Current Status**: ⚠️ **MISSING** - File expected at `prompts/rules/anti_ai_rules.txt`

**Should contain**:
```
BANNED PHRASES:
- Corporate: "facilitates", "leverages", "demonstrates"
- Theatrical: "zapped clean", "stares back", "changes everything"
- Academic: "results suggest", "testament to"

BANNED PATTERNS:
- Repetitive sentence openings
- "[Material] enables/achieves/delivers..."
- "[Gerund phrase] with [material]..."
```

**Responsibility**: ✅ CORRECT concept - AI detection avoidance

---

## 🔧 **Dynamic Parameter Injection**

### **What Should Be Dynamic (NOT in templates)**:

#### **1. Technical Guidance** (from `enrichment_params`)
**Source**: `generation/config/dynamic_config.py` → `calculate_technical_intensity()`

**Calculation**:
```python
# Based on jargon_removal and technical_intensity sliders
if jargon_removal > 0.7:
    return "Use plain everyday language only - no technical specs"
elif tech_intensity < 0.3:
    return "Include 1-2 key measurements if helpful"
else:
    return "Include measurements naturally when useful"
```

**Injected via**: `{technical_guidance}` placeholder in template

#### **2. Sentence Guidance** (from `voice_params`)
**Source**: Voice persona YAML → `sentence_structure[component_type]`

**Calculation**:
```python
# Based on rhythm_variation and target length
if rhythm_variation > 0.7:
    return "Mix 1 short (6-10 words) with 1-2 medium (12-16 words)"
else:
    return "Keep consistent length (10-14 words each)"
```

**Injected via**: `{sentence_guidance}` placeholder in template

#### **3. Voice Characteristics** (from persona YAML)
**Source**: `prompts/personas/{author_id}.yaml`

**Values**:
- `{author}` - Author name
- `{country}` - Country origin
- `{esl_traits}` - ESL characteristics
- `{sentence_style}` - Component-specific style

---

## 📁 **Correct Directory Structure**

```
prompts/
├── system/
│   └── base.txt                    # Universal writing standards
│
├── components/
│   ├── caption.txt                 # Caption structure + placeholders
│   ├── subtitle.txt                # Subtitle structure + placeholders
│   ├── faq.txt                     # FAQ structure + placeholders
│   └── description.txt             # Description structure + placeholders
│
├── personas/
│   ├── 1.yaml                      # Dr. Elena Kovač (Slovenia)
│   ├── 2.yaml                      # Mr. Ravi Patel (India)
│   ├── 3.yaml                      # Ms. Maria Santos (Philippines)
│   └── 4.yaml                      # Dr. Chen Wei (China)
│
├── evaluation/
│   ├── subjective_quality.txt      # Grok evaluation template
│   └── learned_patterns.yaml       # Learning data
│
└── rules/
    └── anti_ai_rules.txt           # AI detection avoidance patterns
```

---

## 🚨 **Required Fixes**

### **Fix 1: Move Prompts to Correct Location**
```bash
# Create correct directory
mkdir -p prompts/components

# Move prompts from domains/materials/prompts/ to prompts/components/
mv domains/materials/prompts/caption.txt prompts/components/
mv domains/materials/prompts/subtitle.txt prompts/components/
mv domains/materials/prompts/faq.txt prompts/components/
```

### **Fix 2: Create Missing Anti-AI Rules**
```bash
# Create anti_ai_rules.txt from learned patterns
cat > prompts/rules/anti_ai_rules.txt << 'EOF'
CRITICAL: Write naturally and avoid AI-typical patterns.

BANNED CORPORATE PHRASES:
- "facilitates", "leverages", "demonstrates"
- "enables", "delivers", "provides"
- "testament to", "showcases"

BANNED THEATRICAL LANGUAGE:
- "zapped clean", "stares back"
- "changes everything", "transforms"
- "revolutionary", "game-changing"

BANNED ACADEMIC PATTERNS:
- "results suggest", "findings indicate"
- "it is noteworthy that"
- "serves to demonstrate"

BANNED REPETITIVE OPENINGS:
- "[Material] enables..."
- "[Material] achieves..."
- "Laser cleaning of [material]..."
- "[Gerund phrase] with [material]..."

SENTENCE VARIATION REQUIRED:
- Start sentences differently
- Vary sentence lengths
- Mix structures (simple, compound, complex)
- Avoid formulaic patterns
EOF
```

### **Fix 3: Clean Up Component Templates**
**Remove hardcoded guidance that should be dynamic**:

**Current `caption.txt` has**:
```
{technical_guidance}      # ✅ KEEP - Dynamic placeholder
{sentence_guidance}       # ✅ KEEP - Dynamic placeholder

# But also has these redundant sections:
VOICE & APPROACH:         # ❌ REMOVE - Should be in system/base.txt
Write like you're explaining...

{sentence_guidance}       # ❌ DUPLICATE
```

**Should be**:
```
You are {author} from {country}, writing a caption about {material}.

TASK: Write two short paragraphs describing {material} at 1000x magnification.
- Paragraph 1: Contaminated surface before laser cleaning  
- Paragraph 2: Clean surface after laser treatment

{technical_guidance}

{sentence_guidance}

FORMATTING:
- Complete sentences (no fragments)
- Separate the two paragraphs with ONE blank line
- NO labels like "Before:", "After:"

OUTPUT: Just the two paragraphs.
```

---

## 🎯 **Validation Checklist**

Use this checklist to ensure proper separation of concerns:

### **For Each Component Template** (`prompts/components/*.txt`):
- [ ] Defines component structure (paragraphs, format, output shape)
- [ ] Has placeholders for dynamic content: `{technical_guidance}`, `{sentence_guidance}`
- [ ] Specifies formatting rules (punctuation, labels, spacing)
- [ ] Lists component-specific banned patterns
- [ ] Does NOT hardcode voice characteristics (uses `{author}`, `{country}`)
- [ ] Does NOT hardcode technical guidance (uses placeholder)
- [ ] Does NOT hardcode sentence rules (uses placeholder)

### **For System Prompt** (`prompts/system/base.txt`):
- [ ] Contains universal writing standards
- [ ] No component-specific instructions
- [ ] No domain-specific instructions
- [ ] Applies to ALL content generation

### **For Voice Personas** (`prompts/personas/*.yaml`):
- [ ] Contains author name, country, linguistic traits
- [ ] Has component-specific sentence styles
- [ ] Grammar norms and preferences
- [ ] No content structure (that's in component templates)

### **For Anti-AI Rules** (`prompts/rules/anti_ai_rules.txt`):
- [ ] Lists banned corporate phrases
- [ ] Lists banned theatrical language
- [ ] Lists banned repetitive patterns
- [ ] No component-specific structure

---

## 📊 **Benefits of Correct Separation**

### **Maintainability**:
- ✅ Change voice → Edit 1 persona YAML file
- ✅ Change component structure → Edit 1 component template
- ✅ Change technical guidance → Edit dynamic_config.py
- ✅ Add new component → Create 1 template + config entry

### **Clarity**:
- ✅ Clear responsibility: System > Component > Voice > Evaluation
- ✅ No duplication between layers
- ✅ Easy to understand where each instruction comes from

### **Flexibility**:
- ✅ Dynamic parameters adapt to context
- ✅ Voice profiles work for ALL components
- ✅ Component templates work for ALL voices
- ✅ System standards apply universally

### **Compliance**:
- ✅ Template-Only Policy: All prompts in template files
- ✅ Component Discovery: Templates define components
- ✅ Prompt Purity: Zero hardcoded prompts in code
- ✅ Dynamic Configuration: Parameters calculated at runtime

---

## 🔍 **Testing Correct Separation**

### **Test 1: Component Template Validation**
```bash
# Each component template should:
# 1. Be in prompts/components/
# 2. Have placeholders: {technical_guidance}, {sentence_guidance}, {author}, {country}
# 3. Define structure, not voice

for template in prompts/components/*.txt; do
    echo "Checking $template:"
    grep -q "{technical_guidance}" "$template" && echo "  ✅ Has technical placeholder" || echo "  ❌ Missing technical placeholder"
    grep -q "{sentence_guidance}" "$template" && echo "  ✅ Has sentence placeholder" || echo "  ❌ Missing sentence placeholder"
    grep -q "{author}" "$template" && echo "  ✅ Has author placeholder" || echo "  ❌ Missing author placeholder"
done
```

### **Test 2: Voice Persona Validation**
```bash
# Each persona should have component-specific sentence styles
for persona in prompts/personas/*.yaml; do
    echo "Checking $persona:"
    grep -q "sentence_structure:" "$persona" && echo "  ✅ Has sentence structure" || echo "  ❌ Missing sentence structure"
    grep -q "caption:" "$persona" && echo "  ✅ Has caption style" || echo "  ❌ Missing caption style"
    grep -q "subtitle:" "$persona" && echo "  ✅ Has subtitle style" || echo "  ❌ Missing subtitle style"
done
```

### **Test 3: Generation Test**
```bash
# Test that prompts load correctly
python3 run.py --caption "Aluminum" --skip-integrity-check

# Check output has BOTH before and after sections
# If AFTER is empty, prompts are not loading correctly
```

---

## 📝 **Summary**

**Current State**:
- ⚠️ Prompts in wrong location (`domains/materials/prompts/` instead of `prompts/components/`)
- ⚠️ Missing `anti_ai_rules.txt`
- ⚠️ Some mixed concerns in templates

**Required Actions**:
1. Move prompts to `prompts/components/`
2. Create `prompts/rules/anti_ai_rules.txt`
3. Clean up templates to use placeholders for dynamic content

**Expected Outcome**:
- ✅ Clear separation: System → Component → Voice → Evaluation
- ✅ Dynamic parameters injected at runtime
- ✅ No duplication between layers
- ✅ Easy to maintain and extend

---

**Last Updated**: November 20, 2025
**Priority**: HIGH - Blocking correct caption generation
**Effort**: 30 minutes to fix all 3 issues
