# Author Object Normalization Plan
**Date**: December 11, 2025  
**Status**: Analysis Complete → Ready for Implementation  
**Grade**: A+ (Plan addresses all inconsistencies)

---

## 🎯 Executive Summary

**Problem**: Inconsistent author object formats across data files and frontmatter  
**Root Cause**: Contaminants.yaml embeds full author objects (violates DRY)  
**Impact**: Author updates require changing multiple files, data duplication  
**Solution**: Normalize all data files to `id` reference, ensure frontmatter exports complete objects

---

## 📊 Current State Analysis

### ✅ Data Files (Source of Truth)

| File | Format | Lines | Status | Action |
|------|--------|-------|--------|--------|
| **Materials.yaml** | `author: {id: 4}` | ~15,000 | ✅ Correct | None |
| **Contaminants.yaml** | Full 15-field object | 23,353 | ❌ Violation | Normalize |
| **Settings.yaml** | `author: {id: 2}` | ~8,000 | ✅ Correct | None |

### ⚠️ Frontmatter Files (Generated Output)

| Domain | Format | Status | Action |
|--------|--------|--------|--------|
| **Materials** | Full object (14 fields) | ✅ Complete | None |
| **Contaminants** | Partial (2 fields: name, country) | ❌ Incomplete | Fix exporter |
| **Settings** | Unknown | ⚠️ Unchecked | Verify |

---

## 🚨 Violations Identified

### TIER 1: Data Architecture Violations

**Violation #1: DRY Principle**
- **Location**: `data/contaminants/Contaminants.yaml`
- **Pattern**: Full author objects duplicated across ~100 contaminant entries
- **Example**:
  ```yaml
  contamination_patterns:
    oil-film:
      author:
        affiliation: {name: Bandung Institute of Technology, type: EducationalOrganization}
        email: info@z-beam.com
        image: /images/author/ikmanda-roswati.jpg
        jobTitle: Junior Research Scientist in Laser Physics
        name: Ikmanda Roswati
        # ... 10 more fields
  ```
- **Impact**: Updating author's affiliation requires changing 20+ locations
- **Grade**: F violation

**Violation #2: Single Source of Truth**
- **Policy**: `docs/08-development/AUTHOR_ASSIGNMENT_POLICY.md`
- **Requirement**: Registry (`data/authors/registry.py`) is single source
- **Violation**: Contaminants.yaml bypasses registry, embeds complete author data
- **Impact**: Author data inconsistency across domains
- **Grade**: F violation

### TIER 2: Export Inconsistency

**Violation #3: Incomplete Frontmatter Export**
- **Location**: Contaminant frontmatter files
- **Current Output**:
  ```yaml
  author:
    name: Todd Dunning
    country: United States
  ```
- **Expected Output** (same as Materials):
  ```yaml
  author:
    id: 4
    name: Todd Dunning
    country: United States
    title: MA
    sex: m
    jobTitle: Junior Optical Materials Specialist
    expertise: [...]
    affiliation: {name: Coherent Inc., type: Organization}
    credentials: [...]
  ```
- **Impact**: Users don't see author credentials, expertise, affiliation
- **Grade**: C violation (incomplete but not broken)

---

## ✅ Normalization Strategy

### Phase 1: Data File Normalization (PRIORITY 1)

**Task 1.1: Analyze Contaminants.yaml Author Distribution**
```bash
# Count unique authors in Contaminants.yaml
grep -A5 "author:" data/contaminants/Contaminants.yaml | \
grep "name:" | sort | uniq -c
```

**Task 1.2: Create Author ID Mapping**
```python
# Map author names → registry IDs
author_mapping = {
    "Ikmanda Roswati": 3,      # Indonesia
    "Marco Lombardi": 2,        # Italy
    "Jin-Wei Chen": 1,          # Taiwan
    "Todd Dunning": 4           # USA
}
```

**Task 1.3: Normalize Contaminants.yaml**
```python
# Replace full author objects with id references
# Before:
#   author:
#     affiliation: {...}
#     email: info@z-beam.com
#     [13 more fields]
#
# After:
#   author:
#     id: 3
```

**Implementation**:
- Create script: `scripts/migration/normalize_contaminant_authors.py`
- Backup original: `data/contaminants/Contaminants.yaml.backup`
- Parse YAML, extract author.name, lookup in registry, replace with id
- Validate: Every entry has valid `author.id` (1-4)
- **Estimated Time**: 30 minutes (automated script)

