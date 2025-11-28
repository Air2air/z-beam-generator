# Distribution Research Quick Reference

## Overview

**Distribution patterns now have EQUAL research depth as visual characteristics.**

- **Before**: 1 distribution field (distribution_factors)
- **After**: 8 distribution fields with detailed prompts
- **Total fields**: 15 (7 visual + 8 distribution)

## New Distribution Fields

| Field | What It Captures | Example |
|-------|-----------------|---------|
| **distribution_patterns** | Types of distribution (uniform, edge, patchy, streaky, etc.) | "Edge-initiated spreading with localized patches" |
| **uniformity_assessment** | How uniform (perfectly uniform → highly variable) | "Moderately patchy - concentrates at moisture points" |
| **concentration_variations** | Where heavy vs light (edges, corners, flat areas) | "Heavy at edges and bottom, light on flat surfaces" |
| **typical_formations** | Physical formations (drips, pools, films, crusts) | "Drip marks on verticals, pools in recessed areas" |
| **geometry_effects** | How surface shape affects it | "Accumulates heavily in corners and crevices" |
| **gravity_influence** | Role of gravity | "Runs downward, pools at bottom edges" |
| **coverage_ranges** | Percentage ranges for light/moderate/heavy | "Sparse <10%, Heavy 60-85%" |
| **edge_center_behavior** | Edge vs center preference | "Strongly prefers edges, spreads inward over time" |
| **buildup_progression** | How it accumulates over time | "Hours: surface film, Days: patches, Months: crust" |

## Research Commands

### Single Pattern, Single Category
```bash
export GEMINI_API_KEY="your_key"

# Research rust on metals
python3 scripts/research/populate_visual_appearances_all_categories.py \
    --pattern rust-oxidation \
    --category metal
```

### Single Pattern, Multiple Categories
```bash
# Research oil on metals, ceramics, and glasses
python3 scripts/research/populate_visual_appearances_all_categories.py \
    --pattern oil-grease \
    --category metal,ceramic,glass
```

### Single Pattern, ALL Categories
```bash
# Research paint across all 159 materials
python3 scripts/research/populate_visual_appearances_all_categories.py \
    --pattern paint-coating
```

### All Patterns (High API Usage)
```bash
# Complete research - use with caution
python3 scripts/research/populate_visual_appearances_all_categories.py \
    --all
```

### List Available Categories
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py \
    --list-categories

# Output:
# metal (30 materials)
# ceramic (18 materials)
# glass (12 materials)
# stone (15 materials)
# composite (8 materials)
# plastic (24 materials)
# wood (20 materials)
# masonry (8 materials)
# rare-earth (16 materials)
# semiconductor (8 materials)
```

## Expected YAML Output

Research populates 15 fields per material:

```yaml
contamination_patterns:
  oil-grease:
    visual_characteristics:
      appearance_on_materials:
        aluminum:
          # Visual characteristics (7 fields)
          description: "Oil appears as dark patches with rainbow sheen..."
          color_variations: "Fresh: Amber, Aged: Dark brown to black..."
          texture_details: "Fresh: Smooth and glossy, Aged: Sticky and matte..."
          common_patterns: "Drip marks, pooling at edges..."
          aged_appearance: "Fresh: Glossy, Aged: Crusty with dust..."
          lighting_effects: "Rainbow iridescence under direct light..."
          thickness_range: "Thin film 0.05mm to pools 5mm..."
          
          # Distribution characteristics (8 fields - EQUAL DETAIL)
          distribution_patterns: "Irregular drip marks on verticals, pools in recessed areas, sharp boundaries..."
          uniformity_assessment: "Highly variable - concentrates at contact points and low spots..."
          concentration_variations: "Heavy at bottom edges and corners, light on exposed flat surfaces..."
          typical_formations: "Drip marks, runs, pools, films, fingerprints clearly visible..."
          geometry_effects: "Accumulates in corners, fills crevices, pools on horizontal surfaces..."
          gravity_influence: "Flows downward, pools at bottom edges, drip marks from top to bottom..."
          coverage_ranges: "Sparse <5%: Thin film, Heavy 60%+: Thick pools with crusty edges..."
          edge_center_behavior: "Prefers edges and perimeter - collects at boundaries..."
          buildup_progression: "Hours: Glossy film, Days: Darker and tackier, Months: Crusty black buildup..."
