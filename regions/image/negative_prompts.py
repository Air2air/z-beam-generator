#!/usr/bin/env python3
"""
Negative Prompts for Historical Image Generation

Comprehensive negative prompts to ensure:
1. Historical accuracy (no anachronisms)
2. Photo quality control (avoid modern perfection)
3. Text/spelling accuracy (proper rendering)
4. Composition control (avoid unwanted layouts)

Based on research of Imagen 4 best practices for historical photography.

Author: AI Assistant
Date: October 31, 2025
"""

from typing import List


# Core accuracy and quality control
ACCURACY_NEGATIVE_PROMPTS = [
    # Modern anachronisms
    "modern elements",
    "contemporary architecture",
    "modern cars",
    "modern vehicles",
    "modern clothing",
    "modern fashion",
    "modern technology",
    "smartphones",
    "computers",
    "LED lights",
    "solar panels",
    "satellite dishes",
    "modern signage",
    "modern street furniture",
    "traffic lights with digital displays",
    "modern crosswalks",
    "bike lanes with modern markings",
    "modern parking meters",
    "modern traffic cones",
    "plastic barriers",
    "modern construction equipment",
    "modern building materials",
    "aluminum siding",
    "vinyl siding",
    "modern windows",
    "double-pane windows",
    "tinted glass",
    "reflective glass",
    "modern storefronts",
    "LED signs",
    "neon signs", # Unless specifically period-appropriate
    "modern awnings",
    "modern street lights",
    "modern utility poles",
    "overhead power lines that look modern",
    
    # Anachronistic vehicles
    "cars from wrong era",
    "vehicles from wrong decade",
    "modern car designs",
    "SUVs",
    "minivans",
    "modern sedans",
    "electric cars",
    "hybrid vehicles",
    "modern trucks",
    "modern buses",
    "modern bicycles",
    "mountain bikes",
    "modern motorcycles",
]


# Text and signage accuracy
TEXT_ACCURACY_NEGATIVE_PROMPTS = [
    # Core spelling issues
    "misspelled words",
    "spelling errors",
    "gibberish text",
    "nonsense words",
    "backwards text",
    "made-up words",
    
    # Letter formation
    "malformed letters",
    "broken letters",
    "incomplete letters",
    "distorted letters",
    
    # Modern signage
    "modern fonts",
    "LED signage",
    "digital displays",
    "QR codes",
    
    # AI failures
    "AI-garbled text",
    "corrupted signage text",
    "placeholder text",
]


# Photo quality issues
PHOTO_QUALITY_NEGATIVE_PROMPTS = [
    # Too modern/perfect
    "pristine condition",
    "perfect preservation",
    "clean photograph",
    "modern photo quality",
    "sharp modern edges",
    "digital clarity",
    "high resolution clarity",
    "modern camera quality",
    "DSLR quality",
    "digital photography",
    "HDR photography",
    "perfect focus throughout",
    "no grain",
    "overly sharp",
    "artificial sharpness",
    
    # Wrong color/format - MUST BE BLACK AND WHITE
    "color photograph",
    "full color",
    "colorized",
    "saturated colors",
    "color tinting",
    "chromatic",
    
    # Physical issues to avoid
    "tears in wrong places",
    "damage that obscures main subject",
    "water damage that ruins image",
    "mold that covers important areas",
    "extreme deterioration that loses detail",
    "completely faded",
    "totally washed out",
    "image falling apart",
    "photograph in pieces",
]


# Composition and layout issues
COMPOSITION_NEGATIVE_PROMPTS = [
    # Multiple images
    "multiple images",
    "collage",
    "split image",
    "divided image",
    "triptych",
    "diptych",
    "grid layout",
    "photo series",
    "multiple panels",
    "side by side images",
    "before and after",
    "comparison images",
    "montage",
    "photo album layout",
    "scrapbook layout",
    
    # Framing issues
    "borders within borders",
    "double framing",
    "picture frames in the image",
    "photos within photos",
    "nested images",
    "image of a photograph",
    "meta photography",
    "photograph of a photograph",
    
    # Perspective issues
    "distorted perspective that looks wrong",
    "impossible angles",
    "unnatural viewpoint",
    "warped buildings",
    "melting structures",
    "buildings that defy physics",
    "gravity-defying objects",
]


