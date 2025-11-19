#!/usr/bin/env python3
"""
City Data Researcher

Uses Grok AI to research comprehensive city data for Bay Area cities
and populate Cities.yaml file with historical information.

Author: AI Assistant
Date: October 31, 2025
"""

import json
import logging
import os
import sys
from typing import Dict, List, Optional
import yaml
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class CityDataResearcher:
    """Research city data using Grok AI and populate Cities.yaml"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize researcher with Grok API.
        
        Args:
            api_key: Optional Grok API key (will use env var if not provided)
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("XAI_API_KEY not found in environment or provided")
        
        # Grok uses OpenAI-compatible API
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1"
            )
            self.model = "grok-beta"
            logger.info("✅ City data researcher initialized with Grok AI")
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")
    
    def research_city(self, city_name: str, county_name: str) -> Dict:
        """
        Research comprehensive city data using Grok AI.
        
        Args:
            city_name: Name of the city
            county_name: Name of the county
            
        Returns:
            Dictionary with comprehensive city data
        """
        prompt = f"""Research comprehensive historical and demographic data for {city_name}, {county_name}, California.

Provide detailed information in the following JSON format:

{{
    "name": "{city_name}",
    "county": "{county_name}",
    "state": "California",
    "region": "San Francisco Bay Area",
    "incorporation_year": <year city was incorporated, or null if unincorporated>,
    "historical_context": "<2-3 sentences about city's founding and historical significance>",
    "population_history": {{
        "1900": <population or null if didn't exist>,
        "1910": <population or null>,
        "1920": <population or null>,
        "1930": <population or null>,
        "1940": <population or null>,
        "1950": <population or null>,
        "1960": <population or null>,
        "1970": <population or null>,
        "1980": <population or null>,
        "1990": <population or null>,
        "2000": <population or null>,
        "2010": <population or null>,
        "2020": <population or null>
    }},
    "geographic_features": {{
        "elevation_feet": <elevation in feet>,
        "area_square_miles": <total area>,
        "terrain": "<description of terrain>",
        "climate": "<climate description>",
        "notable_landmarks": [
            "<landmark 1>",
            "<landmark 2>",
            "<landmark 3>"
        ]
    }},
    "historical_industries": [
        "<primary historical industry 1>",
        "<primary historical industry 2>",
        "<primary historical industry 3>"
    ],
    "current_industries": [
        "<current primary industry 1>",
        "<current primary industry 2>",
        "<current primary industry 3>"
    ],
    "historical_periods": {{
        "indigenous": "<brief description of indigenous peoples>",
        "spanish_mexican": "<brief description 1769-1848>",
        "early_american": "<brief description 1850s-1900>",
        "early_20th_century": "<brief description 1900-1945>",
        "post_war": "<brief description 1945-1980>",
        "modern": "<brief description 1980-present>"
    }},
    "transportation_history": {{
        "railroads": "<railroad history or null>",
        "streetcars": "<streetcar history or null>",
        "ferries": "<ferry history or null>",
        "highways": "<major highway access>"
    }},
    "notable_buildings": [
        {{
            "name": "<building name>",
            "year_built": <year>,
            "architectural_style": "<style>",
            "significance": "<why notable>"
        }}
    ],
    "cultural_significance": "<2-3 sentences about cultural importance>",
    "demographics": {{
        "ethnic_diversity": "<description>",
        "economic_status": "<description>",
        "education_level": "<description>"
    }}
}}

