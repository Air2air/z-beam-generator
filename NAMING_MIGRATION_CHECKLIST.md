# Naming Convention Migration - Implementation Checklist

**Created**: December 26, 2025  
**Status**: Ready for approval  
**Estimated Time**: 2-3 days  

---

## 📋 Phase 1: Critical Base Classes (1 day + testing)

### 1.1 UniversalDomainCoordinator → DomainCoordinator

- [ ] **Find all usages**:
  ```bash
  grep -r "UniversalDomainCoordinator" --include="*.py"
  ```

- [ ] **Files to update**:
  - [ ] `shared/domain/base_coordinator.py` (class definition)
  - [ ] `domains/materials/coordinator.py` (imports + extends)
  - [ ] `domains/compounds/coordinator.py` (imports + extends)
  - [ ] Any other domain coordinators
  - [ ] Tests referencing this class

- [ ] **Rename steps**:
  1. Update class definition
  2. Update all imports
  3. Update all inheritance declarations
  4. Update docstrings/comments
  5. Run tests: `pytest tests/ -v`

- [ ] **Verification**:
  - [ ] No references to old name remain: `grep -r "UniversalDomainCoordinator"`
  - [ ] All tests pass
  - [ ] Export functionality works

**Estimated Time**: 3-4 hours

---

### 1.2 UnifiedConfigManager → ConfigManager

- [ ] **Find all usages**:
  ```bash
  grep -r "UnifiedConfigManager" --include="*.py"
  ```
  **Expected**: 50+ files

- [ ] **High-priority files** (check first):
  - [ ] `shared/config/manager.py` (class definition)
  - [ ] `run.py` (main entry point)
  - [ ] All domain coordinators
  - [ ] All generators
  - [ ] Export system files

- [ ] **Rename steps**:
  1. Update class definition
  2. Create search/replace script:
     ```python
     # rename_config_manager.py
     import os
     import re
     
     def rename_in_file(filepath):
         with open(filepath, 'r') as f:
             content = f.read()
         
         updated = content.replace('UnifiedConfigManager', 'ConfigManager')
         
         if updated != content:
             with open(filepath, 'w') as f:
                 f.write(updated)
             return True
         return False
     ```
  3. Run script on all Python files
  4. Verify with grep
  5. Run full test suite

- [ ] **Verification**:
  - [ ] `grep -r "UnifiedConfigManager"` returns 0 results
  - [ ] All tests pass: `pytest tests/ -v`
  - [ ] Config loading works: `python3 run.py --help`

**Estimated Time**: 4-5 hours

---

### 1.3 UnifiedImportManager → ImportManager

- [ ] **Find all usages**:
  ```bash
  grep -r "UnifiedImportManager" --include="*.py"
  ```
  **Expected**: 20+ files

- [ ] **Files to update**:
  - [ ] `shared/utils/import_system.py` (class definition)
  - [ ] Dynamic import callers
  - [ ] Plugin/extension loaders
  - [ ] Tests

- [ ] **Rename steps**:
  1. Update class definition
  2. Update all imports
  3. Update all instantiations
  4. Run tests

- [ ] **Verification**:
  - [ ] No old references: `grep -r "UnifiedImportManager"`
  - [ ] Tests pass
  - [ ] Dynamic imports work

**Estimated Time**: 2-3 hours

---

## 📋 Phase 2: Domain Coordinators (0.5 days)

### 2.1 UnifiedMaterialsGenerator → MaterialsCoordinator

- [ ] **Find all usages**:
  ```bash
  grep -r "UnifiedMaterialsGenerator" --include="*.py"
  ```

- [ ] **Files to update**:
  - [ ] `domains/materials/coordinator.py` (class definition)
  - [ ] Any files importing/using this class
  - [ ] Tests

- [ ] **Semantic fix**:
  - [ ] Update class name: `MaterialsCoordinator`
  - [ ] Verify extends `DomainCoordinator` (renamed in Phase 1)
  - [ ] Update docstring to match coordinator role
  - [ ] Ensure behavior is coordination, not direct generation

- [ ] **Verification**:
  - [ ] No old references remain
  - [ ] Materials generation works: `python3 run.py --material "Aluminum"`
  - [ ] Tests pass

