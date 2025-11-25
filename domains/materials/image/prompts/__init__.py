"""
Material Image Prompt Generation

Contains prompt builders and contamination research for
contextually-aware material before/after image generation.
"""

from domains.materials.image.prompts.material_prompts import (
    build_material_cleaning_prompt,
    load_base_prompt_template
)
from domains.materials.image.prompts.material_researcher import MaterialContaminationResearcher

__all__ = [
    'build_material_cleaning_prompt',
    'load_base_prompt_template',
    'MaterialContaminationResearcher'
]
