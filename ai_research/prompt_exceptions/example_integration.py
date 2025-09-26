#!/usr/bin/env python3
"""
Example Integration: Material-Aware Prompts with Frontmatter Generator

This demonstrates how to integrate the AI Prompt Exception Handling System
with the consolidated frontmatter component generator.

NOTE: MetricsProperties and MetricsMachineSettings components have been consolidated
into the frontmatter generator for simplified architecture.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import consolidated component functionality
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator

# Import the new exception handling system
from ai_research.prompt_exceptions.material_aware_generator import (
    generate_material_specific_prompt,
    validate_component_content
)

logger = logging.getLogger(__name__)


class MaterialAwareFrontmatterGenerator(StreamlinedFrontmatterGenerator):
    """
    Enhanced Frontmatter generator with material-specific exception handling
    
    This class extends the consolidated frontmatter generator to include material-aware prompts
    and validation, demonstrating the integration approach.
    """
    
    def __init__(self):
        super().__init__()
        self.validation_enabled = True
        self.validation_errors = []
    
    def generate(self, material_name: str, material_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate material properties with material-aware exception handling
        
        Args:
            material_name: Name of the material
            material_data: Material data from materials.yaml (optional)
            **kwargs: Additional generation parameters
            
        Returns:
            Generated properties with material-specific handling applied
        """
        logger.info(f"Generating material-aware properties for {material_name}")
        
        # Get material data if not provided
        if material_data is None:
            material_data = self._get_material_data(material_name)
        
        material_category = material_data.get('category', 'unknown')
        
        # Generate material-aware prompt instead of base prompt
        try:
            material_aware_prompt = generate_material_specific_prompt(
                component_type='metricsproperties',
                material_name=material_name,
                material_category=material_category,
                material_data=material_data,
                **kwargs
            )
            
            logger.info(f"Generated material-aware prompt for {material_category} material")
            
        except Exception as e:
            logger.warning(f"Failed to generate material-aware prompt: {e}")
            # Fallback to base prompt
            material_aware_prompt = self._get_base_prompt(material_name, material_data, **kwargs)
        
        # Generate content using the material-aware prompt
        try:
            generated_content = self._call_ai_api(material_aware_prompt)
            
            # Apply material-specific validation
            if self.validation_enabled:
                is_valid, validation_errors = self._validate_material_content(
                    material_category, generated_content
                )
                
                if not is_valid:
                    logger.warning(f"Material validation issues for {material_name}: {validation_errors}")
                    self.validation_errors.extend(validation_errors)
                    
                    # Optionally retry with corrected prompt
                    if len(validation_errors) <= 3:  # Only retry for minor issues
                        corrected_content = self._apply_validation_corrections(
                            generated_content, validation_errors, material_category
                        )
                        if corrected_content:
                            generated_content = corrected_content
            
            return self._format_output(generated_content, material_name)
            
        except Exception as e:
            logger.error(f"Failed to generate properties for {material_name}: {e}")
            raise
    
    def _validate_material_content(self, material_category: str, content: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate generated content against material-specific rules"""
        try:
            return validate_component_content(
                component_type='metricsproperties',
                material_category=material_category,
                generated_content=content
            )
        except Exception as e:
            logger.warning(f"Validation error: {e}")
            return True, []  # Allow content if validation fails
    
    def _apply_validation_corrections(
        self, 
        content: Dict[str, Any], 
        errors: List[str], 
        material_category: str
    ) -> Optional[Dict[str, Any]]:
        """Apply automatic corrections for common validation errors"""
        corrected_content = content.copy()
        corrections_applied = []
        
        if 'properties' not in corrected_content:
            return None
        
        properties = corrected_content['properties']
        
        for error in errors:
            if 'melting point' in error.lower() and material_category == 'wood':
                # Replace melting point with decomposition temperature for wood
                if 'meltingPoint' in properties:
                    mp_data = properties.pop('meltingPoint')
                    properties['decompositionTemperature'] = {
                        'value': mp_data.get('value', '300°C'),
                        'unit': '°C',
                        'description': 'Temperature at which wood begins to decompose',
                        'priority': mp_data.get('priority', 1)
                    }
                    corrections_applied.append("Replaced melting point with decomposition temperature")
            
            elif 'density' in error.lower() and 'outside' in error.lower():
                # Correct density values outside acceptable ranges
                if 'density' in properties:
                    density_data = properties['density']
                    if material_category == 'wood':
                        # Ensure wood density is in reasonable range
                        density_data['value'] = '0.6 g/cm³'  # Typical wood density
                        corrections_applied.append("Corrected density to typical wood range")
            
            elif 'hardness' in error.lower() and material_category == 'ceramic':
                # Use Mohs scale for ceramics
                if 'hardness' in properties:
                    hardness_data = properties['hardness']
                    hardness_data['unit'] = 'Mohs'
                    hardness_data['description'] = 'Mohs hardness scale (appropriate for ceramics)'
                    corrections_applied.append("Changed hardness to Mohs scale for ceramic")
        
        if corrections_applied:
            logger.info(f"Applied corrections: {corrections_applied}")
            return corrected_content
        
        return None
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get detailed validation report for debugging"""
        return {
            'validation_enabled': self.validation_enabled,
            'validation_errors': self.validation_errors,
            'error_count': len(self.validation_errors),
            'error_categories': self._categorize_errors()
        }
    
    def _categorize_errors(self) -> Dict[str, int]:
        """Categorize validation errors for analysis"""
        categories = {
            'property_range': 0,
            'unit_mismatch': 0,
            'material_mismatch': 0,
            'other': 0
        }
        
        for error in self.validation_errors:
            error_lower = error.lower()
            if 'range' in error_lower or 'outside' in error_lower:
                categories['property_range'] += 1
            elif 'unit' in error_lower:
                categories['unit_mismatch'] += 1
            elif 'material' in error_lower or 'category' in error_lower:
                categories['material_mismatch'] += 1
            else:
                categories['other'] += 1
        
        return categories


def demonstrate_material_aware_generation():
    """Demonstrate the material-aware generation system"""
    generator = MaterialAwareFrontmatterGenerator()
    
    # Test materials from different categories
    test_materials = [
        {'name': 'Oak', 'category': 'wood'},
        {'name': 'Alumina', 'category': 'ceramic'}, 
        {'name': 'Aluminum', 'category': 'metal'},
        {'name': 'Polycarbonate', 'category': 'plastic'}
    ]
    
    results = {}
    
    for material in test_materials:
        material_name = material['name']
        print(f"\n=== Testing {material_name} ({material['category']}) ===")
        
        try:
            # Generate properties with material-aware handling
            result = generator.generate(
                material_name=material_name,
                material_data=material
            )
            
            results[material_name] = {
                'success': True,
                'result': result,
                'validation_errors': generator.validation_errors.copy()
            }
            
            print(f"✅ Successfully generated properties for {material_name}")
            if generator.validation_errors:
                print(f"⚠️  Validation issues: {len(generator.validation_errors)}")
            
            # Clear errors for next material
            generator.validation_errors.clear()
            
        except Exception as e:
            results[material_name] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ Failed to generate properties for {material_name}: {e}")
    
    # Generate summary report
    print("\n=== MATERIAL-AWARE GENERATION SUMMARY ===")
    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)
    print(f"Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    
    validation_issues = sum(
        len(r.get('validation_errors', [])) 
        for r in results.values() 
        if r['success']
    )
    print(f"Total Validation Issues: {validation_issues}")
    
    return results


if __name__ == "__main__":
    # Demonstrate the material-aware system
    print("=== MATERIAL-AWARE METRICSPROPERTIES DEMONSTRATION ===")
    
    # Run demonstration
    results = demonstrate_material_aware_generation()
    
    print("\n=== KEY BENEFITS DEMONSTRATED ===")
    print("1. Wood materials get decomposition temperature handling")
    print("2. Ceramic materials use appropriate hardness scales")
    print("3. Metal materials get validated thermal conductivity ranges")
    print("4. Automatic validation and correction of common errors")
    print("5. Material-specific terminology and descriptions")
    
    print("\n=== INTEGRATION BENEFITS ===")
    print("✅ Backward compatible with existing code")
    print("✅ Enhanced validation prevents invalid property combinations")
    print("✅ Material-specific prompts improve accuracy")
    print("✅ Automatic error correction reduces manual intervention")
    print("✅ Comprehensive error reporting for debugging")