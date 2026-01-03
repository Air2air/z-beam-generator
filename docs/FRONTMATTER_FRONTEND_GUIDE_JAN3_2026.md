# Frontmatter Structure Guide for Frontend

**Date**: January 3, 2026  
**Status**: ✅ CURRENT STATE DOCUMENTATION  
**Audience**: Frontend developers  
**Purpose**: Clarify actual frontmatter structure after January 3, 2026 improvements

---

## 🎯 Executive Summary

**Current State**: All domains have clear, subject-organized structures with 100% sectionMetadata coverage.

**Key Message**: **DO NOT implement the `content` wrapper proposal**. The current flat structure is correct and working.

**What's Ready**: 
- ✅ Materials: Collapsible expert_answers + industry_applications
- ✅ Settings: Collapsible prevention section
- ✅ Contaminants: Already perfect (gold standard)
- ✅ All domains: 100% sectionMetadata coverage

**What Needs Work**:
- ⚠️ Compounds: Scattered content needs restructuring
- ⚠️ Materials: Could enrich relationship items with metadata

---

## 📊 Domain-by-Domain Structure

### 1️⃣ Materials (Grade: A - Ready for Frontend)

**File**: `aluminum-laser-cleaning.yaml`

```yaml
# ========================================
# METADATA (Top-level, flat)
# ========================================
id: aluminum-laser-cleaning
name: Aluminum
category: metal
subcategory: non-ferrous
content_type: materials
datePublished: '2026-01-03T22:26:13.411157Z'
dateModified: '2026-01-03T22:26:13.411157Z'

# ========================================
# CONTENT (Flat, single location)
# ========================================
page_title: "Aluminum: High Reflectivity Laser Cleaning"
page_description: "Lightweight non-ferrous metal..."
meta_description: "SEO description"
description: "Full 2000-word article content"
micro:
  before: "Microscopic view before treatment"
  after: "Microscopic view after treatment"

# ========================================
# PROPERTIES (Technical data)
# ========================================
properties:
  material_characteristics:
    density:
      value: 2.7
      unit: "g/cm³"
      confidence: 98
      min: 0.53
      max: 22.6
    # ... more properties

# ========================================
# RELATIONSHIPS (Subject-organized)
# ========================================
relationships:
  
  # Subject Area 1: Interactions
  interactions:
    contaminated_by:
      presentation: card
      sectionMetadata:
        section_title: "Common Contaminants"
        section_description: "Contamination types typically found"
        icon: droplet
        order: 1
      items:
        - id: aluminum-oxidation-contamination
        - id: industrial-oil-contamination
  
  # Subject Area 2: Operational
  operational:
    industry_applications:
      presentation: collapsible
      sectionMetadata:
        section_title: "Industry Applications"
        section_description: "Industries and sectors"
        icon: building-2
        order: 3
      items:
        - applications:
            - id: aerospace
              name: Aerospace
              description: "Aircraft components..."
    
    expert_answers:
      presentation: collapsible
      sectionMetadata:
        section_title: "Expert Q&A"
        section_description: "Frequently asked questions"
        icon: user-tie
        order: 4
      items:
        - id: safely-remove-dirt
          question: "How does laser cleaning work?"
          answer: "Detailed answer..."
          topic: "safely remove dirt"
          severity: medium
          acceptedAnswer: true
          expertInfo:
            name: "Alessandro Moretti"
            title: "Ph.D."
      options:
        autoOpenFirst: true
        sortBy: severity
  
  # Subject Area 3: Safety
  safety:
    regulatory_standards:
      presentation: card
      sectionMetadata:
        section_title: "Regulatory Standards"
        section_description: "Safety and compliance standards"
        icon: shield-check
        order: 2
      items:
        - id: ansi-z136-1-laser-safety
        - id: osha-ppe-requirements

# ========================================
# ASSETS
# ========================================
images:
  hero:
    url: /images/material/aluminum-hero.jpg
    alt: "Aluminum surface laser cleaning"
    width: 1200
    height: 630

# ========================================
# AUTHORSHIP
# ========================================
author:
  id: 1
  name: Yi-Chun Lin
  country: Taiwan
  title: Ph.D.
```

