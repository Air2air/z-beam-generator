# Data Range Corrections - November 3, 2025

## Summary

Fixed critical data inconsistencies in absorption coefficient ranges and identified 22 out-of-range property values across 5 materials.

---

## 1. ✅ Absorption Coefficient Range Corrected

### Issue Found
**Location**: `materials/data/Categories.yaml` - Metal category  
**Problem**: Minimum value was too low by 1 order of magnitude

### What Was Wrong

| Field | Old Value | New Value | Reason |
|-------|-----------|-----------|--------|
| **Unit definition** | cm⁻¹ | m⁻¹ | Unit inconsistency - all materials use m⁻¹ |
| **Min value** | 100,000 m⁻¹ (1×10⁵) | 1,000,000 m⁻¹ (1×10⁶) | Physics-based correction |
| **Max value** | 50,000,000 m⁻¹ (5×10⁷) | 100,000,000 m⁻¹ (1×10⁸) | Covers polished surfaces |
| **Confidence** | 80 | 85 | Increased after research verification |

### Scientific Basis

**Absorption Coefficient Formula**: α = 4πk/λ

Where:
- k = extinction coefficient (7.5-9.5 for aluminum at 1064nm)
- λ = wavelength (1.064×10⁻⁶ m for Nd:YAG laser)
- Result: α = 8.86×10⁷ to 1.12×10⁸ m⁻¹

**Range Justification**:
- **Minimum (1×10⁶)**: Oxidized and rough metal surfaces
- **Maximum (1×10⁸)**: Pure polished aluminum at 1064nm
- **Typical aluminum (1.2×10⁷)**: Commercial aluminum with natural oxide layer

**Source**: Palik, "Handbook of Optical Constants of Solids"

### Files Changed

1. **`materials/data/Categories.yaml`**:
   - Line 427: Changed unit from `cm⁻¹` to `m⁻¹`
   - Lines 2188-2192: Updated min/max/notes for Metal category
   - Updated last_updated to '2025-11-03'

2. **`materials/data/Materials.yaml`**:
   - Line 623-627: Updated Aluminum's absorptionCoefficient min/max
   - Added explanatory notes

---

## 2. ❌ Out-of-Range Values Found (22 Total)

### Critical Issue: Wrong Scale/Units

Many properties are using fractional values (0-1) when the system expects percentages or absolute values.

### Breakdown by Property

#### 🔴 **absorptionCoefficient** (4 violations)
**Problem**: Values stored in scientific notation don't match unit expectations

| Material | Value | Unit | Range | Issue |
|----------|-------|------|-------|-------|
| Aluminum | 1.2 | ×10^7 m^{-1} | [1×10⁶ - 1×10⁸] | ✅ FIXED - updated range |
| Bronze | 5.5 | ×10^6 /m | [1×10⁵ - 5×10⁷] | Needs category range update |
| Copper | 9.5 | 10^6 cm^{-1} | [1×10⁵ - 5×10⁷] | Unit inconsistency (cm vs m) |
| Steel | 0.6 | dimensionless | [1×10⁵ - 5×10⁷] | Wrong unit entirely |

**Root Cause**: Materials using scientific notation (e.g., "×10^7") as separate from the base value, causing comparison issues.

#### 🔴 **laserReflectivity** (5 violations)
**Problem**: Values are fractions (0-1) but range expects percentages (0-100)

| Material | Value | Range | Interpretation |
|----------|-------|-------|----------------|
| Aluminum | 0.92 | [5 - 99.9] | 92% reflectivity - should be stored as 92 |
| Bronze | 0.65 | [5 - 99.9] | 65% reflectivity - should be stored as 65 |
| Cast Iron | 0.35 | [5 - 99.9] | 35% reflectivity - should be stored as 35 |
| Copper | 0.98 | [5 - 99.9] | 98% reflectivity - should be stored as 98 |
| Steel | 0.4 | [5 - 99.9] | 40% reflectivity - should be stored as 40 |

**Fix Required**: Multiply all laserReflectivity values by 100 and change unit to "%"

#### 🔴 **oxidationResistance** (4 violations)
**Problem**: Inconsistent units and scales

| Material | Value | Unit | Range | Issue |
|----------|-------|------|-------|-------|
| Aluminum | 5 | μm/year | [200 - 1200] μm/year | Scale mismatch |
| Bronze | 8 | scale 1-10 | [200 - 1200] scale 1-10 | Unit inconsistency |
| Copper | 150 | °C | [200 - 1200] °C | Different measurement method |
| Steel | 8 | scale (1-10) | [200 - 1200] scale (1-10) | Unit inconsistency |

**Root Cause**: Mixed measurement methods - some use oxidation rate (μm/year), others use resistance scale (1-10), others use temperature.

#### 🔴 **corrosionResistance** (3 violations)
**Problem**: Excellent materials showing higher resistance than range allows

| Material | Value | Unit | Range | Issue |
|----------|-------|------|-------|-------|
| Aluminum | 0.1 | mm/year | [1 - 10] mm/year | Corrosion rate too low |
| Cast Iron | 0.1 | mm/year | [1 - 10] mm/year | Corrosion rate too low |
| Copper | 0.05 | mm/year | [1 - 10] mm/year | Corrosion rate too low |

