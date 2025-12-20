# Safety Risk/Severity Schema Normalization Plan
**Date**: December 20, 2025  
**Schema Reference**: `docs/SAFETY_RISK_SEVERITY_SCHEMA.md`

## Current State Analysis

### 1. Relationship Severity Fields ✅ COMPLIANT
**Location**: `frontmatter/materials/*.yaml` → `relationships.contaminants[].severity`

**Current values found**: `low`, `high`, `moderate`  
**Status**: ✅ Already using standardized schema values
**Count**: 2,142 relationships across 153 materials

**Example (porcelain-laser-cleaning.yaml)**:
```yaml
relationships:
  contaminants:
    groups:
      organic_residues:
        items:
        - id: environmental-dust-contamination
          severity: low        # ✅ Schema compliant
        - id: paint-removal-contamination  
          severity: high       # ✅ Schema compliant
```

**Action**: ✅ No changes needed - already compliant

---

### 2. Safety Data Structure ⚠️ PARTIAL COMPLIANCE

**Location**: `frontmatter/contaminants/*.yaml` → `safety_data`

**Current structure** (non-standard):
```yaml
safety_data:
  fire_explosion_risk: "moderate"     # ✅ Risk level compliant
  fumes_generated: [...]              # ❌ Non-standard field
  particulate_generation:             # ⚠️ Partial compliance
    respirable_fraction: 0.8          # ✅ Schema compliant
    size_range_um: [0.1, 10.0]        # ✅ Schema compliant
  ppe_requirements:                   # ❌ Non-standard values
    eye_protection: "goggles"         # ❌ Should be "Safety Goggles"
    respiratory: "dust_mask"          # ❌ Should be "N95 Respirator" or "P100 Respirator"
    skin_protection: "gloves"         # ❌ Should be "Leather Gloves" or specific type
```

**Schema-compliant structure** (target):
```yaml
safety_data:
  # Risk Assessment (required)
  fire_explosion_risk: "moderate"              # ✅ Already compliant
  toxic_gas_risk: "high"                       # ❌ MISSING FIELD
  visibility_hazard: "moderate"                # ❌ MISSING FIELD
  
  # PPE Requirements (required - needs standardization)
  ppe_requirements:
    respiratory: "P100 Respirator"             # ❌ Needs standardization
    eye_protection: "Safety Goggles"           # ❌ Needs standardization
    skin_protection: "Leather Gloves"          # ❌ Needs standardization
  
  # Ventilation Requirements (required for moderate+ risks)
  ventilation_requirements:                    # ❌ MISSING SECTION
    minimum_air_changes_per_hour: 12
    exhaust_velocity_m_s: 0.75
    filtration_type: "HEPA + Activated Carbon"
  
  # Particulate Generation (required)
  particulate_generation:                      # ✅ Already present
    respirable_fraction: 0.8                   # ✅ Compliant
    size_range_um: [0.1, 10.0]                 # ✅ Compliant
  
  # Substrate Compatibility Warnings (optional)
  substrate_compatibility_warnings:            # ❌ MISSING SECTION
    - "May cause discoloration on painted surfaces"
```

---

## Required Normalization Work

### Priority 1: Add Missing Required Fields (CRITICAL)

**Target**: All contaminants with `safety_data` section

**Missing fields to add**:
1. `toxic_gas_risk` - Derive from `fumes_generated` hazard classes
2. `visibility_hazard` - Infer from particulate generation
3. `ventilation_requirements` - Calculate from risk levels

**Logic**:
```python
def derive_toxic_gas_risk(fumes_generated):
    """Derive toxic_gas_risk from fumes_generated hazard classes"""
    hazard_classes = [f['hazard_class'] for f in fumes_generated]
    
    if 'carcinogenic' in hazard_classes or 'highly_toxic' in hazard_classes:
        return 'critical'
    elif 'toxic' in hazard_classes:
        return 'high'
    elif 'irritant' in hazard_classes:
        return 'moderate'
    else:
        return 'low'

def derive_visibility_hazard(respirable_fraction):
    """Derive visibility_hazard from particulate generation"""
    if respirable_fraction >= 0.7:
        return 'high'
    elif respirable_fraction >= 0.4:
        return 'moderate'
    else:
        return 'low'

def calculate_ventilation_requirements(fire_risk, toxic_gas_risk, visibility_hazard):
    """Calculate ventilation based on risk levels"""
    max_risk = max([fire_risk, toxic_gas_risk, visibility_hazard], 
                   key=lambda r: ['low', 'moderate', 'high', 'critical'].index(r))
    
    if max_risk == 'critical':
        return {
            'minimum_air_changes_per_hour': 20,
            'exhaust_velocity_m_s': 1.2,
            'filtration_type': 'HEPA + Activated Carbon'
        }
    elif max_risk == 'high':
        return {
            'minimum_air_changes_per_hour': 15,
            'exhaust_velocity_m_s': 1.0,
            'filtration_type': 'HEPA + Activated Carbon'
        }
    elif max_risk == 'moderate':
        return {
            'minimum_air_changes_per_hour': 12,
            'exhaust_velocity_m_s': 0.75,
            'filtration_type': 'HEPA Filtration'
        }
    else:  # low
        return {
            'minimum_air_changes_per_hour': 8,
            'exhaust_velocity_m_s': 0.5,
            'filtration_type': 'Mechanical Filtration'
        }
```

