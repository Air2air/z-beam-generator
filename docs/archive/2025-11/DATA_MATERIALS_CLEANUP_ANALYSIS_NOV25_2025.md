# Data/Materials Cleanup Analysis - November 25, 2025

**Status**: 🔍 ANALYSIS COMPLETE - Cleanup recommendations ready  
**Scope**: Evaluate `data/materials/` vs `domains/materials/` structure  
**Goal**: Identify files that belong in domains vs data

---

## Executive Summary

**Current State**:
- `data/materials/`: **~2,500 lines of Python code** + 27 YAML files + subdirectories
- `domains/materials/`: **52 Python files** (proper generator location)

**Problem**: `data/materials/` contains generator/logic code that belongs in `domains/materials/`

**Recommendation**: **Migrate 2 Python files**, **keep 15 YAML files**, **archive 12+ old files**

---

## Current Structure Analysis

### data/materials/ (What's There Now)

#### ✅ CORRECT - Should Stay (Core Data)
1. **Materials.yaml** (23K lines) - 159 materials with properties ✅
2. **MaterialProperties.yaml** - Property values and ranges ✅
3. **Settings.yaml** - Laser machine settings (migrated from MachineSettings.yaml) ✅
4. **Categories.yaml** - Material categories (may be deprecated by CategoryTaxonomy.yaml)
5. **CategoryTaxonomy.yaml** - Category taxonomy structure ✅
6. **IndustryApplications.yaml** - Industry application metadata ✅
7. **PropertyDefinitions.yaml** - Property metadata and definitions ✅
8. **ParameterDefinitions.yaml** - Parameter metadata and ranges ✅
9. **RegulatoryStandards.yaml** - Regulatory standards ✅
10. **PropertyResearch.yaml** - AI-researched property values ✅
11. **SettingResearch.yaml** - AI-researched settings ✅
12. **frontmatter_template.yaml** - Template structure ✅

**Total Core Data YAML**: ~15 files ✅

#### ❌ WRONG LOCATION - Python Generator Code (Should Move)
1. **loader.py** (1,054 lines) - Data loading logic
   - **Problem**: Generator/logic code in data folder
   - **Fix**: Migrate to `domains/materials/loaders/` or merge with existing loaders
   - **Used By**: 30+ files across codebase

2. **materials.py** (351 lines) - Cached data loading
   - **Problem**: Generator/logic code with caching optimization
   - **Fix**: Migrate to `domains/materials/loaders/` or `domains/materials/utils/`
   - **Used By**: 20+ files for cached material access

3. **__init__.py** (82 lines) - Module initialization
   - **Problem**: Makes data/materials act like a Python package
   - **Fix**: Keep minimal version for backward compatibility during migration

**Total Generator Code**: ~2,500 lines in wrong location ❌

#### 🗑️ CLEANUP NEEDED - Old/Redundant Files

**Backups** (can be archived):
- `Materials.yaml.backup`
- `Materials.yaml.backup_20251124_230544`
- `Materials.yaml.backup_nov24`
- `archive/` directory (5+ old files)

**Possibly Deprecated**:
- `MachineSettings.yaml` - **MIGRATED to Settings.yaml** (Nov 24, 2025)
  - ✅ Can be archived/removed if migration complete
  - ⚠️ Verify no references before removing

- `Categories.yaml` vs `CategoryTaxonomy.yaml` - **Duplicate?**
  - Check which is canonical
  - Archive the unused one

**Subdirectories**:
- `content/` - Contains Captions.yaml, FAQs.yaml, RegulatoryStandards.yaml
  - ⚠️ RegulatoryStandards.yaml duplicates root file
  - May be legacy content storage
  
- `categories/` - Contains property_system.yaml
  - Check if still used or superseded by CategoryTaxonomy.yaml

- `research/` - Contains metals/, stone/, wood/, other/ subdirectories
  - Check if this is old research data or still active
  - May belong in `domains/materials/research/` instead

### domains/materials/ (Proper Generator Location)

