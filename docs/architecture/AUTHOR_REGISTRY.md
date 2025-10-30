# Author Registry Architecture

**Status**: Active  
**Version**: 1.0  
**Last Updated**: October 30, 2025

---

## Overview

The Author Registry provides a **single source of truth** for all author information in the Z-Beam Generator system. It eliminates confusion from country name variations, removes fallback logic, and provides type-safe author lookups with fail-fast behavior.

---

## Problem Solved

### Before: Multiple Sources of Confusion

**Issues**:
- ❌ Country variations: "United States" vs "United States (California)" vs "usa"
- ❌ Fallback logic masking missing data: `.get("country", "Unknown")`
- ❌ Silent degradation to defaults: `.setdefault("country", "usa")`
- ❌ Normalization ambiguity across codebase
- ❌ No validation of author IDs

**Impact**:
- Author information inconsistencies
- Hard-to-debug persona/formatting file lookup failures
- Silent failures degrading to "Unknown" or "usa"

### After: Single Source of Truth

**Solution**:
- ✅ Centralized `AUTHOR_REGISTRY` in `config/authors_registry.py`
- ✅ Type-safe `AuthorCountry` literal: only 4 values allowed
- ✅ Normalized country codes: `taiwan`, `italy`, `indonesia`, `usa`
- ✅ Display country names: `Taiwan`, `Italy`, `Indonesia`, `United States`
- ✅ Fail-fast validation on invalid/missing author IDs
- ✅ Zero fallbacks or silent degradation

---

## Architecture

### Core Components

```
config/authors_registry.py       # Single source of truth
├── AUTHOR_REGISTRY             # Authoritative mapping: ID → Author data
├── get_author()                # Lookup by ID (fail-fast)
├── validate_author_id()        # Check if ID exists
├── get_country_normalized()    # Get normalized country code
├── get_country_display()       # Get display country name
├── get_persona_files()         # Get persona/formatting files
└── resolve_author_for_generation() # Extract from Materials.yaml

data/authors/authors.json        # Backup copy (kept in sync)

utils/core/author_manager.py     # Legacy wrapper (delegates to registry)
```

### Data Flow

```
Materials.yaml
  └── author.id: 1
       ↓
  config.authors_registry.get_author(1)
       ↓
  {
    "id": 1,
    "name": "Yi-Chun Lin",
    "country": "taiwan",           # Normalized key for lookups
    "country_display": "Taiwan",   # Display name for frontmatter
    "persona_file": "taiwan_persona.yaml",
    "formatting_file": "taiwan_formatting.yaml"
  }
```

---

## Author Registry Schema

### AUTHOR_REGISTRY Structure

```python
from typing import Dict, Literal

# Type-safe country codes (only 4 values allowed)
AuthorCountry = Literal["taiwan", "italy", "indonesia", "usa"]

AUTHOR_REGISTRY: Dict[int, Dict[str, str]] = {
    1: {
        "id": 1,                              # Author ID
        "name": "Yi-Chun Lin",                # Full name
        "country": "taiwan",                  # Normalized code (lowercase, no spaces)
        "country_display": "Taiwan",          # Display name for frontmatter
        "title": "Ph.D.",                     # Academic title
        "sex": "f",                           # Gender
        "expertise": "Laser Materials Processing",  # Research area
        "image": "/images/author/yi-chun-lin.jpg",  # Avatar path
        "persona_file": "taiwan_persona.yaml",      # Writing style prompts
        "formatting_file": "taiwan_formatting.yaml" # Presentation rules
    },
    # ... 3 more authors
}
```

### Field Definitions

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `id` | int | Unique identifier (matches Materials.yaml) | `1` |
| `name` | str | Full name for display | `"Yi-Chun Lin"` |
| `country` | AuthorCountry | Normalized code for persona lookup | `"taiwan"` |
| `country_display` | str | Human-readable country name | `"Taiwan"` |
| `title` | str | Academic title | `"Ph.D."` |
| `sex` | str | Gender identifier | `"f"` or `"m"` |
| `expertise` | str | Research specialization | `"Laser Materials Processing"` |
| `image` | str | Avatar image path | `"/images/author/..."` |
| `persona_file` | str | Writing style prompt file | `"taiwan_persona.yaml"` |
| `formatting_file` | str | Formatting rules file | `"taiwan_formatting.yaml"` |

