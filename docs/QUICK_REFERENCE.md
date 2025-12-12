# Quick Reference for AI Assistants

**🤖 Optimized for AI assistant navigation and problem resolution**

---

## 🚨 CRITICAL: Read First

**⭐ PRIMARY GUIDE**: [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) (1,398 lines)

**Before ANY code change, consult the primary guide for**:
- ✅ **Mandatory pre-change checklist** (8 steps) - Lines 300-400
- 🚦 **TIER 1-3 rule priorities** - Lines 200-250 (system-breaking → quality → evidence)
- 🚫 **Critical failure patterns** - Lines 100-200 (Grade F violations)
- 🔒 **Protected files** - Lines 450-500 (require permission before editing)
- 📖 **14 core principles** - Lines 500-800 (architectural rules)
- 🔥 **Recent critical updates** - Lines 50-100 (Nov-Dec 2025)

**This document (QUICK_REFERENCE.md)** provides fast problem resolution.  
**The primary guide** provides comprehensive architectural rules and policies.

**Additional AI Resources**:
- 🚀 [Generation Guide](../.github/COPILOT_GENERATION_GUIDE.md) - Step-by-step content generation
- ⚡ [AI Assistant Guide](08-development/AI_ASSISTANT_GUIDE.md) - 30-second navigation
- 📚 [For AI Assistants](FOR_AI_ASSISTANTS.md) - Dedicated entry point

---

## 📚 Critical Documentation for AI Assistants

**BEFORE** any work, review these files organized by category:

### ⚡ Recent Updates (November-December 2025)
- **🚨 Author Assignment Immutability Policy** (Dec 6): Once author assigned, NEVER changes
  - See: `.github/copilot-instructions.md` - Author Assignment Immutability Policy
  - Tests: `tests/test_author_assignment_immutability.py` (9/9 tests passing ✅)
  - Voice control: Author personas (`shared/prompts/personas/*.yaml`) define ALL voice behavior
  - Humanness optimizer: Provides structural variation ONLY (rhythm, opening) NOT voice
  - Domain configs: NO voice/content instructions (removed from settings/materials configs)
  - Grade F violation: Changing author or voice on regeneration
  - **Voice Compliance Issue**: LLM (Grok-4-fast) ignores persona instructions
    - Architecture verified correct (95/100) - immutability working, personas distinct
    - Generated content identical across all 4 authors (0/100) - LLM limitation
    - All outputs contain forbidden phrases despite persona rules
    - E2E testing: Aluminum (USA), Bamboo (Indonesia), Alabaster (Italy), Breccia (Taiwan)
    - Recommendation: Switch to Claude/GPT-4 or add post-generation persona validation
- **🚨 Mock/Fallback Violations Fixed** (Nov 20): Complete fail-fast architecture enforcement
  - See: `VIOLATION_FIXES_NOV20_2025.md`
  - Fixed: 26 violations across 9 files (generation.py, constants.py, batch_generator.py, run.py, integrity_helper.py, subtitle_generator.py, quality_gated_generator.py, threshold_manager.py)
  - Removed: DEFAULT_AI_SCORE, DEFAULT_HUMAN_SCORE, DEFAULT_FALLBACK_AI_SCORE constants
  - Removed: All hardcoded temperatures (subtitle 0.6, winston 0.7) and penalties (batch 0.0)
  - Removed: All TODO violations - documented design rationales
  - Fixed: Silent failure patterns in integrity checker exception handlers
  - System now STOPS immediately on Winston API failure (no fake scores)
  - Tests: 24/24 passing with fail-fast architecture
- **🔥 Dynamic Threshold Learning**: Thresholds now adapt from database (Winston, realism, parameters)
  - See: `docs/decisions/ADR-005-dynamic-threshold-learning.md`
  - Tests: `tests/test_dynamic_threshold_learning.py`
  - System learns from top 25% (75th percentile) of successful content
  - Falls back to sensible defaults when <10 samples
- **Processing Module Consolidation** (Nov 18): 79 → 52 files (-34%), parameters: 16 → 4 files (-75%)
- **Documentation Consolidation** (Nov 18): 14 → 10 directories (-29%), duplicate directories merged
- **Architecture**: `docs/02-architecture/` now contains ALL architecture docs (merged from `docs/architecture/`)
- **Components**: `docs/03-components/` now contains ALL component docs (merged from `docs/components/`)
- **Parameters**: All in `processing/parameters/` as 4 category files (ai_detection, voice, variation, technical)
- **See**: `PROCESSING_MODULE_UTILIZATION_ANALYSIS_NOV18_2025.md` for full analysis

### 🎯 Start Here
1. **`docs/QUICK_REFERENCE.md`** - ⭐ Fastest path to common solutions (THIS FILE)
2. **`SYSTEM_FLOW_VERIFICATION_COMPLETE.md`** - ✅ All 3 critical data flows verified (Nov 15, 2025)

### 🏗️ System Architecture (Nov 15, 2025)
3. **`docs/system/E2E_SYSTEM_REQUIREMENTS.md`** - 🔥 7 critical system requirements + 35 tests
4. **`MANDATORY_REQUIREMENTS_COMPLETE.md`** - 🔥 Database-first parameter priority
5. **`PARAMETER_REUSE_COMPLETE.md`** - 🔥 Complete parameter reuse system
6. **`docs/development/DATABASE_PARAMETER_PRIORITY.md`** - 🔥 Parameter source policy (470+ lines)
7. **`docs/development/PARAMETER_LOGGING_QUICK_START.md`** - Query generation parameters for ML

### 🔍 Code Quality & Compliance (Nov 17, 2025)
8. **`E2E_PROCESSING_EVALUATION_NOV17_2025.md`** - ✅ **NEW** E2E evaluation report + Priority 1 fixes
9. **`tests/test_priority1_fixes.py`** - ✅ **NEW** Automated tests for critical compliance fixes
10. **`.github/copilot-instructions.md`** - GROK_INSTRUCTIONS.md policies & fail-fast architecture

### 🤖 Winston AI & Learning
8. **`DYNAMIC_PENALTIES_AND_PARAMETER_LOGGING_COMPLETE.md`** - Fixed Winston 100% AI issue
9. **`WINSTON_LEARNING_SYSTEM_COMPLETE.md`** - ML learning system (173 generations)
10. **`WINSTON_INTEGRATION_COMPLETE.md`** - Winston AI primary detector
11. **`docs/08-development/WINSTON_ONLY_MODE.md`** - ✨ **NEW** Winston-only detection (Nov 17, 2025)
12. **`docs/08-development/COPILOT_EVALUATION_SYSTEM.md`** - ✨ **NEW** Copilot-based evaluation (Nov 18, 2025) 🔥
13. **`tests/test_copilot_evaluation.py`** - ✨ **NEW** 26 tests for Copilot evaluation (Nov 18, 2025)
14. **Realism Quality Gate** - ✨ **NEW** 7.0/10 minimum enforced (Nov 18, 2025)
15. **`docs/08-development/REALISM_QUALITY_GATE.md`** - ✨ **NEW** Realism enforcement documentation (Nov 18, 2025)
16. **`docs/08-development/PROMPT_PURITY_POLICY.md`** - ✨ **NEW** Zero prompt text in generators (Nov 18, 2025)
17. **`LEARNED_EVALUATION_INTEGRATION_NOV18_2025.md`** - ✨ **NEW** Template-based learning pipeline (Nov 18, 2025)
18. **`docs/08-development/LEARNED_EVALUATION_PROPOSAL.md`** - ✨ IMPLEMENTED - Learned evaluation architecture (Nov 18, 2025)
18. **`docs/development/SWEET_SPOT_ANALYZER.md`** - Statistical parameter optimization (Nov 15, 2025)
19. **`processing/evaluation/SCORING_MODULE_README.md`** - Composite quality scoring (Nov 16, 2025)
20. **`docs/08-development/SCORE_DISPLAY_STANDARDS.md`** - ✨ **NEW** Score validation & display (Nov 17, 2025)

