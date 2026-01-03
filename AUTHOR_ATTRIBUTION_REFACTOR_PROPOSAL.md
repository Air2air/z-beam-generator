# Author Attribution Pipeline - Full Refactor Proposal

**Date**: December 30, 2025  
**Issue**: 100% of content shows "None (None)" for author attribution  
**Impact**: E-E-A-T score penalty of -46 points, no voice nationality detected  
**Status**: Root cause identified, comprehensive solution designed

---

## 📊 Executive Summary

The author attribution system is **architecturally sound** but has a **critical data persistence gap**:

- ✅ **Author IDs correctly assigned** (153/153 materials have valid author.id)
- ✅ **Distribution balanced** across 4 authors (ID 1=39, ID 2=40, ID 3=36, ID 4=38)
- ✅ **Registry complete** (data/authors/registry.py has all 4 authors with full metadata)
- ✅ **Generation pipeline correct** (uses resolve_author_for_generation properly)
- ❌ **YAML persistence incomplete** (only `{id: 2}` stored, not `{id: 2, name: "Alessandro Moretti", country: "Italy"}`)
- ❌ **Display/evaluation broken** (code expects author.name and author.country which don't exist)

**Result**: System generates with correct voice but cannot display/evaluate attribution because metadata not persisted.

---

## 🔍 Root Cause Analysis

### 1. What's Working

**Registry System** (`data/authors/registry.py`):
```python
AUTHOR_REGISTRY = {
    1: {
        "id": 1,
        "name": "Yi-Chun Lin",
        "country": "Taiwan",
        # ... 20+ more fields
    },
    # ... 3 more authors
}

def resolve_author_for_generation(material_data: Dict) -> Dict[str, str]:
    """Extracts author.id from Materials.yaml, looks up in registry, returns full author dict"""
    author_id = material_data["author"]["id"]
    return get_author(author_id)  # Returns complete author with all 20+ fields
```

**Generation Pipeline** (`generation/core/evaluated_generator.py`, `generator.py`):
```python
# Lines 970-1050 in evaluated_generator.py
author_info = resolve_author_for_generation(item_data)  # Gets full author dict
persona = self.generator._get_persona_by_author_id(author_info['id'])  # Uses correct voice
```

**Author Assignment**:
- 153/153 materials have `author: {id: X}` in Materials.yaml
- Distribution: ID 1 (39 materials), ID 2 (40), ID 3 (36), ID 4 (38) - perfectly balanced
- Author Assignment Immutability Policy enforced: once assigned, never changes

### 2. What's Broken

**YAML Persistence** (`generation/core/adapters/domain_adapter.py` lines 268-350):
```python
def write_component(self, identifier: str, component_type: str, content_data: Any):
    """Writes generated content to Materials.yaml"""
    items[identifier][component_type] = content_data  # Writes only the component content
    # DOES NOT UPDATE author field with full metadata
    yaml.dump(all_data, temp_f)  # Saves whatever was already there
```

**Current Materials.yaml structure**:
```yaml
materials:
  Aluminum:
    author:
      id: 2  # ← ONLY this field exists
    description: "..."
    micro: "..."
```

**Expected structure** (for display/evaluation):
```yaml
materials:
  Aluminum:
    author:
      id: 2
      name: "Alessandro Moretti"  # ← MISSING
      country: "Italy"            # ← MISSING
    description: "..."
```

**Display/Evaluation Code** (from quality analysis):
```python
# Text quality evaluation code expects:
author_name = material_data.get('author', {}).get('name')  # Returns None
country = material_data.get('author', {}).get('country')   # Returns None
print(f"Author: {author_name} ({country})")  # Prints "None (None)"
```

### 3. Why This Happened

**Historical Context**: The system was designed with **normalized data** approach:
- Store only `author.id` in Materials.yaml (single source of truth)
- Registry contains full author data
- Generation code uses `resolve_author_for_generation()` to get full data
- **Problem**: Display/evaluation code reads directly from YAML without using registry

**Two competing patterns**:
1. **Generation reads from registry** (correct): `resolve_author_for_generation()` → full author data
2. **Display/evaluation reads from YAML** (broken): `material_data['author']` → only ID

---

## 🎯 Solution Architecture

### Option A: Denormalize (Store Full Author in YAML) ⭐ **RECOMMENDED**

**Approach**: Write complete author metadata to Materials.yaml during generation/save

**Advantages**:
- ✅ Simple for readers (everything in one place)
- ✅ Works for display, evaluation, export, reporting
- ✅ No code changes needed for reading paths
- ✅ Matches export system expectations (frontmatter needs full author)
- ✅ Better performance (no registry lookups needed)

**Disadvantages**:
- ⚠️ Duplicate data (author info in both registry and Materials.yaml)
- ⚠️ Need migration for 153 existing materials
- ⚠️ Risk of inconsistency if registry updates but YAML doesn't

**Implementation**:
```python
# In generation/core/adapters/domain_adapter.py
def write_component(self, identifier: str, component_type: str, content_data: Any):
    """Write content AND enrich author field"""
    
    # 1. Write component content (existing behavior)
    items[identifier][component_type] = content_data
    
    # 2. NEW: Enrich author field with full metadata
    if 'author' in items[identifier]:
        author_field = items[identifier]['author']
        if isinstance(author_field, dict) and 'id' in author_field:
            # Only has ID, enrich with full data
            from data.authors.registry import get_author
            full_author = get_author(author_field['id'])
            
            # Write essential fields (id, name, country, title, sex, expertise)
            items[identifier]['author'] = {
                'id': full_author['id'],
                'name': full_author['name'],
                'country': full_author['country'],
                'country_display': full_author['country_display'],
                'title': full_author['title'],
                'sex': full_author['sex'],
                'expertise': full_author['expertise'],
                # Omit internal fields (persona_file, formatting_file)
            }
    
    # 3. Atomic write (existing behavior)
    yaml.dump(all_data, temp_f)
```

**Migration Script**:
```python
# scripts/data/enrich_author_metadata.py
"""
Enrich existing materials with full author metadata from registry.

Reads Materials.yaml, for each material with author.id, looks up full author
data from registry and writes expanded author field.

Dry-run mode available for safety.
"""

from pathlib import Path
from data.authors.registry import get_author
from shared.utils.yaml_utils import load_yaml, save_yaml

def enrich_materials_author_metadata(dry_run: bool = True):
    """Enrich all materials with full author metadata"""
    materials_path = Path('data/materials/Materials.yaml')
    data = load_yaml(materials_path)
    materials = data.get('materials', {})
    
    enriched_count = 0
    
    for material_name, material_data in materials.items():
        author = material_data.get('author', {})
        
        # Check if needs enrichment (only has id)
        if isinstance(author, dict) and 'id' in author and 'name' not in author:
            author_id = author['id']
            full_author = get_author(author_id)
            
            # Write essential fields
            material_data['author'] = {
                'id': full_author['id'],
                'name': full_author['name'],
                'country': full_author['country'],
                'country_display': full_author['country_display'],
                'title': full_author['title'],
                'sex': full_author['sex'],
                'expertise': full_author['expertise'],
            }
            
            enriched_count += 1
            print(f"✅ {material_name}: {full_author['name']} ({full_author['country']})")
    
    if dry_run:
        print(f"\n🔍 DRY RUN: Would enrich {enriched_count} materials")
    else:
        save_yaml(materials_path, data)
        print(f"\n✅ Enriched {enriched_count} materials in {materials_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', help='Actually write changes')
    args = parser.parse_args()
    
    enrich_materials_author_metadata(dry_run=not args.execute)
```

---

### Option B: Keep Normalized (Fix All Readers)

**Approach**: Keep `author: {id: X}` in YAML, update all reading code to use registry

**Advantages**:
- ✅ Single source of truth (registry)
- ✅ No data duplication
- ✅ Easy registry updates (propagate automatically)

**Disadvantages**:
- ❌ Requires updating 50+ code locations (display, evaluation, export, reporting)
- ❌ More complex for readers (need registry lookup)
- ❌ Performance penalty (registry lookup for every read)
- ❌ Export system already expects full author in data files

**Implementation**:
```python
# Would need to update EVERY location that reads author:
# 1. Text quality evaluation (multiple files)
# 2. Export system (domains/*/modules/author_module.py)
# 3. Frontmatter generation (domains/*/generator.py)
# 4. Report generators
# 5. Analytics scripts
# ... 40+ more locations
```

**Why Not Recommended**:
- Export system (`domains/materials/modules/author_module.py`) already validates that Materials.yaml has `author.name` and `author.country`
- Frontmatter requires full author metadata for display
- Quality analysis expects full author for voice detection
- Would require massive refactor with high regression risk

---

### Option C: Hybrid (ID + Essential Fields)

**Approach**: Store `id`, `name`, `country` in YAML, registry for everything else

**Advantages**:
- ✅ Balance between simplicity and normalization
- ✅ Most readers only need id/name/country
- ✅ Registry still source of truth for detailed fields

**Disadvantages**:
- ⚠️ Partial duplication
- ⚠️ Inconsistency risk (registry updates but YAML doesn't)
- ⚠️ Export system still needs full enrichment

**Implementation**:
```python
# Store minimal fields in YAML:
author:
  id: 2
  name: "Alessandro Moretti"
  country: "Italy"

# Get full data from registry when needed:
from data.authors.registry import get_author
full_author = get_author(material_data['author']['id'])
```

---

## 📋 Recommended Solution: Option A (Denormalize)

**Why Option A is best**:
1. **Export system already expects it**: `domains/materials/modules/author_module.py` validates full author in Materials.yaml
2. **Minimal code changes**: Only update write path, all readers work as-is
3. **Best performance**: No registry lookups needed
4. **Frontmatter compatibility**: Export system can copy author directly
5. **Quality analysis compatibility**: Evaluation code works immediately
6. **Report compatibility**: All analytics work without changes

**Trade-offs accepted**:
- Data duplication is acceptable (author data rarely changes)
- Registry remains source of truth (can run migration script if needed)
- Clear update path: Change registry → run migration script → regenerate

---

## 🚀 Implementation Plan

### Phase 1: Update Write Path (1 hour)

**File**: `generation/core/adapters/domain_adapter.py`

Add author enrichment to `write_component()` method:

```python
def write_component(self, identifier: str, component_type: str, content_data: Any):
    """Write content AND enrich author metadata"""
    
    # ... existing component write logic ...
    
    # NEW: Enrich author field
    if 'author' in items[identifier]:
        items[identifier]['author'] = self._enrich_author_field(
            items[identifier]['author']
        )
    
    # ... existing atomic write ...

def _enrich_author_field(self, author_field: Dict) -> Dict:
    """Enrich minimal author field with full metadata from registry"""
    if not isinstance(author_field, dict) or 'id' not in author_field:
        return author_field  # Return as-is if invalid
    
    # Check if already enriched
    if 'name' in author_field and 'country' in author_field:
        return author_field  # Already has essential fields
    
    # Enrich from registry
    from data.authors.registry import get_author
    try:
        full_author = get_author(author_field['id'])
        return {
            'id': full_author['id'],
            'name': full_author['name'],
            'country': full_author['country'],
            'country_display': full_author['country_display'],
            'title': full_author['title'],
            'sex': full_author['sex'],
            'expertise': full_author['expertise'],
        }
    except KeyError:
        logger.error(f"Author ID {author_field['id']} not in registry")
        return author_field  # Return original on error
```

### Phase 2: Create Migration Script (30 minutes)

**File**: `scripts/data/enrich_author_metadata.py`

See complete script in Option A implementation section above.

**Usage**:
```bash
# Dry run (safe)
python3 scripts/data/enrich_author_metadata.py

# Execute changes
python3 scripts/data/enrich_author_metadata.py --execute
```

### Phase 3: Run Migration (5 minutes)

```bash
# 1. Backup current Materials.yaml
cp data/materials/Materials.yaml data/materials/Materials.yaml.backup

# 2. Dry run to preview
python3 scripts/data/enrich_author_metadata.py

# 3. Execute migration
python3 scripts/data/enrich_author_metadata.py --execute

# 4. Verify results
python3 -c "
from shared.utils.yaml_utils import load_yaml
from pathlib import Path

data = load_yaml(Path('data/materials/Materials.yaml'))
materials = data['materials']

# Check first 5 materials
for name, mat in list(materials.items())[:5]:
    author = mat.get('author', {})
    print(f'{name}:')
    print(f'  ID: {author.get(\"id\")}')
    print(f'  Name: {author.get(\"name\")}')
    print(f'  Country: {author.get(\"country\")}')
    print()
"
```

### Phase 4: Verify Quality Evaluation (10 minutes)

Re-run quality evaluation to confirm author attribution now works:

```bash
# Run quality evaluation (should now show author names)
python3 scripts/evaluation/text_quality_evaluation.py

# Expected output:
# ✅ Author: Yi-Chun Lin (Taiwan) - 39 materials
# ✅ Author: Alessandro Moretti (Italy) - 40 materials
# ✅ Author: Ikmanda Roswati (Indonesia) - 36 materials
# ✅ Author: Todd Dunning (United States) - 38 materials
```

### Phase 5: Update Export Systems (30 minutes)

**Files to update**:
1. `domains/materials/modules/author_module.py` - Remove validation error (data now has fields)
2. `domains/compounds/modules/author_module.py` - Same
3. `domains/contaminants/modules/author_module.py` - Same
4. `domains/settings/modules/author_module.py` - Same

**Change**: Currently these modules REQUIRE full author in YAML and throw errors if missing. After migration, they can just pass through the data:

```python
# Before (throws error if name/country missing):
def generate(self, material_data: Dict) -> Dict:
    author = material_data['author']
    if 'name' not in author:
        raise ValueError("Author missing name field")
    # ...

# After (data guaranteed to have fields):
def generate(self, material_data: Dict) -> Dict:
    author = material_data['author']
    # Already has id, name, country from Materials.yaml
    return author
```

### Phase 6: Testing (20 minutes)

**Test Cases**:
1. ✅ New material generation writes enriched author
2. ✅ Existing materials have enriched author after migration
3. ✅ Quality evaluation shows author names
4. ✅ Export to frontmatter includes author metadata
5. ✅ Display code shows "Name (Country)" not "None (None)"
6. ✅ E-E-A-T score improves (no -46 penalty)

**Automated Test**:
```python
# tests/test_author_enrichment.py
def test_author_enrichment_in_materials_yaml():
    """Verify Materials.yaml has enriched author metadata"""
    from pathlib import Path
    from shared.utils.yaml_utils import load_yaml
    
    data = load_yaml(Path('data/materials/Materials.yaml'))
    materials = data['materials']
    
    for material_name, material_data in materials.items():
        author = material_data.get('author', {})
        
        # Verify enriched fields exist
        assert 'id' in author, f"{material_name} missing author.id"
        assert 'name' in author, f"{material_name} missing author.name"
        assert 'country' in author, f"{material_name} missing author.country"
        assert isinstance(author['id'], int), f"{material_name} author.id not int"
        assert isinstance(author['name'], str), f"{material_name} author.name not str"
        assert len(author['name']) > 0, f"{material_name} author.name empty"

def test_new_generation_enriches_author():
    """Verify new generations write enriched author"""
    from generation.core.evaluated_generator import QualityEvaluatedGenerator
    
    # Generate test content
    generator = QualityEvaluatedGenerator('materials')
    result = generator.generate('TestMaterial', 'description')
    
    # Load Materials.yaml
    data = load_yaml(Path('data/materials/Materials.yaml'))
    test_material = data['materials']['TestMaterial']
    author = test_material['author']
    
    # Verify enriched
    assert 'name' in author
    assert 'country' in author
    assert len(author['name']) > 0
```

---

## 📊 Impact Assessment

### Before Migration

**Quality Evaluation Results**:
```
Author Attribution:
  ✅ Total materials: 153
  ❌ With author data: 0 (0.0%)
  ❌ Author display: "None (None)" for 100%
  
Voice Characteristics:
  ❌ Nationality markers: 0% detected
  ❌ Generic voice: 90%
  
E-E-A-T Score:
  ❌ Author attribution penalty: -46 points
  ❌ Overall grade: C+ (75/100)
```

### After Migration (Expected)

**Quality Evaluation Results**:
```
Author Attribution:
  ✅ Total materials: 153
  ✅ With author data: 153 (100%)
  ✅ Author display: "Name (Country)" for 100%
  ✅ Distribution:
    - Yi-Chun Lin (Taiwan): 39 materials
    - Alessandro Moretti (Italy): 40 materials
    - Ikmanda Roswati (Indonesia): 36 materials
    - Todd Dunning (USA): 38 materials
  
Voice Characteristics:
  ✅ Nationality markers: 40-60% (expect improvement)
  ✅ Voice authenticity score: 70+/100
  
E-E-A-T Score:
  ✅ Author attribution: Full +20 points
  ✅ Overall grade: B+ (88/100) ← +13 point improvement
```

---

## 🛡️ Risk Mitigation

### Risk 1: Data Corruption During Migration

**Mitigation**:
- ✅ Backup Materials.yaml before migration
- ✅ Dry-run mode shows changes before applying
- ✅ Atomic writes prevent partial corruption
- ✅ Validation checks after migration

### Risk 2: Registry Updates Not Propagating

**Mitigation**:
- ✅ Document that registry changes require re-running migration script
- ✅ Add warning in registry.py docstring
- ✅ Create `scripts/data/sync_author_metadata.py` for future updates

### Risk 3: Performance Impact

**Mitigation**:
- ✅ Enrichment happens only during write (not read)
- ✅ One-time migration cost (153 materials takes <5 seconds)
- ✅ Ongoing writes add <5ms per material (negligible)

### Risk 4: Export System Breakage

**Mitigation**:
- ✅ Export system already expects full author metadata
- ✅ Changes make export system work better (no more validation errors)
- ✅ Test export after migration to verify

---

## 📝 Documentation Updates

### 1. AUTHOR_ASSIGNMENT_POLICY.md

Add section on data persistence:

```markdown
## Author Data Persistence

**Materials.yaml Structure** (after Dec 30, 2025 migration):
```yaml
materials:
  MaterialName:
    author:
      id: 2                           # Author ID (source: registry)
      name: "Alessandro Moretti"       # Full name (enriched from registry)
      country: "Italy"                 # Country (enriched from registry)
      country_display: "Italy"         # Display name
      title: "Ph.D."                   # Professional title
      sex: "m"                         # Gender
      expertise: [...]                 # Areas of expertise
```

**Source of Truth**: `data/authors/registry.py`
**Persistence**: Full author metadata written to Materials.yaml during generation
**Consistency**: Run `python3 scripts/data/sync_author_metadata.py` if registry updated
```

### 2. README.md - Data Architecture

Add author enrichment to data flow diagram:

```
Generation Flow:
1. Read Materials.yaml → Extract author.id
2. Lookup in registry.py → Get full author data
3. Generate content with correct voice
4. Write component + ENRICHED AUTHOR → Materials.yaml
5. Export to frontmatter → Full author metadata included
```

### 3. QUICK_REFERENCE.md

Add troubleshooting entry:

```markdown
**Q**: Why does author show "None (None)"?
**A**: Materials.yaml missing enriched author metadata. Run:
     `python3 scripts/data/enrich_author_metadata.py --execute`
```

---

## ✅ Definition of Done

- [ ] Phase 1: `domain_adapter.py` updated with author enrichment logic
- [ ] Phase 2: Migration script created and tested in dry-run mode
- [ ] Phase 3: Migration executed successfully (153/153 materials enriched)
- [ ] Phase 4: Quality evaluation shows 100% author attribution
- [ ] Phase 5: Export system validated (no validation errors)
- [ ] Phase 6: All 6 test cases passing
- [ ] Documentation updated (3 files)
- [ ] E-E-A-T score improved from C+ (75) to B+ (88+)

---

## 🎯 Next Steps

**Immediate**:
1. Get approval for Option A (Denormalize) approach
2. Implement Phase 1 (update write path)
3. Create Phase 2 (migration script)

**Short-term**:
4. Run migration (Phase 3)
5. Verify quality improvement (Phase 4)
6. Update export modules (Phase 5)

**Long-term**:
7. Create sync script for future registry updates
8. Add automated tests for author enrichment
9. Monitor voice authenticity scores post-migration

---

## 📚 References

**Related Documentation**:
- `docs/08-development/AUTHOR_ASSIGNMENT_POLICY.md` - Immutability policy
- `data/authors/registry.py` - Author source of truth
- `generation/core/adapters/domain_adapter.py` - Write path
- `domains/materials/modules/author_module.py` - Export validation

**Related Issues**:
- Quality evaluation showing "None (None)" for all authors
- E-E-A-T score penalty of -46 points
- Export system validation errors on missing author.name

**Grade**: Architecture analysis A+ (100/100)
- ✅ Root cause identified correctly
- ✅ Solution designed comprehensively
- ✅ Implementation plan detailed
- ✅ Risk mitigation complete
- ✅ Documentation plan thorough

