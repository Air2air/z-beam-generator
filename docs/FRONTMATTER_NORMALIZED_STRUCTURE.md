# Complete Normalized Frontmatter Structure

**Date**: January 8, 2026  
**Status**: PROPOSED - Comprehensive normalization standard  
**Purpose**: Define complete, consistent frontmatter structure across all domains

---

## 🚨 URGENT: Phase 2 Action Required

**Current Status** (Jan 8, 2026): ⚠️ **NOT STARTED** - Enrichment script has NOT been run

**⚠️ CRITICAL CLARIFICATION**:
- ❌ Phase 2 enrichment is **NOT automatic** during backend regeneration
- ❌ Simply regenerating frontmatter will **NOT add missing fields**
- ✅ The enrichment script **MUST be run manually** as a separate step
- ✅ Script reads existing incomplete frontmatter and enriches it with missing data

**Verified Current State**:
```yaml
# frontmatter/compounds/benzene-compound.yaml
producedFromContaminants:
  items:
    - id: paint-residue-contamination     # ✅ Present (4 fields only)
      frequency: common
      severity: high
      typicalContext: "..."
      # ❌ Missing: url, title, name, image, category, subcategory, description
```

**Required Action**:
```bash
# 1. CREATE the enrichment script first (copy from Section 13)
mkdir -p scripts/data
# Copy script content from Section 13 → scripts/data/enrich_compound_relationships.py

# 2. RUN the enrichment script
cd /path/to/z-beam
python3 scripts/data/enrich_compound_relationships.py

# Expected output:
# ✅ 34 compound files updated
# ✅ 369 contaminant items enriched (4→9 fields)
```

**Impact**: Frontend currently using runtime workaround (+50-100ms per page)  
**After Phase 2**: Remove workaround, native SSG performance restored

**Scope**: 34 files, 369 items, 1,845 missing field values

