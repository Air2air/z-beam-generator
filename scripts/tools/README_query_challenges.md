# Challenge Query Tool

Query materials by challenge characteristics for cross-material analysis.

## Quick Start

```bash
# Find all materials with specific challenge
python3 scripts/tools/query_challenges.py high_reflectivity

# Show statistics
python3 scripts/tools/query_challenges.py --stats

# List all challenge IDs
python3 scripts/tools/query_challenges.py --list-challenges
```

## Usage

### Query by Challenge ID

Find all materials affected by a specific challenge:

```bash
python3 scripts/tools/query_challenges.py high_reflectivity
```

**Output**:
```
🔍 Materials with challenge: high_reflectivity
================================================================================
Found 42 materials

📌 Aluminum (aluminum-laser-cleaning)
   Category: surface_characteristics
   Challenge: High reflectivity
   Severity: high
   Impact: Most laser energy reflected, requiring higher power; safety hazard...

📌 Stainless Steel 316 (stainless-steel-316-laser-cleaning)
   Category: surface_characteristics
   Challenge: High reflectivity
   Severity: high
   Impact: Most laser energy reflected, requiring higher power; safety hazard...

[... 40 more materials]
```

### Statistics Mode

View challenge distribution across all materials:

```bash
python3 scripts/tools/query_challenges.py --stats
```

**Output**:
```
📊 Challenge Statistics
============================================================
Materials with challenges: 153
Total challenge instances: 804
Unique challenge types: 51

🔝 Top 10 Most Common Challenges:
------------------------------------------------------------
 1. high_thermal_conductivity_and_heat_spread   ( 42 materials)
 2. melting_and_heat_affected_zone_formation    ( 42 materials)
 3. high_reflectivity                           ( 42 materials)
 4. surface_finish_variations                   ( 42 materials)
 5. rust_and_oxide_layer_removal                ( 42 materials)
 6. oil_and_grease_removal                      ( 42 materials)
 7. charring_and_carbonization                  ( 21 materials)
 8. slow_thermal_diffusivity                    ( 21 materials)
 9. grain_direction_sensitivity                 ( 21 materials)
10. porous_structure_with_deep_contamination    ( 21 materials)
```

### List All Challenges

View all available challenge IDs:

```bash
python3 scripts/tools/query_challenges.py --list-challenges
```

**Output**:
```
📋 All Challenge IDs (51 unique)
============================================================
anisotropic_thermal_properties                           (  4 materials)
charring_and_carbonization                               ( 21 materials)
coating_and_film_removal                                 (  1 materials)
coating_and_label_removal                                (  2 materials)
[... 47 more]
```

## Challenge ID Format

Challenge IDs follow snake_case convention:

| Challenge Name | Challenge ID |
|----------------|-------------|
| High reflectivity | `high_reflectivity` |
| Thermal shock and microcracking | `thermal_shock_and_microcracking` |
| Rust and oxide layer removal | `rust_and_oxide_layer_removal` |

## Common Use Cases

### Find Materials Suitable for Specific Laser Systems

**Scenario**: You have a UV laser (355nm) and want to find materials where high reflectivity is a challenge.

```bash
python3 scripts/tools/query_challenges.py high_reflectivity
# Returns 42 materials where UV wavelength helps with absorption
```

### Analyze Thermal Management Requirements

**Scenario**: Planning thermal management for manufacturing line.

```bash
python3 scripts/tools/query_challenges.py high_thermal_conductivity_and_heat_spread
# Returns all metals requiring careful thermal control
```

### Identify Materials with Specific Contamination Issues

**Scenario**: Cleaning equipment specialized for rust removal.

```bash
python3 scripts/tools/query_challenges.py rust_and_oxide_layer_removal
# Returns all materials where rust is a common contaminant
```

### Cross-Category Analysis

**Scenario**: Find materials with multiple challenge categories.

```bash
# Materials with thermal challenges
python3 scripts/tools/query_challenges.py thermal_shock_and_microcracking

# Materials with surface challenges
python3 scripts/tools/query_challenges.py porous_structure_with_deep_contamination

# Materials with contamination challenges
python3 scripts/tools/query_challenges.py oil_and_grease_removal
```

## Data Source

