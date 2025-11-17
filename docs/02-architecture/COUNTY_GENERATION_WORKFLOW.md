# County-Based Frontmatter Generation Workflow

**Version:** 1.0.0  
**Created:** November 1, 2025  
**Purpose:** Define batch processing workflow for generating city frontmatter by county

---

## Quick Reference

**User Command:**
```bash
python3 run.py --region "San Mateo County"
```

**What It Does:**
1. Retrieves all cities in the county (from `Cities.yaml`)
2. For each city, randomly assigns 1-3 historical images
3. Generates images with unique year/subject/aging parameters
4. Creates long + short captions using Gemini Vision
5. Generates remaining frontmatter content (text research)
6. Saves complete frontmatter to `frontmatter/regions/{city-slug}-laser-cleaning.yaml`

**Time Estimate:** ~30-45 seconds per city (includes image generation + captions + text research)

**Cost Estimate:** ~$0.08-$0.12 per city (images + captions)

---

## Workflow Steps

### Step 1: Retrieve City List

**Load Cities from County:**
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
        if city.get("county") == county_name
    ]
    
    print(f"Found {len(county_cities)} cities in {county_name}")
    
    # Process each city sequentially
    for city in county_cities:
        generate_city_frontmatter(city)
    
    print(f"\n{'='*60}")
    print(f"{county_name} Processing Complete")
    print(f"{'='*60}")
```

**Expected Output:**
```
Found 20 cities in San Mateo County
```

---

### Step 2: Randomly Assign Historical Images (Per City)

**Determine Image Count Based on Population:**
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
    if population > 100000:  # Major cities (SF, San Jose, Oakland)
        num_images = random.choice([2, 3])  # 2 or 3 images
    elif population > 20000:  # Small cities
        num_images = random.choice([1, 2])  # 1 or 2 images
    else:  # Towns
        num_images = random.choice([1, 1, 2])  # Mostly 1, occasionally 2
    
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
        # Select unique subject (no duplicates within same city)
        available_subjects = [s for s in subjects if s not in used_subjects]
        if not available_subjects:
            available_subjects = subjects  # Reset if exhausted
        subject = random.choice(available_subjects)
        used_subjects.add(subject)
        
        # Select unique decade (no duplicates within same city)
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
        
        # Generate filename
        city_slug = city_name.lower().replace(' ', '_').replace('-', '_')
        subject_slug = subject.replace(' ', '_')
        filename = f"{city_slug}_{year}_{subject_slug}.png"
        
        image_specs.append({
            "subject": subject,
            "year": year,
            "photo_condition": photo_condition,
            "scenery_condition": scenery_condition,
            "filename": filename
        })
    
    return image_specs
```

**Example Output:**
```python
# Belmont (population: 27,174) → 1 image
[
    {
        "subject": "main street",
        "year": 1935,
        "photo_condition": 3,
        "scenery_condition": 4,
        "filename": "belmont_1935_main_street.png"
    }
]

# San Mateo (population: 105,661) → 2 images
[
    {
        "subject": "downtown streetscape",
        "year": 1940,
        "photo_condition": 2,
        "scenery_condition": 3,
        "filename": "san_mateo_1940_downtown_streetscape.png"
    },
    {
        "subject": "train station",
        "year": 1928,
        "photo_condition": 4,
        "scenery_condition": 3,
        "filename": "san_mateo_1928_train_station.png"
    }
]

# San Francisco (population: 873,965) → 3 images
[
    {
        "subject": "downtown streetscape",
        "year": 1935,
        "photo_condition": 3,
        "scenery_condition": 3,
        "filename": "san_francisco_1935_downtown_streetscape.png"
    },
    {
        "subject": "harbor",
        "year": 1925,
        "photo_condition": 4,
        "scenery_condition": 3,
        "filename": "san_francisco_1925_harbor.png"
    },
    {
        "subject": "chinatown district",
        "year": 1948,
        "photo_condition": 2,
        "scenery_condition": 3,
        "filename": "san_francisco_1948_chinatown_district.png"
    }
]
```

---

### Step 3: Generate Images with Metadata

**Call Image Generator for Each Specification:**
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
    from datetime import datetime
    
    city_slug = city_name.lower().replace(' ', '_').replace('-', '_')
    output_dir = f"public/images/regions/{city_slug}"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    images_metadata = []
    
    for spec in image_specs:
        print(f"  Generating: {spec['filename']}")
        
        # Call existing image generator
        # (Assuming regions/image/generate.py has this function)
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
        
        # Store metadata (captions will be added in Step 4-5)
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

