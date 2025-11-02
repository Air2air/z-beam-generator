# City Historical Images Specification

**Version:** 1.0.0  
**Created:** November 1, 2025  
**Purpose:** Define image generation and caption strategy for city pages

---

## Overview

Each city frontmatter page includes **1-3 randomly selected historical images** with descriptive captions. Images are generated using the existing `regions/image/generate.py` infrastructure with enhanced subject parameters.

---

## Frontmatter Structure

```yaml
images:
  historical:
    - path: "/images/regions/{city_slug}/{city_slug}_{year}_{subject_slug}.png"
      caption: "2-3 sentence description with specific visual details"
      year: 1935
      subject: "downtown streetscape"
      dimensions:
        width: 1920
        height: 1080
        aspect_ratio: "16:9"
      generation:
        prompt_used: "Full prompt sent to Imagen 4"
        population: 634394
        category: "major_city"
        generated_at: "2025-11-01T10:30:00Z"
```

---

## Image Generation Strategy

### Random Selection (1-3 Images per City)

```python
import random

def determine_image_count(city_population: int) -> int:
    """
    Determine number of images based on city size.
    
    Larger cities get more images for visual richness.
    Smaller cities get fewer to keep pages focused.
    
    Args:
        city_population: Current city population
    
    Returns:
        Number of images (1-3)
    """
    if city_population > 100000:  # Major cities
        return random.choice([2, 3])  # 2 or 3 images
    elif city_population > 20000:  # Small cities
        return random.choice([1, 2])  # 1 or 2 images
    else:  # Towns
        return random.choice([1, 1, 2])  # Mostly 1, occasionally 2
```

### Subject Variety

**Available Subjects** (ensure diversity across images):

1. **downtown streetscape** - Main commercial district
2. **harbor** - Port or waterfront (if coastal)
3. **main street** - Primary street with businesses
4. **train station** - Railroad depot (if historic rail hub)
5. **industrial district** - Factories or manufacturing
6. **residential neighborhood** - Housing areas
7. **city hall** - Government/civic buildings
8. **historic landmark** - Notable building or site

**Selection Logic:**
- First image: Most iconic subject for the city
- Second image: Different subject (no duplicates)
- Third image: Different subject (no duplicates)

**Example for San Francisco:**
1. "downtown streetscape" (Market Street)
2. "harbor" (Ferry Building/waterfront)
3. "chinatown district" (Grant Avenue)

### Decade Variety

**Spread across 1920s-1950s:**
- Image 1: Random decade (1920s-1950s)
- Image 2: Different decade from Image 1
- Image 3: Different decade from Images 1 & 2

**Decade Distribution:**
- 1920s: 20% (if city existed/was significant)
- 1930s: 30% (Great Depression era)
- 1940s: 30% (WWII/post-war)
- 1950s: 20% (post-war boom)

---

## Caption Requirements

### Structure (2-3 Sentences, 150-200 characters)

**Sentence 1:** Location and year context
- "{Location}, {Year} - {Primary visual element}"

**Sentence 2:** Specific visual details
- "{Period-appropriate details: vehicles, clothing, architecture}"

**Sentence 3:** Notable features or atmosphere
- "{Distinctive landmark, activity, or contextual element}"

### Example Captions

**Good Caption (specific, engaging):**
```
Downtown San Francisco, 1935 - Market Street bustling with streetcars, 
Model A Fords, and pedestrians in fedoras and knee-length dresses. 
The Ferry Building clock tower dominates the skyline.
```

**Bad Caption (generic, vague):**
```
A historical photograph of downtown San Francisco from the 1930s 
showing some buildings and people.
```

### Caption Quality Checklist

✅ **Include:**
- Specific year (not just "1930s")
- Exact location (street name or landmark)
- Period-appropriate details (vehicle models, clothing styles)
- Architectural specifics (building types, materials)
- Human activity (what people are doing)
- Local landmarks (recognizable features)

❌ **Avoid:**
- Generic descriptions ("old buildings", "people walking")
- Anachronisms (modern terms for historical scenes)
- Vague locations ("downtown", "the city")
- Passive voice ("was built", "was located")
- Unnecessary adjectives ("beautiful", "quaint")

---

## Image Generation Parameters

### Current Implementation (Existing)

**File:** `regions/image/generate.py`

