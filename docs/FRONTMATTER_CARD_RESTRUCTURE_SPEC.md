# Frontmatter Card & Relationship Restructure Specification

**Date:** December 22, 2025  
**Status:** Specification  
**Priority:** High - Major refactor of frontmatter structure  
**Estimated Impact:** ~3.1% reduction in frontmatter size (315KB), significant architectural improvement

---

## Executive Summary

This specification defines a major restructuring of frontmatter to:
1. **Add card presentation data** - Each entity defines how it appears in card UI
2. **Move to ID-based lookups** - Replace redundant data with entity references
3. **Move presentation to key level** - Apply presentation type to all items in a relationship
4. **Use full_path for URLs** - Derive URLs from canonical full_path field

**Benefits:**
- **DRY principle**: Single source of truth for all entity data
- **Maintainability**: Update entity once, changes propagate everywhere
- **Cleaner frontmatter**: 6,714 fewer `presentation: card` lines, 3,357+ fewer URL duplications
- **Architectural clarity**: Clear separation between entity data and relationship metadata

---

## Part 1: Card Schema

### 1.1 Card Section Structure

Every entity frontmatter (materials, contaminants, compounds, settings) MUST include a `card:` section defining how it appears in various UI contexts.

```yaml
card:
  default:
    heading: string           # Required - displays at bottom of card
    subtitle: string          # Required - displays under heading
    badge:
      text: string           # Required - badge text
      variant: string        # Required - success|warning|danger|info|technical
    metric:
      value: string          # Required - bold numerical value
      unit: string           # Optional - unit of measurement
      legend: string         # Required - explains what the metric means
    severity: string         # Required - critical|high|moderate|low (maps to background color)
    icon: string             # Optional - lucide icon name
    
  [context_name]:            # Optional - context-specific variants
    # Same structure as default
```

### 1.2 Card Contexts

Standard context names for different page types:

| Context Name | Used On | Purpose |
|--------------|---------|---------|
| `default` | All pages | Fallback card appearance |
| `contamination_context` | Contaminant pages | When entity referenced from contamination page |
| `compound_context` | Compound pages | When entity referenced from compound page |
| `material_context` | Material pages | When entity referenced from material page |
| `setting_context` | Setting pages | When entity referenced from settings page |

### 1.3 Severity to Background Color Mapping

```typescript
const severityColors = {
  critical: 'bg-gradient-to-br from-red-600 to-red-800',      // NFPA 4, Health 4
  high: 'bg-gradient-to-br from-orange-500 to-orange-700',    // NFPA 3, Health 3
  moderate: 'bg-gradient-to-br from-yellow-500 to-yellow-700', // NFPA 2, Health 2
  low: 'bg-gradient-to-br from-blue-500 to-blue-700'          // NFPA 1, Health 1
};
```

### 1.4 Example: Compound Card

```yaml
# In acrolein-compound.yaml
id: acrolein-compound
name: Acrolein
full_path: /compounds/toxic-gas/aldehyde/acrolein-compound

card:
  default:
    heading: "Acrolein"
    subtitle: "Toxic Gas / Aldehyde"
    badge:
      text: "Highly Toxic"
      variant: "danger"
    metric:
      value: "0.1"
      unit: "ppm"
      legend: "OSHA PEL"
    severity: "critical"
    icon: "alert-triangle"
    
  contamination_context:
    heading: "Acrolein"
    subtitle: "Common from Oil Decomposition"
    badge:
      text: "High Severity"
      variant: "danger"
    metric:
      value: "0.1"
      unit: "ppm"
      legend: "Exposure Limit"
    severity: "high"
    icon: "droplet"
    
  material_context:
    heading: "Acrolein"
    subtitle: "Composite Pyrolysis Product"
    badge:
      text: "Toxic Emission"
      variant: "warning"
    metric:
      value: "52.7"
      unit: "°C"
      legend: "Boiling Point"
    severity: "high"
    icon: "cube"
```

### 1.5 Example: Material Card

