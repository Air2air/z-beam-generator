# Safety Data Table Structure Normalization

**Date**: January 2, 2026  
**Issue**: Duplicate table structures for hazardous compound data  
**Status**: ✅ Normalized

---

## 🎯 Problem Identified

The safety data schema had **duplicate table structures** for hazardous compound information:

### Before Normalization (Duplicate Structures)

**Structure 1**: `toxic_gas_risk.primary_hazards`
```yaml
toxic_gas_risk:
  items:
    - primary_hazards:
        - compound: "Chemical name"
          concentration_mg_m3: 0.5
          exposure_limit_mg_m3: 0.002
          hazard_class: carcinogenic
```

**Structure 2**: `fumes_generated` (items array)
```yaml
fumes_generated:
  items:
    - compound: "Chemical name"
      concentration_mg_m3: 0.5
      exposure_limit_mg_m3: 0.002
      hazard_class: carcinogenic
```

**Problem**: Same 4 fields, same data types, but documented as separate structures with different type names (`HazardCompound` vs `FumeCompound`).

---

## ✅ Solution: Unified Table Structure

### After Normalization (Single Structure)

**Unified Type**: `HazardousCompound`

```typescript
export interface HazardousCompound {
  compound: string;
  concentration_mg_m3: number;
  exposure_limit_mg_m3: number;
  hazard_class: 'carcinogenic' | 'toxic' | 'irritant' | 'corrosive';
}
```

**Used By**:
1. `toxic_gas_risk.primary_hazards: HazardousCompound[]` (nested array)
2. `fumes_generated.items: HazardousCompound[]` (top-level SafetySection)

---

## 📋 What Changed

### TypeScript Types (`types/safetyData.ts`)

**Removed**:
- `HazardCompound` interface (duplicate)
- `FumeCompound` interface (duplicate)

**Added**:
- `HazardousCompound` interface (unified, well-documented)

**Updated**:
```typescript
// Before
export interface ToxicGasRisk extends RiskAssessment {
  primary_hazards?: HazardCompound[];
}
// ...
export interface FumeCompound { ... }
// ...
fumes_generated?: SafetySection<FumeCompound>;

// After
export interface ToxicGasRisk extends RiskAssessment {
  primary_hazards?: HazardousCompound[];
}
// ...
fumes_generated?: SafetySection<HazardousCompound>;
```

### Documentation (`docs/SAFETY_DATA_NORMALIZATION_E2E.md`)

**Added**:
- Table Structure Normalization section
- Clear explanation of unified structure
- Comments in YAML examples linking the two uses

**Updated**:
- TypeScript interface documentation
- YAML structure examples with clarifying comments

---

## 🎓 Why This Matters

### 1. **Type Safety**
- Single source of truth for hazardous compound data
- No confusion about which type to use
- TypeScript catches errors at compile time

### 2. **Consistency**
- Same validation rules for all hazardous compound data
- Same rendering logic in components
- Same migration script handling

### 3. **Maintainability**
- Change structure once, applies everywhere
- No risk of structures drifting apart
- Clear intent: "hazardous compounds use this structure"

### 4. **Developer Experience**
- Obvious which type to import
- Auto-complete works correctly
- Less code to maintain

---

## 🔍 Usage Examples

### TypeScript Component

```typescript
import type { HazardousCompound, ToxicGasRisk } from '@/types/safetyData';

// Extract primary hazards from toxic gas risk
const toxicRisk = safetyData.toxic_gas_risk?.items[0];
const hazards: HazardousCompound[] = toxicRisk?.primary_hazards || [];

// Extract fumes generated
const fumes: HazardousCompound[] = safetyData.fumes_generated?.items || [];

// Both use same type - consistent handling
function renderHazardousCompounds(compounds: HazardousCompound[]) {
  return compounds.map(c => (
    <tr key={c.compound}>
      <td>{c.compound}</td>
      <td>{c.concentration_mg_m3} mg/m³</td>
      <td>{c.exposure_limit_mg_m3} mg/m³</td>
      <td>{c.hazard_class}</td>
    </tr>
  ));
}
```

### YAML Frontmatter

```yaml
relationships:
  safety:
    # Nested in risk assessment
    toxic_gas_risk:
      presentation: card
      items:
        - severity: moderate
          description: "Toxic fumes generated"
          mitigation: "Use PAPR with organic vapor cartridges"
          primary_hazards:  # HazardousCompound[]
            - compound: "Cadmium oxide"
              concentration_mg_m3: 0.5
              exposure_limit_mg_m3: 0.002
              hazard_class: carcinogenic
    
    # Top-level descriptive section
    fumes_generated:  # SafetySection<HazardousCompound>
      presentation: descriptive
      items:  # HazardousCompound[]
        - compound: "Cadmium oxide"
          concentration_mg_m3: 0.5
          exposure_limit_mg_m3: 0.002
          hazard_class: carcinogenic
```

---

## 📊 Field Definitions

### HazardousCompound

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `compound` | string | Chemical name | "Cadmium oxide" |
| `concentration_mg_m3` | number | Generated concentration in mg/m³ | 0.5 |
| `exposure_limit_mg_m3` | number | Safe exposure limit in mg/m³ | 0.002 |
| `hazard_class` | enum | Hazard classification | "carcinogenic" |

**Hazard Classes**:
- `carcinogenic` - Known or suspected cancer-causing agent
- `toxic` - Poisonous, causes health harm
- `irritant` - Causes irritation (eyes, skin, respiratory)
- `corrosive` - Causes chemical burns or material damage

---

## 🔄 Migration Impact

### Script Updates

The migration script (`scripts/migrate_safety_data.py`) already handles both fields correctly:

```python
# Both fields get same treatment
for field in ['fumes_generated', 'primary_hazards']:
    if field in safety_data:
        # Same validation rules
        # Same transformation logic
        # Same error handling
```

### Component Updates

No changes needed - `SafetyDataPanel` already extracts both fields using the same helper:

```typescript
const toxicHazards = extractSafetyItem(safetyData.toxic_gas_risk)?.primary_hazards;
const fumes = safetyData.fumes_generated?.items || [];
// Both are HazardousCompound[] now
```

---

## ✅ Validation

After normalization, validation ensures:

1. **Type Consistency**: Both fields use `HazardousCompound[]`
2. **Field Completeness**: All 4 required fields present
3. **Value Validation**: 
   - `compound`: Non-empty string
   - `concentration_mg_m3`: Positive number
   - `exposure_limit_mg_m3`: Positive number
   - `hazard_class`: Valid enum value

---

## 📚 Related Documentation

- **Main Spec**: [SAFETY_DATA_NORMALIZATION_E2E.md](./SAFETY_DATA_NORMALIZATION_E2E.md)
- **Type Definitions**: [types/safetyData.ts](../types/safetyData.ts)
- **Migration Script**: [scripts/migrate_safety_data.py](../scripts/migrate_safety_data.py)

---

## 🎯 Key Takeaways

1. **One Structure**: `HazardousCompound` for all hazardous compound data
2. **Two Uses**: `primary_hazards` (nested) and `fumes_generated` (top-level)
3. **Same Format**: 4 fields (compound, concentration, exposure limit, hazard class)
4. **Type Safe**: Single TypeScript interface with clear documentation
5. **Consistent**: Same validation, rendering, and migration handling

**Status**: ✅ Normalization complete and documented
