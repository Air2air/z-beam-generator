# Absorption Coefficient Research Report

**Date**: October 16, 2025  
**Property**: `absorptionCoefficient`  
**Status**: ⚠️ **DATA QUALITY ISSUES IDENTIFIED**

---

## Executive Summary

The `absorptionCoefficient` property has **severe data quality and unit consistency issues** across the system:

### Current State
- ✅ Present in 117 frontmatter files
- ❌ NOT in materials.yaml (no source data)
- ❌ NOT in Categories.yaml ranges
- ❌ **12 different unit variations** used
- ❌ Values range from 0.001 to 12,000,000 (incorrect scale mixing)

---

## Data Analysis

### Unit Inconsistency Problem

**Units Found (12 variations):**
| Unit | Count | Example Values | Issue |
|------|-------|----------------|-------|
| cm⁻¹ | 89 | 0.75 - 0.85 | ✅ Most common |
| m⁻¹ | 8 | Large values | Different scale |
| ×10⁷ m⁻¹ | 4 | 1.2, 4.2 | Scientific notation |
| 1/μm | 3 | 0.03 - 0.35 | Different scale |
| μm⁻¹ | 3 | Small values | Different scale |
| ×10⁵ cm⁻¹ | 3 | Large values | Scientific notation |
| ×10⁴ cm⁻¹ | 2 | 1.0 - 8500 | Scientific notation |
| dimensionless | 1 | 0.85 | ❌ Wrong unit |
| cm⁻¹ at 1064 nm | 1 | 0.85 | Wavelength-specific |
| cm^-1 @ 1064nm | 1 | 0.85 | ❌ Formatting error |
| 10⁵ cm⁻¹ | 1 | Large value | Missing × symbol |
| ×10⁵ m⁻¹ | 1 | Large value | Scientific notation |

### Value Distribution by Category

| Category | Materials | Unit Majority | Value Range | Notes |
|----------|-----------|---------------|-------------|-------|
| **Wood** | 20 | cm⁻¹ (100%) | 0.75 - 0.85 | ✅ Consistent |
| **Stone** | 18 | cm⁻¹ (100%) | 0.15 - 0.85 | ✅ Consistent |
| **Metal** | 36 | cm⁻¹ (39%) | 0.03 - 12M | ❌ Inconsistent units |
| **Masonry** | 7 | cm⁻¹ (100%) | 0.65 - 0.85 | ✅ Consistent |
| **Ceramic** | 7 | cm⁻¹ (100%) | 0.80 - 0.85 | ✅ Consistent |
| **Glass** | 6 | cm⁻¹ (100%) | 0.001 - 0.15 | ✅ Consistent |
| **Plastic** | 6 | cm⁻¹ (67%) | 0.12 - 0.85 | Minor inconsistency |
| **Semiconductor** | 4 | Split | 1.0 - 8500 | ❌ Major inconsistency |
| **Composite** | 13 | cm⁻¹ (85%) | 0.15 - 8500 | ❌ One outlier |

---

## Physical Background

### What is Absorption Coefficient?

The **absorption coefficient** (α) measures how quickly light intensity decreases as it penetrates a material:

```
I(x) = I₀ × e^(-αx)
```

Where:
- I(x) = Intensity at depth x
- I₀ = Initial intensity
- α = Absorption coefficient
- x = Distance

### Standard Units

**Preferred Unit**: **cm⁻¹** (inverse centimeters)

**Conversion Table:**
| From | To cm⁻¹ | Multiplier |
|------|---------|------------|
| m⁻¹ | cm⁻¹ | ÷ 100 |
| μm⁻¹ | cm⁻¹ | × 10,000 |
| 1/μm | cm⁻¹ | × 10,000 |
| ×10⁴ cm⁻¹ | cm⁻¹ | × 10,000 |
| ×10⁵ cm⁻¹ | cm⁻¹ | × 100,000 |
| ×10⁷ m⁻¹ | cm⁻¹ | × 100,000 |

### Typical Ranges by Material Class

**Based on Laser Materials Processing literature:**

| Material | Typical α @ 1064nm (cm⁻¹) | Source |
|----------|---------------------------|---------|
| **Metals** | 10⁴ - 10⁷ | Very high absorption |
| **Semiconductors** | 10³ - 10⁵ | High absorption |
| **Ceramics** | 0.1 - 10 | Low to moderate |
| **Glass (transparent)** | 0.001 - 0.1 | Very low |
| **Polymers** | 0.1 - 10 | Low to moderate |
| **Wood** | 0.5 - 2 | Moderate |
| **Stone** | 0.1 - 1 | Low to moderate |

---

## Issues Identified

### 1. **Metal Values Incorrect**
```
Current: 0.03 - 12,000,000 (mixed units)
Should be: ~10,000 - 1,000,000 cm⁻¹
```

