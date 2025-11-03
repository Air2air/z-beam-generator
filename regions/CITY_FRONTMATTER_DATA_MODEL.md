# City-Based Laser Cleaning Frontmatter Data Model

**Version:** 1.0.0  
**Created:** October 31, 2025  
**Purpose:** SEO-optimized city pages targeting "Laser Cleaning in {City Name}" queries

---

## Overview

This data model creates location-specific landing pages for laser cleaning services, optimized for local search queries. Each city page combines:

1. **Geographic data** from `Cities.yaml` (population, history, landmarks)
2. **Economic context** (industries, employers, applications)
3. **Regulatory environment** (local permits, standards, requirements)
4. **Material applications** from `Materials.yaml` (industry-specific use cases)
5. **Historic preservation** context (buildings, cultural significance)

---

## Target Search Queries

- `laser cleaning in {city_name}`
- `laser cleaning services {city_name}`
- `{city_name} laser cleaning company`
- `industrial laser cleaning {city_name}`
- `{material} laser cleaning {city_name}`

---

## Data Structure

### 1. Core Identification

```yaml
layout: city-service
content_type: city
title: "San Francisco Laser Cleaning Services | Serving SF County | Z-Beam"
meta_title: "San Francisco Laser Cleaning Services | Z-Beam Technology"
meta_description: "Professional laser cleaning in San Francisco and throughout San Francisco County. Industrial, maritime, historic preservation. Non-abrasive, eco-friendly. Free consultation."
```

### 2. Location Data

```yaml
city:
  name: "San Francisco"
  slug: "san-francisco"
  state: "California"
  state_abbrev: "CA"
  county: "San Francisco County"  # Used in content, schema, NOT URL
  region: "San Francisco Bay Area"

location:
  latitude: 37.7749
  longitude: -122.4194
  population: 873965
  population_history:
    1900: 342782
    1920: 506676
    1950: 775357
    1980: 678974
    2000: 776733
    2020: 873965
  area_sq_miles: 46.9
  elevation_feet: 52
```

**Data Source:** `Cities.yaml` (populated by city_data_researcher.py)

### 3. Economic & Industry Profile

```yaml
economy:
  primary_industries:
    - "Technology and Software"
    - "Financial Services"
    - "Tourism and Hospitality"
    - "Biotechnology"
    - "Maritime and Shipping"
  
  historical_industries:
    - "Gold Rush shipping hub (1849)"
    - "Cable car manufacturing"
    - "Shipbuilding and naval yards"
    - "Food processing and canning"
  
  laser_cleaning_applications:
    - industry: "Technology Manufacturing"
      applications:
        - "Semiconductor wafer cleaning"
        - "Data center equipment maintenance"
        - "Server component restoration"
      materials:
        - "Silicon"
        - "Aluminum"
        - "Copper"
        - "Stainless Steel"
    
    - industry: "Maritime and Shipping"
      applications:
        - "Vessel hull cleaning at Port of San Francisco"
        - "Marine equipment restoration"
        - "Historic ship preservation (SS Jeremiah O'Brien)"
      materials:
        - "Steel"
        - "Bronze"
        - "Brass"
        - "Iron"
    
    - industry: "Historic Preservation"
      applications:
        - "Victorian architecture cleaning (Painted Ladies)"
        - "Transamerica Pyramid exterior maintenance"
        - "Golden Gate Bridge component cleaning"
        - "Ferry Building restoration"
      materials:
        - "Granite"
        - "Marble"
        - "Limestone"
        - "Bronze"
        - "Steel"
  
  major_employers:
    - name: "Salesforce"
      industry: "Technology"
      potential_applications:
        - "Office building maintenance"
        - "Server equipment cleaning"
    
    - name: "Port of San Francisco"
      industry: "Maritime"
      potential_applications:
        - "Vessel maintenance"
        - "Port infrastructure cleaning"
        - "Historic ship restoration"
```

**Data Sources:**
- `Cities.yaml`: historical_industries, current_industries
- `Materials.yaml`: Material properties and applications
- Industry mapping logic: Match city industries to relevant materials/applications

### 4. Regulatory Environment

```yaml
regulations:
  state_requirements:
    agency: "Cal/OSHA"
    safety_standard: "California Title 8, ANSI Z136.1"
    additional_requirements:
      - "Stricter than federal OSHA standards"
      - "Mandatory operator certification"
      - "Regular safety audits required"
  
  local_requirements:
    air_quality:
      agency: "Bay Area Air Quality Management District (BAAQMD)"
      permit_required: true
      restrictions:
        - "Strict particulate emission limits"
        - "VOC-free processes preferred"
    
    hazardous_materials:
      agency: "San Francisco Department of Public Health"
      permits:
        - "Hazardous Materials Business Plan"
        - "Underground Storage Tank permit (if applicable)"
    
    business_operations:
      permits:
        - "Business Registration Certificate"
        - "Zoning compliance verification"
      zoning_considerations:
        - "Industrial zones: Allowed by right"
        - "Commercial zones: Conditional use permit may be required"
```