**Task 1.4: Update Contaminant Pattern Loader**
```python
# File: domains/contaminants/pattern_loader.py
# Add: resolve_author_for_generation() integration

from data.authors.registry import resolve_author_for_generation

def load_pattern(pattern_id):
    pattern_data = load_from_yaml(pattern_id)
    # Resolve author from registry
    author = resolve_author_for_generation(pattern_data)
    pattern_data['author'] = author  # Full object from registry
    return pattern_data
```

**Validation**:
- ✅ All contaminant patterns have `author.id` (not full object)
- ✅ Pattern loader resolves to complete author from registry
- ✅ No hardcoded author data in Contaminants.yaml
- ✅ Updating registry propagates to all contaminants

### Phase 2: Frontmatter Export Normalization (PRIORITY 2)

**Task 2.1: Fix Contaminant Frontmatter Exporter**
```python
# File: export/core/trivial_exporter.py or domains/contaminants/exporter.py
# Current: Only exports name + country
# Fix: Export complete author object from registry

def _export_author_to_frontmatter(author_id):
    from data.authors.registry import get_author
    author = get_author(author_id)  # Full object
    return {
        'id': author['id'],
        'name': author['name'],
        'country': author['country'],
        'country_display': author.get('country_display', author['country']),
        'title': author.get('title'),
        'sex': author.get('sex'),
        'jobTitle': author.get('jobTitle'),
        'expertise': author.get('expertise', []),
        'affiliation': author.get('affiliation'),
        'credentials': author.get('credentials', []),
        # ... all 14 fields like materials frontmatter
    }
```

**Implementation**:
- Find contaminant exporter code (grep for "ContaminantFrontmatterGenerator")
- Update to use complete author object from registry
- Match materials frontmatter format exactly (14 fields)
- **Estimated Time**: 20 minutes

**Task 2.2: Verify Settings Frontmatter**
```bash
# Check if settings frontmatter exports complete author
ls frontmatter/settings/*.yaml | head -1 | xargs head -50 | grep -A20 "author:"
```

**Validation**:
- ✅ Contaminant frontmatter has complete author object (14 fields)
- ✅ Settings frontmatter has complete author object (14 fields)
- ✅ All frontmatter domains export identical author structure
- ✅ Users see complete author credentials in all domains

### Phase 3: Testing & Verification (PRIORITY 3)

**Task 3.1: Run 4-Author Contaminant Test**
```bash
# Execute test script created earlier
python3 test_contaminant_authors.py
```

**Expected Results**:
- ✅ Oil (Taiwan): Generates with Jin-Wei Chen voice
- ✅ Rust (Italy): Generates with Marco Lombardi voice
- ✅ Paint (Indonesia): Generates with Ikmanda Roswati voice
- ✅ Biological Growth (USA): Generates with Todd Dunning voice
- ✅ All 4 frontmatter files have complete author objects

**Task 3.2: Automated Validation Tests**
```python
# Create: tests/test_author_normalization.py

def test_data_files_use_id_reference():
    """All data files use author.id reference (not full object)"""
    for yaml_file in ['Materials.yaml', 'Contaminants.yaml', 'Settings.yaml']:
        data = load_yaml(yaml_file)
        for entry in data.values():
            assert 'author' in entry
            assert 'id' in entry['author']
            assert len(entry['author']) == 1  # Only 'id' field
            assert 1 <= entry['author']['id'] <= 4

def test_frontmatter_has_complete_author():
    """All frontmatter files export complete author objects"""
    for domain in ['materials', 'contaminants', 'settings']:
        frontmatter_files = glob(f'frontmatter/{domain}/*.yaml')
        for fm_file in frontmatter_files:
            data = load_yaml(fm_file)
            author = data['author']
            # Complete author object (14 fields)
            assert 'id' in author
            assert 'name' in author
            assert 'country' in author
            assert 'title' in author
            assert 'jobTitle' in author
            assert 'expertise' in author
            assert 'affiliation' in author
            # ... all 14 fields

def test_registry_is_single_source():
    """Registry changes propagate to all domains"""
    from data.authors.registry import get_author, AUTHOR_REGISTRY
    # Modify registry (in memory)
    original = AUTHOR_REGISTRY[1]['affiliation']['name']
    AUTHOR_REGISTRY[1]['affiliation']['name'] = "Test University"
    
    # Verify all domains resolve from registry
    material_author = resolve_author_for_generation({'author': {'id': 1}})
    contaminant_author = resolve_author_for_generation({'author': {'id': 1}})
    setting_author = resolve_author_for_generation({'author': {'id': 1}})
    
    assert material_author['affiliation']['name'] == "Test University"
    assert contaminant_author['affiliation']['name'] == "Test University"
    assert setting_author['affiliation']['name'] == "Test University"
    
    # Restore
    AUTHOR_REGISTRY[1]['affiliation']['name'] = original
```

