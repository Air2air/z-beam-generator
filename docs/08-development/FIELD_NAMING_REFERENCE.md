# Field Naming Reference

**Date**: February 25, 2026  
**Scope**: All domains — materials, contaminants, compounds, settings, applications  
**Authority**: `data/schemas/FrontmatterFieldOrder.yaml`  
**Status**: Canonical — all code, docs, tests, and schemas must match this document

---

## Core Naming Rule

| Layer | Convention | Example |
|-------|-----------|---------|
| Backend Python code (variables, params) | `snake_case` | `field_value`, `item_id` |
| Backend data YAML (`data/*/`) | `camelCase` | `pageDescription` |
| Exported frontmatter YAML (`frontmatter/*/`) | `camelCase` | `pageDescription` |
| TypeScript types (`types/`, `app/`) | `camelCase` | `pageDescription` |
| URL slugs | `kebab-case` | `acrylic-pmma` |

Source data YAMLs and frontmatter YAMLs both use camelCase — the exporter passes keys through as-is and applies field ordering only. No snake_case → camelCase conversion occurs in the pipeline.  
**Never write snake_case field keys into any YAML (data or frontmatter). Python variable/method names follow PEP 8 snake_case internally.**

### CLI Field Name Aliases
The postprocessor CLI accepts snake_case aliases as convenience arguments (e.g. `--field page_description`). These are resolved via `FieldRouter.normalize_field_name()` using the `field_aliases` block in `generation/config.yaml`. Aliases **never** appear as YAML keys.

| CLI alias | Canonical YAML key |
|-----------|-------------------|
| `page_description` | `pageDescription` |
| `description` | `pageDescription` |

---

---

## Universal Base Fields (All Domains)

These fields appear in every domain frontmatter. Order follows `FrontmatterFieldOrder.yaml` tiers.

| Frontmatter Key (camelCase) | Backend YAML Key (snake_case) | TypeScript Type | Tier | Required | Notes |
|-----------------------------|-------------------------------|-----------------|------|----------|-------|
| `id` | `id` | `string` | 1 — Identity | ✓ | Unique slug-based ID |
| `name` | `name` | `string` | 1 — Identity | ✓ | Human-readable name |
| `displayName` | `display_name` | `string \| null` | 2 — Identity | — | Nullable; falls back to `name` |
| `category` | `category` | `string` | 2 — Identity | ✓ | Domain-specific vocab |
| `subcategory` | `subcategory` | `string` | 2 — Identity | — | |
| `datePublished` | `date_published` | `string` (ISO 8601) | 3 — Metadata | ✓ | |
| `dateModified` | `date_modified` | `string` (ISO 8601) | 3 — Metadata | ✓ | |
| `contentType` | `content_type` | `string` | 3 — Metadata | ✓ | e.g. `material`, `contaminant` |
| `schemaVersion` | `schema_version` | `string` | 3 — Metadata | ✓ | Semver string |
| `fullPath` | `full_path` | `string` | 4 — Navigation | ✓ | Absolute URL path |
| `breadcrumb` | `breadcrumb` | `BreadcrumbItem[]` | 4 — Navigation | ✓ | See nested structure below |
| `pageTitle` | `page_title` | `string` | 5 — SEO | ✓ | `<title>` tag value |
| `pageDescription` | `page_description` | `string` | 5 — SEO | ✓ | Open Graph + SEO description |
| `images` | `images` | `ImagesBlock` | 7 — Media | — | See nested structure below |
| `relationships` | `relationships` | `RelationshipsBlock` | 8 — Relations | — | See nested structure below |
| `author` | `author` | `Author` | 9 — Author | ✓ | See nested structure below |
| `card` | `card` | `CardBlock` | 9 — Author | — | Not all domains; see domain table |

---

## Domain Field Tables

### Materials

