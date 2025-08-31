#!/usr/bin/env python3
"""
Enhanced Content Generator for Comprehensive Technical Content

This fixes the critical issues with empty sections by ensuring robust pattern utilization
and comprehensive technical content generation from prompt configurations.
"""

import sys
import random
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.content.generator import ContentComponentGenerator

class EnhancedContentGenerator(ContentComponentGenerator):
    """Enhanced version that generates comprehensive technical content."""
    
    def _generate_section_content(self, section_name: str, focus: str, emphasis: str,
                                config: Dict[str, Any], language_patterns: Dict[str, Any],
                                target_words: int, prompt_key: str) -> List[str]:
        """Generate comprehensive content for sections using ALL available prompt patterns."""
        
        content = [f"## {section_name}", ""]
        
        # Use the enhanced generation methods
        if section_name.lower() == 'overview':
            content.extend(self._generate_enhanced_overview(config, language_patterns))
        elif 'properties' in section_name.lower() or 'material' in section_name.lower():
            content.extend(self._generate_enhanced_properties(config, language_patterns, emphasis))
        elif 'application' in section_name.lower():
            content.extend(self._generate_enhanced_applications(config, language_patterns))
        elif 'parameter' in section_name.lower() or 'optimal' in section_name.lower():
            content.extend(self._generate_enhanced_parameters(config, language_patterns))
        elif 'advantage' in section_name.lower() or 'benefit' in section_name.lower():
            content.extend(self._generate_enhanced_advantages(config, language_patterns))
        elif 'safety' in section_name.lower():
            content.extend(self._generate_enhanced_safety(config, language_patterns))
        elif 'challenge' in section_name.lower():
            content.extend(self._generate_enhanced_challenges(config, language_patterns))
        else:
            content.extend(self._generate_enhanced_generic(config, language_patterns, focus))
        
        return content
    
    def _generate_enhanced_overview(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate comprehensive overview content using available patterns."""
        content = []
        material_name = config['subject']
        formula = config['formula']
        
        # Get available patterns dynamically
        opening_patterns = [
            patterns.get('opening'),
            patterns.get('introduction', {}).get('opening'),
            f"This study presents systematic investigation of"
        ]
        opening = next((p for p in opening_patterns if p), f"Laser cleaning technology for {material_name}")
        
        # Formula integration - try multiple pattern sources
        formula_patterns = [
            patterns.get('formula_integration'),
            patterns.get('introduction', {}).get('formula_integration'),
            f"The chemical composition {formula} provides fundamental understanding"
        ]
        formula_text = next((p for p in formula_patterns if p), f"Material composition {formula}")
        
        # Build comprehensive overview
        if '{material_formula}' in str(formula_text):
            intro_text = formula_text.format(material_formula=formula)
        else:
            intro_text = f"{formula_text} of laser-material interaction"
        
        content.append(f"{opening} in materials processing technology for {material_name} laser cleaning applications. {intro_text} for effective surface processing.")
        content.append("")
        
        # Add technical context
        content.append(f"This comprehensive analysis addresses laser cleaning optimization for {material_name} based on material-specific characteristics and processing requirements.")
        
        return content
    
    def _generate_enhanced_properties(self, config: Dict[str, Any], patterns: Dict[str, Any], emphasis: str) -> List[str]:
        """Generate comprehensive properties content with technical details."""
        content = []
        material_name = config['subject']
        
        # Section introduction with pattern-based language
        intro_patterns = [
            patterns.get('section_intro'),
            patterns.get('properties', {}).get('section_intro'),
            patterns.get('introduction'),
            f"Material characteristics require careful analysis"
        ]
        intro = next((p for p in intro_patterns if p), f"Understanding {material_name} properties")
        content.append(f"{intro} for successful laser cleaning of {material_name} surfaces.")
        content.append("")
        
        # Technical properties section
        content.append("**Key Material Properties for Laser Cleaning:**")
        
        # Use material data from config
        thermal_cond = config.get('thermal_conductivity', config.get('material_properties', {}).get('thermalConductivity'))
        density = config.get('density', config.get('material_properties', {}).get('density'))
        melting_point = config.get('melting_point', config.get('material_properties', {}).get('meltingPoint'))
        
        if thermal_cond and thermal_cond != 'Thermal conductivity':
            content.append(f"• **Thermal Properties**: {thermal_cond} affects heat dissipation during laser cleaning")
        
        if density and density != 'Material density':
            content.append(f"• **Physical Properties**: Density of {density} influences laser interaction parameters")
        
        # Add optical properties for laser cleaning
        content.append(f"• **Optical Properties**: Absorption efficiency at 1064 nm determines optimal laser parameters for {material_name}")
        
        # Add laser-specific properties
        content.append(f"• **Laser Interaction**: Surface morphology and contamination type affect cleaning efficiency")
        
        if emphasis:
            content.append("")
            content.append(f"**Cleaning Focus**: {emphasis} for optimal {material_name} surface processing.")
        
        return content
    
    def _generate_enhanced_applications(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate comprehensive applications with industry focus."""
        content = []
        material_name = config['subject']
        
        # Industry introduction
        industrial_patterns = [
            patterns.get('industrial'),
            patterns.get('applications', {}).get('industrial'),
            f"Industrial implementation demonstrates"
        ]
        industrial = next((p for p in industrial_patterns if p), f"Industrial applications show")
        content.append(f"{industrial} the practical value of laser cleaning for {material_name} surface processing:")
        content.append("")
        
        # Application categories
        content.append(f"**Laser Cleaning Applications for {material_name}:**")
        
        # Get frontmatter applications if available
        frontmatter_apps = config.get('frontmatter_data', {}).get('applications', [])
        if frontmatter_apps and isinstance(frontmatter_apps, list):
            for app in frontmatter_apps[:3]:
                if isinstance(app, dict):
                    industry = app.get('industry', 'Industry')
                    detail = app.get('detail', f'{material_name} laser cleaning')
                    content.append(f"• **{industry}**: {detail}")
                else:
                    content.append(f"• **Application**: {app}")
        else:
            # Standard laser cleaning applications
            content.append(f"• **Surface Preparation**: Removal of contaminants and oxides from {material_name}")
            content.append(f"• **Restoration**: Selective cleaning without substrate damage to {material_name}")
            content.append(f"• **Pre-processing**: Surface conditioning for subsequent {material_name} treatments")
        
        # Industry sectors
        sectors_patterns = [
            patterns.get('sectors'),
            patterns.get('applications', {}).get('sectors'),
            f"Multiple sectors benefit"
        ]
        sectors = next((p for p in sectors_patterns if p), f"Various industries utilize")
        content.append("")
        content.append(f"{sectors} laser cleaning technology for specialized {material_name} processing requirements.")
        
        return content
    
    def _generate_enhanced_parameters(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate comprehensive parameter specifications."""
        content = []
        material_name = config['subject']
        
        # Parameter introduction
        content.append(f"Optimal laser parameters for {material_name} cleaning require systematic consideration of material properties and processing objectives:")
        content.append("")
        
        # Technical specifications from frontmatter
        tech_specs = config.get('frontmatter_data', {}).get('technicalSpecifications', {})
        if tech_specs:
            content.append("**Recommended Laser Parameters:**")
            
            if 'wavelength' in tech_specs:
                content.append(f"• **Wavelength**: {tech_specs['wavelength']} for optimal {material_name} absorption")
            
            if 'pulseDuration' in tech_specs:
                content.append(f"• **Pulse Duration**: {tech_specs['pulseDuration']} to minimize thermal effects")
            
            if 'powerRange' in tech_specs:
                content.append(f"• **Power Range**: {tech_specs['powerRange']} optimized for {material_name} processing")
            
            if 'fluenceRange' in tech_specs:
                content.append(f"• **Fluence**: {tech_specs['fluenceRange']} for effective contamination removal")
        else:
            # Standard laser parameters
            content.append("**Standard Laser Parameters:**")
            content.append(f"• **Wavelength**: 1064 nm (primary) for optimal {material_name} absorption characteristics")
            content.append(f"• **Pulse Duration**: 10-100 ns to minimize thermal effects in {material_name}")
            content.append(f"• **Power Density**: 10⁶-10⁸ W/cm² for effective surface cleaning")
            content.append(f"• **Repetition Rate**: 20-100 kHz for processing efficiency")
        
        return content
    
    def _generate_enhanced_advantages(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate comprehensive advantages of laser cleaning."""
        content = []
        material_name = config['subject']
        
        content.append(f"Laser cleaning offers significant advantages for {material_name} processing:")
        content.append("")
        
        # Core advantages
        content.append("**Key Benefits:**")
        content.append(f"• **Precision Control**: Selective cleaning without {material_name} substrate damage")
        content.append(f"• **Environmental Benefits**: Chemical-free process reduces waste disposal requirements")
        content.append(f"• **Process Efficiency**: Non-contact cleaning eliminates mechanical wear concerns")
        content.append(f"• **Quality Consistency**: Automated parameters ensure repeatable {material_name} surface preparation")
        
        # Use pattern-based conclusion if available
        quality_patterns = [
            patterns.get('quality'),
            patterns.get('applications', {}).get('quality'),
            f"Quality control measures indicate"
        ]
        quality = next((p for p in quality_patterns if p), None)
        if quality:
            content.append("")
            content.append(f"• {quality} superior results compared to traditional cleaning methods")
        
        return content
    
    def _generate_enhanced_safety(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate comprehensive safety considerations."""
        content = []
        material_name = config['subject']
        
        # Safety requirements from frontmatter
        safety_class = config.get('frontmatter_data', {}).get('technicalSpecifications', {}).get('safetyClass')
        if safety_class:
            content.append(f"Laser cleaning of {material_name} requires adherence to {safety_class} safety protocols:")
        else:
            content.append(f"Laser cleaning of {material_name} requires comprehensive safety protocols:")
        
        content.append("")
        content.append("**Safety Requirements:**")
        content.append(f"• **Laser Safety**: Class 4 laser systems require full enclosure and interlocks")
        content.append(f"• **Personal Protection**: Appropriate laser safety eyewear and protective equipment")
        content.append(f"• **Ventilation**: Adequate fume extraction for {material_name} processing byproducts")
        content.append(f"• **Training**: Qualified operators familiar with laser safety protocols")
        
        return content
    
    def _generate_enhanced_challenges(self, config: Dict[str, Any], patterns: Dict[str, Any]) -> List[str]:
        """Generate comprehensive challenges and solutions."""
        content = []
        material_name = config['subject']
        
        content.append(f"Successful laser cleaning of {material_name} requires addressing specific technical challenges:")
        content.append("")
        
        content.append("**Technical Considerations:**")
        content.append(f"• **Parameter Optimization**: Balancing cleaning efficiency with {material_name} surface integrity")
        content.append(f"• **Contamination Variation**: Adapting parameters for different contamination types on {material_name}")
        content.append(f"• **Surface Morphology**: Managing heat-affected zones in {material_name} substrates")
        content.append(f"• **Process Monitoring**: Real-time quality control for consistent {material_name} cleaning results")
        
        return content
    
    def _generate_enhanced_generic(self, config: Dict[str, Any], patterns: Dict[str, Any], focus: str) -> List[str]:
        """Generate generic content using available patterns and focus."""
        content = []
        material_name = config['subject']
        
        content.append(f"Technical analysis of {focus} for {material_name} laser cleaning applications.")
        content.append("")
        
        # Use any available patterns
        if patterns:
            first_pattern = next(iter(patterns.values()))
            if isinstance(first_pattern, str):
                content.append(f"{first_pattern} in {material_name} processing applications.")
        
        return content

# Function to test the enhanced generator
def test_enhanced_generator():
    """Test the enhanced content generator."""
    from components.content.generator import load_base_content_prompt, load_persona_prompt
    
    generator = EnhancedContentGenerator()
    
    # Test with sample data
    test_material = "Aluminum"
    test_material_data = {
        'density': '2.70 g/cm³',
        'melting_point': '660.3°C',
        'thermal_conductivity': '205 W/m·K',
        'formula': 'Al'
    }
    
    test_frontmatter = {
        'name': 'Aluminum',
        'author': 'Yi-Chun Lin',
        'authorCountry': 'Taiwan',
        'technicalSpecifications': {
            'wavelength': '1064nm',
            'pulseDuration': '10-100ns',
            'powerRange': '100-500W',
            'safetyClass': 'Class 4'
        },
        'applications': [
            {'industry': 'Electronics', 'detail': 'Semiconductor wafer cleaning'},
            {'industry': 'Automotive', 'detail': 'Component surface preparation'}
        ]
    }
    
    print("🔧 Testing Enhanced Content Generator...")
    
    content = generator._generate_static_content(
        test_material,
        test_material_data,
        frontmatter_data=test_frontmatter
    )
    
    print("✅ Generated Content:")
    print(f"Length: {len(content)} characters")
    print(f"Word count: {len(content.split())} words")
    print("Preview:")
    print(content[:500] + "..." if len(content) > 500 else content)
    
    return content

if __name__ == '__main__':
    test_enhanced_generator()
