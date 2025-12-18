# Challenge Taxonomy Guide

## Overview

The challenge taxonomy system provides a standardized way to identify and query material-specific challenges across the entire Z-Beam system. Challenges remain **embedded attributes** of materials (not a separate domain) but gain **queryability** through standardized `challenge_id` fields.

**Purpose**: Enable cross-material analysis while preserving material-specific context.

## Architecture

### Why Embedded, Not Separate Domain?

**Decision**: Material challenges are **embedded attributes with IDs**, not a standalone domain.

**Rationale** (from ADR-007):
1. **Material Specificity**: Challenge details vary by material
   - Reflectivity ranges: Aluminum (550nm) vs Titanium (750nm)
   - Thermal thresholds: Steel (1500°C) vs Plastic (150°C)
   - Solutions differ: Metals need wavelength shift, plastics need lower power

2. **No Independent Existence**: Challenges don't exist without material context
   - "High reflectivity" means different things for different materials
   - Same challenge has different severity across materials
   - Solutions are material-dependent

3. **Data Volume**: 804 challenge instances across 153 materials
   - Average: 5.2 challenges per material
   - 42 materials share 6 common challenges (metals)
   - Material-specific data dominates

**Hybrid Approach**: Embedded data + standardized IDs = queryability + context

## Data Structure

### Taxonomy Definition

**Location**: `data/materials/ChallengeTaxonomy.yaml`

**Structure**:
```yaml
# 3 top-level categories
thermal_management:
  high_thermal_conductivity_and_heat_spread:
    name: "High thermal conductivity and heat spread"
    description: "Rapid heat dissipation causing large heat-affected zones"
    typical_materials: ["Aluminum", "Copper", "Silver"]

surface_characteristics:
  high_reflectivity:
    name: "High reflectivity"
    description: "High laser reflectivity at common wavelengths"
    typical_materials: ["Aluminum", "Stainless Steel", "Titanium"]

contamination_challenges:
  rust_and_oxide_layer_removal:
    name: "Rust and oxide layer removal"
    description: "Tenacious oxide layers requiring high energy"
    typical_materials: ["Steel", "Iron", "Cast Iron"]
```

**Purpose**: 
- Canonical list of 51 challenge types
- Reference for ID generation
- Documentation of challenge categories

### Material Settings

**Location**: `data/materials/Settings.yaml`

**Structure**:
```yaml
Aluminum:
  # ... other settings ...
  challenges:
    thermal_management:
    - challenge: High thermal conductivity and heat spread
      challenge_id: high_thermal_conductivity_and_heat_spread  # AUTO-GENERATED
      severity: medium
      property_value: 205 W/(m·K)
      impact: Heat spreads rapidly causing large HAZ requiring pulsed lasers
      solutions:
      - Use shorter pulse durations (picosecond/femtosecond)
      - Increase scan speed to minimize dwell time
```

**Key Point**: `challenge_id` is **AUTO-GENERATED** during export, not manually maintained.

### Exported Frontmatter

**Location**: `frontmatter/settings/aluminum-laser-cleaning-settings.yaml`

**Structure**: Same as Settings.yaml but with guaranteed `challenge_id` fields.

**Generation**: Exporter calls `_enrich_challenges_with_ids()` to add IDs automatically.

## Challenge ID Format

### Naming Convention

**Rule**: snake_case conversion of challenge text

**Examples**:
| Challenge Text | Challenge ID |
|----------------|-------------|
| High reflectivity | `high_reflectivity` |
| Thermal shock and microcracking | `thermal_shock_and_microcracking` |
| Oil and grease removal | `oil_and_grease_removal` |
| Porous structure with deep contamination | `porous_structure_with_deep_contamination` |

**Algorithm**:
```python
challenge_id = challenge_text.lower().replace(' ', '_').replace('-', '_')
```

### ID Stability

**Immutability**: Challenge IDs are derived from challenge text (deterministic)

**Changes**: If challenge text changes, ID changes (breaking change)

