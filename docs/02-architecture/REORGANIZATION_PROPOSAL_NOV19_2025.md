# System Reorganization Proposal - November 19, 2025

## 🎯 Executive Summary

**Problem**: Directory structure and naming don't reflect the system's evolution from post-processor to primary content generator with distinct sequential stages.

**Solution**: Reorganize into three distinct stages that match our successful workflow from November 18, 2025:
1. **Generation Stage** - Content creation with DeepSeek API
2. **Learning Stage** - Parameter adaptation from feedback
3. **Post-Processing Stage** - Quality evaluation and export

**Impact**: Improved clarity, maintainability, and alignment with actual system architecture.

---

## 📊 Current vs. Proposed Architecture

### Current Reality (What Actually Happens)

```
Stage 1: GENERATION (processing/generator.py → DeepSeek API)
  ├─ Load prompts from prompts/*.txt
  ├─ Calculate parameters from config.yaml sliders
  ├─ Enrich with real facts
  ├─ Build unified prompt
  ├─ Generate content via DeepSeek
  ├─ Validate (subjective language only in simple_mode)
  └─ Save to Materials.yaml

Stage 2: LEARNING (processing/learning/*.py - DISABLED in simple_mode)
  ├─ Pattern learning from successful content
  ├─ Temperature adaptation
  ├─ Realism optimization
  └─ Fix management

Stage 3: POST-PROCESSING (processing/evaluation/*.py)
  ├─ Claude/Grok subjective evaluation
  ├─ Quality scoring (6.0-9.0/10)
  ├─ Winston detection (optional, skipped in simple_mode)
  └─ Realism scoring (optional, skipped in simple_mode)

Stage 4: EXPORT (components/frontmatter/)
  └─ Trivial YAML→YAML field mapping to frontmatter files
```

### Proposed Stage-Based Organization

```
z-beam-generator/
├── generation/                    # STAGE 1: Content Generation
│   ├── core/
│   │   ├── generator.py          # Main content generator (DynamicGenerator)
│   │   ├── prompt_builder.py     # Builds prompts from templates
│   │   └── api_adapter.py        # API call wrapper
│   ├── enrichment/
│   │   └── data_enricher.py      # Real fact injection
│   ├── validation/
│   │   └── subjective/           # Inline subjective language check
│   └── config/
│       ├── config.yaml           # User-facing sliders
│       └── dynamic_config.py     # Parameter calculation
│
├── learning/                      # STAGE 2: Parameter Learning
│   ├── pattern_learner.py        # Learn from successful patterns
│   ├── temperature_advisor.py    # Temperature adaptation
│   ├── realism_optimizer.py      # Realism score optimization
│   ├── fix_manager.py            # Fix suggestions
│   └── learned_patterns.yaml     # Persistent learned data
│
├── postprocessing/                # STAGE 3: Quality Evaluation
│   ├── evaluation/
│   │   ├── evaluator.py          # Claude/Grok quality scoring
│   │   └── templates/
│   │       └── subjective_quality.txt
│   ├── detection/
│   │   ├── winston/              # Winston AI detection (optional)
│   │   └── realism/              # Realism scoring (optional)
│   └── reports/
│       └── report_generator.py
│
├── export/                        # STAGE 4: Output Generation
│   ├── exporter.py               # Trivial YAML→YAML mapping
│   ├── formatters/
│   └── validators/
│
├── domains/                       # Domain Coordinators
│   ├── materials/
│   │   ├── coordinator.py        # Wraps generation for materials
│   │   ├── prompts/              # 🔥 Domain-specific prompt templates
│   │   │   ├── caption.txt       # Materials caption prompt (starting point)
│   │   │   ├── subtitle.txt      # Materials subtitle prompt
│   │   │   ├── faq.txt           # Materials FAQ prompt
│   │   │   └── personas/         # Author personas for materials
│   │   ├── research/             # Property research
│   │   └── schema.py
│   ├── contaminants/
│   │   ├── coordinator.py
│   │   ├── prompts/              # Contaminants-specific prompts
│   │   └── schema.json
│   ├── regions/
│   │   ├── coordinator.py
│   │   ├── prompts/              # Regions-specific prompts
│   │   └── schema.json
│   ├── applications/
│   │   ├── coordinator.py
│   │   ├── prompts/              # Applications-specific prompts
│   │   └── schema.json
│   └── thesaurus/
│       ├── coordinator.py
│       ├── prompts/              # Thesaurus-specific prompts
│       └── schema.json
│
├── data/                          # Data Storage
│   ├── materials/
│   │   └── Materials.yaml        # Single source of truth
│   └── [other domains]/
│
├── shared/                        # Shared Utilities
│   ├── commands/
│   ├── api/
│   └── config/
│
└── [scripts, tests, docs, etc.]
```