```yaml
# In steel-laser-cleaning.yaml
id: steel-laser-cleaning
name: Steel
full_path: /materials/metal/ferrous/steel-laser-cleaning

card:
  default:
    heading: "Steel"
    subtitle: "Ferrous Metal"
    badge:
      text: "Common"
      variant: "info"
    metric:
      value: "1064"
      unit: "nm"
      legend: "Wavelength"
    severity: "low"
    icon: "shield"
    
  contamination_context:
    heading: "Steel"
    subtitle: "High Rust Susceptibility"
    badge:
      text: "Very Common"
      variant: "warning"
    metric:
      value: "95"
      unit: "%"
      legend: "Occurrence Rate"
    severity: "moderate"
    icon: "alert-circle"
    
  compound_context:
    heading: "Steel"
    subtitle: "Iron Oxide Source"
    badge:
      text: "Primary Source"
      variant: "technical"
    metric:
      value: "Fe₂O₃"
      unit: ""
      legend: "Primary Compound"
    severity: "low"
    icon: "flask"
```

---

## Part 2: ID-Based Relationship Lookup

### 2.1 Current Structure (Redundant - TO BE REMOVED)

```yaml
# ❌ BEFORE: Redundant data in every relationship
relationships:
  found_on_materials:
    - id: steel-laser-cleaning
      frequency: very_common
      presentation: card                              # ❌ Repeated per item
      url: /materials/metal/ferrous/steel-laser-cleaning  # ❌ Duplicates full_path
    - id: aluminum-laser-cleaning
      frequency: very_common
      presentation: card                              # ❌ Repeated per item
      url: /materials/metal/non-ferrous/aluminum-laser-cleaning  # ❌ Duplicates full_path
```

### 2.2 New Structure (ID Lookup - TO BE IMPLEMENTED)

```yaml
# ✅ AFTER: Clean ID-based lookup
relationships:
  found_on_materials:
    presentation: card        # ✅ Once per relationship, applies to all items
    items:
      - id: steel-laser-cleaning
        frequency: very_common
      - id: aluminum-laser-cleaning
        frequency: very_common
```

### 2.3 Data Resolution Flow

```
1. Relationship references: id: steel-laser-cleaning
2. Lookup steel-laser-cleaning frontmatter file
3. Extract card data: card.contamination_context (or card.default if context not found)
4. Extract URL: full_path field
5. Render card with entity's card data + relationship's frequency metadata
```

### 2.4 Relationship Metadata Rules

**Only include metadata that describes the relationship itself, NOT the entity:**

```yaml
# ✅ CORRECT: Relationship-specific metadata
- id: steel-laser-cleaning
  frequency: very_common      # ✅ Describes how often rust appears on steel (relationship)
  
# ❌ WRONG: Entity intrinsic properties (belong in entity's own frontmatter)
- id: iron-oxide
  hazard_level: moderate      # ❌ Intrinsic to iron-oxide, not relationship-specific
  phase: solid                # ❌ Intrinsic to iron-oxide, not relationship-specific
```

**Exception:** Use `overrides:` when relationship needs to provide context-specific data:

```yaml
- id: irritant-gas-high-concentration
  overrides:                  # ✅ Relationship-specific override
    specific_compound: Acrolein
    pel_ppm: 0.1
```

---

## Part 3: Presentation at Key Level

### 3.1 Current Structure (Item-Level Presentation - TO BE REMOVED)

```yaml
# ❌ BEFORE: Presentation repeated on every item
relationships:
  produces_compounds:
    _section:
      title: Compounds Released
    items:
      - id: iron-oxide
        presentation: card    # ❌ Repeated
      - id: carbon-dioxide
        presentation: card    # ❌ Repeated
```

### 3.2 New Structure (Key-Level Presentation - TO BE IMPLEMENTED)

```yaml
# ✅ AFTER: Presentation once per relationship
relationships:
  produces_compounds:
    presentation: card        # ✅ Applies to all items in this relationship
    _section:
      title: Compounds Released
    items:
      - id: iron-oxide
      - id: carbon-dioxide
```