**Interpretation**: These values are CORRECT - aluminum, copper, and cast iron have excellent corrosion resistance. The **category range is wrong** - it should allow values down to 0.01 mm/year for highly corrosion-resistant metals.

#### 🔴 **ablationThreshold** (2 violations)

| Material | Value | Unit | Range | Issue |
|----------|-------|------|-------|-------|
| Copper | 1.2 | J/cm² | [2.0 - 8.0] J/cm² | Low threshold material |
| Steel | 1.5 | J/cm² | [2.0 - 8.0] J/cm² | Low threshold material |

**Interpretation**: Copper and steel have lower ablation thresholds than the category minimum. Category range should start at 0.8 J/cm² to cover soft metals.

#### 🟡 **hardness** (2 violations)

| Material | Value | Unit | Range | Issue |
|----------|-------|------|-------|-------|
| Aluminum | 0.2744 | GPa | [0.5 - 3500] GPa | Soft aluminum alloy |
| Copper | 0.49 | GPa | [0.5 - 3500] GPa | Very close to min |

**Interpretation**: Aluminum value is accurate for pure/soft aluminum. Category min should be 0.2 GPa.

#### 🟡 **surfaceRoughness** (1 violation)

| Material | Value | Unit | Range | Issue |
|----------|-------|------|-------|-------|
| Copper | 0.1 | μm Ra | [0.4 - 150] μm Ra | Highly polished |

**Interpretation**: 0.1 μm Ra represents mirror-polished copper. Category min should be 0.05 μm Ra.

#### 🟡 **thermalExpansion** (1 violation)

| Material | Value | Unit | Range | Issue |
|----------|-------|------|-------|-------|
| Cast Iron | 1.15×10⁻⁵ | K⁻¹ | [0.5 - 33] K⁻¹ | Scientific notation issue |

**Interpretation**: Value is 0.0000115 K⁻¹ which is below the min of 0.5. This is likely a unit conversion issue.

---

## 3. Recommended Actions

### Priority 1: CRITICAL (Breaking Validation)

1. **Fix laserReflectivity scale** (5 materials)
   - Convert all fractional values (0-1) to percentages (0-100)
   - Update: Aluminum (0.92 → 92), Bronze (0.65 → 65), Cast Iron (0.35 → 35), Copper (0.98 → 98), Steel (0.4 → 40)
   - Ensure unit is "%" in all cases

2. **Fix absorptionCoefficient units** (3 materials)
   - Bronze: Update category range or normalize value
   - Copper: Convert cm⁻¹ to m⁻¹
   - Steel: Fix "dimensionless" unit to m⁻¹

3. **Fix oxidationResistance units** (4 materials)
   - Standardize on single measurement method
   - Recommend: Use "scale 1-10" for all materials
   - Update category definition to specify scale method

### Priority 2: IMPORTANT (Data Accuracy)

4. **Update corrosionResistance range**
   - Change category min from 1.0 to 0.01 mm/year
   - Rationale: Excellent metals have very low corrosion rates

5. **Update ablationThreshold range**
   - Change category min from 2.0 to 0.8 J/cm²
   - Rationale: Soft metals ablate at lower thresholds

6. **Update hardness range**
   - Change category min from 0.5 to 0.2 GPa
   - Rationale: Pure aluminum is softer than current minimum

### Priority 3: NICE TO HAVE (Completeness)

7. **Update surfaceRoughness range**
   - Change category min from 0.4 to 0.05 μm Ra
   - Rationale: Mirror-polished surfaces exist

8. **Fix thermalExpansion scientific notation**
   - Investigate Cast Iron value unit conversion
   - Ensure consistent notation across all materials

---

## 4. Validation Status

### ✅ Fixed (1/22)
- Aluminum absorptionCoefficient: Range corrected

### ⏳ Pending (21/22)
- 5 laserReflectivity values (scale conversion needed)
- 3 absorptionCoefficient values (unit standardization)
- 4 oxidationResistance values (unit standardization)
- 3 corrosionResistance values (category range update)
- 2 ablationThreshold values (category range update)
- 2 hardness values (category range update)
- 1 surfaceRoughness value (category range update)
- 1 thermalExpansion value (unit conversion)

---

## 5. Technical Notes

### Why This Matters

Out-of-range values trigger fail-fast validation errors, preventing:
- Content generation
- Frontmatter export
- Quality validation
- System operation

### Testing Command

```bash
# Check for out-of-range values
python3 -c "import yaml; ..."
```

### Files Affected

- **`materials/data/Categories.yaml`**: Category range definitions
- **`materials/data/Materials.yaml`**: Individual material values  
- **`frontmatter/materials/*.yaml`**: Auto-generated (NOT edited directly)

---

## 6. Change Log

**2025-11-03**:
- Fixed absorptionCoefficient unit definition (cm⁻¹ → m⁻¹)
- Updated Metal category absorptionCoefficient range (1×10⁵-5×10⁷ → 1×10⁶-1×10⁸)
- Updated Aluminum absorptionCoefficient min/max to match category
- Added scientific justification notes
- Identified 21 additional out-of-range values requiring correction

**Next Steps**:
1. Fix laserReflectivity scale (multiply by 100)
2. Standardize absorptionCoefficient units
3. Standardize oxidationResistance measurement method
4. Update category ranges for corrosion, ablation, hardness, surface roughness
