# Exporter Consolidation - Visual Transformation Guide
**Quick Reference for Migrating Exporters to Base Class**

---

## 🔄 **BEFORE vs AFTER Comparison**

### **Settings Exporter Transformation**

#### **BEFORE** (Current - 308 lines)
```python
#!/usr/bin/env python3
"""
Trivial Settings Frontmatter Exporter
"""
import logging
import yaml
from pathlib import Path
from typing import Dict, Any
from collections import OrderedDict

from shared.validation.domain_associations import DomainAssociationsValidator
from shared.services.domain_linkages_service import DomainLinkagesService
from shared.validation.field_order import FrontmatterFieldOrderValidator

logger = logging.getLogger(__name__)


class TrivialSettingsExporter:
    """Copy Settings.yaml → Frontmatter YAML files."""
    
    def __init__(self):
        """Initialize with output directory."""
        # 🔴 DUPLICATE: Output directory setup
        self.output_dir = Path(__file__).resolve().parents[2] / "frontmatter" / "settings"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Load source data
        self.settings_data = self._load_settings()
        self.materials_data = self._load_materials()
        
        # 🔴 DUPLICATE: Validator initialization (repeated in 4 exporters)
        self.associations_validator = DomainAssociationsValidator()
        self.associations_validator.load()
        self.field_order_validator = FrontmatterFieldOrderValidator()
        self.field_order_validator.load_schema()
        
        # 🔴 DUPLICATE: Service initialization
        self.linkages_service = DomainLinkagesService()
        
        self.logger.info(f"✅ Loaded {len(self.settings_data.get('settings', {}))} settings profiles")
    
    def export_single(self, material_name: str, setting_data: Dict, force: bool = False) -> bool:
        """Export single setting to frontmatter."""
        filename = f"{slug}.yaml"
        output_path = self.output_dir / filename
        
        if output_path.exists() and not force:
            self.logger.info(f"⏭️ Skipping {filename} (exists)")
            return False
        
        # Build frontmatter
        frontmatter = {}
        frontmatter['id'] = slug
        frontmatter['name'] = material_name.replace('-', ' ').title()
        
        # 🔴 DUPLICATE: Timestamp generation (repeated 6 times)
        from datetime import datetime
        current_timestamp = datetime.now().isoformat()
        frontmatter['datePublished'] = setting_data.get('datePublished') or current_timestamp
        frontmatter['dateModified'] = setting_data.get('dateModified') or current_timestamp
        
        # ... more frontmatter building ...
        
        # 🔴 DUPLICATE: Field ordering (repeated 5 times)
        ordered_frontmatter = self.field_order_validator.reorder_fields(frontmatter, 'settings')
        
        # 🔴 DUPLICATE: YAML writing (repeated 4 times)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(dict(ordered_frontmatter), f, default_flow_style=False, 
                     allow_unicode=True, sort_keys=False, width=1000)
        
        self.logger.info(f"✅ Exported: {filename}")
        return True
```

**Lines**: 308  
**Duplicates**: Validator init (15 lines), timestamp (4 lines), field ordering (1 line), YAML writing (4 lines)  
**Total Duplication**: ~25 lines

---

#### **AFTER** (Refactored - 248 lines, -60 lines)
```python
#!/usr/bin/env python3
"""
Trivial Settings Frontmatter Exporter
"""
import logging
import yaml
from pathlib import Path
from typing import Dict, Any

# ✅ NEW: Import base class
from export.core.base_trivial_exporter import BaseTrivialExporter

logger = logging.getLogger(__name__)


# ✅ NEW: Inherit from base
class TrivialSettingsExporter(BaseTrivialExporter):
    """Copy Settings.yaml → Frontmatter YAML files."""
    
    def __init__(self):
        """Initialize with base validators and domain-specific data."""
        # ✅ REPLACED: Single line replaces 15 lines of validator init
        super().__init__(
            domain_name='settings',
            output_subdir='settings'
        )
        
        # Domain-specific loading only
        self.settings_data = self._load_settings()
        self.materials_data = self._load_materials()
        
        self.logger.info(f"✅ Loaded {len(self.settings_data.get('settings', {}))} settings profiles")
    
    def export_single(self, material_name: str, setting_data: Dict, force: bool = False) -> bool:
        """Export single setting to frontmatter."""
        filename = f"{slug}.yaml"
        output_path = self.output_dir / filename
        
        if output_path.exists() and not force:
            self.logger.info(f"⏭️ Skipping {filename} (exists)")
            return False
        
        # Build frontmatter
        frontmatter = {}
        frontmatter['id'] = slug
        frontmatter['name'] = material_name.replace('-', ' ').title()
        
        # ✅ REPLACED: Use base class method (4 lines → 3 lines)
        timestamp = self.generate_timestamp()
        frontmatter['datePublished'] = setting_data.get('datePublished') or timestamp
        frontmatter['dateModified'] = setting_data.get('dateModified') or timestamp
        
        # ... more frontmatter building ...
        
        # ✅ REPLACED: Use base class method (6 lines → 1 line)
        self.write_frontmatter_yaml(frontmatter, filename, apply_ordering=True)
        return True
```