**Best Practice**: Keep challenge text stable, append variations as new challenges

**Example**:
```yaml
# ✅ GOOD - New challenge for specific variant
- challenge: High reflectivity at UV wavelengths
  challenge_id: high_reflectivity_at_uv_wavelengths

# ❌ BAD - Modifying existing challenge text
- challenge: High reflectivity (UV)  # Breaks existing challenge_id
```

## Using the Taxonomy

### Querying Challenges

**Query Tool**: `scripts/tools/query_challenges.py`

**Basic Query**:
```bash
# Find all materials with specific challenge
python3 scripts/tools/query_challenges.py high_reflectivity
```

**Statistics**:
```bash
# View distribution across materials
python3 scripts/tools/query_challenges.py --stats
```

**List All**:
```bash
# See all 51 challenge IDs
python3 scripts/tools/query_challenges.py --list-challenges
```

**See**: `scripts/tools/README_query_challenges.md` for complete usage guide.

### Common Query Patterns

**Find Materials Requiring Specific Equipment**:
```bash
# UV lasers help with reflective materials
python3 scripts/tools/query_challenges.py high_reflectivity

# Pulsed lasers for high thermal conductivity
python3 scripts/tools/query_challenges.py high_thermal_conductivity_and_heat_spread
```

**Analyze Contamination Requirements**:
```bash
# Rust removal capability
python3 scripts/tools/query_challenges.py rust_and_oxide_layer_removal

# Oil/grease cleaning
python3 scripts/tools/query_challenges.py oil_and_grease_removal
```

**Thermal Management Planning**:
```bash
# Materials prone to melting
python3 scripts/tools/query_challenges.py melting_and_heat_affected_zone_formation

# Materials prone to cracking
python3 scripts/tools/query_challenges.py thermal_shock_and_microcracking
```

## Adding New Challenges

### Step 1: Update Taxonomy

**File**: `data/materials/ChallengeTaxonomy.yaml`

**Add to appropriate category**:
```yaml
surface_characteristics:
  # ... existing challenges ...
  
  anodized_coating_protection:  # New challenge
    name: "Anodized coating protection"
    description: "Avoid damaging protective anodized layers during cleaning"
    typical_materials: ["Aluminum", "Titanium"]
```

**Categories**:
- `thermal_management` - Heat-related challenges
- `surface_characteristics` - Surface properties affecting cleaning
- `contamination_challenges` - Specific contaminant types

### Step 2: Add to Material Settings

**File**: `data/materials/Settings.yaml`

**Add challenge to relevant materials**:
```yaml
Aluminum:
  challenges:
    surface_characteristics:
    - challenge: Anodized coating protection  # Must match taxonomy name
      severity: high
      property_value: Type II anodizing, 5-25 µm thickness
      impact: Laser can strip anodizing, requiring coating replacement
      solutions:
      - Use lower fluence (<1 J/cm²)
      - Test on coated samples first
      - Consider manual cleaning if coating critical
```

**Required Fields**:
- `challenge` (str) - Human-readable name (matches taxonomy)
- `severity` (str) - low | moderate | high | critical
- `impact` (str) - Effect on cleaning process
- `solutions` (list[str]) - Mitigation strategies

**Optional Fields**:
- `property_value` (str) - Relevant material property
- `frequency` (str) - How often challenge occurs
- `detection` (str) - How to identify the challenge

### Step 3: Re-export Settings

**Command**:
```bash
python3 run.py --deploy
```

**Or**:
```python
from export.core.trivial_exporter import TrivialFrontmatterExporter
exporter = TrivialFrontmatterExporter()
exporter.export_all()
```

**Result**: Frontmatter files regenerated with `challenge_id` fields.

### Step 4: Verify

**Run tests**:
```bash
pytest tests/test_challenge_taxonomy.py -v
```

**Expected**:
- ✅ All settings have challenges
- ✅ All challenges have `challenge_id`
- ✅ IDs follow snake_case convention
- ✅ IDs match challenge text
- ✅ New challenge in taxonomy

