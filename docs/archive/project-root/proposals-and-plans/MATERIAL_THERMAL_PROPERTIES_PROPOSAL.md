# Material Thermal Properties Label Proposal

## Executive Summary

Currently, all materials use "melting point" (`meltingPoint`) in `materialProperties`, which is scientifically incorrect for materials that don't melt. This proposal outlines implementing dynamic property labels and field names based on material category, with proper scientific terminology and data structure modifications.

---

## Current State Analysis

### Database Structure (`data/Materials.yaml`)

Materials already have category-appropriate thermal destruction properties:

**Wood Materials** (Bamboo, Oak, Pine, Cedar, etc.):
- `thermalDestructionPoint`: 195-220°C (decomposition onset)
- `thermalDestructionType`: 280-350°C (carbonization threshold)

**Ceramic Materials** (Alumina, Porcelain, Titanium Carbide):
- `meltingPoint`: 2072-2715°C (sintering/decomposition point)

**Glass Materials** (Borosilicate, Pyrex):
- `thermalDestructionPoint`: 815-830°C (glass transition temperature)
- `thermalDestructionType`: 815-830°C (softening point)

**Composite Materials** (CFRP, GFRP, Epoxy):
- Properties stored but need proper thermal destruction labeling

**Metal Materials** (Aluminum, Steel, Copper):
- `meltingPoint`: True phase transition temperatures

**Stone Materials** (Granite, Marble, Limestone):
- Need thermal degradation point properties

### Frontmatter YAML Structure

```yaml
materialProperties:
  meltingPoint:       # ← INCORRECTLY LABELED FOR NON-METALS
    value: 280
    unit: °C
    confidence: 85
    description: Approximate pyrolysis temperature...
```

---

## Scientific Rationale by Category

### 🪵 Wood (20 materials)
**Materials**: Pine, Oak, Maple, Cedar, Bamboo, Ash, Beech, Birch, Cherry, Fir, Hickory, Mahogany, Poplar, Redwood, Rosewood, Teak, Walnut, Willow, Plywood, MDF

**Scientific Fact**: Wood undergoes **pyrolysis** (thermal decomposition), not melting
- **Hemicellulose breakdown**: 200-260°C
- **Cellulose decomposition**: 280-350°C  
- **Lignin degradation**: 300-500°C
- **Complete carbonization**: Above 400°C

**Proposed Label**: "Decomposition Point" or "Pyrolysis Point"
**Database Field**: `thermalDestructionPoint` (already exists)
**Typical Values**: 195-350°C

---

### 🏺 Ceramics (15 materials)
**Materials**: Porcelain, Brick, Cement, Stucco, Plaster, Mortar, Terracotta, Stoneware, Alumina, Silicon Carbide, Silicon Nitride, Titanium Carbide, Zirconia, Ceramic Matrix Composites

**Scientific Fact**: Ceramics undergo **sintering** (particle fusion) or **decomposition**, not melting
- **Sintering**: Particles fuse without becoming liquid
- **Decomposition**: Chemical bonds break at extreme temperatures
- **Phase transformation**: Structural changes without melting

**Proposed Label**: "Sintering/Decomposition Point"
**Database Field**: `meltingPoint` (repurposed) or new `sinteringPoint`
**Typical Values**: 1200-2715°C

---

### 🪨 Stone (15 materials) 
**Materials**: Granite, Marble, Limestone, Sandstone, Slate, Basalt, Bluestone, Breccia, Calcite, Onyx, Porphyry, Quartzite, Schist, Serpentine, Shale, Soapstone, Travertine

**Scientific Fact**: Rocks undergo **thermal degradation** (structural breakdown), not melting
- **Mineral decomposition**: 400-900°C (carbonates, clays)
- **Structural failure**: 600-1200°C (crystal structure collapse)
- **Partial melting**: Above 1200°C (only under extreme conditions)
- **Calcite to quicklime**: 825°C (limestone decomposition)

**Proposed Label**: "Thermal Degradation Point" or "Decomposition Point"
**Database Field**: New `thermalDegradationPoint` or repurpose `meltingPoint`
**Typical Values**: 400-1200°C

---

### 🧪 Polymers/Composites (12 materials)
**Materials**: Fiberglass (GFRP), Carbon Fiber (CFRP), Epoxy Resin Composites, Kevlar-Reinforced Polymer, Metal Matrix Composites, Ceramic Matrix Composites, Polyester Resin Composites, Phenolic Resin Composites, Urethane Composites, Fiber-Reinforced Polyurethane, Rubber, Thermoplastic Elastomer

**Scientific Fact**: Polymers undergo **chain scission** (molecular breakdown), not melting
- **Glass transition**: 50-200°C (softening, not melting)
- **Polymer decomposition**: 200-500°C (chain breakdown)
- **Filler retention**: Fibers remain after matrix degrades
- **Oxidative degradation**: Accelerated in air

