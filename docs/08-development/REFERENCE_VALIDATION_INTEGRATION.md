# Reference Validation Integration Guide

**How to add reference validation to any generator**

## ✅ What's Now Available

### 1. **ReferenceRegistry** - Central ID Index
- Loads all valid IDs from all domains (materials, contaminants, compounds, settings)
- Fast lookup: `registry.is_valid('contaminants', 'rust-contamination')`
- Provides fix suggestions for broken references
- Auto-loads on first use, can be reloaded anytime

### 2. **ReferenceValidatorMixin** - Generator Integration
- Add validation to any generator class with one line
- Auto-fix broken references (add suffixes, fuzzy match)
- Remove invalid references automatically
- Track statistics (checked, valid, fixed, removed)

### 3. **ValidationSchema** - Validation Rules
- Central definition of all relationship field mappings
- Suffix rules (e.g., contaminants need `-contamination`)
- Bidirectional relationship tracking
- Required/optional field definitions

### 4. **Repair Scripts** - Standalone Tools
- `repair_contaminant_suffixes.py` - Fix missing suffixes
- `repair_broken_links.py` - General link repair tool
- Both support `--dry-run` mode
- Create backups before modifying files

---

## 🚀 Quick Start: Add to Existing Generator

### Step 1: Import the Mixin

```python
from shared.validation import ReferenceValidatorMixin, ValidationSchema
```

### Step 2: Inherit from Mixin

```python
class YourGenerator(ReferenceValidatorMixin):
    def __init__(self):
        # Initialize validator (must be first)
        self.init_validator(auto_load=True)
        
        # Enable auto-fix (optional)
        self.enable_auto_fix(True)
        
        # Your existing init code...
```

### Step 3: Validate Before Saving

```python
def generate(self, item_id):
    # Your generation code...
    item_data = {...}
    
    # Validate relationships before saving
    if 'relationships' in item_data:
        item_data['relationships'] = self.validate_relationship_dict(
            item_data['relationships'],
            field_to_domain=ValidationSchema.FIELD_TO_DOMAIN,
            auto_fix=True  # Auto-fix broken references
        )
    
    # Save item_data...
    return item_data
```

That's it! Your generator now validates all references automatically.

---

## 📋 Complete Example: Materials Generator

```python
from pathlib import Path
from typing import Dict
import yaml
from shared.validation import ReferenceValidatorMixin, ValidationSchema

class MaterialsGenerator(ReferenceValidatorMixin):
    """Materials generator with integrated validation"""
    
    def __init__(self, project_root: Path = None):
        # MUST initialize validator first
        self.init_validator(project_root=project_root, auto_load=True)
        
        # Configure validation behavior
        self.enable_auto_fix(True)  # Auto-fix broken references
        self.enable_validation(True)  # Enable validation
        
        self.project_root = project_root or Path.cwd()
    
    def generate_material(self, material_id: str) -> Dict:
        """Generate material with validated references"""
        
        # Load existing data
        material_data = self._load_material(material_id)
        
        # Validate relationships
        if 'relationships' in material_data:
            print(f"🔍 Validating relationships for {material_id}...")
            
            # This will:
            # - Check all contaminant IDs exist
            # - Auto-add '-contamination' suffix if missing
            # - Remove references that can't be fixed
            # - Log all fixes
            material_data['relationships'] = self.validate_relationship_dict(
                material_data['relationships'],
                field_to_domain=ValidationSchema.FIELD_TO_DOMAIN,
                auto_fix=True
            )
            
            # Show what was done
            stats = self.get_validation_stats()
            if stats['fixed'] > 0 or stats['removed'] > 0:
                print(f"   ✅ Fixed: {stats['fixed']}, Removed: {stats['removed']}")
        
        # Save validated data
        self._save_material(material_id, material_data)
        
        return material_data
    
    def _load_material(self, material_id: str) -> Dict:
        """Load material from Materials.yaml"""
        path = self.project_root / 'data/materials/Materials.yaml'
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return data['materials'][material_id]
    
    def _save_material(self, material_id: str, material_data: Dict):
        """Save material back to Materials.yaml"""
        path = self.project_root / 'data/materials/Materials.yaml'
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        data['materials'][material_id] = material_data
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, 
                     allow_unicode=True, sort_keys=False, width=1000)
```

---

## 🎯 Example: Frontmatter Exporter

```python
from shared.validation import ReferenceValidatorMixin, ValidationSchema

class FrontmatterExporter(ReferenceValidatorMixin):
    """Exporter with validation"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.init_validator(auto_load=True)
        self.enable_auto_fix(True)
    
    def export_all(self):
        """Export all items with validation"""
        items = self._load_domain_data()
        
        for item_id, item_data in items.items():
            # Validate before export
            if 'relationships' in item_data:
                item_data['relationships'] = self.validate_relationship_dict(
                    item_data['relationships'],
                    field_to_domain=ValidationSchema.FIELD_TO_DOMAIN,
                    auto_fix=True
                )
            
            # Export validated data
            self._export_item(item_id, item_data)
```

