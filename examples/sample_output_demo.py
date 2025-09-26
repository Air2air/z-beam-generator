#!/usr/bin/env python3
"""
Sample Enhanced Frontmatter Output
Shows complete output structure for a material using our enhancement system
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

def show_sample_output(material_name: str):
    """Show complete sample output for a material"""
    print(f"🎯 SAMPLE ENHANCED FRONTMATTER OUTPUT: {material_name.upper()}")
    print("=" * 60)
    
    # Load existing frontmatter
    existing_frontmatter = load_existing_frontmatter(material_name)
    if not existing_frontmatter:
        print(f"❌ No existing frontmatter found for {material_name}")
        return
    
    print(f"📄 Original frontmatter: {len(existing_frontmatter)} sections")
    
    # Load materials data
    materials_data = load_materials_data(material_name)
    if not materials_data:
        print(f"❌ No materials data found for {material_name}")
        return
    
    print(f"📊 Materials.yaml data: {len(materials_data)} fields available")
    
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
            
            print(f"✅ Enhanced frontmatter: {len(enhanced_frontmatter)} sections")
            print()
            
            # Show the complete enhanced output
            print("📋 COMPLETE ENHANCED FRONTMATTER STRUCTURE:")
            print("-" * 50)
            
            # Show key sections with preview
            key_sections = [
                'name', 'category', 'title', 'headline', 'description', 'keywords',
                'technicalProperties', 'machineSettings', 'chemicalProperties',
                'applications', 'compatibility', 'regulatoryStandards',
                'laserInteraction', 'enhancement'
            ]
            
            for section in key_sections:
                if section in enhanced_frontmatter:
                    value = enhanced_frontmatter[section]
                    if isinstance(value, dict):
                        if section == 'technicalProperties':
                            print(f"📐 {section}: {len(value)} properties")
                            for i, (k, v) in enumerate(list(value.items())[:3]):
                                print(f"    • {k}: {v}")
                            if len(value) > 3:
                                print(f"    • ... and {len(value) - 3} more properties")
                        elif section == 'machineSettings':
                            print(f"⚙️ {section}: {len(value)} parameters")
                            for i, (k, v) in enumerate(list(value.items())[:3]):
                                print(f"    • {k}: {v}")
                            if len(value) > 3:
                                print(f"    • ... and {len(value) - 3} more parameters")
                        elif section == 'enhancement':
                            print(f"🔧 {section}: Enhancement metadata")
                            print(f"    • level: {value.get('level', 'unknown')}")
                            print(f"    • materials_yaml_utilization: {value.get('materials_yaml_utilization', 'unknown')}%")
                        else:
                            print(f"📄 {section}: {len(value)} fields")
                    elif isinstance(value, list):
                        print(f"📝 {section}: {len(value)} items")
                        for item in value[:2]:
                            if isinstance(item, str):
                                print(f"    • {item[:60]}{'...' if len(str(item)) > 60 else ''}")
                            else:
                                print(f"    • {str(item)[:60]}{'...' if len(str(item)) > 60 else ''}")
                        if len(value) > 2:
                            print(f"    • ... and {len(value) - 2} more items")
                    else:
                        value_str = str(value)
                        if len(value_str) > 80:
                            print(f"📄 {section}: {value_str[:77]}...")
                        else:
                            print(f"📄 {section}: {value_str}")
                    print()
            
            # Show enhancement statistics
            print("📊 ENHANCEMENT STATISTICS:")
            print("-" * 30)
            print(f"Original sections: {len(existing_frontmatter)}")
            print(f"Enhanced sections: {len(enhanced_frontmatter)}")
            print(f"New sections added: {len(enhanced_frontmatter) - len(existing_frontmatter)}")
            
            # Show data utilization
            enhancement_info = enhanced_frontmatter.get('enhancement', {})
            if enhancement_info:
                print(f"Materials.yaml utilization: {enhancement_info.get('materials_yaml_utilization', 'unknown')}%")
                print(f"Enhancement level: {enhancement_info.get('level', 'unknown')}")
                print(f"Processing time: {enhancement_info.get('processing_time_seconds', 'unknown')}s")
        
        else:
            print("❌ Enhancement mapper not available")
            
    except Exception as e:
        print(f"❌ Enhancement failed: {e}")

def main():
    """Show sample outputs for different materials"""
    materials_to_test = ["aluminum", "glass", "carbon-fiber-reinforced-polymer"]
    
    print("🎨 ENHANCED FRONTMATTER SAMPLE OUTPUTS")
    print("=" * 45)
    print("Demonstrating the quality and structure of our enhanced frontmatter system")
    print()
    
    for material in materials_to_test:
        show_sample_output(material)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
