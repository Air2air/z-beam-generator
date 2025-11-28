# Materials Domain Cleanup Analysis
**Date**: November 26, 2025  
**Goal**: Normalize materials domain to be a clean template for other domains

---

## 🎯 Executive Summary

**Materials domain contains 3 types of code:**
1. **Material-specific** (stays in domains/materials/)
2. **Generic research/generation** (move to shared/)
3. **Other domain content** (move to respective domains)

**Recommendation**: Extract 60% of materials domain into shared infrastructure.

---

## 📊 Current Structure Analysis

### domains/materials/ Contents

```
domains/materials/
├── README.md                           # Domain docs (KEEP)
├── __init__.py                         # Domain interface (KEEP)
├── coordinator.py                      # Material coordinator (KEEP)
├── data_loader.py                      # Material data loader (KEEP)
├── category_loader.py                  # Material categories (KEEP)
├── materials_cache.py                  # Material-specific cache (KEEP)
├── schema.py                           # Material schema (KEEP)
│
├── modules/                            # Material frontmatter modules (KEEP)
│   └── 6 material-specific modules
│
├── prompts/                            # Material prompts (EVALUATE)
│   ├── settings_description.txt        # ❌ WRONG DOMAIN
│   └── personas/                       # ✅ CORRECT
│
├── image/                              # Image generation (EVALUATE - likely shared)
│   ├── material_generator.py           # Material-specific wrapper (KEEP)
│   ├── generate.py                     # CLI (KEEP)
│   ├── validator.py                    # Material validator (KEEP)
│   ├── material_config.py              # Material config (KEEP)
│   ├── contamination_levels.py         # Contaminant logic (❌ MOVE)
│   ├── demo_optimizations.py           # ❓ EVALUATE
│   ├── learning/                       # ❌ GENERIC - move to shared
│   │   ├── image_generation_logger.py
│   │   └── analytics.py
│   └── prompts/                        # ❌ GENERIC - move to shared
│       ├── prompt_builder.py
│       ├── prompt_optimizer.py
│       ├── image_pipeline_monitor.py
│       ├── material_researcher.py      # ✅ Material-specific
│       └── category_contamination_researcher.py  # ❓ Category or Material?
│
├── research/                           # ❌ 90% GENERIC
│   ├── base.py                         # Generic base class
│   ├── factory.py                      # Generic factory
│   ├── unified_research_interface.py   # Material-specific orchestrator (KEEP)
│   ├── unified_material_research.py    # Material research impl (KEEP)
│   ├── category_range_researcher.py    # Material category research (KEEP)
│   ├── faq_topic_researcher.py         # Generic FAQ research (MOVE)
│   ├── machine_settings_researcher.py  # ❌ SETTINGS DOMAIN
│   ├── comprehensive_discovery_prompts.py  # Generic prompts (MOVE)
│   └── services/
│       └── ai_research_service.py      # ❌ GENERIC AI service
│
├── services/                           # Material services (KEEP)
│   ├── property_manager.py             # Material properties (KEEP)
│   ├── template_service.py             # Generic template (MOVE)
│   └── pipeline_process_service.py     # Generic pipeline (MOVE)
│
├── utils/                              # Material utils (KEEP)
│   ├── property_helpers.py             # Material properties (KEEP)
│   ├── property_enhancer.py            # Material properties (KEEP)
│   ├── property_taxonomy.py            # Material taxonomy (KEEP)
│   ├── category_property_cache.py      # Material categories (KEEP)
│   └── unit_extractor.py               # ❌ GENERIC utility
│
└── validation/                         # Material validation (KEEP)
    └── completeness_validator.py       # Material completeness (KEEP)
```

---

## 🚀 Proposed Moves

### TIER 1: Critical Moves (Wrong Domain) 🔴

