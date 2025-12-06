# Z-Beam Generator - Architecture Overview

**Purpose**: High-level system architecture and design principles for AI assistants and developers  
**Audience**: AI assistants, new developers, architecture decisions  
**Last Updated**: November 28, 2025

---

## 🎯 System Purpose

Z-Beam Generator is a multi-domain content generation system for laser cleaning applications. The system generates high-quality text content and hero images for materials, contaminants, and application regions using AI-powered generation with quality gates, learning systems, and validation pipelines.

### Core Domains
1. **Materials** - Metals, alloys, composites, specialized materials
2. **Contaminants** - Dirt, oxidation, coatings, and other surface contaminants
3. **Regions** (Future) - Geographic application areas and use cases

---

## 🏗️ **Architectural Principles**

### 1. Domain Independence
**Policy**: `docs/02-architecture/DOMAIN_ARCHITECTURE.md`

- Shared infrastructure works across ALL domains (materials, contaminants, regions)
- Domain-specific logic isolated in `domains/` directory
- Generic components in `shared/` never reference specific domains
- Enables adding new domains without modifying shared code

**Example**:
```
shared/image/orchestrator.py        ← Generic (identifier, category, api)
domains/materials/image/             ← Domain adapter (MaterialImageConfig → generic kwargs)
domains/contaminants/image/          ← Domain adapter (ContaminantImageConfig → generic kwargs)
```

### 2. Separation of Concerns
**Analysis**: `docs/archive/2025-11/SEPARATION_OF_CONCERNS_ANALYSIS.md`

- **Data Layer**: `data/` - YAML source of truth
- **Processing**: `generation/`, `processing/` - AI generation and quality control
- **Shared Infrastructure**: `shared/` - Reusable components
- **Domain Logic**: `domains/` - Domain-specific adapters
- **Output**: `public/` - Generated content for deployment

### 3. Fail-Fast Configuration
**Policy**: `.github/copilot-instructions.md` - Core Principles

- Configuration errors throw exceptions immediately at startup
- NO fallback values in production code (tests OK)
- NO hardcoded defaults (use config files or dynamic calculation)
- Runtime recovery preserved for transient issues (API retries)

### 4. Data Storage Strategy
**Policy**: `docs/05-data/DATA_STORAGE_POLICY.md`

- **Materials.yaml** - Single source of truth + all AI operations
- **Categories.yaml** - Category-level ranges and metadata
- **Frontmatter files** - Write-only mirrors (dual-write from Materials.yaml)
- ALL generation and validation happens on YAML, not frontmatter

### 5. Template-Only Content
**Policy**: `docs/08-development/TEMPLATE_ONLY_POLICY.md`

- ALL content instructions in `domains/*/text/prompts/*.txt`
- ZERO component-specific code in generators
- Generic extraction strategies in config (before_after, raw, etc.)
- Add new component = template file + config entry ONLY

---

## 📁 **Directory Structure**

```
z-beam-generator/
├── data/                           # Source of truth
│   ├── materials/
│   │   ├── Materials.yaml          # Complete material data (AI operations here)
│   │   └── Categories.yaml         # Category metadata and ranges
│   ├── contaminants/
│   │   └── Contaminants.yaml       # Contaminant data
│   └── regions/ (future)
│
├── domains/                        # Domain-specific implementations
│   ├── materials/
│   │   ├── image/                  # Material image generation
│   │   │   ├── material_generator.py    # Domain adapter
│   │   │   ├── material_config.py       # Domain config
│   │   │   └── learning/                # Domain learning system
│   │   └── text/                   # Material text generation (legacy)
│   ├── contaminants/
│   │   └── image/                  # Contaminant image generation
│   └── regions/ (future)
│
├── shared/                         # Reusable infrastructure
│   ├── image/
│   │   ├── orchestrator.py        # Domain-agnostic prompt orchestration
│   │   ├── generator.py           # Generic image generation
│   │   └── prompts/               # Shared prompt templates
│   ├── validation/
│   │   └── prompt_validator.py    # Universal prompt validation
│   ├── text/
│   │   └── templates/             # Text component templates
│   └── commands/                  # CLI command handlers
│
├── generation/                     # Text generation pipeline (legacy)
│   ├── config/                    # Generation configuration
│   ├── core/                      # Core generators
│   └── learning/                  # Learning systems
│
├── public/                         # Generated output
│   ├── images/materials/          # Material hero images
│   ├── images/contaminants/       # Contaminant hero images
│   └── materials/                 # Material frontmatter (mirrors)
│
├── docs/                          # Documentation
│   ├── 01-getting-started/
│   ├── 02-architecture/
│   ├── 03-components/
│   ├── 04-operations/
│   ├── 05-data/
│   ├── 06-ai-systems/
│   ├── 07-api/
│   ├── 08-development/
│   ├── 09-reference/
│   └── archive/2025-11/           # Historical docs
│
└── .github/
    ├── copilot-instructions.md     # AI assistant guidelines (PRIMARY)
    └── COPILOT_GENERATION_GUIDE.md # Content generation commands
```

