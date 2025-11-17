# Service Area Map Data Structure for Frontmatter

**Version:** 1.0.0  
**Created:** November 1, 2025  
**Purpose:** Geographic data structure for city service area visualization

---

## Overview

This document defines the **frontmatter data structure** for service area maps. The z-beam-generator creates YAML frontmatter files containing geographic data. The z-beam Next.js frontend consumes this data to render maps.

**Scope of This Project:**
- ✅ Generate `service_area_map` data in city frontmatter YAML
- ✅ Calculate nearby cities with distances and directions
- ✅ Store map configuration preferences
- ❌ NOT generating images (frontend handles rendering)
- ❌ NOT calling external APIs during generation
- ❌ NOT creating map visualizations (Next.js does this)

**Responsibilities:**
- **z-beam-generator** (this project): Create frontmatter YAML with geographic data
- **z-beam Next.js** (separate project): Render maps using Google Maps API

---

## Architecture

### Data Flow

```
Cities.yaml
    ↓
CityFrontmatterGenerator
    ↓
service_area_map data structure
    ↓
city-name-laser-cleaning.yaml (frontmatter)
    ↓
[Next.js consumes YAML]
    ↓
Google Maps rendering (frontend)
```

**Key Principle:** Zero external dependencies during generation. Pure data transformation.

---

## Frontmatter Data Structure

### 1. Schema Definition

Add to `CITY_FRONTMATTER_DATA_MODEL.md` (Section 8A - after Transportation):

**Note:** See `CITY_FRONTMATTER_DATA_MODEL.md` for complete structure including:
- Section 15: `images` key (historical images with captions)
- URL structure: `/services/{city-slug}-laser-cleaning` (county NOT in URL)
- County inclusion: content, schema `areaServed`, and meta tags only

```yaml
service_area_map:
  # Center point (city location)
  center:
    latitude: 37.7749
    longitude: -122.4194
    city: "San Francisco"
    county: "San Francisco County"
  
  # Service coverage
  service_radius:
    miles: 50
    description: "50-mile service radius covering San Francisco Bay Area"
  
  # Nearby cities for reference points
  nearby_cities:
    - name: "Oakland"
      latitude: 37.8044
      longitude: -122.2712
      distance_miles: 10
      direction: "East"
      county: "Alameda County"
      url_slug: "/alameda-county/oakland-laser-cleaning"
    
    - name: "San Jose"
      latitude: 37.3382
      longitude: -121.8863
      distance_miles: 45
      direction: "Southeast"
      county: "Santa Clara County"
      url_slug: "/santa-clara-county/san-jose-laser-cleaning"
    
    - name: "Berkeley"
      latitude: 37.8715
      longitude: -122.2730
      distance_miles: 12
      direction: "Northeast"
      county: "Alameda County"
      url_slug: "/alameda-county/berkeley-laser-cleaning"
    
    - name: "Palo Alto"
      latitude: 37.4419
      longitude: -122.1430
      distance_miles: 30
      direction: "South"
      county: "Santa Clara County"
      url_slug: "/santa-clara-county/palo-alto-laser-cleaning"
  
  # Map display preferences
  map_config:
    zoom_level: 9  # Google Maps zoom (1-20)
    map_type: "roadmap"  # roadmap, satellite, hybrid, terrain
    show_radius_circle: true
    show_nearby_markers: true
    show_traffic: false
  
  # Textual description for accessibility/SEO
  coverage_description: >
    Z-Beam provides laser cleaning services throughout the San Francisco Bay Area,
    with a primary service area covering a 50-mile radius from San Francisco.
    We serve Oakland (10 miles), San Jose (45 miles), Berkeley (12 miles),
    Palo Alto (30 miles), and surrounding communities.
```

### 2. Generation Logic in CityFrontmatterGenerator

**File:** `regions/frontmatter/city_frontmatter_generator.py` (to be created)

