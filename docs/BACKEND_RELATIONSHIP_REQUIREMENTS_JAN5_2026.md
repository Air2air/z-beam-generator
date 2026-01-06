# Backend Relationship Section Requirements

**Document Version:** 1.0  
**Date:** January 5, 2026  
**Status:** MANDATORY - All relationship sections MUST comply  
**Test Coverage:** 2,669 passing tests verify compliance

## Overview

This document defines the mandatory requirements for relationship section metadata in the Z-Beam backend. All relationship sections in frontmatter YAML files MUST include complete `_section` metadata blocks with all required fields.

**Enforcement:** The system uses fail-fast architecture - missing or incomplete metadata throws immediate errors rather than generating warnings or using fallback values.

---

## 🚨 Critical Rules

### Rule 1: All Sections MUST Have `_section` Metadata
```yaml
# ❌ INVALID - Will throw error
relationships:
  operational:
    industry_applications:
      presentation: card
      items:
        - id: aerospace
          name: Aerospace

# ✅ VALID - Has required _section block
relationships:
  operational:
    industry_applications:
      presentation: card
      items:
        - id: aerospace
          name: Aerospace
      _section:
        sectionTitle: Industry Applications
        sectionDescription: Common industrial uses
        icon: briefcase
        order: 1
```

### Rule 2: Required Fields in `_section`
Every `_section` block MUST include these four fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sectionTitle` | string | ✅ YES | Display title for the section |
| `sectionDescription` | string | ✅ YES | Brief description of section content |
| `icon` | string | ✅ YES | Icon identifier (lucide-react compatible) |
| `order` | number | ✅ YES | Sort order for section display (1-999) |

### Rule 3: Optional Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `variant` | string | ❌ NO | Visual variant (default, warning, info, success) |
| `collapsible` | boolean | ❌ NO | Whether section can be collapsed (default: false) |
| `defaultExpanded` | boolean | ❌ NO | Whether section starts expanded (default: true) |

---

## Schema Definition

### TypeScript Interface
```typescript
interface RelationshipSection {
  sectionTitle: string;        // Required
  sectionDescription: string;  // Required
  icon: string;                // Required
  order: number;               // Required
  variant?: 'default' | 'warning' | 'info' | 'success';  // Optional
  collapsible?: boolean;       // Optional
  defaultExpanded?: boolean;   // Optional
}

interface RelationshipSectionData {
  presentation: 'card' | 'badge' | 'descriptive' | 'table';
  items: Array<any>;
  _section: RelationshipSection;  // Required
}
```

### JSON Schema (for validation)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["presentation", "items", "_section"],
  "properties": {
    "presentation": {
      "type": "string",
      "enum": ["card", "badge", "descriptive", "table"]
    },
    "items": {
      "type": "array",
      "items": {}
    },
    "_section": {
      "type": "object",
      "required": ["sectionTitle", "sectionDescription", "icon", "order"],
      "properties": {
        "sectionTitle": { "type": "string", "minLength": 1 },
        "sectionDescription": { "type": "string", "minLength": 1 },
        "icon": { "type": "string", "minLength": 1 },
        "order": { "type": "number", "minimum": 1 },
        "variant": { 
          "type": "string", 
          "enum": ["default", "warning", "info", "success"] 
        },
        "collapsible": { "type": "boolean" },
        "defaultExpanded": { "type": "boolean" }
      }
    }
  }
}
```

---

## Complete Examples

### Example 1: Minimal Valid Structure
```yaml
relationships:
  operational:
    industry_applications:
      presentation: card
      items:
        - id: aerospace
          name: Aerospace
        - id: automotive
          name: Automotive
      _section:
        sectionTitle: Industry Applications
        sectionDescription: Common industrial uses of this material
        icon: briefcase
        order: 1
```

### Example 2: Full Structure with Optional Fields
```yaml
relationships:
  safety:
    exposure_limits:
      presentation: descriptive
      items:
        - osha_pel: 100 ppm
          niosh_rel: 50 ppm
      _section:
        sectionTitle: Exposure Limits
        sectionDescription: Regulatory exposure limits and guidelines
        icon: shield-check
        order: 1
        variant: warning
        collapsible: true
        defaultExpanded: true
```