Challenge data comes from:
- **Settings files**: `frontmatter/settings/*.yaml`
- **Taxonomy**: `data/materials/ChallengeTaxonomy.yaml`
- **Exporter**: Auto-generates `challenge_id` fields during export

## Challenge Categories

Challenges are organized into three categories:

### 1. Thermal Management
Heat-related challenges during laser processing:
- High thermal conductivity and heat spread
- Melting and heat-affected zone formation
- Thermal shock and microcracking
- Charring and carbonization
- [18 total thermal challenges]

### 2. Surface Characteristics
Material surface properties affecting cleaning:
- High reflectivity
- Surface finish variations
- Porous structure with deep contamination
- Grain direction sensitivity
- [19 total surface challenges]

### 3. Contamination Challenges
Specific contaminant types and removal difficulty:
- Rust and oxide layer removal
- Oil and grease removal
- Paint and coating removal
- Adhesive and resin removal
- [12 total contamination challenges]

## Output Fields

Each query result includes:

- **material_id**: Unique material identifier
- **material_name**: Display name
- **category**: Challenge category (thermal/surface/contamination)
- **challenge**: Human-readable challenge name
- **severity**: low | moderate | high | critical
- **impact**: Description of the challenge's effect (truncated to 80 chars)

## Technical Details

### Data Structure

Challenge data is embedded in settings frontmatter:

```yaml
material_challenges:
  thermal_management:
  - challenge: High thermal conductivity and heat spread
    challenge_id: high_thermal_conductivity_and_heat_spread
    severity: medium
    property_value: 4-400 W/(m·K) depending on metal
    impact: Heat spreads rapidly causing large heat-affected zones
    solutions:
    - Use shorter pulse durations (picosecond/femtosecond)
    - Increase scan speed to minimize dwell time
```

### Query Performance

- **Materials loaded**: 153
- **Load time**: ~100ms
- **Query time**: <10ms
- **Memory usage**: ~5MB

Performance is acceptable for:
- Interactive CLI use
- Automated analysis scripts
- CI/CD validation

## Related Tools

- **Taxonomy**: `data/materials/ChallengeTaxonomy.yaml` (canonical challenge definitions)
- **Exporter**: `export/core/trivial_exporter.py` (generates challenge_ids)
- **Tests**: `tests/test_challenge_taxonomy.py` (validates data quality)

## Architecture Decision

See **ADR-007: Material Challenges as Embedded Attributes** for architectural rationale.

**Key Decision**: Challenges are embedded in material settings (not a separate domain) because:
1. Challenge details vary by material (reflectivity ranges, thresholds)
2. Solutions are material-specific
3. Challenges don't exist independently

The `challenge_id` field enables querying while preserving material context.

## Troubleshooting

### "No materials found with challenge_id: X"

**Cause**: Invalid challenge ID or typo

**Solution**: 
```bash
# List all valid IDs
python3 scripts/tools/query_challenges.py --list-challenges

# Use exact snake_case format
python3 scripts/tools/query_challenges.py thermal_shock_and_microcracking
```

### Empty results for known challenge

**Cause**: Settings files not exported with challenge_ids

**Solution**:
```bash
# Re-export with challenge enrichment
python3 -c "from export.core.trivial_exporter import TrivialFrontmatterExporter; e = TrivialFrontmatterExporter(); e.export_all()"
```

### Query tool crashes on large results

**Cause**: Memory overflow (unlikely with 153 materials)

**Solution**: Redirect output to file
```bash
python3 scripts/tools/query_challenges.py high_reflectivity > results.txt
```

## Future Enhancements

Potential additions to query tool:

1. **Filter by severity**: `--severity high`
2. **Filter by category**: `--category metal`
3. **Export formats**: `--output json|csv|yaml`
4. **Aggregate analysis**: `--aggregate by-category`
5. **Comparison mode**: `--compare challenge1 challenge2`

## Contributing

To add new challenges:

1. **Update Taxonomy**: Add to `ChallengeTaxonomy.yaml`
2. **Add to Settings**: Update relevant material settings in `Settings.yaml`
3. **Re-export**: Run exporter to generate challenge_ids
4. **Verify**: Run `pytest tests/test_challenge_taxonomy.py`

The query tool will automatically detect new challenges.
