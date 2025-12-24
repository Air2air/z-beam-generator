# Relationships Structure Redesign - Backend Implementation Spec
**Date**: December 23, 2025  
**Priority**: HIGH  
**Estimated Effort**: 3-4 weeks  
**Impact**: 403 frontmatter files

---

## Executive Summary

Redesign relationships structure for improved usability, consistency, and scannability for laser cleaning professionals (engineers, facility managers, technicians).

**Key Changes**:
1. **Consolidate duplicate fields** (`valid_materials` → `found_on_materials`)
2. **Rename fields for consistency** (standardize verb tense and perspective)
3. **Add hierarchical grouping** (technical, safety, operational)
4. **Add missing professional context** (time estimates, difficulty, equipment)

**Goal**: Make data digestible for target audience while maintaining technical accuracy.

---

## Phase 1: Field Consolidation & Renaming

### 1.1 Eliminate Duplicate Field

**Change**: Remove `valid_materials`, keep `found_on_materials`

**Files Affected**: 97 contaminants

**Migration**:
```yaml
# BEFORE
relationships:
  valid_materials:
    items:
      - Granite
      - Marble
      - Limestone
  found_on_materials:
    items:
      - id: granite-laser-cleaning
      - id: marble-laser-cleaning

# AFTER
relationships:
  found_on_materials:
    items:
      - id: granite-laser-cleaning
      - id: marble-laser-cleaning
      - id: limestone-laser-cleaning
```

**Migration Script Required**: Convert string-only `valid_materials` to ID format, merge with `found_on_materials`

---

### 1.2 Rename Fields for Consistency

**Naming Convention**: Use consistent verb tense and clear relationships

| Current Name | New Name | Rationale | Files Affected |
|--------------|----------|-----------|----------------|
| `valid_materials` | ❌ **REMOVE** | Duplicate, misleading term | 97 contaminants |
| `found_on_materials` | `affects_materials` | Clearer cause-effect | 97 contaminants |
| `contaminated_by` | `contaminated_by` | ✅ Keep (already clear) | 153 materials |
| `optimized_for_materials` | `works_on_materials` | Clearer action | 153 settings |
| `removes_contaminants` | `removes_contaminants` | ✅ Keep (already clear) | 153 settings |
| `produces_compounds` | `produces_compounds` | ✅ Keep (already clear) | 97 contaminants |

**Implementation**:
```yaml
# CONTAMINANTS: Before
relationships:
  found_on_materials: [...]
  
# CONTAMINANTS: After
relationships:
  affects_materials: [...]  # Renamed

# SETTINGS: Before
relationships:
  optimized_for_materials: [...]
  
# SETTINGS: After
relationships:
  works_on_materials: [...]  # Renamed
```

---

## Phase 2: Add Hierarchical Organization

### 2.1 Group Related Fields

**New Structure**: Three top-level categories under `relationships`

```yaml
relationships:
  # GROUP 1: Technical Specifications
  technical:
    compatible_materials: [...]      # Renamed from affects_materials/works_on_materials
    incompatible_materials: [...]    # Renamed from prohibited_materials
    removes_contaminants: [...]
    produces_compounds: [...]
    laser_parameters: [...]          # Link to settings
  
  # GROUP 2: Safety & Compliance
  safety:
    regulatory_standards: [...]
    ppe_requirements: [...]
    hazardous_compounds: [...]       # From produces_compounds where hazardous
    ventilation_required: boolean
    exposure_limits: [...]
  
  # GROUP 3: Operational Guidance
  operational:
    difficulty_level: enum           # NEW: easy|medium|hard|expert
    typical_time_per_sqm: string     # NEW: "15-30 min/m²"
    equipment_required: [...]        # NEW: [fiber_laser, fume_extractor]
    common_challenges: [...]         # Renamed from challenges
    best_practices: [...]            # NEW
    industry_applications: [...]     # Moved from top-level applications
```

