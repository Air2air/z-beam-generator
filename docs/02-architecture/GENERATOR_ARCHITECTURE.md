# Generator Architecture

**Last Updated**: December 26, 2025  
**Purpose**: Canonical reference for all content generation systems in z-beam-generator

---

## Overview

The z-beam-generator system uses a **unified generation architecture** with specialized generators for different content types. All generators follow fail-fast principles and maintain quality evaluation pipelines.

---

## Core Generator: QualityEvaluatedGenerator

**Location**: `generation/core/evaluated_generator.py` (46KB)  
**Status**: ✅ **ACTIVE** - Primary generator for ALL text content  
**Domains**: materials, compounds, contaminants, settings (universal)

### Purpose
Single-pass content generation with comprehensive quality evaluation and learning integration.

### Features
- ✅ Unified API for all domains (no domain-specific code)
- ✅ Winston AI detection integration
- ✅ Subjective quality evaluation (Realism, Voice Authenticity)
- ✅ Learning integration (logs ALL attempts for continuous improvement)
- ✅ Author voice consistency (persona-based generation)
- ✅ Humanness layer (structural diversity, rhythm variation)
- ✅ Direct save to data YAML files (Materials.yaml, Compounds.yaml, etc.)

### Architecture
```python
from generation.core.evaluated_generator import QualityEvaluatedGenerator

# Initialize with domain
generator = QualityEvaluatedGenerator(
    api_client=api_client,
    subjective_evaluator=evaluator,
    winston_client=winston,
    domain="materials"  # materials, compounds, contaminants, settings
)

# Generate content
result = generator.generate(
    item_name="aluminum-laser-cleaning",
    component_type="description",
    author_id=1
)
```

### Quality Pipeline
1. **Parameter Selection** - Load sweet spot parameters from learning database
2. **Voice Loading** - Load author persona from `shared/voice/profiles/{author}.yaml`
3. **Humanness Layer** - Apply structural diversity (rhythm, opening, transitions)
4. **Generation** - Single API call with optimized parameters
5. **Save to Data** - Write to Materials.yaml/Compounds.yaml immediately
6. **Quality Evaluation** - Winston + Realism + Voice scoring
7. **Learning** - Log ALL attempts (not just successes) for improvement

### When to Use
- ✅ ALL text content generation (micro, description, FAQ)
- ✅ Any domain that needs quality-evaluated content
- ✅ Production content that requires author voice consistency

---

## Auxiliary Generator: Generator

**Location**: `generation/core/generator.py` (33KB)  
**Status**: ✅ **ACTIVE** - Low-level generation primitive  
**Used By**: QualityEvaluatedGenerator (internal), BatchGenerator

### Purpose
Core text generation primitive without quality gates. Used internally by QualityEvaluatedGenerator.

### Features
- ✅ Direct API calls to LLM (Grok)
- ✅ Prompt template loading from `domains/{domain}/prompts/`
- ✅ Voice instruction injection
- ✅ Parameter passing (temperature, penalties, max_tokens)
- ❌ NO quality evaluation (delegated to caller)
- ❌ NO learning integration (delegated to caller)

### When to Use
- ⚠️ **Rarely used directly** - prefer QualityEvaluatedGenerator
- ✅ Internal use by higher-level generators
- ✅ Testing/debugging generation without quality gates

---

## Batch Generator: BatchGenerator

**Location**: `generation/core/batch_generator.py` (27KB)  
**Status**: ✅ **ACTIVE** - Batch processing orchestrator  
**Purpose**: Generate content for multiple items in parallel

### Features
- ✅ Multi-threaded batch processing
- ✅ Progress tracking with rich console output
- ✅ Statistics aggregation (success/fail counts)
- ✅ Domain agnostic (works for all domains)
- ✅ Uses QualityEvaluatedGenerator internally

### When to Use
- ✅ Generate content for 10+ items at once
- ✅ Bulk regeneration after prompt updates
- ✅ Initial content population for new materials

---

## SEO Generator: SEOGenerator

**Location**: `generation/seo/seo_generator.py` (formerly simple_seo_generator.py, 7KB)  
**Status**: ✅ **ACTIVE** - Preferred SEO generator  
**Purpose**: Generate page_title and meta_description for all domains

### Features
- ✅ Unified interface for all domains
- ✅ Domain-specific prompt loading from `generation/seo/domain_prompts.py`
- ✅ Direct writes to data YAML files
- ✅ Follows PAGE_TITLE_META_DESCRIPTION_SPEC.md requirements
- ✅ User search intent optimization

### Architecture
```python
from generation.seo.seo_generator import SEOGenerator

generator = SEOGenerator(api_client, domain='materials')
title_ok, desc_ok = generator.generate_for_item('aluminum-laser-cleaning')
```

### When to Use
- ✅ Generate SEO metadata (page_title, meta_description)
- ✅ Any domain (materials, contaminants, settings, compounds)

### Deprecated Alternative
- ⚠️ `generation/seo/domain_seo_generators.py` (15KB) - Legacy domain-specific generators
- **Status**: Deprecated, use SEOGenerator instead
- **Contains**: MaterialSEOGenerator, ContaminantSEOGenerator, SettingSEOGenerator, CompoundSEOGenerator

---

## Domain Coordinators

**Location**: `domains/{domain}/coordinator.py`  
**Status**: ✅ **ACTIVE** - All 4 domains now have coordinators  
**Purpose**: Orchestrate generation for specific domains

### Hierarchy
```
DomainCoordinator (shared/domain/base_coordinator.py)
├── MaterialsCoordinator (domains/materials/coordinator.py)
├── CompoundCoordinator (domains/compounds/coordinator.py)
├── ContaminantCoordinator (domains/contaminants/coordinator.py) ← NEW (Dec 26)
└── SettingCoordinator (domains/settings/coordinator.py) ← NEW (Dec 26)
```

