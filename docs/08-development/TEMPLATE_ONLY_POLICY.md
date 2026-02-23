# Template-Only Policy (Component Reusability)
**Effective Date**: November 18, 2025  
**Status**: ACTIVE REQUIREMENT  
**Related Policies**: Component Discovery Policy, Content Instruction Policy, Prompt Purity Policy

---

## Policy Statement

**ALL content instructions and formatting rules MUST exist ONLY in prompt templates stored in the consolidated prompt catalog (`prompts/registry/prompt_catalog.yaml`). The `/processing` system MUST be completely reusable across all domains with ZERO component-specific code.**

---

## Core Principles

### 1. Template-Driven Content
- **ALL** content instructions → prompt catalog `catalog.byPath` entries (e.g., `prompts/components/{component}.txt`)
- **ALL** format requirements → prompt catalog `catalog.byPath` entries
- **ALL** style guidelines → prompt catalog `catalog.byPath` entries
- **ALL** structural rules → prompt catalog `catalog.byPath` entries

### 2. Generic Processing Code
- **NO** `if component_type == 'micro':` checks
- **NO** component-specific methods (`_build_micro_prompt()`)
- **NO** hardcoded component lists
- **NO** component-specific extraction logic in generators
- **USE** registry-based discovery: `ComponentRegistry.get_spec(component_type)`
- **USE** strategy pattern: `adapter.extract_content(text, component_type)`

### 3. Configuration-Based Extraction
- Extraction strategies defined in `config.yaml`
- Strategies: `raw`, `before_after`, `json_list`
- Domain adapters implement extraction strategies
- Generators delegate to adapters (no extraction code)

---

## What Goes Where

### ✅ In Prompt Templates (prompt catalog `catalog.byPath` entries like `prompts/components/*.txt`)
- Content focus areas (what to emphasize)
- Format requirements (structure, length, punctuation)
- Style guidelines (voice, tone, formality)
- Forbidden phrases or patterns
- Required terminology
- Structural variations
- Example outputs

**Example** (`prompts/components/micro.txt` stored in `prompt_catalog.yaml`):
```
# Micro Generation Template

## Voice & Tone
- Professional technical documentation
- Objective, factual descriptions
- NO theatrical language
- NO casual phrases ("Wow", "quick zap")

## Structure
- Write before/after descriptions
- Format: BEFORE_TEXT: ... AFTER_TEXT: ...
- Technical verbs only (removes, restores, improves)
- Include 1-2 measurements when relevant

## Forbidden Phrases
- "changes everything"
- "game-changer"
- "quick zap"
- "perfectly clean"

## Generation Task
{material_context}
{generation_instructions}
```

### ✅ In Config Files (`generation/config.yaml`)
- Component word counts (default, min, max)
- Extraction strategies (raw, before_after, json_list)
- End punctuation settings
- Length variation ranges

**Example**:
```yaml
component_lengths:
  micro:
    default: 50
    min_words_before: 20
    max_words_before: 120
    extraction_strategy: before_after
  subtitle:
    default: 30
    extraction_strategy: raw
```

### ✅ In Code (`generation/*.py`, `postprocessing/*.py`, `learning/*.py`)
- Generic template loading
- Parameter application (temperature, penalties)
- Strategy-based extraction dispatch
- Registry pattern for component discovery
- Domain-specific data enrichment (material properties)

**Example** (Generic):
```python
def generate(self, identifier: str, component_type: str):
    # Load template (generic)
    template = self._load_prompt_template(component_type)
    
    # Apply parameters (generic)
    params = self.config.get_parameters(component_type)
    
    # Generate (generic)
    text = self.api_client.generate(template, params)
    
    # Extract (delegated to adapter)
    return self.adapter.extract_content(text, component_type)
```

### ❌ FORBIDDEN in Code
- `if component_type == 'micro':`
- `def _build_micro_prompt():`
- `def _extract_micro():`
- Inline content instructions: `"Write ONLY technical descriptions..."`
- Component-specific enrichment hints
- Hardcoded component lists: `['micro', 'subtitle', 'faq']`

---

## Implementation Requirements

### For Generators (`generation/core/generator.py`, etc.)

