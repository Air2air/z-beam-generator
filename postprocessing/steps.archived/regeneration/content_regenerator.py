"""Content Regenerator Step

Regenerate content with adjusted parameters.
Pass 6, Step 6.1 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class ContentRegenerator(BaseStep):
    """Regenerate content with parameter adjustments"""
    
    def __init__(self, simple_generator):
        super().__init__()
        self.generator = simple_generator
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'material_name' not in context:
            raise ValueError("Missing 'material_name' in context")
        if 'component_type' not in context:
            raise ValueError("Missing 'component_type' in context")
        if 'adjustments' not in context:
            raise ValueError("Missing 'adjustments' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> str:
        """Regenerate content with adjustments"""
        material_name = context['material_name']
        component_type = context['component_type']
        adjustments = context['adjustments']
        
        self.logger.info(f"🔄 Regenerating with {len(adjustments)} adjustments")
        
        # Call SimpleGenerator with adjusted parameters
        new_content = self.generator.generate(
            material_name=material_name,
            component_type=component_type,
            parameter_overrides=adjustments
        )
        
        self.logger.info(f"✅ Regenerated {len(new_content)} chars")
        
        return new_content
