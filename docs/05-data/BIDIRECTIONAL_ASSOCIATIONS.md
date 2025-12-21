# Bidirectional Associations Documentation

**Status**: ✅ IMPLEMENTED (December 19, 2025)  
**Total Associations**: 2,730 (bidirectional)  
**Test Coverage**: `tests/test_bidirectional_associations.py`

---

## Overview

All domain associations in DomainAssociations.yaml are **bidirectional**, meaning relationships can be queried in both directions. This enables rich traversal and discovery across the domain graph.

---

## Relationship Types

### 1. Material ↔ Contaminant (1,063 each direction)

**Forward**: `can_have_contamination` (Material → Contaminant)
```yaml
source_domain: materials
source_id: steel
target_domain: contaminants
target_id: rust-contamination
relationship_type: can_have_contamination
```

**Reverse**: `can_contaminate` (Contaminant → Material)
```yaml
source_domain: contaminants
source_id: rust-contamination
target_domain: materials
target_id: steel
relationship_type: can_contaminate
```

**Query Examples**:
- "Which contaminants can affect Steel?" → 69 results
- "Which materials can Rust contamination appear on?" → 5 results

---

### 2. Contaminant ↔ Compound (302 each direction)

**Forward**: `generates_byproduct` (Contaminant → Compound)
```yaml
source_domain: contaminants
source_id: oil-residue-contamination
target_domain: compounds
target_id: carbon-dioxide
relationship_type: generates_byproduct
```

**Reverse**: `byproduct_of` (Compound → Contaminant)
```yaml
source_domain: compounds
source_id: carbon-dioxide
target_domain: contaminants
target_id: oil-residue-contamination
relationship_type: byproduct_of
```

**Query Examples**:
- "What byproducts does Oil contamination generate?" → 10 results
- "What contamination types produce CO₂?" → 71 results

---

## Usage Examples

### Python API

```python
import yaml

# Load associations
with open('data/associations/DomainAssociations.yaml', 'r') as f:
    data = yaml.safe_load(f)

associations = data['associations']

# Query 1: What contaminants can affect Aluminum?
aluminum_risks = [
    a for a in associations 
    if a['source_id'] == 'aluminum' 
    and a['relationship_type'] == 'can_have_contamination'
]

# Query 2: What materials can be contaminated by Grease?
grease_targets = [
    a for a in associations 
    if 'grease' in a['source_id']
    and a['relationship_type'] == 'can_contaminate'
]

# Query 3: What compounds are byproducts of Paint removal?
paint_byproducts = [
    a for a in associations 
    if 'paint' in a['source_id']
    and a['relationship_type'] == 'generates_byproduct'
]

# Query 4: What contaminants produce Chromium VI?
chromium_sources = [
    a for a in associations 
    if a['source_id'] == 'chromium-vi'
    and a['relationship_type'] == 'byproduct_of'
]
```

### Command Line Queries

```bash
# Count associations by type
python3 << 'EOF'
import yaml
with open('data/associations/DomainAssociations.yaml', 'r') as f:
    data = yaml.safe_load(f)
    
for rel_type in data['metadata']['relationship_types']:
    count = len([a for a in data['associations'] if rel_type.split()[0] in a['relationship_type']])
    print(f"{rel_type}: {count}")
EOF

# Find all materials affected by specific contaminant
python3 << 'EOF'
import yaml
import sys

contaminant_id = sys.argv[1] if len(sys.argv) > 1 else 'rust-contamination'

with open('data/associations/DomainAssociations.yaml', 'r') as f:
    data = yaml.safe_load(f)
    
materials = [
    a['target_id'] for a in data['associations']
    if a['source_id'] == contaminant_id 
    and a['relationship_type'] == 'can_contaminate'
]

print(f"{contaminant_id} can contaminate {len(materials)} materials:")
for m in sorted(materials)[:10]:
    print(f"  • {m}")
EOF
```

---

## Metadata Structure

```yaml
metadata:
  version: 1.0.0
  description: Cross-domain relationships (bidirectional)
  last_updated: '2025-12-19'
  total_associations: 2730
  breakdown: '1063+1063+302+302'
  bidirectional: true
  relationship_types:
    - can_have_contamination (material → contaminant)
    - can_contaminate (contaminant → material)
    - generates_byproduct (contaminant → compound)
    - byproduct_of (compound → contaminant)
```