---

### 2.2 Detailed Field Specifications

#### **Technical Group**

**Field: `compatible_materials`**
```yaml
technical:
  compatible_materials:
    presentation: card
    items:
      - id: granite-laser-cleaning
        effectiveness: high
        notes: "Excellent results on polished granite"
      - id: marble-laser-cleaning
        effectiveness: medium
        notes: "Requires careful power control"
    _section:
      title: Compatible Materials
      icon: check-circle
      order: 1
```

**Field: `incompatible_materials`** (renamed from `prohibited_materials`)
```yaml
technical:
  incompatible_materials:
    presentation: card
    items:
      - id: glass-laser-cleaning
        reason: "Risk of thermal shock"
      - id: thin-plastic-laser-cleaning
        reason: "Melting hazard"
    _section:
      title: Incompatible Materials
      icon: alert-triangle
      order: 2
      variant: danger
```

---

#### **Safety Group**

**NEW Field: `ppe_requirements`**
```yaml
safety:
  ppe_requirements:
    items:
      - id: laser-safety-goggles
        requirement_level: mandatory
        specification: "OD 7+ at 1064nm"
      - id: respiratory-protection
        requirement_level: recommended
        specification: "P100 filter or supplied air"
      - id: protective-gloves
        requirement_level: mandatory
        specification: "Heat-resistant, non-reflective"
    _section:
      title: Required PPE
      icon: shield
      variant: warning
```

**Field: `hazardous_compounds`** (extracted from produces_compounds)
```yaml
safety:
  hazardous_compounds:
    items:
      - id: chromium-vi-compound
        hazard_level: critical
        exposure_limit: "0.005 mg/m³ (OSHA)"
        immediate_action: "Evacuate area, ventilate, PPE required"
      - id: lead-oxide-compound
        hazard_level: high
        exposure_limit: "0.05 mg/m³ (OSHA)"
    _section:
      title: Hazardous Compounds Produced
      icon: skull
      variant: danger
```

**NEW Field: `ventilation_required`**
```yaml
safety:
  ventilation_required: true
  ventilation_spec: "Local exhaust with HEPA filtration, 500+ CFM"
```

---

#### **Operational Group**

**NEW Field: `difficulty_level`**
```yaml
operational:
  difficulty_level: medium
  difficulty_factors:
    - "Requires precise power control"
    - "Multiple passes needed"
    - "Surface preparation critical"
```

**Enum values**: `easy` | `medium` | `hard` | `expert`

**NEW Field: `typical_time_per_sqm`**
```yaml
operational:
  typical_time_per_sqm: "15-30 min/m²"
  time_factors:
    - "Heavy contamination: +50% time"
    - "Complex geometry: +30% time"
    - "Final pass for quality: +10 min"
```

**NEW Field: `equipment_required`**
```yaml
operational:
  equipment_required:
    items:
      - id: fiber-laser
        specification: "1064nm, 100-500W"
        necessity: mandatory
      - id: fume-extractor
        specification: "HEPA filtration, 500+ CFM"
        necessity: mandatory
      - id: surface-preparation-tools
        specification: "Wire brush, compressed air"
        necessity: recommended
```

**Field: `common_challenges`** (renamed from `challenges`)
```yaml
operational:
  common_challenges:
    items:
      - challenge: "Thermal shock on thick oxides"
        severity: high
        solution: "Use lower power with multiple passes"
        frequency: common
      - challenge: "Incomplete removal in recesses"
        severity: medium
        solution: "Adjust scan angle, reduce speed"
        frequency: occasional
    _section:
      title: Common Problems & Solutions
      icon: wrench
```

**NEW Field: `best_practices`**
```yaml
operational:
  best_practices:
    items:
      - "Always start with lowest effective power"
      - "Test on inconspicuous area first"
      - "Maintain 15-20° scan angle for optimal ablation"
      - "Clean fume extractor filters every 4 hours"
      - "Allow surface to cool between passes (2-5 minutes)"
```

