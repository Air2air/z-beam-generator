# Settings Domain Separation - Evaluation & Roadmap

**Date**: November 26, 2025
**Current Status**: Settings.yaml exists in `data/materials/` but lacks domain separation

---

## 📊 Current State Analysis

### File Locations

**Data Files**:
```
data/materials/
├── Materials.yaml          (159 materials, 4.8 MB)
├── Settings.yaml           (159 materials, 616 KB)
├── MaterialProperties.yaml
├── Categories.yaml
└── ... (other files)
```

**Domain Folders**:
```
domains/
├── materials/              ✅ Full domain structure
│   ├── data_loader.py      (loads Settings.yaml)
│   ├── modules/
│   │   └── settings_module.py
│   └── ... (coordinator, cache, etc.)
├── contaminants/           ✅ Separate domain
│   └── data/Contaminants.yaml
└── settings/               ❌ DOES NOT EXIST
```

### Current Architecture Issues

1. **Mixed Data Location**:
   - Settings.yaml in `data/materials/` (should be `data/settings/`)
   - Creates false coupling between materials and settings domains

2. **Missing Domain Folder**:
   - No `domains/settings/` structure
   - Settings logic embedded in materials domain
   - SettingsModule exists but in materials domain

3. **Cross-Domain Dependencies**:
   - Export code loads Settings.yaml from materials path
   - Generation code writes to Settings.yaml in materials path
   - Tests reference materials path for Settings.yaml

4. **Conceptual Mismatch**:
   - Settings are MACHINE/PROCESS data (how to process)
   - Materials are PHYSICAL data (what to process)
   - Different lifecycle, different ownership, different update frequency

---

## 🔍 Dependency Analysis

### Files Referencing Settings.yaml

| File | Type | Impact | Update Needed |
|------|------|--------|---------------|
| `export/core/trivial_exporter.py` | Export | HIGH | Path update |
| `generation/core/simple_generator.py` | Generation | HIGH | Path update |
| `domains/materials/data_loader.py` | Data loader | HIGH | Path update + move logic |
| `tests/test_data_architecture_separation.py` | Test | MEDIUM | Path update |
| `scripts/research/generate_missing_settings.py` | Script | LOW | Path update |
| `domains/materials/modules/settings_module.py` | Module | HIGH | Move to settings domain |

---

## ✨ Benefits of Separation

### Architectural Benefits

1. **Clear Domain Boundaries**:
   - Settings domain owns ALL settings-related logic and data
   - Materials domain focuses ONLY on material properties
   - Matches existing contaminants domain pattern

2. **Independent Evolution**:
   - Settings can be updated without touching materials code
   - Different teams can own different domains
   - Easier to add new settings-related features

3. **Consistent Architecture**:
   - All domains follow same pattern: `domains/X/` + `data/X/`
   - Easier to understand and maintain
   - Better onboarding for new developers

4. **Clearer Data Ownership**:
   - `data/materials/Materials.yaml` → material properties
   - `data/settings/Settings.yaml` → machine settings
   - `data/contaminants/Contaminants.yaml` → contamination data

---

## 🎯 Proposed Structure

### New Directory Layout

```
data/
├── materials/
│   ├── Materials.yaml
│   ├── MaterialProperties.yaml
│   └── Categories.yaml
└── settings/                    # NEW
    └── Settings.yaml           # MOVED from data/materials/

domains/
├── materials/
│   ├── data_loader.py          (materials only)
│   ├── materials_cache.py
│   └── modules/
│       ├── properties_module.py
│       └── (remove settings_module.py)
└── settings/                   # NEW
    ├── __init__.py
    ├── data_loader.py         # Settings.yaml loader
    ├── settings_cache.py      # Cache for settings
    └── modules/
        └── settings_module.py  # MOVED from materials
```

---

## 📋 Migration Steps

### Phase 1: Create New Structure (No Breaking Changes)

**Time Estimate**: 1-2 hours

1. **Create directories**:
   ```bash
   mkdir -p data/settings
   mkdir -p domains/settings/modules
   touch domains/settings/__init__.py
   ```

