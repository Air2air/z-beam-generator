# Shared Architecture Reorganization Proposal

**Date**: December 6, 2025  
**Status**: PROPOSAL - Requires approval before implementation  
**Goal**: Consolidate generation, validation, learning, and voice functions into clean, reusable structure

---

## 🎯 Current Problems

### 1. **Scattered Functionality**
```
generation/          → Text generation logic
processing/          → Content processing (not in shared/)
learning/            → Learning systems (root level)
postprocessing/      → Validation and detection (root level)
shared/              → Mixed utilities, incomplete organization
parameters/          → Voice parameters (root level)
```

### 2. **Unclear Ownership**
- Where does "text generation" logic live? (generation/ or shared/?)
- Where does "image generation" logic live? (shared/image/ or domains/?)
- Where do "validation" functions live? (postprocessing/ or shared/?)
- Where do "learning" systems live? (learning/ or shared/?)

### 3. **Domain Coupling**
- `generation/` folder tightly coupled to text generation
- Image generation in `shared/image/` but text generation not in `shared/text/`
- No clear pattern for adding new generation types (video, audio, etc.)

### 4. **Voice Architecture Split**
- Voice personas: `shared/voice/profiles/` (current location)
- Voice parameters: `parameters/voice/` (deprecated)
- Voice detection: `postprocessing/detection/` (deprecated)
- Voice validation: `postprocessing/evaluation/` (deprecated)

---

## 🏗️ Proposed Architecture

### Overview: Unified `/shared` Structure

```
shared/
├── core/                    # Core abstractions (NEW)
│   ├── generators.py        # Base generator classes
│   ├── validators.py        # Base validator classes
│   ├── learners.py          # Base learning classes
│   └── processors.py        # Base processor classes
│
├── generation/              # ALL generation (EXPANDED)
│   ├── text/               # Text generation (MOVED from /generation)
│   │   ├── generator.py
│   │   ├── evaluator.py
│   │   ├── prompt_builder.py
│   │   └── adapter.py
│   │
│   ├── image/              # Image generation (EXISTS)
│   │   ├── generator.py
│   │   ├── orchestrator.py
│   │   ├── prompt_builder.py
│   │   └── validator.py
│   │
│   ├── common/             # Shared generation utilities (NEW)
│   │   ├── api_client_factory.py
│   │   ├── retry_handler.py
│   │   └── result_types.py
│   │
│   └── config/             # Generation config (MOVED from /generation/config)
│       ├── dynamic_config.py
│       └── api_config.py
│
├── validation/              # ALL validation (CONSOLIDATED)
│   ├── quality/            # Quality validation (from postprocessing/)
│   │   ├── winston_validator.py
│   │   ├── realism_validator.py
│   │   ├── readability_validator.py
│   │   └── composite_scorer.py
│   │
│   ├── content/            # Content validation (NEW)
│   │   ├── schema_validator.py
│   │   ├── completeness_validator.py
│   │   └── consistency_validator.py
│   │
│   └── voice/              # Voice validation (from postprocessing/detection)
│       ├── persona_validator.py
│       ├── forbidden_phrase_detector.py
│       └── voice_post_processor.py
│
├── learning/                # ALL learning (MOVED from /learning)
│   ├── humanness_optimizer.py
│   ├── realism_optimizer.py
│   ├── sweet_spot_analyzer.py
│   ├── threshold_manager.py
│   ├── pattern_learner.py
│   └── weight_learner.py
│
├── voice/                   # ALL voice (CONSOLIDATED)
│   ├── profiles/           # Voice definitions (CURRENT LOCATION)
│   │   ├── indonesia.yaml
│   │   ├── italy.yaml
│   │   ├── taiwan.yaml
│   │   └── united_states.yaml
│   │
│   ├── persona_loader.py   # Persona loading (NEW)
│   ├── voice_renderer.py   # Voice instruction rendering (NEW)
│   └── parameters/         # Voice parameters (MOVED from /parameters/voice)
│       ├── professional_voice.py
│       └── vocabulary.py
│
├── prompts/                 # Prompt templates (EXISTS)
│   ├── templates/          # Shared prompt templates (domain templates in domains/)
│
├── research/                # Research utilities (EXISTS)
│   ├── gemini_researcher.py
│   └── property_researcher.py
│
├── data/                    # Data access layer (NEW)
│   ├── loaders/
│   │   ├── materials_loader.py
│   │   ├── settings_loader.py
│   │   └── contaminants_loader.py
│   │
│   └── savers/
│       ├── yaml_saver.py
│       └── frontmatter_syncer.py
│
├── config/                  # Configuration (EXISTS)
│   └── config_loader.py
│
└── utils/                   # Utilities (EXISTS)
    ├── file_utils.py
    └── text_utils.py
```