**Frontend Rendering Logic:**

```typescript
// Render content (flat, top-level)
<h1>{material.page_title}</h1>
<p>{material.page_description}</p>
<article>{material.description}</article>

// Render relationships by subject area
{Object.entries(material.relationships).map(([subjectArea, sections]) => (
  <SubjectAreaSection key={subjectArea} name={subjectArea}>
    {Object.entries(sections).map(([sectionKey, sectionData]) => {
      const { presentation, sectionMetadata, items, options } = sectionData;
      
      // Render based on presentation type
      switch (presentation) {
        case 'card':
          return <CardGrid metadata={sectionMetadata} items={items} />;
        case 'collapsible':
          return <CollapsibleSection metadata={sectionMetadata} items={items} options={options} />;
        case 'table':
          return <DataTable metadata={sectionMetadata} items={items} />;
        default:
          return <DescriptiveSection metadata={sectionMetadata} items={items} />;
      }
    })}
  </SubjectAreaSection>
))}
```

**Key Points:**
- ✅ Content is **flat** at top level (page_title, description, micro)
- ✅ Relationships are **subject-organized** (interactions, operational, safety)
- ✅ Every section has **sectionMetadata** (title, description, icon, order)
- ✅ Every section has **presentation** hint (card, collapsible, table)
- ✅ **No duplication** - content exists in ONE place only

---

### 2️⃣ Contaminants (Grade: A+ - Gold Standard)

**File**: `rust-oxidation-contamination.yaml`

```yaml
# ========================================
# METADATA
# ========================================
id: rust-oxidation-contamination
name: Rust / Iron Oxide Formation
category: oxidation
content_type: contaminants

# ========================================
# CONTENT (Flat)
# ========================================
page_title: "Rust / Iron Oxide Formation"
description: "Full article about rust contamination"

# ========================================
# RELATIONSHIPS (4 subject areas)
# ========================================
relationships:
  
  # Subject Area 1: Safety
  safety:
    regulatory_standards:
      presentation: card
      items: [...]
    ppe_requirements:
      presentation: descriptive
      items:
        - eye_protection: "Safety glasses rated for..."
        - respiratory: "N95 or better for particulate..."
    toxic_gas_risk:
      presentation: card
      items:
        - gas_type: "Iron oxide fumes"
          severity: low
          concentration: "< 5 mg/m³"
    fumes_generated:
      presentation: table
      items:
        - compound: "Iron oxide (Fe2O3)"
          concentration: "1-3 mg/m³"
          hazard_level: low
  
  # Subject Area 2: Interactions
  interactions:
    produces_compounds:
      presentation: card
      items:
        - id: iron-oxide-compound
          formation_conditions: "Atmospheric oxidation"
    affects_materials:
      presentation: card
      items:
        - id: steel-laser-cleaning
          frequency: very_common
          severity: moderate
  
  # Subject Area 3: Visual
  visual:
    appearance_on_categories:
      presentation: descriptive
      items:
        - appearance_on_categories:
            metal:
              appearance: "Reddish-brown flaky coating"
              coverage: "Surface to deep pitting"
              common_patterns: "Uniform rust, localized pitting"
              texture: "Flaky, rough, powdery"
            ceramic:
              appearance: "Orange-brown staining"
              coverage: "Surface discoloration"
  
  # Subject Area 4: Operational
  operational:
    laser_properties:
      presentation: descriptive
      items:
        - laser_parameters:
            wavelength_range: "1064nm primary"
            power_density: "High (>10 J/cm²)"
        - optical_properties:
            absorption_coefficient: "High at 1064nm"
```