# Human/face accuracy
HUMAN_ACCURACY_NEGATIVE_PROMPTS = [
    # Face/body issues
    "distorted faces",
    "malformed faces",
    "extra limbs",
    "missing limbs",
    "wrong number of fingers",
    "hands with wrong number of digits",
    "mutated hands",
    "deformed hands",
    "extra heads",
    "missing heads",
    "disconnected body parts",
    "body parts in wrong positions",
    "impossible anatomy",
    "merged people",
    "people melting together",
    "floating body parts",
    
    # Anachronistic people
    "modern hairstyles",
    "contemporary fashion",
    "modern accessories",
    "smartphones in hands",
    "modern bags",
    "modern shoes",
    "athletic wear",
    "sportswear",
    "modern sunglasses",
    "earbuds",
    "headphones",
]


# Atmospheric/mood issues
ATMOSPHERE_NEGATIVE_PROMPTS = [
    # Wrong mood
    "apocalyptic",
    "post-apocalyptic",
    "dystopian",
    "science fiction",
    "fantasy elements",
    "magical elements",
    "supernatural",
    "otherworldly",
    "alien",
    "futuristic",
    "cyberpunk",
    "steampunk unless appropriate",
    
    # Extreme conditions
    "extreme weather that obscures scene",
    "heavy fog that hides everything",
    "complete darkness",
    "total whiteout",
    "storm that ruins visibility",
    "tornado",
    "hurricane",
    "tsunami",
    "earthquake effects",
    "fire consuming the scene",
    "flood covering everything",
]


# Technical/digital artifacts
TECHNICAL_NEGATIVE_PROMPTS = [
    # Digital issues
    "digital artifacts",
    "compression artifacts",
    "pixelation",
    "jpeg artifacts",
    "banding",
    "posterization",
    "digital noise that looks modern",
    "chromatic aberration that looks digital",
    "lens flare that looks digital",
    
    # Modern depth of field effects
    "artificial bokeh",
    "fake depth of field",
    "extreme shallow depth of field",
    "modern lens bokeh",
    "circular bokeh balls",
    "creamy bokeh",
    "portrait mode effect",
    "computational depth of field",
    "tilt-shift effect",
    "selective focus effect",
    "everything blurred except subject",
    "background completely out of focus",
    
    # Digital processing
    "digital blur",
    "gaussian blur",
    "motion blur on static buildings",
    "motion blur on stationary objects",
    "excessive motion blur that obscures subject",
    "unrealistic motion blur patterns",
    
    # Rendering issues
    "3D rendering",
    "CGI",
    "computer generated",
    "obviously fake",
    "artificial looking",
    "plastic appearance",
    "waxy skin",
    "video game graphics",
    "low polygon count",
    "texture mapping visible",
    "unnatural lighting that looks rendered",
    "ray traced lighting that looks artificial",
]


# Branding and commercial issues
BRANDING_NEGATIVE_PROMPTS = [
    # Modern brands
    "modern brand names",
    "contemporary logos",
    "Starbucks",
    "McDonald's",
    "modern fast food chains",
    "modern retail chains",
    "big box stores",
    "modern supermarkets",
    "shopping malls",
    "strip malls",
    "modern gas stations",
    "convenience stores",
    "7-Eleven",
    "Walgreens",
    "CVS",
    "modern chain stores",
    
    # Watermarks and text overlays
    "watermarks",
    "copyright notices",
    "photo credits",
    "timestamps",
    "date stamps",
    "camera metadata visible",
    "EXIF data visible",
    "photographer signature unless appropriate",
    "text overlays",
    "captions on the image",
    "labels on the image",
    "arrows",
    "annotations",
    "markup",
    "highlighting",
]


