#!/usr/bin/env python3
"""
Historical Population Researcher

Uses Gemini API to research historical population data for cities
and determine appropriate image generation parameters.

Author: AI Assistant
Date: October 30, 2025
"""

import json
import logging
import os
from typing import Dict, Optional
from functools import lru_cache

import google.generativeai as genai

logger = logging.getLogger(__name__)


class PopulationResearcher:
    """Research historical population data to inform image generation"""
    
    # Population size categories and their characteristics
    # Refined to prevent over-representing town size in images
    POPULATION_CATEGORIES = {
        "rural_hamlet": {
            "max": 500,
            "description": "rural hamlet or village",
            "street_type": "unpaved dirt road or single lane",
            "development": "1-3 small wooden buildings, general store, possibly a church",
            "density": "extremely sparse, rural farmland character",
            "vehicles": "primarily horse-drawn wagons, maybe 1-2 early automobiles",
            "details": "simple wooden structures, dirt paths, agricultural setting, minimal signage",
            "buildings": "1-3 simple structures",
            "pedestrians": "few people (2-5 visible)",
            "street_width": "narrow single track"
        },
        "small_village": {
            "max": 2000,
            "description": "small village",
            "street_type": "unpaved main street, dusty or muddy",
            "development": "4-8 simple storefronts along one street, mostly wooden construction",
            "density": "low-density, primarily residential with small commercial center",
            "vehicles": "mix of horse-drawn and early automobiles (1-3 visible)",
            "details": "wooden facades, simple painted signs, hitching posts, minimal street activity",
            "buildings": "4-8 modest storefronts",
            "pedestrians": "sparse (5-10 people)",
            "street_width": "two-lane unpaved"
        },
        "town": {
            "max": 5000,
            "description": "small town",
            "street_type": "main street, possibly partially paved",
            "development": "10-15 storefronts on main commercial block, mix of wood and brick",
            "density": "compact town center with surrounding residential areas",
            "vehicles": "several period automobiles and horse-drawn vehicles",
            "details": "mix of wooden and brick buildings, awnings, readable business signs, moderate activity",
            "buildings": "10-15 storefronts",
            "pedestrians": "moderate (10-20 people)",
            "street_width": "standard two-lane"
        },
        "large_town": {
            "max": 10000,
            "description": "large town or small city",
            "street_type": "paved main commercial street",
            "development": "15-25 commercial buildings, mostly 2-story brick or stone",
            "density": "established downtown core with continuous storefronts",
            "vehicles": "regular automobile traffic, parked cars visible",
            "details": "substantial brick buildings, prominent signage, active pedestrian traffic, developed infrastructure",
            "buildings": "15-25 two-story buildings",
            "pedestrians": "busy (20-40 people)",
            "street_width": "wide two-lane with parking"
        },
        "small_city": {
            "max": 30000,
            "description": "small city",
            "street_type": "paved commercial boulevard",
            "development": "dense continuous row of 2-3 story commercial buildings",
            "density": "urban density with established commercial district",
            "vehicles": "steady automobile traffic, possibly streetcars or trolleys",
            "details": "substantial architecture, multiple prominent businesses, active street life, urban infrastructure",
            "buildings": "25-40 multi-story buildings",
            "pedestrians": "crowded (40-80 people)",
            "street_width": "wide boulevard with streetcar tracks"
        },
        "city": {
            "max": 100000,
            "description": "city",
            "street_type": "major downtown thoroughfare",
            "development": "tall 3-4 story buildings, continuous urban streetscape",
            "density": "high urban density, city center",
            "vehicles": "heavy traffic, streetcars, many parked automobiles",
            "details": "impressive architecture, large commercial signs, dense pedestrian crowds, prominent civic buildings",
            "buildings": "40+ three-to-four story buildings",
            "pedestrians": "very crowded (80-150 people)",
            "street_width": "major thoroughfare with multiple lanes"
        },
        "major_city": {
            "max": float('inf'),
            "description": "major city",
            "street_type": "bustling metropolitan downtown",
            "development": "tall buildings 4-8+ stories, dense urban canyon effect",
            "density": "metropolitan density",
            "vehicles": "congested traffic, multiple streetcar lines, parking difficulties",
            "details": "grand architecture, large department stores, prominent signage, very crowded sidewalks, urban intensity",
            "buildings": "dense high-rise district",
            "pedestrians": "extremely crowded (150+ people)",
            "street_width": "wide multi-lane thoroughfare"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize researcher with Gemini API.
        
        Args:
            api_key: Optional Gemini API key (will use env var if not provided)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or provided")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        logger.info("✅ Population researcher initialized with Gemini Flash 2.0")
    
    @lru_cache(maxsize=128)
    def research_population(self, city_name: str, county_name: str, decade: str, subject: str = None) -> Dict[str, any]:
        """
        Research historical population for a city in a specific decade, with optional subject focus.
        
        Args:
            city_name: Name of the city
            county_name: Name of the county
            decade: Decade string (e.g., "1930s")
            subject: Optional specific subject (e.g., "harbor", "ranch", "train station")
            
        Returns:
            Dictionary with population data and image parameters:
            {
                "population": int,
                "category": str,
                "characteristics": dict,
                "year": str,
                "source_info": str,
                "main_street": str,
                "street_details": str,
                "subject_details": str (if subject provided)
            }
        """
        logger.info(f"🔍 Researching: {city_name}, {county_name} in {decade}" + (f" (subject: {subject})" if subject else ""))
        
        # Extract year from decade (e.g., "1930s" -> "1935")
        year = decade.replace("s", "")
        mid_decade = str(int(year) + 5)
        
        # Build base prompt
        if subject:
            prompt = f"""Research the historical context of {city_name}, {county_name}, California during the {decade}, with specific focus on {subject}.

Provide:
1. The approximate population in the middle of the decade (around {mid_decade})
2. Specific details about the {subject} in {city_name} during the {decade} (location, characteristics, notable features, historical significance)
3. The atmosphere and visual characteristics of the {subject} at that time
4. Brief character description of the city at that time

Format your response as JSON (IMPORTANT: Use plain numbers without commas or formatting):
{{
    "population": <number without commas>,
    "year": "{mid_decade}",
    "main_street": "<location name or area where {subject} was located>",
    "street_details": "<2-3 sentences about the {subject} in {decade}, including what it looked like, what activities happened there, specific buildings or features>",
    "subject_details": "<detailed description of {subject} visual characteristics, structures, equipment, atmosphere, people, activities>",
    "character": "<brief city description emphasizing connection to {subject}>",
    "source_note": "<historical context>"
}}

Be specific and historically accurate. Include actual locations, real names, and authentic period details about the {subject}."""
        else:
            prompt = f"""Research the ACTUAL HISTORICAL POPULATION and visual character of {city_name}, {county_name}, California in {mid_decade}.

CRITICAL REQUIREMENTS:

1. VERIFY ACTUAL POPULATION from {mid_decade} census or historical records
   - Use U.S. Census Bureau data, historical archives, or credible local history sources
   - If exact {mid_decade} data unavailable, interpolate between nearest census years
   - Population MUST match actual historical records - this is essential for accurate scene scale
   - Include your source/reasoning for the population figure

2. MATCH SCENE SCALE TO ACTUAL POPULATION:
   - Under 500: Rural hamlet (1-3 buildings, dirt road, minimal activity)
   - 500-2000: Small village (4-8 simple storefronts, unpaved street, few people)
   - 2000-5000: Small town (10-15 buildings, possibly paved, moderate activity)
   - 5000-10000: Large town (15-25 two-story buildings, paved streets, busy)
   - 10000-30000: Small city (25-40 buildings, continuous storefronts, urban feel)
   - 30000-100000: City (40+ tall buildings, dense crowds, major infrastructure)
   - 100000+: Major city (high-rises, metropolitan density, congested)

3. IDENTIFY THE MOST ICONIC SCENE for {city_name} in {decade}

4. 5-7 KEY VISUAL ELEMENTS (each 10-15 words max):
   - Most distinctive building/landmark with architectural details
   - Typical clothing styles (be period-specific)
   - Transportation type and quantity (match population scale)
   - Street characteristics (paving, width, condition)
   - SPECIFIC BUSINESS NAMES with CORRECT SPELLING (real historical businesses if known)
   - Number of people visible (must match town size - don't show crowds in small villages!)
   - Atmospheric qualities (light, weather, activity level)

5. 3-5 SCENE-SPECIFIC NEGATIVE PROMPTS (anachronisms that break authenticity)

CRITICAL: The visual scale must match the actual population. A village of 800 people should NOT look like a bustling city with crowds and dozens of buildings. Be historically accurate.

Format as JSON (NO commas in numbers):
{{
    "population": <actual historical number>,
    "year": "{mid_decade}",
    "population_source": "<how you verified this - census year, historical record, interpolation method>",
    "iconic_scene": "<short descriptive name>",
    "main_street": "<specific street or location name>",
    "street_details": "<1-2 sentences describing the scene and what's happening>",
    "key_visuals": [
        "Building/landmark with architectural style",
        "Clothing: specific period styles for men and women",
        "Transportation: type and quantity appropriate to population",
        "Street: paving, width, and condition",
        "Businesses: 'Name's Business Type' with correct spelling",
        "People: specific number visible, activities",
        "Atmosphere: lighting, weather, activity level"
    ],
    "scene_negatives": [
        "Specific modern element that breaks period",
        "Another anachronism to avoid",
        "Scale mismatch to avoid"
    ]
}}

VERIFY POPULATION ACCURACY - the entire image authenticity depends on correct historical population data."""

        try:
            # Generate research response
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Try to parse JSON, with fallback for common issues
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Try to fix common JSON issues (unescaped quotes in strings)
                logger.warning(f"Initial JSON parse failed, attempting repair: {e}")
                # Replace unescaped quotes within string values (simple heuristic)
                import re
                # Find string values and escape internal quotes
                fixed_text = re.sub(r'("(?:[^"\\]|\\.)*")', lambda m: m.group(0), response_text)
                # More aggressive: replace parenthetical quotes with single quotes
                fixed_text = re.sub(r'\("([^)]+)"\)', r"('\1')", response_text)
                try:
                    data = json.loads(fixed_text)
                    logger.info("✅ JSON repaired successfully")
                except json.JSONDecodeError:
                    # Last resort: try json5 or manual extraction
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Raw response: {response_text}")
                    raise
            
            # Extract and format visual elements
            key_visuals = data.get("key_visuals", [])
            if key_visuals:
                # Join key visuals into a concise description
                visual_summary = ". ".join(key_visuals)
                data["subject_details"] = visual_summary
                logger.info(f"🎨 Key visuals: {len(key_visuals)} elements")
            else:
                # Fallback to subject_details if present (for backward compatibility)
                data["subject_details"] = data.get("subject_details", "")
            
            # Extract scene-specific negatives
            if data.get("scene_negatives"):
                data["scene_negative_prompts"] = ", ".join(data["scene_negatives"])
                logger.info(f"🚫 Scene negatives: {len(data['scene_negatives'])} items")
            
            # Determine population category
            population = data.get("population", 10000)
            category = self._categorize_population(population)
            category_info = self.POPULATION_CATEGORIES[category]
            
            # Get population source verification
            pop_source = data.get("population_source", "unverified")
            
            result = {
                "population": population,
                "year": data.get("year", mid_decade),
                "category": category,
                "characteristics": category_info,
                "character": data.get("character", ""),
                "source_note": data.get("source_note", ""),
                "population_source": pop_source,
                "main_street": data.get("main_street", "downtown"),
                "street_details": data.get("street_details", ""),
                "subject_details": data.get("subject_details", ""),
                "iconic_scene": data.get("iconic_scene", "")
            }
            
            # Enhanced logging with population validation
            logger.info(f"✅ Population: {population:,} ({category_info['description']})")
            logger.info(f"📊 Source: {pop_source}")
            logger.info(f"🏘️  Scale: {category_info['buildings']}, {category_info['pedestrians']}")
            
            # Warn if population seems unrealistic for the year
            if population > 50000 and int(mid_decade) < 1920:
                logger.warning(f"⚠️  High population ({population:,}) for early period ({mid_decade}) - verify accuracy")
            
            if result.get("iconic_scene"):
                logger.info(f"🌟 Iconic scene: {result['iconic_scene']}")
            if result.get("main_street"):
                logger.info(f"📍 Location: {result['main_street']}")
            if result.get("street_details"):
                logger.info(f"📝 Details: {result['street_details']}")
            if result.get("subject_details"):
                logger.info(f"🎯 Visual details: {result['subject_details']}")
            
            return result
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response: {e}\nRaw response: {response_text}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
            
        except Exception as e:
            logger.error(f"❌ Population research failed: {e}")
            raise
    
    def _categorize_population(self, population: int) -> str:
        """
        Categorize population into size category.
        
        Args:
            population: Population number
            
        Returns:
            Category key (small_town, suburb, small_city, medium_city)
        """
        for category, info in self.POPULATION_CATEGORIES.items():
            if population <= info["max"]:
                return category
        raise ValueError(f"Population {population} exceeds all defined categories")

    def _categorize_population(self, population: int) -> str:
        """
        Categorize population into size category.
        
        Args:
            population: Population number
            
        Returns:
            Category key (small_town, suburb, small_city, medium_city)
        """
        for category, info in self.POPULATION_CATEGORIES.items():
            if population <= info["max"]:
                return category
        raise ValueError(f"Population {population} exceeds all defined categories")
    
    def get_prompt_enhancements(self, population_data: Dict[str, any]) -> Dict[str, str]:
        """
        Get prompt enhancements based on population research.
        
        Args:
            population_data: Result from research_population()
            
        Returns:
            Dictionary with prompt enhancement strings:
            {
                "street_type": str,
                "development": str,
                "density": str,
                "vehicles": str,
                "details": str
            }
        """
        characteristics = population_data.get("characteristics")
        if not characteristics:
            raise ValueError("Population data must include characteristics")
        
        return {
            "street_type": characteristics["street_type"],
            "development": characteristics["development"],
            "density": characteristics["density"],
            "vehicles": characteristics["vehicles"],
            "details": characteristics["details"]
        }