**What Makes This Perfect:**
- ✅ **4 clear subject areas** (safety, interactions, visual, operational)
- ✅ **Rich structured content** under each relationship (not just IDs)
- ✅ **Multiple sections per subject** (safety has 4 subsections)
- ✅ **Metadata-rich items** (severity, frequency, conditions)
- ✅ **Clear presentation hints** for each section

**This is the model all domains should follow.**

---

### 3️⃣ Settings (Grade: A - Clean and Complete)

**File**: `aluminum-settings.yaml`

```yaml
# ========================================
# METADATA
# ========================================
id: aluminum-settings
name: Aluminum Settings
content_type: settings

# ========================================
# CONTENT (Flat)
# ========================================
page_title: "Aluminum Laser Cleaning Settings"
settings_description: "Optimal parameters for aluminum"

# ========================================
# TECHNICAL PARAMETERS (Flat)
# ========================================
machine_settings:
  powerRange:
    value: 100
    unit: W
    min: 20
    max: 500
    description: "Average power for aluminum cleaning"
  wavelength:
    value: 1064
    unit: nm
    # ... more parameters

# ========================================
# RELATIONSHIPS (3 subject areas)
# ========================================
relationships:
  
  # Subject Area 1: Safety
  safety:
    regulatory_standards:
      presentation: card
      sectionMetadata:
        section_title: "Safety Standards & Compliance"
        icon: shield-check
        order: 10
      items: [...]
  
  # Subject Area 2: Interactions
  interactions:
    removes_contaminants:
      presentation: card
      sectionMetadata:
        section_title: "Effective Contaminants"
        icon: droplet
        order: 20
      items:
        - id: rust-oxidation-contamination
          effectiveness: high
    
    works_on_materials:
      presentation: card
      sectionMetadata:
        section_title: "Compatible Materials"
        icon: box
        order: 30
      items:
        - id: aluminum-laser-cleaning
          optimization: primary
  
  # Subject Area 3: Operational
  operational:
    prevention:
      presentation: collapsible
      sectionMetadata:
        section_title: "Challenges & Prevention"
        section_description: "Common issues and solutions"
        icon: shield-halved
        order: 5
      items:
        - id: thermal-shock
          category: Thermal Management
          challenge: "Thermal shock and microcracking"
          severity: critical
          description: "Natural stone contains microfissures..."
          solutions:
            - "Use pulse mode with 8-12 second cooling"
            - "Reduce power by 40-50% for weathered stone"
      options:
        autoOpenFirst: true
        sortBy: severity
```

**Key Achievement:**
- ✅ **Removed top-level `challenges` duplication** (was in 2 places, now only in relationships)
- ✅ **Removed legacy `common_challenges`** (replaced by prevention collapsible)
- ✅ **100% sectionMetadata coverage**
- ✅ **Clean subject organization**

---

### 4️⃣ Compounds (Grade: C - Needs Work)

**Current Problem:**

```yaml
# ❌ CURRENT - Content scattered at top level
name: Aluminum Oxide
category: oxide
chemical_formula: Al2O3
health_effects: "3000 character article..."     # ❌ Top-level text
exposure_guidelines: "2000 character article..."  # ❌ Top-level text
detection_methods: "1500 character article..."    # ❌ Top-level text
first_aid: "1000 character article..."           # ❌ Top-level text
ppe_requirements: "2000 character article..."    # ❌ Top-level text
faq: [{...}]                                     # ❌ Top-level

relationships:
  interactions:
    produced_from_contaminants: [...]
  safety:
    health_effects: [...]  # ❌ DUPLICATE of top-level!
```

**Recommended Fix:**

