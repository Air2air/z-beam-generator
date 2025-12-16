# Frontmatter Generation Guide for AI Assistants

**Version**: 1.0  
**Last Updated**: December 16, 2025  
**For**: AI assistants generating material frontmatter files

---

## 🎯 Purpose

This guide ensures all generated material frontmatter files meet Z-Beam's quality, completeness, and SEO standards. Follow these requirements precisely when generating or updating frontmatter YAML files.

---

## 📋 Schema Version & Structure

**Required Schema Version**: `4.0.0`

```yaml
schema_version: 4.0.0
content_type: unified_material
```

---

## ✅ Required Fields Checklist

### **1. Basic Metadata** (MANDATORY)

```yaml
name: [Material Name]
slug: [kebab-case-slug]
id: [material-slug-laser-cleaning]
category: [metal|plastic|ceramic|composite|wood|other]
subcategory: [specific type]
content_type: unified_material
schema_version: 4.0.0
```

### **2. Publication Dates** (MUST NOT BE NULL) 🔥 **CRITICAL**

```yaml
datePublished: '2025-12-16T00:00:00Z'  # ISO 8601 format - REQUIRED
dateModified: '2025-12-16T00:00:00Z'   # ISO 8601 format - REQUIRED
```

**✅ CORRECT**: Use generation date or current date  
**❌ WRONG**: `datePublished: null` or `dateModified: null`

**🚨 DISCOVERED ISSUE**: All 153 existing files have null dates (100% failure rate)  
**SEO IMPACT**: Blocks Google freshness signals, reduces ranking potential  
**FIX PRIORITY**: Critical - must be addressed before deployment

### **3. Author Information** (MANDATORY - Full Profile)

```yaml
author:
  id: [1-4]
  name: [Full Name]
  country: [Country]
  country_display: [Display Name]
  title: [Degree/Title]
  sex: [m|f]
  jobTitle: [Professional Title]
  expertise:
    - [Area 1]
    - [Area 2]
  affiliation:
    name: [Organization]
    type: Organization
  credentials:
    - [Credential 1]
    - [Credential 2]
  email: info@z-beam.com
  image: /images/author/[slug].jpg
  imageAlt: [Descriptive alt text]
  url: https://z-beam.com/authors/[slug]
  sameAs:
    - [LinkedIn URL]
    - [Professional profile URL]
  persona_file: [country]_persona.yaml
  formatting_file: [country]_formatting.yaml
```

### **4. Voice Metadata** (MANDATORY)

```yaml
_metadata:
  voice:
    author_name: [Author Name]
    author_country: [Country]
    voice_applied: true
    content_type: material
```

### **5. Title & Description** (MANDATORY)

```yaml
title: [Material Name] Laser Cleaning
material_description: [30-50 word description highlighting key benefits and characteristics for laser cleaning applications]
```

**Requirements**:
- Description: 30-50 words
- Focus on practical benefits
- Technical but accessible language
- Avoid generic phrases like "ideal for" or "perfect for"

### **6. Breadcrumb Navigation** (MANDATORY)

```yaml
breadcrumb:
  - label: Home
    href: /
  - label: Materials
    href: /materials
  - label: [Category]
    href: /materials/[category-slug]
  - label: [Subcategory]
    href: /materials/[category-slug]/[subcategory-slug]
  - label: [Material Name]
    href: /materials/[category-slug]/[subcategory-slug]/[material-slug]
```

**Requirements**:
- Always 5 levels (Home → Materials → Category → Subcategory → Material)
- URLs must match directory structure
- Labels must match material hierarchy

### **7. Images** (MANDATORY)

```yaml
images:
  hero:
    alt: [Material name] surface during precision laser cleaning process removing contamination layer
    url: /images/material/[material-slug]-laser-cleaning-hero.jpg
  micro:
    alt: [Material name] surface at 500x magnification showing laser cleaning results
    url: /images/material/[material-slug]-laser-cleaning-micro.jpg
```

### **8. Micro Content** (MANDATORY - Before/After)

```yaml
micro:
  before: [60-80 words describing contaminated surface in vivid detail at high magnification. Use sensory language, describe texture, distribution, and visual characteristics.]
  after: [60-80 words describing cleaned surface. Contrast with before state, emphasize clarity, smoothness, and restoration quality.]
```

**Requirements**:
- Each section: 60-80 words
- Use vivid, descriptive language
- Focus on visual and tactile characteristics
- Maintain scientific accuracy
- Use present tense

### **9. FAQ Section** (MANDATORY - Minimum 3 Questions)