**Estimated Time**: 1-2 hours

---

### 2.2 Create SettingsCoordinator (NEW FILE)

- [ ] **Create file**: `domains/settings/coordinator.py`

- [ ] **Template**:
  ```python
  """Settings domain coordinator"""
  from shared.domain.base_coordinator import DomainCoordinator
  
  class SettingsCoordinator(DomainCoordinator):
      """Coordinates settings operations"""
      
      def __init__(self, config):
          super().__init__(config, domain='settings')
      
      # Add settings-specific coordination methods
  ```

- [ ] **Integration**:
  - [ ] Import in `domains/settings/__init__.py`
  - [ ] Update any settings operations to use coordinator
  - [ ] Add tests

- [ ] **Verification**:
  - [ ] Settings export works
  - [ ] Tests pass

**Estimated Time**: 1 hour

---

### 2.3 Create ContaminantsCoordinator (NEW FILE)

- [ ] **Create file**: `domains/contaminants/coordinator.py`

- [ ] **Template**:
  ```python
  """Contaminants domain coordinator"""
  from shared.domain.base_coordinator import DomainCoordinator
  
  class ContaminantsCoordinator(DomainCoordinator):
      """Coordinates contaminants operations"""
      
      def __init__(self, config):
          super().__init__(config, domain='contaminants')
      
      # Add contaminants-specific coordination methods
  ```

- [ ] **Integration**:
  - [ ] Import in `domains/contaminants/__init__.py`
  - [ ] Update contaminants operations
  - [ ] Add tests

- [ ] **Verification**:
  - [ ] Contaminants export works
  - [ ] Tests pass

**Estimated Time**: 1 hour

---

## 📋 Phase 3: Active Systems (0.25 days)

### 3.1 SimpleSEOGenerator → SEOGenerator

- [ ] **Find all usages**:
  ```bash
  grep -r "SimpleSEOGenerator" --include="*.py"
  ```

- [ ] **Files to update**:
  - [ ] `generation/seo/simple_seo_generator.py` (rename file too)
  - [ ] Class definition
  - [ ] All imports
  - [ ] Export system usage

- [ ] **File rename**:
  - [ ] `mv generation/seo/simple_seo_generator.py generation/seo/seo_generator.py`
  - [ ] Update all imports to new path

- [ ] **Verification**:
  - [ ] SEO generation works in export
  - [ ] Tests pass

**Estimated Time**: 1-2 hours

---

### 3.2 Enricher Renames (DEFER)

- [ ] **Decision needed**: 
  - Will enricher system be deprecated in generator migration?
  - If YES: Skip these renames
  - If NO: Rename in Phase 4

- [ ] **If proceeding**:
  - [ ] UniversalLinkageEnricher → LinkageEnricher
  - [ ] UniversalRestructureEnricher → RestructureEnricher
  - [ ] UniversalFrontmatterExporter → FrontmatterExporter

**Status**: ⏸️ DEFERRED pending generator migration decision

---

## 📋 Phase 4: Support Systems (0.25 days)

### 4.1 SimpleCache → Cache or MemoryCache

- [ ] **Decide naming**:
  - [ ] If only cache implementation: `Cache`
  - [ ] If distinguishing from other caches: `MemoryCache`

- [ ] **Find usages**:
  ```bash
  grep -r "SimpleCache" --include="*.py"
  ```

- [ ] **Update**:
  - [ ] Class definition
  - [ ] All imports
  - [ ] Tests

**Estimated Time**: 30 minutes

---

### 4.2 UnifiedValidator → Validator

- [ ] **Find usages**:
  ```bash
  grep -r "UnifiedValidator" --include="*.py"
  ```

- [ ] **Update**:
  - [ ] `shared/validation/validator.py`
  - [ ] All imports
  - [ ] Tests

**Estimated Time**: 30 minutes

---

### 4.3 UnifiedValidation* Classes

- [ ] **Three classes to rename**:
  - [ ] `UnifiedValidationError` → `ValidationError`
  - [ ] `UnifiedValidationResult` → `ValidationResult`
  - [ ] `UnifiedSchemaValidator` → `SchemaValidator`

- [ ] **File**: `shared/services/validation/schema_validator.py`