**Data Source:** `regions/data.yaml` + city-specific research

### 5. Service Information

```yaml
services:
  available_services:
    - service_category: "Industrial Cleaning"
      description: "High-volume production facility cleaning for manufacturing operations"
      typical_materials:
        - "Aluminum"
        - "Steel"
        - "Stainless Steel"
        - "Copper"
      typical_contaminants:
        - "Rust and oxidation"
        - "Coatings and paints"
        - "Industrial residues"
        - "Welding spatter"
      turnaround_time: "1-5 days depending on volume"
    
    - service_category: "Precision Cleaning"
      description: "Medical device and electronics cleaning to exacting standards"
      typical_materials:
        - "Silicon"
        - "Titanium"
        - "Glass"
        - "Ceramics"
      typical_contaminants:
        - "Microscopic particles"
        - "Manufacturing residues"
        - "Oxidation layers"
      turnaround_time: "Same day to 3 days"
    
    - service_category: "Historic Restoration"
      description: "Cultural heritage and architectural restoration services"
      typical_materials:
        - "Granite"
        - "Marble"
        - "Bronze"
        - "Limestone"
      typical_contaminants:
        - "Environmental soiling"
        - "Biological growth"
        - "Graffiti"
        - "Previous restoration attempts"
      turnaround_time: "Project-based, 1-4 weeks"
    
    - service_category: "Marine Services"
      description: "Vessel and maritime equipment cleaning and restoration"
      typical_materials:
        - "Steel"
        - "Aluminum"
        - "Bronze"
        - "Brass"
      typical_contaminants:
        - "Marine growth"
        - "Corrosion"
        - "Salt deposits"
        - "Coatings"
      turnaround_time: "2-7 days"
  
  mobile_service_available: true
  onsite_available: true
  facility_address: "123 Industrial Way, San Francisco, CA 94124"
```

### 6. Materials & Capabilities

```yaml
materials_served:
  - material_name: "Aluminum"
    category: "metal"
    slug: "aluminum-laser-cleaning"
    local_applications:
      - "Tech hardware manufacturing"
      - "Marine vessel components"
      - "Architectural facades and trim"
    common_contaminants:
      - "Oxidation"
      - "Anodizing removal"
      - "Industrial coatings"
      - "Salt deposits (marine)"
    typical_projects:
      - "Server chassis cleaning for data centers"
      - "Ferry boat component restoration"
      - "Building facade maintenance"
  
  - material_name: "Granite"
    category: "stone"
    slug: "granite-laser-cleaning"
    local_applications:
      - "Historic building facades"
      - "Ferry Building restoration"
      - "Financial district bank buildings"
    common_contaminants:
      - "Environmental soiling (fog, pollution)"
      - "Biological growth (lichens, algae)"
      - "Soot from historic fires"
    typical_projects:
      - "Ferry Building exterior cleaning"
      - "Palace Hotel facade restoration"
      - "Monument cleaning in Golden Gate Park"
  
  - material_name: "Bronze"
    category: "metal"
    slug: "bronze-laser-cleaning"
    local_applications:
      - "Historic monuments and statues"
      - "Architectural door hardware"
      - "Decorative sculptures"
    common_contaminants:
      - "Patina (controlled removal)"
      - "Vandalism and graffiti"
      - "Bird deposits"
      - "Environmental corrosion"
    typical_projects:
      - "Civic Center monument restoration"
      - "Historic building door hardware"
      - "Museum sculpture conservation"
  
  - material_name: "Steel"
    category: "metal"
    slug: "steel-laser-cleaning"
    local_applications:
      - "Golden Gate Bridge components"
      - "Maritime vessels and equipment"
      - "Industrial manufacturing"
    common_contaminants:
      - "Rust and corrosion"
      - "Marine fouling"
      - "Coatings and paints"
      - "Welding residues"
    typical_projects:
      - "Port equipment maintenance"
      - "Bridge component restoration"
      - "Shipyard vessel cleaning"
```

**Data Source:** `Materials.yaml` + city industry mapping

### 7. Historic Context & Preservation

