# Frontmatter Generation Guide
**For AI Content Generators**  
**Version**: 2.1  
**Date**: December 23, 2025  
**Status**: PRODUCTION STANDARD

## 🎯 Purpose

This document defines the **exact structure and requirements** for generating frontmatter YAML files for the Z-Beam laser cleaning system. All AI generators MUST follow these specifications precisely.

## 🚨 **CRITICAL: Source of Truth Policy**

**Frontmatter files are GENERATED OUTPUT, not source data.**

**⛔ NEVER edit frontmatter files directly.** ALL changes MUST be made in:
- **Source data**: `data/*.yaml` (for content/data changes)
- **Export configs**: `export/config/*.yaml` (for structure/metadata changes)

**📖 Required Reading**: [`docs/08-development/FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md`](08-development/FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md)

Frontmatter files are regenerated on every export and manual edits WILL BE OVERWRITTEN.

---

## 📋 Universal Structure Requirements

### 1. Core Metadata (ALWAYS REQUIRED)

```yaml
id: entity-slug
name: Human Readable Name
title: Full Display Title
category: primary-category
datePublished: '2025-12-23T23:27:09.340450Z'
dateModified: '2025-12-23T23:27:09.340450Z'
content_type: materials|contaminants|compounds|settings
schema_version: 5.0.0
full_path: /content-type/category/subcategory/id
```

**Rules**:
- `id`: kebab-case, unique identifier
- `datePublished`/`dateModified`: ISO 8601 format with timezone
- `full_path`: MUST match actual route structure (category/subcategory/slug)
- `schema_version`: Always "5.0.0"

### 2. Breadcrumb Navigation (ALWAYS REQUIRED)

```yaml
breadcrumb:
- label: Home
  href: /
- label: [Content Type]
  href: /[content-type]
- label: [Category Label]
  href: /[content-type]/[category]
- label: [Subcategory Label]
  href: /[content-type]/[category]/[subcategory]
- label: [Entity Name]
  href: /[content-type]/[category]/[subcategory]/[id]
```

**Rules**:
- MUST include all levels from Home to current entity
- href values MUST match full_path structure
- Labels are human-readable (Title Case)

### 3. Author Data (ALWAYS REQUIRED)

```yaml
author:
  id: 1|2|3|4
  name: Full Name
  country: Country Name
  country_display: Country Display Name
  title: Degree (Ph.D., MA, MS, BS)
  sex: m|f
  jobTitle: Professional Title
  expertise:
    - Expertise Area 1
    - Expertise Area 2
  affiliation:
    name: Organization Name
    type: Organization|EducationalOrganization
  credentials:
    - Credential 1
    - Credential 2
    - Credential 3
    - Years of experience
  email: info@z-beam.com
  image: /images/author/[slug].jpg
  imageAlt: [Name], [Title], [Job Title] at [Affiliation]
  url: https://z-beam.com/authors/[slug]
  sameAs:
    - https://scholar.google.com/citations?user=[id]
    - https://linkedin.com/in/[slug]
    - https://www.researchgate.net/profile/[Name]
  persona_file: [country]_persona.yaml
  formatting_file: [country]_formatting.yaml
```

**Available Author IDs**:
- ID 1: Yi-Chun Lin (Taiwan, Female, Ph.D., Laser Processing Engineer)
- ID 2: (Reserved for future author)
- ID 3: (Reserved for future author)
- ID 4: Todd Dunning (USA, Male, MA, Junior Optical Materials Specialist)

**Rules**:
- Select appropriate author ID based on content domain
- ALL fields are required
- persona_file matches country (taiwan_persona.yaml, usa_persona.yaml, etc.)
- email is always "info@z-beam.com"

---

## 🔗 Relationship Structure (STANDARD FORMAT)

### Core Relationship Pattern

