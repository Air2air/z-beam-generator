
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
    from regions.image.hero_image_config import HeroImageConfig


def get_period_focal_characteristics(decade: str) -> str:
    """
    Get concise period-accurate focal depth characteristics.
    
    Args:
        decade: Decade string (e.g., "1920s")
        
    Returns:
        Description of period-accurate focal characteristics
    """
    year = int(decade.replace("s", ""))
    
    if year <= 1920:
        return f"{decade} large format camera: sharp focus on subject, natural falloff to background, deep DOF (f/8-f/16), no modern bokeh."
    elif year <= 1940:
        return f"{decade} press camera: sharp subject, gentle transition to softer background (f/8-f/11), moderate DOF, no modern lens effects."
    else:
        return f"{decade} camera: sharp subject and surroundings, natural background softness, moderate DOF, period lens characteristics."



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
    
    # Extract population characteristics to constrain scale
    characteristics = population_data.get("characteristics", {})
    scale_constraint = ""
    if characteristics:
        scale_constraint = (
            f" SCALE REQUIREMENTS (population {population_data.get('population', 0):,}): "
            f"{characteristics.get('buildings', '')}, "
            f"{characteristics.get('pedestrians', '')}, "
            f"{characteristics.get('street_width', '')}. "
            f"{characteristics.get('density', '')}. "
        )
    
    # Extract iconic scene from research
    iconic_scene = population_data.get("iconic_scene", "")
    
    # Determine subject and build context with research
    subject_context = ""
    
    if subject:
        # User specified subject - must have research
        if not subject_research:
            raise ValueError(f"Research failed to provide details for subject: {subject}")
        subject_context = f" {subject_research}"
        scene_type = f"{subject}, {city_name}"
    elif iconic_scene:
        # No explicit subject - use researched iconic scene
        if not subject_research:
            raise ValueError(f"Research failed to provide details for iconic scene: {iconic_scene}")
        subject_context = f" {subject_research}"
        # If iconic scene is long/complex, just use city name
        if len(iconic_scene) > 40:
            scene_type = f"{city_name}"
        else:
            scene_type = f"{iconic_scene}, {city_name}"
    else:
        raise ValueError("Research must provide either subject_details or iconic_scene")
    
    # Get period-accurate focal characteristics
    focal_depth = get_period_focal_characteristics(actual_decade)
    
    # Build prompt with research-based details (county removed)
    # Structure: Medium → Scene → Scale → Research → Trees → Camera Tech → Aging (CRITICAL)
    return (
        f"Authentic {actual_decade} silver gelatin print on fiber-based paper, "
        f"low-resolution period photograph, full frame. "
        f"{scene_type}.{street_context} "
        f"{scale_constraint}"
        f"{subject_context} "
        f"Period-appropriate trees visible: mature shade trees lining streets (oak, elm, sycamore typical for California), "
        f"some bare branches if winter, full foliage if summer, natural growth patterns, not perfectly manicured.\n\n"  # Add trees and line break
        f"CAMERA: Period camera motion blur: slight blur on moving subjects, static elements sharp. "
        f"{focal_depth} "
        f"CRITICAL REQUIREMENT - ALL VISIBLE TEXT MUST BE PERFECTLY SPELLED: Every sign, storefront, advertisement, banner, "
        f"poster, and any readable text MUST use correct English spelling with authentic {actual_decade} typography. "
        f"No misspellings, no gibberish, no AI-garbled text, no corrupted letters. Every word must be a real word spelled correctly. "
        f"CRITICAL REQUIREMENT - ALL HUMAN FACES MUST BE ANATOMICALLY CORRECT: Every person must have normal human facial features. "
        f"Two eyes properly positioned, one nose, one mouth in correct location, properly proportioned face, normal human anatomy. "
        f"No distorted faces, no extra or missing features, no merged faces, no malformed heads, no wrong number of eyes or mouths. "
        f"All facial features must be in correct positions and properly formed. Every person must look like a real human being. "
        f"{scenery_condition}\n\n"  # Add line break before aging
        f"PHOTOGRAPH AGING: {photo_aging}"  # Make aging prominent with label
    )
