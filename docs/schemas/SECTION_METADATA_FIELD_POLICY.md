# Section Metadata Field Policy

**Status**: Active Policy (January 13, 2026)  
**Schema File**: `data/schemas/section_display_schema.yaml` (sections.* entries)  
**Applies To**: All relationship sections across all domains

**🚨 MANDATORY REQUIREMENT**: Every section in exported frontmatter MUST have:
- `sectionTitle` - Section heading/title displayed in UI
- `sectionDescription` - Generated contextual content about the section
- `sectionMetadata` - Technical metadata for the section

**Note**: `data/schemas/section_display_schema.yaml` is the authoritative schema source used by generation and export pipelines.

---

## 📖 Overview

Section metadata in `section_display_schema.yaml` defines three distinct fields with different purposes and export behaviors. Understanding these distinctions is critical for proper schema usage and export generation.

---

## 🚨 MANDATORY REQUIREMENTS

**EVERY SECTION** in exported frontmatter must have these three fields populated:

### 1. sectionTitle (REQUIRED)
- **Source**: `sections.{section_key}.description` field from section_display_schema.yaml
- **Export As**: `_section.sectionTitle`
- **Purpose**: Human-readable section heading displayed in UI
- **Validation**: Must be present and non-empty, maximum 5 words
- **Example**: "Common Contaminants", "Industry Applications"

### 2. sectionDescription (REQUIRED)
- **Source**: AI-generated content using prompt resolution via `PromptRegistryService` from schema `prompt_ref` (preferred) or `prompt`/`prompt_file` fallback
- **Export As**: `_section.sectionDescription`
- **Purpose**: Contextual description explaining what the section contains
- **Validation**: Must be present and non-empty, minimum 5 words
- **Example**: "This section details the most frequently encountered contaminants found on aluminum surfaces during industrial operations."

### 3. sectionMetadata (REQUIRED)
- **Source**: `sections.{section_key}.metadata` field from section_display_schema.yaml
- **Export As**: `_section.sectionMetadata`
- **Purpose**: Technical metadata for export processing and UI behavior
- **Validation**: Must be present and non-empty
- **Example**: "contaminatedBy:relationships:safety"

### Enforcement

**Test Validation**: `test_mandatory_section_metadata_in_frontmatter()` verifies all three fields are present and properly populated in exported frontmatter.

**Export Failure**: If any section lacks required fields, the export process should fail with clear error messages indicating which section and which field is missing.

**Schema Compliance**: All sections must include required display metadata (`icon`, `order`, `variant`) and either `prompt_ref` (preferred) or `prompt`/`prompt_file` for generation-time prompt resolution.

---

## 🎯 Field Definitions

### 1. `description` - Section Title (EXPORTED)

**Purpose**: Section heading/title displayed in the frontend UI  
**Export Behavior**: ✅ EXPORTED to frontmatter `_section.sectionTitle`  
**Content Format**: Short title (2-4 words)  
**Usage**: Frontend display, UI navigation, section headers

**Examples**:
- `"Common Contaminants"` (not "Lists of common contaminants found on this material")
- `"Regulatory Standards"` (not "Regulatory compliance requirements")
- `"Industry Applications"` (not "Industries where this is used")

### 2. `metadata` - Internal Reference (NOT EXPORTED)

**Purpose**: Documentation describing what the section contains and why  
**Export Behavior**: ❌ NOT EXPORTED - internal reference only  
**Content Format**: Single descriptive sentence  
**Usage**: Developer documentation, schema understanding, content guidelines

**Examples**:
- `"Lists contaminants that commonly appear on this material during use and storage, explaining why they cause problems and how they accumulate"`
- `"OSHA, ANSI, and ISO compliance requirements governing handling and workplace safety"`
- `"Industries and sectors where commonly encountered, including specific processes and application suitability"`

### 3. `prompt_ref` / `prompt` / `prompt_file` - Generation Prompt Source (NOT EXPORTED)

**Purpose**: Instructions for AI content generation  
**Export Behavior**: ❌ NOT EXPORTED - generation-time only  
**Content Format**: Reference-based prompt lookup (preferred) or inline/file fallback  
**Usage**: Content generation, AI prompts, data population via `PromptRegistryService`

**Examples**:
- `prompt_ref: "contaminatedBy"`
- `prompt_ref: "regulatoryStandards"`
- `prompt_ref: "industryApplications"`

---

## 📋 Complete Field Structure

```yaml
# In data/schemas/section_display_schema.yaml
sections:
  interactions.contaminatedBy:
    wordCount: 50                   # Generation word count target
    icon: droplet                   # Visual icon identifier
    order: 10                       # Display order
    variant: default                # Visual variant (default/warning/danger)
    description: "Common Contaminants"  # ✅ EXPORTED - Section title
    metadata: "Lists contaminants that commonly appear on this material during use and storage, explaining why they cause problems and how they accumulate"  # ❌ NOT EXPORTED - Internal reference
    prompt_ref: contaminatedBy  # ❌ NOT EXPORTED - Generation prompt source (preferred)
```

---

## 🚦 Export Behavior Summary

| Field | Exported? | Frontend Display? | Purpose |
|-------|-----------|-------------------|---------|
| `icon` | ✅ Yes | ✅ Yes | Section icon |
| `order` | ✅ Yes | No | Sort order |
| `variant` | ✅ Yes | ✅ Yes | Visual styling |
| `description` | ✅ Yes | ✅ Yes | Section title |
| `metadata` | ❌ No | ❌ No | Documentation |
| `prompt_ref` / `prompt` / `prompt_file` | ❌ No | ❌ No | Generation |

