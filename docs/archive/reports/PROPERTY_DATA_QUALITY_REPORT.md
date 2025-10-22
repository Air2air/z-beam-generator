# Property Data Quality Analysis Report

**Date**: October 16, 2025  
**Analysis**: Systematic review of all properties for data inconsistencies  
**Scope**: All 42 properties across 122 frontmatter files

---

## Executive Summary

Following the discovery and removal of `absorptionCoefficient` due to severe data quality issues, a comprehensive analysis was conducted on all remaining properties. 

**Results:**
- ✅ **34 properties**: Clean, consistent data
- ⚠️ **8 properties**: Data quality issues identified
- 🔴 **2 properties**: SEVERE issues requiring immediate action
- 🟡 **4 properties**: MODERATE issues requiring standardization
- 🟢 **2 properties**: MINOR issues (easy fixes)

---

## Issues Identified

### 🔴 SEVERE Issues (Require Immediate Action)

#### 1. **chemicalStability**
**Issue**: 13 different units - qualitative vs quantitative mix

| Metric | Value |
|--------|-------|
| Files affected | 38 |
| Unit variations | 13 |
| Consistency | ❌ Very Poor |

**Units Used:**
- `% resistance` (10 files)
- `qualitative` (9 files) - "Moderate", "Poor", "Good"
- `scale 1-10` (4 files)
- `rating (1-10)` (3 files)
- `mg/cm²` (2 files) - Mass loss measurement
- `pH range` (1 file)
- `% weight retention` (1 file)
- Plus 6 other variations

**Examples:**
- Plastic: `99 % resistance`
- Glass: `0.7 mg/cm²` vs `8 scale 1-10` vs `99.5 % resistance`
- Stone: `95 % resistance` vs `low qualitative` vs `pH range`
- Masonry: `8 rating 1-10` vs `Moderate qualitative` vs `7 pH`

**Problem:**
- Mixing **qualitative** ("Moderate") with **quantitative** (99%)
- Mixing different **measurement types** (resistance %, mass loss, pH)
- Mixing different **scales** (1-10, %, mg/cm²)

**Recommendation:**
```
❌ REMOVE from system - too inconsistent to be useful
OR
📋 Complete research campaign to standardize all to single scale
```

**Reasoning:**
- Property is poorly defined for laser cleaning context
- No authoritative source in materials.yaml
- Mix of incompatible measurement approaches

---

#### 2. **crystallineStructure**
**Issue**: Qualitative property with 7 unit variations (already flagged for removal)

| Metric | Value |
|--------|-------|
| Files affected | 52 |
| Unit variations | 7 |
| Consistency | ❌ Poor |

**Units Used:**
- `crystal system` (34 files) - "FCC", "BCC", "Hexagonal"
- `none` (10 files)
- `qualitative` (2 files) - "Amorphous", "Semi-crystalline"
- `% crystallinity` (2 files) - 0%, 95%
- `n/a` (2 files)
- `crystal_system` (1 file) - formatting variation
- `Crystal System` (1 file) - capitalization variation

**Problem:**
- **Non-numeric** qualitative property
- Mixing **crystal system names** with **crystallinity percentages**
- Inconsistent formatting and NULL handling

**Recommendation:**
```
❌ REMOVE from system (already scheduled)
```

**Reasoning:**
- Already identified for removal
- Non-numeric property doesn't fit range-based system
- Qualitative data not useful for laser parameter calculations

---

### 🟡 MODERATE Issues (Require Standardization)

#### 3. **hardness**
**Issue**: 13 different units - but this is EXPECTED

| Metric | Value |
|--------|-------|
| Files affected | 122 |
| Unit variations | 13 |
| Consistency | ⚠️ Variable by material type |

**Units Used:**
- `Mohs` (40 files) - Minerals/ceramics
- `MPa` (33 files) - Vickers hardness
- `HV` (16 files) - Vickers hardness
- `GPa` (8 files) - Very hard materials
- `Shore D` (7 files) - Plastics/rubbers
- `N/mm²` (6 files)
- `HB` (4 files) - Brinell hardness
- `Shore A`, `HRM`, `Rockwell R`, `Barcol`, `kgf/mm²`, `N` (1-2 each)

**Analysis:**
✅ **This is EXPECTED and CORRECT**

Different material classes use different hardness scales:
- **Minerals/Stone**: Mohs scale (1-10)
- **Metals**: Vickers (HV) or Brinell (HB) 
- **Plastics**: Shore A/D scale
- **Ceramics**: GPa or Vickers

**Recommendation:**
```
✅ KEEP AS-IS - Unit variation is appropriate
📋 Document that multiple scales are used by material type
🔍 Optionally normalize to single scale in future (complex conversion)
```

