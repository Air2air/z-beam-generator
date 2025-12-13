# Author Assignment Policy

**Status**: MANDATORY  
**Effective**: December 1, 2025  
**Enforcement**: Fail-fast architecture - no fallbacks allowed

---

## Overview

Every material in `Materials.yaml` MUST have an `author.id` field assigned. This policy ensures:
1. Content voice consistency across all generated text
2. No silent fallbacks that could create inconsistent content
3. Clear attribution for all material content

---

## The 4 Authorized Authors

From `data/authors/registry.py`:

| ID | Name | Country | Persona File |
|----|------|---------|--------------|
| 1 | Yi-Chun Lin | Taiwan | `taiwan_persona.yaml` |
| 2 | Alessandro Moretti | Italy | `italy_persona.yaml` |
| 3 | Ikmanda Roswati | Indonesia | `indonesia_persona.yaml` |
| 4 | Todd Dunning | United States | `usa_persona.yaml` |

---

## Policy Rules

### Rule 1: NO Author Fallbacks

❌ **PROHIBITED**:
```python
author_id = material_data.get('author', {}).get('id', 2)  # NO DEFAULT
author_id = author_id or 2  # NO FALLBACK
```

✅ **REQUIRED**:
```python
from data.authors.registry import resolve_author_for_generation
author_info = resolve_author_for_generation(material_data)  # Fails if missing
```

### Rule 2: Random Assignment for New Materials

When adding a new material to `Materials.yaml`, an author MUST be randomly assigned:

```python
from data.authors.registry import assign_random_author

# For new materials without author
author_data = assign_random_author()
material_data['author'] = author_data
```

### Rule 3: Fail-Fast on Missing Author

If a material lacks `author.id`, generation MUST fail immediately with a clear error:

```
ValueError: Material 'NewMaterial' missing 'author' field. 
Add author.id to Materials.yaml for this material.
Valid author IDs: [1, 2, 3, 4]
```

---

## Implementation

### Adding a New Material

```python
from data.authors.registry import assign_random_author

# 1. Create material data
new_material = {
    'name': 'New Material',
    'category': 'metal',
    'subcategory': 'alloy',
    # ... other properties
}

# 2. Assign random author (MANDATORY)
new_material['author'] = assign_random_author()

# 3. Save to Materials.yaml
```

### Using the Registry

```python
from data.authors.registry import (
    get_author,              # Get by ID (fail-fast)
    resolve_author_for_generation,  # Get from material_data (fail-fast)
    assign_random_author,    # Random assignment for new materials
    list_valid_author_ids,   # [1, 2, 3, 4]
    validate_author_id,      # Check if ID is valid
)
```

---

## Testing Requirements

All tests MUST verify:
1. ✅ No author fallback patterns in production code
2. ✅ New materials get random author assignment
3. ✅ Missing author.id causes immediate failure
4. ✅ All 4 authors are used (balanced distribution over time)

Test file: `tests/test_author_assignment_policy.py`

---

## Enforcement

- **Pre-commit hook**: Scan for fallback patterns
- **Integrity checker**: Verify all materials have valid author.id
- **CI/CD**: Run author assignment tests on every PR

---

## Related Files

- `data/authors/registry.py` - Single source of truth for authors
- `shared/voice/profiles/*.yaml` - Voice persona configurations
- `tests/test_author_assignment_policy.py` - Policy enforcement tests
