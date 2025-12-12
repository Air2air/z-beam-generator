# Phase 5: Directory Migration Guide
**Date**: December 11, 2025  
**Status**: 🔄 IN PROGRESS  
**Approach**: Strategic migration with examples

---

## 🎯 Objective

Migrate remaining YAML loading patterns in export/ and generation/ directories to use BaseDataLoader architecture.

---

## 📊 Audit Results

### Export Directory
```bash
grep -r "yaml.safe_load" --include="*.py" export/ | grep -v "test_" | wc -l
```
**Result**: **11 instances** found in:
- `export/core/trivial_exporter.py` (4 instances) - Micros, FAQs, Settings, RegulatoryStandards
- `export/core/streamlined_generator.py` (4 instances) - Categories, voice profiles
- `export/core/validation_helpers.py` (1 instance) - Frontmatter parsing
- `export/core/base_generator.py` (1 instance) - Materials data
- `export/enhancement/property_enhancement_service.py` (1 instance) - Materials config

**Path Resolution**: 6 instances of `Path(__file__).parent.parent...`

### Generation Directory
```bash
grep -r "yaml.safe_load" --include="*.py" generation/ | grep -v "test_" | wc -l
```
**Result**: **20 instances** found

---

## 🎯 Strategic Approach

Rather than migrating every individual YAML load, we'll demonstrate the pattern and create reusable data access utilities.

### Phase 5A: Create Centralized Data Access (✅ RECOMMENDED)

**Create**: `shared/data/unified_loader.py`

This provides a single point of access for ALL data files:
- Materials.yaml → MaterialsDataLoader
- Contaminants.yaml → ContaminantsDataLoader  
- Settings.yaml → SettingsDataLoader
- Micros.yaml, FAQs.yaml, etc. → ContentDataLoader (new)
- Categories.yaml → CategoryDataLoader (new)

**Benefits**:
- Single import for all data access
- Consistent caching across all code
- Zero duplicate YAML loading
- Easy to swap implementations

---

## 📋 Migration Pattern Example

### Before (Direct YAML Loading)
```python
# export/core/trivial_exporter.py
def _load_micros(self) -> Dict[str, Any]:
    captions_file = Path(__file__).resolve().parents[3] / "materials" / "data" / "content" / "Micros.yaml"
    if not captions_file.exists():
        self.logger.warning(f"Micros.yaml not found at {captions_file}")
        return {}
    
    with open(captions_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    return data.get('micros', {})
```

**Problems**:
- ❌ Direct file path resolution (fragile)
- ❌ Duplicate YAML loading code
- ❌ No caching (reads file every time)
- ❌ Manual error handling
- ❌ Inconsistent with other loaders

### After (BaseDataLoader Migration)
```python
# Approach 1: Use domain-specific loader
from domains.materials.data_loader_v2 import MaterialsDataLoader

def _load_micros(self) -> Dict[str, Any]:
    loader = MaterialsDataLoader()
    return loader.load_micros()  # Cached, validated, consistent
```

```python
# Approach 2: Use unified data access (RECOMMENDED)
from shared.data.unified_loader import get_data_loader

def _load_micros(self) -> Dict[str, Any]:
    loader = get_data_loader('materials')
    return loader.load_micros()
```

**Benefits**:
- ✅ Automatic caching (CacheManager)
- ✅ Thread-safe operations
- ✅ Consistent error handling
- ✅ No path resolution needed
- ✅ Single line of code

---

## 🔧 Implementation Strategy

### Option A: Gradual File-by-File Migration (Time: 40-50 hours)
**Pros**: Thorough, complete coverage  
**Cons**: Time-intensive, many small changes

**Steps**:
1. Migrate export/core/trivial_exporter.py (4 instances)
2. Migrate export/core/streamlined_generator.py (4 instances)
3. Migrate export/core/base_generator.py (1 instance)
4. Migrate export/enhancement/property_enhancement_service.py (1 instance)
5. Migrate generation/ directory (20 instances)
6. Test each file individually

### Option B: Create Unified Loader + Selective Migration (Time: 8-12 hours) ⭐ **RECOMMENDED**
**Pros**: High ROI, reusable pattern, demonstrates approach  
**Cons**: Not every file migrated immediately

**Steps**:
1. ✅ Create `shared/data/unified_loader.py` (central data access)
2. ✅ Extend MaterialsDataLoader with content methods (Micros, FAQs, etc.)
3. ✅ Migrate 2-3 high-impact files as examples
4. ✅ Document pattern for future migrations
5. ✅ Provide migration guide for remaining files

---

## 🚀 Phase 5B Implementation Plan

### Step 1: Extend MaterialsDataLoader (1 hour)

Add content loading methods to `domains/materials/data_loader_v2.py`:

```python
def load_micros(self) -> Dict[str, Any]:
    """Load Micros.yaml (material captions)"""
    cached = cache_manager.get('materials', 'micros')
    if cached:
        return cached
    
    micros_file = self.project_root / 'materials' / 'data' / 'content' / 'Micros.yaml'
    data = read_yaml_file(micros_file)
    micros = data.get('micros', {})
    
    cache_manager.set('materials', 'micros', micros, ttl=3600)
    return micros

def load_faqs(self) -> Dict[str, Any]:
    """Load FAQs.yaml"""
    # Similar pattern

def load_regulatory_standards(self) -> Dict[str, Any]:
    """Load RegulatoryStandards.yaml"""
    # Similar pattern
```

### Step 2: Create Unified Loader (2 hours)

`shared/data/unified_loader.py`:

```python
"""
Unified Data Loader

Single point of access for all data files across all domains.

Usage:
    from shared.data.unified_loader import get_data_loader
    
    # Get domain-specific loader
    materials_loader = get_data_loader('materials')
    contaminants_loader = get_data_loader('contaminants')
    settings_loader = get_data_loader('settings')
    
    # Load data
    materials = materials_loader.load_materials()
    patterns = contaminants_loader.load_patterns()
    settings = settings_loader.load_settings()
"""

from typing import Union, Literal
from domains.materials.data_loader_v2 import MaterialsDataLoader
from domains.contaminants.data_loader_v2 import ContaminantsDataLoader
from domains.settings.data_loader_v2 import SettingsDataLoader

DataLoaderType = Union[MaterialsDataLoader, ContaminantsDataLoader, SettingsDataLoader]
DomainName = Literal['materials', 'contaminants', 'settings']

# Singleton instances
_loaders = {}

def get_data_loader(domain: DomainName) -> DataLoaderType:
    """
    Get data loader for specified domain.
    
    Args:
        domain: Domain name ('materials', 'contaminants', 'settings')
    
    Returns:
        Domain-specific data loader instance (cached)
    
    Example:
        >>> loader = get_data_loader('materials')
        >>> materials = loader.load_materials()
    """
    if domain not in _loaders:
        if domain == 'materials':
            _loaders[domain] = MaterialsDataLoader()
        elif domain == 'contaminants':
            _loaders[domain] = ContaminantsDataLoader()
        elif domain == 'settings':
            _loaders[domain] = SettingsDataLoader()
        else:
            raise ValueError(f"Unknown domain: {domain}")
    
    return _loaders[domain]
```

### Step 3: Migrate High-Impact Files (3-4 hours)

**File 1**: `export/core/trivial_exporter.py`
- Migrate _load_micros() → use loader.load_micros()
- Migrate _load_faqs() → use loader.load_faqs()
- Migrate _load_settings() → use loader.load_settings()
- Migrate _load_regulatory_standards() → use loader.load_regulatory_standards()

**File 2**: `export/core/streamlined_generator.py`
- Migrate categories loading
- Migrate voice profile loading

**File 3**: `generation/config/dynamic_config.py`
- Migrate config loading

### Step 4: Testing (2 hours)

- Run export tests: `pytest tests/export/`
- Run generation tests: `pytest tests/generation/`
- Run full test suite: `pytest tests/`
- Verify zero regressions

### Step 5: Documentation (1 hour)

- Update migration guide
- Document unified loader usage
- Provide examples for remaining files

---

## 📈 Expected Impact

### Immediate (Option B - Recommended)
- **Time**: 8-12 hours
- **Files migrated**: 3-5 key files
- **YAML calls eliminated**: 10-15 instances
- **Lines eliminated**: ~150-200 lines
- **Infrastructure created**: Unified loader (reusable)

### Complete (Option A)
- **Time**: 40-50 hours
- **Files migrated**: All files
- **YAML calls eliminated**: 31 instances
- **Lines eliminated**: ~400-500 lines
- **Benefit**: 100% consolidation

---

## 🎯 Recommendation

**Proceed with Option B (Unified Loader + Selective Migration)**

**Rationale**:
1. Creates reusable infrastructure (unified_loader.py)
2. Demonstrates pattern clearly
3. High ROI for time invested (10-15 instances in 8-12 hours)
4. Provides clear migration path for remaining files
5. Can be completed incrementally

**Next Steps**:
1. Create unified_loader.py
2. Extend MaterialsDataLoader with content methods
3. Migrate trivial_exporter.py as example
4. Document pattern
5. Mark remaining files for future migration

---

## 📋 Files Requiring Future Migration

### Export Directory (Remaining)
- `export/core/streamlined_generator.py` (3 instances)
- `export/core/validation_helpers.py` (1 instance)
- `export/core/base_generator.py` (1 instance)
- `export/enhancement/property_enhancement_service.py` (1 instance)

### Generation Directory
- `generation/config/dynamic_config.py` (estimated 5-8 instances)
- `generation/core/*.py` (estimated 8-10 instances)
- `generation/utils/*.py` (estimated 2-4 instances)

**Migration Guide**: See `docs/08-development/YAML_LOADING_MIGRATION_PATTERN.md`

---

**Status**: 📋 Ready for implementation  
**Decision Required**: Approve Option A (complete) or Option B (strategic)?