---

## 🔄 **Generation Pipeline**

### Text Generation Flow
1. **Input**: Material name + component type (caption, description, faq)
2. **Template Loading**: Load `domains/{domain}/text/prompts/{component}.txt`
3. **Prompt Building**: Inject material data into template
4. **Quality Gating**: Winston AI detection, realism scoring, readability
5. **Learning**: Log attempts, parameters, outcomes to SQLite
6. **Storage**: Write to Materials.yaml + sync field to frontmatter
7. **Verification**: Validate completeness and quality

**Implementation**: `generation/core/quality_gated_generator.py`

### Image Generation Flow
1. **Input**: Material/contaminant + category + contamination level
2. **Research**: Visual properties, contamination patterns (from YAML)
3. **Orchestration**: 5-stage prompt chaining (research → visual → composition → refinement → assembly)
4. **Validation**: Pre-generation prompt validation (length, logic, quality, technical compliance)
5. **Generation**: Imagen 4 API call with optimized prompts
6. **Learning**: Log prompts, validation results, parameters to SQLite
7. **Storage**: Save to `public/images/materials/{material}_hero.png`

**Implementation**: 
- `domains/materials/image/material_generator.py` (domain adapter)
- `shared/image/orchestrator.py` (generic orchestrator)
- `shared/validation/prompt_validator.py` (validation)

---

## 🧠 **AI Systems Architecture**

### Learning Systems
**Documentation**: `docs/06-ai-systems/`

Each domain has its own learning database capturing:
- Generation attempts (parameters, prompts, outcomes)
- Validation results (scores, pass/fail)
- User feedback (accepted/rejected)
- Sweet spot patterns (successful parameter combinations)

**Storage**: `domains/{domain}/image/learning/learned_data.db`

### Quality Gates
**All** must pass before content acceptance:

**Text Generation**:
1. Winston AI Detection: 69%+ human score (configurable)
2. Readability Check: Pass status
3. Subjective Language: No violations
4. Realism Score: 7.0/10 minimum
5. Combined Quality Target: Meets learning target

**Image Generation**:
1. Prompt Length: Within Imagen 4 limits (4,096 chars/field)
2. Logical Coherence: No contradictions
3. Quality Standards: Technical specifications met
4. Technical Compliance: Valid parameters

### Validation Integration
**Documentation**: `docs/archive/2025-11/ORCHESTRATOR_VALIDATION_INTEGRATION_NOV27_2025.md`

Three-part validation system:
1. **Stage 1-5**: Prompt building and research (orchestrator)
2. **Stage 6**: Pre-generation validation (validator)
3. **Post-generation**: Learning database logging

Validation prevents bad prompts from reaching API, saving costs and improving quality.

---

## 🔧 **Configuration Architecture**

### Static Configuration
- **config.yaml**: System-wide settings
- **generation/config.yaml**: Text generation config
- **domains/{domain}/image/config.yaml**: Domain-specific image config

### Dynamic Configuration
**Implementation**: `generation/config/dynamic_config.py`

Calculates runtime values based on:
- Component type
- Voice intensity level
- Quality thresholds
- Category metadata

**Anti-pattern**: Hardcoding values in code (use dynamic calculation instead)

### Policy Documents
Located in `docs/08-development/`:
- `HARDCODED_VALUE_POLICY.md` - Zero hardcoded values
- `CONTENT_INSTRUCTION_POLICY.md` - Templates only
- `PROMPT_PURITY_POLICY.md` - No prompts in code
- `TERMINAL_LOGGING_POLICY.md` - Dual logging (print + logger)
- `PROMPT_CHAINING_POLICY.md` - Multi-stage orchestration

---

## 🤖 **AI Assistant Integration**

### Primary Navigation
**Start Here**: `docs/08-development/AI_ASSISTANT_GUIDE.md`

