# Hybrid Contamination Architecture - Quick Reference

**Implementation Date**: November 26, 2025  
**Status**: ✅ COMPLETE

---

## 🎯 Architecture Overview

**Hybrid Approach**: Best of both worlds
- **Contaminants.yaml**: Source of truth (contamination → materials)
- **Materials.yaml**: Cached reverse index (material → contaminations)
- **Result**: Fast O(1) lookups in BOTH directions

---

## 📂 File Structure

```
data/
├── contaminants/
│   └── Contaminants.yaml          # SOURCE OF TRUTH
│       contamination_patterns:
│         rust-oxidation:
│           valid_materials: [Steel, Iron, ...]
│           laser_parameters: {...}
│           visual_appearance: {...}
│
└── materials/
    └── Materials.yaml              # CACHED REVERSE INDEX
        materials:
          Steel:
            common_contaminants:    # ← AUTO-GENERATED
              - rust-oxidation
              - industrial-oil
              - scale-buildup
```

---

## 🔧 Usage

### Quick Lookups (Helper Functions)

```python
from shared.helpers.contamination_lookup import ContaminationLookup

lookup = ContaminationLookup()

# What materials can have rust?
materials = lookup.get_materials_for_contaminant('rust-oxidation')
# → ['Steel', 'Iron', 'Cast Iron']

# What contaminants affect Aluminum?
contaminants = lookup.get_contaminants_for_material('Aluminum')
# → ['industrial-oil', 'aluminum-oxidation', ...]

# Is combination valid?
if lookup.is_valid_combination('Aluminum', 'rust-oxidation'):
    print("Valid combination")
else:
    print("Invalid: Aluminum doesn't rust")

# Get full pattern data
pattern = lookup.get_pattern('rust-oxidation')
params = pattern['laser_parameters']
```

### Convenience Functions

```python
# Quick imports for common operations
from shared.helpers.contamination_lookup import (
    get_materials_for_contaminant,
    get_contaminants_for_material,
    is_valid_combination
)

# Use directly
materials = get_materials_for_contaminant('rust-oxidation')
contaminants = get_contaminants_for_material('Aluminum')
valid = is_valid_combination('Steel', 'rust-oxidation')
```

---

## 🔄 Sync Script

**When to run**: After ANY changes to Contaminants.yaml

```bash
# Dry run (show what would change)
python3 scripts/sync/populate_material_contaminants.py --dry-run

# Apply changes
python3 scripts/sync/populate_material_contaminants.py

# Verbose output
python3 scripts/sync/populate_material_contaminants.py --verbose
```

**What it does**:
1. Reads Contaminants.yaml (source of truth)
2. Builds reverse index: Material → List[Contaminant IDs]
3. Updates `common_contaminants` field in Materials.yaml
4. Creates backup before saving

---

## 📊 Performance

| Operation | Time Complexity | Method |
|-----------|----------------|--------|
| Get materials for contamination | O(1) | Direct lookup in Contaminants.yaml |
| Get contaminants for material | O(1) | Cached lookup in Materials.yaml |
| Validate combination | O(1) | Check membership in list |
| Add new contamination | O(1) + sync | Edit 1 file + run sync script |

---

## 🎯 Use Cases

### 1. Image Generation
```python
# User: "Generate Aluminum with rust"
lookup = ContaminationLookup()

if lookup.is_valid_combination('Aluminum', 'rust-oxidation'):
    # Generate image
    pattern = lookup.get_pattern('rust-oxidation')
    appearance = pattern['visual_characteristics']
else:
    print("Invalid: Aluminum doesn't rust")
```

### 2. Material Page Display
```python
# Show all contaminants for a material
contaminants = lookup.get_contaminants_for_material('Steel')

for c_id in contaminants:
    name = lookup.get_pattern_name(c_id)
    print(f"• {name}")
```

### 3. Contamination Pattern Page
```python
# Show all materials affected by contamination
materials = lookup.get_materials_for_contaminant('rust-oxidation')

for material in materials:
    print(f"• {material}")
```

