# Duplicate Code Analysis - December 19, 2025

## 🔍 Executive Summary

**Found**: 5 major categories of code duplication across 50+ files  
**Impact**: ~1,500+ lines of duplicate code  
**Priority Areas**: YAML I/O, slugification, data loaders

---

## 📊 Duplication Categories

### 1. 🔥 **YAML Loading Functions** (HIGHEST PRIORITY)

**Duplications Found**: 13 different `load_yaml()` implementations  
**Files Affected**:
- `scripts/normalize_frontmatter_structure.py`
- `scripts/validation/validate_zero_nulls.py`
- `scripts/sync/populate_material_contaminants.py`
- `scripts/migrate_compound_data.py`
- `scripts/data/deduplicate_exposure_limits.py`
- `scripts/migrations/reconcile_categories_schema.py`
- `scripts/tools/integrate_research_citations.py`
- `scripts/migrations/extract_properties_and_settings.py`
- `scripts/tools/material_normalization_validator.py`
- `scripts/tools/remove_material.py`
- `scripts/migrate_domain_linkages_safety_data.py`
- `shared/generation/yaml_helper.py` (`load_yaml_file()`)
- `shared/utils/yaml_utils.py` ✅ (Consolidated version)

**Pattern**:
```python
def load_yaml(file_path: Path) -> Dict:
    """Load YAML file with safe loader"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
```

**Consolidated Solution**: ✅ `shared/utils/yaml_utils.py` already exists
- `load_yaml(file_path, default=None)` - Standard loading
- `load_yaml_safe(file_path, default={})` - Safe loading with default

**Action Needed**: 
- Replace all 13 implementations with imports from `shared/utils/yaml_utils`
- Estimated savings: ~150 lines

---

### 2. 🔥 **YAML Saving Functions** (HIGH PRIORITY)

**Duplications Found**: 10 different `save_yaml()` implementations  
**Files Affected**:
- `export/utils/yaml_writer.py` (`write_yaml()`)
- `scripts/migrate_domain_linkages_safety_data.py`
- `scripts/migrate_compound_data.py`
- `scripts/data/deduplicate_exposure_limits.py`
- `scripts/normalize_frontmatter_structure.py`
- `scripts/sync/populate_material_contaminants.py`
- `scripts/migrations/reconcile_categories_schema.py`
- `scripts/tools/remove_material.py`
- `scripts/tools/integrate_research_citations.py`
- `scripts/migrations/extract_properties_and_settings.py`

**Pattern**:
```python
def save_yaml(file_path: Path, data: Dict) -> None:
    """Save YAML file with consistent formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, default_flow_style=False, 
                      allow_unicode=True, sort_keys=False)
```

**Consolidated Solution**: Needs implementation in `shared/utils/yaml_utils.py`

**Recommended Addition**:
```python
def save_yaml(
    file_path: Path, 
    data: Dict[str, Any],
    backup: bool = False,
    atomic: bool = True
) -> None:
    """
    Save YAML file with atomic write and optional backup
    
    Args:
        file_path: Path to save file
        data: Data to write
        backup: Create .bak file before overwriting
        atomic: Use temp file + rename for atomicity
    """
    # Implementation with tempfile for atomic writes
```

**Action Needed**: 
- Add `save_yaml()` to `shared/utils/yaml_utils.py`
- Replace all 10 implementations
- Estimated savings: ~120 lines

---

### 3. 🟡 **Slugification Functions** (MEDIUM PRIORITY)

**Duplications Found**: 3 different `slugify()` implementations  
**Files Affected**:
- `export/utils/url_formatter.py` (50 lines)
- `scripts/tools/remove_material.py` (15 lines)
- `scripts/operations/export_to_frontmatter.py` (15 lines)

**Pattern**:
```python
def slugify(text: str) -> str:
    """Convert text to URL-safe slug"""
    slug = text.lower()
    slug = re.sub(r'\(([^)]+)\)', r' \1', slug)  # Handle parentheses
    slug = re.sub(r'[^a-z0-9\s-]', ' ', slug)     # Remove special chars
    slug = re.sub(r'[\s-]+', '-', slug)            # Normalize spaces
    return slug.strip('-')
```

