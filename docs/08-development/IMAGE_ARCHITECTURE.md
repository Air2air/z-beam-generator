# Image Generation Architecture

**Date**: November 30, 2025  
**Status**: Post-Consolidation (Clean Architecture)

## Overview

The image generation system creates before/after laser cleaning images using a layered architecture that separates concerns between domain-specific and shared components.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DOMAIN LAYER (materials/)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MaterialImageGenerator                                                     │
│  ├── ContaminationPatternSelector (reads Contaminants.yaml)                │
│  ├── Orchestrator (delegates prompt building)                              │
│  └── Domain-specific: negative prompts, rust exclusion, shape research     │
│                                                                             │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ delegates to
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SHARED LAYER (shared/image/)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ImagePromptOrchestrator (3 stages)                                        │
│  ├── Stage 1: RESEARCH - Load or use provided research data                │
│  ├── Stage 2: ASSEMBLY - SharedPromptBuilder creates prompt                │
│  └── Stage 3: VALIDATION - UnifiedValidator checks prompt                  │
│                                                                             │
│  SharedPromptBuilder                                                        │
│  ├── Loads 4-layer templates (base + physics + contamination + micro)      │
│  ├── Applies variable replacements (material, patterns, visual props)       │
│  ├── Calls PromptOptimizer for Imagen API limits                           │
│  └── Calls ResearchDataVerifier to ensure data retention                   │
│                                                                             │
│  UnifiedValidator (3-stage validation)                                     │
│  ├── EarlyStageValidator - config, templates, material                     │
│  ├── PromptStageValidator - length, logic, contradictions, required        │
│  └── PostStageValidator - vision/realism (after image generation)          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Domain Layer (`domains/materials/image/`)

| Component | Responsibility |
|-----------|---------------|
| `MaterialImageGenerator` | Domain entry point - loads contamination, delegates to orchestrator, adds negative prompts |
| `ContaminationPatternSelector` | Reads Contaminants.yaml (ZERO API calls) |
| `MaterialShapeResearcher` | Optional Gemini API call for shape research |
| `AssemblyResearcher` | Optional research for complex part assembly context |
| `material_config.py` | Domain-specific config (MaterialImageConfig) |

### Shared Layer (`shared/image/`)

| Component | Responsibility |
|-----------|---------------|
| `ImagePromptOrchestrator` | 3-stage pipeline: Research → Assembly → Validation |
| `SharedPromptBuilder` | Template loading, variable replacement, optimization |
| `PromptOptimizer` | Imagen API length optimization (preserves CRITICAL markers) |
| `ResearchDataVerifier` | Ensures 70%+ research data retained after optimization |
| `UnifiedValidator` | Single validator for all stages (early/prompt/post) |

### Validation Layer (`shared/validation/`)

| Component | Responsibility |
|-----------|---------------|
| `UnifiedValidator` | Consolidated validator - all validation in one place |
| `EarlyStageValidator` | Pre-research: config, templates, material existence |
| `PromptStageValidator` | Pre-generation: length, logic, required content |
| `PostStageValidator` | Post-generation: vision analysis, realism scoring |

## Data Flow

```
1. User Request
   └── MaterialImageGenerator.generate_complete(material_name, config)

2. Research (Domain-Specific)
   ├── ContaminationPatternSelector.get_patterns_for_image_gen()
   │   └── Returns patterns from Contaminants.yaml (ZERO API calls)
   └── Optional: MaterialShapeResearcher.get_common_shape()

3. Orchestration (Shared)
   └── ImagePromptOrchestrator.generate_hero_prompt()
       ├── Stage 1: Use provided research_data
       ├── Stage 2: SharedPromptBuilder.build_generation_prompt()
       │   ├── Load templates (base_structure, realism_physics, etc.)
       │   ├── Build replacements (material, patterns, visual props)
       │   ├── Optimize for Imagen limits
       │   └── Verify research data retention (70%+ threshold)
       └── Stage 3: UnifiedValidator.validate_prompt()

4. Return Result
   └── {prompt, negative_prompt, research_data, config, stage_outputs}
```

## Template System

Prompts are built from 4 layers in `domains/materials/image/prompts/shared/generation/`:

| Layer | File | Purpose |
|-------|------|---------|
| 1. Base | `base_structure.txt` | Split-screen format, position shift, background |
| 2. Physics | `realism_physics.txt` | Gravity, accumulation, layering rules |
| 3. Contamination | `contamination_rules.txt` | Distribution, edge effects, grain following |
| 4. Micro-scale | `micro_scale_details.txt` | Porosity, feathering, lighting |

Plus:
- `forbidden_patterns.txt` - Anti-patterns to avoid
- `feedback/user_corrections.txt` - User feedback applied to all prompts

## Key Design Decisions

### Single Validator (UnifiedValidator)
**Why**: Previously had 3 validators (prompt_validator, payload_validator, unified_validator) with 60-70% overlap. Consolidated into one for single source of truth.

### 3-Stage Orchestrator (not 6)
**Why**: Stages 2-4 (Visual/Composition/Refinement) were no-ops without API client. Simplified to stages that actually execute: Research, Assembly, Validation.

### SharedPromptBuilder as Core
**Why**: All prompt building goes through one component that handles templates, optimization, and verification. Domain generators are thin wrappers.

### Zero API Calls for Contamination
**Why**: All contamination data pre-populated in Contaminants.yaml. Pattern selector reads YAML only - deterministic, fast, no cache dependencies.

## Files Removed (Dead Code)

| File | Reason |
|------|--------|
| `shared/image/generator.py` | UniversalImageGenerator - duplicate of SharedPromptBuilder functionality |
| `shared/image/validation/payload_validator.py` | Imagen-specific validation merged into UnifiedValidator |

**Note**: `shared/validation/prompt_validator.py` remains - it provides `validate_image_prompt()` which wraps UnifiedValidator for backward compatibility.

## Usage Example

```python
from domains.materials.image.material_generator import MaterialImageGenerator
from domains.materials.image.material_config import MaterialImageConfig

# Initialize
generator = MaterialImageGenerator(gemini_api_key="optional")

# Configure
config = MaterialImageConfig(
    material_name="Aluminum",
    category="metal_non_ferrous",
    contamination_uniformity=3,  # 1-5 variety
    view_mode="Contextual"
)

# Generate
result = generator.generate_complete(
    material_name="Aluminum",
    config=config
)

# Use prompt with Imagen API
prompt = result["prompt"]
negative_prompt = result["negative_prompt"]
```

## Validation Usage

```python
from shared.validation.unified_validator import UnifiedValidator, validate_prompt_quick

# Quick validation
report = validate_prompt_quick(prompt, material="Aluminum")
if report.status != ValidationStatus.PASS:
    print(report.fix_instructions)

# Full pipeline validation
validator = UnifiedValidator(prompts_dir=Path("prompts/shared"))
early_report = validator.validate_early(material="Aluminum", config={...})
prompt_report = validator.validate_prompt(prompt, negative_prompt, material)
```