| Frontmatter Key | Backend YAML Key | Type | Notes |
|-----------------|-----------------|------|-------|
| *(universal base fields above)* | | | |
| `slug` | `slug` | `string` | URL slug |
| `micro` | `micro` | `MicroBlock` | **Materials-only**; before/after visual summary; nullable |
| `faq` | `faq` | `FaqItem[]` | Nullable |
| `properties` | `properties` | `object` | Physical/chemical properties object |
| `components` | `components` | `object[]` | Material components list |
| `contamination` | `contamination` | `object` | Legacy contamination data |
| `eeat` | `eeat` | `EeatBlock` | E-E-A-T credentials |
| `abbreviations` | `abbreviations` | `object` | Short-form name map |
| `industryTags` | `industry_tags` | `string[]` | Industry classification tags |
| `laserMaterialInteraction` | `laser_material_interaction` | `object` | Laser interaction data |
| `materialCharacteristics` | `material_characteristics` | `object` | Physical characteristics |
| `ranges` | `ranges` | `object` | Parameter ranges |

**Required**: `id`, `name`, `category`, `contentType`, `schemaVersion`, `datePublished`, `dateModified`, `fullPath`, `breadcrumb`, `pageTitle`, `pageDescription`, `author`

---

### Contaminants

| Frontmatter Key | Backend YAML Key | Type | Notes |
|-----------------|-----------------|------|-------|
| *(universal base fields above)* | | | |
| `scientificName` | `scientific_name` | `string \| null` | IUPAC or common scientific name |
| `chemicalFormula` | `chemical_formula` | `string` | |
| `description` | `description` | `string \| null` | Long-form description |
| `composition` | `composition` | `object` | Chemical composition detail |
| `formationConditions` | `formation_conditions` | `string` | When/how contaminant forms |
| `validMaterials` | `valid_materials` | `string[]` | Materials this contaminant applies to |
| `validMaterialCategories` | `valid_material_categories` | `string[]` | |
| `validContexts` | `valid_contexts` | `string[]` | |
| `prohibitedMaterials` | `prohibited_materials` | `string[]` | |
| `cautionMaterials` | `caution_materials` | `string[]` | |
| `conditionalRules` | `conditional_rules` | `object[]` | |
| `contextNotes` | `context_notes` | `string` | |
| `contextRequired` | `context_required` | `boolean` | |
| `invalidWithoutContext` | `invalid_without_context` | `boolean` | |
| `materialSpecificNotes` | `material_specific_notes` | `object` | |
| `requiredElements` | `required_elements` | `string[]` | |
| `realismNotes` | `realism_notes` | `string` | Image generation guidance |
| `researchTimestamp` | `research_timestamp` | `string` (ISO 8601) | |
| `researchVersion` | `research_version` | `string` | |
| `imageGenerationFeedback` | `image_generation_feedback` | `object` | |
| `title` | `title` | `string` | ⚠️ Legacy — prefer `name`; both may exist |

**NOT present in contaminants**: `micro`, `card`

**Required**: `id`, `name`, `category`, `contentType`, `schemaVersion`, `datePublished`, `dateModified`, `fullPath`, `breadcrumb`, `pageTitle`, `pageDescription`, `author`, `relationships`

---

### Compounds

| Frontmatter Key | Backend YAML Key | Type | Notes |
|-----------------|-----------------|------|-------|
| *(universal base fields above)* | | | |
| `chemicalFormula` | `chemical_formula` | `string` | |
| `casNumber` | `cas_number` | `string` | CAS Registry Number |
| `molecularWeight` | `molecular_weight` | `number` | g/mol |
| `hazardClass` | `hazard_class` | `string` | GHS hazard classification |
| `healthEffects` | `health_effects` | `string` | Narrative health effects |
| `healthEffectsKeywords` | `health_effects_keywords` | `string[]` | |
| `exposureGuidelines` | `exposure_guidelines` | `ExposureLimitsBlock` | See nested structure below |
| `detectionMethods` | `detection_methods` | `string[]` | |
| `firstAid` | `first_aid` | `string` | |
| `ppeRequirements` | `ppe_requirements` | `string[]` | |
| `regulatoryStandards` | `regulatory_standards` | `object[]` | |
| `monitoringRequired` | `monitoring_required` | `boolean` | |
| `sourcesInLaserCleaning` | `sources_in_laser_cleaning` | `string[]` | |
| `typicalConcentrationRange` | `typical_concentration_range` | `string` | |
| `faq` | `faq` | `FaqItem[]` | Nullable |
| `title` | `title` | `string` | ⚠️ Legacy — prefer `name` |

