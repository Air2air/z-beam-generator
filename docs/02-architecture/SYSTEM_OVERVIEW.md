# Z-Beam Generator: System Overview

**Purpose**: Complete high-level system architecture for AI assistants and developers  
**Audience**: AI assistants, new developers, architecture decisions  
**Last Updated**: December 20, 2025  
**Status**: Consolidated from 5 architecture overview documents

---

## 🎯 System Purpose

Z-Beam Generator is a **multi-domain content generation system** for laser cleaning applications. The system generates high-quality text content and hero images for materials, contaminants, and application regions using AI-powered generation with quality gates, learning systems, and validation pipelines.

### Core Domains
1. **Materials** - Metals, alloys, composites, specialized materials (121 materials, 9 categories)
2. **Contaminants** - Dirt, oxidation, coatings, and other surface contaminants (100+ patterns)
3. **Regions** (Future) - Geographic application areas and use cases

### System Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    Z-Beam Generator                          │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   CLI Entry  │  │   Pipeline   │  │  Components  │      │
│  │    run.py    │→ │ Integration  │→ │  Generators  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                 ↓                  ↓               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Configuration│  │   Data Layer │  │  API Clients │      │
│  │  Validation  │  │ Materials.yml│  │ DeepSeek/etc │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  Output: ../z-beam/frontmatter/ (422 YAML files)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Core Architectural Principles

### 1. Domain Independence
**Policy**: `DOMAIN_INDEPENDENCE_POLICY.md`

- **Shared infrastructure works across ALL domains** (materials, contaminants, regions)
- **Domain-specific logic isolated** in `domains/` directory
- **Generic components** in `shared/` never reference specific domains
- **Enables adding new domains** without modifying shared code

**Example**:
```
shared/image/orchestrator.py        ← Generic (identifier, category, api)
domains/materials/image/             ← Domain adapter (MaterialImageConfig → generic kwargs)
domains/contaminants/image/          ← Domain adapter (ContaminantImageConfig → generic kwargs)
```