---

## API Reference

### Core Functions

#### `get_author(author_id: int) -> Dict[str, str]`

Get complete author information by ID.

**Parameters**:
- `author_id`: Author ID from Materials.yaml

**Returns**: Author dictionary with all fields

**Raises**: `KeyError` if author_id not in registry

**Example**:
```python
from config.authors_registry import get_author

author = get_author(1)
# Returns: {"id": 1, "name": "Yi-Chun Lin", "country": "taiwan", ...}
```

---

#### `validate_author_id(author_id: int) -> bool`

Check if author ID exists in registry.

**Parameters**:
- `author_id`: Author ID to validate

**Returns**: `True` if valid, `False` otherwise

**Example**:
```python
from config.authors_registry import validate_author_id

validate_author_id(1)    # True
validate_author_id(999)  # False
```

---

#### `get_country_normalized(author_id: int) -> AuthorCountry`

Get normalized country code for persona/formatting lookup.

**Parameters**:
- `author_id`: Author ID from Materials.yaml

**Returns**: One of: `"taiwan"`, `"italy"`, `"indonesia"`, `"usa"`

**Raises**: `KeyError` if author_id not in registry

**Example**:
```python
from config.authors_registry import get_country_normalized

country = get_country_normalized(1)  # Returns: "taiwan"
```

---

#### `get_country_display(author_id: int) -> str`

Get display-friendly country name for frontmatter.

**Parameters**:
- `author_id`: Author ID from Materials.yaml

**Returns**: Display country name

**Example**:
```python
from config.authors_registry import get_country_display

country = get_country_display(1)  # Returns: "Taiwan"
```

---

#### `get_persona_files(author_id: int) -> Tuple[str, str]`

Get persona and formatting files for prompt construction.

**Parameters**:
- `author_id`: Author ID from Materials.yaml

**Returns**: Tuple of (persona_file, formatting_file)

**Example**:
```python
from config.authors_registry import get_persona_files

persona, formatting = get_persona_files(1)
# Returns: ("taiwan_persona.yaml", "taiwan_formatting.yaml")
```

---

#### `resolve_author_for_generation(material_data: Dict) -> Dict[str, str]`

Extract author.id from Materials.yaml and resolve to complete author info.

**Parameters**:
- `material_data`: Material dictionary from Materials.yaml

**Returns**: Complete author information

**Raises**: 
- `ValueError`: If material_data malformed or missing author.id
- `KeyError`: If author.id not in registry

**Example**:
```python
from config.authors_registry import resolve_author_for_generation

material_data = {
    "name": "Aluminum",
    "author": {"id": 1}
}

author = resolve_author_for_generation(material_data)
# Returns: {"id": 1, "name": "Yi-Chun Lin", ...}
```

---

## Usage Patterns

### Pattern 1: Direct Registry Lookup

```python
from config.authors_registry import get_author

# Get author from Materials.yaml author.id
author_id = material_data["author"]["id"]
author = get_author(author_id)

# Use normalized country for persona lookup
persona_file = f"prompts/personas/{author['country']}_persona.yaml"
```

### Pattern 2: Material Author Resolution

```python
from config.authors_registry import resolve_author_for_generation

# Extract author from material data (fail-fast if missing)
author = resolve_author_for_generation(material_data)

# Use for content generation
generate_content(
    material_name=material_data["name"],
    author_country=author["country"],
    author_name=author["name"]
)
```

### Pattern 3: Validation

```python
from config.authors_registry import validate_author_id

# Validate before lookup
author_id = material_data.get("author", {}).get("id")
if not validate_author_id(author_id):
    raise ValueError(f"Invalid author ID: {author_id}")

author = get_author(author_id)
```

---

## Migration Guide

### From Old System

**Before** (with fallbacks):
```python
# ❌ Old way - fallbacks mask issues
author = material_data.get("author", {})
author_id = author.get("id", 1)  # Fallback to 1
country = author.get("country", "usa")  # Fallback to usa
```