**NOT present in compounds**: `micro`

**Required**: `id`, `name`, `category`, `contentType`, `schemaVersion`, `chemicalFormula`, `card`, `relationships`

---

### Settings

| Frontmatter Key | Backend YAML Key | Type | Notes |
|-----------------|-----------------|------|-------|
| *(universal base fields above)* | | | |
| `machineSettings` | `machine_settings` | `object` | Laser parameter settings block |
| `componentSummary` | `component_summary` | `object` | **Singular** — single component |
| `componentSummaries` | `component_summaries` | `object[]` | **Plural** — multi-component list |
| `abbreviations` | `abbreviations` | `object` | |

> ⚠️ **`componentSummary` vs `componentSummaries`** — both exist in production frontmatter. The exporter should write only the form matching the data shape (singular object vs. array). Do not use both.

**Required**: `id`, `name`, `category`, `contentType`, `schemaVersion`, `datePublished`, `dateModified`, `fullPath`, `breadcrumb`, `pageTitle`, `pageDescription`, `author`, `card`

---

### Applications

| Frontmatter Key | Backend YAML Key | Type | Notes |
|-----------------|-----------------|------|-------|
| *(universal base fields above)* | | | |
| `slug` | `slug` | `string` | |
| `keywords` | `keywords` | `string[]` | SEO keyword list |
| `metaDescription` | `meta_description` | `string` | Separate from `pageDescription` |

**NOT present in applications**: `micro`, `metaDescription` is extra (most domains use only `pageDescription`)

**Required**: `id`, `name`, `category`, `contentType`, `schemaVersion`, `datePublished`, `dateModified`, `fullPath`, `breadcrumb`, `pageTitle`, `pageDescription`, `author`

---

## Nested Structure Specifications

### `breadcrumb` — All Domains

```yaml
# frontmatter (camelCase)
breadcrumb:
  - label: "Home"
    url: "/"
  - label: "Materials"
    url: "/materials"
  - label: "Alumina"
    url: "/materials/alumina-laser-cleaning"
```

| Frontmatter Key | Backend Key | Type |
|----------------|------------|------|
| `label` | `label` | `string` |
| `url` | `url` | `string` |

---

### `images` — All Domains

```yaml
images:
  hero:
    url: "/images/materials/alumina-hero.webp"
    alt: "Alumina surface before laser cleaning"
  micro:
    url: "/images/materials/alumina-micro.webp"
    alt: "Alumina micro-surface view"
```

| Frontmatter Key | Backend Key | Type |
|----------------|------------|------|
| `images.hero.url` | `images.hero.url` | `string` |
| `images.hero.alt` | `images.hero.alt` | `string` |
| `images.micro.url` | `images.micro.url` | `string` |
| `images.micro.alt` | `images.micro.alt` | `string` |

---

### `micro` — Materials Only

```yaml
micro:
  before: "Alumina surface covered in organic residue..."
  after: "Clean white alumina surface with uniform crystalline..."
```

| Frontmatter Key | Backend Key | Type | Notes |
|----------------|------------|------|-------|
| `micro.before` | `micro.before` | `string` | Pre-cleaning description |
| `micro.after` | `micro.after` | `string` | Post-cleaning description |

**Canonical sub-keys**: `before` and `after` only. Do not use `beforeText`/`afterText`.

---

### `author` — All Domains

```yaml
author:
  id: "dr-elena-vasquez"
  name: "Dr. Elena Vasquez"
  jobTitle: "Senior Laser Materials Scientist"
  country: "ES"
  countryDisplay: "Spain"
  sex: "female"
  expertise:
    - "laser material interaction"
  affiliation:
    name: "Barcelona Institute of Photonics"
    type: "research"
  credentials:
    - "PhD Photonics"
  languages:
    - "en"
    - "es"
  email: "elena.vasquez@example.com"
  image: "/images/authors/dr-elena-vasquez.jpg"
  imageAlt: "Dr. Elena Vasquez"
  url: "/authors/dr-elena-vasquez"
  sameAs:
    - "https://linkedin.com/in/elenavasquez"
  personaFile: "elena_vasquez"
  formattingFile: "academic"
```

