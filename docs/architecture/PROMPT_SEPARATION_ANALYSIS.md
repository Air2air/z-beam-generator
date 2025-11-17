# Prompt Separation of Concerns Analysis

**Date**: November 16, 2025  
**Status**: Post-Option A Architecture  
**Purpose**: Analyze separation of concerns and reorganize prompt folder

---

## 📊 Current State Analysis

### ✅ What's CORRECT (After Option A):

#### 1. **Component Task Specifications** ✅
**Location**: `prompts/components/{component}.txt` (caption.txt, subtitle.txt, etc.)  
**Purpose**: Define WHAT to generate and basic format  
**Content**: Task description, output requirements, formatting rules  
**Separation**: ✅ GOOD - Clean task definitions without implementation details

**Example** (caption.txt):
```
TASK: Write two caption paragraphs for {material}
Paragraph 1: Contaminated surface before cleaning
Paragraph 2: Clean surface after laser treatment
CRITICAL FORMATTING: [formatting rules]
```

#### 2. **Author Voice Personas** ✅
**Location**: `prompts/personas/{country}.yaml`  
**Purpose**: Define HOW each author writes (linguistic patterns, style)  
**Content**: Style patterns, sentence structure, vocabulary approach  
**Separation**: ✅ GOOD - Abstract patterns without content instructions

**Example** (united_states.yaml):
```yaml
style_patterns:
  sentence_structure:
    - "Front-load main action: [Subject] [verb] [object]"
  vocabulary_approach:
    - "Action verbs: removes, restores, improves"
```

#### 3. **Grammar Standards** ✅
**Location**: `prompts/grammar_rules.txt`  
**Purpose**: Define universal grammar rules for all generations  
**Content**: Sentence length variation, punctuation, spelling standards  
**Separation**: ✅ GOOD - Generic rules separate from component/author specifics

#### 4. **Anti-AI Rules** ✅
**Location**: `prompts/anti_ai_rules.txt`  
**Purpose**: Define prohibited patterns to avoid AI detection  
**Content**: Banned phrases, structural patterns, variation requirements  
**Separation**: ✅ GOOD - Universal prohibitions separate from generation logic

---

### ❌ What's PROBLEMATIC:

#### 1. **voice_rules.txt** ❌ REDUNDANT/UNUSED
**Location**: `prompts/voice_rules.txt`  
**Content**: Generic voice template with placeholders  
**Problem**: 
- NOT loaded by any code (grep search found zero matches)
- Duplicates functionality of persona files
- Simple template that could be inline code
- Adds confusion without value