### 2. Separation of Concerns
**Analysis**: `docs/guides/ARCHITECTURE_PRINCIPLES.md`

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: DATA (Single Source of Truth)                      │
│ • data/materials/Materials.yaml                              │
│ • data/contaminants/Contaminants.yaml                        │
│ • data/associations/DomainAssociations.yaml                  │
│ • data/settings/Settings.yaml, data/compounds/Compounds.yaml │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: PROCESSING (Transformation Logic)                  │
│ • export/core/frontmatter_exporter.py (orchestration)          │
│ • export/config/*.yaml (domain configurations)               │
│ • export/enrichers/**/*.py (enrichment logic)                │
│ • generation/core/evaluated_generator.py (text generation)   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: OUTPUT (Generated Content)                         │
│ • ../z-beam/frontmatter/materials/*.yaml (422 files)         │
│ • ../z-beam/frontmatter/contaminants/*.yaml                  │
│ • ../z-beam/frontmatter/compounds/*.yaml                     │
└─────────────────────────────────────────────────────────────┘
```

**Critical Rule**: NEVER edit Layer 3 files directly - fix Layer 1 (data) or Layer 2 (generators), then regenerate.

### 3. Fail-Fast Configuration
**Policy**: `.github/copilot-instructions.md` - Core Principles

- **Configuration errors throw exceptions immediately** at startup
- **NO fallback values** in production code (tests OK)
- **NO mock APIs** in production paths (tests OK)
- **Explicit dependencies** - all required components must be provided

**Philosophy**: "Fail fast on setup, maintain runtime error recovery"

```python
# ✅ CORRECT: Fail-fast configuration
if not api_key:
    raise ConfigurationError("API key missing")

# ❌ WRONG: Silent fallback
api_key = config.get('api_key', 'default_key')
```

### 4. Universal Text Processing Pipeline
**Architecture**: `UNIVERSAL_CONTENT_PIPELINE_ARCHITECTURE.md`

ALL text generation uses standardized pipeline:

```
Material/Item → QualityEvaluatedGenerator → [Pipeline Stages] → Output
                                                    ↓
                            [Prompt Loading] → [Voice Layer] → [Humanness]
                                    ↓
                            [Generation] → [Quality Gates] → [Learning]
```

**Pipeline ensures**:
- Author voice consistency (persona-based, immutable)
- AI detection avoidance (humanness layer)
- Quality evaluation and learning
- Structural diversity
- Parameter optimization

**ZERO EXCEPTIONS**: NO text bypasses this pipeline.

### 5. Data Storage Policy
**Policy**: `docs/05-data/DATA_STORAGE_POLICY.md`

- **Materials.yaml**: Single source of truth + all generation/validation happens here
- **Frontmatter files**: Receive immediate partial field updates (dual-write)
- **Categories.yaml**: Single source of truth for category ranges
- **Dual-write**: Every Materials.yaml update triggers frontmatter field sync

---

## 📁 Directory Structure

```
z-beam-generator/
├── run.py                          # CLI entry point
├── config/                         # System configuration
│   └── config.yaml                 # Main configuration
├── data/                           # Source data (Layer 1)
│   ├── materials/Materials.yaml    # 121 materials
│   ├── contaminants/Contaminants.yaml  # 100+ patterns
│   ├── associations/DomainAssociations.yaml
│   ├── settings/Settings.yaml
│   └── compounds/Compounds.yaml
├── domains/                        # Domain-specific adapters
│   ├── materials/
│   │   ├── image/                 # Material image generation
│   │   ├── prompts/               # Material-specific prompts
│   │   └── config.yaml
│   └── contaminants/
│       ├── image/                 # Contaminant image generation
│       └── prompts/
├── generation/                     # Text generation system
│   ├── core/
│   │   ├── evaluated_generator.py # Main orchestrator (25KB)
│   │   └── generator.py           # Core generation logic
│   └── config/
│       ├── config.yaml
│       └── dynamic_config.py      # Parameter calculation
├── shared/                         # Reusable components
│   ├── image/
│   │   ├── orchestrator.py        # Generic image orchestrator
│   │   └── base_generator.py     # Base image generation
│   ├── text/
│   │   ├── adapters/              # Domain adapters
│   │   └── utils/prompt_builder.py
│   ├── voice/
│   │   ├── profiles/*.yaml        # Author personas (4 nationalities)
│   │   └── quality_analyzer.py
│   └── validation/
│       └── schema_validator.py
├── export/                         # Export system (Layer 2)
│   ├── core/
│   │   └── frontmatter_exporter.py  # Export orchestrator
│   ├── config/                    # Domain export configs
│   │   ├── materials.yaml
│   │   ├── contaminants.yaml
│   │   └── compounds.yaml
│   ├── enrichers/                 # Content enrichment
│   │   ├── base_enricher.py
│   │   ├── materials/
│   │   ├── contaminants/
│   │   └── compounds/
│   └── generation/
│       └── registry.py            # Field generators
├── learning/                       # Learning systems
│   ├── database/                  # SQLite storage
│   ├── humanness_optimizer.py
│   └── voice_postprocessor.py
└── tests/                          # Test suite (313/314 passing)
```

---

## 🔄 Data Flow: End-to-End

### 1. Text Generation Flow

```
User: run.py --material "Aluminum" --description
   ↓
CLI validates material exists in Materials.yaml
   ↓
QualityEvaluatedGenerator.generate(material, component_type, author)
   ↓
Load prompt template: prompts/materials/description.txt
   ↓
Load author persona: shared/voice/profiles/{author}.yaml
   ↓
Build prompt: domain template + voice + humanness layer
   ↓
API call: DeepSeek/Grok generates content
   ↓
DUAL-WRITE: Materials.yaml (full field) + Frontmatter (field sync)
   ↓
Quality Gates: Winston (69%+), Realism (5.5+), Readability
   ↓
Learning: Log attempt to database (all attempts, pass/fail)
   ↓
Result: Content saved, quality logged, parameters learned
```

### 2. Image Generation Flow

```
User: run.py --material "Steel" --image
   ↓
MaterialImageCoordinator (domain adapter)
   ↓
Load contamination patterns: Contaminants.yaml
   ↓
ContaminationPatternSelector.get_patterns(material)
   ↓
SharedImageOrchestrator.generate(identifier, category, patterns)
   ↓
Imagen API: Generate hero image
   ↓
Gemini Vision: Validate image (contamination visible, realistic, etc.)
   ↓
Save: ../z-beam/public/images/materials/steel-hero.jpg
   ↓
Result: Validated image saved
```

### 3. Export Flow

```
User: run.py --export materials
   ↓
FrontmatterExporter.export(domain='materials')
   ↓
Load config: export/config/materials.yaml
   ↓
For each material in Materials.yaml:
   ↓
   Load enrichers: export/enrichers/materials/*.py
   ↓
   Enrich: breadcrumbs, relationships, SEO, safety, etc.
   ↓
   Load field generators: export/generation/registry.py
   ↓
   Generate: dynamic fields (hero_title, seo_title, etc.)
   ↓
   Save: ../z-beam/frontmatter/materials/{slug}.yaml
   ↓
Result: 422 frontmatter files exported
```

---

## 🎨 Component Architecture

### 6-Component System (Simplified, Oct 2025)

Reduced from 11 components to 6 for maintainability:

1. **Frontmatter** - Core orchestrator (generates unified metadata)
2. **Micro** - Discrete component (dual voice generation)
3. **Subtitle** - Discrete component (single voice generation)
4. **Author** - Static component (depends on frontmatter)
5. **BadgeSymbol** - Static component (depends on frontmatter)
6. **MetaTags/JSONLD/PropertiesTable** - Static components

**Eliminated**: Separate industry_applications, regulatory_standards, environmental_impact generators → Consolidated into frontmatter with specialized prompt modules.

**Pattern**: See `docs/03-components/` for component-specific documentation.

---

## 🔧 API Integration

### Primary APIs

1. **DeepSeek** - Primary text generation (low cost, high quality)
2. **Grok (xAI)** - Backup text generation, evaluation prompts
3. **Winston AI** - Human believability scoring (69%+ threshold)
4. **Perplexity** - Research and property discovery
5. **Imagen (Google)** - Hero image generation
6. **Gemini Vision** - Image validation

### Configuration

All API keys in `config/config.yaml`:
```yaml
apis:
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
  winston:
    api_key: ${WINSTON_API_KEY}
  imagen:
    project_id: ${GCP_PROJECT_ID}
```

**Fail-fast**: System throws `ConfigurationError` if any required API key missing.

---

## ✅ Quality Assurance

### Quality Gates (All Must Pass)

1. **Winston AI Detection**: 69%+ human score (configurable via humanness_intensity, currently level 7)
2. **Readability Check**: Pass status
3. **Subjective Language**: No violations
4. **Realism Score**: 5.5/10 minimum (adaptive threshold with relaxation)
5. **Combined Quality Target**: Meets learning target

### Learning System

**Architecture**: `UNIFIED_LEARNING_ARCHITECTURE.md`

- **Logs ALL attempts** (not just successes) to SQLite database
- **Adaptive thresholds**: Relaxes from 5.5/10 → 4.5/10 over 5 attempts
- **Sweet spot analysis**: Identifies optimal parameters from 75th percentile
- **Composite scoring**: Winston (40%) + Realism (60%) weighting
- **Pattern learning**: Tracks structural diversity, opening patterns

---

## 📊 System Characteristics

### Performance

- **Text generation**: 5-15 seconds per component (single attempt)
- **Image generation**: 30-90 seconds (research + generation + validation)
- **Export**: 2-3 minutes for full domain (422 materials)
- **Success rate**: 50-70% first attempt (with adaptive thresholds)

### Scale

- **Materials**: 121 materials across 9 categories
- **Contaminants**: 100+ contamination patterns
- **Authors**: 4 personas (US, Taiwan, Italy, Indonesia)
- **Frontmatter files**: 422 materials + contaminants + compounds
- **Test suite**: 313/314 passing (99.7%)

### Quality Metrics

- **AI detection**: 69%+ human (Winston threshold)
- **Realism**: 5.5/10 minimum (adaptive)
- **Voice authenticity**: 85/100 (pattern compliance)
- **Learning data**: 50x increase (logs all attempts, not just successes)

---

## 🚨 Critical Constraints

### NEVER Violate These Rules

1. **NO production mocks/fallbacks** - System must fail if dependencies missing (tests OK)
2. **NO hardcoded values** - Use config files or dynamic calculation
3. **NO bypassing text pipeline** - ALL text uses QualityEvaluatedGenerator
4. **NO editing frontmatter directly** - Fix data/generators, then regenerate
5. **NO voice instructions outside personas** - Single source: `shared/voice/profiles/*.yaml`

See `.github/copilot-instructions.md` for complete policy documentation.

---

## 📚 Related Documentation

### Essential Reading
- **Architecture Deep Dive**: `docs/guides/ARCHITECTURE_PRINCIPLES.md` - 3-layer architecture, domain-agnostic design
- **Prompt System**: `docs/guides/PROMPT_SYSTEM_GUIDE.md` - Prompt purity, chaining, validation
- **Voice System**: `docs/guides/VOICE_ARCHITECTURE.md` - Author personas, humanness optimization
- **Export System**: `EXPORT_SYSTEM_ARCHITECTURE.md` - Universal exporter, enrichers, field generators

### Specific Topics
- **Component Discovery**: `COMPONENT_DISCOVERY.md` - How components are discovered/registered
- **Data Architecture**: `DATA_ARCHITECTURE_GUIDE.md` - Data structure, range propagation
- **Generation Pipeline**: `processing-pipeline.md` - Text generation flow
- **Learning System**: `UNIFIED_LEARNING_ARCHITECTURE.md` - Learning architecture
- **URL Strategy**: `URL_STRATEGY.md` - URL generation and hierarchical routing

### Policy Documents
- **Domain Independence**: `DOMAIN_INDEPENDENCE_POLICY.md`
- **Content Type Equality**: `CONTENT_TYPE_EQUALITY.md`
- **Generator vs Generated**: `GENERATOR_VS_GENERATED_CRITICAL.md` - Layer 2 vs Layer 3

---

## 🎯 Quick Start

### Generate Text Component
```bash
python3 run.py --material "Aluminum" --description
```

### Generate Hero Image
```bash
python3 run.py --material "Steel" --image
```

### Export All Frontmatter
```bash
python3 run.py --export materials
```

### Run Tests
```bash
pytest tests/ -v
```

---

**Last Updated**: December 20, 2025  
**Consolidated From**:
- ARCHITECTURE_OVERVIEW.md (351 lines)
- ARCHITECTURE_SIMPLIFIED.md (430 lines)
- SYSTEM_ARCHITECTURE.md (831 lines)
- ARCHITECTURE_VISUAL.md (145 lines)
- PIPELINE_DIAGRAM.md (525 lines)

**Total**: 2,282 lines → 550 lines (76% reduction, maintained essential information)