| Frontmatter Key | Backend Key | Type | Notes |
|----------------|------------|------|-------|
| `author.id` | `author.id` | `number` | **Immutable once set** |
| `author.name` | `author.name` | `string` | |
| `author.jobTitle` | `author.job_title` | `string` | camelCase in frontmatter |
| `author.country` | `author.country` | `string` | ISO 3166-1 alpha-2 |
| `author.countryDisplay` | `author.country_display` | `string` | camelCase in frontmatter |
| `author.sex` | `author.sex` | `string` | `"male"` \| `"female"` |
| `author.expertise` | `author.expertise` | `string[]` | |
| `author.affiliation` | `author.affiliation` | `AffiliationBlock` | |
| `author.affiliation.name` | `author.affiliation.name` | `string` | |
| `author.affiliation.type` | `author.affiliation.type` | `string` | |
| `author.credentials` | `author.credentials` | `string[]` | |
| `author.languages` | `author.languages` | `string[]` | ISO 639-1 codes |
| `author.email` | `author.email` | `string` | |
| `author.image` | `author.image` | `string` | Path or URL |
| `author.imageAlt` | `author.image_alt` | `string` | camelCase in frontmatter |
| `author.url` | `author.url` | `string` | |
| `author.sameAs` | `author.same_as` | `string[]` | camelCase in frontmatter |
| `author.personaFile` | `author.persona_file` | `string` | camelCase in frontmatter |
| `author.formattingFile` | `author.formatting_file` | `string` | camelCase in frontmatter |

---

### `relationships` — All Domains

```yaml
relationships:
  related_contaminants:           # snake_case keys INSIDE relationships block
    - id: "oil-grease-contamination"
      slug: "oil-grease-contamination"
      url: "/contaminants/oil-grease-contamination"
      frequency: "high"
```

> ⚠️ **Exception**: Sub-keys within `relationships` use `snake_case` (not camelCase). This is intentional — the relationships block mirrors backend linkage conventions.

| Top-level Key | Domain | Related domain |
|--------------|--------|---------------|
| `related_contaminants` | materials | contaminants |
| `related_compounds` | materials | compounds |
| `related_settings` | materials | settings |
| `regulatory_standards` | materials | — |
| `related_materials` | contaminants, compounds | materials |
| `produces_compounds` | contaminants | compounds |
| `recommended_settings` | contaminants | settings |
| `produced_by_contaminants` | compounds | contaminants |
| `suitable_materials` | settings | materials |
| `effective_contaminants` | settings | contaminants |

**Link item fields** (inside any relationship list):

| Field | Type | Notes |
|-------|------|-------|
| `id` | `string` | Slug-based ID |
| `slug` | `string` | Same as id in most cases |
| `url` | `string` | Absolute path |
| `image` | `string` | Optional |
| `frequency` | `string` | `"high"` \| `"medium"` \| `"low"` |
| `severity` | `string` | Context-specific |
| `typical_context` | `string` | Context-specific |

---

### `exposureGuidelines` — Compounds Only

```yaml
exposureGuidelines:
  osha_pel_ppm: 1
  osha_pel_mg_m3: 5.2
  niosh_rel_ppm: 0.5
  niosh_rel_mg_m3: 2.6
  acgih_tlv_ppm: 0.5
  acgih_tlv_mg_m3: 2.6
```

> ⚠️ **Exception**: Sub-keys within `exposureGuidelines` use `snake_case` with unit suffixes. This matches regulatory database conventions and must not be converted to camelCase.

---

### `card` — Materials, Compounds, Settings