```

## Quality Validation

### Check Distribution Detail

After research, verify distribution fields are as detailed as visual fields:

**✅ GOOD - Equal Detail**:
```
color_variations: 89 words, 3 specific examples with progression
distribution_patterns: 91 words, 4 specific patterns with locations
```

**❌ BAD - Distribution Under-Detailed**:
```
color_variations: 89 words, 3 specific examples with progression
distribution_patterns: 12 words, generic statement
```

### Re-Research if Needed

If distribution fields are significantly shorter, re-run with force flag:
```bash
python3 scripts/research/populate_visual_appearances_all_categories.py \
    --pattern oil-grease \
    --category metal \
    --force  # Overwrites existing data
```

## API Usage

### Token Estimates

- **Per material**: ~2,000-3,000 tokens (was ~1,200-1,800)
- **Increase**: ~50-70% due to 8 additional fields
- **Single pattern, all 159 materials**: ~318,000-477,000 tokens

### Batch Strategy

**Recommended: Category-by-category**
```bash
# Day 1: Metals (30 materials)
--pattern oil-grease --category metal

# Day 2: Ceramics (18 materials)
--pattern oil-grease --category ceramic

# Day 3: Glasses (12 materials)
--pattern oil-grease --category glass

# etc...
```

This spreads API costs and allows quality validation between batches.

## Image Generation Impact

Enhanced distribution data improves AI image generation:

### Spatial Accuracy
- **Before**: Generic "accumulates in areas"
- **After**: "Edge-initiated spreading, pools in recessed corners, drips on verticals"

### Realistic Coverage
- **Before**: Uniform or random
- **After**: "Sparse <10% shows thin film, Heavy 70% shows thick pools with crusty edges"

### Temporal Progression
- **Before**: Generic "ages over time"
- **After**: "Hours: Glossy amber film, Days: Tacky brown patches, Months: Crusty black buildup"

## Troubleshooting

### Field Missing in Output
If a distribution field is missing, the researcher will warn:
```
⚠️  Missing field in response: distribution_patterns
```
The field will default to "Not researched". Re-run research or add manually.

### Parse Error
If Gemini returns invalid JSON:
```
❌ Failed to parse JSON response
```
All fields will show "Parse failed - see description". Check API logs for response format issues.

### Low Detail in Distribution Fields
If distribution fields are generic:
1. Check prompt includes all 8 distribution questions (code updated Nov 26, 2025)
2. Verify Gemini API is using Flash 2.0 model (temperature: 0.3)
3. Re-run with --force flag to regenerate

## Next Steps

1. **Test**: Run small batch to verify quality
   ```bash
   python3 scripts/research/populate_visual_appearances_all_categories.py \
       --pattern oil-grease \
       --category metal
   ```

2. **Validate**: Check Contaminants.yaml for equal distribution detail

3. **Scale**: Run category-by-category for remaining patterns

4. **Generate**: Use populated data for contamination images
   ```bash
   python3 shared/commands/image_generation_handler.py \
       "Generate Aluminum oil contamination before after"
   ```

## Related Documentation

- `DISTRIBUTION_RESEARCH_ENHANCEMENT_NOV26_2025.md` - Complete implementation details
- `VISUAL_APPEARANCE_ALL_CATEGORIES_GUIDE.md` - Original research system
- `IMAGE_GENERATION_HANDLER_QUICK_REF.md` - Image generation commands
- `domains/contaminants/research/visual_appearance_researcher.py` - Source code

## Status

✅ **COMPLETE** - Distribution research enhanced (Nov 26, 2025)  
✅ **TESTED** - Import and field structure validated  
✅ **READY** - Production research with Gemini API

Distribution patterns now receive **equal research depth** as visual characteristics.
