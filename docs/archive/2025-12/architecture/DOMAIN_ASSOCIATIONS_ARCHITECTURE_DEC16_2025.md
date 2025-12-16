# Domain Associations Architecture
**Status**: ✅ IMPLEMENTED  
**Date**: December 16, 2025  
**Purpose**: Centralized, validated, bidirectional cross-domain relationships

---

## 📋 Overview

The **Domain Associations** system provides a single source of truth for all cross-domain relationships in the Z-Beam content system. It replaces scattered linkage data with a centralized, validated, research-backed approach that automatically ensures bidirectionality.

### Key Benefits

1. **✅ Single Source of Truth** - All relationships in one file
2. **✅ Automatic Bidirectionality** - Impossible to have one-way links
3. **✅ Built-in Validation** - IDs, URLs, and data verified before export
4. **✅ Research Verification** - Every relationship tracked with source
5. **✅ Fail-Fast Architecture** - Invalid associations block exports
6. **✅ Centralized Management** - Easy to review, update, audit

---

## 🏗️ Architecture

### File Structure

```
data/associations/
├── DomainAssociations.yaml     # Primary associations file
└── ExtractedLinkages.yaml      # Extracted from existing frontmatter
```

### Data Flow

```
┌─────────────────────────────────────────────────────┐
│  data/associations/DomainAssociations.yaml          │
│  ═══════════════════════════════════════════        │
│  • material_contaminant_associations (1962)         │
│  • contaminant_compound_associations (78)           │
│  • material_compound_associations (transitive)      │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓ (Load & Validate)
┌─────────────────────────────────────────────────────┐
│  shared/validation/domain_associations.py           │
│  ═══════════════════════════════════════            │
│  • Validate all IDs exist in source data            │
│  • Check frequency/severity values                  │
│  • Verify research sources                          │
│  • Validate URLs                                    │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓ (Generate Bidirectional Links)
┌─────────────────────────────────────────────────────┐
│  export/*/trivial_exporter.py                       │
│  ═══════════════════════════                        │
│  • Read associations for domain                     │
│  • Generate forward linkages                        │
│  • Generate reverse linkages                        │
│  • Inject into frontmatter                          │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓ (Output)
┌─────────────────────────────────────────────────────┐
│  frontmatter/*/                                     │
│  ═══════════════                                    │
│  • All files have complete bidirectional links      │
│  • Validated URLs                                   │
│  • Research-backed relationships                    │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Association Schema

### Material ↔ Contaminant Association

```yaml
material_contaminant_associations:
  - material_id: aluminum-laser-cleaning         # Required
    contaminant_id: oxidation-contamination      # Required
    frequency: very_common                       # Required: very_common|common|occasional|rare
    severity: moderate                           # Required: critical|high|moderate|low
    typical_context: "Aluminum naturally oxidizes in air"
    verified: true                               # Required: true|false
    verification_source: "ASM Materials Handbook Vol 2, 2024"  # Required if verified=true
    notes: "Anodized layers require higher fluence"
```

**Generates**:
- `materials/aluminum-laser-cleaning.yaml` → `domain_linkages.related_contaminants`
- `contaminants/oxidation-contamination.yaml` → `domain_linkages.related_materials`

### Contaminant ↔ Compound Association

```yaml
contaminant_compound_associations:
  - contaminant_id: carbon-buildup-contamination  # Required
    compound_id: pahs-compound                    # Required
    frequency: very_common                        # Required
    severity: high                                # Required
    typical_context: "Vaporization and reformation of existing PAHs"
    verified: true                                # Required
    verification_source: "NIOSH 5506 - PAH analysis"  # Required if verified=true
    notes: "Pre-existing PAHs become airborne during ablation"