```yaml
historic_context:
  founded: 1776
  
  notable_history:
    - "Spanish Mission Dolores founded 1776"
    - "Gold Rush boom town 1849"
    - "1906 earthquake and rebuilding"
    - "Golden Gate Bridge construction 1933-1937"
    - "Summer of Love 1967"
    - "Tech boom 1990s-present"
  
  historic_buildings:
    - name: "Ferry Building"
      year_built: 1898
      architectural_style: "Beaux-Arts"
      materials:
        - "Granite"
        - "Sandstone"
        - "Steel"
      cleaning_applications:
        - "Facade restoration and cleaning"
        - "Interior stonework preservation"
        - "Decorative metalwork maintenance"
      significance: "San Francisco Historic Landmark #86"
    
    - name: "Painted Ladies (Alamo Square Victorians)"
      year_built: 1892
      architectural_style: "Victorian Queen Anne"
      materials:
        - "Wood"
        - "Iron"
        - "Brass"
      cleaning_applications:
        - "Delicate wood restoration without damage"
        - "Hardware cleaning and preservation"
        - "Paint layer analysis and selective removal"
      significance: "National Register of Historic Places"
    
    - name: "Transamerica Pyramid"
      year_built: 1972
      architectural_style: "Modern"
      materials:
        - "Quartz aggregate panels"
        - "Aluminum"
        - "Glass"
      cleaning_applications:
        - "High-rise facade maintenance"
        - "Window frame cleaning"
        - "Structural component maintenance"
      significance: "San Francisco icon, 260m tall"
  
  preservation_priorities:
    - "Victorian architecture (1890s-1910s)"
    - "Art Deco landmarks (1920s-1930s)"
    - "Industrial heritage sites (shipyards, factories)"
    - "Gold Rush era structures"
```

**Data Source:** `Cities.yaml` notable_buildings + cultural_significance

### 8. Transportation & Access

```yaml
transportation:
  current:
    major_highways:
      - "I-80 (Bay Bridge)"
      - "US-101 (South to Silicon Valley)"
      - "I-280 (Peninsula connection)"
    
    airports:
      - name: "San Francisco International Airport (SFO)"
        distance_miles: 13
        service_area: "International hub"
    
    seaports:
      - name: "Port of San Francisco"
        capabilities: "Cargo and cruise"
      - name: "Port of Oakland"
        distance_miles: 10
        capabilities: "Major container port"
    
    rail_access:
      - "Caltrain (Peninsula)"
      - "BART (Bay Area Rapid Transit)"
      - "Amtrak (Capitol Corridor)"
  
  historical_transportation:
    - "Cable car system (1873-present)"
    - "Ferry terminal hub (1898-present)"
    - "Transcontinental Railroad terminus (1869)"
    - "Streetcar network (historic)"
  
  service_area_radius: 50
  typical_response_time: "Same day for SF proper, next day for Bay Area"
```

**Data Source:** `Cities.yaml` transportation_history + current data

### 9. Environmental Benefits

```yaml
environmental_benefits:
  local_impact:
    - benefit: "Zero VOC emissions"
      relevance: "Critical for BAAQMD compliance in air quality non-attainment area"
      regulatory_context: "Avoids BAAQMD permitting for VOC-emitting processes"
    
    - benefit: "Water conservation"
      relevance: "Supports California drought management and water conservation goals"
      quantified: "Zero water usage vs. 500-5000 gallons for pressure washing"
    
    - benefit: "Chemical waste elimination"
      relevance: "Reduces hazardous waste disposal costs and CUPA reporting"
      quantified: "Eliminates 100% of chemical stripping agents"
    
    - benefit: "Energy efficiency"
      relevance: "Lower carbon footprint aligns with SF climate action goals"
      quantified: "60% less energy than heated chemical tanks"
  
  sustainability_alignment:
    - standard: "California Green Building Standards (CALGreen)"
      how: "Non-toxic cleaning for LEED-certified buildings"
    
    - standard: "San Francisco Zero Waste goals"
      how: "Eliminates chemical containers and disposable media"
    
    - standard: "Climate Action Plan compliance"
      how: "Reduced energy consumption and emissions"
```

### 10. Competitive Advantages (City-Specific)

```yaml
local_advantages:
  - advantage: "No water usage"
    context: "Critical in drought-prone California; San Francisco promotes water conservation"
    benefit: "Aligns with city sustainability goals"
  
  - advantage: "Precision cleaning"
    context: "Essential for Bay Area tech manufacturing and semiconductor industry"
    benefit: "Meets cleanroom standards without contamination"
  
  - advantage: "Historic preservation expertise"
    context: "Rich Victorian architecture and Gold Rush landmarks require delicate care"
    benefit: "Non-invasive cleaning preserves patina and original materials"
  
  - advantage: "Maritime specialization"
    context: "Port of San Francisco and historic ships require salt-resistant cleaning"
    benefit: "Removes marine growth and corrosion without surface damage"
  
  - advantage: "Regulatory compliance"
    context: "Strictest environmental regulations in nation (BAAQMD, Cal/OSHA)"
    benefit: "Meets all local requirements without additional permits"
```

### 11. FAQ Section

