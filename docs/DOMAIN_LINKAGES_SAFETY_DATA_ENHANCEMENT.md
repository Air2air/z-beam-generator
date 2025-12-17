# Domain Linkages Safety Data Enhancement Proposal

**Date**: December 16, 2025  
**Implementation Date**: December 17, 2025  
**Status**: ✅ IMPLEMENTED (Phase 1 & 2)  
**Scope**: Enhance all `domain_linkages` structures in contaminant and compound frontmatter  
**Goal**: Create unified data structure combining navigational links with safety/technical metrics  
**Priority**: HIGH - Enables richer UI components and eliminates data duplication

---

## ✅ Implementation Status (December 17, 2025)

**COMPLETED:**
- ✅ Schema definition and validation
- ✅ Migration script created (`scripts/migrate_domain_linkages_safety_data.py`)
- ✅ 24 contaminant files enhanced with safety data fields
- ✅ Test suite created (`tests/test_domain_linkages_safety_enhancement.py`)
- ✅ Migration status tracking in files

**ENHANCED FIELDS ADDED:**
- ✅ `exposure_limits` (OSHA, NIOSH, ACGIH, IDLH)
- ✅ `concentration_range` (min, max, typical)
- ✅ `exceeds_limits` (boolean)
- ✅ `monitoring_required` (boolean)
- ✅ `control_measures` (ventilation, PPE level, filtration)
- ✅ `particulate_properties` (optional, when available)

**REMAINING:**
- ⏳ UI component updates (Phase 3)
- ⏳ Legacy code cleanup (Phase 4)
- ⏳ 75 additional contaminants need `produces_compounds` data first

---

## Executive Summary

Currently, contaminant pages maintain **two separate compound lists**:
1. **domain_linkages.produces_compounds** - Navigation data (URLs, images, context)
2. **safety_data.fumes_generated** - Safety data (concentrations, exposure limits)

**Proposal**: Enhance `domain_linkages` to include safety/technical data, creating a **single source of truth** for compound relationships that supports both navigation and regulatory compliance display.

---

## Current State Analysis

### Existing Structure: domain_linkages.produces_compounds
```yaml
domain_linkages:
  produces_compounds:
    - id: acetaldehyde-compound
      title: Acetaldehyde
      url: /compounds/irritant/aldehyde/acetaldehyde-compound
      image: /images/compounds/acetaldehyde.jpg
      category: irritant
      subcategory: aldehyde
      frequency: common           # ✅ Has relationship metadata
      severity: moderate           # ✅ Has severity
      typical_context: Decomposition of vinyl and acrylic adhesives
      exposure_risk: moderate
      # ❌ MISSING: concentration data
      # ❌ MISSING: exposure limits
      # ❌ MISSING: regulatory data
```

### Existing Structure: safety_data.fumes_generated
```yaml
safety_data:
  fumes_generated:
    - compound: Acetaldehyde     # ❌ Name only, no id/url
      concentration_mg_m3: 5-25  # ✅ Has concentration
      exposure_limit_mg_m3: 25   # ✅ Has exposure limit
      hazard_class: irritant     # ✅ Has hazard class
      # ❌ MISSING: All navigational data
      # ❌ MISSING: Context information
```

### Problems with Current Approach
1. **Data Duplication**: Same compounds listed in two places
2. **Maintenance Burden**: Updates require changes in multiple locations
3. **Inconsistency Risk**: Lists may drift out of sync
4. **Limited UI Options**: Cannot show safety data in domain linkage cards
5. **Missing Connections**: Fumes table cannot link to compound pages

---

## Proposed Enhanced Schema

### Schema Definition

