# Regulatory Standards Architecture

## Overview
Two-tier regulatory standards system with parent framework and material-specific display data.

## Files

### 1. **RegulatoryStandards.yaml** (17KB - Parent Framework)
**Location**: `data/materials/RegulatoryStandards.yaml`

**Purpose**: Comprehensive regulatory framework with detailed requirements

**Content**:
- Universal standards (laser_safety, occupational_safety, environmental_safety)
- Industry-specific standards (aerospace, automotive, medical_devices, marine, electronics, semiconductor, heritage_conservation, nuclear)
- Application compliance frameworks
- Testing and certification standards
- Regional regulatory authorities
- Certification requirements

**Structure**: Each standard has a unique `id` field for cross-referencing
```yaml
universal_standards:
  laser_safety:
    - id: std_fda_21cfr1040
      standard: FDA 21 CFR 1040.10
      title: Laser Product Performance Standards
      region: United States
      authority: Food and Drug Administration
      scope: Laser product manufacturing and safety requirements
```

**Use Cases**:
- Reference documentation for compliance planning
- Industry filtering and material categorization
- Detailed requirement lookup for engineering teams
- Future features (compliance reports, certification tracking)

---

### 2. **content/RegulatoryStandards.yaml** (126KB - Display Data)
**Location**: `data/materials/content/RegulatoryStandards.yaml`

**Purpose**: Material-specific regulatory standards for website frontmatter generation

**Content**:
- Per-material regulatory standards (132 materials)
- Display-ready format with logos, URLs, descriptions
- Extracted from Materials.yaml

**Structure**: Simple array format optimized for website display
```yaml
regulatory_standards:
  Aluminum:
    - description: FDA 21 CFR 1040.10 - Laser Product Performance Standards
      image: /images/logo/logo-org-fda.png
      longName: Food and Drug Administration
      name: FDA
      url: https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J/part-1040/section-1040.10
```

**Metadata**: References parent framework
```yaml
_metadata:
  parent_framework: ../RegulatoryStandards.yaml
  purpose: Display data for website (logos, links, descriptions)
```

**ID Mapping** (documented in file):
```
FDA 21 CFR 1040.10 → std_fda_21cfr1040
ANSI Z136.1 → std_ansi_z136_1
IEC 60825 → std_iec_60825_1
OSHA 29 CFR 1926.95 → std_osha_1926_95
```

**Use Cases**:
- Frontmatter generation for material pages
- Website display with logos and links
- Material-specific compliance information

---

## Relationship

```
RegulatoryStandards.yaml (Parent)
├─ Universal Standards
│  ├─ std_fda_21cfr1040 (FDA 21 CFR 1040.10)
│  ├─ std_ansi_z136_1 (ANSI Z136.1)
│  ├─ std_iec_60825_1 (IEC 60825-1)
│  └─ std_osha_1926_95 (OSHA 29 CFR 1926.95)
├─ Industry Standards
│  ├─ std_as9100 (Aerospace quality)
│  ├─ std_nadcap (Aerospace accreditation)
│  └─ std_iso_13485 (Medical devices)
└─ Application Compliance

    ↓ Referenced by

content/RegulatoryStandards.yaml (Child)
├─ Alabaster → [FDA, ANSI, IEC, OSHA]
├─ Aluminum → [FDA, ANSI, IEC, OSHA]
├─ Brass → [FDA, ANSI, IEC, OSHA]
└─ ... (132 materials total)
```

## Standard ID Scheme

All standards in the parent framework use unique IDs following this pattern:

- **Format**: `std_{organization}_{standard_number}`
- **Examples**:
  - `std_fda_21cfr1040` → FDA 21 CFR 1040.10
  - `std_ansi_z136_1` → ANSI Z136.1
  - `std_iec_60825_1` → IEC 60825-1
  - `std_osha_1926_95` → OSHA 29 CFR 1926.95
  - `std_iso_45001` → ISO 45001
  - `std_as9100` → AS9100
  - `std_nadcap` → NADCAP

## Integration Points

### Materials.yaml
Currently contains full regulatory standards arrays:
```yaml
regulatoryStandards:
  - description: FDA 21 CFR 1040.10 - Laser Product Performance Standards
    image: /images/logo/logo-org-fda.png
    longName: Food and Drug Administration
    name: FDA
    url: https://...
```

### Frontmatter Generator
Reads from `content/RegulatoryStandards.yaml` to populate material frontmatter with:
- Standard logos
- Standard names and descriptions
- Official URLs
- Regulatory authority information

### Future Enhancement (Optional)
Could add `standard_id` fields to Materials.yaml for direct parent framework lookups:
```yaml
regulatoryStandards:
  - standard_id: std_fda_21cfr1040
  - standard_id: std_ansi_z136_1
  - standard_id: std_iec_60825_1
  - standard_id: std_osha_1926_95
```

This would enable:
- Dynamic standard details lookup from parent framework
- Centralized standard data maintenance
- Automatic updates when parent framework changes
- Industry-specific standard filtering

## Summary

**Both files are preserved**:
- ✅ Parent framework (17KB) - Comprehensive requirements reference
- ✅ Material display data (126KB) - Website generation optimized
- ✅ Clear documentation of relationship and ID mapping
- ✅ Flexible architecture for future enhancements

**No data duplication concerns** because:
1. Parent has detailed requirements, compliance frameworks, certifications
2. Child has display-optimized data (logos, URLs, formatting)
3. Different use cases justify different structures
4. ID mapping enables future integration when needed