**Field: `industry_applications`** (moved from top-level `applications`)
```yaml
operational:
  industry_applications:
    items:
      - id: aerospace
        relevance: high
        use_cases:
          - "Aircraft skin cleaning"
          - "Engine component restoration"
          - "Pre-coating surface prep"
      - id: automotive
        relevance: high
        use_cases:
          - "Body panel rust removal"
          - "Engine block cleaning"
          - "Weld preparation"
      - id: cultural-heritage
        relevance: medium
        use_cases:
          - "Monument restoration"
          - "Artifact cleaning"
    _section:
      title: Industry Applications
      icon: building
```

---

## Phase 3: Schema Updates

### 3.1 Remove Deprecated Fields

```json
{
  "relationships": {
    "properties": {
      // REMOVE these fields
      "valid_materials": {},           // ❌ REMOVE
      "prohibited_materials": {},      // ❌ REMOVE (rename to incompatible_materials)
      "challenges": {}                 // ❌ REMOVE (move to operational.common_challenges)
    }
  }
}
```

### 3.2 Add New Structure

```json
{
  "relationships": {
    "type": "object",
    "properties": {
      "technical": {
        "type": "object",
        "properties": {
          "compatible_materials": {
            "$ref": "#/definitions/relationship_block"
          },
          "incompatible_materials": {
            "$ref": "#/definitions/relationship_block"
          },
          "removes_contaminants": {
            "$ref": "#/definitions/relationship_block"
          },
          "produces_compounds": {
            "$ref": "#/definitions/relationship_block"
          }
        }
      },
      "safety": {
        "type": "object",
        "properties": {
          "regulatory_standards": {
            "$ref": "#/definitions/relationship_block"
          },
          "ppe_requirements": {
            "$ref": "#/definitions/relationship_block"
          },
          "hazardous_compounds": {
            "$ref": "#/definitions/relationship_block"
          },
          "ventilation_required": {
            "type": "boolean"
          },
          "ventilation_spec": {
            "type": "string"
          }
        }
      },
      "operational": {
        "type": "object",
        "properties": {
          "difficulty_level": {
            "type": "string",
            "enum": ["easy", "medium", "hard", "expert"]
          },
          "typical_time_per_sqm": {
            "type": "string",
            "pattern": "^\\d+-\\d+ min/m²$"
          },
          "equipment_required": {
            "$ref": "#/definitions/relationship_block"
          },
          "common_challenges": {
            "$ref": "#/definitions/relationship_block"
          },
          "best_practices": {
            "type": "object",
            "properties": {
              "items": {
                "type": "array",
                "items": {"type": "string"}
              }
            }
          },
          "industry_applications": {
            "$ref": "#/definitions/relationship_block"
          }
        }
      }
    }
  }
}
```

### 3.3 Relationship Block Definition

```json
{
  "definitions": {
    "relationship_block": {
      "type": "object",
      "required": ["items"],
      "properties": {
        "presentation": {
          "type": "string",
          "enum": ["card", "list", "table"]
        },
        "items": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id"],
            "properties": {
              "id": {"type": "string"},
              "effectiveness": {
                "type": "string",
                "enum": ["low", "medium", "high"]
              },
              "relevance": {
                "type": "string",
                "enum": ["low", "medium", "high"]
              },
              "notes": {"type": "string"},
              "specification": {"type": "string"},
              "necessity": {
                "type": "string",
                "enum": ["optional", "recommended", "mandatory"]
              }
            }
          }
        },
        "_section": {
          "type": "object",
          "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "icon": {"type": "string"},
            "order": {"type": "integer"},
            "variant": {
              "type": "string",
              "enum": ["default", "success", "warning", "danger"]
            }
          }
        }
      }
    }
  }
}
```

---

## Phase 4: Migration Scripts

