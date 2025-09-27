#!/usr/bin/env python3
"""
Properties Redundancy Analysis - Targeted

This script analyzes the specific property redundancy patterns in the materials.yaml
structure, focusing on the massive duplication in composite materials and others.
"""

import yaml
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

def analyze_property_redundancy():
    """Analyze property redundancy with focus on actual material data structure."""
    
    print("🔍 PROPERTIES REDUNDANCY ANALYSIS - TARGETED")
    print("=" * 60)
    
    # Load materials.yaml  
    materials_file = Path("data/materials.yaml")
    if not materials_file.exists():
        print("❌ materials.yaml not found")
        return
        
    with open(materials_file, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    print(f"📂 Loaded materials.yaml")
    
    # Extract actual materials from the nested structure
    categories_with_materials = materials_data.get('materials', {})
    
    print(f"📊 Found {len(categories_with_materials)} material categories")
    
    all_materials = {}
    category_material_count = {}
    
    for category_name, category_data in categories_with_materials.items():
        if isinstance(category_data, dict) and 'items' in category_data:
            materials_list = category_data['items']
            category_material_count[category_name] = len(materials_list)
            
            for material in materials_list:
                if isinstance(material, dict) and 'name' in material:
                    material_name = material['name']
                    all_materials[material_name] = {
                        'category': category_name,
                        'data': material
                    }
    
    print(f"📋 Material counts by category:")
    for category, count in category_material_count.items():
        print(f"   📊 {category}: {count} materials")
    
    total_materials = len(all_materials)
    print(f"📊 Total materials analyzed: {total_materials}")
    
    # Analyze property patterns
    print(f"\n🔍 PROPERTY REDUNDANCY ANALYSIS:")
    
    # Track property structures and values
    property_types = ['thermal_properties', 'mechanical_properties', 'electrical_properties', 'processing_properties']
    property_analysis = {}
    
    for prop_type in property_types:
        print(f"\n   📋 {prop_type.upper()} ANALYSIS:")
        
        materials_with_prop = []
        property_values = defaultdict(Counter)
        property_structures = defaultdict(list)
        exact_matches = defaultdict(list)
        
        for material_name, material_info in all_materials.items():
            material_data = material_info['data']
            category = material_info['category']
            
            if prop_type in material_data:
                materials_with_prop.append(material_name)
                prop_data = material_data[prop_type]
                
                if isinstance(prop_data, dict):
                    # Track structure (keys)
                    structure = tuple(sorted(prop_data.keys()))
                    property_structures[structure].append({
                        'material': material_name,
                        'category': category,
                        'data': prop_data
                    })
                    
                    # Track individual property values
                    for prop_name, prop_value in prop_data.items():
                        property_values[prop_name][prop_value] += 1
                        
                    # Track exact property set matches
                    exact_match_key = tuple(sorted(f"{k}:{v}" for k, v in prop_data.items()))
                    exact_matches[exact_match_key].append({
                        'material': material_name,
                        'category': category
                    })
        
        materials_count = len(materials_with_prop)
        coverage = (materials_count / total_materials) * 100 if total_materials > 0 else 0
        
        print(f"      📊 Materials with {prop_type}: {materials_count}/{total_materials} ({coverage:.1f}%)")
        
        # Analyze structural consistency
        print(f"      📋 Property structures found: {len(property_structures)}")
        
        structure_redundancy = []
        for structure, materials_list in property_structures.items():
            if len(materials_list) > 1:
                categories_using = set(m['category'] for m in materials_list)
                structure_redundancy.append({
                    'structure': structure,
                    'materials_count': len(materials_list),
                    'categories': list(categories_using),
                    'materials': [m['material'] for m in materials_list]
                })
        
        # Sort by redundancy level
        structure_redundancy.sort(key=lambda x: x['materials_count'], reverse=True)
        
        if structure_redundancy:
            print(f"      🔄 Redundant structures: {len(structure_redundancy)}")
            
            for i, redundancy in enumerate(structure_redundancy[:3], 1):  # Show top 3
                count = redundancy['materials_count']
                categories = redundancy['categories']
                structure = redundancy['structure']
                
                print(f"         {i}. Structure {structure}")
                print(f"            📊 {count} materials across {len(categories)} categories")
                print(f"            📁 Categories: {', '.join(categories)}")
                print(f"            📋 Materials: {', '.join(redundancy['materials'][:5])}{' ...' if len(redundancy['materials']) > 5 else ''}")
        
        # Analyze exact value matches (complete duplication)
        exact_duplications = [(key, materials_list) for key, materials_list in exact_matches.items() 
                             if len(materials_list) > 1]
        exact_duplications.sort(key=lambda x: len(x[1]), reverse=True)
        
        if exact_duplications:
            print(f"      ⚠️  EXACT DUPLICATIONS: {len(exact_duplications)}")
            
            total_duplicate_entries = 0
            for i, (exact_key, materials_list) in enumerate(exact_duplications[:3], 1):  # Show top 3
                duplicate_count = len(materials_list) - 1  # Subtract original
                total_duplicate_entries += duplicate_count
                
                categories = set(m['category'] for m in materials_list)
                materials_names = [m['material'] for m in materials_list]
                
                print(f"         {i}. Exact duplicate property set:")
                print(f"            🔄 {len(materials_list)} materials with identical values")
                print(f"            📊 {duplicate_count} redundant entries")
                print(f"            📁 Categories: {', '.join(categories)}")
                print(f"            📋 Materials: {', '.join(materials_names[:5])}{' ...' if len(materials_names) > 5 else ''}")
                
                # Show the actual duplicated values (first few)
                example_material = materials_list[0]
                example_data = all_materials[example_material['material']]['data'][prop_type]
                print(f"            💡 Example values: {list(example_data.items())[:3]}")
            
            print(f"      🎯 Total eliminatable entries in {prop_type}: {total_duplicate_entries}")
        else:
            total_duplicate_entries = 0
            print(f"      ✅ No exact duplications found")
        
        # Analyze individual property value redundancy
        high_redundancy_props = []
        for prop_name, value_counts in property_values.items():
            total_occurrences = sum(value_counts.values())
            if total_occurrences > 1:
                most_common_value, most_common_count = value_counts.most_common(1)[0]
                if most_common_count >= total_occurrences * 0.5:  # 50% or more use same value
                    redundancy_rate = (most_common_count / total_occurrences) * 100
                    high_redundancy_props.append({
                        'property': prop_name,
                        'common_value': most_common_value,
                        'frequency': most_common_count,
                        'total_occurrences': total_occurrences,
                        'redundancy_rate': redundancy_rate
                    })
        
        high_redundancy_props.sort(key=lambda x: x['redundancy_rate'], reverse=True)
        
        if high_redundancy_props:
            print(f"      📈 High redundancy individual properties: {len(high_redundancy_props)}")
            for prop_info in high_redundancy_props[:3]:  # Show top 3
                prop_name = prop_info['property']
                value = prop_info['common_value']
                rate = prop_info['redundancy_rate']
                freq = prop_info['frequency']
                total = prop_info['total_occurrences']
                
                print(f"         • {prop_name}: '{value}' appears {freq}/{total} times ({rate:.1f}%)")
        
        property_analysis[prop_type] = {
            'materials_count': materials_count,
            'coverage_percentage': coverage,
            'structure_redundancies': len(structure_redundancy),
            'exact_duplications': len(exact_duplications),
            'eliminatable_entries': total_duplicate_entries,
            'high_redundancy_properties': len(high_redundancy_props)
        }
    
    # Overall consolidation assessment
    print(f"\n🏆 OVERALL CONSOLIDATION ASSESSMENT:")
    
    total_eliminatable = sum(analysis['eliminatable_entries'] for analysis in property_analysis.values())
    total_exact_duplications = sum(analysis['exact_duplications'] for analysis in property_analysis.values())
    total_structure_redundancies = sum(analysis['structure_redundancies'] for analysis in property_analysis.values())
    
    print(f"   🎯 Total eliminatable property entries: {total_eliminatable}")
    print(f"   🔄 Total exact property set duplications: {total_exact_duplications}")
    print(f"   📋 Total redundant structures: {total_structure_redundancies}")
    
    # Calculate potential savings
    if total_eliminatable > 0:
        print(f"\n💡 CONSOLIDATION STRATEGY:")
        print(f"   🎯 Primary opportunity: Category-level property defaults")
        print(f"   📊 Estimated redundancy reduction: {total_eliminatable} entries")
        print(f"   🏗️ Implementation: Enhanced materialPropertiesDefinitions with inheritance")
        print(f"   ✨ Approach: Category defaults + material-specific overrides")
        
        # Specific recommendations by category
        category_recommendations = defaultdict(list)
        
        for prop_type, analysis in property_analysis.items():
            if analysis['eliminatable_entries'] > 0:
                category_recommendations['high_priority'].append({
                    'property_type': prop_type,
                    'eliminatable': analysis['eliminatable_entries'],
                    'duplications': analysis['exact_duplications']
                })
        
        if category_recommendations['high_priority']:
            print(f"\n   🎯 HIGH PRIORITY CONSOLIDATIONS:")
            for rec in sorted(category_recommendations['high_priority'], 
                            key=lambda x: x['eliminatable'], reverse=True):
                prop_type = rec['property_type']
                eliminatable = rec['eliminatable']
                duplications = rec['duplications']
                print(f"      📊 {prop_type}: {eliminatable} eliminatable entries from {duplications} exact duplications")
    else:
        print(f"\n🎉 EXCELLENT NEWS:")
        print(f"   ✅ No significant property redundancy detected")
        print(f"   🏆 Properties appear well-optimized already!")
    
    # Save analysis results
    analysis_results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "total_materials_analyzed": total_materials,
        "category_material_counts": category_material_count,
        "property_analysis": property_analysis,
        "consolidation_metrics": {
            "total_eliminatable_entries": total_eliminatable,
            "total_exact_duplications": total_exact_duplications,
            "total_structure_redundancies": total_structure_redundancies
        }
    }
    
    report_file = "properties_redundancy_analysis.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed analysis saved to: {report_file}")
    
    return analysis_results

if __name__ == "__main__":
    analyze_property_redundancy()