**Lines**: 248 (-60 lines)  
**Duplicates Removed**: All  
**Benefits**: 
- ✅ Validators initialized in base (15 lines saved)
- ✅ Timestamp utility (4 lines → 3 lines)
- ✅ YAML writing utility (6 lines → 1 line)
- ✅ Field ordering automatic (via write_frontmatter_yaml)

---

## 📊 **Code Reduction Summary**

| Exporter | Current Lines | After Refactor | Lines Saved | Effort |
|----------|---------------|----------------|-------------|--------|
| **Compounds** | 180 | 130 | **-50** | 30 min |
| **Contaminants** | 350 | 290 | **-60** | 45 min |
| **Settings** | 308 | 248 | **-60** | 45 min |
| **Materials** | 2100 | 2020 | **-80** | 1.5 hours |
| **Base Class** | 0 | 220 | **+220** | Already created ✅ |
| **TOTAL** | **2938** | **2908** | **-30 net** | **3-4 hours** |

---

## 🎯 **Key Patterns Consolidated**

### **1. Validator Initialization** (4 exporters)
```python
# ❌ BEFORE (15 lines per exporter = 60 total lines)
self.associations_validator = DomainAssociationsValidator()
self.associations_validator.load()
self.field_order_validator = FrontmatterFieldOrderValidator()
self.field_order_validator.load_schema()
self.linkages_service = DomainLinkagesService()

# ✅ AFTER (1 line per exporter = 4 lines, base handles rest)
super().__init__(domain_name='materials', output_subdir='materials')
```
**Savings**: 56 lines across 4 exporters

---

### **2. Timestamp Generation** (6 occurrences)
```python
# ❌ BEFORE (4 lines × 6 occurrences = 24 lines)
from datetime import datetime
current_timestamp = datetime.now().isoformat()
frontmatter['datePublished'] = data.get('datePublished') or current_timestamp
frontmatter['dateModified'] = data.get('dateModified') or current_timestamp

# ✅ AFTER (3 lines × 6 occurrences = 18 lines)
timestamp = self.generate_timestamp()
frontmatter['datePublished'] = data.get('datePublished') or timestamp
frontmatter['dateModified'] = data.get('dateModified') or timestamp
```
**Savings**: 6 lines across 6 occurrences

---

### **3. Field Ordering + YAML Writing** (5 occurrences)
```python
# ❌ BEFORE (6 lines × 5 occurrences = 30 lines)
ordered_frontmatter = self.field_order_validator.reorder_fields(frontmatter, 'domain')

output_path = self.output_dir / filename
with open(output_path, 'w', encoding='utf-8') as f:
    yaml.dump(dict(ordered_frontmatter), f, default_flow_style=False,
             allow_unicode=True, sort_keys=False, width=1000)

# ✅ AFTER (1 line × 5 occurrences = 5 lines)
self.write_frontmatter_yaml(frontmatter, filename)
```
**Savings**: 25 lines across 5 occurrences

---

## 🔧 **Migration Steps per Exporter**

### **Step 1: Update Imports**
```python
# Add this import:
from export.core.base_trivial_exporter import BaseTrivialExporter

# Remove these (now in base):
# from shared.validation.domain_associations import DomainAssociationsValidator
# from shared.services.domain_linkages_service import DomainLinkagesService
# from shared.validation.field_order import FrontmatterFieldOrderValidator
```

### **Step 2: Update Class Declaration**
```python
# Change from:
class TrivialSettingsExporter:

# To:
class TrivialSettingsExporter(BaseTrivialExporter):
```

