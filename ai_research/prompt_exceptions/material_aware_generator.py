#!/usr/bin/env python3
"""
Material-Aware Prompt Generator

Integrates the AI Prompt Exception Handling System with existing component generators
to provide material-specific prompt modifications.
"""

import logging
from typing import Dict, Any, List, Optional
import re
from .material_exception_handler import apply_material_exceptions, validate_property_for_material_type
from .category_aware_enhancer import enhance_prompt_with_category_awareness

logger = logging.getLogger(__name__)


class MaterialAwarePromptGenerator:
    """
    Generates material-aware prompts by integrating exception handling with base prompts
    """
    
    def __init__(self):
        self.component_prompt_templates = {
            'text': self._get_text_template(),
            'frontmatter': self._get_frontmatter_template()
        }
    
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
            component_type: Type of component (frontmatter, text)
            material_name: Name of the material
            material_category: Category (metal, wood, ceramic, etc.)
            material_data: Material property data from materials.yaml
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
        material_aware_prompt = apply_material_exceptions(
            material_category, 
            material_aware_prompt, 
            material_data
        )
        
        # Step 2: Enhance with category-aware relative data context
        try:
            category_enhanced_prompt = enhance_prompt_with_category_awareness(
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
    
    def _get_text_template(self) -> str:
        """Base template for text component"""
        return """
Generate comprehensive technical content about {material_name} for laser cleaning applications.

MATERIAL DETAILS:
- Name: {material_name}
- Category: {material_category}

Generate detailed technical content covering:
1. Material properties and characteristics
2. Laser cleaning applications and benefits
3. Processing parameters and considerations
4. Safety and environmental factors
5. Industry applications and case studies

CRITICAL: Ensure technical accuracy for material category.
Use appropriate terminology and focus on relevant properties.
Consider material-specific challenges and solutions.
"""
    
    def _get_frontmatter_template(self) -> str:
        """Enhanced template for comprehensive frontmatter property discovery"""
        return """
Generate comprehensive frontmatter metadata for {material_name} with COMPLETE property research.

MATERIAL DETAILS:
- Name: {material_name}
- Category: {material_category}

CRITICAL RESEARCH REQUIREMENTS:

=== MATERIAL PROPERTIES RESEARCH ===
You must research and include ALL relevant properties for {material_category} materials:

UNIVERSAL PROPERTIES (required for all materials):
- density: Core physical property for laser calculations
- thermalConductivity: Essential for heat transfer analysis
- specificHeat: Required for thermal modeling

CATEGORY-SPECIFIC PROPERTIES for {material_category}:
- For METALS: Include meltingPoint, youngsModulus, tensileStrength, hardness, thermalExpansion, electricalConductivity
- For CERAMICS: Include meltingPoint, hardness, compressiveStrength, thermalShockResistance, thermalExpansion, porosity
- For POLYMERS: Include glassTransitionTemperature, decompositionTemperature, tensileStrength, flexuralModulus, thermalExpansion
- For WOOD: Include decompositionTemperature, moistureContent, grainDensity, ligninContent, anisotropicStrength
- For GLASS: Include meltingPoint, hardness, thermalExpansion, refractiveIndex, thermalShockResistance
- For COMPOSITES: Include fiberVolumeFraction, matrixProperties, anisotropicModulus, interlaminearStrength

OPTICAL/LASER-SPECIFIC PROPERTIES:
- laserAbsorption: Material-specific absorption coefficients
- laserReflectivity: Surface reflectance at common laser wavelengths
- ablationThreshold: Minimum energy for material removal
- thermalDiffusivity: Heat distribution characteristics

=== MACHINE SETTINGS RESEARCH ===
You must calculate ALL relevant laser parameters for {material_name}:

POWER PARAMETERS:
- powerRange: Optimal power range with min/max values calculated from material properties
- fluenceThreshold: Energy density thresholds for effective processing
- ablationThreshold: Minimum energy for material removal

TEMPORAL PARAMETERS:
- pulseDuration: Optimal pulse duration based on thermal properties
- repetitionRate: Frequency settings for material-specific processing
- processingSpeed: Scan speeds optimized for material thermal response

BEAM PARAMETERS:
- wavelength: Optimal wavelengths based on material absorption characteristics
- spotSize: Beam diameter recommendations for material type
- beamQuality: Required beam characteristics for effective processing

SCANNING PARAMETERS:
- scanningSpeed: Optimal traverse rates for material processing
- lineSpacing: Overlap requirements for complete coverage
- passCount: Multiple pass strategies for thick materials

=== RESEARCH METHODOLOGY ===
For EACH property, you must:
1. Research the EXACT value for {material_name} specifically (not generic category values)
2. Calculate appropriate min/max ranges based on material variations
3. Assign confidence scores based on source reliability (80-100% for database values)
4. Provide technical descriptions explaining the property's significance
5. Validate against {material_category} category constraints

FAIL-FAST REQUIREMENTS:
- NO fallback values or estimates allowed
- ALL properties must be researched dynamically
- System must fail if research unavailable rather than use defaults
- Every value requires source validation and confidence scoring

Generate structured YAML with complete DataMetrics for all discovered properties.
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
        
        # Component-specific additional rules are now handled by frontmatter generator
        
        return "\n".join(guidance_lines)
    
    def validate_generated_content(
        self, 
        component_type: str, 
        material_category: str, 
        generated_content: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
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
        
        # Validation now handled by frontmatter generator and PropertyResearcher
        # Legacy property-specific validation removed since components are consolidated
        
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
        component_type: Component type (frontmatter, text)
        material_name: Name of material
        material_category: Material category (metal, wood, etc.)
        material_data: Material data from materials.yaml
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
) -> tuple[bool, List[str]]:
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
    
    # Test frontmatter prompt
    frontmatter_prompt = generator.generate_material_aware_prompt(
        component_type='frontmatter',
        material_name='Oak',
        material_category='wood',
        material_data={'name': 'Oak', 'category': 'wood'}
    )
    
    print("=== WOOD FRONTMATTER PROMPT ===")
    print(frontmatter_prompt[:1000] + "...")
    
    # Test text component prompt
    text_prompt = generator.generate_material_aware_prompt(
        component_type='text', 
        material_name='Alumina',
        material_category='ceramic',
        material_data={'name': 'Alumina', 'category': 'ceramic'}
    )
    
    print("\n=== CERAMIC TEXT PROMPT ===")
    print(text_prompt[:1000] + "...")