```python
def generate_service_area_map_data(self, city_data: Dict, cities_yaml: Dict) -> Dict:
    """
    Generate service area map data for frontmatter.
    
    Args:
        city_data: City data from Cities.yaml
        cities_yaml: Full Cities.yaml for nearby city lookup
    
    Returns:
        service_area_map dictionary for frontmatter
    """
    from math import radians, cos, sin, asin, sqrt
    
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance in miles between two lat/lon points"""
        R = 3959  # Earth radius in miles
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return R * c
    
    def get_direction(lat1, lon1, lat2, lon2):
        """Get cardinal direction from point 1 to point 2"""
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        if abs(dlon) > abs(dlat):
            return "East" if dlon > 0 else "West"
        else:
            return "North" if dlat > 0 else "South"
    
    # Extract city center coordinates
    center_lat = city_data["latitude"]
    center_lon = city_data["longitude"]
    city_name = city_data["name"]
    county_name = city_data["county"]
    
    # Find nearby cities within 50 miles
    nearby_cities = []
    service_radius = 50  # miles
    
    for other_city_key, other_city_data in cities_yaml["cities"].items():
        # Skip self
        if other_city_data["name"] == city_name:
            continue
        
        other_lat = other_city_data["latitude"]
        other_lon = other_city_data["longitude"]
        
        distance = haversine_distance(center_lat, center_lon, other_lat, other_lon)
        
        # Include cities within service radius, prioritize larger/closer cities
        if distance <= service_radius:
            nearby_cities.append({
                "name": other_city_data["name"],
                "latitude": other_lat,
                "longitude": other_lon,
                "distance_miles": round(distance),
                "direction": get_direction(center_lat, center_lon, other_lat, other_lon),
                "county": other_city_data["county"],
                "url_slug": f"/{other_city_data['county'].lower().replace(' ', '-')}/{other_city_data['name'].lower().replace(' ', '-')}-laser-cleaning",
                "population": other_city_data.get("population", 0)
            })
    
    # Sort by distance and take top 8 (mix of close and far)
    nearby_cities.sort(key=lambda x: x["distance_miles"])
    
    # Intelligent selection: 4 closest + 4 largest within radius
    closest_4 = nearby_cities[:4]
    remaining = [c for c in nearby_cities[4:] if c["population"] > 20000]
    remaining.sort(key=lambda x: x["population"], reverse=True)
    largest_4 = remaining[:4]
    
    # Combine and remove duplicates
    selected_cities = closest_4 + [c for c in largest_4 if c not in closest_4]
    selected_cities = selected_cities[:8]  # Cap at 8 markers
    
    # Remove population key (not needed in frontmatter)
    for city in selected_cities:
        city.pop("population", None)
    
    # Build coverage description
    city_names = ", ".join([f"{c['name']} ({c['distance_miles']} miles)" for c in selected_cities[:4]])
    coverage_description = (
        f"Z-Beam provides laser cleaning services throughout the {city_data.get('region', 'region')}, "
        f"with a primary service area covering a {service_radius}-mile radius from {city_name}. "
        f"We serve {city_names}, and surrounding communities."
    )
    
    return {
        "center": {
            "latitude": center_lat,
            "longitude": center_lon,
            "city": city_name,
            "county": county_name
        },
        "service_radius": {
            "miles": service_radius,
            "description": f"{service_radius}-mile service radius covering {city_data.get('region', 'region')}"
        },
        "nearby_cities": selected_cities,
        "map_config": {
            "zoom_level": 9,  # Good for 50-mile radius
            "map_type": "roadmap",
            "show_radius_circle": True,
            "show_nearby_markers": True,
            "show_traffic": False
        },
        "coverage_description": coverage_description
    }
```

### 3. Integration with CityFrontmatterGenerator

```python
class CityFrontmatterGenerator(BaseFrontmatterGenerator):
    """Generate city-specific laser cleaning frontmatter"""
    
    def _build_frontmatter_data(self, identifier: str, context: GenerationContext) -> Dict[str, Any]:
        """Build complete city frontmatter data"""
        
        # ... existing sections ...
        
        # Generate service area map data
        service_area_map = self.generate_service_area_map_data(
            city_data=self.cities_data["cities"][identifier],
            cities_yaml=self.cities_data
        )
        
        frontmatter = {
            # ... existing fields ...
            "service_area_map": service_area_map,
            # ... rest of frontmatter ...
        }
        
        return frontmatter
```

---

## Example Output YAML

**File:** `frontmatter/cities/san-francisco-county/san-francisco-laser-cleaning.yaml`

```yaml
# ... other frontmatter fields ...

service_area_map:
  center:
    latitude: 37.7749
    longitude: -122.4194
    city: "San Francisco"
    county: "San Francisco County"
  
  service_radius:
    miles: 50
    description: "50-mile service radius covering San Francisco Bay Area"
  
  nearby_cities:
    - name: "Oakland"
      latitude: 37.8044
      longitude: -122.2712
      distance_miles: 10
      direction: "East"
      county: "Alameda County"
      url_slug: "/alameda-county/oakland-laser-cleaning"
    
    - name: "Berkeley"
      latitude: 37.8715
      longitude: -122.2730
      distance_miles: 12
      direction: "Northeast"
      county: "Alameda County"
      url_slug: "/alameda-county/berkeley-laser-cleaning"
    
    - name: "Palo Alto"
      latitude: 37.4419
      longitude: -122.1430
      distance_miles: 30
      direction: "South"
      county: "Santa Clara County"
      url_slug: "/santa-clara-county/palo-alto-laser-cleaning"
    
    - name: "San Jose"
      latitude: 37.3382
      longitude: -121.8863
      distance_miles: 45
      direction: "Southeast"
      county: "Santa Clara County"
      url_slug: "/santa-clara-county/san-jose-laser-cleaning"
  
  map_config:
    zoom_level: 9
    map_type: "roadmap"
    show_radius_circle: true
    show_nearby_markers: true
    show_traffic: false
  
  coverage_description: "Z-Beam provides laser cleaning services throughout the San Francisco Bay Area, with a primary service area covering a 50-mile radius from San Francisco. We serve Oakland (10 miles), Berkeley (12 miles), Palo Alto (30 miles), San Jose (45 miles), and surrounding communities."

# ... rest of frontmatter ...
```