```yaml
relationships:
  relationship_name:
    presentation: card|table|list
    items:
      - id: entity-id
        frequency: very_common|common|occasional|rare  # Optional
        severity: high|medium|low  # Optional
        effectiveness: high|medium|low  # Optional
        typical_context: Description text  # Optional
    _section:
      title: Display Title
      description: Clear description of what this section contains
      icon: icon-name  # Optional
      order: 1  # Optional - for section sequencing
      variant: default|success|warning|danger  # Optional
```

### Available Icons for _section

| Icon | Use For |
|------|---------|
| `shield` | Safety, protection, PPE |
| `flame` | Hazards, compounds, reactions |
| `wind` | Ventilation, airflow, fumes |
| `alert-triangle` | Warnings, cautions |
| `gauge` | Measurements, limits, thresholds |
| `microscope` | Visual characteristics, analysis |
| `droplet` | Liquids, contamination |
| `zap` | Energy, power, laser |
| `file-text` | Documentation, standards |
| `users` | Materials, relationships |
| `settings` | Machine settings, parameters |
| `eye` | Visual inspection, appearance |

### Common Relationship Types by Domain

#### Materials Domain
```yaml
relationships:
  contaminated_by:
    presentation: card
    items:
      - id: contaminant-slug
        frequency: very_common|common|occasional
    _section:
      title: Common Contaminants
      description: Types of contamination typically found on this material that require laser cleaning
      icon: droplet
      order: 1
      
  regulatory:
    presentation: card
    items:
      - name: FDA
        longName: Food and Drug Administration
        description: Regulation description
        url: https://regulation-url.gov
        image: /images/logo/logo-org-fda.png
    _section:
      title: Regulatory Standards
      description: Safety and compliance standards applicable to laser cleaning of this material
      icon: file-text
      order: 2
```

#### Contaminants Domain
```yaml
relationships:
  produces_compounds:
    presentation: card
    items:
      - id: compound-slug
        phase: gas|solid|liquid  # Optional
        hazard_level: high|medium|low  # Optional
    _section:
      title: Hazardous Compounds Generated
      description: Chemical compounds released during laser removal of this contamination
      icon: flame
      order: 1
      
  found_on_materials:
    presentation: card
    items:
      - id: material-slug
        frequency: very_common|common|occasional
    _section:
      title: Found on Materials
      description: Materials commonly affected by this type of contamination
      icon: users
      order: 2
      
  visual_characteristics:
    presentation: card
    items:
      - appearance_on_categories:
          ceramic:
            description: Full description of appearance on ceramic
            aged_appearance: How contamination looks when aged
            buildup_progression: How it develops over time
            color_variations: Color range descriptions
            common_patterns: Distribution patterns
            concentration_variations: How concentration varies
            coverage_ranges: Coverage percentage descriptions
            distribution_patterns: Spatial distribution patterns
          metal:
            [same structure as ceramic]
          plastic:
            [same structure as ceramic]
          wood:
            [same structure as ceramic]
    _section:
      title: Visual Characteristics
      description: Detailed appearance and identification characteristics across different material categories
      icon: microscope
      order: 3
```

