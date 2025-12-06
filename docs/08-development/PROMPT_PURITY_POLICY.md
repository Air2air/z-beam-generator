# Prompt Purity Policy

**Status**: ✅ ACTIVE  
**Effective Date**: November 18, 2025  
**Severity**: CRITICAL - System Architecture Requirement  
**Enforcement**: Automated tests + Manual code review

---

## Overview

The **Prompt Purity Policy** ensures that all content generation instructions reside ONLY in prompt template files (`prompts/`), never hardcoded in generator Python code. This separation of concerns maintains clean architecture, enables non-technical prompt editing, and prevents prompt drift where code overrides diverge from documented templates.

## Policy Statement

**ALL content generation instructions MUST exist ONLY in prompt template files. ZERO prompt text, content rules, or generation instructions are permitted in generator code.**

---

## Core Principles

### 1. Single Source of Truth

**Prompt templates** (`domains/*/text/prompts/*.txt`, `shared/text/templates/personas/*.yaml`) are the ONLY authoritative source for:
- Content instructions
- Style guidance
- Voice/tone rules
- Format requirements
- Focus areas
- Forbidden phrases
- Required elements

**Generator code** (`processing/`) handles ONLY:
- Technical mechanisms (API calls, retries, logging)
- Parameter application (temperature, penalties, voice params)
- Quality validation (Winston, readability, realism gates)
- Data flow (reading templates, writing results)

### 2. Zero Prompt Overrides

**FORBIDDEN in generator code**:
```python
# ❌ VIOLATION: Hardcoded prompt text in code
system_prompt = "You are a professional technical writer..."

# ❌ VIOLATION: Inline content instructions
prompt += "\nCRITICAL RULE: Write ONLY in qualitative terms..."

# ❌ VIOLATION: Dynamic prompt injection
if condition:
    prompt = prompt.replace("text", "YOU MUST NOT INCLUDE...")

# ❌ VIOLATION: Content rules in code
instructions = "ABSOLUTELY FORBIDDEN: Any numbers, measurements..."
```

**CORRECT approach**:
```python
# ✅ CORRECT: Load prompt from template file
prompt_template = self._load_prompt_template('caption.txt')

# ✅ CORRECT: Apply parameters to template
prompt = self._apply_parameters(prompt_template, parameters)

# ✅ CORRECT: Pass prompt as-is to API
response = api_client.generate(prompt=prompt, temperature=temp)
```

### 3. Template Parameterization

Prompts may contain **placeholders** for dynamic values, but NOT content instructions:

**✅ ALLOWED placeholders**:
```
{material_name}
{property_values}
{component_type}
{word_count}
{context_data}
```

**❌ FORBIDDEN inline instructions**:
```python
# Don't do this:
prompt = template.format(
    material=material,
    extra_rules="Never use numbers, measurements, or units"  # ❌ Content instruction
)
```

**✅ CORRECT approach**:
Put the instruction IN THE TEMPLATE FILE:
```
# In domains/materials/text/prompts/caption.txt:
Write about {material_name} properties.

CRITICAL: Never use numbers, measurements, or units.
Focus on qualitative descriptions only.
```

---

## Violation Types & Examples

### Type 1: System Prompt Hardcoding

**VIOLATION** (found in `processing/orchestrator.py:614`):
```python
system_prompt = "You are a professional technical writer creating concise, clear content."
```

**WHY IT'S WRONG**: This content instruction should be in a template file where it can be edited, versioned, and reviewed by non-programmers.

**FIX**: Create `shared/text/templates/system/technical_writer.txt`:
```
You are a professional technical writer creating concise, clear content.
```

Then load it:
```python
system_prompt = self._load_prompt_template('system/technical_writer.txt')
```

---

### Type 2: Conditional Prompt Injection

**VIOLATION** (found in `processing/orchestrator.py:621-626`):
```python
if tech_intensity < 0.15:
    system_prompt = (
        "You are a professional technical writer creating concise, clear content. "
        "CRITICAL RULE: Write ONLY in qualitative, conceptual terms. "
        "ABSOLUTELY FORBIDDEN: Any numbers, measurements, units, or technical specifications..."
    )
```

**WHY IT'S WRONG**: Content instructions are hardcoded inline based on parameter values. This creates hidden prompt logic that's not visible in template files.

**FIX**: Create `prompts/modes/qualitative_only.txt`:
```
You are a professional technical writer creating concise, clear content.

CRITICAL RULE: Write ONLY in qualitative, conceptual terms.
ABSOLUTELY FORBIDDEN: Any numbers, measurements, units, or technical specifications.
Use ONLY descriptive words: 'strong', 'heat-resistant', 'conductive', 'durable'.
```

