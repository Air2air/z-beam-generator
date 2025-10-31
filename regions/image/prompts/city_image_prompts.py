
#!/usr/bin/env python3
"""
City Image Base Prompts

Base prompt templates for city image generation with population-adaptive characteristics.
Integrates historical population research to generate contextually accurate images.

Author: AI Assistant
Date: October 30, 2025
"""

from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from regions.hero_image_config import HeroImageConfig


def get_period_focal_characteristics(decade: str) -> str:
    """
    Get period-accurate focal depth and depth of field characteristics.
    
    Early cameras had different optical characteristics than modern cameras:
    - Large format cameras (common 1900s-1940s) had shallow DOF at wide apertures
    - Box cameras had deep DOF (everything in focus)
    - View cameras allowed tilt/shift for selective focus
    - Film sensitivity required different apertures in different lighting
    
    Args:
        decade: Decade string (e.g., "1920s")
        
    Returns:
        Description of period-accurate focal characteristics
    """
    year = int(decade.replace("s", ""))
    
    if year <= 1920:
        # Early period: mix of box cameras (deep DOF) and large format (shallow DOF capable)
        return (
            "Period-accurate focal depth: sharp focus on main subject with natural falloff to background, "
            "typical of large format cameras with moderate aperture. "
            "Foreground and background show gradual softness, not modern bokeh. "
            "Overall depth of field deeper than modern cameras due to larger format and typical f/8-f/16 apertures."
        )
    elif year <= 1940:
        # 1920s-1940s: Professional large format common, amateur box cameras
        return (
            "Period-accurate focal depth: primary subject in sharp focus with gentle transition to softer background, "
            "characteristic of {decade} large format press cameras at working apertures (f/8-f/11). "
            "Mid-ground moderately sharp, distant elements progressively softer. "
            "No extreme shallow depth of field or modern lens effects."
        )
    else:
        # 1940s+: Mix of formats, more 35mm adoption
        return (
            "Period-accurate focal depth: subject and immediate surroundings in sharp focus, "
            "background with natural softness typical of {decade} press and field cameras. "
            "Moderate depth of field reflecting typical working apertures. "
            "Natural lens characteristics without modern optical corrections."
        )



def get_historical_base_prompt(
    city_name: str, 
    county_name: str, 
    decade: str,
    population_data: Optional[Dict] = None,
    config: Optional["HeroImageConfig"] = None,
    subject: Optional[str] = None
) -> str:
    """
    Get base historical prompt for a city with population-based adaptations.
    
    Args:
        city_name: Name of the city
        county_name: Name of the county
        decade: Historical decade (e.g., "1920s", "1930s")
        population_data: Optional population research data with characteristics
        config: Optional HeroImageConfig for aging/condition control
        subject: Optional specific subject to focus on (e.g., "harbor", "barber shop", "train station")
        
    Returns:
        Base prompt string for historical image
    """
    # Get aging/condition text from config or use defaults
    if config:
        from regions.image.aging_levels import get_photo_aging_text, get_scenery_condition_text
        photo_aging = get_photo_aging_text(config.photo_condition)
        scenery_condition = get_scenery_condition_text(config.scenery_condition)
        actual_decade = config.get_decade()
    else:
        photo_aging = (
            "The photograph shows significant aging: noticeable yellowing with brown toning, "
            "visible scratches and creases, water spots, corner wear, faded contrast."
        )
        scenery_condition = (
            "Buildings and street show moderate wear: weathered wooden facades, somewhat faded paint, "
            "worn awnings, aged signage, visible cracks in pavement, period patina."
        )
        actual_decade = decade
    
    # Research data is required - fail if not provided
    if population_data is None:
        raise ValueError("Population research data is required for image generation")
    
    # Extract research details
    subject_research = population_data.get("subject_details", "")
    street_name = population_data.get("main_street", "")
    street_details = population_data.get("street_details", "")
    street_context = f" Location: {street_name}. {street_details}" if street_details else (f" on {street_name}" if street_name else "")
    
    # Extract iconic scene from research
    iconic_scene = population_data.get("iconic_scene", "")
    
    # Determine effective subject and build context with research
    subject_context = ""
    effective_subject = subject  # Track what subject we're actually using
    
    if subject:
        # User specified subject - must have research
        if not subject_research:
            raise ValueError(f"Research failed to provide details for subject: {subject}")
        subject_context = f" Focus on the {subject}. {subject_research}"
    elif iconic_scene:
        # No explicit subject - use researched iconic scene
        if not subject_research:
            raise ValueError(f"Research failed to provide details for iconic scene: {iconic_scene}")
        subject_context = f" Focus on {iconic_scene}. {subject_research}"
        effective_subject = iconic_scene  # Treat iconic scene as the subject
    else:
        raise ValueError("Research must provide either subject_details or iconic_scene")
    
    # Scene type from effective subject
    scene_type = f"{effective_subject} scene"
    
    # Get period-accurate focal characteristics
    focal_depth = get_period_focal_characteristics(actual_decade)
    
    # Build prompt with research-based details (county removed)
    return (
        f"Authentic {actual_decade} silver gelatin print on fiber-based paper, "
        f"low-resolution period photograph, full frame. "
        f"California {scene_type} in {city_name}.{street_context} "
        f"{subject_context} "
        f"Long exposure motion blur typical of period cameras: moving elements show slight blur and ghosting, static elements remain sharp. "
        f"{focal_depth} "
        f"All visible text must be correctly spelled with authentic {actual_decade} typography. "
        f"{scenery_condition} "
        f"{photo_aging}"
    )