```bash
python3 regions/image/generate.py \
  --city "San Francisco" \
  --county "San Francisco County" \
  --year 1935 \
  --photo-condition 3 \
  --scenery-condition 3 \
  --subject "downtown streetscape"
```

### Parameters to Pass

```python
{
    "city_name": "San Francisco",
    "county_name": "San Francisco County",
    "year": 1935,  # Specific year, not decade
    "photo_condition": 3,  # Default aged appearance (1-5 scale)
    "scenery_condition": 3,  # Default wear level (1-5 scale)
    "subject": "downtown streetscape",  # NEW: Subject focus
    "output_dir": f"public/images/regions/{city_slug}",
    "filename": f"{city_slug}_{year}_{subject_slug}.png"
}
```

### Future Enhancements (Not Yet Implemented)

**Enhanced Subject Parameters** (for later image researcher updates):

```python
{
    # Current parameters
    "city_name": str,
    "county_name": str,
    "year": int,
    "subject": str,
    
    # Future: Enhanced subject control
    "subject_type": "landmark" | "street" | "building" | "district",
    "specific_location": str,  # "Market Street", "Ferry Building", etc.
    "time_of_day": "morning" | "afternoon" | "evening",
    "weather": "clear" | "foggy" | "overcast",
    "season": "spring" | "summer" | "fall" | "winter",
    "focus_elements": ["architecture", "vehicles", "people", "signage"],
    "composition": "wide" | "medium" | "tight",
    
    # Caption generation hints
    "caption_style": "descriptive" | "narrative" | "technical",
    "highlight_features": ["buildings", "transportation", "fashion", "landmarks"]
}
```

---

## Caption Generation Methods

### Option 1: Gemini Vision Analysis (Recommended)

**Already implemented:** `regions/image/validator.py`

```python
from regions.image.validator import ImageValidator

def generate_caption_from_image(image_path: str, city: str, year: int) -> str:
    """
    Generate caption by analyzing generated image with Gemini Vision.
    
    Args:
        image_path: Path to generated image
        city: City name
        year: Historical year
    
    Returns:
        2-3 sentence descriptive caption
    """
    validator = ImageValidator(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    Analyze this historical photograph of {city} from {year}.
    
    Write a 2-3 sentence caption that includes:
    1. Specific location and year context
    2. Visual details: architecture, vehicles, clothing, activities
    3. Notable landmarks or atmospheric elements
    
    Style: Natural, engaging, specific (not generic).
    Focus on what you actually see in the image.
    Use active voice and concrete nouns.
    """
    
    # Use Gemini Vision to analyze image and generate caption
    response = validator.api_client.generate_content([prompt, image_path])
    caption = response.text.strip()
    
    return caption
```

**Cost:** ~$0.0002 per caption (negligible)

### Option 2: Template-Based Generation

**Fallback if vision analysis unavailable:**

```python
def generate_caption_from_metadata(
    city: str,
    year: int,
    subject: str,
    population_data: Dict
) -> str:
    """
    Generate caption from metadata without analyzing image.
    
    Less specific than vision analysis, but acceptable fallback.
    """
    templates = {
        "downtown streetscape": [
            f"Downtown {city}, {year} - {population_data['main_street']} bustling with {population_data['vehicles']}. {population_data['details']}.",
            f"{city}'s commercial district, {year} - {population_data['street_details']} {population_data['buildings']}."
        ],
        "harbor": [
            f"{city} Harbor, {year} - Wooden piers lined with vessels and maritime activity. {population_data['details']}.",
            f"Waterfront district, {year} - {city}'s port with ships and cargo operations. {population_data['transportation_context']}."
        ],
        # ... more templates for each subject type
    }
    
    template = random.choice(templates.get(subject, templates["downtown streetscape"]))
    return template
```

**Quality:** Lower than vision analysis, but deterministic and fast.

---

## Implementation Workflow

### County-Based Batch Processing

**User Input:**
```bash
# Generate frontmatter for all cities in a specific county
python3 run.py --region "San Mateo County"
```

**Workflow Steps:**

#### Step 1: Retrieve City List
```python
def generate_county_frontmatter(county_name: str):
    """
    Generate frontmatter for all cities in a county.
    
    Args:
        county_name: County name (e.g., "San Mateo County")
    """
    # Load Cities.yaml
    cities_data = load_yaml("regions/Cities.yaml")
    
    # Filter cities by county
    county_cities = [
        city for city in cities_data["cities"].values()
        if city["county"] == county_name
    ]
    
    print(f"Found {len(county_cities)} cities in {county_name}")
    
    # Process each city
    for city in county_cities:
        generate_city_frontmatter(city)
```