```

**Generates**:
- `contaminants/carbon-buildup-contamination.yaml` → `domain_linkages.produces_compounds`
- `compounds/pahs-compound.yaml` → `domain_linkages.produced_by_contaminants`

### Material ↔ Compound Association (Transitive)

```yaml
material_compound_associations:
  - material_id: steel-laser-cleaning
    compound_id: pahs-compound
    via_contaminants:                            # Generated automatically
      - rust-oxidation-contamination
      - paint-residue-contamination
    exposure_risk: moderate
    source: laser_ablation
    verified: true
    verification_source: "Derived from contaminant associations"
```

**Generates**:
- `materials/steel-laser-cleaning.yaml` → `domain_linkages.related_compounds`
- `compounds/pahs-compound.yaml` → `domain_linkages.related_materials`

---

## 🔧 Usage

### 1. Validate Associations

```bash
python3 shared/validation/domain_associations.py
```

**Output**:
```
✅ Domain associations validation PASSED

Statistics:
  Total associations: 2040
  Material ↔ Contaminant: 1962
  Contaminant ↔ Compound: 78
  Material ↔ Compound: 0 (auto-generated)
  Verified: 16 (0.8%)
```

### 2. Extract Existing Linkages

```bash
python3 scripts/data/extract_existing_linkages.py
```

Extracts all linkages from frontmatter files → `data/associations/ExtractedLinkages.yaml`

### 3. Use in Exporters

```python
from shared.validation.domain_associations import DomainAssociationsValidator

# Initialize and validate
validator = DomainAssociationsValidator()
validator.validate_all()  # Raises ValueError if invalid

# Get bidirectional linkages
contaminants = validator.get_contaminants_for_material('aluminum-laser-cleaning')
compounds = validator.get_compounds_for_contaminant('rust-oxidation-contamination')
materials = validator.get_materials_for_compound('pahs-compound')  # Reverse lookup

