# Settings Data Directory

**Location**: `data/settings/`  
**Domain**: Settings (separate from materials)  
**Separation Date**: November 26, 2025

---

## 📁 Contents

### Settings.yaml
**Single source of truth for laser machine settings**

**Structure**:
```yaml
_metadata:
  version: "1.0.0"
  last_updated: "2025-11-24T21:00:00Z"
  schema_version: "1.0.0"
  source_of_truth: true
  created: "2025-11-24"
  migrated_from: "MachineSettings.yaml"

settings:
  Aluminum:
    machine_settings:
      powerRange:
        value: 50
        unit: "W"
        min: 10
        max: 100
      wavelength:
        value: 1064
        unit: "nm"
      # ... 7 more parameters
    challenges:
      thermal_management: [...]
      precision_requirements: [...]
      contamination_challenges: [...]
    description: "AI-generated description..."
```

**Coverage**: 159/159 materials (100%)

**Parameters** (9 per material):
- `powerRange` - Laser output power (W)
- `wavelength` - Laser wavelength (nm)
- `repetitionRate` - Pulse frequency (kHz)
- `scanSpeed` - Scanning speed (mm/s)
- `spotSize` - Beam spot diameter (μm)
- `fluenceThreshold` - Energy density (J/cm²)
- `pulseDuration` - Pulse width (ns)
- `focusDepth` - Focus position (mm)
- `beamQuality` - M² factor (dimensionless)

---

## 🏗️ Architecture

### Domain Separation
Settings domain is **completely separate** from materials domain:

```
data/
├── materials/          # Material properties ONLY
│   └── Materials.yaml
└── settings/           # Machine settings ONLY
    └── Settings.yaml

domains/
├── materials/          # Material property logic
│   └── data_loader.py
└── settings/           # Settings logic
    ├── data_loader.py
    ├── settings_cache.py
    └── modules/
        └── settings_module.py
```

### Why Separate?
1. **Different Concerns**: Settings = "HOW to process", Materials = "WHAT to process"
2. **Independent Evolution**: Settings can change without touching materials
3. **Clear Ownership**: Different teams can own different domains
4. **Consistent Pattern**: Matches contaminants domain structure

---

## 🔌 Usage

### Load Settings Data
```python
from domains.settings.data_loader import load_settings_yaml

# Load all settings
settings = load_settings_yaml()

# Access specific material
aluminum = settings['Aluminum']
power = aluminum['powerRange']['value']  # 50
```

### Get Settings Path
```python
from domains.settings.data_loader import get_settings_path

settings_path = get_settings_path()
# Returns: data/settings/Settings.yaml
```

### Use Cached Loader (Faster)
```python
from domains.settings.settings_cache import load_settings_cached

# First call: Parse YAML (~100ms)
settings = load_settings_cached()

# Subsequent calls: Memory access (<1ms)
settings = load_settings_cached()
```

---

## 📊 Data Completeness

| Field | Coverage | Status |
|-------|----------|--------|
| machine_settings | 159/159 (100%) | ✅ COMPLETE |
| challenges | 159/159 (100%) | ✅ COMPLETE |
| description | 159/159 (100%) | ✅ COMPLETE |

**Last Verified**: November 26, 2025

---

## 🔄 Data Flow

### Settings Generation
```
1. AI generates description
   ↓
2. Saves to Settings.yaml
   ↓
3. Immediate frontmatter sync
   ↓
4. Exported to frontmatter/settings/{slug}-settings.yaml
```

### Frontmatter Export
```
Settings.yaml
   ↓
SettingsModule (adds ranges from Categories.yaml)
   ↓
TrivialFrontmatterExporter
   ↓
frontmatter/settings/{material-slug}-settings.yaml
```

---

## 📝 Schema

### Machine Settings
Each parameter has:
- `value`: Numeric value
- `unit`: Unit of measurement
- `min`: Minimum value (from Categories.yaml)
- `max`: Maximum value (from Categories.yaml)
- `confidence`: Confidence score (0-1)

### Material Challenges
Three categories:
- `thermal_management`: Heat-related challenges
- `precision_requirements`: Accuracy needs
- `contamination_challenges`: Cleaning difficulties

### Settings Description
AI-generated text describing optimal settings and considerations for laser cleaning this material.

---

## 🚫 What NOT to Put Here

❌ Material properties (density, hardness, etc.) → Use `data/materials/Materials.yaml`  
❌ Property research data → Use `data/materials/PropertyResearch.yaml`  
❌ Category definitions → Use `data/materials/Categories.yaml`  
❌ Industry guidance → Use `data/materials/IndustryApplications.yaml`

✅ Only machine settings, challenges, and descriptions

---

## 📚 Related Documentation

- **Architecture**: `SETTINGS_DOMAIN_SEPARATION_EVALUATION.md`
- **Data Policy**: `DATA_ARCHITECTURE_SEPARATION.md`
- **Separation Completed**: November 26, 2025

---

## 🔍 Validation

Settings.yaml is validated by:
1. `tests/test_data_architecture_separation.py` - Zero cross-contamination
2. Schema version validation
3. Completeness checks (100% coverage required)

Run validation:
```bash
python3 -m pytest tests/test_data_architecture_separation.py -v
```

Expected: **5 passed** ✅