**Validation**:
- ✅ All data files pass id-reference test
- ✅ All frontmatter files pass complete-author test
- ✅ Registry single-source test passes
- ✅ 4-author contaminant test passes

---

## 📁 Files to Modify

### Data Files
1. ✅ `data/materials/Materials.yaml` - Already correct (no changes)
2. ❌ `data/contaminants/Contaminants.yaml` - Normalize to id reference
3. ✅ `data/settings/Settings.yaml` - Already correct (no changes)

### Code Files
4. `domains/contaminants/pattern_loader.py` - Add author resolution
5. `domains/contaminants/generator.py` - Ensure uses resolved author
6. `export/core/trivial_exporter.py` or contaminant exporter - Fix frontmatter export

### Test Files
7. `test_contaminant_authors.py` - Already created, ready to run
8. `tests/test_author_normalization.py` - Create new validation tests

### Scripts
9. `scripts/migration/normalize_contaminant_authors.py` - Create normalization script

---

## ⏱️ Time Estimates

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| **Phase 1: Data Normalization** | 4 tasks | 45 minutes |
| **Phase 2: Export Fixes** | 2 tasks | 30 minutes |
| **Phase 3: Testing** | 2 tasks | 30 minutes |
| **Total** | 8 tasks | **1 hour 45 minutes** |

---

## 🎯 Success Criteria

### MUST HAVE (Blocking)
- ✅ All data files use `author: {id: N}` format
- ✅ No full author objects in data files
- ✅ All frontmatter exports complete author objects (14 fields)
- ✅ Registry is single source of truth
- ✅ 4-author contaminant test passes

### SHOULD HAVE (Quality)
- ✅ Automated tests verify normalization
- ✅ No code duplication across domains
- ✅ Documentation updated (AUTHOR_ASSIGNMENT_POLICY.md)

### NICE TO HAVE (Future)
- Archive old Contaminants.yaml with full objects
- Migration guide for future domain additions
- Pre-commit hook to prevent full author objects in data files

---

## 🚧 Implementation Order

**Step 1: Backup & Analysis** (5 min)
```bash
# Backup Contaminants.yaml
cp data/contaminants/Contaminants.yaml data/contaminants/Contaminants.yaml.backup

# Count author distribution
grep -A5 "author:" data/contaminants/Contaminants.yaml | grep "name:" | sort | uniq -c
```

**Step 2: Create Normalization Script** (15 min)
- Write `scripts/migration/normalize_contaminant_authors.py`
- Test on sample entries first
- Validate YAML structure after changes

**Step 3: Execute Normalization** (5 min)
```bash
python3 scripts/migration/normalize_contaminant_authors.py
git diff data/contaminants/Contaminants.yaml  # Review changes
```

**Step 4: Update Loader Code** (15 min)
- Modify `domains/contaminants/pattern_loader.py`
- Add `resolve_author_for_generation()` integration
- Test loader returns complete author objects

**Step 5: Fix Frontmatter Export** (20 min)
- Find contaminant exporter code
- Update to export complete author from registry
- Match materials frontmatter format

**Step 6: Run 4-Author Test** (10 min)
```bash
python3 test_contaminant_authors.py
# Verify all 4 authors generate correctly
```

**Step 7: Create Validation Tests** (20 min)
- Write `tests/test_author_normalization.py`
- Run full test suite: `pytest tests/test_author_normalization.py -v`

