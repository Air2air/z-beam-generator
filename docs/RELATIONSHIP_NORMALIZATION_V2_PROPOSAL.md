# Relationship Normalization V2 Proposal
**Date**: December 22, 2025  
**Status**: PROPOSAL - Universal Section Schema + Display Metadata  
**Purpose**: Normalize data-frontend relationships for zero-friction rendering

---

## 🎯 Goals

1. **Relationship Display Metadata** - Include section rendering hints in data
2. **Universal Section Schema** - All domains follow same pattern
3. **Zero Frontend Logic** - Data drives display, not hardcoded conditions
4. **Backward Compatible** - Gradual migration, no breaking changes

---

## 📋 Normalized Relationship Structure

### Current (Minimal Refs Only)
```yaml
relationships:
  produces_compounds:
  - id: hydrogen-chloride-compound
    frequency: common
    severity: high
```

### Proposed (With Display Metadata)
```yaml
relationships:
  produces_compounds:
    _section:
      title: "Compounds Produced"
      description: "Hazardous compounds released during laser cleaning"
      order: 2
      variant: "relationship"
      icon: "beaker"
    items:
    - id: hydrogen-chloride-compound
      frequency: common
      severity: high
      typical_context: "PVC decomposition"
```

---

## 🏗️ Universal Section Schema

### Section Wrapper Structure

Every relationship that renders as a section uses this wrapper:

```yaml
relationship_key:
  _section:                    # Section metadata (prefixed with _ to distinguish)
    title: string              # REQUIRED: Display heading
    description: string        # Optional: Section description  
    order: number              # Optional: Render order (lower = earlier)
    variant: string            # Optional: Display variant (relationship|info|grid)
    icon: string               # Optional: Icon identifier
    condition: string          # Optional: Render condition expression
    component: string          # Optional: Override component type
  items: array                 # REQUIRED: Relationship items (minimal refs)
```

### Benefits

✅ **Data-Driven Sections** - Frontend reads section config from data  
✅ **No Hardcoded Titles** - All titles come from `_section.title`  
✅ **Flexible Ordering** - `order` field controls section sequence  
✅ **Consistent Structure** - Same pattern across all domains  
✅ **Easy to Extend** - Add new relationships without frontend changes

---

## 📊 Domain Examples

### Compounds Domain

```yaml
# File: ammonia-compound.yaml
relationships:
  
  # Chemical properties section
  chemical_properties:
    _section:
      title: "Chemical Properties"
      description: "Physical and chemical characteristics"
      order: 1
      variant: "info"
      icon: "beaker"
    items:
    - type: chemical_properties
      id: ammonia-physical-data
  
  # Source contaminants section
  produced_from_contaminants:
    _section:
      title: "Contaminant Sources"
      description: "Contaminants that produce this compound during laser cleaning"
      order: 2
      variant: "relationship"
      icon: "droplet"
    items:
    - id: blood-residue-contamination
      frequency: occasional
      severity: low
      typical_context: "Breakdown of proteins"
      url: /contaminants/biological/deposit/blood-residue-contamination
  
  # Source materials section
  produced_from_materials:
    _section:
      title: "Material Sources"
      description: "Materials that release this compound when laser cleaned"
      order: 3
      variant: "relationship"
      icon: "layers"
    items:
    - id: ceramic-matrix-composites-cmcs-laser-cleaning
      url: /materials/composite/fiber-reinforced/ceramic-matrix-composites-cmcs-laser-cleaning
    - id: epoxy-resin-composites-laser-cleaning
      url: /materials/composite/fiber-reinforced/epoxy-resin-composites-laser-cleaning
  
  # Safety section
  ppe_requirements:
    _section:
      title: "Safety Requirements"
      description: "Personal protective equipment and safety protocols"
      order: 4
      variant: "safety"
      icon: "shield"
    items:
    - type: ppe_requirements
      id: corrosive-liquid-moderate
      overrides:
        specific_compound: Ammonia
        pel_ppm: 50
```

### Contaminants Domain