Then load conditionally:
```python
if tech_intensity < 0.15:
    system_prompt = self._load_prompt_template('modes/qualitative_only.txt')
else:
    system_prompt = self._load_prompt_template('system/technical_writer.txt')
```

---

### Type 3: Dynamic Prompt Modification

**VIOLATION** (found in `processing/orchestrator.py:337-341`):
```python
prompt = prompt.replace(
    "ABSOLUTELY NO technical specifications",
    "YOU MUST NOT INCLUDE ANY NUMBERS WITH UNITS - THIS IS THE MOST IMPORTANT RULE"
)
```

**WHY IT'S WRONG**: Runtime string replacement creates prompt variations not reflected in template files. The "escalated" instruction is invisible to prompt reviewers.

**FIX**: Define intensity levels IN THE TEMPLATE:
```
# In domains/materials/text/prompts/caption.txt:

{qualitative_emphasis}

Write about {material_name}...
```

Then in code, select the emphasis level:
```python
if attempt == 1:
    emphasis = "ABSOLUTELY NO technical specifications"
elif attempt >= 3:
    emphasis = "CRITICAL: NO numbers with units - qualitative descriptions only"
else:
    emphasis = ""

prompt = template.format(
    qualitative_emphasis=emphasis,
    material_name=material
)
```

Or better, create separate template files:
- `prompts/modes/qualitative_standard.txt`
- `prompts/modes/qualitative_strict.txt`

---

### Type 4: Inline Content Rules

**VIOLATION** (found in `processing/generator.py:1096-1097`):
```python
"CRITICAL RULE: Write ONLY in qualitative, conceptual terms. "
"ABSOLUTELY FORBIDDEN: Any numbers, measurements, units, or technical specifications. "
```

**WHY IT'S WRONG**: Same content instruction duplicated in multiple files (orchestrator.py, generator.py, unified_orchestrator.py). No single source of truth.

**FIX**: Extract to `prompts/rules/no_technical_specs.txt`:
```
CRITICAL RULE: Write ONLY in qualitative, conceptual terms.
ABSOLUTELY FORBIDDEN: Any numbers, measurements, units, or technical specifications.
Examples of forbidden content: '110 GPa', '1941 K', '400 MPa', '41,000,000 S/m'
Use descriptive words instead: 'strong', 'heat-resistant', 'conductive', 'durable'
```

Then include it in relevant prompts:
```python
base_prompt = self._load_prompt_template('components/caption.txt')
if tech_intensity < 0.15:
    rules = self._load_prompt_template('rules/no_technical_specs.txt')
    prompt = f"{base_prompt}\n\n{rules}"
```

---

## Allowed Use Cases

### ✅ Technical Parameters (NOT Content Instructions)

These are **technical controls**, not content instructions:

```python
# ✅ ALLOWED: API parameters
temperature = 0.8
max_tokens = 250
frequency_penalty = 0.0
presence_penalty = 0.5

# ✅ ALLOWED: Voice parameters
voice_params = {
    'formality': 0.7,
    'technical_intensity': 0.85,
    'sentence_rhythm_variation': 0.6
}

# ✅ ALLOWED: Quality gates
if ai_score > 0.20:
    reject_content()

if realism_score < 7.0:
    retry_generation()
```

These control HOW the API behaves, not WHAT content to generate.

---

### ✅ Dynamic Data Insertion (NOT Instructions)

Inserting **data** into prompts is allowed:

```python
# ✅ ALLOWED: Material properties
prompt = template.format(
    material_name="Aluminum",
    density="2.7 g/cm³",
    melting_point="660°C"
)

# ✅ ALLOWED: Context data
prompt = template.format(
    before_image="Contaminated surface with rust",
    after_image="Clean surface, no oxidation"
)
```

This is **data**, not **instructions**. The template defines HOW to use the data.

---

## Enforcement

### Automated Testing

**Test Suite**: `tests/test_prompt_purity.py` (to be created)

```python
def test_no_hardcoded_prompts_in_generators():
    """Verify no prompt text hardcoded in generator files."""
    generator_files = [
        'processing/generator.py',
        'processing/orchestrator.py',
        'processing/unified_orchestrator.py'
    ]
    
    forbidden_patterns = [
        r'system_prompt = ["\']',  # Hardcoded system prompts
        r'CRITICAL RULE:',
        r'ABSOLUTELY FORBIDDEN:',
        r'YOU MUST',
        r'Write about',
        r'Create content',
        r'Generate text'
    ]
    
    for file_path in generator_files:
        content = Path(file_path).read_text()
        for pattern in forbidden_patterns:
            matches = re.findall(pattern, content)
            assert len(matches) == 0, \
                f"Found hardcoded prompt in {file_path}: {pattern}"
```

---

### Manual Code Review Checklist

Before merging code that touches generation:

- [ ] No `system_prompt = "..."` assignments with content instructions
- [ ] No `CRITICAL RULE:` or `ABSOLUTELY FORBIDDEN:` strings in code
- [ ] No `prompt.replace()` or `prompt +=` with instruction text
- [ ] No conditional prompt injection based on parameters
- [ ] All content instructions exist in `prompts/` directory
- [ ] Prompt templates are loaded via `_load_prompt_template()`
- [ ] Only technical parameters (temp, penalties) in code

---

## Migration Guide

### Step 1: Identify Violations

Search codebase for hardcoded prompts:

```bash
# Find hardcoded system prompts
grep -rn 'system_prompt = ["\']' processing/

# Find content instruction keywords
grep -rn 'CRITICAL RULE\|ABSOLUTELY FORBIDDEN\|YOU MUST' processing/

# Find dynamic prompt modification
grep -rn 'prompt.replace\|prompt +=' processing/
```

---

### Step 2: Extract to Template Files

For each violation found:

1. **Create template file** in `prompts/`:
   ```
   prompts/
     system/
       technical_writer.txt
     modes/
       qualitative_only.txt
     rules/
       no_technical_specs.txt
   ```

2. **Move content** from code to template

3. **Load template** in code:
   ```python
   template_path = 'modes/qualitative_only.txt'
   prompt = self._load_prompt_template(template_path)
   ```

---

### Step 3: Test Equivalence

Verify migrated prompts produce identical output:

```python
# Before migration
old_prompt = "You are a professional technical writer..."

# After migration
new_prompt = self._load_prompt_template('system/technical_writer.txt')

# Verify content matches
assert old_prompt.strip() == new_prompt.strip()
```

---

### Step 4: Update Documentation

Document the new template files:

```markdown
# prompts/README.md

## Template Files

### System Prompts
- `system/technical_writer.txt` - Base system prompt for all generations
- `modes/qualitative_only.txt` - Qualitative mode (no numbers/units)

### Rules
- `rules/no_technical_specs.txt` - Strict no-numbers rule
```

---

## Current Violations (As of Nov 18, 2025)

### Critical Violations to Fix

| File | Line | Violation | Priority |
|------|------|-----------|----------|
| `processing/orchestrator.py` | 614 | Hardcoded system_prompt | HIGH |
| `processing/orchestrator.py` | 621-626 | Conditional prompt injection | HIGH |
| `processing/orchestrator.py` | 337-341 | Dynamic prompt.replace() | HIGH |
| `processing/generator.py` | 1096-1097 | Inline CRITICAL RULE text | HIGH |
| `processing/unified_orchestrator.py` | 1034-1035 | Duplicate inline rules | MEDIUM |

### Recommended Fixes

1. **Create `prompts/system/` directory** with base system prompts
2. **Create `prompts/modes/` directory** for conditional modes (qualitative_only, etc.)
3. **Create `prompts/rules/` directory** for reusable rule snippets
4. **Implement `_load_prompt_template()` helper** if not exists
5. **Replace all hardcoded strings** with template loads
6. **Add automated tests** to prevent regressions

---

## Benefits of Compliance

### 1. Maintainability
- Non-programmers can edit prompts without touching code
- Changes visible in git diffs of .txt files, not .py files
- Single source of truth eliminates prompt drift

### 2. Testability
- Prompt variations testable independently
- A/B testing easier with separate template files
- Rollback to previous prompts via git without code changes

### 3. Transparency
- All generation instructions visible in `prompts/` directory
- No hidden prompt logic buried in code
- Easier to audit and review prompts

### 4. Flexibility
- Swap prompts without code deployment
- Experiment with prompt variations safely
- Reuse prompt components across generators

---

## Related Policies

- **[Content Instruction Policy](../prompts/CONTENT_INSTRUCTION_POLICY.md)** - Where content rules belong
- **[Component Discovery Policy](../architecture/COMPONENT_DISCOVERY.md)** - How components are defined
- **[Hardcoded Value Policy](./HARDCODED_VALUE_POLICY.md)** - No hardcoded config values

---

## Exemptions

### None Permitted

There are **NO exemptions** to this policy. All prompt text must reside in template files.

**Temporary workarounds** during migration are acceptable IF:
1. Clearly marked with `# TODO: PROMPT_PURITY - Extract to template`
2. Tracked in issue tracker with deadline
3. Covered by test that expects failure until fixed

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-18 | 1.0 | Initial policy document | System |
| 2025-11-18 | 1.0 | Documented 5 critical violations | System |

---

## Policy Enforcement

**Automatic**: Integrity checker validates prompt purity (to be implemented)  
**Manual**: Code review checklist for all generation code changes  
**Exception Process**: None - all prompts must be in template files  
**Review Cycle**: Every commit touching `processing/` directory

**Contact**: System administrators for questions about this policy.
