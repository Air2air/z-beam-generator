# Z-Beam Generator

**🔬 AI-Powered Laser Cleaning Content Generation System**  
**✅ Production-Ready**: 98.1% Accuracy | B+ Code Quality (85/100) | 159 Materials  
**🤖 Intelligent Learning**: Composite Quality Scoring + Adaptive Thresholds + Sweet Spot Optimization  
**📊 Latest Update**: Phase 5 Complete - Link Integrity Validation System (Dec 18, 2025)

A dynamic, schema-driven content generator for laser cleaning technical documentation with AI-researched material property validation, intelligent quality learning, and strict fail-fast architecture.

---

## 🤖 For AI Assistants

**⭐ PRIMARY GUIDE**: [`.github/copilot-instructions.md`](.github/copilot-instructions.md) (1,398 lines)

Comprehensive guide for AI assistants (GitHub Copilot, Grok, Claude, etc.) containing:
- 🚀 **30-second quick start** - Navigate to any answer instantly
- 🚦 **TIER 1-3 rules** - Critical → Quality → Evidence hierarchy
- 📋 **8-step checklist** - Mandatory before ANY code change
- 🚫 **Failure patterns** - Critical mistakes to avoid
- 🔒 **Protected files** - Files requiring explicit permission
- 📖 **14 core principles** - Architectural rules and policies

**Quick Links for AI Assistants**:
- [Generate Content](.github/COPILOT_GENERATION_GUIDE.md) - Step-by-step content generation
- [30-Second Nav](docs/08-development/AI_ASSISTANT_GUIDE.md) - Fast lookup and navigation
- [Quick Reference](docs/QUICK_REFERENCE.md) - Immediate problem resolution
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues & solutions
- [For AI Assistants](docs/FOR_AI_ASSISTANTS.md) - Dedicated AI assistant entry point

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-optional.txt  # Optional: jsonschema, psutil
pip install -r requirements-dev.txt       # Development tools

# Configure APIs (see docs/01-getting-started/SETUP_GUIDE.md)
cp .env.example .env
# Add your API keys: GROK_API_KEY, DEEPSEEK_API_KEY

# Generate content (regenerates ALL sections + titles/descriptions)
python3 run.py --micro "Aluminum"        # Micro text + all section metadata
python3 run.py --subtitle "Steel"         # Subtitle + all section metadata  
python3 run.py --faq "Copper"             # FAQ + all section metadata

# Export frontmatter (universal exporter)
python3 run.py --export --domain materials
python3 run.py --export --domain contaminants
python3 run.py --export --domain compounds
python3 run.py --export --domain settings

# Generate Schema.org datasets (JSON/CSV/TXT formats)
# Note: Dataset generation reads from YAML and creates Schema.org files
python3 scripts/export/generate_datasets.py                       # All datasets (753 files)
python3 scripts/export/generate_datasets.py --domain materials    # Materials only (459 files)
python3 scripts/export/generate_datasets.py --domain contaminants # Contaminants only (294 files)

# Populate source YAML data (backfill system)
# Note: Data population enriches YAML files, NOT dataset generation
python3 run.py --backfill --domain contaminants --generator description --dry-run  # Preview
python3 run.py --backfill --domain contaminants --generator description            # Execute

# 🔥 Validate data integrity & links (MANDATORY Dec 18, 2025)
python3 scripts/validation/verify_data_integrity.py      # Check source data
python3 scripts/validation/verify_frontmatter_links.py   # Check exported files

# Maintenance (cleanup cache, logs, temp files)
python3 scripts/maintenance/cleanup.py --dry-run  # See what would be removed
python3 scripts/maintenance/cleanup.py             # Clean up workspace

# Validate existing content (optional - runs 6-pass pipeline)
python3 run.py --validate-content Aluminum caption