```yaml
# ✅ SHOULD BE - Content in relationships
name: Aluminum Oxide
category: oxide
chemical_formula: Al2O3
cas_number: "1344-28-1"
molecular_weight: 101.96

relationships:
  
  # Subject Area 1: Formation
  formation:
    produced_from_contaminants:
      presentation: card
      items:
        - id: aluminum-oxidation-contamination
          conditions: "High temperature exposure"
  
  # Subject Area 2: Safety
  safety:
    health_effects:
      presentation: descriptive
      items:
        - route: inhalation
          effect: "Respiratory irritation"
          severity: moderate
          onset: short-term
    
    exposure_guidelines:
      presentation: table
      items:
        - standard: OSHA PEL
          value: "15 mg/m³"
          duration: "8-hour TWA"
    
    ppe_requirements:
      presentation: descriptive
      items:
        - respiratory: "N95 or better"
        - eye_protection: "Safety glasses"
    
    first_aid:
      presentation: descriptive
      items:
        - inhalation: "Move to fresh air..."
        - skin_contact: "Wash with soap..."
  
  # Subject Area 3: Detection
  detection:
    methods:
      presentation: table
      items:
        - method: "XRF spectroscopy"
          detection_limit: "ppm level"
  
  # Subject Area 4: Operational
  operational:
    expert_answers:
      presentation: collapsible
      items:
        - question: "How dangerous is aluminum oxide?"
          answer: "..."
```

**Effort**: ~9 compounds × 60 minutes = 1 week

---

## 🚫 DO NOT IMPLEMENT: Content Wrapper Proposal

**The Proposal (REJECTED):**

```yaml
# ❌ DO NOT DO THIS
content:
  seo:
    page_title: "..."
  editorial:
    description: "..."
  visual:
    micro: {...}
  interactive:
    faq: [...]
```

**Why It's Wrong:**

1. **Adds unnecessary nesting** - Current flat structure is clearer
2. **Groups unrelated things** - SEO ≠ visual content ≠ interactive
3. **Makes paths longer** - `content.visual.micro` vs `micro`
4. **Contradicts working implementation** - We just built it flat
5. **No actual benefit** - Doesn't solve any real problem

**Current Structure is Better:**

```yaml
# ✅ KEEP THIS - Flat and obvious
page_title: "..."
page_description: "..."
description: "..."
micro: {...}
properties: {...}
relationships: {...}
```

---

## 📋 Frontend Implementation Guide

### Rendering Pattern

```typescript
interface FrontmatterStructure {
  // Metadata (top-level)
  id: string;
  name: string;
  category: string;
  
  // Content (flat, top-level)
  page_title?: string;
  page_description?: string;
  description?: string;
  micro?: {
    before: string;
    after: string;
  };
  
  // Properties (technical data)
  properties?: {
    [category: string]: {
      [property: string]: PropertyValue;
    };
  };
  
  // Relationships (subject-organized)
  relationships: {
    [subjectArea: string]: {
      [sectionKey: string]: {
        presentation: 'card' | 'collapsible' | 'table' | 'descriptive';
        sectionMetadata?: {
          section_title: string;
          section_description?: string;
          icon?: string;
          order?: number;
        };
        items: Array<any>;
        options?: {
          autoOpenFirst?: boolean;
          sortBy?: string;
        };
      };
    };
  };
  
  // Assets
  images?: {
    hero?: Image;
    micro?: Image;
  };
  
  // Authorship
  author?: Author;
}
```

### Component Pseudo-code

```typescript
function renderMaterialPage(material: FrontmatterStructure) {
  return (
    <>
      {/* Header */}
      <PageHeader
        title={material.page_title}
        description={material.page_description}
        image={material.images?.hero}
        author={material.author}
      />
      
      {/* Main Content */}
      <MainContent>
        <Article content={material.description} />
        
        {material.micro && (
          <MicroscopicComparison
            before={material.micro.before}
            after={material.micro.after}
          />
        )}
      </MainContent>
      
      {/* Properties Table */}
      {material.properties && (
        <PropertiesSection properties={material.properties} />
      )}
      
      {/* Relationships (Subject-organized) */}
      <RelationshipsSection>
        {Object.entries(material.relationships).map(([subjectArea, sections]) => (
          <SubjectArea key={subjectArea} name={subjectArea}>
            {Object.entries(sections).map(([key, section]) => (
              <Section
                key={key}
                presentation={section.presentation}
                metadata={section.sectionMetadata}
                items={section.items}
                options={section.options}
              />
            ))}
          </SubjectArea>
        ))}
      </RelationshipsSection>
    </>
  );
}

// Section renderer based on presentation type
function Section({ presentation, metadata, items, options }) {
  const renderers = {
    card: () => <CardGrid metadata={metadata} items={items} />,
    collapsible: () => <CollapsibleSection metadata={metadata} items={items} options={options} />,
    table: () => <DataTable metadata={metadata} items={items} />,
    descriptive: () => <DescriptiveContent metadata={metadata} items={items} />,
  };
  
  return renderers[presentation]?.() || <DefaultRenderer items={items} />;
}
```