#### Compounds Domain
```yaml
relationships:
  produced_from_contaminants:
    presentation: card
    items:
      - id: contaminant-slug
        frequency: very_common|common|occasional
        severity: high|medium|low
        typical_context: Context description
    _section:
      title: Source Contaminants
      description: Contaminants that produce this compound when removed with laser cleaning
      icon: droplet
      order: 1
      
  ppe_requirements:
    presentation: card
    items:
      - type: respiratory_protection
        equipment: Respirator type
        standard: NIOSH N95
        additional_requirements:
          - Additional requirement 1
          - Additional requirement 2
    _section:
      title: PPE Requirements
      description: Required personal protective equipment for handling this compound
      icon: shield
      order: 2
      
  storage_requirements:
    presentation: card
    items:
      - temperature_range: 15-25°C
        ventilation: Required|Not Required
        incompatibilities:
          - Incompatible substance 1
          - Incompatible substance 2
    _section:
      title: Storage Requirements
      description: Proper storage conditions and incompatibilities
      icon: alert-triangle
      order: 3
      
  workplace_exposure:
    presentation: card
    items:
      - limit_type: TWA|STEL|Ceiling
        value: Numeric value
        unit: ppm|mg/m³
        authority: OSHA|NIOSH|ACGIH
        ceiling: Ceiling value  # Optional
        idlh: IDLH value  # Optional (Immediately Dangerous to Life or Health)
    _section:
      title: Workplace Exposure Limits
      description: Occupational exposure limits and monitoring requirements
      icon: gauge
      order: 4
      
  regulatory_classification:
    presentation: card
    items:
      - regulation: Regulation name
        classification: Classification type
        label: DOT Label  # Optional
        hazard_class: Class number  # Optional
    _section:
      title: Regulatory Classification
      description: Regulatory classifications and hazard categories
      icon: file-text
      order: 5
      
  detection_monitoring:
    presentation: card
    items:
      - method: Detection method
        sensitivity: Detection sensitivity
        calibration_frequency: Frequency description
    _section:
      title: Detection and Monitoring
      description: Methods for detecting and monitoring compound presence
      icon: eye
      order: 6
```

#### Settings Domain
```yaml
relationships:
  optimized_for_materials:
    presentation: card
    items:
      - id: material-slug
        effectiveness: high|medium|low
    _section:
      title: Optimized for Materials
      description: Materials these settings are specifically optimized for
      icon: users
      order: 1
```

---

## 🚫 CRITICAL: What NOT to Include

### ❌ Never Include Null Items

**WRONG**:
```yaml
items:
  - id: valid-item
  - null  # ❌ NEVER DO THIS
```

**CORRECT**:
```yaml
items:
  - id: valid-item
  # Simply omit items that don't exist
```

### ❌ Never Use Hardcoded Fallback URLs

**WRONG**:
```yaml
url: /materials/${id}  # ❌ Missing category/subcategory
url: /contaminants/${id}  # ❌ Wrong structure
```

**CORRECT**:
```yaml
url: /materials/metal/non-ferrous/brass-laser-cleaning  # ✅ Full path
# OR use full_path from frontmatter metadata
```

### ❌ Never Skip _section Metadata

**WRONG**:
```yaml
relationships:
  contaminated_by:
    presentation: card
    items:
      - id: rust-contamination
    # ❌ Missing _section
```

**CORRECT**:
```yaml
relationships:
  contaminated_by:
    presentation: card
    items:
      - id: rust-contamination
    _section:
      title: Common Contaminants
      description: Types of contamination typically found on this material
      icon: droplet
```

---

## 📝 Content Fields

### Description Fields (ALWAYS REQUIRED)

```yaml
description: Main description paragraph (150-200 words, natural human writing)
micro: Micro description (25-50 words) OR structured before/after
```

**Micro Formats**:

**Option 1: Simple String**
```yaml
micro: Brief description of the entity in 25-50 words.
```

**Option 2: Before/After Structure** (for contaminants)
```yaml
micro:
  before: Description of surface before cleaning
  after: Description of surface after cleaning
```

### FAQ (Materials and Compounds)

```yaml
faq:
  - question: Main question about the entity
    answer: |
      Multi-paragraph answer with detailed information.
      
      Second paragraph with more details.
      
      Third paragraph.
      
      (Word count: XX)
```

**Rules**:
- Materials: 1 comprehensive FAQ entry
- Compounds: FAQ optional
- Include word count at end
- Use natural, human writing style (avoid AI patterns)

### Images (ALWAYS REQUIRED)

```yaml
images:
  hero:
    url: /images/[type]/[slug]-hero.jpg
    alt: Descriptive alt text for accessibility
  micro:
    url: /images/[type]/[slug]-micro.jpg
    alt: Microscopic view alt text
```

