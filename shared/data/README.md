# Shared Data Loaders

`shared/data/` is a loader package. Canonical YAML lives under `data/`, not here.

## Structure

```
shared/data/
├── base_loader.py              # Abstract loader base class
├── loader_factory.py           # Generic factory + backward-compatible aliases
└── specialized/
    ├── author_loader.py        # Author/persona loading
    └── safety_loader.py        # Safety data loading
```

## Canonical Data Ownership

- Canonical domain YAML: `data/<domain>/`
- Canonical authors YAML: `data/authors/Authors.yaml`
- Canonical schemas: `data/schemas/` and `schemas/`

`shared/data/` should not contain mirrored domain datasets. It exists to provide shared loader code for canonical data stored under `data/`.

## Usage

### Generic Loader Factory

```python
from shared.data.loader_factory import create_data_loader

loader = create_data_loader("materials")
materials = loader.load_materials()
```

### Specialized Loaders

```python
from shared.data.specialized.author_loader import AuthorLoader
from shared.data.specialized.safety_loader import SafetyLoader
```

### Domain-Specific Loaders

```python
from domains.materials.loaders.data_loader_v2 import MaterialsDataLoader
from domains.contaminants.loaders.data_loader_v2 import ContaminantsDataLoader
```

## Notes

- `base_loader.py` is active; it is not a legacy file.
- `loader_factory.py` is the shared loader entry point.
- If a domain needs a compatibility copy, document the reason explicitly; do not create silent mirrors under `shared/data/`.