#### Step 2: Randomly Assign Historical Images (Per City)
```python
import random

def assign_historical_images(city_name: str, population: int) -> List[Dict]:
    """
    Randomly assign 1-3 historical images with unique parameters.
    
    Args:
        city_name: City name
        population: City population (determines image count)
    
    Returns:
        List of image specifications with research params
    """
    # Determine number of images based on city size
    if population > 100000:  # Major cities
        num_images = random.choice([2, 3])
    elif population > 20000:  # Small cities
        num_images = random.choice([1, 2])
    else:  # Towns
        num_images = random.choice([1, 1, 2])  # Mostly 1
    
    # Available subjects (ensure variety)
    subjects = [
        "downtown streetscape",
        "harbor",
        "main street",
        "train station",
        "industrial district",
        "residential neighborhood",
        "city hall",
        "historic landmark"
    ]
    
    # Decades to sample from
    decades = ["1920s", "1930s", "1940s", "1950s"]
    
    # Generate unique image specifications
    image_specs = []
    used_subjects = set()
    used_decades = set()
    
    for i in range(num_images):
        # Select unique subject
        available_subjects = [s for s in subjects if s not in used_subjects]
        if not available_subjects:
            available_subjects = subjects  # Reset if exhausted
        subject = random.choice(available_subjects)
        used_subjects.add(subject)
        
        # Select unique decade
        available_decades = [d for d in decades if d not in used_decades]
        if not available_decades:
            available_decades = decades  # Reset if exhausted
        decade = random.choice(available_decades)
        used_decades.add(decade)
        
        # Generate specific year within decade
        year = int(decade.replace("s", "")) + random.randint(0, 9)
        
        # Random aging parameters
        photo_condition = random.randint(2, 4)  # 2-4 scale (light to moderate aging)
        scenery_condition = random.randint(2, 4)  # 2-4 scale (light to moderate wear)
        
        image_specs.append({
            "subject": subject,
            "year": year,
            "photo_condition": photo_condition,
            "scenery_condition": scenery_condition,
            "filename": f"{city_name.lower().replace(' ', '_')}_{year}_{subject.replace(' ', '_')}.png"
        })
    
    return image_specs
```

#### Step 3: Generate Images with Metadata
```python
def generate_city_images(
    city_name: str,
    county_name: str,
    image_specs: List[Dict]
) -> List[Dict]:
    """
    Generate historical images for a city.
    
    Args:
        city_name: City name
        county_name: County name
        image_specs: List of image specifications from Step 2
    
    Returns:
        List of image metadata entries for frontmatter
    """
    from regions.image.generate import generate_historical_image
    
    city_slug = city_name.lower().replace(' ', '_')
    output_dir = f"public/images/regions/{city_slug}"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    images_metadata = []
    
    for spec in image_specs:
        print(f"  Generating: {spec['filename']}")
        
        # Call image generator
        image_path = generate_historical_image(
            city_name=city_name,
            county_name=county_name,
            year=spec["year"],
            subject=spec["subject"],
            photo_condition=spec["photo_condition"],
            scenery_condition=spec["scenery_condition"],
            output_dir=output_dir,
            filename=spec["filename"]
        )
        
        # Store metadata
        images_metadata.append({
            "path": f"/images/regions/{city_slug}/{spec['filename']}",
            "year": spec["year"],
            "subject": spec["subject"],
            "dimensions": {
                "width": 1920,
                "height": 1080,
                "aspect_ratio": "16:9"
            },
            "generation": {
                "photo_condition": spec["photo_condition"],
                "scenery_condition": spec["scenery_condition"],
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }
        })
    
    return images_metadata
```

