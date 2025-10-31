# Region Images Directory

This directory stores AI-generated images for regions, counties, and cities.

## Structure

Images are saved with standardized naming:
```
{region_name}_historical.png  - Historical photo (4:3 aspect ratio)
{region_name}_business.png    - Business photo (16:9 aspect ratio)
```

## Generation

Images are generated using the Gemini Imagen API:

```bash
# Generate prompts only (no cost)
python3 scripts/research/populate_region_images.py
# Select option 1

# Generate prompts + images (~$4.64 cost)
python3 scripts/research/populate_region_images.py
# Select option 2
```

## Web Access

Images are web-accessible via:
```
/images/regions/{region_name}_historical.png
/images/regions/{region_name}_business.png
```

## Storage

- **Directory**: `/public/images/regions/`
- **Format**: PNG
- **Historical**: 4:3 aspect ratio (classic photo format)
- **Business**: 16:9 aspect ratio (modern wide format)
- **Quality**: High resolution with SynthID watermark (Gemini default)

## Current Coverage

Expected images:
- 7 regions × 2 images = 14 images
- 9 Bay Area counties × 2 images = 18 images
- **Total**: 32 images (~$0.64 at $0.02 per image)

Optional: 100+ Bay Area cities can be added later.

## Example URLs

```
/images/regions/north_america_historical.png
/images/regions/north_america_business.png
/images/regions/alameda_county_historical.png
/images/regions/alameda_county_business.png
/images/regions/san_francisco_historical.png
/images/regions/san_francisco_business.png
```

## Data Storage

Image metadata is stored in `regions/data.yaml`:

```yaml
regions:
  north_america:
    imagePrompts:
      historical: "Historical photograph from..."
      business: "Professional photograph of..."
    imageFiles:
      historical: "/images/regions/north_america_historical.png"
      business: "/images/regions/north_america_business.png"
```