---

## 🔄 Detailed Migration Plan

### Phase 1: Stage Separation (Low Risk)

**Goal**: Separate generation, learning, and post-processing into distinct directories.

#### 1.1 Create New Stage Directories

```bash
# Create stage directories
mkdir -p generation/core
mkdir -p generation/enrichment
mkdir -p generation/validation/subjective
mkdir -p generation/config

mkdir -p learning

mkdir -p postprocessing/evaluation/templates
mkdir -p postprocessing/detection/winston
mkdir -p postprocessing/detection/realism
mkdir -p postprocessing/reports

mkdir -p export
```

#### 1.2 Move Generation Components

```bash
# GENERATION STAGE
mv processing/generator.py generation/core/generator.py
mv processing/generation/prompt_builder.py generation/core/prompt_builder.py
mv processing/adapters/ generation/core/adapters/
mv processing/enrichment/ generation/enrichment/
mv processing/validation/subjective/ generation/validation/subjective/
mv processing/config/ generation/config/

# Keep validation/readability in generation (inline validation)
mv processing/validation/readability/ generation/validation/readability/
```

#### 1.3 Move Learning Components

```bash
# LEARNING STAGE (currently in processing/learning/)
mv processing/learning/* learning/

# Move learned patterns from prompts to learning
mv prompts/evaluation/learned_patterns.yaml learning/learned_patterns.yaml
```

#### 1.4 Move Post-Processing Components

```bash
# POST-PROCESSING STAGE
mv processing/evaluation/ postprocessing/evaluation/
mv processing/detection/ postprocessing/detection/
mv processing/subjective/evaluator.py postprocessing/evaluation/subjective_evaluator.py
mv processing/reports/ postprocessing/reports/

# Move evaluation templates
mv prompts/evaluation/ postprocessing/evaluation/templates/
```

#### 1.5 Move Export Components

```bash
# EXPORT STAGE (formerly components/frontmatter/)
mv components/frontmatter/* export/
rmdir components/frontmatter
rmdir components  # If empty

# Rename main exporter
mv export/core/trivial_exporter.py export/core/exporter.py
```

#### 1.6 Move Prompts to Domains

```bash
# CRITICAL: Prompts are domain-specific starting points
# Move prompts into each domain directory

# Materials domain prompts
mkdir -p domains/materials/prompts/
mv prompts/components/caption.txt domains/materials/prompts/caption.txt
mv prompts/components/subtitle.txt domains/materials/prompts/subtitle.txt
mv prompts/components/faq.txt domains/materials/prompts/faq.txt
mv prompts/personas/ domains/materials/prompts/personas/

# Create prompt directories for other domains
mkdir -p domains/contaminants/prompts/
mkdir -p domains/regions/prompts/
mkdir -p domains/applications/prompts/
mkdir -p domains/thesaurus/prompts/

# Note: Other domains may share materials prompts initially
# or create domain-specific variants as needed
```

#### 1.7 Archive Deprecated Files

```bash
# Create archive for deprecated code
mkdir -p generation/archive/

# Archive orchestrator (not used in production)
mv processing/orchestrator.py generation/archive/orchestrator_deprecated.py

# Remove now-empty directories
rmdir prompts/components/
rmdir prompts/
rmdir processing/
```

---

### Phase 2: Domain Consolidation (Medium Risk)

**Goal**: Group all domain coordinators under `domains/` with their domain-specific prompts.

```bash
# Create domains directory
mkdir -p domains/

# Move domain directories
mv materials/ domains/materials/
mv contaminants/ domains/contaminants/
mv regions/ domains/regions/
mv applications/ domains/applications/
mv thesaurus/ domains/thesaurus/

# Rename domain coordinators for clarity
mv domains/materials/unified_generator.py domains/materials/coordinator.py
# (Add similar renames for other domains if they have similar files)

# Move prompts INTO domains (prompts are domain-specific starting points)
mkdir -p domains/materials/prompts/
mv prompts/components/*.txt domains/materials/prompts/
mv prompts/personas/ domains/materials/prompts/personas/
mv prompts/evaluation/ postprocessing/evaluation/templates/

# Remove empty prompts directory
rmdir prompts/components/ prompts/ 2>/dev/null || true
```

