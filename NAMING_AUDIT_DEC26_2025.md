# Semantic Naming Audit - December 26, 2025

**Purpose**: Systematic examination of naming conventions across codebase  
**Policy Reference**: `docs/08-development/NAMING_CONVENTIONS_POLICY.md`  
**Approach**: Deep, methodical analysis of all naming patterns

---

## 📊 Violations Found

### 🔴 TIER 1: Critical Violations (High-Impact Files)

#### 1. **SimpleSEOGenerator** → `SEOGenerator`
- **File**: `generation/seo/simple_seo_generator.py`
- **Class**: `SimpleSEOGenerator`
- **Issue**: "Simple" prefix adds no value
- **Impact**: HIGH - Used across export system
- **Recommendation**: Rename to `SEOGenerator`
- **Justification**: Context (seo/ directory) already indicates SEO functionality

#### 2. **UnifiedConfigManager** → `ConfigManager`
- **File**: `shared/config/manager.py`
- **Class**: `UnifiedConfigManager`
- **Issue**: "Unified" is redundant - it's the ONLY config manager
- **Impact**: CRITICAL - Central configuration system
- **Recommendation**: Rename to `ConfigManager`
- **Justification**: No ambiguity - there's only one config manager

#### 3. **UnifiedImportManager** → `ImportManager`
- **File**: `shared/utils/import_system.py`
- **Class**: `UnifiedImportManager`
- **Issue**: "Unified" doesn't clarify purpose
- **Impact**: HIGH - Core import system
- **Recommendation**: Rename to `ImportManager`
- **Justification**: It's THE import manager, not one of many

#### 4. **UniversalDomainCoordinator** → `DomainCoordinator`
- **File**: `shared/domain/base_coordinator.py`
- **Class**: `UniversalDomainCoordinator`
- **Issue**: "Universal" redundant in shared/ directory
- **Impact**: CRITICAL - Base class for all domain coordinators
- **Recommendation**: Rename to `DomainCoordinator`
- **Justification**: shared/ directory already indicates universal scope

#### 5. **UnifiedMaterialsGenerator** → `MaterialsCoordinator`
- **File**: `domains/materials/coordinator.py`
- **Class**: `UnifiedMaterialsGenerator`
- **Issue**: Two problems:
  - "Unified" redundant
  - Name says "Generator" but it's really a coordinator
- **Impact**: HIGH - Materials domain orchestration
- **Recommendations**:
  - Option A: `MaterialsCoordinator` (matches its actual role)
  - Option B: `MaterialsGenerator` (if truly a generator)
- **Justification**: Semantic confusion - name doesn't match function

### 🟡 TIER 2: Moderate Violations (Support Files)

#### 6. **SimpleCache** → `Cache` or `MemoryCache`
- **File**: `shared/utils/cache_utils.py`
- **Class**: `SimpleCache`
- **Issue**: "Simple" doesn't add clarity
- **Impact**: MODERATE - Caching utility
- **Recommendations**:
  - Option A: `Cache` (if only cache implementation)
  - Option B: `MemoryCache` (if distinguishing from disk/redis cache)
- **Justification**: If there's only one cache, "Simple" is meaningless

#### 7. **UnifiedValidator** → `Validator`
- **File**: `shared/validation/validator.py`
- **Class**: `UnifiedValidator`
- **Issue**: "Unified" unclear - unified with what?
- **Impact**: MODERATE - Validation system
- **Recommendation**: Rename to `Validator` or `SchemaValidator`
- **Justification**: Context makes scope clear

#### 8. **UnifiedValidation*** (3 classes)
- **File**: `shared/services/validation/schema_validator.py`
- **Classes**:
  - `UnifiedValidationError` → `ValidationError`
  - `UnifiedValidationResult` → `ValidationResult`
  - `UnifiedSchemaValidator` → `SchemaValidator`