**Query the challenge**:
```bash
python3 scripts/tools/query_challenges.py anodized_coating_protection
```

**Expected**: Returns all materials with the new challenge.

## Challenge Categories

### Thermal Management (18 challenges)

Heat-related processing challenges:

**Examples**:
- High thermal conductivity and heat spread
- Melting and heat-affected zone formation
- Thermal shock and microcracking
- Charring and carbonization
- Slow thermal diffusivity

**Typical Materials**: Metals, ceramics with thermal sensitivity

**Common Solutions**:
- Shorter pulse durations (picosecond/femtosecond)
- Increased scan speed
- Lower fluence
- Wavelength selection

### Surface Characteristics (19 challenges)

Material surface properties affecting laser cleaning:

**Examples**:
- High reflectivity
- Surface finish variations
- Porous structure with deep contamination
- Grain direction sensitivity
- Textured or embossed surfaces

**Typical Materials**: Metals, composites, treated surfaces

**Common Solutions**:
- Wavelength optimization
- Angle adjustment
- Multiple passes
- Surface preparation

### Contamination Challenges (12 challenges)

Specific contaminant types and removal difficulty:

**Examples**:
- Rust and oxide layer removal
- Oil and grease removal
- Paint and coating removal
- Adhesive and resin removal
- Biological and organic matter removal

**Typical Materials**: All materials, contaminant-dependent

**Common Solutions**:
- Higher fluence for tenacious contaminants
- Chemical pre-treatment
- Multiple wavelengths
- Sequential cleaning stages

## Data Quality

### Validation

**Test Suite**: `tests/test_challenge_taxonomy.py` (9 tests)

**Validated Properties**:
1. ✅ All 153 materials have challenges
2. ✅ All 804 challenges have `challenge_id`
3. ✅ All IDs follow snake_case format
4. ✅ All IDs correctly match challenge text
5. ✅ Taxonomy covers all challenge types (51)
6. ✅ Expected distribution maintained (42 metals share 6 challenges)
7. ✅ Required metadata present (severity, impact, solutions)
8. ✅ Only 3 valid categories
9. ✅ Query tool compatible (804 instances indexed)

**Run validation**:
```bash
pytest tests/test_challenge_taxonomy.py -v
```

### Coverage Statistics

**Current Status** (December 16, 2025):
- Materials: 153
- Challenge instances: 804
- Unique challenge types: 51
- Average challenges per material: 5.2
- Test pass rate: 100% (9/9)

**Distribution**:
- Top 6 challenges: 42 materials each (common metal challenges)
- Medium frequency: 21 materials each
- Low frequency: 1-10 materials each

## Architecture Decisions

### ADR-007: Challenge Hybrid Approach

**Decision**: Embed challenges with standardized IDs (not separate domain)

**Trade-offs**:

**Advantages** ✅:
- Material context preserved (reflectivity values, thermal limits)
- Solutions are material-specific
- No additional API calls (data already in settings)
- Static site compatible (no database needed)
- Queryable via challenge_id

**Disadvantages** ⚠️:
- Some redundancy (same challenge text across materials)
- Must re-export to update IDs
- Query tool loads all settings (acceptable: 153 files, <100ms)

**Rejected Alternatives**:

**Option A: Separate Challenge Domain** ❌
- **Why rejected**: Challenges don't exist independently
- **Problem**: Would need material references, losing context
- **Complexity**: Bidirectional linkages, API overhead

**Option B: Fully Embedded (no IDs)** ❌
- **Why rejected**: Not queryable
- **Problem**: Can't find "all materials with high reflectivity"
- **Workaround**: Manual search of 153 files

**See**: `docs/decisions/ADR-007-challenge-hybrid-approach.md`

## Integration Points

### Exporter

**File**: `export/core/trivial_exporter.py`

**Method**: `_enrich_challenges_with_ids(challenges: Dict) -> Dict`

**Location**: Line ~1645

