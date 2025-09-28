# Frontmatter Data Sources Documentation

## Overview

This document defines the authoritative data sources for all frontmatter fields to ensure compliance with GROK_INSTRUCTIONS.md fail-fast principles. No fallbacks, mocks, or AI-generated values are allowed where explicit source data exists.

## Data Source Hierarchy

### 1. Categories.yaml (Primary Configuration Source)
**Location**: `data/Categories.yaml`
**Purpose**: Authoritative source for material property ranges, environmental templates, application definitions, and system-wide standards.

#### Sections and Usage:

- **`category_ranges`**: Material property min/max values by category
  - **Used for**: `materialProperties.*.min` and `materialProperties.*.max`
  - **Rule**: Properties WITH category_ranges MUST use these values
  - **Rule**: Properties WITHOUT category_ranges MUST have `min: null, max: null`
  - **Enforcement**: No AI-generated or calculated min/max values allowed

- **`environmentalImpactTemplates`**: Predefined environmental benefit templates
  - **Used for**: `environmentalImpact[].benefit` names and descriptions
  - **Rule**: Benefits MUST correspond to template keys (e.g., `chemical_waste_elimination` → "Chemical Waste Elimination")

- **`applicationTypeDefinitions`**: Standard application type definitions
  - **Used for**: `applicationTypes[].type` names and properties
  - **Rule**: Application types MUST correspond to definition keys (e.g., `precision_cleaning` → "Precision Cleaning")

- **`standardOutcomeMetrics`**: Standard outcome metric definitions
  - **Used for**: `outcomeMetrics[].metric` names and properties
  - **Rule**: Metrics MUST correspond to standard keys (e.g., `contaminant_removal_efficiency` → "Contaminant Removal Efficiency")

- **`machineSettingsDescriptions`**: Machine setting definitions with units
  - **Used for**: `machineSettings` unit extraction and validation
  - **Rule**: All machine settings MUST have corresponding descriptions with units

- **`materialPropertyDescriptions`**: Material property definitions
  - **Used for**: Property validation and unit extraction
  - **Rule**: All properties MUST have corresponding descriptions

- **`universal_regulatory_standards`**: Standard regulatory compliance references
  - **Used for**: `regulatoryStandards` array
  - **Rule**: Universal standards MUST be included in all materials

### 2. Materials.yaml (Material-Specific Data)
**Location**: `data/Materials.yaml`
**Purpose**: Material-specific data including categories, industry applications, and machine settings ranges.

#### Sections and Usage:

- **`material_index`**: Material name to category mapping
  - **Used for**: Determining which category_ranges to apply
  - **Rule**: Every material MUST have a defined category

- **`machineSettingsRanges`**: Material-specific machine setting ranges
  - **Used for**: `machineSettings.*.min` and `machineSettings.*.max`
  - **Rule**: MUST be used when available, fail-fast if missing for required settings

### 3. AI Generation (Controlled Research Only)
**Purpose**: Generate specific property values and descriptions within Categories.yaml constraints.
**Restrictions**: 
- **ALLOWED**: Property values, descriptions, confidence scores within defined ranges
- **FORBIDDEN**: Min/max ranges, benefit names, application types, metric names
- **Rule**: AI content MUST be validated against Categories.yaml templates and ranges

## File Naming Conventions

### Frontmatter Output Files
All frontmatter files are generated with consistent naming conventions:
- **Pattern**: `{material-name}-laser-cleaning.yaml`
- **Space Handling**: All spaces in material names are replaced with hyphens (`-`)
- **Case**: Material names are converted to lowercase
- **Examples**:
  - "Stainless Steel" → `stainless-steel-laser-cleaning.yaml`
  - "Borosilicate Glass" → `borosilicate-glass-laser-cleaning.yaml`
  - "Carbon Fiber Reinforced Polymer" → `carbon-fiber-reinforced-polymer-laser-cleaning.yaml`

### Implementation
The filename generation logic ensures consistent naming across all components:
```python
filename = material_name.lower().replace(' ', '-').replace('_', '-')
output_file = f"{output_dir}/{filename}-laser-cleaning.yaml"
```

## Field-by-Field Data Source Map