```yaml
domain_linkages:
  produces_compounds:
    - id: string                          # Compound slug (required)
      title: string                       # Display name (required)
      url: string                         # Full URL path (required)
      image: string                       # Hero image path (required)
      category: string                    # Hazard category (required)
      subcategory: string                 # Specific classification (required)
      frequency: enum                     # Occurrence frequency (required)
      severity: enum                      # Overall severity (required)
      typical_context: string             # Context description (required)
      exposure_risk: enum                 # Exposure risk level (required)
      
      # NEW: Safety & Technical Data
      concentration_range:                # Typical concentration (NEW)
        min_mg_m3: number                 # Minimum concentration
        max_mg_m3: number                 # Maximum concentration
        typical_mg_m3: number             # Expected/average value
      exposure_limits:                    # Regulatory limits (NEW)
        osha_pel_mg_m3: number | null     # OSHA Permissible Exposure Limit
        niosh_rel_mg_m3: number | null    # NIOSH Recommended Exposure Limit
        acgih_tlv_mg_m3: number           # ACGIH Threshold Limit Value
        idlh_mg_m3: number | null         # Immediately Dangerous to Life/Health
      exceeds_limits: boolean             # Quick status check (NEW)
      monitoring_required: boolean        # Requires monitoring (NEW)
      particulate_properties:             # Physical properties (NEW, optional)
        respirable_fraction: number       # 0.0-1.0 fraction
        size_range_um: [number, number]   # [min, max] in micrometers
      control_measures:                   # Mitigation requirements (NEW)
        ventilation_required: boolean
        ppe_level: enum                   # none/basic/enhanced/full
        filtration_type: string | null    # HEPA, activated_carbon, etc.
```

### Field Enumerations

```yaml
# frequency: How often this compound is generated
- very_common   # >80% of operations
- common        # 50-80% of operations
- occasional    # 20-50% of operations
- rare          # <20% of operations

# severity: Overall hazard severity
- low           # Minor irritation, no long-term effects
- moderate      # Significant irritation, temporary effects
- high          # Severe health effects possible
- severe        # Life-threatening, permanent damage risk

# exposure_risk: Risk level during typical operations
- low           # Well below exposure limits
- moderate      # Approaches exposure limits
- high          # Exceeds exposure limits
- critical      # Immediately dangerous levels

# ppe_level: Personal protective equipment required
- none          # No special PPE needed
- basic         # Safety glasses, gloves
- enhanced      # Respirator, full coverage
- full          # Full hazmat suit, SCBA
```

---

## Complete Example: Before & After

### BEFORE (Current Structure)

**In domain_linkages**:
```yaml
domain_linkages:
  produces_compounds:
    - id: formaldehyde-compound
      title: Formaldehyde
      url: /compounds/carcinogen/aldehyde/formaldehyde-compound
      image: /images/compounds/formaldehyde.jpg
      category: carcinogen
      subcategory: aldehyde
      frequency: common
      severity: moderate
      typical_context: Thermal breakdown of formaldehyde-based adhesives
      exposure_risk: moderate
```

**In safety_data** (separate section):
```yaml
safety_data:
  fumes_generated:
    - compound: Formaldehyde
      concentration_mg_m3: 1-10
      exposure_limit_mg_m3: 0.3
      hazard_class: carcinogenic
```

### AFTER (Enhanced Structure)

**In domain_linkages only** (unified):
```yaml
domain_linkages:
  produces_compounds:
    - id: formaldehyde-compound
      title: Formaldehyde
      url: /compounds/carcinogen/aldehyde/formaldehyde-compound
      image: /images/compounds/formaldehyde.jpg
      category: carcinogen
      subcategory: aldehyde
      frequency: common
      severity: moderate
      typical_context: Thermal breakdown of formaldehyde-based adhesives
      exposure_risk: moderate
      
      # NEW: Safety & Technical Data
      concentration_range:
        min_mg_m3: 1
        max_mg_m3: 10
        typical_mg_m3: 5
      exposure_limits:
        osha_pel_mg_m3: 0.75
        niosh_rel_mg_m3: null
        acgih_tlv_mg_m3: 0.3
        idlh_mg_m3: 20
      exceeds_limits: true
      monitoring_required: true
      particulate_properties:
        respirable_fraction: 0.9
        size_range_um: [0.1, 5.0]
      control_measures:
        ventilation_required: true
        ppe_level: enhanced
        filtration_type: activated_carbon
```

---

## Implementation Benefits

### 1. Single Source of Truth
- All compound relationship data in one location
- Eliminates duplication and sync issues
- Easier to maintain and update