### **Step 3: Simplify __init__()**
```python
# Replace 15 lines of validator init with:
super().__init__(
    domain_name='settings',
    output_subdir='settings'
)

# Keep domain-specific loading:
self.settings_data = self._load_settings()
self.materials_data = self._load_materials()
```

### **Step 4: Replace Timestamp Generation**
```python
# Replace:
from datetime import datetime
current_timestamp = datetime.now().isoformat()

# With:
timestamp = self.generate_timestamp()
```

### **Step 5: Replace YAML Writing**
```python
# Replace all of this:
ordered_frontmatter = self.field_order_validator.reorder_fields(frontmatter, 'domain')
output_path = self.output_dir / filename
with open(output_path, 'w', encoding='utf-8') as f:
    yaml.dump(dict(ordered_frontmatter), f, ...)

# With this:
self.write_frontmatter_yaml(frontmatter, filename)
```

### **Step 6: Test**
```bash
# Run exporter
python3 -m export.settings.trivial_exporter

# Compare output (should be byte-identical)
diff -r frontmatter/settings/ /tmp/settings_backup/
```

---

## 🚦 **Rollout Order** (Easiest → Hardest)

### **1. Compounds** ⭐ START HERE
- **Why First**: Simplest exporter, easiest to validate
- **Complexity**: LOW (180 lines, minimal logic)
- **Time**: 30 minutes
- **Risk**: VERY LOW
- **Validation**: 20 compound files should be byte-identical

### **2. Contaminants** 
- **Why Second**: Medium complexity, validates pattern
- **Complexity**: MEDIUM (350 lines, pattern matching)
- **Time**: 45 minutes
- **Risk**: LOW
- **Validation**: 98 contamination patterns should be byte-identical

### **3. Settings**
- **Why Third**: Multi-data-source pattern
- **Complexity**: MEDIUM (308 lines, Materials.yaml lookup)
- **Time**: 45 minutes
- **Risk**: LOW
- **Validation**: 169 settings files should be byte-identical

### **4. Materials** 
- **Why Last**: Most complex, dual-page export
- **Complexity**: HIGH (2100 lines, materials + settings pages)
- **Time**: 1.5 hours
- **Risk**: MEDIUM (large exporter, multiple export methods)
- **Validation**: 153 materials + 153 settings pages should be byte-identical

---

## ✅ **Validation Checklist per Exporter**

**Before Migration**:
- [ ] Backup current frontmatter files: `cp -r frontmatter/{domain}/ /tmp/{domain}_backup/`
- [ ] Note current line count: `wc -l export/{domain}/trivial_exporter.py`
- [ ] Run current exporter: `python3 -m export.{domain}.trivial_exporter`

**During Migration**:
- [ ] Update imports (add base, remove duplicates)
- [ ] Update class declaration (inherit base)
- [ ] Simplify `__init__()` (call super, keep domain loading)
- [ ] Replace timestamp generation (use `self.generate_timestamp()`)
- [ ] Replace YAML writing (use `self.write_frontmatter_yaml()`)
- [ ] Remove duplicate methods (`_strip_generation_metadata` if identical to base)

**After Migration**:
- [ ] Run migrated exporter: `python3 -m export.{domain}.trivial_exporter`
- [ ] Compare output: `diff -r frontmatter/{domain}/ /tmp/{domain}_backup/`
- [ ] Verify byte-identical (no differences)
- [ ] Check line count reduction: `wc -l export/{domain}/trivial_exporter.py`
- [ ] Commit changes: `git commit -m "Migrate {domain} exporter to base class (-X lines)"`

---

## 🎯 **Expected Results**

After completing all 4 migrations:

**Code Metrics**:
- ✅ **-250 lines removed** (duplicated code)
- ✅ **+220 lines added** (base class)
- ✅ **-30 net lines** (overall reduction)
- ✅ **6 duplicate patterns eliminated**

**Quality Metrics**:
- ✅ **Single source of truth** for shared logic
- ✅ **DRY principle applied** (Don't Repeat Yourself)
- ✅ **Easier to maintain** (fix once, applies to all)
- ✅ **Easier to extend** (new domain = 2 methods vs 200+ lines)

**Validation Metrics**:
- ✅ **440 files exported** (same as before)
- ✅ **Byte-identical output** (no functional changes)
- ✅ **Zero regressions** (all tests pass)
- ✅ **100% compliance maintained** (FRONTMATTER_GENERATION_GUIDE_V2.md)

---

**Ready to start with Compounds exporter?** It's the easiest and validates the pattern works!
