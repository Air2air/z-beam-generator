#!/usr/bin/env python3
"""
Material-Aware Prompt Generator - Core Component

Integrates the Material Prompting System with existing component generators
to provide material-specific prompt modifications with category and subcategory awareness.

This is the main entry point for material-aware prompt generation across all components.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class MaterialAwarePromptGenerator:
    """
    Generates material-aware prompts by integrating exception handling with base prompts
    
    Provides comprehensive material-specific prompt generation with:
    - Material category and subcategory awareness
    - Exception handling for edge cases
    - Property validation and guidance
    - Component-specific customization
    """
    
    def __init__(self):
        self.component_prompt_templates = {
            'frontmatter': self._get_frontmatter_template()
        }
        
        # Initialize integrations lazily
        self._exception_handler = None
        self._category_enhancer = None
    
    def generate_material_aware_prompt(
        self, 
        component_type: str = None,
        material_name: str = None,
        material_category: str = None, 
        material_data: Dict[str, Any] = None,
        base_prompt: str = None,
        **kwargs
    ) -> str:
        """
        Generate a material-aware prompt for any component type
        
        Supports both calling patterns:
        1. generate_material_aware_prompt(component_type, material_name, material_category, material_data)
        2. generate_material_aware_prompt(material_name=..., component_type=..., base_prompt=...)
        
        Args:
            component_type: Type of component (metricsproperties, text, etc.)
            material_name: Name of the material
            material_category: Category (metal, wood, ceramic, etc.)
            material_data: Material property data from Materials.yaml
            base_prompt: Custom base prompt (overrides template)
            **kwargs: Additional template variables
            
        Returns:
            Material-specific prompt with exception handling and category-aware context
        """
        
        # Handle missing material_data
        if material_data is None:
            material_data = kwargs.get('material_data', {})
        
        # Extract category from material_data if not provided
        if material_category is None:
            material_category = material_data.get('category', 'unknown')
        
        # Use custom base prompt or get template
        if base_prompt:
            # Custom base prompt provided
            material_aware_prompt = base_prompt
        else:
            # Get base template for component
            base_template = self.component_prompt_templates.get(component_type)
            if not base_template:
                raise ValueError(f"No template found for component type: {component_type}")
            
            # Apply basic template substitution
            template_vars = {
                'material_name': material_name,
                'material_category': material_category,
                **kwargs
            }
            
            material_aware_prompt = base_template.format(**template_vars)
        
        # Step 1: Apply material-specific exceptions
        try:
            material_aware_prompt = self._apply_material_exceptions(
                material_category, 
                material_aware_prompt, 
                material_data
            )
        except Exception as e:
            logger.warning(f"Material exception handling failed: {e}")
        
        # Step 2: Enhance with category-aware relative data context
        try:
            category_enhanced_prompt = self._enhance_with_category_awareness(
                material_aware_prompt,
                material_name,
                material_data,
                component_type
            )
            material_aware_prompt = category_enhanced_prompt
        except Exception as e:
            # If category enhancement fails, continue with material-aware prompt
            logger.warning(f"Category enhancement failed: {e}")
        
        # Step 3: Add property validation guidance
        validation_guidance = self._generate_property_validation_guidance(
            material_category, 
            component_type
        )
        
        if validation_guidance:
            material_aware_prompt += "\n\n" + validation_guidance
        
        return material_aware_prompt
    
    def _apply_material_exceptions(
        self, 
        material_category: str, 
        prompt: str, 
        material_data: Dict[str, Any]
    ) -> str:
        """Apply material-specific exception handling"""
        if self._exception_handler is None:
            try:
                from ..exceptions.handler import apply_material_exceptions
                self._apply_exceptions_func = apply_material_exceptions
            except ImportError:
                logger.warning("Exception handler not available")
                return prompt
        
        return self._apply_exceptions_func(material_category, prompt, material_data)
    
    def _enhance_with_category_awareness(
        self,
        prompt: str,
        material_name: str,
        material_data: Dict[str, Any],
        component_type: str
    ) -> str:
        """Enhance prompt with category-aware context"""
        if self._category_enhancer is None:
            try:
                from ..enhancers.category_aware_enhancer import enhance_prompt_with_category_awareness
                self._enhance_prompt_func = enhance_prompt_with_category_awareness
            except ImportError:
                logger.warning("Category enhancer not available")
                return prompt
        
        return self._enhance_prompt_func(prompt, material_name, material_data, component_type)
    

    

    

    
    def _get_frontmatter_template(self) -> str:
        """Base template for frontmatter component"""
        return """