---

## 🎨 Card Configuration

```yaml
card:
  default:
    heading: Display Heading
    subtitle: category / subcategory
    badge:
      text: Badge Text (Common|Uncommon|Rare|Low Hazard|High Hazard)
      variant: info|success|warning|danger
    metric:
      value: Numeric or text value
      unit: Unit of measurement
      legend: Metric description  # Optional
    severity: low|medium|high  # Optional
    icon: icon-name  # Optional
```

---

## 🎯 Consistency Requirements (MANDATORY)

### 1. Every Relationship MUST Have _section

**REQUIREMENT**: 100% coverage - no exceptions.

**Check Command**:
```bash
# Count relationships vs _section blocks
grep -c "^  [a-z_]*:" frontmatter/materials/aluminum.yaml
grep -c "_section:" frontmatter/materials/aluminum.yaml
# Numbers should match
```

**Wrong**:
```yaml
relationships:
  contaminated_by:
    presentation: card
    items:
      - id: rust
    # ❌ Missing _section
  regulatory:
    presentation: card
    items:
      - name: OSHA
    # ❌ Missing _section
```

**Correct**:
```yaml
relationships:
  contaminated_by:
    presentation: card
    items:
      - id: rust
    _section:
      title: Common Contaminants
      description: Types of contamination requiring removal
      icon: droplet
      
  regulatory:
    presentation: card
    items:
      - name: OSHA
    _section:
      title: Regulatory Standards
      description: Safety standards applicable to this material
      icon: file-text
```

### 2. Complete _section Metadata Fields

**REQUIRED FIELDS**:
- `title` (string) - Display heading
- `description` (string) - Clear explanation of section content
- `icon` (string) - From approved icon list
- `order` (integer) - Section sequencing (1, 2, 3...)
- `variant` (string) - Styling hint (default|success|warning|danger)

**Example**:
```yaml
_section:
  title: Hazardous Compounds Generated
  description: Chemical compounds released during laser removal of this contamination
  icon: flame
  order: 1
  variant: danger
```

### 3. Visual Characteristics Structure (Contaminants Only)

**REQUIREMENT**: Must be nested by material category.

**Structure**:
```yaml
relationships:
  visual_characteristics:
    presentation: card
    items:
      - appearance_on_categories:
          ceramic:
            description: Full appearance description
            aged_appearance: Age-related changes
            buildup_progression: Development over time
            color_variations: Color range descriptions
            common_patterns: Distribution patterns
            concentration_variations: Concentration variance
            coverage_ranges: Coverage percentage descriptions
            distribution_patterns: Spatial distribution
          metal:
            [same fields as ceramic]
          plastic:
            [same fields as ceramic]
          wood:
            [same fields as ceramic]
    _section:
      title: Visual Characteristics
      description: Detailed appearance across different material categories
      icon: microscope
      order: 3
```

**Rules**:
- MUST include all 4 categories: ceramic, metal, plastic, wood
- Each category MUST have all 8 sub-fields
- Descriptions must be material-specific (not generic)

### 4. Zero Null Items Policy

**REQUIREMENT**: No null items anywhere in frontmatter.

**Detection Command**:
```bash
grep -r "^    - null$" frontmatter/ --include="*.yaml"
# Should return ZERO results
```

**Wrong**:
```yaml
items:
  - id: valid-item-1
  - null  # ❌ NEVER
  - id: valid-item-2
```

**Correct**:
```yaml
items:
  - id: valid-item-1
  - id: valid-item-2
  # Simply omit items that don't exist
```

### 5. Relationship Frequency Consistency

**REQUIREMENT**: Use standard frequency values.

**Allowed Values**:
- `very_common` - Occurs in >70% of cases
- `common` - Occurs in 40-70% of cases
- `occasional` - Occurs in 10-40% of cases
- `rare` - Occurs in <10% of cases