### 2. Enhanced UI Components
- Domain linkage cards can show concentration warnings
- "Exceeds Limits" badges on cards
- Hover tooltips with exposure data
- Color-coded severity matching actual risk

### 3. Improved User Experience
- Hazardous Fumes Table becomes navigable
- Consistent data across all components
- Richer safety information display
- Better regulatory compliance documentation

### 4. Data Integrity
- Single update point for compound data
- Validation at generation time
- Consistent formatting and units
- Reduced human error

---

## Migration Strategy & Cleanup Plan

### Overview
The migration follows a **4-phase approach** ensuring zero data loss and full backward compatibility during transition.

---

### Phase 1: Schema Extension & Validation (Week 1)

**Objectives**:
- Define complete enhanced schema
- Validate data structure
- Prepare migration tools

**Tasks**:
1. ✅ Add new fields to domain_linkages schema definition
2. ✅ Update TypeScript interfaces in `app/types/domain-linkages.ts`
3. ✅ Create validation script to verify enhanced schema
4. ✅ Test schema with 3 sample contaminants
5. ✅ Document field requirements and constraints
6. ✅ Deploy schema updates to development environment

**Deliverables**:
- Updated schema documentation
- TypeScript type definitions
- Validation script (`scripts/validate-enhanced-linkages.ts`)
- Test results from sample data

**What Happens to fumes_generated?**:
- **No changes yet** - Keep existing structure intact
- Validation script checks both old and new structures coexist

---

### Phase 2: Data Enhancement & Dual-Write (Week 2)

**Objectives**:
- Populate enhanced domain_linkages
- Maintain fumes_generated during transition
- Enable dual-write mode

**Tasks**:
1. ✅ Write migration script (`scripts/migrate-safety-data.py`)
2. ✅ Merge fumes_generated data into produces_compounds
3. ✅ Add concentration/exposure data from compound frontmatter
4. ✅ Calculate derived fields (exceeds_limits, monitoring_required)
5. ✅ Add control measures from safety guidelines
6. ✅ Migrate 5 test contaminants and validate
7. ✅ Migrate remaining contaminants (batch processing)
8. ✅ Run validation checks on all migrated files

**Dual-Write Strategy**:
```yaml
# During Phase 2: BOTH structures exist
domain_linkages:
  produces_compounds:
    - id: formaldehyde-compound
      # ... enhanced fields (NEW)
      concentration_range:
        min_mg_m3: 1
        max_mg_m3: 10
      # ... all new fields

safety_data:
  fumes_generated:  # ⚠️ MAINTAINED during transition
    - compound: Formaldehyde
      concentration_mg_m3: 1-10
      # ... legacy fields
```

**Why Dual-Write?**:
- Components can fall back if new data missing
- Validation can compare both structures
- Rollback possible if issues discovered
- Gradual component migration without breakage

**What Happens to fumes_generated?**:
- ✅ **Keep existing data** - Do not delete
- ✅ **Mark as deprecated** in schema comments
- ✅ **Add migration metadata** to track completion
  ```yaml
  safety_data:
    _migration_status:
      fumes_data_migrated: true
      migration_date: '2025-12-20'
      validated: true
    fumes_generated:  # @deprecated - Use domain_linkages.produces_compounds
      # ... existing data
  ```

**Deliverables**:
- Migration script with dry-run mode
- All contaminants with enhanced domain_linkages
- Validation report comparing old/new data
- Migration status tracking

---

### Phase 3: Component Updates & Switchover (Week 3)

**Objectives**:
- Update all UI components to use new structure
- Implement fallback for backward compatibility
- Test all affected pages

**Tasks**:
1. ✅ Update DomainLinkageSection component
2. ✅ Enhance domain linkage cards with safety indicators
3. ✅ Update HazardousFumesTable to read from domain_linkages
4. ✅ Add fallback logic for legacy structure
5. ✅ Add warning badges for exceeded limits
6. ✅ Test all contaminant pages
7. ✅ Performance testing with new data structure
8. ✅ Fix any rendering issues

