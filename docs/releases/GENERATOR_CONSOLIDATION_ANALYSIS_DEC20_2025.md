# Generator Field Consolidation & Data Structure Analysis
## December 20, 2025

---

## 📊 PART 1: GENERATOR FIELD ANALYSIS

### Current Generator Configurations

#### Materials
```yaml
generators:
- type: field_cleanup
- type: seo_description
  source_field: description
  output_field: seo_description
  max_length: 160
```

#### Contaminants
```yaml
generators:
- type: relationships
  domain: contaminants
  output_field: relationships
- type: contaminant_materials_grouping
- type: field_cleanup
- type: seo_description
  source_field: contaminant_description
  output_field: seo_description
  max_length: 160
```

#### Compounds
```yaml
generators:
- type: field_cleanup
- type: seo_description
  source_field: compound_description
  output_field: seo_description
  max_length: 160
- type: excerpt
  source_field: compound_description
  output_field: micro
  mode: sentences
  length: 2
```

#### Settings
```yaml
generators:
- type: field_cleanup
- type: seo_description
  source_field: description
  output_field: seo_description
  max_length: 160
- type: excerpt
  source_field: description
  output_field: micro
  mode: words
  length: 50
```

---

## 🎯 CONSOLIDATION OPPORTUNITIES

### 1. SEO Description Generator ✅ ALREADY CONSISTENT

**Status**: Nearly perfect consistency

**Current Configuration**:
| Domain | Source Field | Output Field | Max Length |
|--------|-------------|--------------|------------|
| Materials | description | seo_description | 160 |
| Contaminants | contaminant_description | seo_description | 160 |
| Compounds | compound_description | seo_description | 160 |
| Settings | description | seo_description | 160 |

**Inconsistency**: Only the source field names differ (domain-specific)

**Recommendation**: ✅ **KEEP AS-IS**
- Source field names are appropriately domain-specific
- Output field and max_length are perfectly consistent
- No consolidation needed

---

### 2. Micro/Excerpt Generator ⚠️ NEEDS CONSOLIDATION

**Status**: Inconsistent field names and missing from domains

**Current State**:
| Domain | Generator | Output Field | Present? |
|--------|-----------|--------------|----------|
| Materials | (none) | (none) | ❌ Missing |
| Contaminants | (none) | (none) | ❌ Missing |
| Compounds | excerpt | **micro** | ✅ Yes |
| Settings | excerpt | **micro** | ✅ Yes |

**Issue**: Materials doesn't have excerpt/micro generator in config, but has micro field in frontmatter

**Investigation Needed**:
- Where is materials micro field coming from?
- Should materials/contaminants have micro generators?

**Recommendation**: 🔧 **NORMALIZE TO MICRO**
```yaml
# Add to materials.yaml
- type: excerpt
  source_field: description
  output_field: micro
  mode: sentences
  length: 2

# Add to contaminants.yaml (if desired)
- type: excerpt
  source_field: contaminant_description
  output_field: micro
  mode: sentences
  length: 2
```

---

### 3. Field Cleanup Generator ✅ PERFECT CONSISTENCY

**Status**: 100% consistent across all domains

**Current State**:
- Materials: ✅ Has field_cleanup
- Contaminants: ✅ Has field_cleanup
- Compounds: ✅ Has field_cleanup
- Settings: ✅ Has field_cleanup

**Recommendation**: ✅ **KEEP AS-IS**

---

### 4. Domain-Specific Generators ℹ️ BY DESIGN

**Contaminants-Only Generators**:
```yaml
- type: relationships          # Contaminants only
- type: contaminant_materials_grouping  # Contaminants only
```

**Reason**: These are domain-specific requirements
**Recommendation**: ✅ **KEEP AS-IS** - Not applicable to other domains

---

## 📋 CONSOLIDATION RECOMMENDATIONS

### Priority 1: Add Micro Generator to Materials
**Status**: ⚠️ MISSING (but micro field exists in frontmatter)