**Proposed Label**: "Degradation Point" or "Decomposition Point"
**Database Field**: New `degradationPoint` or repurpose `thermalDestructionPoint`
**Typical Values**: 200-500°C

---

### 🔍 Glass (8 materials)
**Materials**: Pyrex, Borosilicate Glass, Float Glass, Tempered Glass, Crown Glass, Fused Silica, Gorilla Glass, Lead Crystal, Quartz Glass, Sapphire Glass, Soda-Lime Glass

**Scientific Fact**: Glass undergoes **gradual softening**, not sharp melting
- **Glass transition (Tg)**: 500-600°C (becomes pliable)
- **Softening point**: 700-850°C (flows under own weight)
- **Working point**: 1000-1500°C (easily shaped)
- **No sharp melting point**: Amorphous structure softens gradually

**Proposed Label**: "Softening Point" or "Glass Transition Point"
**Database Field**: `thermalDestructionPoint` (already exists) or new `softeningPoint`
**Typical Values**: 500-850°C

---

### ⚙️ Metals (35 materials)
**Materials**: Aluminum, Steel, Stainless Steel, Copper, Brass, Bronze, Titanium, Gold, Silver, Platinum, Iron, Nickel, Zinc, Lead, Tin, Chromium, Cobalt, Manganese, Molybdenum, Tungsten, Vanadium, Beryllium, Gallium, Hafnium, Hastelloy, Inconel, Indium, Iridium, Magnesium, Niobium, Palladium, Rhenium, Rhodium, Ruthenium, Tantalum, Zirconium

**Scientific Fact**: Metals undergo **true phase transition** to liquid state
- **Crystalline structure**: Sharp melting point
- **Phase change**: Solid → Liquid at specific temperature
- **Latent heat**: Energy absorbed during transition
- **Reversible**: Solidifies at same temperature

**Proposed Label**: "Melting Point" (unchanged)
**Database Field**: `meltingPoint` (unchanged)
**Typical Values**: 29.76°C (Gallium) to 3422°C (Tungsten)

---

### 🔬 Semiconductors (4 materials)
**Materials**: Silicon, Gallium Arsenide, Silicon Germanium, Silicon Carbide

**Scientific Fact**: Semiconductors have **true melting points** (crystalline materials)
- **Silicon**: 1414°C (sharp melting point)
- **Gallium Arsenide**: 1238°C (congruent melting)
- **Silicon Carbide**: 2830°C (decomposes before melting)

**Proposed Label**: "Melting Point" or "Decomposition Point" (SiC)
**Database Field**: `meltingPoint` (unchanged for Si, GaAs) or `decompositionPoint` (SiC)
**Typical Values**: 1238-2830°C

---

## Proposed Implementation

### Phase 1: Database Schema Addition

Add new fields to `data/Materials.yaml` property groups:

```yaml
property_groups:
  thermalProperties:
    - thermalConductivity
    - thermalExpansion
    - specificHeat
    - meltingPoint              # Metals, semiconductors
    - thermalDestructionPoint   # Wood, glass, polymers
    - thermalDestructionType    # Wood (pyrolysis vs carbonization)
    - sinteringPoint            # Ceramics
    - thermalDegradationPoint   # Stone
    - degradationPoint          # Polymers/composites
    - softeningPoint            # Glass (alternative to thermalDestructionPoint)
```

### Phase 2: Material-Specific Mapping

Create category-to-property mapping:

```python
THERMAL_PROPERTY_MAP = {
    'wood': {
        'field': 'thermalDestructionPoint',
        'label': 'Decomposition Point',
        'description': 'Temperature where pyrolysis (thermal decomposition) begins',
        'scientific_process': 'Pyrolysis'
    },
    'ceramic': {
        'field': 'sinteringPoint',  # or 'meltingPoint' if already correct
        'label': 'Sintering/Decomposition Point',
        'description': 'Temperature where ceramic particles fuse or decompose',
        'scientific_process': 'Sintering or Decomposition'
    },
    'stone': {
        'field': 'thermalDegradationPoint',
        'label': 'Thermal Degradation Point',
        'description': 'Temperature where mineral structure breaks down',
        'scientific_process': 'Thermal Degradation'
    },
    'composite': {
        'field': 'degradationPoint',
        'label': 'Degradation Point',
        'description': 'Temperature where polymer matrix decomposes',
        'scientific_process': 'Polymer Decomposition'
    },
    'plastic': {
        'field': 'degradationPoint',
        'label': 'Degradation Point',
        'description': 'Temperature where polymer chains break down',
        'scientific_process': 'Polymer Decomposition'
    },
    'glass': {
        'field': 'softeningPoint',  # or 'thermalDestructionPoint'
        'label': 'Softening Point',
        'description': 'Temperature where glass transitions from rigid to pliable state',
        'scientific_process': 'Glass Transition'
    },
    'metal': {
        'field': 'meltingPoint',
        'label': 'Melting Point',
        'description': 'Temperature where solid metal transitions to liquid phase',
        'scientific_process': 'Phase Transition'
    },
    'semiconductor': {
        'field': 'meltingPoint',  # or 'decompositionPoint' for SiC
        'label': 'Melting Point',
        'description': 'Temperature where crystalline structure melts',
        'scientific_process': 'Phase Transition'
    },
    'masonry': {  # Brick, cement, concrete
        'field': 'thermalDegradationPoint',
        'label': 'Thermal Degradation Point',
        'description': 'Temperature where structural integrity fails',
        'scientific_process': 'Thermal Degradation'
    }
}
```