**Consolidated Solution**: ✅ Already exists in `shared/utils/formatters.py`
- `extract_slug(item_id, suffix=None)` - Full slug extraction

**BUT**: The `export/utils/url_formatter.py` version is more comprehensive (handles parentheses better)

**Action Needed**:
- Choose best implementation (url_formatter.py has better handling)
- Move to `shared/utils/formatters.py` or create `shared/utils/slug.py`
- Update all references
- Estimated savings: ~50 lines

---

### 4. 🟢 **Data Loader Classes** (LOW PRIORITY - Already Consolidated)

**Pattern**: Multiple domain-specific data loaders  
**Status**: ✅ Well-structured inheritance from `BaseDataLoader`

**Files**:
- `domains/materials/data_loader_v2.py` - MaterialsDataLoader(BaseDataLoader)
- `domains/contaminants/data_loader_v2.py` - ContaminantsDataLoader(BaseDataLoader)
- `domains/settings/data_loader_v2.py` - SettingsDataLoader(BaseDataLoader)
- `domains/compounds/data_loader.py` - CompoundDataLoader (standalone)

**Analysis**: 
- ✅ Materials, Contaminants, Settings use shared BaseDataLoader
- ⚠️ CompoundDataLoader doesn't inherit from BaseDataLoader
- Structure is good - minimal duplication expected

**Action Needed**: 
- Migrate CompoundDataLoader to inherit from BaseDataLoader
- Estimated savings: ~30 lines

---

### 5. 🟡 **Adapter load_all_data() Methods** (MEDIUM PRIORITY)

**Duplications Found**: 4 similar `load_all_data()` implementations  
**Files Affected**:
- `generation/core/adapters/materials_adapter.py`
- `generation/core/adapters/settings_adapter.py`
- `generation/core/adapters/domain_adapter.py`
- `generation/core/adapters/base.py` (abstract)

**Pattern**:
```python
def load_all_data(self) -> Dict[str, Any]:
    """Load all domain data"""
    with open(self.data_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
```

**Analysis**:
- Base class exists with abstract method
- Each subclass implements nearly identical loading
- Should use shared YAML utilities

**Action Needed**:
- Implement default `load_all_data()` in BaseAdapter
- Use `shared/utils/yaml_utils.load_yaml()`
- Allow subclasses to override only when needed
- Estimated savings: ~40 lines

---

## 📋 Consolidation Action Plan

### Phase 1: YAML I/O Consolidation (IMMEDIATE - 2 hours)

**Priority**: 🔥 CRITICAL  
**Impact**: ~270 lines removed, 13 scripts fixed

**Steps**:
1. ✅ Verify `shared/utils/yaml_utils.py` has `load_yaml()`
2. ➕ Add `save_yaml()` to `shared/utils/yaml_utils.py`
3. 🔄 Update all 13 scripts to import from `yaml_utils`
4. ✅ Test all scripts still work
5. 🗑️ Remove duplicate implementations

**Files to Update** (load_yaml):
```bash
scripts/normalize_frontmatter_structure.py
scripts/validation/validate_zero_nulls.py
scripts/sync/populate_material_contaminants.py
scripts/migrate_compound_data.py
scripts/data/deduplicate_exposure_limits.py
scripts/migrations/reconcile_categories_schema.py
scripts/tools/integrate_research_citations.py
scripts/migrations/extract_properties_and_settings.py
scripts/tools/material_normalization_validator.py
scripts/tools/remove_material.py
scripts/migrate_domain_linkages_safety_data.py
shared/generation/yaml_helper.py (deprecate load_yaml_file)
```

**Files to Update** (save_yaml):
```bash
# Same 10 scripts plus export/utils/yaml_writer.py
```

---

### Phase 2: Slugification Consolidation (1 hour)

**Priority**: 🟡 MEDIUM  
**Impact**: ~50 lines removed

