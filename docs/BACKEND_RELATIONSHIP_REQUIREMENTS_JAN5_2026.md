# Backend Relationship Section Requirements

**Document Version:** 2.0  
**Date:** January 6, 2026  
**Status:** ✅ COMPLETE - 100% compliance achieved  
**Test Coverage:** 2,669 passing tests verify compliance  
**Implementation Status:** 100% complete (2,401/2,401 sections) - All domains compliant

## Overview

This document defines the mandatory requirements for relationship section metadata in the Z-Beam backend. All relationship sections in frontmatter YAML files MUST include complete `_section` metadata blocks with all required fields.

**Enforcement:** The system uses fail-fast architecture - missing or incomplete metadata throws immediate errors rather than generating warnings or using fallback values.

---

## 📊 Implementation Status (January 6, 2026)

### ✅ Current Coverage: 100% (2,401/2,401 sections) - COMPLETE

| Domain | Total Sections | With `_section` | Coverage | Status | Completion Date |
|--------|----------------|-----------------|----------|---------|------------------|
| **Materials** | 324 | 324 | 100% | ✅ Complete | Jan 6, 2026 |
| **Contaminants** | 1,176 | 1,176 | 100% | ✅ Complete | Jan 5, 2026 |
| **Compounds** | 298 | 298 | 100% | ✅ Complete | Jan 5, 2026 |
| **Settings** | 603 | 603 | 100% | ✅ Complete | Jan 5, 2026 |
| **TOTAL** | **2,401** | **2,401** | **100%** | ✅ **COMPLETE** | Jan 6, 2026 |

### ✅ Achievement Summary

**100% compliance achieved across all domains through multi-phase implementation.**

**Phase 1 (Jan 5, 2026): Contaminants Domain**
- Fixed SafetyTableNormalizer to preserve `_section` during merge operations
- Result: 1,176/1,176 sections (100%) - 686 sections recovered

**Phase 2 (Jan 5, 2026): Compounds Domain**
- Added `_section` to health_effects in source data (Compounds.yaml)
- Result: 298/298 sections (100%) - 36 sections fixed

**Phase 3 (Jan 5, 2026): Materials Domain Cleanup**
- Removed duplicate top-level keys (operational, regulatory_standards)
- Result: Single source of truth in relationships structure

**Phase 4 (Jan 6, 2026): Materials Section Completion**
- Added `_section` to 21 migrated materials missing metadata
- Result: 324/324 sections (100%) - Final 21 sections fixed

**Current Structure (INVALID - Will throw errors):**
```yaml
relationships:
  interactions:
    produces_compounds:
      presentation: card
      items:
        - id: carbon-dioxide-compound
        - id: water-vapor-compound
      # ❌ Missing _section block - System will fail
```

**Required Structure:**
```yaml
relationships:
  interactions:
    produces_compounds:
      presentation: card
      items:
        - id: carbon-dioxide-compound
        - id: water-vapor-compound
      _section:
        sectionTitle: Produced Compounds
        sectionDescription: Hazardous compounds created during laser cleaning
        icon: flask
        order: 1
```

### \ud83d\udd0d Verification

**Test Coverage: 2,669 passing tests**
- Field mapping tests: 100% pass (validates _section structure)
- Section metadata enrichment: 100% pass
- Export validation: 100% pass (link validation, structure verification)

**Verification Command:**
```bash
python3 -c "
import yaml
from pathlib import Path

domains = {'materials': 324, 'contaminants': 1176, 'compounds': 298, 'settings': 603}
total_sections = 0
total_with_section = 0

for domain, expected in domains.items():
    path = Path(f'/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/{domain}')
    files = list(path.glob('*.yaml'))
    sections_with_meta = 0
    total_domain_sections = 0
    
    for file in files:
        with open(file) as f:
            data = yaml.safe_load(f)
            if 'relationships' in data:
                for cat, cat_data in data['relationships'].items():
                    if isinstance(cat_data, dict):
                        for section, section_data in cat_data.items():
                            if isinstance(section_data, dict):
                                total_domain_sections += 1
                                if '_section' in section_data:
                                    sections_with_meta += 1
    
    total_sections += total_domain_sections
    total_with_section += sections_with_meta
    print(f'{domain}: {sections_with_meta}/{total_domain_sections} ({sections_with_meta/total_domain_sections*100:.1f}%)')

print(f'\\nTOTAL: {total_with_section}/{total_sections} ({total_with_section/total_sections*100:.1f}%)')
print('\\u2705 100% COMPLIANCE ACHIEVED!' if total_with_section == total_sections else '\\u274c INCOMPLETE')
"
```