**Component Fallback Pattern**:
```typescript
function getCompoundSafetyData(frontmatter: any) {
  // Priority 1: Enhanced domain_linkages
  const produces = frontmatter?.domain_linkages?.produces_compounds;
  if (produces?.[0]?.concentration_range) {
    return produces;
  }
  
  // Priority 2: Legacy fumes_generated (with transformation)
  const fumes = frontmatter?.safety_data?.fumes_generated;
  if (fumes) {
    console.warn(
      `[Deprecated] Page still using fumes_generated: ${frontmatter.id}`,
      'Please regenerate frontmatter with enhanced schema'
    );
    return transformLegacyToEnhanced(fumes);
  }
  
  return [];
}
```

**What Happens to fumes_generated?**:
- ✅ **Still present** in YAML files
- ✅ **Not read by components** (unless new data missing)
- ✅ **Logged as deprecated** when accessed
- ⚠️ **Not yet deleted** - waiting for validation

**Deliverables**:
- Updated components with fallback logic
- Test coverage for both data structures
- Performance benchmarks
- User-facing changes documentation

---

### Phase 4: Deprecation & Cleanup (Week 4)

**Objectives**:
- Remove fumes_generated from all files
- Clean up legacy code
- Archive migration documentation

**Tasks**:

#### Step 1: Validation Pre-Check (Days 1-2)
```bash
# Verify all files have enhanced data
npm run validate:enhanced-linkages

# Check component usage
grep -r "fumes_generated" app/components/
grep -r "safety_data.fumes" app/

# Verify no fallbacks being triggered
npm run dev:monitor-deprecated-access
```

**Go/No-Go Decision**:
- ✅ All contaminants have enhanced domain_linkages
- ✅ All components reading from new structure
- ✅ Zero fallback access logged in production
- ✅ All tests passing
- ✅ Performance acceptable

#### Step 2: Remove fumes_generated (Days 3-4)
```python
# scripts/cleanup-legacy-fumes.py
import yaml
import glob

def cleanup_fumes_generated(file_path):
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Remove fumes_generated
    if 'safety_data' in data and 'fumes_generated' in data['safety_data']:
        del data['safety_data']['fumes_generated']
        
        # Remove migration metadata
        if '_migration_status' in data['safety_data']:
            del data['safety_data']['_migration_status']
        
        # If safety_data is now empty except for metadata, keep other fields
        # but mark cleanup complete
        data['safety_data']['_cleanup_date'] = '2025-12-23'
    
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

# Process all contaminants
for file in glob.glob('frontmatter/contaminants/**/*.yaml', recursive=True):
    cleanup_fumes_generated(file)
    print(f"✅ Cleaned: {file}")
```

#### Step 3: Remove Fallback Code (Day 5)
```typescript
// Before: Fallback logic
function getCompoundSafetyData(frontmatter: any) {
  const produces = frontmatter?.domain_linkages?.produces_compounds;
  if (produces) return produces;
  
  // ❌ DELETE THIS BLOCK
  const fumes = frontmatter?.safety_data?.fumes_generated;
  if (fumes) {
    return transformLegacyToEnhanced(fumes);
  }
  
  return [];
}

// After: Direct access only
function getCompoundSafetyData(frontmatter: any) {
  return frontmatter?.domain_linkages?.produces_compounds || [];
}
```

**Files to Clean**:
- `app/components/SafetyDataPanel/SafetyDataPanel.tsx`
- `app/components/HazardousFumesTable/HazardousFumesTable.tsx`
- `app/components/DomainLinkages/DomainLinkageSection.tsx`
- `app/utils/domainLinkageMapper.ts`

#### Step 4: Archive & Document (Days 6-7)
```bash
# Create archive directory
mkdir -p docs/archive/2025-12-migration/

# Archive migration artifacts
mv scripts/migrate-safety-data.py docs/archive/2025-12-migration/
mv scripts/validate-enhanced-linkages.ts docs/archive/2025-12-migration/
mv DOMAIN_LINKAGES_SAFETY_DATA_ENHANCEMENT.md docs/archive/2025-12-migration/

# Create completion report
cat > MIGRATION_COMPLETE_DEC2025.md << EOF
# Domain Linkages Safety Data Migration - COMPLETE

**Completion Date**: December 23, 2025
**Files Migrated**: 47 contaminants
**Data Preserved**: 100%
**Legacy Code Removed**: Yes

## Summary
- Enhanced domain_linkages with safety/technical data
- Removed fumes_generated duplication
- All components updated
- Zero data loss

## Rollback (if needed)
Archived migration scripts in docs/archive/2025-12-migration/
EOF
```

