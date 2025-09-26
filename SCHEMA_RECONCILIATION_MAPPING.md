# Schema Reconciliation Mapping

## Overview

This document maps field relationships across all four Z-Beam Generator schemas and identifies conflicts that need resolution.

## Schema Hierarchy

```
base.json (Foundation)
├── material.json (Material Profiles) 
├── frontmatter.json (Output Structure)
└── materials_yaml.json (Database Structure)
```

## Field Mapping Analysis

### 1. Core Identity Fields

| Purpose | base.json | material.json | frontmatter.json | materials_yaml.json |
|---------|-----------|---------------|------------------|---------------------|
| Name | `name` | `profile.category` | `name` | `Material.name` |
| Category | - | `profile.category` | `category` | `Material.category` |
| Subcategory | - | - | `subcategory` | `material_index.subcategory` |
| Description | `description` | - | `description` | `Material.description` |

**Issues:**
- Missing category/subcategory in base and material schemas
- Description field inconsistency

### 2. Author Information

| Purpose | base.json | material.json | frontmatter.json | materials_yaml.json |
|---------|-----------|---------------|------------------|---------------------|
| Author Object | `author` | `author_object` | `author_object` | - |
| Author ID | `author.author_id` | `author_object.id` | `author_id` | `Material.author_id` |
| Author Name | `author.author_name` | `author_object.name` | `author_object.name` | - |
| Country | `author.author_country` | `author_object.country` | `author_object.country` | - |

**Issues:**
- Different field names (`author_id` vs `id`)
- Missing author metadata in materials_yaml.json

### 3. Material Properties

| Purpose | base.json | material.json | frontmatter.json | materials_yaml.json |
|---------|-----------|---------------|------------------|---------------------|
| Density | - | `properties.density` | `properties.density` OR `materialProperties.physical.density` | `Material.density` |
| Thermal Conductivity | - | `properties.thermalConductivity` | `properties.thermalConductivity` OR `materialProperties.thermal.thermalConductivity` | `Material.thermal_conductivity` |
| Chemical Formula | - | `chemicalProperties.formula` | `chemicalProperties.formula` OR `materialProperties.chemical.formula` | `Material.formula` |

**Issues:**
- Frontmatter.json has dual structure (legacy flat + new hierarchical)
- Field naming inconsistencies (`thermal_conductivity` vs `thermalConductivity`)
- Missing properties in base.json

### 4. Laser Processing Settings

| Purpose | base.json | material.json | frontmatter.json | materials_yaml.json |
|---------|-----------|---------------|------------------|---------------------|
| Wavelength | - | `technicalSpecifications.wavelength` | `machineSettings.wavelength` OR `laserProcessing.recommended.wavelength` | `Material.machine_settings.wavelength_optimal` |
| Power Range | - | `technicalSpecifications.powerRange` | `machineSettings.powerRange` OR `laserProcessing.recommended.powerRange` | `Material.machine_settings.power_range` |
| Fluence | - | `technicalSpecifications.fluenceRange` | `machineSettings.fluenceRange` OR `laserProcessing.recommended.fluenceRange` | `Material.machine_settings.fluence_threshold` |

**Issues:**
- Multiple naming conventions for same fields
- Hierarchical vs flat structures
- Missing laser settings in base.json

### 5. Applications & Industries

| Purpose | base.json | material.json | frontmatter.json | materials_yaml.json |
|---------|-----------|---------------|------------------|---------------------|
| Applications | `applications` | `applications` | `applications` | `Material.applications` |
| Industry Tags | - | `industryTags` | `industryTags` | `Material.industry_tags` |
| Primary Industries | - | `primaryIndustries` | `primaryIndustries` | - |

**Issues:**
- Missing industry fields in base.json and materials_yaml.json
- Inconsistent application object structures

### 6. Regulatory & Compliance

| Purpose | base.json | material.json | frontmatter.json | materials_yaml.json |
|---------|-----------|---------------|------------------|---------------------|
| Standards | `regulatoryStandards` | - | `regulatoryStandards` | `Material.regulatory_standards` |

**Issues:**
- Different field names (`regulatoryStandards` vs `regulatory_standards`)
- Different data types (object array vs string array)
- Missing in material.json

### 7. Environmental Impact

| Purpose | base.json | material.json | frontmatter.json | materials_yaml.json |
|---------|-----------|---------------|------------------|---------------------|
| Environmental Benefits | `environmentalImpact` | `environmentalImpact` | `environmentalImpact` | - |

**Issues:**
- Missing environmental fields in materials_yaml.json
- Inconsistent object structures

### 8. SEO & Content Fields

| Purpose | base.json | material.json | frontmatter.json | materials_yaml.json |
|---------|-----------|---------------|------------------|---------------------|
| Keywords | `keywords` | - | `keywords` | `Material.keywords` |
| Tags | `tags` | - | `tags` | - |
| Title | - | `title` | `title` | `Material.title` |
| Headline | - | `headline` | `headline` | `Material.headline` |

**Issues:**
- Missing SEO fields in base.json
- Inconsistent field presence across schemas

## Critical Conflicts Identified

### 1. **Field Naming Convention Conflicts**
```
thermal_conductivity (materials_yaml.json)
vs
thermalConductivity (material.json, frontmatter.json)
```

### 2. **Data Type Conflicts**
```
regulatoryStandards: array of objects (base.json)
vs
regulatoryStandards: string or array of strings (frontmatter.json)
vs  
regulatory_standards: array of strings (materials_yaml.json)
```

### 3. **Structure Hierarchy Conflicts**
```
Flat: properties.density (legacy frontmatter.json)
vs
Hierarchical: materialProperties.physical.density (new frontmatter.json)
```

### 4. **Missing Critical Fields**
- `category` and `subcategory` missing from base.json and material.json
- Author information missing from materials_yaml.json
- Laser processing settings missing from base.json

## Recommended Reconciliation Strategy

### Phase 1: Establish Common Field Naming
1. Standardize on camelCase: `thermalConductivity` not `thermal_conductivity`
2. Unify regulatory field: `regulatoryStandards` as object array
3. Consistent author structure: `authorObject` with `id`, `name`, `country`

### Phase 2: Align Data Structures  
1. Adopt hierarchical approach from frontmatter.json
2. Implement `materialProperties` structure in all schemas
3. Standardize `laserProcessing` hierarchy

### Phase 3: Complete Field Coverage
1. Add missing category/subcategory to base.json and material.json
2. Add author metadata to materials_yaml.json
3. Add laser processing to base.json
4. Add environmental impact to materials_yaml.json

### Phase 4: Validation Alignment
1. Align required/optional field designations
2. Standardize enum values across all schemas
3. Implement cross-schema validation rules

## Implementation Priority

**HIGH PRIORITY (Breaking Changes)**
1. Field naming standardization
2. Data type conflicts resolution
3. Required field alignment

**MEDIUM PRIORITY (Enhancement)**
1. Structure hierarchy alignment
2. Missing field additions
3. Enum standardization

**LOW PRIORITY (Optimization)**
1. Validation enhancement
2. Documentation updates
3. Default value alignment

## Next Steps

1. Create unified field mapping specification
2. Update each schema systematically
3. Test against existing data
4. Update generators and validators
5. Document migration path for existing code

---

*This mapping serves as the foundation for schema reconciliation and ensures data consistency across the Z-Beam Generator system.*