### 4.1 Consolidate valid_materials → found_on_materials

**Script**: `scripts/migrations/consolidate-valid-materials.js`

```javascript
const yaml = require('js-yaml');
const fs = require('fs');
const glob = require('glob');

// Find all contaminant files
const files = glob.sync('frontmatter/contaminants/*.yaml');

files.forEach(filepath => {
  const data = yaml.load(fs.readFileSync(filepath, 'utf8'));
  
  if (!data.relationships) return;
  
  const rels = data.relationships;
  
  // If has valid_materials
  if (rels.valid_materials && rels.valid_materials.items) {
    const validMaterials = rels.valid_materials.items;
    
    // Convert strings to ID objects
    const converted = validMaterials.map(material => {
      // Convert "Granite" -> "granite-laser-cleaning"
      const id = material.toLowerCase().replace(/\s+/g, '-') + '-laser-cleaning';
      return { id };
    });
    
    // Merge with found_on_materials
    if (!rels.found_on_materials) {
      rels.found_on_materials = { items: [] };
    }
    
    // Add converted items (avoid duplicates)
    const existingIds = new Set(
      rels.found_on_materials.items.map(item => item.id)
    );
    
    converted.forEach(item => {
      if (!existingIds.has(item.id)) {
        rels.found_on_materials.items.push(item);
      }
    });
    
    // Remove valid_materials
    delete rels.valid_materials;
    
    // Save
    fs.writeFileSync(filepath, yaml.dump(data, {lineWidth: -1}));
    console.log(`✅ Migrated: ${filepath}`);
  }
});
```

---

### 4.2 Rename Fields

**Script**: `scripts/migrations/rename-relationship-fields.js`

```javascript
const yaml = require('js-yaml');
const fs = require('fs');
const glob = require('glob');

const RENAMES = [
  {
    pattern: 'frontmatter/contaminants/*.yaml',
    from: 'found_on_materials',
    to: 'affects_materials'
  },
  {
    pattern: 'frontmatter/settings/*.yaml',
    from: 'optimized_for_materials',
    to: 'works_on_materials'
  },
  {
    pattern: 'frontmatter/**/*.yaml',
    from: 'prohibited_materials',
    to: 'incompatible_materials'
  },
  {
    pattern: 'frontmatter/**/*.yaml',
    from: 'challenges',
    to: 'common_challenges'
  }
];

RENAMES.forEach(({pattern, from, to}) => {
  const files = glob.sync(pattern);
  
  files.forEach(filepath => {
    const data = yaml.load(fs.readFileSync(filepath, 'utf8'));
    
    if (data.relationships && data.relationships[from]) {
      // Rename field
      data.relationships[to] = data.relationships[from];
      delete data.relationships[from];
      
      // Save
      fs.writeFileSync(filepath, yaml.dump(data, {lineWidth: -1}));
      console.log(`✅ Renamed ${from} → ${to} in ${filepath}`);
    }
  });
});
```

---

### 4.3 Add Hierarchical Structure

**Script**: `scripts/migrations/add-hierarchical-structure.js`