**Change**:
```yaml
# export/config/materials.yaml
generators:
- type: field_cleanup
- type: seo_description
  source_field: description
  output_field: seo_description
  max_length: 160
- type: excerpt              # ADD THIS
  source_field: description
  output_field: micro
  mode: sentences
  length: 2
```

**Reason**: Materials frontmatter has micro field, but no generator config

---

### Priority 2: Standardize Micro Generator Parameters
**Status**: ⚠️ INCONSISTENT

**Current**:
- Compounds: mode=sentences, length=2
- Settings: mode=words, length=50

**Recommended**:
```yaml
# Standard micro generator (all domains)
- type: excerpt
  source_field: {domain}_description
  output_field: micro
  mode: sentences     # Consistent mode
  length: 2          # Consistent length
```

**Change Settings**:
```yaml
# export/config/settings.yaml (CHANGE)
- type: excerpt
  source_field: description
  output_field: micro
  mode: sentences    # CHANGE from words
  length: 2          # CHANGE from 50
```

**Reason**: Sentence-based excerpts are more natural than word counts

---

### Priority 3: Consider Micro for Contaminants
**Status**: ❓ OPTIONAL

**Question**: Should contaminants have micro field?

**If YES**:
```yaml
# export/config/contaminants.yaml (ADD)
- type: excerpt
  source_field: contaminant_description
  output_field: micro
  mode: sentences
  length: 2
```

---

## 📈 PROPOSED CONSOLIDATED GENERATOR STRUCTURE

### Standard Generators (All Domains)
```yaml
generators:
  # Required for all domains
  - type: field_cleanup
  
  # SEO Description (all domains)
  - type: seo_description
    source_field: {domain}_description  # Domain-specific
    output_field: seo_description
    max_length: 160
  
  # Micro Excerpt (all domains except where N/A)
  - type: excerpt
    source_field: {domain}_description  # Domain-specific
    output_field: micro
    mode: sentences
    length: 2
  
  # Domain-specific generators (as needed)
  - type: {domain_specific_generator}
```

### Implementation
```yaml
# Materials
generators:
- type: field_cleanup
- type: seo_description
  source_field: description
  output_field: seo_description
  max_length: 160
- type: excerpt                    # ADD
  source_field: description
  output_field: micro
  mode: sentences
  length: 2

# Contaminants
generators:
- type: relationships              # Domain-specific (keep)
  domain: contaminants
  output_field: relationships
- type: contaminant_materials_grouping  # Domain-specific (keep)
- type: field_cleanup
- type: seo_description
  source_field: contaminant_description
  output_field: seo_description
  max_length: 160
- type: excerpt                    # ADD (optional)
  source_field: contaminant_description
  output_field: micro
  mode: sentences
  length: 2

# Compounds
generators:
- type: field_cleanup
- type: seo_description
  source_field: compound_description
  output_field: seo_description
  max_length: 160
- type: excerpt                    # Already present ✅
  source_field: compound_description
  output_field: micro
  mode: sentences                  # Already correct ✅
  length: 2                        # Already correct ✅

# Settings
generators:
- type: field_cleanup
- type: seo_description
  source_field: description
  output_field: seo_description
  max_length: 160
- type: excerpt
  source_field: description
  output_field: micro
  mode: sentences                  # CHANGE from words
  length: 2                        # CHANGE from 50
```

---

## 📊 PART 2: SAFETY_DATA STRUCTURE ANALYSIS

### Overview
**Location**: Only in `Contaminants.yaml`
**Path**: `contamination_patterns.{pattern_id}.laser_properties.safety_data`
**Total Keys**: **8**

### Complete Key List
1. **fire_explosion_risk** (dict with 3 keys)
2. **fumes_generated** (list of compound dicts)
3. **particulate_generation** (dict with 2 keys)
4. **ppe_requirements** (dict with 4 keys)
5. **substrate_compatibility_warnings** (list of strings)
6. **toxic_gas_risk** (dict with 4 keys)
7. **ventilation_requirements** (dict with 4 keys)
8. **visibility_hazard** (dict with 5 keys)

### Detailed Structure

#### 1. fire_explosion_risk (dict)
```yaml
severity: low | moderate | high
description: string
mitigation: string
```