**✅ REQUIRED**:
```python
def _extract_content(self, text: str, component_type: str):
    """Delegate extraction to domain adapter."""
    return self.adapter.extract_content(text, component_type)
```

**❌ FORBIDDEN**:
```python
def _extract_content(self, text: str, component_type: str):
    if component_type == 'micro':
        return self._extract_micro(text)  # ❌ HARDCODED DISPATCH
    elif component_type == 'faq':
        return self._extract_faq(text)      # ❌ HARDCODED DISPATCH
```

### For Prompt Builders (`shared/text/utils/prompt_builder.py`)

**✅ REQUIRED**:
```python
def build_prompt(self, component_type: str, **kwargs):
    """Generic template loading."""
    template = self._load_prompt_template(component_type)
    return template.format(**kwargs)
```

**❌ FORBIDDEN**:
```python
def build_prompt(self, component_type: str, **kwargs):
    if component_type == 'micro':
        return self._build_micro_prompt(**kwargs)  # ❌ COMPONENT-SPECIFIC METHOD
```

### For Domain Adapters (`generation/core/adapters/*.py`)

**✅ REQUIRED**:
```python
def extract_content(self, text: str, component_type: str):
    """Strategy-based extraction."""
    registry = ComponentRegistry()
    spec = registry.get_spec(component_type)
    strategy = spec.extraction_strategy
    
    if strategy == 'raw':
        return text.strip()
    elif strategy == 'before_after':
        return self._extract_before_after(text)  # Generic method name
    elif strategy == 'json_list':
        return self._extract_json_list(text)     # Generic method name
```

**❌ FORBIDDEN**:
```python
def extract_content(self, text: str, component_type: str):
    if component_type == 'micro':
        return self._extract_micro(text)  # ❌ HARDCODED DISPATCH
```

---

## Adding New Components

### Before (NON-COMPLIANT - Required Code Changes)
```bash
# To add "description" component
1. ❌ Edit generator.py - add elif component_type == 'description'
2. ❌ Edit materials_adapter.py - add _extract_description() method
3. ❌ Edit prompt_builder.py - add _build_description_prompt() method
4. ❌ Add content instructions to code
5. ✅ Create prompt catalog entry `prompts/components/description.txt` in `prompts/registry/prompt_catalog.yaml`
Result: 4 code files + 1 template = NOT REUSABLE
```

### After (COMPLIANT - Zero Code Changes)
```bash
# To add "description" component
1. ✅ Create prompt catalog entry `prompts/components/description.txt` (all content instructions)
2. ✅ Add to config.yaml:
   component_lengths:
     description:
       default: 200
       extraction_strategy: raw
Result: 1 config file + 1 template = FULLY REUSABLE
```

---

## Validation

### Automated Checks (Integrity Checker)
```bash
python3 run.py --integrity-check
```

**Checks**:
- ✅ No `if component_type ==` in generation/postprocessing/learning Python modules
- ✅ No component-specific methods in generators
- ✅ No hardcoded component lists
- ✅ All content instructions in prompt catalog entries
- ✅ All extraction strategies in config.yaml

### Manual Review Checklist
- [ ] All component types discoverable from prompt catalog entries (`prompts/components/*.txt` keys)
- [ ] Zero hardcoded component names in generation/postprocessing/learning modules
- [ ] All content instructions in template files
- [ ] All extraction strategies in config.yaml
- [ ] Generic method names (`_extract_before_after`, not `_extract_micro`)
- [ ] Registry pattern used for component discovery
- [ ] Strategy pattern used for extraction

---

## Benefits

### 1. Full Reusability
- Generation and postprocessing modules work for **ANY** domain:
  - ✅ Materials (micro, subtitle, faq, description)
  - ✅ Contaminants (subtitle, troubleshooter)
  - ✅ Applications (description, use_case)
  - ✅ Regions (overview, regulations)
- Add new domain = zero generator engine rewrites

### 2. Easy Extension
- New component = create template + config entry
- No code changes required
- No generator-engine rewrites needed
- Instant availability across all domains

### 3. Maintainability
- Content changes = edit templates only
- No code deployment required
- Clear separation of concerns
- Single source of truth for content rules