---

## 📋 Migration Plan

### Phase 1: Core Abstractions (Week 1)
**Create**: `shared/core/`
- Base classes for generators, validators, learners, processors
- Common interfaces and protocols
- Shared result types

**Files Created**:
- `shared/core/generators.py` - BaseGenerator, TextGenerator, ImageGenerator
- `shared/core/validators.py` - BaseValidator, QualityValidator
- `shared/core/learners.py` - BaseLearner, PatternLearner
- `shared/core/processors.py` - BaseProcessor, ContentProcessor

### Phase 2: Voice Consolidation (Week 1-2)
**Move**: All voice-related functionality to `shared/voice/`

**Files Moved**:
```
shared/prompts/personas/*.yaml           → shared/voice/personas/
parameters/voice/*.py                    → shared/voice/parameters/
postprocessing/detection/voice_*.py      → shared/voice/detection/
```

**Files Created**:
- `shared/voice/persona_loader.py` - Single point for loading personas
- `shared/voice/voice_renderer.py` - Render voice instructions into prompts

**Deprecated**:
- `parameters/voice/` → DELETE after migration
- `postprocessing/detection/voice_*` → DELETE after migration

### Phase 3: Learning Consolidation (Week 2)
**Move**: All learning systems to `shared/learning/`

**Files Moved**:
```
learning/*.py                           → shared/learning/
generation/learning/*.py                → shared/learning/ (if any)
```

**Benefits**:
- Single location for all learning logic
- Easier to discover learning systems
- Clear separation from generation/validation

### Phase 4: Validation Consolidation (Week 2-3)
**Move**: All validation to `shared/validation/`

**Files Moved**:
```
postprocessing/detection/*.py           → shared/validation/voice/
postprocessing/evaluation/*.py          → shared/validation/quality/
domains/*/validation/*.py               → shared/validation/content/
```

**Files Created**:
- `shared/validation/orchestrator.py` - Coordinate all validation
- `shared/validation/quality/composite_scorer.py` - Unified quality scoring

### Phase 5: Generation Consolidation (Week 3-4)
**Move**: Text generation to `shared/generation/text/`

**Files Moved**:
```
generation/core/*.py                    → shared/generation/text/
generation/config/*.py                  → shared/generation/config/
generation/enrichment/*.py              → shared/generation/text/enrichment/
```

**Benefits**:
- Parallel structure: `shared/generation/text/` and `shared/generation/image/`
- Easy to add new types: `shared/generation/video/`, `shared/generation/audio/`
- Clear ownership: ALL generation in `shared/generation/`

### Phase 6: Data Layer (Week 4)
**Create**: `shared/data/` for all data access

**Files Created**:
- `shared/data/loaders/materials_loader.py`
- `shared/data/loaders/settings_loader.py`
- `shared/data/savers/yaml_saver.py`
- `shared/data/savers/frontmatter_syncer.py`

**Files Consolidated**:
```
domains/materials/data_loader.py        → shared/data/loaders/materials_loader.py
domains/settings/data_loader.py         → shared/data/loaders/settings_loader.py
generation/utils/frontmatter_sync.py    → shared/data/savers/frontmatter_syncer.py
```

---

## 🎯 Benefits

### 1. **Clear Ownership**
```
Generation?     → shared/generation/
Validation?     → shared/validation/
Learning?       → shared/learning/
Voice?          → shared/voice/
Data access?    → shared/data/
```

### 2. **Parallel Structures**
```
shared/generation/text/     # Text generation
shared/generation/image/    # Image generation
shared/generation/video/    # Future: Video generation

shared/validation/quality/  # Quality validation
shared/validation/content/  # Content validation
shared/validation/voice/    # Voice validation
```

