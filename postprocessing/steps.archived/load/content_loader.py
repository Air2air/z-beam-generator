"""Content Loader Step

Loads generated content from Materials.yaml.
Pass 1, Step 1.1 of validation pipeline.
"""

from pathlib import Path
import yaml
from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class ContentLoader(BaseStep):
    """Load content from Materials.yaml"""
    
    def _validate_inputs(self, context: Dict[str, Any]):
        """Validate material_name and component_type exist"""
        if 'material_name' not in context:
            raise ValueError("Missing 'material_name' in context")
        if 'component_type' not in context:
            raise ValueError("Missing 'component_type' in context")
        
        if not context['material_name']:
            raise ValueError("material_name is empty")
        if not context['component_type']:
            raise ValueError("component_type is empty")
    
    def _execute_logic(self, context: Dict[str, Any]) -> str:
        """Load content from Materials.yaml"""
        material_name = context['material_name']
        component_type = context['component_type']
        
        materials_path = Path("data/materials/Materials.yaml")
        
        if not materials_path.exists():
            raise FileNotFoundError(f"Materials.yaml not found at {materials_path}")
        
        with open(materials_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if 'materials' not in data:
            raise ValueError("Invalid Materials.yaml structure: missing 'materials' key")
        
        material = data['materials'].get(material_name)
        if not material:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        components = material.get('components', {})
        content = components.get(component_type)
        
        if not content:
            raise ValueError(
                f"Component '{component_type}' not found for material '{material_name}'"
            )
        
        self.logger.info(f"📄 Loaded {len(content)} chars from {material_name}/{component_type}")
        
        return content