2. **Copy Settings.yaml** (don't delete original yet):
   ```bash
   cp data/materials/Settings.yaml data/settings/Settings.yaml
   ```

3. **Create settings domain loader**:
   - `domains/settings/data_loader.py` - Load Settings.yaml from new location
   - Similar pattern to `domains/materials/data_loader.py`
   - Include caching with `@lru_cache`

4. **Move settings_module.py**:
   ```bash
   mv domains/materials/modules/settings_module.py domains/settings/modules/
   ```
   - Update imports in moved file

5. **Create settings_cache.py**:
   - Pattern from `domains/materials/materials_cache.py`
   - Cache loaded settings data

### Phase 2: Update References (Breaking Changes)

**Time Estimate**: 2-3 hours

**Critical Files to Update**:

1. **`export/core/trivial_exporter.py`**:
   - Change: `from domains.materials.data_loader import ...`
   - To: `from domains.settings.data_loader import load_settings`
   - Update `_load_settings()` method to use new loader

2. **`generation/core/simple_generator.py`**:
   ```python
   # OLD:
   settings_path = Path("data/materials/Settings.yaml")
   
   # NEW:
   from domains.settings.data_loader import get_settings_path
   settings_path = get_settings_path()
   ```

3. **`domains/materials/data_loader.py`**:
   - Remove `load_settings_yaml()` function
   - Remove `SETTINGS_FILE` constant
   - Remove settings-related functions
   - Document that settings moved to separate domain

4. **`tests/test_data_architecture_separation.py`**:
   ```python
   # OLD:
   cls.settings_path = Path("data/materials/Settings.yaml")
   
   # NEW:
   cls.settings_path = Path("data/settings/Settings.yaml")
   ```

5. **Update all script references**:
   - `scripts/research/generate_missing_settings.py`
   - Any other scripts that reference Settings.yaml path

### Phase 3: Cleanup & Verification

**Time Estimate**: 1 hour

1. **Delete old Settings.yaml**:
   ```bash
   rm data/materials/Settings.yaml
   rm data/materials/Settings_backup_*.yaml  # Optional: move to data/settings/
   ```

2. **Run all tests**:
   ```bash
   python3 -m pytest tests/test_data_architecture_separation.py -v
   python3 -m pytest tests/ -v  # Run full suite
   ```

3. **Test export & deployment**:
   ```bash
   python3 run.py --deploy
   ```

4. **Update documentation**:
   - `DATA_ARCHITECTURE_SEPARATION.md` - Update paths
   - `data/materials/README.md` - Remove Settings.yaml references
   - Create `data/settings/README.md` - Document settings structure
   - Update `DOCUMENTATION_MAP.md`

---

## ⚠️ Risks & Mitigation

### Risk 1: Breaking Changes
**Impact**: HIGH - Code will fail if Settings.yaml path is wrong

**Mitigation**:
- Do Phase 1 completely before Phase 2
- Keep old Settings.yaml until all references updated
- Test each file update individually
- Use git branches for safe rollback

### Risk 2: Missing References
**Impact**: MEDIUM - Some code might still reference old path

**Mitigation**:
```bash
# Search for all references before deleting
grep -r "data/materials/Settings" . --exclude-dir=.git
grep -r "Settings\.yaml" . --exclude-dir=.git | grep -v "data/settings"
```

### Risk 3: Import Errors
**Impact**: MEDIUM - Moved modules may cause import failures

**Mitigation**:
- Update all imports simultaneously
- Add `__init__.py` with proper exports
- Test imports: `python3 -c 'from domains.settings.data_loader import load_settings'`

---

## ⏱️ Estimated Effort

| Phase | Tasks | Time | Risk |
|-------|-------|------|------|
| Phase 1 | Create structure, copy files | 1-2 hours | LOW |
| Phase 2 | Update all references | 2-3 hours | MEDIUM |
| Phase 3 | Cleanup & verification | 1 hour | LOW |
| **TOTAL** | **Complete separation** | **4-6 hours** | **MEDIUM** |

---

## 💡 Recommendation

### Should We Do This?

**YES - Recommended**, but NOT urgent. Here's why:

**Pros**:
- ✅ Cleaner architecture (matches contaminants pattern)
- ✅ Easier to maintain long-term
- ✅ Better domain separation
- ✅ Supports independent evolution

**Cons**:
- ⚠️ Requires 4-6 hours of focused work
- ⚠️ Breaking changes (must update all references)
- ⚠️ Current system works fine as-is

### When to Do This?

**Best Time**: During a planned refactoring sprint or when:
1. Adding significant new settings-related features
2. Expanding settings domain with new data types
3. Multiple developers working on different domains
4. After current development cycle completes

**NOT Now If**:
- Critical deadlines approaching
- Major features in active development
- System stability is priority over architecture

---

## 🔀 Alternative Approaches

### Option A: Full Separation (Recommended Above)
**Effort**: 4-6 hours
**Benefit**: Complete domain independence

### Option B: Symbolic Links
**Effort**: 30 minutes
**Benefit**: Quick fix, minimal code changes

```bash
mkdir -p data/settings
ln -s ../materials/Settings.yaml data/settings/Settings.yaml
```

**Pros**: Fast, maintains backward compatibility
**Cons**: Not true separation, confusing structure

### Option C: Do Nothing
**Effort**: 0 hours
**Benefit**: No risk, system works

**When to choose**: If architecture doesn't cause actual problems

---

## 📊 Summary

```
Current:  data/materials/Settings.yaml (mixed with materials)
          domains/materials/modules/settings_module.py

Proposed: data/settings/Settings.yaml (separate domain)
          domains/settings/data_loader.py
          domains/settings/modules/settings_module.py
```

**Verdict**: Architecturally sound improvement, but not urgent.
Current system works - separation is "nice to have" for long-term maintainability.

**Next Step**: Discuss with team and schedule for appropriate sprint.