**What Happens to fumes_generated?**:
- ❌ **DELETED** from all frontmatter files
- ❌ **Fallback code REMOVED** from components
- ✅ **Migration scripts ARCHIVED** for reference
- ✅ **Cleanup complete** - single source of truth established

**Deliverables**:
- Clean frontmatter files (no fumes_generated)
- Simplified component code (no fallbacks)
- Migration completion report
- Archived migration documentation

---

## Rollback Procedures

### If Issues Discovered in Phase 2
```bash
# Restore original files from git
git checkout HEAD -- frontmatter/contaminants/

# Or restore specific files
git checkout HEAD -- frontmatter/contaminants/plastic-residue-contamination.yaml
```

### If Issues Discovered in Phase 3
- Components have fallback logic - will automatically use fumes_generated
- No data loss - both structures present
- Can delay component updates

### If Issues Discovered in Phase 4
**CRITICAL**: Cannot rollback after fumes_generated deleted

**Prevention**:
1. Complete validation before deletion
2. Tag git commit before cleanup: `git tag pre-cleanup-v1`
3. Backup files: `tar -czf fumes-backup.tar.gz frontmatter/contaminants/`
4. Test in staging environment first

**Emergency Recovery**:
```bash
# Restore from git tag
git reset --hard pre-cleanup-v1

# Or restore from backup
tar -xzf fumes-backup.tar.gz
```

---

## Data Preservation Validation

### Validation Checklist
Run before Phase 4 cleanup:

```bash
# 1. Verify all compounds migrated
python3 scripts/validate-migration-completeness.py

# 2. Compare old vs new data
python3 scripts/compare-fumes-to-linkages.py

# 3. Check for missing compounds
python3 scripts/audit-compound-coverage.py

# 4. Verify URLs are valid
python3 scripts/validate-compound-urls.py

# 5. Test exposure limit calculations
python3 scripts/test-exceeds-limits-accuracy.py
```

### Validation Script Example
```python
# scripts/validate-migration-completeness.py
import yaml
import glob

def validate_migration(file_path):
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    fumes = data.get('safety_data', {}).get('fumes_generated', [])
    produces = data.get('domain_linkages', {}).get('produces_compounds', [])
    
    issues = []
    
    # Check: All fumes compounds exist in produces_compounds
    for fume in fumes:
        compound_name = fume['compound']
        found = any(p['title'] == compound_name for p in produces)
        if not found:
            issues.append(f"❌ Missing in linkages: {compound_name}")
    
    # Check: All produces compounds with concentration data
    for produce in produces:
        if not produce.get('concentration_range'):
            issues.append(f"⚠️ No concentration data: {produce['title']}")
    
    return issues

# Run validation
total_files = 0
total_issues = 0

for file in glob.glob('frontmatter/contaminants/**/*.yaml', recursive=True):
    issues = validate_migration(file)
    total_files += 1
    if issues:
        print(f"\n{file}:")
        for issue in issues:
            print(f"  {issue}")
            total_issues += 1

print(f"\n{'='*60}")
print(f"Validation Complete")
print(f"Files checked: {total_files}")
print(f"Issues found: {total_issues}")
print(f"Status: {'✅ PASS' if total_issues == 0 else '❌ FAIL'}")
```

---

## Data Sources for Population

### Concentration Ranges
**Source 1**: Existing `safety_data.fumes_generated`
- Extract min/max from range strings (e.g., "5-25" → min: 5, max: 25)
- Calculate typical as midpoint or use explicit value if available

**Source 2**: Compound frontmatter `typical_concentration_range`
- Some compounds have this field defined
- Use as authoritative source when available

