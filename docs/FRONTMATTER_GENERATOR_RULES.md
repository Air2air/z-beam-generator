# Frontmatter Generator Rules & Standards

**Last Updated**: December 15, 2025  
**Status**: Production Requirements  
**Applies To**: Material, Contaminant, and Settings frontmatter generation

---

## 🚨 **CRITICAL: Content Type Field Rules**

### **✅ CORRECT Structure**

Top-level content_type field ONLY:

```yaml
# Materials
content_type: unified_material
schema_version: 4.0.0
name: Aluminum
# ... rest of frontmatter

# Contaminants
content_type: unified_contamination
schema_version: 4.0.0
name: Rust
# ... rest of frontmatter

# Settings
content_type: unified_settings
schema_version: 4.0.0
name: Aluminum
# ... rest of frontmatter
```

### **❌ INCORRECT: Do NOT Duplicate in Micro Section**

**NEVER include content_type inside micro, author, or any nested section:**

```yaml
# ❌ WRONG - Do not do this
micro:
  content_type: material      # DELETE THIS
  before: "..."
  after: "..."

# ❌ WRONG - Do not do this
author:
  content_type: material      # DELETE THIS
  author_name: "..."
```

### **Why This Matters**

- **Redundancy**: Top-level `content_type: unified_*` already identifies the content type
- **Legacy Cleanup**: We removed 251 duplicate fields (153 materials + 98 contaminants) on Dec 15, 2025
- **Clean Architecture**: Nested sections should NOT repeat parent-level metadata

---

## 📋 **Micro Field Population Standards**

### **Required Fields**

Every frontmatter file MUST have a `micro` section with:

```yaml
micro:
  before: "Description of material/contaminant BEFORE laser cleaning"
  after: "Description of material/contaminant AFTER laser cleaning"
```

### **Micro Content Quality Requirements**

#### **1. Content Must Be Present**
- ❌ **Empty strings**: `before: ""`
- ❌ **Placeholder text**: `before: "Description pending"`
- ❌ **Duplicate text**: `before` and `after` should be different
- ✅ **Actual content**: Meaningful descriptions of the transformation

#### **2. Before/After Descriptions Should Be Specific**

**✅ GOOD Examples:**

```yaml
# Material Example (Aluminum)
micro:
  before: "Oxidized aluminum surface showing dull gray-white aluminum oxide layer with scattered contamination, diminishing natural metallic luster and creating uneven surface appearance"
  after: "Clean aluminum surface revealing natural silver-white metallic sheen with uniform reflectivity, restored structural surface revealing original grain boundaries and machining marks"

# Contaminant Example (Rust)
micro:
  before: "Ferrous metal surface exhibiting reddish-brown iron oxide accumulation with flaking layers, showing progressive corrosion patterns and compromised substrate integrity beneath oxidation zones"
  after: "Restored metal surface displaying clean substrate with removed oxidation products, revealing original metallic characteristics and arrest of further corrosion propagation through oxide layer removal"
```

**❌ BAD Examples:**

```yaml
# Too generic
micro:
  before: "Contaminated surface"
  after: "Clean surface"

# Too short/placeholder
micro:
  before: "Needs content"
  after: "TBD"

# Identical text
micro:
  before: "Surface with contamination"
  after: "Surface with contamination"
```

#### **3. Length Guidelines**

- **Minimum**: 50 words per field (before/after combined ~100 words)
- **Maximum**: 150 words per field (before/after combined ~300 words)
- **Optimal**: 75-100 words per field (before/after combined ~150-200 words)

#### **4. Technical Accuracy**

- Use correct material science terminology
- Reference actual laser cleaning effects
- Mention specific visual/structural changes
- Include measurable outcomes when applicable

---

## 🏗️ **Complete Frontmatter Structure**

### **Materials Frontmatter Template**