**Breakdown Explanation**:
- `1063`: Material → Contaminant associations
- `1063`: Contaminant → Material associations (reverse)
- `302`: Contaminant → Compound associations
- `302`: Compound → Contaminant associations (reverse)

---

## Regeneration

Associations are automatically regenerated from source data using:

```bash
python3 scripts/sync/regenerate_associations.py
```

**Process**:
1. Load Materials.yaml, Contaminants.yaml, Compounds.yaml
2. Extract material-contaminant relationships from `valid_materials` field
3. Extract contaminant-compound relationships from `byproducts` field
4. Create forward associations
5. Create reverse associations
6. Deduplicate
7. Write to DomainAssociations.yaml

**Triggers for regeneration**:
- After adding new materials
- After adding new contaminants
- After adding new compounds
- After normalizing byproduct compound names

---

## Testing

**Test Suite**: `tests/test_bidirectional_associations.py`

**Tests**:
1. ✅ Bidirectional structure verified
2. ✅ Material ↔ Contaminant counts match (1,063 each)
3. ✅ Contaminant ↔ Compound counts match (302 each)
4. ✅ Query capabilities work in all directions
5. ✅ Metadata accuracy verified

**Run tests**:
```bash
python3 tests/test_bidirectional_associations.py
```

---

## Benefits

### 1. Rich Querying
- Query from any direction without manual joins
- Discover relationships starting from any domain

### 2. Graph Traversal
- Navigate the domain graph bidirectionally
- Find indirect relationships (e.g., material → contaminant → compound)

### 3. Data Discovery
- "What produces this compound?" (sources)
- "What can this material experience?" (risks)
- "Where can this contamination appear?" (targets)

### 4. Validation
- Verify reverse relationships exist
- Detect orphaned associations
- Ensure data integrity

### 5. Performance
- Pre-computed relationships (no runtime joins)
- O(1) lookup in both directions
- Efficient filtering and aggregation

---

## Implementation Details

### Source Data

**Material → Contaminant** (from Contaminants.yaml):
```yaml
contamination_patterns:
  rust-contamination:
    valid_materials:
      - Steel
      - Iron
      - Stainless Steel
```

**Contaminant → Compound** (from Contaminants.yaml):
```yaml
contamination_patterns:
  rust-contamination:
    laser_properties:
      removal_characteristics:
        byproducts:
          - compound: iron-oxide
          - compound: carbon-dioxide
```

### Generated Associations

From the above, 4 associations are created:
1. `steel → rust-contamination` (can_have_contamination)
2. `rust-contamination → steel` (can_contaminate)
3. `rust-contamination → iron-oxide` (generates_byproduct)
4. `iron-oxide → rust-contamination` (byproduct_of)

---

## Maintenance

### Adding Relationships

**Automatic** (via regeneration script):
- Add material to `valid_materials` in Contaminants.yaml
- Add compound to `byproducts` in Contaminants.yaml
- Run regeneration script

**Manual** (not recommended):
- Must create BOTH forward and reverse associations
- Must update metadata breakdown
- Must maintain consistency

### Removing Relationships

**Recommended**:
1. Remove from source data (Contaminants.yaml)
2. Regenerate associations

**Not Recommended**:
- Manual deletion (breaks bidirectionality)

### Validation

Check association integrity:
```bash
python3 tests/test_bidirectional_associations.py
```

Verify counts match:
```python
import yaml

with open('data/associations/DomainAssociations.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Should be equal
forward = len([a for a in data['associations'] if a['relationship_type'] == 'can_have_contamination'])
reverse = len([a for a in data['associations'] if a['relationship_type'] == 'can_contaminate'])

assert forward == reverse, "Bidirectional counts must match"
```

---

## Related Documentation

- `E2E_DATA_ARCHITECTURE_EVALUATION_DEC19_2025.md` - Overall architecture
- `docs/05-data/DATA_ARCHITECTURE_QUICK_REF.md` - Quick reference
- `PHASE1_COMPOUND_NORMALIZATION_COMPLETE_DEC19_2025.md` - Compound associations
- `scripts/sync/regenerate_associations.py` - Regeneration script
- `tests/test_bidirectional_associations.py` - Test suite