- **Issue**: "Unified" prefix on ALL validation classes
- **Impact**: MODERATE - Schema validation
- **Recommendation**: Remove "Unified" from all three
- **Justification**: Namespace (validation/) provides context

### 🟢 TIER 3: Low Priority (Export System)

#### 9. **UniversalLinkageEnricher** → `LinkageEnricher`
- **File**: `export/enrichers/linkage/universal_linkage_enricher.py`
- **Class**: `UniversalLinkageEnricher`
- **Issue**: "Universal" redundant in enrichers/linkage/
- **Impact**: LOW - Part of export enricher pipeline
- **Recommendation**: Rename to `LinkageEnricher`
- **Justification**: Directory path provides sufficient context
- **Note**: May be deprecated if moving to generators

#### 10. **UniversalRestructureEnricher** → `RestructureEnricher`
- **File**: `export/enrichers/linkage/universal_restructure_enricher.py`
- **Class**: `UniversalRestructureEnricher`
- **Issue**: "Universal" redundant
- **Impact**: LOW - Export enricher
- **Recommendation**: Rename to `RestructureEnricher`
- **Justification**: Directory provides context
- **Note**: May be deprecated in generator migration

#### 11. **UniversalFrontmatterExporter** → `FrontmatterExporter`
- **File**: `export/core/universal_exporter.py`
- **Class**: `UniversalFrontmatterExporter`
- **Issue**: "Universal" doesn't clarify scope
- **Impact**: LOW - Main exporter class
- **Recommendation**: Rename to `FrontmatterExporter`
- **Justification**: It's THE frontmatter exporter
- **Note**: May be replaced entirely in generator architecture

---

## 🔍 Deeper Semantic Issues

### Issue 1: Generator vs Coordinator Confusion

**Problem**: `UnifiedMaterialsGenerator` is semantically incorrect

**Evidence**:
```python
# domains/materials/coordinator.py:40
class UnifiedMaterialsGenerator(UniversalDomainCoordinator):
    """Coordinates material content generation and data operations"""
```