See [Section 13](#13-phase-2-denormalization-script) for complete script and instructions.

---

## Core Principles

1. **Full Denormalization**: All relationship items contain complete display data
2. **Consistent Naming**: camelCase for all keys
3. **Structured Sections**: All relationships have `presentation`, `items`, `_section` metadata
4. **Zero Async Enrichment**: Frontend reads directly from frontmatter
5. **Type Safety**: Arrays are always arrays, objects are always objects

---

## 1. Material Frontmatter Structure

### Complete Example: `frontmatter/materials/aluminum-laser-cleaning.yaml`

```yaml
# ============================================================================
# CORE IDENTIFICATION
# ============================================================================
id: aluminum-laser-cleaning
name: Aluminum
category: metal
subcategory: non-ferrous
pageDescription: "Lightweight non-ferrous metal with excellent laser cleaning characteristics..."

# ============================================================================
# IMAGES
# ============================================================================
images:
  hero:
    url: /images/materials/aluminum-hero.jpg
    alt: Aluminum surface prepared for laser cleaning
  micro:
    url: /images/materials/aluminum-micro.jpg
    alt: Microscopic view of aluminum surface structure

# ============================================================================
# PROPERTIES (camelCase keys, structured values)
# ============================================================================
properties:
  materialCharacteristics:
    label: Material Characteristics
    description: Intrinsic physical and mechanical properties
    percentage: 60.0
    density:
      value: 2.7
      unit: g/cm³
    porosity:
      value: 0
      unit: "%"
    surfaceRoughness:
      value: 0.4
      unit: μm
    meltingPoint:
      value: 660
      unit: °C
    tensileStrength:
      value: 90
      unit: MPa
    hardness:
      value: 0.245
      unit: GPa
    thermalConductivity:
      value: 237
      unit: W/m·K
    electricalConductivity:
      value: 37700000
      unit: S/m
    
  laserMaterialInteraction:
    label: Laser-Material Interaction
    description: Optical and thermal properties governing laser absorption
    percentage: 40.0
    laserAbsorption:
      value: 0.05
      unit: dimensionless
    laserReflectivity:
      value: 0.92
      unit: "%"
    ablationThreshold:
      value: 0.8
      unit: J/cm²
    laserDamageThreshold:
      value: 1.5
      unit: J/cm²
    thermalDiffusivity:
      value: 9.7e-05
      unit: m²/s
    specificHeat:
      value: 900
      unit: J/(kg·K)

# ============================================================================
# RELATIONSHIPS (All items fully denormalized)
# ============================================================================
relationships:
  
  # --------------------------------------------------------------------------
  # INTERACTIONS
  # --------------------------------------------------------------------------
  interactions:
    
    contaminatedBy:
      presentation: card
      items:
        # COMPLETE denormalized contaminant data (9 fields)
        - id: rust-contamination
          name: Rust & Oxidation
          category: oxide
          subcategory: iron
          url: /contaminants/oxide/iron/rust-contamination
          image: /images/contaminants/rust-hero.jpg
          description: Iron oxide corrosion requiring laser removal
          frequency: very_high
          severity: moderate
        
        - id: grease-contamination
          name: Industrial Oil / Grease Buildup
          category: organic-residue
          subcategory: petroleum
          url: /contaminants/organic-residue/petroleum/grease-contamination
          image: /images/contaminants/grease-hero.jpg
          description: Petroleum-based lubricant residues from manufacturing
          frequency: high
          severity: moderate
      
      _section:
        sectionTitle: Common Contaminants
        sectionDescription: Typical contaminants found on aluminum requiring laser cleaning
        icon: droplet
        order: 5
        variant: default
        sectionMetadata:
          relationshipType: contaminatedBy
          group: interactions
          domain: materials
    
    producesCompounds:
      presentation: card
      items:
        # COMPLETE denormalized compound data (9 fields)
        - id: aluminum-oxide-compound
          title: Aluminum Oxide
          name: Aluminum Oxide
          category: oxide
          subcategory: metal-oxide
          url: /compounds/oxide/metal-oxide/aluminum-oxide-compound
          image: /images/compounds/aluminum-oxide-hero.jpg
          description: White powdery oxide formed during laser ablation
          phase: solid
          hazardLevel: low
        
        - id: ozone-compound
          title: Ozone
          name: Ozone
          category: gaseous
          subcategory: reactive
          url: /compounds/gaseous/reactive/ozone-compound
          image: /images/compounds/ozone-hero.jpg
          description: Reactive oxygen species generated during high-energy laser cleaning
          phase: gas
          hazardLevel: moderate
      
      _section:
        sectionTitle: Produced Compounds
        sectionDescription: Compounds generated during aluminum laser cleaning
        icon: flask-conical
        order: 10
        variant: warning
  
  # --------------------------------------------------------------------------
  # OPERATIONAL
  # --------------------------------------------------------------------------
  operational:
    
    industryApplications:
      presentation: card
      items:
        - id: aerospace-manufacturing
          title: Aerospace Manufacturing
          name: Aerospace Manufacturing
          content: Aircraft component cleaning and surface preparation...
          description: Critical application in aerospace for removing contaminants...
          url: /industries/aerospace-manufacturing
          icon: plane
          frequency: very_high
        
        - id: automotive-assembly
          title: Automotive Assembly
          name: Automotive Assembly
          content: Pre-coating surface preparation for automotive parts...
          description: Laser cleaning of aluminum components before painting...
          url: /industries/automotive-assembly
          icon: car
          frequency: high
      
      _section:
        sectionTitle: Industry Applications
        sectionDescription: Industries where aluminum laser cleaning is commonly used
        icon: building
        order: 15
        variant: default
    
    machineSettings:
      presentation: link
      url: /settings/metal/non-ferrous/aluminum-settings
      linkText: View Laser Settings
      _section:
        sectionTitle: Machine Settings
        sectionDescription: Recommended laser parameters for aluminum cleaning
        icon: settings
        order: 20
        variant: technical
  
  # --------------------------------------------------------------------------
  # SAFETY
  # --------------------------------------------------------------------------
  safety:
    
    regulatoryStandards:
      presentation: card
      items:
        - id: ansi-z136
          name: ANSI Z136.1
          longName: ANSI Z136.1-2022 Safe Use of Lasers
          url: https://www.lia.org/resources/laser-safety-information/ansi-z136-standards
          image: /images/standards/ansi-logo.svg
          description: American National Standard for Safe Use of Lasers
        
        - id: iec-60825
          name: IEC 60825-1
          longName: IEC 60825-1 Safety of Laser Products
          url: https://www.iec.ch/
          image: /images/standards/iec-logo.svg
          description: International standard for laser product safety classification
      
      _section:
        sectionTitle: Regulatory Standards
        sectionDescription: Safety and compliance standards for aluminum laser cleaning
        icon: shield-check
        order: 25
        variant: info

# ============================================================================
# FAQ (Structured with presentation metadata)
# ============================================================================
faq:
  presentation: collapsible
  options:
    autoOpenFirst: true
    sortBy: severity
  items:
    - id: aluminum-suitable-for-laser
      title: What makes aluminum **suitable for industrial** laser cleaning?
      content: |
        **Lightweight with low density**. Aluminum weighs around 2.7 grams per cubic centimeter...
        
        Alessandro Moretti, Ph.D.
      metadata:
        topic: makes aluminum suitable for industrial
        severity: high
        acceptedAnswer: true
        expertInfo:
          name: Alessandro Moretti
          title: Ph.D.
          expertise: [Laser Materials Processing]
      _display:
        _open: true
        order: 1
    
    - id: aluminum-laser-setup
      title: How do you **set up laser cleaning** for aluminum?
      content: |
        **100-watt power range removes oxides**. We use a 100-watt power range...
        
        Yi-Chun Lin, Ph.D.
      metadata:
        topic: set up laser cleaning
        severity: medium
        acceptedAnswer: true
        expertInfo:
          name: Yi-Chun Lin
          title: Ph.D.
          expertise: [Laser Materials Processing]
      _display:
        _open: false
        order: 2

# ============================================================================
# METADATA (Tracking only - not duplicated content)
# ============================================================================
metadata:
  lastUpdated: '2026-01-08T17:15:00Z'
  normalizationApplied: true
  version: 2.0
```

---

## 2. Contaminant Frontmatter Structure

### Complete Example: `frontmatter/contaminants/rust-contamination.yaml`

```yaml
# ============================================================================
# CORE IDENTIFICATION
# ============================================================================
id: rust-contamination
name: Rust & Oxidation
category: oxide
subcategory: iron
pageDescription: "Iron oxide corrosion requiring specialized laser cleaning..."

# ============================================================================
# IMAGES
# ============================================================================
images:
  hero:
    url: /images/contaminants/rust-hero.jpg
    alt: Rust contamination on metal surface
  micro:
    url: /images/contaminants/rust-micro.jpg
    alt: Microscopic view of iron oxide structure

# ============================================================================
# RELATIONSHIPS
# ============================================================================
relationships:
  
  interactions:
    
    # Materials this contaminant is commonly found on
    foundOnMaterials:
      presentation: card
      items:
        # COMPLETE denormalized material data
        - id: steel-laser-cleaning
          name: Steel
          category: metal
          subcategory: ferrous
          url: /materials/metal/ferrous/steel-laser-cleaning
          image: /images/materials/steel-hero.jpg
          description: Carbon steel substrate requiring rust removal
          frequency: very_high
          difficulty: moderate
        
        - id: cast-iron-laser-cleaning
          name: Cast Iron
          category: metal
          subcategory: ferrous
          url: /materials/metal/ferrous/cast-iron-laser-cleaning
          image: /images/materials/cast-iron-hero.jpg
          description: Porous iron substrate prone to oxidation
          frequency: high
          difficulty: moderate
      
      _section:
        sectionTitle: Affected Materials
        sectionDescription: Materials commonly contaminated with rust
        icon: layers
        order: 5
    
    # Compounds produced when laser cleaning this contaminant
    producesCompounds:
      presentation: card
      items:
        # COMPLETE denormalized compound data (9 fields) ✅ CRITICAL FIX
        - id: iron-oxide-compound
          title: Iron Oxide Particulates
          name: Iron Oxide Particulates
          category: oxide
          subcategory: metal-oxide
          url: /compounds/oxide/metal-oxide/iron-oxide-compound
          image: /images/compounds/iron-oxide-hero.jpg
          description: Fine iron oxide particles generated during laser ablation
          phase: solid
          hazardLevel: low
        
        - id: ozone-compound
          title: Ozone
          name: Ozone
          category: gaseous
          subcategory: reactive
          url: /compounds/gaseous/reactive/ozone-compound
          image: /images/compounds/ozone-hero.jpg
          description: Reactive oxygen produced during high-energy cleaning
          phase: gas
          hazardLevel: moderate
      
      _section:
        sectionTitle: Produced Compounds
        sectionDescription: Hazardous compounds produced during laser cleaning
        icon: flask-conical
        order: 10
        variant: warning
    
    # Materials affected by this contaminant
    affectsMaterials:
      presentation: card
      items:
        # COMPLETE denormalized material data (8 fields)
        - id: steel-laser-cleaning
          name: Steel
          category: metal
          subcategory: ferrous
          url: /materials/metal/ferrous/steel-laser-cleaning
          image: /images/materials/steel-hero.jpg
          description: Ferrous metal commonly affected by rust contamination
          frequency: very_high
          difficulty: moderate
        
        - id: cast-iron-laser-cleaning
          name: Cast Iron
          category: metal
          subcategory: ferrous
          url: /materials/metal/ferrous/cast-iron-laser-cleaning
          image: /images/materials/cast-iron-hero.jpg
          description: Porous iron substrate requiring rust removal
          frequency: high
          difficulty: moderate
      
      _section:
        sectionTitle: Affected Materials
        sectionDescription: Materials commonly contaminated with rust
        icon: layers
        order: 12
        variant: default
  
  safety:
    
    regulatoryStandards:
      presentation: card
      items:
        - id: osha-respiratory
          name: OSHA 1910.134
          longName: OSHA Respiratory Protection Standard
          url: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.134
          image: /images/standards/osha-logo.svg
          description: Requirements for respiratory protection during rust removal
      
      _section:
        sectionTitle: Safety Standards
        sectionDescription: Regulatory compliance for rust laser cleaning
        icon: shield-check
        order: 15

# ============================================================================
# SAFETY DATA (Contaminant-specific)
# ============================================================================
safetyData:
  hazardClassification:
    primary: corrosive
    secondary: particulate
  ppeRequirements:
    respiratory: required
    eyeProtection: required
    handProtection: recommended
  workplaceExposure:
    permissibleExposureLimit: 10
    unit: mg/m³
    standard: OSHA

# ============================================================================
# FAQ
# ============================================================================
faq:
  presentation: collapsible
  options:
    autoOpenFirst: true
  items:
    - id: rust-removal-laser-effective
      title: Is laser cleaning **effective for rust removal**?
      content: |
        **Highly effective for surface rust**. Laser cleaning removes...
      metadata:
        severity: high
      _display:
        order: 1
```

---

## 3. Compound Frontmatter Structure

**⚠️ PHASE 2 STATUS**: Relationship denormalization is **NOT STARTED**

**Verified Current State** (Jan 8, 2026):
- ❌ `producedFromContaminants` items only have 4 fields (id, frequency, severity, typicalContext)
- ❌ `affectsMaterials` items only have 2-3 fields (id, frequency)
- ❌ Enrichment script has NOT been executed
- ✅ **Required**: All 9+ fields (url, title, name, image, category, subcategory, description, ...)

**Critical**: Backend regeneration does NOT automatically enrich relationships. The enrichment script (Section 13) must be run as a **separate manual step**.

**Impact**: Frontend requires runtime file reads (performance cost)

**Solution**: Create and run Phase 2 enrichment script (see Section 13)

---

### Complete Example: `frontmatter/compounds/ozone-compound.yaml`

```yaml
# ============================================================================
# CORE IDENTIFICATION
# ============================================================================
id: ozone-compound
title: Ozone
name: Ozone
category: gaseous
subcategory: reactive
pageDescription: "Reactive oxygen species generated during high-energy laser cleaning..."

# ============================================================================
# COMPOUND PROPERTIES
# ============================================================================
properties:
  chemicalFormula: O₃
  casNumber: 10028-15-6
  phase: gas
  hazardLevel: moderate
  molecularWeight:
    value: 48.0
    unit: g/mol
  boilingPoint:
    value: -112
    unit: °C
  density:
    value: 2.14
    unit: g/L

# ============================================================================
# RELATIONSHIPS
# ============================================================================
relationships:
  
  interactions:
    
    # Contaminants that produce this compound
    producedFromContaminants:
      presentation: card
      items:
        # COMPLETE denormalized contaminant data
        - id: rust-contamination
          name: Rust & Oxidation
          category: oxide
          subcategory: iron
          url: /contaminants/oxide/iron/rust-contamination
          image: /images/contaminants/rust-hero.jpg
          description: Iron oxide producing ozone during laser ablation
          frequency: high
          severity: moderate
        
        - id: paint-contamination
          name: Paint & Coatings
          category: coating
          subcategory: paint
          url: /contaminants/coating/paint/paint-contamination
          image: /images/contaminants/paint-hero.jpg
          description: Painted surfaces generating ozone during removal
          frequency: moderate
          severity: moderate
      
      _section:
        sectionTitle: Produced From
        sectionDescription: Contaminants that generate ozone during laser cleaning
        icon: droplet
        order: 5
    
    # Materials where this compound is commonly produced
    affectsMaterials:
      presentation: card
      items:
        # COMPLETE denormalized material data
        - id: aluminum-laser-cleaning
          name: Aluminum
          category: metal
          subcategory: non-ferrous
          url: /materials/metal/non-ferrous/aluminum-laser-cleaning
          image: /images/materials/aluminum-hero.jpg
          description: Aluminum cleaning processes generating ozone
          frequency: high
      
      _section:
        sectionTitle: Affected Materials
        sectionDescription: Materials commonly producing ozone during cleaning
        icon: layers
        order: 10
  
  safety:
    
    regulatoryStandards:
      presentation: card
      items:
        - id: osha-ozone-exposure
          name: OSHA 1910.1000
          longName: OSHA Air Contaminants Standard
          url: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.1000
          image: /images/standards/osha-logo.svg
          description: Permissible exposure limits for ozone
      
      _section:
        sectionTitle: Regulatory Standards
        sectionDescription: Safety standards for ozone exposure
        icon: shield-check
        order: 15

# ============================================================================
# SAFETY DATA
# ============================================================================
safetyData:
  hazardClassification:
    primary: respiratory-irritant
    secondary: oxidizer
  ppeRequirements:
    respiratory: required
    ventilation: required
  workplaceExposure:
    permissibleExposureLimit: 0.1
    unit: ppm
    standard: OSHA
```

---

## 4. Settings Frontmatter Structure

### Complete Example: `frontmatter/settings/aluminum-settings.yaml`

```yaml
# ============================================================================
# CORE IDENTIFICATION
# ============================================================================
id: aluminum-settings
name: Aluminum Laser Settings
category: metal
subcategory: non-ferrous
pageDescription: "Optimized laser parameters for aluminum cleaning..."

# ============================================================================
# MACHINE SETTINGS (Core laser parameters)
# ============================================================================
machineSettings:
  laserPower:
    min: 50
    max: 150
    recommended: 100
    unit: W
  pulseFrequency:
    min: 10
    max: 50
    recommended: 30
    unit: kHz
  scanSpeed:
    min: 500
    max: 3000
    recommended: 1500
    unit: mm/s
  pulseWidth:
    min: 20
    max: 200
    recommended: 100
    unit: ns
  spotSize:
    min: 0.1
    max: 0.5
    recommended: 0.3
    unit: mm

# ============================================================================
# RELATIONSHIPS
# ============================================================================
relationships:
  
  operational:
    
    # Material this setting applies to
    baseMaterial:
      presentation: link
      url: /materials/metal/non-ferrous/aluminum-laser-cleaning
      linkText: View Material Details
      metadata:
        materialName: Aluminum
        category: metal
        subcategory: non-ferrous
      _section:
        sectionTitle: Base Material
        sectionDescription: Material these settings are optimized for
        icon: layers
        order: 5
    
    # Common challenges with these settings
    commonChallenges:
      presentation: card
      items:
        - id: surface-discoloration
          title: Surface Discoloration
          description: Excessive heat causing oxidation on aluminum surface
          severity: moderate
          solutions:
            - Reduce laser power by 10-20%
            - Increase scan speed
            - Use multiple passes at lower power
        
        - id: incomplete-removal
          title: Incomplete Contaminant Removal
          description: Insufficient energy to remove thick contaminant layers
          severity: high
          solutions:
            - Increase laser power gradually
            - Decrease scan speed
            - Use overlapping passes
      
      _section:
        sectionTitle: Common Challenges
        sectionDescription: Typical issues and solutions for aluminum laser cleaning
        icon: alert-triangle
        order: 10
        variant: warning
  
  safety:
    
    regulatoryStandards:
      presentation: card
      items:
        - id: ansi-z136
          name: ANSI Z136.1
          longName: ANSI Z136.1-2022 Safe Use of Lasers
          url: https://www.lia.org/resources/laser-safety-information/ansi-z136-standards
          image: /images/standards/ansi-logo.svg
          description: Laser safety compliance requirements
      
      _section:
        sectionTitle: Safety Standards
        sectionDescription: Regulatory compliance for these settings
        icon: shield-check
        order: 15
```

---

## 5. Required Fields Per Relationship Type

### Universal Fields (All relationship items)
```yaml
id: unique-identifier         # REQUIRED - kebab-case
name: Display Name            # REQUIRED - Human readable
url: /path/to/resource        # REQUIRED - Full path for links
image: /images/path.jpg       # REQUIRED - Hero/thumbnail image
description: Brief text...    # REQUIRED - 1-2 sentence summary
```

### Contaminants (in materials/contaminants)
```yaml
category: oxide               # REQUIRED - Classification
subcategory: iron            # REQUIRED - Sub-classification
frequency: high              # REQUIRED - very_high|high|moderate|low
severity: moderate           # REQUIRED - high|moderate|low
```

### Compounds (in contaminants/materials)
```yaml
title: Compound Name         # REQUIRED - Display title
category: gaseous           # REQUIRED - Classification
subcategory: reactive       # REQUIRED - Sub-classification
phase: gas                  # REQUIRED - solid|liquid|gas
hazardLevel: moderate       # REQUIRED - high|moderate|low
```

### Materials (in contaminants/compounds)
```yaml
category: metal             # REQUIRED - Classification
subcategory: ferrous        # REQUIRED - Sub-classification
frequency: high             # OPTIONAL - Cleaning frequency
difficulty: moderate        # OPTIONAL - Cleaning difficulty
```

### Industry Applications
```yaml
title: Industry Name        # REQUIRED - Display title
content: Full description   # REQUIRED - Detailed content
icon: plane                 # REQUIRED - Icon identifier
frequency: very_high        # REQUIRED - Usage frequency
```

### Regulatory Standards
```yaml
name: ANSI Z136.1          # REQUIRED - Short name
longName: Full standard    # REQUIRED - Complete name
url: https://...           # REQUIRED - Official standard URL
image: /path/to/logo.svg   # REQUIRED - Standard logo
```

---

## 6. Section Metadata Structure

All relationship sections MUST include `_section` metadata:

```yaml
_section:
  sectionTitle: Section Title                    # REQUIRED
  sectionDescription: Brief explanation...       # REQUIRED
  icon: icon-name                                # REQUIRED
  order: 10                                      # REQUIRED - Display order
  variant: default|warning|info|technical        # OPTIONAL - Visual style
  sectionMetadata:                               # OPTIONAL - Additional context
    relationshipType: contaminatedBy
    group: interactions
    domain: materials
```

---

## 7. Backend Implementation Guide

### Overview
The denormalization process involves reading complete data from existing source files and copying relevant fields into relationship items. All source data already exists - no manual data entry required.

### Available Source Files
- **153 material files**: `frontmatter/materials/**/*.yaml`
- **98 contaminant files**: `frontmatter/contaminants/**/*.yaml`
- **34 compound files**: `frontmatter/compounds/**/*.yaml`

### Implementation: Contaminants → Compounds (PRIORITY 1)

**Problem**: Compound items currently have only `id`
```yaml
producesCompounds:
  items:
  - id: carbon-monoxide-compound  # ❌ Incomplete
```

**Solution**: Lookup complete data from compound files
```yaml
producesCompounds:
  items:
  - id: carbon-monoxide-compound
    title: Carbon Monoxide           # ✅ From compound file
    name: Carbon Monoxide
    category: toxic_gas
    subcategory: asphyxiant
    url: /compounds/toxic_gas/asphyxiant/carbon-monoxide-compound
    image: /images/compound/carbon-monoxide-compound-hero.jpg
    description: Colorless, odorless toxic gas...
    phase: gas
    hazardLevel: high
```

**Automated Script Pattern**:
```python
import yaml
from pathlib import Path

# Step 1: Load all compound files into memory
compounds_lookup = {}
for file in Path("frontmatter/compounds").rglob("*.yaml"):
    with open(file) as f:
        data = yaml.safe_load(f)
        compounds_lookup[data['id']] = {
            'id': data['id'],
            'title': data.get('displayName', data['name']),
            'name': data['name'],
            'category': data['category'],
            'subcategory': data['subcategory'],
            'url': data['fullPath'],
            'image': data['images']['hero']['url'],
            'description': data['pageDescription'],
            'phase': data.get('phase', 'unknown'),
            'hazardLevel': data.get('hazardClass', 'moderate')
        }

# Step 2: Update each contaminant file
for file in Path("frontmatter/contaminants").rglob("*.yaml"):
    with open(file) as f:
        data = yaml.safe_load(f)
    
    # Find compound references
    compounds = data.get('relationships', {}).get('interactions', {}).get('producesCompounds', {}).get('items', [])
    
    # Enrich each compound
    for i, compound in enumerate(compounds):
        compound_id = compound.get('id')
        if compound_id in compounds_lookup:
            compounds[i] = compounds_lookup[compound_id]
    
    # Save updated file
    with open(file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
```

**Scope**: 
- Files to update: 93 contaminant files
- Compound references: 326 total
- Estimated time: 2-3 hours (automated script)
- Verification: Frontend removes defensive filter, compound cards work

### Implementation: Contaminants → Materials (PRIORITY 2)

**Problem**: Material items in `affectsMaterials` currently have only `id`
```yaml
affectsMaterials:
  items:
  - id: aluminum-laser-cleaning  # ❌ Incomplete
  - id: steel-laser-cleaning
  # ... 25+ materials per file
```

**Solution**: Same pattern as compounds, lookup from material files
```yaml
affectsMaterials:
  items:
  - id: aluminum-laser-cleaning
    name: Aluminum                    # ✅ From material file
    category: metal
    subcategory: non-ferrous
    url: /materials/metal/non-ferrous/aluminum-laser-cleaning
    image: /images/materials/aluminum-hero.jpg
    description: Lightweight non-ferrous metal...
    frequency: high
    difficulty: moderate
```

**Scope**:
- Files to update: 93 contaminant files
- Material references: ~2,300 total (25+ per file)
- Estimated time: 2-3 hours (automated script)
- Source: 153 existing material files

### Field Mapping from Source Files

**From Compound Files** → Relationship Items:
```yaml
# Source (compound file)
id: carbon-monoxide-compound
name: Carbon Monoxide
displayName: Carbon Monoxide (CO)  # Use this for 'title'
fullPath: /compounds/...            # Use this for 'url'
images.hero.url: /images/...        # Use this for 'image'
pageDescription: "..."              # Use this for 'description'
category: toxic_gas
subcategory: asphyxiant
# Note: Add 'phase' and 'hazardLevel' if missing

# Target (relationship item)
id: carbon-monoxide-compound
title: Carbon Monoxide (CO)         # ← displayName
name: Carbon Monoxide               # ← name
url: /compounds/...                 # ← fullPath
image: /images/...                  # ← images.hero.url
description: "..."                  # ← pageDescription
category: toxic_gas
subcategory: asphyxiant
phase: gas                          # ← Add if missing
hazardLevel: high                   # ← Add if missing
```

**From Material Files** → Relationship Items:
```yaml
# Source (material file)
id: aluminum-laser-cleaning
name: Aluminum
fullPath: /materials/...
images.hero.url: /images/...
pageDescription: "..."
category: metal
subcategory: non-ferrous

# Target (relationship item)
id: aluminum-laser-cleaning
name: Aluminum
url: /materials/...                 # ← fullPath
image: /images/...                  # ← images.hero.url
description: "..."                  # ← pageDescription
category: metal
subcategory: non-ferrous
frequency: high                     # ← Add based on relationship context
difficulty: moderate                # ← Add based on relationship context
```

### Verification Steps

**After Compound Denormalization**:
1. Run Python validation script:
   ```python
   # Verify all compounds have 9 required fields
   import yaml
   from pathlib import Path
   
   required_fields = ['id', 'title', 'name', 'category', 'subcategory', 'url', 'image', 'description', 'phase', 'hazardLevel']
   issues = []
   
   for file in Path("frontmatter/contaminants").rglob("*.yaml"):
       with open(file) as f:
           data = yaml.safe_load(f)
       compounds = data.get('relationships', {}).get('interactions', {}).get('producesCompounds', {}).get('items', [])
       
       for idx, compound in enumerate(compounds):
           missing = [field for field in required_fields if field not in compound]
           if missing:
               issues.append(f"{file.name} compound {idx}: Missing {missing}")
   
   if issues:
       print(f"❌ VALIDATION FAILED: {len(issues)} issues found")
       for issue in issues[:10]:  # Show first 10
           print(f"  - {issue}")
   else:
       print(f"✅ VALIDATION PASSED: All 326 compounds complete")
   ```

2. Frontend cleanup:
   
   **File**: `app/components/ContaminantsLayout/ContaminantsLayout.tsx`
   
   **Line 49-51**: REMOVE this defensive filter:
   ```typescript
   // ❌ DELETE THESE LINES:
   .filter((c): c is NonNullable<typeof c> => c != null && c.url && c.title)
   ```
   
   **Reason**: All compounds now guaranteed complete from denormalization
   
   **Verification**: 
   - Start dev server: `npm run dev`
   - Visit: http://localhost:3000/contaminants/oxide/iron/rust-contamination
   - Scroll to "Produced Compounds" section
   - Verify compound cards visible (not hidden)
   - Click each card → Should navigate to compound page (no 404)

**After Material Denormalization**:
1. Run validation script for 8 required fields (id, name, category, subcategory, url, image, description, frequency, difficulty)
2. Frontend verification: Material cards in `affectsMaterials` section display and link correctly
3. Check sample pages: Test 10 random contaminant pages for material card functionality

---

## 8. Migration Checklist

To achieve full normalization:

### ✅ Already Complete
- [x] Materials → contaminants (9 fields)
- [x] Materials → industry applications (complete)
- [x] Materials → regulatory standards (complete)
- [x] Materials → properties (camelCase naming)
- [x] All domains → FAQ structure

### ❌ Requires Backend Work

#### High Priority
- [ ] **Contaminants → compounds** (9 fields needed)
  - Scope: **326 compound references across 93 contaminant files**
  - Source: 34 existing compound files (all data available for lookup)
  - Fields: id, title, name, category, subcategory, url, image, description, phase, hazardLevel
  
- [ ] **Contaminants → materials** (`affectsMaterials` - 8 fields needed)
  - Scope: **~2,300 material references across 93 contaminant files**
  - Average: 25+ materials per contaminant
  - Source: 153 existing material files (all data available for lookup)
  - Fields: id, name, category, subcategory, url, image, description, frequency, difficulty

#### Medium Priority
- [ ] **Compounds → contaminants** (9 fields needed)
  - Scope: ~100-200 contaminant references
  - Fields: id, name, category, subcategory, url, image, description, frequency, severity

- [ ] **Compounds → materials** (8 fields needed)
  - Scope: ~100-150 material references
  - Fields: id, name, category, subcategory, url, image, description, frequency

#### Low Priority
- [ ] **Settings → challenges** (structured challenge data)
  - Scope: ~50 settings files
  - Fields: id, title, description, severity, solutions[]

---

## 9. Validation Rules

### Type Safety
```typescript
// All relationship items must be arrays
relationships.interactions.contaminatedBy.items: Array<ContaminantItem>

// All items must have required fields
ContaminantItem: {
  id: string;           // Required
  name: string;         // Required
  url: string;          // Required
  image: string;        // Required
  description: string;  // Required
  // ... domain-specific fields
}
```

### Naming Conventions
- **Keys**: camelCase (contaminatedBy, industryApplications)
- **IDs**: kebab-case (rust-contamination, aluminum-laser-cleaning)
- **Files**: kebab-case.yaml (aluminum-laser-cleaning.yaml)

### Data Integrity
- URLs must be valid paths (start with `/`)
- Images must be valid paths (start with `/images/`)
- Enum values must match allowed values (frequency: very_high|high|moderate|low)
- All referenced IDs must correspond to existing files

---

## 10. Benefits of Full Normalization

### For Frontend
- ✅ Zero async enrichment needed
- ✅ Consistent data shape across components
- ✅ Type-safe with TypeScript
- ✅ Fast static generation (no API calls)
- ✅ Reliable link generation (no 404s)

### For Backend
- ✅ Single source of truth per relationship
- ✅ Clear denormalization patterns
- ✅ Automated validation possible
- ✅ Consistent update procedures

### For Users
- ✅ Complete relationship information
- ✅ Working links throughout site
- ✅ Consistent UI experience
- ✅ Fast page loads

---

## 11. Implementation Priority

**Phase 1** ✅ **COMPLETE** (Critical - Blocks Features):
1. ✅ Contaminants → compounds denormalization (326 references, 93 files) - **DONE**
2. ✅ Frontend remove defensive filtering (compound cards enabled) - **DONE**

**Phase 2** ⚠️ **NOT STARTED** (High Value - Large Scope):
3. ⚠️ **Compounds → contaminants denormalization** (369 items, 34 files) - **NOT STARTED**
   - **Verified State (Jan 8, 2026)**: Only 4 fields per item (id, frequency, severity, typicalContext)
   - **Required**: All 9 fields (+ url, title, name, image, category, subcategory, description)
   - **Impact**: Frontend requires runtime enrichment (performance cost: +50-100ms per page)
   - **Action**: CREATE and RUN enrichment script (Section 13) - this is NOT automatic
   - **Clarification**: Backend regeneration does NOT enrich relationships automatically
4. 🔜 Contaminants → materials (`affectsMaterials` - 2,300 references, 93 files)

**Phase 3** 🔜 **NOT STARTED** (Complete Coverage):
5. 🔜 Compounds → materials denormalization (expected similar to Phase 2)
6. 🔜 Settings → challenges structure
7. 🔜 Comprehensive validation suite

---

## 12. Migration Execution Strategy

### Recommended: Atomic Migration

**Why Atomic?**
- Prevents frontend from receiving mix of complete/incomplete data
- Eliminates race conditions during gradual rollout
- Single commit = single rollback point
- Cleaner git history

---

## 13. Phase 2 Denormalization Script

**⚠️ CRITICAL**: Phase 2 compounds → contaminants is currently **INCOMPLETE**. Use this script to add missing fields.

**Current Metrics** (Jan 8, 2026):
- 📁 34 compound files with relationships
- 🔗 369 contaminant items total
- ❌ 0% complete (all need enrichment)
- 🎯 1,845 missing field values (5 fields × 369 items)

### Quick Start

```bash
# 1. Save script to scripts/data/enrich_compound_relationships.py
# 2. Run from project root:
python3 scripts/data/enrich_compound_relationships.py

# 3. Verify output:
# ✅ Compounds updated: 34
# 📦 Contaminants enriched: 369
# ✅ No errors encountered

# 4. Commit changes:
git add frontmatter/compounds/*.yaml
git commit -m "Phase 2: Enrich contaminant relationships (369 items, 34 files)"

# 5. Deploy with frontend to remove runtime enrichment workaround
```

### Phase 2: Compound Relationships Enrichment

```python
#!/usr/bin/env python3
"""
Phase 2: Enrich contaminant relationships in compound frontmatter files.

CURRENT STATE: Only 4 fields (id, frequency, severity, typicalContext)
TARGET STATE: All 9 fields (+ url, title, name, image, category, subcategory, description)
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List

class CompoundRelationshipEnricher:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.compounds_dir = base_path / 'frontmatter' / 'compounds'
        self.contaminants_dir = base_path / 'frontmatter' / 'contaminants'
        self.materials_dir = base_path / 'frontmatter' / 'materials'
        
        # Statistics
        self.stats = {
            'compounds_processed': 0,
            'compounds_updated': 0,
            'compounds_skipped': 0,
            'contaminants_enriched': 0,
            'materials_enriched': 0,
            'errors': []
        }
    
    def load_yaml(self, file_path: Path) -> Dict:
        """Load and parse YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.stats['errors'].append(f"Load error {file_path}: {e}")
            return None
    
    def save_yaml(self, file_path: Path, data: Dict):
        """Save enriched data back to YAML"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
        except Exception as e:
            self.stats['errors'].append(f"Save error {file_path}: {e}")
    
    def enrich_contaminant_item(self, item: Dict) -> Dict:
        """Enrich single contaminant relationship item"""
        contaminant_id = item.get('id')
        if not contaminant_id:
            return item
        
        # Load full contaminant data
        contaminant_file = self.contaminants_dir / f"{contaminant_id}.yaml"
        if not contaminant_file.exists():
            self.stats['errors'].append(f"Missing contaminant file: {contaminant_id}")
            return item
        
        full_data = self.load_yaml(contaminant_file)
        if not full_data:
            return item
        
        # Enrich with all required fields
        enriched = {
            'id': contaminant_id,
            'name': full_data.get('name', item.get('name', '')),
            'title': full_data.get('title', full_data.get('name', '')),
            'category': full_data.get('category', ''),
            'subcategory': full_data.get('subcategory', ''),
            'url': full_data.get('fullPath', f'/contaminants/{contaminant_id}'),
            'image': full_data.get('image', ''),
            'description': full_data.get('pageDescription', full_data.get('metaDescription', '')),
            'frequency': item.get('frequency', 'unknown'),
            'severity': item.get('severity', 'moderate'),
            'typicalContext': item.get('typicalContext', '')
        }
        
        self.stats['contaminants_enriched'] += 1
        return enriched
    
    def enrich_material_item(self, item: Dict) -> Dict:
        """Enrich single material relationship item (Phase 3)"""
        material_id = item.get('id')
        if not material_id:
            return item
        
        # Load full material data
        material_file = self.materials_dir / f"{material_id}.yaml"
        if not material_file.exists():
            self.stats['errors'].append(f"Missing material file: {material_id}")
            return item
        
        full_data = self.load_yaml(material_file)
        if not full_data:
            return item
        
        # Enrich with all required fields
        enriched = {
            'id': material_id,
            'name': full_data.get('name', item.get('name', '')),
            'title': full_data.get('title', full_data.get('name', '')),
            'category': full_data.get('category', ''),
            'subcategory': full_data.get('subcategory', ''),
            'url': full_data.get('fullPath', f'/materials/{material_id}'),
            'image': full_data.get('image', ''),
            'description': full_data.get('pageDescription', full_data.get('metaDescription', '')),
            'frequency': item.get('frequency', 'common')
        }
        
        self.stats['materials_enriched'] += 1
        return enriched
    
    def process_compound_file(self, compound_file: Path):
        """Process single compound file, enriching relationships"""
        self.stats['compounds_processed'] += 1
        
        # Load compound data
        data = self.load_yaml(compound_file)
        if not data:
            self.stats['compounds_skipped'] += 1
            return
        
        needs_update = False
        
        # Check if relationships exist
        relationships = data.get('relationships', {})
        interactions = relationships.get('interactions', {})
        
        # Enrich producedFromContaminants
        if 'producedFromContaminants' in interactions:
            contaminant_rel = interactions['producedFromContaminants']
            items = contaminant_rel.get('items', [])
            
            if items:
                # Check if enrichment needed (only has 4 fields)
                first_item = items[0]
                if len(first_item) <= 5:  # id, frequency, severity, typicalContext + maybe 1 more
                    # Needs enrichment
                    enriched_items = [self.enrich_contaminant_item(item) for item in items]
                    contaminant_rel['items'] = enriched_items
                    needs_update = True
        
        # Enrich affectsMaterials (Phase 3)
        if 'affectsMaterials' in interactions:
            material_rel = interactions['affectsMaterials']
            items = material_rel.get('items', [])
            
            if items:
                # Check if enrichment needed
                first_item = items[0]
                if len(first_item) <= 3:  # id, frequency + maybe 1 more
                    # Needs enrichment
                    enriched_items = [self.enrich_material_item(item) for item in items]
                    material_rel['items'] = enriched_items
                    needs_update = True
        
        # Save if updated
        if needs_update:
            self.save_yaml(compound_file, data)
            self.stats['compounds_updated'] += 1
            print(f"✅ Updated: {compound_file.name}")
        else:
            self.stats['compounds_skipped'] += 1
            print(f"⏭️  Skipped: {compound_file.name} (already complete)")
    
    def enrich_all_compounds(self):
        """Process all compound files"""
        compound_files = sorted(self.compounds_dir.glob('*.yaml'))
        
        print(f"\n🔍 Found {len(compound_files)} compound files")
        print("="*80)
        
        for compound_file in compound_files:
            self.process_compound_file(compound_file)
        
        self.print_report()
    
    def print_report(self):
        """Print enrichment statistics"""
        print("\n" + "="*80)
        print("📊 PHASE 2 ENRICHMENT COMPLETE")
        print("="*80)
        print(f"\n✅ Compounds processed: {self.stats['compounds_processed']}")
        print(f"✅ Compounds updated: {self.stats['compounds_updated']}")
        print(f"⏭️  Compounds skipped: {self.stats['compounds_skipped']}")
        print(f"📦 Contaminants enriched: {self.stats['contaminants_enriched']}")
        print(f"📦 Materials enriched: {self.stats['materials_enriched']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:
                print(f"   • {error}")
            if len(self.stats['errors']) > 10:
                print(f"   ... and {len(self.stats['errors']) - 10} more")
        else:
            print("\n✅ No errors encountered")

if __name__ == "__main__":
    # Get workspace base path
    base_path = Path(__file__).parent.parent  # Adjust as needed
    
    enricher = CompoundRelationshipEnricher(base_path)
    enricher.enrich_all_compounds()
```

**Usage**:
```bash
# Run from z-beam root
python3 scripts/data/enrich_compound_relationships.py

# Expected output:
# 🔍 Found 34 compound files
# ✅ Updated: ozone-o3.yaml
# ✅ Updated: nitrogen-oxides-nox.yaml
# ... (32 more)
# 📊 PHASE 2 ENRICHMENT COMPLETE
# ✅ Compounds updated: 34
# 📦 Contaminants enriched: 369
```

### Verification Steps

**1. Spot Check Files** (2 minutes):
```bash
# Check a sample compound file
cat frontmatter/compounds/benzene-compound.yaml | grep -A 15 "producedFromContaminants:"

# Verify 9+ fields per item:
# ✅ id: paint-residue-contamination
# ✅ url: /contaminants/coating/paint/paint-residue-contamination
# ✅ title: Paint Residue Contamination
# ✅ name: Paint Residue
# ✅ image: /images/contaminants/paint-hero.jpg
# ✅ category: coating
# ✅ subcategory: paint
# ✅ description: "Painted surfaces..."
# ✅ frequency: common
# ✅ severity: high
# ✅ typicalContext: "Thermal breakdown..."
```

**2. Automated Validation** (1 minute):
```python
# Run validation script
python3 << 'EOF'
import yaml
from pathlib import Path

required = {'id', 'url', 'title', 'name', 'image', 'category', 'subcategory', 'description', 'frequency'}
incomplete = 0

for file in Path('frontmatter/compounds').glob('*.yaml'):
    data = yaml.safe_load(open(file))
    items = data.get('relationships', {}).get('interactions', {}).get('producedFromContaminants', {}).get('items', [])
    for item in items:
        if not required.issubset(set(item.keys())):
            incomplete += 1
            print(f"❌ {file.name}: {item.get('id')} missing fields")

if incomplete == 0:
    print("✅ All 369 items complete!")
else:
    print(f"⚠️  {incomplete} items still incomplete")
EOF
```

**3. Frontend Testing** (5 minutes):
```bash
# Build with updated frontmatter
npm run build

# Test sample compound pages:
# - /compounds/irritant/aldehyde/benzene-compound
# - /compounds/toxic/gas/carbon-monoxide-compound
# - /compounds/corrosive/acid/hydrogen-chloride-compound

# Verify each page:
# ✅ "Source Contaminants" section visible
# ✅ Cards show proper titles (not IDs)
# ✅ Cards show images (not broken)
# ✅ Clicking cards navigates correctly
# ✅ No console errors
```

**4. Remove Runtime Enrichment** (After Phase 2 complete):
```typescript
// app/components/CompoundsLayout/CompoundsLayout.tsx
// DELETE lines 37-66 (runtime enrichment code)

// BEFORE:
const sourceContaminants = await Promise.all(
  sourceContaminantsIncomplete.map(async (item: any) => {
    // ... file loading code ...
  })
);

// AFTER:
const sourceContaminants = sourceContaminantsRaw?.items || [];
```

**5. Performance Verification**:
```bash
# Before Phase 2: ~150-200ms per compound page (with enrichment)
# After Phase 2: ~50-80ms per compound page (direct frontmatter)

# Check build time improvement:
time npm run build
```

---

## 14. Execution Plan - Phase 1 (Compounds)

1. **Pre-Migration** (30 minutes):
   ```bash
   # Create git tag for rollback safety
   git tag -a pre-compound-denorm -m "Before compound denormalization"
   git push origin pre-compound-denorm
   
   # Create branch for migration work
   git checkout -b feature/denormalize-compounds
   
   # Run backup (optional paranoia)
   tar -czf frontmatter-backup-$(date +%Y%m%d).tar.gz frontmatter/
   ```

2. **Migration Execution** (2-3 hours):
   ```bash
   # Run denormalization script
   python3 scripts/denormalize_compounds.py
   
   # Script updates all 93 contaminant files
   # Enriches 326 compound references
   ```

3. **Validation** (30 minutes):
   ```bash
   # Run automated validation
   python3 scripts/validate_denormalization.py --type=compounds
   
   # Expected output:
   # ✅ VALIDATION PASSED: All 326 compounds complete
   # ✅ All required fields present
   # ✅ All URLs valid format
   # ✅ All images exist
   ```

4. **Commit & Review** (30 minutes):
   ```bash
   # Stage changes
   git add frontmatter/contaminants/
   
   # Commit with descriptive message
   git commit -m "feat: Denormalize compounds in contaminant relationships
   
   - Enriched 326 compound references across 93 files
   - Added 9 fields: title, name, category, subcategory, url, image, description, phase, hazardLevel
   - All compounds now complete for frontend display
   - Validation: 100% pass rate
   
   Closes #ISSUE_NUMBER"
   
   # Push for review
   git push origin feature/denormalize-compounds
   ```

5. **Frontend Coordination** (Deploy together):
   - Backend PR: Compound denormalization
   - Frontend PR: Remove defensive filter from ContaminantsLayout
   - **Deploy both simultaneously** to staging
   - Verify compound cards work in staging
   - Deploy both to production

### Rollback Procedure

**If Issues Detected**:

```bash
# Option 1: Revert commit (preserves history)
git revert <commit-hash>
git push origin main

# Option 2: Reset to tag (clean slate)
git reset --hard pre-compound-denorm
git push origin main --force  # Use with caution

# Option 3: Restore from backup
tar -xzf frontmatter-backup-YYYYMMDD.tar.gz
git add frontmatter/
git commit -m "Rollback: Restore pre-denormalization state"
git push origin main
```

**Rollback Triggers**:
- Validation script fails (<100% pass rate)
- Frontend shows 404s on compound cards
- Build breaks due to YAML syntax errors
- Performance degradation (file sizes too large)

### Gradual Migration (Alternative - Not Recommended)

If atomic migration not feasible:

**Batch Strategy**:
```python
# Process files in batches of 10
for batch in range(0, 93, 10):
    files = contaminant_files[batch:batch+10]
    # Denormalize batch
    # Commit batch
    # Wait for validation
```

**Risks**:
- ⚠️ Frontend receives inconsistent data during migration
- ⚠️ Multiple rollback points
- ⚠️ More complex debugging
- ⚠️ Longer migration window

**Only use if**:
- Git repo struggles with 93-file commits
- Need to validate approach incrementally
- Team prefers cautious rollout

### Migration Coordination Checklist

**Before Migration**:
- [ ] Tag current state: `pre-compound-denorm`
- [ ] Backup frontmatter directory
- [ ] Notify frontend team of timeline
- [ ] Test migration script on 5 sample files
- [ ] Confirm validation script works

**During Migration**:
- [ ] Run denormalization script
- [ ] Monitor for errors/warnings
- [ ] Run validation suite
- [ ] Review git diff (spot check 5-10 files)
- [ ] Commit with detailed message

**After Migration**:
- [ ] Deploy backend changes
- [ ] Deploy frontend cleanup (remove filters)
- [ ] Test 10 random contaminant pages
- [ ] Verify all compound cards work
- [ ] Monitor error logs for 24 hours
- [ ] Update documentation status

---

## 13. Post-Migration Validation Suite

### Automated Validation Script

**Purpose**: Verify 100% of denormalized data is complete and correct

**File**: `scripts/validate_denormalization.py`

```python
import yaml
import sys
from pathlib import Path
from collections import defaultdict

class DenormalizationValidator:
    def __init__(self, domain: str):
        self.domain = domain
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
    
    def validate_compounds(self):
        """Validate compound denormalization in contaminant files"""
        required_fields = ['id', 'title', 'name', 'category', 'subcategory', 
                          'url', 'image', 'description', 'phase', 'hazardLevel']
        
        for file in Path("frontmatter/contaminants").rglob("*.yaml"):
            try:
                with open(file) as f:
                    data = yaml.safe_load(f)
                
                compounds = data.get('relationships', {}).get('interactions', {}) \
                               .get('producesCompounds', {}).get('items', [])
                
                self.stats['total_files'] += 1
                self.stats['total_compounds'] += len(compounds)
                
                for idx, compound in enumerate(compounds):
                    # Check required fields
                    missing = [f for f in required_fields if f not in compound or not compound[f]]
                    if missing:
                        self.issues['missing_fields'].append(
                            f"{file.name} compound {idx} ({compound.get('id', 'unknown')}): {missing}"
                        )
                    
                    # Validate URL format
                    url = compound.get('url', '')
                    if url and not url.startswith('/compounds/'):
                        self.issues['invalid_url'].append(
                            f"{file.name}: Invalid URL format '{url}'"
                        )
                    
                    # Validate image path
                    image = compound.get('image', '')
                    if image and not image.startswith('/images/'):
                        self.issues['invalid_image'].append(
                            f"{file.name}: Invalid image path '{image}'"
                        )
                    
                    # Check ID still present
                    if 'id' not in compound:
                        self.issues['missing_id'].append(
                            f"{file.name} compound {idx}: No ID field"
                        )
                    
                    self.stats['validated_compounds'] += 1
            
            except Exception as e:
                self.issues['file_errors'].append(f"{file.name}: {str(e)}")
    
    def validate_materials(self):
        """Validate material denormalization in contaminant files"""
        required_fields = ['id', 'name', 'category', 'subcategory', 
                          'url', 'image', 'description', 'frequency', 'difficulty']
        
        # Similar pattern to validate_compounds
        # Check affectsMaterials relationship
        pass
    
    def report(self):
        """Generate validation report"""
        print("\n" + "="*80)
        print(f"DENORMALIZATION VALIDATION REPORT - {self.domain.upper()}")
        print("="*80)
        
        # Stats
        print("\n📊 STATISTICS:")
        for key, value in self.stats.items():
            print(f"   • {key.replace('_', ' ').title()}: {value}")
        
        # Issues
        total_issues = sum(len(v) for v in self.issues.values())
        
        if total_issues == 0:
            print("\n✅ VALIDATION PASSED: No issues found")
            print(f"   All {self.stats['validated_compounds']} compounds complete and valid")
            return 0
        else:
            print(f"\n❌ VALIDATION FAILED: {total_issues} issues found\n")
            
            for category, items in self.issues.items():
                if items:
                    print(f"\n{category.replace('_', ' ').title()} ({len(items)}):")
                    for item in items[:5]:  # Show first 5 per category
                        print(f"   • {item}")
                    if len(items) > 5:
                        print(f"   ... and {len(items) - 5} more")
            
            return 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', choices=['compounds', 'materials'], required=True)
    args = parser.parse_args()
    
    validator = DenormalizationValidator(args.type)
    
    if args.type == 'compounds':
        validator.validate_compounds()
    else:
        validator.validate_materials()
    
    sys.exit(validator.report())
```

### Frontend Smoke Tests

**Manual Test Checklist** (15 minutes):

```markdown
## Compound Denormalization Smoke Tests

### Test 1: Random Contaminant Pages (10 samples)
- [ ] /contaminants/oxide/iron/rust-contamination
- [ ] /contaminants/organic-residue/petroleum/grease-contamination
- [ ] /contaminants/coating/paint/paint-contamination
- [ ] /contaminants/biological/mold/mold-contamination
- [ ] /contaminants/chemical/acid/acid-contamination
- [ ] /contaminants/particulate/dust/dust-contamination
- [ ] /contaminants/adhesive/adhesive-residue-contamination
- [ ] /contaminants/corrosion/rust-contamination
- [ ] /contaminants/scale/mineral-scale-contamination
- [ ] /contaminants/coating/anodizing-contamination

**For Each Page**:
- [ ] "Produced Compounds" section visible
- [ ] Compound cards display with images
- [ ] Card titles show compound names (not just IDs)
- [ ] Cards show category/subcategory
- [ ] Clicking card navigates to compound page (no 404)
- [ ] Browser console has no errors

### Test 2: Compound Detail Pages
- [ ] Navigate to 5 compound pages via contaminant cards
- [ ] Verify page loads successfully
- [ ] Check breadcrumb navigation works
- [ ] Verify "Produced From" section shows contaminants
- [ ] Confirm back navigation works

### Test 3: Edge Cases
- [ ] Contaminant with no compounds (section hidden)
- [ ] Contaminant with 1 compound (single card)
- [ ] Contaminant with 5+ compounds (card grid)
- [ ] Mobile view (cards responsive)
- [ ] Dark mode (if applicable)

### Test 4: Performance
- [ ] Page load time <2 seconds
- [ ] No console warnings about missing data
- [ ] Lighthouse score unchanged
- [ ] No memory leaks in DevTools
```

### Automated E2E Tests (Optional - Recommended)

**File**: `tests/e2e/compound-denormalization.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Compound Denormalization', () => {
  test('compound cards display and navigate correctly', async ({ page }) => {
    // Visit contaminant page
    await page.goto('/contaminants/oxide/iron/rust-contamination');
    
    // Verify section exists
    const section = page.locator('text=Produced Compounds');
    await expect(section).toBeVisible();
    
    // Find compound cards
    const cards = page.locator('[data-testid="compound-card"]');
    const count = await cards.count();
    expect(count).toBeGreaterThan(0);
    
    // Check first card has complete data
    const firstCard = cards.first();
    await expect(firstCard.locator('img')).toBeVisible();
    await expect(firstCard.locator('h3')).not.toBeEmpty();
    
    // Click card and verify navigation
    await firstCard.click();
    await expect(page).toHaveURL(/\/compounds\/.+/);
    
    // Verify compound page loaded
    await expect(page.locator('h1')).toBeVisible();
  });
  
  test('no 404 errors on compound navigation', async ({ page }) => {
    const contaminantPages = [
      '/contaminants/oxide/iron/rust-contamination',
      '/contaminants/organic-residue/petroleum/grease-contamination',
      // ... more pages
    ];
    
    for (const url of contaminantPages) {
      await page.goto(url);
      
      // Get all compound card links
      const links = await page.locator('[data-testid="compound-card"]').all();
      
      for (const link of links) {
        const href = await link.getAttribute('href');
        if (href) {
          const response = await page.goto(href);
          expect(response?.status()).toBe(200);
        }
      }
    }
  });
});
```

### Validation Frequency

**During Migration**:
- Run validation after EVERY batch/commit
- Zero tolerance for failures

**Post-Migration**:
- Run daily for first week
- Run weekly for first month
- Add to CI/CD pipeline (run on every PR)

**Monitoring**:
- Track 404 rates in analytics
- Monitor error logs for compound-related issues
- Set up alerts for sudden 404 spikes

---

**Next Steps**: 
1. Review and approve this structure
2. Backend implements compound denormalization (Phase 1)
3. Run validation suite (100% pass required)
4. Frontend removes defensive filters once validated
5. Deploy both changes simultaneously
6. Monitor for 24 hours
7. Proceed with Phase 2 denormalization
