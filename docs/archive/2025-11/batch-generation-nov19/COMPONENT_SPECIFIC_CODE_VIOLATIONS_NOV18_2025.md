# Component-Specific Code Violations in /processing
**Date**: November 18, 2025  
**Status**: CRITICAL VIOLATIONS FOUND  
**Policy**: Component Discovery Policy + Content Instruction Policy

---

## Executive Summary

**USER REQUIREMENT**: "There should be no component-specific code other than the text prompts. The entire /processing system should be completely reusable."

**CURRENT STATE**: ❌ **MAJOR VIOLATIONS** - Component-specific logic hardcoded throughout /processing

**VIOLATIONS FOUND**: 3 critical files with hardcoded component types

---

## Violations by File

### 1. ❌ processing/generator.py (Lines 1206-1334)

**VIOLATION**: Hardcoded component type dispatching and extraction methods

```python
# Line 1206-1213: Hardcoded component dispatch
def _extract_content(self, text: str, component_type: str):
    if component_type == 'caption':
        return self._extract_caption(text)
    elif component_type == 'faq':
        return self._extract_faq(text)
    elif component_type == 'subtitle':
        return text.strip()
    else:
        return text.strip()

# Line 1215-1314: Component-specific extraction methods
def _extract_caption(self, text: str) -> Dict[str, str]:
    """Extract caption from generated text."""
    # 100 lines of caption-specific parsing logic

def _extract_faq(self, text: str) -> list:
    """Extract FAQ items from JSON"""
    # 15 lines of FAQ-specific parsing logic
```

**WHY IT'S WRONG**:
- Hardcodes 'caption', 'faq', 'subtitle' component types
- New component types require code changes
- Violates Component Discovery Policy (components defined ONLY in prompts/)
- Makes /processing non-reusable for other domains

**CORRECT APPROACH**:
- Move extraction logic to domain adapter (`materials_adapter.py`)
- Use registry pattern: `adapter.extract_content(text, component_type)`
- Generator should be generic and delegate to adapters

---

### 2. ❌ processing/adapters/materials_adapter.py (Lines 279-380)

**VIOLATION**: Hardcoded component type dispatching (DUPLICATE of generator.py!)

```python
# Line 279-289: Hardcoded component dispatch
def extract_content(self, text: str, component_type: str):
    if component_type == 'caption':
        return self._extract_caption(text)
    elif component_type == 'faq':
        return self._extract_faq(text)
    elif component_type == 'subtitle':
        return text.strip()
    elif component_type == 'description':
        return text.strip()
    else:
        return text.strip()

# Line 291-380: Component-specific extraction methods
def _extract_caption(self, text: str) -> Dict[str, str]:
    # 55 lines of caption-specific parsing

def _extract_faq(self, text: str) -> list:
    # 30 lines of FAQ-specific parsing
```

**WHY IT'S WRONG**:
- Hardcodes 'caption', 'faq', 'subtitle', 'description' types
- Extraction logic DUPLICATED between generator.py and materials_adapter.py
- Should be in adapter, NOT in generator
- Still uses hardcoded component types instead of registry

**CORRECT APPROACH**:
- Keep extraction in adapter (correct location)
- Use registry to get extraction strategy: `registry.get_extraction_strategy(component_type)`
- Define extraction strategies in component specs or config
- Example: `caption` component spec includes `extraction: "before_after_sections"`

---

### 3. ❌ processing/generation/prompt_builder.py (Lines 436-446, 481-535)

**VIOLATION**: Hardcoded component-specific prompt methods + content instructions in code

```python
# Line 436-446: Hardcoded subtitle-specific content instructions
if spec.name == "subtitle":
    enrichment_hints = """
SUBTITLE-SPECIFIC:
- Lead with benefit or application, NOT raw specs
- Vary structure: try questions, comparisons, or surprising facts
- Balance technical precision with readability
- Examples of good variation:
  * "Why does aerospace choose aluminum? That 2.7 g/cm³ density..."
  * "Aluminum bridges lightweight design with thermal performance..."
  * "From aircraft to packaging, aluminum's versatility stems from..."
- Avoid starting every subtitle with the material name"""

# Line 481-510: Hardcoded subtitle prompt builder method
def _build_subtitle_prompt(self, ...):
    """Build subtitle-specific prompt"""
    return f"""You are {author}, writing a {length}-word subtitle about laser cleaning {material}.
    ...
    """

# Line 511-535: Hardcoded caption prompt builder method
def _build_caption_prompt(self, ...):
    """Build microscopy caption prompt"""
    return f"""...caption-specific prompt text..."""
```