**After** (fail-fast):
```python
# ✅ New way - fail if missing
from config.authors_registry import resolve_author_for_generation

author = resolve_author_for_generation(material_data)  # Raises if missing
country = author["country"]  # Always valid, no fallback needed
```

### Updating Materials.yaml

All materials must have `author.id`:

```yaml
materials:
  Aluminum:
    author:
      id: 1  # REQUIRED - no fallbacks
    category: metal
    # ... other properties
```

---

## Fail-Fast Behavior

### What Triggers Failures

1. **Missing author field in Materials.yaml**:
   ```python
   material_data = {"name": "Test"}  # Missing author
   resolve_author_for_generation(material_data)  # ValueError
   ```

2. **Missing author.id**:
   ```python
   material_data = {"name": "Test", "author": {}}  # No id
   resolve_author_for_generation(material_data)  # ValueError
   ```

3. **Invalid author ID**:
   ```python
   author = get_author(999)  # KeyError: Author ID 999 not in registry
   ```

### Error Messages

All errors provide clear, actionable messages:

```python
KeyError: Author ID 999 not in registry. Valid IDs: [1, 2, 3, 4]. 
Check Materials.yaml author.id field.

ValueError: Material missing 'author' field. 
Add author.id to Materials.yaml for this material.
```

---

## Testing

### Test Coverage

Located in `tests/e2e/test_author_resolution.py`:

- ✅ Author lookup by ID
- ✅ Registry validation
- ✅ Country normalization
- ✅ Fail-fast on missing author
- ✅ Fail-fast on invalid author ID
- ✅ Registry/JSON synchronization

### Running Tests

```bash
# Run all author tests
python3 -m pytest tests/e2e/test_author_resolution.py -v

# Test specific functionality
python3 -m pytest tests/e2e/test_author_resolution.py::TestAuthorResolution::test_author_registry_validation -v
```

---

## Maintenance

### Adding New Authors

1. **Update Registry** (`config/authors_registry.py`):
   ```python
   AUTHOR_REGISTRY[5] = {
       "id": 5,
       "name": "New Author",
       "country": "usa",  # Must be: taiwan, italy, indonesia, usa
       "country_display": "United States",
       "persona_file": "usa_persona.yaml",
       "formatting_file": "usa_formatting.yaml",
       # ... other fields
   }
   ```

2. **Update JSON** (`data/authors/authors.json`):
   ```json
   {
     "id": 5,
     "name": "New Author",
     "country": "usa",
     "country_display": "United States"
   }
   ```

3. **Run Tests**:
   ```bash
   python3 -m pytest tests/e2e/test_author_resolution.py -v
   ```

### Modifying Existing Authors

**IMPORTANT**: Never change author IDs. Update other fields as needed.

```python
# ✅ OK: Update name, expertise, etc.
AUTHOR_REGISTRY[1]["expertise"] = "Updated expertise"

# ❌ NEVER: Change ID (breaks Materials.yaml references)
AUTHOR_REGISTRY[1]["id"] = 999  # DON'T DO THIS
```

---

## Benefits

### Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| Country values | 4+ variations | Exactly 4 normalized codes |
| Lookup failures | Silent fallback to "usa" | Immediate KeyError with message |
| Missing authors | Degraded to "Unknown" | Immediate ValueError with fix |
| Type safety | None | AuthorCountry literal type |
| Testing | Hard to validate | Clear pass/fail tests |
| Debugging | Confusing fallback chains | Clear error at source |

### Key Improvements

1. ✅ **Single Source of Truth**: Registry is authoritative
2. ✅ **Type Safety**: Literal types prevent typos
3. ✅ **Fail-Fast**: Invalid data raises errors immediately
4. ✅ **Zero Ambiguity**: Only 4 country codes exist
5. ✅ **Explicit Mapping**: Each author specifies persona files
6. ✅ **No Silent Failures**: No degradation to defaults

---

## See Also

- **Implementation**: `config/authors_registry.py`
- **Tests**: `tests/e2e/test_author_resolution.py`
- **Legacy Wrapper**: `utils/core/author_manager.py`
- **Text Component**: Uses author country for persona selection
- **Frontmatter**: Uses author for metadata population