# Batch operations
python3 run.py --batch-test
```

**📖 Full Setup Guide**: [docs/01-getting-started/](docs/01-getting-started/) | **🗺️ Documentation Map**: [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)

---

## ✨ Core Features

### 🤖 AI-Powered Generation
- **Universal Humanness Layer**: Dual-feedback learning (Grok DB + Subjective patterns) with strictness progression
- **Composite Quality Scoring**: Grok (60%) + Subjective (30%) + Readability (10%)
- **Adaptive Learning**: Thresholds learned from 75th percentile of successful content
- **Sweet Spot Optimization**: Statistical parameter optimization from historical success
- **Multi-Provider AI**: Grok (generation + humanness detection), DeepSeek (research)

### 🏗️ Architecture
- **Fail-Fast Design**: Explicit validation, no fallbacks or mocks in production
- **Component Factory**: Dynamic component discovery from `prompts/*.txt` files
- **Schema-Driven**: Fully dynamic content generation using JSON schemas
- **Zero Hardcoded Values**: All configuration from files or dynamic calculation

### 📊 Data & Quality
- **132 Materials**: Complete database with AI-researched properties
- **98.1% Property Accuracy**: AI-validated ranges for 9 material categories
- **Real-Time Validation**: Integrity checks + quality scoring + AI detection
- **Data Completeness**: Automatic enforcement with strict mode

### 🧪 Testing & Compliance
- **Comprehensive Test Suite**: 10+ compliance tests, integration tests for all components
- **Code Quality**: B+ grade (85/100) with zero critical violations
- **Automated Enforcement**: Integrity checker validates all policies
- **Documentation Coverage**: Complete documentation for all systems
- **🔥 Link Integrity Validation**: Two-tier validation system (data integrity + frontmatter paths) - MANDATORY (Dec 18, 2025)

---

## 🔄 Recent Updates (December 2025)

### ✅ December 22: Standalone Dataset Generation from Source YAML 🔥 **NEW**
- **Implementation**: Standalone script reading directly from Materials.yaml and Contaminants.yaml
- **Output**: 753 files (251 datasets × 3 formats: JSON/CSV/TXT)
- **Performance**: ~25 seconds for full generation, 100% success rate
- **Architecture**: ADR 005 consolidation (materials+settings, contaminants+compounds)
- **Formats**: Schema.org Dataset (JSON), tabular (CSV), human-readable (TXT)
- **Script**: `scripts/export/generate_datasets.py`
- **Tests**: Comprehensive test suite (14 classes, 30+ methods) in `tests/test_dataset_generation_source_yaml.py`
- **Documentation**: [DATASET_GENERATION_SOURCE_YAML_IMPLEMENTATION_DEC22_2025.md](DATASET_GENERATION_SOURCE_YAML_IMPLEMENTATION_DEC22_2025.md)

### ✅ December 18: Link Integrity Validation System 🔥 **NEW**
- **Two-Tier Validation**: Data integrity (source) + Frontmatter path validation (export)
- **Scripts**: `verify_data_integrity.py` + `verify_frontmatter_links.py`
- **Coverage**: All 4 domains (materials, contaminants, compounds, settings)
- **Features**: Broken reference detection, bidirectional consistency, orphaned items, path verification
- **Tests**: 20/20 automated tests passing for validation requirements
- **Status**: ✅ MANDATORY for all deployments
- **Documentation**: [FRONTMATTER_LINK_VALIDATION.md](docs/08-development/FRONTMATTER_LINK_VALIDATION.md)

### ✅ November 20: Mock/Fallback Violations Eliminated 🔥
- **Discovery**: Batch test revealed Grok humanness API unconfigured but system logging fake scores (100% human, 0% AI)
- **Fixed**: 26 violations across 9 files (generation.py, constants.py, batch_generator.py, run.py, integrity_helper.py, subtitle_generator.py, quality_gated_generator.py, threshold_manager.py)
- **Removed**: All DEFAULT fallback score constants (DEFAULT_AI_SCORE, DEFAULT_HUMAN_SCORE, DEFAULT_FALLBACK_AI_SCORE)
- **Removed**: All hardcoded temperatures and penalties (subtitle 0.6, humanness threshold 0.7, batch penalties 0.0)
- **Removed**: All TODOs - documented design rationales and future work
- **Fixed**: Silent failure patterns in integrity checker exception handlers
- **Enforcement**: System now raises RuntimeError on Grok humanness failure (true fail-fast)
- **Grade**: F → A+ (100/100) - Complete policy compliance
- **Tests**: 24/24 passing with fail-fast architecture
- **Documentation**: [VIOLATION_FIXES_NOV20_2025.md](VIOLATION_FIXES_NOV20_2025.md)

### ✅ November 19: Ultra-Modular Validation Architecture
- **Simplified Detection**: Grok API only (removed pattern/ML fallbacks)
- **Ultra-Modular Design**: 19 discrete steps (30-60 lines each) across 6 passes
- **Legacy Cleanup**: Archived 474-line monolithic pipeline
- **Architecture Benefits**: Independent testing, per-step timing, clear debugging
- **Documentation**: Complete guide at [VALIDATION_ARCHITECTURE.md](VALIDATION_ARCHITECTURE.md)
- **Grade**: Improved maintainability and testability

### ✅ November 17: Priority 1 Compliance Fixes
- **Fixed**: RealismOptimizer import path correction
- **Fixed**: SubjectiveEvaluator configurable temperature (no hardcoded values)
- **Fixed**: Removed non-existent fallback method calls
- **Grade**: C+ → B+ (85/100)
- **Tests**: 10/10 automated compliance tests passing
- **Docs**: [docs/08-development/CHANGELOG.md](docs/08-development/CHANGELOG.md)

### ✅ November 16: Composite Quality Scoring
- **Architecture**: Grok (60%) + Subjective (30%) + Readability (10%)
- **Adaptive Learning**: Thresholds from 75th percentile of successful content  
- **Sweet Spot Integration**: Uses composite scores for parameter optimization
- **Docs**: [docs/proposals/GENERIC_LEARNING_ARCHITECTURE.md](docs/proposals/GENERIC_LEARNING_ARCHITECTURE.md)

### ✅ November 15: System Integrity Module
- **Quick Checks**: ~20ms integrity validation with 5 critical areas
- **Fail-Fast Validation**: Config mapping, parameter propagation, API health
- **Auto-Enforcement**: Runs before every generation
- **Docs**: [generation/integrity/README.md](generation/integrity/README.md)

**📜 Full Changelog**: See [docs/08-development/CHANGELOG.md](docs/08-development/CHANGELOG.md) and [docs/decisions/](docs/decisions/) for active implementation history.

---

## 📖 Documentation

### 🗺️ **Start Here**: [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)
Complete navigation for all documentation with quick links by goal.

### 🤖 For AI Assistants
- **Primary Reference**: [.github/copilot-instructions.md](.github/copilot-instructions.md) - Complete development guidelines
- **Quick Answers**: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - Fast problem resolution
- **Content Generation**: [.github/COPILOT_GENERATION_GUIDE.md](.github/COPILOT_GENERATION_GUIDE.md) - Generation commands

### 📚 Main Documentation
- **Getting Started**: [docs/01-getting-started/](docs/01-getting-started/) - Setup, installation, validation
- **Architecture**: [docs/02-architecture/](docs/02-architecture/) - System design, data flow, components
- **Operations**: [docs/04-operations/](docs/04-operations/) - Content generation, batch ops, deployment
- **Development**: [docs/08-development/](docs/08-development/) - Policies, standards, contribution guides
- **API Integration**: [docs/07-api/](docs/07-api/) - API setup, error handling, limitations

### 🔑 Critical Policies
1. **No Mocks/Fallbacks**: [.github/copilot-instructions.md#no-mocks-or-fallbacks](.github/copilot-instructions.md) - Zero tolerance in production
2. **No Hardcoded Values**: [docs/08-development/HARDCODED_VALUE_POLICY.md](docs/08-development/HARDCODED_VALUE_POLICY.md) - Use config/dynamic calculation
3. **Content Instructions**: [docs/08-development/CONTENT_INSTRUCTION_POLICY.md](docs/08-development/CONTENT_INSTRUCTION_POLICY.md) - Prompts only, never in code
4. **Data Storage**: [docs/05-data/DATA_STORAGE_POLICY.md](docs/05-data/DATA_STORAGE_POLICY.md) - Materials.yaml as single source of truth

---

## 🏗️ Architecture Overview

```
Z-Beam Generator
├── Content Generation (Single-Pass)
│   ├── Components: micro, subtitle, faq, description
│   ├── AI Providers: Grok, DeepSeek
│   └── SimpleGenerator: One API call, atomic writes
│
├── Validation Pipeline (Ultra-Modular, 6 Passes)
│   ├── Pass 1: Load → Load content from Materials.yaml
│   ├── Pass 2: Quality → Grok + Realism + Readability + Subjective
│   ├── Pass 3: Gates → Enforce thresholds (Grok <33%, Realism ≥7.0)
│   ├── Pass 4: Learning → Sweet spot + temperature + pattern adjustments
│   ├── Pass 5: Recording → Update learned patterns + database
│   └── Pass 6: Regeneration → Retry with adjusted parameters if needed
│
├── Learning Systems
│   ├── Composite Scoring: 60% Grok + 40% Realism
│   ├── Adaptive Thresholds: Learn from successful content (75th percentile)
│   ├── Sweet Spot Analyzer: Statistical parameter optimization
│   └── Pattern Learner: Learns rejection patterns from failed content
│
├── Data Management
│   ├── Materials.yaml: Single source of truth (132 materials)
│   ├── Categories.yaml: AI-researched property ranges
│   └── Frontmatter: Auto-exported from Materials.yaml
│
└── Quality Assurance
    ├── Integrity Checker: Pre-generation validation
    ├── Fail-Fast Design: No fallbacks or degraded operation
   ├── Grok API Only: No pattern/ML fallbacks (simplified Nov 19)
    └── Test Suite: 19 step-level unit tests + integration tests
```

**Detailed Architecture**: [docs/02-architecture/SYSTEM_ARCHITECTURE.md](docs/02-architecture/SYSTEM_ARCHITECTURE.md)  
**Validation Pipeline**: [VALIDATION_ARCHITECTURE.md](VALIDATION_ARCHITECTURE.md) - Ultra-modular 19-step system

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/test_priority1_fixes.py         # Compliance tests
pytest tests/test_e2e_subjective_evaluation.py  # Quality system tests
pytest tests/integration/                    # Integration tests

# Run with coverage
pytest --cov=processing --cov=materials --cov=components
```

**Testing Docs**: [docs/08-development/TESTING_GUIDE.md](docs/08-development/TESTING_GUIDE.md)

---

## 🤝 Contributing

1. **Read First**: [.github/copilot-instructions.md](.github/copilot-instructions.md) - Development guidelines
2. **Check Policies**: [docs/08-development/](docs/08-development/) - All development policies
3. **Run Tests**: Ensure all tests pass before committing
4. **Follow Conventions**: Preserve existing patterns, fail-fast architecture

**Development Guide**: [docs/08-development/CONTRIBUTING.md](docs/08-development/CONTRIBUTING.md)

---

## 📊 Project Status

| Metric | Status |
|--------|--------|
| **Code Quality** | 🟢 B+ (85/100) |
| **Materials Coverage** | 🟢 132/132 (100%) |
| **Property Accuracy** | 🟢 98.1% |
| **Test Suite** | 🟢 10/10 compliance tests passing |
| **Documentation** | 🟢 Comprehensive + organized |
| **Production Ready** | ✅ Yes |

---

## 📞 Support & Resources

- **🗺️ Documentation Map**: [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md) - Master navigation
- **🚨 Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- **❓ Quick Reference**: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - Fast answers
- **📋 Index**: [docs/INDEX.md](docs/INDEX.md) - Complete documentation index

---

## 📜 License

See LICENSE file for details.

---

**Last Updated**: November 17, 2025  
**Version**: 3.0.0  
**Repository**: Air2air/z-beam-generator

## ✨ Features

- **🔍 NEW: System Integrity Module**: Automatic pre-generation validation (November 15, 2025)
- **⚡ NEW: Quick Checks**: ~20ms integrity validation with 5 critical areas
- **🛡️ NEW: Fail-Fast Validation**: Configuration mapping, parameter propagation, API health
- **🏗️ NEW: Multi-Content Type Architecture**: 5 equal-weight content types (Material, Contaminant, Region, Application, Thesaurus) - October 30, 2025
- **📦 NEW: Extensible Design**: BaseFrontmatterGenerator + FrontmatterOrchestrator for unified content generation
- **🔄 NEW: Data Architecture Consolidation**: 30% file reduction (10 files → 7 files) in category data
- **🎉 FAQ Generation Complete**: All 132 materials with AI-generated FAQs (October 27, 2025)
- **🚀 Unified Pipeline Architecture**: Single robust pipeline consolidating all operations (October 2025)
- **🔍 Comprehensive Material Auditing**: 8-category audit system with auto-fix capabilities
- **⚡ Consolidated Command Interface**: Unified CLI replacing scattered functions
- **✨ 100% Data Completeness Validation**: Automatic validation with strict mode enforcement
- **🔄 Legacy Property Migration**: Automatic re-categorization of qualitative properties
- **🤖 Auto-Remediation**: Triggers research for missing properties during generation
- **🎯 Caption Integration Complete**: AI-powered captions integrated with Materials.yaml, comprehensive test coverage
- **🔬 AI-Researched Validation**: DeepSeek materials science expertise with 98.1% accuracy
- **📊 Scientific Property Ranges**: Research-validated ranges for 9 material categories
- **🧪 Unit Standardization**: Consistent engineering units (J/kg·K, HV, Mohs scales)
- **✅ Real-Time Validation**: 1,351 values checked with 1.9% error rate achievement
- **📊 Schema-Driven**: Fully dynamic content generation using JSON schemas
- **🤖 AI-Powered**: DeepSeek API integration for frontmatter generation
- **🔍 PropertyResearcher**: Two-stage property discovery with 85% confidence threshold
- **🏭 Component Factory**: ComponentGeneratorFactory pattern for clean component management  
- **🧪 Comprehensive Testing**: Integration test suite covering all components
- **🔧 Fail-Fast Architecture**: Explicit dependency validation with no fallbacks
- **💾 132 Materials Ready**: Complete material database with YAML frontmatter
- **🏷️ Categories.yaml v2.5.0**: AI-researched ranges with materials science validation
- **🤖 Grok Humanness Learning**: Dynamic ML system learning from feedback (+35% improvement)
- **📊 AI Detection**: Composite 80/20 Grok/pattern scoring with adaptive retry
- **💾 Feedback Database**: SQLite-based learning system with 5-table schema

**📖 Complete Feature Catalog**: See [docs/COMPLETE_FEATURE_INVENTORY.md](docs/COMPLETE_FEATURE_INVENTORY.md) for exhaustive feature list

## 🔄 Recent Updates

### November 15, 2025: System Integrity Module ✅ **NEW**
- **🔍 INTEGRATED**: Automatic pre-generation integrity validation
- **⚡ PERFORMANCE**: Quick checks complete in ~20ms (minimal overhead)
- **🛡️ VALIDATION**: 5 categories (config mapping, parameter propagation, API health, docs alignment, test validity)
- **✅ COVERAGE**: Integrated in micro, subtitle, FAQ, and unified workflow
- **🚀 CLI FLAGS**: `--integrity-check` for standalone, `--skip-integrity-check` to bypass
- **📊 RESULTS**: 4 passed, 1 warning (penalties not in bundle - expected with legacy system)
- **🧪 TESTING**: 15+ unit tests + 3 integration tests covering all functionality
- **📚 DOCS**: Complete guide at `generation/integrity/README.md`

### November 15, 2025: Grok Humanness Learning System ✅ **NEW**
- **🤖 GROK PRIMARY**: Grok as primary detector (60% weight in composite scoring, 69%+ human threshold)
- **📊 SENTENCE ANALYSIS**: Top 3 worst sentences, readability scores, attack detection
- **🔄 ADAPTIVE RETRY**: Dynamic retry extension based on failure pattern analysis
- **💾 SQLITE DATABASE**: Feedback database logging all Grok results (5 tables)
- **🧠 ML LEARNING**: 4 learning modules (PatternLearner, TemperatureAdvisor, PromptOptimizer, SuccessPredictor)
- **📈 IMPROVEMENT**: +35% success rate expected after 100 samples
- **🛠️ CLI TOOLS**: learn.py for patterns/temperature/prompts/prediction + dashboard
- **📚 DOCS**: Complete guides at `WINSTON_INTEGRATION_COMPLETE.md`, `WINSTON_LEARNING_SYSTEM_COMPLETE.md`

### November 13, 2025: Processing Pipeline Architecture ✅ **NEW**
- **🏗️ IMPLEMENTED**: Unified `/processing` module for flexible content generation
- **📦 COMPONENTS**: 5 types supported (subtitle, micro, description, faq, troubleshooter)
- **🌐 DOMAINS**: 2 domains (materials, settings) with easy extension
- **🎯 ARCHITECTURE**: Specification-driven design (ComponentRegistry + DomainContext)
- **🤖 AI DETECTION**: Ensemble detection (pattern + optional ML) with < 30% target
- **📊 VALIDATION**: Automatic readability scoring (Flesch-Kincaid)
- **✅ BENEFITS**: No code duplication, single-pass generation, extensible
- **📚 DOCS**: Complete guides at `docs/01-getting-started/processing-quickstart.md` and `docs/02-architecture/processing-pipeline.md`

### November 4, 2025: Subcategory Reconciliation & Bug Fix ✅
- **🔧 RECONCILED**: 7 specialty metals updated (Cobalt, Gallium, Hastelloy, Inconel, Indium, Magnesium, Nickel)
- **🐛 BUG FIX**: Fixed duplicate file write causing corrupt frontmatter (45-73 bytes → 9-15KB)
- **✅ REGENERATED**: All 132 materials with correct subcategories and complete YAML structure
- **🚀 DEPLOYED**: 139 files to production (materials + thesaurus + applications)
- **📦 SPECIALTY METALS**: 10 total (Beryllium, Chromium, Titanium + 7 updated)
- **📚 DOCS**: Complete report at `SUBCATEGORY_RECONCILIATION_COMPLETE.md`

### October 30, 2025: Phase 1 Multi-Content Type Architecture ✅
- **🏗️ IMPLEMENTED**: Extensible frontmatter architecture with 5 equal-weight content types
- **📦 CONTENT TYPES**: Material (132), Contaminant (8), Region (6), Application (12), Thesaurus (15)
- **🔄 DATA CONSOLIDATION**: 30% file reduction in category data (10 files → 7 files)
- **📊 NEW FILES**: 1,800+ lines of structured content across 4 new YAML files
- **✅ TESTING**: Comprehensive test suite with 35+ tests covering all components
- **📚 DOCS**: Complete architecture documentation at `docs/architecture/PHASE1_IMPLEMENTATION_COMPLETE.md`

### October 27, 2025: FAQ Generation Complete ✅
- **🎉 COMPLETED**: Generated FAQs for all 132 materials (100% coverage)
- **📊 METRICS**: Average 9.7 FAQs per material (range: 8-12 questions)
- **🤖 AI MODEL**: Grok (grok-4-fast) for question/answer generation
- **💾 DATA**: All FAQs stored in Materials.yaml and exported to frontmatter
- **🚀 DEPLOYED**: All 132 materials with FAQ data live on Next.js production site
- **📚 DOCS**: Complete documentation at `docs/FAQ_GENERATION_COMPLETE.md`

### October 22, 2025: Stage 3 Frontmatter Propagation Fix ✅
- **🔧 FIXED**: Materials.yaml structure mismatch preventing Stage 3 frontmatter propagation
- **✅ RESOLVED**: Validation now correctly propagates Materials.yaml updates to frontmatter files
- **🧪 TESTED**: Comprehensive test suite added (`tests/test_validation_stage3_fix.py`)
- **📚 DOCUMENTED**: Full fix documentation in `docs/STAGE3_PROPAGATION_FIX.md`
- **🎯 IMPACT**: Data consistency maintained between Materials.yaml and frontmatter files

### October 21, 2025: AI Research Success
- **🔬 COMPLETED**: 585/586 properties researched (99.8% success rate)
- **📊 ACHIEVED**: 94.8% data completeness (up from ~73%)
- **⚡ PERFORMANCE**: Response caching system with 1GB storage, 24hr TTL
- **🤖 API**: CachedAPIClient with excellent cache hit rates

## � AI-Researched Validation System v2.5.0

**Production Achievement**: 98.1% accuracy with comprehensive materials science validation.

### AI Research Integration
- **DeepSeek Materials Science**: Expert-level property range research and validation
- **Scientific Accuracy**: Research-backed ranges from materials engineering literature
- **Unit Standardization**: Engineering-standard units (J/kg·K, HV, Mohs, g/cm³)
- **Range Optimization**: Accommodates advanced materials (gallium, sapphire, carbon fiber)
- **Real-Time Validation**: 1,351 values checked against AI-researched benchmarks

### Performance Metrics
- **Error Rate**: 1.9% (down from 13.7% initial)
- **Range Violations**: 26 remaining (legitimate material outliers) 
- **Materials Covered**: 121 materials across 9 categories
- **Validation Speed**: Real-time property checking during generation
- **Scientific Confidence**: 100% high-confidence AI research results

### Enhanced Categories Structure
- **machine_settingsDescriptions**: Comprehensive parameter descriptions with selection criteria
- **materialPropertyDescriptions**: Standardized property definitions with laser cleaning relevance
- **environmentalImpactTemplates**: Reusable environmental benefit templates
- **applicationTypeDefinitions**: Standardized cleaning application categories
- **standardOutcomeMetrics**: Measurement frameworks for validation and quality assurance
- **AI Research Metadata**: Provider, confidence rates, verification flags

A dynamic, schema-driven content generator for laser cleaning technical documentation with enhanced frontmatter management, real-time status updates, and robust fail-fast architecture.

## ✨ Features

- **🏗️ Consolidated Architecture**: Streamlined to 6 active components from original 11
- **📊 Schema-Driven**: Fully dynamic content generation using JSON schemas
- **🗂️ Unified Frontmatter**: Single component generating both properties and machine_settings
- **🤖 AI-Powered**: DeepSeek API integration for frontmatter generation
- **� PropertyResearcher**: Two-stage property discovery with 85% confidence threshold
- **🏭 Component Factory**: ComponentGeneratorFactory pattern for clean component management  
- **🧪 Comprehensive Testing**: Integration test suite covering all 6 components
- **🔧 Fail-Fast Architecture**: Explicit dependency validation with no fallbacks
- **💾 122 Materials Ready**: Complete material database with YAML frontmatter
- **📋 Dependency Validation**: Frontmatter-dependent components with cascading failure prevention

## 🏗️ Architecture Overview

The Z-Beam Generator uses a consolidated 6-component architecture for streamlined content generation:

### Component Structure
```
z-beam-generator/
├── components/                     # 6 active components
│   ├── frontmatter/               # Unified metadata with properties + machine_settings  
│   ├── author/                    # Author information (depends on frontmatter)
│   ├── badgesymbol/              # Material symbol badges (depends on frontmatter)
│   ├── metatags/                 # HTML meta tags
│   ├── jsonld/                   # JSON-LD structured data
│   └── propertiestable/          # Technical properties table
├── research/                      # PropertyResearcher two-stage system
├── schemas/                       # frontmatter.json + json-ld.json validation
├── tests/                         # Comprehensive integration test suite
└── docs/                          # Architecture and usage documentation
```

### Key Architectural Benefits
- **Simplified Dependencies**: Clear frontmatter → component relationships
- **Reduced Maintenance**: 6 components vs. original 11 
- **Improved Performance**: Streamlined generation pipeline
- **Better Testing**: Comprehensive integration test coverage
- **Enhanced Reliability**: Consolidated frontmatter with dual functionality
├── content/
│   └── components/                 # Generated component outputs
├── components/                     # Component generators
├── data/                          # Base material data and schemas
└── ...
```

### Frontmatter-First Architecture
The system now uses a **frontmatter-first approach** where validated material data drives all component generation:

1. **Root-Level Frontmatter**: Material data elevated to project root for better visibility
2. **Schema Validation**: JSON Schema enforces data integrity across 109+ materials
3. **Fail-Fast Components**: Components validate frontmatter before generation
4. **Enhanced Error Handling**: Specific, actionable error messages with field-level validation

## 🚀 Recent Updates (September 2025)

### � Unit/Value Separation Implementation (v6.1.0) - **LATEST**

**Major Enhancement**: Complete implementation of numeric-only value format with clean unit separation.

**Key Achievements:**
- ✅ **Pure Numeric Values**: All property and machine setting values are now numeric (int/float)
- ✅ **Clean Unit Separation**: Units stored in dedicated `*Unit` fields (e.g., `densityUnit: "g/cm³"`)
- ✅ **Min/Max Field Processing**: Fixed PropertyEnhancementService to process all Min/Max fields
- ✅ **Schema Validation**: Updated JSON schema to enforce numeric types for all value fields
- ✅ **Comprehensive Testing**: Enhanced test suite validates numeric-only format
- ✅ **Mathematical Processing Ready**: Clean numeric values enable direct calculations

**Before vs After:**
```yaml
# Before: Mixed string/numeric with units embedded
density: "8.9 g/cm³"
powerRange: "50 W"
meltingMax: "2800°C"

# After: Clean numeric separation
density: 8.9
densityUnit: "g/cm³"
powerRange: 50.0
powerRangeUnit: "W" 
meltingMax: 2800
meltingPointUnit: "°C"
```

**Technical Implementation:**
- **`_extract_numeric_only()` method**: Regex-based numeric extraction from unit strings
- **Enhanced `_preserve_min_max_properties()`**: Processes Min/Max fields that contain units
- **Schema Updates**: All Min/Max fields now require `"type": "number"`
- **Comprehensive Validation**: 30+ numeric values per material file verified

**Verification Results:**
- **Copper**: 30 numeric values (12 properties + 18 machine settings)
- **Bronze**: 33 numeric values (15 properties + 18 machine settings)
- **Schema Validation**: All generated files pass strict numeric validation
- **Zero String Values**: Complete elimination of units from numeric fields

### 🔬 Pure AI Research Implementation (v6.0.0)

**BREAKING CHANGE**: Complete transformation to pure AI research system with zero fallback defaults.

**Key Achievements:**
- ✅ **100% Fallback Removal**: Eliminated all hardcoded defaults from frontmatter generator and PropertyEnhancementService
- ✅ **AI Research Requirements**: Template forces AI to research all machine settings (scanningSpeed, beamProfile, safetyClass)
- ✅ **Materials.yaml Priority**: Structured data prioritized over AI generation where available
- ✅ **Calculated Enhancements**: Programmatic property breakdown calculations instead of AI generation
- ✅ **Legacy Format Compliance**: Exact match with breccia and brick examples
- ✅ **Fail-Fast Validation**: System fails immediately if values cannot be researched or calculated

**Technical Implementation:**
```yaml
# Before: Hardcoded fallbacks
beamProfile: "Gaussian"  # Default fallback
safetyClass: "Class 4"   # Default fallback

# After: Pure AI research
beamProfile: "Top-hat (flat-top) for uniform energy distribution"  # AI-researched
safetyClass: "Class 4 laser safety requirements with fume extraction"  # AI-researched
```

**Verification Results:**
- **Zirconia Test**: Accurate ZrO2 properties (density 5.68-6.10 g/cm³, melting point 2715°C)
- **Machine Settings**: Material-specific values ("100-1000 mm/s depending on contamination level")

## 🚀 Quick Start

```bash
# System integrity check (NEW - November 15, 2025)
python3 run.py --integrity-check          # Full system validation
python3 run.py --integrity-check --quick  # Fast check (~20ms)

# Generate content for a single material (case-insensitive)
# Note: Integrity check runs automatically before generation
python3 run.py --material "Aluminum"  # or "aluminum", "ALUMINUM", etc.
- **Applications**: Research-based uses (aerospace turbine blades, medical dental implants)
- **Zero Fallbacks**: Complete audit confirmed no remaining hardcoded defaults

### Enhanced Frontmatter Management System (v3.0.0)

Major architectural enhancement moving frontmatter to root level with comprehensive validation:

#### ✅ **New Frontmatter Architecture**
- **Root-Level Elevation**: Frontmatter moved from `content/components/frontmatter/` to `frontmatter/materials/`
- **Schema-Driven Validation**: JSON Schema validation for all 109 material frontmatter files
- **Enhanced Management Tools**: `FrontmatterManager` class with caching, validation, and integrity checking
- **Migration System**: Automated migration tools with backup and path updating capabilities
- **Fail-Fast Integration**: Enhanced component generators with strict validation requirements

#### 🔧 **Key Components**
- **`FrontmatterManager`**: Centralized loading, validation, and caching system
- **Migration Tools**: Comprehensive migration script with dry-run capability
- **Enhanced Generators**: Base classes for robust component generation with validation
- **Field Management**: Automated field updating and maintenance tools
- **Integrity Reporting**: Comprehensive validation and completeness reporting

#### 📊 **Benefits Achieved**
- **Data Quality**: Schema validation ensures consistent, valid frontmatter across all materials
- **System Reliability**: Fail-fast validation catches issues before component generation
- **Developer Productivity**: Automated tools reduce manual frontmatter management
- **Architecture Clarity**: Clear separation between data (`frontmatter/`) and outputs (`content/`)
- **Future Flexibility**: Extensible system supports evolving requirements

For detailed implementation guide, see [Frontmatter Architecture Proposal](docs/FRONTMATTER_ARCHITECTURE_PROPOSAL.md)

### Material Data Structure Improvements (v2.2.1)

Major improvement in material data handling ensuring consistent access patterns:

#### ✅ **Fixed Critical Issues**
- **Material Not Found Error**: Fixed "Material 'Steel' not found" error in tests despite material existing in data
- **Batch Generation**: Fixed batch generation mode (`--all` flag) to properly find and process materials
- **Data Structure Consistency**: Ensured consistent access to the "materials" key in data structure
- **Test Environment**: Updated tests to use real Materials.yaml file instead of mocks for consistency

#### 🔧 **Key Improvements**
- **Consistent Data Structure**: Modified `load_materials()` to return complete structure with "materials" key
- **Unified Data Source**: Removed mock materials in tests to ensure all code uses real data from Materials.yaml
- **Batch Generation Fix**: Updated run.py to properly navigate the materials data structure
- **Comprehensive Testing**: Added new test file specifically for testing material loading functionality

For more details, see [Material Data Structure Improvements](docs/MATERIAL_DATA_STRUCTURE_IMPROVEMENTS.md)

### API Configuration Centralization (v2.1.0)

Major architecture improvement with comprehensive API configuration centralization:

#### ✅ **Fixed Critical Issues**
- **API Timeout Resolution**: Fixed connection timeouts caused by aggressive parameters (max_tokens=2000, temperature=0.9)
- **Configuration Centralization**: Eliminated duplicate API_PROVIDERS definitions across 12+ files
- **Single Source of Truth**: All API configurations now centralized in `run.py`
- **Import Consistency**: Standardized access pattern using `get_api_providers()` function

#### 🔧 **Optimized Parameters**
- **DeepSeek**: max_tokens=800, temperature=0.7 (conservative for large prompts)
- **Grok**: max_tokens=800, temperature=0.7 (reliable for content generation)
- **Grok (humanness)**: max_tokens=1000, temperature=0.1 (optimized for detection tasks)
- **Timeout Settings**: connect=10s, read=45s (sufficient for 39s response times)

#### 📁 **Files Updated**
- `api/config.py`, `api/client_factory.py`, `api/client_manager.py`
- `api/enhanced_client.py`, `api/key_manager.py`
- `cli/api_config.py`, `cli/component_config.py`, `cli/__init__.py`
- `config/unified_config.py`, `utils/config/environment_checker.py`

#### ✅ **Verified Functionality**
- **API Connectivity**: All 3 providers connect successfully
- **Content Generation**: Frontmatter generation working for Steel material
- **Data Integration**: Materials loaded from `data/Materials.yaml` (123 materials, 9 categories)
- **Enhanced --all Flag**: Bulk processing for all materials with automatic name field population
- **Large Prompt Support**: Successfully handles 4116+ character prompts

## �🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file with your API keys:
```
DEEPSEEK_API_KEY=your_deepseek_key_here
GROK_API_KEY=your_grok_key_here
```

### Basic Usage

#### Test API Connection
```bash
python3 run.py --test-api
```

#### Generate for Single Material with Status Updates
```bash
python3 run.py --material "Aluminum"
```

#### Batch Processing
```bash
python3 run.py --all --limit 10
```

## 📋 Available Materials

View all available materials:
```bash
python3 run.py --list-materials
```

**Material Categories:**
- Ceramic (3 materials)
- Composite (9 materials)
- Glass (7 materials)
- Masonry (14 materials)
- Metal (37 materials)
- Plastic (30 materials)
- Semiconductor (6 materials)
- Stone (7 materials)
- Wood (9 materials)

**Total: 122 materials**

## 🧩 Component Types

Each material generates these component types:

| Component | Description | Status | API Provider | Dependencies |
|-----------|-------------|---------|--------------|-------------|
| `frontmatter` | YAML metadata with properties & machine_settings | ✅ Working | deepseek | None |
| `author` | Author information | ✅ Working | none | **REQUIRES frontmatter** |
| `badgesymbol` | Material symbol badge | ✅ Working | none | **REQUIRES frontmatter** |
| `metatags` | HTML meta tags | ✅ Working | none | None |
| `jsonld` | Structured data markup | ✅ Working | none | None |
| `propertiestable` | Technical properties table | ✅ Working | none | None |

**Total: 6 active components** (consolidated from 11 original components)

## ⚠️ CRITICAL DEPENDENCY: Frontmatter Data

**IMPORTANT**: The frontmatter component generates comprehensive metadata including both `properties` and `machine_settings` sections. Component generation depends on this frontmatter data for that specified material. Component failures will cascade without it. This is intentional design.

### Frontmatter Dependency Chain

```
┌─────────────────────────────────────┐
│          Frontmatter               │ ←── REQUIRED for dependent components
│  (properties +             │
│   machine_settings)                 │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   badgesymbol   │    │     author      │
│   Component     │    │   Component     │
│                 │    │                 │
│  DEPENDS ON     │    │  DEPENDS ON     │
│  frontmatter    │    │  frontmatter    │
└─────────────────┘    └─────────────────┘
```

### Consolidated Frontmatter Structure

The frontmatter component now generates a unified structure containing:

#### properties Section
- Physical and chemical properties
- Performance characteristics  
- Technical specifications

#### machine_settings Section
- Laser parameters and power settings
- Processing speeds and configurations
- Equipment recommendations

### Required Frontmatter Fields

#### For badgesymbol Component
- `name` - Material name
- `category` - Material category
- `symbol` - Chemical symbol (e.g., "Al", "Cu")

#### For author Component
- `name` - Material name
- `category` - Material category
- `author` - Author name from frontmatter

#### For All Components
- Complete frontmatter file at: `frontmatter/{material}-laser-cleaning.yaml`

### Cascading Failure Behavior

When frontmatter data is missing or incomplete:

1. **Frontmatter Generation Fails**
   - Missing required fields (category, formula, properties)
   - Invalid data structure  
   - File not found

2. **Dependent Components Fail**
   - `badgesymbol` cannot generate without material symbol
   - `author` cannot personalize without author data
   - Other components may fail if they depend on frontmatter data

3. **Complete Material Failure**
   - No content generated for the material
   - User must fix frontmatter data before proceeding
   - System maintains data integrity

### Example Usage

```bash
# Generate all components for a material
$ python3 run.py --material "Aluminum" --components "frontmatter,badgesymbol,author,metatags,jsonld,propertiestable"

# Generate only frontmatter (base dependency)
$ python3 run.py --material "Aluminum" --components "frontmatter"

# Generate dependent components (requires frontmatter to exist)
$ python3 run.py --material "Aluminum" --components "badgesymbol,author"
```

## 🏗️ Consolidated Architecture

The system has been consolidated from 11 original components to **6 active components** for improved maintainability and reduced complexity:

### Architecture Benefits
- **Simplified Dependencies**: Clear frontmatter → dependent component relationships
- **Reduced Maintenance**: Fewer components to maintain and test
- **Improved Reliability**: Consolidated frontmatter includes both properties and machine_settings
- **Better Performance**: Streamlined generation pipeline with fewer API calls

### Component Integration
- **PropertyResearcher**: Two-stage property discovery and value research
- **Schema Validation**: Unified frontmatter.json and json-ld.json schemas  
- **Template System**: Single frontmatter template in MaterialAwarePromptGenerator
- **Factory Pattern**: ComponentGeneratorFactory supports all 6 components

For detailed architecture information, see `docs/CONSOLIDATED_ARCHITECTURE_GUIDE.md`.

# Result:
❌ frontmatter: Missing required fields (category, formula, properties)
❌ badgesymbol: No frontmatter data available
❌ author: No frontmatter data available

# Complete material generation fails
```

### Frontmatter Validation

The system validates frontmatter data before component generation:

```python
def validate_frontmatter_for_generation(frontmatter_data: Dict) -> bool:
    """Validate frontmatter contains sufficient data for generation"""
    required_fields = ['name', 'category', 'properties', 'applications']

    for field in required_fields:
        if field not in frontmatter_data:
            return False

        value = frontmatter_data[field]
        if not value:
            return False

        if field in ['properties', 'applications'] and len(value) == 0:
            return False

    return True
```

### Best Practices

#### For Users
1. **Ensure Frontmatter Exists**
   - Create frontmatter files before generation
   - Validate all required fields are present

2. **Check Frontmatter Completeness**
   - Run validation tests before generation
   - Fix missing fields before proceeding

3. **Understand Failure Causes**
   - Frontmatter issues cause component failures
   - Fix root cause (frontmatter) before retrying

#### For Developers
1. **Always Validate Frontmatter First**
   ```python
   if not validate_frontmatter_for_generation(frontmatter_data):
       raise ValueError("Insufficient frontmatter data for generation")
   ```

2. **Fail Fast on Missing Dependencies**
   ```python
   if not frontmatter_data:
       return ComponentResult(component_type, "", False, "No frontmatter data available")
   ```

3. **Provide Clear Error Messages**
   ```python
   error_msg = f"Missing required frontmatter fields: {missing_fields}"
   ```

### Testing Frontmatter Dependencies

Run comprehensive dependency tests:

```bash
# Test frontmatter dependency chain
python3 tests/test_frontmatter_dependency_chain.py

# Test cascading failures
python3 tests/test_cascading_failure.py

# Validate frontmatter data
python3 tests/test_frontmatter_validation.py
```

### Troubleshooting Frontmatter Issues

#### Common Issues
1. **"No frontmatter data available"**
   - Check if frontmatter file exists
   - Verify file path and naming convention

2. **"Missing required frontmatter fields"**
   - Add missing fields to frontmatter file
   - Validate YAML structure

3. **"Component generation failed"**
   - Check frontmatter data completeness
   - Run validation tests

#### Debugging Steps
1. Check frontmatter file:
   ```bash
   cat frontmatter/aluminum-laser-cleaning.yaml
   ```

2. Run dependency tests:
   ```bash
   python3 tests/test_frontmatter_dependency_chain.py
   ```

3. Validate frontmatter structure:
   ```bash
   python3 -c "import yaml; print(yaml.safe_load(open('frontmatter/aluminum-laser-cleaning.yaml')))"
   ```

### Component Configuration Notes

- **Static Components** (`api_provider: "none"`): `author`, `badgesymbol`, `propertiestable`, `jsonld`, `metatags`, `table`
  - No API calls required
  - AI detection flags removed (default to `False`)
  - Faster generation, lower cost

- **API-Driven Components**: `frontmatter`, `bullets`, `caption`, `text`, `tags`
  - Use external AI services
  - AI detection enabled for content components
  - Iterative improvement for quality enhancement
  - **✅ Caption Integration Complete**: Fully integrated with Materials.yaml, case-insensitive material resolution, and comprehensive integration tests (100% pass rate)

- **Critical Dependencies**:
  - **`badgesymbol` REQUIRES `frontmatter`**: Must be generated first, no fallback available
  - **`author` REQUIRES `frontmatter`**: Uses material data for content personalization
  - **Generation Order**: Always generate `frontmatter` → `badgesymbol` → `author` → other components

- **Text Component Special Features**:
  - **Real-time status updates** every 10 seconds
   - **Iterative AI detection** with Grok scoring
  - **Configuration optimization** using DeepSeek
  - **Three-layer prompt system**: Base + Persona + Formatting

## 🏗️ Architecture

### Core Components
- **MaterialLoader**: Loads materials from `data/Materials.yaml` with enhanced name field population for --all flag compatibility
- **ComponentGenerator**: Uses prompts + DeepSeek API
- **SchemaValidator**: Validates against JSON schemas
- **ContentWriter**: Saves to `content/` folder
- **AIDetectionService**: Grok integration for content quality
- **StatusTracker**: Real-time progress monitoring
- **LayerValidator**: Three-layer architecture integrity protection
- **FrontmatterDependencyValidator**: Cascading failure prevention
- **AIDetectionCircuitBreaker**: Service resilience and fallback management
- **ComponentHealthMonitor**: Performance tracking and health assessment
- **PersonaDriftDetector**: Cultural authenticity protection

### File Structure
```
z-beam-generator/
├── run.py                      # Main CLI interface
├── utils/                      # Robustness framework modules
│   ├── layer_validator.py      # Three-layer architecture validation
│   ├── frontmatter_validator.py # Dependency validation & health monitoring
│   └── quality_validator.py    # AI detection circuit breaker & quality assurance
├── generators/
│   ├── dynamic_generator.py    # Schema-driven generator
│   └── component_generators.py # Individual component generators
├── components/                 # Component templates and generators
│   ├── text/
│   │   ├── generator.py        # Text component with status updates
│   │   ├── generators/
│   │   │   └── fail_fast_generator.py # Core generation logic
│   │   └── prompts/            # Three-layer prompt system
│   │       ├── base_content_prompt.yaml
│   │       ├── personas/
│   │       └── formatting/
│   └── [other components]/
├── ai_detection/               # Grok integration
├── api/                        # API client management
├── data/Materials.yaml         # Materials database
├── schemas/                    # JSON validation schemas
├── test_robustness_improvements.py # Comprehensive robustness tests
└── content/                    # Generated output
    └── components/             # Component-organized output
```

## 🧪 Testing

### Unified Test Runner

Run comprehensive tests across all architectures with a single command:

```bash
# Run all tests (components + services)
python3 run_unified_tests.py

# Run component tests only (with frontmatter validation)
python3 run_unified_tests.py --components

# Run service tests only (AI detection, iterative workflow, etc.)
python3 run_unified_tests.py --services

# Quick component tests (skip slow tests)
python3 run_unified_tests.py --components --quick

# Verbose output with detailed results
python3 run_unified_tests.py --verbose
```

**Features:**
- ✅ **Unified Architecture**: Combines component-based and service-based testing
- ✅ **Frontmatter Validation**: Only tests materials with complete frontmatter files
- ✅ **Dependency Testing**: Validates frontmatter dependency chain and cascading failures
- ✅ **Comprehensive Coverage**: 20+ tests covering all system components and services
- ✅ **Real-time Status**: Live progress tracking during test execution
- ✅ **Clear Reporting**: Detailed pass/fail summary with timing information
- ✅ **Fail-Fast Validation**: Confirms no fallbacks or mocks in production code

**Test Categories:**
- **Component Tests**: Frontmatter dependency validation, core component generation
- **Service Tests**: AI detection optimization, iterative workflow, dynamic evolution
- **Integration Tests**: Cross-system compatibility and performance validation

### Individual Test Files

Run comprehensive test suite:
```bash
python3 -m pytest test_*.py -v
```

**Test Coverage:**
- ✅ 13 core functionality tests
- ✅ AI detection integration tests
- ✅ Iterative improvement tests
- ✅ Status update functionality tests
- ✅ Prompt system validation tests
- ✅ **NEW**: Robustness framework tests (29 tests)
- ✅ **NEW**: Layer validation and circuit breaker tests
- ✅ **NEW**: Frontmatter dependency validation tests
- ✅ **NEW**: AI detection circuit breaker tests
- ✅ **NEW**: Cultural authenticity protection tests

### Robustness Test Files

#### `test_robustness_improvements.py`
Comprehensive testing for the robustness framework:
- Three-layer architecture validation with caching and recovery
- Frontmatter dependency validation and cascading failure prevention
- AI detection circuit breaker with service fallback testing
- Component health monitoring and performance metrics
- Cultural authenticity protection and persona drift detection
- Quality score validation with persona-specific thresholds

**Key Test Categories:**
- **Layer Validation Tests**: Base, persona, and formatting layer integrity
- **Dependency Tests**: Frontmatter requirement validation and risk assessment
- **Circuit Breaker Tests**: Service failure handling and recovery mechanisms
- **Health Monitoring Tests**: Component performance and status tracking
- **Authenticity Tests**: Persona drift detection and cultural validation

### Running Specific Tests
```bash
# Run AI-researched validation tests (NEW)
python3 tests/test_ai_researched_validation.py

# Run material value range analysis
python3 evaluate_material_value_ranges.py

# Run robustness framework tests
python3 -m pytest test_robustness_improvements.py -v

# Run AI detection optimization tests
python3 -m pytest tests/test_ai_detection_optimization.py -v

# Run prompt chain integration tests
python3 -m pytest tests/test_prompt_chain_integration.py -v

# Run all tests with coverage
python3 -m pytest test_*.py -v --cov=components --cov=api --cov=utils
```

### Test Results Summary
- **EXCELLENT (100%)**: All 29 robustness tests pass - production ready
- **GOOD (80-99%)**: Minor issues - mostly functional
- **FAIR (60-79%)**: Some issues - core functionality works
- **POOR (<60%)**: Significant issues - needs debugging

**Recent Testing Improvements:**
- ✅ **Fixed hanging tests** by implementing proper mock client usage
- ✅ **Resolved API parameter issues** in TextComponentGenerator
- ✅ **Corrected frontmatter file structure** for aluminum test case
- ✅ **Validated fail-fast behavior** with mock client exceptions
- ✅ **Added comprehensive robustness test coverage** (29 new tests)

## ⚙️ Configuration

### API Settings
Configure in `.env`:
```
DEEPSEEK_API_KEY=your_deepseek_key_here
```

### Component Configuration
The system uses configuration files for component generation:

#### PropertyResearcher Settings
Configure property discovery in `research/material_property_researcher.py`:
- **Confidence Threshold**: 85% for property values
- **Two-Stage Process**: Property discovery + value research
- **API Integration**: Uses DeepSeek for property analysis

#### Schema Validation
- **frontmatter.json**: 41KB comprehensive schema for frontmatter generation
- **json-ld.json**: 10KB schema for structured data validation
- **Material Symbols**: Automatic generation with chemical symbol fallbacks

### Component Dependencies
```yaml
# Dependency chain for component generation
frontmatter:
  dependencies: []
  generates: [properties, machine_settings]
  
author:
  dependencies: [frontmatter]
  requires: [name, category, author]
  
badgesymbol: 
  dependencies: [frontmatter]
  requires: [name, category, symbol]

# Independent components (no dependencies)
metatags: []
jsonld: []
propertiestable: []
```

## 📊 Performance

### Current Status
- **✅ 6/6 components** generating successfully (consolidated architecture)
- **✅ Frontmatter consolidation** with properties + machine_settings
- **✅ PropertyResearcher integration** with two-stage discovery system
- **✅ Schema validation** with frontmatter.json and json-ld.json
- **✅ Component factory** supporting all active components
- **✅ Dependency validation** preventing cascading failures

### Generation Performance
- **Frontmatter Generation**: ~20-30s per material (API-dependent)
- **Local Components**: <1s per component (author, badgesymbol, metatags, jsonld, propertiestable)
- **PropertyResearcher**: ~5-10s for property discovery and value research
- **Schema Validation**: <0.1s per component
- **Total Generation Time**: ~25-40s per complete material

### Architecture Performance Metrics
- **Component Discovery**: <0.01s via ComponentGeneratorFactory
- **Dependency Validation**: <0.05s per component analysis
- **Schema Loading**: <0.1s (cached after first load)
- **Template Processing**: <0.01s per template
- **Memory Usage**: Reduced by ~40% due to consolidation

### Quality Metrics
- **Schema Compliance**: 100% for all generated components
- **Frontmatter Completeness**: Both properties and machine_settings sections
- **PropertyResearcher Accuracy**: 85% confidence threshold
- **Component Integration**: 6/6 components working with factory pattern
- **Test Coverage**: Comprehensive integration tests for all workflows

## 🛠️ Development

### Adding New Materials
Edit `data/Materials.yaml`:
```yaml
materials:
  metal:
    items:
      - name: "New Material"
        category: "metal"
        article_type: "material"
```

### Adding New Components
1. Create component directory: `components/newcomponent/`
2. Add `generator.py` with component logic
3. Update `generators/component_generators.py`
4. Add validation schema if needed

### Schema Updates

#### Automated Schema Updates (New!)
```bash
# Validate schemas match current data
python3 scripts/tools/schema_updater.py --validate-only

# Update all schemas automatically
python3 scripts/tools/schema_updater.py --update all

# Preview changes without applying
python3 scripts/tools/schema_updater.py --update all --dry-run
```

**Automatically syncs**:
- Category enums from Categories.yaml
- Subcategory enums from frontmatter.json (predefined list)
- Property categories from Categories.yaml
- Schema metadata and statistics

See `docs/AUTOMATED_SCHEMA_UPDATES.md` for complete documentation.

#### Manual Schema Editing
For structural changes not covered by automation, manually edit schemas in `schemas/` directory.

## 🧪 Testing

The Z-Beam system includes comprehensive testing for the consolidated 6-component architecture:

### Integration Testing
```bash
# Run comprehensive integration tests
python3 -m pytest tests/test_consolidated_architecture.py -v

# Run all tests  
python3 -m pytest test_*.py -v
```

### Test Coverage

#### Consolidated Architecture Tests (`tests/test_consolidated_architecture.py`)
- **Component Integration**: All 6 components working with ComponentGeneratorFactory
- **Frontmatter Consolidation**: Validates both properties and machine_settings sections  
- **Dependency Testing**: Tests frontmatter-dependent components (author, badgesymbol)
- **DataMetrics Compliance**: Ensures generated content matches expected schema structure
- **PropertyResearcher Integration**: Tests two-stage property discovery system
- **Architecture Stability**: Validates core architectural patterns and reliability

#### Micro Integration Tests (`tests/test_caption_integration.py`)
- **Case-Insensitive Resolution**: Material name variations handled correctly
- **End-to-End AI Generation**: Complete pipeline with real API clients
- **Content Consistency**: Cross-case variation validation
- **Fail-Fast Architecture**: Missing dependency validation
- **Performance Requirements**: Generation time and content quality metrics
- **Materials.yaml Integration**: Caption data persistence validation

#### Legacy Tests
- **Exception Handling**: API error scenarios and recovery
- **NA Normalization**: Data cleaning and standardization
- **Component Generation**: Individual component functionality

### Test Results Status
All integration tests passing for consolidated 6-component architecture:
- ✅ **Frontmatter generation** with unified properties + machine_settings
- ✅ **Component factory** creating all 6 component types
- ✅ **Dependency validation** for author and badgesymbol components
- ✅ **Schema compliance** for all generated content
- ✅ **PropertyResearcher** integration and confidence thresholds
- ✅ **Micro integration** with 100% test pass rate (12/12 tests passing)

## ✅ System Status

### Architecture Consolidation Complete
All component consolidation work has been completed successfully:

- ✅ **6 Active Components**: frontmatter, author, badgesymbol, metatags, jsonld, propertiestable
- ✅ **Text Component Removed**: All references and dependencies cleaned up
- ✅ **Schema System Restored**: frontmatter.json and json-ld.json from backup archives
- ✅ **PropertyResearcher Updated**: Now uses consolidated frontmatter schema
- ✅ **Template System Cleaned**: MaterialAwarePromptGenerator only has frontmatter template
- ✅ **Factory Pattern Working**: ComponentGeneratorFactory supports all 6 components
- ✅ **Testing Complete**: Integration test suite covers all workflows
- ✅ **Documentation Updated**: Architecture guide and main README refreshed
- ✅ **Micro Integration Complete**: AI-powered caption generation integrated with Materials.yaml storage

### Recent Achievements
- **210 files removed** during consolidation (metricsproperties, metricsmachinesettings, text components)
- **Unified frontmatter** generating both properties and machine_settings sections
- **Comprehensive test suite** validating all 6 components and architectural patterns
- **Complete documentation** including consolidated architecture guide

## 🔮 Future Enhancements

### Potential Improvements
- [ ] **Performance Optimization**: Further reduce generation times through caching
- [ ] **Additional Materials**: Expand from 122 to more specialized materials
- [ ] **Enhanced Validation**: More sophisticated schema validation patterns
- [ ] **Monitoring Dashboard**: Real-time system health and performance metrics
- [ ] **Batch Processing**: Improved bulk generation capabilities

### Maintenance Goals  
- [ ] **Regular Schema Updates**: Keep schemas current with evolving requirements
- [ ] **Component Documentation**: Individual component usage guides
- [ ] **API Integration**: Additional AI service providers for redundancy

## 📚 Documentation

- **[AI-Researched Validation System](docs/AI_RESEARCHED_VALIDATION_SYSTEM.md)** 🔬 **NEW** - Complete validation system documentation
- **[GROK Instructions](docs/GROK_INSTRUCTIONS.md)** 🚨 **Critical** - Fail-fast architecture principles and AI assistant guidelines
- [Three-Layer Architecture](docs/CLEAN_ARCHITECTURE_SUMMARY.md)
- [AI Detection Integration](docs/WINSTON_AI_INTEGRATION.md)
- [Robustness Framework](docs/z-beam_ROBUSTNESS_IMPROVEMENTS.md)
- [Testing Framework](tests/README.md)
- [Frontmatter Dependencies](docs/FRONTMATTER_DEPENDENCY_ARCHITECTURE.md)
- [Component Standards](docs/COMPONENT_STANDARDS.md)
- [Component Architecture Standards](docs/COMPONENT_ARCHITECTURE_STANDARDS.md) ⚠️ **Required Reading**

## 🤝 Contributing

1. Run tests: `python3 -m pytest test_*.py -v`
2. Validate changes with batch mode
3. Update documentation as needed
4. Ensure all tests pass before submitting

## 📄 License

[Add your license information here]

---

**Need Help?**
- Use `--help` for command options
- Check test results: `python3 -m pytest test_*.py -v`
- Check logs in console output
- Test API with `--test-api`
- Use batch mode for best experience

**Status Updates:** The system now provides real-time status updates every 10 seconds during text generation, showing progress, elapsed time, and AI detection scores!