IMPORTANT: 
- Use actual historical data from reliable sources
- Population figures should be from US Census data when available
- For years before incorporation, use null
- Be specific about historical context and landmarks
- Include architectural styles accurately
- Format as valid JSON with no trailing commas"""

        try:
            logger.info(f"🔍 Researching: {city_name}, {county_name}")
            
            # Call Grok API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a historical researcher specializing in California Bay Area history and demographics. Provide accurate, well-researched data in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=2000
            )
            
            # Extract response text
            response_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            data = json.loads(response_text)
            
            logger.info(f"✅ Successfully researched {city_name}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error for {city_name}: {e}")
            logger.error(f"Response text: {response_text}")
            raise
        except Exception as e:
            logger.error(f"❌ Error researching {city_name}: {e}")
            raise
    
    def load_existing_cities(self, yaml_path: str) -> Dict:
        """Load existing Cities.yaml if it exists."""
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as f:
                return yaml.safe_load(f) or {"cities": {}}
        return {"cities": {}}
    
    def save_cities(self, data: Dict, yaml_path: str):
        """Save cities data to YAML file."""
        with open(yaml_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        logger.info(f"💾 Saved cities data to {yaml_path}")
    
    def research_bay_area_cities(self, counties: List[tuple], output_path: str = None, limit: int = None):
        """
        Research multiple Bay Area cities and populate Cities.yaml.
        
        Args:
            counties: List of (county_name, [city_list]) tuples
            output_path: Path to output YAML file (default: regions/Cities.yaml)
            limit: Optional limit on number of cities to research (for testing)
        """
        if output_path is None:
            output_path = os.path.join(os.path.dirname(__file__), "Cities.yaml")
        
        # Load existing data
        cities_data = self.load_existing_cities(output_path)
        
        # Ensure cities key exists
        if "cities" not in cities_data:
            cities_data["cities"] = {}
        
        # Add metadata
        cities_data["_metadata"] = {
            "version": "1.0.0",
            "created": "2025-10-31",
            "updated": "2025-10-31",
            "description": "Comprehensive historical and demographic data for San Francisco Bay Area cities",
            "data_source": "Grok AI research with historical US Census data",
            "total_cities": 0,  # Will update at end
            "coverage": "San Francisco Bay Area - 9 counties"
        }
        
        total_researched = 0
        
        for county_name, city_list in counties:
            logger.info(f"\n{'='*60}")
            logger.info(f"📍 Researching {county_name}")
            logger.info(f"{'='*60}")
            
            for city_name in city_list:
                # Check if already researched
                city_key = city_name.lower().replace(" ", "_")
                if city_key in cities_data["cities"]:
                    logger.info(f"⏭️  Skipping {city_name} (already researched)")
                    continue
                
                try:
                    # Research city
                    city_data = self.research_city(city_name, county_name)
                    
                    # Add to data structure
                    cities_data["cities"][city_key] = city_data
                    
                    total_researched += 1
                    
                    # Save after each city (incremental saves)
                    cities_data["_metadata"]["total_cities"] = len(cities_data["cities"])
                    self.save_cities(cities_data, output_path)
                    
                    logger.info(f"✅ {total_researched}. {city_name} - Complete")
                    
                    # Check limit
                    if limit and total_researched >= limit:
                        logger.info(f"\n⚠️  Reached limit of {limit} cities")
                        return
                    
                except Exception as e:
                    logger.error(f"❌ Failed to research {city_name}: {e}")
                    logger.error(f"   Continuing with next city...")
                    continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Research complete!")
        logger.info(f"📊 Total cities researched: {total_researched}")
        logger.info(f"📊 Total cities in database: {len(cities_data['cities'])}")
        logger.info(f"💾 Saved to: {output_path}")
        logger.info(f"{'='*60}")


def main():
    """Main execution function"""
    import argparse
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Research Bay Area city data using Grok AI')
    parser.add_argument('--county', type=str, help='Research specific county only')
    parser.add_argument('--city', type=str, help='Research specific city only')
    parser.add_argument('--limit', type=int, help='Limit number of cities to research (for testing)')
    parser.add_argument('--output', type=str, help='Output YAML file path')
    
    args = parser.parse_args()
    
    # Bay Area counties and cities from regions/data.yaml
    bay_area_cities = [
        ("Alameda County", [
            "Oakland", "Fremont", "Hayward", "Berkeley", "San Leandro",
            "Alameda", "Union City", "Newark", "Pleasanton", "Dublin",
            "Livermore", "Albany", "Emeryville", "Piedmont"
        ]),
        ("Contra Costa County", [
            "Concord", "Richmond", "Antioch", "Walnut Creek", "San Ramon",
            "Pittsburg", "Brentwood", "Martinez", "Pleasant Hill", "El Cerrito",
            "Pinole", "Hercules", "Danville", "San Pablo", "Lafayette",
            "Orinda", "Moraga"
        ]),
        ("Marin County", [
            "San Rafael", "Novato", "Sausalito", "Mill Valley", "Tiburon",
            "Larkspur", "Corte Madera", "San Anselmo", "Fairfax"
        ]),
        ("Napa County", [
            "Napa", "American Canyon", "St. Helena", "Calistoga", "Yountville"
        ]),
        ("San Francisco County", [
            "San Francisco"
        ]),
        ("San Mateo County", [
            "Daly City", "San Mateo", "Redwood City", "South San Francisco",
            "San Bruno", "Pacifica", "Burlingame", "Millbrae", "Foster City",
            "San Carlos", "Belmont", "Half Moon Bay", "Menlo Park", "Atherton",
            "Portola Valley", "Hillsborough"
        ]),
        ("Santa Clara County", [
            "San Jose", "Sunnyvale", "Santa Clara", "Mountain View", "Palo Alto",
            "Milpitas", "Cupertino", "Campbell", "Los Gatos", "Saratoga",
            "Los Altos", "Morgan Hill", "Gilroy", "Los Altos Hills", "Monte Sereno"
        ]),
        ("Solano County", [
            "Fairfield", "Vallejo", "Vacaville", "Suisun City", "Benicia",
            "Dixon", "Rio Vista"
        ]),
        ("Sonoma County", [
            "Santa Rosa", "Petaluma", "Rohnert Park", "Sebastopol", "Cotati",
            "Cloverdale", "Healdsburg", "Windsor", "Sonoma"
        ])
    ]
    
    # Filter by county or city if specified
    if args.county or args.city:
        filtered_cities = []
        for county_name, city_list in bay_area_cities:
            if args.county and args.county.lower() not in county_name.lower():
                continue
            
            if args.city:
                city_list = [c for c in city_list if args.city.lower() in c.lower()]
            
            if city_list:
                filtered_cities.append((county_name, city_list))
        
        bay_area_cities = filtered_cities
    
    # Initialize researcher
    try:
        researcher = CityDataResearcher()
    except ValueError as e:
        logger.error(f"❌ {e}")
        logger.error("Please set XAI_API_KEY environment variable with your Grok API key")
        sys.exit(1)
    
    # Research cities
    researcher.research_bay_area_cities(
        bay_area_cities,
        output_path=args.output,
        limit=args.limit
    )


if __name__ == "__main__":
    main()