#### Step 4: Generate Captions (Long & Short)
```python
def generate_image_captions(
    image_path: str,
    city_name: str,
    year: int,
    subject: str
) -> Dict[str, str]:
    """
    Generate long and short captions for an image.
    
    Args:
        image_path: Path to generated image
        city_name: City name
        year: Historical year
        subject: Image subject
    
    Returns:
        Dict with "long_caption" and "short_caption"
    """
    from regions.image.validator import ImageValidator
    
    validator = ImageValidator(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Prompt for Gemini Vision analysis
    long_caption_prompt = f"""
    Analyze this historical photograph of {city_name} from {year} showing {subject}.
    
    Write a detailed 2-3 sentence caption (150-200 characters) that includes:
    1. Specific location and year context
    2. Visual details: architecture, vehicles, clothing, activities
    3. Notable landmarks or atmospheric elements
    
    Style: Natural, engaging, specific (not generic).
    Focus on what you actually see in the image.
    Use active voice and concrete nouns.
    
    Example: "Market Street, San Francisco, 1935 - Electric streetcars share the road with Model A Fords while pedestrians in fedoras and knee-length dresses browse storefronts. The Ferry Building's clock tower rises above the bustling commercial district."
    """
    
    short_caption_prompt = f"""
    Analyze this historical photograph and write a SHORT caption (40-60 characters) for alt text.
    
    Format: "{city_name}, {year} - [key visual element]"
    
    Example: "San Francisco, 1935 - Market Street streetcars"
    """
    
    # Generate long caption
    long_response = validator.api_client.generate_content([
        long_caption_prompt,
        image_path
    ])
    long_caption = long_response.text.strip()
    
    # Generate short caption
    short_response = validator.api_client.generate_content([
        short_caption_prompt,
        image_path
    ])
    short_caption = short_response.text.strip()
    
    return {
        "long_caption": long_caption,
        "short_caption": short_caption
    }
```

#### Step 5: Update Image Metadata with Captions
```python
def add_captions_to_images(images_metadata: List[Dict]) -> List[Dict]:
    """
    Generate and add captions to image metadata.
    
    Args:
        images_metadata: List of image metadata from Step 3
    
    Returns:
        Updated list with captions added
    """
    for img in images_metadata:
        print(f"  Generating captions for: {img['path']}")
        
        # Generate captions using Gemini Vision
        captions = generate_image_captions(
            image_path=f"public{img['path']}",  # Convert to local path
            city_name=extract_city_from_path(img['path']),
            year=img['year'],
            subject=img['subject']
        )
        
        # Add captions to metadata
        img["caption"] = captions["long_caption"]
        img["caption_short"] = captions["short_caption"]
    
    return images_metadata
```

#### Step 6: Generate Remaining Frontmatter Content
```python
def generate_city_frontmatter(city_data: Dict):
    """
    Complete frontmatter generation workflow for a single city.
    
    Args:
        city_data: City data from Cities.yaml
    """
    city_name = city_data["name"]
    county_name = city_data["county"]
    population = city_data.get("population_2020", 50000)
    
    print(f"\n{'='*60}")
    print(f"Processing: {city_name}, {county_name}")
    print(f"{'='*60}")
    
    # Step 2: Randomly assign historical images
    print(f"Step 2: Assigning {city_name} historical images...")
    image_specs = assign_historical_images(city_name, population)
    print(f"  Assigned {len(image_specs)} images")
    
    # Step 3: Generate images with metadata
    print(f"Step 3: Generating images...")
    images_metadata = generate_city_images(city_name, county_name, image_specs)
    
    # Step 4 & 5: Generate and add captions
    print(f"Step 4-5: Generating captions...")
    images_metadata = add_captions_to_images(images_metadata)
    
    # Step 6: Generate remaining frontmatter content
    print(f"Step 6: Generating frontmatter text content...")
    
    # Build complete frontmatter
    frontmatter = CityFrontmatterGenerator.build_frontmatter(
        city_data=city_data,
        images=images_metadata  # Pass images to generator
    )
    
    # Save to YAML file
    output_path = f"frontmatter/regions/{city_data['slug']}-laser-cleaning.yaml"
    save_yaml(frontmatter, output_path)
    
    print(f"✅ Complete: {output_path}\n")
```

### Complete Workflow Example

**User Command:**
```bash
python3 run.py --region "San Mateo County"
```