**Recommendation**: 🗑️ DELETE - Functionality covered by personas/*.yaml

#### 2. **component_specs.yaml** ❌ VIOLATES POLICY
**Location**: `prompts/component_specs.yaml`  
**Content**: Component lengths + CONTENT INSTRUCTIONS  
**Problem**:
```yaml
subtitle:
  format_rules: "No period at end; concise and punchy"  # ❌ Content instruction
  focus_areas: "Unique characteristics, key benefits"    # ❌ Content instruction
  style_notes: "Professional but natural"                # ❌ Content instruction
```
- Violates "no content instructions outside component prompts" policy
- Content instructions belong in `prompts/components/subtitle.txt`
- Only structural metadata (lengths, end_punctuation) should be here
- NOT loaded by code (grep search found zero matches)

**Recommendation**: 
- 🗑️ DELETE this file
- Structural metadata moved to `processing/config.yaml` (already there)
- Content instructions already in component .txt files (correct location)

#### 3. **ai_detection_patterns.txt** ⚠️ WRONG LOCATION
**Location**: `prompts/ai_detection_patterns.txt`  
**Content**: Pattern matching rules for AI detection (technical, not content)  
**Problem**:
- This is DETECTION LOGIC, not content generation guidance
- Used by `processing/detection/ai_detection.py` and `ensemble.py`
- Belongs in `processing/detection/` folder, not `prompts/`
- Mixing operational config with content prompts

**Recommendation**: 
- 📦 MOVE to `processing/detection/ai_detection_patterns.txt`
- Update import paths in ai_detection.py and ensemble.py
- Keep prompts/ for content instructions only

---

## 🎯 Correct Separation of Concerns

### The 4-Layer Model (CORRECT):

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: TASK SPECIFICATION (What to generate)             │
│ Location: prompts/components/{component}.txt                │
│ Content: Task description, output format, requirements      │
│ Example: "Write two caption paragraphs..."                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: UNIVERSAL CONSTRAINTS (What to avoid)             │
│ Location: prompts/rules/                                    │
│   - grammar_rules.txt (generic grammar standards)           │
│   - anti_ai_rules.txt (prohibited patterns)                 │
│ Content: Universal rules for all generations                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: AUTHOR VOICE (How to write)                       │
│ Location: prompts/personas/{country}.yaml                   │
│ Content: Style patterns, linguistic traits, rhythm          │
│ Example: "Front-load main action: [Subject] [verb]"         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: DYNAMIC OVERRIDES (Critical requirements)         │
│ Location: Generated by code (prompt_builder.py)             │
│ Content: Technical intensity overrides, emergency rules     │
│ Example: "🔥 CRITICAL: NO technical specs allowed"          │
└─────────────────────────────────────────────────────────────┘
```

### What Should Be WHERE:

| Content Type | Correct Location | Purpose |
|--------------|------------------|---------|
| Component task specs | `prompts/components/{name}.txt` | Define generation task |
| Grammar rules | `prompts/rules/grammar_rules.txt` | Universal grammar standards |
| Anti-AI rules | `prompts/rules/anti_ai_rules.txt` | Prohibited patterns |
| Author personas | `prompts/personas/{country}.yaml` | Writing style patterns |
| Detection patterns | `processing/detection/patterns/` | AI detection logic |
| Component metadata | `processing/config.yaml` | Lengths, punctuation flags |
| Archive | `prompts/archive/` | Deprecated templates |
| Documentation | `prompts/README.md` | Explain structure |

---

## 🗂️ Proposed Folder Reorganization

### Current Structure:
```
prompts/
├── README.md
├── ai_detection_patterns.txt        ❌ Wrong location
├── anti_ai_rules.txt                 ✅ Keep
├── grammar_rules.txt                 ✅ Keep
├── voice_rules.txt                   ❌ Delete (unused)
├── component_specs.yaml              ❌ Delete (violates policy)
├── caption.txt                       ✅ Move to components/
├── subtitle.txt                      ✅ Move to components/
├── description.txt                   ✅ Move to components/
├── faq.txt                           ✅ Move to components/
├── troubleshooter.txt                ✅ Move to components/
├── personas/                         ✅ Keep
│   ├── united_states.yaml
│   ├── italy.yaml
│   ├── indonesia.yaml
│   └── taiwan.yaml
└── archive/                          ✅ Keep
    ├── legacy_caption_template.txt
    ├── legacy_subtitle_template.txt
    └── unified_template.txt
```

### Proposed Structure:
```
prompts/
├── README.md                         📖 Updated with structure guide
│
├── components/                       📁 NEW - Component task specs
│   ├── README.md                     📖 Explain component prompts
│   ├── caption.txt                   ✅ Moved from root
│   ├── subtitle.txt                  ✅ Moved from root
│   ├── description.txt               ✅ Moved from root
│   ├── faq.txt                       ✅ Moved from root
│   └── troubleshooter.txt            ✅ Moved from root
│
├── rules/                            📁 NEW - Universal constraints
│   ├── README.md                     📖 Explain rule files
│   ├── grammar_rules.txt             ✅ Moved from root
│   └── anti_ai_rules.txt             ✅ Moved from root
│
├── personas/                         📁 EXISTING - Author voices
│   ├── README.md                     📖 Explain persona system
│   ├── united_states.yaml            ✅ Keep
│   ├── italy.yaml                    ✅ Keep
│   ├── indonesia.yaml                ✅ Keep
│   └── taiwan.yaml                   ✅ Keep
│
└── archive/                          📁 EXISTING - Deprecated files
    ├── README.md                     📖 NEW - Explain archive purpose
    ├── legacy_caption_template.txt   ✅ Keep
    ├── legacy_subtitle_template.txt  ✅ Keep
    ├── unified_template.txt          ✅ Keep
    ├── voice_rules.txt               🗑️ Moved from root (deprecated)
    └── component_specs.yaml          🗑️ Moved from root (deprecated)
```

### Files to Move/Delete:

**MOVE to new locations:**
- `caption.txt` → `components/caption.txt`
- `subtitle.txt` → `components/subtitle.txt`
- `description.txt` → `components/description.txt`
- `faq.txt` → `components/faq.txt`
- `troubleshooter.txt` → `components/troubleshooter.txt`
- `grammar_rules.txt` → `rules/grammar_rules.txt`
- `anti_ai_rules.txt` → `rules/anti_ai_rules.txt`
- `ai_detection_patterns.txt` → `processing/detection/patterns/ai_detection_patterns.txt`

**MOVE to archive (deprecated):**
- `voice_rules.txt` → `archive/voice_rules.txt` (unused)
- `component_specs.yaml` → `archive/component_specs.yaml` (violates policy)

**CREATE new documentation:**
- `prompts/README.md` - Overall structure guide
- `prompts/components/README.md` - Component prompt guide
- `prompts/rules/README.md` - Rule file guide
- `prompts/personas/README.md` - Persona system guide
- `prompts/archive/README.md` - Archive purpose

---

## 📋 Code Changes Required

### 1. Update Component Template Loading
**File**: `processing/generation/prompt_builder.py`

```python
# BEFORE (line 66):
template_path = os.path.join('prompts', f'{component_type}.txt')

# AFTER:
template_path = os.path.join('prompts', 'components', f'{component_type}.txt')
```

### 2. Update Anti-AI Rules Loading
**File**: `processing/generation/prompt_builder.py`

```python
# BEFORE (line 48):
rules_path = os.path.join('prompts', 'anti_ai_rules.txt')

# AFTER:
rules_path = os.path.join('prompts', 'rules', 'anti_ai_rules.txt')
```

### 3. Update Grammar Rules References (if any)
**Search**: Need to check if grammar_rules.txt is explicitly loaded anywhere

### 4. Update AI Detection Patterns Path
**File**: `processing/detection/ai_detection.py` (line 40)

```python
# BEFORE:
PATTERNS_FILE = os.path.join(CURRENT_DIR, '..', '..', 'prompts', 'ai_detection_patterns.txt')

# AFTER:
PATTERNS_FILE = os.path.join(CURRENT_DIR, 'patterns', 'ai_detection_patterns.txt')
```

**File**: `processing/detection/ensemble.py` (line 73)

```python
# BEFORE:
return str(Path(__file__).parent.parent.parent / "prompts" / "ai_detection_patterns.txt")

# AFTER:
return str(Path(__file__).parent / "patterns" / "ai_detection_patterns.txt")
```

---

## ✅ Benefits of Reorganization

### 1. **Clear Separation of Concerns**
- Components define WHAT to generate
- Rules define WHAT TO AVOID
- Personas define HOW to write
- No overlap or confusion

### 2. **Easier Navigation**
- New developers find files by category
- Related files grouped together
- Purpose clear from folder structure

### 3. **Scalability**
- Add new components in `components/` folder
- Add new rules in `rules/` folder
- Add new authors in `personas/` folder
- Structure remains clear

### 4. **Policy Compliance**
- Content instructions ONLY in component prompts
- No content in config files
- Technical detection logic moved to processing/

### 5. **Reduced Clutter**
- Root folder no longer has 10+ files
- Clear hierarchy (3 main folders + archive)
- Deprecated files clearly separated

---

## 🚀 Migration Plan

### Phase 1: Preparation (5 min)
1. ✅ Create new folder structure
2. ✅ Create README files with documentation
3. ✅ Verify no additional code references

### Phase 2: Move Files (10 min)
1. ✅ Create `prompts/components/` folder
2. ✅ Move component .txt files
3. ✅ Create `prompts/rules/` folder
4. ✅ Move grammar_rules.txt and anti_ai_rules.txt
5. ✅ Create `processing/detection/patterns/` folder
6. ✅ Move ai_detection_patterns.txt
7. ✅ Move deprecated files to archive/

### Phase 3: Update Code (15 min)
1. ✅ Update prompt_builder.py (2 path changes)
2. ✅ Update ai_detection.py (1 path change)
3. ✅ Update ensemble.py (1 path change)
4. ✅ Search for any other references

### Phase 4: Validate (10 min)
1. ✅ Run test generation (all 4 authors)
2. ✅ Verify prompts load correctly
3. ✅ Verify AI detection still works
4. ✅ Run integrity check

### Phase 5: Documentation (10 min)
1. ✅ Update main README.md with new structure
2. ✅ Create folder-specific README files
3. ✅ Update developer documentation
4. ✅ Document deprecated files in archive/

**Total Time**: ~50 minutes

---

## 📝 README Templates

### prompts/README.md
```markdown
# Prompts Directory Structure

Content generation prompts organized by function.

## Structure

- **components/** - Component-specific task specifications (WHAT to generate)
- **rules/** - Universal constraints (WHAT TO AVOID)
- **personas/** - Author voice patterns (HOW to write)
- **archive/** - Deprecated/legacy files

## Adding New Components

1. Create `components/{component_name}.txt`
2. Define task, format, and output requirements
3. Follow existing component templates
4. Keep content instructions here ONLY

## See Also

- `components/README.md` - Component prompt guide
- `rules/README.md` - Rule file guide
- `personas/README.md` - Persona system guide
```

### prompts/components/README.md
```markdown
# Component Prompts

Task specifications for different content types.

## Purpose

Define WHAT to generate and basic formatting requirements.

## File Format

```plaintext
{context}  ← Placeholder for material facts

TASK: Clear description of what to generate

CRITICAL FORMATTING:
- Output structure requirements
- Sentence/paragraph rules
- Special formatting notes

OUTPUT ONLY: Specify exact output format
```

## Guidelines

1. ✅ **Include**: Task description, format rules, output requirements
2. ❌ **Exclude**: Author voice patterns (→ personas/), grammar rules (→ rules/)
3. Keep task-focused and component-specific
4. Use placeholders: {material}, {author}, {context}, {facts}

## Available Components

- caption.txt - Microscopy captions (2 paragraphs)
- subtitle.txt - Professional subtitles (no period)
- description.txt - Full descriptions (150 words)
- faq.txt - Question-answer format (100 words)
- troubleshooter.txt - Problem-solution format (120 words)
```

### prompts/rules/README.md
```markdown
# Universal Rules

Constraints applied to ALL generations regardless of component or author.

## Purpose

Define what to AVOID across all content types.

## Files

### grammar_rules.txt
Generic grammar standards:
- Sentence length variation requirements
- Punctuation standards
- Spelling conventions
- Active/passive voice balance

### anti_ai_rules.txt
Prohibited patterns to avoid AI detection:
- Banned phrases and words
- Structural patterns to avoid
- Variation requirements
- AI-characteristic patterns

## Guidelines

1. Rules must be universal (apply to all components)
2. Rules must be clear and actionable
3. Provide examples of good/bad patterns
4. Update based on detection feedback
```

### prompts/personas/README.md
```markdown
# Author Personas

Writing style patterns for authentic author voices.

## Purpose

Define HOW each author writes using abstract style patterns.

## File Format (YAML)

```yaml
style_patterns:
  sentence_structure:
    - "Pattern: [Subject] [verb] [object]"
  vocabulary_approach:
    - "Verb types: action, result, measurement"
  length_rhythm:
    - "30% short (under 12 words)"
  connector_usage:
    - "Minimal: and, thus, since"
```

## Guidelines

1. ✅ **Use abstract patterns**: "[Subject] [verb]" NOT "Steel removes contaminants"
2. ✅ **Focus on style**: Sentence structure, vocabulary, rhythm
3. ❌ **No content examples**: Avoid concrete laser cleaning examples
4. ❌ **No content instructions**: Task specs belong in components/

## Available Personas

- united_states.yaml - Direct American technical writing
- italy.yaml - Italian EFL with relative clauses
- indonesia.yaml - Indonesian EFL with cause-effect chains
- taiwan.yaml - East Asian EFL with data-first approach
```

### prompts/archive/README.md
```markdown
# Archive - Deprecated Files

Legacy files kept for reference only.

## Not Used in Current System

These files are NOT loaded by the current codebase:

- **voice_rules.txt** - Superseded by personas/*.yaml system
- **component_specs.yaml** - Violated content instruction policy
  - Content instructions moved to components/*.txt
  - Structural metadata moved to processing/config.yaml

## Legacy Templates

- **legacy_caption_template.txt** - Original caption prompt
- **legacy_subtitle_template.txt** - Original subtitle prompt  
- **unified_template.txt** - First attempt at unified prompt

## Do NOT Use These Files

Reference only for understanding system evolution.
Use current prompt structure in parent folders.
```

---

## 🎯 Summary

### Current State (After Option A):
✅ **Good separation**: Component prompts, personas, grammar rules, anti-AI rules  
❌ **Problems**: voice_rules.txt unused, component_specs.yaml violates policy, ai_detection_patterns.txt wrong location, flat folder structure

### Proposed State:
✅ **Clear hierarchy**: components/, rules/, personas/, archive/  
✅ **Policy compliant**: Content instructions only in component prompts  
✅ **Logical grouping**: Related files together, technical files in processing/  
✅ **Well documented**: README in each folder explaining purpose  
✅ **Scalable**: Easy to add new components, rules, personas

### Action Items:
1. Create folder structure
2. Move files to correct locations
3. Update 4 code paths
4. Create 5 README files
5. Validate with test generation

**Estimated Time**: 50 minutes  
**Risk**: Low (mostly file moves, minimal code changes)  
**Benefit**: Much clearer architecture, easier maintenance