---

### Phase 3: Import Path Updates (High Risk - Requires Testing)

**Goal**: Update all import statements to reflect new structure.

#### 3.1 Generation Stage Imports

**Before**:
```python
from processing.generator import DynamicGenerator
from processing.generation.prompt_builder import PromptBuilder
from processing.config.dynamic_config import DynamicConfig
from processing.enrichment.data_enricher import DataEnricher
```

**After**:
```python
from generation.core.generator import DynamicGenerator
from generation.core.prompt_builder import PromptBuilder
from generation.config.dynamic_config import DynamicConfig
from generation.enrichment.data_enricher import DataEnricher
```

#### 3.2 Learning Stage Imports

**Before**:
```python
from processing.learning.pattern_learner import PatternLearner
from processing.learning.temperature_advisor import TemperatureAdvisor
from processing.learning.realism_optimizer import RealismOptimizer
```

**After**:
```python
from learning.pattern_learner import PatternLearner
from learning.temperature_advisor import TemperatureAdvisor
from learning.realism_optimizer import RealismOptimizer
```

#### 3.3 Post-Processing Stage Imports

**Before**:
```python
from processing.subjective.evaluator import SubjectiveEvaluator
from processing.detection.ensemble import AIDetectorEnsemble
from processing.evaluation.evaluator import Evaluator
```

**After**:
```python
from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator
from postprocessing.detection.winston.ensemble import AIDetectorEnsemble
from postprocessing.evaluation.evaluator import Evaluator
```

#### 3.4 Domain Coordinator Imports

**Before**:
```python
from materials.unified_generator import UnifiedMaterialsGenerator
```

**After**:
```python
from domains.materials.coordinator import MaterialsCoordinator
```

#### 3.5 Export Stage Imports

**Before**:
```python
from components.frontmatter.core.trivial_exporter import TrivialExporter
```

**After**:
```python
from export.core.exporter import Exporter
```

---

### Phase 4: Files Requiring Import Updates

#### Critical Files (Must Update):

1. **`run.py`** - Main entry point
   - Import DynamicGenerator from generation.core
   - Import MaterialsCoordinator from domains.materials

2. **`shared/commands/generation.py`** - Command handlers
   - Import MaterialsCoordinator from domains.materials
   - Import DynamicGenerator from generation.core

3. **`generation/core/generator.py`** - Main generator
   - Update internal imports for enrichment, validation, config
   - Update learning imports (if not using simple_mode)
   - Update post-processing imports

4. **`domains/materials/coordinator.py`** - Materials wrapper
   - Import DynamicGenerator from generation.core

5. **`tests/*.py`** - All test files
   - Update all import paths to match new structure

#### Search Commands for Finding Import References:

```bash
# Find all imports from processing/
grep -r "from processing" --include="*.py" .

# Find all imports from materials.unified_generator
grep -r "from materials.unified_generator" --include="*.py" .

# Find all imports from components.frontmatter
grep -r "from components.frontmatter" --include="*.py" .
```

---

## 📋 Testing Checklist

### Before Migration:
- [ ] Run full test suite: `pytest tests/`
- [ ] Generate test caption: `python3 run.py --caption "Aluminum"`
- [ ] Verify Materials.yaml output
- [ ] Check batch generation still works

### After Phase 1 (Stage Separation):
- [ ] Update imports in critical files
- [ ] Run full test suite: `pytest tests/`
- [ ] Generate test caption: `python3 run.py --caption "Aluminum"`
- [ ] Verify same output as before

### After Phase 2 (Domain Consolidation):
- [ ] Update domain imports
- [ ] Run full test suite
- [ ] Test caption, subtitle, FAQ generation

### After Phase 3 (All Import Updates):
- [ ] Run full test suite (all tests passing)
- [ ] Batch generate 5 materials as smoke test
- [ ] Verify post-processing evaluation works
- [ ] Check export to frontmatter works

---

## 🎯 Success Criteria

1. **All 132 materials regenerate successfully** with same quality
2. **All tests pass** (currently 17/17 passing)
3. **Simple mode works** (generation → save → evaluate)
4. **Learning mode works** (when enabled)
5. **Export generates valid frontmatter** files
6. **Documentation updated** to reflect new structure

---

## 📝 Naming Rationale

### Why `generation/` instead of `processing/`?

**Current Reality**: This code makes API calls, builds prompts, controls all parameters, and generates content from scratch. It IS the generator, not a post-processor.