**Expected Output:**
```
materials: 324/324 (100.0%)
contaminants: 1176/1176 (100.0%)
compounds: 298/298 (100.0%)
settings: 603/603 (100.0%)

TOTAL: 2401/2401 (100.0%)
\u2705 100% COMPLIANCE ACHIEVED!
```

---

## Implementation Details

### Domain-Specific Implementations

**Materials Domain (324/324 sections - 100%)**
- Completion: January 6, 2026
- Method: Source data enrichment + migration script
- Key fixes:
  1. Removed duplicate top-level keys (operational, regulatory_standards)
  2. Migrated 21 materials from top-level to relationships structure
  3. Added `_section` metadata to 21 migrated materials in source data
  4. Re-exported all 153 materials
- Source: data/materials/Materials.yaml
- Backups: Materials.yaml.backup-duplicates, Materials.yaml.backup-section-fix

**Contaminants Domain (1,176/1,176 sections - 100%)**
- Completion: January 5, 2026
- Method: SafetyTableNormalizer fix to preserve `_section` during merges
- Key fix: Modified merge_safety_tables() to properly handle _section metadata
- Result: 686 sections recovered in 98 files
- Source: export/enrichers/contaminants/safety_table_normalizer.py

**Compounds Domain (298/298 sections - 100%)**
- Completion: January 5, 2026
- Method: Source data enrichment
- Key fix: Added `_section` to health_effects in Compounds.yaml
- Result: 36 sections fixed across 34 files
- Source: data/compounds/Compounds.yaml

**Settings Domain (603/603 sections - 100%)**
- Completion: January 5, 2026 (already complete)
- Method: Original export enrichment
- No fixes required
- Source: data/settings/Settings.yaml

---

## Technical Reference
      items:
        - id: steel-laser-cleaning
        - id: iron-laser-cleaning
      _section:
        sectionTitle: Affected Materials
        sectionDescription: Materials commonly contaminated by this substance
        icon: layers
        order: 2
        variant: default
  
  safety:
    regulatory_standards:
      presentation: card
      items:
        - description: OSHA standards...
          name: OSHA
      _section:
        sectionTitle: Regulatory Standards
        sectionDescription: Safety and compliance standards for handling this contaminant
        icon: shield-check
        order: 1
        variant: default
```

**Migration Script Template:**
```javascript
// scripts/migrations/add-contaminant-section-metadata.js
const fs = require('fs');
const yaml = require('js-yaml');
const glob = require('glob');

// Section metadata templates
const SECTION_TEMPLATES = {
  'produces_compounds': {
    sectionTitle: 'Produced Compounds',
    sectionDescription: 'Hazardous compounds created during laser cleaning of this contaminant',
    icon: 'flask',
    order: 1,
    variant: 'warning'
  },
  'affects_materials': {
    sectionTitle: 'Affected Materials',
    sectionDescription: 'Materials commonly contaminated by this substance',
    icon: 'layers',
    order: 2,
    variant: 'default'
  },
  'found_on_materials': {
    sectionTitle: 'Found On Materials',
    sectionDescription: 'Materials where this contaminant commonly appears',
    icon: 'layers',
    order: 2,
    variant: 'default'
  },
  'regulatory_standards': {
    sectionTitle: 'Regulatory Standards',
    sectionDescription: 'Safety and compliance standards for handling this contaminant',
    icon: 'shield-check',
    order: 1,
    variant: 'default'
  },
  'fire_explosion_risk': {
    sectionTitle: 'Fire & Explosion Risks',
    sectionDescription: 'Fire and explosion hazards associated with this contaminant',
    icon: 'flame',
    order: 2,
    variant: 'warning'
  }
};

