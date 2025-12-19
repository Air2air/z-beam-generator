# URL Format Fix - December 19, 2025

## Problem

All internal URLs in frontmatter files were using **WRONG format**:
- ❌ **Actual**: `/contaminants/organic-residue/adhesive/adhesive-residue` (nested category paths, no suffix)
- ✅ **Expected**: `/contaminants/adhesive-residue-contamination` (flat with domain suffix)

This affected 424 frontmatter files across all domains.

## Root Cause

The issue had TWO parts:

### Part 1: Old Data in Materials.yaml
- **Materials.yaml** had old relationship data with wrong URLs already baked in
- Example: `relationships.related_contaminants` array with nested category URLs
- These were exported from an earlier system version

### Part 2: Key Name Mismatch
- **DomainLinkagesService** generates NEW key names: `contaminants`, `materials`, `compounds`
- **Materials.yaml** had OLD key names: `related_contaminants`, `related_materials`
- **RelationshipGroupingEnricher** was looking for OLD keys and finding wrong URLs
- Merge in relationships enricher kept BOTH keys → grouping enricher used wrong one

## Solution

### Fix 1: Remove Old Relationship Keys (MaterialsRestructureEnricher)
```python
# export/enrichers/linkage/materials_restructure_enricher.py

# REMOVE old relationship keys that will be regenerated
old_relationship_keys = ['related_contaminants', 'related_materials', 'related_compounds']
for key in old_relationship_keys:
    # Remove from root
    if key in frontmatter:
        frontmatter.pop(key)
    # Remove from relationships
    if key in frontmatter.get('relationships', {}):
        frontmatter['relationships'].pop(key)
```

### Fix 2: Update Key Names (RelationshipGroupingEnricher)
```python
# export/enrichers/linkage/relationship_grouping_enricher.py

# OLD (WRONG):
contaminants = relationships.get('related_contaminants', [])

# NEW (CORRECT):
contaminants = relationships.get('contaminants', [])  # NEW KEY from DomainLinkagesService
```

Changed at 3 locations:
- Line 136: `_group_materials_relationships()` - contaminants
- Line 360: `_group_settings_relationships()` - materials  
- Line 375: `_group_settings_relationships()` - contaminants

## Files Modified

1. **export/enrichers/linkage/materials_restructure_enricher.py**
   - Added code to remove old relationship keys from source data
   - Ensures clean slate before DomainLinkagesService populates new keys

2. **export/enrichers/linkage/relationship_grouping_enricher.py**
   - Updated 3 `.get()` calls to use NEW key names
   - Now correctly reads from DomainLinkagesService output

## Verification

```python
import yaml

with open('../z-beam/frontmatter/materials/steel-laser-cleaning.yaml', 'r') as f:
    data = yaml.safe_load(f)

groups = data['relationships']['contaminants']['groups']
first_item = next(iter(groups.values()))['items'][0]
print(first_item['url'])
# ✅ Output: /contaminants/adhesive-residue-contamination (CORRECT!)
```

## Results

- ✅ All 424 frontmatter files regenerated with correct URLs
- ✅ Materials → Contaminants: `/contaminants/{slug}-contamination`
- ✅ Contaminants → Materials: `/materials/{slug}-laser-cleaning`
- ✅ Contaminants → Compounds: `/compounds/{slug}-compound`
- ✅ All URLs now use flat structure with domain suffix

## Related Issues

- This fix also resolves the key name inconsistency between old and new systems
- Old keys (`related_*`) are now deprecated and removed on export
- New keys (`contaminants`, `materials`, `compounds`) are the standard

## Testing Commands

```bash
# Export all domains
python3 run.py --export-all

# Verify URLs in specific file
python3 << 'EOF'
import yaml
with open('../z-beam/frontmatter/materials/aluminum-laser-cleaning.yaml', 'r') as f:
    data = yaml.safe_load(f)
items = data['relationships']['contaminants']['groups']['organic_residues']['items']
for item in items[:5]:
    print(item['url'])
EOF
```

All URLs should follow the pattern: `/{domain}/{slug}-{suffix}`
- materials: `/materials/{slug}-laser-cleaning`
- contaminants: `/contaminants/{slug}-contamination`
- compounds: `/compounds/{slug}-compound`
- settings: `/settings/{slug}-setting`