#### 2. fumes_generated (list)
```yaml
- compound: string
  concentration_mg_m3: string (range)
  exposure_limit_mg_m3: number
  hazard_class: string
```
**Count**: Variable (typically 4-6 compounds per pattern)

#### 3. particulate_generation (dict)
```yaml
respirable_fraction: float (0.0-1.0)
size_range_um: [min, max]
```

#### 4. ppe_requirements (dict)
```yaml
eye_protection: string
respiratory: string
skin_protection: string
rationale: string
```

#### 5. substrate_compatibility_warnings (list)
```yaml
- string (warning text)
- string (warning text)
```
**Count**: Variable (typically 2-4 warnings)

#### 6. toxic_gas_risk (dict)
```yaml
severity: low | moderate | high
primary_hazards: [string, ...]
description: string
mitigation: string
```

#### 7. ventilation_requirements (dict)
```yaml
exhaust_velocity_m_s: float
filtration_type: string
minimum_air_changes_per_hour: integer
rationale: string
```

#### 8. visibility_hazard (dict)
```yaml
severity: low | moderate | high
description: string
source: string
mitigation: string
related_field: string (reference to other field)
```

---

## 🏗️ PART 3: DATA STRUCTURE IMPROVEMENTS FOR FRONTMATTER GENERATION

### Problem Analysis

#### Current Issues
1. **Nested Structure**: safety_data buried under `laser_properties.safety_data`
   - ✅ **SOLVED**: Dec 20, 2025 - Extracted to top-level with keep_at_top_level config

2. **Complex Nested Objects**: Many dict/list structures
   - Makes frontmatter templates complex
   - Hard to display in UI

3. **Inconsistent Severity Scales**: Some fields have severity, others don't

4. **Cross-References**: visibility_hazard.related_field points to particulate_generation

---

### Recommended Data Structure Changes

#### 1. Flatten Risk Severity Fields ⭐ HIGH PRIORITY

**Current**:
```yaml
fire_explosion_risk:
  severity: low
  description: "..."
  mitigation: "..."
```

**Proposed** (Flattened):
```yaml
fire_explosion_risk_severity: low
fire_explosion_risk_description: "..."
fire_explosion_risk_mitigation: "..."
```

**Benefits**:
- Easier to query individual fields
- Simpler frontmatter templates
- Better for filtering/sorting

**Implementation**: Create migration script to flatten nested risk dicts

---

#### 2. Normalize Severity Enums ⭐ HIGH PRIORITY

**Current**: Inconsistent presence
- fire_explosion_risk: ✅ has severity
- toxic_gas_risk: ✅ has severity
- visibility_hazard: ✅ has severity
- particulate_generation: ❌ no severity
- fumes_generated: ❌ no severity
- ppe_requirements: ❌ no severity

**Proposed**: Add severity to ALL fields
```yaml
particulate_generation_severity: moderate
fumes_generated_severity: high
ppe_requirements_severity: moderate
```

**Benefits**:
- Consistent risk assessment across all safety aspects
- Easy to create safety summary dashboards
- Enable risk-based sorting/filtering

---

#### 3. Create Safety Summary Field 🆕 NEW FIELD

**Proposed**: Auto-generated summary at frontmatter generation
```yaml
safety_summary:
  overall_risk: moderate  # Computed from all severity fields
  primary_concerns:
    - Toxic fumes (high)
    - Particulates (moderate)
  required_ppe:
    - full_face respiratory
    - safety goggles
    - gloves
  ventilation_required: true
```

**Benefits**:
- Quick risk assessment without parsing all fields
- Better for UI displays (danger badges, warnings)
- Enables safety-based filtering

**Implementation**: Add generator in export config

---

#### 4. Flatten Fumes Generated List ⚠️ CONSIDER

**Current**:
```yaml
fumes_generated:
  - compound: Acetaldehyde
    concentration_mg_m3: "5-25"
    exposure_limit_mg_m3: 25
    hazard_class: irritant
  - compound: Formaldehyde
    ...
```

