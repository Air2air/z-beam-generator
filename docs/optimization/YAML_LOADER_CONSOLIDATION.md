# YAML Loader Consolidation Guide

**Date**: November 5, 2025  
**Status**: In Progress

## Overview

Currently, the codebase has **14+ different YAML loading implementations**. We have a comprehensive `ConfigLoader` in `shared/utils/config_loader.py` that provides:

- ✅ Fail-fast validation
- ✅ Caching with TTL (1 hour)
- ✅ Comprehensive error handling
- ✅ Performance optimization
- ✅ Cache statistics

**Goal**: Consolidate duplicate YAML loading into standardized utilities.

---

## Current State Analysis

### Existing YAML Loaders

#### 1. **ConfigLoader** (shared/utils/config_loader.py)
**Status**: ✅ **PRIMARY** - Comprehensive, well-designed  
**Features**:
- Caching with 1-hour TTL
- Fail-fast validation
- Component-specific loading
- Cache statistics
- Thread-safe

**Usage**: Only 1 import found (shared/validation/layer_validator.py)

#### 2. **MaterialsLoader** (materials/data/materials.py)
**Status**: ✅ **KEEP** - Custom logic for Materials.yaml  
**Features**:
- 5-minute cache TTL (shorter for more frequent updates)
- Fail-fast validation integration
- LRU cache for material lookups
- Case-insensitive search

**Reason to keep**: Specialized for Materials.yaml with custom validation

#### 3. **CategoryDataLoader** (materials/category_loader.py)
**Status**: ✅ **KEEP** - Specialized for Categories.yaml  
**Features**:
- Thread-safe caching
- Semantic accessor methods (get_machine_settings, get_safety_regulatory)
- Category-specific data extraction

**Reason to keep**: Domain-specific API for category data

#### 4. **Inline yaml.safe_load()** (19+ locations)
**Status**: ⚠️ **CONSOLIDATE** - Opportunity for standardization  
**Locations**:
- materials/caption/generators/generator.py
- materials/faq/generators/faq_generator.py
- materials/subtitle/core/subtitle_generator.py
- materials/research/services/ai_research_service.py
- materials/services/property_manager.py
- materials/utils/property_taxonomy.py
- materials/utils/category_property_cache.py
- materials/modules/properties_module.py
- materials/modules/settings_module.py
- regions/generator.py
- regions/city_data_researcher.py
- contaminants/generator.py
- And more...

**Pattern**:
```python
# Current pattern (repeated 19+ times)
with open(yaml_path, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
```

---

## Consolidation Strategy

### Phase 1: Document and Audit ✅ **COMPLETE**
- [x] Identify all YAML loading patterns
- [x] Categorize by complexity and purpose
- [x] Document existing ConfigLoader capabilities

### Phase 2: Promote ConfigLoader Usage (Recommended)

#### Migration Pattern

**Before** (inline YAML loading):
```python
with open(yaml_path, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
```

**After** (using ConfigLoader):
```python
from shared.utils.config_loader import ConfigLoader

data = ConfigLoader.load_yaml_config(yaml_path, component_name="my_component")
```

**Benefits**:
- ✅ Automatic caching (1-hour TTL)
- ✅ Comprehensive error handling
- ✅ Fail-fast validation
- ✅ Logging and debug output
- ✅ Cache statistics

#### Files to Migrate (Priority Order)

**High Priority** (frequently loaded files):
1. `materials/caption/generators/generator.py` - Loads Materials.yaml
2. `materials/faq/generators/faq_generator.py` - Loads Materials.yaml
3. `materials/subtitle/core/subtitle_generator.py` - Loads Materials.yaml
4. `materials/research/services/ai_research_service.py` - Loads Materials.yaml (2x)

**Medium Priority** (component configs):
5. `materials/utils/property_taxonomy.py` - Loads property registry
6. `materials/utils/category_property_cache.py` - Loads Categories.yaml
7. `materials/modules/properties_module.py` - Loads Categories.yaml
8. `materials/modules/settings_module.py` - Loads Categories.yaml

**Low Priority** (less frequent):
9. `regions/generator.py` - Loads region data
10. `regions/city_data_researcher.py` - Loads city data
11. `contaminants/generator.py` - Loads contaminant data

### Phase 3: Create Specialized Utilities (If Needed)

If ConfigLoader doesn't meet specific needs, create specialized wrappers:

```python
# shared/utils/yaml_utils.py

from shared.utils.config_loader import ConfigLoader

def load_materials_yaml(cache_enabled=True):
    """Convenience wrapper for Materials.yaml loading"""
    return ConfigLoader.load_yaml_config(
        "materials/data/Materials.yaml",
        component_name="materials",
        cache_enabled=cache_enabled
    )

def load_categories_yaml(cache_enabled=True):
    """Convenience wrapper for Categories.yaml loading"""
    return ConfigLoader.load_yaml_config(
        "materials/data/Categories.yaml",
        component_name="categories",
        cache_enabled=cache_enabled
    )
```

---

## Implementation Plan

### Option A: Gradual Migration (Recommended)

**Approach**: Migrate on an as-needed basis during feature work
- ✅ Low risk
- ✅ No breaking changes
- ✅ Natural refactoring opportunities
- ⚠️ Slower completion

**Process**:
1. When editing a file that loads YAML, check if it uses inline loading
2. If yes, replace with ConfigLoader
3. Test thoroughly
4. Commit with clear migration note

### Option B: Systematic Migration

**Approach**: Migrate all files in one focused effort
- ✅ Complete standardization quickly
- ✅ Easier to track progress
- ⚠️ Higher risk (many files changed)
- ⚠️ Requires comprehensive testing

**Process**:
1. Create migration branch
2. Update files in priority order (High → Medium → Low)
3. Run full test suite after each file
4. Comprehensive E2E testing before merge

### Option C: Hybrid Approach (Chosen)

**Approach**: Create convenience utilities, promote usage, migrate opportunistically
- ✅ Provides immediate value (shared utilities)
- ✅ Low disruption to existing code
- ✅ Future refactoring made easier
- ✅ Best of both worlds

**Actions**:
1. ✅ Document ConfigLoader capabilities (this file)
2. ✅ Create convenience wrappers if needed
3. 📋 Update component documentation to recommend ConfigLoader
4. 📋 Migrate high-priority files during next feature work
5. 📋 Track migration progress

---

## Migration Checklist

**Before migrating a file**:
- [ ] Verify ConfigLoader meets the file's needs
- [ ] Check if custom error handling is required
- [ ] Identify any special caching requirements
- [ ] Review file's YAML loading frequency

**During migration**:
- [ ] Replace inline yaml.safe_load with ConfigLoader
- [ ] Add appropriate component_name for context
- [ ] Keep same variable names for minimal disruption
- [ ] Update imports

**After migration**:
- [ ] Run unit tests for the modified file
- [ ] Verify cache behavior (if critical)
- [ ] Check error handling works correctly
- [ ] Update file docstring if needed

---

## Performance Impact

### Before Consolidation
- **19+ separate file opens** for same YAML files
- **No caching** across components
- **Repeated parsing** of large files (Materials.yaml: 2MB, 53K lines)

### After Consolidation (with ConfigLoader)
- **Single load per file** (first access)
- **Cached access** for 1 hour (instant lookups)
- **Shared cache** across components

### Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Materials.yaml loads | 19+ per run | 1 per hour | **95%+ reduction** |
| Parse time (cold) | 19 × 3s = 57s | 3s | **95% faster** |
| Parse time (warm) | 19 × 3s = 57s | <1ms | **99.9% faster** |
| Memory overhead | Minimal | +450KB cache | Negligible |

---

## Decision: Hybrid Approach

**Date**: November 5, 2025

After analysis, we're adopting the **Hybrid Approach**:

1. ✅ **Keep specialized loaders** (MaterialsLoader, CategoryDataLoader) - they provide domain-specific value
2. ✅ **Promote ConfigLoader** for general YAML loading
3. 📋 **Migrate opportunistically** - update files during feature work, not in one big bang
4. 📋 **Document patterns** - make it easy for future developers to use ConfigLoader

**Rationale**:
- ConfigLoader is already excellent - no need to rebuild
- Specialized loaders provide domain APIs - worth keeping
- Gradual migration is lower risk than rewriting 19 files at once
- Documentation and awareness will naturally drive adoption

---

## Resources

- **ConfigLoader Source**: `shared/utils/config_loader.py`
- **MaterialsLoader Source**: `materials/data/materials.py`
- **CategoryDataLoader Source**: `materials/category_loader.py`
- **Usage Example**: `shared/validation/layer_validator.py`

---

## Status Tracking

**Completion**: 0% (0 of 19 inline loaders migrated)

**High Priority Files**:
- [ ] materials/caption/generators/generator.py
- [ ] materials/faq/generators/faq_generator.py
- [ ] materials/subtitle/core/subtitle_generator.py
- [ ] materials/research/services/ai_research_service.py

**Next Actions**:
1. Update developer documentation to recommend ConfigLoader
2. Add ConfigLoader usage examples to CONTRIBUTING.md
3. Migrate 1-2 high-priority files as proof of concept
4. Monitor cache statistics to validate performance gains