#### ✅ CORRECT Structure
- **52 Python files** organized into:
  - `category_loader.py` - Category data access ✅
  - `coordinator.py` - Generation orchestration ✅
  - `schema.py` - Type-safe data structures ✅
  - `image/` - Image generation ✅
  - `modules/` - Frontmatter modules ✅
  - `research/` - AI research tools ✅
  - `services/` - Business logic ✅
  - `utils/` - Helper functions ✅
  - `validation/` - Data validation ✅

**This is the CORRECT architecture** ✅

---

## Migration Plan

### Phase 1: Migrate Python Code (Priority: HIGH)

**Goal**: Move generator code from `data/materials/` to `domains/materials/`

#### Step 1.1: Create New Loader Module
```bash
# Create domains/materials/loaders/ directory
mkdir -p domains/materials/loaders/

# Migrate loader.py
cp data/materials/loader.py domains/materials/loaders/materials_loader.py

# Migrate materials.py (caching functionality)
cp data/materials/materials.py domains/materials/loaders/cached_materials_loader.py
```

#### Step 1.2: Update Imports (30+ files affected)
```python
# OLD (wrong location)
from data.materials.loader import load_materials_data, load_material
from data.materials.materials import load_materials_cached, get_material_by_name_cached

# NEW (correct location)
from domains.materials.loaders.materials_loader import load_materials_data, load_material
from domains.materials.loaders.cached_materials_loader import load_materials_cached, get_material_by_name_cached
```

**Files to Update** (~30 files):
- `generation/core/quality_gated_generator.py`
- `export/core/streamlined_generator.py`
- `export/core/trivial_exporter.py`
- `export/core/hybrid_generation_manager.py`
- `export/research/property_value_researcher.py`
- `scripts/research/populate_deep_research.py`
- `scripts/validation/validate_data_extraction.py`
- `scripts/validation/fail_fast_materials_validator.py`
- `scripts/tools/normalize_materials_to_template.py`
- `scripts/migration/import_new_materials.py`
- `scripts/tools/migrate_other_properties.py`
- `scripts/voice/enhance_materials_voice.py`
- `scripts/operations/regenerate_all_frontmatter.py`
- `scripts/operations/clear_cache_and_regenerate.py`
- ...and ~16 more files

**Effort**: 2-3 hours (automated find/replace with verification)

#### Step 1.3: Keep Minimal Backward Compatibility
```python
# data/materials/__init__.py (keep for transition period)
"""
DEPRECATED: Import from domains.materials.loaders instead.
This module provides backward compatibility during migration.
"""
import warnings

def __getattr__(name):
    warnings.warn(
        f"Importing {name} from data.materials is deprecated. "
        f"Use domains.materials.loaders instead.",
        DeprecationWarning,
        stacklevel=2
    )
    from domains.materials.loaders import materials_loader
    return getattr(materials_loader, name)
```

---

### Phase 2: Clean Up Old Files (Priority: MEDIUM)

#### Step 2.1: Archive Old Backups
```bash
# Move backups to archive
mv data/materials/Materials.yaml.backup data/materials/archive/
mv data/materials/Materials.yaml.backup_20251124_230544 data/materials/archive/
mv data/materials/Materials.yaml.backup_nov24 data/materials/archive/
```

#### Step 2.2: Remove Migrated MachineSettings.yaml
```bash
# Verify Settings.yaml migration complete
python3 -c "from domains.materials.loaders.materials_loader import load_settings_yaml; print(len(load_settings_yaml()))"

# If successful, archive old file
mv data/materials/MachineSettings.yaml data/materials/archive/MachineSettings_MIGRATED_NOV24.yaml

# Update BACKUP_RETENTION_POLICY.md
```

#### Step 2.3: Resolve Category File Duplication
```bash
# Check which is canonical
diff data/materials/Categories.yaml data/materials/CategoryTaxonomy.yaml

# If CategoryTaxonomy.yaml is canonical:
mv data/materials/Categories.yaml data/materials/archive/Categories_LEGACY.yaml
```

