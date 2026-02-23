# Architecture Principles Comprehensive Guide

**Last Updated**: December 20, 2025  
**Consolidates**: 4 architecture policy documents  
**Status**: ✅ ACTIVE - Single Source of Truth

---

## Overview

This guide consolidates all system architecture principles, patterns, and best practices into a single comprehensive reference. It covers separation of concerns, reusable system design, example-free architecture, and shared component patterns.

**Consolidated Sources**:
- `CLEAN_SEPARATION_OF_CONCERNS_DEC12_2025.md` (211 lines) - Three-layer architecture
- `FULLY_REUSABLE_SYSTEM_GUIDE.md` (376 lines) - Domain-agnostic design
- `EXAMPLE_FREE_ARCHITECTURE.md` (281 lines) - Voice-driven generation
- `SHARED_ARCHITECTURE_PROPOSAL.md` (396 lines) - Shared component patterns

**NOT Consolidated** (domain-specific, kept separate):
- `IMAGE_ARCHITECTURE.md` - Image generation system architecture

---

## Table of Contents

1. [Core Architecture Principles](#core-architecture-principles)
2. [Three-Layer Architecture](#three-layer-architecture)
3. [Domain-Agnostic Design](#domain-agnostic-design)
4. [Example-Free Architecture](#example-free-architecture)
5. [Shared Component Patterns](#shared-component-patterns)
6. [Adding New Domains](#adding-new-domains)
7. [Quality Standards](#quality-standards)

---

## Core Architecture Principles

### 1. Separation of Concerns

**Each layer has ONE responsibility. No overlap, no duplication, no confusion.**

| Layer | Responsibility | Location |
|-------|---------------|----------|
| **Voice** | Author characteristics | `shared/voice/profiles/*.yaml` |
| **Humanness** | Structural variation | `learning/humanness_optimizer.py` |
| **Domain** | Content requirements | `prompts/registry/prompt_catalog.yaml` (`catalog.byPath` entries like `prompts/{domain}/*.txt`) |
| **Generation** | API orchestration | `generation/core/` |
| **Quality** | Evaluation and learning | `learning/` + `shared/text/quality/` |

**NO overlap, NO duplication, NO confusion.**

### 2. Single Source of Truth

Each piece of information exists in EXACTLY ONE authoritative location:

- **Author voice** → `shared/voice/profiles/*.yaml` ONLY
- **Component specs** → prompt catalog `catalog.byPath` entries + `domains/*/config.yaml`
- **Data** → `data/{domain}/Data.yaml` (Materials, Contaminants, Settings, etc.)
- **Configuration** → `generation/config.yaml` + `domains/*/config.yaml`

**NO duplication, NO drift, NO conflicts.**

### 3. Configuration Over Code

**Add new domains/components by creating config files, NOT by modifying code.**

**Example**: Adding new domain requires:
- ✅ Create `domains/new_domain/config.yaml` (data paths, context keys)
- ✅ Add prompt catalog entries (catalog.byPath: `prompts/new_domain/*.txt`) in `prompts/registry/prompt_catalog.yaml`
- ❌ NO code changes in `generation/core/`
- ❌ NO modifications to generator classes

### 4. Template-Driven Generation

**ALL content instructions in templates, ZERO hardcoded prompts in code.**

- **Templates define**: Content structure, style requirements, focus areas
- **Code handles**: Loading templates, API calls, quality validation, data flow

### 5. Fail-Fast Architecture

**Validate immediately, fail explicitly, NO silent degradation.**

```python
# ✅ CORRECT: Fail fast on missing config
if 'data_path' not in config:
    raise ConfigurationError("data_path missing from config")

# ❌ WRONG: Silent fallback
data_path = config.get('data_path', 'data/materials/Materials.yaml')
```

---

## Three-Layer Architecture

### Layer 1: Author Personas (Voice Definition)

**Location**: `shared/voice/profiles/*.yaml`

**Purpose**: Define voice characteristics ONLY

**Contains**:
- Core voice instruction (writing style, linguistic patterns)
- Tonal restraint (what to avoid)
- Forbidden phrases (AI-like language to reject)
- Linguistic patterns (nationality-specific traits)

**Does NOT contain**:
- Structural guidance (opening patterns)
- Length targets (word counts)
- Rhythm instructions (sentence variation)
- Property integration strategies

**Injected by**: `prompt_builder.py` → `_build_voice_instruction()` → `{voice_instruction}` placeholder in domain prompts

**Example Structure**:
```yaml
# shared/voice/profiles/todd_dunning.yaml
nationality: United States
core_voice_instruction: |
  Write with paratactic chains, causal links...
  Use phrasal verbs ("line up", "dial in", "ramp up")...
tonal_restraint: |
  Avoid theatrical language, excessive hedging...
forbidden_phrases:
  - "presents a challenge"
  - "critical pitfall"
  - "unique opportunity"
linguistic_patterns:
  phrasal_verbs: ["line up", "dial in", "ramp up"]
  quantified_outcomes: true
  practical_transitions: true
```

**Key Principle**: Voice is IMMUTABLE per author. Once assigned, never changes.

---

### Layer 2: Humanness Optimizer (Structural Variation)

**Location**: `learning/humanness_optimizer.py` + `prompts/core/humanness_layer*.txt`

**Purpose**: Structural diversity ONLY (NOT voice)

**Contains**:
- Opening pattern randomization (15+ patterns)
- Sentence rhythm variation (short/long, balanced)
- Property integration strategies (problem-solution, comparison, context)
- Warning placement (beginning/end)
- Anti-AI pattern breaking (avoid robotic structures)

**Does NOT contain**:
- Voice instructions (comes from Layer 1)
- Tone guidance (comes from Layer 1)
- Forbidden phrases (comes from Layer 1)
- Author-specific patterns (comes from Layer 1)

**Called by**: `generator.py` and `evaluated_generator.py` → `generate_humanness_instructions(component_type)`

**NO voice parameter** - voice comes from persona, not humanness

**Example Output**:
```
🎲 RANDOMIZATION APPLIED:
   • Structure: Experience-Based (20% chance)
   • Sentence Rhythm: SHORT & PUNCHY
   • Property Strategy: PROBLEM-SOLUTION
   
NOTE: Voice style comes from assigned author persona (specified above).
```

**Key Principle**: Humanness provides STRUCTURE, not VOICE. Same author gets different structures on each generation.

---

### Layer 3: Domain Prompts (Content Requirements)

**Location**: prompt catalog `catalog.byPath` entries like `prompts/{domain}/*.txt`

**Purpose**: Component-specific content requirements

**Contains**:
- Task description ("Write a focused description of X")
- Word count targets ("50-150 words")
- Content requirements (what to include/exclude)
- Domain-specific context (material properties, contamination patterns)
- **`{voice_instruction}` placeholder** → filled by Layer 1
- Format rules (paragraph structure)

**Does NOT contain**:
- Hardcoded voice instructions (use placeholder)
- Structural randomization (comes from Layer 2)
- Author-specific patterns (comes from Layer 1)

**Example Template**:
```
# prompt catalog entry: prompts/materials/description.txt

TASK: Write a focused technical description of {material_name}.

CONTEXT:
Category: {category}
Properties: {properties}

CONTENT REQUIREMENTS:
- 1-2 sentences maximum
- Focus on practical applications
- Qualitative terms only (no numbers)

{voice_instruction}

WORD COUNT: 50-150 words
```

**Key Principle**: Domain prompts define WHAT to write, not HOW to write it (voice).

---

### Layer Integration

**How layers combine during generation**:

```python
# 1. Load author persona (Layer 1)
author_id = data.get('author', {}).get('id')
persona = self._load_persona(author_id)
voice_instruction = persona['core_voice_instruction']

# 2. Generate humanness layer (Layer 2)
humanness = self.humanness_optimizer.generate_humanness_instructions(component_type)

# 3. Load domain prompt (Layer 3)
domain_template = self._load_domain_template(component_type)

# 4. Assemble final prompt
base_prompt = domain_template.format(
    material_name=material,
    properties=properties,
    voice_instruction=voice_instruction  # ← Layer 1 fills Layer 3 placeholder
)

# 5. Add humanness layer
final_prompt = f"{base_prompt}\n\n{humanness}"  # ← Layer 2 appended

# 6. Generate
content = self.api_client.generate(final_prompt, temperature=temp)
```

**Result**: Voice (Layer 1) + Structure (Layer 2) + Requirements (Layer 3) = Final prompt

---

## Domain-Agnostic Design

### Core Principle

**Processing code works for ANY domain without modification.**

### Architecture Pattern

```
User Request
    ↓
Generator (domain-agnostic)
    ↓
DomainAdapter (config-driven)
    ↓
PromptBuilder (template-based)
    ↓
VoiceSystem (persona-based)
    ↓
LLM API
    ↓
QualityEvaluator
    ↓
Output
```

### Key Components

| Component | Location | Purpose | Domain-Specific? |
|-----------|----------|---------|------------------|
| **Generator** | `generation/core/generator.py` | Orchestrates generation | ❌ NO |
| **Domain Adapter** | `generation/core/adapters/domain_adapter.py` | Loads domain config | ❌ NO (config-driven) |
| **Prompt Builder** | `shared/text/utils/prompt_builder.py` | Assembles prompts | ❌ NO (template-driven) |
| **Voice Profiles** | `shared/voice/profiles/*.yaml` | Author personas | ❌ NO (shared) |
| **Domain Config** | `domains/{domain}/config.yaml` | Data paths, context keys | ✅ YES |
| **Prompt Templates** | Prompt catalog `catalog.byPath` entries like `prompts/{domain}/*.txt` | Content structure | ✅ YES |

**2 domain-specific files, 4 shared components. All processing code reusable.**

### Domain Configuration

**File**: `domains/{domain}/config.yaml`

**Required Fields**:
```yaml
# Data configuration
data_path: "data/{domain}/Data.yaml"  # Where to find data
data_root_key: "items"                # Root key in YAML (materials, contaminants, settings)
author_key: "author.id"               # Path to author ID field

# Context keys (classification + raw data ONLY)
context_keys:
  - category          # Classification
  - properties.key1   # Raw numerical data
  # NO description, context_notes, or other text fields

# Frontmatter configuration
frontmatter_directory: "frontmatter/{domain}"
frontmatter_filename_pattern: "{slug}.yaml"

# Prompt templates
prompts:
  description:
    template: "description.txt"
  micro:
    template: "micro.txt"
```

**Key Insight**: Config defines domain-specific details, code remains generic.

### Generic Generator Methods

**NO component-specific methods**:

```python
# ❌ WRONG: Component-specific methods
def _generate_micro(self, material): ...
def _generate_description(self, material): ...
def _generate_faq(self, material): ...

# ✅ CORRECT: Generic method with parameter
def generate(self, item_name: str, component_type: str, domain: str):
    # Works for ANY domain and ANY component type
    adapter = self._get_domain_adapter(domain)
    template = adapter.load_prompt_template(component_type)
    prompt = self._build_prompt(template, item_name)
    content = self.api_client.generate(prompt)
    return content
```

### Universal Command Pattern

**Same command works for all domains**:

```bash
# Materials domain
python3 run.py --domain materials --item aluminum --component description

# Contaminants domain
python3 run.py --domain contaminants --item adhesive-residue --component description

# Settings domain
python3 run.py --domain settings --item aluminum-standard --component description

# Future domain (no code changes needed)
python3 run.py --domain regions --item north-america --component description
```

**Zero code changes required for new domains.**

---

## Example-Free Architecture

### Core Principle

**Voice instructions dominate, no example templates needed.**

### Traditional Approach (Anti-Pattern)

❌ **WRONG**: Using example templates

```
# Template contains example output
EXAMPLE OUTPUT:
"Aluminum's lightweight strength lines up with aerospace demands, 
while its corrosion resistance cuts down maintenance..."

Now write similar content for: {material_name}
```

**Problems**:
- Examples constrain creativity
- Model mimics structure too closely
- Hard to maintain consistency across examples
- Examples become outdated
- Can't handle materials significantly different from example

### Voice-Driven Approach (Correct)

✅ **RIGHT**: Strong voice instructions, no examples

```
# prompts/materials/description.txt

TASK: Write a focused description of {material_name}.

{voice_instruction}  ← Comprehensive voice from persona file

REQUIREMENTS:
- 1-2 sentences
- Qualitative terms only
- Focus on practical applications

NO EXAMPLES NEEDED - Voice instruction provides complete guidance.
```

**Benefits**:
- More creative variation
- Consistent voice across all materials
- No example maintenance burden
- Handles any material naturally
- Voice is single source of truth

### Voice Instruction Power

**Comprehensive voice instructions replace examples**:

```yaml
# shared/voice/profiles/todd_dunning.yaml (838 chars)

core_voice_instruction: |
  Write with paratactic chains (independent clauses linked by conjunctions).
  Use phrasal verbs: "line up", "dial in", "ramp up", "cut down", "work out".
  Prefer quantified outcomes: "by 20%", "cuts X%", "improves Y%".
  Use practical transitions: "turns out", "in practice", "overall".
  Connect statements with "and", "but", "while" for paratactic flow.
  
  FORBIDDEN PHRASES (reject content containing these):
  - "presents a challenge/opportunity"
  - "critical pitfall"
  - "unique challenge"
  - "significant concern"
  
  Write naturally with paratactic rhythm. No theatrical language.
```

**Result**: 838 chars of voice instruction = 100% consistency across all content, no examples needed.

### Testing Voice-Driven Generation

**Verification**: Generate 10 items with same author

```bash
for material in aluminum steel titanium copper brass; do
  python3 run.py --domain materials --item "$material" --component description
done
```

**Expected**: All 10 use phrasal verbs, paratactic chains, quantified outcomes (voice consistency)

**NOT Expected**: All 10 have identical structure (humanness provides variation)

---

## Shared Component Patterns

### Universal Components

**Components used across ALL domains**:

| Component | Location | Used By |
|-----------|----------|---------|
| **Generator** | `generation/core/generator.py` | All domains |
| **Prompt Builder** | `shared/text/utils/prompt_builder.py` | All domains |
| **Voice Profiles** | `shared/voice/profiles/*.yaml` | All domains |
| **Quality Evaluator** | `shared/text/quality/evaluator.py` | All domains |
| **Humanness Optimizer** | `learning/humanness_optimizer.py` | All domains |
| **Data Manager** | `shared/data/manager.py` | All domains |

### Domain-Specific Components

**Components unique to each domain**:

| Component | Pattern | Example |
|-----------|---------|---------|
| **Config** | `domains/{domain}/config.yaml` | `domains/materials/config.yaml` |
| **Prompts** | Prompt catalog `catalog.byPath` entries like `prompts/{domain}/*.txt` | `prompts/materials/description.txt` |
| **Data** | `data/{domain}/Data.yaml` | `data/materials/Materials.yaml` |

### Dependency Pattern

**Shared components never import domain-specific components**:

```python
# ✅ CORRECT: Shared imports only
from shared.voice.profiles import load_persona
from shared.text.utils.prompt_builder import PromptBuilder
from generation.core.generator import Generator

# ❌ WRONG: Shared importing domain-specific
from domains.materials.config import MaterialConfig  # ❌ Creates tight coupling
```

**Domain-specific components CAN import shared components**:

```python
# ✅ CORRECT: Domain imports shared
from shared.voice.profiles import load_persona
from shared.text.utils.prompt_builder import PromptBuilder
```

**Dependency Direction**: `domains/` → `shared/`, NEVER `shared/` → `domains/`

### Reusability Test

**Question**: Can this component work for a completely different domain?

- ✅ **YES** → Put in `shared/`
- ❌ **NO** → Put in `domains/{domain}/`

**Examples**:
- Voice profiles → `shared/` (used by all domains)
- Prompt builder → `shared/` (assembles prompts for any domain)
- Material properties → `domains/materials/` (material-specific)
- Contamination patterns → `domains/contaminants/` (contaminant-specific)

---

## Adding New Domains

### 3-Step Process (Zero Code Changes)

#### Step 1: Create Domain Configuration

**File**: `domains/{new_domain}/config.yaml`

```yaml
# Data configuration
data_path: "data/{new_domain}/Data.yaml"
data_root_key: "items"  # Root key in YAML
author_key: "author.id"

# Context keys (classification + raw data ONLY)
context_keys:
  - category
  - subcategory
  - properties.temperature_range
  - properties.efficiency
  # NO text fields (description, context_notes, etc.)

# Frontmatter configuration
frontmatter_directory: "frontmatter/{new_domain}"
frontmatter_filename_pattern: "{slug}.yaml"

# Component configuration
prompts:
  description:
    template: "description.txt"
  micro:
    template: "micro.txt"
```

#### Step 2: Create Prompt Templates

**Prompt catalog entry**: `prompts/{new_domain}/description.txt`

```
TASK: Write a focused description of {topic}.

CONTEXT:
Category: {category}
Key facts: {facts}

REQUIREMENTS:
- 1-2 sentences
- Focus on practical applications
- Qualitative terms only

{voice_instruction}

WORD COUNT: 50-150 words
```

#### Step 3: Create Data File

**File**: `data/{new_domain}/Data.yaml`

```yaml
items:
  item-one:
    category: "Category A"
    properties:
      key1: "value1"
    author:
      id: "todd_dunning"
```

**That's it. No code changes. System automatically discovers new domain.**

### Verification

```bash
# Generate content for new domain
python3 run.py --domain new_domain --item item-one --component description

# Expected: Works immediately, no code modifications needed
```

---

## Quality Standards

### Zero Fallbacks Policy

**NO defaults, NO fallbacks, NO silent degradation.**

```python
# ❌ WRONG: Fallback value
author_id = data.get('author', {}).get('id', 'todd_dunning')  # Silent fallback

# ✅ CORRECT: Fail fast
author_id = data.get('author', {}).get('id')
if not author_id:
    raise ValueError(f"No author assigned for {item_name}")
```

### Quality Gates

**ALL content must pass quality evaluation**:

1. **Winston AI Detection**: 69%+ human score (threshold varies by humanness intensity)
2. **Readability Check**: Pass status
3. **Subjective Language**: No violations
4. **Realism Score**: 7.0/10 minimum
5. **Voice Authenticity**: Pattern compliance (phrasal verbs, quantified outcomes, etc.)

**If ANY gate fails**: Content rejected, parameters adjusted, regeneration attempted

### Learning Integration

**Every generation logged to learning database**:

```python
# Log to database for learning
self._log_to_learning_db(
    item_name=material_name,
    component_type=component_type,
    content=content,
    quality_scores={
        'winston': winston_score,
        'realism': realism_score,
        'voice_authenticity': voice_score
    },
    parameters={
        'temperature': temp,
        'frequency_penalty': freq_penalty
    }
)
```

**Learning system uses logs to**:
- Optimize temperature and penalties (sweet spot analysis)
- Identify AI-like patterns (rejection learning)
- Improve voice authenticity (pattern compliance)
- Refine humanness layer (structural diversity)

---

## Implementation Examples

### Example 1: Materials Domain (Current)

**Configuration**: `domains/materials/config.yaml`
```yaml
# Standardized nested structure (Jan 2026)
domain:
  name: materials
  display_name: "Laser Cleaning Materials"
  version: "1.0.0"

data_adapter:
  data_path: "data/materials/Materials.yaml"
  data_root_key: "materials"
  author_key: "author.id"
  context_keys: [category, properties.hardness, properties.melting_point]

frontmatter:
  directory: "frontmatter/materials"
  filename_pattern: "{slug}-laser-cleaning.yaml"
```

**Usage**:
```bash
python3 run.py --domain materials --item aluminum --component description
```

### Example 2: Contaminants Domain (Current)

**Configuration**: `domains/contaminants/config.yaml`
```yaml
# Standardized nested structure (Jan 2026)
domain:
  name: contaminants
  display_name: "Contamination Patterns"
  version: "1.0.0"

data_adapter:
  data_path: "data/contaminants/Contaminants.yaml"
  data_root_key: "contamination_patterns"
  author_key: "author.id"
  context_keys: [category, removal_difficulty, health_risk]

frontmatter:
  directory: "frontmatter/contaminants"
  filename_pattern: "{slug}-contamination.yaml"
```

**Usage**:
```bash
python3 run.py --domain contaminants --item oil-residue --component description
```

### Example 3: Settings Domain (Current)

**Configuration**: `domains/settings/config.yaml`
```yaml
# Standardized nested structure (Jan 2026)
domain:
  name: settings
  display_name: "Laser Parameter Settings"
  version: "1.0.0"

data_adapter:
  data_path: "data/settings/Settings.yaml"
  data_root_key: "settings"
  author_key: "author.id"
  context_keys: [material_category, process_type]

frontmatter:
  directory: "frontmatter/settings"
  filename_pattern: "{slug}-settings.yaml"
```

**Usage**:
```bash
python3 run.py --domain settings --item aluminum-standard --component description
```

### Example 4: Future Domain (Hypothetical)

**Configuration**: `domains/regions/config.yaml`
```yaml
data_path: "data/regions/Regions.yaml"
data_root_key: "regions"
author_key: "author.id"
context_keys: [continent, industry_focus]
prompts:
  description: {template: "description.txt"}
```

**Usage**:
```bash
python3 run.py --domain regions --item north-america --component description
```

**No code changes needed - system discovers automatically.**

---

## Anti-Patterns

### ❌ Domain-Specific Generator Methods

**WRONG**:
```python
class Generator:
    def generate_material_description(self, material): ...
    def generate_contaminant_description(self, contaminant): ...
    def generate_setting_description(self, setting): ...
```

**Correct**:
```python
class Generator:
    def generate(self, item_name: str, component_type: str, domain: str):
        # Works for ANY domain
```

### ❌ Hardcoded Domain Logic

**WRONG**:
```python
if domain == 'materials':
    data_path = 'data/materials/Materials.yaml'
elif domain == 'contaminants':
    data_path = 'data/contaminants/Contaminants.yaml'
```

**Correct**:
```python
# Load from config
config = self._load_domain_config(domain)
data_path = config['data_path']
```

### ❌ Example Templates

**WRONG**:
```
EXAMPLE: "Aluminum's lightweight strength lines up..."
Now write similar content for: {material_name}
```

**Correct**:
```
{voice_instruction}  ← Comprehensive voice guidance, no examples
```

### ❌ Voice Instructions in Domain Prompts

**WRONG**:
```
# prompt catalog entry: prompts/materials/description.txt
Write with paratactic chains...  ← Hardcoded voice
```

**Correct**:
```
# prompt catalog entry: prompts/materials/description.txt
{voice_instruction}  ← Placeholder filled from persona
```

### ❌ Fallback Values

**WRONG**:
```python
author_id = data.get('author', {}).get('id', 'todd_dunning')
```

**Correct**:
```python
author_id = data.get('author', {}).get('id')
if not author_id:
    raise ValueError("No author assigned")
```

---

## Testing & Enforcement

### Automated Tests

**File**: `tests/test_architecture_principles.py`

**Test Coverage**:
1. **Domain-Agnostic**:
   - `test_generator_works_for_all_domains()` - Same code for all domains
   - `test_no_domain_specific_methods()` - No hardcoded domain logic
   - `test_config_driven_data_loading()` - Data paths from config

2. **Separation of Concerns**:
   - `test_voice_only_in_personas()` - No voice in domain prompts
   - `test_humanness_only_in_optimizer()` - No humanness in personas
   - `test_domain_prompts_have_placeholder()` - `{voice_instruction}` present

3. **Example-Free**:
   - `test_no_example_templates()` - No example output in prompts
   - `test_voice_instructions_sufficient()` - Voice provides all guidance

4. **Shared Components**:
   - `test_shared_never_imports_domain()` - Dependency direction correct
   - `test_reusability_across_domains()` - Components work universally

### Manual Verification

**Checklist for New Domains**:
- [ ] Configuration file created (`domains/{domain}/config.yaml`)
- [ ] Prompt catalog entries created (`prompts/{domain}/*.txt`)
- [ ] Data file created (`data/{domain}/Data.yaml`)
- [ ] NO code changes in `generation/core/`
- [ ] NO domain-specific methods added
- [ ] `{voice_instruction}` placeholder in prompts
- [ ] No example templates
- [ ] Generation works immediately: `python3 run.py --domain {domain} --item {item} --component {component}`

---

## Quick Reference

### Architecture Checklist

| Principle | Implementation | Verification |
|-----------|---------------|--------------|
| **Separation of Concerns** | 3 layers (Voice/Humanness/Domain) | Voice ONLY in personas, Humanness ONLY in optimizer |
| **Single Source of Truth** | One authoritative location per data type | No duplication across files |
| **Configuration Over Code** | Domain config + prompts = new domain | No code changes for new domains |
| **Template-Driven** | All prompts in .txt files | Zero hardcoded prompts in code |
| **Fail-Fast** | Explicit exceptions, no fallbacks | No `.get(key, default)` in production |
| **Domain-Agnostic** | Generic generator methods | Same code works for all domains |
| **Example-Free** | Voice instructions dominate | No example templates in prompts |
| **Shared Components** | Universal reusability | `shared/` → used by all domains |

### File Organization

```
project/
├── shared/                          # Universal components
│   ├── voice/profiles/*.yaml        # Author personas (Layer 1)
│   ├── text/utils/prompt_builder.py # Prompt assembly
│   └── text/quality/evaluator.py   # Quality evaluation
├── learning/                        # Learning system
│   └── humanness_optimizer.py       # Structural variation (Layer 2)
├── generation/core/                 # Generation orchestration
│   ├── generator.py                 # Domain-agnostic generator
│   └── adapters/domain_adapter.py  # Config-driven data loading
├── prompts/registry/                # Prompt catalog
│   └── prompt_catalog.yaml          # Component templates (Layer 3)
├── domains/{domain}/                # Domain-specific config
│   ├── config.yaml                  # Data paths, context keys
└── data/{domain}/                   # Data files
    └── Data.yaml                    # Domain data
```

### Command Examples

```bash
# Materials domain
python3 run.py --domain materials --item aluminum --component description

# Contaminants domain
python3 run.py --domain contaminants --item oil-residue --component description

# Settings domain
python3 run.py --domain settings --item aluminum-standard --component description

# Test architecture
pytest tests/test_architecture_principles.py -v

# Verify separation of concerns
pytest tests/test_separation_of_concerns.py -v
```

---

## Summary

**Single Source of Truth**: This guide consolidates 4 architecture policy documents into one comprehensive reference.

**Core Principles**:
1. **Separation of Concerns**: Voice (Layer 1) + Humanness (Layer 2) + Domain (Layer 3)
2. **Domain-Agnostic Design**: Same code works for all domains
3. **Example-Free Architecture**: Voice instructions dominate, no examples
4. **Shared Component Patterns**: Universal reusability across domains
5. **Configuration Over Code**: Add domains via config files, not code changes

**Key Benefits**:
- ✅ Add new domains without code changes (3-step process)
- ✅ Consistent voice across all content (persona-driven)
- ✅ Clean separation of concerns (no overlap)
- ✅ High reusability (shared components)
- ✅ Easy maintenance (single source of truth)
- ✅ Fail-fast architecture (no silent degradation)

**Enforcement**: Automated tests + manual code review  
**Grade**: A+ compliance - All principles operational

**Status**: ✅ ACTIVE - All patterns implemented and enforced

---

**See Also**:
- `PROMPT_SYSTEM_GUIDE.md` - Prompt architecture and policies
- `VOICE_SYSTEM_GUIDE.md` - Author voice architecture
- `IMAGE_ARCHITECTURE.md` - Image generation system (domain-specific, kept separate)
- `docs/02-architecture/processing-pipeline.md` - Full generation pipeline

**Archived Sources** (2025-12-20):
- `docs/archive/2025-12/policies/CLEAN_SEPARATION_OF_CONCERNS_DEC12_2025.md`
- `docs/archive/2025-12/policies/FULLY_REUSABLE_SYSTEM_GUIDE.md`
- `docs/archive/2025-12/policies/EXAMPLE_FREE_ARCHITECTURE.md`
- `docs/archive/2025-12/policies/SHARED_ARCHITECTURE_PROPOSAL.md`