**Reasoning:**
- Industry standard practice
- Each scale appropriate for material class
- Conversion between scales is complex and material-dependent

---

#### 4. **oxidationResistance**
**Issue**: 6 units - °C vs qualitative scales

| Metric | Value |
|--------|-------|
| Files affected | 54 |
| Unit variations | 6 |
| Consistency | ⚠️ Moderate |

**Units Used:**
- `°C` (44 files) - **Temperature resistance** ✅ Preferred
- `qualitative` (5 files) - "Good", "Excellent", "Moderate"
- `relative scale 0-100` (2 files)
- `rating (1-10)` (1 file)
- `rating (1-5)` (1 file)
- `%` (1 file)

**Problem:**
- **Majority (81%) use °C** - good foundation
- **5 files use qualitative** - should be researched/converted
- **Inconsistent rating scales** - should standardize

**Recommendation:**
```
📋 STANDARDIZE to °C (oxidation onset temperature)
🔍 Research the 5 qualitative values to find temperature equivalents
✅ Convert rating scales to temperature values
```

**Action Required:**
- Research qualitative values for actual temperature data
- Standardize all to °C format
- Update category ranges after standardization

---

#### 5. **thermalExpansion**
**Issue**: 11 different unit formats (all represent same quantity)

| Metric | Value |
|--------|-------|
| Files affected | 122 |
| Unit variations | 11 |
| Consistency | ⚠️ Poor formatting |

**Units Used:**
- `10^-6/K` (87 files) - Most common ✅
- `10⁻⁶/K` (12 files) - Unicode superscript
- `μm/m·°C` (7 files) - Equivalent unit
- `μm/m·K` (6 files) - Equivalent unit
- `×10⁻⁶/°C` (3 files)
- `10^-6/°C` (2 files)
- `×10⁻⁶/K`, `10^-6 K^-1`, `μm·m⁻¹·K⁻¹`, `µm/m·°C`, `10 ^-6 /K` (1 each)

**Problem:**
- All represent **same quantity** (10⁻⁶/K)
- Formatting inconsistencies:
  - `^` vs `⁻` (superscript)
  - `×` vs no multiplication symbol
  - `/K` vs `/°C` (same for differences)
  - Spacing variations

**Recommendation:**
```
📋 STANDARDIZE to: 10⁻⁶/K (unicode superscript)
OR: μm/m·K (explicit unit)
✅ Convert all 11 variations to single format
🔍 Low complexity - pure formatting fix
```

**Action Required:**
- Choose standard format
- Convert all values to standard format
- Update category ranges if needed

---

### 🟢 MINOR Issues (Easy Fixes)

#### 6. **laserAbsorption**
**Issue**: 5 units but 93% consistent

| Metric | Value |
|--------|-------|
| Files affected | 122 |
| Unit variations | 5 |
| Consistency | ✅ Good (93%) |

**Units Used:**
- `%` (114 files) - **93% of files** ✅
- `cm⁻¹` (3 files)
- `1/cm` (2 files)
- `unitless` (2 files)
- `1/m` (1 file)

**Problem:**
- **Only 8 files** use non-standard units
- Easy to convert to %

**Recommendation:**
```
✅ Convert 8 outlier files to % format
🔍 Low priority - already 93% consistent
📋 Simple unit conversion
```

**Action Required:**
- Convert 8 files to % format
- Verify conversion factors
- Regenerate category ranges

---

#### 7. **thermalDiffusivity**
**Issue**: 2 units (mm²/s vs m²/s)

| Metric | Value |
|--------|-------|
| Files affected | 122 |
| Unit variations | 2 |
| Consistency | ✅ Good (96%) |

**Units Used:**
- `mm²/s` (117 files) - **96% of files** ✅
- `m²/s` (5 files)

**Problem:**
- Only 5 files use wrong scale
- Simple conversion: m²/s → mm²/s (multiply by 1,000,000)

**Recommendation:**
```
✅ Convert 5 m²/s values to mm²/s
🔍 Very low priority - highly consistent
📋 Trivial conversion factor
```

**Action Required:**
- Multiply 5 values by 1,000,000
- Update units to mm²/s
- Regenerate category ranges

---

#### 8. **youngsModulus**
**Issue**: GPa vs MPa (context-dependent)

| Metric | Value |
|--------|-------|
| Files affected | 122 |
| Unit variations | 2 |
| Consistency | ✅ Good (87%) |

**Units Used:**
- `GPa` (106 files) - **87% of files** ✅
- `MPa` (16 files) - Used for very flexible materials

**Problem:**
- 16 files use MPa (soft materials like plastics, wood)
- Conversion: MPa → GPa (divide by 1,000)