```yaml
faq:
  questions:
    - question: "Why choose laser cleaning over sandblasting in San Francisco?"
      answer: "Laser cleaning is ideal for San Francisco's strict environmental regulations. Unlike sandblasting, it generates no hazardous waste, requires no BAAQMD air quality permits, and eliminates the disposal costs associated with spent abrasive media. It's particularly valuable for our Victorian architecture and historic landmarks where preservation is critical."
      keywords:
        - "laser vs sandblasting"
        - "San Francisco regulations"
        - "historic preservation"
      related_materials:
        - "granite-laser-cleaning"
        - "bronze-laser-cleaning"
    
    - question: "Is laser cleaning approved for use in San Francisco?"
      answer: "Yes, laser cleaning is fully approved and actually preferred by San Francisco regulators. It complies with all BAAQMD air quality standards, Cal/OSHA safety requirements, and San Francisco's strict environmental protection policies. The process generates no VOCs, no hazardous waste, and requires no water discharge permits."
      keywords:
        - "San Francisco regulations"
        - "BAAQMD compliance"
        - "environmental approval"
      regulatory_references:
        - "BAAQMD Regulation 8"
        - "Cal/OSHA Title 8"
    
    - question: "What industries in San Francisco benefit from laser cleaning?"
      answer: "San Francisco's diverse economy creates demand across multiple sectors: (1) Technology - semiconductor wafer and server equipment cleaning, (2) Maritime - Port of San Francisco vessel maintenance and historic ship restoration, (3) Historic Preservation - Victorian architecture, Ferry Building, and landmark restoration, (4) Biotechnology - cleanroom equipment and medical device manufacturing, (5) Financial Services - building facade and monument maintenance."
      keywords:
        - "San Francisco industries"
        - "laser cleaning applications"
        - "maritime cleaning"
        - "historic preservation"
    
    - question: "Can you clean historic San Francisco buildings without damage?"
      answer: "Absolutely. Laser cleaning is the preferred method for San Francisco's Victorian and Gold Rush era architecture. Unlike abrasive methods, it removes dirt and pollution while preserving original paint layers, patina, and delicate wood grain. We've successfully cleaned Painted Ladies-style homes, Ferry Building stonework, and bronze monuments with zero material loss."
      keywords:
        - "Victorian architecture"
        - "historic building cleaning"
        - "non-invasive restoration"
      case_studies:
        - "Ferry Building facade restoration"
        - "Alamo Square Victorian preservation"
    
    - question: "What's the typical turnaround time for laser cleaning in San Francisco?"
      answer: "Turnaround varies by project scope: Small components and hardware (same day to 3 days), Industrial equipment and machinery (1-5 days), Building facades and large structures (project-based, 1-4 weeks), Emergency marine vessel cleaning (24-48 hours). We offer mobile service throughout San Francisco and the Bay Area for rapid response."
      keywords:
        - "turnaround time"
        - "San Francisco service"
        - "mobile cleaning"
    
    - question: "How does San Francisco's marine environment affect laser cleaning?"
      answer: "San Francisco's coastal location creates unique challenges - salt air accelerates corrosion on metal structures, and marine growth affects vessels and waterfront equipment. Laser cleaning excels in this environment, removing salt deposits, rust, and marine fouling without introducing water that could worsen corrosion. It's ideal for Golden Gate Bridge components, Port equipment, and historic ships."
      keywords:
        - "marine environment"
        - "salt corrosion"
        - "Port of San Francisco"
        - "maritime cleaning"
    
    - question: "What permits are required for laser cleaning in San Francisco?"
      answer: "Laser cleaning requires minimal permitting compared to alternatives. Typically needed: (1) Business Registration Certificate from SF Treasurer, (2) Zoning compliance verification, (3) Hazardous Materials Business Plan if storing chemicals (though laser cleaning uses none). NOT required: BAAQMD air quality permits (no VOCs), water discharge permits (dry process), hazardous waste transport permits (no waste generation)."
      keywords:
        - "San Francisco permits"
        - "BAAQMD"
        - "regulatory compliance"
    
    - question: "Can laser cleaning help LEED-certified buildings in San Francisco?"
      answer: "Yes, laser cleaning supports LEED certification and maintenance. It contributes to: (1) Material & Resources credits - no hazardous cleaning agents, (2) Indoor Environmental Quality - no toxic residues or odors, (3) Water Efficiency - zero water consumption, (4) Energy & Atmosphere - lower energy use than chemical processes. Many San Francisco green buildings use laser cleaning for ongoing maintenance."
      keywords:
        - "LEED certification"
        - "green building"
        - "sustainable cleaning"
        - "CALGreen compliance"
```

### 12. Related Content & Internal Linking

