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
PHOTO_AGING_LEVELS: Dict[int, str] = {
    1: (
        "The photograph is severely aged and heavily deteriorated: extreme yellowing with deep brown and sepia toning, "
        "pervasive dust and grime accumulation, extensive deep scratches and prominent creases throughout, "
        "widespread emulsion cracks with visible peeling and flaking, severe water damage with dark stains, "
        "mold spots and discoloration patterns, heavily bent corners with tears and missing pieces, "
        "multiple tape residue marks and adhesive stains, prominent fingerprint smudges and handling marks, "
        "severely faded contrast with completely bleached highlights and muddy shadows, "
        "surface degradation with visible grain structure breakdown, overall heavily weathered appearance "
        "characteristic of a photograph stored in extremely poor conditions for many decades, "
        "significant loss of detail and sharpness throughout."
    ),
    2: (
        "The photograph shows heavy aging and substantial deterioration: deep yellowing with pronounced brown toning, "
        "thick dust accumulation and surface grime, numerous deep scratches and prominent creases, "
        "extensive emulsion cracks with visible peeling in multiple areas, pronounced water damage with "
        "dark staining patterns and water spots, severe corner wear with bending and minor tears, "
        "visible tape residue and adhesive marks, multiple fingerprint smudges, heavily faded contrast "
        "with bleached highlights and weak shadows, noticeable surface degradation, "
        "overall heavily weathered with significant detail loss."
    ),
    3: (
        "The photograph shows substantial aging and noticeable deterioration: strong yellowing with brown toning throughout, "
        "dust accumulation and surface dirt, many visible scratches and multiple creases, water staining and spots, "
        "visible emulsion cracks, pronounced corner wear and bending, tape marks or adhesive residue, "
        "fingerprint smudges, significantly faded contrast with bleached areas, surface wear and degradation, "
        "overall aged appearance with moderate detail loss."
    ),
    4: (
        "The photograph shows light aging: moderate yellowing, minor scratches and spots, "
        "some edge wear, slight fading but overall well-preserved."
    ),
    5: (
        "The photograph is in excellent condition with minimal aging. "
        "Slight yellowing, very faint scratches, well-preserved with good contrast."
    )
}


# Scenery/building condition descriptions (1=worst, 5=best)
SCENERY_CONDITION_LEVELS: Dict[int, str] = {
    1: (
        "Buildings and street are severely deteriorated and heavily weathered: weathered wooden facades with "
        "extensive peeling and flaking paint revealing multiple layers and bare wood beneath, "
        "heavily torn and tattered awnings with holes and frayed edges hanging loosely, "
        "badly weathered signage with severe paint loss and barely legible lettering, "
        "storefronts with extensively faded and peeling paint and visible wood rot, "
        "deeply worn and splintered wood siding with warping and gaps, heavily weathered brick with "
        "crumbling mortar and missing pieces, vintage architectural details showing severe wear and damage, "
        "extensively cracked and broken pavement with potholes and missing chunks, exposed underlayers, "
        "visible street surface decay with significant deterioration, heavy authentic period weathering "
        "showing decades of neglect and harsh conditions."
    ),
    2: (
        "Buildings and street show heavy deterioration and substantial wear: weathered wooden facades with "
        "extensive peeling paint exposing bare wood in multiple areas, heavily worn and torn awnings with "
        "significant fading and fraying, aged signage with heavy paint loss and fading, "
        "storefronts with substantially faded and peeling paint, badly worn wood siding with visible damage, "
        "heavily weathered brick with deteriorating mortar and surface damage, vintage details showing heavy wear, "
        "severely cracked pavement with deep fissures and broken areas, pronounced street surface decay, "
        "heavy authentic period weathering throughout."
    ),
    3: (
        "Buildings and street show substantial wear and noticeable deterioration: weathered wooden facades with "
        "widespread peeling paint, worn and faded awnings with tears and damage, aged signage with significant "
        "paint loss and weathering, storefronts with noticeably faded and peeling paint, worn wood siding with "
        "visible weathering and damage, weathered brick with worn mortar and surface wear, "
        "architectural details showing heavy use and age, extensively cracked pavement with visible damage, "
        "street surface showing clear decay, substantial authentic period weathering and patina."
    ),
    4: (
        "Buildings and street show light wear: slightly faded paint, minor weathering, "
        "awnings with some age, generally well-maintained appearance, minor street wear."
    ),
    5: (
        "Buildings and street are in pristine condition: fresh paint, clean facades, "
        "new awnings, well-maintained storefronts, smooth pavement."
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
