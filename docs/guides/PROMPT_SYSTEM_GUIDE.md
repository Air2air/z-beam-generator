# Prompt System Comprehensive Guide

**Last Updated**: December 20, 2025  
**Consolidates**: 6 prompt-related policy documents  
**Status**: ✅ ACTIVE - Single Source of Truth

---

## Overview

This guide consolidates all prompt system architecture, policies, and best practices into a single comprehensive reference. It covers prompt purity (zero hardcoded prompts), chaining/orchestration patterns, validation requirements, and size-aware compression strategies.

**Consolidated Sources**:
- `PROMPT_PURITY_POLICY.md` (497 lines) - Zero hardcoded prompts
- `PROMPT_CHAINING_POLICY.md` (545 lines) - Multi-stage orchestration
- `PROMPT_VALIDATION_POLICY.md` (320 lines) - Auto-fix validation
- `PROMPT_CHAIN_SEPARATION_POLICY.md` (236 lines) - Duplicate coverage
- `PROMPT_SEPARATION_OF_CONCERNS.md` (153 lines) - Duplicate coverage
- `COMPONENT_SUMMARY_GENERATION_PROMPT.md` - Summary generation

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Prompt Purity Policy](#prompt-purity-policy)
3. [Prompt Chaining & Orchestration](#prompt-chaining--orchestration)
4. [Validation & Auto-Fix](#validation--auto-fix)
5. [Size-Aware Compression](#size-aware-compression)
6. [Implementation Examples](#implementation-examples)
7. [Testing & Enforcement](#testing--enforcement)

---

## Core Principles

### 1. Single Source of Truth

**ALL content generation instructions MUST exist ONLY in prompt template files.**

**Prompt Templates** (authoritative sources):
- `prompts/{domain}/*.txt` - Component-specific content requirements
- `shared/voice/profiles/*.yaml` - Author personas and voice instructions
- `prompts/core/humanness_layer*.txt` - Structural variation

**Generator Code** (technical mechanisms only):
- `generation/core/generator.py` - Orchestration and API calls
- `generation/core/evaluated_generator.py` - Quality evaluation
- `shared/text/utils/prompt_builder.py` - Template assembly

### 2. Zero Prompt Overrides

**FORBIDDEN in generator code**:
```python
# ❌ VIOLATION: Hardcoded prompt text
system_prompt = "You are a professional technical writer..."

# ❌ VIOLATION: Inline content instructions
prompt += "\nCRITICAL RULE: Write ONLY in qualitative terms..."

# ❌ VIOLATION: Dynamic prompt injection
prompt = prompt.replace("text", "YOU MUST NOT INCLUDE...")
```

**CORRECT approach**:
```python
# ✅ Load prompt from template file
prompt_template = self._load_prompt_template('micro.txt')

# ✅ Apply parameters to template
prompt = self._apply_parameters(prompt_template, parameters)

# ✅ Pass prompt as-is to API
response = api_client.generate(prompt=prompt, temperature=temp)
```

### 3. Separation of Concerns

Each layer has ONE responsibility:

| Layer | Purpose | Location | Contains |
|-------|---------|----------|----------|
| **Voice** | Author characteristics | `shared/voice/profiles/*.yaml` | Voice instruction, tone, forbidden phrases |
| **Humanness** | Structural variation | `learning/humanness_optimizer.py` | Opening patterns, rhythm, property strategies |
| **Domain** | Content requirements | `prompts/{domain}/*.txt` | Task, word count, `{voice_instruction}` placeholder |

**NO overlap, NO duplication, NO confusion.**

---

## Prompt Purity Policy

### Policy Statement

**ZERO prompt text, content rules, or generation instructions are permitted in generator code.**

### Template Parameterization

**✅ ALLOWED placeholders**:
```
{material_name}
{property_values}
{component_type}
{word_count}
{context_data}
{voice_instruction}  ← Filled from persona files
```

**❌ FORBIDDEN inline instructions**:
```python
# Don't do this:
prompt = template.format(
    material=material,
    extra_rules="Never use numbers"  # ❌ Content instruction in code
)
```

**✅ CORRECT - Put instruction IN TEMPLATE**:
```
# In prompts/materials/micro.txt:
Write about {material_name} properties.

CRITICAL: Never use numbers, measurements, or units.
Focus on qualitative descriptions only.
```

### What Belongs Where

**In Prompt Templates** (`prompts/{domain}/*.txt`):
- ✅ Content instructions ("Write about X")
- ✅ Style requirements ("Use qualitative terms")
- ✅ Format rules ("Single paragraph, 50 words")
- ✅ Focus areas ("Emphasize practical applications")
- ✅ Forbidden phrases ("Never use: challenge, pitfall")
- ✅ Required elements ("Must mention: category, properties")

**In Generator Code** (`generation/core/`):
- ✅ API calls (`api_client.generate()`)
- ✅ Parameter application (`temperature=0.7`)
- ✅ Quality validation (Winston, realism gates)
- ✅ Retry logic (adaptive thresholds)
- ✅ Template loading (`_load_prompt_template()`)
- ✅ Data flow (reading config, writing results)
- ❌ NO content instructions of any kind

### Enforcement

**Automated Tests**: `tests/test_prompt_purity_policy.py`

**Checks**:
1. Zero hardcoded prompts in generator code
2. All prompts loaded from template files
3. No dynamic prompt injection in code
4. No content rules in Python files

**Grade**: F violation for ANY hardcoded prompt text

---

## Prompt Chaining & Orchestration

### Core Principle

**Break generation into specialized prompts instead of one monolithic prompt.**

### Anti-Pattern: Monolithic Prompt

❌ **WRONG**: Single massive prompt trying to do everything

```
Single prompt that attempts:
- Research material properties
- Generate visual descriptions
- Apply style guidelines
- Ensure technical accuracy
- Format output
- All at once with conflicting instructions
```

**Problems**:
- Conflicting instructions confuse model
- Hard to debug which part failed
- Can't reuse components
- Loses specificity as prompt grows
- Quality degrades with complexity

### Correct Pattern: Chained Prompts

✅ **RIGHT**: Multi-stage orchestrated prompts

```
Stage 1 (Research): Extract material properties
   ↓ (properties data)
Stage 2 (Visual): Generate appearance description
   ↓ (visual details)
Stage 3 (Style): Apply domain-specific style
   ↓ (styled content)
Stage 4 (Format): Structure and polish
   ↓ (final output)
```

**Benefits**:
- Each prompt focused on ONE task
- Clear data flow between stages
- Easy to debug specific stage
- Reusable components across domains
- Maintains specificity and quality

### Implementation: Orchestration Layer

**Pattern**: Create orchestrator classes that chain specialized prompts

**Example**: Image Generation Orchestrator

```python
class ImagePromptOrchestrator:
    """Chains specialized prompts for image generation"""
    
    def generate_hero_image_prompt(self, material: str) -> str:
        # Stage 1: Research material properties
        properties = self._research_properties(material)
        
        # Stage 2: Generate visual appearance
        visual = self._generate_visual_description(material, properties)
        
        # Stage 3: Compose hero layout
        composition = self._compose_hero_layout(material, visual)
        
        # Stage 4: Technical refinement
        refined = self._refine_technical_accuracy(composition, properties)
        
        # Stage 5: Final assembly
        final_prompt = self._assemble_final_prompt(refined)
        
        return final_prompt
    
    def _research_properties(self, material: str) -> dict:
        """Stage 1: Property extraction (low temp 0.3)"""
        template = self._load_template('research/material_properties.txt')
        prompt = template.format(material=material)
        return self.api_client.generate(prompt, temperature=0.3)
    
    def _generate_visual_description(self, material: str, properties: dict) -> str:
        """Stage 2: Visual description (high temp 0.7)"""
        template = self._load_template('generation/visual_appearance.txt')
        prompt = template.format(material=material, properties=properties)
        return self.api_client.generate(prompt, temperature=0.7)
```

### Context Passing

**Each stage receives previous output as input:**

```python
# Stage 1 output becomes Stage 2 input
properties = stage1_research(material)

# Stage 2 output becomes Stage 3 input
visual = stage2_visual_description(material, properties)

# Stage 3 output becomes Stage 4 input
composition = stage3_hero_layout(material, visual)
```

### Prompt File Organization

**Organize by stage/function**:

```
shared/image/templates/
├── research/
│   ├── material_properties.txt      # Stage 1: Research
│   └── contamination_patterns.txt   # Stage 1: Research
├── generation/
│   ├── hero_composition.txt         # Stage 2: Generate layout
│   ├── contamination_details.txt    # Stage 2: Generate details
│   └── lighting_setup.txt           # Stage 2: Generate atmosphere
└── refinement/
    ├── technical_accuracy.txt       # Stage 3: Refine
    └── image_polish.txt             # Stage 3: Polish
```

### Temperature Strategy

**Different temperatures for different stages**:

| Stage | Temperature | Rationale |
|-------|-------------|-----------|
| Research | 0.3 | Precise, factual extraction |
| Creative | 0.7-0.9 | Varied, creative descriptions |
| Refinement | 0.4-0.5 | Balanced accuracy + polish |

### Benefits of Chaining

1. **Separation of concerns** - Research vs creativity vs accuracy
2. **Optimal parameters** - Different temps for different tasks
3. **Reusable components** - Same research for multiple outputs
4. **Easy debugging** - Test each stage independently
5. **Better quality** - Focused prompts produce better results

---

## Validation & Auto-Fix

### Severity Levels

#### 🔴 CRITICAL - AUTO-FIX (Automatic Optimization)

**Definition**: Issues that will cause API failure or unusable output

**Examples**:
- Prompt exceeds API hard limit (8000 chars text, 4096 chars image)
- Excessive whitespace and redundancy
- Overly verbose instructions

**Action**: **AUTO-OPTIMIZE** - Prompt automatically rewritten

**Optimization Strategies**:
1. Remove excessive blank lines (triple newlines → double)
2. Deduplicate emphasis markers (CRITICAL, IMPORTANT)
3. Condense verbose phrases ("You must ensure that you" → "Ensure")
4. Remove redundant intensifiers ("very", "really", "extremely")
5. Break long lines at sentence boundaries

#### 🟠 ERROR - WARNING (Logged, Not Blocking)

**Definition**: Issues likely to cause quality problems but won't break API

**Examples**:
- Contradictory instructions (formal vs casual tone)
- Multiple conflicting length targets
- Style contradictions (technical vs simple)

**Action**: **LOG WARNING** - Proceed but log to learning database

#### 🟡 WARNING - INFO (Logged, Not Blocking)

**Definition**: Issues that may reduce quality but are minor

**Examples**:
- Prompt approaching warning threshold (6000/8000 chars)
- Excessive emphasis markers
- Redundant intensifiers

**Action**: **LOG INFO** - Proceed, log for optimization

#### 🔵 INFO - SUGGESTION (Logged, Not Blocking)

**Definition**: Optional improvements for quality

**Examples**:
- Line length optimization
- Whitespace condensation
- Minor formatting suggestions

**Action**: **LOG DEBUG** - Proceed silently

### Enforcement in Pipeline

**File**: `generation/core/generator.py`  
**Method**: `generate_without_save()` (lines 260-410)

```python
# Stage 1: Standard validation
validation_result = validate_text_prompt(prompt)

# Stage 2: Coherence validation
coherence_issues = check_prompt_coherence(prompt)

# Stage 3: Auto-fix if CRITICAL
if validation_result.severity == 'CRITICAL':
    prompt = auto_optimize_prompt(prompt, validation_result.issues)
    self.logger.info(f"✅ Auto-optimized prompt: {len(prompt)} chars")

# Stage 4: Log warnings/errors
for issue in validation_result.issues:
    if issue.severity in ['ERROR', 'WARNING']:
        self.logger.warning(f"⚠️ Prompt issue: {issue.message}")
```

### Validation Rules

**Hard Limits** (AUTO-FIX):
- Text prompts: 8000 chars max
- Image prompts: 4096 chars max
- Single line: 200 chars max (readability)

**Soft Limits** (WARNING):
- Text prompts: 6000 chars (warning threshold)
- Image prompts: 3000 chars (warning threshold)

**Coherence Checks** (ERROR):
- Conflicting tone instructions
- Multiple contradictory length targets
- Style conflicts

---

## Size-Aware Compression

### Problem

**Full humanness layer (~9,000 chars) causes prompts to exceed 8,000 char API limit**

### Solution

**Automatically compress humanness layer based on base prompt size**

### Threshold

```python
SIZE_THRESHOLD = 2000  # chars
```

### Behavior

```python
if base_prompt_size > 2000:
    # Use COMPRESSED humanness (~800 chars, 9% of full)
    humanness = optimizer.generate_compressed_humanness(component_type, strictness_level=1)
else:
    # Use FULL humanness (~9,000 chars)
    humanness = optimizer.generate_humanness_instructions(component_type, strictness_level=2)
```

### Results

**Before compression**:
- Prompt size: 12,057 chars (51% over limit) ❌
- API rejection: "Prompt exceeds maximum length"

**After compression**:
- Prompt size: 3,797 chars (52% below limit) ✅
- Compression: 68% size reduction
- Quality maintained: 85/100 voice authenticity

### Implementation

**File**: `generation/core/evaluated_generator.py`

```python
def _build_prompt_with_compression(self, component_type: str, base_prompt: str) -> str:
    """Build prompt with size-aware humanness compression"""
    
    base_size = len(base_prompt)
    
    if base_size > SIZE_THRESHOLD:
        # Use compressed humanness
        humanness = self.humanness_optimizer.generate_compressed_humanness(
            component_type, 
            strictness_level=1
        )
        self.logger.info(f"📦 Using compressed humanness ({len(humanness)} chars)")
    else:
        # Use full humanness
        humanness = self.humanness_optimizer.generate_humanness_instructions(
            component_type,
            strictness_level=2
        )
        self.logger.info(f"📋 Using full humanness ({len(humanness)} chars)")
    
    final_prompt = f"{base_prompt}\n\n{humanness}"
    
    # Validate total size
    if len(final_prompt) > 8000:
        raise ValueError(f"Prompt exceeds limit even with compression: {len(final_prompt)} chars")
    
    return final_prompt
```

### Compression Strategies

**Full Humanness** (~9,000 chars):
- Complete opening pattern library (15+ patterns)
- Detailed rhythm variations
- Comprehensive property integration strategies
- Full anti-AI pattern breaking instructions

**Compressed Humanness** (~800 chars):
- 3 opening patterns (most effective)
- 2 rhythm variations (short/long)
- 1 property strategy (problem-solution)
- Essential anti-AI patterns only

**Quality Impact**: Minimal (voice comes from persona, not humanness)

---

## Implementation Examples

### Example 1: Text Generation (Current System)

**Single-Pass with Quality Evaluation**:

```python
class QualityEvaluatedGenerator:
    """Text generation with quality learning"""
    
    def generate(self, material_name: str, component_type: str) -> dict:
        # Stage 1: Build base prompt from template
        base_prompt = self._load_domain_template(component_type)
        
        # Stage 2: Add humanness layer (size-aware)
        prompt = self._build_prompt_with_compression(component_type, base_prompt)
        
        # Stage 3: Generate content (single API call)
        content = self.api_client.generate(prompt, temperature=temp)
        
        # Stage 4: Save immediately to Materials.yaml
        self.data_manager.save_content(material_name, component_type, content)
        
        # Stage 5: Evaluate quality for learning
        quality = self._evaluate_quality(content)  # Winston, Realism, Structural
        
        # Stage 6: Log to learning database
        self._log_to_learning_db(material_name, component_type, content, quality)
        
        return {'content': content, 'quality': quality}
```

### Example 2: Image Generation (Multi-Stage)

**Orchestrated with Context Passing**:

```python
class ImagePromptOrchestrator:
    """Multi-stage image prompt generation"""
    
    def generate_hero_image_prompt(self, material: str) -> str:
        # Stage 1: Research properties (temp 0.3)
        properties = self._research_properties(material)
        
        # Stage 2: Generate visual (temp 0.7)
        visual = self._generate_visual_description(material, properties)
        
        # Stage 3: Compose layout (temp 0.5)
        composition = self._compose_hero_layout(material, visual)
        
        # Stage 4: Refine accuracy (temp 0.4)
        refined = self._refine_technical(composition, properties)
        
        # Stage 5: Final assembly (temp 0.5)
        final = self._assemble_final_prompt(refined)
        
        return final
```

### Example 3: Voice + Humanness + Domain Prompts

**Three-Layer Integration**:

```python
# Layer 1: Load author persona (voice)
persona = self._load_persona(author_id)  # From shared/voice/profiles/
voice_instruction = persona['core_voice_instruction']

# Layer 2: Generate humanness layer (structure)
humanness = self.humanness_optimizer.generate_humanness_instructions(component_type)

# Layer 3: Load domain prompt template
domain_template = self._load_domain_template(component_type)

# Assemble: Domain prompt + Voice + Humanness
final_prompt = domain_template.format(
    material_name=material,
    voice_instruction=voice_instruction  # ← Filled from Layer 1
)
final_prompt += f"\n\n{humanness}"  # ← Append Layer 2

# Generate
content = self.api_client.generate(final_prompt, temperature=temp)
```

---

## Testing & Enforcement

### Automated Tests

**File**: `tests/test_prompt_system_policies.py`

**Test Coverage**:
1. **Prompt Purity**:
   - `test_no_hardcoded_prompts_in_generators()` - Zero prompt text in code
   - `test_all_prompts_loaded_from_templates()` - All prompts from files
   - `test_no_dynamic_prompt_injection()` - No runtime prompt modification

2. **Validation**:
   - `test_prompt_validation_enforced()` - Validation runs before API
   - `test_critical_issues_auto_fixed()` - Auto-optimization for oversized
   - `test_warnings_logged_not_blocking()` - Warnings logged but proceed

3. **Size-Aware Compression**:
   - `test_compressed_humanness_used_for_large_prompts()` - Compression triggers
   - `test_full_humanness_used_for_small_prompts()` - Full layer when space available
   - `test_final_prompt_never_exceeds_limit()` - Always under 8000 chars

4. **Chaining**:
   - `test_orchestrator_chains_prompts()` - Multi-stage execution
   - `test_context_passed_between_stages()` - Data flow between stages
   - `test_different_temps_per_stage()` - Temperature strategy applied

### Manual Code Review

**Checklist for Code Review**:
- [ ] Zero prompt text in generator code
- [ ] All prompts loaded from template files
- [ ] No dynamic prompt injection
- [ ] Validation runs before API submission
- [ ] Size-aware compression implemented
- [ ] Chaining uses specialized prompts
- [ ] Context passed between stages
- [ ] Different temperatures per stage
- [ ] Clear separation: voice vs humanness vs domain

### Enforcement

**Grade**: F violation for:
- Hardcoded prompts in generator code
- Bypassing validation before API submission
- Single monolithic prompt (no chaining)
- Prompt text in code comments

---

## Quick Reference

### Do's and Don'ts

| ✅ DO | ❌ DON'T |
|-------|----------|
| Load prompts from template files | Hardcode prompt text in code |
| Use `{voice_instruction}` placeholder | Write voice instructions in domain prompts |
| Chain specialized prompts | Create monolithic prompts |
| Auto-fix CRITICAL validation issues | Skip validation |
| Compress humanness for large prompts | Let prompts exceed 8000 chars |
| Pass context between stages | Duplicate research in each stage |
| Use different temps per stage | Use same temp for all tasks |
| Test each stage independently | Test only final output |

### File Locations

| What | Where |
|------|-------|
| **Prompt Templates** | `prompts/{domain}/*.txt` |
| **Voice Profiles** | `shared/voice/profiles/*.yaml` |
| **Humanness Templates** | `prompts/core/humanness_layer*.txt` |
| **Generator** | `generation/core/generator.py` |
| **Evaluated Generator** | `generation/core/evaluated_generator.py` |
| **Prompt Builder** | `shared/text/utils/prompt_builder.py` |
| **Validation** | `shared/text/validation/prompt_validator.py` |

### Command Examples

```bash
# Generate with full pipeline
python3 run.py --domain materials --item aluminum --component description

# Test prompt validation
pytest tests/test_prompt_validation.py -v

# Test prompt purity policy
pytest tests/test_prompt_purity_policy.py -v

# Check prompt file sizes
find prompts/* -name "*.txt" -exec wc -c {} \;
```

---

## Summary

**Single Source of Truth**: This guide consolidates 6 prompt-related policy documents into one comprehensive reference.

**Core Principles**:
1. **Prompt Purity**: Zero hardcoded prompts in code
2. **Chaining**: Multi-stage specialized prompts
3. **Validation**: Auto-fix critical issues
4. **Compression**: Size-aware humanness layer
5. **Separation**: Voice vs Humanness vs Domain prompts

**Enforcement**: Automated tests + manual code review  
**Grade**: F violation for any hardcoded prompts or bypassing validation

**Status**: ✅ ACTIVE - All policies operational and enforced

---

**See Also**:
- `ARCHITECTURE_PRINCIPLES.md` - System architecture patterns
- `VOICE_SYSTEM_GUIDE.md` - Author voice architecture
- `docs/02-architecture/processing-pipeline.md` - Full generation pipeline

**Archived Sources** (2025-12-20):
- `docs/archive/2025-12/policies/PROMPT_PURITY_POLICY.md`
- `docs/archive/2025-12/policies/PROMPT_CHAINING_POLICY.md`
- `docs/archive/2025-12/policies/PROMPT_VALIDATION_POLICY.md`
- `docs/archive/2025-12/policies/PROMPT_CHAIN_SEPARATION_POLICY.md`
- `docs/archive/2025-12/policies/PROMPT_SEPARATION_OF_CONCERNS.md`
- `docs/archive/2025-12/policies/COMPONENT_SUMMARY_GENERATION_PROMPT.md`
