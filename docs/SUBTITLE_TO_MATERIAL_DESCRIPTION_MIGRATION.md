# Subtitle → Material Description Migration Plan

**Date**: November 22, 2025  
**Status**: READY FOR EXECUTION  
**Impact**: 300+ files, Core architecture change

---

## 📋 Overview

This migration restructures how material descriptions are stored across the Z-Beam Generator system:

### **Changes**:
1. **Materials frontmatter**: Remove `subtitle_metadata`, rename `subtitle` → `material_description`, remove `description`
2. **Settings frontmatter**: Add `settings_description` (from materials `description`)
3. **Materials.yaml**: Apply same transformations to source of truth
4. **Code**: Update all references to use new field names
5. **Tests**: Update assertions and expectations
6. **Schema**: Update validation rules
7. **Documentation**: Update field references

---

## 🎯 Rationale

### **Current Structure**:
```yaml
# frontmatter/materials/aluminum-laser-cleaning.yaml
subtitle: "Short description..."         # Used for material overview
subtitle_metadata: {}                     # Empty metadata
description: "Long technical content..." # Technical cleaning details

# frontmatter/settings/aluminum-settings.yaml
subtitle: "Advanced Parameter Configuration..." # Generic subtitle
# (no description field)
```

### **New Structure**:
```yaml
# frontmatter/materials/aluminum-laser-cleaning.yaml
material_description: "Short description..." # Clearer naming
# (subtitle_metadata removed)
# (description moved to settings)

# frontmatter/settings/aluminum-settings.yaml
subtitle: "Advanced Parameter Configuration..." # Unchanged
settings_description: "Long technical content..." # From materials description
```

### **Benefits**:
- **Clearer naming**: `material_description` is more semantic than `subtitle`
- **Proper separation**: Technical content in settings, overview in materials
- **Reduced duplication**: Remove unused `subtitle_metadata`
- **Better structure**: Each file has appropriate content

---

## 📂 Files Affected

### **Data Files**:
- `data/materials/Materials.yaml` (1 file, 132 materials)

### **Frontmatter Files**:
- `frontmatter/materials/*.yaml` (132 files)
- `frontmatter/materials-new/*.yaml` (20 files)
- `frontmatter/settings/*.yaml` (132 files)
- `frontmatter/settings-new/*.yaml` (20 files)
- **Total**: 304 YAML files

### **Python Code** (Estimated 30-40 files):
- `export/core/trivial_exporter.py` - Frontmatter generation
- `export/core/streamlined_generator.py` - Generation logic
- `export/core/hybrid_generation_manager.py` - Field management
- `generation/core/simple_generator.py` - Component generation
- `generation/core/batch_generator.py` - Batch operations
- `generation/utils/frontmatter_sync.py` - Sync utilities
- `generation/config/*.py` - Configuration files
- `shared/commands/generation.py` - CLI commands
- All test files referencing these fields

### **Schema/Validation**:
- Schema definition files
- Validation rules
- Type definitions

### **Documentation**:
- Component documentation
- API references
- Generation guides

---

## 🚀 Migration Steps

### **Phase 1: Data Migration** (Script-based)

Run the migration script:
```bash
# Dry run first (verify changes)
python3 scripts/migrations/migrate_subtitle_to_material_description.py --dry-run

# Apply changes
python3 scripts/migrations/migrate_subtitle_to_material_description.py --confirm
```

This handles:
- ✅ Materials.yaml transformations
- ✅ All frontmatter/materials files
- ✅ All frontmatter/settings files

### **Phase 2: Code Updates** (Manual)

#### **2.1: Export/Generation Code**

**File**: `export/core/trivial_exporter.py`
- Line 241: Update field list `'subtitle'` → `'material_description'`
- Line 317-322: Update component handling
- Line 374-375: Update material page generation
- Remove subtitle_metadata handling (line 245, 375)

**File**: `export/core/streamlined_generator.py`
- Update subtitle references to material_description
- Update skip_subtitle parameter to skip_material_description