```yaml
faq:
  - question: [Practical question about laser cleaning this material]
    answer: [100-150 word answer with practical guidance, comparisons, and real-world context. Include author's experience.]
  - question: [Another practical question]
    answer: [100-150 word answer]
  - question: [Third practical question]
    answer: [100-150 word answer - MUST BE COMPLETE]
  # Additional FAQs encouraged for complex materials
```

**Requirements**:
- Minimum 3 FAQ items (more encouraged for complex topics)
- Questions: Practical, specific to material
- Answers: 100-150 words each
- Include comparisons to similar materials
- Mention real-world applications
- Use first-person experience ("I've seen", "In my experience")
- **ALL answers must be complete** - no truncation

### **10. Regulatory Standards** (MANDATORY - Minimum 2)

```yaml
regulatoryStandards:
  - description: [Standard identifier] - [Standard name]
    image: /images/logo/logo-org-[org-slug].png
    longName: [Full organization name]
    name: [Acronym]
    url: [Official standard URL]
```

**Common Standards**:
- FDA 21 CFR 1040.10 (Laser Product Performance)
- ANSI Z136.1 (Safe Use of Lasers)
- OSHA regulations
- ISO standards

### **11. Material Properties** (MANDATORY - 100% Complete)

```yaml
materialProperties:
  material_characteristics:
    label: Material Characteristics
    percentage: 60.0
    density:
      value: [number]
      unit: g/cm³
      min: [category min]
      max: [category max]
    # ... 11 more properties with values, units, min/max
    
  laser_material_interaction:
    label: Laser-Material Interaction
    percentage: 40.0
    thermalDestruction:
      value: [number]
      unit: K
      min: [category min]
      max: [category max]
    # ... 8 more properties with scientific citations
```

**Required Material Characteristics** (12 total):
- density, porosity, surfaceRoughness, tensileStrength
- youngsModulus, hardness, flexuralStrength, oxidationResistance
- corrosionResistance, compressiveStrength, fractureToughness, electricalResistivity

**Required Laser Interaction Properties** (9 total):
- thermalDestruction, laserAbsorption, laserDamageThreshold, ablationThreshold
- thermalDiffusivity, thermalExpansion, specificHeat, thermalConductivity, laserReflectivity

**For Properties with Research**:
```yaml
propertyName:
  value: [number]
  unit: [unit]
  source: scientific_literature
  source_type: [journal_article|materials_database|reference_handbook]
  source_name: [Publication name]
  citation: [Full citation with DOI if available]
  context: [Material purity, temperature, test conditions, methodology]
  researched_date: [ISO 8601 timestamp]
  needs_validation: true
  min: [category min]
  max: [category max]
```

### **12. Domain Linkages** (MANDATORY - 4 Contaminants)

```yaml
domain_linkages:
  related_contaminants:
    - id: [contaminant-slug]
      title: [Contaminant Title]
      url: /contaminants/[path]/[slug]
      image: /images/contaminants/[path]/[slug].jpg
      frequency: [rare|occasional|common|frequent]
      severity: [low|moderate|high|critical]
      typical_context: [industrial|general|specialized]
```

**Requirements**:
- Include 4-6 relevant contaminants
- All fields must be complete
- URLs must be valid paths
- Frequency/severity should reflect real-world occurrence

### **13. Service Offering** (MANDATORY)

```yaml
serviceOffering:
  enabled: true
  type: professionalCleaning
  materialSpecific:
    estimatedHoursMin: [1-8]
    estimatedHoursTypical: [2-12]
    targetContaminants:
      - [Contaminant type 1]
      - [Contaminant type 2]
    notes: [Specific considerations for this material]
```

### **14. EEAT Data** (MUST NOT BE NULL)

**🚨 DISCOVERED ISSUE**: 21 files (14%) have null EEAT data  
**GOOD EXAMPLE** (from Alabaster):

```yaml
eeat:
  reviewedBy: Z-Beam Quality Assurance Team
  citations:
    - IEC 60825 - Safety of Laser Products
    - OSHA 29 CFR 1926.95 - Personal Protective Equipment
    - FDA 21 CFR 1040.10 - Laser Product Performance
  isBasedOn:
    name: IEC 60825 - Safety of Laser Products
    url: https://webstore.iec.ch/publication/3587
```

**ALTERNATIVE STRUCTURE** (more detailed):

```yaml
eeat:
  experience_indicators:
    hands_on_projects: [number or description]
    years_in_field: [number]
    practical_applications: [list of applications]
  expertise_indicators:
    technical_depth: [high|medium]
    specialization_areas:
      - [Area 1]
      - [Area 2]
    credentials_mentioned: true
  authoritativeness_indicators:
    institutional_affiliation: true
    professional_credentials: [list]
    publication_record: [description if applicable]
  trustworthiness_indicators:
    factual_accuracy: true
    cited_sources: true
    balanced_perspective: true
    limitations_acknowledged: [true if applicable]
```

