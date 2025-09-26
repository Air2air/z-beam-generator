"""
Material Prompting System

AI-powered materials research and population system for laser cleaning applications.

KEY PURPOSE: Research and populate Materials.yaml and frontmatter with comprehensive,
scientifically accurate material data through intelligent AI-driven analysis.

Core Functions:
- Materials.yaml Research & Population: Intelligent gap detection and data completion
- Frontmatter Enhancement: Generate accurate material-specific metadata and properties
- Material-specific prompt generation with category and subcategory awareness
- Exception handling for material-specific edge cases
- Machine settings optimization based on material characteristics
- Integration with existing component generators

Directory Structure:
- core/: Core prompt generation and material awareness
- exceptions/: Material-specific exception handling
- enhancers/: Category and subcategory-aware prompt enhancers
- generators/: Specialized generators for properties and machine settings
- properties/: Material properties analysis and enhancement
- machine_settings/: Material-specific machine setting optimization
- integration/: Component wrapper and factory integration

Usage:
    from material_prompting import material_prompting
    
    # Research and populate Materials.yaml
    update_result = material_prompting.update_materials_yaml(
        target_materials=["Aluminum 6061", "Steel"],
        backup=True
    )
    
    # Generate frontmatter-specific prompts
    frontmatter_prompt = material_prompting.generate_material_aware_prompt(
        component_type="frontmatter",
        material_name="aluminum",
        material_category="metal"
    )
    
    # Research and enhance material properties for population
    properties = material_prompting.enhance_material_properties(
        material_name="Aluminum 6061",
        material_category="metal",
        existing_properties={"density": {"value": "2.70 g/cm³"}}
    )
"""

__version__ = "1.0.0"
__author__ = "Z-Beam Generator Team"

# Import main integration wrapper for easy access
from .integration.wrapper import (
    MaterialPromptingIntegration,
    material_prompting,
    generate_material_aware_prompt,
    enhance_material_properties,
    optimize_machine_settings,
    update_materials_yaml,
    research_frontmatter_metadata
)

# Import core classes for direct access if needed
try:
    from .core.material_aware_generator import MaterialAwarePromptGenerator
    from .exceptions.handler import MaterialExceptionHandler
    from .enhancers.category_aware_enhancer import CategoryAwarePromptEnhancer
    from .properties.enhancer import MaterialPropertiesEnhancer
    from .machine_settings.optimizer import MaterialMachineSettingsEnhancer
    from .generators.materials_yaml_updater import MaterialsYamlUpdater
except ImportError as e:
    # Handle import errors gracefully during development
    import logging
    logging.getLogger(__name__).warning(f"Some material prompting components not available: {e}")

__all__ = [
    # Main integration interface
    'MaterialPromptingIntegration',
    'material_prompting',
    
    # Research and population functions
    'research_frontmatter_metadata',
    'update_materials_yaml',
    
    # Enhancement functions
    'generate_material_aware_prompt',
    'enhance_material_properties', 
    'optimize_machine_settings',
    
    # Core classes (if successfully imported)
    'MaterialAwarePromptGenerator',
    'MaterialExceptionHandler',
    'CategoryAwarePromptEnhancer',
    'MaterialPropertiesEnhancer',
    'MaterialMachineSettingsEnhancer',
    'MaterialsYamlUpdater'
]