**Expected Output:**
```
  Generating: belmont_1935_main_street.png
  → Image saved to: public/images/regions/belmont/belmont_1935_main_street.png
```

**Files Created:**
```
public/images/regions/
└── belmont/
    └── belmont_1935_main_street.png  (1920x1080, 16:9)
```

---

### Step 4: Generate Long Captions

**Use Gemini Vision to Analyze Images:**
```python
def generate_long_caption(
    image_path: str,
    city_name: str,
    year: int,
    subject: str
) -> str:
    """
    Generate detailed 2-3 sentence caption using Gemini Vision.
    
    Args:
        image_path: Path to generated image
        city_name: City name
        year: Historical year
        subject: Image subject
    
    Returns:
        Long caption (150-200 characters)
    """
    from regions.image.validator import ImageValidator
    
    validator = ImageValidator(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    Analyze this historical photograph of {city_name} from {year} showing {subject}.
    
    Write a detailed 2-3 sentence caption (150-200 characters) that includes:
    1. Specific location and year context (e.g., "Market Street, San Francisco, 1935")
    2. Visual details: architecture, vehicles, clothing, activities you SEE in the image
    3. Notable landmarks or atmospheric elements
    
    Writing Style:
    - Natural, engaging, specific (not generic)
    - Focus ONLY on what you actually see in the image
    - Use active voice and concrete nouns
    - Period-appropriate vocabulary
    
    Good Example:
    "Market Street, San Francisco, 1935 - Electric streetcars share the road with Model A Fords while pedestrians in fedoras and knee-length dresses browse storefronts. The Ferry Building's clock tower rises above the bustling commercial district."
    
    Bad Example:
    "A historical photograph of downtown San Francisco from the 1930s showing some buildings and people."
    
    Write the caption now:
    """
    
    # Use Gemini Vision to analyze image
    response = validator.api_client.generate_content([prompt, image_path])
    caption = response.text.strip()
    
    # Remove quotes if present
    caption = caption.strip('"').strip("'")
    
    return caption
```

**Example Output:**
```
"Ralston Avenue, Belmont, 1935 - A modest row of storefronts lines the dirt road, including the General Store with its wooden false front. A handful of Model T Fords are parked outside while a farmer loads supplies onto a horse-drawn wagon."
```

---

### Step 5: Generate Short Captions (Alt Text)

**Use Gemini Vision for Concise Alt Text:**
```python
def generate_short_caption(
    image_path: str,
    city_name: str,
    year: int,
    subject: str
) -> str:
    """
    Generate short caption for alt text (40-60 characters).
    
    Args:
        image_path: Path to generated image
        city_name: City name
        year: Historical year
        subject: Image subject
    
    Returns:
        Short caption (40-60 characters) for alt text
    """
    from regions.image.validator import ImageValidator
    
    validator = ImageValidator(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    Analyze this historical photograph and write a SHORT caption (40-60 characters) for alt text.
    
    Format: "{city_name}, {year} - [key visual element]"
    
    Examples:
    - "San Francisco, 1935 - Market Street streetcars"
    - "Belmont, 1935 - Ralston Avenue storefronts"
    - "Oakland, 1940 - downtown business district"
    
    Focus on the most distinctive visual element you see.
    Keep it concise and SEO-friendly.
    
    Write the short caption now:
    """
    
    # Use Gemini Vision to analyze image
    response = validator.api_client.generate_content([prompt, image_path])
    short_caption = response.text.strip()
    
    # Remove quotes if present
    short_caption = short_caption.strip('"').strip("'")
    
    return short_caption
```

**Example Output:**
```
"Belmont, 1935 - Ralston Avenue storefronts"
```

---

### Step 6: Add Captions to Image Metadata

**Update Metadata with Generated Captions:**
```python
def add_captions_to_images(
    images_metadata: List[Dict],
    city_name: str
) -> List[Dict]:
    """
    Generate and add long + short captions to image metadata.
    
    Args:
        images_metadata: List of image metadata from Step 3
        city_name: City name (for context)
    
    Returns:
        Updated list with captions added
    """
    for img in images_metadata:
        print(f"  Generating captions for: {img['path']}")
        
        # Convert frontmatter path to local filesystem path
        local_path = f"public{img['path']}"
        
        # Generate long caption
        long_caption = generate_long_caption(
            image_path=local_path,
            city_name=city_name,
            year=img['year'],
            subject=img['subject']
        )
        
        # Generate short caption
        short_caption = generate_short_caption(
            image_path=local_path,
            city_name=city_name,
            year=img['year'],
            subject=img['subject']
        )
        
        # Add captions to metadata
        img["caption"] = long_caption
        img["caption_short"] = short_caption
    
    return images_metadata
```