### 3.3 Presentation Types

```yaml
presentation: card     # Card UI (default) - full card with all elements
presentation: badge    # Badge UI - compact inline badge
presentation: list     # List UI - simple list item
presentation: inline   # Inline text link
presentation: banner   # Banner UI - wide horizontal card
```

### 3.4 Section Structure with Presentation

```yaml
relationships:
  [relationship_key]:
    presentation: card        # Required - applies to all items
    _section:                 # Optional - section metadata
      title: string
      description: string
      order: number
      variant: string
      icon: string
    items:                    # Required - array of entity references
      - id: entity-id
        [relationship_metadata]: value
```

---

## Part 4: URL Derivation from full_path

### 4.1 Current Structure (Redundant URLs - TO BE REMOVED)

```yaml
# ❌ BEFORE: URL duplicated in relationships
# In steel-laser-cleaning.yaml
id: steel-laser-cleaning
full_path: /materials/metal/ferrous/steel-laser-cleaning

# In rust-oxidation-contamination.yaml
relationships:
  found_on_materials:
    - id: steel-laser-cleaning
      url: /materials/metal/ferrous/steel-laser-cleaning  # ❌ Duplicates full_path
```

### 4.2 New Structure (Derive from full_path - TO BE IMPLEMENTED)

```yaml
# ✅ AFTER: URL derived from entity's full_path
# In steel-laser-cleaning.yaml
id: steel-laser-cleaning
full_path: /materials/metal/ferrous/steel-laser-cleaning

# In rust-oxidation-contamination.yaml
relationships:
  found_on_materials:
    presentation: card
    items:
      - id: steel-laser-cleaning  # ✅ URL derived from entity's full_path
```

### 4.3 Lookup Logic

```python
def resolve_entity_url(entity_id: str, content_type: str) -> str:
    """
    Resolve entity URL from its frontmatter full_path.
    
    Args:
        entity_id: Entity identifier (e.g., 'steel-laser-cleaning')
        content_type: Content type directory (e.g., 'materials', 'compounds')
    
    Returns:
        Full URL path from entity's frontmatter
    """
    frontmatter_path = f"frontmatter/{content_type}/{entity_id}.yaml"
    frontmatter = load_yaml(frontmatter_path)
    return frontmatter.get('full_path')
```

---

## Part 5: Migration Strategy

### 5.1 Phase 1: Add Card Schema (No Breaking Changes)

**Action:** Add `card:` section to all entity frontmatter files

```bash
# Add card sections without removing existing structure
python scripts/migration/add_card_schema.py
```

**Impact:** Additive only, no breaking changes

### 5.2 Phase 2: Restructure Relationships (Breaking Changes)

**Action:** Convert relationships to new structure

```bash
# Backup existing frontmatter
cp -r frontmatter frontmatter.backup.$(date +%Y%m%d)

# Run migration
python scripts/migration/restructure_relationships.py

# Verify
python scripts/migration/verify_restructure.py
```

**Changes:**
- Move `presentation` from items to key level
- Remove `url` field from items
- Wrap items in `items:` array (if flat structure)
- Remove intrinsic properties (hazard_level, phase, etc.) from items

### 5.3 Phase 3: Update Components

**Action:** Update React components to use new structure

**Files to modify:**
- `app/components/Card/RelationshipCard.tsx` - Add card lookup logic
- `app/components/Card/MaterialCard.tsx` - Use card schema
- `app/components/CardGridSSR.tsx` - Handle context prop
- `app/utils/frontmatter.ts` - Add entity lookup helpers

### 5.4 Phase 4: Validation & Testing

```bash
# Validate all frontmatter files
python scripts/validation/validate_card_schema.py

# Test relationship resolution
python scripts/validation/test_relationship_lookup.py

# Check for orphaned IDs
python scripts/validation/check_orphaned_ids.py
```

---

## Part 6: Implementation Guidelines for Python Generator