### Purpose
- ✅ Initialize QualityEvaluatedGenerator with domain config
- ✅ Manage Winston client and SubjectiveEvaluator
- ✅ Handle domain-specific data loading
- ✅ Provide convenient wrappers (e.g., `generate_compound_content()`)

### Common Interface (via DomainCoordinator)
```python
# All coordinators provide the same interface
coordinator.generate_content(item_id, component_type, force_regenerate)
coordinator.list_items()
coordinator.get_item_data(item_id)
```

### When to Use
- ✅ Domain-specific generation workflows
- ✅ Need access to domain data loaders
- ✅ Batch generation for entire domain

---

## Removed/Deprecated Generators

### ❌ evaluated_generator_new.py (REMOVED Dec 26, 2025)
- **Reason**: Experimental refactor that was never adopted
- **Replacement**: Use `evaluated_generator.py` (canonical version)

### ❌ minimal_generator.py (REMOVED Dec 26, 2025)
- **Reason**: Unused minimal SEO generator
- **Replacement**: Use `seo_generator.py`

---

## Decision Matrix: Which Generator to Use?

| Use Case | Generator | Location |
|----------|-----------|----------|
| Text content (micro, description, FAQ) | `QualityEvaluatedGenerator` | `generation/core/evaluated_generator.py` |
| SEO metadata (title, description) | `SEOGenerator` | `generation/seo/seo_generator.py` |
| Batch generation (10+ items) | `BatchGenerator` | `generation/core/batch_generator.py` |
| Domain-specific workflow | `*Coordinator` | `domains/{domain}/coordinator.py` |
| Low-level testing/debugging | `Generator` | `generation/core/generator.py` |

---

## Key Principles

### 1. **Universal Architecture**
All generators work across ALL domains without domain-specific code. Domain logic lives in configuration files and prompt templates.

### 2. **Fail-Fast Design**
Generators validate inputs and fail immediately on missing dependencies. No silent degradation or fallback values.

### 3. **Quality-First**
Text content always goes through quality evaluation pipeline (Winston, Realism, Voice). Only SEO generation skips quality gates (different requirements).

### 4. **Learning Integration**
ALL generation attempts (not just successes) are logged to learning database for continuous parameter optimization.

### 5. **Single Responsibility**
- `Generator`: Generate text (no evaluation)
- `QualityEvaluatedGenerator`: Orchestrate generation + evaluation + learning
- `BatchGenerator`: Process multiple items in parallel
- `SEOGenerator`: Generate SEO metadata specifically
- `*Coordinator`: Domain-specific orchestration and data access

---

## File Organization

```
generation/
├── core/
│   ├── evaluated_generator.py      ← Primary text generator (46KB) ✅
│   ├── generator.py                 ← Low-level primitive (33KB) ✅
│   ├── batch_generator.py          ← Batch processing (27KB) ✅
│   ├── parameter_manager.py        ← Parameter optimization
│   ├── quality_orchestrator.py     ← Quality evaluation
│   └── learning_integrator.py      ← Learning database integration
│
├── seo/
│   ├── seo_generator.py            ← Preferred SEO generator (7KB) ✅
│   ├── domain_seo_generators.py    ← Legacy (deprecated) ⚠️
│   └── domain_prompts.py           ← SEO prompt templates
│
└── config/
    └── dynamic_config.py           ← Parameter calculation

domains/
├── materials/coordinator.py         ← Materials orchestration ✅
├── compounds/coordinator.py         ← Compounds orchestration ✅
├── contaminants/coordinator.py     ← Contaminants orchestration ✅ NEW
└── settings/coordinator.py          ← Settings orchestration ✅ NEW
```

---

## Migration Guide

### If you're using deprecated generators:

**FROM**: `domain_seo_generators.py`  
**TO**: `seo_generator.py`
```python
# OLD (deprecated):
from generation.seo.domain_seo_generators import MaterialSEOGenerator
generator = MaterialSEOGenerator(api_client)

# NEW (preferred):
from generation.seo.seo_generator import SEOGenerator
generator = SEOGenerator(api_client, domain='materials')
```

**FROM**: Direct use of `Generator`  
**TO**: `QualityEvaluatedGenerator`
```python
# OLD (no quality evaluation):
from generation.core.generator import Generator
generator = Generator(api_client)

# NEW (with quality evaluation):
from generation.core.evaluated_generator import QualityEvaluatedGenerator
generator = QualityEvaluatedGenerator(api_client, evaluator, winston, domain='materials')
```

---

## Testing

All generators have comprehensive test coverage:
- `tests/test_evaluated_generator.py` - Quality evaluation pipeline
- `tests/test_batch_generator.py` - Batch processing
- `tests/test_seo_generator.py` - SEO metadata generation
- `tests/test_*_coordinator.py` - Domain coordinator tests

---

## Related Documentation

- [Processing Pipeline](./processing-pipeline.md) - Complete generation flow
- [Prompt System](../domains/PROMPT_SYSTEM.md) - Prompt template architecture
- [Voice System](../08-development/VOICE_SYSTEM.md) - Author persona management
- [Learning System](../08-development/LEARNING_SYSTEM.md) - Parameter optimization

---

## Questions?

- **"Which generator should I use?"** → See Decision Matrix above
- **"Why are there multiple generators?"** → Separation of concerns (text vs SEO vs batch)
- **"Can I use Generator directly?"** → Only for testing; use QualityEvaluatedGenerator in production
- **"What happened to evaluated_generator_new.py?"** → Removed Dec 26, 2025 (never adopted)
