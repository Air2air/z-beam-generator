"""
Materials Image Research Utilities

Contamination research, pattern analysis, and material-specific prompt generation.
"""

from domains.materials.image.research.material_prompts import (
    build_material_cleaning_prompt,
    load_base_prompt_template
)
from domains.materials.image.research.material_researcher import MaterialContaminationResearcher
from domains.materials.image.research.category_contamination_researcher import CategoryContaminationResearcher
from domains.materials.image.research.persistent_research_cache import PersistentResearchCache

__all__ = [
    'build_material_cleaning_prompt',
    'load_base_prompt_template',
    'MaterialContaminationResearcher',
    'CategoryContaminationResearcher',
    'PersistentResearchCache',
]