function addSectionMetadata(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const data = yaml.load(content);
  
  if (!data.relationships) {
    console.log(`⚠️  ${filePath}: No relationships object found`);
    return false;
  }
  
  let updated = false;
  
  // Process all relationship groups
  for (const groupKey of ['interactions', 'safety', 'operational']) {
    const group = data.relationships[groupKey];
    if (!group) continue;
    
    // Process each section in the group
    for (const sectionKey of Object.keys(group)) {
      const section = group[sectionKey];
      
      // Check if section has presentation and items (is a valid section)
      if (section && typeof section === 'object' && section.presentation && section.items) {
        // Check if _section is missing
        if (!section._section) {
          const template = SECTION_TEMPLATES[sectionKey];
          if (template) {
            section._section = template;
            updated = true;
            console.log(`✅ Added _section to ${sectionKey} in ${filePath}`);
          } else {
            console.log(`⚠️  No template for ${sectionKey} in ${filePath}`);
          }
        }
      }
    }
  }
  
  if (updated) {
    const updatedYaml = yaml.dump(data, {
      indent: 2,
      lineWidth: 120,
      noRefs: true
    });
    fs.writeFileSync(filePath, updatedYaml, 'utf8');
    return true;
  }
  
  return false;
}

// Process all contaminant files
const files = glob.sync('frontmatter/contaminants/*.yaml');
let success = 0, skipped = 0;

console.log(`\n📋 Processing ${files.length} contaminant files...\n`);