**Expected Output:**
```
Found 20 cities in San Mateo County

============================================================
Processing: Belmont, San Mateo County
============================================================
Step 2: Assigning Belmont historical images...
  Assigned 1 images
Step 3: Generating images...
  Generating: belmont_1935_main_street.png
Step 4-5: Generating captions...
  Generating captions for: /images/regions/belmont/belmont_1935_main_street.png
Step 6: Generating frontmatter text content...
  Researching historic buildings...
  Researching industries...
  Generating service area map...
  Generating FAQ...
✅ Complete: frontmatter/regions/belmont-laser-cleaning.yaml

============================================================
Processing: San Mateo, San Mateo County
============================================================
Step 2: Assigning San Mateo historical images...
  Assigned 2 images
Step 3: Generating images...
  Generating: san_mateo_1940_downtown_streetscape.png
  Generating: san_mateo_1928_train_station.png
Step 4-5: Generating captions...
  Generating captions for: /images/regions/san_mateo/san_mateo_1940_downtown_streetscape.png
  Generating captions for: /images/regions/san_mateo/san_mateo_1928_train_station.png
Step 6: Generating frontmatter text content...
  Researching historic buildings...
  Researching industries...
  Generating service area map...
  Generating FAQ...
✅ Complete: frontmatter/regions/san_mateo-laser-cleaning.yaml

[... continues for all 20 cities ...]

============================================================
San Mateo County Processing Complete
============================================================
Total cities: 20
Total images generated: 38
Total frontmatter files: 20
Total time: 12m 34s
Cost: $1.52 (images) + $0.23 (captions) = $1.75
```

---

## File Structure

```
public/images/regions/
├── san_francisco/
│   ├── san_francisco_1935_downtown_streetscape.png
│   ├── san_francisco_1925_harbor.png
│   └── san_francisco_1940_chinatown_district.png
├── oakland/
│   ├── oakland_1930_main_street.png
│   └── oakland_1945_industrial_district.png
├── san_jose/
│   ├── san_jose_1935_downtown_streetscape.png
│   ├── san_jose_1950_residential_neighborhood.png
│   └── san_jose_1920_train_station.png
└── ...
```

**Naming Convention:**
```
{city_slug}_{year}_{subject_slug}.png
```

**City Slug Rules:**
- Lowercase
- Spaces → underscores
- Remove special characters
- Example: "San Francisco" → "san_francisco"

---

## Cost Analysis

### Per City (1-3 Images)

**Image Generation (Imagen 4):**
- 1 image: $0.04
- 2 images: $0.08
- 3 images: $0.12

**Caption Generation (Gemini Vision):**
- Per caption: $0.0002
- 3 captions: $0.0006 (negligible)

**Total per City:**
- Minimum (1 image): $0.04
- Average (2 images): $0.08
- Maximum (3 images): $0.12

### 93 Bay Area Cities

**Estimated Distribution:**
- 20 major cities (100k+): 3 images each = 60 images
- 40 small cities (10k-100k): 2 images each = 80 images
- 33 towns (<10k): 1 image each = 33 images

**Total Images:** ~173 images

**Total Cost:**
- Image generation: 173 × $0.04 = $6.92
- Caption generation: 173 × $0.0002 = $0.03
- **Total: ~$6.95** for all 93 cities

**Very affordable** for high-quality, unique historical imagery.

---

## Quality Assurance

### Image Validation Checklist

- [ ] Image resolution: 1920×1080 (16:9)
- [ ] Historical accuracy: Period-appropriate details
- [ ] No anachronisms: Text spelling, architecture, vehicles
- [ ] Visual quality: Clear, well-composed
- [ ] Subject matches specification
- [ ] Year matches specification

### Caption Validation Checklist

- [ ] Length: 150-200 characters
- [ ] Structure: 2-3 sentences
- [ ] Specificity: Exact location, year, visual details
- [ ] Accuracy: Matches image content
- [ ] Engagement: Natural, active voice
- [ ] No generic phrases: Avoid "old buildings", "people walking"

### Automated Validation

```python
def validate_image_entry(image: Dict) -> List[str]:
    """Validate image entry in frontmatter"""
    errors = []
    
    # Check required fields
    required = ["path", "caption", "year", "subject", "dimensions"]
    for field in required:
        if field not in image:
            errors.append(f"Missing required field: {field}")
    
    # Validate caption length
    if len(image.get("caption", "")) < 100:
        errors.append("Caption too short (< 100 chars)")
    if len(image.get("caption", "")) > 250:
        errors.append("Caption too long (> 250 chars)")
    
    # Validate year range
    year = image.get("year", 0)
    if not 1900 <= year <= 1960:
        errors.append(f"Year {year} out of range (1900-1960)")
    
    # Validate dimensions
    dims = image.get("dimensions", {})
    if dims.get("aspect_ratio") != "16:9":
        errors.append("Aspect ratio must be 16:9")
    
    return errors
```