### 6.1 Card Schema Generation

```python
def generate_card_schema(entity: dict, content_type: str) -> dict:
    """
    Generate card schema based on entity type and available data.
    
    Args:
        entity: Entity data dictionary
        content_type: Type of content (materials, compounds, contaminants)
    
    Returns:
        Complete card schema with default + context variants
    """
    card = {
        'default': generate_default_card(entity, content_type)
    }
    
    # Add context-specific variants
    if content_type == 'compounds':
        card['contamination_context'] = generate_compound_contamination_card(entity)
        card['material_context'] = generate_compound_material_card(entity)
    elif content_type == 'materials':
        card['contamination_context'] = generate_material_contamination_card(entity)
        card['compound_context'] = generate_material_compound_card(entity)
        card['setting_context'] = generate_material_setting_card(entity)
    
    return card

def generate_default_card(entity: dict, content_type: str) -> dict:
    """Generate default card variant."""
    if content_type == 'compounds':
        return {
            'heading': entity['name'],
            'subtitle': f"{entity['category']} / {entity.get('subcategory', '')}",
            'badge': {
                'text': determine_hazard_text(entity),
                'variant': determine_hazard_variant(entity)
            },
            'metric': {
                'value': str(entity['exposure_limits'].get('osha_pel_ppm', 'N/A')),
                'unit': 'ppm',
                'legend': 'OSHA PEL'
            },
            'severity': determine_severity(entity),
            'icon': determine_icon(entity)
        }
    # ... similar for other content types
```

### 6.2 Relationship Restructuring

```python
def restructure_relationships(relationships: dict) -> dict:
    """
    Restructure relationships from old format to new format.
    
    Old format:
      relationship_key:
        - id: entity-id
          presentation: card
          url: /path/to/entity
    
    New format:
      relationship_key:
        presentation: card
        items:
          - id: entity-id
    """
    restructured = {}
    
    for key, value in relationships.items():
        if key == '_section' or value is None:
            restructured[key] = value
            continue
            
        # Detect presentation type (all items should have same value)
        presentation = 'card'  # default
        if isinstance(value, list) and len(value) > 0:
            presentation = value[0].get('presentation', 'card')
        
        # Build new structure
        new_relationship = {
            'presentation': presentation
        }
        
        # Preserve _section if exists
        if isinstance(value, dict) and '_section' in value:
            new_relationship['_section'] = value['_section']
            items = value.get('items', [])
        else:
            items = value if isinstance(value, list) else []
        
        # Clean items - remove presentation and url
        cleaned_items = []
        for item in items:
            cleaned = {k: v for k, v in item.items() 
                      if k not in ['presentation', 'url']}
            cleaned_items.append(cleaned)
        
        new_relationship['items'] = cleaned_items
        restructured[key] = new_relationship
    
    return restructured
```

### 6.3 Validation Rules