```yaml
related_pages:
  materials:
    - slug: "aluminum-laser-cleaning"
      title: "Aluminum Laser Cleaning"
      relevance: "Common in SF tech manufacturing and marine applications"
      connection: "Used in server equipment, vessels, and building facades"
    
    - slug: "granite-laser-cleaning"
      title: "Granite Laser Cleaning"
      relevance: "SF historic building facades and monuments"
      connection: "Ferry Building, financial district banks, Golden Gate Park monuments"
    
    - slug: "bronze-laser-cleaning"
      title: "Bronze Laser Cleaning"
      relevance: "Historic monuments and architectural details"
      connection: "Civic Center statues, building hardware, memorial plaques"
    
    - slug: "steel-laser-cleaning"
      title: "Steel Laser Cleaning"
      relevance: "Golden Gate Bridge, maritime vessels, industrial equipment"
      connection: "Port equipment, bridge components, shipyard maintenance"
  
  regions:
    - slug: "san-francisco-bay-area-laser-cleaning"
      type: "parent_region"
      title: "San Francisco Bay Area Laser Cleaning"
      relation: "SF is part of broader Bay Area market"
    
    - slug: "alameda-county/oakland-laser-cleaning"
      type: "nearby_city"
      title: "Laser Cleaning in Oakland, CA"
      relation: "Adjacent city across the Bay, Port of Oakland"
    
    - slug: "santa-clara-county/san-jose-laser-cleaning"
      type: "nearby_city"
      title: "Laser Cleaning in San Jose, CA"
      relation: "South Bay tech manufacturing hub"
    
    - slug: "california-laser-cleaning"
      type: "parent_state"
      title: "California Laser Cleaning Services"
      relation: "State-level overview and regulations"
  
  applications:
    - slug: "semiconductor-laser-cleaning"
      relevance: "Bay Area tech manufacturing"
    
    - slug: "historic-preservation-laser-cleaning"
      relevance: "Victorian and Gold Rush architecture"
    
    - slug: "maritime-laser-cleaning"
      relevance: "Port of San Francisco and historic vessels"
  
  contaminants:
    - slug: "rust-laser-removal"
      relevance: "Marine environment corrosion"
    
    - slug: "graffiti-laser-removal"
      relevance: "Urban building maintenance"
    
    - slug: "biological-growth-laser-removal"
      relevance: "Fog and moisture promote growth on stone"
```

### 13. Schema.org Structured Data

```yaml
schema_org:
  "@context": "https://schema.org"
  "@type": "ProfessionalService"
  name: "Z-Beam Laser Cleaning - San Francisco"
  description: "Professional laser cleaning services for industrial, maritime, and historic preservation applications in San Francisco"
  
  serviceType: "Laser Cleaning Service"
  
  areaServed:
    "@type": "City"
    name: "San Francisco"
    state: "California"
    country: "USA"
  
  hasOfferCatalog:
    "@type": "OfferCatalog"
    name: "Laser Cleaning Services"
    itemListElement:
      - "@type": "Offer"
        itemOffered:
          "@type": "Service"
          name: "Industrial Laser Cleaning"
          description: "High-volume manufacturing facility cleaning"
          category: "Industrial Services"
      
      - "@type": "Offer"
        itemOffered:
          "@type": "Service"
          name: "Historic Building Restoration"
          description: "Victorian and Gold Rush era architecture cleaning"
          category: "Restoration Services"
      
      - "@type": "Offer"
        itemOffered:
          "@type": "Service"
          name: "Maritime Vessel Cleaning"
          description: "Port of San Francisco vessel and equipment maintenance"
          category: "Marine Services"
  
  geo:
    "@type": "GeoCoordinates"
    latitude: 37.7749
    longitude: -122.4194
  
  address:
    "@type": "PostalAddress"
    streetAddress: "123 Industrial Way"
    addressLocality: "San Francisco"
    addressRegion: "CA"
    postalCode: "94124"
    addressCountry: "US"
  
  telephone: "+1-415-555-BEAM"
  email: "sf@z-beam.com"
  url: "https://z-beam.com/san-francisco-county/san-francisco-laser-cleaning"
  
  openingHours: "Mo-Fr 08:00-18:00"
  
  priceRange: "$$-$$$"
  
  areaServed:
    - "@type": "City"
      name: "San Francisco"
      containedIn:
        "@type": "State"
        name: "California"
    - "@type": "AdministrativeArea"
      name: "San Francisco County"
      containedIn:
        "@type": "State"
        name: "California"
  
  aggregateRating:
    "@type": "AggregateRating"
    ratingValue: 4.9
    reviewCount: 127
```

### 14. Author & Voice

```yaml
author:
  name: "Todd Dunning"
  country: "United States (California)"
  expertise: "Optical Materials for Laser Systems"
  title: "MA"
  image: "/images/author/todd-dunning.jpg"
  voice_applied: true
  
voice_characteristics:
  tone: "Professional, technically precise"
  style: "California tech industry communication"
  regional_awareness: "Bay Area environmental consciousness"
  local_knowledge: "SF maritime history, Victorian architecture, tech manufacturing"
```

