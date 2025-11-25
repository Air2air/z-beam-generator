#!/usr/bin/env python3
"""
Region Hero Image Configuration

User-defined configuration for manual control of hero image generation.
Defines year, photo condition, and scenery condition.

Author: AI Assistant
Date: October 30, 2025
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class HeroImageConfig:
    """
    Configuration for hero image generation.
    
    User-controlled parameters for fine-tuning image aesthetics.
    
    Condition Scale (1=worst, 5=best):
        1 = Heavily aged/deteriorated
        2 = Heavy aging/wear
        3 = Moderate aging/wear
        4 = Light aging/wear
        5 = Excellent/pristine condition
    """
    city: str
    year: int
    photo_condition: int  # 1-5 (1=heavily aged, 5=pristine)
    scenery_condition: int  # 1-5 (1=heavily worn, 5=pristine)
    
    def __post_init__(self):
        """Validate configuration values"""
        if not 1800 <= self.year <= 2025:
            raise ValueError(f"Year must be between 1800-2025, got {self.year}")
        if not 1 <= self.photo_condition <= 5:
            raise ValueError(f"Photo condition must be 1-5, got {self.photo_condition}")
        if not 1 <= self.scenery_condition <= 5:
            raise ValueError(f"Scenery condition must be 1-5, got {self.scenery_condition}")
    
    def get_decade(self) -> str:
        """Get decade string from year (e.g., 1935 -> '1930s')"""
        decade_base = (self.year // 10) * 10
        return f"{decade_base}s"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        from regions.image.aging_levels import get_photo_aging_text, get_scenery_condition_text
        
        return {
            "city": self.city,
            "year": self.year,
            "decade": self.get_decade(),
            "photo_condition": self.photo_condition,
            "scenery_condition": self.scenery_condition,
            "photo_aging_text": get_photo_aging_text(self.photo_condition),
            "scenery_condition_text": get_scenery_condition_text(self.scenery_condition)
        }