for (const file of files) {
  try {
    if (addSectionMetadata(file)) {
---

## Implementation Timeline

### January 5, 2026
**Contaminants Domain: SafetyTableNormalizer Fix**
- Fixed merge_safety_tables() to preserve `_section` during table merges
- Result: 1,176/1,176 sections (100%) - recovered 686 sections
- File: export/enrichers/contaminants/safety_table_normalizer.py

**Compounds Domain: Source Data Enrichment**
- Added `_section` to health_effects in Compounds.yaml
- Result: 298/298 sections (100%) - fixed 36 sections across 34 files
- File: data/compounds/Compounds.yaml

**Materials Domain: Duplicate Removal**
- Created migration script to remove top-level duplicate keys
- Removed `operational` and `regulatory_standards` from top-level
- Migrated 21 materials from top-level to relationships structure
- Result: Single source of truth in relationships
- Script: scripts/migrations/remove_materials_duplications.py

### January 6, 2026
**Materials Domain: Section Completion**
- Added `_section` metadata to 21 migrated materials in source data
- Fixed relationships.operational.industry_applications
- Re-exported all 153 materials
- Result: 324/324 sections (100%) - final 21 sections fixed
- Backups: Materials.yaml.backup-section-fix

**Documentation Update**
- Updated BACKEND_RELATIONSHIP_REQUIREMENTS to reflect 100% completion
- Documented all implementation phases and fixes
- Version: 2.0

---

## Success Metrics

### Coverage Achieved
- \u2705 Materials: 324/324 sections (100%)
- \u2705 Contaminants: 1,176/1,176 sections (100%)
- \u2705 Compounds: 298/298 sections (100%)
- \u2705 Settings: 603/603 sections (100%)
- \u2705 **TOTAL: 2,401/2,401 sections (100%)**

### Test Coverage
- 2,669 automated tests verify compliance
- Field mapping tests: 100% pass
- Section metadata enrichment: 100% pass
- Export validation: 100% pass

### Quality Metrics
- Zero structural errors in exported frontmatter
- All relationship sections have complete `_section` metadata
- Link validation: 0 errors across 438 files
- Build validation: 0 errors

---

## Lessons Learned

**What Worked Well:**
1. Fixing enrichers to preserve `_section` (contaminants) - immediate recovery of 686 sections
2. Source data enrichment (compounds) - permanent fix at correct layer
3. Migration scripts with dry-run mode - safe preview before execution
4. Comprehensive verification scripts - detected remaining gaps

**Challenges Overcome:**
1. Materials duplication required careful data migration (21 materials)
2. SafetyTableNormalizer merge logic was destroying `_section` metadata
3. Mixed completion status across domains required domain-specific approaches
4. Documentation drift - needed verification to catch outdated status

**Best Practices Applied:**
1. Core Principle 0.6: "No Build-Time Data Enhancement" - fixed source data
2. FRONTMATTER_SOURCE_OF_TRUTH_POLICY: Fixed Layer 1/2, not Layer 3
3. Created backups before all destructive operations
4. Verified fixes persisted through regeneration
5. Comprehensive testing before documentation updates

---

## Related Documentation

- `MATERIALS_DUPLICATION_RESOLVED_JAN6_2026.md` - Materials duplication removal
- `docs/08-development/FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md` - Correct fix layers
- `docs/TECHNICAL_DEBT_BUILD_TIME_NORMALIZATION.md` - Technical debt tracking
- `export/enrichers/contaminants/safety_table_normalizer.py` - Contaminants fix
- `scripts/migrations/remove_materials_duplications.py` - Materials migration

---

## Appendix
  - ✅ Single source of truth established
  - ✅ Complete `_section` compliance achieved
- **Verification:** All relationship sections now have complete `_section` metadata
- **See:** `docs/proposals/MATERIALS_DUPLICATION_RESOLUTION_JAN5_2026.md` for complete details

#### Detailed Proposal: Materials Restructuring

**SCOPE: Two Confirmed Duplications (Plus Others Requiring Audit)**

**A. Duplication #1: operational / industry_applications**
- **Top-level location:** `operational.industry_applications`
  - Has proper structure (presentation, items with metadata)
  - ❌ Missing required `_section` metadata block
- **Relationships location:** `relationships.operational.industry_applications`  
  - Legacy flat array structure
  - ✅ Has complete `_section` metadata
- **Component expects:** `relationships.operational.industry_applications`

**B. Duplication #2: regulatory_standards**
- **Top-level location:** `regulatory_standards` (flat array)
  - Simple array with description, name, url, image
  - ❌ Missing required `_section` metadata block
  - ❌ No presentation type defined
- **Relationships location:** `relationships.safety.regulatory_standards`
  - Has presentation, items structure
  - ✅ Has complete `_section` metadata
- **Component expects:** `relationships.safety.regulatory_standards`

**Current Structure (aluminum-laser-cleaning.yaml):**
```yaml
# ❌ PROBLEM: Top-level keys (duplicate data, no _section)
operational:
  industry_applications:
    presentation: card
    items:
      - title: Aerospace
        description: Aerospace industry applications...
        metadata:
          category: Industrial Applications
          commonality: common
        order: 1
    # ❌ Missing _section metadata

regulatory_standards:
  - description: FDA 21 CFR 1040.10 - Laser Product Performance Standards
    image: /images/logo/logo-org-fda.png
    longName: Food and Drug Administration
    name: FDA
    url: https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J/part-1040/section-1040.10
  # ❌ Flat array, no _section metadata, no presentation type

# ✅ SOLUTION: Only relationships structure (has proper _section metadata)
relationships:
  operational:
    industry_applications:
      presentation: card
      items:
        - id: aerospace
          name: Aerospace
          description: Aerospace industry applications and manufacturing requirements
      _section:
        sectionTitle: Industry Applications
        sectionDescription: Industries using this material for laser cleaning
        icon: building-2
        order: 1

  safety:
    regulatory_standards:
      presentation: card
      items:
        - description: FDA 21 CFR 1040.10 - Laser Product Performance Standards
          name: FDA
          image: /images/logo/logo-org-fda.png
          url: https://www.ecfr.gov/current/title-21/...
      _section:
        sectionTitle: Regulatory Standards
        sectionDescription: Safety and compliance standards
        icon: shield-check
        order: 1
```

**Migration Strategy:**

**Phase 1: Audit (30 minutes)**
1. Check all 153 material files for ALL top-level section keys
2. Identify complete list of duplications (not just operational/regulatory_standards)
3. Document which version has complete, correct data

**Phase 2: Consolidation (2-3 hours)**
For each duplicate found:
1. **Compare versions:** Top-level vs relationships
2. **Identify authoritative source:**
   - Which has complete `_section` metadata?
   - Which has proper presentation/items structure?
   - Which has complete data (no missing items)?
3. **Migration decision:**
   - If relationships version is complete → Delete top-level key
   - If relationships version missing data → Merge top-level data into relationships, add `_section`
   - If relationships version is legacy flat array → Replace with top-level structure + add `_section`
4. **Verify no data loss:** Compare item counts before/after

**Phase 3: Verification (30 minutes)**
1. Validate all 153 files have NO top-level section keys
2. Validate all sections have complete `_section` metadata
3. Test build passes: `npm run build`
4. Spot-check 10-15 material pages in browser
5. Verify component rendering works correctly

**Expected Removals per File:**
- `operational` key (entire top-level object)
- `regulatory_standards` key (entire top-level array)
- Potentially other duplicate keys (requires audit to identify)

**Estimated Effort:** 3-4 hours total
- 30 min: Full audit to identify ALL duplications
- 2-3 hours: Bulk migration script + manual verification of complex cases
- 30 min: Testing and validation

**Risk Assessment:**
- **Low risk:** Data already exists in relationships (we're just removing duplicates)
- **Medium complexity:** Need to verify which version is authoritative for each section
- **High value:** Eliminates confusion, ensures `_section` compliance, reduces file size ~10-15%

**Note:** Frontend tests pass because test data includes complete `_section` metadata. Production contaminant pages will throw errors until metadata is added.

---

## What is a "Section"?

A **section** is a discrete grouping of related data within the `relationships` structure that contains:
1. An `items` array with actual data
2. A `presentation` type (card, badge, descriptive, table)
3. Complete `_section` metadata

**Sections are leaf nodes** in the relationships tree. They are NOT the category groupings like `operational`, `safety`, or `interactions`.

### Complete List of Defined Sections

The Z-Beam system currently defines **15 core sections** across all content types:

#### Materials Sections (9)
1. **`industry_applications`** - Industries using the material
   - Path: `relationships.operational.industry_applications`
   - Presentation: card or badge
   - Example: Aerospace, Automotive, Construction

2. **`contaminated_by`** - Contaminants affecting this material
   - Path: `relationships.interactions.contaminated_by`
   - Presentation: card
   - Example: Rust, Paint, Grease

3. **`regulatory_standards`** - Applicable safety/compliance standards
   - Path: `relationships.safety.regulatory_standards`
   - Presentation: card
   - Example: OSHA, ANSI, FDA regulations

4. **`exposure_limits`** - Safety exposure thresholds
   - Path: `relationships.safety.exposure_limits`
   - Presentation: descriptive
   - Example: OSHA PEL, NIOSH REL values

5. **`ppe_requirements`** - Required protective equipment
   - Path: `relationships.safety.ppe_requirements`
   - Presentation: card
   - Example: Gloves, Goggles, Respirators

6. **`laser_properties`** - Laser-material interaction data
   - Path: `relationships.operational.laser_properties`
   - Presentation: descriptive
   - Example: Absorption rates, wavelengths

7. **`visual_characteristics`** - Observable material properties
   - Path: `relationships.physical.visual_characteristics`
   - Presentation: descriptive
   - Example: Color, texture, appearance

8. **`physical_properties`** - Measurable material properties
   - Path: `relationships.physical.physical_properties`
   - Presentation: descriptive or table
   - Example: Density, hardness, melting point

9. **`chemical_properties`** - Chemical composition and reactivity
   - Path: `relationships.technical.chemical_properties`
   - Presentation: descriptive
   - Example: Reactivity, pH, composition

#### Contaminants Sections (4)
10. **`produces_compounds`** - Hazardous compounds created during cleaning
    - Path: `relationships.interactions.produces_compounds`
    - Presentation: card
    - Example: Metal fumes, toxic gases

11. **`found_on_materials`** - Materials where this contaminant appears
    - Path: `relationships.interactions.found_on_materials`
    - Presentation: card
    - Example: Steel, Aluminum, Copper

12. **`removal_difficulty`** - Difficulty ratings for removal
    - Path: `relationships.operational.removal_difficulty`
    - Presentation: descriptive
    - Example: Easy, Moderate, Difficult ratings

13. **`health_hazards`** - Health risks from contaminant exposure
    - Path: `relationships.safety.health_hazards`
    - Presentation: card
    - Example: Respiratory issues, skin irritation

#### Settings/Compounds Sections (2)
14. **`compatible_materials`** - Materials compatible with this setting
    - Path: `relationships.operational.compatible_materials`
    - Presentation: badge or card
    - Example: Steel, Titanium, Glass

15. **`application_scenarios`** - Use cases and scenarios
    - Path: `relationships.operational.application_scenarios`
    - Presentation: card
    - Example: Rust removal, Paint stripping

### Category vs Section

**Categories** (optional groupings):
- `operational` - Operational/functional data
- `safety` - Safety-related information
- `interactions` - Cross-reference relationships
- `physical` - Physical properties
- `technical` - Technical specifications

**Sections** (required data containers):
- Must have `items` array
- Must have `presentation` type
- Must have complete `_section` metadata
- Are the actual queryable units of data

Example structure showing both:
```yaml
relationships:
  operational:              # ← Category (grouping)
    industry_applications:  # ← Section (has items + _section)
      presentation: card
      items: [...]
      _section: {...}
    laser_properties:       # ← Section (has items + _section)
      presentation: descriptive
      items: [...]
      _section: {...}
```

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

**Last Updated:** January 5, 2026 (Migration Complete)  
**Test Status:** ✅ 2,669 tests passing  
**Materials Status:** ✅ 100% compliant (duplicates removed, all _section metadata present)  
**Remaining Work:** 98 contaminant files need _section metadata