---

## 🔧 Advanced Usage

### Manual Validation

```python
# Validate single reference
info = self.validate_reference('contaminants', 'rust')
if not info.exists and info.suggestions:
    print(f"Did you mean: {info.suggestions[0]}?")

# Validate list of IDs
valid_ids, invalid_info = self.validate_and_fix_references(
    'contaminants',
    ['rust', 'rust-contamination', 'nonexistent'],
    auto_fix=True,
    remove_invalid=True
)
```

### Custom Logging

```python
class MyGenerator(ReferenceValidatorMixin):
    def _log_fix(self, domain, old_id, new_id):
        """Custom logging for fixes"""
        logger.info(f"Fixed {domain}: {old_id} → {new_id}")
    
    def _log_removal(self, domain, ref_id, suggestions):
        """Custom logging for removals"""
        logger.warning(f"Removed invalid {domain}: {ref_id}")
```

### Statistics

```python
# Get validation stats
stats = self.get_validation_stats()
print(f"Checked: {stats['checked']}")
print(f"Valid: {stats['valid']}")
print(f"Fixed: {stats['fixed']}")
print(f"Removed: {stats['removed']}")

# Reset for next operation
self.reset_validation_stats()
```

### Reload Registry

```python
# If data files change during runtime
self.reload_registry()
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│ Generator (Your Code)                                │
│  - Inherits ReferenceValidatorMixin                  │
│  - Calls validate_relationship_dict()                │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│ ReferenceValidatorMixin                              │
│  - validate_reference()                              │
│  - validate_and_fix_references()                     │
│  - validate_relationship_dict()                      │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│ ReferenceRegistry                                    │
│  - Loads all data files                              │
│  - Maintains ID index                                │
│  - Provides suggestions                              │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│ ValidationSchema                                     │
│  - Field → Domain mappings                           │
│  - Suffix rules                                      │
│  - Bidirectional relationships                       │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Configuration Options

### Enable/Disable Validation

```python
generator.enable_validation(True)   # Enable
generator.enable_validation(False)  # Disable
```

### Enable/Disable Auto-Fix

```python
generator.enable_auto_fix(True)   # Auto-fix enabled
generator.enable_auto_fix(False)  # Manual fix only
```

### Per-Call Override

```python
# Override auto_fix for specific call
valid_ids, invalid = self.validate_and_fix_references(
    'contaminants',
    reference_ids,
    auto_fix=False,  # Override setting
    remove_invalid=True
)
```

---

## 🧪 Testing

Run the integration example:

```bash
PYTHONPATH=. python3 shared/validation/integration_example.py
```

Expected output:
```
🔧 Generating: aluminum-laser-cleaning
   Validating relationships...
   ⚠️  Removed invalid reference: contaminants/rust
   🔧 Fixed reference: contaminants/aluminum-oxidation → aluminum-oxidation-contamination
   📊 Validated: 4 refs, Fixed: 1, Removed: 1
```

---

## 🛠️ Standalone Repair Tools

### Repair Contaminant Suffixes

```bash
# Dry run (show what would be fixed)
python3 scripts/validation/repair_contaminant_suffixes.py --dry-run

# Apply fixes
python3 scripts/validation/repair_contaminant_suffixes.py
```

### Repair All Broken Links

```bash
# Dry run all domains
python3 scripts/validation/repair_broken_links.py --dry-run

# Fix specific domain
python3 scripts/validation/repair_broken_links.py --domain materials

# Apply fixes
python3 scripts/validation/repair_broken_links.py
```

---

## ✅ Benefits

1. **Real-time Validation** - Catch broken references during generation, not at export
2. **Auto-Fix** - Common issues fixed automatically (suffixes, typos)
3. **Clean Data** - Invalid references removed before saving
4. **Statistics** - Track validation performance
5. **Consistent** - Same validation rules across all generators
6. **Maintainable** - Central schema, easy to update
7. **Backward Compatible** - Can be disabled if needed

---

## 🎓 Best Practices

1. **Always initialize validator first** in `__init__`
2. **Enable auto-fix by default** for production generators
3. **Log fixes clearly** so users know what changed
4. **Validate before saving** to maintain data integrity
5. **Check statistics** after bulk operations
6. **Reload registry** if data changes during runtime
7. **Use dry-run mode** when testing repair scripts

---

## 📚 See Also

- `shared/validation/integration_example.py` - Complete working examples
- `scripts/validation/verify_data_integrity.py` - Pre-export validator
- `scripts/validation/verify_frontmatter_links.py` - Post-export validator
- `docs/VALIDATION.md` - Validation system documentation
