#!/usr/bin/env python3
"""
Aging Levels and Condition Descriptions

Defines the visual characteristics for different levels of photo aging
and scenery/building condition.

Author: AI Assistant
Date: October 30, 2025
"""

from typing import Dict


# Photo aging level descriptions (1=worst, 5=best)
# Concise keyword-focused descriptions for efficient prompt generation
PHOTO_AGING_LEVELS: Dict[int, str] = {
    1: (
        "Severely aged photograph: extreme yellowing with deep brown sepia toning, pervasive dust and grime, "
        "extensive deep scratches and creases, widespread emulsion cracks with peeling and flaking, "
        "severe water damage with dark stains and mold spots, heavily bent corners with tears and missing pieces, "
        "tape residue and adhesive marks, prominent fingerprint smudges, severely faded contrast with bleached highlights. "
        "Significant focus degradation with overall softness and blur throughout image, loss of sharpness in all areas, "
        "emulsion deterioration causing blurred edges and indistinct details, optical clarity severely compromised."
    ),
    2: (
        "Heavy aging: deep yellowing with brown toning, thick dust and surface grime, numerous deep scratches and creases, "
        "extensive emulsion cracks with peeling, water damage with dark stains and spots, severe corner wear with bending and tears, "
        "tape residue and adhesive marks, fingerprint smudges, heavily faded contrast. "
        "Noticeable focus problems with soft blurred areas, reduced sharpness and clarity, emulsion damage causing fuzzy indistinct regions."
    ),
    3: (
        "Moderate aging: strong yellowing with brown toning, dust accumulation, many scratches and creases, "
        "water stains and spots, visible emulsion cracks, corner wear and bending, tape marks, "
        "fingerprint smudges, faded contrast with bleached areas. Some loss of sharpness with slight overall softness."
    ),
    4: (
        "Light aging: moderate yellowing, minor scratches and spots, some edge wear, slight fading, overall well-preserved with good sharpness."
    ),
    5: (
        "Minimal aging: slight yellowing, very faint scratches, well-preserved with good contrast and sharp focus."
    )
}


# Scenery/building condition descriptions (1=worst, 5=best)
# Concise keyword-focused descriptions for efficient prompt generation
SCENERY_CONDITION_LEVELS: Dict[int, str] = {
    1: (
        "Severe deterioration: wooden facades with extensive peeling paint exposing bare wood, torn tattered awnings with holes, "
        "badly weathered signage with severe paint loss, faded storefronts with wood rot, deeply worn splintered siding, "
        "heavily weathered brick with crumbling mortar, extensively cracked pavement with potholes and missing chunks."
    ),
    2: (
        "Heavy wear: wooden facades with extensive peeling paint, heavily worn torn awnings, aged signage with heavy paint loss, "
        "faded peeling storefronts, badly worn wood siding, weathered brick with deteriorating mortar, severely cracked pavement with fissures."
    ),
    3: (
        "Moderate wear: weathered facades with peeling paint, worn faded awnings with tears, aged signage with paint loss, "
        "faded storefronts, worn wood siding, weathered brick with worn mortar, extensively cracked pavement."
    ),
    4: (
        "Light wear: slightly faded paint, minor weathering, awnings with some age, generally well-maintained, minor street wear."
    ),
    5: (
        "Pristine condition: fresh paint, clean facades, new awnings, well-maintained storefronts, smooth pavement."
    )
}


def get_photo_aging_text(condition_level: int) -> str:
    """
    Get photo aging description based on condition level.
    
    Args:
        condition_level: Integer 1-5
        
    Returns:
        Description of photograph aging effects
    """
    return PHOTO_AGING_LEVELS.get(condition_level, PHOTO_AGING_LEVELS[3])


def get_scenery_condition_text(condition_level: int) -> str:
    """
    Get scenery/building condition description based on level.
    
    Args:
        condition_level: Integer 1-5
        
    Returns:
        Description of building and street wear
    """
    return SCENERY_CONDITION_LEVELS.get(condition_level, SCENERY_CONDITION_LEVELS[3])
