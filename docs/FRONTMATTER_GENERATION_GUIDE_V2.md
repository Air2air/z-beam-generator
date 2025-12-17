# Frontmatter Generation Guide for AI Assistants

**Version**: 2.0  
**Last Updated**: December 16, 2025  
**For**: AI assistants generating frontmatter files across all domains

---

## 🎯 Purpose

This guide ensures all generated frontmatter files meet Z-Beam's quality, completeness, and SEO standards. Follow these requirements precisely when generating or updating frontmatter YAML files across **4 domains**: Materials, Contaminants, Settings, and Compounds.

---

## 📁 Frontmatter Domains Overview

Z-Beam uses **4 frontmatter domains** with 424 total files:

| Domain | Files | Purpose | Schema | Status |
|--------|-------|---------|--------|--------|
| **Materials** | 153 | Material laser cleaning data | 4.0.0 | ⚠️ Needs dates + metadata |
| **Contaminants** | 98 | Contamination types & cleaning | 4.0.0 | ⚠️ Needs dates |
| **Settings** | 153 | Laser parameter settings | 4.0.0 | ⚠️ Needs dates |
| **Compounds** | 20 | Chemical compound data | N/A | ✅ **Reference model** |

### 🎯 Domain-Specific Content Types

```yaml
# Materials domain
content_type: unified_material

# Contaminants domain
content_type: unified_contamination

# Settings domain
content_type: unified_settings

# Compounds domain
# (No content_type field - uses simpler structure)
```

---

## 🚨 Critical Cross-Domain Issue: Null Dates

**404 of 424 files** (95%) have null date fields:

- ✅ **Compounds**: 0/20 null dates (0%) - **USE AS REFERENCE MODEL**
- ❌ **Contaminants**: 98/98 null dates (100%)
- ❌ **Materials**: 153/153 null dates (100%)
- ❌ **Settings**: 153/153 null dates (100%)

**ACTION REQUIRED**: The compounds generator successfully creates valid ISO 8601 timestamps. Apply the same date generation logic to the other 3 domains.

---

## 🔍 DISCOVERED ISSUES FROM EXISTING FILES (Dec 2025)

### **Cross-Domain Analysis: 424 Total Files**

**Last Generated**: December 15, 2025 (all domains)

| Domain | Files | Date Status | EEAT Status | Metadata Status | Overall Grade |
|--------|-------|-------------|-------------|-----------------|---------------|
| **Compounds** | 20 | ✅ Valid (0%) | N/A | N/A | **A (100%)** ✅ |
| **Materials** | 153 | ❌ 100% null | ❌ 14% null | ❌ 14% null | **B (82%)** |
| **Contaminants** | 98 | ❌ 100% null | 🟡 10% have | N/A | **C+ (75%)** |
| **Settings** | 153 | ❌ 100% null | N/A | N/A | **C+ (78%)** |

#### **Critical Issues Summary**

| Issue | Materials | Contaminants | Settings | Compounds | Total Affected |
|-------|-----------|--------------|----------|-----------|----------------|
| **Null datePublished** | 153 | 98 | 153 | **0** ✅ | **404/424** (95%) 🔴 |
| **Null dateModified** | 153 | 98 | 153 | **0** ✅ | **404/424** (95%) 🔴 |
| **Null EEAT** | 21 | 88 | N/A | N/A | **109/251** (43%) 🟡 |
| **Null material_metadata** | 21 | N/A | N/A | N/A | **21/153** (14%) 🟡 |
| **Truncated FAQ** | ~3 | Unknown | N/A | N/A | **~3** 🟡 |

### **Compounds Domain** (20 files) ✅ **Reference Model**

**Overall Grade**: A (100/100) ✅

**✅ SUCCESS FACTORS**:
- ✅ **Valid datePublished**: 0/20 null (0%)
- ✅ **Valid dateModified**: 0/20 null (0%)
- ✅ Complete chemical data: CAS numbers, molecular weights
- ✅ Exposure limits properly structured
- ✅ Health effects documented

**Why This Works**:
The compounds generator correctly implements ISO 8601 timestamp generation. Study this generator's date handling logic and apply to the other 3 domains.

**Unique Fields**:
- CAS numbers, molecular weights, chemical formulas
- Exposure limits (OSHA, NIOSH, ACGIH)
- Health effects and hazard classifications
- No schema_version or content_type fields (simplified structure)

### **Materials Domain** (153 files)

**Overall Grade**: B (82/100)

**Critical Issues**:
- ❌ **Null datePublished**: 153/153 (100%)
- ❌ **Null dateModified**: 153/153 (100%)
- ❌ **Null eeat**: 21/153 (14%)
- ❌ **Null material_metadata**: 21/153 (14%)
- ❌ **Truncated FAQ answers**: ~3 files