**1. Settings Research → domains/settings/**
```bash
# MOVE
domains/materials/research/machine_settings_researcher.py (29KB)
→ domains/settings/research/machine_settings_researcher.py

# WHY: Settings domain owns machine settings, not materials
# IMPACT: Settings domain can research its own data
```

**2. Contaminant Logic → domains/contaminants/**
```bash
# MOVE
domains/materials/image/contamination_levels.py
→ domains/contaminants/contamination_levels.py

# WHY: Contaminants domain owns contamination logic
# IMPACT: Reusable across all domains
```

**3. Settings Prompt → domains/settings/**
```bash
# DELETE (already identified as unused)
domains/materials/prompts/settings_description.txt

# WHY: Unused file, wrong domain, root prompt is correct
```

---

### TIER 2: Generic Infrastructure (Shared) 🟡

**4. Research Base Classes → shared/research/**
```bash
# MOVE
domains/materials/research/base.py (4KB)
domains/materials/research/factory.py (3.5KB)
domains/materials/research/comprehensive_discovery_prompts.py (8KB)
domains/materials/research/faq_topic_researcher.py (10KB)
domains/materials/research/services/ai_research_service.py
→ shared/research/

# WHY: Generic research infrastructure, not material-specific
# BENEFITS: Reusable by settings, contaminants, regions domains
# PATTERN: Same as shared/types/ for contamination types
```

**5. Image Generation Infrastructure → shared/image/**
```bash
# MOVE
domains/materials/image/learning/          # Learning system
domains/materials/image/prompts/prompt_builder.py
domains/materials/image/prompts/prompt_optimizer.py
domains/materials/image/prompts/image_pipeline_monitor.py
→ shared/image/

# KEEP IN MATERIALS (domain-specific wrappers)
domains/materials/image/material_generator.py    # Material wrapper
domains/materials/image/generate.py              # Material CLI
domains/materials/image/validator.py             # Material validator
domains/materials/image/material_config.py       # Material config
domains/materials/image/prompts/material_researcher.py  # Material-specific

# WHY: Generic image generation, learning, monitoring
# BENEFITS: Other domains can generate images (contaminants, regions)
```

**6. Generic Services → shared/services/**
```bash
# MOVE
domains/materials/services/template_service.py
domains/materials/services/pipeline_process_service.py
→ shared/services/

# KEEP
domains/materials/services/property_manager.py  # Material-specific

# WHY: Template and pipeline services are generic
```

**7. Generic Utils → shared/utils/**
```bash
# MOVE
domains/materials/utils/unit_extractor.py
→ shared/utils/

# KEEP (material-specific)
domains/materials/utils/property_helpers.py
domains/materials/utils/property_enhancer.py
domains/materials/utils/property_taxonomy.py
domains/materials/utils/category_property_cache.py
```

---

### TIER 3: Evaluation Needed 🟢

**8. Category Contamination Researcher**
```bash
# CURRENT
domains/materials/image/prompts/category_contamination_researcher.py

# QUESTION: Is this material categories or contaminant categories?
# IF material categories: KEEP in materials
# IF contaminant categories: MOVE to domains/contaminants/
# NEED: Review code to determine scope
```

**9. Demo Optimizations**
```bash
# CURRENT
domains/materials/image/demo_optimizations.py

# QUESTION: Is this material-specific or generic image optimization?
# IF material demos: KEEP
# IF generic image optimization: MOVE to shared/image/
# NEED: Review code to determine scope
```

---

## 📋 Migration Plan

### Phase 1: Wrong Domain Fixes (30 min)
1. ✅ Delete unused settings prompt (5 min)
2. Move machine_settings_researcher → domains/settings/ (10 min)
3. Move contamination_levels → domains/contaminants/ (10 min)
4. Update imports (5 min)

### Phase 2: Generic Research Infrastructure (1 hour)
1. Create shared/research/ directory
2. Move base.py, factory.py, faq_topic_researcher.py
3. Move comprehensive_discovery_prompts.py
4. Move ai_research_service.py
5. Update imports in materials domain (use shared.research)
6. Update imports in other domains
7. Test all research operations

### Phase 3: Generic Image Infrastructure (1.5 hours)
1. Create shared/image/ directory
2. Move learning/ subdirectory
3. Move generic prompt utilities (builder, optimizer, monitor)
4. Keep material-specific wrappers in materials/image/
5. Update imports
6. Test image generation for materials

### Phase 4: Generic Services (30 min)
1. Create shared/services/ (if doesn't exist)
2. Move template_service.py
3. Move pipeline_process_service.py
4. Update imports
5. Test frontmatter generation

### Phase 5: Generic Utils (15 min)
1. Move unit_extractor.py → shared/utils/
2. Update imports
3. Test property operations

### Phase 6: Evaluation Items (1 hour)
1. Review category_contamination_researcher scope
2. Review demo_optimizations scope
3. Move based on analysis
4. Update imports

**Total Time**: 4.5 hours

---

## ✅ Expected Outcome

### Clean Materials Domain Structure

```
domains/materials/
├── README.md                           # Domain documentation
├── __init__.py                         # Domain interface
├── coordinator.py                      # Material coordinator
├── data_loader.py                      # Material data loader
├── category_loader.py                  # Material categories
├── materials_cache.py                  # Material cache
├── schema.py                           # Material schema
│
├── modules/                            # Material frontmatter
│   └── 6 material modules
│
├── prompts/                            # Material prompts
│   └── personas/                       # Author personas
│
├── image/                              # Material image generation
│   ├── material_generator.py           # Material wrapper (uses shared/image/)
│   ├── generate.py                     # Material CLI
│   ├── validator.py                    # Material validator
│   ├── material_config.py              # Material config
│   └── prompts/
│       └── material_researcher.py      # Material contamination research
│
├── research/                           # Material research
│   ├── unified_research_interface.py   # Material orchestrator
│   ├── unified_material_research.py    # Material implementation
│   └── category_range_researcher.py    # Material category ranges
│
├── services/                           # Material services
│   └── property_manager.py             # Material properties
│
├── utils/                              # Material utilities
│   ├── property_helpers.py
│   ├── property_enhancer.py
│   ├── property_taxonomy.py
│   └── category_property_cache.py
│
└── validation/                         # Material validation
    └── completeness_validator.py
```

### New Shared Infrastructure

```
shared/
├── research/                           # Generic research (NEW)
│   ├── base.py                         # ContentResearcher base
│   ├── factory.py                      # ResearcherFactory
│   ├── faq_topic_researcher.py         # Generic FAQ research
│   ├── comprehensive_discovery_prompts.py
│   └── services/
│       └── ai_research_service.py      # Generic AI service
│
├── image/                              # Generic image generation (NEW)
│   ├── learning/                       # Learning system
│   │   ├── image_generation_logger.py
│   │   └── analytics.py
│   └── prompts/                        # Generic prompt utilities
│       ├── prompt_builder.py
│       ├── prompt_optimizer.py
│       └── image_pipeline_monitor.py
│
├── services/                           # Generic services (EXPAND)
│   ├── template_service.py             # Template handling
│   └── pipeline_process_service.py     # Pipeline processing
│
└── utils/                              # Generic utilities (EXPAND)
    └── unit_extractor.py               # Unit extraction
```

### Settings Domain Gets Its Research

```
domains/settings/
├── research/                           # Settings research (NEW)
│   └── machine_settings_researcher.py  # From materials domain
└── ... (existing settings files)
```

### Contaminants Domain Gets Its Logic

```
domains/contaminants/
├── contamination_levels.py             # From materials domain
└── ... (existing contaminants files)
```

---

## 💡 Key Benefits

### 1. Domain Independence ✅
- Materials domain only contains material-specific code
- Settings domain owns settings research
- Contaminants domain owns contamination logic
- Zero cross-domain imports (except orchestrators)

### 2. Reusability ✅
- shared/research/ can be used by ANY domain
- shared/image/ enables image generation for ALL domains
- shared/services/ provides common infrastructure
- New domains bootstrap faster (use shared/)

### 3. Clarity ✅
- Materials domain is clean example for other domains
- Clear separation: domain-specific vs generic
- Easy to understand what belongs where
- Less confusion about file ownership

### 4. Maintainability ✅
- Changes to generic code benefit all domains
- Domain-specific changes stay isolated
- Testing is clearer (domain tests vs shared tests)
- Fewer duplicate implementations

---

## 🚫 What NOT to Move

**Keep in Materials Domain**:
- ✅ Material data loader (materials-specific)
- ✅ Material properties manager (materials-specific)
- ✅ Material categories (materials-specific)
- ✅ Material frontmatter modules (materials-specific)
- ✅ Material validation (materials-specific)
- ✅ Material image generator wrapper (materials-specific)
- ✅ Material research orchestrator (materials-specific)
- ✅ Material prompts/personas (materials-specific)

**Rationale**: These are truly material-specific implementations, not generic infrastructure.

---

## 📊 Metrics

### Before Cleanup
- Materials domain: ~50 files
- Shared infrastructure: Limited
- Cross-domain violations: 2 (machine_settings, contamination_levels)
- Domain independence: 60%

### After Cleanup
- Materials domain: ~25 files (50% reduction)
- Shared infrastructure: +15 files
- Cross-domain violations: 0
- Domain independence: 100%
- Reusability: High (shared research, image, services)

---

## ⚠️ Migration Risks

### Risk 1: Import Breakage
- **Impact**: High
- **Mitigation**: Update all imports systematically
- **Test**: Run full test suite after each phase

### Risk 2: Missed Dependencies
- **Impact**: Medium
- **Mitigation**: Use grep to find all imports before moving
- **Test**: Search for "from domains.materials.research" etc.

### Risk 3: Domain Logic in Generic Code
- **Impact**: Medium
- **Mitigation**: Review each file before moving (is it truly generic?)
- **Test**: Check for material-specific logic in moved files

### Risk 4: Circular Dependencies
- **Impact**: Low (shared can't import from domains)
- **Mitigation**: Follow established shared/ pattern
- **Test**: Verify shared/ imports only from shared/

---

## ✅ Success Criteria

1. **Zero cross-domain imports** (except orchestrators)
2. **Materials domain is clean example** (only material-specific code)
3. **Shared infrastructure is reusable** (other domains can use)
4. **All tests passing** (no breakage)
5. **Documentation updated** (new structure documented)
6. **Settings domain owns settings research**
7. **Contaminants domain owns contamination logic**

---

## 📝 Action Items

### Immediate (Get Approval)
- [ ] Review analysis with user
- [ ] Confirm migration plan
- [ ] Prioritize phases (all or subset?)
- [ ] Get go/no-go decision

### Phase 1: Wrong Domain (30 min)
- [ ] Delete unused settings prompt
- [ ] Move machine_settings_researcher
- [ ] Move contamination_levels
- [ ] Update imports
- [ ] Test

### Phase 2-6: Generic Infrastructure (3.5 hours)
- [ ] Execute phases 2-6 as outlined
- [ ] Update all imports
- [ ] Run tests after each phase
- [ ] Document new structure

### Documentation (30 min)
- [ ] Update materials/README.md
- [ ] Create shared/research/README.md
- [ ] Create shared/image/README.md
- [ ] Update DOMAIN_INDEPENDENCE_POLICY.md
- [ ] Document new patterns

---

**Status**: Analysis complete, awaiting user decision  
**Recommendation**: Execute all 6 phases for clean domain separation  
**Total Time**: 4.5 hours + 30 min documentation = **5 hours**