### Exposure Limits
**Source 1**: Compound frontmatter `exposure_limits`
```yaml
exposure_limits:
  osha_pel_ppm: 200
  osha_pel_mg_m3: 360
  niosh_rel_ppm: null
  niosh_rel_mg_m3: null
  acgih_tlv_ppm: 25
  acgih_tlv_mg_m3: 45
```

**Source 2**: OSHA/NIOSH databases (if compound missing data)

### Particulate Properties
**Source**: Existing `safety_data.particulate_generation`
```yaml
particulate_generation:
  respirable_fraction: 0.7
  size_range_um: [0.1, 10.0]
```

### Control Measures
**Source**: Existing `safety_data.ppe_requirements` and `ventilation_requirements`
```yaml
ppe_requirements:
  respiratory: organic_vapor_cartridge
  eye_protection: chemical_goggles
  skin_protection: chemical_resistant_gloves

ventilation_requirements:
  minimum_air_changes_per_hour: 20
  exhaust_velocity_m_s: 1.5
  filtration_type: activated_carbon
```

---

## Implementation Pseudocode

```python
def enhance_domain_linkages(contaminant_data):
    """
    Enhance domain_linkages with safety data from multiple sources.
    """
    produces_compounds = contaminant_data.get('domain_linkages', {}).get('produces_compounds', [])
    fumes_generated = contaminant_data.get('safety_data', {}).get('fumes_generated', [])
    
    # Create lookup for fumes data by compound name
    fumes_lookup = {
        normalize_name(fume['compound']): fume 
        for fume in fumes_generated
    }
    
    # Enhance each compound in domain_linkages
    for compound in produces_compounds:
        compound_id = compound['id']
        compound_name = compound['title']
        
        # Load compound frontmatter for detailed data
        compound_frontmatter = load_compound_frontmatter(compound_id)
        
        # Add concentration data
        fume_data = fumes_lookup.get(normalize_name(compound_name))
        if fume_data:
            concentration_str = fume_data.get('concentration_mg_m3')
            if isinstance(concentration_str, str) and '-' in concentration_str:
                min_val, max_val = map(float, concentration_str.split('-'))
                compound['concentration_range'] = {
                    'min_mg_m3': min_val,
                    'max_mg_m3': max_val,
                    'typical_mg_m3': (min_val + max_val) / 2
                }
        
        # Add exposure limits from compound frontmatter
        if compound_frontmatter and 'exposure_limits' in compound_frontmatter:
            limits = compound_frontmatter['exposure_limits']
            compound['exposure_limits'] = {
                'osha_pel_mg_m3': limits.get('osha_pel_mg_m3'),
                'niosh_rel_mg_m3': limits.get('niosh_rel_mg_m3'),
                'acgih_tlv_mg_m3': limits.get('acgih_tlv_mg_m3'),
                'idlh_mg_m3': limits.get('idlh_mg_m3')
            }
            
            # Calculate exceeds_limits
            typical_concentration = compound['concentration_range'].get('typical_mg_m3')
            acgih_limit = compound['exposure_limits'].get('acgih_tlv_mg_m3')
            compound['exceeds_limits'] = (
                typical_concentration and acgih_limit and 
                typical_concentration > acgih_limit
            )
        
        # Add monitoring requirement
        compound['monitoring_required'] = compound_frontmatter.get('monitoring_required', False)
        
        # Add particulate properties from safety_data
        particulate = contaminant_data.get('safety_data', {}).get('particulate_generation', {})
        if particulate:
            compound['particulate_properties'] = {
                'respirable_fraction': particulate.get('respirable_fraction'),
                'size_range_um': particulate.get('size_range_um')
            }
        
        # Add control measures
        ppe = contaminant_data.get('safety_data', {}).get('ppe_requirements', {})
        ventilation = contaminant_data.get('safety_data', {}).get('ventilation_requirements', {})
        
        compound['control_measures'] = {
            'ventilation_required': bool(ventilation),
            'ppe_level': determine_ppe_level(ppe),
            'filtration_type': ventilation.get('filtration_type')
        }
    
    return produces_compounds

def determine_ppe_level(ppe_requirements):
    """Determine PPE level from requirements."""
    if not ppe_requirements:
        return 'none'
    
    respiratory = ppe_requirements.get('respiratory', '').lower()
    
    if 'scba' in respiratory or 'supplied_air' in respiratory:
        return 'full'
    elif 'organic_vapor' in respiratory or 'p100' in respiratory:
        return 'enhanced'
    elif respiratory:
        return 'basic'
    else:
        return 'none'
```