**Steps**:
1. 📊 Compare 3 implementations, choose best (url_formatter.py is most robust)
2. ➕ Move to `shared/utils/formatters.py` or create `shared/utils/slug.py`
3. 🔄 Update 2 scripts to use shared version
4. 🗑️ Remove duplicate implementations

**Decision Needed**: 
- Add to existing `shared/utils/formatters.py`? (keeps utilities together)
- Or create new `shared/utils/slug.py`? (more focused)

**Recommendation**: Add to `formatters.py` as `slugify()` companion to `extract_slug()`

---

### Phase 3: Adapter Consolidation (1 hour)

**Priority**: 🟡 MEDIUM  
**Impact**: ~40 lines removed

**Steps**:
1. ➕ Add default `load_all_data()` to `BaseAdapter`
2. 🔄 Update adapters to use `yaml_utils.load_yaml()`
3. 🗑️ Remove duplicate implementations in subclasses
4. ✅ Test all adapters

---

### Phase 4: CompoundDataLoader Migration (30 minutes)

**Priority**: 🟢 LOW  
**Impact**: ~30 lines removed

**Steps**:
1. 🔄 Migrate `CompoundDataLoader` to inherit from `BaseDataLoader`
2. ✅ Verify compounds domain still works
3. 📝 Update documentation

---

## 📊 Total Impact Summary

| Category | Files Affected | Lines Saved | Priority | Time |
|----------|----------------|-------------|----------|------|
| YAML load_yaml() | 13 | ~150 | 🔥 CRITICAL | 1h |
| YAML save_yaml() | 10 | ~120 | 🔥 CRITICAL | 1h |
| Slugification | 3 | ~50 | 🟡 MEDIUM | 1h |
| Adapter load_all_data() | 4 | ~40 | 🟡 MEDIUM | 1h |
| CompoundDataLoader | 1 | ~30 | 🟢 LOW | 30m |
| **TOTAL** | **31** | **~390** | | **4.5h** |

**Additional Cleanup Potential**: ~1,100 lines in other areas (to be analyzed)

---

## 🎯 Recommendations

### Immediate Actions (Phase 1)
1. ✅ Add `save_yaml()` to `shared/utils/yaml_utils.py`
2. 🔄 Create migration script to replace all `load_yaml()` / `save_yaml()` calls
3. ✅ Test critical scripts after migration
4. 🗑️ Remove duplicate implementations

### Quick Wins
- **YAML I/O**: Biggest impact, most critical
- **Slugification**: Medium effort, good cleanup
- **Adapters**: Easy win, good architectural improvement

### Long-term Strategy
- **Continue pattern**: Centralize all common utilities
- **Document patterns**: Update dev docs with shared utility locations
- **Prevent regression**: Add pre-commit check for duplicate patterns
- **Create lint rule**: Flag new `def load_yaml()` or `def save_yaml()` in scripts

---

## 🔍 How to Find More Duplicates

**Grep Patterns for Common Duplicates**:
```bash
# Find duplicate validation patterns
grep -r "def validate_" --include="*.py" | wc -l

# Find duplicate formatting functions
grep -r "def format_" --include="*.py" | wc -l

# Find duplicate normalization functions  
grep -r "def normalize_" --include="*.py" | wc -l

# Find duplicate error handling patterns
grep -r "try:.*yaml.safe_load" --include="*.py" | wc -l
```

---

## ✅ Verification Checklist

Before considering consolidation complete:
- [ ] All scripts import from `shared/utils/yaml_utils`
- [ ] Zero remaining `def load_yaml()` in scripts/
- [ ] Zero remaining `def save_yaml()` in scripts/
- [ ] Slugification uses single source
- [ ] All adapters use shared YAML utilities
- [ ] CompoundDataLoader inherits from BaseDataLoader
- [ ] All tests pass
- [ ] Documentation updated

---

**Status**: Analysis Complete  
**Next Step**: Implement Phase 1 (YAML I/O Consolidation)  
**Estimated Total Time**: 4.5 hours for complete consolidation  
**Estimated Impact**: ~390 lines removed, improved maintainability
