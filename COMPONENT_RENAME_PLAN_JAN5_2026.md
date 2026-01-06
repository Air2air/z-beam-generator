# Component Rename Plan: 'description' → 'pageDescription'
**Date**: January 5, 2026  
**Status**: ⚠️ PLANNING  
**Impact**: HIGH - Affects 50+ files, CLI commands, and all domains

---

## 🎯 Objective

**Rename 'description' component to 'pageDescription'** while deprecating the legacy pageDescription field that was stored in source YAML.

### Current State (Confusion)
- **'description' component**: AI-generated technical content (50-150 words) - ACTIVE
- **'pageDescription' field**: Historical subtitle text (150-200 chars) - PRESERVED from backup

### Target State (Clear)
- **'pageDescription' component**: AI-generated technical content (50-150 words) - NEW PRIMARY
- **Legacy 'pageDescription'**: Deprecated, will be removed from source YAML

---

## 📊 Impact Analysis

### Files to Update

#### 1. **Prompt Templates** (4 files) - RENAME
- `domains/materials/prompts/description.txt` → `pageDescription.txt`
- `domains/settings/prompts/description.txt` → `pageDescription.txt`
- `domains/contaminants/prompts/description.txt` → `pageDescription.txt`
- `domains/compounds/prompts/description.txt` → `pageDescription.txt`

#### 2. **Component Configuration** (5 files) - UPDATE
- `domains/materials/config.yaml` (component_lengths.description → pageDescription)
- `domains/settings/config.yaml`
- `domains/contaminants/config.yaml`
- `domains/compounds/config.yaml`
- `generation/config.yaml`

#### 3. **CLI Command Handler** (1 file) - ADD FLAG
- `run.py` (add --pageDescription flag, deprecate --description)

#### 4. **Field Router** (1 file) - UPDATE MAPPINGS
- `generation/field_router.py`
  ```python
  # OLD
  'description': 'text'
  
  # NEW
  'pageDescription': 'text'
  ```

#### 5. **Component Specs** (1 file) - UPDATE REGISTRY
- `shared/text/utils/component_specs.py`
  - Rename 'description' spec to 'pageDescription'
  - Update default lengths, icons, etc.

#### 6. **Generation Code** (3 files) - UPDATE REFERENCES
- `shared/commands/generation.py` (icon_map, component_label)
- `generation/core/batch_generator.py` (component_type = 'description')
- `generation/utils/frontmatter_sync.py` (field mapping logic)

#### 7. **Tests** (5+ files) - UPDATE COMPONENT NAMES
- `tests/test_frontmatter_partial_field_sync.py`
- `tests/test_structural_length_constraints.py`
- `tests/test_settings_filename_compliance.py`
- Any tests referencing 'description' component

#### 8. **Documentation** (15+ files) - UPDATE EXAMPLES
- `.github/copilot-instructions.md`
- `docs/08-development/AI_ASSISTANT_GUIDE.md`
- `docs/05-data/DATA_STORAGE_POLICY.md`
- All files with `--description` examples
- All files explaining 'description' component

#### 9. **Data Migration** (438 items) - REMOVE LEGACY FIELD
- `data/materials/Materials.yaml` (153 items)
- `data/settings/Settings.yaml` (153 items)
- `data/contaminants/Contaminants.yaml` (98 items)
- `data/compounds/Compounds.yaml` (34 items)
- **Action**: Remove `pageDescription` field from all source data

#### 10. **Export System** (2 files) - STOP PRESERVING
- `export/generation/universal_content_generator.py`
  - Remove lines 185-186 (pageDescription preservation logic)
  - Stop passing through legacy pageDescription

---

## 🔧 Implementation Steps

### Phase 1: Preparation (No Breaking Changes)
1. ✅ Create this implementation plan
2. ⏳ Review all affected files
3. ⏳ Create backup of prompt files
4. ⏳ Document current behavior for rollback

### Phase 2: Component Rename (Breaking Changes Begin)
5. ⏳ Rename prompt files (description.txt → pageDescription.txt)
6. ⏳ Update config.yaml files (component_lengths)
7. ⏳ Update component specs (ComponentRegistry)
8. ⏳ Update field router mappings
9. ⏳ Update CLI flag in run.py

### Phase 3: Code Updates
10. ⏳ Update generation command handlers
11. ⏳ Update batch generator
12. ⏳ Update frontmatter sync logic
13. ⏳ Update all test files

### Phase 4: Documentation Updates
14. ⏳ Update copilot-instructions.md
15. ⏳ Update AI_ASSISTANT_GUIDE.md
16. ⏳ Update all docs with --description examples
17. ⏳ Update architecture documentation

### Phase 5: Data Migration
18. ⏳ Create script to remove legacy pageDescription from source YAML
19. ⏳ Run migration on all 438 items
20. ⏳ Verify field removal complete

### Phase 6: Export System Update
21. ⏳ Remove pageDescription preservation logic from export
22. ⏳ Regenerate all domains to remove legacy field from frontmatter

### Phase 7: Verification
23. ⏳ Run test suite (all tests must pass)
24. ⏳ Test CLI command: `python3 run.py --pageDescription "Aluminum"`
25. ⏳ Verify generated content saves correctly
26. ⏳ Verify frontmatter export works
27. ⏳ Verify no legacy pageDescription in output

