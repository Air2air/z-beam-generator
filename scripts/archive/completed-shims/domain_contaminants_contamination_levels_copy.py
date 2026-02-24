#!/usr/bin/env python3
"""
Contamination Level Descriptions

Detailed descriptions for contamination intensity, uniformity, and view modes.

Author: AI Assistant
Date: November 24, 2025
"""

# Contamination Intensity Levels (1-5)
CONTAMINATION_LEVELS = {
    1: {
        "name": "Minimal",
        "description": "Light surface dust or minimal staining. Contamination barely visible, covers <20% of surface. Base material clearly visible through contamination.",
        "coverage": "Sparse, isolated spots",
        "color_impact": "Minimal darkening (5-10%)",
        "texture": "Thin, powdery or light film"
    },
    2: {
        "name": "Light",
        "description": "Noticeable contamination but still light. Covers 20-40% of surface. Base material color partially visible.",
        "coverage": "Scattered, uneven patches",
        "color_impact": "Moderate darkening (10-25%)",
        "texture": "Thin layers with some buildup"
    },
    3: {
        "name": "Moderate",
        "description": "Significant contamination covering 40-60% of surface. Base material color obscured in many areas. Typical real-world contamination.",
        "coverage": "Widespread with heavy spots",
        "color_impact": "Noticeable darkening (25-50%)",
        "texture": "Mixed thin and thick layers"
    },
    4: {
        "name": "Heavy",
        "description": "Extensive contamination covering 60-80% of surface. Base material barely visible. Heavy buildup in crevices and low areas.",
        "coverage": "Nearly complete coverage",
        "color_impact": "Significant darkening (50-75%)",
        "texture": "Thick, crusty, multi-layer buildup"
    },
    5: {
        "name": "Severe",
        "description": "Extreme contamination covering 80-95% of surface. Base material almost completely obscured. Thick, multi-layer buildup throughout.",
        "coverage": "Near-total coverage",
        "color_impact": "Extreme darkening (75-90%)",
        "texture": "Very thick, encrusted, flaking"
    }
}

# Contamination Uniformity Levels (1-5)
UNIFORMITY_LEVELS = {
    1: {
        "name": "Single Type",
        "description": "Only ONE type of contamination present. Uniform appearance throughout contaminated areas.",
        "variety": "Homogeneous",
        "contaminant_count": 1,
        "visual_complexity": "Simple, consistent"
    },
    2: {
        "name": "Two Types",
        "description": "TWO types of contamination present. Slight visual variety with distinct layers or zones.",
        "variety": "Low diversity",
        "contaminant_count": 2,
        "visual_complexity": "Basic layering"
    },
    3: {
        "name": "Three Types",
        "description": "THREE types of contamination present. Moderate visual complexity with overlapping layers.",
        "variety": "Moderate diversity",
        "contaminant_count": 3,
        "visual_complexity": "Mixed layers, some interaction"
    },
    4: {
        "name": "Four Types",
        "description": "FOUR types of contamination present. High visual complexity with multiple overlapping layers and interactions.",
        "variety": "High diversity",
        "contaminant_count": 4,
        "visual_complexity": "Complex layering, visible interactions"
    },
    5: {
        "name": "Diverse (4+ Types)",
        "description": "FOUR OR MORE types of contamination present. Very high visual complexity with multiple overlapping layers, color variations, and interactions.",
        "variety": "Very high diversity",
        "contaminant_count": "4+",
        "visual_complexity": "Highly complex, natural chaos"
    }
}

# View Mode Descriptions
VIEW_MODES = {
    "Contextual": {
        "name": "Contextual (3D Perspective)",
        "description": "Object shown in realistic 3D perspective within typical environment. Natural lighting, depth, shadows. Shows object in real-world context.",
        "perspective": "3D perspective",
        "framing": "Object in environment",
        "lighting": "Natural, directional",
        "background": "Typical working environment visible",
        "use_case": "Marketing, demonstration, real-world context"
    },
    "Isolated": {
        "name": "Isolated (2D Technical)",
        "description": "Object shown in flat, 2D top-down or front view against neutral background. Studio lighting, minimal shadows. Technical documentation style.",
        "perspective": "2D orthographic (flat)",
        "framing": "Object only, centered",
        "lighting": "Even, studio lighting",
        "background": "Neutral gray or white",
        "use_case": "Technical documentation, comparison, analysis"
    }
}

# Environment Wear Levels (1-5)
ENVIRONMENT_WEAR_LEVELS = {
    1: {
        "name": "Pristine",
        "description": "Like new. Clean environment, no visible wear. Background surfaces clean and well-maintained.",
        "visible_signs": "None",
        "age_appearance": "Brand new"
    },
    2: {
        "name": "Minimal Wear",
        "description": "Very light use. Environment shows minimal signs of age. Slight dust, minor marks.",
        "visible_signs": "Light dust, very minor marks",
        "age_appearance": "Recently used, well-maintained"
    },
    3: {
        "name": "Moderate Wear",
        "description": "Regular use. Environment shows moderate aging. Visible wear patterns, dust accumulation, minor scratches.",
        "visible_signs": "Dust, wear patterns, minor scratches",
        "age_appearance": "Actively used, normal maintenance"
    },
    4: {
        "name": "Significant Wear",
        "description": "Heavy use. Environment shows significant aging. Obvious wear, accumulated dirt, scratches, staining on background.",
        "visible_signs": "Obvious wear, dirt, scratches, stains",
        "age_appearance": "Long-term use, minimal maintenance"
    },
    5: {
        "name": "Extensive Wear",
        "description": "Extreme use. Environment shows extensive aging. Heavy wear everywhere, significant dirt/dust, damaged surfaces.",
        "visible_signs": "Heavy wear, significant damage, neglect",
        "age_appearance": "Decades of use, poor maintenance"
    }
}


def get_contamination_text(level: int) -> str:
    """Get detailed contamination level description."""
    if level not in CONTAMINATION_LEVELS:
        raise ValueError(f"Invalid contamination level: {level}. Must be 1-5.")
    return CONTAMINATION_LEVELS[level]['description']


def get_uniformity_text(level: int) -> str:
    """Get detailed uniformity level description."""
    if level not in UNIFORMITY_LEVELS:
        raise ValueError(f"Invalid uniformity level: {level}. Must be 1-5.")
    return UNIFORMITY_LEVELS[level]['description']


def get_view_mode_text(mode: str) -> str:
    """Get detailed view mode description."""
    if mode not in VIEW_MODES:
        raise ValueError(f"Invalid view mode: {mode}. Must be 'Contextual' or 'Isolated'.")
    return VIEW_MODES[mode]['description']


def get_environment_wear_text(level: int) -> str:
    """Get detailed environment wear level description."""
    if level not in ENVIRONMENT_WEAR_LEVELS:
        raise ValueError(f"Invalid environment wear level: {level}. Must be 1-5.")
    return ENVIRONMENT_WEAR_LEVELS[level]['description']