```javascript
const yaml = require('js-yaml');
const fs = require('fs');
const glob = require('glob');

// Field mappings to new groups
const TECHNICAL_FIELDS = [
  'affects_materials',
  'works_on_materials',
  'incompatible_materials',
  'removes_contaminants',
  'produces_compounds',
  'contaminated_by',
  'produced_from_materials',
  'produced_from_contaminants'
];

const SAFETY_FIELDS = [
  'regulatory_standards',
  'ppe_requirements',
  'exposure_limits',
  'emergency_response',
  'hazardous_compounds'
];

const OPERATIONAL_FIELDS = [
  'common_challenges',
  'best_practices',
  'industry_applications',
  'equipment_required'
];

const files = glob.sync('frontmatter/**/*.yaml');

files.forEach(filepath => {
  const data = yaml.load(fs.readFileSync(filepath, 'utf8'));
  
  if (!data.relationships) return;
  
  const rels = data.relationships;
  const newRels = {
    technical: {},
    safety: {},
    operational: {}
  };
  
  // Categorize existing fields
  Object.keys(rels).forEach(field => {
    if (TECHNICAL_FIELDS.includes(field)) {
      newRels.technical[field] = rels[field];
    } else if (SAFETY_FIELDS.includes(field)) {
      newRels.safety[field] = rels[field];
    } else if (OPERATIONAL_FIELDS.includes(field)) {
      newRels.operational[field] = rels[field];
    } else {
      // Keep uncategorized fields at root for now
      newRels[field] = rels[field];
    }
  });
  
  // Clean up empty groups
  if (Object.keys(newRels.technical).length === 0) delete newRels.technical;
  if (Object.keys(newRels.safety).length === 0) delete newRels.safety;
  if (Object.keys(newRels.operational).length === 0) delete newRels.operational;
  
  data.relationships = newRels;
  
  // Save
  fs.writeFileSync(filepath, yaml.dump(data, {lineWidth: -1}));
  console.log(`✅ Restructured: ${filepath}`);
});
```

---

### 4.4 Move applications to relationships

**Script**: `scripts/migrations/move-applications-to-relationships.js`

```javascript
const yaml = require('js-yaml');
const fs = require('fs');
const glob = require('glob');

const files = glob.sync('frontmatter/materials/*.yaml');

files.forEach(filepath => {
  const data = yaml.load(fs.readFileSync(filepath, 'utf8'));
  
  // If has top-level applications
  if (data.applications && Array.isArray(data.applications)) {
    // Convert to structured format
    const structured = {
      presentation: 'card',
      items: data.applications.map(app => ({
        id: app.toLowerCase().replace(/\s+/g, '-'),
        name: app,
        relevance: 'high'
      })),
      _section: {
        title: 'Industry Applications',
        icon: 'building',
        order: 20
      }
    };
    
    // Move to relationships.operational.industry_applications
    if (!data.relationships) data.relationships = {};
    if (!data.relationships.operational) data.relationships.operational = {};
    
    data.relationships.operational.industry_applications = structured;
    
    // Remove top-level applications
    delete data.applications;
    
    // Save
    fs.writeFileSync(filepath, yaml.dump(data, {lineWidth: -1}));
    console.log(`✅ Moved applications to relationships: ${filepath}`);
  }
});
```

---

## Phase 5: Add New Operational Fields

### 5.1 Add difficulty_level (AI-generated or manual)

**Script**: `scripts/migrations/add-difficulty-level.js`

```javascript
// Generate difficulty based on challenges count and severity
const calculateDifficulty = (data) => {
  const challenges = data.relationships?.operational?.common_challenges?.items || [];
  
  if (challenges.length === 0) return 'easy';
  
  const criticalCount = challenges.filter(c => c.severity === 'critical').length;
  const highCount = challenges.filter(c => c.severity === 'high').length;
  
  if (criticalCount >= 2 || highCount >= 3) return 'expert';
  if (criticalCount >= 1 || highCount >= 2) return 'hard';
  if (highCount >= 1 || challenges.length >= 3) return 'medium';
  return 'easy';
};

// Apply to all files
files.forEach(filepath => {
  const data = yaml.load(fs.readFileSync(filepath, 'utf8'));
  
  if (!data.relationships?.operational) {
    if (!data.relationships) data.relationships = {};
    data.relationships.operational = {};
  }
  
  data.relationships.operational.difficulty_level = calculateDifficulty(data);
  
  fs.writeFileSync(filepath, yaml.dump(data, {lineWidth: -1}));
});
```

---

### 5.2 Add typical_time_per_sqm (manual or estimated)