Generate comprehensive frontmatter metadata for {material_name}.

MATERIAL DETAILS:
- Name: {material_name}
- Category: {material_category}

Generate structured YAML frontmatter including:
- Basic material information
- Physical and thermal properties
- Mechanical properties
- Laser processing parameters
- Applications and compatibility
- Safety and regulatory information

CRITICAL: Ensure all properties are appropriate for material category.
Use correct units and realistic value ranges.
Include category-specific fields and considerations.
"""
    
    def _generate_property_validation_guidance(self, material_category: str, component_type: str) -> str:
        """Generate property validation guidance for specific material and component"""
        guidance_lines = ["=== PROPERTY VALIDATION REQUIREMENTS ==="]
        
        # Category-specific validation rules
        validation_rules = {
            'wood': [
                "Use decomposition temperature instead of melting point",
                "Ensure density is within wood range (0.16-1.4 g/cm³)",
                "Use Janka hardness (kN) for wood hardness measurements",
                "Consider moisture content effects on properties",
                "Include grain direction considerations for mechanical properties"
            ],
            'ceramic': [
                "Use Mohs hardness scale when appropriate",
                "Emphasize compressive over tensile strength",
                "Consider thermal shock resistance",
                "Include porosity effects if applicable",
                "Account for wide thermal conductivity range"
            ],
            'metal': [
                "Ensure high thermal conductivity values",
                "Include high reflectance considerations for laser processing",
                "Consider surface oxidation effects",
                "Use appropriate metal hardness scales (HV, HB, HRC)",
                "Account for alloy composition effects"
            ],
            'plastic': [
                "Distinguish thermoplastic vs thermoset behavior",
                "Consider glass transition temperature",
                "Account for temperature-dependent properties",
                "Include polymer degradation considerations",
                "Use appropriate plastic property ranges"
            ],
            'composite': [
                "Account for anisotropic properties",
                "Consider fiber orientation effects",
                "Include matrix and fiber contributions",
                "Account for direction-dependent strength",
                "Consider delamination potential"
            ]
        }
        
        if material_category in validation_rules:
            guidance_lines.extend([f"- {rule}" for rule in validation_rules[material_category]])
        
        # Component-specific additional rules for frontmatter only
        if component_type == 'frontmatter':
            guidance_lines.extend([
                "- Include comprehensive material properties",
                "- Add machine settings with appropriate ranges",
                "- Ensure schema compliance with all required fields"
            ])
        
        return "\n".join(guidance_lines)
    
    def validate_generated_content(
        self, 
        component_type: str, 
        material_category: str, 
        generated_content: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate generated content against material-specific rules
        
        Args:
            component_type: Type of component
            material_category: Material category
            generated_content: Generated content to validate
            
        Returns:
            (is_valid, list_of_validation_errors)
        """
        validation_errors = []
        
        # No component-specific validation needed - frontmatter handles all validation internally
        
        # Category-specific validations
        category_validations = {
            'wood': self._validate_wood_content,
            'ceramic': self._validate_ceramic_content,
            'metal': self._validate_metal_content
        }
        
        if material_category in category_validations:
            category_errors = category_validations[material_category](generated_content)
            validation_errors.extend(category_errors)
        
        return len(validation_errors) == 0, validation_errors
    
    def _validate_wood_content(self, content: Dict[str, Any]) -> List[str]:
        """Validate wood-specific content"""
        errors = []
        
        if 'properties' in content:
            properties = content['properties']
            
            # Check for melting point vs decomposition temperature
            if 'meltingPoint' in properties and 'decompositionTemperature' not in properties:
                errors.append("Wood should use decomposition temperature, not melting point")
            
            # Check density range
            if 'density' in properties:
                density_str = str(properties['density'].get('value', ''))
                try:
                    density_val = float(re.findall(r'(\d+\.?\d*)', density_str)[0])
                    if not (0.16 <= density_val <= 1.4):
                        errors.append(f"Wood density {density_val} outside typical range 0.16-1.4 g/cm³")
                except (ValueError, IndexError):
                    errors.append("Could not validate wood density value")
        
        return errors
    
    def _validate_ceramic_content(self, content: Dict[str, Any]) -> List[str]:
        """Validate ceramic-specific content"""
        errors = []
        
        if 'properties' in content:
            properties = content['properties']
            
            # Check hardness units
            if 'hardness' in properties:
                hardness_data = properties['hardness']
                if isinstance(hardness_data, dict) and 'unit' in hardness_data:
                    unit = hardness_data['unit']
                    if unit not in ['Mohs', 'HV', 'GPa']:
                        errors.append(f"Ceramic hardness unit '{unit}' may not be appropriate")
        
        return errors
    
    def _validate_metal_content(self, content: Dict[str, Any]) -> List[str]:
        """Validate metal-specific content"""
        errors = []
        
        if 'properties' in content:
            properties = content['properties']
            
            # Check thermal conductivity range
            if 'thermalConductivity' in properties:
                tc_str = str(properties['thermalConductivity'].get('value', ''))
                try:
                    tc_val = float(re.findall(r'(\d+\.?\d*)', tc_str)[0])
                    if tc_val < 1.0:
                        errors.append(f"Metal thermal conductivity {tc_val} seems too low")
                except (ValueError, IndexError):
                    errors.append("Could not validate metal thermal conductivity")
        
        return errors