---

## TypeScript Interface Updates

```typescript
// app/types/domain-linkages.ts

export interface DomainLinkageCompound {
  // Existing fields
  id: string;
  title: string;
  url: string;
  image: string;
  category: string;
  subcategory: string;
  frequency: 'very_common' | 'common' | 'occasional' | 'rare';
  severity: 'low' | 'moderate' | 'high' | 'severe';
  typical_context: string;
  exposure_risk: 'low' | 'moderate' | 'high' | 'critical';
  
  // NEW: Safety & Technical Data
  concentration_range?: {
    min_mg_m3: number;
    max_mg_m3: number;
    typical_mg_m3: number;
  };
  exposure_limits?: {
    osha_pel_mg_m3: number | null;
    niosh_rel_mg_m3: number | null;
    acgih_tlv_mg_m3: number;
    idlh_mg_m3: number | null;
  };
  exceeds_limits?: boolean;
  monitoring_required?: boolean;
  particulate_properties?: {
    respirable_fraction: number;
    size_range_um: [number, number];
  };
  control_measures?: {
    ventilation_required: boolean;
    ppe_level: 'none' | 'basic' | 'enhanced' | 'full';
    filtration_type: string | null;
  };
}

export interface DomainLinkages {
  produces_compounds?: DomainLinkageCompound[];
  produced_by_contaminants?: DomainLinkageCompound[];
  related_materials?: DomainLinkageMaterial[];
  compatible_materials?: DomainLinkageMaterial[];
}
```

---

## Validation Rules

```yaml
# Required fields (must exist)
required:
  - id
  - title
  - url
  - category
  - subcategory
  - frequency
  - severity

# Conditional requirements
conditional:
  - if: exceeds_limits == true
    then: monitoring_required must be true
  
  - if: severity == 'high' or severity == 'severe'
    then: control_measures.ppe_level must be 'enhanced' or 'full'
  
  - if: concentration_range exists
    then: exposure_limits.acgih_tlv_mg_m3 must exist

# Value constraints
constraints:
  - concentration_range.min_mg_m3 >= 0
  - concentration_range.max_mg_m3 >= concentration_range.min_mg_m3
  - concentration_range.typical_mg_m3 >= concentration_range.min_mg_m3
  - concentration_range.typical_mg_m3 <= concentration_range.max_mg_m3
  - particulate_properties.respirable_fraction >= 0.0
  - particulate_properties.respirable_fraction <= 1.0
  - particulate_properties.size_range_um[0] < particulate_properties.size_range_um[1]
```

---

## UI Component Examples

### Enhanced Domain Linkage Card
```tsx
<DomainLinkageCard
  title="Formaldehyde"
  severity="moderate"
  exceedsLimits={true}
  concentration="1-10 mg/m³"
  exposureLimit="0.3 mg/m³"
  monitoringRequired={true}
  ppeLevel="enhanced"
/>
```

**Displays**:
- Colored background/border based on severity
- ⚠️ Warning badge if exceeds_limits
- Concentration range in small text
- "Monitoring Required" indicator
- PPE level icon

### Unified Table Component
```tsx
<HazardousCompoundsTable
  compounds={domain_linkages.produces_compounds}
  showConcentrations={true}
  showExposureLimits={true}
  clickableLinks={true}
/>
```

**Features**:
- Clickable compound names (using url field)
- Concentration vs. limit comparison
- Status indicators (Exceeds/Within Limit)
- Sort by severity, concentration, or alphabetically
- Filter by exceeds_limits or ppe_level

---

## Backward Compatibility