**Default Values by Material Type**:
```javascript
const DEFAULT_TIMES = {
  metal: '10-20 min/m²',
  stone: '15-30 min/m²',
  plastic: '5-15 min/m²',
  wood: '10-25 min/m²',
  ceramic: '15-30 min/m²',
  glass: '5-10 min/m²'
};
```

---

## Phase 6: Frontend Component Updates

### 6.1 Components to Update

**Files requiring changes**:
```
app/components/relationships/RelationshipsSection.tsx
app/components/relationships/TechnicalRelationships.tsx   (NEW)
app/components/relationships/SafetyRelationships.tsx      (NEW)
app/components/relationships/OperationalRelationships.tsx (NEW)
app/components/cards/MaterialCard.tsx
app/components/cards/ContaminantCard.tsx
app/materials/[...slug]/page.tsx
app/contaminants/[...slug]/page.tsx
app/settings/[...slug]/page.tsx
```

### 6.2 Update Type Definitions

**File**: `types/centralized.ts`

```typescript
// Add new enums
export type DifficultyLevel = 'easy' | 'medium' | 'hard' | 'expert';
export type NecessityLevel = 'optional' | 'recommended' | 'mandatory';
export type HazardLevel = 'low' | 'medium' | 'high' | 'critical';

// Update relationships structure
export interface Relationships {
  technical?: TechnicalRelationships;
  safety?: SafetyRelationships;
  operational?: OperationalRelationships;
}

export interface TechnicalRelationships {
  compatible_materials?: RelationshipBlock<MaterialRelationshipItem>;
  incompatible_materials?: RelationshipBlock<IncompatibleMaterialItem>;
  removes_contaminants?: RelationshipBlock<ContaminantRelationshipItem>;
  produces_compounds?: RelationshipBlock<CompoundRelationshipItem>;
}

export interface SafetyRelationships {
  regulatory_standards?: RelationshipBlock<RegulatoryItem>;
  ppe_requirements?: RelationshipBlock<PPEItem>;
  hazardous_compounds?: RelationshipBlock<HazardousCompoundItem>;
  ventilation_required?: boolean;
  ventilation_spec?: string;
}

export interface OperationalRelationships {
  difficulty_level?: DifficultyLevel;
  typical_time_per_sqm?: string;
  equipment_required?: RelationshipBlock<EquipmentItem>;
  common_challenges?: RelationshipBlock<ChallengeItem>;
  best_practices?: BestPractices;
  industry_applications?: RelationshipBlock<IndustryApplicationItem>;
}

export interface RelationshipBlock<T> {
  presentation?: 'card' | 'list' | 'table';
  items: T[];
  _section?: SectionMetadata;
}

export interface PPEItem {
  id: string;
  requirement_level: NecessityLevel;
  specification: string;
}

export interface HazardousCompoundItem {
  id: string;
  hazard_level: HazardLevel;
  exposure_limit?: string;
  immediate_action?: string;
}

export interface EquipmentItem {
  id: string;
  specification: string;
  necessity: NecessityLevel;
}

export interface ChallengeItem {
  challenge: string;
  severity: HazardLevel;
  solution: string;
  frequency?: 'rare' | 'occasional' | 'common' | 'frequent';
}

export interface IndustryApplicationItem {
  id: string;
  name?: string;
  relevance: 'low' | 'medium' | 'high';
  use_cases?: string[];
}
```

---

## Phase 7: Testing & Validation

### 7.1 Validation Scripts

**Test 1: No deprecated fields remain**
```bash
# Should return 0 results
grep -r "valid_materials:" frontmatter/
grep -r "prohibited_materials:" frontmatter/
grep -r "^  challenges:" frontmatter/
grep -r "^applications:" frontmatter/materials/
```

**Test 2: All files have hierarchical structure**
```bash
# Should return all files
grep -r "relationships:" frontmatter/ | wc -l
grep -r "technical:" frontmatter/ | wc -l
```

**Test 3: Schema validation**
```bash
node scripts/validate-frontmatter-schema.js
```

