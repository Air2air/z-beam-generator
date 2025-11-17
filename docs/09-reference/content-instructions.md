# Content Instruction Policy

## 🚨 CRITICAL ARCHITECTURAL REQUIREMENT

**Content instructions MUST ONLY exist in `prompts/*.txt` files.**  
**They MUST NOT exist anywhere in the `/processing` folder.**

---

## The Rule

### ✅ ALLOWED: Content instructions in prompts/*.txt
```
prompts/subtitle.txt:
  CONTENT INSTRUCTIONS:
  - Focus on: Most distinctive characteristics
  - Format: Single compelling statement
  - Style: Conversational but precise
```

### ❌ FORBIDDEN: Content instructions in processing/*.py
```python
# NEVER do this in processing/ folder:
format_rules = "Single compelling statement, no period"
focus_areas = "Most distinctive characteristics"
style_notes = "Conversational but precise"
```

---

## Rationale

### Why This Separation Matters

1. **User Control**: Non-technical users can edit prompt templates without touching code
2. **Rapid Iteration**: Content strategy changes don't require code deployment
3. **Clear Separation**: Technical mechanism (code) vs content strategy (prompts)
4. **Version Control**: Content changes tracked separately from code changes
5. **Testing Clarity**: Tests verify mechanism, prompts verify content strategy

---

## Architecture

### Two-Layer System

```
┌─────────────────────────────────────────┐
│     prompts/*.txt files                 │
│     (WHAT to write)                     │
│  - Focus areas                          │
│  - Format requirements                  │
│  - Style guidance                       │
│  - Content strategy                     │
└─────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│     processing/*.py files               │
│     (HOW to generate)                   │
│  - API integration                      │
│  - Length calculation                   │
│  - Voice modulation                     │
│  - Technical mechanisms                 │
└─────────────────────────────────────────┘
```

### Data Flow

1. **Load Template**: `PromptBuilder._load_component_template(component_type)`
   - Reads `prompts/{component_type}.txt`
   - Returns template with all content instructions

2. **Build Context**: Template content added to prompt
   - Contains: focus, format, style guidance
   - Replaces placeholders: `{author}`, `{material}`, `{country}`

3. **Generate**: Processing code handles technical aspects
   - Word count calculations
   - Voice parameter application
   - API communication
   - Quality validation

---

## File Structure

### Prompt Template Files
All located in `prompts/` directory:

```
prompts/
├── subtitle.txt          # Subtitle content instructions
├── caption.txt           # Caption content instructions
├── description.txt       # Description content instructions
├── faq.txt              # FAQ content instructions
└── troubleshooter.txt   # Troubleshooting content instructions
```

### Required Template Format

Each template MUST contain:

```
You are {author}, writing a {component_type} about {material}...

CONTENT INSTRUCTIONS:
- Focus on: [What to emphasize]
- Format: [Structural requirements]
- Style: [Voice and tone guidance]
- [Component-specific rules]

CONTEXT:
{facts}

Write the {component_type}:
```

---

## Component Specification

### ComponentSpec Dataclass
Contains ONLY structural metadata:

```python
@dataclass
class ComponentSpec:
    """CRITICAL: Content instructions are in prompts/*.txt files only."""
    name: str                           # Component identifier
    default_length: int                 # Target word count
    end_punctuation: bool = True        # Period at end?
    min_length: Optional[int] = None    # Minimum words
    max_length: Optional[int] = None    # Maximum words
    prompt_template_file: Optional[str] = None  # Path to template
```