```yaml
# File: algae-growth-contamination.yaml
relationships:
  
  # Compounds produced section
  produces_compounds:
    _section:
      title: "Compounds Produced"
      description: "Hazardous compounds released during laser removal"
      order: 1
      variant: "relationship"
      icon: "flask"
    items:
    - id: acetaldehyde-compound
      phase: vapor
      hazard_level: moderate
      url: /compounds/volatile-organic/aldehyde/acetaldehyde-compound
    - id: acrolein-compound
      phase: vapor
      hazard_level: high
      url: /compounds/volatile-organic/unsaturated-aldehyde/acrolein-compound
  
  # Materials section
  found_on_materials:
    _section:
      title: "Common Substrates"
      description: "Materials where this contamination typically occurs"
      order: 2
      variant: "relationship"
      icon: "layers"
    items:
    - id: aluminum-laser-cleaning
      url: /materials/metal/non-ferrous/aluminum-laser-cleaning
    - id: brass-laser-cleaning
      url: /materials/metal/alloy/brass-laser-cleaning
  
  # Standards section
  regulatory_standards:
    _section:
      title: "Regulatory Standards"
      description: "Applicable industry standards and regulations"
      order: 3
      variant: "info"
      icon: "book"
    items:
    - type: regulatory_standards
      id: iso-9001-quality-standard
    - type: regulatory_standards
      id: osha-hazmat-guidelines
```

### Materials Domain

```yaml
# File: aluminum-laser-cleaning.yaml
relationships:
  
  # Contamination section
  contaminated_by:
    _section:
      title: "Common Contaminants"
      description: "Contaminants typically removed from this material"
      order: 1
      variant: "relationship"
      icon: "droplet"
    items:
    - id: oil-grease-contamination
      frequency: very_common
      severity: moderate
      url: /contaminants/organic/hydrocarbon/oil-grease-contamination
    - id: oxidation-layer-contamination
      frequency: common
      severity: low
      url: /contaminants/chemical/corrosion/oxidation-layer-contamination
```

### Settings Domain

```yaml
# File: high-power-pulsed-setting.yaml
relationships:
  
  # Optimized materials section
  optimized_for_materials:
    _section:
      title: "Optimized For"
      description: "Materials best suited for this setting"
      order: 1
      variant: "relationship"
      icon: "target"
    items:
    - id: steel-laser-cleaning
      effectiveness: excellent
      url: /materials/metal/ferrous/steel-laser-cleaning
    - id: titanium-laser-cleaning
      effectiveness: excellent
      url: /materials/metal/non-ferrous/titanium-laser-cleaning
  
  # Removal capabilities section
  removes_contaminants:
    _section:
      title: "Removes"
      description: "Contaminants effectively removed by this setting"
      order: 2
      variant: "relationship"
      icon: "zap"
    items:
    - id: rust-contamination
      effectiveness: excellent
      url: /contaminants/chemical/corrosion/rust-contamination
    - id: paint-contamination
      effectiveness: good
      url: /contaminants/coating/organic/paint-contamination
```

---

## 🎨 Frontend Integration

### Universal Section Renderer

```typescript
// app/components/UniversalSection/UniversalSection.tsx
interface UniversalSectionProps {
  sectionKey: string;
  sectionData: {
    _section: {
      title: string;
      description?: string;
      order?: number;
      variant?: 'relationship' | 'info' | 'grid' | 'safety';
      icon?: string;
      condition?: string;
      component?: string;
    };
    items: any[];
  };
  metadata: any;
}

export function UniversalSection({ sectionKey, sectionData, metadata }: UniversalSectionProps) {
  const { _section, items } = sectionData;
  
  // Skip if no items
  if (!items || items.length === 0) return null;
  
  // Evaluate condition if specified
  if (_section.condition && !evaluateCondition(_section.condition, metadata)) {
    return null;
  }
  
  // Select component based on variant
  const Component = selectComponent(_section.variant || 'relationship', _section.component);
  
  return (
    <SectionContainer
      title={_section.title}
      icon={getIcon(_section.icon)}
      className="mb-8"
    >
      {_section.description && (
        <p className="text-muted mb-4">{_section.description}</p>
      )}
      <Component items={items} metadata={metadata} />
    </SectionContainer>
  );
}
```