**Example Output:**
```
  Generating captions for: /images/regions/belmont/belmont_1935_main_street.png
  → Long caption: "Ralston Avenue, Belmont, 1935 - A modest row of storefronts..."
  → Short caption: "Belmont, 1935 - Ralston Avenue storefronts"
```

**Updated Metadata:**
```python
[
    {
        "path": "/images/regions/belmont/belmont_1935_main_street.png",
        "caption": "Ralston Avenue, Belmont, 1935 - A modest row of storefronts lines the dirt road, including the General Store with its wooden false front. A handful of Model T Fords are parked outside while a farmer loads supplies onto a horse-drawn wagon.",
        "caption_short": "Belmont, 1935 - Ralston Avenue storefronts",
        "year": 1935,
        "subject": "main street",
        "dimensions": {
            "width": 1920,
            "height": 1080,
            "aspect_ratio": "16:9"
        },
        "generation": {
            "photo_condition": 3,
            "scenery_condition": 4,
            "generated_at": "2025-11-01T14:22:15Z"
        }
    }
]
```

---

### Step 7: Generate Remaining Frontmatter Content

**Complete Text Research and Data Assembly:**
```python
def generate_city_frontmatter(city_data: Dict):
    """
    Complete frontmatter generation workflow for a single city.
    
    Orchestrates:
    - Historical image generation (Steps 2-6)
    - Text content research (Step 7)
    - Service area map data
    - FAQ generation
    - Complete frontmatter assembly
    
    Args:
        city_data: City data from Cities.yaml
    """
    city_name = city_data["name"]
    county_name = city_data["county"]
    population = city_data.get("population_2020", 50000)
    
    print(f"\n{'='*60}")
    print(f"Processing: {city_name}, {county_name}")
    print(f"{'='*60}")
    
    # ========================================
    # STEPS 2-6: Historical Images
    # ========================================
    
    # Step 2: Randomly assign historical images
    print(f"Step 2: Assigning historical images...")
    image_specs = assign_historical_images(city_name, population)
    print(f"  → Assigned {len(image_specs)} images")
    
    # Step 3: Generate images with metadata
    print(f"Step 3: Generating images...")
    images_metadata = generate_city_images(city_name, county_name, image_specs)
    
    # Steps 4-6: Generate and add captions
    print(f"Step 4-6: Generating captions...")
    images_metadata = add_captions_to_images(images_metadata, city_name)
    
    # ========================================
    # STEP 7: Remaining Frontmatter Content
    # ========================================
    
    print(f"Step 7: Generating frontmatter text content...")
    
    # Initialize CityFrontmatterGenerator
    generator = CityFrontmatterGenerator(city_data)
    
    # Research components
    print(f"  → Researching historic buildings...")
    historic_buildings = generator.research_historic_buildings()
    
    print(f"  → Researching industries...")
    industries = generator.research_industries()
    
    print(f"  → Generating service area map...")
    service_area_map = generator.generate_service_area_map()
    
    print(f"  → Generating FAQ...")
    faq = generator.generate_faq()
    
    print(f"  → Generating content sections...")
    content = generator.generate_content_sections()
    
    # Build complete frontmatter
    frontmatter = {
        "title": f"{city_name} Laser Cleaning Services | Z-Beam",
        "slug": generator.get_slug(),
        "location": generator.build_location_data(),
        "images": {"historical": images_metadata},  # Add images here
        "service_area_map": service_area_map,
        "historic_context": {
            "historic_buildings": historic_buildings,
            "historical_industries": industries
        },
        "content": content,
        "faq": faq,
        "_metadata": generator.build_metadata()
    }
    
    # Save to YAML file
    output_path = f"frontmatter/regions/{generator.get_slug()}.yaml"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Complete: {output_path}\n")
```

**Expected Output:**
```
Step 7: Generating frontmatter text content...
  → Researching historic buildings...
  → Researching industries...
  → Generating service area map...
  → Generating FAQ...
  → Generating content sections...
✅ Complete: frontmatter/regions/belmont-laser-cleaning.yaml
```

---

## Complete Workflow Example

### User Command
```bash
python3 run.py --region "San Mateo County"
```