**Flow**:
1. Load material settings from `Settings.yaml`
2. Extract `challenges` dictionary
3. Call `_enrich_challenges_with_ids()`
4. Add `challenge_id` to each challenge
5. Export to frontmatter with enriched data

**Key Code**:
```python
def _enrich_challenges_with_ids(self, challenges: Dict) -> Dict:
    """Add standardized challenge_id to each challenge."""
    enriched = {}
    for category in ['thermal_management', 'surface_characteristics', 'contamination_challenges']:
        if category in challenges:
            enriched[category] = []
            for challenge in challenges[category]:
                enriched_challenge = challenge.copy()
                challenge_text = challenge.get('challenge', '')
                if challenge_text:
                    # Convert to snake_case
                    challenge_id = challenge_text.lower().replace(' ', '_').replace('-', '_')
                    enriched_challenge['challenge_id'] = challenge_id
                enriched[category].append(enriched_challenge)
    return enriched
```

### Query Tool

**File**: `scripts/tools/query_challenges.py`

**Functionality**:
- Loads all settings frontmatter
- Indexes challenges by `challenge_id`
- Provides query, stats, list commands

**Performance**:
- Load time: ~100ms (153 files)
- Query time: <10ms
- Memory: ~5MB

**See**: `scripts/tools/README_query_challenges.md`

### Tests

**File**: `tests/test_challenge_taxonomy.py`

**Coverage**:
- Data integrity (all materials have challenges)
- ID format validation (snake_case)
- ID accuracy (matches challenge text)
- Taxonomy completeness (51 types)
- Metadata presence (severity, impact, solutions)
- Query compatibility (indexing works)

**Status**: 9/9 passing (100%)

## Best Practices

### When to Add New Challenges

**Add if**:
✅ Challenge affects multiple materials (potential for reuse)
✅ Challenge requires specific solutions or equipment
✅ Challenge is distinct from existing taxonomy

**Don't add if**:
❌ Challenge is material-specific variant (add detail to existing)
❌ Challenge overlaps with existing (refine existing instead)
❌ Challenge is too broad ("hard to clean" - not actionable)

**Example**:
```yaml
# ✅ GOOD - Specific, actionable, affects multiple materials
- challenge: High reflectivity at 1064nm
  challenge_id: high_reflectivity_at_1064nm
  
# ❌ BAD - Too broad, not actionable
- challenge: Difficult cleaning
  challenge_id: difficult_cleaning
  
# ❌ BAD - Too specific, single material
- challenge: Aluminum 7075-T6 surface oxidation
  challenge_id: aluminum_7075_t6_surface_oxidation
  # Better: Use "rust_and_oxide_layer_removal" with property_value details
```

### Challenge Text Guidelines

**Rules**:
1. **Descriptive**: Clear what the challenge is
2. **Specific**: Not too broad or vague
3. **Action-oriented**: Implies what needs to be addressed
4. **Stable**: Avoid frequent text changes (IDs derive from text)

**Good Examples**:
- "High reflectivity" ✅ (clear, specific, stable)
- "Thermal shock and microcracking" ✅ (descriptive, actionable)
- "Oil and grease removal" ✅ (specific contaminant type)

**Bad Examples**:
- "Cleaning problems" ❌ (too vague)
- "Various surface issues" ❌ (not specific)
- "High reflectivity (updated 2025)" ❌ (includes volatile data)

### Severity Guidelines

**Levels**:
- **low**: Minor inconvenience, workaround available
- **moderate**: Requires adjustment, success still likely
- **high**: Major challenge, specialized approach needed
- **critical**: May prevent laser cleaning entirely

**Example Progression**:
```yaml
# Low severity - minor adjustment needed
- challenge: Light surface scratches
  severity: low
  impact: Slight variation in cleaning uniformity
  
# Moderate severity - requires technique adjustment
- challenge: Surface finish variations
  severity: moderate
  impact: Inconsistent cleaning results across surface
  
# High severity - specialized equipment needed
- challenge: High reflectivity
  severity: high
  impact: Most laser energy reflected, requiring higher power or wavelength shift
  
# Critical severity - may not be feasible
- challenge: Extreme thermal shock sensitivity
  severity: critical
  impact: Material fractures during cleaning, laser not recommended
```

