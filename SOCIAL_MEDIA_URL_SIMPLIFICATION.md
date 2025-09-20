# Social Media Image URL Simplification

## Change Summary

Simplified social media image URLs by removing the `-social` suffix. Social media images now use the same URLs as microscopic images for consistency and simplicity.

## Pattern Change

### Before
- **Microscopic Images**: `*-laser-cleaning-micro.jpg`
- **Social Media Images**: `*-laser-cleaning-micro-social.jpg` 

### After  
- **Microscopic Images**: `*-laser-cleaning-micro.jpg`
- **Social Media Images**: `*-laser-cleaning-micro.jpg` ✅ (same as microscopic)

## Files Modified

### Generator Templates
- **`components/caption/generators/generator.py`**: Updated `og_image` pattern from `*-laser-cleaning-micro-social.jpg` to `*-laser-cleaning-micro.jpg`

### Schema Updates
- **`schemas/material.json`**: Updated example from `/images/aluminum-laser-cleaning-micro-social.jpg` to `/images/aluminum-laser-cleaning-micro.jpg`

### Example Files
- **`content/components/caption/limestone-laser-cleaning.yaml`**: Updated og_image
- **`content/components/caption/aluminum-laser-cleaning.yaml`**: Updated og_image

### Documentation Updates
- **`IMAGE_URL_PATTERN_UPDATE.md`**: Updated examples and patterns
- **`IMAGE_PATH_DEVIATION_ANALYSIS.md`**: Simplified pattern list

## Rationale

1. **Simplicity**: One URL pattern instead of two for the same image
2. **Consistency**: Social media and content use the same image URL
3. **Maintenance**: Fewer URL patterns to manage and maintain
4. **Performance**: Same image can be cached and reused for both purposes

## Final URL Patterns

The system now uses only 2 image URL patterns:

1. **`*-laser-cleaning-micro.jpg`** - for detailed/microscopic images and social media
2. **`*-laser-cleaning-hero.jpg`** - for main/hero images

## Impact

- ✅ **No breaking changes**: Old social media URLs can redirect to micro URLs if needed
- ✅ **Generator updated**: New caption generations use simplified pattern
- ✅ **Schema updated**: Examples reflect new pattern
- ✅ **Documentation updated**: All docs reflect simplified patterns

## Testing

- ✅ Aluminum caption generation: Uses new pattern correctly
- ✅ Limestone caption generation: Uses new pattern correctly  
- ✅ No remaining `micro-social.jpg` references in codebase

## Date
September 19, 2025
