# Section Registry

**Last Updated**: January 4, 2026  
**Purpose**: Comprehensive catalog of all relationship sections across all domains  
**Audience**: Developers, content strategists, frontend implementers

---

## Overview

This document catalogs all relationship sections used across the four primary domains (Materials, Settings, Contaminants, Compounds). Each section represents a topic area on the website, organized into a two-level hierarchy: **category.section_key**.

### Architecture

**Hierarchy**: `relationships.{category}.{section_key}`

**Metadata Structure**:
- **Display Fields** (shown to users):
  - `section_title`: Display title for the section
  - `section_description`: Optional descriptive text
  - `icon`: Lucide icon name for visual identification
  - `order`: Display sequence
  - `variant`: Visual styling (`default`, `warning`, `danger`)

- **Internal Fields** (developer reference only):
  - `section_metadata`: Object containing:
    - `notes`: Developer context and purpose
    - `source_field`: Origin field in source YAML
    - `moved_from`: Migration history (if applicable)
    - `presentation_type`: Frontend display format
    - `relationship_type`: Type of relationship (for relational sections)
    - `features`: Special capabilities (e.g., `auto_open_first`)

---

## Category Taxonomy

### 1. **identity** - Core Identification Data
Defines what the entity is, its physical/chemical properties, and alternate names.

**Applicable Domains**: Compounds  
**Purpose**: Establish foundational identity and classification  
**Presentation**: Typically descriptive or table format

### 2. **interactions** - Relational Connections
Shows how entities relate to or interact with other entities in the system.

**Applicable Domains**: Materials, Settings, Contaminants, Compounds  
**Purpose**: Display cross-domain relationships and contextual connections  
**Presentation**: Card-based layouts with linked items

### 3. **operational** - Practical Application Information
Provides real-world usage guidance, applications, and expert insights.

**Applicable Domains**: Materials, Settings, Contaminants, Compounds  
**Purpose**: Help users understand practical applications and expert recommendations  
**Presentation**: Collapsible panels (Q&A format) or card layouts

### 4. **safety** - Health and Safety Information
Critical safety data including hazards, protections, and regulatory compliance.

**Applicable Domains**: Materials, Settings, Contaminants, Compounds  
**Purpose**: Ensure user safety awareness and regulatory compliance  
**Presentation**: High-visibility formats (tables, cards) with warning variants

### 5. **environmental** - Environmental Impact Data
Information about environmental effects, sustainability, and ecological considerations.

**Applicable Domains**: Compounds  
**Purpose**: Support environmental responsibility and compliance  
**Presentation**: Descriptive format with impact assessment

### 6. **detection_monitoring** - Detection and Monitoring Systems
Methods and technologies for identifying, measuring, and monitoring entities.

**Applicable Domains**: Contaminants, Compounds  
**Purpose**: Enable effective detection and quality control  
**Presentation**: Table or card format with technical specifications

### 7. **detection** - Detection Methods (Alternate)
Alternative categorization for detection-related content.

**Applicable Domains**: Compounds  
**Purpose**: Specific detection methodologies  
**Presentation**: Descriptive or table format

### 8. **visual** - Visual Characteristics
Appearance-based information including colors, textures, and visual identification.

**Applicable Domains**: Contaminants  
**Purpose**: Support visual identification and quality assessment  
**Presentation**: Descriptive format with visual details

### 9. **quality_control** - Quality Assurance (Planned)
Quality control standards, testing procedures, and acceptance criteria.

**Status**: Category exists but no sections currently defined  
**Applicable Domains**: TBD  
**Purpose**: Support quality management and process control

### 10. **performance** - Performance Metrics (Planned)
Performance characteristics, benchmarks, and optimization data.

**Status**: Category exists but no sections currently defined  
**Applicable Domains**: TBD  
**Purpose**: Enable performance optimization and comparison

---

## Domain Section Catalog

### Materials Domain

**Total Sections**: 4  
**Categories Used**: 3 (interactions, operational, safety)

