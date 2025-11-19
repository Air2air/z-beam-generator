# Regions Content Type

Geographic and regulatory frontmatter generation for laser cleaning markets.

## Structure

- `generator.py` - RegionFrontmatterGenerator class
- `image_prompts.py` - RegionImagePromptGenerator for image generation
- `data.yaml` - 7 regions + 9 Bay Area counties with image prompts
- `images/` - Generated images (if created)
- `output/` - Generated frontmatter files

## Usage

### Generate Frontmatter
```bash
# Generate region frontmatter
python3 run.py --content-type region --identifier "north_america"
python3 run.py --content-type region --identifier "europe"
```

### Generate Image Prompts
```bash
# Generate prompts only (no API cost)
python3 scripts/research/populate_region_images.py
# Select option 1

# Generate prompts + images (uses Gemini API, ~$4.64)
python3 scripts/research/populate_region_images.py
# Select option 2
```

## Image Generation System

Each region, county, and city can have **two AI-generated images**:

1. **Historical Photo** - Period-appropriate city/county scene
   - Black and white photography
   - Historical architecture and landmarks
   - Vintage vehicles and era-specific details
   - 4:3 aspect ratio (classic photo format)

2. **Business Photo** - Modern laser cleaning operation
   - Local business using laser cleaning
   - Industry-specific applications
   - Professional workplace setting
   - 16:9 aspect ratio (modern format)

### Image Prompt Features

- **Contextual**: Uses actual region data (industries, landmarks, cities)
- **Authentic**: Period-appropriate historical details
- **Professional**: Photography terminology for quality output
- **Gemini-optimized**: Designed for Google's Imagen 4 model

### Pricing

- **Prompts only**: FREE (just generates text prompts)
- **With images**: ~$0.02 per image via Gemini API
  - 7 regions × 2 = $0.28
  - 9 counties × 2 = $0.36
  - Total: ~$4.64 for all regions + counties

## Data Structure

Each region in `data.yaml` includes:
- Countries covered
- Market size and growth rate
- Regulatory framework
- Common applications
- Key agencies
- **NEW**: `imagePrompts` (historical + business)
- **NEW**: `imageFiles` (paths to generated images, if created)

### Image Prompt Structure
```yaml
regions:
  north_america:
    imagePrompts:
      historical: "Historical photograph from 1950s industrial America..."
      business: "Professional photograph of modern automotive plant..."
    imageFiles:  # Only present if images generated
      historical: "regions/images/north_america/north_america_historical.png"
      business: "regions/images/north_america/north_america_business.png"
```

## Available Regions

- `north_america` - USA, Canada, Mexico
- `europe` - EU member states
- `asia_pacific` - China, Japan, South Korea, etc.
- `middle_east` - UAE, Saudi Arabia, etc.
- `south_america` - Brazil, Argentina, Chile, etc.
- `africa` - South Africa, Nigeria, etc.
- `san_francisco_bay_area` - 9 counties, 100+ cities (detailed coverage)

## Bay Area Coverage

The San Francisco Bay Area has comprehensive coverage with:
- **9 Counties**: Alameda, Contra Costa, Marin, Napa, San Francisco, San Mateo, Santa Clara, Solano, Sonoma
- **100+ Cities**: All major cities with individual data
- **Detailed Industries**: Semiconductor, biotech, wine production, aerospace, etc.
- **Image Prompts**: County-specific historical scenes and industry applications

## Setup for Image Generation

1. **Install Google GenAI SDK**:
   ```bash
   pip install google-genai
   ```

2. **Get Gemini API Key**:
   - Visit: https://aistudio.google.com/apikey
   - Copy your API key

3. **Set Environment Variable**:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

4. **Run Script**:
   ```bash
   python3 scripts/research/populate_region_images.py
   ```

## Workflow

1. **Generate prompts first** (no cost) - Review and refine
2. **Edit prompts** in `data.yaml` if needed
3. **Generate images** (costs ~$4.64) - Creates actual PNG files
4. **Use images** in frontmatter and website

This approach avoids regenerating expensive images unnecessarily!