# Global instance for use throughout the system
material_aware_generator = MaterialAwarePromptGenerator()


def generate_material_specific_prompt(
    component_type: str,
    material_name: str, 
    material_category: str,
    material_data: Dict[str, Any],
    **kwargs
) -> str:
    """
    Global function to generate material-specific prompts for any component
    
    Args:
        component_type: Component type (metricsproperties, text, etc.)
        material_name: Name of material
        material_category: Material category (metal, wood, etc.)
        material_data: Material data from Materials.yaml
        **kwargs: Additional template variables
        
    Returns:
        Material-specific prompt with exception handling
    """
    return material_aware_generator.generate_material_aware_prompt(
        component_type, material_name, material_category, material_data, **kwargs
    )


def validate_component_content(
    component_type: str,
    material_category: str,
    generated_content: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Global function to validate generated content against material rules
    
    Args:
        component_type: Type of component
        material_category: Material category  
        generated_content: Generated content to validate
        
    Returns:
        (is_valid, list_of_validation_errors)
    """
    return material_aware_generator.validate_generated_content(
        component_type, material_category, generated_content
    )


if __name__ == "__main__":
    # Test the material-aware prompt generator
    generator = MaterialAwarePromptGenerator()
    
    # Test wood properties prompt
    wood_prompt = generator.generate_material_aware_prompt(
        component_type='metricsproperties',
        material_name='Oak',
        material_category='wood',
        material_data={'name': 'Oak', 'category': 'wood'}
    )
    
    print("=== WOOD METRICSPROPERTIES PROMPT ===")
    print(wood_prompt[:1000] + "...")
    
    # Test ceramic machine settings prompt
    ceramic_prompt = generator.generate_material_aware_prompt(
        component_type='metricsmachinesettings', 
        material_name='Alumina',
        material_category='ceramic',
        material_data={'name': 'Alumina', 'category': 'ceramic'}
    )
    
    print("\n=== CERAMIC MACHINE SETTINGS PROMPT ===")
    print(ceramic_prompt[:1000] + "...")