### Transition Period
- Keep `safety_data.fumes_generated` for 1 month after migration
- Mark as `@deprecated` in schema
- Components check domain_linkages first, fall back to fumes_generated
- Log warnings when legacy structure is used

### Fallback Logic
```typescript
function getCompoundSafetyData(frontmatter: any) {
  // NEW: Try enhanced domain_linkages first
  const produces = frontmatter?.domain_linkages?.produces_compounds;
  if (produces && produces.length > 0 && produces[0].concentration_range) {
    return produces;
  }
  
  // LEGACY: Fall back to old fumes_generated structure
  const fumes = frontmatter?.safety_data?.fumes_generated;
  if (fumes) {
    console.warn('[Deprecated] Using legacy fumes_generated structure');
    return transformLegacyFumes(fumes);
  }
  
  return [];
}
```

---

## Testing Requirements

### Unit Tests
- [ ] Schema validation passes for enhanced structure
- [ ] Backward compatibility with legacy structure
- [ ] TypeScript types compile without errors
- [ ] Edge cases: missing optional fields, null values

### Integration Tests
- [ ] Domain linkage cards render with new data
- [ ] Hazardous compounds table shows all fields
- [ ] Exceeds limits badges display correctly
- [ ] Links navigate to compound pages

### Data Validation
- [ ] All contaminants have at least one compound with full data
- [ ] No compounds missing required fields
- [ ] Concentration ranges are logical (min < max)
- [ ] Exposure limits match compound frontmatter

---

## Documentation Updates Required

### Files to Update
1. **DOMAIN_LINKAGES_IMAGE_URL_FIX.md** - Add safety data fields
2. **CONTAMINANT_DATASET_FORMAT_SPECIFICATION.md** - New schema definition
3. **Component documentation** - DomainLinkageSection, HazardousFumesTable
4. **TypeScript interfaces** - domain-linkages.ts, card-types.ts

### New Documentation
1. **DOMAIN_LINKAGES_SAFETY_DATA_SCHEMA.md** - Complete field reference
2. **MIGRATION_GUIDE_SAFETY_DATA.md** - Step-by-step migration instructions
3. **COMPONENT_USAGE_ENHANCED_LINKAGES.md** - How to use new data in UI

---

## Timeline & Milestones

### Week 1: Schema & Foundation
- [ ] Define complete schema with all fields
- [ ] Update TypeScript interfaces
- [ ] Create validation rules
- [ ] Write unit tests

### Week 2: Data Migration
- [ ] Write migration script
- [ ] Test on 5 sample contaminants
- [ ] Migrate all contaminant frontmatter
- [ ] Validate migrated data

### Week 3: Component Updates
- [ ] Update DomainLinkageSection component
- [ ] Enhance domain linkage cards
- [ ] Update HazardousFumesTable
- [ ] Add warning badges and indicators

### Week 4: Validation & Cleanup
- [ ] Full integration testing
- [ ] Fix any issues discovered
- [ ] Deprecate old fumes_generated structure
- [ ] Update all documentation

---

## Success Metrics

- ✅ 100% of contaminants migrated to new structure
- ✅ Zero data duplication (fumes_generated removed)
- ✅ All compound links functional
- ✅ All safety data displaying correctly
- ✅ No regressions in existing functionality
- ✅ Improved user experience with richer data display

---

## Questions & Considerations

1. **Should material linkages also be enhanced?**
   - Currently materials don't have concentration data
   - Could add frequency of contamination occurrence
   - Could add removal difficulty metrics

2. **How to handle compounds without exposure limits?**
   - Set to null
   - Mark as "No established limit"
   - Use closest analog compound limit

3. **Should we add regional variations?**
   - Different exposure limits by country (OSHA/EU/Asia)
   - Regional severity classifications
   - Locale-specific control measures

---

## Approval Checklist

- [ ] Schema reviewed by safety engineer
- [ ] Data migration script tested
- [ ] Component updates approved
- [ ] Documentation complete
- [ ] Timeline feasible
- [ ] Backward compatibility verified
- [ ] Testing plan approved

---

**Prepared by**: Development Team  
**Last Updated**: December 16, 2025  
**Status**: Proposal - Awaiting Approval