**Example**:
```yaml
contaminated_by:
  presentation: card
  items:
    - id: rust-contamination
      frequency: very_common  # ✅ Standard value
    - id: oil-contamination
      frequency: common  # ✅ Standard value
    - id: paint-contamination
      frequency: occasional  # ✅ Standard value
```

### 6. URL Path Consistency

**REQUIREMENT**: All URLs must use full_path structure.

**Format**: `/[content-type]/[category]/[subcategory]/[slug]`

**Examples**:
- Material: `/materials/metal/non-ferrous/aluminum-laser-cleaning`
- Contaminant: `/contaminants/organic-residue/petroleum/industrial-oil-contamination`
- Compound: `/compounds/particulate/carbon-based/carbon-particulates-compound`
- Setting: `/settings/laser-parameters/power-density/medium-power-density`

**Wrong**:
```yaml
url: /materials/aluminum  # ❌ Missing category and subcategory
url: /contaminants/${id}  # ❌ Variable syntax not allowed
```

**Correct**:
```yaml
full_path: /materials/metal/non-ferrous/aluminum-laser-cleaning  # ✅
```

---

## 🔧 Remaining Enhancement Requirements

### Phase 1: Complete _section Coverage (IMMEDIATE)

**Task**: Add _section to every relationship block that's missing it.

**Priority**: HIGH - Required for UI feature parity

**Process**:
1. Scan all frontmatter files
2. Identify relationships without _section
3. Add appropriate _section block with all 5 fields (title, description, icon, order, variant)

**Command to Find Missing**:
```bash
# Find files where relationship count > _section count
for file in frontmatter/*/*.yaml; do
  rels=$(grep -c "^  [a-z_]*:" "$file" 2>/dev/null || echo 0)
  secs=$(grep -c "_section:" "$file" 2>/dev/null || echo 0)
  if [ "$rels" -gt "$secs" ]; then
    echo "$file: $rels relationships, $secs _sections (missing: $((rels - secs)))"
  fi
done
```

### Phase 2: Remove All Null Items (IMMEDIATE)

**Task**: Delete all `- null` entries from items arrays.

**Priority**: HIGH - Prevents runtime errors

**Process**:
1. Search: `grep -r "^    - null$" frontmatter/ --include="*.yaml"`
2. For each match, delete the line
3. Verify: `grep -r "- null" frontmatter/` should return 0 results

**Example Fix**:
```yaml
# Before
items:
  - id: valid-item
  - null
  - id: another-item

# After
items:
  - id: valid-item
  - id: another-item
```

### Phase 3: Standardize Compound Safety (MEDIUM PRIORITY)

**Task**: Ensure all compound safety relationships follow exact structure.

**Required Relationships**:
1. `ppe_requirements` - With additional_requirements array
2. `storage_requirements` - With incompatibilities array
3. `regulatory_classification` - With label and hazard_class
4. `workplace_exposure` - With ceiling and idlh values
5. `reactivity` - With incompatible_materials and hazardous_decomposition
6. `detection_monitoring` - With calibration_frequency

**Each MUST have _section with icon, order, variant**.

### Phase 4: Visual Characteristics Validation (MEDIUM PRIORITY)

**Task**: Verify all contaminants have complete visual_characteristics.

**Validation**:
```bash
# Check structure
grep -A 50 "visual_characteristics:" frontmatter/contaminants/*.yaml | grep -E "ceramic:|metal:|plastic:|wood:"
```

**Requirements**:
- All 4 material categories present
- Each category has 8 sub-fields (description, aged_appearance, buildup_progression, color_variations, common_patterns, concentration_variations, coverage_ranges, distribution_patterns)
- No generic copy-paste between categories

### Phase 5: Settings Challenges (LOW PRIORITY)

**Task**: Standardize challenges structure across settings.

**Current State**: Variable structure
**Target State**: Consistent presentation + items + _section format