**Evidence**:
- All 132 materials generated through processing/generator.py
- Makes primary API calls to DeepSeek
- No separate generator feeding this system
- "Post-processing" implies processing after generation, but this IS generation

**Conclusion**: Name should reflect function. This is generation.

### Why separate `learning/` from `generation/`?

**Sequential Stages**: Our successful workflow (Nov 18, 2025) demonstrated:
1. **Generate** content (fast, no learning blocking)
2. **Evaluate** quality (post-save)
3. **Learn** from feedback (update parameters for next run)

**Benefits**:
- Clear stage boundaries
- Learning doesn't block generation
- Simple mode can skip learning entirely
- Advanced mode can enable learning separately

### Why `postprocessing/` for evaluation?

**Timing**: Evaluation happens AFTER generation completes and saves to Materials.yaml.

**Components**:
- Claude/Grok subjective scoring
- Winston AI detection (optional)
- Realism scoring (optional)
- Quality reports

**Not Generation**: These don't create content, they assess it.

### Why `domains/` for coordinators?

**Purpose**: Materials, contaminants, regions are domain-specific wrappers around the universal generation engine.

**Structure**:
- Each domain has specific schemas
- Each domain has **domain-specific prompts** (starting point for generation)
- Each domain has specific research needs
- Each coordinates generation for its domain
- All use same generation/learning/postprocessing pipeline

**Benefits**: 
- Clear separation between domain logic and generation logic
- **Prompts live with their domain** - easier to customize per domain
- Self-contained domain modules - all domain-specific content in one place
- Makes it obvious that prompts are the **starting point** for each domain's content

**Key Insight**: Prompts are NOT universal templates - they're domain-specific content strategies. A materials caption requires different content focus than a contaminants caption or regions caption.

### Why `export/` instead of `components/frontmatter/`?

**Function**: This code doesn't generate or process. It performs trivial YAML→YAML field mapping.

**Characteristics**:
- Should take seconds for 132 materials
- No API calls, no validation
- Pure data transformation
- Output files, not components

**Accuracy**: "Export" describes what it does.

---

## 🔧 Configuration Updates

### `generation/config/config.yaml`

Remains largely unchanged, but add stage configuration and prompt path resolution:

```yaml
# Stage Control
stages:
  generation:
    enabled: true
  learning:
    enabled: false  # Disabled in simple_mode
  postprocessing:
    enabled: true
    winston_detection: false  # Skip in simple_mode
    realism_scoring: false    # Skip in simple_mode
    claude_evaluation: true   # Always run
  export:
    enabled: true

# Simple Mode (disables learning, skips optional post-processing)
simple_mode:
  enabled: true

# Prompt Resolution (NEW)
prompts:
  # Prompts now live in domain directories
  # Generator loads from: domains/{domain}/prompts/{component_type}.txt
  materials:
    path: "domains/materials/prompts"
  contaminants:
    path: "domains/contaminants/prompts"
  regions:
    path: "domains/regions/prompts"
  applications:
    path: "domains/applications/prompts"
  thesaurus:
    path: "domains/thesaurus/prompts"
```

---

## 📚 Documentation Updates Required

### 1. Architecture Documentation

- **`docs/02-architecture/SYSTEM_ARCHITECTURE.md`**
  - Update to reflect three-stage architecture
  - Add stage flow diagram
  - Explain simple_mode vs learning_mode

- **`docs/02-architecture/PROCESSING_PIPELINE.md`** → **`GENERATION_PIPELINE.md`**
  - Rename file to match new terminology
  - Update all diagrams and flows
  - Add stage separation details

- **NEW: `docs/02-architecture/STAGE_ARCHITECTURE.md`**
  - Detailed explanation of three stages
  - When each stage runs
  - How stages communicate
  - Simple vs learning modes

### 2. Developer Documentation

- **`.github/copilot-instructions.md`**
  - Update all path references
  - Update import examples
  - Clarify stage responsibilities

- **`docs/08-development/`**
  - Update code examples with new imports
  - Update architecture decision records
  - Add migration guide reference

### 3. API/Reference Documentation

- **`docs/09-reference/`**
  - Update API references with new paths
  - Update class hierarchies
  - Update import patterns

### 4. Quick Start & README

- **`README.md`**
  - Update architecture overview
  - Update directory structure
  - Update getting started imports

- **`QUICK_START.md`**
  - Update command examples
  - Update troubleshooting paths
  - Update file locations

---

## ⚠️ Risks & Mitigation