#### Step 2.4: Clean Up Content Directory
```bash
# Check if content/ is still used
grep -r "data/materials/content" . --include="*.py"

# If unused or deprecated:
# - Archive Captions.yaml (if superseded by unified system)
# - Archive FAQs.yaml (if superseded by unified system)
# - Remove duplicate RegulatoryStandards.yaml
```

---

### Phase 3: Reorganize Research Data (Priority: LOW)

#### Step 3.1: Evaluate Research Subdirectory
```bash
# Check what's in research/
ls -la data/materials/research/*/

# Determine if this is:
# A) Active research data → Keep
# B) Old research data → Archive
# C) Should be in domains/materials/research/ → Move
```

#### Step 3.2: Consolidate Category Metadata
```bash
# Check categories/ subdirectory
cat data/materials/categories/property_system.yaml

# Determine if superseded by CategoryTaxonomy.yaml
# If yes: archive
# If no: keep or merge
```

---

## Impact Analysis

### Before Cleanup
```
data/materials/
├── Python code: 2,500 lines (❌ WRONG LOCATION)
├── Core YAML: ~15 files (✅ CORRECT)
├── Backups: 3-5 files (🗑️ CAN ARCHIVE)
├── Old files: 5+ archived files
├── Subdirectories: content/, categories/, research/
└── Total: ~30+ files, mixed purpose

domains/materials/
├── Generator code: 52 Python files (✅ CORRECT)
├── Proper architecture ✅
└── No data files ✅
```

### After Cleanup
```
data/materials/
├── Python code: 0 lines (✅ PURE DATA)
├── Core YAML: ~15 files (✅ STREAMLINED)
├── Backups: Archived (✅ CLEAN)
├── Deprecated: Archived (✅ CLEAN)
└── Total: ~15 YAML files, pure data ✅

domains/materials/
├── Generator code: 54 Python files (+2 migrated)
├── Proper architecture ✅
├── loaders/ subdirectory (NEW) ✅
└── All logic in correct location ✅
```

---

## Benefits of Cleanup

