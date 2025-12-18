# Materials Data Architecture

**Last Updated**: November 7, 2025  
**Structure Version**: 3.0 (Multi-file architecture)

---

## 📂 File Structure

The materials data is now organized across **three dedicated YAML files** for better maintainability and independent enhancement:

```
materials/data/
├── Materials.yaml              # Core metadata (1.2 MB)
│   └── Material definitions, descriptions, FAQs, micros, etc.
│
├── MaterialProperties.yaml     # Material properties (490 KB)
│   └── Physical, mechanical, chemical, and thermal properties
│
├── MachineSettings.yaml        # Laser settings (168 KB)
│   └── Laser processing parameters (power, wavelength, fluence, etc.)
│
├── Categories.yaml             # Category taxonomy and ranges
│
├── loader.py                   # Centralized data loader (NEW)
│   └── Transparently merges all files by material name
│
└── materials.py                # Cached loader wrapper
    └── Uses loader.py for backward compatibility
```

---

## 🔄 Data Loading

### Primary Method (Recommended)
```python
from materials.data import load_materials_data, load_material

# Load all materials (merged from all 3 files)
all_data = load_materials_data()
materials = all_data['materials']

# Each material has complete data merged
aluminum = materials['Aluminum']
print(aluminum['properties'])  # From MaterialProperties.yaml
print(aluminum['machine_settings'])     # From MachineSettings.yaml

# Or load specific material
aluminum = load_material("Aluminum")
```

### Legacy Method (Backward Compatible)
```python
from materials.data.materials import load_materials_cached

# Still works - uses new loader internally
data = load_materials_cached()
materials = data['materials']
aluminum = materials['Aluminum']
```

Both methods return **identical structure** - properties and machine_settings are merged into each material.

---

## 📋 File Specifications

### Materials.yaml
**Purpose**: Core material metadata  
**Size**: 1.2 MB  
**Contains**:
- Material names, categories, subcategories
- Descriptions, titless
- FAQs, micros, author metadata
- Regulatory standards, applications
- Images, E-E-A-T metadata
- Material characteristics (legacy field)

**Does NOT contain** (extracted to separate files):
- ❌ properties (→ MaterialProperties.yaml)
- ❌ machine_settings (→ MachineSettings.yaml)

**Example Structure**:
```yaml
materials:
  Aluminum:
    name: Aluminum
    category: metal
    subcategory: pure_metals
    description: "Laser cleaning parameters for Aluminum"
    title: "Aluminum Laser Cleaning"
    faq: [...]
    micro: {...}
    # properties merged at runtime from MaterialProperties.yaml
    # machine_settings merged at runtime from MachineSettings.yaml
```

---

### MaterialProperties.yaml
**Purpose**: Material property data  
**Size**: 490 KB (19,968 lines)  
**Contains**: Physical, mechanical, chemical, and thermal properties

**Structure**:
```yaml
_metadata:
  description: Material properties extracted from Materials.yaml
  extracted_date: '2025-11-07T11:22:52.152170'
  total_materials: 132

properties:
  Aluminum:
    material_characteristics:
      label: Material Characteristics
      percentage: 40.0
      density:
        value: 2.7
        unit: g/cm³
        confidence: 98
        source: ai_research
      hardness:
        value: 2.75
        unit: Mohs
        confidence: 98
        source: ai_research
      # ... more properties
    
    laser_material_interaction:
      label: Laser-Material Interaction
      percentage: 60.0
      laserAbsorption:
        value: 0.08
        unit: ''
        confidence: 95
        source: ai_research
      # ... more interaction properties
```

**Property Categories**:
1. **material_characteristics** (40%):
   - Physical: density, hardness, tensileStrength, compressiveStrength
   - Thermal: thermalConductivity, thermalExpansion, specificHeat
   - Mechanical: youngsModulus, fractureToughness
   - Chemical: corrosionResistance, oxidationResistance

2. **laser_material_interaction** (60%):
   - Optical: laserAbsorption, laserReflectivity, absorptivity
   - Thermal: meltingPoint, boilingPoint, thermalDiffusivity
   - Processing: ablationThreshold, laserDamageThreshold

---

### MachineSettings.yaml
**Purpose**: Laser machine processing parameters  
**Size**: 168 KB (5,010 lines)  
**Contains**: Optimal laser settings for each material

**Structure**:
```yaml
_metadata:
  description: Machine settings extracted from Materials.yaml
  extracted_date: '2025-11-07T11:22:52.851666'
  total_materials: 132

settings:
  Aluminum:
    powerRange:
      description: Optimal average power for Aluminum surface cleaning
      unit: W
      value: 100
      min: 50
      max: 200
    
    wavelength:
      description: Near-IR wavelength for optimal absorption
      unit: nm
      value: 1064
    
    fluenceThreshold:
      description: Energy density for effective contaminant removal
      unit: J/cm²
      value: 2.5
    
    # ... 9 total parameters
```