### Phase 8: Cleanup
28. ⏳ Remove deprecated --description flag warning
29. ⏳ Update CHANGELOG.md
30. ⏳ Create migration documentation
31. ⏳ Commit all changes with comprehensive message

---

## 🚨 Breaking Changes

### CLI Commands
```bash
# OLD (will be deprecated)
python3 run.py --material "Aluminum" --description

# NEW (preferred)
python3 run.py --material "Aluminum" --pageDescription
```

### Component Type Names
```python
# OLD
component_type = 'description'

# NEW
component_type = 'pageDescription'
```

### Prompt File Names
```
# OLD
domains/materials/prompts/description.txt

# NEW
domains/materials/prompts/pageDescription.txt
```

### Config Structure
```yaml
# OLD
component_lengths:
  description:
    default: 100
    min: 50
    max: 150

# NEW
component_lengths:
  pageDescription:
    default: 100
    min: 50
    max: 150
```

---

## 🔄 Migration Path for Users

### Backward Compatibility Strategy

**Option A: Immediate Deprecation (Recommended)**
- Remove --description flag entirely
- Force users to use --pageDescription
- Clear, no confusion

**Option B: Gradual Deprecation**
- Keep --description as alias for 6 months
- Show deprecation warning
- Remove in future version

**Recommendation**: Option A - Clean break, no confusion

---

## 📝 Data Migration Script

```python
#!/usr/bin/env python3
"""
Remove legacy pageDescription from source YAML files

This script removes the historical pageDescription field that was
restored from git backup. Going forward, pageDescription will be
an AI-generated component (renamed from 'description').
"""

import yaml
from pathlib import Path

def remove_legacy_page_description(domain_file):
    """Remove pageDescription field from all items"""
    with open(domain_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # Determine top-level key (materials, settings, contaminants, compounds)
    top_key = None
    for key in ['materials', 'settings', 'contaminants', 'compounds']:
        if key in data:
            top_key = key
            break
    
    if not top_key:
        print(f"❌ Unknown structure in {domain_file}")
        return 0
    
    removed_count = 0
    for item_name, item_data in data[top_key].items():
        if 'pageDescription' in item_data:
            del item_data['pageDescription']
            removed_count += 1
    
    # Save updated file
    with open(domain_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    return removed_count

# Run migration
domains = [
    'data/materials/Materials.yaml',
    'data/settings/Settings.yaml',
    'data/contaminants/Contaminants.yaml',
    'data/compounds/Compounds.yaml'
]

total_removed = 0
for domain_file in domains:
    count = remove_legacy_page_description(domain_file)
    print(f"✅ {domain_file}: Removed {count} pageDescription fields")
    total_removed += count

print(f"\n📊 Total removed: {total_removed} fields")
```

---

## ⚠️ Risks & Mitigations

### Risk 1: Breaking Existing Scripts
**Impact**: High - Any scripts using --description will break  
**Mitigation**: Search codebase for all --description usage, update all references

### Risk 2: Documentation Lag
**Impact**: Medium - Users may follow outdated documentation  
**Mitigation**: Update ALL documentation in same commit, use grep to find all references

### Risk 3: Test Failures
**Impact**: High - Many tests reference 'description' component  
**Mitigation**: Update all tests before merging, run full test suite

### Risk 4: Data Loss
**Impact**: Critical - Accidentally removing wrong pageDescription  
**Mitigation**: Git backup, verify migration script thoroughly, test on single file first

### Risk 5: Incomplete Migration
**Impact**: High - Some references missed, system partially broken  
**Mitigation**: Use comprehensive grep searches, checklist verification, peer review

---

## ✅ Pre-Implementation Checklist

Before starting implementation:
- [ ] Review all grep search results for 'description' references
- [ ] Backup current prompt files
- [ ] Backup current data files
- [ ] Review test suite for description-related tests
- [ ] Get user approval for breaking changes
- [ ] Confirm backward compatibility strategy (Option A vs B)
- [ ] Plan rollback procedure if needed

---

## 📋 Verification Checklist

After implementation:
- [ ] All prompt files renamed
- [ ] All config files updated
- [ ] CLI flag works: `--pageDescription "Material"`
- [ ] Component registry updated
- [ ] Field router updated
- [ ] All tests passing
- [ ] Documentation updated (15+ files)
- [ ] Legacy pageDescription removed from source YAML (438 items)
- [ ] Export system no longer preserves legacy field
- [ ] Frontmatter files regenerated without legacy field
- [ ] No grep matches for old component name in active code

---

## 🎯 Success Criteria

- ✅ CLI command `--pageDescription` works for all domains
- ✅ Generated content saves to correct field
- ✅ No legacy pageDescription in source YAML files
- ✅ No legacy pageDescription in exported frontmatter
- ✅ All tests passing (0 failures)
- ✅ All documentation updated
- ✅ Clear, unambiguous component naming

---

## 📚 Related Documentation

- `docs/05-data/SOURCE_DATA_SCHEMA.md` - Update pageDescription definition
- `docs/BACKEND_FRONTMATTER_REQUIREMENTS_JAN4_2026.md` - Update field descriptions
- `.github/COPILOT_GENERATION_GUIDE.md` - Update command examples
- `docs/08-development/COMPONENT_DISCOVERY.md` - Update component type examples

---

**Next Steps**: Review this plan with user, get approval for backward compatibility strategy, then proceed with implementation in phases.