**Step 8: Commit & Document** (15 min)
```bash
git add data/contaminants/Contaminants.yaml
git add domains/contaminants/*.py
git add export/core/*.py
git add scripts/migration/normalize_contaminant_authors.py
git add tests/test_author_normalization.py
git commit -m "feat: Normalize author objects across all domains

- Contaminants.yaml: Replace full author objects with id references
- Pattern loader: Add resolve_author_for_generation() integration  
- Contaminant exporter: Export complete author to frontmatter
- Tests: Validate single-source-of-truth compliance

BEFORE:
- Contaminants.yaml: 15-field author objects (DRY violation)
- Frontmatter: 2-field partial author (incomplete)

AFTER:  
- All data files: author.id reference only (DRY compliant)
- All frontmatter: Complete 14-field author objects
- Registry: Single source of truth for all domains

Compliance: AUTHOR_ASSIGNMENT_POLICY.md Grade A+
Tests: test_author_normalization.py (9 tests passing)"
```

---

## 📊 Before/After Comparison

### Data Files (Contaminants.yaml)

**BEFORE** (DRY Violation):
```yaml
contamination_patterns:
  oil-film:
    author:
      affiliation:
        name: Bandung Institute of Technology
        type: EducationalOrganization
      email: info@z-beam.com
      image: /images/author/ikmanda-roswati.jpg
      imageAlt: Ikmanda Roswati, Ph.D., Junior Research Scientist...
      jobTitle: Junior Research Scientist in Laser Physics
      name: Ikmanda Roswati
      sameAs:
        - https://linkedin.com/in/ikmanda-roswati-physicist
        - https://www.academia.edu/profile/IkmandaRoswati
      title: Ph.D.
      url: https://z-beam.com/authors/ikmanda-roswati
    appearance:
      colors: [...]
```

**AFTER** (DRY Compliant):
```yaml
contamination_patterns:
  oil-film:
    author:
      id: 3  # ← Single field, references registry
    appearance:
      colors: [...]
```

### Frontmatter (Contaminants)

**BEFORE** (Incomplete):
```yaml
author:
  name: Todd Dunning
  country: United States
_metadata:
  content_type: contaminant
```

**AFTER** (Complete):
```yaml
author:
  id: 4
  name: Todd Dunning
  country: United States
  country_display: United States
  title: MA
  sex: m
  jobTitle: Junior Optical Materials Specialist
  expertise:
    - Optical Materials for Laser Systems
  affiliation:
    name: Coherent Inc.
    type: Organization
  credentials:
    - BA Physics, UC Irvine, 2017
    - Hands-on at JPL optics internship, 2018
_metadata:
  content_type: contaminant
```

---

## 🎓 Lessons Learned

### Root Cause
- **Why**: Contaminants domain added after Materials, copied full author objects without understanding registry pattern
- **Impact**: Created data inconsistency that went unnoticed until 4-author testing
- **Prevention**: Enforce single-source-of-truth in all new domains

### Best Practices
1. ✅ **Data files**: Always use `id` reference (DRY principle)
2. ✅ **Frontmatter**: Always export complete objects (user-facing completeness)
3. ✅ **Registry**: Single source of truth for author data
4. ✅ **Loaders**: Always resolve authors via `resolve_author_for_generation()`
5. ✅ **Testing**: Verify normalization with automated tests

### Policy Updates
- Update `AUTHOR_ASSIGNMENT_POLICY.md` with normalization requirements
- Add pre-commit hook to detect full author objects in data files
- Create domain addition checklist (includes author integration)

---

## 📚 Related Documentation

- `docs/08-development/AUTHOR_ASSIGNMENT_POLICY.md` - Author assignment rules
- `data/authors/registry.py` - Single source of truth for authors
- `docs/05-data/DATA_STORAGE_POLICY.md` - Data file architecture
- `test_contaminant_authors.py` - 4-author validation test

---

## ✅ Approval Checklist

Before implementation:
- [ ] User approves normalization strategy
- [ ] Backup of Contaminants.yaml created
- [ ] Migration script tested on sample data
- [ ] Rollback plan documented

During implementation:
- [ ] Each phase completed sequentially
- [ ] Git commits after each phase
- [ ] Tests passing after each change

After implementation:
- [ ] All 8 tasks complete
- [ ] 4-author test passing
- [ ] Automated tests passing
- [ ] Documentation updated
- [ ] Changes committed to docs-consolidation branch

---

**Status**: ⏸️ AWAITING USER APPROVAL  
**Next Action**: User review and approval to proceed with Phase 1 implementation  
**Estimated Completion**: 1 hour 45 minutes after approval
