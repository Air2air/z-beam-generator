#!/usr/bin/env python3
"""
Image Context Settings Loader

Loads environmental context settings from YAML for image generation.
Enables learning system integration by storing parameters in data instead of code.

Author: AI Assistant
Date: November 29, 2025
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

# Cache for loaded settings
_settings_cache: Optional[Dict[str, Any]] = None


def _get_settings_path() -> Path:
    """Get path to ImageContextSettings.yaml."""
    # Try relative to this file first
    this_dir = Path(__file__).parent
    
    # Navigate to data/settings/
    possible_paths = [
        this_dir / "data" / "settings" / "ImageContextSettings.yaml",
        this_dir.parent / "data" / "settings" / "ImageContextSettings.yaml",
        this_dir.parent.parent / "data" / "settings" / "ImageContextSettings.yaml",
        this_dir.parent.parent.parent / "data" / "settings" / "ImageContextSettings.yaml",
        this_dir.parent.parent.parent.parent / "data" / "settings" / "ImageContextSettings.yaml",
        Path("data/settings/ImageContextSettings.yaml"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    raise FileNotFoundError(
        f"ImageContextSettings.yaml not found. Searched: {[str(p) for p in possible_paths]}"
    )


def load_context_settings(force_reload: bool = False) -> Dict[str, Any]:
    """
    Load context settings from YAML.
    
    Args:
        force_reload: If True, reload from disk even if cached
        
    Returns:
        Dictionary with all context settings
    """
    global _settings_cache
    
    if _settings_cache is not None and not force_reload:
        return _settings_cache
    
    settings_path = _get_settings_path()
    
    with open(settings_path, 'r') as f:
        _settings_cache = yaml.safe_load(f)
    
    logger.debug(f"Loaded context settings from {settings_path}")
    return _settings_cache


def get_context_config(context: str) -> Dict[str, Any]:
    """
    Get configuration for a specific context.
    
    Args:
        context: Context name (indoor, outdoor, industrial, marine, architectural)
        
    Returns:
        Dictionary with context configuration including:
        - description
        - pattern_weights (aging_weight, contamination_weight)
        - default_severity
        - background (setting, lighting, surface, depth_cues, atmosphere)
        - priority_patterns (by material category)
        
    Raises:
        ValueError: If context not found
    """
    settings = load_context_settings()
    contexts = settings.get('contexts', {})
    
    if context not in contexts:
        valid = list(contexts.keys())
        raise ValueError(f"Unknown context '{context}'. Valid contexts: {valid}")
    
    return contexts[context]


def get_pattern_weights(context: str) -> Dict[str, float]:
    """
    Get pattern selection weights for a context.
    
    Args:
        context: Context name
        
    Returns:
        Dictionary with aging_weight and contamination_weight
    """
    config = get_context_config(context)
    return config.get('pattern_weights', {
        'aging_weight': 1.5,
        'contamination_weight': 1.0
    })


def get_default_severity(context: str) -> str:
    """
    Get default severity for a context.
    
    Args:
        context: Context name
        
    Returns:
        Severity string (light, moderate, heavy)
    """
    config = get_context_config(context)
    return config.get('default_severity', 'moderate')


def get_background_settings(context: str) -> Dict[str, str]:
    """
    Get background environment settings for a context.
    
    Args:
        context: Context name
        
    Returns:
        Dictionary with setting, lighting, surface, depth_cues, atmosphere
    """
    config = get_context_config(context)
    return config.get('background', {
        'setting': 'neutral studio',
        'lighting': 'even studio lighting',
        'surface': 'neutral surface',
        'depth_cues': 'shallow depth of field',
        'atmosphere': 'clean'
    })


def get_priority_patterns(context: str, material_category: str) -> List[str]:
    """
    Get priority contamination patterns for a context and material category.
    
    Args:
        context: Context name
        material_category: Material category (wood, metal, glass, etc.)
        
    Returns:
        List of pattern IDs in priority order
    """
    config = get_context_config(context)
    priorities = config.get('priority_patterns', {})
    return priorities.get(material_category, [])


def get_available_contexts() -> List[str]:
    """Get list of available context names."""
    settings = load_context_settings()
    return list(settings.get('contexts', {}).keys())


def get_context_description(context: str) -> str:
    """Get human-readable description of a context."""
    config = get_context_config(context)
    return config.get('description', f'{context} environment')


# Convenience function for prompt building
def build_background_prompt(context: str) -> str:
    """
    Build background description for image generation prompt.
    
    Args:
        context: Context name
        
    Returns:
        Formatted string describing the background environment
    """
    bg = get_background_settings(context)
    
    parts = [
        f"Setting: {bg.get('setting', 'neutral environment')}",
        f"Lighting: {bg.get('lighting', 'even lighting')}",
        f"Surface: {bg.get('surface', 'work surface')}",
        f"Background: {bg.get('depth_cues', 'blurred background')}",
        f"Atmosphere: {bg.get('atmosphere', 'clean')}"
    ]
    
    return ". ".join(parts)


# Test function
if __name__ == "__main__":
    print("Testing ImageContextSettings loader...")
    print()
    
    contexts = get_available_contexts()
    print(f"Available contexts: {contexts}")
    print()
    
    for ctx in contexts:
        print(f"=== {ctx.upper()} ===")
        print(f"Description: {get_context_description(ctx)}")
        print(f"Default severity: {get_default_severity(ctx)}")
        print(f"Pattern weights: {get_pattern_weights(ctx)}")
        print(f"Background prompt: {build_background_prompt(ctx)[:100]}...")
        print(f"Wood priorities: {get_priority_patterns(ctx, 'wood')[:3]}")
        print()
