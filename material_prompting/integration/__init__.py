"""Integration components for material prompting"""

from .wrapper import (
    MaterialPromptingIntegration,
    material_prompting,
    generate_material_aware_prompt,
    enhance_material_properties,
    optimize_machine_settings,
    update_materials_yaml
)

__all__ = [
    'MaterialPromptingIntegration',
    'material_prompting',
    'generate_material_aware_prompt',
    'enhance_material_properties', 
    'optimize_machine_settings',
    'update_materials_yaml'
]