---

### 7.2 Manual Testing Checklist

- [ ] Load material page - verify technical relationships display
- [ ] Load contaminant page - verify safety warnings prominent
- [ ] Load settings page - verify operational guidance clear
- [ ] Check difficulty badges render correctly
- [ ] Verify time estimates display
- [ ] Test equipment requirements section
- [ ] Check best practices list formatting
- [ ] Verify industry applications cards
- [ ] Test mobile responsiveness
- [ ] Verify SEO metadata updated

---

## Phase 8: Documentation Updates

### 8.1 Update Documentation Files

**Files to update**:
```
docs/FRONTMATTER_GENERATION_GUIDE.md
docs/01-core/frontmatter/STRUCTURE.md
schemas/frontmatter-v5.0.0.json → frontmatter-v6.0.0.json
examples/aluminum-unified-frontmatter.yaml
README.md (if mentions relationships)
```

### 8.2 Add Migration Guide

**File**: `docs/migrations/RELATIONSHIPS-V6-MIGRATION.md`

Include:
- Changelog of field changes
- Before/after examples
- Common issues and solutions
- Rollback procedure

---

## Timeline & Milestones

### Week 1: Consolidation & Renaming
- [ ] Day 1-2: Write and test migration scripts
- [ ] Day 3: Run consolidation (valid_materials removal)
- [ ] Day 4: Run field renaming
- [ ] Day 5: Validation and fixes

### Week 2: Hierarchical Restructure
- [ ] Day 1-2: Add hierarchical grouping
- [ ] Day 3: Move applications to relationships
- [ ] Day 4-5: Validation and refinement

### Week 3: Add New Fields
- [ ] Day 1-2: Generate/add difficulty levels
- [ ] Day 2-3: Add time estimates (manual review)
- [ ] Day 4: Add equipment requirements
- [ ] Day 5: Validation

### Week 4: Frontend & Testing
- [ ] Day 1-2: Update type definitions
- [ ] Day 2-3: Update components
- [ ] Day 4: Full testing pass
- [ ] Day 5: Documentation and deploy

---

## Rollback Plan

If issues arise:

1. **Keep backups**: Create `frontmatter-backup-YYYYMMDD/` before migration
2. **Atomic commits**: One migration script = one commit
3. **Feature flags**: Use environment variable to toggle new structure
4. **Gradual rollout**: Test on staging first, then production

**Rollback command**:
```bash
git revert <commit-hash>
# OR restore from backup
rm -rf frontmatter/
cp -r frontmatter-backup-20251223/ frontmatter/
```

---

## Success Criteria

### Technical
- ✅ Zero instances of deprecated fields
- ✅ 100% schema validation pass rate
- ✅ All relationship IDs resolve to valid entities
- ✅ TypeScript compilation succeeds
- ✅ All tests pass

### User Experience
- ✅ Engineers can quickly scan technical specs
- ✅ Safety info is prominent and grouped
- ✅ Facility managers can estimate project scope (time, equipment)
- ✅ Technicians can find troubleshooting guidance easily
- ✅ Page load time unchanged or improved

### Business
- ✅ Zero user complaints about missing data
- ✅ Improved engagement metrics (time on page, pages per session)
- ✅ Reduced support queries about "which materials work"

---

## Contact & Approval

**Backend Lead**: [Name]  
**Frontend Lead**: [Name]  
**Product Owner**: [Name]  

**Approval Required From**:
- [ ] Backend team (data structure changes)
- [ ] Frontend team (component updates)
- [ ] Product owner (UX changes)
- [ ] QA team (testing scope)

**Questions?** Contact: [Your contact info]

---

**Status**: 🟡 Awaiting Approval  
**Priority**: HIGH  
**Risk Level**: MEDIUM (breaking changes, but planned migration)  
**Estimated Value**: HIGH (improved usability for target audience)