### Phase 3: Generator Code Modification

Update `components/frontmatter/core/streamlined_generator.py`:

```python
def _get_thermal_property_info(self, category: str) -> dict:
    """Get appropriate thermal property field and label based on material category."""
    return THERMAL_PROPERTY_MAP.get(category.lower(), THERMAL_PROPERTY_MAP['metal'])

def _extract_thermal_property(self, material_data: dict, category: str) -> dict:
    """Extract appropriate thermal property based on material category."""
    thermal_info = self._get_thermal_property_info(category)
    field_name = thermal_info['field']
    
    # Check Material.yaml for the appropriate field
    properties = material_data.get('properties', {})
    thermal_props = material_data.get('thermalProperties', {})
    
    # Try multiple potential sources
    value = None
    if field_name in properties:
        value = properties[field_name]
    elif field_name in thermal_props:
        value = thermal_props[field_name]
    elif 'meltingPoint' in thermal_props:  # Fallback for backward compatibility
        value = thermal_props['meltingPoint']
    
    return {
        'field': field_name,
        'label': thermal_info['label'],
        'value': value,
        'description': thermal_info['description']
    }
```

### Phase 4: Frontmatter YAML Schema Update

Modify frontmatter generation to use dynamic property names:

**Current** (all materials):
```yaml
materialProperties:
  meltingPoint:
    value: 280
    unit: °C
```

**Proposed** (category-specific):

**Wood**:
```yaml
materialProperties:
  decompositionPoint:  # or thermalDestructionPoint
    value: 280
    unit: °C
    confidence: 85
    description: Pyrolysis temperature where thermal decomposition begins
```

**Ceramic**:
```yaml
materialProperties:
  sinteringPoint:
    value: 2072
    unit: °C
    confidence: 95
    description: Temperature where ceramic particles fuse or decompose
```

**Stone**:
```yaml
materialProperties:
  thermalDegradationPoint:
    value: 900
    unit: °C
    confidence: 90
    description: Temperature where mineral structure breaks down
```

**Glass**:
```yaml
materialProperties:
  softeningPoint:
    value: 821
    unit: °C
    confidence: 95
    description: Glass transition temperature where material becomes pliable
```

**Metal** (unchanged):
```yaml
materialProperties:
  meltingPoint:
    value: 660
    unit: °C
    confidence: 98
    description: Temperature where solid metal transitions to liquid phase
```

### Phase 5: Frontend Display Logic

The Next.js frontend already handles this correctly by using category-based label mapping. Ensure consistency:

```typescript
// Frontend (already implemented)
function getThermalPropertyLabel(category: string): string {
  const labelMap = {
    'wood': 'Decomposition Point',
    'ceramic': 'Sintering/Decomposition Point',
    'stone': 'Thermal Degradation Point',
    'composite': 'Degradation Point',
    'plastic': 'Degradation Point',
    'glass': 'Softening Point',
    'metal': 'Melting Point',
    'semiconductor': 'Melting Point',
    'masonry': 'Thermal Degradation Point'
  };
  return labelMap[category.toLowerCase()] || 'Melting Point';
}
```

---

## Data Migration Strategy

### Option A: Dual-Field Approach (Recommended)

**Advantages**:
- Backward compatible
- Gradual migration
- Frontend can choose appropriate field

**Implementation**:
1. Keep existing `meltingPoint` field
2. Add category-specific fields alongside
3. Frontend reads category-specific field first, falls back to `meltingPoint`
4. Eventually deprecate `meltingPoint` for non-metals

**Example (Wood)**:
```yaml
materialProperties:
  meltingPoint:              # Deprecated but present for compatibility
    value: 280
    unit: °C
  decompositionPoint:        # New, correct field
    value: 280
    unit: °C
    confidence: 85
    description: Pyrolysis temperature...
```

### Option B: Single-Field Approach