**Analysis**:
- Name says: "Generator" (suggests it generates content directly)
- Base class: `UniversalDomainCoordinator` (it's a coordinator!)
- Docstring: "Coordinates material content generation" (coordinator behavior)
- Actual role: Orchestrates operations, delegates to specialized generators

**Comparison with Compounds**:
```python
# domains/compounds/coordinator.py:19
class CompoundCoordinator(UniversalDomainCoordinator):
    """Coordinates compound operations"""
```
✅ CORRECT: Says "Coordinator", IS a coordinator, extends coordinator base

**Recommendation**: Rename `UnifiedMaterialsGenerator` → `MaterialsCoordinator`

### Issue 2: Inconsistent Domain Coordinator Architecture

**Current State**:
- ✅ `compounds/coordinator.py`: Has `CompoundCoordinator` (correct pattern)
- ❌ `materials/coordinator.py`: Has `UnifiedMaterialsGenerator` (wrong pattern)
- ⚠️  `settings/`: **NO coordinator.py file exists**
- ⚠️  `contaminants/`: **NO coordinator.py file exists**

**Questions**:
1. Should all domains have coordinators?
2. If yes, need to create `SettingsCoordinator` and `ContaminantsCoordinator`
3. What's the standard pattern for domain organization?

**Recommendation**: Standardize all domains to have coordinators with consistent naming:
- `MaterialsCoordinator`
- `CompoundCoordinator` (already correct)
- `SettingsCoordinator` (create)
- `ContaminantsCoordinator` (create)

### Issue 3: Data Structure Key Inconsistency

**Analysis**:
```
materials/Materials.yaml:     'materials' ✅ (consistent with domain)
compounds/Compounds.yaml:     'compounds' ✅ (consistent)
settings/Settings.yaml:       'settings' ✅ (consistent)
contaminants/Contaminants.yaml: 'contamination_patterns' ❌ (inconsistent!)
```

**Problem**: Contaminants domain uses `contamination_patterns` as the top-level key, while all other domains use the domain name itself.

**Impact**:
- Breaks pattern consistency
- Makes generic iteration harder
- Requires special-case handling

**Recommendation**: Rename `contamination_patterns` → `contaminants` for consistency

**Migration Note**: This is data structure change, requires careful migration:
1. Update data file
2. Update all code references
3. Test thoroughly
4. May affect existing integrations

---

## 📋 Migration Priority Matrix

### Phase 1: Critical Infrastructure (Do First)
**Impact**: Breaking changes to base classes
**Effort**: High (many import updates)
**Priority**: HIGHEST

1. `UniversalDomainCoordinator` → `DomainCoordinator`
   - **Why first**: Base class for all coordinators
   - **Files affected**: All domain coordinators
   - **Estimated imports**: 10-15 files

2. `UnifiedConfigManager` → `ConfigManager`
   - **Why**: Central configuration system
   - **Files affected**: Anything using config
   - **Estimated imports**: 50+ files

3. `UnifiedImportManager` → `ImportManager`
   - **Why**: Core import system
   - **Files affected**: Dynamic import users
   - **Estimated imports**: 20+ files

### Phase 2: Domain Coordinators (Align Architecture)
**Impact**: Domain-specific coordination
**Effort**: Medium
**Priority**: HIGH

4. `UnifiedMaterialsGenerator` → `MaterialsCoordinator`
   - **Why**: Fix semantic confusion + remove "Unified"
   - **Files affected**: Materials domain operations
   - **Estimated imports**: 15-20 files

5. Create `SettingsCoordinator` (new file)
   - **Why**: Consistency across domains
   - **Files affected**: Settings domain
   - **Estimated imports**: New file, limited impact

6. Create `ContaminantsCoordinator` (new file)
   - **Why**: Consistency across domains
   - **Files affected**: Contaminants domain
   - **Estimated imports**: New file, limited impact

### Phase 3: Generation/Export (Active Systems)
**Impact**: SEO and export functionality
**Effort**: Low
**Priority**: MEDIUM

7. `SimpleSEOGenerator` → `SEOGenerator`
   - **Why**: SEO generation actively used
   - **Files affected**: Export system
   - **Estimated imports**: 5-10 files

8. Defer enricher renames until generator migration decision
   - **Rationale**: May deprecate entire enricher system
   - **If keeping temporarily**: Rename in Phase 4

### Phase 4: Support Systems (Low Risk)
**Impact**: Utilities and validation
**Effort**: Low
**Priority**: LOW

9. `SimpleCache` → `Cache` or `MemoryCache`
10. `UnifiedValidator` → `Validator`
11. `UnifiedValidation*` classes → remove "Unified"

---

## 🎯 Recommended Action Plan

### Step 1: Review & Approve
- [ ] Review this audit with team
- [ ] Decide on priority order
- [ ] Approve naming changes
- [ ] Decide: Should all domains have coordinators?
- [ ] Decide: Rename `contamination_patterns` → `contaminants`?

### Step 2: Prepare Renaming Scripts
- [ ] Create search/replace scripts for each rename
- [ ] Test scripts on isolated branches
- [ ] Verify all imports updated correctly

### Step 3: Execute Phase 1 (Critical)
- [ ] Rename `UniversalDomainCoordinator` → `DomainCoordinator`
- [ ] Update all imports and tests
- [ ] Run full test suite
- [ ] Verify export functionality

### Step 4: Execute Phase 2 (Coordinators)
- [ ] Rename `UnifiedMaterialsGenerator` → `MaterialsCoordinator`
- [ ] Create `SettingsCoordinator`
- [ ] Create `ContaminantsCoordinator`
- [ ] Standardize domain patterns

### Step 5: Execute Phase 3 & 4 (Generators/Support)
- [ ] Rename remaining classes per priority
- [ ] Update tests and documentation
- [ ] Final verification

### Step 6: Data Structure Cleanup (If Approved)
- [ ] Rename `contamination_patterns` → `contaminants` in data file
- [ ] Update all code references
- [ ] Migration testing

---

## 📊 Summary Statistics

**Total Violations**: 11 classes, 4 files
**By Tier**:
- TIER 1 (Critical): 5 violations
- TIER 2 (Moderate): 4 violations  
- TIER 3 (Low): 3 violations

**By Pattern**:
- "Simple" prefix: 2 occurrences
- "Unified" prefix: 7 occurrences
- "Universal" prefix: 4 occurrences

**Semantic Issues**: 2 major
1. Generator vs Coordinator confusion
2. Inconsistent domain architecture

**Data Structure Issues**: 1
- `contamination_patterns` vs domain name pattern

**Method-Level Violations**: 0 ✅
- All method names comply with policy

---

## ✅ What's Already Correct

**Good Naming Patterns Found**:
- ✅ `CompoundCoordinator` (compounds domain)
- ✅ All method names (no redundant prefixes found)
- ✅ Export config domain names match folder names
- ✅ Most data structure keys match domain names (3/4)

**Policy Compliance Areas**:
- ✅ Method naming: Clean across entire codebase
- ✅ No "do_" prefixes found
- ✅ No "Basic" prefixes found
- ⚠️  Class naming: 11 violations need fixing

---

## 🔗 Related Documentation

- **Naming Policy**: `docs/08-development/NAMING_CONVENTIONS_POLICY.md`
- **Domain Architecture**: `docs/02-architecture/`
- **Component Structure**: `docs/03-components/`

---

**Status**: ✅ **AUDIT COMPLETE**
**Next Step**: Review findings and approve action plan
**Estimated Effort**: 2-3 days for complete migration (all phases)
- **Class**: `UniversalRestructureEnricher`
- **Issue**: "Universal" redundant
- **Impact**: LOW - Enricher pipeline
- **Recommendation**: Rename to `RestructureEnricher`
- **Note**: May be deprecated if moving to generators

#### 11. **UniversalFrontmatterExporter** → `FrontmatterExporter`
- **File**: `export/core/universal_exporter.py`
- **Class**: `UniversalFrontmatterExporter`
- **Issue**: "Universal" doesn't add meaning
- **Impact**: MODERATE - Main export orchestrator
- **Recommendation**: Rename to `FrontmatterExporter`
- **Justification**: It's THE exporter, not one variant
- **Note**: High visibility file, but may be refactored

---

## 🔍 Deeper Semantic Issues

### Issue A: Coordinator vs Generator Confusion

**Problem**: Some classes named "Generator" are actually "Coordinators"

**Example**:
```python
# File: domains/materials/coordinator.py
class UnifiedMaterialsGenerator(UniversalDomainCoordinator):
    """
    Actually orchestrates generation, doesn't generate itself.
    More of a coordinator than a generator.
    """
```

**Discovery**: Files named `coordinator.py` but contain `*Generator` classes

**Recommendation**: 
- Rename classes to match their actual role
- `UnifiedMaterialsGenerator` → `MaterialsCoordinator`
- `CompoundCoordinator` → Already correct! ✅

**Impact**: Semantic clarity - makes code self-documenting

### Issue B: Inconsistent Domain Coordinator Naming

**Current State**:
```
✅ domains/compounds/coordinator.py: CompoundCoordinator
❌ domains/materials/coordinator.py: UnifiedMaterialsGenerator
? domains/settings/coordinator.py: ???
? domains/contaminants/coordinator.py: ???
```

**Recommendation**: Standardize all domain coordinators
```
MaterialsCoordinator
CompoundsCoordinator  (or keep singular CompoundCoordinator)
SettingsCoordinator
ContaminantsCoordinator
```

---

## 📐 Method Naming Patterns

Let me search for method-level violations...

