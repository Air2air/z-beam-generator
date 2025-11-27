# Domain Independence Policy

**Date**: November 26, 2025  
**Status**: ✅ ENFORCED

---

## 🎯 Core Principle

**Zero cross-domain contamination. Each domain must be completely independent.**

```
❌ FORBIDDEN: domains/materials importing from domains/settings
❌ FORBIDDEN: domains/settings importing from domains/materials  
❌ FORBIDDEN: domains/contaminants importing from other domains

✅ ALLOWED: All domains importing from shared/* root-level utilities
✅ ALLOWED: Domains importing standard libraries
✅ ALLOWED: Domains importing third-party packages
```

---

## 📁 Domain Structure

### Current Domains

```
domains/
├── materials/          # Material properties domain
│   ├── data_loader.py  # Loads data/materials/*.yaml
│   ├── modules/        # Material-specific modules
│   ├── research/       # Material property research
│   └── ...
│
├── settings/           # Machine settings domain  
│   ├── data_loader.py  # Loads data/settings/*.yaml
│   ├── modules/        # Settings-specific modules
│   └── ...
│
└── contaminants/       # Contamination domain
    ├── data_loader.py  # Loads data/contaminants/*.yaml
    └── ...
```

### Shared Utilities (Root Level)

```
shared/
├── config/             # Configuration utilities
├── utils/              # Common utilities
├── research/           # Research interfaces (NEW)
└── ...
```

---

## 🚫 Anti-Patterns (FORBIDDEN)

### ❌ Cross-Domain Imports
```python
# WRONG: Materials importing from settings
from domains.settings.data_loader import load_settings_yaml  # ❌ FORBIDDEN

# WRONG: Settings importing from materials  
from domains.materials.research.property_researcher import PropertyResearcher  # ❌ FORBIDDEN

# WRONG: Contaminants importing from materials
from domains.materials.materials_cache import load_materials_cached  # ❌ FORBIDDEN
```

### ❌ Shared State Between Domains
```python
# WRONG: Global cache shared between domains
_global_material_settings_cache = {}  # ❌ FORBIDDEN
```

### ❌ Domain-Specific Logic in Shared Code
```python
# WRONG: Material-specific logic in shared utilities
def shared_function():
    from domains.materials import something  # ❌ FORBIDDEN
```

---

## ✅ Correct Patterns

### ✅ Using Shared Utilities
```python
# CORRECT: Both domains use shared utilities independently
from shared.utils.yaml_loader import load_yaml_file
from shared.research.interfaces import ResearchResult
```

### ✅ Domain-Specific Implementations
```python
# materials/research/property_researcher.py
class PropertyResearcher:
    """Material property research - stays in materials domain"""
    pass

# settings/research/settings_researcher.py  
class SettingsResearcher:
    """Machine settings research - stays in settings domain"""
    pass
```

### ✅ Shared Interfaces (No Implementation)
```python
# shared/research/interfaces.py
from dataclasses import dataclass

@dataclass
class ResearchResult:
    """Shared data structure - no domain logic"""
    value: Any
    confidence: int
    source: str
```

---

## 🔄 When Domains Need to Communicate

### Option 1: Through Export Layer (Recommended)
```python
# Materials domain exports to frontmatter
materials_exporter.export()  # → frontmatter/materials/

# Settings domain reads exported frontmatter (not materials data directly)
settings_generator.load_from_frontmatter()
```

### Option 2: Through Shared Data Layer
```python
# Both domains read from their own data files
materials_data = load_materials_yaml()  # data/materials/
settings_data = load_settings_yaml()    # data/settings/

# Orchestrator combines them (outside both domains)
combined = orchestrator.merge(materials_data, settings_data)
```

### Option 3: Through Shared Interface
```python
# shared/research/research_coordinator.py
class ResearchCoordinator:
    """Coordinates research across domains WITHOUT importing them"""
    
    def research_material_and_settings(self, material_name: str):
        # Loads researchers dynamically, no direct imports
        materials_researcher = self._load_researcher('materials')
        settings_researcher = self._load_researcher('settings')
```

