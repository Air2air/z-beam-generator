#!/usr/bin/env python3
"""
City Image Generator

Focused generator for city historical images with population-adaptive prompting.
Clean, simple, purpose-built for Bay Area city image generation.

Author: AI Assistant
Date: October 30, 2025
"""

import logging
from typing import Dict, Any, Optional

from regions.image.prompts.city_image_prompts import get_historical_base_prompt
from regions.image.prompts.population_researcher import PopulationResearcher
from regions.image.negative_prompts import get_default_negative_prompt, get_era_specific_additions

logger = logging.getLogger(__name__)


class CityImageGenerator:
    """
    Lightweight generator for city historical images.
    
    Automatically researches historical population and generates
    contextually appropriate image prompts.
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize city image generator.
        
        Args:
            gemini_api_key: Optional Gemini API key for population research
        """
        self.researcher = None
        if gemini_api_key:
            try:
                self.researcher = PopulationResearcher(api_key=gemini_api_key)
                logger.info("✅ Population research enabled")
            except Exception as e:
                logger.warning(f"⚠️  Population research disabled: {e}")
    
    def generate_prompt(
        self,
        city_name: str,
        county_name: str,
        decade: str = "1930s",
        config = None,
        subject: Optional[str] = None
    ) -> str:
        """
        Generate historical image prompt for a city.
        
        Args:
            city_name: Name of the city
            county_name: Name of the county
            decade: Historical decade (default: "1930s")
            config: Optional HeroImageConfig for aging/condition control
            subject: Optional specific subject to focus on (e.g., "harbor", "barber shop")
            
        Returns:
            Image prompt string optimized for Imagen 4
        """
        # Validate subject parameter
        if subject and not subject.strip():
            logger.warning("⚠️  Empty subject string provided, treating as None")
            subject = None
        
        population_data = None
        
        # Research population if researcher available
        if self.researcher:
            try:
                population_data = self.researcher.research_population(
                    city_name, county_name, decade, subject
                )
                pop = population_data.get("population", 0)
                category = population_data.get("category", "suburb")
                logger.info(f"📊 {city_name}: {pop:,} population in {decade} ({category})")
            except Exception as e:
                logger.warning(f"⚠️  Population research failed, using defaults: {e}")
        
        # Generate prompt with population context, config, and subject
        prompt = get_historical_base_prompt(city_name, county_name, decade, population_data, config, subject)
        
        return prompt
    
    def get_negative_prompt(self, decade: str = "1930s", subject: Optional[str] = None) -> str:
        """
        Get comprehensive negative prompt for historical image accuracy.
        
        Includes:
        - Historical accuracy (no anachronisms)
        - Text/spelling accuracy
        - Photo quality control
        - Composition control
        - Era-specific exclusions
        - Subject-specific exclusions
        
        Args:
            decade: Historical decade for era-specific exclusions
            subject: Optional subject to add subject-specific exclusions
        
        Returns:
            Comprehensive negative prompt string
        """
        # Get comprehensive base negative prompt
        base_negative = get_default_negative_prompt()
        
        # Add era-specific exclusions
        era_additions = get_era_specific_additions(decade)
        if era_additions:
            base_negative += ", " + ", ".join(era_additions)
        
        # Add subject-specific exclusions
        if subject:
            if any(word in subject.lower() for word in ["harbor", "port", "dock", "waterfront"]):
                base_negative += ", retail storefronts, shopping areas, commercial storefronts, street vendors, sidewalk cafes, residential buildings in foreground, landlocked scene, no water visible, desert landscape, mountains without water"
            elif any(word in subject.lower() for word in ["factory", "mill", "plant", "cannery"]):
                base_negative += ", retail storefronts, residential houses, clean corporate offices, shopping areas, entertainment venues"
        
        return base_negative
    
    def get_generation_params(self) -> Dict[str, Any]:
        """
        Get generation parameters for Imagen 4.
        
        Returns:
            Dictionary with aspect_ratio, guidance_scale, safety_filter_level
        """
        return {
            "aspect_ratio": "16:9",
            "guidance_scale": 12.0,
            "safety_filter_level": "block_few"
        }
    
    def generate_complete(
        self,
        city_name: str,
        county_name: str,
        decade: str = "1930s",
        config = None,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete prompt package for image generation.
        
        Args:
            city_name: Name of the city
            county_name: Name of the county
            decade: Historical decade (default: "1930s")
            config: Optional HeroImageConfig for aging/condition control
            subject: Optional specific subject to focus on (e.g., "harbor", "barber shop")
            
        Returns:
            Dictionary with prompt, negative_prompt, and generation_params:
            {
                "prompt": str,
                "negative_prompt": str,
                "aspect_ratio": str,
                "guidance_scale": float,
                "safety_filter_level": str
            }
        """
        prompt = self.generate_prompt(city_name, county_name, decade, config, subject)
        negative_prompt = self.get_negative_prompt(decade, subject)
        params = self.get_generation_params()
        
        return {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            **params
        }
