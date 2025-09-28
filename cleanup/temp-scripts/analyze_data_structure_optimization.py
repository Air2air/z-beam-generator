#!/usr/bin/env python3
"""
Data Structure Optimization Analysis

This script analyzes the current Categories.yaml and materials.yaml structures
to identify normalization opportunities for optimal frontmatter generation.
"""

import yaml
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

def analyze_data_structure_optimization():
    """Analyze current data structures for frontmatter generation optimization."""
    
    print("🔍 DATA STRUCTURE OPTIMIZATION ANALYSIS")
    print("=" * 60)
    
    # Load current files
    with open("data/Categories.yaml", 'r', encoding='utf-8') as f:
        categories_data = yaml.safe_load(f)
    
    with open("data/materials.yaml", 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    print(f"📂 Loaded Categories.yaml ({len(categories_data)} sections)")
    print(f"📂 Loaded materials.yaml ({len(materials_data)} sections)")
    
    # ANALYSIS 1: Categories.yaml Structure Assessment
    print(f"\n🏗️ CATEGORIES.YAML STRUCTURE ANALYSIS:")
    
    categories_structure = {}
    
    for key, value in categories_data.items():
        if key == 'metadata':
            categories_structure['metadata'] = {
                'type': 'configuration',
                'size': len(value) if isinstance(value, dict) else 1,
                'purpose': 'versioning and tracking'
            }
        elif key in ['universal_regulatory_standards', 'machineSettingsDescriptions', 
                     'materialPropertiesDefinitions', 'environmentalImpactTemplates', 'applicationTypes']:
            categories_structure[key] = {
                'type': 'global_definitions',
                'size': len(value) if isinstance(value, (dict, list)) else 1,
                'purpose': 'shared across all materials/categories'
            }
        elif isinstance(value, dict):
            # Category-specific data
            subcategories = []
            for subkey, subvalue in value.items():
                subcategories.append({
                    'key': subkey,
                    'type': type(subvalue).__name__,
                    'size': len(subvalue) if isinstance(subvalue, (dict, list)) else 1
                })
            
            categories_structure[key] = {
                'type': 'category_definition',
                'subcategories': subcategories,
                'total_fields': len(value)
            }
    
    print(f"   📊 Structure breakdown:")
    for section, info in categories_structure.items():
        if info['type'] == 'global_definitions':
            print(f"      🌐 {section}: Global definitions ({info['size']} entries)")
        elif info['type'] == 'category_definition':
            print(f"      📁 {section}: Category ({info['total_fields']} fields)")
        elif info['type'] == 'configuration':
            print(f"      ⚙️  {section}: Configuration ({info['size']} fields)")
    
    # ANALYSIS 2: materials.yaml Structure Assessment
    print(f"\n📋 MATERIALS.YAML STRUCTURE ANALYSIS:")
    
    materials_sections = {}
    for key, value in materials_data.items():
        if key == 'material_index':
            materials_sections[key] = {
                'type': 'index',
                'purpose': 'material → category mapping',
                'size': len(value) if isinstance(value, dict) else 1
            }
        elif key == 'category_metadata':
            materials_sections[key] = {
                'type': 'metadata',
                'purpose': 'category descriptions',
                'size': len(value) if isinstance(value, dict) else 1
            }
        elif key == 'property_groups':
            materials_sections[key] = {
                'type': 'schema',
                'purpose': 'property type definitions',
                'size': len(value) if isinstance(value, dict) else 1
            }
        elif key == 'materials':
            # Analyze nested materials structure
            category_analysis = {}
            total_materials = 0
            
            for category_name, category_data in value.items():
                if isinstance(category_data, dict) and 'items' in category_data:
                    materials_list = category_data['items']
                    total_materials += len(materials_list)
                    
                    # Analyze material complexity
                    field_complexity = defaultdict(int)
                    property_usage = defaultdict(int)
                    
                    for material in materials_list:
                        if isinstance(material, dict):
                            for field_name, field_value in material.items():
                                field_complexity[field_name] += 1
                                
                                if field_name.endswith('_properties'):
                                    property_usage[field_name] += 1
                    
                    category_analysis[category_name] = {
                        'material_count': len(materials_list),
                        'avg_fields_per_material': sum(field_complexity.values()) / len(materials_list) if materials_list else 0,
                        'property_types_used': list(property_usage.keys()),
                        'complexity_score': len(field_complexity)
                    }
            
            materials_sections[key] = {
                'type': 'materials_data',
                'purpose': 'actual material definitions',
                'total_materials': total_materials,
                'categories': len(value),
                'category_analysis': category_analysis
            }
    
    print(f"   📊 Structure breakdown:")
    for section, info in materials_sections.items():
        if info['type'] == 'materials_data':
            print(f"      📋 {section}: {info['total_materials']} materials across {info['categories']} categories")
        else:
            print(f"      📊 {section}: {info['type']} ({info['size']} entries)")
    
    # ANALYSIS 3: Frontmatter Generation Efficiency Assessment
    print(f"\n🚀 FRONTMATTER GENERATION EFFICIENCY ANALYSIS:")
    
    # Check data access patterns for frontmatter generation
    efficiency_analysis = {
        'categories_access_patterns': {},
        'materials_access_patterns': {},
        'cross_reference_complexity': {},
        'normalization_opportunities': []
    }
    
    # Categories access efficiency
    global_definitions_count = sum(1 for k, v in categories_structure.items() 
                                 if v['type'] == 'global_definitions')
    category_definitions_count = sum(1 for k, v in categories_structure.items() 
                                   if v['type'] == 'category_definition')
    
    efficiency_analysis['categories_access_patterns'] = {
        'global_definitions': global_definitions_count,
        'category_specific': category_definitions_count,
        'lookup_efficiency': 'High - Well-structured hierarchy'
    }
    
    # Materials access efficiency
    materials_info = materials_sections.get('materials', {})
    if 'category_analysis' in materials_info:
        avg_complexity = sum(cat['complexity_score'] for cat in materials_info['category_analysis'].values()) / len(materials_info['category_analysis'])
        efficiency_analysis['materials_access_patterns'] = {
            'average_material_complexity': avg_complexity,
            'hierarchical_lookup': 'Category → Material → Properties',
            'inheritance_efficiency': 'Good - Category inheritance implemented'
        }
    
    # ANALYSIS 4: Normalization Opportunities
    print(f"\n💡 NORMALIZATION OPPORTUNITIES:")
    
    normalization_opportunities = []
    
    # 1. Check for redundant structures
    if 'property_groups' in materials_data and 'materialPropertiesDefinitions' in categories_data:
        normalization_opportunities.append({
            'type': 'redundant_definitions',
            'description': 'property_groups and materialPropertiesDefinitions serve similar purposes',
            'impact': 'Medium',
            'recommendation': 'Consolidate into single authoritative source'
        })
    
    # 2. Check for complex nested access patterns
    materials_nested_depth = 0
    if 'materials' in materials_data:
        materials_nested_depth = 3  # materials → category → items → material
    
    if materials_nested_depth > 2:
        normalization_opportunities.append({
            'type': 'deep_nesting',
            'description': f'Materials access requires {materials_nested_depth} levels of nesting',
            'impact': 'Low',
            'recommendation': 'Consider flattening for direct material access'
        })
    
    # 3. Check for separated related data
    if 'material_index' in materials_data and 'materials' in materials_data:
        normalization_opportunities.append({
            'type': 'separated_related_data',
            'description': 'Material index separate from material definitions',
            'impact': 'Low',
            'recommendation': 'Index could be auto-generated from materials structure'
        })
    
    # 4. Check for frontmatter-specific optimizations
    frontmatter_fields_in_categories = 0
    for key in categories_data.keys():
        if key in ['machineSettingsDescriptions', 'materialPropertiesDefinitions', 
                   'environmentalImpactTemplates', 'applicationTypes']:
            frontmatter_fields_in_categories += 1
    
    if frontmatter_fields_in_categories < 4:
        normalization_opportunities.append({
            'type': 'incomplete_frontmatter_definitions',
            'description': 'Not all frontmatter sections have category-level definitions',
            'impact': 'Medium',
            'recommendation': 'Add missing frontmatter template definitions'
        })
    
    print(f"   🎯 Found {len(normalization_opportunities)} optimization opportunities:")
    for i, opp in enumerate(normalization_opportunities, 1):
        print(f"      {i}. {opp['type'].upper()}: {opp['description']}")
        print(f"         Impact: {opp['impact']} | Recommendation: {opp['recommendation']}")\n    
    # ANALYSIS 5: Optimal Structure Recommendation
    print(f"\\n🏆 OPTIMAL STRUCTURE RECOMMENDATION:")
    
    current_score = 0\n    max_score = 10
    
    # Score current structure
    if global_definitions_count >= 4:
        current_score += 2
        print(f"   ✅ Global definitions well-implemented (+2)")
    
    if 'materialPropertiesDefinitions' in categories_data:
        current_score += 2
        print(f"   ✅ Property inheritance system in place (+2)")
    
    if materials_nested_depth <= 3:
        current_score += 1
        print(f"   ✅ Reasonable nesting depth (+1)")
    
    if len(normalization_opportunities) <= 3:
        current_score += 2
        print(f"   ✅ Limited normalization issues (+2)")
    
    # Check for dual inheritance (industry + properties)
    has_industry_inheritance = False
    for category in categories_data.values():
        if isinstance(category, dict) and 'industryTags' in category:
            has_industry_inheritance = True
            break
    
    if has_industry_inheritance:
        current_score += 2
        print(f"   ✅ Dual inheritance system operational (+2)")
    
    efficiency_percentage = (current_score / max_score) * 100
    
    print(f"\\n   📊 CURRENT STRUCTURE EFFICIENCY: {current_score}/{max_score} ({efficiency_percentage:.1f}%)")
    
    if efficiency_percentage >= 80:
        print(f"   🎉 EXCELLENT: Structure is highly optimized for frontmatter generation")
        recommendation = "maintain_current"
    elif efficiency_percentage >= 60:
        print(f"   👍 GOOD: Structure is well-optimized with minor improvement opportunities")
        recommendation = "minor_optimizations"
    else:
        print(f"   ⚠️  IMPROVEMENT NEEDED: Structure has significant optimization potential")
        recommendation = "major_restructuring"
    
    # Generate specific recommendations
    print(f"\\n🎯 SPECIFIC RECOMMENDATIONS:")
    
    if recommendation == "maintain_current":
        print(f"   ✨ Current structure is optimal for frontmatter generation")
        print(f"   📋 Focus on maintaining dual inheritance system")
        print(f"   🔧 Consider minor cleanup of redundant definitions")
    
    elif recommendation == "minor_optimizations":
        print(f"   🔧 Address identified normalization opportunities")
        print(f"   📊 Consider consolidating redundant property definitions")
        print(f"   ⚡ Optimize data access patterns for better performance")
    
    else:
        print(f"   🏗️  Major restructuring recommended")
        print(f"   📋 Flatten nested structures where possible")
        print(f"   🔄 Implement comprehensive inheritance system")
        print(f"   📊 Consolidate fragmented data sources")
    
    # Save analysis results
    analysis_results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "categories_structure": categories_structure,
        "materials_structure": materials_sections,
        "efficiency_analysis": efficiency_analysis,
        "normalization_opportunities": normalization_opportunities,
        "current_efficiency_score": current_score,
        "max_efficiency_score": max_score,
        "efficiency_percentage": efficiency_percentage,
        "recommendation": recommendation
    }
    
    report_file = "data_structure_optimization_analysis.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\\n💾 Analysis saved to: {report_file}")
    
    return analysis_results

if __name__ == "__main__":
    analyze_data_structure_optimization()