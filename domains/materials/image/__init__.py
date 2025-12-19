"""
Material Image Generation Module

Contains material before/after image generation, contamination research,
and laser cleaning visualization for materials.
"""

from domains.materials.image.material_config import MaterialImageConfig
from domains.materials.image.material_generator import MaterialImageGenerator
from shared.types.contamination_levels import (
    CONTAMINATION_LEVELS,
    UNIFORMITY_LEVELS,
    VIEW_MODES,
    get_contamination_text,
    get_uniformity_text,
)

__all__ = [
    'MaterialImageGenerator',
    'MaterialImageConfig',
    'CONTAMINATION_LEVELS',
    'UNIFORMITY_LEVELS',
    'VIEW_MODES',
    'get_contamination_text',
    'get_uniformity_text'
]
