# Backend Frontmatter Field Naming Specification

**Version:** 5.0.0  
**Last Updated:** December 26, 2025  
**Purpose:** Eliminate frontend mapping requirements by using exact field names

---

## 📋 Required Field Names (No Mapping Needed)

### Core Metadata Fields

```yaml
id: string                          # Unique identifier (slug format)
name: string                        # Display name (e.g., "Aluminum")
title: string                       # SEO title (e.g., "Aluminum Laser Cleaning")
page_description: string            # ⚠️ MUST be 'page_description' NOT 'description'
category: string                    # Primary category
subcategory: string                 # Secondary category (optional)
content_type: string                # 'materials' | 'contaminants' | 'compounds' | 'settings'
schema_version: string              # e.g., "5.0.0"
slug: string                        # URL slug (often same as id)
full_path: string                   # Complete URL path
```

### Dates

```yaml
datePublished: string               # ISO 8601 format: '2025-12-26T19:59:22.743729Z'
dateModified: string                # ISO 8601 format: '2025-12-26T19:59:22.743729Z'
```

**Important:** Always include timezone in ISO 8601 format.

---

## 🖼️ Images Structure (Nested Object)

⚠️ **CRITICAL:** Must be a nested object structure, not a flat string.

```yaml
images:
  hero:
    url: string                     # Path to hero image
    alt: string                     # Alt text for accessibility
    width: number                   # Optional: image width in pixels
    height: number                  # Optional: image height in pixels
  micro:
    url: string                     # Path to micro/detail image
    alt: string                     # Alt text
    width: number                   # Optional
    height: number                  # Optional
  social:                           # Optional: social share image
    url: string
    alt: string
```

**Example:**
```yaml
images:
  hero:
    url: /images/material/aluminum-hero.jpg
    alt: Aluminum surface during laser cleaning process
    width: 1200
    height: 630
  micro:
    url: /images/material/aluminum-micro.jpg
    alt: Microscopic view of cleaned aluminum surface
```

---

## 👤 Author Structure (Nested Object)

⚠️ **CRITICAL:** Author must be an object, never a string.

```yaml
author:
  id: number                        # Author ID (numeric)
  name: string                      # Full name
  country: string                   # Country code (e.g., "Taiwan", "United States")
  country_display: string           # Display name for country
  title: string                     # Academic/professional degree (Ph.D., MA, etc.)
  sex: string                       # 'm' | 'f'
  jobTitle: string                  # Professional title
  email: string                     # Contact email
  expertise: string[]               # Array of expertise areas
  credentials: string[]             # Array of credentials/qualifications
  affiliation:
    name: string                    # Institution/company name
    type: string                    # Schema.org type ("EducationalOrganization", etc.)
  image: string                     # Optional: path to author photo
  imageAlt: string                  # Optional: alt text for author photo
  url: string                       # Optional: author profile URL
  persona_file: string              # Optional: persona configuration file
  formatting_file: string           # Optional: formatting configuration file
  sameAs: string[]                  # Optional: social media profile URLs
```

**Example:**
```yaml
author:
  id: 1
  name: Yi-Chun Lin
  country: Taiwan
  country_display: Taiwan
  title: Ph.D.
  sex: f
  jobTitle: Laser Processing Engineer
  email: info@z-beam.com
  expertise:
    - Laser Materials Processing
    - Surface Engineering
  credentials:
    - Ph.D. Materials Engineering, National Taiwan University, 2018
    - Post-Ph.D. fellowship at TSMC's laser fab lab, 2018-2020
  affiliation:
    name: National Taiwan University
    type: EducationalOrganization
  image: /images/author/yi-chun-lin.jpg
  imageAlt: Yi-Chun Lin, Ph.D., Laser Processing Engineer
  url: https://z-beam.com/authors/yi-chun-lin
```

---

## 📝 Micro Content Structure (Nested Object)

```yaml
micro:
  before: string                    # Before state description
  after: string                     # After state description
```

**Example:**
```yaml
micro:
  before: The surface shows heavy contamination with dark patches and scattered debris. Laser cleaning effectively strips away all foreign material while leaving the underlying stone completely intact.
  after: Now it reveals a uniform, clean texture with the material's natural gray color fully restored. This process removes buildup without any damage to the basalt itself.
```