### Expected Terminal Output
```
============================================================
Generating Frontmatter for San Mateo County
============================================================
Found 20 cities in San Mateo County

============================================================
Processing: Belmont, San Mateo County
============================================================
Step 2: Assigning historical images...
  → Assigned 1 images
Step 3: Generating images...
  Generating: belmont_1935_main_street.png
  → Image saved to: public/images/regions/belmont/belmont_1935_main_street.png
Step 4-6: Generating captions...
  Generating captions for: /images/regions/belmont/belmont_1935_main_street.png
  → Long caption: "Ralston Avenue, Belmont, 1935 - A modest row of storefronts..."
  → Short caption: "Belmont, 1935 - Ralston Avenue storefronts"
Step 7: Generating frontmatter text content...
  → Researching historic buildings...
  → Researching industries...
  → Generating service area map...
  → Generating FAQ...
  → Generating content sections...
✅ Complete: frontmatter/regions/belmont-laser-cleaning.yaml

============================================================
Processing: San Mateo, San Mateo County
============================================================
Step 2: Assigning historical images...
  → Assigned 2 images
Step 3: Generating images...
  Generating: san_mateo_1940_downtown_streetscape.png
  → Image saved to: public/images/regions/san_mateo/san_mateo_1940_downtown_streetscape.png
  Generating: san_mateo_1928_train_station.png
  → Image saved to: public/images/regions/san_mateo/san_mateo_1928_train_station.png
Step 4-6: Generating captions...
  Generating captions for: /images/regions/san_mateo/san_mateo_1940_downtown_streetscape.png
  → Long caption: "Third Avenue, San Mateo, 1940 - Two-story commercial buildings..."
  → Short caption: "San Mateo, 1940 - downtown Third Avenue"
  Generating captions for: /images/regions/san_mateo/san_mateo_1928_train_station.png
  → Long caption: "San Mateo train station, 1928 - The Southern Pacific depot..."
  → Short caption: "San Mateo, 1928 - Southern Pacific depot"
Step 7: Generating frontmatter text content...
  → Researching historic buildings...
  → Researching industries...
  → Generating service area map...
  → Generating FAQ...
  → Generating content sections...
✅ Complete: frontmatter/regions/san_mateo-laser-cleaning.yaml

[... continues for remaining 18 cities ...]

============================================================
San Mateo County Processing Complete
============================================================
Total cities processed: 20
Total images generated: 38
Total frontmatter files: 20
Total time: 15m 42s

Cost Breakdown:
  Image generation (Imagen 4): 38 × $0.04 = $1.52
  Caption generation (Gemini Vision): 76 × $0.0003 = $0.02
  Text research (Gemini Pro): 20 × $0.01 = $0.20
  TOTAL: $1.74
```

---

## File Structure After Completion

```
z-beam-generator/
├── frontmatter/regions/
│   ├── belmont-laser-cleaning.yaml
│   ├── san_mateo-laser-cleaning.yaml
│   ├── redwood_city-laser-cleaning.yaml
│   └── ... (20 files total)
│
└── public/images/regions/
    ├── belmont/
    │   └── belmont_1935_main_street.png
    ├── san_mateo/
    │   ├── san_mateo_1940_downtown_streetscape.png
    │   └── san_mateo_1928_train_station.png
    ├── redwood_city/
    │   ├── redwood_city_1935_main_street.png
    │   └── redwood_city_1950_industrial_district.png
    └── ... (20 directories, 38 images total)
```

---

## Implementation Checklist

### Phase 1: Setup (1-2 hours)
- [ ] Add `--region` argument to `run.py`
- [ ] Create `generate_county_frontmatter()` function
- [ ] Test with single county (e.g., "San Mateo County")

### Phase 2: Image Assignment (2-3 hours)
- [ ] Implement `assign_historical_images()` function
- [ ] Test random selection logic (1-3 images per city)
- [ ] Validate subject and decade uniqueness

### Phase 3: Image Generation (2-3 hours)
- [ ] Enhance `regions/image/generate.py` to accept subject parameter
- [ ] Implement `generate_city_images()` function
- [ ] Test image generation with pilot cities

### Phase 4: Caption Generation (3-4 hours)
- [ ] Implement `generate_long_caption()` using Gemini Vision
- [ ] Implement `generate_short_caption()` using Gemini Vision
- [ ] Test caption quality and length constraints
- [ ] Validate captions match image content

### Phase 5: Integration (2-3 hours)
- [ ] Update `CityFrontmatterGenerator` to accept images
- [ ] Integrate image metadata into frontmatter
- [ ] Test complete workflow with 3-5 cities

### Phase 6: Production Rollout (varies)
- [ ] Generate all 93 Bay Area cities by county
- [ ] Validate all frontmatter files
- [ ] Document for frontend team

