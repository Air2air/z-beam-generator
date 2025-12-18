# Data Architecture Separation Policy

**Last Updated**: November 26, 2025  
**Status**: ✅ ENFORCED - Automated test verification  
**Settings Domain Separation**: ✅ COMPLETE (Nov 26, 2025)

---

## 🎯 Core Principle

**Strict separation between material properties and machine settings.**

```
data/materials/Materials.yaml → properties (ONLY)
data/settings/Settings.yaml   → machine_settings (ONLY)
```

**Zero cross-contamination allowed.**

**Domain Separation** (Nov 26, 2025):
- Settings data: `data/settings/Settings.yaml`
- Settings domain: `domains/settings/`
- Completely independent from materials domain

---

## 📁 File Responsibilities

### Materials.yaml
**Single Source of Truth for Material Properties**

✅ **ALLOWED**:
- `properties` → Contains:
  - `laser_material_interaction` (absorption, reflectivity, thermal properties, ablation threshold, etc.)
  - `material_characteristics` (physical properties, composition, density, etc.)
- `category` (material classification)
- `applications` (use cases)
- `environmentalImpact`
- `author` (attribution)

❌ **FORBIDDEN**:
- `machine_settings` (belongs in Settings.yaml)
- Any laser processing parameters (power, wavelength, etc.)

**Structure**:
```yaml
materials:
  Material-Name:
    category: "category_name"
    properties:
      laser_material_interaction:
        absorptionCoefficient: {...}
        reflectivity: {...}
        thermalConductivity: {...}
        ablationThreshold: {...}
      material_characteristics:
        density: {...}
        meltingPoint: {...}
```

---

### Settings.yaml
**Single Source of Truth for Machine Settings**

**Location**: `data/settings/Settings.yaml` (separated Nov 26, 2025)  
**Domain**: `domains/settings/` (independent from materials)

✅ **ALLOWED**:
- `machine_settings` → Contains:
  - `powerRange` (laser power parameters)
  - `wavelength` (laser wavelength)
  - `pulseDuration` (pulse timing)
  - `repetitionRate` (frequency)
  - `scanSpeed` (scanning parameters)
  - `spotSize` (beam parameters)
  - `fluence` (energy density)
  - `pulseEnergy` (pulse parameters)
- `challenges` (operational considerations)
- `settings_description` (human-readable description)

❌ **FORBIDDEN**:
- `properties` (belongs in Materials.yaml)
- Any physical/thermal/chemical properties

**Structure**:
```yaml
settings:
  Material-Name:
    machine_settings:
      powerRange: {...}
      wavelength: {...}
      repetitionRate: {...}
      scanSpeed: {...}
      spotSize: {...}
    challenges: "Text describing operational challenges"
    settings_description: "Text describing settings rationale"
```

---

## 🔄 Export Architecture

**Dual-File Frontmatter Generation**

```
Materials.yaml + Settings.yaml
         ↓
TrivialFrontmatterExporter
         ↓
    ┌────────┴────────┐
    ↓                 ↓
materials/*.yaml    settings/*-settings.yaml
(properties)        (machine settings)
```

### Materials Pages
- **Path**: `frontmatter/materials/{slug}-laser-cleaning.yaml`
- **Content**: Material properties, environmental impact, applications
- **Source**: Materials.yaml only

### Settings Pages
- **Path**: `frontmatter/settings/{slug}-settings.yaml`
- **Content**: Machine settings, operational guidance, challenges
- **Source**: Settings.yaml only

---

## ✅ Enforcement

### Automated Test
**Location**: `tests/test_data_architecture_separation.py`

**Tests**:
1. ✅ Materials.yaml has NO machine_settings
2. ✅ Settings.yaml has NO properties
3. ✅ Materials.yaml HAS properties
4. ✅ Settings.yaml HAS machine_settings
5. ✅ Architecture separation summary report

**Run**:
```bash
python3 -m pytest tests/test_data_architecture_separation.py -v
```

**Expected Result**:
```
5 passed - ✅ ARCHITECTURE COMPLIANT
```

---

## 📊 Current Status

**As of November 26, 2025**:

### Materials.yaml (159 materials)
- ✅ properties: 159/159 materials (100%)
- ✅ machine_settings: 0/159 materials (0% - correct)

### Settings.yaml (159 materials)
- ✅ machine_settings: 159/159 materials (100%)
- ✅ properties: 0/159 materials (0% - correct)

**Violations**: 0  
**Architecture Status**: ✅ COMPLIANT

---

## 🚨 Historical Context

### Migration (November 24, 2025)
- **Before**: 132 materials had duplicate machine_settings in BOTH files
- **Action**: Removed all machine_settings from Materials.yaml
- **Result**: Settings.yaml became single source of truth
- **Documentation**: `MACHINESETTINGS_MIGRATION_NOV24_2025.md`

### Why This Matters
- **Data Integrity**: Single source of truth prevents conflicts
- **Maintainability**: Clear ownership of data types
- **Export Logic**: Simpler generation (no merging logic needed)
- **API Clarity**: Clear data contracts for consumers

---

## 🔧 Maintenance Guidelines

### Adding New Materials
1. ✅ Add material properties to Materials.yaml
2. ✅ Add machine settings to Settings.yaml
3. ❌ NEVER add both to the same file
4. ✅ Run architecture test to verify compliance

### Updating Data
- **Properties changed?** → Update Materials.yaml only
- **Settings changed?** → Update Settings.yaml only
- **Both changed?** → Update both files separately

### Code Changes
- **Always run test** after modifying data structure
- **Update documentation** if structure evolves
- **Maintain separation** in export/generation code

---

## 📚 Related Documentation

- `MACHINESETTINGS_MIGRATION_NOV24_2025.md` - Migration history
- `FIELD_RESTRUCTURING_VERIFICATION.md` - Restructuring details
- `export/README.md` - Export architecture (updated Nov 26, 2025)
- `generation/core/component_specs.py` - Generation specs (updated Nov 26, 2025)

---

## ✨ Summary

```
✅ Materials.yaml = Properties (what the material IS)
✅ Settings.yaml  = Settings (how to process it)
❌ Never mix them
✅ Test enforces separation
✅ 100% compliant as of Nov 26, 2025
```

**The architecture is clean, enforced, and maintained.**