---

## ❓ FAQ Array Structure

⚠️ **CRITICAL:** Must be an array of objects, not a single string or object.

```yaml
faq:
  - question: string                # Question text
    answer: string                  # Answer text
    topic_keyword: string           # Optional: main keyword
    topic_statement: string         # Optional: summary statement
  - question: string
    answer: string
    topic_keyword: string
    topic_statement: string
```

**Example:**
```yaml
faq:
  - question: How does laser cleaning restore the natural appearance of weathered basalt surfaces?
    answer: Laser cleaning employs precise energy pulses to eliminate dirt, grime, and oxidation layers from basalt without harming the stone itself. This non-abrasive approach restores the original dark luster and texture.
    topic_keyword: weathered basalt surfaces
    topic_statement: Revives dark luster and texture
  - question: Can laser cleaning address brittleness issues in basalt structures?
    answer: Yes, but indirectly. It cleans contaminants that exacerbate cracking, thus improving surface integrity. For inherent brittleness, combine with sealants post-cleaning to boost resistance.
    topic_keyword: brittleness issues
    topic_statement: Combine with post-cleaning sealants
```

---

## 🧭 Breadcrumb Navigation

```yaml
breadcrumb:
  - label: string                   # Display text
    href: string                    # URL path
  - label: string
    href: string
```

**Example:**
```yaml
breadcrumb:
  - label: Home
    href: /
  - label: Materials
    href: /materials
  - label: Stone
    href: /materials/stone
  - label: Igneous
    href: /materials/stone/igneous
  - label: Basalt
    href: /materials/stone/igneous/basalt-laser-cleaning
```

---

## 🔬 Material Properties Structure

```yaml
properties:
  material_characteristics:
    density:
      value: number                 # Numeric value
      unit: string                  # Unit of measurement (e.g., 'g/cm³')
      min: number                   # Optional: minimum value
      max: number                   # Optional: maximum value
    meltingPoint:
      value: number
      unit: string                  # e.g., '°C' or 'K'
      min: number
      max: number
    hardness:
      value: number
      unit: string                  # e.g., 'Mohs', 'GPa'
      min: number
      max: number
  laser_material_interaction:
    thermalConductivity:
      value: number
      unit: string                  # e.g., 'W/(m·K)'
      min: number
      max: number
    reflectivity:
      value: number
      unit: string                  # e.g., '%'
      min: number
      max: number
    absorptivity:
      value: number
      unit: string                  # e.g., '%'
      min: number
      max: number
```

**Example:**
```yaml
properties:
  material_characteristics:
    density:
      value: 2.7
      unit: g/cm³
      min: 0.5
      max: 23
    meltingPoint:
      value: 660
      unit: °C
      min: 100
      max: 3800
  laser_material_interaction:
    thermalConductivity:
      value: 237
      unit: W/(m·K)
      min: 7
      max: 430
    reflectivity:
      value: 88
      unit: '%'
      min: 10
      max: 95
```

---

## ⚙️ Machine Settings Structure (for Settings Pages)

```yaml
machineSettings:
  powerRange:
    value: number
    unit: string                    # 'W' (watts)
    min: number
    max: number
  wavelength:
    value: number
    unit: string                    # 'nm' (nanometers)
    min: number
    max: number
  spotSize:
    value: number
    unit: string                    # 'μm' (micrometers)
    min: number
    max: number
  repetitionRate:
    value: number
    unit: string                    # 'kHz' (kilohertz)
    min: number
    max: number
  pulseWidth:
    value: number
    unit: string                    # 'ns' (nanoseconds)
    min: number
    max: number
  scanSpeed:
    value: number
    unit: string                    # 'mm/s' (millimeters per second)
    min: number
    max: number
  passCount:
    value: number
    unit: string                    # 'passes'
    min: number
    max: number
  overlapRatio:
    value: number
    unit: string                    # '%' (percentage)
    min: number
    max: number
```