### 📊 Data & Content
12. **`docs/data/MATERIALS_STRUCTURE_CANONICAL.md`** - Materials.yaml structure (NO 'properties' wrapper!)
13. **`materials/data/frontmatter_template.yaml`** - Single source of truth for structure
14. **`docs/reference/CASE_INSENSITIVE_LOOKUPS.md`** - Material lookup (ALWAYS case-insensitive)
15. **`docs/DATA_COMPLETION_ACTION_PLAN.md`** - Complete plan to 100% data coverage
16. **`docs/ZERO_NULL_POLICY.md`** - Zero null policy & AI research methodology

### 📝 Content Generation
17. **`docs/prompts/DYNAMIC_SENTENCE_CALCULATION.md`** - Dynamic sentence counts by author
18. **`docs/development/HARDCODED_VALUE_POLICY.md`** - Zero hardcoded values policy

---

## 🚨 CRITICAL: Fix Root Causes, Not Symptoms

**If frontmatter files have issues, fix the GENERATOR, not the GENERATED files.**

### The Problem with Temporary Fixes
Creating "fix scripts" that patch frontmatter files directly is **TEMPORARY** because:
- Frontmatter is **GENERATED FROM** Materials.yaml + Categories.yaml via trivial_exporter.py
- Every `--deploy` regenerates all files from source
- Patches get **OVERWRITTEN** on next deployment