**Example Target**:
```yaml
relationships:
  challenges:
    presentation: list
    items:
      - title: Challenge Title
        description: Challenge description
        severity: high|medium|low
        mitigation: Mitigation strategy
    _section:
      title: Common Challenges
      description: Challenges encountered with these settings
      icon: alert-triangle
      order: 4
```

---

## ✅ Validation Checklist

Before generating frontmatter, verify:

- [ ] All required core metadata fields present
- [ ] Breadcrumb has all levels from Home to entity
- [ ] Author object is complete with all required fields
- [ ] **ALL relationship blocks have `_section` metadata** (100% coverage)
- [ ] **ALL `_section` blocks have 5 fields: title, description, icon, order, variant**
- [ ] **ZERO null items in any arrays** (grep verification passed)
- [ ] All URLs use full_path structure (category/subcategory/slug)
- [ ] Icons are from approved icon list
- [ ] Frequency values are standard (very_common|common|occasional|rare)
- [ ] Description and micro fields are present
- [ ] Images have both url and alt text
- [ ] Card configuration is complete
- [ ] datePublished and dateModified are in ISO 8601 format
- [ ] schema_version is "5.0.0"
- [ ] **Visual characteristics (contaminants): All 4 material categories present**
- [ ] **Visual characteristics (contaminants): Each category has 8 sub-fields**
- [ ] **Compound safety relationships: All 6 safety blocks present with complete structure**

---

## 📋 Complete Example: Material Frontmatter

```yaml
id: aluminum-laser-cleaning
name: Aluminum
title: Aluminum Laser Cleaning
category: metal
datePublished: '2025-12-23T23:00:00.000000Z'
dateModified: '2025-12-23T23:00:00.000000Z'
content_type: materials
schema_version: 5.0.0
full_path: /materials/metal/non-ferrous/aluminum-laser-cleaning
breadcrumb:
- label: Home
  href: /
- label: Materials
  href: /materials
- label: Metal
  href: /materials/metal
- label: Non Ferrous
  href: /materials/metal/non-ferrous
- label: Aluminum
  href: /materials/metal/non-ferrous/aluminum-laser-cleaning
description: Aluminum presents unique challenges for laser cleaning due to its high reflectivity and thermal conductivity. The material efficiently dissipates heat, requiring careful parameter selection to achieve effective contamination removal without surface damage. Its oxide layer forms rapidly when exposed to air, creating a protective but visually unappealing coating that laser cleaning effectively removes.
micro: Laser cleaning of aluminum requires precise parameter control to overcome high reflectivity while preventing thermal damage to the substrate.
faq:
  - question: What makes aluminum challenging for laser cleaning?
    answer: |
      Aluminum's high reflectivity at common laser wavelengths means much of the incident energy reflects rather than absorbs. This requires higher power settings or specific wavelength selection. Additionally, its excellent thermal conductivity spreads heat quickly, necessitating careful control to avoid warping or melting.
      
      The rapid formation of aluminum oxide creates a thin protective layer that, while preventing corrosion, dulls the metal's appearance. Laser cleaning removes this oxide layer effectively, restoring the bright metallic finish.
      
      (Word count: 85)
images:
  hero:
    url: /images/material/aluminum-laser-cleaning-hero.jpg
    alt: Aluminum surface undergoing laser cleaning showing oxide removal
  micro:
    url: /images/material/aluminum-laser-cleaning-micro.jpg
    alt: Microscopic view of aluminum after laser cleaning treatment
author:
  id: 1
  name: Yi-Chun Lin
  country: Taiwan
  country_display: Taiwan
  title: Ph.D.
  sex: f
  jobTitle: Laser Processing Engineer
  expertise:
    - Laser Materials Processing
    - Surface Engineering
  affiliation:
    name: National Taiwan University
    type: EducationalOrganization
  credentials:
    - Ph.D. Materials Engineering, National Taiwan University, 2018
    - Post-Ph.D. fellowship at TSMC's laser fab lab, 2018-2020
    - 3+ years in laser processing R&D
  email: info@z-beam.com
  image: /images/author/yi-chun-lin.jpg
  imageAlt: Yi-Chun Lin, Ph.D., Laser Processing Engineer at National Taiwan University
  url: https://z-beam.com/authors/yi-chun-lin
  sameAs:
    - https://scholar.google.com/citations?user=example123
    - https://linkedin.com/in/yi-chun-lin-engineer
  persona_file: taiwan_persona.yaml
  formatting_file: taiwan_formatting.yaml
subcategory: non-ferrous
card:
  default:
    heading: Aluminum
    subtitle: metal / non-ferrous
    badge:
      text: Common
      variant: info
    metric:
      value: '1064'
      unit: nm
      legend: Optimal Wavelength
    severity: low
    icon: cube
relationships:
  contaminated_by:
    presentation: card
    items:
      - id: aluminum-oxidation-contamination
        frequency: very_common
      - id: industrial-oil-contamination
        frequency: common
      - id: paint-residue-contamination
        frequency: common
    _section:
      title: Common Contaminants
      description: Types of contamination typically found on aluminum requiring laser cleaning
      icon: droplet
      order: 1
  regulatory:
    presentation: card
    items:
      - name: ANSI
        longName: American National Standards Institute
        description: ANSI Z136.1 - Safe Use of Lasers
        url: https://webstore.ansi.org/standards/lia/ansiz1362022
        image: /images/logo/logo-org-ansi.png
      - name: OSHA
        longName: Occupational Safety and Health Administration
        description: OSHA 29 CFR 1926.102 - Eye and Face Protection
        url: https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.102
        image: /images/logo/logo-org-osha.png
    _section:
      title: Regulatory Standards
      description: Safety and compliance standards applicable to laser cleaning of aluminum
      icon: file-text
      order: 2
```

