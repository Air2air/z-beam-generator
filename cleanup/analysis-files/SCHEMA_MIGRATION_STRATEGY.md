# Schema Reconciliation Migration Strategy

## Overview

The schema reconciliation has successfully unified field naming and structures across all four schemas. However, existing data needs to be migrated to work with the updated schemas. This document outlines the migration strategy.

## Migration Requirements

### 1. Materials.yaml Data Migration

**Issues Identified:**
- 1,194+ validation errors
- Missing required fields in `material_index` entries
- Unexpected top-level properties
- Field naming mismatches

**Required Changes:**

#### A. Material Index Entries
Every material in `material_index` needs:
```yaml
MaterialName:
  category: "metal"           # Already exists
  subcategory: "ferrous"      # Already exists  
  complexity: "medium"        # NEW - needs to be added
  author_id: 1               # NEW - needs to be added
  index: 0                   # May be missing
```

#### B. Remove Unexpected Properties
```yaml
# Remove these top-level properties:
defaults: ...        # Move to appropriate sections
metadata: ...        # Move to appropriate sections  
parameter_templates: # Move to appropriate sections
```

#### C. Field Name Updates (Snake_case → camelCase)
```yaml
# In Material definitions:
thermal_conductivity → thermalConductivity
thermal_expansion → thermalExpansion
tensile_strength → tensileStrength
youngs_modulus → youngsModulus
electrical_resistivity → electricalResistivity
regulatory_standards → regulatoryStandards

# In MachineSettings:
pulse_duration → pulseDuration
fluence_threshold → fluenceThreshold
power_range → powerRange
repetition_rate → repetitionRate
spot_size → spotSize
laser_type → laserType
ablation_threshold → ablationThreshold
thermal_damage_threshold → thermalDamageThreshold
processing_speed → processingSpeed
surface_roughness_change → surfaceRoughnessChange

# In Compatibility:
laser_types → laserTypes
surface_treatments → surfaceTreatments
incompatible_conditions → incompatibleConditions
```

### 2. Frontmatter Files Migration

**Issues Identified:**
- Missing required `materialProperties` and `laserProcessing` hierarchical structures
- `keywords` field expects string but receives array
- Legacy flat structure vs. new hierarchical structure

**Required Changes:**

#### A. Add Missing Required Fields
```yaml
# Add to every frontmatter file:
materialProperties:
  chemical:
    formula: "..."
    symbol: "..."
  physical:
    density: 2.7
    densityUnit: "g/cm³"
  thermal:
    thermalConductivity: 237
    thermalConductivityUnit: "W/m·K"

laserProcessing:
  recommended:
    wavelength: 1064
    wavelengthUnit: "nm" 
  thresholds:
    spotSize: 0.5
    spotSizeUnit: "mm"
  compatibility:
    laserTypes: ["Fiber Laser"]
```

#### B. Convert Keywords Array to String
```yaml
# Change from:
keywords: ['keyword1', 'keyword2', 'keyword3']

# To:
keywords: "keyword1, keyword2, keyword3"
```

## Migration Implementation Strategy

### Phase 1: Automated Field Renaming
1. Create migration script to rename all snake_case fields to camelCase
2. Update all existing Materials.yaml entries systematically
3. Update all frontmatter files with field name changes

### Phase 2: Data Structure Migration  
1. Convert flat properties to hierarchical `materialProperties` structure
2. Convert flat machine settings to hierarchical `laserProcessing` structure
3. Migrate `keywords` arrays to comma-separated strings

### Phase 3: Missing Data Population
1. Add `complexity` and `author_id` to all `material_index` entries
2. Add required hierarchical structures to frontmatter files
3. Populate missing fields with appropriate default values

### Phase 4: Validation and Testing
1. Re-run validation tests against updated data
2. Test content generation with migrated data
3. Verify no functionality breaks

## Migration Script Structure

```python
class SchemaMigration:
    def migrate_materials_yaml(self):
        # 1. Load Materials.yaml
        # 2. Rename snake_case fields to camelCase
        # 3. Add missing required fields to material_index
        # 4. Remove unexpected top-level properties
        # 5. Save updated Materials.yaml
    
    def migrate_frontmatter_files(self):
        # 1. Process each .md file in frontmatter directory
        # 2. Convert keywords array to string
        # 3. Create hierarchical materialProperties structure
        # 4. Create hierarchical laserProcessing structure  
        # 5. Save updated frontmatter files
    
    def validate_migration(self):
        # 1. Run schema validation on migrated data
        # 2. Report success/failure status
        # 3. List any remaining issues
```

## Backward Compatibility Considerations

### Option 1: Breaking Change (Recommended)
- Migrate all existing data to new schema format
- Update all generators and components to use new field names
- Faster, cleaner implementation
- Requires coordination across all system components

### Option 2: Dual Support (Temporary)
- Support both old and new field names during transition period
- Add compatibility layer in generators
- More complex implementation
- Allows gradual migration

## Recommended Approach

**Phase 1: Create Migration Scripts** ✅ 
**Phase 2: Test Migration on Sample Data** ✅
**Phase 3: Full Data Migration** ✅
**Phase 4: Update Components and Generators** 
**Phase 5: Remove Legacy Support**

## Migration Timeline

1. **Week 1**: Create and test migration scripts
2. **Week 2**: Execute full data migration  
3. **Week 3**: Update generators and components
4. **Week 4**: Final validation and cleanup

## Risk Mitigation

1. **Data Backup**: Full backup before migration
2. **Rollback Plan**: Ability to restore previous state
3. **Incremental Testing**: Test each migration step
4. **Validation Gates**: Ensure data integrity at each phase

## Success Criteria

- ✅ All schemas pass JSON syntax validation
- ✅ Materials.yaml validates against Materials_yaml.json (0 errors)
- ✅ All frontmatter files validate against frontmatter.json (0 errors) 
- ✅ Content generation works with migrated data
- ✅ No functionality regressions

---

**Next Step**: Implement automated migration scripts to execute this strategy.