```yaml
content_type: unified_material
schema_version: 4.0.0
active: true
slug: material-name-laser-cleaning
name: Material Name
category: category-name
subcategory: subcategory-name
title: Material Name Laser Cleaning
description: "One-sentence description focusing on laser cleaning advantages (50-150 words)"

author:
  persona_file: usa_persona.yaml
  formatting_file: usa_formatting.yaml

_metadata:
  voice:
    author_name: Todd Dunning
    author_country: United States
    voice_applied: true

micro:
  before: "Description of material BEFORE laser cleaning (75-100 words)"
  after: "Description of material AFTER laser cleaning (75-100 words)"

breadcrumb:
- label: Home
  href: /
- label: Materials
  href: /materials
- label: Category
  href: /materials/category
- label: Subcategory
  href: /materials/category/subcategory
- label: Material Name
  href: /materials/category/subcategory/material-name

images:
  hero:
    alt: "Material Name surface during precision laser cleaning process"
    url: /images/material/material-name-laser-cleaning-hero.jpg
  micro:
    alt: "Material Name surface at 500x magnification showing laser cleaning results"
    url: /images/material/material-name-micro.jpg

# ... rest of material-specific fields (properties, machine_settings, etc.)
```

### **Contaminants Frontmatter Template**

```yaml
content_type: unified_contamination
schema_version: 4.0.0
active: true
slug: contaminant-name-contamination
name: Contaminant Name
category: category-name
subcategory: subcategory-name
title: Contaminant Name Contamination
description: "One-sentence description of contamination challenge (50-150 words)"

author:
  persona_file: usa_persona.yaml
  formatting_file: usa_formatting.yaml

_metadata:
  voice:
    author_name: Todd Dunning
    author_country: United States
    voice_applied: true

micro:
  before: "Description of contaminated surface BEFORE laser cleaning (75-100 words)"
  after: "Description of surface AFTER contaminant removal (75-100 words)"

breadcrumb:
- label: Home
  href: /
- label: Contaminants
  href: /contaminants
- label: Category
  href: /contaminants/category
- label: Subcategory
  href: /contaminants/category/subcategory
- label: Contaminant Name
  href: /contaminants/category/subcategory/contaminant-name

images:
  hero:
    alt: "Contaminant Name contamination during laser cleaning removal process"
    url: /images/contaminant/contaminant-name-contamination-hero.jpg
  micro:
    alt: "Contaminant Name at 500x magnification showing removal effectiveness"
    url: /images/contaminant/contaminant-name-micro.jpg

# ... rest of contaminant-specific fields (hazards, removal techniques, etc.)
```

### **Settings Frontmatter Template**

```yaml
content_type: unified_settings
schema_version: 4.0.0
active: true
slug: material-name-settings
name: Material Name
materialRef: material-name-laser-cleaning.yaml
category: category-name
subcategory: subcategory-name
title: Material Name Laser Cleaning Settings
subtitle: "Precision Parameters for [Material Category] Processing"
description: "Optimized laser cleaning parameters for Material Name"
settings_description: "One-sentence technical overview (50-100 words)"

author:
  persona_file: usa_persona.yaml
  formatting_file: usa_formatting.yaml

_metadata:
  voice:
    author_name: Todd Dunning
    author_country: United States
    voice_applied: true
  structure_version: "2.0"
  optimization_applied: true

# NO MICRO FIELD - Settings pages don't need before/after micro descriptions

breadcrumb:
- label: Home
  href: /
- label: Settings
  href: /settings
- label: Category
  href: /settings/category
- label: Subcategory
  href: /settings/category/subcategory
- label: Material Name Settings
  href: /settings/category/subcategory/material-name-settings

images:
  hero:
    alt: "Material Name laser cleaning parameter visualization"
    url: /images/settings/material-name-settings-hero.jpg

# ... rest of settings-specific fields (machine_settings, parameter_relationships, etc.)
```

---

## 🔍 **Validation Checklist**

Before generating frontmatter, verify:

### **Structure Validation**
- [ ] `content_type` exists ONLY at top level
- [ ] `content_type` value is correct: `unified_material`, `unified_contamination`, or `unified_settings`
- [ ] `schema_version: 4.0.0` is present
- [ ] NO `content_type` field in `micro`, `author`, or any nested sections

### **Micro Field Validation** (Materials & Contaminants Only)
- [ ] `micro` section exists
- [ ] `micro.before` has meaningful content (not empty/placeholder)
- [ ] `micro.after` has meaningful content (not empty/placeholder)
- [ ] `before` and `after` are different
- [ ] Each field is 75-100 words (50-150 acceptable range)
- [ ] Content is technically accurate and specific
- [ ] Language is professional and descriptive