**Advantages**:
- Cleaner data structure
- No duplication
- Forces scientific accuracy

**Implementation**:
1. Replace `meltingPoint` with category-specific field
2. Update all frontmatter YAML files
3. Update generator code
4. Update frontend to read new field names

**Example (Wood)**:
```yaml
materialProperties:
  decompositionPoint:        # Replaces meltingPoint
    value: 280
    unit: °C
```

---

## Detailed Material Breakdown

### Current Database Analysis

| Category | Materials | Current Field | Proposed Field | Typical Range |
|----------|-----------|---------------|----------------|---------------|
| Wood | 20 | `meltingPoint` | `thermalDestructionPoint` | 195-350°C |
| Ceramic | 9 | `meltingPoint` | `sinteringPoint` | 1200-2715°C |
| Stone | 17 | `meltingPoint` (missing) | `thermalDegradationPoint` | 400-1200°C |
| Composite | 10 | Various | `degradationPoint` | 200-500°C |
| Plastic | 6 | Various | `degradationPoint` | 200-400°C |
| Glass | 11 | `thermalDestructionPoint` | `softeningPoint` | 500-850°C |
| Metal | 35 | `meltingPoint` | `meltingPoint` (unchanged) | 30-3422°C |
| Semiconductor | 4 | `meltingPoint` | `meltingPoint` | 1238-2830°C |
| Masonry | 9 | `meltingPoint` (missing) | `thermalDegradationPoint` | 600-1200°C |

### Materials Requiring Data Addition

**Stone materials currently missing thermal properties**:
- Granite, Marble, Limestone, Sandstone, Slate, Basalt, etc.
- Need to add `thermalDegradationPoint` from research data

**Masonry materials missing thermal properties**:
- Brick, Cement, Concrete, Mortar, Stucco, Plaster
- Need to add `thermalDegradationPoint` from research data

---

## Recommended Action Plan

### Immediate (Week 1)
1. ✅ Document current state (this proposal)
2. ⬜ Review with team for scientific accuracy
3. ⬜ Choose migration strategy (Option A recommended)
4. ⬜ Create category-to-field mapping in generator code

### Short-term (Week 2-3)
5. ⬜ Add new property fields to database schema
6. ⬜ Research and add missing thermal properties for stone/masonry
7. ⬜ Update generator to use dynamic field selection
8. ⬜ Generate test frontmatter for all categories

### Medium-term (Week 4-6)
9. ⬜ Regenerate all 122 frontmatter YAML files with correct fields
10. ⬜ Update documentation and schemas
11. ⬜ Deploy and verify frontend displays correct labels
12. ⬜ Run validation tests across all materials

### Long-term (Future)
13. ⬜ Deprecate `meltingPoint` for non-metal categories
14. ⬜ Remove backward compatibility fields
15. ⬜ Add educational tooltips explaining the science

---

## Scientific References

### Wood Pyrolysis
- Antal, M. J., & Varhegyi, G. (1995). "Cellulose pyrolysis kinetics: The current state of knowledge." *Industrial & Engineering Chemistry Research*, 34(3), 703-717.
- Li et al. (2021). "Thermal degradation behavior of bamboo: A review." *Journal of Materials Science*, 56, 9021-9046.

### Ceramic Sintering
- German, R. M. (1996). *Sintering Theory and Practice*. Wiley-Interscience.
- ASM Handbook, Volume 4: Ceramics and Glasses (1991).

### Stone Thermal Degradation
- Hajpál, M., & Török, Á. (2004). "Mineralogical and colour changes of quartz sandstones by heat." *Environmental Geology*, 46(3-4), 311-322.
- Dwivedi, A., et al. (2008). "Thermo-mechanical properties of Indian and other granites." *International Journal of Rock Mechanics and Mining Sciences*, 45(3), 303-315.

### Polymer Decomposition
- Pielichowski, K., & Njuguna, J. (2005). *Thermal Degradation of Polymeric Materials*. Rapra Technology.
- NIST Polymer Database: https://polymerdatabase.com/

### Glass Transition
- Scholze, H. (1991). *Glass: Nature, Structure, and Properties*. Springer-Verlag.
- ASTM C1468-19: Standard Specification for Glass and Glass Ceramics.

---

## Conclusion

Implementing category-specific thermal property labels is essential for scientific accuracy and user education. The dual-field migration strategy (Option A) provides the best balance of compatibility and correctness, allowing gradual transition while maintaining system stability.

**Key Benefits**:
- ✅ Scientific accuracy across all 122 materials
- ✅ Educational value for users
- ✅ Backward compatible during migration
- ✅ Leverages existing database structure
- ✅ Frontend already supports dynamic labels

**Next Steps**:
1. Team review and approval
2. Choose migration strategy
3. Begin implementation with generator code updates