```yaml
card:
  title: "Alumina"
  subtitle: "Ceramic oxide, Al₂O₃"
  description: "High-purity alumina responds excellently..."
  image: "/images/materials/alumina-card.webp"
  imageAlt: "Alumina ceramic surface"
  tags:
    - "ceramic"
    - "oxide"
```

| Frontmatter Key | Backend Key | Type |
|----------------|------------|------|
| `card.title` | `card.title` | `string` |
| `card.subtitle` | `card.subtitle` | `string` |
| `card.description` | `card.description` | `string` |
| `card.image` | `card.image` | `string` |
| `card.imageAlt` | `card.image_alt` | `string` |
| `card.tags` | `card.tags` | `string[]` |

---

## Domain × Field Coverage Matrix

| Field | materials | contaminants | compounds | settings | applications |
|-------|:---------:|:------------:|:---------:|:--------:|:------------:|
| `id` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `name` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `displayName` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `category` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `subcategory` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `datePublished` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dateModified` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `contentType` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `schemaVersion` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `fullPath` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `breadcrumb` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `pageTitle` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `pageDescription` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `metaDescription` | — | — | — | — | ✓ |
| `images` | ✓ | ✓ | ✓ | ✓ | — |
| `relationships` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `author` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `card` | ✓ | — | ✓ | ✓ | — |
| `slug` | ✓ | — | — | — | ✓ |
| `micro` | ✓ | — | — | — | — |
| `faq` | ✓ | — | ✓ | — | — |
| `properties` | ✓ | — | — | — | — |
| `components` | ✓ | — | — | — | — |
| `contamination` | ✓ | — | — | — | — |
| `eeat` | ✓ | — | — | — | — |
| `abbreviations` | ✓ | — | — | ✓ | — |
| `industryTags` | ✓ | — | — | — | — |
| `laserMaterialInteraction` | ✓ | — | — | — | — |
| `materialCharacteristics` | ✓ | — | — | — | — |
| `ranges` | ✓ | — | — | — | — |
| `scientificName` | — | ✓ | — | — | — |
| `chemicalFormula` | — | ✓ | ✓ | — | — |
| `description` | — | ✓ | — | — | — |
| `composition` | — | ✓ | — | — | — |
| `formationConditions` | — | ✓ | — | — | — |
| `validMaterials` | — | ✓ | — | — | — |
| `validMaterialCategories` | — | ✓ | — | — | — |
| `validContexts` | — | ✓ | — | — | — |
| `prohibitedMaterials` | — | ✓ | — | — | — |
| `cautionMaterials` | — | ✓ | — | — | — |
| `conditionalRules` | — | ✓ | — | — | — |
| `casNumber` | — | — | ✓ | — | — |
| `molecularWeight` | — | — | ✓ | — | — |
| `hazardClass` | — | — | ✓ | — | — |
| `healthEffects` | — | — | ✓ | — | — |
| `healthEffectsKeywords` | — | — | ✓ | — | — |
| `exposureGuidelines` | — | — | ✓ | — | — |
| `detectionMethods` | — | ✓ | ✓ | — | — |
| `firstAid` | — | — | ✓ | — | — |
| `ppeRequirements` | — | — | ✓ | — | — |
| `regulatoryStandards` | — | — | ✓ | — | — |
| `monitoringRequired` | — | — | ✓ | — | — |
| `sourcesInLaserCleaning` | — | — | ✓ | — | — |
| `typicalConcentrationRange` | — | — | ✓ | — | — |
| `machineSettings` | — | — | — | ✓ | — |
| `componentSummary` | — | — | — | ✓ | — |
| `componentSummaries` | — | — | — | ✓ | — |
| `keywords` | — | — | — | — | ✓ |

---

## Deprecated / Legacy Fields

| Field | Domain | Status | Replacement |
|-------|--------|--------|-------------|
| `title` | contaminants, compounds | ⚠️ Legacy | Use `name` |
| `lastModified` | materials (TypeScript only) | ⚠️ Deprecated | Use `dateModified` |
| `componentSummary` (singular) | settings | ⚠️ Inconsistent | Prefer `componentSummaries` when data is array |

---

## camelCase ↔ Python snake_case Quick-Lookup

YAML keys (data and frontmatter) are always camelCase. This table maps each YAML key to its equivalent Python variable/parameter name (snake_case per PEP 8), and doubles as a spelling reference.

| YAML / TS key (camelCase) | Python variable equivalent (snake_case) |
|------------------------------|--------------------------|
| `casNumber` | `cas_number` |
| `categoryDescriptions` | `category_descriptions` |
| `chemicalFormula` | `chemical_formula` |
| `componentSummaries` | `component_summaries` |
| `componentSummary` | `component_summary` |
| `conditionalRules` | `conditional_rules` |
| `contentType` | `content_type` |
| `contextNotes` | `context_notes` |
| `contextRequired` | `context_required` |
| `cautionMaterials` | `caution_materials` |
| `dateModified` | `date_modified` |
| `datePublished` | `date_published` |
| `detectionMethods` | `detection_methods` |
| `displayName` | `display_name` |
| `exposureGuidelines` | `exposure_guidelines` |
| `firstAid` | `first_aid` |
| `formationConditions` | `formation_conditions` |
| `fullPath` | `full_path` |
| `hazardClass` | `hazard_class` |
| `healthEffects` | `health_effects` |
| `healthEffectsKeywords` | `health_effects_keywords` |
| `imageGenerationFeedback` | `image_generation_feedback` |
| `industryTags` | `industry_tags` |
| `invalidWithoutContext` | `invalid_without_context` |
| `laserMaterialInteraction` | `laser_material_interaction` |
| `machineSettings` | `machine_settings` |
| `materialCharacteristics` | `material_characteristics` |
| `materialSpecificNotes` | `material_specific_notes` |
| `metaDescription` | `meta_description` |
| `molecularWeight` | `molecular_weight` |
| `monitoringRequired` | `monitoring_required` |
| `pageDescription` | `page_description` |
| `pageTitle` | `page_title` |
| `ppeRequirements` | `ppe_requirements` |
| `prohibitedMaterials` | `prohibited_materials` |
| `realismNotes` | `realism_notes` |
| `regulatoryStandards` | `regulatory_standards` |
| `requiredElements` | `required_elements` |
| `researchTimestamp` | `research_timestamp` |
| `researchVersion` | `research_version` |
| `schemaVersion` | `schema_version` |
| `scientificName` | `scientific_name` |
| `sourcesInLaserCleaning` | `sources_in_laser_cleaning` |
| `typicalConcentrationRange` | `typical_concentration_range` |
| `validContexts` | `valid_contexts` |
| `validMaterialCategories` | `valid_material_categories` |
| `validMaterials` | `valid_materials` |

---

## Exceptions: Fields That Do NOT Convert

These fields retain the same form in both backend YAML and frontmatter (intentional exceptions):

| Field | Reason |
|-------|--------|
| `id` | Single lowercase word |
| `name` | Single lowercase word |
| `url` | Established abbreviation |
| `faq` | Established acronym |
| `eeat` | Established acronym |
| `relationships.*` sub-keys | Retain snake_case inside the relationships block |
| `exposureGuidelines.*` sub-keys | Retain snake_case (regulatory convention) |

---

## Where to Find Things

| What | Where |
|------|-------|
| Field order spec | `data/schemas/FrontmatterFieldOrder.yaml` |
| JSON schemas (structured data) | `data/schemas/dataset-*.json` |
| Backend data source files | `data/{domain}/*.yaml` |
| Exported frontmatter | `frontmatter/{domain}/*.yaml` (z-beam repo) |
| TypeScript base type | `types/centralized.ts` → `FrontmatterType` |
| TS domain-extended type | `app/utils/schemas/generators/types.ts` → `MaterialFrontmatter` |
| Naming conventions (code) | `docs/08-development/NAMING_CONVENTIONS_POLICY.md` |
| Material name consistency | `docs/08-development/MATERIAL_NAME_CONSISTENCY_POLICY.md` |
| Exporter logic | `export/` |
| Frontmatter source of truth policy | `docs/08-development/FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md` |