## Troubleshooting

### Challenge Not Found in Query

**Symptom**: `query_challenges.py` returns no results for known challenge

**Possible Causes**:
1. Typo in challenge_id
2. Settings not re-exported after taxonomy update
3. Challenge text changed (ID changed)

**Solutions**:
```bash
# List all valid IDs
python3 scripts/tools/query_challenges.py --list-challenges

# Re-export settings
python3 run.py --deploy

# Check taxonomy
cat data/materials/ChallengeTaxonomy.yaml | grep -A2 "challenge_name"
```

### ID Mismatch

**Symptom**: Test fails with "challenge_id doesn't match challenge text"

**Cause**: Manual `challenge_id` entry doesn't match auto-generated ID

**Solution**: Remove manual `challenge_id` from Settings.yaml, let exporter generate:
```yaml
# ❌ WRONG - Manual ID that doesn't match
- challenge: High reflectivity
  challenge_id: reflectivity_issues  # Doesn't match!
  
# ✅ RIGHT - Let exporter generate
- challenge: High reflectivity
  # challenge_id added automatically during export
```

### Missing challenge_id

**Symptom**: Query tool crashes or test fails

**Cause**: Frontmatter exported before enrichment implemented

**Solution**: Re-export with current exporter:
```bash
python3 run.py --deploy
pytest tests/test_challenge_taxonomy.py -v  # Verify
```

## Future Enhancements

### Potential Additions

1. **Challenge Severity Analysis**
   - Aggregate severity across materials
   - Identify most problematic challenges
   - Prioritize equipment upgrades

2. **Solution Library**
   - Standardized solution taxonomy
   - Link solutions to equipment specifications
   - Success rate tracking

3. **Challenge Dependencies**
   - Challenges that co-occur frequently
   - Challenges that contradict (mutually exclusive solutions)
   - Challenge hierarchies

4. **Material Recommendations**
   - Reverse query: "Find materials without challenge X"
   - Suitability scoring based on challenge profile
   - Alternative material suggestions

### Extension Points

**Challenge Metadata**:
```yaml
- challenge: High reflectivity
  challenge_id: high_reflectivity
  severity: high
  # NEW FIELDS (future)
  equipment_requirements: ["UV laser", "High power (>500W)"]
  estimated_difficulty: 7.5/10
  success_rate: 85%
  avg_cleaning_time: "2-3 minutes per m²"
```

**Challenge Relationships**:
```yaml
high_reflectivity:
  name: "High reflectivity"
  # NEW FIELDS (future)
  related_challenges: ["surface_finish_variations"]
  contradicts: []  # Mutually exclusive solutions
  co_occurs_with: ["high_thermal_conductivity_and_heat_spread"]
```

## Summary

**Key Points**:
1. ✅ Challenges are **embedded attributes** with **standardized IDs**
2. ✅ `challenge_id` enables **cross-material querying**
3. ✅ Challenge text determines ID (deterministic, no manual maintenance)
4. ✅ Taxonomy provides **51 standardized challenges** across 3 categories
5. ✅ Query tool enables **efficient cross-material analysis**
6. ✅ Tests validate **100% data integrity** (9/9 passing)
7. ✅ Export auto-generates IDs (zero manual work)

**Architecture Trade-off**: Slight redundancy (same text across materials) for major benefit (material-specific context + queryability).

**Result**: Best of both worlds - embedded data richness with separate domain queryability.

## Related Documentation

- **ADR-007**: Challenge Hybrid Approach rationale
- **Query Tool README**: `scripts/tools/README_query_challenges.md`
- **Test Suite**: `tests/test_challenge_taxonomy.py`
- **Taxonomy**: `data/materials/ChallengeTaxonomy.yaml`
- **Exporter**: `export/core/trivial_exporter.py` (line ~1645)
