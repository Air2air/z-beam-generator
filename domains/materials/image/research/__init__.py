"""
Materials Image Research Utilities

Contamination research, pattern analysis, and material-specific prompt generation.
"""

from domains.materials.image.research.contamination_pattern_selector import (
    ContaminationPatternSelector,
)
from domains.materials.image.research.material_prompts import (
    build_material_cleaning_prompt,
    load_base_prompt_template,
)

__all__ = [
    'build_material_cleaning_prompt',
    'load_base_prompt_template',
    'ContaminationPatternSelector',
]