### **15. Material Metadata** (MUST NOT BE NULL)

**🚨 DISCOVERED ISSUE**: 21 files (14%) have null material_metadata  
**GOOD EXAMPLE** (from Alabaster):

```yaml
material_metadata:
  last_updated: '2025-10-27T23:48:40.921556Z'
  normalization_applied: true
  normalization_date: '2025-10-27T23:48:40.921587Z'
  structure_version: '2.0'
```

**COMPREHENSIVE STRUCTURE** (recommended):

```yaml
material_metadata:
  completeness_score: 0.95  # 0.0-1.0 based on filled fields
  last_updated: '2025-12-16T00:00:00Z'
  last_verified: '2025-12-16T00:00:00Z'
  normalization_applied: true
  normalization_date: '2025-12-16T00:00:00Z'
  structure_version: '4.0.0'  # Match schema_version
  content_quality:
    technical_depth: high
    practical_utility: high
    seo_optimized: true
  relevance_scores:
    industrial_applications: 0.9
    research_applications: 0.7
    consumer_applications: 0.5
```

### **16. Preserved Data** (MANDATORY)

```yaml
preservedData:
  generationMetadata:
    generated_date: '[ISO 8601 timestamp]'
    generation_context: [brief description]
    quality_checks_passed: true
```

---

## � DISCOVERED ISSUES FROM EXISTING FILES (Dec 2025)

### **Analysis of 153 Material Files**

**Last Generated**: December 15, 2025 (all files)  
**Schema Version**: 4.0.0 ✅  
**Overall Grade**: B (82/100)

#### **Critical Issues (Must Fix)**

| Issue | Affected Files | Impact | Priority |
|-------|----------------|--------|----------|
| **Null datePublished** | 153/153 (100%) | SEO rankings blocked | 🔴 Critical |
| **Null dateModified** | 153/153 (100%) | Change tracking missing | 🔴 Critical |
| **Null eeat** | 21/153 (14%) | E-E-A-T signals missing | 🟡 High |
| **Null material_metadata** | 21/153 (14%) | Completeness tracking absent | 🟡 High |
| **Truncated FAQ answers** | ~3 files | Incomplete content | 🟡 High |

#### **Quality Highlights** ✅

- ✅ **Material Properties**: 100% complete with research citations
- ✅ **FAQ Content**: Most files have 3-9 FAQs (good depth)
- ✅ **Regulatory Standards**: 2-4 standards per file
- ✅ **Domain Linkages**: 4+ related contaminants
- ✅ **Schema Compliance**: All files use schema 4.0.0
- ✅ **Content Quality**: Descriptions, micro content within target ranges

#### **Examples of Excellence**

**Iron (iron-laser-cleaning.yaml)**:
- ✅ 9 comprehensive FAQ items
- ✅ Technical depth with specific parameters
- ✅ Complete micro before/after descriptions
- ✅ 4 regulatory standards
- ⚠️ Missing: dates, some metadata
- **Grade**: 88% (B+)

**Alabaster (alabaster-laser-cleaning.yaml)**:
- ✅ Complete EEAT structure
- ✅ Material metadata present
- ✅ Citations and isBasedOn fields
- ⚠️ Missing: dates (assumed)
- **Grade**: 85-90% (B+/A-)

#### **Immediate Actions Required**

1. **Add ISO 8601 timestamps** to all datePublished/dateModified fields
2. **Populate EEAT data** for 21 files missing it
3. **Add material_metadata** for 21 files missing it
4. **Complete truncated FAQs** (Aluminum Bronze, possibly others)
5. **Verify no mid-sentence endings** across all FAQ answers

#### **Success Metrics**

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Date fields populated | 0% | 100% | ❌ |
| EEAT data present | 86% | 100% | 🟡 |
| Material metadata | 86% | 100% | 🟡 |
| Content completeness | 98% | 100% | 🟢 |
| Schema compliance | 100% | 100% | ✅ |

---

## �🚫 Common Issues to Avoid

### **Issue #1: Null Date Fields**
```yaml
# ❌ WRONG
datePublished: null
dateModified: null

# ✅ CORRECT
datePublished: '2025-12-16T00:00:00Z'
dateModified: '2025-12-16T00:00:00Z'
```

