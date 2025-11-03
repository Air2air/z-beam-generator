# Category Data - Modular Structure

**Version**: 1.0.0  
**Created**: October 30, 2025  
**Source**: Split from Categories.yaml (121KB)

---

## 📁 File Structure

This directory contains **8 focused subcategory files** extracted from the monolithic `Categories.yaml`:

| File | Size | Description | Use Cases |
|------|------|-------------|-----------|
| `category_metadata.yaml` | 8KB | Category definitions & metadata | Category info, lookups |
| `material_properties.yaml` | 85KB | Property ranges by category | Property research, range validation |
| `machine_settings.yaml` | 7KB | Machine parameter guidance | Parameter components, UI generation |
| `safety_regulatory.yaml` | 15KB | Safety & compliance templates | Safety components, regulatory content |
| `industry_applications.yaml` | 12KB | Industry-specific guidance | Application generation, industry content |
| `environmental_impact.yaml` | 1KB | Sustainability templates | Environmental content, marketing |
| `property_taxonomy.yaml` | 4KB | Property classification system | Property analysis, categorization |
| `material_index.yaml` | 2KB | Category metadata lookup | Quick references |

**Total Size**: 134KB (original: 121KB + 13KB metadata)

---

## 🔧 Usage

### Recommended: Use CategoryDataLoader

```python
from utils.loaders.category_loader import CategoryDataLoader

loader = CategoryDataLoader()

# Load specific data
machine_settings = loader.get_machine_settings()
safety_data = loader.get_safety_regulatory()
properties = loader.get_material_properties()
```

### Legacy: Direct YAML Loading (Not Recommended)

```python
import yaml

# Works but loads unnecessary data
with open('data/categories/machine_settings.yaml', 'r') as f:
    data = yaml.safe_load(f)
    settings = data['machineSettingsRanges']
```

---

## 📊 File Contents

### 1. category_metadata.yaml
```yaml
metadata:
  version: 3.0.0
  total_categories: 10
  
categories:
  metal:
    name: Metallic Materials
    description: Pure metals, alloys, and metallic compounds
  ceramic:
    name: Ceramic Materials
    description: Advanced ceramic materials
  # ... 8 more categories
```

### 2. material_properties.yaml
```yaml
materialPropertyDescriptions:
  density:
    description: Mass per unit volume
    unit: g/cm³
    relevance: Affects thermal mass
    
categories:
  metal:
    category_ranges:
      density:
        min: 0.53
        max: 22.6
        unit: g/cm³
```

### 3. machine_settings.yaml
```yaml
machineSettingsRanges:
  wavelength:
    min: 355
    max: 10640
    unit: nm
    
machineSettingsDescriptions:
  wavelength:
    description: Laser wavelength for optimal interaction
    selection_criteria: Material absorption characteristics
```

### 4. safety_regulatory.yaml
```yaml
universal_regulatory_standards:
  - FDA 21 CFR 1040.10
  - ANSI Z136.1
  
safetyTemplates:
  flammable_metals:
    applicable_materials: [Magnesium, Aluminum]
    primary_hazards: [...]
```

### 5. industry_applications.yaml
```yaml
industryGuidance:
  aerospace:
    typical_materials: [Aluminum, Titanium]
    critical_requirements: [...]
    
applicationTypeDefinitions:
  precision_cleaning:
    description: High-precision removal
    industries: [Semiconductor, MEMS]
```

### 6. environmental_impact.yaml
```yaml
environmentalImpactTemplates:
  chemical_waste_elimination:
    description: Eliminates hazardous waste
    applicable_industries: [Semiconductor, Medical]
    quantified_benefits: Up to 100% reduction
```

### 7. property_taxonomy.yaml
```yaml
propertyCategories:
  categories:
    laser_material_interaction:
      properties: [laserAbsorption, reflectivity, ...]
    material_characteristics:
      properties: [density, hardness, ...]
```

### 8. material_index.yaml
```yaml
category_metadata:
  metal:
    article_type: material
    description: Metal materials for laser cleaning
```

---

## 🎯 Benefits

### Performance
- Load only what you need (7KB vs 121KB)
- Parallel loading possible
- Automatic caching

### Maintainability  
- Single responsibility per file
- Easier to update specific sections
- Clear data boundaries

### Reusability
- Export files to other projects
- Use as API data sources
- Component-specific loading

---

## 🔄 Backward Compatibility

The original `Categories.yaml` remains in `data/` for backward compatibility.

CategoryDataLoader automatically:
1. Prefers split files if available
2. Falls back to Categories.yaml if needed
3. Caches loaded data for performance

---

## 📝 Metadata Header

Each file includes a metadata header:

```yaml
_metadata:
  source: Categories.yaml
  generated: 2025-10-30T12:43:43.932295
  description: File purpose and contents
  version: 1.0.0
```

This header is automatically stripped by CategoryDataLoader.

---

## 🧪 Testing

Verify files are properly loaded:

```bash
python3 scripts/data/test_category_loader.py
```

---

## 📚 Documentation

- **Migration Guide**: `docs/data/CATEGORY_DATA_MIGRATION_GUIDE.md`
- **Loader API**: `utils/loaders/category_loader.py`
- **Examples**: `scripts/data/migration_example.py`

---

## 🔄 Regeneration

To regenerate from Categories.yaml:

```bash
python3 scripts/data/split_categories.py
```

This will:
1. Read `data/Categories.yaml`
2. Extract data into 8 subcategories
3. Save to `data/categories/`
4. Add metadata headers
5. Report file sizes

---

## ⚠️ Important Notes

1. **Don't edit manually** - Regenerate from Categories.yaml
2. **material_index** is in `Materials.yaml`, not here
3. **Backup Categories.yaml** before major changes
4. **Test after regeneration** using test script

---

## 📊 Size Comparison

```
Categories.yaml:        121,404 bytes (100%)
Split files total:      134,622 bytes (111%)
Difference:            +13,218 bytes (metadata overhead)

Typical component load:
- Old way: 121KB (entire file)
- New way: 7-15KB (specific file)
- Savings: ~90% for most components
```

---

## 🎉 Status

✅ **COMPLETE** - All 8 files generated and tested  
✅ **LOADER** - CategoryDataLoader implemented with backward compatibility  
✅ **TESTS** - All tests passing  
🔄 **MIGRATION** - Component updates in progress

See `docs/data/CATEGORY_DATA_MIGRATION_GUIDE.md` for migration details.
