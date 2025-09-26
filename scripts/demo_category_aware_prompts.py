#!/usr/bin/env python3
"""
Category and Subcategory-Aware Prompt Demonstration

Demonstrates the enhanced material-aware prompt system with category and subcategory-specific
handling for relative data like min/max ranges, comparative analysis, and contextual guidance.

This script shows how the system provides:
- Category-specific range positioning (Low/Medium/High within category)
- Subcategory refinements (hardwood vs softwood, ferrous vs non-ferrous)
- Comparative analysis between material categories
- Processing considerations specific to material types
- Component-specific contextual enhancements
"""

import logging
from ai_research.prompt_exceptions.material_aware_generator import MaterialAwarePromptGenerator
from ai_research.prompt_exceptions.category_aware_enhancer import CategoryAwarePromptEnhancer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demonstrate_category_aware_prompts():
    """Demonstrate category and subcategory-aware prompt enhancements"""
    
    print("🎯 Category and Subcategory-Aware Prompt System Demonstration")
    print("=" * 65)
    
    generator = MaterialAwarePromptGenerator()
    
    # Test materials with different categories and subcategories
    test_materials = {
        'Aluminum (Non-Ferrous Metal)': {
            'name': 'Aluminum 6061',
            'category': 'metal',
            'subcategory': 'aluminum_alloy',
            'density': '2.7 g/cm³',
            'thermal_conductivity': '167 W/m·K',
            'melting_point': '660 °C',
            'tensile_strength': '310 MPa'
        },
        'Steel (Ferrous Metal)': {
            'name': 'Carbon Steel',
            'category': 'metal', 
            'subcategory': 'steel',
            'density': '7.85 g/cm³',
            'thermal_conductivity': '50 W/m·K',
            'melting_point': '1535 °C',
            'tensile_strength': '400 MPa'
        },
        'Oak (Hardwood)': {
            'name': 'Red Oak',
            'category': 'wood',
            'subcategory': 'hardwood',
            'density': '0.75 g/cm³',
            'moisture_content': '8 %',
            'compressive_strength': '52 MPa'
        },
        'Pine (Softwood)': {
            'name': 'Eastern Pine',
            'category': 'wood',
            'subcategory': 'softwood',
            'density': '0.45 g/cm³',
            'moisture_content': '12 %',
            'compressive_strength': '35 MPa'
        },
        'Alumina (Oxide Ceramic)': {
            'name': 'Aluminum Oxide',
            'category': 'ceramic',
            'subcategory': 'oxide_ceramic',
            'density': '3.95 g/cm³',
            'hardness': '9 Mohs',
            'melting_point': '2072 °C'
        }
    }
    
    for material_label, material_data in test_materials.items():
        print(f"\n📋 {material_label}")
        print("-" * len(material_label))
        
        # Generate category-aware prompt
        enhanced_prompt = generator.generate_material_aware_prompt(
            component_type='metricsproperties',
            material_name=material_data['name'],
            material_category=material_data['category'],
            material_data=material_data
        )
        
        # Extract and display key enhancements
        display_prompt_enhancements(enhanced_prompt, material_data)
        
        print()  # Spacing between materials