def get_comprehensive_negative_prompt(
    include_text_accuracy: bool = True,
    include_human_accuracy: bool = True,
    era: str = "1930s",
    allow_people: bool = True
) -> str:
    """
    Get comprehensive negative prompt with customizable components.
    
    Args:
        include_text_accuracy: Include detailed text/signage accuracy prompts
        include_human_accuracy: Include human/face accuracy prompts
        era: Historical era (for era-specific exclusions)
        allow_people: If False, adds prompts to minimize people in scene
        
    Returns:
        Comprehensive negative prompt string
    """
    prompts = []
    
    # Always include core accuracy
    prompts.extend(ACCURACY_NEGATIVE_PROMPTS)
    
    # Text accuracy (important for storefronts)
    if include_text_accuracy:
        prompts.extend(TEXT_ACCURACY_NEGATIVE_PROMPTS)
    
    # Photo quality control
    prompts.extend(PHOTO_QUALITY_NEGATIVE_PROMPTS)
    
    # Composition control
    prompts.extend(COMPOSITION_NEGATIVE_PROMPTS)
    
    # Human accuracy (if people might appear)
    if include_human_accuracy and allow_people:
        prompts.extend(HUMAN_ACCURACY_NEGATIVE_PROMPTS)
    
    # Add "no people" if requested
    if not allow_people:
        prompts.extend([
            "people",
            "humans",
            "pedestrians",
            "crowds",
            "individuals",
            "figures",
            "persons",
            "men",
            "women",
            "children",
        ])
    
    # Atmospheric control
    prompts.extend(ATMOSPHERE_NEGATIVE_PROMPTS)
    
    # Technical issues
    prompts.extend(TECHNICAL_NEGATIVE_PROMPTS)
    
    # Branding control
    prompts.extend(BRANDING_NEGATIVE_PROMPTS)
    
    # Join with proper formatting
    return ", ".join(prompts)


def get_default_negative_prompt() -> str:
    """
    Get the default comprehensive negative prompt.
    
    This is the recommended configuration for most historical city images.
    
    Returns:
        Default comprehensive negative prompt
    """
    return get_comprehensive_negative_prompt(
        include_text_accuracy=True,
        include_human_accuracy=True,
        era="1930s",
        allow_people=True
    )


def get_era_specific_additions(era: str) -> List[str]:
    """
    Get era-specific negative prompts to exclude anachronisms.
    
    Args:
        era: Decade string like "1920s", "1930s", etc.
        
    Returns:
        List of era-specific negative prompts
    """
    additions = []
    
    # Extract decade
    decade = int(era.replace("s", ""))
    
    # Pre-1920s: Exclude automobiles that didn't exist
    if decade < 1920:
        additions.extend([
            "closed-body automobiles",
            "modern car bodies",
            "streamlined vehicles",
        ])
    
    # Pre-1930s: Limited electric lighting
    if decade < 1930:
        additions.extend([
            "extensive electric street lighting",
            "bright electric signs",
            "abundant electric lighting",
        ])
    
    # Pre-1940s: Limited building heights in small towns
    if decade < 1940:
        additions.extend([
            "skyscrapers in small towns",
            "tall buildings in rural areas",
            "modern high-rises",
        ])
    
    # 1950s+: Avoid earlier automobile styles
    if decade >= 1950:
        additions.extend([
            "Model T Fords",
            "1920s automobiles",
            "brass era cars",
            "very early automobiles",
        ])
    
    return additions


# Preset configurations for common use cases
PRESET_NEGATIVE_PROMPTS = {
    "strict": get_comprehensive_negative_prompt(
        include_text_accuracy=True,
        include_human_accuracy=True,
        allow_people=True
    ),
    
    "no_people": get_comprehensive_negative_prompt(
        include_text_accuracy=True,
        include_human_accuracy=False,
        allow_people=False
    ),
    
    "minimal": ", ".join(
        ACCURACY_NEGATIVE_PROMPTS +
        PHOTO_QUALITY_NEGATIVE_PROMPTS +
        COMPOSITION_NEGATIVE_PROMPTS
    ),
    
    "text_focused": ", ".join(
        ACCURACY_NEGATIVE_PROMPTS +
        TEXT_ACCURACY_NEGATIVE_PROMPTS +
        PHOTO_QUALITY_NEGATIVE_PROMPTS
    ),
}