---

## Frontend Usage (z-beam Next.js)

**Reading images from frontmatter:**

```typescript
// Example city page component
const { images } = frontmatter;

{images.historical.map((img, idx) => (
  <figure key={idx} className="my-8">
    <img 
      src={img.path}
      alt={img.caption}
      width={img.dimensions.width}
      height={img.dimensions.height}
      className="rounded-lg shadow-lg"
    />
    <figcaption className="mt-2 text-sm text-gray-600">
      {img.caption}
    </figcaption>
  </figure>
))}
```

**Benefits for SEO:**
- Unique historical imagery (not stock photos)
- Descriptive alt text from captions
- Local relevance (specific landmarks)
- Rich visual content for engagement

---

## Examples

### San Francisco (Major City - 3 Images)

```yaml
images:
  historical:
    - path: "/images/regions/san_francisco/san_francisco_1935_downtown_streetscape.png"
      caption: "Market Street, 1935 - Electric streetcars share the road with Model A Fords while pedestrians in fedoras and knee-length dresses browse storefronts. The Ferry Building's clock tower rises above the bustling commercial district."
      year: 1935
      subject: "downtown streetscape"
    
    - path: "/images/regions/san_francisco/san_francisco_1925_harbor.png"
      caption: "San Francisco waterfront, 1925 - Wooden piers extend into the bay, lined with cargo vessels and fishing boats. Longshoremen in flat caps unload crates as seagulls circle above the fog-shrouded Golden Gate."
      year: 1925
      subject: "harbor"
    
    - path: "/images/regions/san_francisco/san_francisco_1948_chinatown.png"
      caption: "Grant Avenue, Chinatown, 1948 - Paper lanterns and ornate balconies adorn the street as shoppers examine silk fabrics and porcelain. Chinese characters on shop signs advertise tea merchants and herbal apothecaries."
      year: 1948
      subject: "chinatown district"
```

### Belmont (Small Town - 1 Image)

```yaml
images:
  historical:
    - path: "/images/regions/belmont/belmont_1935_main_street.png"
      caption: "Ralston Avenue, Belmont, 1935 - A modest row of storefronts lines the dirt road, including the General Store with its wooden false front. A handful of Model T Fords are parked outside while a farmer loads supplies onto a horse-drawn wagon."
      year: 1935
      subject: "main street"
```

### San Jose (City - 2 Images)

```yaml
images:
  historical:
    - path: "/images/regions/san_jose/san_jose_1940_downtown_streetscape.png"
      caption: "First Street, San Jose, 1940 - Two-story commercial buildings with Art Deco facades line the paved street. A vintage Nash sedan passes the Fox California Theatre marquee as shoppers in 1940s attire window-shop."
      year: 1940
      subject: "downtown streetscape"
    
    - path: "/images/regions/san_jose/san_jose_1952_agricultural_district.png"
      caption: "Santa Clara Valley orchards, 1952 - Vast fruit orchards stretch toward the Santa Cruz Mountains. Workers in wide-brimmed hats pick apricots while wooden crates stack beside a vintage pickup truck."
      year: 1952
      subject: "agricultural district"
```

---

## Summary

**This Specification Defines:**

1. ✅ **Frontmatter structure** for `images.historical` key
2. ✅ **Random selection strategy** (1-3 images per city)
3. ✅ **Subject variety** (8 distinct subject types)
4. ✅ **Decade distribution** (1920s-1950s)
5. ✅ **Caption requirements** (2-3 sentences, 150-200 chars)
6. ✅ **Quality standards** (specificity, engagement, accuracy)
7. ✅ **Generation parameters** (current + future enhancements)
8. ✅ **Implementation roadmap** (4-week plan)
9. ✅ **Cost analysis** (~$6.95 for 93 cities)
10. ✅ **Validation criteria** (automated quality checks)

**Next Steps:**

1. Update `CityFrontmatterGenerator` to include `images` section
2. Implement random selection logic
3. Test with 3-5 pilot cities
4. Validate caption quality with Gemini Vision
5. Roll out to all 93 Bay Area cities

**Future:** Enhanced subject parameters when you design image researcher updates.