---

### Priority 2: Standardize PPE Values (HIGH)

**Current non-standard values** → **Schema-compliant values**:

| Current | Standardized |
|---------|-------------|
| `goggles` | `Safety Goggles` |
| `dust_mask` | `N95 Respirator` (low risk) or `P100 Respirator` (high respirable fraction) |
| `gloves` | `Leather Gloves` (heat/abrasion) or `Chemical-Resistant Gloves` (toxic) |

**Logic**:
```python
def standardize_respiratory(current_value, respirable_fraction, toxic_gas_risk):
    """Standardize respiratory protection value"""
    if toxic_gas_risk in ['critical', 'high']:
        if toxic_gas_risk == 'critical':
            return 'SCBA Required'
        else:
            return 'Full-Face Respirator'
    elif respirable_fraction >= 0.6:
        return 'P100 Respirator'
    else:
        return 'N95 Respirator'

def standardize_eye_protection(current_value, fire_risk):
    """Standardize eye protection value"""
    if fire_risk in ['critical', 'high']:
        return 'Combination (Goggles + Shield)'
    elif current_value in ['goggles', 'safety goggles']:
        return 'Safety Goggles'
    else:
        return 'Safety Glasses'

def standardize_skin_protection(current_value, toxic_gas_risk):
    """Standardize skin protection value"""
    if toxic_gas_risk in ['critical', 'high']:
        return 'Chemical-Resistant Gloves'
    elif current_value in ['gloves', 'leather gloves']:
        return 'Leather Gloves'
    else:
        return 'Leather Gloves'
```

---

### Priority 3: Add Substrate Compatibility Warnings (OPTIONAL)

**Target**: Contaminants with known substrate issues

This can be populated gradually based on:
- Known material interactions from `fumes_generated` data
- Regulatory warnings from compound hazard data
- User-reported issues

**Example**:
```yaml
substrate_compatibility_warnings:
  - "Generates highly toxic lead fumes"  # If lead compounds present
  - "May damage thin aluminum substrates (<2mm)"  # If thermal shock risk
  - "Requires sealed enclosure for indoor use"  # If visibility hazard is high
```

---

## Implementation Strategy

### Step 1: Create Normalization Script

**File**: `scripts/maintenance/normalize_safety_data.py`

**Features**:
- Read all contaminant frontmatter files
- Derive missing fields from existing data
- Standardize PPE values
- Calculate ventilation requirements
- Add substrate warnings (where applicable)
- Validate against schema
- Write back to frontmatter files

### Step 2: Dry Run Validation

Run script with `--dry-run` flag to:
- Show proposed changes for each file
- Identify any edge cases
- Generate change summary report

### Step 3: Apply Changes

Run script in update mode to:
- Backup original files
- Apply normalization changes
- Log all modifications
- Generate completion report

### Step 4: Verification

- Check sample files manually
- Run schema validator
- Verify UI components render correctly with new data

---

## Files Requiring Normalization

**Estimate**: 98 contaminant files  
**Complexity**: Medium (derive from existing data + standardize values)  
**Time**: ~30 minutes to write script, ~5 minutes to execute

**Current non-compliant files** (sample):
- `water-stain-contamination.yaml` - Missing toxic_gas_risk, visibility_hazard, ventilation
- `hydraulic-fluid-contamination.yaml` - Non-standard PPE values
- `plastic-residue-contamination.yaml` - Missing ventilation requirements
- `carbon-soot-contamination.yaml` - Missing toxic_gas_risk field
- `quench-oil-contamination.yaml` - Non-standard PPE values

---

## Expected Outcome

After normalization:
- ✅ **100% schema compliance** across all safety data
- ✅ **Consistent risk vocabulary** (critical/high/moderate/low)
- ✅ **Standardized PPE values** matching UI expectations
- ✅ **Complete ventilation data** for all contaminants
- ✅ **Validated data structure** for RiskCard/InfoCard components

**Benefits**:
- Reliable UI component rendering
- Consistent safety communication
- Easier filtering/sorting by risk level
- Compliance with regulatory display requirements
- Future-proof data structure for safety features