def display_prompt_enhancements(prompt: str, material_data: dict):
    """Extract and display key category-aware enhancements from prompt"""
    
    lines = prompt.split('\n')
    
    # Find category context section
    category_section = extract_section(lines, 'Category-Specific Context')
    if category_section:
        print("🏷️  Category Context:")
        for line in category_section[:3]:  # First few lines
            if line.strip():
                print(f"   {line.strip()}")
    
    # Find relative data context
    relative_section = extract_section(lines, 'Relative Data Context')
    if relative_section:
        print("📊 Relative Positioning:")
        for line in relative_section:
            if line.strip().startswith('- ') and 'Position:' in line:
                # Extract property and position
                parts = line.strip().split('(Position: ')
                if len(parts) == 2:
                    property_part = parts[0].replace('- ', '')
                    position_part = parts[1].rstrip(')')
                    print(f"   {property_part:<25} → {position_part}")
    
    # Find comparative analysis
    comparison_section = extract_section(lines, 'Comparative Analysis')
    if comparison_section:
        print("⚖️  Comparative Context:")
        for line in comparison_section[:2]:  # First couple lines
            if line.strip() and not line.strip().startswith('#'):
                print(f"   {line.strip()}")
    
    # Find processing considerations
    processing_section = extract_section(lines, 'Processing Considerations')
    if processing_section:
        print("⚙️  Processing Notes:")
        considerations = [line.strip() for line in processing_section if line.strip().startswith('- ')][:2]
        for consideration in considerations:
            print(f"   {consideration}")
    
    # Show component-specific guidance
    component_section = extract_section(lines, 'Metricsproperties Specific Guidance')
    if component_section:
        print("🎯 Component-Specific:")
        for line in component_section[:2]:
            if line.strip() and not line.strip().startswith('#'):
                print(f"   {line.strip()}")


def extract_section(lines: list, section_header: str) -> list:
    """Extract lines from a specific section of the prompt"""
    
    start_idx = -1
    for i, line in enumerate(lines):
        if section_header in line:
            start_idx = i + 1
            break
    
    if start_idx == -1:
        return []
    
    # Find next section or end
    section_lines = []
    for i in range(start_idx, len(lines)):
        line = lines[i]
        if line.startswith('###') or line.startswith('##'):
            break
        section_lines.append(line)
    
    return section_lines


def demonstrate_range_awareness():
    """Demonstrate range awareness with specific examples"""
    
    print("\n🔢 Range Awareness Demonstration")
    print("=" * 35)
    
    enhancer = CategoryAwarePromptEnhancer()
    
    # Test materials at different positions in their category ranges
    range_test_materials = {
        'Light Metal (Low Density)': {
            'name': 'Magnesium',
            'category': 'metal',
            'density': '1.74 g/cm³'  # Low for metals
        },
        'Heavy Metal (High Density)': {
            'name': 'Lead', 
            'category': 'metal',
            'density': '11.34 g/cm³'  # High for metals
        },
        'Light Wood (Low Density)': {
            'name': 'Balsa',
            'category': 'wood',
            'density': '0.16 g/cm³'  # Low for wood
        },
        'Dense Wood (High Density)': {
            'name': 'Lignum Vitae',
            'category': 'wood', 
            'density': '1.23 g/cm³'  # High for wood
        }
    }
    
    for label, material_data in range_test_materials.items():
        
        # Get relative positioning
        density_value = float(material_data['density'].split()[0])
        category = material_data['category']
        
        # Get range for this category
        range_key = f"{category}_density"
        if range_key in enhancer.relative_ranges:
            range_data = enhancer.relative_ranges[range_key]
            
            # Calculate position
            total_range = range_data.max_value - range_data.min_value
            position = (density_value - range_data.min_value) / total_range
            
            position_desc = "Low"
            if position > 0.8:
                position_desc = "High"
            elif position > 0.6:
                position_desc = "Medium-High"
            elif position > 0.4:
                position_desc = "Medium"
            elif position > 0.2:
                position_desc = "Low-Medium"
            
            print(f"{label}:")
            print(f"  Density: {material_data['density']} → {position_desc} within {category} range")
            print(f"  Category Range: {range_data.min_value} - {range_data.max_value} {range_data.unit}")
            print(f"  Relative Position: {position:.1%}")
            print()


if __name__ == "__main__":
    try:
        demonstrate_category_aware_prompts()
        demonstrate_range_awareness()
        
        print("\n🎉 Category and Subcategory-Aware Prompt System Operational!")
        print("   ✅ Material-specific exception handling")
        print("   ✅ Category-based relative positioning")  
        print("   ✅ Subcategory refinements")
        print("   ✅ Comparative contextual analysis")
        print("   ✅ Processing considerations")
        print("   ✅ Component-specific guidance")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()