# Material Before/After Image Generator

**Status**: ✅ Enhanced with Aging Research System  
**Date**: November 25, 2025  
**Architecture**: Gemini 2.0 Flash (research) + Imagen 4 (generation) + Gemini Vision (validation)

---

## Overview

Automated AI-powered image generation system that creates scientifically accurate before/after laser cleaning images for materials. Uses Gemini API to research real-world contamination data AND aging effects (weighted equally), then generates 16:9 composite images showing the same object in contaminated/aged (left) and cleaned (right) states.

**Latest Enhancement (Nov 25, 2025)**: Optimized shared dynamic prompting system - 67.7% smaller prompts (6,113 → 1,976 chars), automatic Imagen API compliance, single source of truth for generation and validation. Deep aging research system treats aging effects as equal to traditional contamination, with 11 research dimensions, micro-scale distribution accuracy, and material-specific priorities.

📖 **Quick Access**: [Full Documentation](#-documentation-quick-links) | [Aging Research Details](docs/AGING_RESEARCH_SYSTEM.md) | [Development Archive](docs/archive/)

📚 **Development History**: Complete implementation documentation available in `docs/archive/` including prompt optimization, config simplification, validation fixes, and reference implementations.

## Architecture

### Research System (Gemini 2.0 Flash)
- **ContaminationPatternSelector**: Selects contamination and aging patterns from Contaminants.yaml (zero API calls)
- **ShapeResearcher**: Performs optional object/shape research via Gemini
- **Enhanced Research Protocol**: 11 dimensions (expanded from 9)
  1. Pattern name & type (contamination|aging|combined)
  2. Photo reference descriptions (conservation docs, weathering studies)
  3. Visual characteristics (color/texture evolution, surface topology changes)
  4. Distribution physics (gravity, UV gradients, substrate interaction)
  5. **Aging timeline** (4-stage progression: 0-25%, 25-75%, 75-100%, advanced)
  6. Layer interaction (synergistic effects: UV + moisture, oil + heat)
  7. **Micro-scale distribution** (grain following, edge effects, stress points)
  8. Lighting response (gloss changes, angle-dependent appearance)
  9. **Environmental context** (formation conditions, accelerating/protective factors)
  10. Prevalence & real-world frequency
  11. Realism red flags (10 categories of AI mistakes to avoid)
- **Material-Specific Priorities**:
  - Wood/organics: 70% aging, 30% contamination
  - Polymers: 60% aging, 40% contamination
  - Metals: 50% corrosion, 50% deposits
  - Ceramics: 50% weathering, 50% deposits
- **Caching**: @lru_cache(maxsize=32) at category level for reusability
- **Cost**: $0.0001 per research query

📖 **Deep Dive**: See `docs/AGING_RESEARCH_SYSTEM.md` for complete aging research methodology

### Prompt Generation System (NEW - Nov 25, 2025)
- **SharedPromptBuilder**: Shared dynamic prompting for generation AND validation
- **Template System**: External .txt templates (not hardcoded in code)
  - `shared/generation/` - 5 condensed templates (base, physics, contamination, micro-scale, forbidden)
  - `shared/validation/` - 3 mirrored templates (criteria, checklist, red flags)
  - `shared/feedback/` - User corrections automatically applied to both systems
- **PromptOptimizer**: Automatic optimization for Imagen API limits
  - Condensing: Removes repetitive wording ("MUST show" → "Show")
  - Example removal: Cuts "(e.g., ...)" clarifications
  - Emergency truncation: Smart truncation preserving critical content
  - **Result**: 2,060 char prompts (67.7% reduction from 6,113 chars)
- **Variables**: Material name, contamination level, uniformity, view mode, environment wear
- **Output**: Imagen 4-optimized prompt under 4,096 char limit (2,036 char margin)
- **Imagen API Compliance**: ✅ 100% - well under hard limit with quality preserved

📖 **Deep Dive**: See `IMAGEN_PROMPT_OPTIMIZATION_COMPLETE.md` for optimization details

### Image Generation (Imagen 4)
- **MaterialImageGenerator**: Main generator class
- **Format**: 16:9 side-by-side composite (left=before, right=after)
- **Guidance Scale**: 13.0-15.0 (higher for technical accuracy)
- **Cost**: $0.04 per image

### Configuration System
- **Contamination Level** (1-5): Intensity of contamination
  - 1 = Minimal (<20% coverage)
  - 3 = Moderate (40-60%, typical real-world)
  - 5 = Severe (80-95% coverage)
- **Contamination Uniformity** (1-5): Variety of contaminants
  - 1 = Single type
  - 3 = Three types
  - 5 = Diverse (4+ types)
- **View Mode**: 
  - Contextual = 3D perspective in realistic environment
  - Isolated = 2D technical documentation view
- **Environment Wear** (1-5): Background aging level

### Validation System (Gemini Vision)
- **MaterialImageValidator**: Validates image realism and consistency
- **SharedPromptBuilder Integration**: Uses same standards as generation
- **Fail-Fast Architecture**: Raises ValueError on invalid JSON or missing fields (no fallbacks)
- **JSON Format Preservation**: Response schema preserved even during prompt optimization
- **Validation Criteria**: Mirrors generation standards exactly
  - Physics checklist: Same physics rules as generation
  - Red flags: Inverse of generation forbidden patterns
  - User feedback: Applied to both generation and validation
- **Quality Gates**:
  - Realism score: 75/100 minimum
  - Physics compliance: Required
  - Distribution realism: Required
  - Before/after consistency: Required
- **Cost**: $0.0002 per validation
- **Status**: ✅ COMPLETE (TIER 1 compliant, no fallbacks, 15/15 tests passing)

### Learning System (SQLite) 🔥 NEW
- **ImageGenerationLogger**: Automatic attempt tracking and analytics
- **Database**: SQLite (local, no infrastructure needed)
- **Automatic Logging**: Every generation logged with parameters and outcomes
- **Feedback Capture**: Stores full feedback text, category, and source
- **Analytics Methods**:
  - Category statistics (success rates by material type)
  - Physics violation patterns (most common issues)
  - Feedback effectiveness (before/after comparison)
  - Feedback patterns (which types work best)
  - Search capability (find similar issues/solutions)
  - Best examples (library of successful feedback)
- **CLI Tool**: `analytics.py` for viewing reports without code
- **Cost**: Free (local SQLite database)
- **Status**: ✅ COMPLETE (14/14 tests passing)
- 📖 **Full Documentation**: `docs/LEARNING_SYSTEM.md`

---

## File Structure

```
domains/materials/image/
├── docs/                            # 📖 CENTRALIZED DOCUMENTATION
│   ├── README.md                    # System overview (you are here)
│   ├── AGING_RESEARCH_SYSTEM.md     # Deep aging research methodology
│   ├── AGING_IMPLEMENTATION.md      # Implementation details & test results
│   ├── SYSTEM_VERIFICATION.md       # Verification report (fail-fast, dynamic params)
│   ├── PROMPT_VALIDATION.md         # Prompt quality validation system
│   ├── ARCHITECTURE.md              # System architecture & data flow
│   ├── API_USAGE.md                 # Python API examples
│   ├── CONFIGURATION.md             # Configuration options guide
│   ├── TESTING.md                   # Test coverage & validation
│   └── TROUBLESHOOTING.md           # Common issues & solutions
├── research/
│   ├── contamination_pattern_selector.py  # Pattern selection from Contaminants.yaml
│   ├── shape_researcher.py                # Optional shape/object research
│   ├── payload_monitor.py                 # JSON payload monitoring
│   └── material_prompts.py                # Prompt builder with validation
├── material_generator.py            # Main generator (fail-fast architecture)
├── material_config.py               # Configuration dataclass with validation
├── contamination_levels.py          # Level descriptions (1-5 scales)
├── aging_levels.py                  # Aging progression descriptions
├── generate.py                      # CLI script
├── validator.py                     # Prompt & image validation
└── presets.py                       # Preset configurations
```

### 📖 Documentation Quick Links

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **README.md** (this file) | System overview | Getting started |
| **LEARNING_SYSTEM.md** 🔥 **NEW** | Learning & analytics | Understanding feedback system |
| **FEEDBACK_GUIDELINES.md** | User feedback policy | Adding quality corrections |
| **AGING_RESEARCH_SYSTEM.md** | Aging methodology | Understanding aging patterns |
| **AGING_IMPLEMENTATION.md** | Implementation details | Reviewing what was built |
| **SYSTEM_VERIFICATION.md** | Verification report | Checking system compliance |
| **PROMPT_VALIDATION.md** | Prompt quality | Debugging prompt issues |
| **ARCHITECTURE.md** | System design | Understanding data flow |
| **API_USAGE.md** | Code examples | Integrating into code |
| **CONFIGURATION.md** | Config options | Customizing generation |
| **TESTING.md** | Test suite | Running/writing tests |
| **TROUBLESHOOTING.md** | Common issues | Fixing problems |

**💡 Quick Access in Code**: Research system automatically loads aging research documentation when initialized.

**🚨 Feedback Policy**: All user corrections must be general/category-level, never material-specific. See `FEEDBACK_GUIDELINES.md`.

---

## Usage

### Basic Generation
```bash
python3 domains/materials/image/generate.py --material "Aluminum"
```

### Custom Configuration
```bash
python3 domains/materials/image/generate.py \
  --material "Stainless Steel" \
  --contamination-level 4 \
  --uniformity 3 \
  --view-mode Contextual \
  --environment-wear 3
```

### Technical Documentation View
```bash
python3 domains/materials/image/generate.py \
  --material "Copper" \
  --contamination-level 2 \
  --uniformity 2 \
  --view-mode Isolated
```

### Show Prompt (Dry Run)
```bash
python3 domains/materials/image/generate.py \
  --material "Titanium" \
  --show-prompt \
  --dry-run
```

### With Validation
```bash
python3 domains/materials/image/generate.py \
  --material "Brass" \
  --validate
```

---

## Python API Usage

```python
from domains.materials.image.material_generator import MaterialImageGenerator
from domains.materials.image.material_config import MaterialImageConfig

# Initialize generator
generator = MaterialImageGenerator(gemini_api_key="your_key")

# Create configuration
config = MaterialImageConfig(
    material="Aluminum",
    contamination_level=3,
    contamination_uniformity=3,
    view_mode="Contextual",
    environment_wear=3
)

# Generate complete prompt package
prompt_package = generator.generate_complete(
    material_name="Aluminum",
    config=config
)

# Access components
prompt = prompt_package["prompt"]
negative_prompt = prompt_package["negative_prompt"]
research_data = prompt_package["research_data"]
aspect_ratio = prompt_package["aspect_ratio"]
guidance_scale = prompt_package["guidance_scale"]
```

---

## Key Features

### Scientific Accuracy
- ✅ Real contaminants with chemical formulas
- ✅ Accurate appearance (color, texture, pattern, thickness)
- ✅ Environmental causes documented
- ✅ Prevalence levels specified
- ✅ **Optimized prompts** - 67.7% smaller, automatic Imagen API compliance

### Prompt System (NEW)
- ✅ **Shared dynamic prompting** - Single source of truth for generation and validation
- ✅ **Template-based** - External .txt files (not hardcoded in code)
- ✅ **Automatic optimization** - PromptOptimizer ensures Imagen API compliance
- ✅ **User feedback integration** - Edit text files, automatically applied to both systems
- ✅ **General/category-level feedback** - Applies to ALL materials in category (never material-specific)
- ✅ **10x faster iteration** - Text file edits vs code changes (5 min vs 30-45 min)
- ✅ **Imagen 4 compliant** - 2,060 char prompts (2,036 char margin under 4,096 limit)

### Contamination Research
- ✅ Automatic research via Gemini 2.0 Flash
- ✅ 3-5 scientifically accurate contaminants per material
- ✅ Common objects and typical environments
- ✅ Base material appearance when clean

### Configuration Control
- ✅ 5-level intensity scale (minimal → severe)
- ✅ 5-level uniformity scale (single type → diverse)
- ✅ 2 view modes (contextual 3D or isolated 2D)
- ✅ 5-level environment wear

### Cost Optimization
- ✅ Research caching (@lru_cache)
- ✅ Single research call per material
- ✅ Fallback research data if API unavailable

---

## Example Research Output

**Material**: Aluminum  
**Common Object**: Aluminum ladder  
**Environment**: Construction sites, warehouses  
**Contaminants**:
1. **Aluminum Oxide (Al₂O₃)**
   - Cause: Natural oxidation in air/moisture
   - Color: Dull gray to white
   - Texture: Fine, powdery to chalky
   - Pattern: Uniform coating, thicker in exposed areas
   - Thickness: Thin (0.1-1mm)
   - Prevalence: Universal on exposed aluminum

2. **Carbon Deposits**
   - Cause: Combustion, industrial pollution
   - Color: Dark gray to black
   - Texture: Sooty, granular
   - Pattern: Concentrated in crevices
   - Thickness: Thin (< 0.5mm)
   - Prevalence: Common in industrial environments

3. **Oil/Grease Contamination**
   - Cause: Handling, machinery contact
   - Color: Dark brown to black with sheen
   - Texture: Sticky, viscous
   - Pattern: Smeared, fingerprints visible
   - Thickness: Very thin film
   - Prevalence: Very common in industrial use

---

## Next Steps

### Immediate (Ready to Implement)
1. **Test Complete Pipeline**: Generate test images for Aluminum, Steel, Copper
2. **Validate Research Quality**: Verify contamination data accuracy
3. **Implement Validation**: Adapt validator.py for before/after checks
4. **Cost Analysis**: Measure actual costs per material

### Future Enhancements
1. **Preset Configurations**: Common contamination scenarios
2. **Batch Generation**: Generate multiple materials automatically
3. **Material Database Integration**: Read from Materials.yaml
4. **Enhanced Validation**: Check contamination matches research
5. **Quality Scoring**: Rate generated images automatically

---

## Technical Details

### Dependencies
- **Gemini 2.0 Flash**: Research and validation
- **Imagen 4**: Image generation via Vertex AI
- **Python 3.10+**: Type hints, dataclasses
- **LRU Cache**: Research result caching

### API Costs (Per Material)
- Research: $0.0001
- Image Generation: $0.04
- Validation (optional): $0.0002
- **Total**: ~$0.04 per material

### Performance
- Research: ~2-3 seconds (cached after first call)
- Image Generation: ~5-10 seconds
- Total Time: ~7-13 seconds per material

---

## Differences from City Generator

| Aspect | City Generator | Material Generator |
|--------|---------------|-------------------|
| **Research** | Historical population | Material contamination |
| **Subject** | City in specific decade | Material before/after cleaning |
| **Configuration** | Year, photo/scenery aging | Contamination level/uniformity, view mode |
| **Scale** | Population-adaptive (hamlet → city) | Contamination-adaptive (minimal → severe) |
| **Output** | Single historical photo | Side-by-side before/after composite |
| **Research Data** | Population, building counts, focal characteristics | Contaminants (formula, appearance, causes) |
| **Negative Prompts** | Anachronisms, crowds for small towns | Inconsistent splits, wrong contamination |

---

## Status Summary

✅ **Complete**:
- Material contamination researcher (Gemini 2.0 Flash)
- Base prompt template (7KB comprehensive)
- Prompt builder (research + template)
- Configuration system (dataclass + validation)
- Contamination level descriptions (1-5 scales)
- Main generator class (MaterialImageGenerator)
- CLI script (generate.py)

⚠️ **In Progress**:
- Validation system adaptation
- Preset configurations
- Batch generation scripts

❌ **Not Started**:
- Testing with real materials
- Integration with Materials.yaml
- Quality scoring system
- Documentation site updates

---

## 🤖 For AI Assistants

**CRITICAL RULES - READ BEFORE ANY CODE CHANGES:**

### 1. Documentation First
- ✅ **ALWAYS check TROUBLESHOOTING.md** before proposing fixes
- ✅ **Read ARCHITECTURE.md** to understand data flow before modifying
- ✅ **Consult API_USAGE.md** for integration patterns

### 2. Fail-Fast Architecture (NON-NEGOTIABLE)
- ❌ **NEVER add production fallbacks** - validator must raise errors, not return fake data
- ❌ **NEVER swallow exceptions** - let errors propagate with clear messages  
- ❌ **NEVER add `.get('key', default)`** patterns - must raise errors on missing config
- ❌ **NEVER create fallback research data** - research is REQUIRED
- ✅ **ALWAYS raise ValueError/RuntimeError** when config or research missing
- ✅ **Validator fails fast**: Raises ValueError on invalid JSON or missing realism_score
- ✅ Example: `raise ValueError("MaterialImageConfig is required")`
- 📖 **Policy**: See `.github/copilot-instructions.md` TIER 1 requirements

### 3. Configuration-Driven Parameters
- ❌ **NEVER hardcode values** - temperature, guidance_scale, thresholds, penalties
- ✅ **ALWAYS use MaterialImageConfig** - all params in config dataclass
- ✅ **Dynamic adjustment OK** - config can auto-adjust (e.g., guidance_scale by view_mode)
- ✅ Example: `guidance_scale = config.guidance_scale` not `guidance_scale = 15.0`
- 📖 **Policy**: See `docs/08-development/HARDCODED_VALUE_POLICY.md`

### 4. Validation is MANDATORY
- ✅ **validation runs by default** - `validate=True` in MaterialImageConfig
- ✅ **JSON format preserved** - PromptOptimizer never truncates JSON schema
- ✅ **log errors clearly** - validation failures visible in terminal
- ❌ **NEVER skip validation silently** - must use `--no-validate` flag explicitly
- 📖 **Tests**: 15/15 tests verify validation compliance

### 5. Evidence-Based Changes
- ✅ **Test before claiming fixes** - provide proof (test output, logs)
- ✅ **Measure actual behavior** - don't assume it works
- ✅ **Document with examples** - show before/after in code comments
- ❌ **NEVER claim compliance without verification**

### Common Anti-Patterns to Avoid
```python
# ❌ WRONG: Fallback on missing config
config = config or MaterialImageConfig()

# ✅ RIGHT: Fail-fast
if config is None:
    raise ValueError("MaterialImageConfig is required")

# ❌ WRONG: Hardcoded parameter
guidance_scale = 15.0

# ✅ RIGHT: Config-driven
guidance_scale = config.guidance_scale

# ❌ WRONG: Silent research failure
research_data = research_data or {"contaminants": []}

# ✅ RIGHT: Fail on missing research
if research_data is None:
    raise RuntimeError("Research data required for generation")
```

### Before Making Changes - Checklist
- [ ] Read relevant docs (TROUBLESHOOTING, ARCHITECTURE, etc.)
- [ ] Understand current implementation (no assumptions)
- [ ] Plan minimal fix (surgical precision, not rewrites)
- [ ] Verify config-driven (no hardcoded values)
- [ ] Test with evidence (actual output, not theoretical)
- [ ] Update docs if behavior changes

### System Compliance Status
✅ **Fail-fast**: All entry points validate config  
✅ **No defaults**: ValueError raised on missing config  
✅ **Config-driven**: guidance_scale, all params in MaterialImageConfig  
✅ **Validation**: Prompt validation runs by default  
✅ **Evidence**: SYSTEM_VERIFICATION.md documents compliance

---

## Credits

**Based On**: Historical City Image Generator (domains/regions/image/)  
**Architecture**: Gemini API stack (Flash 2.0 + Imagen 4 + Vision)  
**Date**: November 24, 2025  
**Status**: Core system complete, ready for testing