**Quality Highlights** ✅:
- ✅ Material Properties: 100% complete with research citations
- ✅ FAQ Content: Most files have 3-9 FAQs (good depth)
- ✅ Regulatory Standards: 2-4 standards per file
- ✅ Domain Linkages: 4+ related contaminants
- ✅ Schema Compliance: All files use schema 4.0.0

**Examples of Excellence**:
- **Iron** (iron-laser-cleaning.yaml): 9 comprehensive FAQs, 88% grade
- **Alabaster** (alabaster-laser-cleaning.yaml): Complete EEAT, 85-90% grade

### **Contaminants Domain** (98 files)

**Overall Grade**: C+ (75/100)

**Critical Issues**:
- ❌ **Null datePublished**: 98/98 (100%)
- ❌ **Null dateModified**: 98/98 (100%)
- 🟡 **EEAT data**: Only 10/98 files (10%) have it

**Unique Fields**:
- Contamination categories: organic-residue, corrosion, oxide-layer
- Author: Primarily Yi-Chun Lin (Taiwan)
- Content structure similar to materials but contamination-focused

**Action Required**:
1. Add ISO 8601 timestamps to all 98 files
2. Consider adding EEAT to remaining 88 files (10% currently have it)

### **Settings Domain** (153 files)

**Overall Grade**: C+ (78/100)

**Critical Issues**:
- ❌ **Null datePublished**: 153/153 (100%)
- ❌ **Null dateModified**: 153/153 (100%)

**Note**: No EEAT or material_metadata fields (settings-specific schema)

**Unique Fields**:
- Laser parameter specifications
- Power ranges, wavelengths, pulse durations
- Safety thresholds
- 1:1 relationship with materials domain

**Action Required**:
1. Add ISO 8601 timestamps to all 153 files

---

## ✅ Required Fields by Domain

### 🎯 Domain Selection

First, identify which domain you're generating for:
- **Materials**: Laser cleaning of materials (metals, plastics, ceramics, etc.)
- **Contaminants**: Types of contamination and their removal
- **Settings**: Laser parameter configurations per material
- **Compounds**: Chemical compounds encountered in cleaning

---

## 📋 Schema Version & Structure by Domain

### **Materials Domain** (153 files)

**Required Schema Version**: `4.0.0`

```yaml
schema_version: 4.0.0
content_type: unified_material
```

**Unique Requirements**:
- Full EEAT data structure
- Material metadata with completeness scores
- 21 material properties + 9 laser interaction properties
- Related contaminants linkages

### **Contaminants Domain** (98 files)

**Required Schema Version**: `4.0.0`

```yaml
schema_version: 4.0.0
content_type: unified_contamination
```

**Unique Requirements**:
- EEAT data (10 files currently have it)
- Contamination categories: organic-residue, corrosion, oxide-layer, etc.
- Related materials linkages
- Cleaning difficulty ratings

### **Settings Domain** (153 files)

**Required Schema Version**: `4.0.0`

```yaml
schema_version: 4.0.0
content_type: unified_settings
active: true
```

**Unique Requirements**:
- Laser parameter specifications
- Power ranges, wavelengths, pulse durations
- Safety thresholds
- Material-specific adjustments
- No EEAT or material_metadata (settings-specific schema)

### **Compounds Domain** (20 files) ✅ **Reference Model**

**No schema version field**

```yaml
id: [compound-name]-compound
name: [Compound Name]
chemical_formula: [Formula]
cas_number: [CAS#]
```

**✅ SUCCESS MODEL**: This domain correctly generates ISO 8601 timestamps for all files. Study its date generation logic.

**Unique Requirements**:
- CAS numbers, molecular weights
- Exposure limits (OSHA, NIOSH, ACGIH)
- Health effects and hazard classifications
- No content_type or schema_version fields

---

## 📝 Universal Required Fields (All Domains)

### **1. Basic Metadata** (MANDATORY)

**Materials Domain**:
```yaml
name: [Material Name]
slug: [kebab-case-slug]
id: [material-slug-laser-cleaning]
category: [metal|plastic|ceramic|composite|wood|other]
subcategory: [specific type]
content_type: unified_material
schema_version: 4.0.0
```

**Contaminants Domain**:
```yaml
name: [Contaminant Name]
slug: [kebab-case-slug]
id: [contaminant-slug-contamination]
category: [organic-residue|corrosion|oxide-layer|coating|biological|other]
subcategory: [specific type]
content_type: unified_contamination
schema_version: 4.0.0
```

