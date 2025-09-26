#!/usr/bin/env python3
"""
Show Complete Enhanced YAML Output
Displays the actual YAML structure that would be generated
"""

import sys
import yaml
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_materials_data(material_name: str) -> dict:
    """Load material data from Materials.yaml"""
    materials_path = project_root / "data" / "Materials.yaml"
    
    if not materials_path.exists():
        return {}
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        all_data = yaml.safe_load(f)
    
    def search_materials(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    for material in value:
                        if isinstance(material, dict) and material.get('name', '').lower() == material_name.lower():
                            return material
                elif isinstance(value, dict):
                    result = search_materials(value)
                    if result:
                        return result
        return None
    
    return search_materials(all_data) or {}

def load_existing_frontmatter(material_name: str) -> dict:
    """Load existing frontmatter file"""
    frontmatter_path = project_root / "frontmatter" / "materials" / f"{material_name.lower()}.yaml"
    
    if not frontmatter_path.exists():
        return {}
    
    with open(frontmatter_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def show_yaml_output_sample():
    """Show actual YAML output sample"""
    material_name = "aluminum"
    
    print("📄 COMPLETE ENHANCED FRONTMATTER YAML OUTPUT SAMPLE")
    print("=" * 60)
    print(f"Material: {material_name.title()}")
    print("=" * 60)
    
    # Load data
    existing_frontmatter = load_existing_frontmatter(material_name)
    materials_data = load_materials_data(material_name)
    
    if not existing_frontmatter or not materials_data:
        print("❌ Required data not available")
        return
    
    try:
        from components.frontmatter.enhancement.additive_enhancer import AdditiveFrontmatterEnhancer
        
        enhancer = AdditiveFrontmatterEnhancer()
        
        if enhancer.mapper:
            enhanced_frontmatter = enhancer.enhance_frontmatter_additively(
                existing_frontmatter=existing_frontmatter.copy(),
                material_data=materials_data,
                material_name=material_name,
                enhancement_level="comprehensive"
            )
            
            # Show the first 100 lines of YAML output
            yaml_output = yaml.dump(enhanced_frontmatter, default_flow_style=False, allow_unicode=True, width=80)
            yaml_lines = yaml_output.split('\n')
            
            print("YAML OUTPUT (first 80 lines):")
            print("-" * 40)
            for i, line in enumerate(yaml_lines[:80]):
                print(f"{i+1:3d} | {line}")
            
            if len(yaml_lines) > 80:
                print(f"... and {len(yaml_lines) - 80} more lines")
            
            print(f"\n📊 OUTPUT STATISTICS:")
            print(f"Total YAML lines: {len(yaml_lines)}")
            print(f"Total sections: {len(enhanced_frontmatter)}")
            print(f"File size: ~{len(yaml_output)} characters")
            
        else:
            print("❌ Enhancement mapper not available")
            
    except Exception as e:
        print(f"❌ Enhancement failed: {e}")

def show_key_sections_detail():
    """Show key sections in detail"""
    material_name = "steel"  # Use Steel since we know it works
    
    print("\n🔍 KEY SECTIONS DETAILED VIEW")
    print("=" * 40)
    
    existing_frontmatter = load_existing_frontmatter(material_name)
    materials_data = load_materials_data(material_name)
    
    if not existing_frontmatter or not materials_data:
        print("❌ Required data not available")
        return
    
    try:
        from components.frontmatter.enhancement.additive_enhancer import AdditiveFrontmatterEnhancer
        
        enhancer = AdditiveFrontmatterEnhancer()
        
        if enhancer.mapper:
            enhanced_frontmatter = enhancer.enhance_frontmatter_additively(
                existing_frontmatter=existing_frontmatter.copy(),
                material_data=materials_data,
                material_name=material_name,
                enhancement_level="comprehensive"
            )
            
            # Show specific sections in detail
            sections_to_show = ['machineSettings', 'technicalProperties', 'applications', 'laserInteraction']
            
            for section in sections_to_show:
                if section in enhanced_frontmatter:
                    print(f"\n🔧 {section.upper()} SECTION:")
                    print("-" * 30)
                    section_yaml = yaml.dump({section: enhanced_frontmatter[section]}, 
                                           default_flow_style=False, allow_unicode=True, width=80)
                    section_lines = section_yaml.split('\n')[:20]  # First 20 lines
                    for line in section_lines:
                        print(f"  {line}")
                    if len(section_yaml.split('\n')) > 20:
                        print(f"  ... (truncated for display)")
            
        else:
            print("❌ Enhancement mapper not available")
            
    except Exception as e:
        print(f"❌ Enhancement failed: {e}")

def main():
    """Show complete YAML output samples"""
    show_yaml_output_sample()
    show_key_sections_detail()

if __name__ == "__main__":
    main()
