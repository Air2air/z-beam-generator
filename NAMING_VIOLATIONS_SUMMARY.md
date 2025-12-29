# Naming Violations - Quick Reference

## 📊 11 Violations Found

### 🔴 TIER 1: Critical (5) - Fix First

| Current Name | Recommended | File | Impact |
|--------------|-------------|------|--------|
| `SimpleSEOGenerator` | `SEOGenerator` | generation/seo/simple_seo_generator.py | HIGH |
| `UnifiedConfigManager` | `ConfigManager` | shared/config/manager.py | **CRITICAL** |
| `UnifiedImportManager` | `ImportManager` | shared/utils/import_system.py | HIGH |
| `UniversalDomainCoordinator` | `DomainCoordinator` | shared/domain/base_coordinator.py | **CRITICAL** |
| `UnifiedMaterialsGenerator` | `MaterialsCoordinator` | domains/materials/coordinator.py | HIGH + Semantic |

### 🟡 TIER 2: Moderate (4) - Fix Second

| Current Name | Recommended | File | Impact |
|--------------|-------------|------|--------|
| `SimpleCache` | `Cache` or `MemoryCache` | shared/utils/cache_utils.py | MODERATE |
| `UnifiedValidator` | `Validator` | shared/validation/validator.py | MODERATE |
| `UnifiedValidationError` | `ValidationError` | shared/services/validation/schema_validator.py | MODERATE |
| `UnifiedValidationResult` | `ValidationResult` | shared/services/validation/schema_validator.py | MODERATE |
| `UnifiedSchemaValidator` | `SchemaValidator` | shared/services/validation/schema_validator.py | MODERATE |

### 🟢 TIER 3: Low Priority (3) - Defer or Fix with Generator Migration

| Current Name | Recommended | File | Note |
|--------------|-------------|------|------|
| `UniversalLinkageEnricher` | `LinkageEnricher` | export/enrichers/linkage/universal_linkage_enricher.py | May deprecate |
| `UniversalRestructureEnricher` | `RestructureEnricher` | export/enrichers/linkage/universal_restructure_enricher.py | May deprecate |
| `UniversalFrontmatterExporter` | `FrontmatterExporter` | export/core/universal_exporter.py | May replace |

---

## 🎯 Critical Semantic Issues

### Issue 1: Generator vs Coordinator Mismatch
```
❌ UnifiedMaterialsGenerator (materials/coordinator.py)
   - Name says "Generator" but it's actually a Coordinator
   - Extends UniversalDomainCoordinator
   - Docstring says "Coordinates material operations"
   
✅ Recommended: MaterialsCoordinator
```

### Issue 2: Inconsistent Domain Architecture
```
✅ compounds/coordinator.py:  CompoundCoordinator (correct)
❌ materials/coordinator.py:  UnifiedMaterialsGenerator (wrong name + semantic)
⚠️  settings/:                NO COORDINATOR FILE
⚠️  contaminants/:            NO COORDINATOR FILE
```

**Recommendation**: Create coordinators for all domains
- MaterialsCoordinator (rename existing)
- CompoundCoordinator (already correct)
- SettingsCoordinator (create new)
- ContaminantsCoordinator (create new)

### Issue 3: Data Structure Key Inconsistency
```
✅ Materials.yaml:      'materials'
✅ Compounds.yaml:      'compounds'
✅ Settings.yaml:       'settings'
❌ Contaminants.yaml:   'contamination_patterns' (should be 'contaminants')
```

---

## 🚀 Quick Action Plan

### Phase 1: Critical Base Classes (Breaking Changes)
1. `UniversalDomainCoordinator` → `DomainCoordinator` (affects all coordinators)
2. `UnifiedConfigManager` → `ConfigManager` (affects 50+ files)
3. `UnifiedImportManager` → `ImportManager` (affects 20+ files)

**Estimated Effort**: 1 day + testing

### Phase 2: Domain Coordinators (Architecture Alignment)
4. `UnifiedMaterialsGenerator` → `MaterialsCoordinator`
5. Create `SettingsCoordinator`
6. Create `ContaminantsCoordinator`

**Estimated Effort**: 0.5 days

### Phase 3: Active Systems (SEO, Export)
7. `SimpleSEOGenerator` → `SEOGenerator`
8. Defer enricher renames (may deprecate in generator migration)

**Estimated Effort**: 0.25 days

### Phase 4: Support Systems (Low Risk)
9. Cache, Validator, Validation classes

**Estimated Effort**: 0.25 days

**Total Estimated Time**: 2-3 days for complete migration

---

## ✅ Clean Areas (No Action Needed)

- ✅ Method naming: 0 violations found
- ✅ Export config: Domain names consistent
- ✅ 75% of data structure keys consistent
- ✅ CompoundCoordinator already follows correct pattern

---

**Full Details**: See `NAMING_AUDIT_DEC26_2025.md`
