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
    POPULATION_CATEGORIES = {
        "small_town": {
            "max": 5000,
            "description": "small town",
            "street_type": "two-lane main street",
            "development": "modest commercial district with 4-6 storefronts",
            "density": "low-density, rural character",
            "vehicles": "few automobiles",
            "details": "simple awnings, wooden facades, minimal traffic"
        },
        "suburb": {
            "max": 25000,
            "description": "suburban community",
            "street_type": "main two-lane road",
            "development": "clear row of vintage storefronts with flat awnings",
            "density": "moderate suburban development",
            "vehicles": "period automobiles parked diagonally",
            "details": "authentic urban development, residential character"
        },
        "small_city": {
            "max": 100000,
            "description": "small city",
            "street_type": "main commercial boulevard",
            "development": "dense row of two-story commercial buildings",
            "density": "urban density with commercial core",
            "vehicles": "busy street with multiple automobiles and pedestrians",
            "details": "brick buildings, prominent signage, active street life"
        },
        "medium_city": {
            "max": float('inf'),
            "description": "medium to large city",
            "street_type": "bustling downtown thoroughfare",
            "development": "tall commercial buildings, 3-4 stories, continuous storefronts",
            "density": "high urban density, city center",
            "vehicles": "heavy automobile traffic, possible streetcar tracks",
            "details": "urban architecture, dense pedestrian activity, prominent commercial district"
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
            prompt = f"""Research the historical context of {city_name}, {county_name}, California during the {decade}.

TASK: Identify the most iconic scene that captures {city_name} in the {decade}.

Provide ONLY the essential visual information needed for an image generator:

1. Population (number only, no commas)
2. Iconic scene name (short, e.g., "Ferry Building waterfront", "Main Street downtown")
3. Exact location/street name
4. 5-7 KEY VISUAL ELEMENTS as a list (each 10-15 words max):
   - Most distinctive building/landmark with architectural style
   - Typical clothing/people (be specific about styles)
   - Primary vehicles/transportation visible
   - Street/pavement characteristics
   - SPECIFIC BUSINESS NAMES with correct spelling (e.g., "Smith's Hardware Store", "Johnson's Bakery", "Martinez Theatre")
   - Atmospheric qualities (light, activity level)
   - Any unique defining features

5. 3-5 scene-specific negative prompts (things that would break authenticity)

CRITICAL FOR SIGNS: Research and provide REAL historical business names with CORRECT SPELLING. 
Use actual businesses from {decade} {city_name} if known, or create period-authentic names (owner's last name + business type).
Every business name must be spelled correctly with proper capitalization.

Format as JSON (NO commas in numbers):
{{
    "population": <number>,
    "year": "{mid_decade}",
    "iconic_scene": "<short scene name>",
    "main_street": "<street name>",
    "street_details": "<1 sentence what's happening here>",
    "key_visuals": [
        "Visual element 1",
        "Visual element 2",
        "Visual element 3",
        "Visual element 4",
        "Visual element 5"
    ],
    "scene_negatives": [
        "Modern element that breaks period",
        "Another modern element",
        "..."
    ]
}}

CRITICAL: Keep key_visuals SHORT and SPECIFIC. Focus on what makes this scene distinctive in {decade}."""

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
            
            result = {
                "population": population,
                "year": data.get("year", mid_decade),
                "category": category,
                "characteristics": self.POPULATION_CATEGORIES[category],
                "character": data.get("character", ""),
                "source_note": data.get("source_note", ""),
                "main_street": data.get("main_street", "downtown"),
                "street_details": data.get("street_details", ""),
                "subject_details": data.get("subject_details", ""),
                "iconic_scene": data.get("iconic_scene", "")
            }
            
            logger.info(f"✅ Population: {population:,} ({category})")
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