**Option A** - Keep as-is (list of dicts)
- ✅ Preserves detailed data
- ❌ Complex to query
- ❌ Hard to display in frontmatter

**Option B** - Separate arrays
```yaml
fumes_generated_compounds: ["Acetaldehyde", "Formaldehyde", ...]
fumes_generated_concentrations: ["5-25", "10-50", ...]
fumes_generated_hazard_classes: ["irritant", "toxic", ...]
```
- ✅ Easy to query
- ❌ Loses compound-to-concentration mapping

**Option C** - Move to relationships
```yaml
relationships:
  produces_compounds:
    - id: acetaldehyde
      concentration_mg_m3: "5-25"
      exposure_limit_mg_m3: 25
      hazard_class: irritant
```
- ✅ Uses existing relationship structure
- ✅ Compounds already have full data
- ❌ Requires DomainAssociations population

**Recommendation**: **Option C** - Move to relationships (best for long-term)

---

#### 5. Add Computed Fields for UI Display 🆕 NEW FIELDS

**Proposed Computed Fields**:
```yaml
# At frontmatter generation time
requires_respiratory_protection: true  # Boolean
requires_eye_protection: true
requires_skin_protection: true
minimum_ventilation_ach: 12
overall_visibility_impact: moderate
contains_toxic_compounds: true
compound_count: 6
highest_risk_compound: "Formaldehyde"
```

**Benefits**:
- Quick boolean checks for UI
- No need to parse complex structures
- Enable faceted search/filtering

**Implementation**: Add field generators in export config

---

#### 6. Standardize Units in Field Names 💡 NICE TO HAVE

**Current**:
```yaml
exhaust_velocity_m_s: 0.5           # Units in field name ✅
minimum_air_changes_per_hour: 12   # Units in field name ✅
respirable_fraction: 0.7             # Unitless ✅
concentration_mg_m3: "5-25"         # Units in field name ✅
```

**Status**: ✅ Already following best practice

---

### Summary of Recommended Changes

#### Immediate (Do Now)
1. ✅ **Safety data extraction** - COMPLETE (Dec 20, 2025)
2. 🔧 **Add micro generator to materials** - Add to config
3. 🔧 **Normalize micro generator** - Change settings to sentences/2

#### Short-term (Next Sprint)
1. 🏗️ **Flatten risk severity fields** - Migration script
2. 🏗️ **Add severity to all safety fields** - Data enhancement
3. 🆕 **Create safety_summary field** - Generator in export

#### Long-term (Future Enhancement)
1. 🔗 **Move fumes_generated to relationships** - Requires DomainAssociations
2. 🆕 **Add computed safety fields** - Generators for booleans/counts
3. 📊 **Create safety risk dashboard** - UI using new fields

---

## 🎯 Implementation Priority Matrix

| Change | Priority | Effort | Impact | Status |
|--------|----------|--------|--------|--------|
| Add micro to materials | HIGH | 5 min | High | ⏳ Ready |
| Normalize micro mode/length | HIGH | 10 min | Medium | ⏳ Ready |
| Flatten risk severity | MEDIUM | 2 hours | High | 📋 Needs script |
| Add missing severity fields | MEDIUM | 3 hours | High | 📋 Needs research |
| Safety summary generator | MEDIUM | 1 hour | High | 📋 Needs design |
| Move fumes to relationships | LOW | 4 hours | Medium | 📋 Needs DomainAssociations |
| Computed safety fields | LOW | 2 hours | Medium | 📋 Needs generators |

---

## 📝 Next Actions

### For Generator Consolidation
1. Add micro generator to materials.yaml
2. Update settings micro generator (sentences, length 2)
3. Decide: Add micro to contaminants? (Yes/No)
4. Re-export all domains
5. Validate consistency

### For Safety Data Enhancement
1. Create safety data flattening migration script
2. Add severity fields to all safety categories
3. Create safety_summary generator
4. Test with sample contaminant
5. Roll out to all 98 contaminants

---

Generated: December 20, 2025 15:00 PST
User: Air2air/z-beam-generator
Branch: main