**What ComponentSpec DOES NOT contain:**
- ❌ `format_rules` - REMOVED, belongs in prompts/*.txt
- ❌ `focus_areas` - REMOVED, belongs in prompts/*.txt
- ❌ `style_notes` - REMOVED, belongs in prompts/*.txt

### SPEC_DEFINITIONS Dictionary
Contains ONLY technical metadata:

```python
SPEC_DEFINITIONS = {
    'subtitle': {
        'end_punctuation': False,  # Technical: no period
        'prompt_template_file': 'prompts/subtitle.txt'  # Where to find instructions
    }
}
```

**What SPEC_DEFINITIONS DOES NOT contain:**
- ❌ Content instructions (focus, format, style)
- ❌ Writing guidance
- ❌ Strategic direction

---

## Enforcement

### Automated Tests
Located in `tests/test_content_instruction_policy.py`:

1. **test_no_content_instructions_in_processing_folder()**
   - Scans all `/processing/*.py` files
   - Flags any `format_rules`, `focus_areas`, `style_notes` assignments
   - **FAIL** if found → Move to prompts/*.txt

2. **test_component_spec_no_content_fields()**
   - Verifies `ComponentSpec` dataclass structure
   - **FAIL** if content instruction fields present
   - Expected fields: name, lengths, punctuation, template_file only

3. **test_spec_definitions_no_content_instructions()**
   - Verifies `SPEC_DEFINITIONS` dict keys
   - **FAIL** if content instruction keys present
   - Expected keys: end_punctuation, prompt_template_file only

4. **test_all_components_have_prompt_template_files()**
   - Verifies each component has a template file
   - **FAIL** if missing → Create prompts/{component}.txt

5. **test_prompt_templates_contain_content_instructions()**
   - Verifies templates have proper structure
   - **FAIL** if missing sections → Add CONTENT INSTRUCTIONS

### CI/CD Integration
These tests run automatically on every commit to prevent violations.

---

## Migration Guide

### If You Find Content Instructions in /processing

**Step 1: Identify the instructions**
```python
# Found in processing/some_file.py:
format_rules = "Single statement, no period"
focus_areas = "Most distinctive characteristics"
```

**Step 2: Move to appropriate prompt template**
```
# Add to prompts/subtitle.txt:
CONTENT INSTRUCTIONS:
- Focus on: Most distinctive characteristics
- Format: Single statement, no period
```

**Step 3: Remove from processing/ code**
Delete the assignment from Python files.

**Step 4: Update references**
If code referenced these fields:
```python
# Before:
prompt += f"Format: {spec.format_rules}"

# After:
# Template already contains this - remove the line
```

---

## Benefits

### For Content Strategists
- ✅ Edit content guidance without code knowledge
- ✅ Test new prompts instantly (no deployment)
- ✅ Version control for content strategy
- ✅ A/B test different approaches easily

### For Developers
- ✅ Clear separation of concerns
- ✅ Code focuses on technical mechanisms only
- ✅ Fewer merge conflicts (content vs code)
- ✅ Easier testing (mock templates, not code)

### For System
- ✅ Maintainable architecture
- ✅ Flexible content strategy
- ✅ Clear ownership boundaries
- ✅ Auditable changes

---

## Examples

### ✅ CORRECT: Prompt Template
```
prompts/caption.txt:

You are {author}, writing a microscopy caption about {material}.

CONTENT INSTRUCTIONS:
- Focus on: Surface analysis details, microscopy observations
- Format: Technical description with 1-2 measurements
- Style: Technical but accessible; mix short and long sentences
- End with period (full punctuation required)

CONTEXT:
{facts}

Write the caption:
```

### ✅ CORRECT: Processing Code
```python
# processing/generation/prompt_builder.py

def _build_spec_driven_prompt(...):
    # Load template (contains all content instructions)
    template = PromptBuilder._load_component_template(spec.name)
    
    # Replace placeholders
    context = template.format(
        author=author,
        material=topic,
        country=country,
        facts=facts
    )
    
    # Add technical requirements only
    requirements = [
        f"Length: {length} words (range: {spec.min_length}-{spec.max_length})",
        f"Terminology: {terminology}"
    ]
```

### ❌ WRONG: Hardcoded Content Instructions
```python
# DON'T DO THIS in processing/ folder:

SPEC_DEFINITIONS = {
    'subtitle': {
        'format_rules': "Single statement, no period",  # ❌ Belongs in prompts/subtitle.txt
        'focus_areas': "Most distinctive characteristics",  # ❌ Belongs in prompts/subtitle.txt
        'style_notes': "Conversational but precise"  # ❌ Belongs in prompts/subtitle.txt
    }
}
```

---

## Summary

### The One Rule
**Content instructions live in `prompts/*.txt` files ONLY.**

### What Goes Where

**prompts/*.txt files:**
- Focus areas (what to emphasize)
- Format rules (structural requirements)
- Style guidance (voice and tone)
- Content strategy

**processing/*.py files:**
- Word count calculations
- Voice parameter application
- API integration
- Quality validation
- Technical mechanisms

### Enforcement
- 5 automated tests ensure compliance
- Tests run on every commit
- Violations cause build failure
- Clear error messages guide fixes

---

**Last Updated**: 2025-01-21  
**Status**: ✅ Enforced by automated tests
