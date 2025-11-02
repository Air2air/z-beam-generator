#!/usr/bin/env python3
"""
Preset Configurations for Hero Images

Common preset configurations for quick use.
Separate from user config for clean separation of concerns.

Author: AI Assistant
Date: October 30, 2025
"""

from regions.image.hero_image_config import HeroImageConfig


# Preset configurations for common use cases (without city, added dynamically)
# Note: Condition scale is 1=worst, 5=best
PRESET_CONFIGS = {
    "pristine_1920s": HeroImageConfig(city="", year=1925, photo_condition=5, scenery_condition=5),
    "light_1930s": HeroImageConfig(city="", year=1935, photo_condition=4, scenery_condition=4),
    "moderate_1930s": HeroImageConfig(city="", year=1935, photo_condition=3, scenery_condition=3),
    "aged_1930s": HeroImageConfig(city="", year=1935, photo_condition=2, scenery_condition=2),
    "heavily_aged_1930s": HeroImageConfig(city="", year=1935, photo_condition=1, scenery_condition=1),
    "moderate_1940s": HeroImageConfig(city="", year=1945, photo_condition=3, scenery_condition=3),
    "aged_1950s": HeroImageConfig(city="", year=1955, photo_condition=2, scenery_condition=3),
}


def get_config(city: str, preset_name: str = None, year: int = None, 
               photo_condition: int = None, scenery_condition: int = None) -> HeroImageConfig:
    """
    Get a hero image configuration.
    
    Args:
        city: City name (required)
        preset_name: Optional preset name (e.g., "aged_1930s")
        year: Optional year (used if preset_name not provided)
        photo_condition: Optional photo condition 1-5
        scenery_condition: Optional scenery condition 1-5
        
    Returns:
        HeroImageConfig instance
        
    Examples:
        # Use preset
        config = get_config(city="Belmont", preset_name="aged_1930s")
        
        # Custom configuration
        config = get_config(city="Belmont", year=1935, photo_condition=4, scenery_condition=3)
    """
    if preset_name:
        if preset_name not in PRESET_CONFIGS:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(PRESET_CONFIGS.keys())}")
        base_config = PRESET_CONFIGS[preset_name]
        return HeroImageConfig(
            city=city,
            year=base_config.year,
            photo_condition=base_config.photo_condition,
            scenery_condition=base_config.scenery_condition
        )
    
    # Defaults if not specified
    year = year or 1935
    photo_condition = photo_condition or 3
    scenery_condition = scenery_condition or 3
    
    return HeroImageConfig(
        city=city,
        year=year,
        photo_condition=photo_condition,
        scenery_condition=scenery_condition
    )