### Example 3: Nested Structure
```yaml
relationships:
  safety:
    exposure_limits:
      presentation: descriptive
      items:
        - osha_pel: 100 ppm
      _section:
        sectionTitle: Exposure Limits
        sectionDescription: OSHA and NIOSH regulatory limits
        icon: shield-check
        order: 1
    
    ppe_requirements:
      presentation: card
      items:
        - id: gloves
          type: Hand Protection
        - id: goggles
          type: Eye Protection
      _section:
        sectionTitle: PPE Requirements
        sectionDescription: Required protective equipment
        icon: alert-triangle
        order: 2
        variant: warning
```

### Example 4: Multi-Level Nested Paths
```yaml
relationships:
  level1:
    level2:
      level3:
        presentation: badge
        items:
          - id: deep-item
            name: Deep Item
        _section:
          sectionTitle: Deep Section
          sectionDescription: Deeply nested section example
          icon: layers
          order: 10
```

---

## Error Handling

### What Happens When Metadata is Missing?

The system throws **immediate errors** (fail-fast) rather than generating warnings or using fallbacks.

#### Error Example 1: Missing `_section` Block
```typescript
// Input YAML:
relationships:
  test_section:
    items: [{ id: 'test' }]
    // No _section block

// Runtime Error:
Error: Missing required _section metadata at path: test_section. 
All relationship sections MUST have a _section block with 
sectionTitle, sectionDescription, icon, and order fields.
```

#### Error Example 2: Incomplete `_section` Block
```typescript
// Input YAML:
relationships:
  test_section:
    items: [{ id: 'test' }]
    _section:
      sectionTitle: Test Section
      # Missing sectionDescription, icon, order

// Runtime Error:
Error: Missing required _section metadata at path: test_section.
All relationship sections MUST have a _section block with
sectionTitle, sectionDescription, icon, and order fields.
```

### Component-Level Errors

Components that consume relationship data will also throw errors:

```typescript
// IndustryApplicationsPanel.tsx
if (!sectionMetadata) {
  throw new Error(
    `Missing required _section metadata for industry_applications. ` +
    `All sections MUST have explicit _section metadata with ` +
    `sectionTitle and sectionDescription.`
  );
}
```

---

## Validation Utilities

### Helper Functions

#### `getRelationshipSection()`
```typescript
import { getRelationshipSection } from '@/app/utils/relationshipHelpers';

// Returns section data with metadata or null
const section = getRelationshipSection(relationships, 'safety.exposure_limits');

if (section) {
  console.log(section.metadata.sectionTitle);  // "Exposure Limits"
  console.log(section.items);                  // Array of items
  console.log(section.presentation);           // "descriptive"
}
```

#### `validateRelationshipSection()`
```typescript
import { validateRelationshipSection } from '@/app/utils/relationshipHelpers';

const result = validateRelationshipSection(relationships, 'safety.exposure_limits');

if (!result.isValid) {
  console.error('Validation failed:', result.errors);
}
```

#### `getAllRelationshipSections()`
```typescript
import { getAllRelationshipSections } from '@/app/utils/relationshipHelpers';

// Returns all sections sorted by order
const sections = getAllRelationshipSections(relationships);

sections.forEach(section => {
  console.log(`${section.path}: ${section.metadata.sectionTitle}`);
});
```

### Validation Script
```bash
# Run validation on all frontmatter files
npm run validate:frontmatter

# Run comprehensive validation
npm run test:all
```

---

## Migration Guide

### Step 1: Identify Incomplete Sections
Run validation to find sections missing `_section` metadata:
```bash
npm run test:all 2>&1 | grep "Missing required _section"
```

### Step 2: Add Required Fields
For each section missing metadata, add the complete `_section` block:

```yaml
# Before (INVALID)
relationships:
  operational:
    industry_applications:
      items:
        - Aerospace
        - Automotive

# After (VALID)
relationships:
  operational:
    industry_applications:
      presentation: card  # Add presentation type
      items:
        - id: aerospace  # Convert to proper structure
          name: Aerospace
        - id: automotive
          name: Automotive
      _section:  # Add complete metadata
        sectionTitle: Industry Applications
        sectionDescription: Industries using this material
        icon: briefcase
        order: 1
```

### Step 3: Choose Appropriate Icons
Common icon choices by section type:

| Section Type | Recommended Icons |
|--------------|------------------|
| Industry applications | `briefcase`, `building`, `factory` |
| Safety information | `shield-check`, `alert-triangle`, `shield` |
| Physical properties | `ruler`, `thermometer`, `weight` |
| Visual characteristics | `eye`, `palette`, `image` |
| Compliance/regulations | `clipboard-check`, `gavel`, `file-text` |
| Technical specifications | `settings`, `cpu`, `layers` |

Full icon list: [Lucide Icons](https://lucide.dev/icons/)

### Step 4: Set Appropriate Order
Order sections logically (1-999):
- 1-10: Critical safety information
- 11-20: Primary operational data
- 21-30: Physical/visual characteristics
- 31-40: Technical specifications
- 41-50: Compliance/regulatory
- 51+: Additional/supplementary info

### Step 5: Test Changes
```bash
# Run tests to verify all sections are valid
npm run test:all

# Run build to catch any compilation errors
npm run build
```

---

## Testing Requirements

### Unit Tests Must Include Complete Metadata
All tests that create relationship section data must include complete `_section` blocks:

```typescript
// ❌ INVALID TEST - Will fail
const testData = {
  items: [{ id: 'test' }]
};

// ✅ VALID TEST
const testData = {
  presentation: 'card',
  items: [{ id: 'test', name: 'Test' }],
  _section: {
    sectionTitle: 'Test Section',
    sectionDescription: 'Test section description',
    icon: 'box',
    order: 1
  }
};
```

### Test Coverage
Current test coverage for relationship requirements:
- **IndustryApplicationsPanel:** 17 tests
- **relationshipHelpers:** 25+ tests  
- **frontmatterValidation:** 15+ tests
- **Total:** 2,669 passing tests verify compliance

---

## Common Patterns

### Pattern 1: Material Industry Applications
```yaml
relationships:
  operational:
    industry_applications:
      presentation: card
      items:
        - id: aerospace
          name: Aerospace
          description: Aircraft components and assemblies
        - id: automotive
          name: Automotive
          description: Vehicle manufacturing and parts
      _section:
        sectionTitle: Industry Applications
        sectionDescription: Common industries using {materialName}
        icon: briefcase
        order: 10
```

### Pattern 2: Safety Exposure Limits
```yaml
relationships:
  safety:
    exposure_limits:
      presentation: descriptive
      items:
        - osha_pel: 5 mg/m³
          niosh_rel: 5 mg/m³
          acgih_tlv: 5 mg/m³
      _section:
        sectionTitle: Exposure Limits
        sectionDescription: Regulatory exposure limits and guidelines
        icon: shield-check
        order: 1
        variant: warning
```

### Pattern 3: Visual Characteristics
```yaml
relationships:
  physical:
    visual_characteristics:
      presentation: descriptive
      items:
        - color: Silver-white metallic
          texture: Smooth when polished
          appearance: Lustrous finish
      _section:
        sectionTitle: Visual Characteristics
        sectionDescription: Physical appearance and observable properties
        icon: eye
        order: 15
```

### Pattern 4: Contaminant Industry Impact
```yaml
relationships:
  operational:
    industries_affected:
      presentation: badge
      items:
        - id: manufacturing
          name: Manufacturing
        - id: construction
          name: Construction
      _section:
        sectionTitle: Industries Affected by {contaminantName}
        sectionDescription: Industries commonly impacted by this contaminant
        icon: alert-triangle
        order: 5
        variant: warning
```

---

## Presentation Types

### Card Presentation
Best for: Lists with titles and descriptions
```yaml
presentation: card
items:
  - id: aerospace
    name: Aerospace
    description: Aircraft manufacturing
  - id: automotive
    name: Automotive  
    description: Vehicle production
```

### Badge Presentation
Best for: Simple lists without descriptions
```yaml
presentation: badge
items:
  - id: aerospace
    name: Aerospace
  - id: automotive
    name: Automotive
```

### Descriptive Presentation
Best for: Key-value pairs, technical specs
```yaml
presentation: descriptive
items:
  - osha_pel: 100 ppm
    niosh_rel: 50 ppm
    acgih_tlv: 75 ppm
```

### Table Presentation
Best for: Structured data with multiple columns
```yaml
presentation: table
items:
  - parameter: Density
    value: 2.70 g/cm³
    unit: g/cm³
  - parameter: Melting Point
    value: 660
    unit: °C
```

---

## Variant Styling

### Visual Variants
Control the visual appearance of sections:

- **`default`** - Standard blue/neutral styling
- **`warning`** - Yellow/amber for caution information
- **`info`** - Blue for informational content
- **`success`** - Green for positive/safe information

```yaml
_section:
  sectionTitle: Safety Warning
  sectionDescription: Critical safety information
  icon: alert-triangle
  order: 1
  variant: warning  # Renders with yellow/amber styling
```

---

## FAQ

### Q: Can I omit `_section` metadata for simple sections?
**A:** No. All sections MUST have complete `_section` metadata. The system uses fail-fast architecture and will throw errors if metadata is missing.

### Q: What happens if I'm missing just one required field?
**A:** The system will throw an error listing the missing fields. All four required fields (sectionTitle, sectionDescription, icon, order) must be present.

### Q: Can I use custom icons?
**A:** Icons must be valid Lucide icon identifiers. See [Lucide Icons](https://lucide.dev/icons/) for the full list.

### Q: How do I handle legacy flat arrays?
**A:** Convert them to the normalized structure with presentation, items, and `_section` metadata. See Migration Guide above.

### Q: What order numbers should I use?
**A:** Use 1-999. Lower numbers display first. Group related sections in ranges (1-10 for safety, 11-20 for operational, etc.).

### Q: Can sections be collapsible?
**A:** Yes, set `collapsible: true` in `_section` metadata. Control default state with `defaultExpanded`.

### Q: How do I test my changes?
**A:** Run `npm run test:all` to verify all relationship sections have valid metadata.

---

## Related Documentation

- **Frontend Requirements:** `docs/FRONTEND_REQUIRED_FIELDS_JAN4_2026.md`
- **Frontend Normalization:** `docs/FRONTEND_NORMALIZATION_COMPLETE_JAN4_2026.md`
- **Backend Frontmatter:** `docs/BACKEND_FRONTMATTER_REQUIREMENTS_JAN4_2026.md`
- **Naming Standards:** `docs/NAMING_STANDARDS_VERIFICATION_JAN4_2026.md`
- **Unified Schema:** `docs/FRONTMATTER_UNIFIED_SCHEMA_PROPOSAL_JAN3_2026.md`

---

## Compliance Checklist

Before deploying changes to relationship sections:

- [ ] All sections have `_section` metadata block
- [ ] All required fields present (sectionTitle, sectionDescription, icon, order)
- [ ] Icons are valid Lucide identifiers
- [ ] Order numbers are logical (1-999)
- [ ] Presentation type is specified
- [ ] Items array has proper structure (with id fields for card/badge)
- [ ] Tests pass: `npm run test:all`
- [ ] Build succeeds: `npm run build`
- [ ] Validation passes: `npm run validate:frontmatter`

---

## Support

For questions or issues:
1. Check existing tests in `tests/utils/relationshipHelpers.test.ts`
2. Review component implementations in `app/components/`
3. Run validation utilities to identify specific issues
4. Refer to this document for complete requirements

**Last Updated:** January 5, 2026  
**Test Status:** ✅ 2,669 tests passing