- [ ] **Update all three + imports**

**Estimated Time**: 1 hour

---

## 📋 Optional: Data Structure Cleanup

### 5.1 Rename contamination_patterns → contaminants (OPTIONAL)

⚠️ **WARNING**: Data structure change - requires careful migration

- [ ] **Decision needed**: Approve this breaking change?

- [ ] **If approved**:
  
  **Backup first**:
  ```bash
  cp data/contaminants/Contaminants.yaml data/contaminants/Contaminants.yaml.backup
  ```

  **Update YAML**:
  - [ ] Change top-level key from `contamination_patterns` to `contaminants`
  - [ ] Verify YAML still valid: `python3 -c "import yaml; yaml.safe_load(open('data/contaminants/Contaminants.yaml'))"`

  **Update all code references**:
  ```bash
  grep -r "contamination_patterns" --include="*.py"
  ```
  - [ ] Update all dictionary access: `data['contamination_patterns']` → `data['contaminants']`
  - [ ] Update documentation
  - [ ] Update tests

  **Verification**:
  - [ ] Export contaminants: `python3 run.py --export --domain contaminants`
  - [ ] All tests pass
  - [ ] No old references remain

**Estimated Time**: 2-3 hours + extensive testing

---

## ✅ Final Verification Checklist

After completing all phases:

- [ ] **Full test suite passes**:
  ```bash
  pytest tests/ -v --tb=short
  ```

- [ ] **No old names remain**:
  ```bash
  # Check for any old class names
  grep -r "UniversalDomainCoordinator\|UnifiedConfigManager\|UnifiedImportManager\|UnifiedMaterialsGenerator\|SimpleSEOGenerator\|SimpleCache\|UnifiedValidator\|UnifiedValidation" --include="*.py" --exclude-dir=".git"
  ```
  **Expected**: 0 results

- [ ] **Export works for all domains**:
  ```bash
  python3 run.py --export --domain materials
  python3 run.py --export --domain contaminants
  python3 run.py --export --domain compounds
  python3 run.py --export --domain settings
  ```

- [ ] **Generation works**:
  ```bash
  python3 run.py --material "Aluminum" --component micro
  ```

- [ ] **Documentation updated**:
  - [ ] Update architecture docs
  - [ ] Update API references
  - [ ] Update developer guide
  - [ ] Update this file's status to "COMPLETE"

---

## 📊 Progress Tracking

| Phase | Items | Status | Time Spent | Notes |
|-------|-------|--------|------------|-------|
| Phase 1 | 3 | ⬜ Not Started | 0h | Base classes |
| Phase 2 | 3 | ⬜ Not Started | 0h | Coordinators |
| Phase 3 | 2 | ⬜ Not Started | 0h | Active systems |
| Phase 4 | 3 | ⬜ Not Started | 0h | Support |
| Optional | 1 | ⬜ Pending Decision | 0h | Data structure |

**Legend**: ⬜ Not Started | 🔄 In Progress | ✅ Complete | ⏸️ Deferred | ❌ Blocked

---

## 🚨 Rollback Plan

If issues occur during migration:

### Quick Rollback (Git)
```bash
# If committed, revert the commit
git revert HEAD

# If not committed, discard changes
git checkout .

# Return to last known good state
git checkout <previous-commit-hash>
```

### Partial Rollback (Per Phase)
- Each phase can be rolled back independently
- Phase 1 changes are breaking - test thoroughly before Phase 2
- Keep backups of data files before structure changes

---

## 📝 Notes & Decisions

**Date: Dec 26, 2025**
- [ ] Approved to proceed with Phase 1? (Y/N)
- [ ] Approved to proceed with Phase 2? (Y/N)
- [ ] Decision on enricher renames? (Rename / Defer / Skip)
- [ ] Decision on data structure rename? (Approve / Defer / Skip)

**Blockers**:
- None currently

**Questions**:
1. Should SettingsCoordinator and ContaminantsCoordinator have the same methods as MaterialsCoordinator?
2. If we're migrating to generators, should we do that BEFORE renaming enrichers?
3. What's the timeline for generator migration?

---

**Status**: ✅ CHECKLIST READY  
**Next Action**: Review with team, get approval, begin Phase 1