---

## 🔄 Version History

- **v2.0** (Dec 23, 2025): Complete restructure with relationship standards, _section metadata, author data requirements
- **v2.1** (Dec 23, 2025): Added consistency requirements, remaining enhancement specifications, validation commands
- **v1.0** (Initial): Basic frontmatter structure

---

## 📊 Quality Metrics

**Target Standards**:
- _section Coverage: **100%** (every relationship must have _section)
- Null Items: **0** (zero tolerance)
- Icon Usage: **100%** (all _section blocks must have icon from approved list)
- Visual Characteristics Completeness: **100%** (contaminants: 4 categories × 8 fields)
- Compound Safety Completeness: **100%** (all 6 safety relationships present)
- URL Structure Compliance: **100%** (all use full_path format)

**Measurement Commands**:
```bash
# Count total relationships
find frontmatter -name "*.yaml" -exec grep -c "^  [a-z_]*:" {} \; | awk '{s+=$1} END {print s}'

# Count _section blocks
find frontmatter -name "*.yaml" -exec grep -c "_section:" {} \; | awk '{s+=$1} END {print s}'

# Find null items
grep -r "^    - null$" frontmatter/ --include="*.yaml" | wc -l

# Missing _section per file
for file in frontmatter/*/*.yaml; do
  rels=$(grep -c "^  [a-z_]*:" "$file" 2>/dev/null || echo 0)
  secs=$(grep -c "_section:" "$file" 2>/dev/null || echo 0)
  if [ "$rels" -gt "$secs" ]; then
    echo "$file: Missing $((rels - secs)) _section blocks"
  fi
done
```

---

## 📞 Questions or Issues?

If you encounter ambiguity or edge cases not covered in this guide, refer to:
1. Existing frontmatter examples in `/frontmatter/` directory
2. `docs/FRONTMATTER_OPTIMIZATION_DEC23_2025.md` for detailed specifications
3. Component implementations in `/app/components/` for usage patterns

**Priority**: Follow this guide strictly. Consistency is critical for system functionality.
