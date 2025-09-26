#!/usr/bin/env python3
"""
Demo: Material Research Integration

Demonstrates how the new material research system integrates with 
the existing Z-Beam generator to enhance material-specific content.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from research.material_property_researcher import MaterialPropertyResearcher
from data.materials import get_material_by_name
import json


def demonstrate_research_integration(material_name: str):
    """Show how research enhances material understanding"""
    
    print(f"🔬 MATERIAL RESEARCH DEMONSTRATION: {material_name}")
    print("=" * 60)
    
    # Initialize researcher
    researcher = MaterialPropertyResearcher()
    
    # Get current material data
    try:
        current_material = get_material_by_name(material_name)
        print(f"\n📊 CURRENT MATERIAL DATA:")
        if current_material:
            print(f"  Category: {current_material.get('category', 'Unknown')}")
            print(f"  Subcategory: {current_material.get('subcategory', 'None')}")
            
            # Show existing properties
            properties = current_material.get('properties', {})
            if properties:
                print(f"  Existing properties: {len(properties)} fields")
                for prop_name in list(properties.keys())[:3]:  # Show first 3
                    print(f"    - {prop_name}")
            else:
                print("  No existing properties found")
        else:
            print(f"  ❌ Material '{material_name}' not found in database")
            return
            
    except Exception as e:
        print(f"  ❌ Error loading material: {e}")
        return
    
    # Step 1: Research scientific properties
    print(f"\n🧪 STEP 1: SCIENTIFIC PROPERTY RESEARCH")
    properties_research = researcher.research_material_properties(material_name)
    
    if 'error' in properties_research:
        print(f"  ❌ Error: {properties_research['error']}")
        return
    
    recommended_props = properties_research.get('recommended_properties', [])
    print(f"  ✅ Found {len(recommended_props)} recommended properties")
    
    # Show high-priority missing properties
    critical_missing = [p for p in recommended_props 
                       if p['research_priority'] == 1 and p['current_value'] is None]
    
    if critical_missing:
        print(f"  🚨 {len(critical_missing)} CRITICAL missing properties:")
        for prop in critical_missing[:5]:  # Show top 5
            score = prop['laser_relevance_score']
            print(f"    - {prop['field_key']}: {prop['common_name']} (relevance: {score:.1f})")
    
    # Step 2: Research machine settings
    print(f"\n⚙️ STEP 2: MACHINE SETTINGS RESEARCH")
    settings_research = researcher.research_machine_settings(material_name)
    
    if 'error' in settings_research:
        print(f"  ❌ Error: {settings_research['error']}")
        return
    
    recommended_settings = settings_research.get('recommended_settings', [])
    print(f"  ✅ Found {len(recommended_settings)} recommended settings")
    
    # Show high material dependency settings
    material_specific = [s for s in recommended_settings 
                        if s['material_dependency'] > 0.8]
    
    if material_specific:
        print(f"  🎯 {len(material_specific)} MATERIAL-SPECIFIC settings:")
        for setting in material_specific[:3]:  # Show top 3
            dependency = setting['material_dependency']
            units = ', '.join(setting['units'])
            print(f"    - {setting['field_key']}: {setting['parameter_name']} ({units}) - dependency: {dependency:.1f}")
    
    # Step 3: Schema field analysis for key field
    print(f"\n📋 STEP 3: SCHEMA INTEGRATION ANALYSIS")
    
    # Pick a high-priority field for analysis
    key_field = None
    if critical_missing:
        key_field = critical_missing[0]['field_key']
    elif material_specific:
        key_field = material_specific[0]['field_key']
    
    if key_field:
        field_analysis = researcher.research_schema_field_values(key_field, material_name)
        print(f"  🔍 Analyzing field: {key_field}")
        
        recommendations = field_analysis.get('recommendations', [])
        if recommendations:
            print(f"  💡 {len(recommendations)} recommendations:")
            for rec in recommendations[:2]:  # Show first 2
                print(f"    - {rec}")
        
        # Show schema validation info
        schema_def = field_analysis.get('schema_definition')
        if schema_def and 'properties' in schema_def:
            props = list(schema_def['properties'].keys())
            print(f"  📊 Schema supports {len(props)} validation fields")
    
    # Generate enhancement summary
    print(f"\n📈 ENHANCEMENT OPPORTUNITIES:")
    
    total_recommended = len(recommended_props) + len(recommended_settings)
    current_props = len(current_material.get('properties', {}))
    current_settings = len(current_material.get('machineSettings', {}))
    current_total = current_props + current_settings
    
    enhancement_potential = total_recommended - current_total
    if enhancement_potential > 0:
        print(f"  🚀 Could add {enhancement_potential} new fields")
        print(f"  📊 Current: {current_total} fields → Potential: {total_recommended} fields")
        print(f"  📈 Enhancement factor: {total_recommended/max(current_total, 1):.1f}x")
    else:
        print(f"  ✅ Material data appears comprehensive")
    
    # Show special considerations
    special_considerations = properties_research.get('special_considerations', [])
    if special_considerations:
        print(f"\n⚠️  SPECIAL CONSIDERATIONS:")
        for consideration in special_considerations[:3]:
            print(f"    • {consideration}")
    
    print(f"\n✅ Research complete for {material_name}")


def compare_materials_research(materials: list):
    """Compare research findings across multiple materials"""
    
    print(f"\n🔍 COMPARATIVE MATERIAL RESEARCH")
    print("=" * 50)
    
    researcher = MaterialPropertyResearcher()
    
    comparison_data = {}
    
    for material in materials:
        print(f"\n📊 Researching {material}...")
        
        # Get basic research data
        props_research = researcher.research_material_properties(material)
        settings_research = researcher.research_machine_settings(material)
        
        if 'error' not in props_research and 'error' not in settings_research:
            comparison_data[material] = {
                'category': props_research.get('category', 'unknown'),
                'property_count': len(props_research.get('recommended_properties', [])),
                'setting_count': len(settings_research.get('recommended_settings', [])),
                'critical_properties': len([p for p in props_research.get('recommended_properties', []) 
                                          if p['research_priority'] == 1]),
                'high_dependency_settings': len([s for s in settings_research.get('recommended_settings', [])
                                               if s['material_dependency'] > 0.8])
            }
    
    # Display comparison
    if comparison_data:
        print(f"\n📋 RESEARCH SUMMARY:")
        print(f"{'Material':<15} {'Category':<10} {'Properties':<12} {'Settings':<10} {'Critical':<10} {'Mat.Dep.':<8}")
        print("-" * 70)
        
        for material, data in comparison_data.items():
            print(f"{material:<15} {data['category']:<10} {data['property_count']:<12} "
                  f"{data['setting_count']:<10} {data['critical_properties']:<10} {data['high_dependency_settings']:<8}")


def main():
    """Run material research demonstrations"""
    
    # Single material deep dive
    print("🎯 SINGLE MATERIAL RESEARCH DEMO")
    demonstrate_research_integration("Aluminum")
    
    # Multi-material comparison
    materials_to_compare = ["Aluminum", "Stainless Steel", "Ceramic"]
    compare_materials_research(materials_to_compare)
    
    print(f"\n🎓 INTEGRATION LESSONS:")
    print("  1. Research system identifies missing critical properties")
    print("  2. Material-specific machine settings optimization available")
    print("  3. Schema integration ensures proper data structure")
    print("  4. Comparative analysis reveals material-specific needs")
    print("  5. Automated enhancement recommendations provided")


if __name__ == '__main__':
    main()