#!/usr/bin/env python3
"""
Integration Guide for AI Prompt Exception Handling System

This file demonstrates how to integrate the material-specific exception handling
system with existing component generators.
"""

from typing import Dict, Any, List
import yaml
import json
from pathlib import Path

# Import the exception handling system
from ai_research.prompt_exceptions.material_aware_generator import (
    generate_material_specific_prompt,
    validate_component_content
)


class ComponentIntegrationGuide:
    """
    Provides integration examples for different component types
    """
    
    def __init__(self):
        self.integration_examples = {
            'metricsproperties': self._metricsproperties_integration,
            'metricsmachinesettings': self._metricsmachinesettings_integration,
            'text': self._text_integration,
            'frontmatter': self._frontmatter_integration
        }
    
    def _metricsproperties_integration(self) -> Dict[str, Any]:
        """Example integration for metricsproperties component"""
        return {
            'component_file': 'components/metricsproperties/generator.py',
            'integration_points': [
                {
                    'location': 'generate method',
                    'modification': 'Replace base prompt with material-aware prompt',
                    'code_example': '''
# BEFORE (existing code):
prompt = self.prompt_template.format(
    material_name=material_name,
    properties_summary=properties_summary
)

# AFTER (with exception handling):
from ai_research.prompt_exceptions.material_aware_generator import generate_material_specific_prompt

material_category = material_data.get('category', 'unknown')
prompt = generate_material_specific_prompt(
    component_type='metricsproperties',
    material_name=material_name,
    material_category=material_category,
    material_data=material_data,
    properties_summary=properties_summary
)
'''
                },
                {
                    'location': 'validation method',
                    'modification': 'Add material-specific validation',
                    'code_example': '''
# Add after content generation:
from ai_research.prompt_exceptions.material_aware_generator import validate_component_content

is_valid, errors = validate_component_content(
    component_type='metricsproperties',
    material_category=material_category,
    generated_content=generated_content
)

if not is_valid:
    logger.warning(f"Material validation errors for {material_name}: {errors}")
    # Handle validation errors (retry, fallback, etc.)
'''
                }
            ],
            'benefits': [
                'Wood materials get decomposition temperature instead of melting point',
                'Ceramic materials use appropriate hardness scales (Mohs)',
                'Metal materials get validated thermal conductivity ranges',
                'Proper unit handling for different material types'
            ]
        }
    
    def _metricsmachinesettings_integration(self) -> Dict[str, Any]:
        """Example integration for metricsmachinesettings component"""
        return {
            'component_file': 'components/metricsmachinesettings/generator.py',
            'integration_points': [
                {
                    'location': 'generate method',
                    'modification': 'Material-aware laser parameter generation',
                    'code_example': '''
# Enhanced prompt generation:
material_category = material_data.get('category', 'unknown')
prompt = generate_material_specific_prompt(
    component_type='metricsmachinesettings',
    material_name=material_name, 
    material_category=material_category,
    material_data=material_data,
    machine_settings_summary=machine_settings_summary
)
'''
                }
            ],
            'benefits': [
                'Metal materials get high-reflectance considerations',
                'Wood materials get moisture content warnings',
                'Ceramic materials get thermal shock considerations',
                'Appropriate power ranges for material categories'
            ]
        }
    
    def _text_integration(self) -> Dict[str, Any]:
        """Example integration for text component"""
        return {
            'component_file': 'components/text/generators/fail_fast_generator.py',
            'integration_points': [
                {
                    'location': 'prompt construction',
                    'modification': 'Material-specific content guidance',
                    'code_example': '''
# In prompt construction phase:
material_category = material_data.get('category', 'unknown')
material_aware_prompt = generate_material_specific_prompt(
    component_type='text',
    material_name=material_name,
    material_category=material_category,
    material_data=material_data,
    content_requirements=content_requirements
)

# Combine with existing localization prompts:
final_prompt = localization_prompt + "\\n\\n" + material_aware_prompt
'''
                }
            ],
            'benefits': [
                'Wood content focuses on decomposition and grain properties',
                'Ceramic content emphasizes brittleness and thermal shock',
                'Metal content highlights conductivity and reflectance',
                'Appropriate technical terminology for each material type'
            ]
        }
    
    def _frontmatter_integration(self) -> Dict[str, Any]:
        """Example integration for frontmatter component"""
        return {
            'component_file': 'components/frontmatter/core/streamlined_generator.py',
            'integration_points': [
                {
                    'location': 'property enhancement',
                    'modification': 'Material-aware property validation',
                    'code_example': '''
# During property enhancement:
from ai_research.prompt_exceptions.material_exception_handler import validate_property_for_material_type

for prop_name, prop_value in properties.items():
    is_valid, message = validate_property_for_material_type(
        material_category, prop_name, prop_value
    )
    
    if not is_valid:
        logger.warning(f"Property validation issue: {message}")
        # Apply correction or use fallback
'''
                }
            ],
            'benefits': [
                'Prevents invalid property combinations',
                'Ensures appropriate units for material types',
                'Validates property ranges against material categories',
                'Provides material-specific property descriptions'
            ]
        }
    
    def generate_integration_documentation(self) -> str:
        """Generate comprehensive integration documentation"""
        doc_sections = []
        
        doc_sections.append("# AI Prompt Exception Handling - Integration Guide")
        doc_sections.append("")
        doc_sections.append("## Overview")
        doc_sections.append("This system provides material-specific exception handling for AI prompts,")
        doc_sections.append("ensuring that generated content respects the unique characteristics of different")
        doc_sections.append("material categories (wood, ceramic, metal, plastic, composite, etc.).")
        doc_sections.append("")
        
        for component_type, integration_func in self.integration_examples.items():
            integration_info = integration_func()
            
            doc_sections.append(f"## {component_type.title()} Integration")
            doc_sections.append(f"**File:** `{integration_info['component_file']}`")
            doc_sections.append("")
            
            doc_sections.append("### Integration Points:")
            for point in integration_info['integration_points']:
                doc_sections.append(f"**{point['location'].title()}:**")
                doc_sections.append(f"- {point['modification']}")
                doc_sections.append("```python")
                doc_sections.append(point['code_example'].strip())
                doc_sections.append("```")
                doc_sections.append("")
            
            doc_sections.append("### Benefits:")
            for benefit in integration_info['benefits']:
                doc_sections.append(f"- {benefit}")
            doc_sections.append("")
        
        doc_sections.append("## Material-Specific Exception Rules")
        doc_sections.append("")
        doc_sections.append("### Wood Materials")
        doc_sections.append("- `meltingPoint` → `decompositionTemperature`")
        doc_sections.append("- Density range: 0.16-1.4 g/cm³")
        doc_sections.append("- Hardness units: kN (Janka scale)")
        doc_sections.append("- Thermal conductivity: 0.04-0.4 W/m·K")
        doc_sections.append("- Considerations: Grain direction, moisture content")
        doc_sections.append("")
        
        doc_sections.append("### Ceramic Materials")
        doc_sections.append("- Hardness units: Mohs scale preferred")
        doc_sections.append("- Emphasis on compressive over tensile strength")  
        doc_sections.append("- Thermal shock resistance considerations")
        doc_sections.append("- Wide thermal conductivity range: 0.5-200 W/m·K")
        doc_sections.append("")
        
        doc_sections.append("### Metal Materials")
        doc_sections.append("- High thermal conductivity expected: 1-500 W/m·K")
        doc_sections.append("- High reflectance considerations: 60-98%")
        doc_sections.append("- Surface oxidation effects on laser processing")
        doc_sections.append("- Electrical conductivity properties")
        doc_sections.append("")
        
        doc_sections.append("### Plastic Materials")
        doc_sections.append("- Distinguish thermoplastic vs thermoset behavior")
        doc_sections.append("- Glass transition temperature considerations")
        doc_sections.append("- Temperature-dependent properties")
        doc_sections.append("- Low thermal conductivity: 0.1-2.0 W/m·K")
        doc_sections.append("")
        
        doc_sections.append("### Composite Materials")
        doc_sections.append("- Anisotropic properties (direction-dependent)")
        doc_sections.append("- Fiber orientation effects")
        doc_sections.append("- Matrix and fiber property contributions")
        doc_sections.append("- Delamination considerations")
        doc_sections.append("")
        
        doc_sections.append("## Implementation Checklist")
        doc_sections.append("")
        doc_sections.append("### For Each Component:")
        doc_sections.append("- [ ] Import material-aware prompt generator")
        doc_sections.append("- [ ] Replace base prompts with material-aware versions")
        doc_sections.append("- [ ] Add material category detection")
        doc_sections.append("- [ ] Implement content validation")
        doc_sections.append("- [ ] Add error handling for validation failures")
        doc_sections.append("- [ ] Test with different material categories")
        doc_sections.append("")
        
        doc_sections.append("### System-Wide:")
        doc_sections.append("- [ ] Update materials.yaml to ensure category consistency")
        doc_sections.append("- [ ] Add material category validation to input processing")
        doc_sections.append("- [ ] Create material-specific test cases")
        doc_sections.append("- [ ] Update documentation and examples")
        doc_sections.append("- [ ] Monitor validation errors and improve rules")
        doc_sections.append("")
        
        return "\n".join(doc_sections)