```python
def validate_card_schema(card: dict) -> list[str]:
    """Validate card schema structure."""
    errors = []
    
    # Must have default variant
    if 'default' not in card:
        errors.append("Missing required 'default' variant")
    
    # Validate each variant
    for variant_name, variant_data in card.items():
        # Required fields
        required = ['heading', 'subtitle', 'badge', 'metric', 'severity']
        for field in required:
            if field not in variant_data:
                errors.append(f"Variant '{variant_name}' missing required field '{field}'")
        
        # Validate badge structure
        if 'badge' in variant_data:
            badge = variant_data['badge']
            if 'text' not in badge or 'variant' not in badge:
                errors.append(f"Variant '{variant_name}' badge missing text or variant")
            if badge.get('variant') not in ['success', 'warning', 'danger', 'info', 'technical']:
                errors.append(f"Invalid badge variant: {badge.get('variant')}")
        
        # Validate metric structure
        if 'metric' in variant_data:
            metric = variant_data['metric']
            if 'value' not in metric or 'legend' not in metric:
                errors.append(f"Variant '{variant_name}' metric missing value or legend")
        
        # Validate severity
        if variant_data.get('severity') not in ['critical', 'high', 'moderate', 'low']:
            errors.append(f"Invalid severity: {variant_data.get('severity')}")
    
    return errors

def validate_relationship_structure(relationships: dict) -> list[str]:
    """Validate relationship structure."""
    errors = []
    
    for key, value in relationships.items():
        if key in ['_section'] or value is None:
            continue
        
        # Must have presentation at key level
        if 'presentation' not in value:
            errors.append(f"Relationship '{key}' missing 'presentation' field")
        
        # Must have items array
        if 'items' not in value:
            errors.append(f"Relationship '{key}' missing 'items' array")
        
        # Items must be array
        if not isinstance(value.get('items'), list):
            errors.append(f"Relationship '{key}' items must be array")
        
        # Check for old structure remnants
        items = value.get('items', [])
        for idx, item in enumerate(items):
            if 'presentation' in item:
                errors.append(f"Relationship '{key}' item {idx} has item-level 'presentation' (should be key-level)")
            if 'url' in item:
                errors.append(f"Relationship '{key}' item {idx} has 'url' field (should use full_path lookup)")
    
    return errors
```

---

## Part 7: Expected Outcomes

### 7.1 File Size Reduction

**Current:** 10,232,772 bytes total frontmatter  
**Projected:** 9,917,214 bytes total frontmatter  
**Reduction:** 315,558 bytes (3.1%)

**Breakdown:**
- 6,714 `presentation: card` lines removed = 147,708 bytes
- 3,357 `url` fields removed (estimated) = 167,850 bytes

### 7.2 Architectural Improvements

- ✅ Single source of truth for all entity data
- ✅ Card appearance defined once per entity
- ✅ Relationships only store relationship metadata
- ✅ URLs derived from canonical `full_path`
- ✅ Context-aware card rendering
- ✅ Easier maintenance and updates

### 7.3 Git Diff Improvements

**Before:** Changing presentation affects 100+ files  
**After:** Changing presentation affects 1 file (the relationship parent)

**Before:** Updating URL format requires changes to 6,714 lines  
**After:** Updating URL format affects 0 relationship lines (derived from full_path)

---

## Part 8: Rollback Plan

### 8.1 Backup Strategy

```bash
# Before migration
tar -czf frontmatter.backup.$(date +%Y%m%d_%H%M%S).tar.gz frontmatter/
```

### 8.2 Rollback Procedure

```bash
# If issues discovered after migration
tar -xzf frontmatter.backup.[timestamp].tar.gz
git checkout HEAD -- frontmatter/
```

### 8.3 Validation Checkpoints

- [ ] All entity files have valid `card:` schema
- [ ] All relationships have `presentation` at key level
- [ ] All relationships have `items:` array
- [ ] No `url` fields in relationship items
- [ ] No orphaned entity IDs
- [ ] All frontend components pass tests
- [ ] Production build completes successfully

---

## Part 9: Timeline & Dependencies

### 9.1 Estimated Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Add Card Schema | 3-5 days | Python generator updates |
| Phase 2: Restructure Relationships | 2-3 days | Phase 1 complete |
| Phase 3: Update Components | 3-4 days | Phase 2 complete |
| Phase 4: Validation & Testing | 2-3 days | Phase 3 complete |
| **Total** | **10-15 days** | Sequential execution |

### 9.2 Team Dependencies

- **Python Generator Team**: Implement card schema generation logic
- **Frontend Team**: Update React components for new structure
- **QA Team**: Validate migration and test all card contexts
- **DevOps Team**: Manage backups and rollback procedures

---

## Appendix A: Complete Examples

### A.1 Complete Compound Frontmatter (After Migration)