### 1. Clear Separation of Concerns ✅
- **data/** = Pure data (YAML files only)
- **domains/** = Generator logic (Python code)
- **No more confusion** about where to add code

### 2. Easier Maintenance ✅
- Data changes don't affect generator code
- Generator changes don't affect data structure
- Import paths reflect actual purpose

### 3. Better Discoverability ✅
- Developers look in `domains/materials/` for ALL materials code
- Data scientists look in `data/materials/` for YAML files only
- No "Is this data or code?" questions

### 4. Consistent with Other Domains ✅
- `domains/contaminants/` has proper structure already
- `data/contaminants/` is pure YAML
- Materials should match this pattern

### 5. Reduced File Count ✅
- `data/materials/`: 30+ files → ~15 files (-50%)
- Archive old backups and deprecated files
- Cleaner directory listings

---

## Rollout Strategy

### Week 1: Migration Preparation
1. ✅ Create `domains/materials/loaders/` directory
2. ✅ Copy loader.py → materials_loader.py (verify works)
3. ✅ Copy materials.py → cached_materials_loader.py (verify works)
4. ✅ Add deprecation warnings to old imports

### Week 2: Gradual Import Updates
1. Update 10 files per day (morning batch)
2. Run tests after each batch
3. Fix any import issues immediately
4. Total: 30 files over 3 days

### Week 3: Cleanup & Archive
1. Archive old backups (Monday)
2. Archive deprecated files (Tuesday)
3. Remove old Python files from data/ (Wednesday)
4. Update documentation (Thursday)
5. Final verification (Friday)

### Rollback Plan
If issues arise:
1. Revert import changes (git checkout)
2. Keep both locations temporarily
3. Fix issues before re-attempting
4. Deprecation warnings still provide guidance

---

## Testing Strategy

### Before Migration
```bash
# Baseline tests
python3 -m pytest tests/ -v
python3 run.py --test

# Verify loader functionality
python3 -c "from data.materials.loader import load_materials_data; print(len(load_materials_data()))"
python3 -c "from data.materials.materials import load_materials_cached; print(len(load_materials_cached()))"
```

### After Migration (Each File)
```bash
# Verify new imports work
python3 -c "from domains.materials.loaders.materials_loader import load_materials_data; print(len(load_materials_data()))"
python3 -c "from domains.materials.loaders.cached_materials_loader import load_materials_cached; print(len(load_materials_cached()))"

# Run affected tests
python3 -m pytest tests/test_[affected_module].py -v

# Verify generation still works
python3 run.py --material "Aluminum" --data-only
```

### Final Verification
```bash
# Full test suite
python3 -m pytest tests/ -v
python3 run.py --test

# Integration test
python3 run.py --material "Steel"
python3 run.py --caption "Copper"

# Verify no old imports remain
grep -r "from data.materials.loader import" --include="*.py" | grep -v "archive/" | grep -v "__pycache__"
grep -r "from data.materials.materials import" --include="*.py" | grep -v "archive/" | grep -v "__pycache__"
```

---

## Recommended Execution Order

### Immediate (This Week)
1. ✅ **Create analysis document** (this file) - DONE
2. ✅ **Review with team** - Get approval for migration plan
3. ✅ **Create backup** - Full data/materials/ backup before changes

### Phase 1 (Week 1)
4. Create `domains/materials/loaders/` directory
5. Migrate loader.py → materials_loader.py
6. Migrate materials.py → cached_materials_loader.py  
7. Add deprecation warnings

### Phase 2 (Week 2)
8. Update imports in 30+ files (batched)
9. Run tests after each batch
10. Fix any issues immediately

### Phase 3 (Week 3)
11. Archive old backups
12. Archive deprecated files
13. Remove old Python files
14. Update documentation

---

## Files to Migrate

### Confirmed Migrations

#### 1. loader.py (1,054 lines)
- **From**: `data/materials/loader.py`
- **To**: `domains/materials/loaders/materials_loader.py`
- **Purpose**: Core materials data loading
- **Used By**: 15+ files
- **Priority**: HIGH

#### 2. materials.py (351 lines)
- **From**: `data/materials/materials.py`
- **To**: `domains/materials/loaders/cached_materials_loader.py`
- **Purpose**: Cached materials loading with TTL
- **Used By**: 15+ files
- **Priority**: HIGH

#### 3. __init__.py (82 lines)
- **From**: `data/materials/__init__.py`
- **To**: Keep minimal version with deprecation warnings
- **Purpose**: Backward compatibility during transition
- **Priority**: MEDIUM

---

## Risk Assessment

### Low Risk ✅
- **Pure Python code migration** - No data changes
- **Gradual rollout** - Update 10 files per day
- **Deprecation warnings** - Catch missed imports
- **Full test coverage** - Verify each change
- **Easy rollback** - Git revert if needed

### Medium Risk ⚠️
- **30+ files to update** - Time-consuming but straightforward
- **Import path changes** - Could miss some files
- **Cached imports** - May need Python restart in dev environments

### Mitigation
- Automated grep to find ALL import references
- Update imports in batches with verification
- Run full test suite after each batch
- Keep old location working with deprecation warnings
- 2-week parallel operation period before removal

---

## Success Criteria

### ✅ Migration Complete When:
1. All imports updated to `domains/materials/loaders/`
2. All tests passing
3. No references to `data/materials/loader` or `data/materials/materials`
4. Old Python files archived
5. Documentation updated

### ✅ Cleanup Complete When:
1. `data/materials/` contains only YAML files
2. Old backups archived
3. Deprecated files removed/archived
4. Directory structure matches contaminants domain
5. Documentation reflects new structure

---

## Conclusion

**Recommendation**: **EXECUTE MIGRATION**

**Why**:
- Clear architectural violation (generator code in data/)
- Affects 30+ files but straightforward fixes
- Low risk with gradual rollout
- Aligns with contaminants domain structure
- Improves long-term maintainability

**Timeline**: 3 weeks (prep + migration + cleanup)  
**Effort**: ~8-12 hours total (2-3 hours per week)  
**Impact**: +Clean architecture, -confusion, -file count

**Next Step**: Get team approval, then start Phase 1 (create loaders/ directory)