# Inject into frontmatter during export
material_data['domain_linkages']['related_contaminants'] = contaminants
contaminant_data['domain_linkages']['produces_compounds'] = compounds
```

---

## ✅ Validation Rules

### Required Fields
- Source ID (`material_id` or `contaminant_id`)
- Target ID (`contaminant_id` or `compound_id`)
- `frequency` (very_common|common|occasional|rare)
- `severity` (critical|high|moderate|low)
- `verified` (true|false)

### ID Validation
- All IDs must exist in source data files
- `material_id` validated against `data/materials/Materials.yaml`
- `contaminant_id` validated against `data/contaminants/Contaminants.yaml`
- `compound_id` validated against `data/compounds/Compounds.yaml`

### URL Validation
- All generated URLs validated against target domain structure
- Fails if target file doesn't exist
- Validates URL format matches domain conventions

### Verification Requirements
- `verified=true` requires `verification_source`
- Unverified associations generate warnings
- Can configure to block export if unverified (strict mode)

---

## 📊 Current Status (Dec 16, 2025)

### Extraction Complete
- ✅ **1962** Material ↔ Contaminant associations extracted
- ✅ **78** Contaminant ↔ Compound associations extracted
- ✅ **2040** Total associations captured

### Verification Status
- ✅ **16** Manually verified associations (0.8%)
- ⚠️ **2024** Require verification (99.2%)
- 📝 All have placeholders with `verified: false`

### Implementation Status
- ✅ Schema defined (`DomainAssociations.yaml`)
- ✅ Validator implemented (`domain_associations.py`)
- ✅ Extraction tool created (`extract_existing_linkages.py`)
- ⏳ Exporter integration (next step)
- ⏳ Test suite (next step)

---

## 🚀 Next Steps

### 1. Verification Campaign
**Priority**: HIGH  
**Timeline**: 2-3 weeks

Review all 2040 associations and add `verification_source`:
- Scientific papers
- Material handbooks
- OSHA/NIOSH documentation
- Lab analysis reports
- Industry standards

### 2. Exporter Integration
**Priority**: CRITICAL  
**Timeline**: 1-2 days

Update all exporters to read from `DomainAssociations.yaml`:
- `export/core/trivial_exporter.py` (Materials, Settings)
- `export/contaminants/trivial_exporter.py` (Contaminants)
- `export/compounds/trivial_exporter.py` (Compounds)

### 3. Test Suite
**Priority**: HIGH  
**Timeline**: 1 day

Create comprehensive tests:
- Bidirectional completeness validation
- URL validation tests
- Verification status checks
- Edge case handling

### 4. Documentation
**Priority**: MEDIUM  
**Timeline**: 2 hours

Update system documentation:
- Development workflow guides
- Contribution guidelines
- API documentation

---

## 🔒 Mandatory Requirements

### Enforced by Validator
1. ✅ All IDs must exist in source data
2. ✅ All associations have valid frequency/severity
3. ✅ verified=true requires verification_source
4. ✅ No duplicate associations allowed
5. ✅ URL format validated

### Enforced by Exporters (After Integration)
1. ⏳ Bidirectional linkages automatically generated
2. ⏳ Invalid associations block export
3. ⏳ All URLs validated before export
4. ⏳ Unverified associations generate warnings

### Enforced by Tests (After Implementation)
1. ⏳ 100% bidirectional completeness required
2. ⏳ All linkages have validated URLs
3. ⏳ Verification rate tracked and reported
4. ⏳ No orphaned relationships allowed

---

## 📁 Related Files

### Implementation
- `data/associations/DomainAssociations.yaml` - Primary associations file
- `data/associations/ExtractedLinkages.yaml` - Extracted linkages (2040 total)
- `shared/validation/domain_associations.py` - Validator (518 lines)
- `scripts/data/extract_existing_linkages.py` - Extraction tool (284 lines)

### Documentation
- `docs/DOMAIN_LINKAGES_STRUCTURE.md` - Linkage structure specification
- `docs/FORMAL_LINKAGE_SPECIFICATION.md` - Original spec (superseded)
- `DOMAIN_LINKAGES_MIGRATION_COMPLETE_DEC15_2025.md` - Migration history

### Exporters (To Be Updated)
- `export/core/trivial_exporter.py` - Materials & Settings exporter
- `export/contaminants/trivial_exporter.py` - Contaminants exporter
- `export/compounds/trivial_exporter.py` - Compounds exporter

---

## 🎯 Success Criteria

### Phase 1: Foundation (COMPLETE ✅)
- [x] Schema defined
- [x] Validator implemented
- [x] Extraction tool created
- [x] 2040 associations extracted

### Phase 2: Integration (IN PROGRESS 🔄)
- [ ] Exporters updated to use associations
- [ ] Tests created and passing
- [ ] Documentation complete
- [ ] All frontmatter regenerated

### Phase 3: Verification (PENDING ⏳)
- [ ] 50%+ associations verified
- [ ] Research sources documented
- [ ] Quality review complete
- [ ] Production deployment

---

## 💡 Key Insights

### Why Centralized Associations?

**Before** (Scattered):
```yaml
# compounds/pahs-compound.yaml
domain_linkages:
  produced_by_contaminants:
    - id: carbon-buildup
      # ... metadata

# contaminants/carbon-buildup-contamination.yaml
# ❌ MISSING: produces_compounds section
# ❌ ONE-WAY RELATIONSHIP
```

**After** (Centralized):
```yaml
# data/associations/DomainAssociations.yaml
contaminant_compound_associations:
  - contaminant_id: carbon-buildup-contamination
    compound_id: pahs-compound
    # ... metadata

# ✅ Exporters generate BOTH directions automatically
# ✅ Impossible to have one-way relationships
# ✅ Single place to validate and maintain
```

### Benefits Realized

1. **Maintainability**: Update one file, not 424 frontmatter files
2. **Quality**: All relationships validated before export
3. **Auditability**: Easy to review all relationships
4. **Research**: Verification sources in one place
5. **Automation**: Bidirectionality automatic, not manual

---

**Document Version**: 1.0  
**Last Updated**: December 16, 2025  
**Status**: Architecture complete, integration pending
