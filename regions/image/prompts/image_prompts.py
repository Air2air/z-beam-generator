#!/usr/bin/env python3
"""
Region Image Prompt Generator

Generates Gemini-optimized image prompts for regions, counties, and cities.
Creates two prompts per entry: historical photo + business photo.

Each prompt is carefully crafted to produce authentic, contextual images:
- Historical: Period-appropriate architecture, landmarks, and scenes
- Business: Modern laser cleaning operations in local industrial settings

Author: AI Assistant
Date: October 30, 2025
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class RegionImagePromptGenerator:
    """
    Generate historical + business image prompts for regions and cities.
    
    Produces Gemini Imagen-optimized prompts that incorporate:
    - City/regional landmarks and architectural styles
    - Local industries and applications
    - Historical periods and cultural elements
    - Professional photography terminology
    
    Example:
        generator = RegionImagePromptGenerator()
        prompts = generator.generate_prompts(
            "Belmont",
            city_data,
            entry_type="city"
        )
        # Returns: {"historical": "...", "business": "..."}
    """
    
    def __init__(self, gemini_client=None):
        """
        Initialize generator.
        
        Args:
            gemini_client: Optional GeminiImageClient for direct image generation
        """
        self.gemini_client = gemini_client
    
    def generate_prompts(
        self,
        region_name: str,
        region_data: Dict[str, Any],
        entry_type: str = "region"
    ) -> Dict[str, str]:
        """
        Generate historical + business image prompts.
        
        Args:
            region_name: Name of region or city
            region_data: Data dictionary from regions/data.yaml
            entry_type: Type of entry (city or region)
            
        Returns:
            Dictionary with "historical" and "business" prompt strings
        """
        if entry_type == "city":
            return self._generate_city_prompts(region_name, region_data)
        else:
            return self._generate_region_prompts(region_name, region_data)
    
    def _generate_region_prompts(
        self,
        region_name: str,
        region_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate prompts for broad regions (North America, Europe, etc.)"""
        
        # Extract data
        industries = region_data.get("key_industries", [])
        applications = region_data.get("common_applications", [])
        countries = region_data.get("countries", [])
        
        # Choose representative country for context
        country_context = countries[0] if countries else region_name
        
        # Historical prompt (generic industrial era)
        historical = (
            f"Historical black and white photograph from 1950s industrial {country_context}. "
            f"Shows manufacturing facility with vintage machinery and equipment. "
            f"Mid-century industrial architecture with steel beams and large windows. "
            f"Workers in period-appropriate clothing operating machinery. "
            f"Documentary style photography, high contrast, archival quality. "
            f"Industrial heritage, vintage manufacturing era, authentic period details."
        )
        
        # Business prompt (modern laser cleaning)
        business_industry = industries[0] if industries else "manufacturing"
        business_app = applications[0] if applications else "industrial cleaning"
        
        business = (
            f"Professional photograph of modern {business_industry} facility in {country_context}. "
            f"Worker using advanced fiber laser cleaning system for {business_app}. "
            f"Shows precision industrial cleaning process on metal components. "
            f"Contemporary workplace with safety equipment, protective eyewear, and PPE. "
            f"Clean professional lighting, industrial setting with modern equipment. "
            f"4K HDR professional photography, workplace safety standards visible."
        )
        
        return {
            "historical": historical,
            "business": business
        }
    
    def _generate_city_prompts(
        self,
        city_name: str,
        parent_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate city-specific prompts with population research"""
        from regions.image.prompts.city_image_prompts import get_historical_base_prompt
        from regions.image.prompts.researcher import PopulationResearcher
        
        county_name = parent_data.get("name", "California")
        decade = self._get_historical_decade(county_name)
        
        # Research historical population to inform prompt generation
        population_data = None
        try:
            researcher = PopulationResearcher()
            population_data = researcher.research_population(city_name, county_name, decade)
            
            pop = population_data.get("population", 0)
            category = population_data.get("category", "suburb")
            logger.info(f"📊 {city_name}: {pop:,} population in {decade} ({category})")
            
        except Exception as e:
            logger.warning(f"⚠️  Population research failed for {city_name}, using defaults: {e}")
        
        # Use historical prompt from city_image_prompts.py with population data
        historical = get_historical_base_prompt(city_name, county_name, decade, population_data)
        
        return {
            "historical": historical,
            "business": None  # No business prompt for cities
        }
    
    def get_negative_prompts(self, entry_type: str = "city") -> Dict[str, str]:
        """
        Get negative prompts for quality control.
        
        Args:
            entry_type: Type of entry (city or region)
            
        Returns:
            Dictionary with "historical" and "business" negative prompts
        """
        historical_negative = (
            "text, words, letters, signs with text, readable text, distorted faces, "
            "modern elements, anachronistic details, blurry, digital artifacts, "
            "color, colored photograph, multiple images, collage, split image, triptych, "
            "diptych, grid layout, photo series, pristine condition, clean photograph, "
            "modern photo quality, sharp edges, perfect preservation"
        )
        
        business_negative = (
            "text, words, letters, labels, readable text on equipment, gibberish text, "
            "distorted faces, unsafe conditions, blurry, low quality, artifacts, "
            "multiple images, collage, split image, grid layout"
        )
        
        return {
            "historical": historical_negative,
            "business": business_negative if entry_type == "region" else None
        }
    
    def get_generation_params(self, entry_type: str = "city") -> Dict[str, Dict[str, Any]]:
        """
        Get generation parameters for image quality.
        
        Args:
            entry_type: Type of entry (city or region)
            
        Returns:
            Dictionary with "historical" and "business" generation parameters
        """
        historical_params = {
            "aspect_ratio": "4:3",
            "guidance_scale": 12.0,
            "safety_filter_level": "block_few"
        }
        
        business_params = {
            "aspect_ratio": "16:9",
            "guidance_scale": 12.0,
            "safety_filter_level": "block_some"
        }
        
        return {
            "historical": historical_params,
            "business": business_params if entry_type == "region" else None
        }
    
    def _get_historical_decade(self, county_name: str) -> str:
        """
        Determine appropriate historical decade based on county.
        
        Returns period when county had peak historical significance.
        """
        # Default to 1930s for all counties
        return "1930s"
    
    def _get_industry_application(self, industry: str) -> str:
        """
        Map industry to specific laser cleaning application.
        
        Returns appropriate application context for the industry.
        """
        industry_lower = industry.lower()
        
        applications = {
            "technology": "electronic component cleaning",
            "semiconductor": "wafer surface preparation",
            "biotechnology": "medical device sterilization",
            "aerospace": "aircraft component restoration",
            "automotive": "automotive part cleaning",
            "oil refining": "pipeline maintenance",
            "chemical": "equipment decontamination",
            "food processing": "food equipment sanitization",
            "wine production": "barrel and tank cleaning",
            "marine": "vessel hull maintenance",
            "electronics": "PCB cleaning and preparation",
            "medical": "surgical instrument cleaning",
        }
        
        for key, app in applications.items():
            if key in industry_lower:
                return app
        
        return "industrial component cleaning"
    
    def generate_and_save(
        self,
        region_name: str,
        region_data: Dict[str, Any],
        output_dir: Optional[Path] = None,
        entry_type: str = "region"
    ) -> Dict[str, Any]:
        """
        Generate prompts AND images, save to public/images/regions directory.
        
        Requires gemini_client to be initialized.
        
        Args:
            region_name: Name of region or city
            region_data: Region data dictionary
            output_dir: Optional output directory (defaults to public/images/regions)
            entry_type: Type of entry (city or region)
            
        Returns:
            Dictionary with paths and web URLs:
            {
                "historical": {"path": Path, "url": "/images/regions/..."},
                "business": {"path": Path, "url": "/images/regions/..."}
            }
            
        Raises:
            ValueError: If gemini_client not initialized
        """
        if not self.gemini_client:
            raise ValueError(
                "gemini_client required for image generation. "
                "Initialize with: RegionImagePromptGenerator(gemini_client)"
            )
        
        # Generate prompts
        prompts = self.generate_prompts(region_name, region_data, entry_type)
        
        # Use public directory for web serving if not specified
        if output_dir is None:
            output_dir = Path("public/images/regions")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate safe filename
        safe_name = region_name.lower().replace(" ", "_").replace(",", "").replace("(", "").replace(")", "")
        
        historical_path = output_dir / f"{safe_name}_historical.png"
        business_path = output_dir / f"{safe_name}_business.png"
        
        print(f"\n🎨 Generating images for: {region_name}")
        print(f"📁 Output directory: {output_dir}")
        
        # Historical image (4:3 classic photo ratio)
        print(f"\n📸 Historical image...")
        self.gemini_client.generate_image(
            prompts["historical"],
            output_path=historical_path,
            aspect_ratio="4:3"
        )
        
        # Business image (16:9 modern wide format)
        print(f"\n📸 Business image...")
        self.gemini_client.generate_image(
            prompts["business"],
            output_path=business_path,
            aspect_ratio="16:9"
        )
        
        print(f"\n✅ Generated images saved to: {output_dir}")
        
        # Generate web URLs (relative to public directory)
        historical_url = f"/images/regions/{safe_name}_historical.png"
        business_url = f"/images/regions/{safe_name}_business.png"
        
        return {
            "historical": {
                "path": historical_path,
                "url": historical_url,
                "prompt": prompts["historical"]
            },
            "business": {
                "path": business_path,
                "url": business_url,
                "prompt": prompts["business"]
            }
        }
    
    def generate_batch(
        self,
        entries: List[Dict[str, Any]],
        output_base_dir: Path,
        generate_images: bool = False
    ) -> Dict[str, Dict[str, str]]:
        """
        Generate prompts for multiple entries in batch.
        
        Args:
            entries: List of entry dictionaries with 'name', 'data', 'type'
            output_base_dir: Base directory for outputs
            generate_images: Whether to generate actual images
            
        Returns:
            Dictionary mapping entry names to their prompts
        """
        results = {}
        
        for entry in entries:
            name = entry["name"]
            data = entry["data"]
            entry_type = entry.get("type", "region")
            
            print(f"\n📝 Processing: {name} ({entry_type})")
            
            # Generate prompts
            prompts = self.generate_prompts(name, data, entry_type)
            results[name] = prompts
            
            # Optionally generate images
            if generate_images and self.gemini_client:
                safe_name = name.lower().replace(" ", "_").replace(",", "")
                output_dir = output_base_dir / safe_name
                self.generate_and_save(name, data, output_dir, entry_type)
        
        return results