| Section Key | Category | Title | Presentation | Source Field | Notes |
|------------|----------|-------|--------------|--------------|-------|
| `contaminated_by` | interactions | Contaminated By | Card | contaminated_by | Common contaminants for this material |
| `industry_applications` | operational | Industry Applications | Collapsible | industry_applications | Real-world use cases, auto-opens first item |
| `expert_answers` | operational | Expert Answers | Collapsible | expert_answers | Q&A format expert insights |
| `regulatory_standards` | safety | Regulatory Standards | Card | regulatory_standards | Compliance requirements |

---

### Settings Domain

**Total Sections**: 4  
**Categories Used**: 3 (safety, interactions, operational)

| Section Key | Category | Title | Presentation | Source Field | Notes |
|------------|----------|-------|--------------|--------------|-------|
| `prevention` | safety | Prevention | Collapsible | prevention | Safety guidelines, auto-opens first item |
| `suitable_for_materials` | interactions | Suitable For Materials | Card | suitable_for_materials | Compatible materials |
| `suitable_for_contaminants` | interactions | Suitable For Contaminants | Card | suitable_for_contaminants | Compatible contaminants |
| `expert_answers` | operational | Expert Answers | Collapsible | expert_answers | Q&A format expert insights |

---

### Contaminants Domain

**Total Sections**: 15+  
**Categories Used**: 4 (safety, interactions, visual, operational)

| Section Key | Category | Title | Presentation | Source Field | Notes |
|------------|----------|-------|--------------|--------------|-------|
| `health_effects` | safety | Health Effects | Table | health_effects | Medical impacts and severity |
| `removal_settings` | interactions | Removal Settings | Card | removal_settings | Effective laser settings |
| `found_on_materials` | interactions | Found On Materials | Card | found_on_materials | Common material hosts |
| `visual_characteristics` | visual | Visual Characteristics | Descriptive | visual_characteristics | Appearance details |
| `expert_answers` | operational | Expert Answers | Collapsible | expert_answers | Q&A format expert insights |
| *(10+ additional sections)* | *(various)* | *(various)* | *(various)* | *(various)* | *See contaminants.yaml for complete list* |

**Note**: Contaminants domain has the most comprehensive section coverage, reflecting its safety-critical nature.

---

### Compounds Domain

**Total Sections**: 17  
**Categories Used**: 7 (identity, safety, environmental, detection, detection_monitoring, interactions, operational)

#### Identity Sections (3)

| Section Key | Title | Icon | Order | Variant | Presentation | Source | Notes |
|------------|-------|------|-------|---------|--------------|--------|-------|
| `chemical_properties` | Chemical Properties | atom | 1 | default | Descriptive | chemical_properties | Molecular formula, weight, structure |
| `physical_properties` | Physical Properties | thermometer | 2 | default | Descriptive | physical_properties | State, melting/boiling points, density |
| `synonyms_identifiers` | Synonyms & Identifiers | bookmark | 3 | default | Descriptive | synonyms_identifiers | Alternative names, CAS numbers |

#### Safety Sections (6)

| Section Key | Title | Icon | Order | Variant | Presentation | Source | Notes |
|------------|-------|------|-------|---------|--------------|--------|-------|
| `health_impacts` | Health Impacts | alert-circle | 1 | warning | Table | health_impacts | Exposure routes, acute/chronic effects |
| `exposure_guidance` | Exposure Guidance | shield | 2 | warning | Table | exposure_guidance | Occupational limits, regulatory thresholds |
| `personal_protection` | Personal Protection | shield-check | 3 | default | Table | personal_protection | PPE requirements, engineering controls |
| `emergency_procedures` | Emergency Procedures | ambulance | 4 | danger | Card | emergency_procedures | First aid, spill response |
| `storage_requirements` | Storage Requirements | package | 5 | default | Descriptive | storage_requirements | Proper storage conditions |
| `regulatory_classification` | Regulatory Classification | file-text | 6 | default | Table | regulatory_classification | GHS classification, legal requirements |

#### Environmental Section (1)