**Analysis:**
- MPa used for **materials with E < 10 GPa**
- This is contextually appropriate (better precision)
- Example: Rubber might be 0.001 GPa = 1 MPa

**Recommendation:**
```
✅ Convert to GPa for consistency
OR
✅ Keep MPa for materials < 10 GPa (preserves precision)
🔍 Medium priority - both approaches valid
```

**Action Required:**
- **Option A**: Convert all to GPa
- **Option B**: Document that MPa used for E < 10 GPa
- Update category ranges

---

## Priority Action Matrix

| Priority | Property | Action | Complexity | Impact |
|----------|----------|--------|------------|--------|
| 🔴 **P0** | chemicalStability | Remove OR complete research | HIGH | HIGH |
| 🔴 **P0** | crystallineStructure | Remove (already scheduled) | LOW | MEDIUM |
| 🟡 **P1** | oxidationResistance | Standardize to °C | MEDIUM | MEDIUM |
| 🟡 **P1** | thermalExpansion | Standardize format | LOW | LOW |
| 🟡 **P2** | hardness | Document (keep as-is) | LOW | LOW |
| 🟢 **P3** | laserAbsorption | Convert 8 files | LOW | LOW |
| 🟢 **P3** | thermalDiffusivity | Convert 5 files | LOW | LOW |
| 🟢 **P3** | youngsModulus | Convert or document | LOW | LOW |

---

## Recommended Immediate Actions

### 1. Remove Problematic Properties (P0)

**chemicalStability**:
```bash
python3 scripts/tools/remove_chemical_stability.py
```
- Remove from Categories.yaml propertyCategories
- Remove from 38 frontmatter files
- Reason: Too inconsistent (13 units, qualitative vs quantitative)

**crystallineStructure** (already done):
```bash
python3 scripts/tools/remove_crystalline_structure.py
```
- Already scheduled for removal
- Non-numeric, qualitative property

### 2. Standardize Units (P1)

**oxidationResistance**:
- Research 5 qualitative values to find temperature equivalents
- Convert rating scales to °C
- Regenerate category ranges

**thermalExpansion**:
- Choose standard format: `10⁻⁶/K` or `μm/m·K`
- Convert all 11 variations
- Simple formatting fix

### 3. Document Expected Variations (P2)

**hardness**:
- Add documentation note
- Explain why multiple scales are appropriate
- No conversion needed

### 4. Quick Fixes (P3)

**laserAbsorption**, **thermalDiffusivity**, **youngsModulus**:
- Simple unit conversions
- Low priority (already >85% consistent)
- Can be batched together

---

## Impact Assessment

### Properties to Remove (2)

- `chemicalStability` - 38 files affected
- `crystallineStructure` - 52 files affected (done)

**Total impact**: 90 property instances removed

### Properties to Standardize (4)

- `oxidationResistance` - 10 files need research/conversion
- `thermalExpansion` - 35 files need formatting fixes
- `laserAbsorption` - 8 files need conversion
- `thermalDiffusivity` - 5 files need conversion

**Total impact**: 58 property instances need updates

### Properties to Document (1)

- `hardness` - No changes needed, just documentation

### Properties Already Clean (34)

- No action needed for remaining 34 properties

---

## Comparison with absorptionCoefficient

| Property | Units | Issue Severity | Action Taken |
|----------|-------|----------------|--------------|
| **absorptionCoefficient** | 12 | 🔴 SEVERE | ✅ Removed |
| **chemicalStability** | 13 | 🔴 SEVERE | 📋 Recommend removal |
| **crystallineStructure** | 7 | 🔴 SEVERE | ✅ Removing |
| **hardness** | 13 | ✅ Expected | Keep (appropriate) |
| **thermalExpansion** | 11 | 🟡 Formatting | Standardize |
| **oxidationResistance** | 6 | 🟡 Mixed | Standardize |
| **laserAbsorption** | 5 | 🟢 Minor | Convert 8 files |

---

## Conclusion

The systematic analysis identified **8 properties with data quality issues**, ranging from severe to minor. 

### Summary:
- ✅ **absorptionCoefficient**: Already removed (12 units, 9 orders of magnitude)
- 🔴 **2 properties** require removal (chemicalStability, crystallineStructure)
- 🟡 **4 properties** require standardization
- 🟢 **2 properties** have minor fixable issues
- ✅ **34 properties** are clean and consistent

### Next Steps:
1. Remove `chemicalStability` (P0)
2. Confirm removal of `crystallineStructure` (P0)
3. Standardize `oxidationResistance` and `thermalExpansion` (P1)
4. Document `hardness` multi-scale approach (P2)
5. Batch fix minor unit conversions (P3)

This cleanup will result in a **robust, consistent property taxonomy** with high data quality standards.