**In Exported Frontmatter**:
```yaml
relationships:
  interactions:
    contaminatedBy:
      _section:
        sectionTitle: "Common Contaminants"  # From description field
        sectionDescription: "..."            # Generated content (NOT from metadata!)
        icon: droplet
        order: 10
        variant: default
```

**Note**: `sectionDescription` in frontmatter is GENERATED CONTENT about the items in that section, NOT a copy of the metadata field!

---

## ✅ Compliance Requirements

### For Schema Updates:
- ✅ `description` must be short title (2-4 words)
- ✅ `metadata` must be single descriptive sentence
- ✅ define generation source using `prompt_ref` (preferred) or `prompt`/`prompt_file`
- ❌ DO NOT put long sentences in `description` field
- ❌ DO NOT export `metadata` field to frontmatter
- ❌ DO NOT confuse `metadata` with `sectionDescription` (they're different!)

### For Export Code:
- ✅ Read `description` field for `sectionTitle` in frontmatter
- ✅ Ignore `metadata` field during export (internal documentation only)
- ✅ Use prompt source fields (`prompt_ref`/`prompt`/`prompt_file`) only during content generation phase
- ❌ DO NOT export `metadata` to frontmatter
- ❌ DO NOT use `metadata` as `sectionDescription` (that's generated content!)

### For Test Code:
- ✅ Verify `description` contains short title (not sentence)
- ✅ Verify `metadata` exists but is NOT in exported frontmatter
- ✅ Verify `sectionTitle` in frontmatter matches `description` from schema
- ❌ DO NOT expect `metadata` field in exported frontmatter
- ❌ DO NOT validate `metadata` against `sectionDescription` (they're unrelated)

---

## 🔍 Common Mistakes to Avoid

### ❌ WRONG: Long sentence in description
```yaml
description: "Lists contaminants that commonly appear on this material"
# This should be in metadata field instead!
```

### ✅ CORRECT: Short title in description
```yaml
description: "Common Contaminants"
metadata: "Lists contaminants that commonly appear on this material during use and storage"
```

### ❌ WRONG: Exporting metadata to frontmatter
```python
section_meta = {
    'sectionTitle': schema['description'],
    'metadata': schema['metadata']  # ❌ Should not export this!
}
```

### ✅ CORRECT: Only exporting display fields
```python
section_meta = {
    'sectionTitle': schema['description'],  # ✅ Short title
    'icon': schema['icon'],
    'order': schema['order'],
    'variant': schema['variant']
    # metadata and prompt source fields are NOT exported
}
```

### ❌ WRONG: Confusing metadata with sectionDescription
```yaml
# In frontmatter - these are DIFFERENT things!
_section:
  sectionTitle: "Common Contaminants"  # From schema description field
  sectionDescription: "..."             # GENERATED content about items
  # metadata field does NOT appear here - it's internal to schema
```

---

## 📝 Section Inventory

**Total Sections**: 24 across 7 groups

### Interactions (6 sections)
- `interactions.contaminatedBy`
- `interactions.producedByMaterials`
- `interactions.producedFromContaminants`
- `interactions.relatedContaminants`
- `interactions.relatedCompounds`
- `interactions.reactivity`

### Safety (7 sections)
- `safety.regulatoryStandards`
- `safety.healthEffects`
- `safety.ppeRequirements`
- `safety.emergencyResponse`
- `safety.exposureLimits`
- `safety.storageRequirements`
- `safety.regulatoryClassification`

### Operational (5 sections)
- `operational.industryApplications`
- `operational.commonChallenges`
- `operational.removalMethods`
- `operational.detectionMethods`
- `operational.preventionStrategies`

### Environmental (1 section)
- `environmental.environmentalImpact`

### Visual (1 section)
- `visual.appearanceVariations`

### Identity (2 sections)
- `identity.chemicalProperties`
- `identity.physicalProperties`
- `identity.synonymsIdentifiers`

### Detection & Monitoring (1 section)
- `detectionMonitoring.detectionMonitoring`

---

## 🔧 Implementation Files

### Schema Definition
- `data/schemas/section_display_schema.yaml` (sections.* entries) - Authoritative source for all section metadata

### Export Code (Reads schema)
- `export/enrichers/section_metadata_enricher.py` - Adds _section blocks during export
- `export/generation/universal_content_generator.py` - Section metadata task
- `export/config/*.yaml` - Export configurations using schema

### Test Files (Validation)
- `tests/test_comprehensive_standard_compliance.py` - Validates section metadata structure
- `tests/unit/test_section_metadata.py` - Unit tests for schema structure (if exists)

### Scripts (Maintenance)
- `scripts/enrichment/enrich_section_metadata.py` - Enriches source data from schema
- `scripts/data/test_section_metadata_generation.py` - Tests schema loading

---

## 📚 Related Documentation

- `.github/copilot-instructions.md` - Core Principle 0.6: Generate to Data, Not Enrichers
- `docs/08-development/FRONTMATTER_SOURCE_OF_TRUTH_POLICY.md` - Layer architecture
- `FRONTMATTER_OPTIMIZATION_GUIDE.md` - Field usage and optimization strategy

---

## 🎓 Summary

**Remember**:
- `description` = **Short title** (EXPORTED to UI)
- `metadata` = **Internal docs** (NOT exported, reference only)
- `prompt` = **Generation instructions** (NOT exported, generation-time only)

**The metadata field is for human developers to understand what a section contains. It is NOT exported to frontmatter and is NOT the same as sectionDescription (which is generated content about the actual items in that section).**

---

**Policy Enforcement**: MANDATORY  
**Grade for Violations**: Policy non-compliance (affects system correctness)  
**Last Updated**: January 8, 2026