| Section Key | Title | Icon | Order | Variant | Presentation | Source | Notes |
|------------|-------|------|-------|---------|--------------|--------|-------|
| `environmental_impact` | Environmental Impact | leaf | 1 | default | Descriptive | environmental_impact | Ecotoxicity, persistence, disposal |

#### Detection Sections (2)

| Section Key | Title | Icon | Order | Variant | Presentation | Source | Notes |
|------------|-------|------|-------|---------|--------------|--------|-------|
| `methods` | Detection Methods | search | 1 | default | Table | detection_methods | Analytical techniques |
| `detection_monitoring` | Detection Monitoring | activity | 1 | default | Card | detection_monitoring | Monitoring systems |

#### Interactions Sections (3)

| Section Key | Title | Icon | Order | Variant | Presentation | Source | Notes |
|------------|-------|------|-------|---------|--------------|--------|-------|
| `produced_from_contaminants` | Produced From Contaminants | arrow-right | 1 | default | Card | produced_from_contaminants | Source contaminants |
| `produced_from_materials` | Produced From Materials | package | 2 | default | Card | produced_from_materials | Source materials |
| `reactivity` | Reactivity | zap | 3 | default | Descriptive | reactivity | Chemical reactivity, incompatibilities |

#### Operational Section (1)

| Section Key | Title | Icon | Order | Variant | Presentation | Source | Notes |
|------------|-------|------|-------|---------|--------------|--------|-------|
| `expert_answers` | Expert Answers | message-circle | 1 | default | Collapsible | expert_answers | Q&A format, auto-opens first |

---

## Presentation Type Matrix

| Type | Description | Use Cases | Domains |
|------|-------------|-----------|---------|
| **card** | Card-based grid layout | Lists of related items, cross-references | All domains |
| **collapsible** | Accordion/expandable panels | Q&A content, detailed explanations | Materials, Settings, Contaminants, Compounds |
| **table** | Tabular data display | Structured data with multiple fields | Contaminants, Compounds |
| **descriptive** | Free-form text content | Narrative descriptions, explanations | All domains |

---

## Relationship Type Classifications

### produced_from
**Source → Output**: Describes what creates or generates the entity  
**Examples**: Contaminants → Compounds, Materials → Compounds  
**Direction**: Backward-looking (what created this)

### suitable_for
**Entity → Compatible Entities**: Describes compatibility relationships  
**Examples**: Settings → Materials, Settings → Contaminants  
**Direction**: Forward-looking (what this works with)

### contaminated_by
**Material → Contaminants**: Shows which contaminants commonly affect a material  
**Direction**: Forward-looking (what affects this)

### found_on_materials
**Contaminant → Materials**: Shows where a contaminant typically appears  
**Direction**: Backward-looking (where this is found)

### removal_settings
**Contaminant → Settings**: Effective removal configurations  
**Direction**: Forward-looking (how to address this)

---

## Field Standardization Notes

### Recent Consolidations

The following field pairs were consolidated to standardize naming:

**Compounds Domain** (consolidated Dec 2025):
- `health_effects` → **`health_impacts`** (standardized)
- `ppe_requirements` → **`personal_protection`** (standardized)
- `emergency_response` → **`emergency_procedures`** (standardized)
- `exposure_limits` → **`exposure_guidance`** (standardized)

**Action**: `remove_duplicate_safety_fields` task removes legacy field names during export.

---

## Icon Guidelines