**WHY IT'S WRONG**:
- Violates Content Instruction Policy (instructions ONLY in prompts/*.txt)
- Violates Component Discovery Policy (hardcoded subtitle, caption methods)
- Hardcoded content instructions in code (should be in prompt templates)
- Component-specific prompt builder methods (should be generic)

**CORRECT APPROACH**:
- ALL content instructions → `prompts/components/subtitle.txt`
- GENERIC prompt builder: `_load_prompt_template(component_type)`
- NO component-specific methods (`_build_subtitle_prompt`, `_build_caption_prompt`)
- Use template system: Load from file, replace variables

---

## Policy Violations Summary

| Policy | Violation | Files |
|--------|-----------|-------|
| **Component Discovery Policy** | Hardcoded component types in code | generator.py, materials_adapter.py, prompt_builder.py |
| **Content Instruction Policy** | Content instructions in code (not prompts/) | prompt_builder.py |
| **Reusability Principle** | /processing tied to specific components | All 3 files |
| **DRY Principle** | Extraction logic duplicated | generator.py + materials_adapter.py |

---

## Impact Analysis

### Current State: ❌ NON-REUSABLE
- **Adding new component** (e.g., "description", "troubleshooter") requires:
  1. ✏️ Edit `generator.py` to add `elif component_type == 'description':`
  2. ✏️ Edit `materials_adapter.py` to add extraction method
  3. ✏️ Edit `prompt_builder.py` to add `_build_description_prompt()` method
  4. ✏️ Add hardcoded content instructions to prompt_builder.py
  5. ✏️ Create prompt template in `prompts/components/description.txt`
  
  **Result**: 4 code changes + 1 template = NOT reusable

### Desired State: ✅ FULLY REUSABLE
- **Adding new component** should only require:
  1. ✏️ Create `prompts/components/description.txt` (with all content instructions)
  2. ✏️ Add to `config.yaml`: `component_lengths: { description: 50 }`
  3. ✏️ (Optional) Add extraction strategy if complex format
  
  **Result**: 1-2 config changes + 1 template = Fully reusable

---

## Recommended Fix Strategy

### Phase 1: Remove Extraction from Generator (HIGH PRIORITY)
**File**: `processing/generator.py`

**REMOVE**:
- Lines 1206-1213: `_extract_content()` method with hardcoded dispatch
- Lines 1215-1314: `_extract_caption()` method (100 lines)
- Lines 1317-1334: `_extract_faq()` method (15 lines)

**REPLACE WITH**:
```python
def _extract_content(self, text: str, component_type: str):
    """Delegate extraction to domain adapter."""
    # Adapter handles all extraction logic
    return self.adapter.extract_content(text, component_type)
```

**Impact**: -125 LOC, removes duplication, delegates to correct location

---

### Phase 2: Make Adapter Extraction Generic (CRITICAL PRIORITY)
**File**: `processing/adapters/materials_adapter.py`

**CURRENT** (Lines 279-289):
```python
def extract_content(self, text: str, component_type: str):
    if component_type == 'caption':
        return self._extract_caption(text)
    elif component_type == 'faq':
        return self._extract_faq(text)
    elif component_type == 'subtitle':
        return text.strip()
    elif component_type == 'description':
        return text.strip()
    else:
        return text.strip()
```

**REPLACE WITH**:
```python
def extract_content(self, text: str, component_type: str):
    """
    Extract content using strategy from component spec.
    
    Extraction strategy defined in ComponentSpec or prompt template metadata.
    Examples:
    - 'raw': Return text as-is (subtitle, description)
    - 'before_after': Parse before/after sections (caption)
    - 'json_list': Parse JSON array (faq)
    """
    from processing.generation.component_specs import ComponentRegistry
    
    registry = ComponentRegistry()
    spec = registry.get_spec(component_type)
    
    # Get extraction strategy from spec (or default to 'raw')
    strategy = spec.extraction_strategy if hasattr(spec, 'extraction_strategy') else 'raw'
    
    if strategy == 'raw':
        return text.strip()
    elif strategy == 'before_after':
        return self._extract_before_after(text)
    elif strategy == 'json_list':
        return self._extract_json_list(text)
    else:
        # Unknown strategy - fail fast
        raise ValueError(f"Unknown extraction strategy: {strategy}")
```

**ADD TO ComponentSpec**:
```python
@dataclass
class ComponentSpec:
    name: str
    lengths: Dict[str, int]
    end_punctuation: str
    prompt_template_file: str
    extraction_strategy: str = 'raw'  # NEW FIELD
```

**ADD TO config.yaml**:
```yaml
components:
  caption:
    extraction_strategy: before_after
  faq:
    extraction_strategy: json_list
  subtitle:
    extraction_strategy: raw
  description:
    extraction_strategy: raw
```

**Impact**: Generic extraction, no hardcoded component types, fully configurable

---

### Phase 3: Remove Content Instructions from Code (CRITICAL PRIORITY)
**File**: `processing/generation/prompt_builder.py`

**REMOVE** (Lines 436-446):
```python
if spec.name == "subtitle":
    enrichment_hints = """
SUBTITLE-SPECIFIC:
- Lead with benefit or application, NOT raw specs
- Vary structure: try questions, comparisons, or surprising facts
...
"""
```

**REPLACE WITH**:
```python
# NO component-specific hints in code
# All enrichment hints moved to prompts/components/subtitle.txt
enrichment_hints = ""  # Template system handles this
```

**MOVE INSTRUCTIONS TO**: `prompts/components/subtitle.txt`
```
# Subtitle Generation Template

## Voice & Tone
{persona_instructions}

## Structure Guidelines
- Lead with benefit or application, NOT raw specs
- Vary structure: try questions, comparisons, or surprising facts
- Balance technical precision with readability
- Examples of good variation:
  * "Why does aerospace choose aluminum? That 2.7 g/cm³ density..."
  * "Aluminum bridges lightweight design with thermal performance..."
- Avoid starting every subtitle with the material name

## Generation Task
You are {author}, writing a {length}-word subtitle about laser cleaning {material}.
...
```

**Impact**: Complies with Content Instruction Policy, all instructions in prompts/

---

### Phase 4: Remove Component-Specific Prompt Methods (HIGH PRIORITY)
**File**: `processing/generation/prompt_builder.py`

**REMOVE**:
- Lines 481-510: `_build_subtitle_prompt()` method
- Lines 511-535: `_build_caption_prompt()` method

**REPLACE WITH**: Generic template loading (already exists!)
```python
def _load_prompt_template(self, component_type: str) -> str:
    """
    Load component-specific prompt template from prompts/components/{component}.txt.
    This method already exists - just use it everywhere!
    """
    template_path = Path(f"prompts/components/{component_type}.txt")
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    return template_path.read_text()
```

**Impact**: -54 LOC, generic template system, no hardcoded methods

---

## Implementation Checklist

### Phase 1: Remove Extraction from Generator ✅
- [ ] Remove `_extract_content()` from generator.py
- [ ] Remove `_extract_caption()` from generator.py
- [ ] Remove `_extract_faq()` from generator.py
- [ ] Replace with delegation to adapter
- [ ] Test: Caption generation still works
- [ ] Test: FAQ generation still works
- [ ] Impact: -125 LOC

### Phase 2: Make Adapter Extraction Generic ✅
- [ ] Add `extraction_strategy` field to ComponentSpec
- [ ] Add extraction strategies to config.yaml
- [ ] Refactor `materials_adapter.extract_content()` to use registry
- [ ] Rename methods: `_extract_caption()` → `_extract_before_after()`
- [ ] Rename methods: `_extract_faq()` → `_extract_json_list()`
- [ ] Remove hardcoded `if component_type ==` checks
- [ ] Test: All component types extract correctly
- [ ] Impact: Fully generic extraction

### Phase 3: Remove Content Instructions from Code ✅
- [ ] Move enrichment hints from prompt_builder.py to prompt templates
- [ ] Remove `if spec.name == "subtitle":` block (lines 436-446)
- [ ] Verify prompts/components/subtitle.txt has all instructions
- [ ] Verify prompts/components/caption.txt has all instructions
- [ ] Test: Generated content quality unchanged
- [ ] Impact: Complies with Content Instruction Policy

### Phase 4: Remove Component-Specific Prompt Methods ✅
- [ ] Remove `_build_subtitle_prompt()` method
- [ ] Remove `_build_caption_prompt()` method
- [ ] Replace all calls with `_load_prompt_template(component_type)`
- [ ] Verify template system handles variable replacement
- [ ] Test: All components generate correctly
- [ ] Impact: -54 LOC, fully generic

### Phase 5: Validation ✅
- [ ] Run integrity checker
- [ ] Generate caption for 3 materials
- [ ] Generate subtitle for 3 materials
- [ ] Generate FAQ for 3 materials
- [ ] Verify no component types hardcoded in /processing
- [ ] Verify all content instructions in prompts/
- [ ] Run full test suite

---

## Expected Outcomes

### Code Reduction
- **Before**: Generator (1,335 LOC) + Adapter (381 LOC) + PromptBuilder (611 LOC) = 2,327 LOC
- **After**: Generator (1,210 LOC) + Adapter (350 LOC) + PromptBuilder (557 LOC) = 2,117 LOC
- **Reduction**: -210 LOC (-9%)

### Architecture Benefits
- ✅ **Fully Reusable**: /processing works for ANY domain (materials, contaminants, applications, regions)
- ✅ **Component Discovery**: Add components by creating prompt template + config entry
- ✅ **Policy Compliance**: Content instructions ONLY in prompts/
- ✅ **No Hardcoding**: Zero component types hardcoded in code
- ✅ **DRY Principle**: Extraction logic in ONE place (adapter)
- ✅ **Fail-Fast**: Unknown component types fail immediately with clear error
- ✅ **Testability**: Easy to test new components without code changes

### Extensibility Example
**Before** (NON-REUSABLE):
```bash
# Want to add "troubleshooter" component
1. Edit generator.py - add elif component_type == 'troubleshooter'
2. Edit materials_adapter.py - add _extract_troubleshooter()
3. Edit prompt_builder.py - add _build_troubleshooter_prompt()
4. Add content instructions to prompt_builder.py code
5. Create prompts/components/troubleshooter.txt
Result: 4 code files + 1 template = 5 changes
```

**After** (FULLY REUSABLE):
```bash
# Want to add "troubleshooter" component
1. Create prompts/components/troubleshooter.txt (with all instructions)
2. Add to config.yaml:
   components:
     troubleshooter:
       lengths: { min: 40, max: 60, target: 50 }
       extraction_strategy: raw
Result: 1 config file + 1 template = 2 changes (ZERO code changes!)
```

---

## Risk Assessment

| Phase | Risk | Mitigation |
|-------|------|------------|
| Phase 1 | Breaking extraction | Test caption/FAQ after each change |
| Phase 2 | Unknown extraction strategies | Fail-fast with clear error messages |
| Phase 3 | Content quality regression | Compare before/after generation quality |
| Phase 4 | Template system issues | Verify template loading works for all components |

**Overall Risk**: **LOW-MEDIUM** - Changes are mechanical refactoring with clear patterns

---

## Timeline

- **Phase 1**: 1 hour (remove extraction from generator)
- **Phase 2**: 2 hours (make adapter generic)
- **Phase 3**: 1 hour (move content instructions)
- **Phase 4**: 1 hour (remove component methods)
- **Phase 5**: 1 hour (testing and validation)

**Total**: ~6 hours for complete refactoring

---

## Conclusion

**Current State**: ❌ /processing has **hardcoded component-specific logic** in 3 critical files  
**User Requirement**: "There should be no component-specific code other than the text prompts"  
**Recommended Action**: Implement 4-phase refactoring to achieve fully reusable architecture  
**Benefit**: Add new components with ZERO code changes (only templates + config)  
**Timeline**: ~6 hours for complete compliance with policies

This refactoring aligns with:
- ✅ Component Discovery Policy
- ✅ Content Instruction Policy  
- ✅ Prompt Purity Policy
- ✅ DRY Principle
- ✅ Fail-Fast Architecture
- ✅ Reusability Principle