### 4. Parameter Lookup
```python
# Get laser parameters for specific combination
if lookup.is_valid_combination(material, pattern_id):
    pattern = lookup.get_pattern(pattern_id)
    params = pattern['laser_parameters']
    fluence = params['fluence_range']['recommended_j_cm2']
```

---

## 🛠️ Maintenance

### Adding New Contamination Pattern

1. **Edit Contaminants.yaml** (source of truth):
   ```yaml
   contamination_patterns:
     my-new-pattern:
       name: "My New Contamination"
       valid_materials: [Steel, Aluminum, Copper]
       laser_parameters: {...}
   ```

2. **Run sync script**:
   ```bash
   python3 scripts/sync/populate_material_contaminants.py
   ```

3. **Verify**:
   ```python
   lookup = ContaminationLookup()
   assert 'my-new-pattern' in lookup.get_contaminants_for_material('Steel')
   ```

### Adding New Material

1. **Add to Materials.yaml** (no contaminants field needed)
2. **Edit relevant patterns in Contaminants.yaml**:
   ```yaml
   rust-oxidation:
     valid_materials:
       - Steel
       - NewMaterial  # ← Add here
   ```

3. **Run sync script** to populate cache

### Fixing Accuracy Issues

**Scenario**: "Steel" is too generic, need "Carbon Steel"

1. **Update Contaminants.yaml**:
   ```yaml
   rust-oxidation:
     valid_materials:
       - Carbon Steel  # ← More specific
       - Cast Iron
       # Remove generic "Steel"
   ```

2. **Run sync**:
   ```bash
   python3 scripts/sync/populate_material_contaminants.py
   ```

3. **Verify**:
   - Only edit 1 file (Contaminants.yaml)
   - Sync updates all 159 materials automatically
   - No risk of inconsistency

---

## 📈 Statistics

Current state (November 26, 2025):
- **100** contamination patterns
- **159** materials total
- **31** materials with contaminants (cached)
- **185** total material-contaminant associations
- **6.0** average contaminants per material

---

## ✅ Benefits

1. **Fast Lookups Both Directions**: O(1) for both queries
2. **Single Source of Truth**: Contaminants.yaml is authoritative
3. **No Manual Duplication**: Cache auto-generated by script
4. **Easy Maintenance**: Edit 1 file, run sync
5. **Consistency Guaranteed**: Sync ensures Materials.yaml matches Contaminants.yaml
6. **Accuracy Improvements**: Fix once in Contaminants.yaml, propagates everywhere

---

## 🔍 Example Workflow

**User wants to see contaminants for Aluminum material page**:

```python
from shared.helpers.contamination_lookup import ContaminationLookup

lookup = ContaminationLookup()

# Fast O(1) lookup from cached field
contaminants = lookup.get_contaminants_for_material('Aluminum')
# → ['industrial-oil', 'aluminum-oxidation', 'uv-chalking', ...]

# Display on page
for c_id in contaminants:
    pattern = lookup.get_pattern(c_id)
    print(f"### {pattern['name']}")
    print(f"Description: {pattern['description']}")
    
    # Show laser parameters
    params = pattern['laser_parameters']
    print(f"Recommended fluence: {params['fluence_range']['recommended_j_cm2']} J/cm²")
```

**Result**: Fast page load, accurate data, single query

---

## 🚨 Important Notes

1. **NEVER manually edit** `common_contaminants` in Materials.yaml
   - It's auto-generated by sync script
   - Manual edits will be overwritten

2. **ALWAYS run sync** after editing Contaminants.yaml
   - Keeps cache up to date
   - Ensures consistency

3. **Use helper functions** for lookups
   - Don't parse YAML directly in application code
   - Helper provides consistent interface

4. **Contaminants.yaml is source of truth**
   - All contamination properties live here
   - Materials.yaml just caches the reverse index

---

## 📚 Related Documentation

- **Accuracy Improvement**: `CONTAMINATION_ACCURACY_IMPROVEMENT_PROPOSAL.md`
- **Helper API**: `shared/helpers/contamination_lookup.py`
- **Sync Script**: `scripts/sync/populate_material_contaminants.py`
- **Architecture Decision**: Compare current vs reversed approaches