### 15. Historical Images

```yaml
images:
  historical:
    # Random selection: 1-3 images per city page
    # Each image has path, long caption, short caption (alt text)
    
    - path: "/images/regions/san_francisco/san_francisco_1935_downtown_streetscape.png"
      caption: "Market Street, San Francisco, 1935 - Electric streetcars share the road with Model A Fords while pedestrians in fedoras and knee-length dresses browse storefronts. The Ferry Building's clock tower rises above the bustling commercial district."
      caption_short: "San Francisco, 1935 - Market Street streetcars"
      year: 1935
      subject: "downtown streetscape"
      dimensions:
        width: 1920
        height: 1080
        aspect_ratio: "16:9"
      generation:
        photo_condition: 3
        scenery_condition: 3
        generated_at: "2025-11-01T10:30:00Z"
    
    - path: "/images/regions/san_francisco/san_francisco_1925_harbor.png"
      caption: "San Francisco waterfront, 1925 - Wooden piers extend into the bay, lined with cargo vessels and fishing boats. Longshoremen in flat caps unload crates as seagulls circle above the fog-shrouded Golden Gate."
      caption_short: "San Francisco, 1925 - waterfront piers"
      year: 1925
      subject: "harbor"
      dimensions:
        width: 1920
        height: 1080
        aspect_ratio: "16:9"
      generation:
        photo_condition: 4
        scenery_condition: 3
        generated_at: "2025-11-01T10:32:00Z"
    
    - path: "/images/regions/san_francisco/san_francisco_1940_chinatown_district.png"
      caption: "Grant Avenue, Chinatown, 1948 - Paper lanterns and ornate balconies adorn the street as shoppers examine silk fabrics and porcelain. Chinese characters on shop signs advertise tea merchants and herbal apothecaries."
      caption_short: "San Francisco, 1948 - Chinatown shops"
      year: 1948
      subject: "chinatown district"
      dimensions:
        width: 1920
        height: 1080
        aspect_ratio: "16:9"
      generation:
        photo_condition: 2
        scenery_condition: 3
        generated_at: "2025-11-01T10:35:00Z"
  
  # Future: Add business/modern images if needed
  # business:
  #   - path: "/images/regions/san_francisco/modern_facility.png"
  #     caption: "Modern laser cleaning facility"
```

**Data Source:** Imagen 4 generation via `regions/image/generate.py`

**Generation Workflow:** (County-based batch processing)
1. **User input**: `python3 run.py --region "San Mateo County"`
2. **Retrieve cities**: Load all cities in county from `Cities.yaml`
3. **Random assignment**: Each city gets 1-3 images with unique year/subject/aging params
4. **Image generation**: Generate images to `/public/images/regions/{city_slug}/`
5. **Caption generation**: Gemini Vision creates long + short captions
6. **Frontmatter research**: Generate remaining text content per data model

**Generation Strategy:**
1. **Random selection**: Each city gets 1-3 historical images (randomized per city)
2. **Diverse subjects**: Vary between downtown, harbor, district, landmark, industry
3. **Decade variety**: Spread across 1920s-1950s for visual diversity
4. **Caption quality**: Long (150-200 chars) + short (40-60 chars) captions
5. **Metadata preservation**: Store generation parameters for reproducibility

**Caption Requirements:**
- **Long caption** (`caption`): 2-3 sentences (150-200 characters) for figure captions
  - Specific visual details (what you see in the image)
  - Period-appropriate context (vehicles, clothing, architecture)
  - Local landmarks or notable features
  - Natural, engaging tone (not generic)
- **Short caption** (`caption_short`): 40-60 characters for alt text
  - Format: "{City}, {Year} - [key visual element]"
  - SEO-friendly, concise description

**Image Selection Logic** (to be implemented in CityFrontmatterGenerator):
```python
import random

def generate_historical_images(city_name: str, county: str, num_images: int = None):
    """
    Generate 1-3 random historical images for city page.
    
    Args:
        city_name: City name
        county: County name
        num_images: Optional override (default: random 1-3)
    
    Returns:
        List of image dictionaries with path, caption, metadata
    """
    if num_images is None:
        num_images = random.randint(1, 3)
    
    # Possible subjects for variety
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
    
    images = []
    used_subjects = set()
    
    for i in range(num_images):
        # Select unique subject
        available_subjects = [s for s in subjects if s not in used_subjects]
        if not available_subjects:
            available_subjects = subjects  # Reset if exhausted
        
        subject = random.choice(available_subjects)
        used_subjects.add(subject)
        
        # Select random decade
        decade = random.choice(decades)
        year = int(decade.replace("s", "")) + random.randint(0, 9)
        
        # Generate image using existing infrastructure
        # TODO: Call regions/image/generate.py with subject parameter
        # image_path, caption, metadata = generate_city_image(
        #     city_name, county, year, subject
        # )
        
        # Placeholder structure (implement actual generation)
        images.append({
            "path": f"/images/regions/{city_name.lower().replace(' ', '_')}/{city_name.lower().replace(' ', '_')}_{year}_{subject.replace(' ', '_')}.png",
            "caption": "",  # Generated by image validation system
            "year": year,
            "subject": subject,
            "dimensions": {
                "width": 1920,
                "height": 1080,
                "aspect_ratio": "16:9"
            },
            "generation": {
                "prompt_used": "",  # Stored during generation
                "population": 0,  # From population research
                "category": "",  # From population research
                "generated_at": ""  # ISO timestamp
            }
        })
    
    return images
```