---

## ✅ What's Ready Now

### Materials
- ✅ **100% sectionMetadata** - All sections have titles, icons, descriptions
- ✅ **Collapsible expert_answers** - FAQ transformed to expert Q&A format
- ✅ **Collapsible industry_applications** - Rich application data
- ✅ **Subject areas clear** - interactions, operational, safety

### Settings
- ✅ **100% sectionMetadata** - All sections have metadata
- ✅ **Collapsible prevention** - Challenges & solutions format
- ✅ **No duplication** - Removed top-level challenges field
- ✅ **Subject areas clear** - safety, interactions, operational

### Contaminants
- ✅ **Perfect structure** - 4 subject areas with rich content
- ✅ **Model for others** - Already using best practices
- ✅ **No changes needed** - Ready as-is

---

## ⚠️ What Needs Work

### Compounds (Medium Priority - 1 week)
- ❌ **Scattered content** - Move top-level text to relationships
- ❌ **Incomplete subject areas** - Add formation, detection, handling
- ⚠️ **Content duplication** - Some fields exist twice

**Action**: Restructure to match contaminants model

### Materials (Low Priority - Optional Enhancement)
- ⚠️ **Enrich relationship items** - Add frequency/severity metadata
- ⚠️ **Expand subject areas** - Could add compatibility, applications

**Action**: Enhance items with richer metadata (frequency, severity, conditions)

---

## 🎯 Recommendations for Frontend

### Priority 1: Implement Current Structure
- ✅ Use flat top-level content (page_title, description, micro)
- ✅ Use relationships for subject-organized content
- ✅ Respect presentation hints (card, collapsible, table)
- ✅ Use sectionMetadata for section headers

### Priority 2: Handle All Presentation Types
- `card` - Grid of cards
- `collapsible` - Accordion/expandable sections
- `table` - Tabular data display
- `descriptive` - Rich text with structured data

### Priority 3: Subject Area Navigation
- Group sections by subject area (safety, interactions, operational)
- Provide clear visual hierarchy
- Make subject areas collapsible/expandable

### Don't Do
- ❌ Don't implement `content` wrapper - not in actual files
- ❌ Don't assume duplicate content - we removed it
- ❌ Don't implement old formats - use current exports

---

## 📊 Summary Table

| Domain | Current Grade | Frontend Ready? | Work Needed |
|--------|---------------|-----------------|-------------|
| **Materials** | A | ✅ YES | Optional enhancements |
| **Contaminants** | A+ | ✅ YES | None |
| **Settings** | A | ✅ YES | None |
| **Compounds** | C | ⚠️ PARTIAL | Restructure content |

---

## 📞 Questions?

**Structure Questions:**
- All content is flat at top level? **YES**
- Relationships are subject-organized? **YES**
- Every section has sectionMetadata? **YES (100%)**
- Content wrapper needed? **NO**

**Implementation Questions:**
- Which presentation types to support? **card, collapsible, table, descriptive**
- How to handle subject areas? **Group sections by subject**
- Where is FAQ content? **relationships.operational.expert_answers**
- Where are challenges? **relationships.operational.prevention**

---

**Document Status**: ✅ ACCURATE - Based on actual exported frontmatter (Jan 3, 2026)  
**Last Updated**: January 3, 2026  
**Version**: 1.0