**Example:**
```yaml
machineSettings:
  powerRange:
    value: 200
    unit: W
    min: 100
    max: 300
  wavelength:
    value: 1064
    unit: nm
    min: 532
    max: 1064
  spotSize:
    value: 50
    unit: μm
    min: 25
    max: 100
  repetitionRate:
    value: 50
    unit: kHz
    min: 20
    max: 200
  pulseWidth:
    value: 100
    unit: ns
    min: 50
    max: 500
  scanSpeed:
    value: 1000
    unit: mm/s
    min: 100
    max: 5000
  passCount:
    value: 3
    unit: passes
    min: 1
    max: 10
  overlapRatio:
    value: 50
    unit: '%'
    min: 10
    max: 90
```

---

## 🔗 Relationships Structure

```yaml
relationships:
  technical:
    materials: string[]             # Array of related material IDs
    compounds: string[]             # Array of related compound IDs
    settings: string[]              # Array of related settings IDs
  operational:
    settings: string[]              # Operational settings
    processes: string[]             # Related processes
  safety:
    contaminants: string[]          # Related contaminant IDs
    precautions: string[]           # Safety precautions
```

**Example:**
```yaml
relationships:
  technical:
    materials:
      - aluminum-laser-cleaning
      - steel-laser-cleaning
    compounds:
      - aluminum-oxide
  operational:
    settings:
      - aluminum-settings
  safety:
    contaminants:
      - rust-contamination
      - oxide-layer
```

---

## ⚠️ Contamination Info Structure

```yaml
contamination:
  valid: string[]                   # Array of valid contaminant IDs
  prohibited: string[]              # Array of prohibited contaminant IDs
  conditional:                      # Array of conditional contaminations
    - contaminant_id: string
      condition: string
```

**Example:**
```yaml
contamination:
  valid:
    - rust-contamination
    - oxide-layer
    - paint-coating
  prohibited:
    - asbestos-contamination
    - lead-paint
  conditional:
    - contaminant_id: oil-contamination
      condition: Must pre-treat with solvent
```

---

## 📦 Components Structure (Generated Content)

```yaml
components:
  micro:                            # Optional micro content object
    before: string
    after: string
  settings_description: string      # Settings page description
  description: string               # Material description (different from page_description)
```

**Note:** This is separate from the top-level `micro` field and `page_description`.

---

## 🚫 DEPRECATED Fields (Do NOT Use)

```yaml
# ❌ WRONG - These fields have been removed or renamed
description: XXX                    # Use 'page_description' instead
subtitle: XXX                       # REMOVED - do not include
subject: XXX                        # Legacy field - do not use
```

---

## ⚡ Critical Rules

1. **`page_description` NOT `description`**
   - This is the #1 cause of mapping issues
   - Frontend expects `page_description` for page-level descriptions

2. **No `subtitle` field**
   - This field has been completely removed from the schema
   - Do not include it in any frontmatter files

3. **All nested objects must maintain structure**
   - Don't flatten nested objects into strings
   - Example: `author` must be an object, not `author: "John Doe"`

4. **Arrays must be arrays**
   - `faq: []` not `faq: {}`
   - `expertise: []` not `expertise: "skill1, skill2"`

5. **ISO 8601 dates with timezone**
   - Always include timezone: `'2025-12-26T19:59:22.743729Z'`
   - Don't use: `'2025-12-26'` or `'12/26/2025'`

6. **Units always included**
   - Every measurement needs `{ value, unit, min, max }`
   - Never use just a number: `density: 2.7` ❌
   - Always use object: `density: { value: 2.7, unit: 'g/cm³' }` ✅

7. **Author is object not string**
   - Full structure required with all fields
   - Minimum: `id`, `name`, `title`, `jobTitle`, `email`

8. **Images is object with nested objects**
   - Not flat: `images: /path/to/image.jpg` ❌
   - Nested: `images: { hero: { url: '/path', alt: 'text' } }` ✅

---

## ✅ Complete Valid Example