**File**: `export/core/hybrid_generation_manager.py`
- Line 318: Update field_name == 'subtitle' check
- Add field_name == 'material_description' case
- Add settings_description handling

#### **2.2: Generation Core**

**File**: `generation/core/simple_generator.py`
- Line 334: Update component list check
- Add material_description to valid components

**File**: `generation/core/batch_generator.py`
- Line 49: Update 'subtitle' → 'material_description'
- Line 169: Update component_type assignment

**File**: `generation/utils/frontmatter_sync.py`
- Line 55, 79: Update field name references
- Add material_description and settings_description

#### **2.3: CLI/Commands**

**File**: `run.py`
- Update --subtitle flag to --material-description
- Update help text and documentation

**File**: `shared/commands/generation.py`
- Update command handlers
- Update success messages

#### **2.4: Configuration**

**File**: `generation/config/validate_config.py`
- Line 111, 123: Update component type lists

**File**: `generation/config.yaml`
- Update component_lengths section
- Rename subtitle → material_description

### **Phase 3: Test Updates**

Update all test files:
- Replace `subtitle` assertions with `material_description`
- Remove `subtitle_metadata` expectations
- Add `settings_description` assertions for settings tests
- Update mock data and fixtures

### **Phase 4: Schema Updates**

- Update YAML schema definitions
- Update validation rules
- Update type hints and interfaces

### **Phase 5: Documentation Updates**

- Update all documentation referencing subtitle
- Update API documentation
- Update generation guides
- Update component architecture docs

---

## ✅ Verification Checklist

After migration, verify:

### **Data Integrity**:
- [ ] All 152 materials files have `material_description`
- [ ] All 152 settings files have `settings_description`
- [ ] No materials files have `subtitle` or `subtitle_metadata`
- [ ] No materials files have `description`
- [ ] Materials.yaml reflects all changes

### **Code Functionality**:
- [ ] `python3 run.py --material-description "Aluminum"` works
- [ ] Generation saves to correct field names
- [ ] Frontmatter sync updates correct fields
- [ ] Deploy exports correct field names

### **Tests**:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] No references to old field names in tests

### **Production**:
- [ ] Run `python3 run.py --deploy` successfully
- [ ] Verify exported files have correct structure
- [ ] Check Next.js site renders correctly

---

## 🔄 Rollback Plan

If migration fails:

```bash
# Restore from git
git checkout HEAD -- data/materials/Materials.yaml
git checkout HEAD -- frontmatter/materials/
git checkout HEAD -- frontmatter/materials-new/
git checkout HEAD -- frontmatter/settings/
git checkout HEAD -- frontmatter/settings-new/

# Verify restoration
git status
```

---

## 📊 Estimated Timeline

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Data Migration Script | 30min | ✅ Complete |
| 2 | Code Updates | 2-3hrs | ⏳ Pending |
| 3 | Test Updates | 1-2hrs | ⏳ Pending |
| 4 | Schema Updates | 30min | ⏳ Pending |
| 5 | Documentation | 1hr | ⏳ Pending |
| 6 | Testing & Verification | 1hr | ⏳ Pending |
| **Total** | | **6-8 hours** | |

---

## 🚨 Critical Notes

1. **Backup First**: Commit current state before migration
2. **Test Thoroughly**: Run full test suite after each phase
3. **Deploy Last**: Only deploy after all tests pass
4. **Coordinate**: This affects frontend rendering - coordinate with Next.js team

---

## 📝 Next Steps

**Ready to proceed? Execute in order:**

1. ✅ Review this plan
2. ⏳ Run migration script with --confirm
3. ⏳ Update code (Phase 2)
4. ⏳ Update tests (Phase 3)
5. ⏳ Update schema (Phase 4)
6. ⏳ Update docs (Phase 5)
7. ⏳ Verify & test (Phase 6)
8. ⏳ Commit & deploy

---

**Questions or concerns? Discuss before proceeding with Phase 2.**