### 3. **Easy Discovery**
- All generation in ONE place
- All validation in ONE place
- All learning in ONE place
- All voice in ONE place

### 4. **Domain Agnostic**
- `shared/` contains reusable logic
- `domains/` contains domain-specific prompts and configs
- Clear separation of concerns

### 5. **Scalability**
- Add new generation type? → `shared/generation/[type]/`
- Add new validation type? → `shared/validation/[type]/`
- Add new learning system? → `shared/learning/[name].py`

---

## 🚦 Migration Rules

### DO:
- ✅ Move files in batches (one subsystem at a time)
- ✅ Update imports comprehensively
- ✅ Run tests after each phase
- ✅ Update documentation as you go
- ✅ Keep git history (use `git mv`)

### DON'T:
- ❌ Move everything at once (too risky)
- ❌ Skip test verification
- ❌ Leave broken imports
- ❌ Forget to update `__init__.py` files
- ❌ Leave empty directories

---

## 📊 Success Metrics

### Code Organization
- ✅ Zero top-level directories for generation/validation/learning
- ✅ All shared logic in `shared/`
- ✅ Clear parallel structure for all generation types
- ✅ Single import path for each function type

### Developer Experience
- ✅ "Where does X live?" has obvious answer
- ✅ New developers can navigate in <5 minutes
- ✅ Adding new features requires minimal structural changes
- ✅ Documentation matches code structure

### Testing
- ✅ 100% of tests passing after migration
- ✅ No increase in test complexity
- ✅ Faster test discovery (clear structure)

---

## 🗓️ Timeline

| Phase | Duration | Effort | Risk |
|-------|----------|--------|------|
| 1. Core abstractions | 1 week | Medium | Low |
| 2. Voice consolidation | 1-2 weeks | Medium | Low |
| 3. Learning consolidation | 1 week | Low | Low |
| 4. Validation consolidation | 1-2 weeks | High | Medium |
| 5. Generation consolidation | 1-2 weeks | High | Medium |
| 6. Data layer | 1 week | Medium | Low |
| **Total** | **6-9 weeks** | **High** | **Low-Medium** |

---

## 🎓 Example: Before vs After

### Before (Current)
```python
# Scattered imports
from generation.core.evaluated_generator import EvaluatedGenerator
from learning.humanness_optimizer import HumannessOptimizer
from postprocessing.detection.voice_detector import VoiceDetector
from parameters.voice.professional_voice import ProfessionalVoice
from shared.prompts.personas import load_persona
```

### After (Proposed)
```python
# Clean, organized imports
from shared.generation.text.generator import TextGenerator
from shared.learning.humanness_optimizer import HumannessOptimizer
from shared.validation.voice.detector import VoiceDetector
from shared.voice.parameters import ProfessionalVoice
from shared.voice.persona_loader import load_persona
```

---

## 🔄 Backwards Compatibility

### Option A: Deprecated Imports (Recommended)
```python
# generation/core/evaluated_generator.py (deprecated)
"""DEPRECATED: Use shared.generation.text.generator instead"""
from shared.generation.text.generator import TextGenerator as EvaluatedGenerator

import warnings
warnings.warn(
    "generation.core.evaluated_generator is deprecated. "
    "Use shared.generation.text.generator instead.",
    DeprecationWarning,
    stacklevel=2
)
```

### Option B: Hard Cutover
- Update all imports in one PR
- Run comprehensive test suite
- Deploy with confidence

**Recommendation**: Use Option A for 2-4 weeks, then remove deprecated imports.

---

## 🚀 Next Steps

1. **Approval**: Get stakeholder approval on proposed structure
2. **Phase 1 Pilot**: Implement core abstractions (low risk)
3. **Voice Migration**: Complete voice consolidation (validates approach)
4. **Full Migration**: Execute phases 3-6
5. **Cleanup**: Remove deprecated imports and empty directories
6. **Documentation**: Update all docs to reflect new structure

---

## 📚 Related Documents

- **Voice Policy**: `VOICE_INSTRUCTION_CENTRALIZATION_POLICY.md`
- **Current Architecture**: `docs/02-architecture/`
- **Migration Issues**: Track in GitHub issues with `architecture` label

---

**Status**: PROPOSAL - Awaiting approval  
**Champion**: AI Assistant  
**Reviewers**: Project maintainers
