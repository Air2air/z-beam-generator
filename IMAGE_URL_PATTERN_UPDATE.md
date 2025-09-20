# Image URL Pattern Update

## Change Summary

Updated the image URL pattern in the caption generator from `*cleaning-analysis.jpg` to `*laser-cleaning-micro.jpg` to maintain consistency with the frontmatter generator pattern.

## Files Modified

### Generator Templates
- **`components/caption/generators/generator.py`**: Updated image URL pattern from `{material_name.lower().replace(' ', '-')}-cleaning-analysis.jpg` to `{material_name.lower().replace(' ', '-')}-laser-cleaning-micro.jpg`
- **`components/caption/generators/generator.py`**: Updated social media image URL pattern from `{material_name.lower().replace(' ', '-')}-cleaning-analysis-social.jpg` to `{material_name.lower().replace(' ', '-')}-laser-cleaning-micro.jpg`

### Schema Updates
- **`schemas/material.json`**: Updated example from `/images/aluminum-cleaning-analysis-social.jpg` to `/images/aluminum-laser-cleaning-micro.jpg`

### Test Files (Example)
- **`content/components/caption/limestone-laser-cleaning.yaml`**: Updated as example of new pattern
- **`content/components/caption/aluminum-laser-cleaning.yaml`**: Regenerated with new pattern

## Pattern Comparison

### Before (Old Pattern)
```
/images/limestone-cleaning-analysis.jpg
/images/limestone-cleaning-analysis-social.jpg
```

### After (New Pattern)  
```
/images/limestone-laser-cleaning-micro.jpg
/images/limestone-laser-cleaning-micro.jpg
```

## Consistency Achieved

All components now use the same URL pattern:

- **Frontmatter**: `{subject_slug}-laser-cleaning-micro.jpg` ✅ (already correct)
- **Caption**: `{material_name.lower().replace(' ', '-')}-laser-cleaning-micro.jpg` ✅ (updated)
- **JSON-LD**: Uses frontmatter image URLs ✅ (already correct)

## Impact

### Generated Files
- **New generations**: Will automatically use the new pattern
- **Existing files**: Maintain old pattern until regenerated (107 files as of change)
- **No breaking changes**: Old URLs remain functional during transition

### Testing
- ✅ Caption generator test passes
- ✅ URL pattern verification confirms change working
- ✅ Aluminum and limestone test generations successful

## Regeneration Required

To apply the new pattern to all existing caption files, run:

```bash
python3 run.py --all --components caption
```

This will regenerate all caption files with the new URL pattern.

## Date
September 19, 2025