### 4. Policy Compliance
- ✅ Component Discovery Policy
- ✅ Content Instruction Policy
- ✅ Prompt Purity Policy
- ✅ DRY Principle

---

## Migration Guide

### Phase 1: Remove Extraction from Generators
**Before**:
```python
def _extract_content(self, text, component_type):
    if component_type == 'micro':
        return self._extract_micro(text)
```

**After**:
```python
def _extract_content(self, text, component_type):
    return self.adapter.extract_content(text, component_type)
```

### Phase 2: Make Adapter Extraction Generic
**Before**:
```python
def extract_content(self, text, component_type):
    if component_type == 'micro':
        return self._extract_micro(text)
```

**After**:
```python
def extract_content(self, text, component_type):
    registry = ComponentRegistry()
    spec = registry.get_spec(component_type)
    strategy = spec.extraction_strategy
    
    if strategy == 'before_after':
        return self._extract_before_after(text)
```

### Phase 3: Remove Component-Specific Prompt Methods
**Before**:
```python
def _build_micro_prompt(self, ...):
    return f"""You are {author}, describing...
    MICRO-SPECIFIC INSTRUCTIONS...
    """
```

**After**:
```python
# REMOVED - Use generic template loading
# Content instructions now in prompt catalog entry prompts/components/micro.txt
```

### Phase 4: Move Content Instructions to Templates
**Before** (in code):
```python
if spec.name == "subtitle":
    enrichment_hints = """
- Lead with benefit, NOT raw specs
- Vary structure
"""
```

**After** (in template):
```
# prompt catalog entry: prompts/components/subtitle.txt
## Structure Guidelines
- Lead with benefit, NOT raw specs
- Vary structure: questions, comparisons, facts
```

---

## Enforcement

### Pre-Commit Hooks
- Scan for `if component_type ==` in generation/postprocessing/learning modules
- Scan for component-specific method names
- Verify no content instructions in code

### Code Review Requirements
- All new components must follow template-only pattern
- No component-specific code in generation/postprocessing/learning modules
- All content rules in template files

### Documentation
- Update this policy when patterns change
- Document new extraction strategies
- Maintain examples of compliant code

---

## Examples

### ✅ COMPLIANT: Adding "troubleshooter" Component

**Step 1**: Create template with ALL content instructions
```bash
# Prompt catalog entry: prompts/components/troubleshooter.txt
# Troubleshooter Generation Template

## Voice & Tone
- Conversational problem-solving language
- Start with problem impact
- Mix preventive and reactive solutions

## Structure
- Problem identification (what's wrong)
- Root cause explanation (why it happens)
- Solution steps (how to fix)
- Prevention tips (avoid in future)

## Required Format
- 150-200 words
- Use bullet points for steps
- Include diagnostic indicators

## Generation Task
{material_context}
Write troubleshooting guide...
```

**Step 2**: Add config entry
```yaml
# File: generation/config.yaml
component_lengths:
  troubleshooter:
    default: 150
    extraction_strategy: raw
```

**Step 3**: Generate!
```bash
python3 run.py --material "Aluminum" --component troubleshooter
```

**Result**: Works immediately, zero code changes! ✅

---

### ❌ NON-COMPLIANT: Old Pattern

**Problem**: Component-specific code in generator
```python
# ❌ WRONG - Hardcoded component dispatch
def _extract_content(self, text, component_type):
    if component_type == 'micro':
        return self._extract_micro(text)
    elif component_type == 'faq':
        return self._extract_faq(text)
```

**Problem**: Content instructions in code
```python
# ❌ WRONG - Content rules in code
if spec.name == "micro":
    instructions = """
    - Write ONLY technical descriptions
    - NO theatrical language
    """
```

**Problem**: Component-specific prompt methods
```python
# ❌ WRONG - Component-specific method
def _build_micro_prompt(self, ...):
    return f"""Micro-specific prompt..."""
```

---

## Conclusion

**The Template-Only Policy ensures:**
- ✅ `/processing` is **fully reusable** across all domains
- ✅ New components require **ZERO code changes**
- ✅ Content instructions exist **ONLY in templates**
- ✅ Complete separation of concerns
- ✅ Easy maintenance and extension
- ✅ Full policy compliance

**To add a new component**: Create template + config entry = Done! 🎉