### 16. Generation Metadata

```yaml
_metadata:
  generator: "CityFrontmatterGenerator"
  version: "1.0.0"
  generated: "2025-10-31T08:30:00Z"
  last_updated: "2025-10-31T08:30:00Z"
  
  data_sources:
    primary: "regions/Cities.yaml"
    regional_context: "regions/data.yaml"
    materials: "materials/data/Materials.yaml"
  
  parent_region: "san-francisco-bay-area"
  state: "california"
  
  content_status: "researched"
  research_completed: true
  requires_human_review: false
  
  quality_metrics:
    word_count: 2847
    internal_links: 12
    external_links: 3
    faq_count: 8
    material_references: 4
    historical_images: 3  # Number of images generated
```

---

## URL Structure

### Pattern (SEO-Optimized)
```
/services/{city-slug}-laser-cleaning
```

**Rationale:**
- ✅ Matches search behavior: `"{city} laser cleaning"` (not `"{county} laser cleaning"`)
- ✅ Shorter, more shareable URLs
- ✅ Service-first hierarchy signals business focus
- ✅ County included in content, schema, and meta tags (not URL)

### Examples
- `/services/san-francisco-laser-cleaning`
- `/services/oakland-laser-cleaning`
- `/services/palo-alto-laser-cleaning`
- `/services/belmont-laser-cleaning`

### Canonical URL
```
https://z-beam.com/services/{city-slug}-laser-cleaning
```

### Breadcrumb Structure
```
Home > Services > {City} Laser Cleaning
```

**Breadcrumb Schema:**
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://z-beam.com"},
    {"@type": "ListItem", "position": 2, "name": "Services", "item": "https://z-beam.com/services"},
    {"@type": "ListItem", "position": 3, "name": "San Francisco Laser Cleaning"}
  ]
}
```

### County Inclusion Strategy

**Where to Include County (NOT in URL):**

1. **Page Title:**
   ```
   San Francisco Laser Cleaning Services | Serving San Francisco County
   ```

2. **Meta Description:**
   ```
   Professional laser cleaning services in San Francisco and throughout 
   San Francisco County. Industrial, historic preservation, and commercial 
   applications. Request a quote today.
   ```

3. **H2 Service Area:**
   ```html
   <h2>Serving San Francisco and All of San Francisco County</h2>
   <p>Our laser cleaning services cover San Francisco and the surrounding 
   communities throughout San Francisco County, including [nearby cities].</p>
   ```

4. **Schema Markup (LocalBusiness):**
   ```json
   {
     "@type": "LocalBusiness",
     "areaServed": [
       {"@type": "City", "name": "San Francisco"},
       {"@type": "AdministrativeArea", "name": "San Francisco County", "containedIn": "California"}
     ]
   }
   ```

5. **Service Area Map Description:**
   ```yaml
   service_area_map:
     description: "Serving San Francisco and all surrounding cities in 
                   San Francisco County within 50 miles"
   ```

**Why County Is NOT in URL:**
- Users search "{city} laser cleaning", not "{county} laser cleaning"
- Shorter URLs improve CTR and mobile sharing
- County context preserved in content, schema, and metadata where it matters for SEO

---

## Data Population Pipeline

### Step 1: Load City Data
**Source:** `regions/Cities.yaml`
```python
city_data = load_yaml("regions/Cities.yaml")
sf_data = city_data["cities"]["San Francisco"]
```

**Extracted Fields:**
- `population_history` → location.population_history
- `geographic_features` → location context
- `historical_industries` → economy.historical_industries
- `current_industries` → economy.primary_industries
- `transportation_history` → transportation.historical_transportation
- `notable_buildings` → historic_context.historic_buildings
- `cultural_significance` → historic_context.notable_history

### Step 2: Map Industries to Materials
**Logic:**
```python
# For each primary_industry in city
for industry in city_data["current_industries"]:
    # Match to material applications
    materials = match_industry_to_materials(industry, materials_db)
    
    # Create application mapping
    laser_cleaning_applications.append({
        "industry": industry,
        "applications": get_applications(industry),
        "materials": materials
    })
