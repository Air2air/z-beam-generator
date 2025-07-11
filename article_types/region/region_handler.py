#!/usr/bin/env python3
"""
Region Handler - Handles region-specific article generation
"""
import logging
from typing import Dict, Any, Tuple
from ..base_handler import BaseHandler

logger = logging.getLogger(__name__)

class RegionHandler(BaseHandler):
    """Handler for region-type articles"""
    
    def __init__(self):
        super().__init__("region")
    
    def prepare_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for region articles"""
        subject = context.get("subject", "unknown")
        material = context.get("material", "steel")
        
        enhanced_context = context.copy()
        enhanced_context.update({
            "region": subject,
            "region_title": subject.title(),
            "material": material,
            "material_title": material.title(),
            "article_focus": "regional_market",
            "primary_subject": subject
        })
        
        return enhanced_context
    
    def validate_context(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate context for region articles"""
        subject = context.get("subject")
        
        if not subject:
            return False, "Subject (region name) is required for region articles"
        
        return True, "Valid region context"
    
    def get_tag_config(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get tag generation configuration for region articles"""
        return {
            "max_tags": 15,
            "tag_categories": [
                "geographic_location",
                "material_industry",
                "market_business",
                "technology_process",
                "economic_geographic"
            ],
            "required_tags": ["LaserCleaning"],
            "tag_weights": {
                "geographic_location": 0.3,
                "material_industry": 0.25,
                "market_business": 0.25,
                "technology_process": 0.15,
                "economic_geographic": 0.05
            },
            "fallback_tags": [
                "GlobalMarket", "MarketAnalysis", 
                "ManufacturingHub", "IndustrialDevelopment", "RegionalTrends"
            ]
        }
    
    def get_tag_template_path(self) -> str:
        """Get tag template path for region articles"""
        return "tags/tag_region.md"
    
    def prepare_tag_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tag-specific context for region articles"""
        region = context.get("region", "unknown")
        material = context.get("material", "steel")
        
        return {
            "region": region,
            "region_title": region.title(),
            "material": material,
            "material_title": material.title(),
            "author_name": context.get("authorName", "Unknown"),
            "author_country": context.get("authorCountry", "Unknown"),
            "county_name": self._get_county_name(region),
            "city_category": self._get_city_category(region),
            "primary_industries": self._get_primary_industries(region),
            "regional_focus": "NorthernCalifornia"
        }
    
    def _get_county_name(self, city: str) -> str:
        """Get county name for cities"""
        city_to_county = {
            "fremont": "Alameda",
            "san jose": "SantaClara",
            "oakland": "Alameda"
        }
        return city_to_county.get(city.lower(), "Unknown")
    
    def _get_city_category(self, city: str) -> str:
        """Get city category"""
        return "ManufacturingHub"
    
    def _get_primary_industries(self, city: str) -> str:
        """Get primary industries for city"""
        return "AdvancedManufacturing"