Icons use [Lucide](https://lucide.dev/) icon set. Common patterns:

| Category | Typical Icons | Examples |
|----------|---------------|----------|
| Identity | atom, bookmark, thermometer | chemical_properties, synonyms |
| Safety | alert-circle, shield, ambulance | health_impacts, emergency |
| Environmental | leaf, droplet, cloud | environmental_impact |
| Detection | search, activity, eye | methods, monitoring |
| Interactions | arrow-right, link, package | produced_from, found_on |
| Operational | message-circle, lightbulb, briefcase | expert_answers, applications |

---

## Variant Usage

| Variant | Purpose | Typical Use Cases |
|---------|---------|-------------------|
| `default` | Standard informational content | Most sections |
| `warning` | Caution-level safety information | Health impacts, exposure guidance |
| `danger` | Critical safety information | Emergency procedures, severe hazards |

---

## Export Task Dependencies

### Task Execution Order (Compounds Example)

**ARCHITECTURE (Core Principle 0.6 - Jan 5, 2026):**
- Section metadata (_section) MUST exist in source data BEFORE export
- Source enrichment: `scripts/enrichment/add_section_metadata_to_source.py`
- Export task preserves existing _section metadata from source

1. **normalize_compounds**: Consolidate scattered fields into structured relationships
2. **remove_duplicate_safety_fields**: Remove legacy field names (health_effects, ppe_requirements, etc.)
3. **section_metadata**: Preserve display metadata (sectionTitle, sectionDescription, icon, order) from source
4. **enrich_relationships**: Add cross-domain relationship metadata

---

## Adding New Sections

**REQUIRED: Section metadata must be in source data (Core Principle 0.6)**

To add a new section to any domain:

1. **Define in source YAML** (`data/{domain}/{Domain}.yaml`):
   ```yaml
   relationships:
     {category}:
       {section_key}:
         _section:  # MUST include sectionTitle, sectionDescription
           sectionTitle: "Display Title"
           sectionDescription: "Optional description"
           icon: lucide-icon-name
           order: 1
           variant: default
           sectionMetadata:  # Optional internal notes
             notes: "Implementation details"
         # ... section data (items, presentation, etc.)
   ```

2. **Define metadata config** (`export/config/{domain}.yaml`) - for enrichment reference:
   ```yaml
   section_metadata:
     {category}.{section_key}:
       section_title: "Display Title"  # Note: Config uses snake_case
       section_description: "Optional description"
       icon: lucide-icon-name
       order: 1
       variant: default
       section_metadata:  # Optional internal developer notes
         notes: "Implementation details"
   ```

3. **Enrich source data** (if adding to existing items):
   ```bash
   python3 scripts/enrichment/add_section_metadata_to_source.py
   ```
   ```bash
   python3 run.py --export --domain {domain}
   ```

---

## Section Metadata Generation

Section metadata is applied during export via the `add_section_metadata` task:

**Task**: `add_section_metadata`  
**Handler**: `_task_add_section_metadata`  
**Location**: `export/generation/universal_content_generator.py`

**Process**:
1. Load section metadata from domain config
2. For each relationship section in frontmatter
3. Apply display fields: section_title, section_description, icon, order, variant
4. Apply internal metadata (if configured)
5. Log metadata application

**Note**: Internal `section_metadata` field is preserved in config for developer reference but typically not exported to frontmatter (frontend doesn't need it).

---

## Cross-Domain Consistency

### Common Sections Across Domains

**expert_answers**:
- **Domains**: Materials, Settings, Contaminants, Compounds
- **Category**: operational
- **Format**: Collapsible (Q&A)
- **Feature**: auto_open_first item
- **Purpose**: Consistent expert insight presentation

### Domain-Specific Patterns

**Materials**: Focused on applications and contamination
**Settings**: Focused on compatibility and prevention
**Contaminants**: Comprehensive safety and detection focus
**Compounds**: Most detailed, covers identity through safety

---

## Future Enhancements

### Planned Sections

- **quality_control** category: Quality standards, testing procedures
- **performance** category: Performance metrics, benchmarks

### Potential Improvements

1. **Auto-generated section descriptions**: Use AI to generate descriptions from section content
2. **Section analytics**: Track most-viewed sections for UX optimization
3. **Dynamic section ordering**: User-configurable section display order
4. **Section templates**: Reusable templates for common section structures

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-04 | 1.0 | Initial registry creation with comprehensive section catalog |

---

## References

- **Export Configuration**: `export/config/*.yaml`
- **Section Metadata Task**: `export/generation/universal_content_generator.py` (line 95, 1247-1290)
- **Frontmatter Examples**: `frontmatter/{domain}/*.yaml`
- **Source Data**: `data/{domain}/{Domain}.yaml`