def create_example_configuration() -> Dict[str, Any]:
    """Create example configuration for the exception handling system"""
    return {
        "ai_prompt_exceptions": {
            "enabled": True,
            "validation_level": "strict",  # strict, moderate, permissive
            "material_categories": {
                "wood": {
                    "property_replacements": {
                        "meltingPoint": "decompositionTemperature"
                    },
                    "unit_overrides": {
                        "hardness": "kN"
                    },
                    "range_limits": {
                        "density": [0.16, 1.4],
                        "thermalConductivity": [0.04, 0.4]
                    },
                    "required_considerations": [
                        "grain_direction",
                        "moisture_content"
                    ]
                },
                "ceramic": {
                    "unit_preferences": {
                        "hardness": "Mohs"
                    },
                    "emphasis": {
                        "compressive_over_tensile": True,
                        "thermal_shock_resistance": True
                    },
                    "range_limits": {
                        "thermalConductivity": [0.5, 200]
                    }
                },
                "metal": {
                    "expected_properties": {
                        "high_thermal_conductivity": True,
                        "high_reflectance": True,
                        "electrical_conductivity": True
                    },
                    "range_limits": {
                        "thermalConductivity": [1, 500],
                        "reflectance": [60, 98]
                    },
                    "considerations": [
                        "surface_oxidation",
                        "alloy_composition"
                    ]
                }
            },
            "component_integration": {
                "metricsproperties": {
                    "validate_property_ranges": True,
                    "enforce_unit_consistency": True,
                    "material_specific_descriptions": True
                },
                "metricsmachinesettings": {
                    "material_optical_properties": True,
                    "thermal_considerations": True,
                    "damage_threshold_validation": True
                },
                "text": {
                    "material_specific_terminology": True,
                    "category_appropriate_focus": True,
                    "technical_accuracy_validation": True
                },
                "frontmatter": {
                    "property_validation": True,
                    "unit_standardization": True,
                    "range_checking": True
                }
            }
        }
    }