---

## 📋 Migration Guide

### Found Cross-Domain Import? Fix It:

**Step 1**: Identify the dependency
```python
# Found in domains/materials/foo.py
from domains.settings.bar import something  # ❌ Problem
```

**Step 2**: Determine if it's truly needed
- If YES: Extract to `shared/` as generic utility
- If NO: Remove the dependency

**Step 3**: Refactor
```python
# Option A: Move to shared
# shared/utils/common.py
def something():
    """Generic implementation - no domain logic"""
    pass

# domains/materials/foo.py
from shared.utils.common import something  # ✅ Fixed

# domains/settings/bar.py  
from shared.utils.common import something  # ✅ Both can use
```

**Step 4**: Verify independence
```bash
# Check for cross-domain imports
grep -r "from domains\." domains/materials/ | grep -v "from domains.materials"
grep -r "from domains\." domains/settings/ | grep -v "from domains.settings"
```

---

## 🧪 Testing Domain Independence

### Automated Check
```python
# tests/test_domain_independence.py

def test_materials_domain_independence():
    """Materials domain must not import from other domains"""
    violations = find_cross_domain_imports('domains/materials')
    assert len(violations) == 0, f"Found violations: {violations}"

def test_settings_domain_independence():
    """Settings domain must not import from other domains"""
    violations = find_cross_domain_imports('domains/settings')
    assert len(violations) == 0, f"Found violations: {violations}"
```

### Manual Verification
```bash
# Check materials domain
cd domains/materials
grep -r "from domains\." . | grep -v "from domains.materials"

# Check settings domain  
cd domains/settings
grep -r "from domains\." . | grep -v "from domains.settings"

# Should return NO results
```

---

## 📊 Current Status

### ✅ Domains Separated
- [x] Materials domain: `domains/materials/` + `data/materials/`
- [x] Settings domain: `domains/settings/` + `data/settings/`
- [x] Contaminants domain: `domains/contaminants/` + `data/contaminants/`

### ⚠️ Cleanup Completed (Nov 26, 2025)
- [x] Removed `SettingsModule` import from materials/modules/__init__.py
- [x] Commented out cross-domain imports in materials/research/
- [x] Created `shared/research/` for shared utilities

### 🎯 Next Steps
- [ ] Create domain independence tests
- [ ] Audit all domains for remaining cross-imports
- [ ] Document shared interface patterns
- [ ] Create migration examples for common scenarios

---

## 🔍 Exceptions (Explicitly Allowed)

### Export Layer Can Access Multiple Domains
```python
# export/core/trivial_exporter.py - ALLOWED
from domains.materials.data_loader import load_materials_yaml
from domains.settings.data_loader import load_settings_yaml

# Reason: Export layer is the integration point
```

### Orchestrators Can Access Multiple Domains  
```python
# orchestrators/content_orchestrator.py - ALLOWED
from domains.materials.coordinator import MaterialsCoordinator
from domains.settings.data_loader import get_settings_path

# Reason: Orchestrators coordinate across domains
```

### Tests Can Access Multiple Domains
```python
# tests/test_integration.py - ALLOWED
from domains.materials import load_materials_data
from domains.settings import load_settings_data

# Reason: Integration tests verify cross-domain workflows
```

---

## 💡 Key Principles

1. **Independence**: Each domain stands alone
2. **Shared Utilities**: Common code goes in `shared/`
3. **No Cross-Imports**: Domains never import from each other
4. **Integration at Edges**: Export/orchestration layer handles coordination
5. **Fail-Fast**: Tests enforce independence automatically

---

## 📚 Related Documentation

- `SETTINGS_DOMAIN_SEPARATION_COMPLETE.md` - Settings separation details
- `DATA_ARCHITECTURE_SEPARATION.md` - Data file organization
- `docs/02-architecture/` - System architecture docs

---

**Enforcement**: Automated tests + manual code review  
**Violations**: Grade F - Must be fixed immediately  
**Updated**: November 26, 2025
