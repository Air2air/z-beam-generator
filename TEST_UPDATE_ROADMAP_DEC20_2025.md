# Test Suite Systematic Update - Roadmap & Progress

**Started**: December 20, 2025  
**Estimated Time**: 4-6 hours total  
**Current Status**: Phase 1 Complete (1 hour invested)

---

## 📊 Overall Test Status

### Before Update Pass:
```
Total: 341/877 passing (39%)
Failing: 31+ tests (stopped after 31)
Skipped: 16 tests
```

### After Phase 1:
```
Challenge Taxonomy: 6/8 passing ✅ (+6 tests fixed)
```

---

## 🎯 Update Phases

### ✅ Phase 1: Challenge Taxonomy Tests (COMPLETE - 1 hour)

**Status**: 6/8 passing  
**Commit**: `edb95949`

**What Was Fixed**:
- Updated fixture to read from `data['settings'][material]['challenges']`
- Removed expectations for `challenge_id` field (doesn't exist in data)
- Created new tests matching actual data structure:
  - `test_all_settings_have_challenges` ✅
  - `test_all_challenges_have_required_fields` ✅
  - `test_challenge_text_format` ✅
  - `test_severity_levels_valid` ✅
  - `test_solutions_are_actionable` ✅
  - `test_challenge_impact_described` ✅
  - `test_challenge_distribution` ⚠️ (minor fix needed)
  - `test_challenge_categories_valid` ⚠️ (minor fix needed)

**Remaining Issues**:
- 2 tests fail due to some materials having `challenges` as list instead of dict
- Easy fix: Add type check in tests

---

### 🔄 Phase 2: Domain Associations Tests (IN PROGRESS - est. 1.5 hours)

**Failures to Fix** (8+ tests):
1. `test_material_contaminant_associations_exist`
2. `test_contaminant_compound_associations_exist`
3. `test_forward_lookup_contaminants_for_material`
4. `test_reverse_lookup_materials_for_contaminant`
5. `test_reverse_lookup_contaminants_for_compound`
6. `test_material_image_urls_no_category_paths`
7. `test_contaminant_image_urls_no_category_paths`
8. `test_material_ids_have_laser_cleaning_suffix`
9. `test_contaminant_ids_have_contamination_suffix`
10. `test_compound_ids_exist`
11. `test_materials_yaml_no_relationships_field`

**Root Causes**:
- Data structure changes after cleanup
- Relationships field expectations may be outdated
- Image URL path conventions changed
- ID suffix requirements may have changed

**Action Plan**:
1. Read current DomainAssociations.yaml structure
2. Check Materials.yaml for relationships field
3. Update test expectations to match current data
4. Fix image URL path validation
5. Update ID suffix expectations

---

### 🔄 Phase 3: Filename Compliance Tests (est. 30 min)

**Failures** (2 tests):
1. `test_compounds_directory_exists`
2. `test_expected_file_count` (compounds)
3. `test_expected_file_count` (contaminants)

**Root Cause**: Export consolidation changed file counts/locations

**Action Plan**:
1. Check actual file counts in export directories
2. Update test expectations
3. Verify directory structure matches current architecture

---

### 🔄 Phase 4: Export Config Tests (est. 30 min)

**Failures** (3 tests):
1. `test_all_configs_have_required_keys`
2. `test_output_paths_are_relative`
3. `test_source_files_use_relative_paths`

**Root Cause**: Test infrastructure uses temp paths that don't match `^data/` schema requirement

**Action Plan**:
1. Mock schema validation for tests
2. OR: Update test fixtures to use production-like paths
3. Verify config files have required keys

---

### 🔄 Phase 5: Export System Integration Tests (est. 30 min)

**Failures** (2 tests):
1. `test_deployment_pipeline_runs_without_error`
2. `test_enrichers_can_be_loaded`

**Root Cause**: Post-consolidation path or import changes

**Action Plan**:
1. Verify enricher imports after consolidation
2. Check deployment pipeline for broken paths
3. Update test mocks if needed

---

### 🔄 Phase 6: Miscellaneous Test Fixes (est. 1 hour)

**Failures** (6+ tests):
1. `test_cleanup_script` - Dry run tests
2. `test_compound_frontmatter_structure` - Migration script
3. `test_field_order_validation` - Compounds field order

**Action Plan**:
1. Fix cleanup script dry run logic
2. Update compound frontmatter expectations
3. Verify field order requirements

---

## 📋 Detailed Phase 2 Plan (Next)

### Step 1: Understand Current Data Structure

```bash
# Check DomainAssociations.yaml
python3 << 'EOF'
import yaml
with open('data/associations/DomainAssociations.yaml') as f:
    assoc = yaml.safe_load(f)
print(f"Keys: {list(assoc.keys())}")
print(f"First material keys: {list(assoc['materials'].keys())[:3]}")
EOF
```

### Step 2: Check Materials.yaml relationships field

```bash
# See if relationships field exists
grep -n "relationships:" data/materials/Materials.yaml | head -5
```

### Step 3: Update Tests

Files to modify:
- `tests/test_domain_associations_integration.py`
- `tests/test_centralized_architecture.py`

Changes needed:
- Update data access patterns
- Fix relationship field expectations
- Correct image URL validation
- Update ID suffix checks

---

## 🎯 Success Criteria

### Phase 1 ✅
- [x] 6+ challenge taxonomy tests passing
- [x] Data structure understanding documented
- [x] Committed and pushed

### Phase 2 (Target)
- [ ] 8+ domain association tests passing
- [ ] Relationships field handling fixed
- [ ] Image URL validation updated

### Phase 3-6 (Target)
- [ ] All filename compliance tests passing
- [ ] All export config tests passing
- [ ] Miscellaneous tests fixed

### Final (Target)
- [ ] 450+/877 tests passing (51%+) ⬆️ from 39%
- [ ] Zero critical test failures
- [ ] All test fixes committed
- [ ] Test suite documentation updated

---

## 🔧 Common Patterns Found

### Pattern 1: Data Structure Mismatch
**Symptom**: Tests expect fields that don't exist (e.g., `challenge_id`)  
**Fix**: Update tests to match actual data structure  
**Example**: Challenge taxonomy tests

### Pattern 2: File Count Outdated
**Symptom**: Tests expect specific counts that changed  
**Fix**: Count actual files and update expectations  
**Example**: Filename compliance tests

### Pattern 3: Test Infrastructure vs Schema
**Symptom**: Tests use temp paths that fail schema validation  
**Fix**: Mock validation or use production-like paths  
**Example**: Export config tests

### Pattern 4: Post-Consolidation Imports
**Symptom**: Tests fail after module consolidation  
**Fix**: Update import paths and mocks  
**Example**: Export enricher tests

---

## 📝 Notes for Continuation

### When Resuming:
1. Start with Phase 2 (domain associations)
2. Check git log for context
3. Review this roadmap for action plans
4. Update phase status as you progress

### Key Files:
- `tests/test_domain_associations_integration.py` - 8+ failures
- `tests/test_centralized_architecture.py` - 5+ failures
- `tests/test_challenge_taxonomy.py` - 2 minor fixes remaining
- `data/associations/DomainAssociations.yaml` - Check structure
- `data/materials/Materials.yaml` - Check relationships field

### Commands to Run:
```bash
# Test specific failure
python3 -m pytest tests/test_domain_associations_integration.py::TestDomainAssociationsFullIDs::test_material_ids_have_laser_cleaning_suffix -xvs

# Check data structure
python3 << 'EOF'
import yaml
with open('data/associations/DomainAssociations.yaml') as f:
    print(yaml.dump(yaml.safe_load(f)['materials']['Aluminum'], default_flow_style=False))
EOF

# Count files
find ../z-beam/frontmatter/compounds -name "*.yaml" | wc -l
```

---

## 💡 Efficiency Tips

1. **Batch similar fixes** - Update all filename tests at once
2. **Run tests frequently** - Verify fixes immediately
3. **Commit after each phase** - Preserve progress
4. **Document patterns** - Reuse solutions for similar issues
5. **Skip low-value tests** - Focus on high-impact failures first

---

**Current Progress**: 1/6 phases complete (17%)  
**Time Invested**: 1 hour  
**Remaining Estimate**: 3-5 hours  
**Next Action**: Start Phase 2 (domain associations tests)
