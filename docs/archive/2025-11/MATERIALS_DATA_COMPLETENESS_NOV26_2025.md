# Data Completeness Report
**Generated**: November 26, 2025 11:22:09

---

## 📦 Materials.yaml

**Total Materials**: 159
**Schema Version**: 4.0.0
**Last Updated**: 2025-11-26

### Critical Properties Completeness

| Property | Count | Percentage | Status |
|----------|-------|------------|--------|
| thermalConductivity | 159/159 | 100.0% | ✅ |
| thermalDiffusivity | 159/159 | 100.0% | ✅ |
| ablationThreshold | 159/159 | 100.0% | ✅ |

---

## ⚙️ Settings.yaml

**Total Materials**: 159
**Schema Version**: 1.0.0
**Created Date**: 2025-11-24T20:15:14.903526

### Critical Settings Completeness

| Parameter | Count | Percentage | Status |
|-----------|-------|------------|--------|
| powerRange | 159/159 | 100.0% | ✅ |
| wavelength | 159/159 | 100.0% | ✅ |
| repetitionRate | 159/159 | 100.0% | ✅ |
| scanSpeed | 159/159 | 100.0% | ✅ |
| spotSize | 159/159 | 100.0% | ✅ |

---

## 🧪 Contaminants.yaml

**Total Contamination Patterns**: 100
**Schema Version**: 1.0.0
**Last Updated**: 2025-11-25

### Structure Completeness

| Field | Count | Percentage | Status |
|-------|-------|------------|--------|
| name | 100/100 | 100.0% | ✅ |
| description | 100/100 | 100.0% | ✅ |
| laser_properties | 100/100 | 100.0% | ✅ |
| valid_materials | 100/100 | 100.0% | ✅ |

---

## 🔒 Architecture Validation

### Separation Compliance

| Check | Result | Status |
|-------|--------|--------|
| machineSettings in Materials.yaml | 0 | ✅ PASS |
| materialProperties in Settings.yaml | 0 | ✅ PASS |

---

## 📊 Summary

### ✅ Strengths
- **Materials.yaml**: 100% complete for critical thermal properties (thermalConductivity, thermalDiffusivity, ablationThreshold)
- **Settings.yaml**: 100% complete for all basic machine settings (powerRange, wavelength, repetitionRate, scanSpeed, spotSize)
- **Contaminants.yaml**: 100% complete for all critical structure fields
- **Architecture**: Perfect separation - 0 violations
- **Schema Versioning**: All files now have proper schema metadata

### 📋 Status by File

| File | Critical Fields | Status | Notes |
|------|----------------|--------|-------|
| Materials.yaml | 3/3 (100%) | ✅ COMPLETE | Thermal properties fully populated |
| Settings.yaml | 5/5 (100%) | ✅ COMPLETE | All basic settings populated |
| Contaminants.yaml | 4/4 (100%) | ✅ COMPLETE | 100 contamination patterns documented |

### 🎯 Recommendations

**Optional Enhancements** (Non-Critical):
1. Materials: Consider populating absorptionCoefficient (78.6%) and reflectivity (75.5%)
2. Settings: Optional parameters like fluence (1.3%) and dwellTime (18.9%) can be added if needed
3. All critical data is 100% complete - system is production-ready
