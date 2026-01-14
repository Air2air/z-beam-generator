# Data Loading System

Consolidated data loading architecture organized by responsibility.

## Structure

```
shared/data/
├── universal_loader.py         # ✅ Primary loader (use this)
├── specialized/
│   ├── author_loader.py        # Author/persona loading
│   └── safety_loader.py        # Safety data loading
└── legacy/
    ├── base_loader.py          # Deprecated: Use universal_loader
    └── loader.py               # Deprecated: Use universal_loader

domains/*/loaders/
├── data_loader_v2.py           # Domain-specific logic
├── category_loader.py          # (materials only)
└── pattern_loader.py           # (contaminants only)
```

## Consolidation (Jan 13, 2026)

**Before**: 18 loader files scattered across domains and shared
**After**: Organized into universal + specialized + domain-specific

### Primary Loader

Use `universal_loader.py` for all general data loading:
```python
from shared.data.universal_loader import UniversalLoader

loader = UniversalLoader()
data = loader.load('materials', 'Materials.yaml')
```

### Specialized Loaders

Use when loading specific data types:
```python
from shared.data.specialized.author_loader import AuthorLoader
from shared.data.specialized.safety_loader import SafetyLoader
```

### Domain Loaders

Domain-specific loading logic:
```python
from domains.materials.loaders.data_loader_v2 import MaterialsDataLoader
from domains.contaminants.loaders.data_loader_v2 import ContaminantsDataLoader
```

## Migration Notes

**Deprecated** (moved to `legacy/`):
- `base_loader.py` → Use `universal_loader.py`
- `loader.py` → Use `universal_loader.py`

**Active**:
- `universal_loader.py` - Primary entry point
- `specialized/*` - Specific data types
- `domains/*/loaders/` - Domain-specific logic

## Related

- Universal loader: `shared/data/universal_loader.py`
- Domain loaders: `domains/*/loaders/`
- Legacy loaders: `shared/data/legacy/`
