# YAML Loading Migration Pattern
**Date**: December 11, 2025  
**Purpose**: Guide for migrating direct YAML loading to BaseDataLoader pattern

---

## 🎯 Quick Reference

**Old Pattern** (❌ Don't do this):
```python
import yaml
from pathlib import Path

file_path = Path(__file__).parent.parent / 'data' / 'Materials.yaml'
with open(file_path, 'r') as f:
    data = yaml.safe_load(f)
```

**New Pattern** (✅ Do this instead):
```python
from shared.data.unified_loader import get_materials_loader

loader = get_materials_loader()
data = loader.load_materials()
```

---

## 📋 Migration Steps

### Step 1: Identify Current Pattern

Look for these anti-patterns:
```python
❌ yaml.safe_load()
❌ yaml.load()
❌ Path(__file__).parent.parent.parent...
❌ open(file_path, 'r') as f:
❌ @lru_cache on YAML loading functions
```

### Step 2: Determine Data Source

| File Being Loaded | Use This Loader |
|-------------------|-----------------|
| Materials.yaml | `get_materials_loader()` |
| MaterialProperties.yaml | `get_materials_loader()` |
| Contaminants.yaml | `get_contaminants_loader()` |
| Settings.yaml | `get_settings_loader()` |

### Step 3: Replace with Unified Loader

**Before**:
```python
def load_materials():
    materials_file = Path(__file__).resolve().parents[3] / "data" / "materials" / "Materials.yaml"
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data.get('materials', {})
```

**After**:
```python
def load_materials():
    from shared.data.unified_loader import get_materials_loader
    loader = get_materials_loader()
    data = loader.load_materials()
    return data.get('materials', {})
```

**Even Better** (one-liner):
```python
def load_materials():
    return get_materials_loader().load_materials().get('materials', {})
```

### Step 4: Remove Imports

**Remove**:
```python
import yaml  # ← Remove if only used for data loading
from pathlib import Path  # ← Remove if only used for data file paths
from functools import lru_cache  # ← Remove if only used for data caching
```

**Add**:
```python
from shared.data.unified_loader import get_materials_loader, get_contaminants_loader, get_settings_loader
```

---

## 📚 Complete Examples

### Example 1: Loading Materials

**Before (25 lines)**:
```python
import yaml
from pathlib import Path
from functools import lru_cache

PROJECT_ROOT = Path(__file__).parent.parent.parent
MATERIALS_FILE = PROJECT_ROOT / "data" / "materials" / "Materials.yaml"

@lru_cache(maxsize=1)
def load_materials_yaml():
    """Load Materials.yaml"""
    if not MATERIALS_FILE.exists():
        raise FileNotFoundError(f"Materials.yaml not found at {MATERIALS_FILE}")
    
    try:
        with open(MATERIALS_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in Materials.yaml: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load Materials.yaml: {e}")

def get_all_materials():
    data = load_materials_yaml()
    return data.get('materials', {})
```

**After (4 lines)**:
```python
from shared.data.unified_loader import get_materials_loader

def get_all_materials():
    loader = get_materials_loader()
    data = loader.load_materials()
    return data.get('materials', {})
```

**Reduction**: 21 lines eliminated (84% reduction)

---

### Example 2: Loading Contaminants

**Before (30 lines)**:
```python
import yaml
from pathlib import Path
import threading

class PatternLoader:
    _cache = {}
    _lock = threading.Lock()
    
    def __init__(self):
        self.contaminants_file = Path(__file__).resolve().parents[3] / "data" / "contaminants" / "Contaminants.yaml"
    
    def _load_file(self):
        cache_key = str(self.contaminants_file)
        
        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        with open(self.contaminants_file, 'r') as f:
            data = yaml.safe_load(f)
        
        with self._lock:
            self._cache[cache_key] = data
        
        return data
    
    def get_pattern(self, pattern_id):
        data = self._load_file()
        patterns = data.get('contamination_patterns', {})
        return patterns.get(pattern_id)
```

**After (8 lines)**:
```python
from shared.data.unified_loader import get_contaminants_loader

class PatternLoader:
    def __init__(self):
        self.loader = get_contaminants_loader()
    
    def get_pattern(self, pattern_id):
        return self.loader.get_pattern(pattern_id)
```

**Reduction**: 22 lines eliminated (73% reduction)

---

### Example 3: Loading Settings

**Before (20 lines)**:
```python
import yaml
from pathlib import Path

def load_settings_for_material(material_name):
    settings_file = Path(__file__).resolve().parents[3] / "data" / "settings" / "Settings.yaml"
    
    if not settings_file.exists():
        print(f"Settings.yaml not found at {settings_file}")
        return {}
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"Failed to load Settings.yaml: {e}")
        return {}
    
    settings = data.get('settings', {})
    return settings.get(material_name, {}).get('machine_settings', {})
```

**After (5 lines)**:
```python
from shared.data.unified_loader import get_settings_loader

def load_settings_for_material(material_name):
    loader = get_settings_loader()
    return loader.get_material_settings(material_name)
```

**Reduction**: 15 lines eliminated (75% reduction)

---

## 🔧 Advanced Patterns

### Pattern 1: Multiple Data Sources in One Class

**Before**:
```python
class DataManager:
    def __init__(self):
        self.materials = self._load_materials()
        self.contaminants = self._load_contaminants()
        self.settings = self._load_settings()
    
    def _load_materials(self):
        # 20 lines of YAML loading...
        pass
    
    def _load_contaminants(self):
        # 20 lines of YAML loading...
        pass
    
    def _load_settings(self):
        # 20 lines of YAML loading...
        pass
```

**After**:
```python
from shared.data.unified_loader import get_data_loader

class DataManager:
    def __init__(self):
        self.materials_loader = get_data_loader('materials')
        self.contaminants_loader = get_data_loader('contaminants')
        self.settings_loader = get_data_loader('settings')
    
    @property
    def materials(self):
        return self.materials_loader.load_materials()
    
    @property
    def contaminants(self):
        return self.contaminants_loader.load_patterns()
    
    @property
    def settings(self):
        return self.settings_loader.load_settings()
```

### Pattern 2: Conditional Loading

**Before**:
```python
def get_material_data(material_name, include_properties=False):
    materials_file = PROJECT_ROOT / "data" / "materials" / "Materials.yaml"
    with open(materials_file, 'r') as f:
        materials_data = yaml.safe_load(f)
    
    if include_properties:
        properties_file = PROJECT_ROOT / "data" / "materials" / "MaterialProperties.yaml"
        with open(properties_file, 'r') as f:
            properties_data = yaml.safe_load(f)
        return materials_data, properties_data
    
    return materials_data
```

**After**:
```python
def get_material_data(material_name, include_properties=False):
    loader = get_materials_loader()
    materials_data = loader.load_materials()
    
    if include_properties:
        properties_data = loader.load_properties()
        return materials_data, properties_data
    
    return materials_data
```

---

## ✅ Benefits of Migration

| Aspect | Before | After |
|--------|--------|-------|
| **Lines of code** | 20-30 per loader | 4-8 per loader |
| **Caching** | Manual (@lru_cache) | Automatic (CacheManager) |
| **Thread safety** | Manual locks | Built-in |
| **Error handling** | Inconsistent | Standardized |
| **Path resolution** | Manual (.parent.parent...) | Automatic |
| **Testing** | Mock file I/O | Mock loader (easier) |
| **Maintenance** | Duplicate code | Single implementation |

---

## 📊 Impact Metrics

Based on actual migrations (Phases 1-4):

| Metric | Average Reduction |
|--------|-------------------|
| Lines per file | 70-80% |
| YAML loading code | 100% |
| Path resolution code | 100% |
| Cache management code | 100% |
| Error handling code | 80% |

**Example**: trivial_exporter.py
- Before: 4 YAML loading functions × 15 lines = 60 lines
- After: 4 loader calls × 2 lines = 8 lines
- **Reduction**: 52 lines (87%)

---

## 🚀 Quick Migration Checklist

Before submitting PR with YAML loading migration:

- [ ] All `yaml.safe_load()` replaced with loader calls
- [ ] All `Path(__file__).parent.parent...` removed
- [ ] All `@lru_cache` on data loading removed
- [ ] Imports updated (removed yaml, added unified_loader)
- [ ] Tests still pass (zero regressions)
- [ ] No hardcoded file paths remain
- [ ] Error handling preserved (loader handles it)

---

## 📝 Common Questions

**Q: What if I need a file not yet supported by loaders?**  
A: Add the method to the appropriate loader. Example: Add `load_micros()` to MaterialsDataLoader.

**Q: What if I need custom error handling?**  
A: Wrap the loader call:
```python
try:
    data = loader.load_materials()
except ConfigurationError:
    # Custom handling
    pass
```

**Q: What about performance?**  
A: Loaders use CacheManager - first load caches result, subsequent calls are instant.

**Q: Can I still use the old API during migration?**  
A: Yes! Old loaders (data_loader.py) still work. v2 loaders are additive, not breaking.

---

**Status**: ✅ Pattern documented and tested  
**Next**: Apply pattern to export/ and generation/ directories