### Risk 1: Broken Imports

**Mitigation**:
- Create migration script to update imports automatically
- Test after each phase
- Keep git history clean for easy rollback

### Risk 2: Forgotten References

**Mitigation**:
- Use grep to find all import statements
- Search for hardcoded path strings
- Check configuration files

### Risk 3: Test Failures

**Mitigation**:
- Run tests before migration (baseline)
- Run tests after each phase
- Fix incrementally, don't batch

### Risk 4: Production Downtime

**Mitigation**:
- Perform migration in development branch
- Full testing before merge to main
- Keep backup of working state

---

## 🚀 Implementation Timeline

### Phase 1: Stage Separation (2-3 hours)
- Day 1 Morning: Create directories, move files
- Day 1 Afternoon: Update critical imports, test

### Phase 2: Domain Consolidation (1 hour)
- Day 1 Evening: Move domains, update imports, test

### Phase 3: Complete Import Updates (2-3 hours)
- Day 2 Morning: Find all imports with grep
- Day 2 Afternoon: Update systematically, test continuously

### Phase 4: Documentation (2-3 hours)
- Day 2 Evening: Update all documentation
- Day 3: Final review and validation

**Total Estimated Time: 8-10 hours over 2-3 days**

---

## 📊 Rollback Plan

If migration fails:

```bash
# Rollback to previous commit
git reset --hard HEAD~1

# Or restore specific files
git checkout HEAD~1 -- processing/
git checkout HEAD~1 -- materials/
git checkout HEAD~1 -- components/frontmatter/
```

Keep working commit hash: `[RECORD BEFORE STARTING]`

---

## ✅ Migration Script Template

```bash
#!/bin/bash
# migrate_to_stages.sh - Automated migration script

set -e  # Exit on error

echo "🚀 Starting Stage-Based Reorganization..."

# Phase 1: Create new directories
echo "📁 Creating stage directories..."
mkdir -p generation/core generation/enrichment generation/validation/subjective generation/config
mkdir -p learning
mkdir -p postprocessing/evaluation/templates postprocessing/detection/winston postprocessing/detection/realism postprocessing/reports
mkdir -p export
mkdir -p domains

# Phase 2: Move generation files
echo "🔄 Moving generation components..."
mv processing/generator.py generation/core/generator.py
mv processing/generation/prompt_builder.py generation/core/prompt_builder.py
# ... [add all mv commands]

# Phase 3: Update imports in critical files
echo "📝 Updating imports in run.py..."
sed -i '' 's/from processing.generator/from generation.core.generator/g' run.py
# ... [add all sed commands]

# Phase 4: Run tests
echo "🧪 Running test suite..."
pytest tests/ -v

echo "✅ Migration complete! Verify manually before committing."
```

---

## 🎯 Next Steps

1. **Review this proposal** - Confirm alignment with vision
2. **Test current state** - Establish baseline (all tests passing, 132 captions generated)
3. **Execute Phase 1** - Stage separation + Move prompts to domains
4. **Validate Phase 1** - Run tests, generate test content
5. **Execute Phase 2** - Domain consolidation
6. **Execute Phase 3** - Import updates (including prompt path resolution)
7. **Update documentation** - Reflect new architecture
8. **Final validation** - Full system test

## 🔑 Key Architectural Insight

**Prompts are the starting point for each domain's content generation.**

- Materials domain: `domains/materials/prompts/caption.txt` describes how to write materials captions
- Contaminants domain: `domains/contaminants/prompts/caption.txt` describes how to write contaminant captions
- Each domain owns its content strategy from the start

This makes the system truly domain-agnostic at the generation layer while maintaining domain specificity at the prompt layer.

---

## 📞 Questions for Decision

1. **Naming**: Agree with `generation/`, `learning/`, `postprocessing/`, `export/`, `domains/`?
2. **Prompt Location**: Confirm prompts belong in `domains/{domain}/prompts/` as domain-specific starting points?
3. **Timing**: Execute all at once or phase-by-phase with testing?
4. **Documentation**: Update docs before or after code migration?
5. **Rollback**: Keep old structure in parallel temporarily?
6. **Tests**: Update test imports during migration or after?
7. **Other Domains**: Should contaminants/regions/applications initially share materials prompts or create their own immediately?

---

**Document Version**: 1.0  
**Date**: November 19, 2025  
**Status**: PROPOSAL - Awaiting Approval  
**Author**: GitHub Copilot (Claude Sonnet 4.5)
