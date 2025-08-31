#!/usr/bin/env python3
"""
Laser Parameter Management System for Z-Beam Generator

This module provides dynamic laser parameter loading for frontmatter generation,
supporting category-specific laser settings for optimal material processing.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


def load_laser_parameters(category: str) -> Dict[str, str]:
    """
    Load laser parameters for a specific material category.
    
    Args:
        category: Material category (metal, ceramic, polymer, etc.) - required
        
    Returns:
        Dictionary with laser parameters for the category
    """
    params_path = Path("data/laser_parameters.yaml")
    
    with open(params_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    categories = data['categories']  # Must exist, no fallback
    
    if category in categories:
        logger.info(f"Loaded laser parameters for category: {category}")
        return categories[category]
    else:
        # Use default if category not found, but this is the only fallback allowed
        logger.info(f"Using default laser parameters (category '{category}' not found)")
        return data['default']


def get_dynamic_laser_parameters(category: str) -> Dict[str, str]:
    """
    Get dynamic laser parameters for template substitution.
    
    Args:
        category: Material category
        
    Returns:
        Dictionary with parameter values ready for template substitution
    """
    params = load_laser_parameters(category)
    
    # Format for template substitution without fallbacks
    return {
        'dynamic_spot_size': params['spotSize'],
        'dynamic_repetition_rate': params['repetitionRate'],
        'dynamic_safety_class': params['safetyClass'],
        'dynamic_power_range': params['powerRange']
    }