### Updated Layout Components

```typescript
// app/components/CompoundsLayout/CompoundsLayout.tsx
export async function CompoundsLayout(props: CompoundsLayoutProps) {
  const { metadata } = props;
  const relationships = metadata?.relationships || {};
  
  // Extract sections from relationships
  const sections = Object.entries(relationships)
    .filter(([_, value]) => value?._section)
    .map(([key, value]) => ({
      key,
      data: value,
      order: value._section?.order || 999
    }))
    .sort((a, b) => a.order - b.order);
  
  return (
    <BaseContentLayout {...props}>
      {sections.map(section => (
        <UniversalSection
          key={section.key}
          sectionKey={section.key}
          sectionData={section.data}
          metadata={metadata}
        />
      ))}
      <ScheduleCards />
    </BaseContentLayout>
  );
}
```

---

## 🔄 Migration Strategy

### Phase 1: Backend Generation (Week 1)
- [ ] Update export enrichers to add `_section` metadata
- [ ] Create section config per domain in export/config/*.yaml
- [ ] Regenerate all frontmatter with new structure
- [ ] Verify backward compatibility (items still at top level for old frontend)

### Phase 2: Frontend Universal Components (Week 2)
- [ ] Create UniversalSection component
- [ ] Update layouts to read `_section` metadata
- [ ] Test with compounds domain (pilot)
- [ ] Rollout to contaminants, materials, settings

### Phase 3: Cleanup (Week 3)
- [ ] Remove hardcoded section titles from layouts
- [ ] Remove conditional logic from layouts
- [ ] Delete domain-specific section components
- [ ] Consolidate to universal components

---

## 📝 Section Configuration Examples

### Backend Config (export/config/compounds.yaml)

```yaml
# export/config/compounds.yaml
sections:
  chemical_properties:
    title: "Chemical Properties"
    description: "Physical and chemical characteristics"
    order: 1
    variant: "info"
    icon: "beaker"
    condition: "has_chemical_properties"
  
  produced_from_contaminants:
    title: "Contaminant Sources"
    description: "Contaminants that produce this compound during laser cleaning"
    order: 2
    variant: "relationship"
    icon: "droplet"
    condition: "has_produced_from_contaminants"
  
  produced_from_materials:
    title: "Material Sources"
    description: "Materials that release this compound when laser cleaned"
    order: 3
    variant: "relationship"
    icon: "layers"
    condition: "has_produced_from_materials"
  
  ppe_requirements:
    title: "Safety Requirements"
    description: "Personal protective equipment and safety protocols"
    order: 4
    variant: "safety"
    icon: "shield"
    condition: "has_ppe_requirements"
```

---

## ✅ Benefits Summary

| Benefit | Current | Proposed |
|---------|---------|----------|
| **Section Titles** | Hardcoded in layout | Driven by data |
| **Section Order** | Hardcoded sequence | `order` field controls |
| **Conditional Logic** | Frontend code checks | Data includes condition |
| **New Relationships** | Requires frontend changes | Add to config only |
| **Cross-Domain Consistency** | Each domain different | Universal pattern |
| **Maintenance Effort** | High (2 systems) | Low (data-driven) |

---

## 🚀 Next Steps

1. **Review & Approve** - Validate this approach
2. **Create Section Configs** - Define per-domain section metadata
3. **Update Export System** - Add section wrapper generation
4. **Pilot with Compounds** - Test with one domain first
5. **Gradual Rollout** - Expand to all domains
6. **Frontend Migration** - Update layouts to universal components

---

## 📚 Related Documents

- `RELATIONSHIP_DATA_SPECIFICATION.md` - Current minimal ref spec (V1)
- `export/config/*.yaml` - Domain export configurations
- `app/components/*/Layout.tsx` - Current layout implementations