if __name__ == "__main__":
    # Generate integration guide
    guide = ComponentIntegrationGuide()
    documentation = guide.generate_integration_documentation()
    
    # Save documentation
    doc_path = Path(__file__).parent / "INTEGRATION_GUIDE.md"
    with open(doc_path, 'w') as f:
        f.write(documentation)
    
    print(f"Integration guide saved to: {doc_path}")
    
    # Save example configuration
    config = create_example_configuration()
    config_path = Path(__file__).parent / "exception_handling_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"Example configuration saved to: {config_path}")
    
    # Print summary
    print("\n=== AI PROMPT EXCEPTION HANDLING SYSTEM ===")
    print("Created comprehensive exception handling for material-specific AI prompts:")
    print("1. Material Exception Handler - Core exception rules")
    print("2. Material Aware Generator - Prompt generation with exceptions")
    print("3. Integration Guide - How to integrate with existing components")
    print("4. Example Configuration - Configuration templates")
    print("")
    print("Key Benefits:")
    print("- Wood materials get decomposition temperature instead of melting point")
    print("- Ceramic materials use appropriate hardness scales (Mohs)")
    print("- Metal materials get validated thermal conductivity ranges")
    print("- Proper validation prevents physically impossible property values")
    print("- Material-specific terminology and focus in generated content")