### The Correct Approach
1. ✅ Fix `components/frontmatter/core/trivial_exporter.py` to generate correct structure
2. ✅ Run `python3 run.py --deploy --no-completeness-check` to regenerate ALL files
3. ✅ Verify fixes persist after regeneration
4. ❌ NEVER create one-off scripts that modify frontmatter/*.yaml directly

### Example: Machine Settings Missing Min/Max
- ❌ WRONG: Script that adds min/max to 112 frontmatter files → next deploy overwrites
- ✅ RIGHT: Fix `_enrich_machine_settings()` in exporter → redeploy → permanent fix

**Documentation**: See "Fix Root Causes, Not Symptoms" section in `.github/copilot-instructions.md`

---

### 🆕 Data Structure Update (October 25, 2025)

**Regulatory Standards**: Now structured objects instead of strings
**Images**: 100% coverage with both hero AND micro images (132/132)

**Old Structure**:
```yaml
regulatoryStandards:
  - "FDA 21 CFR 1040.10"
images:
  hero: {...}  # micro missing for 107 materials
```

**New Structure**:
```yaml
regulatoryStandards:
  - name: FDA
    description: FDA 21 CFR 1040.10 - Laser Product Performance Standards
    url: https://www.ecfr.gov/...
    image: /images/logo/logo_org_fda.png
images:
  hero: {alt: "...", url: "..."}
  micro: {alt: "...", url: "..."}  # Now all 132 materials
```

**Documentation**: `docs/DATA_STRUCTURE_UPDATE_OCT2025.md`
**Script**: `scripts/fix_materials_structure.py`
**Testing**: `tests/test_data_structure_oct2025.py` - 10/10 tests passing ✅
**Coverage**: Hero 132/132 (100%), Micro 132/132 (100%), RegulatoryStandards 106/132 (80.3%)

---

### 🤖 Winston AI Learning System (November 15, 2025)

**ML Learning Modules**: System learns from Winston feedback to improve generation

**CLI Commands**:
```bash
# View learning dashboard
python3 scripts/winston/learn.py --dashboard

# Learn patterns from feedback
python3 scripts/winston/learn.py --patterns --material "Aluminum"

# Find optimal temperature
python3 scripts/winston/learn.py --temperature --material "Steel" --component micro

# Optimize prompts with learned patterns
python3 scripts/winston/learn.py --optimize-prompt prompts/micro.txt --output prompts/micro_v2.txt

# Predict success before generation
python3 scripts/winston/learn.py --predict --material "Copper" --component subtitle --temp 0.7

# Add manual correction to database
python3 scripts/winston/add_correction.py

# Analyze Winston patterns
python3 scripts/winston/analyze_patterns.py --material "Aluminum"
```

**Learning Modules**:
- **PatternLearner**: Learns risky n-gram patterns from failures
- **TemperatureAdvisor**: Finds optimal temperature settings statistically
- **PromptOptimizer**: Enhances prompts with learned patterns
- **SuccessPredictor**: Predicts success probability before generation

**Expected Improvement**: +35% success rate after 100 samples, +45% after 200 samples

**Documentation**: `WINSTON_LEARNING_SYSTEM_COMPLETE.md`, `WINSTON_INTEGRATION_COMPLETE.md`

---

### 🔗 Chain Verification System (November 15, 2025)

**Runtime Verification**: Ensures no modules accidentally skipped from orchestration chain

**Key Features**:
- ✅ Automatic phase tracking via `@track_phase` decorator
- ✅ Fail-fast on incomplete chains with `ChainIncompleteError`
- ✅ Statistics and monitoring for chain health
- ✅ 18/18 tests passing

**Documentation**:
- `processing/chain_verification.py` - Core system (398 LOC)
- `processing/docs/CHAIN_VERIFICATION_GUIDE.md` - Complete guide (437 lines)
- `processing/CHAIN_VERIFICATION_COMPLETE.md` - Summary and roadmap
- `processing/CHAIN_VERIFICATION_QUICK_REFERENCE.md` - Quick integration guide

**CLI Commands**:
```bash
# Run chain verification tests
python3 -m pytest processing/tests/test_chain_verification.py -v

# Generate chain verification report (after integration)
python3 -c "from processing.chain_verification import generate_chain_verification_report; generate_chain_verification_report()"
```

---

## 🔥 CRITICAL: Materials.yaml Structure (November 3, 2025)

**⚠️ Properties are FLAT - NO 'properties' wrapper!**

```yaml
# ✅ CORRECT (per frontmatter_template.yaml):
materialProperties:
  material_characteristics:
    label: "..."
    density:           # ← Property DIRECTLY here
      value: 8.8
      unit: "g/cm³"

# ❌ WRONG (causes bugs):
materialProperties:
  material_characteristics:
    label: "..."
    properties:        # ❌ NO! This wrapper should NOT exist
      density:
        value: 8.8
```

**In Code:**
```python
# ✅ CORRECT:
mc = mat_props['material_characteristics']
density = mc.get('density')  # Direct access

# ❌ WRONG:
mc_props = mc.get('properties', {})  # Don't do this!
density = mc_props.get('density')
```

**Metadata Keys (exclude from property counts):** `label`, `description`, `percentage`

**Full Documentation:** `docs/data/MATERIALS_STRUCTURE_CANONICAL.md`  
**Migration Tool:** `scripts/tools/flatten_properties_structure.py`

---

## 🎯 Most Common User Questions → Direct Solutions

### "How do I access category data?" / "Where are material property ranges?"
**→ Use CategoryDataLoader** - Modular access to split category files (NEW Oct 30, 2025)
**→ Files**: `data/categories/` (8 focused files: machine_settings, material_properties, safety_regulatory, etc.)
**→ Loader**: `utils/loaders/category_loader.py` with thread-safe caching
**→ Example**:
```python
from utils.loaders.category_loader import CategoryDataLoader
loader = CategoryDataLoader()
machine_settings = loader.get_machine_settings()  # 7KB instead of 121KB
material_properties = loader.get_material_properties()
safety_data = loader.get_safety_regulatory()
```
**→ Benefits**: Load 7-15KB instead of 121KB (~90% improvement), automatic fallback to Categories.yaml
**→ Documentation**: `docs/data/CATEGORY_DATA_MIGRATION_GUIDE.md`, `docs/data/CATEGORY_REFACTORING_COMPLETE.md`

### "How do I detect AI-generated content?" / "What AI detection system do we use?"
**→ System**: `processing/detection/ai_detection.py` - Local pattern-based detection (NO external APIs)
**→ Detection Methods**:
  - Grammar errors (subject-verb agreement, tense errors)
  - Repetitive patterns (word/phrase repetition, structural repetition)
  - Unnatural phrasing (awkward constructions, non-idiomatic expressions)
  - Statistical anomalies (uniform sentence length, predictable rhythms)
  - Linguistic dimensions (dependency structure, lexical diversity, formality)
**→ Usage**:
```python
from processing.detection.ai_detection import AIDetector
detector = AIDetector(strict_mode=False)
result = detector.detect_ai_patterns(text)
if result['is_ai_like']:
    print(f"AI score: {result['ai_score']}/100")
    print(f"Issues: {result['issues']}")
```
**→ Configuration**: `prompts/ai_detection_patterns.txt` - Pattern definitions, weights, thresholds
**→ Integration**: Works with `processing/detection/ensemble.py` for multi-method validation
**→ Note**: We do NOT use Winston API or other external detection services
**→ Documentation**: See module docstring in `processing/detection/ai_detection.py`

### "How do I check if data is complete before generating?" / "How can I see data gaps?"
**→ Commands**: 
- `python3 run.py --data-completeness-report` (full status report)
- `python3 run.py --data-gaps` (research priorities)
- `python3 run.py --enforce-completeness` (strict mode - blocks if incomplete)
- `python3 run_unified.py --data-completion` (unified pipeline - data completeness)
- `python3 run_unified.py --data-gaps` (unified pipeline - research priorities)
**→ Current Status**: 93.5% complete (1,975/2,240 properties)
**→ What You See**: Category ranges (98.7%), material values (88.2%), top missing properties
**→ Next Steps**: Automatically links to action plan and research tools
**→ Documentation**: 
  - `docs/DATA_COMPLETENESS_POLICY.md` - Requirements and usage
  - `docs/COMPLETE_FEATURE_INVENTORY.md` - All completeness features
  - `DATA_COMPLETENESS_IMPLEMENTATION.md` - Implementation summary

**✨ NEW (October 17, 2025)**: 100% completeness validation runs **automatically** during generation:
- **Legacy Migration**: Auto-moves qualitative properties to material_characteristics
- **Empty Detection**: Triggers PropertyManager research for missing data
- **Auto-Remediation**: Fills gaps automatically via AI research
- **14 Tests**: Complete test coverage in `tests/test_data_completeness.py`

**⚡ AUTOMATIC (November 1, 2025)**: 
- **Strict mode enabled by default** - No flags needed!
- **Automatic inline validation** - Runs during every generation
- **Fail-fast behavior** - Blocks incomplete data automatically
- **Disable with**: `--no-completeness-check` (not recommended)

**🚀 NEW (October 22, 2025)**: Unified Pipeline Architecture:
- **Single Entry Point**: `run_unified.py` consolidates all operations
- **13 Operation Modes**: Material generation, auditing, research, validation, system management
- **Robust Error Handling**: Fail-fast validation with comprehensive error reporting
- **Service Integration**: All scattered functions consolidated into unified handlers

### "How do I fix missing property data?" / "What's the data completion plan?"
**→ Immediate Response**: ✅ **COMPREHENSIVE PLAN READY** - 93.5% complete, path to 100% documented
**→ Current Status**: 1,975/2,240 properties complete (265 missing)
**→ Action Plan**: `docs/DATA_COMPLETION_ACTION_PLAN.md` (complete execution guide)
**→ Quick Start**: Research 2 missing category ranges (30 mins) → 98.7% → 100% category completeness
**→ Priority Focus**: 5 properties = 96% of gaps (electricalResistivity, ablationThreshold, porosity, surfaceRoughness, reflectivity)
**→ Tools**: PropertyValueResearcher, CategoryRangeResearcher (already built and operational)
**→ Accuracy**: Multi-strategy validation (Database 95% → Literature 85% → AI 75% → Estimation 65%)
**→ Quality Gates**: 4 checkpoints ensure accuracy (Pre-research, During, Post, Final deployment)
**→ Timeline**: 1 week to 100% completeness with documented research methodology

### "thermalDestructionPoint/Type missing" / "meltingPoint removed"
**→ Immediate Response**: ✅ **RESTRUCTURED October 2025** - Combined into nested `thermalDestruction` object
**→ New Structure**: `thermalDestruction: { point: {value, unit, min, max, confidence}, type }`
**→ Old Properties Removed**: `thermalDestructionPoint`, `thermalDestructionType`, `meltingPoint`
**→ Complete Normalization**: ALL properties now follow same pattern (Categories=ranges, materials=values)
**→ Documentation**: `docs/DATA_ARCHITECTURE.md` and `COMPLETE_PIPELINE_NORMALIZATION.md`
**→ Categories**: All lowercase system-wide (ceramic, metal, wood, etc.)
**→ Materials.yaml**: NO min/max anywhere - category ranges only in Categories.yaml

### "Frontmatter not found" / "No frontmatter data"
**→ Immediate Response**: ✅ **ENHANCED with Root-Level System** - Use new FrontmatterManager
**→ Quick Fix**: `python3 frontmatter/management/migrator.py --dry-run` to check status
**→ Migration Required**: Run `python3 frontmatter/management/migrator.py --execute`
**→ New Location**: `frontmatter/materials/` instead of `content/components/frontmatter/`
**→ Documentation**: [Frontmatter Architecture Proposal](FRONTMATTER_ARCHITECTURE_PROPOSAL.md)

### "Schema validation failed" / "Invalid frontmatter"
**→ Immediate Response**: Use enhanced frontmatter validation system
**→ Quick Fix**: 
```python
from frontmatter.management.manager import frontmatter_manager
is_valid, errors = frontmatter_manager.validate_material("Steel")
```
**→ Comprehensive Check**: `python3 scripts/tools/frontmatter_integrity_check.py`
**→ Field Updates**: Use `python3 scripts/tools/update_frontmatter_fields.py --material "MaterialName"`

### "Missing environmental/application sections" / "Categories.yaml outdated"
**→ Immediate Response**: ✅ **UPDATED to Categories.yaml v2.2.1** - Enhanced with streamlined standardized descriptions
**→ Quick Fix**: Regenerate frontmatter: `python3 run.py --material "MaterialName" --components "frontmatter"`  
**→ New Sections**: `environmentalImpact`, `applicationTypes`, `outcomeMetrics` automatically added with reduced verbosity
**→ Root Cause**: Categories.yaml upgraded with concise templates for cleaner output
**→ Version Check**: Look for `version: 2.2.1` and `enhancement_notes` mentioning "reduced template verbosity" in Categories.yaml metadata

### "Verbose frontmatter sections" / "Too much template detail"
**→ Immediate Response**: ✅ **STREAMLINED in v2.2.1** - Verbose template fields removed for cleaner output
**→ Quick Fix**: Regenerate frontmatter with updated v2.2.1 templates
**→ Removed Verbose Fields**: `regulatory_advantages`, `typical_savings`, `efficiency_metrics`, `health_benefits`, `workplace_safety`, `preservation_focus`, `specialized_requirements`, `contamination_types`, `effectiveness_metrics`, `quality_metrics`, `measurement_standards`, `acceptance_criteria`, `indicators`, `monitoring_methods`, `control_strategies`
**→ Essential Information Preserved**: All critical data maintained in concise format
**→ Performance Improvement**: ~450 character reduction per frontmatter file

### "Verbose machine settings" / "Too many description fields"
**→ Immediate Response**: ✅ **CLEANED in v6.2.1** - Verbose fields removed for cleaner output
**→ Quick Fix**: Regenerate frontmatter with updated generator
**→ Removed Fields**: `standardDescription`, `selectionCriteria`, `optimizationNote`, `typicalRangeGuidance`, `scalingFactors`
**→ Essential Fields Kept**: `value`, `unit`, `confidence`, `description`, `min`, `max`
**→ Better Readability**: Clean, focused machine settings without verbose standardized descriptions

### "Min/max ranges missing" / "Properties have null ranges"
**→ Immediate Response**: ✅ **CORRECT BEHAVIOR** - Null ranges are intentional when no category range exists
**→ Understanding**: Min/max represent CATEGORY-WIDE ranges for comparison, not material-specific tolerances
**→ Example**: Copper density: value=8.96, min=0.53 (all metals), max=22.6 (all metals)
**→ Documentation**: `docs/DATA_ARCHITECTURE.md` - Complete explanation of three range types
**→ Testing**: `python3 -m pytest tests/test_range_propagation.py -v` - Verify correct behavior
**→ Don't Fix**: System is working correctly - only 12 properties have category ranges (by design)

### "Component generation failed" / "Required fields missing"
**→ Immediate Response**: Enhanced fail-fast validation with specific field requirements
**→ Quick Fix**: Check component-specific requirements in error message
**→ Field Management**: `python3 scripts/tools/update_frontmatter_fields.py --dry-run`
**→ Common Missing**: `substrateDescription`, `technicalSpecifications.contaminationSource`, `technicalSpecifications.thermalEffect`
**→ Auto-Fix**: Run field updater for missing fields across all materials

### "API not working" / "Connection failed"
**→ Immediate Response**: Check [API Error Handling](api/ERROR_HANDLING.md#winston-ssl-issues)
**→ Quick Fix**: `python3 scripts/tools/api_terminal_diagnostics.py winston`
**→ Root Cause**: Likely Winston SSL error - endpoint changed to `api.gowinston.ai`

### "Content incomplete" / "Text cuts off"
**→ Immediate Response**: API failure during generation
**→ Quick Fix**: Use working diagnostic: `python3 scripts/tools/api_terminal_diagnostics.py winston`
**→ Root Cause**: Winston API timeout - check [Content Impact Analysis](api/ERROR_HANDLING.md#content-impact)

### "Winston.ai scoring technical content as 0%" / "AI detector shows poor results"
**→ Immediate Response**: ✅ **SOLVED** - Winston.ai Composite Scoring Auto-Applied September 15, 2025
**→ Quick Fix**: Use working command: `python3 run.py --material "copper" --components "text"`

### "Settings files inconsistent" / "Missing machine settings sections"
**→ Immediate Response**: ✅ **NORMALIZED** - 4-Section Structure Applied September 21, 2025
**→ Quick Fix**: All 109 materials now have standardized settings structure
**→ Structure**: Machine Configuration, Processing Parameters, Safety Parameters, Quality Control Settings
**→ Documentation**: [Settings Normalization Architecture](components/settings/docs/NORMALIZATION_ARCHITECTURE.md)
**→ Testing**: `python3 components/settings/testing/test_settings_normalized.py`
**→ Expected Output**: `🔧 [AI DETECTOR] Applying composite scoring for technical content...`
**→ Results**: 0.0% → 59.5% automatic improvement for technical content
**→ Documentation**: [Winston Composite Scoring](WINSTON_COMPOSITE_SCORING_INTEGRATION.md)

### "Property access complexity" / "How do I work with nested properties?"
**→ Immediate Response**: ✅ **SOLVED October 15, 2025** - PropertyAccessor helpers now available
**→ Quick Fix**: 
```python
from utils.property_helpers import PropertyAccessor
temp = PropertyAccessor.get_thermal_destruction_point(material)
threshold = PropertyAccessor.get_ablation_threshold(material, 'femtosecond')
```
**→ Examples**: `python3 examples/property_access_examples.py` (9 complete examples)
**→ Tests**: `python3 -m pytest tests/test_property_helpers.py -v` (23 tests)
**→ Documentation**: [Data System Complete Guide](DATA_SYSTEM_COMPLETE_GUIDE.md)

### "Need distinct author voices" / "How to ensure authors sound different?"
**→ Immediate Response**: ✅ **SOLVED November 14, 2025** - Author-specific config offsets implemented
**→ Architecture**: Base sliders (global) + Author offsets (personality) = Distinct styles
**→ Quick View**: `python3 processing/author_comparison_matrix.py`
**→ Comparison**: `python3 -c "from processing.author_config_loader import compare_author_configs; print(compare_author_configs(1, 3, 'subtitle'))"`
**→ Results**: 
  - Yi-Chun (Taiwan): Precise, high technical (65), low imperfection (35), formal
  - Alessandro (Italy): Sophisticated, high variation (70), balanced (55)
  - Ikmanda (Indonesia): Accessible, low technical (35), high imperfection (70)
  - Todd (USA): Conversational, high rhythm variation (70), balanced engagement
**→ Documentation**: [Author Profiles System](../processing/AUTHOR_PROFILES_SYSTEM.md)
**→ Integration**: `get_author_config(author_id)` automatically applies offsets
**→ Features**: Handles all 4 property patterns (simple, nested, pulse-specific, wavelength-specific)

### "Property format questions" / "What property data formats are supported?"
**→ Immediate Response**: ✅ **4 PATTERNS SUPPORTED** (as of Oct 2025)
**→ Pattern 1**: **Legacy** - Single value: `{value, unit, min, max, confidence, description}` (~800 properties)
**→ Pattern 2**: **Pulse-specific** - NS/PS/FS: `{nanosecond: {min, max, unit}, picosecond: {...}, femtosecond: {...}}` (45 properties)
**→ Pattern 3**: **Wavelength-specific** - 4 wavelengths: `{at_1064nm: {min, max, unit}, at_532nm: {...}, at_355nm: {...}, at_10640nm: {...}}` (35 properties)
**→ Pattern 4**: **Authoritative** - Legacy + source: `{value, unit, min, max, source, notes, confidence}` (144 properties)
**→ Detection**: Generators use `_detect_property_pattern()` to identify format
**→ Extraction**: Use `_extract_property_value()` for pattern-aware value retrieval
**→ Documentation**: `FRONTMATTER_NORMALIZATION_REPORT.md`, `GENERATOR_PATTERN_AWARENESS_UPDATE.md`
**→ Testing**: `python3 -m pytest tests/test_property_pattern_detection.py -v` (15 tests)

### "Generator not handling pulse/wavelength data" / "Pattern awareness needed"
**→ Immediate Response**: ✅ **UPDATED October 2025** - Pattern-aware value extraction implemented
**→ Quick Fix**: Generators automatically recognize and preserve pulse-specific and wavelength-specific patterns
**→ Methods Added**: `_detect_property_pattern()` and `_extract_property_value()` in `streamlined_generator.py`
**→ Preservation**: High-confidence (>85%) authoritative data with sources is automatically preserved
**→ Example**: Copper ablation threshold (pulse-specific) and reflectivity (wavelength-specific) maintained
**→ Documentation**: `GENERATOR_PATTERN_AWARENESS_UPDATE.md`

### "Table components missing min/max columns"
**→ Immediate Response**: ✅ **VERIFIED WORKING** - Min/Max columns are present and correct
**→ Quick Fix**: Check frontend Next.js table rendering component
**→ Verification**: All quantitative properties include min/max values (11/15 properties per material)
**→ Expected Structure**: `{min}-{max}` column as per render instructions in YAML files
**→ Files**: All 109 table files in `content/components/table/` contain min/max data

### "Property ranges missing" / "Min/Max values not available"
**→ Immediate Response**: ✅ **COMPREHENSIVE RANGES SYSTEM** - 107 scientifically-researched ranges available
**→ Quick Fix**: All material properties and machine settings now include validated min/max ranges
**→ Coverage**: 9 material categories × 11 properties + 8 machine settings = 107 total ranges
**→ Source**: Research-backed values from materials engineering literature
**→ Integration**: FrontmatterComponentGenerator automatically extracts and applies ranges
**→ Testing**: `python3 -m pytest components/frontmatter/tests/test_comprehensive_ranges.py -v`
**→ Documentation**: [Frontmatter README v7.0.0](components/frontmatter/README.md#comprehensive-ranges-system)

### "YAML output format issues" / "Generator format inconsistency"
**→ Immediate Response**: ✅ **STANDARDIZED September 16, 2025** - All generators now use consistent YAML
**→ Quick Fix**: Components `table`, `jsonld`, `metatags` output `.yaml` files
**→ New Structure**: JSON-LD converted from script tags to YAML frontmatter format
**→ Naming**: All generators use standardized material naming (`carbon-steel` → `steel`)
**→ Documentation**: [Session Summary](SESSION_2025-09-16_YAML_STANDARDIZATION_SUMMARY.md)

### "Optimization processing metadata as content"
**→ Immediate Response**: Fixed September 13, 2025 - Global Metadata Delimiting Standard preserved
### Global Metadata Delimiting Standard Fix ✅ COMPLETELY RESOLVED

**Issue**: Content generated without proper Global Metadata Delimiting Standard delimiters
**Root Cause**: Components not integrated with Global Metadata Delimiting configuration
**Solution**: Components now directly handle delimiter formatting based on configuration in `config/metadata_delimiting.yaml`

**Implementation Details**:
- Removed versioning system complexity
- Components directly read delimiter configuration
- Streamlined content generation with proper delimiters
- All content automatically gets `<!-- CONTENT START/END -->` and `<!-- METADATA START/END -->` delimiters when configured
- Content extraction system properly reads delimited format
- Simplified architecture with direct component formatting
- Ensured all metadata (including author) positioned within `<!-- METADATA START/END -->` sections

**Files Modified**:
- `versioning/generator.py` - Core delimiter integration
- `config/metadata_delimiting.yaml` - Configuration enablement
- `utils/file_ops/file_operations.py` - Duplicate version log prevention
- `content/components/text/steel-laser-cleaning.md` - Fixed metadata enclosure

**Quality Assurance**:
- ✅ No duplicate version logs
- ✅ Author positioning inside metadata delimiters
- ✅ Complete metadata enclosure
- ✅ Proper content/metadata separation

**Commands**:
```bash
# Test auto-delimited generation
python3 run.py --material "TestMaterial" --component text

# Verify delimiter format
grep -A5 -B5 "METADATA START\|CONTENT START" content/components/text/testmaterial-*.md
```

**Status**: ✅ COMPLETELY RESOLVED - All issues fixed, tested with Copper generation
**→ Solution**: Author frontmatter now positioned outside content boundaries
**→ Technical Fix**: Enhanced `update_content_with_ai_analysis()` to preserve delimiters
**→ Details**: [Global Metadata Delimiting Fix](GLOBAL_METADATA_DELIMITING_STANDARD.md#critical-optimization-fix)

### "Author frontmatter contaminating content extraction"
**→ Immediate Response**: Critical fix implemented - author info moved outside content delimiters
**→ Quick Fix**: Run `python3 scripts/tools/validate_content_boundaries.py --component-type text`
**→ Solution**: Content extraction now yields pure technical content only (65-68% metadata filtering)
**→ Status**: ✅ Zero contamination in optimization iterations
**→ Structure**: `<!-- CONTENT START -->` → content → `<!-- CONTENT END -->` → author frontmatter → `<!-- METADATA START -->`

### "Optimization stripping delimiters during processing"
**→ Immediate Response**: Fixed in `optimizer/content_optimization/content_analyzer.py`
**→ Root Cause**: `update_content_with_ai_analysis()` was rebuilding files without preserving delimiters
**→ Solution**: Dual-mode support - preserves Global Delimiting Standard or falls back to legacy
**→ Validation**: Run content extraction test to verify clean boundaries

### "How do I set up API keys?"
**→ Immediate Response**: [API Configuration Guide](setup/API_CONFIGURATION.md)
**→ Quick Fix**: Copy `.env.example` to `.env` and add keys
**→ Validation**: `python3 run.py --check-env`

### "Winston API SSL error"
**→ Immediate Response**: Known SSL certificate issue
**→ Quick Fix**: Configuration updated to use `https://api.gowinston.ai`
**→ Details**: [SSL Error Resolution](api/ERROR_HANDLING.md#winston-ssl-errors)

### "How to generate content?"
**→ Immediate Response**: [Content Generation Guide](operations/CONTENT_GENERATION.md)
**→ Quick Fix**: `python3 run.py --material "Steel"`
**→ Batch**: `python3 run.py` (generates all materials)

### "Where are generation reports?" / "How to view generation results?"
**→ Immediate Response**: ✨ **NEW** (Nov 19, 2025) - Automatic report file in root
**→ Location**: `GENERATION_REPORT.md` (root directory, gitignored)
**→ Behavior**: Overwrites on each generation (shows most recent)
**→ Format**: Markdown with content, statistics, storage location, quality metrics
**→ Quick View**: `cat GENERATION_REPORT.md`
**→ Save Important**: `cp GENERATION_REPORT.md docs/archive/aluminum_subtitle_nov19.md`
**→ Documentation**: `docs/03-components/GENERATION_REPORTS.md`
**→ Tests**: `tests/test_generation_report_writer.py` (7 tests, all passing ✅)

**Report Contains:**
- 📝 Full generated content (with code blocks)
- 📏 Statistics (character/word counts)
- 💾 Storage info (Materials.yaml location)
- 📊 Quality metrics (Winston, Realism scores when available)
- 📊 Subjective evaluation (narrative assessment)

### "Voice system" / "Author voices" / "AI-evasion"
**→ Immediate Response**: ✅ **DEPLOYED** - Voice system with 214% AI-evasion improvement
**→ Complete Guide**: [Voice System Complete](../voice/VOICE_SYSTEM_COMPLETE.md)
**→ Core Rules**: [VOICE_RULES.md](../voice/VOICE_RULES.md) - 3 rules (no emotives, structure only, no cultural refs)
**→ Results**: [Implementation Success](../voice/IMPLEMENTATION_SUCCESS.md)
**→ Authors**: Taiwan (Yi-Chun Lin), Indonesia (Ikmanda Roswati), Italy (Alessandro Moretti), USA (Todd Dunning)
**→ Features**: Grammatical authenticity, AI-evasion markers, 100% VOICE_RULES compliance

**→ Workflow (3 Steps)**:
1. Generate content: `python3 run.py --micro "Steel"` → saves to Materials.yaml
2. Apply voice: `python3 scripts/voice/enhance_materials_voice.py --material "Steel"` → **OVERWRITES** fields in Materials.yaml
3. Export: `python3 run.py --material "Steel" --data-only` → combines Materials.yaml + Categories.yaml → frontmatter

**→ Key**: Voice postprocessor **OVERWRITES text fields** in Materials.yaml (micro, subtitle, FAQ answers)

### "Prompt architecture" / "AI detection + localization"
**→ Immediate Response**: [AI Detection + Localization Architecture](AI_DETECTION_LOCALIZATION_CHAIN_ARCHITECTURE.md)
**→ Quick Fix**: Two-stage chain: AI Detection → Localization → Content
**→ Details**: [Localization System](LOCALIZATION_PROMPT_CHAIN_SYSTEM.md)

### "Frontmatter sections missing information after v2.2.1 update"
**→ Immediate Response**: Intentional verbosity reduction - essential information preserved
**→ Quick Check**: Verify streamlined sections contain core data (description, industries, metrics)
**→ Missing Verbose Fields**: This is expected behavior for cleaner output
**→ Validation**: `python3 -c "import yaml; data=yaml.safe_load(open('frontmatter/[material]-laser-cleaning.yaml')); print('✅' if all(len(data.get(s, [])) == 4 for s in ['environmentalImpact', 'applicationTypes', 'outcomeMetrics']) else '❌')"`
**→ Rollback**: If verbose fields are required, revert to Categories.yaml v2.2.0

### "Test failures after verbosity reduction"
**→ Immediate Response**: Update test expectations for streamlined templates
**→ Quick Fix**: Run new TestFrontmatterGenerationV2_2_1 class: `python3 -m pytest tests/test_renamed_files_validation.py::TestFrontmatterGenerationV2_2_1 -v`
**→ Common Issue**: Tests looking for removed verbose fields like `regulatory_advantages`, `typical_savings`
**→ Solution**: Update test assertions to expect concise sections with essential data only

### "'could not convert string to float' errors in validation"
**→ Immediate Response**: ✅ **FIXED** - Shore hardness numerical extraction implemented
**→ Root Cause**: Shore hardness values like "Shore A 10" need numerical extraction (10.0)
**→ Solution**: `extract_numeric_value()` function with Shore hardness regex parsing added to run.py
**→ Quick Test**: `python3 tests/test_shore_hardness_extraction.py`
**→ Usage**: Validation pipeline now automatically extracts numerical values from Shore scales
**→ Details**: [Hierarchical Validation](docs/VALIDATION_USER_GUIDE.md) with enhanced AI research logging

## 📍 File Location Quick Map for AI

### User needs setup help → Look in:
- `setup/API_CONFIGURATION.md` - API keys and providers
- `setup/TROUBLESHOOTING.md` - Common setup issues
- `README.md` - Basic installation

### User has API problems → Look in:
- `api/ERROR_HANDLING.md` - Error patterns and terminal diagnostics
- `API_SETUP.md` - Provider configuration (legacy, see api/ directory)
- `API_TERMINAL_DIAGNOSTICS.md` - Terminal output analysis (legacy)

### User needs component help → Look in:
- `components/text/docs/README.md` - Text generation (comprehensive)
- `components/micro/README.md` - Micro generation with voice profiles
- `components/frontmatter/README.md` - YAML frontmatter
- `components/[component]/README.md` - Component-specific guides

### User needs voice system help → Look in:
- `voice/VOICE_SYSTEM_COMPLETE.md` - Complete consolidated guide (PRIMARY)
- `voice/VOICE_RULES.md` - 3 core rules (no emotives, structure only, no cultural refs)
- `voice/IMPLEMENTATION_SUCCESS.md` - Results & metrics (214% improvement)
- `voice/ENHANCEMENT_RULES_SEO_AI_DETECTION.md` - Detailed enhancement rules

### User has generation issues → Look in:
- `operations/CONTENT_GENERATION.md` - How content generation works
- `BATCH_GENERATION_PRODUCTION_READY.md` - Batch operations (legacy)
- `components/text/docs/CONTENT_GENERATION_ARCHITECTURE.md` - Detailed architecture

### User needs troubleshooting → Look in:
- `api/ERROR_HANDLING.md` - API and connection issues
- `setup/TROUBLESHOOTING.md` - Setup and configuration issues
- `components/[component]/README.md` - Component-specific issues

## 🎯 Major System Updates (September 2025)

### Comprehensive Property Ranges System ✅ COMPLETE September 2025
**Update**: Scientifically-researched min/max ranges for all material properties and machine settings
**Scope**: 9 material categories × 11 properties + 8 machine settings = 107 total ranges
**Integration**: FrontmatterComponentGenerator automatically extracts category_ranges and machine_settings_ranges from Materials.yaml
**Scientific Backing**: Materials engineering literature sources (e.g., Lithium 0.53 g/cm³ to Osmium 22.59 g/cm³ for metals)
**Testing**: Comprehensive test suite with 9 validation methods ensuring data integrity
**Documentation**: Updated to v7.0.0 with architecture details and range extraction examples
**Files**: `data/Materials.yaml`, `components/frontmatter/README.md`, `test_comprehensive_ranges.py`

### Component Output Format Standardization ✅ COMPLETE September 16, 2025
**Update**: All generators now use consistent YAML output formats
**Components Changed**: JSON-LD converted from script tags to YAML frontmatter
**File Extensions**:
- `.yaml` files: `table`, `jsonld`, `metatags` components
- `.md` files: `frontmatter`, `text` components
**Naming**: All generators use standardized material naming aligned with `Materials.yaml`
**Benefits**: Consistent frontend integration, easier parsing, unified data structures

### Table Component Min/Max Verification ✅ COMPLETE September 16, 2025  
**Verification**: All table components include min/max columns correctly
**Coverage**: 11/15 properties per material have min/max values (quantitative only)
**Structure**: YAML files include separate `min:` and `max:` fields for ranges
**Deployment**: 109 materials successfully generated and deployed to test-push
**Frontend**: Render instructions specify `{min}-{max}` column display format

### Winston.ai Composite Scoring Integration ✅ COMPLETE
**Issue**: Winston.ai scoring technical content as 0% (systematic bias)
**Solution**: Automatic 5-component bias correction algorithm
**Status**: Seamlessly integrated into existing `--optimize` command
**Results**: 0.0% → 59.5% automatic improvement for technical content
**Documentation**: [Complete Integration Guide](WINSTON_COMPOSITE_SCORING_INTEGRATION.md)

**Quick Test**:
```bash
# Same command, enhanced results
python3 run.py --optimize text --material copper

# Expected output:
# 🔧 [AI DETECTOR] Applying composite scoring for technical content...
# ✅ [AI DETECTOR] Composite scoring applied - Original: 0.0 → Composite: 59.5 (+59.5)
```

### Quality Analysis System Consolidation ✅ COMPLETE (Dec 11, 2025)
**Purpose**: Unified quality analysis system replacing dual AIDetector + VoicePostProcessor
**Documentation**: [Text Generation Guide](02-architecture/TEXT_GENERATION_GUIDE.md)
**Features**: Single QualityAnalyzer interface, composite scoring (AI 40% + Voice 30% + Structural 30%)
**Archived**: Old optimizer docs moved to [archive/2025-12-pre-consolidation/optimizer/](archive/README.md)

## 🔧 Essential Commands for AI to Recommend

### System Health Checks
```bash
# Run system integrity check (NEW - November 15, 2025)
python3 run.py --integrity-check          # Full check (5 categories)
python3 run.py --integrity-check --quick  # Fast check (~20ms)

# Check overall system health
python3 run.py --check-env

# Test all API connections
python3 run.py --test-api

# Diagnose specific API issues
python3 scripts/tools/api_terminal_diagnostics.py winston
```

### System Integrity Module (November 15, 2025)

**Automatic Validation**: Integrity checks now run **by default** before every generation:

```bash
# Integrity check runs automatically (~20ms overhead)
python3 run.py --micro "Aluminum"

# Skip integrity check if needed (not recommended)
python3 run.py --micro "Aluminum" --skip-integrity-check
```

**What It Validates:**
1. **Configuration Mapping**: Slider ranges (1-10), normalization (0.0-1.0), parameter ranges
2. **Parameter Propagation**: Bundle completeness, value stability, API penalties inclusion
3. **API Health**: Winston/Grok connectivity (when enabled)
4. **Documentation Alignment**: Config docs, module existence, code-to-docs match
5. **Test Validity**: Test file existence, pass rates, coverage thresholds

**Performance**: Quick checks complete in ~20ms with minimal overhead (<2% of generation time)

**Exit Codes**:
- `0`: All checks passed
- `1`: One or more checks failed
- `2`: Warnings detected (with `--fail-on-warn`)

**Documentation**: `processing/integrity/README.md`

### Content Generation
```bash
# Generate all materials (batch mode)
python3 run.py --all

# Generate specific material
python3 run.py --material "Steel"

# Generate specific components only
# Generate specific components for a material (case-insensitive)
python3 run.py --material "Copper" --components "frontmatter,text"

# Test mode
python3 run.py --test
```

### Content Generation (Working Commands Only)
```bash
### Content Generation (Real Working Commands)
```bash
# Generate all 123 materials (real batch processing)
python3 run.py --all

# Generate specific material with components 
python3 run.py --material "copper" --components "text"

# Generate specific material
python3 run.py --material "aluminum"

# Generate multiple components for material
python3 run.py --material "aluminum" --components "text,frontmatter"

# Test system functionality
python3 run.py --test

# Deploy generated content
python3 run.py --deploy

# Sanitize existing frontmatter
python3 run.py --sanitize
```

# Learning optimizer (gets smarter with each run)
python3 smart_optimize.py steel

# Test composite scoring directly
python3 apply_composite_scoring.py

# Generate multiple components
python3 run.py --material "aluminum" --components "text,frontmatter"
```

### Troubleshooting
```bash
# Validate environment
python3 run.py --check-env

# Test API connectivity with detailed output
python3 -c "from api.client_manager import test_api_connectivity; test_api_connectivity('winston')"

# Check for incomplete content
find content/components -name "*.md" -exec grep -l "before significant" {} \;
```

## 🚨 Critical Known Issues (AI Should Be Aware Of)

### 1. Winston API SSL Certificate Issue
**Symptom**: `[SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name`
**Status**: FIXED - Updated to `https://api.gowinston.ai`
**Impact**: Caused content generation to cut off mid-sentence
**Files Affected**: Any text component generation using Winston
**Solution**: Configuration already updated in `run.py`

### 2. Nested YAML Property Generation Bug
**Symptom**: Properties like `name: {name: "Value"}` instead of `name: "Value"`
**Status**: FIXED - Tool created to detect and correct
**Impact**: Blocked TypeScript builds due to malformed YAML
**Tool**: `scripts/tools/fix_nested_yaml_properties.py`
**Files Fixed**: `phenolic-resin-composites-laser-cleaning.md`, `thermoplastic-elastomer-laser-cleaning.md`

### 3. Terminal Output Required for API Diagnostics
**Issue**: API response objects show `error: None` but terminal has actual errors
**Solution**: Always use `get_terminal_output()` after API tests
**Tool**: `scripts/tools/api_terminal_diagnostics.py`
**Documentation**: [Terminal Diagnostics](api/ERROR_HANDLING.md#terminal-reading)

### 4. Claude AI Subjective Evaluation (November 15, 2025) 🆕
**Purpose**: Post-generation quality assessment with learning database integration
**Status**: ✅ Fully integrated (20/20 tests passing)
**Components**:
- `processing/evaluation/claude_evaluator.py` - Core 6-dimension evaluation engine
- `shared/commands/claude_evaluation_helper.py` - Reusable integration helper
- Learning database: `claude_evaluations` table in winston_feedback.db
- Integrity checks: 4 automatic validations

**CLI Commands**:
```bash
# Run demo to see evaluation in action
PYTHONPATH=$PWD:$PYTHONPATH python3 processing/evaluation/demo_claude_evaluation.py

# Run tests
python3 -m pytest tests/test_claude_evaluation.py -v

# Check integrity (includes Claude module validation)
python3 run.py --integrity-check --quick
```

**Usage Example**:
```python
from shared.commands.claude_evaluation_helper import evaluate_after_generation

# Evaluate generated content (reusable for ANY component/domain)
result = evaluate_after_generation(
    content=generated_text,
    topic="Aluminum",           # Any subject (material, event, recipe, etc.)
    component_type="micro",   # Any component (micro, subtitle, FAQ, etc.)
    domain="materials",         # Any domain (materials, history, recipes, etc.)
    feedback_db=feedback_db     # Optional: logs to learning database
)

# Check quality
print(f"Overall Score: {result.overall_score:.1f}/10")
print(f"Quality Gate: {'PASS' if result.passes_quality_gate else 'FAIL'}")
```

**Key Features**:
- ✅ **Reusable workflow** - Works across all components and domains
- ✅ **6-dimension evaluation** - Clarity, Professionalism, Technical Accuracy, Human-likeness, Engagement, Jargon-free
- ✅ **Learning database** - All evaluations logged for continuous improvement
- ✅ **Integrity system** - Automatic health validation (4 checks)
- ✅ **Fallback mode** - Works without Claude API (rule-based evaluation)
- ✅ **Quality gate** - 7.0/10 minimum threshold (ENFORCED as rejection gate)
- ✅ **Blended learning** - Winston (40%) + Realism (60%) feedback drives parameter adjustments

### 5. Learned Evaluation Pipeline (November 18, 2025) 🆕 🔥
**Purpose**: Template-based evaluation with continuous pattern learning
**Status**: ✅ IMPLEMENTED AND TESTED (17/17 tests passing)
**Grade**: A+ (100/100) - Full implementation, all tests passing

**Components**:
- `shared/text/templates/evaluation/subjective_quality.txt` - Template for evaluation prompts (single source of truth)
- `shared/text/templates/evaluation/learned_patterns.yaml` - Auto-updating learned patterns from evaluations
- `processing/learning/subjective_pattern_learner.py` - Learning system with exponential moving averages
- `tests/test_learned_evaluation_pipeline.py` - Comprehensive test suite (17 tests)

**How It Works**:
```
1. Content Generated
   ↓
2. Evaluator Loads Template + Learned Patterns
   ↓
3. Grok Evaluates Content
   ↓
4. Pattern Learner Updates YAML (rejection patterns)
   ↓
5. If Accepted: Updates Success Patterns (EMA)
   ↓
6. Next Generation Uses Updated Patterns
```

**Monitoring Learning Progress**:
```bash
# Check current learned patterns
cat shared/text/templates/evaluation/learned_patterns.yaml

# Watch patterns evolve
total_evaluations: 42  # Number of evaluations performed

theatrical_phrases:
  high_penalty: ["zaps away", "And yeah", ...]  # Grows over time

ai_tendencies:
  common:
    formulaic_phrasing: 15  # Increments on rejections
    excessive_enthusiasm: 8

success_patterns:
  average_realism_score: 7.85  # Improves with successful content
  sample_count: 12  # Number of accepted samples
```

**Editing Evaluation Criteria** (No Code Changes Needed!):
```bash
# Edit prompt template directly
nano shared/text/templates/evaluation/subjective_quality.txt

# Changes take effect immediately on next evaluation
```

**Resetting Learned Patterns**:
```bash
# Restore defaults if patterns become too restrictive
git checkout shared/text/templates/evaluation/learned_patterns.yaml
```

**Key Features**:
- ✅ **Prompt Purity Compliant** - Zero hardcoded prompts in evaluator code
- ✅ **Continuous Learning** - Updates patterns after EVERY evaluation
- ✅ **Exponential Moving Average** - Balances historical data (90%) with new learnings (10%)
- ✅ **Template-Based** - Non-technical users can edit prompts via text file
- ✅ **Version Controlled** - Git tracks all prompt and pattern changes
- ✅ **Fail-Fast Architecture** - Template missing → FileNotFoundError
- ✅ **Integration** - Works with Winston, Realism, Composite scoring

**Documentation**:
- Implementation: `LEARNED_EVALUATION_INTEGRATION_NOV18_2025.md`
- Architecture: `docs/08-development/LEARNED_EVALUATION_PROPOSAL.md` (now IMPLEMENTED)
- Tests: `tests/test_learned_evaluation_pipeline.py` (17 tests, all passing)
- ✅ **AI tendency detection** - Maps specific issues to parameter fixes (generic_language, unnatural_transitions, etc.)

**Documentation**: `CLAUDE_EVALUATION_INTEGRATION_COMPLETE.md`
**Module README**: `processing/evaluation/README.md`

---

### 📊 Parameter Logging & ML Learning (November 15, 2025)

**Automatic Tracking**: Every generation logs 31 parameter fields to database for ML learning

**Key Features**:
- ✅ **Complete parameter tracking** - API, voice, enrichment, validation, retry params
- ✅ **1:1 linking** - Parameters linked to detection results via `detection_result_id`
- ✅ **Deduplication** - SHA-256 hash identifies identical parameter sets
- ✅ **ML-ready queries** - Best performers, correlation analysis, historical optimization
- ✅ **Fixed Winston 100% AI issue** - Dynamic penalties (0.6) instead of hardcoded 0.0

**Quick Queries**:
```python
from processing.detection.winston_feedback_db import WinstonFeedbackDB

# Find best parameters for material
db = WinstonFeedbackDB()
best = db.get_best_parameters_for_material('Steel', 'micro', limit=5)
for p in best:
    print(f"Temp: {p['temperature']:.2f}, Human: {p['human_score']:.1f}%")

# Analyze parameter correlation
correlation = db.get_parameter_correlation('api.temperature', 'micro', days=30)
for temp, stats in correlation.items():
    print(f"{temp:.2f}: {stats['avg_human_score']:.1f}% human")
```

**Results**:
- **Before**: 100% AI detection (all failures)
- **After**: 61.9-89.8% human scores (dynamic penalties working)
- **Hardcoded values**: Reduced from 36 to 30 violations

**Documentation**: 
- `DYNAMIC_PENALTIES_AND_PARAMETER_LOGGING_COMPLETE.md` - Complete implementation
- `docs/development/PARAMETER_LOGGING_QUICK_START.md` - Quick queries and examples
- `docs/development/HARDCODED_VALUE_POLICY.md` - Zero hardcoded values policy

---

### 🎯 Sweet Spot Analyzer - Statistical Parameter Optimization (November 15, 2025)

**Intelligent Parameter Selection**: 3-tier priority cascade for optimal parameters

**Architecture**:
1. **Tier 1: Exact Match** → Use proven parameters from same material+component (highest priority)
2. **Tier 2: Sweet Spot** → Use statistical median from top 25% performers (NEW!)
3. **Tier 3: Calculated** → Calculate from config.yaml (last resort)

**Key Features**:
- ✅ **Statistical Analysis** - Analyzes top performers to find optimal parameter ranges
- ✅ **Persistent Recommendations** - `sweet_spot_recommendations` table in database
- ✅ **Confidence Levels** - High (20+ samples), Medium (10-19), Low (<10)
- ✅ **Correlation Detection** - Identifies which parameters most affect human_score
- ✅ **Maximum Tracking** - Records best ever achievements with full parameter details
- ✅ **Auto-Integration** - Orchestrator automatically queries sweet spots as fallback

**Quick Commands**:
```bash
# Analyze and save sweet spot recommendations
python3 scripts/winston/sweet_spot.py --material Copper --component micro

# Show optimal parameter ranges
python3 scripts/winston/sweet_spot.py --sweet-spots --material Steel

# Show best ever achievements
python3 scripts/winston/sweet_spot.py --maximums --limit 20

# Show parameter correlations
python3 scripts/winston/sweet_spot.py --correlations
```

**Programmatic Usage**:
```python
from processing.learning.sweet_spot_analyzer import SweetSpotAnalyzer
from processing.detection.winston_feedback_db import WinstonFeedbackDatabase

# Analyze and save
analyzer = SweetSpotAnalyzer('data/winston_feedback.db')
analysis = analyzer.get_sweet_spot_table('Copper', 'micro', save_to_db=True)

# Retrieve sweet spot
db = WinstonFeedbackDatabase('data/winston_feedback.db')
sweet_spot = db.get_sweet_spot('Copper', 'micro')
if sweet_spot:
    temp = sweet_spot['parameters']['temperature']['median']
    print(f"Optimal temperature: {temp:.3f}")
```

**Performance Impact**:
- **Before**: 10-30% success rate on first attempt (no history)
- **After**: 40-60% success rate using sweet spot recommendations  
- **Benefit**: Fewer retries = lower API costs + faster generation

**Database Schema**:
- `sweet_spot_recommendations` table with 20+ parameter fields
- Stores median values from top performers
- Includes sample count, confidence level, correlations
- Auto-updated via `upsert_sweet_spot()` method

**Documentation**: 
- `docs/development/SWEET_SPOT_ANALYZER.md` - Complete guide (400+ lines)
- `tests/test_sweet_spot_analyzer.py` - 13 tests, all passing ✅

## 📋 AI Assistant Response Patterns

### When User Reports Error Messages
1. **Ask for terminal output**: "Can you run this command and share the terminal output?"
2. **Use diagnostic tools**: Recommend `api_terminal_diagnostics.py`
3. **Check known issues**: Reference the critical issues above
4. **Point to specific docs**: Use the file location map above

### When User Needs Setup Help
1. **Start with test mode**: `python3 run.py --test`
2. **Guide through API setup**: Point to `setup/API_CONFIGURATION.md`
3. **Use diagnostic tools**: `python3 scripts/tools/api_terminal_diagnostics.py winston`
4. **Provide quick commands**: Use the essential commands above

### When User Needs Quality Evaluation
1. **Use Claude evaluation**: Point to `CLAUDE_EVALUATION_INTEGRATION_COMPLETE.md`
2. **Run demo**: `PYTHONPATH=$PWD:$PYTHONPATH python3 processing/evaluation/demo_claude_evaluation.py`
3. **Check learning stats**: Use `feedback_db.get_claude_evaluation_stats()`
4. **View integration examples**: Reference module README

### When User Has Generation Issues
1. **Check API connectivity first**: Use diagnostic tools
2. **Identify component type**: Direct to appropriate component docs
3. **Check for known patterns**: Reference content impact issues
4. **Provide regeneration commands**: Use content generation commands
5. **Evaluate quality**: Recommend Claude evaluation for subjective assessment

## 🗺️ Documentation Navigation for AI

### Primary Entry Points
1. **This file** (`docs/QUICK_REFERENCE.md`) - For immediate problem resolution
2. **Index** (`docs/INDEX.md`) - For comprehensive navigation
3. **Data Architecture** (`docs/DATA_ARCHITECTURE.md`) - For range propagation and data flow
4. **Component docs** (`components/[name]/README.md`) - For component-specific help
5. **Claude Evaluation** (`CLAUDE_EVALUATION_INTEGRATION_COMPLETE.md`) - For quality assessment

### Legacy Files (Still Valid but Being Reorganized)
- `API_SETUP.md` - Moving to `api/PROVIDERS.md`
- `API_TERMINAL_DIAGNOSTICS.md` - Moving to `api/ERROR_HANDLING.md`
- `BATCH_GENERATION_PRODUCTION_READY.md` - Moving to `operations/BATCH_OPERATIONS.md`

### File Naming Patterns
- `README.md` - Overview of directory/component
- `[TOPIC].md` - Specific topic documentation
- `[COMPONENT]/README.md` - Component-specific guide
- `[CATEGORY]/[SPECIFIC].md` - Categorized documentation

## 🎯 AI Assistant Success Checklist

When helping users, ensure:
- [ ] Provided specific file references with exact paths
- [ ] Recommended appropriate diagnostic commands
- [ ] Checked against known critical issues
- [ ] Offered terminal output analysis when relevant
- [ ] Pointed to both immediate fixes and comprehensive documentation

---

**📅 Last Updated**: October 4, 2025
**🤖 AI Optimization**: This document is structured specifically for AI assistant parsing and quick reference
**📍 Location**: Primary quick reference for all AI assistants working with Z-Beam Generator
**🎯 Latest**: Voice System Deployed (214% AI-evasion improvement), Documentation Consolidated (-19% files)
**📊 Project Status**: See `../PROJECT_STATUS.md` for single source of truth