**Settings Domain**:
```yaml
name: [Material Name]
slug: [kebab-case-slug]
id: [material-slug-settings]
category: [metal|plastic|ceramic|composite|wood|other]
subcategory: [specific type]
content_type: unified_settings
schema_version: 4.0.0
active: true
```

**Compounds Domain** (simplified):
```yaml
id: [compound-name]-compound
name: [Compound Name]
display_name: [Name with Formula Subscripts]
slug: [kebab-case-slug]
chemical_formula: [Formula]
cas_number: [CAS Number]
molecular_weight: [g/mol]
category: [irritant|toxic|hazardous_gas|other]
subcategory: [specific type]
hazard_class: [classification]
```

### **2. Publication Dates** (MUST NOT BE NULL) 🔥 **CRITICAL - ALL DOMAINS**

```yaml
datePublished: '2025-12-16T00:00:00Z'  # ISO 8601 format - REQUIRED
dateModified: '2025-12-16T00:00:00Z'   # ISO 8601 format - REQUIRED
```

**✅ CORRECT**: Use generation date or current date  
**❌ WRONG**: `datePublished: null` or `dateModified: null`

**🚨 DISCOVERED ISSUE - AFFECTS 404 FILES**:
- Materials: 153/153 files (100%) have null dates
- Contaminants: 98/98 files (100%) have null dates
- Settings: 153/153 files (100%) have null dates
- **Compounds: 0/20 files (0%) have null dates** ✅ **USE AS MODEL**

**SEO IMPACT**: Blocks Google freshness signals, reduces ranking potential  
**FIX PRIORITY**: Critical - must be addressed before deployment  
**SOLUTION**: Study compounds domain date generation logic and apply to other domains

---

## 🔧 Domain-Specific Generation Guide

### **Materials Domain Generation**

See the original FRONTMATTER_GENERATION_GUIDE.md for complete materials requirements including:
- Author information (4 personas)
- Voice metadata
- Material properties (21 properties with research)
- Domain linkages (4-6 contaminants)
- FAQ section (minimum 3+ questions)
- EEAT data
- Material metadata

### **Contaminants Domain Generation**

**Key Fields**:
```yaml
removal_difficulty:
  rating: [easy|moderate|difficult|very_difficult]
  factors:
    - [Factor 1]
    - [Factor 2]

cleaning_parameters:
  recommended_wavelength: [nm]
  recommended_power: [W]
  pulse_duration_range: [range]

related_materials:
  - id: [material-slug]
    frequency: [common|occasional|rare]
    severity: [low|moderate|high|critical]
```

### **Settings Domain Generation**

**Key Fields**:
```yaml
laserSettings:
  wavelength:
    value: [number]
    unit: nm
    range: [min-max]
  
  power:
    value: [number]
    unit: W
    min: [number]
    max: [number]
  
  pulse_duration:
    value: [number]
    unit: [ns|ps|fs]
  
  safety_limits:
    max_power: [W]
    max_fluence: [J/cm²]
```

### **Compounds Domain Generation** ✅ **Reference Model**

**Key Fields**:
```yaml
chemical_formula: C2H4O
cas_number: 75-07-0
molecular_weight: 44.05

exposure_limits:
  osha_pel_ppm: 200
  osha_pel_mg_m3: 360
  acgih_tlv_ppm: 25
  acgih_tlv_mg_m3: 45

health_effects_keywords:
  - respiratory_irritation
  - eye_irritation
  
monitoring_required: true
typical_concentration_range: 5-25 mg/m³
```

---

## 🎯 Immediate Action Required

### **Priority 1: Fix Null Dates (404 files)**

1. **Study Compounds Generator**: Identify how it generates valid ISO 8601 timestamps
2. **Apply to Materials**: Add timestamp generation to materials generator
3. **Apply to Contaminants**: Add timestamp generation to contaminants generator
4. **Apply to Settings**: Add timestamp generation to settings generator

### **Priority 2: Add EEAT Data**

- **Materials**: 21 files missing (14%)
- **Contaminants**: 88 files missing (90%)

### **Priority 3: Add Material Metadata**

- **Materials**: 21 files missing (14%)

---

## 📊 Success Metrics

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| Date fields populated | 5% (20/424) | 100% | 🔴 Critical |
| EEAT data (materials) | 86% | 100% | 🟡 High |
| EEAT data (contaminants) | 10% | 50%+ | 🟢 Medium |
| Material metadata | 86% | 100% | 🟡 High |

---

## 🏆 Target Quality Standards

**Target**: Every frontmatter file should be production-ready at 95%+ quality across all domains.

**Model for Success**: Compounds domain (100% grade) - use as reference for date generation logic.