**Parameters** (per material):
- `powerRange` - Laser average power (W)
- `wavelength` - Laser wavelength (nm)
- `spotSize` - Beam spot diameter (μm)
- `repetitionRate` - Pulse frequency (kHz)
- `fluenceThreshold` - Energy density (J/cm²)
- `pulseWidth` - Pulse duration (ns)
- `scanSpeed` - Scanning velocity (mm/s)
- `passCount` - Number of cleaning passes
- `overlapRatio` - Beam overlap percentage (%)

---

## 🔧 Loader API Reference

### `load_materials_data() -> Dict`
Load complete materials database with merged properties and settings.

**Returns**:
```python
{
    'materials': {
        'Aluminum': {
            'name': 'Aluminum',
            'category': 'metal',
            'properties': {...},  # Merged from MaterialProperties.yaml
            'machine_settings': {...},     # Merged from MachineSettings.yaml
            # ... other fields from Materials.yaml
        },
        # ... 131 more materials
    },
    'category_metadata': {...},
    'material_index': {...},
    # ... other metadata
}
```

### `load_material(name: str) -> Optional[Dict]`
Load specific material with merged data.

**Example**:
```python
aluminum = load_material("Aluminum")
if aluminum:
    density = aluminum['properties']['material_characteristics']['density']
    power = aluminum['machine_settings']['powerRange']
```

### `get_material_names() -> List[str]`
Get sorted list of all material names.

**Returns**: `['Alabaster', 'Alumina', 'Aluminum', ..., 'Zirconium']`

### `clear_cache()`
Clear LRU cache if YAML files modified at runtime.

---

## ✅ Validation

All materials are validated to have:
- ✅ Complete properties (132/132 materials)
- ✅ Complete machine_settings (132/132 materials)
- ✅ All required property fields
- ✅ All required setting parameters

**Validation happens during load** via `fail_fast_materials_validator`.

---

## 🎯 Benefits of Multi-File Architecture

### 1. **Separation of Concerns**
- Material metadata in Materials.yaml
- Physical properties in MaterialProperties.yaml  
- Machine parameters in MachineSettings.yaml

### 2. **Independent Enhancement**
```yaml
# Easy to expand MaterialProperties.yaml
Aluminum:
  material_characteristics:
    # Add new property here
    wettability:
      value: 0.75
      unit: contact_angle
      
# Easy to expand MachineSettings.yaml
Aluminum:
  # Add new setting here
  beamProfile:
    value: gaussian
```

### 3. **Better Organization**
- Smaller files (1.2MB + 490KB + 168KB vs 2.4MB monolith)
- Focused editing (properties vs settings)
- Clear data ownership

### 4. **Performance**
- LRU caching for fast lookups
- In-memory merge (no I/O overhead)
- Same performance as single-file

---

## 🔄 Migration from Single-File

**Before (v2.0)**:
```python
# Everything in Materials.yaml
with open('Materials.yaml') as f:
    data = yaml.safe_load(f)
    aluminum = data['materials']['Aluminum']
    props = aluminum['properties']  # Embedded
    settings = aluminum['machine_settings']  # Embedded
```

**After (v3.0)**:
```python
# Transparently merged from 3 files
from materials.data import load_materials_data
data = load_materials_data()
aluminum = data['materials']['Aluminum']
props = aluminum['properties']  # Merged from MaterialProperties.yaml
settings = aluminum['machine_settings']  # Merged from MachineSettings.yaml
```

**Result**: Same code, same structure, better architecture! ✅

---

## 📦 Backup & Recovery

Original Materials.yaml backed up before extraction:
```
materials/data/backups/Materials_20251107_112252.yaml
```

To rollback (if needed):
```bash
cp materials/data/backups/Materials_20251107_112252.yaml materials/data/Materials.yaml
# Then delete MaterialProperties.yaml and MachineSettings.yaml
# And revert loader.py changes
```

---

## 🚀 Future Enhancements

With separate files, you can now:

### Material Properties
- Add crystallographic data
- Add electromagnetic properties  
- Add surface chemistry data
- Expand thermal properties

### Machine Settings
- Add multi-wavelength support
- Add beam shaping parameters
- Add environmental settings
- Add safety parameters

Each enhancement can be developed **independently** without affecting other datasets.

---

## 📚 See Also

- **DATA_ARCHITECTURE_EXTRACTION_COMPLETE.md** - Complete migration documentation
- **materials/schema.py** - MaterialEntry schema definition
- **Categories.yaml** - Category taxonomy and ranges

---

## ⚡ Quick Reference

```python
# Load all materials
from materials.data import load_materials_data
data = load_materials_data()

# Load specific material
from materials.data import load_material
aluminum = load_material("Aluminum")

# Get material names
from materials.data import get_material_names
names = get_material_names()  # ['Alabaster', ..., 'Zirconium']

# Clear cache (if files modified)
from materials.data import clear_cache
clear_cache()
```

**All loaders return the same merged structure** - your code doesn't need to know about the multi-file architecture! 🎉