```yaml
id: acrolein-compound
name: Acrolein
full_path: /compounds/toxic-gas/aldehyde/acrolein-compound
chemical_formula: C₃H₄O
cas_number: 107-02-8

card:
  default:
    heading: "Acrolein"
    subtitle: "Toxic Gas / Aldehyde"
    badge:
      text: "Highly Toxic"
      variant: "danger"
    metric:
      value: "0.1"
      unit: "ppm"
      legend: "OSHA PEL"
    severity: "critical"
    icon: "alert-triangle"
    
  contamination_context:
    heading: "Acrolein"
    subtitle: "Common from Oil Decomposition"
    badge:
      text: "High Severity"
      variant: "danger"
    metric:
      value: "0.1"
      unit: "ppm"
      legend: "Exposure Limit"
    severity: "high"
    icon: "droplet"
    
  material_context:
    heading: "Acrolein"
    subtitle: "Composite Pyrolysis Product"
    badge:
      text: "Toxic Emission"
      variant: "warning"
    metric:
      value: "52.7"
      unit: "°C"
      legend: "Boiling Point"
    severity: "high"
    icon: "cube"

relationships:
  produced_from_contaminants:
    presentation: card
    _section:
      title: Source Contaminants
      description: Contamination types that generate this compound
      order: 2
      variant: relationship
      icon: droplet
    items:
      - id: industrial-oil-contamination
        frequency: common
        severity: high
        typical_context: Thermal decomposition of fats and oils
      - id: quench-oil-contamination
        frequency: common
        severity: high
      - id: cutting-fluid-contamination
        frequency: common
        severity: high
  
  produced_from_materials:
    presentation: card
    _section:
      title: Source Materials
      description: Materials that generate this compound
      order: 3
      variant: relationship
      icon: cube
    items:
      - id: ceramic-matrix-composites-cmcs-laser-cleaning
      - id: epoxy-resin-composites-laser-cleaning
      - id: metal-matrix-composites-mmcs-laser-cleaning
```

### A.2 Component Implementation Example

```typescript
// app/components/Card/RelationshipCard.tsx
import { loadEntityFrontmatter } from '@/utils/frontmatter';
import type { CardSchema, RelationshipItem } from '@/types';

interface RelationshipCardProps {
  item: RelationshipItem;
  context?: string;
}

export function RelationshipCard({ item, context = 'default' }: RelationshipCardProps) {
  // Load entity frontmatter by ID
  const entity = loadEntityFrontmatter(item.id);
  
  // Get card data for context (fallback to default)
  const cardData: CardSchema = entity.card?.[context] || entity.card?.default;
  
  // Derive URL from entity's full_path
  const url = entity.full_path;
  
  // Determine background color from severity
  const bgColor = {
    critical: 'bg-gradient-to-br from-red-600 to-red-800',
    high: 'bg-gradient-to-br from-orange-500 to-orange-700',
    moderate: 'bg-gradient-to-br from-yellow-500 to-yellow-700',
    low: 'bg-gradient-to-br from-blue-500 to-blue-700'
  }[cardData.severity];
  
  return (
    <a href={url} className={`block rounded-lg p-6 ${bgColor}`}>
      {/* Badge */}
      <Badge variant={cardData.badge.variant}>
        {cardData.badge.text}
      </Badge>
      
      {/* Metric */}
      <div className="mt-4">
        <div className="text-4xl font-bold text-white">
          {cardData.metric.value}
          {cardData.metric.unit && (
            <span className="text-2xl ml-1">{cardData.metric.unit}</span>
          )}
        </div>
        <div className="text-sm text-white/80 mt-1">
          {cardData.metric.legend}
        </div>
      </div>
      
      {/* Heading & Subtitle */}
      <div className="mt-4 border-t border-white/20 pt-4">
        <h3 className="text-xl font-semibold text-white">
          {cardData.heading}
        </h3>
        <p className="text-sm text-white/80">
          {cardData.subtitle}
        </p>
      </div>
    </a>
  );
}
```

---

## Appendix B: Validation Scripts

See separate files:
- `scripts/migration/add_card_schema.py`
- `scripts/migration/restructure_relationships.py`
- `scripts/validation/validate_card_schema.py`
- `scripts/validation/check_orphaned_ids.py`

---

**End of Specification**
