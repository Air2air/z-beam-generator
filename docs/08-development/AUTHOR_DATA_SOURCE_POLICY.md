# Author Data Source Policy

**Status**: MANDATORY  
**Date**: December 13, 2025  
**Scope**: All domains (materials, contaminants, settings)

## Policy Statement

**Author data MUST be read from data YAML files (single source of truth), NEVER from frontmatter.**

## Rationale

Frontmatter files are **generated FROM** data YAML files and serve as output/cache for the website. They are NOT the authoritative source of data. Reading from frontmatter creates a circular dependency and data inconsistency risks.

## Architecture

```
DATA YAML (Source of Truth)
    ↓
  Generation Pipeline
    ↓
FRONTMATTER (Generated Output)
```

**Flow**: `Data → Generation → Frontmatter`  
**NEVER**: `Frontmatter → Generation`

## Required Behavior

### ✅ CORRECT: Read from Data YAML

```python
# Materials domain
from domains.materials.data_loader import load_materials_data
materials_data = load_materials_data()
author_id = materials_data['materials']['Aluminum']['author']['id']

# Contaminants domain
from domains.contaminants.data_loader import load_pattern_data
pattern_data = load_pattern_data('rust_oxidation')
author_id = pattern_data['author']['id']

# Domain-agnostic (BEST)
all_data = generator.adapter.load_all_data()
data_root_key = generator.adapter.data_root_key
author_id = all_data[data_root_key][item_name]['author']['id']
```

### ❌ WRONG: Read from Frontmatter

```python
# NEVER DO THIS
frontmatter_path = f"frontmatter/materials/{slug}.yaml"
with open(frontmatter_path) as f:
    data = yaml.safe_load(f)
    author_id = data['author']['id']  # ❌ WRONG SOURCE
```

## Data File Locations

| Domain | Data File | Root Key |
|--------|-----------|----------|
| Materials | `data/materials/Materials.yaml` | `materials` |
| Contaminants | `data/contaminants/Contaminants.yaml` | `contamination_patterns` |
| Settings | `data/settings/Settings.yaml` | `settings` |

## Test Requirements

All tests MUST set author data in data YAML files:

```python
# ✅ CORRECT - Set in data file
def set_author_for_item(item_name: str, author_id: int):
    """
    Set author ID in data YAML (NOT frontmatter)
    
    POLICY: Author data MUST be read from data YAML files.
    """
    data_path = Path(f"data/{domain}/{domain.title()}.yaml")
    with open(data_path, 'r') as f:
        data = yaml.safe_load(f)
    
    data[data_root_key][item_name]['author']['id'] = author_id
    
    with open(data_path, 'w') as f:
        yaml.dump(data, f)
```

## Enforcement

- All generator code reads from data YAML via domain adapters
- Tests set author data in data files, not frontmatter
- Code reviews verify no frontmatter reading for author data
- Grade F violation if author read from frontmatter

## Related Policies

- `DATA_STORAGE_POLICY.md` - Overall data architecture
- `DUAL_WRITE_POLICY.md` - Data → Frontmatter sync requirements

## References

- `generation/core/evaluated_generator.py` - Domain-aware author loading
- `generation/core/adapters/domain_adapter.py` - Generic data access
- `test_4_materials_4_authors.py` - Example test (materials)
- `test_4_contaminants_4_authors.py` - Example test (contaminants)