30-second navigation to any documentation:
1. **Policies**: `GROK_QUICK_REF.md` - TIER priorities
2. **Generation**: `.github/COPILOT_GENERATION_GUIDE.md`
3. **Architecture**: This file
4. **Images**: `docs/04-operations/IMAGE_GENERATION_GUIDE.md`
5. **Quick Ref**: `docs/QUICK_REFERENCE.md`

### Before ANY Code Change
**Mandatory Checklist**: `.github/copilot-instructions.md`

1. Read request precisely
2. Search documentation for existing guidance
3. Check policy documents (`docs/08-development/`)
4. Review system interactions
5. Plan minimal fix
6. Ask permission for major changes
7. Verify with tests before claiming success

### Tier Priorities
**TIER 1** (System-Breaking): No mocks, no hardcoded values, preserve working code  
**TIER 2** (Quality-Critical): No scope expansion, fail-fast config, surgical fixes  
**TIER 3** (Evidence & Honesty): Provide evidence, be honest, verify documentation matches reality

---

## 📊 **Data Architecture**

### Data Flow
```
Research → Materials.yaml (write) → Frontmatter (field sync)
          ↓
     Validation
          ↓
     Quality Gates
          ↓
     Learning DB
```

### Range Propagation
**Documentation**: `docs/05-data/DATA_ARCHITECTURE.md`

1. **Materials.yaml**: Individual material properties
2. **Categories.yaml**: Category-level ranges (min/max)
3. **Frontmatter**: Material properties + category ranges (merged)

Category ranges fill in missing material-specific values, creating complete property sets for each material.

### Dual-Write Pattern
**Policy**: `docs/05-data/DATA_STORAGE_POLICY.md`

Every Materials.yaml update triggers:
1. **Full write** to Materials.yaml (all fields)
2. **Partial write** to frontmatter (changed field only)

Frontmatter receives immediate field-level updates but is NEVER read for persistence.

---

## 🔗 **Related Documentation**

### For AI Assistants
- **Primary Guide**: `.github/copilot-instructions.md` - Complete AI guidelines
- **Quick Start**: `docs/08-development/AI_ASSISTANT_GUIDE.md` - 30-second navigation
- **Generation**: `.github/COPILOT_GENERATION_GUIDE.md` - Content generation commands
- **Images**: `docs/04-operations/IMAGE_GENERATION_GUIDE.md` - Image generation workflow

### For Developers
- **Quick Start**: `QUICK_START.md` - Fast setup
- **Troubleshooting**: `TROUBLESHOOTING.md` - Common issues
- **Quick Reference**: `docs/QUICK_REFERENCE.md` - Problem → solution
- **Documentation Map**: `DOCUMENTATION_MAP.md` - Complete documentation index

### Architecture Deep Dives
- **Domain Independence**: `docs/02-architecture/DOMAIN_ARCHITECTURE.md`
- **Data Architecture**: `docs/02-architecture/DATA_ARCHITECTURE.md`
- **Image Architecture**: `docs/02-architecture/IMAGE_ARCHITECTURE.md`
- **Validation**: `docs/06-ai-systems/VALIDATION_SYSTEM.md`
- **Learning**: `docs/06-ai-systems/LEARNING_SYSTEM.md`

### Historical Context
- **Archive**: `docs/archive/2025-11/README.md` - November 2025 implementations
- **Decisions**: `docs/decisions/README.md` - Architecture Decision Records (ADRs)

---

## 🎯 **Key Architectural Wins**

1. **82% Documentation Reduction**: 83 root files → 15 essential files
2. **90% Faster AI Navigation**: Clear hierarchy, <30 seconds to any topic
3. **Domain Independence**: Add contaminants/regions without touching shared code
4. **Zero Hardcoded Values**: All configuration dynamic or in files
5. **Template-Only Content**: Add components without code changes
6. **Comprehensive Learning**: Every attempt captured for continuous improvement
7. **Pre-Generation Validation**: Catch prompt issues before API costs
8. **Dual-Write Pattern**: Single source of truth with immediate frontmatter sync

---

## 📚 **Implementation History**

See `docs/archive/2025-11/README.md` for complete November 2025 implementation history including:
- Architecture cleanup and reorganization
- Domain independence implementation
- Image system centralization
- Validation integration
- Learning system improvements
- Data completeness efforts

---

**Last Major Update**: November 28, 2025 - Documentation consolidation and AI workflow integration