**Example Errors:**
- Copper: Listed as `1.2 ×10⁷ m⁻¹` = 120,000 cm⁻¹ ✅ Correct order
- Silver: Listed as `0.03 1/μm` = 300 cm⁻¹ ❌ Too low for metals
- Some metals using cm⁻¹ directly (0.45) ❌ Should be ×10⁴ or ×10⁵

### 2. **Semiconductor Values Inconsistent**
```
Silicon: 1.0 ×10⁴ cm⁻¹ (10,000) ✅
Silicon-Germanium: 8500 cm⁻¹ ✅
But mixed with plain cm⁻¹ values
```

### 3. **Unit Notation Errors**
- `dimensionless` - Wrong, should have units
- `cm^-1` - Formatting inconsistency
- `10⁵ cm⁻¹` - Missing × symbol
- `cm⁻¹ at 1064 nm` - Wavelength should be in description

---

## Recommended Corrections

### Step 1: Standardize to cm⁻¹

Convert all values to **cm⁻¹** as the standard unit.

### Step 2: Research-Based Ranges by Category

Based on laser materials processing literature (Steen & Mazumder, "Laser Material Processing"):

| Category | Min (cm⁻¹) | Max (cm⁻¹) | Notes |
|----------|-----------|-----------|--------|
| **metal** | 50,000 | 1,000,000 | High metallic absorption |
| **semiconductor** | 1,000 | 100,000 | Band gap dependent |
| **ceramic** | 0.1 | 10 | Low absorption (oxides) |
| **glass** | 0.001 | 1.0 | Transparent materials |
| **plastic** | 0.1 | 10 | Organic polymers |
| **wood** | 0.5 | 2.0 | Cellulose/lignin |
| **stone** | 0.1 | 1.0 | Mineral composition |
| **masonry** | 0.5 | 2.0 | Cement-based |
| **composite** | 0.1 | 10 | Matrix-dependent |

### Step 3: Fix Specific Material Values

**Metals** (should be ×10⁴ to ×10⁶ range):
- Copper: 120,000 cm⁻¹ ✅
- Aluminum: ~100,000 cm⁻¹
- Silver: ~300,000 cm⁻¹ (not 0.03!)
- Steel: ~50,000 cm⁻¹

**Semiconductors** (should be ×10³ to ×10⁵ range):
- Silicon: 10,000 cm⁻¹ ✅
- GaAs: 10,000 cm⁻¹ ✅
- Germanium: 50,000 cm⁻¹

---

## Recommended Actions

### Immediate Actions

1. **Remove from Frontmatter Generation** ✅ Already done (not in materials.yaml)
   - Property exists in frontmatter but shouldn't propagate with bad data

2. **Do NOT add to Categories.yaml ranges** until data is corrected
   - Current frontmatter data is too inconsistent

3. **Flag for Research** 
   - Needs comprehensive literature review
   - Requires wavelength-specific values (typically @ 1064 nm for Nd:YAG)

### Future Actions

1. **Research Campaign**: Gather authoritative absorption coefficient data
   - Source: "Laser Material Processing" (Steen & Mazumder, 4th Ed.)
   - Source: "Handbook of Optical Constants" (Palik, 1998)
   - Source: Material-specific laser processing papers

2. **Standardize Units**: Convert all to cm⁻¹

3. **Add to materials.yaml**: With proper values and sources

4. **Generate Category Ranges**: Once materials.yaml is corrected

---

## Current Recommendation

### ❌ DO NOT USE current absorptionCoefficient data

**Reasoning:**
1. 12 different unit variations indicate data entry errors
2. Values span 9 orders of magnitude incorrectly
3. No source verification in materials.yaml
4. Mixing wavelength-specific and general values

### ✅ RECOMMENDED PATH FORWARD

**Option A**: Remove absorptionCoefficient entirely until proper research is done
```yaml
# Remove from propertyCategories in Categories.yaml
# Remove from all frontmatter files
# Re-add later with researched values
```

**Option B**: Mark as "research needed" and exclude from range propagation
```yaml
# Keep in taxonomy but don't propagate to frontmatter
# Add note: "Requires wavelength-specific research"
```

**Option C**: Quick fix with literature-based estimates (NOT RECOMMENDED)
- Uses generic ranges, not material-specific
- Better than current inconsistent data but still not ideal

---

## Conclusion

The `absorptionCoefficient` property **should NOT have ranges calculated** from current data because:

1. ❌ Unit inconsistency (12 variations)
2. ❌ Value errors (wrong orders of magnitude)
3. ❌ No source verification
4. ❌ Not wavelength-specific

**Recommended**: Remove or mark for future research with proper authoritative sources.