**Frontend Usage (z-beam Next.js):**
The Next.js frontend reads this YAML and renders maps using Google Maps API. Frontend implementation details are in the z-beam project, not here.

---

## Implementation Steps (z-beam-generator)

### Step 1: Update CITY_FRONTMATTER_DATA_MODEL.md
- [ ] Add `service_area_map` section to data model
- [ ] Define schema with all required fields
- [ ] Document data sources and generation logic

### Step 2: Implement Generation Logic
- [ ] Add `generate_service_area_map_data()` method to generator utilities
- [ ] Implement haversine distance calculation
- [ ] Add cardinal direction calculation
- [ ] Implement nearby city selection (closest + largest)

### Step 3: Integrate with CityFrontmatterGenerator
- [ ] Call `generate_service_area_map_data()` in `_build_frontmatter_data()`
- [ ] Add to frontmatter dictionary
- [ ] Validate YAML output structure

### Step 4: Test with Pilot Cities
- [ ] Generate frontmatter for San Francisco
- [ ] Generate frontmatter for Oakland
- [ ] Generate frontmatter for San Jose
- [ ] Validate coordinate accuracy
- [ ] Verify nearby city calculations

### Step 5: Production Rollout
- [ ] Generate all 93 Bay Area cities
- [ ] Validate all frontmatter files
- [ ] Commit to repository
- [ ] Document for frontend team

**Timeline:** 1-2 days for implementation + testing

---

## Frontend Implementation (z-beam Next.js)

**Note:** This is NOT implemented in z-beam-generator. This is for the frontend team's reference.

### Frontend Responsibilities:
1. Read `service_area_map` from frontmatter YAML
2. Render map using Google Maps API (Static or JS API)
3. Display as hero image on city pages
4. Handle user interactions (if using interactive maps)

### Google Maps API Costs (Frontend):
- **Static Maps API**: Free tier 25k/month ($2 per 1k beyond)
- **Maps JS API**: Free tier 28k/month ($7 per 1k beyond)
- **Expected cost**: $0/month (within free tiers)

---

## Benefits of This Data Structure

### For z-beam-generator (This Project)
✅ **Zero external dependencies** - Pure data transformation, no API calls  
✅ **Fast generation** - Haversine calculation is lightweight  
✅ **Deterministic** - Same input always produces same output  
✅ **Testable** - Easy to validate coordinate accuracy  
✅ **Maintainable** - Simple data structure, clear schema

### For z-beam Next.js (Frontend)
✅ **Complete geographic data** - Everything needed to render maps  
✅ **Flexible rendering** - Can use Google Maps, Mapbox, Leaflet, or custom SVG  
✅ **SEO-friendly** - coverage_description provides text for search engines  
✅ **Internal linking** - url_slug enables cross-linking between city pages  
✅ **User experience** - Visual map shows service area at a glance

### For Business
✅ **Trust signal** - Professional map shows real local presence  
✅ **Lead generation** - Clear coverage area reduces customer uncertainty  
✅ **Cross-selling** - Nearby city links drive additional page views  
✅ **Competitive advantage** - Most competitors use generic stock photos

---

## Recommendation

**Implement frontmatter data structure now:**

1. ✅ Add `service_area_map` schema to `CITY_FRONTMATTER_DATA_MODEL.md`
2. ✅ Implement `generate_service_area_map_data()` in generator utilities
3. ✅ Integrate with `CityFrontmatterGenerator`
4. ✅ Test with 3-5 pilot cities
5. ✅ Generate all 93 Bay Area cities

**Frontend team handles:**
- Google Maps API integration
- Map rendering (static or interactive)
- User interaction handling
- Performance optimization

**Separation of concerns:**
- **z-beam-generator**: Pure data (YAML frontmatter)
- **z-beam Next.js**: Presentation (map visualization)

This keeps the generator lightweight with zero external dependencies.