```yaml
id: aluminum-laser-cleaning
name: Aluminum
title: Aluminum Laser Cleaning
page_description: Aluminum requires precise wavelength control due to 88% reflectivity, making it challenging for laser cleaning without proper parameter adjustment.
category: metal
subcategory: non-ferrous
content_type: materials
schema_version: 5.0.0
slug: aluminum-laser-cleaning
full_path: /materials/metal/non-ferrous/aluminum-laser-cleaning
datePublished: '2025-12-26T19:59:22.743729Z'
dateModified: '2025-12-26T19:59:22.743729Z'

images:
  hero:
    url: /images/material/aluminum-hero.jpg
    alt: Aluminum surface during laser cleaning process
    width: 1200
    height: 630
  micro:
    url: /images/material/aluminum-micro.jpg
    alt: Microscopic view of cleaned aluminum surface
    width: 800
    height: 600

author:
  id: 1
  name: Yi-Chun Lin
  country: Taiwan
  country_display: Taiwan
  title: Ph.D.
  sex: f
  jobTitle: Laser Processing Engineer
  email: info@z-beam.com
  expertise:
    - Laser Materials Processing
    - Surface Engineering
  credentials:
    - Ph.D. Materials Engineering, National Taiwan University, 2018
  affiliation:
    name: National Taiwan University
    type: EducationalOrganization

micro:
  before: Surface shows oxide layer and surface contamination with visible discoloration.
  after: Clean metallic surface with natural luster and uniform appearance restored.

faq:
  - question: How does laser cleaning work on aluminum?
    answer: The laser removes oxide layers and contaminants without damaging the base metal, preserving the anodized finish.
    topic_keyword: aluminum laser cleaning
    topic_statement: Non-destructive oxide removal
  - question: What wavelength is best for aluminum?
    answer: 1064nm wavelength is most effective due to aluminum's high reflectivity at shorter wavelengths.
    topic_keyword: wavelength selection
    topic_statement: Use 1064nm for optimal results

breadcrumb:
  - label: Home
    href: /
  - label: Materials
    href: /materials
  - label: Metal
    href: /materials/metal
  - label: Non-Ferrous
    href: /materials/metal/non-ferrous
  - label: Aluminum
    href: /materials/metal/non-ferrous/aluminum-laser-cleaning

properties:
  material_characteristics:
    density:
      value: 2.7
      unit: g/cm³
      min: 0.5
      max: 23
    meltingPoint:
      value: 660
      unit: °C
      min: 100
      max: 3800
  laser_material_interaction:
    thermalConductivity:
      value: 237
      unit: W/(m·K)
      min: 7
      max: 430
    reflectivity:
      value: 88
      unit: '%'
      min: 10
      max: 95

contamination:
  valid:
    - rust-contamination
    - oxide-layer
    - grease-contamination
  prohibited:
    - asbestos-contamination

relationships:
  technical:
    materials:
      - steel-laser-cleaning
      - titanium-laser-cleaning
  operational:
    settings:
      - aluminum-settings
```

---

## ❌ Invalid Example (Common Mistakes)

```yaml
# ❌ WRONG - DO NOT DO THIS

# Wrong field name
description: Some text              # Should be 'page_description'

# Deprecated field
subtitle: Extra text                # Field has been removed

# Wrong author structure
author: "John Doe"                  # Should be object with full structure

# Wrong images structure
images: /path/to/image.jpg          # Should be nested object

# Wrong micro structure
micro: "Some text"                  # Should be object with before/after

# Wrong FAQ structure
faq: "Question and answer"          # Should be array of objects

# Missing units
density: 2.7                        # Should be { value: 2.7, unit: 'g/cm³' }

# Wrong date format
datePublished: 12/26/2025           # Should be ISO 8601 with timezone

# Flattened expertise
expertise: "Laser Processing, Surface Engineering"  # Should be array
```

---

## 🔍 Validation Checklist

Before generating frontmatter, verify:

- [ ] `page_description` used (not `description`)
- [ ] No `subtitle` field present
- [ ] `author` is object with all required fields
- [ ] `images` has nested structure (`hero`, `micro`)
- [ ] `micro` is object with `before` and `after`
- [ ] `faq` is array of objects
- [ ] All properties have `value`, `unit`, `min`, `max`
- [ ] Dates are ISO 8601 with timezone
- [ ] All arrays are actually arrays (not strings)
- [ ] `breadcrumb` array has `label` and `href` for each item

---

## 📞 Questions?

If you encounter field requirements not covered in this spec, contact the frontend team before implementing custom mappings.

**Last Updated:** December 26, 2025  
**Schema Version:** 5.0.0