### **Issue #2: Truncated FAQ Answers**
```yaml
# ❌ WRONG (incomplete answer)
answer: Laser cleaning acrylic demands careful control since its clear nature can fog from uneven heating. Compared to opaque thermoplastics, PMMA reveals contaminants easily but risks haze if pulses are too intense.

# ✅ CORRECT (complete answer)
answer: Laser cleaning acrylic demands careful control since its clear nature can fog from uneven heating. Compared to opaque thermoplastics, PMMA reveals contaminants easily but risks haze if pulses are too intense. I've found that gradual power ramping prevents this issue, letting you restore optical clarity without compromising the surface finish for applications like lenses and display panels.
```

### **Issue #3: Null EEAT/Metadata Fields**
```yaml
# ❌ WRONG
eeat: null
material_metadata: null

# ✅ CORRECT - Always populate these fields
```

### **Issue #4: Incomplete Property Research**
```yaml
# ❌ WRONG - Missing citation details
laserDamageThreshold:
  value: 1.8
  unit: J/cm²

# ✅ CORRECT - Full research metadata
laserDamageThreshold:
  value: 1.8
  unit: J/cm²
  source: scientific_literature
  source_type: journal_article
  source_name: 'Applied Physics A: Materials Science & Processing'
  citation: 'B. W. Smith et al., Applied Physics A 79, 1023-1026 (2004)'
  context: Commercial-grade clear PMMA (99% purity), 25°C, 532 nm Nd:YAG laser
  researched_date: '2025-11-24T12:30:31.076360'
  needs_validation: true
  min: 0.71
  max: 2.6
```

---

## 📊 Quality Standards

### **Content Quality Requirements**

| Section | Min Words | Max Words | Quality Check |
|---------|-----------|-----------|---------------|
| material_description | 30 | 50 | Technical + practical benefits |
| micro.before | 60 | 80 | Vivid sensory description |
| micro.after | 60 | 80 | Clear contrast with before |
| FAQ answer | 100 | 150 | Complete, practical, experienced |
| FAQ count | 3+ | No limit | More for complex materials |

### **Completeness Requirements**

- ✅ **100%** of material properties must have values
- ✅ **100%** of laser interaction properties must have research metadata
- ✅ **4-6** related contaminants with complete metadata
- ✅ **3+ FAQ items** (more for complex materials - Iron has 9!)
- ✅ **2+** regulatory standards (most files have 2-4)
- ✅ **0** null fields in critical sections (datePublished, dateModified, eeat, material_metadata)

**🚨 CRITICAL**: Current files fail on date fields (100% null rate) and partial metadata (14% null rate)

### **SEO Requirements**

- ✅ Title follows pattern: "[Material Name] Laser Cleaning"
- ✅ All image alt text is descriptive and unique
- ✅ Breadcrumb navigation is complete and accurate
- ✅ URLs are properly formatted and consistent
- ✅ Meta descriptions are concise and keyword-rich

---

## 🎯 Example: High-Quality Frontmatter

See `/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter/materials/acrylic-pmma-laser-cleaning.yaml` for a reference implementation that scores **93%** quality (with only minor date/metadata issues).

**Strengths to Emulate**:
- ✅ 100% complete material properties with scientific citations
- ✅ Rich, vivid micro before/after descriptions
- ✅ Well-structured FAQ with practical guidance
- ✅ Complete domain linkages with 4 related contaminants
- ✅ Comprehensive author metadata
- ✅ Strong service offering details

---

## 🔧 Pre-Generation Checklist

Before generating frontmatter:

- [ ] Verify material name, category, and subcategory
- [ ] Confirm author assignment (ID 1-4)
- [ ] **🔥 Generate ISO 8601 timestamps for dates** (CRITICAL - currently 100% missing)
- [ ] Research all 21 material properties with citations
- [ ] Identify 4-6 relevant contaminants
- [ ] Draft complete FAQ answers (no truncation, 100-150 words each)
- [ ] **🔥 Populate EEAT data** (14% of files missing this)
- [ ] **🔥 Calculate and add material_metadata** (14% of files missing this)
- [ ] Validate all URLs and image paths
- [ ] Ensure no null fields in critical sections
- [ ] **Verify FAQ answers are complete** (check for mid-sentence endings)
- [ ] Test with one file before batch generation

---

## 🎓 After Generation

1. **Validate Structure**: Ensure YAML is valid and properly indented
2. **Check Completeness**: All required fields present and non-null
3. **Verify Quality**: Word counts, descriptions meet standards
4. **Test URLs**: All href/url values are valid paths
5. **Review Content**: Technical accuracy and readability
6. **Grade Result**: Aim for 95%+ quality score

---

## 📞 Questions?

When uncertain about:
- **Author selection**: Choose based on material expertise
- **Property values**: Research from scientific literature
- **Contaminant linkages**: Consider real-world cleaning scenarios
- **Quality standards**: Default to higher quality and completeness

**Target**: Every frontmatter file should be production-ready at 95%+ quality.