### **Settings Validation** (Settings Pages Only)
- [ ] NO `micro` field (settings don't need before/after descriptions)
- [ ] `materialRef` field points to corresponding material YAML file
- [ ] `machine_settings` or `components.parameter_relationships` exists

---

## 📊 **Quality Standards Summary**

| Field | Requirement | Materials | Contaminants | Settings |
|-------|-------------|-----------|--------------|----------|
| `content_type` (top-level) | Required | ✅ `unified_material` | ✅ `unified_contamination` | ✅ `unified_settings` |
| `content_type` (nested) | Forbidden | ❌ Never | ❌ Never | ❌ Never |
| `micro.before` | Required | ✅ Yes | ✅ Yes | ❌ No |
| `micro.after` | Required | ✅ Yes | ✅ Yes | ❌ No |
| Micro word count | 75-100 words/field | ✅ Yes | ✅ Yes | N/A |
| `materialRef` | Optional | ❌ No | ❌ No | ✅ Yes |

---

## 🚀 **Generator Implementation Notes**

### **What Changed (December 15, 2025)**

We cleaned up **251 duplicate content_type fields** across the codebase:
- **153 materials**: Removed `content_type: material` from micro sections
- **98 contaminants**: Removed `content_type: contaminant` from micro sections

### **Cleanup Script Reference**

If you need to clean up existing files:
```bash
# Remove duplicate content_type from materials
find frontmatter/materials -name "*.yaml" -exec sed -i '' '/^[[:space:]]*content_type: material$/d' {} \;

# Remove duplicate content_type from contaminants
find frontmatter/contaminants -name "*.yaml" -exec sed -i '' '/^[[:space:]]*content_type: contaminant$/d' {} \;
```

See: `scripts/cleanup-duplicate-content-type.sh`

### **Validation Commands**

Check for violations:
```bash
# Check materials for duplicates
grep -r "content_type: material" frontmatter/materials/*.yaml | grep -v "unified_material"

# Check contaminants for duplicates
grep -r "content_type: contaminant" frontmatter/contaminants/*.yaml | grep -v "unified_contamination"

# Both should return 0 results
```

---

## 📝 **Common Mistakes to Avoid**

### **Mistake 1: Nesting content_type**
```yaml
# ❌ WRONG
micro:
  content_type: material  # DELETE THIS LINE
  before: "..."
```

### **Mistake 2: Empty micro fields**
```yaml
# ❌ WRONG
micro:
  before: ""
  after: ""
```

### **Mistake 3: Generic descriptions**
```yaml
# ❌ WRONG
micro:
  before: "Dirty surface"
  after: "Clean surface"
```

### **Mistake 4: Settings with micro fields**
```yaml
# ❌ WRONG - Settings don't need micro fields
content_type: unified_settings
micro:
  before: "..."  # DELETE THIS SECTION
  after: "..."
```

---

## ✅ **Success Criteria**

Your generated frontmatter passes if:

1. ✅ `content_type` appears ONLY at top level
2. ✅ `content_type` value matches content type: `unified_material`, `unified_contamination`, or `unified_settings`
3. ✅ Materials/Contaminants have complete `micro` section with meaningful content
4. ✅ Settings do NOT have `micro` section
5. ✅ All micro descriptions are 75-100 words and technically accurate
6. ✅ No placeholder text like "TBD", "pending", or empty strings

---

## 📚 **Reference Documents**

- **Architecture**: `docs/02-architecture/`
- **Data Standards**: `docs/05-data/DATA_STORAGE_POLICY.md`
- **Cleanup Script**: `scripts/cleanup-duplicate-content-type.sh`
- **Commit Reference**: `4effb407a` (Dec 15, 2025)

---

## 🎯 **Quick Reference: Do's and Don'ts**

| ✅ DO | ❌ DON'T |
|-------|----------|
| Put `content_type` at top level | Nest `content_type` in micro/author sections |
| Use `unified_material`, `unified_contamination`, `unified_settings` | Use legacy values like `material`, `contaminant` |
| Populate micro.before and micro.after with 75-100 words | Leave micro fields empty or with placeholders |
| Make before/after descriptions different and specific | Copy-paste same text for before and after |
| Include micro for materials and contaminants | Include micro for settings pages |
| Use technical, accurate terminology | Use generic or marketing language |

---

**End of Document**