```

**Example Mapping:**
- Industry: "Technology Manufacturing"
  - Materials: Silicon, Aluminum, Copper, Stainless Steel
  - Applications: Wafer cleaning, server maintenance, component restoration

### Step 3: Apply Regional Regulations
**Source:** `regions/data.yaml`
```python
regional_regulations = get_regulations(city.region)
state_regulations = get_regulations(city.state)
local_regulations = research_city_regulations(city.name)
```

### Step 4: Generate City-Specific Content
**Components:**
- Economic overview (from Cities.yaml + materials mapping)
- Local applications (industry × materials matrix)
- Regulatory context (regional + state + local)
- Historic preservation (notable_buildings + cultural_significance)
- FAQ (template + local context injection)

### Step 5: Create Internal Links
**Logic:**
```python
# Link to materials common in city industries
materials_served = get_materials_for_industries(city.industries)

# Link to nearby cities
nearby_cities = get_nearby_cities(city, radius=30)

# Link to parent region
parent_region = city.region
```

---

## SEO Optimization Strategy

### Primary Keyword
`laser cleaning {city_name}`

### Secondary Keywords
- `laser cleaning services {city_name}`
- `industrial laser cleaning {city_name}`
- `{city_name} laser cleaning company`
- `precision cleaning {city_name}`

### Long-Tail Keywords
- `laser cleaning for {industry} in {city_name}`
- `historic building cleaning {city_name}`
- `{material} laser cleaning {city_name}`
- `eco-friendly cleaning services {city_name}`

### Local SEO Elements
- Google My Business integration
- Schema.org LocalBusiness + ProfessionalService markup
- City-specific content (landmarks, industries, regulations)
- Internal linking to related city pages
- Geographic coordinates for map integration

### Content Quality Targets
- **Word count:** 2000-3000 words
- **Readability:** Professional (12th grade level)
- **Keyword density:** 1-2%
- **Header structure:** H1 > H2 > H3 hierarchy
- **Internal links:** 8-15 relevant pages
- **External links:** 2-3 authoritative sources (regulatory agencies)

---

## Implementation Notes

### Generator Class
```python
class CityFrontmatterGenerator:
    def __init__(self, cities_yaml_path, materials_yaml_path, regions_yaml_path):
        self.cities_data = load_yaml(cities_yaml_path)
        self.materials_data = load_yaml(materials_yaml_path)
        self.regions_data = load_yaml(regions_yaml_path)
    
    def generate_city_page(self, city_name):
        # Load city data
        city = self.cities_data["cities"][city_name]
        
        # Map industries to materials
        applications = self.map_industries_to_materials(city["current_industries"])
        
        # Apply regional regulations
        regulations = self.get_regulations(city["county"], city["state"])
        
        # Generate historic context
        historic = self.build_historic_context(city["notable_buildings"], 
                                                city["cultural_significance"])
        
        # Create FAQ with city-specific content
        faq = self.generate_faq(city_name, applications, historic)
        
        # Build frontmatter
        frontmatter = self.build_frontmatter(city, applications, 
                                             regulations, historic, faq)
        
        return frontmatter
```

### File Naming Convention
```
frontmatter/cities/san-francisco-county/san-francisco-laser-cleaning.yaml
frontmatter/cities/alameda-county/oakland-laser-cleaning.yaml
frontmatter/cities/contra-costa-county/martinez-laser-cleaning.yaml
```

### Generation Order
1. Research all cities with city_data_researcher.py
2. Populate Cities.yaml with comprehensive data
3. Run CityFrontmatterGenerator for each city
4. Validate generated frontmatter
5. Export to Next.js content directory

---

## Quality Assurance Checklist

- [ ] City data complete in Cities.yaml
- [ ] All industries mapped to materials
- [ ] Local regulations researched and applied
- [ ] Historic buildings included with materials list
- [ ] FAQ answers include city-specific context
- [ ] 8-15 internal links to materials/regions/applications
- [ ] Schema.org markup includes geo-coordinates
- [ ] Word count 2000-3000
- [ ] All required frontmatter fields present
- [ ] Author voice applied consistently
- [ ] SEO meta descriptions under 160 characters
- [ ] No broken internal links
- [ ] All material slugs valid

---

## Next Steps

1. **Populate Cities.yaml** with city_data_researcher.py (93 Bay Area cities)
2. **Create CityFrontmatterGenerator** class
3. **Implement industry-to-material mapping** logic
4. **Build FAQ generation** with city context injection
5. **Generate frontmatter** for all 93 cities
6. **Validate output** against schema
7. **Export to Next.js** content directory
8. **Test local SEO** ranking for target queries