**Total Estimated Time:** 10-15 hours of development + testing

---

## Cost Analysis

### Per City Costs

**Image Generation (Imagen 4):**
- 1 image: $0.04
- 2 images: $0.08
- 3 images: $0.12

**Caption Generation (Gemini Vision):**
- Long caption: $0.0003
- Short caption: $0.0003
- Total per image: $0.0006

**Text Research (Gemini Pro):**
- Per city: ~$0.01

**Total Per City:**
- Minimum (1 image): $0.04 + $0.0006 + $0.01 = $0.05
- Average (2 images): $0.08 + $0.0012 + $0.01 = $0.09
- Maximum (3 images): $0.12 + $0.0018 + $0.01 = $0.13

### San Mateo County (20 Cities)

**Estimated Distribution:**
- 3 cities (100k+): 3 images each = 9 images
- 10 cities (10k-100k): 2 images each = 20 images
- 7 cities (<10k): 1 image each = 7 images

**Total Images:** ~36 images

**Total Cost:**
- Image generation: 36 × $0.04 = $1.44
- Caption generation: 72 × $0.0003 = $0.02
- Text research: 20 × $0.01 = $0.20
- **Total: ~$1.66** for San Mateo County

### All 93 Bay Area Cities

**Estimated Distribution:**
- 20 major cities (100k+): 3 images each = 60 images
- 40 small cities (10k-100k): 2 images each = 80 images
- 33 towns (<10k): 1 image each = 33 images

**Total Images:** ~173 images

**Total Cost:**
- Image generation: 173 × $0.04 = $6.92
- Caption generation: 346 × $0.0003 = $0.10
- Text research: 93 × $0.01 = $0.93
- **Total: ~$7.95** for all Bay Area cities

**Very affordable** for complete frontmatter generation with unique historical imagery.

---

## Quality Assurance

### Automated Validation

**Image Validation:**
- [ ] File exists at `public/images/regions/{city_slug}/{filename}`
- [ ] Resolution: 1920×1080 (16:9)
- [ ] File size: 100KB - 2MB (reasonable range)

**Caption Validation:**
- [ ] Long caption: 100-250 characters
- [ ] Short caption: 30-70 characters
- [ ] Both captions non-empty
- [ ] City name and year present in captions

**Frontmatter Validation:**
- [ ] YAML valid (parseable)
- [ ] All required fields present
- [ ] Images array has 1-3 entries
- [ ] All image paths valid

### Manual Quality Checks (Random Sampling)

**Review 3-5 cities per county:**
- [ ] Images look historically accurate
- [ ] No anachronisms (wrong vehicle types, modern elements)
- [ ] Captions match image content
- [ ] Text content relevant to city

---

## Troubleshooting

### Issue: "County not found"
```python
# Check county name spelling in Cities.yaml
grep -r "San Mateo County" regions/Cities.yaml
```

### Issue: "Image generation failed"
```python
# Check Imagen API credentials
echo $GOOGLE_APPLICATION_CREDENTIALS

# Test image generation manually
python3 regions/image/generate.py \
  --city "Belmont" \
  --county "San Mateo County" \
  --year 1935 \
  --photo-condition 3 \
  --scenery-condition 3
```

### Issue: "Caption generation failed"
```python
# Check Gemini API key
echo $GEMINI_API_KEY

# Test caption generation manually
python3 regions/image/validator.py --test-caption
```

### Issue: "Frontmatter file not created"
```python
# Check output directory exists
mkdir -p frontmatter/regions

# Check file permissions
chmod +w frontmatter/regions
```

---

## Summary

**This Workflow Enables:**

1. ✅ **County-based batch processing** - Process all cities in a county with one command
2. ✅ **Automated image selection** - Random 1-3 images per city based on population
3. ✅ **Unique visual variety** - No duplicate subjects/decades within same city
4. ✅ **High-quality captions** - Gemini Vision generates long + short captions
5. ✅ **Complete frontmatter** - Images + text research in single workflow
6. ✅ **Cost-efficient** - ~$0.09 per city average
7. ✅ **Fast processing** - ~30-45 seconds per city
8. ✅ **Reproducible** - Consistent quality across all cities

**Ready to Implement:**
- Clear step-by-step workflow
- Code examples for each step
- Cost and time estimates
- Quality validation checks
- Troubleshooting guide

**Next Steps:**
1. Implement `--region` argument in `run.py`
2. Create image assignment logic
3. Enhance image generator with subject parameter
4. Integrate caption generation
5. Test with San Mateo County (20 cities)
6. Roll out to remaining counties
