"""
Image Prompt Generation

Contains prompt builders and population research for
contextually-aware city image generation.
"""

from regions.image.prompts.city_image_prompts import get_historical_base_prompt
from regions.image.prompts.researcher import PopulationResearcher

__all__ = [
    'get_historical_base_prompt',
    'PopulationResearcher'
]