| Frontmatter Field | Source | Enforcement Level |
|------------------|--------|------------------|
| `name` | Material name input | Required |
| `category` | Materials.yaml material_index | Required |
| `materialProperties.*.min` | Categories.yaml category_ranges | Strict - No AI generation |
| `materialProperties.*.max` | Categories.yaml category_ranges | Strict - No AI generation |
| `materialProperties.*.value` | AI Research | Validated within ranges |
| `materialProperties.*.unit` | Categories.yaml category_ranges | Required |
| `materialProperties.*.description` | AI Research | Generated |
| `materialProperties.*.confidence` | Calculated from data quality | No defaults |
| `machineSettings.*.min` | Materials.yaml machineSettingsRanges | Required |
| `machineSettings.*.max` | Materials.yaml machineSettingsRanges | Required |
| `machineSettings.*.unit` | Categories.yaml machineSettingsDescriptions | Required |
| `environmentalImpact[].benefit` | Categories.yaml environmentalImpactTemplates | Strict - Must match templates |
| `environmentalImpact[].description` | Categories.yaml environmentalImpactTemplates | Template-based |
| `applicationTypes[].type` | Categories.yaml applicationTypeDefinitions | Strict - Must match definitions |
| `applicationTypes[].description` | Categories.yaml applicationTypeDefinitions | Template-based |
| `outcomeMetrics[].metric` | Categories.yaml standardOutcomeMetrics | Strict - Must match standards |
| `outcomeMetrics[].description` | Categories.yaml standardOutcomeMetrics | Template-based |
| `regulatoryStandards` | Categories.yaml universal_regulatory_standards | Required inclusion |
| `author_id` | AI Research | Generated |
| `images` | AI Research | Generated |

## Compliance Rules

### Fail-Fast Principles
1. **No Fallback Values**: If Categories.yaml data is missing, system MUST fail
2. **No Default Ranges**: Min/max values MUST come from category_ranges or be null
3. **No Mock Data**: All API clients must be real, no mock responses
4. **Explicit Dependencies**: All required data sources must be validated on startup

### Data Source Validation
1. **Categories.yaml Structure**: All required sections must exist and be well-formed
2. **Materials.yaml Integrity**: All materials must have valid category mappings
3. **Template Compliance**: Generated content must strictly follow template structures
4. **Unit Consistency**: All numeric fields must have proper units from source data

### Testing Requirements
1. **Source Compliance Tests**: Verify all fields use correct data sources
2. **Template Matching Tests**: Ensure generated content matches Categories.yaml templates
3. **Range Validation Tests**: Confirm min/max values come from category_ranges
4. **Fail-Fast Tests**: Validate system fails when source data is missing

## Implementation Notes

### Generator Responsibilities
- Load and validate all source data on initialization
- Fail immediately if required data sources are missing
- Use explicit data source mapping for all fields
- No silent fallbacks or default value generation

### API Research Boundaries
- Generate content WITHIN defined constraints only
- Never generate structural data (ranges, templates, standards)
- Validate all generated content against source templates
- Fail if generated content doesn't match expected patterns

### Configuration Loading
- Validate file existence before loading
- Check for required sections and fail if missing
- Load data into typed structures with validation
- Cache loaded data for performance

## Migration and Updates

### Adding New Fields
1. Define source in Categories.yaml if structural
2. Add field to data source map
3. Implement source validation
4. Add compliance tests

### Modifying Existing Sources
1. Update Categories.yaml with new structure
2. Update generator to use new structure
3. Update tests to validate new structure
4. Document changes in this file

### Version Control
- Categories.yaml changes require version bump
- Data source documentation must be updated with changes
- All tests must pass before merging changes
- Generator must validate data source versions

## Examples

### Correct Min/Max Usage
```yaml
# Material: copper (category: metal)
materialProperties:
  density:
    value: 8.96        # AI-generated
    min: 0.53         # From Categories.yaml metal.category_ranges.density.min
    max: 22.6         # From Categories.yaml metal.category_ranges.density.max
    unit: g/cm³       # From Categories.yaml metal.category_ranges.density.unit
```

### Correct Template Usage
```yaml
# Environmental impact using Categories.yaml templates
environmentalImpact:
  - benefit: Chemical Waste Elimination  # From environmentalImpactTemplates.chemical_waste_elimination
    description: Eliminates hazardous chemical waste streams  # From template
```

### Incorrect Usage (Violations)
```yaml
# ❌ WRONG: AI-generated min/max values
materialProperties:
  density:
    min: 8.5    # ❌ Should be 0.53 from Categories.yaml
    max: 9.2    # ❌ Should be 22.6 from Categories.yaml

# ❌ WRONG: Non-template environmental benefit  
environmentalImpact:
  - benefit: Cost Savings  # ❌ Not in environmentalImpactTemplates
```

## Summary

This data source specification ensures:
- ✅ Complete traceability of all frontmatter field sources
- ✅ Elimination of AI-generated structural data
- ✅ Strict compliance with Categories.yaml templates  
- ✅ Fail-fast behavior when source data is missing
- ✅ Comprehensive testing of data source compliance

All frontmatter generation must follow these data source rules to maintain system integrity and comply with GROK_INSTRUCTIONS.md principles.