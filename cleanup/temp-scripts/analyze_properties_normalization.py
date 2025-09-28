#!/usr/bin/env python3
"""
Material Properties Normalization Analysis

This script analyzes *_properties structures across Categories.yaml and materials.yaml
to identify consolidation and normalization opportunities.
"""

import yaml
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

def analyze_properties_normalization():
    """Analyze material properties for normalization opportunities."""
    
    print("🔍 MATERIAL PROPERTIES NORMALIZATION ANALYSIS")
    print("=" * 65)
    
    # Load Categories.yaml
    categories_file = Path("data/Categories.yaml")
    if not categories_file.exists():
        print("❌ Categories.yaml not found")
        return
        
    with open(categories_file, 'r', encoding='utf-8') as f:
        categories_data = yaml.safe_load(f)
    
    # Load materials.yaml  
    materials_file = Path("data/materials.yaml")
    if not materials_file.exists():
        print("❌ materials.yaml not found")
        return
        
    with open(materials_file, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    print(f"📂 Loaded Categories.yaml with {len(categories_data)} sections")
    print(f"📂 Loaded materials.yaml with {len(materials_data)} entries")
    
    # Extract category-level property templates/definitions
    print(f"\n📋 CATEGORY-LEVEL PROPERTY STRUCTURES:")
    
    category_property_templates = {}
    
    # Check for materialPropertiesDefinitions
    if 'materialPropertiesDefinitions' in categories_data:
        prop_defs = categories_data['materialPropertiesDefinitions']
        print(f"   ✅ materialPropertiesDefinitions: {len(prop_defs)} property types defined")
        category_property_templates['definitions'] = prop_defs
        
        for prop_type, definition in prop_defs.items():
            if isinstance(definition, dict):
                fields = list(definition.keys()) if definition else []
                print(f"      📊 {prop_type}: {len(fields)} fields ({', '.join(fields[:3])}{'...' if len(fields) > 3 else ''})")
    else:
        print(f"   ❌ No materialPropertiesDefinitions found")
    
    # Check individual categories for property templates
    actual_categories = {k: v for k, v in categories_data.items() 
                        if k not in ['metadata', 'universal_regulatory_standards', 'machineSettingsDescriptions', 
                                   'materialPropertiesDefinitions', 'environmentalImpactTemplates', 'applicationTypes']}
    
    category_properties = {}
    for category_name, category_data in actual_categories.items():
        if isinstance(category_data, dict):
            # Look for property-related structures
            property_structures = {}
            
            for key, value in category_data.items():
                if 'properties' in key.lower() or 'property' in key.lower():
                    property_structures[key] = value
                    if isinstance(value, dict):
                        print(f"   📁 {category_name}.{key}: {len(value)} entries")
            
            if property_structures:
                category_properties[category_name] = property_structures
    
    # Extract material-level properties
    print(f"\n📋 MATERIAL-LEVEL PROPERTY ANALYSIS:")
    
    actual_materials = {k: v for k, v in materials_data.items() 
                       if k not in ['material_index'] and isinstance(v, dict)}
    
    print(f"   📊 Analyzing {len(actual_materials)} materials")
    
    # Find all *_properties patterns
    property_patterns = defaultdict(list)
    material_properties_data = {}
    
    for material_name, material_data in actual_materials.items():
        if isinstance(material_data, dict):
            material_props = {}
            
            for field_name, field_value in material_data.items():
                if field_name.endswith('_properties'):
                    property_patterns[field_name].append(material_name)
                    material_props[field_name] = field_value
                    
                    if isinstance(field_value, dict):
                        print(f"   📊 {material_name}.{field_name}: {len(field_value)} properties")
                        
                        # Analyze property structure
                        for prop_name, prop_value in field_value.items():
                            if isinstance(prop_value, dict):
                                prop_fields = list(prop_value.keys())
                                print(f"      🔧 {prop_name}: {prop_fields}")
            
            if material_props:
                material_properties_data[material_name] = material_props
    
    print(f"\n🔍 PROPERTY PATTERN FREQUENCY:")
    for pattern, materials_list in property_patterns.items():
        frequency = len(materials_list) / len(actual_materials) * 100
        print(f"   📈 {pattern}: {len(materials_list)}/{len(actual_materials)} materials ({frequency:.1f}%)")
        print(f"      Materials: {', '.join(materials_list[:5])}{' ...' if len(materials_list) > 5 else ''}")
    
    # Analyze property field structures for normalization
    print(f"\n🔍 PROPERTY FIELD STRUCTURE ANALYSIS:")
    
    property_field_analysis = {}
    
    for property_type in property_patterns.keys():
        print(f"\n   📋 {property_type} ANALYSIS:")
        
        # Collect all property names and their structures
        all_property_names = set()
        property_structures = defaultdict(list)
        property_value_patterns = defaultdict(Counter)
        
        for material_name in property_patterns[property_type]:
            if material_name in material_properties_data:
                props = material_properties_data[material_name].get(property_type, {})
                
                if isinstance(props, dict):
                    for prop_name, prop_data in props.items():
                        all_property_names.add(prop_name)
                        
                        if isinstance(prop_data, dict):
                            # Analyze structure
                            structure = tuple(sorted(prop_data.keys()))
                            property_structures[prop_name].append({
                                'material': material_name,
                                'structure': structure,
                                'data': prop_data
                            })
                            
                            # Analyze field patterns
                            for field_name, field_value in prop_data.items():
                                if isinstance(field_value, (str, int, float)):
                                    property_value_patterns[f"{prop_name}.{field_name}"][field_value] += 1
        
        print(f"      📊 Total unique property names: {len(all_property_names)}")
        print(f"      📊 Property names: {', '.join(sorted(list(all_property_names))[:10])}{' ...' if len(all_property_names) > 10 else ''}")
        
        # Analyze structural consistency
        structural_consistency = {}
        for prop_name, structures in property_structures.items():
            if len(structures) > 1:
                # Check if all materials use the same structure for this property
                structure_patterns = [s['structure'] for s in structures]
                structure_counter = Counter(structure_patterns)
                
                if len(structure_counter) == 1:
                    print(f"      ✅ {prop_name}: Consistent structure across {len(structures)} materials")
                else:
                    print(f"      ⚠️  {prop_name}: Inconsistent structures:")
                    for structure, count in structure_counter.items():
                        print(f"         📋 {structure}: {count} materials")
                
                structural_consistency[prop_name] = {
                    'materials_count': len(structures),
                    'structure_patterns': dict(structure_counter),
                    'is_consistent': len(structure_counter) == 1
                }
        
        property_field_analysis[property_type] = {
            'total_properties': len(all_property_names),
            'properties_list': sorted(list(all_property_names)),
            'structural_consistency': structural_consistency,
            'materials_using': len(property_patterns[property_type])
        }
    
    # Identify normalization opportunities
    print(f"\n💡 NORMALIZATION OPPORTUNITIES:")
    
    normalization_opportunities = []
    
    # 1. Check for properties that could be standardized at category level
    for property_type, analysis in property_field_analysis.items():
        materials_count = analysis['materials_using']
        total_materials = len(actual_materials)
        
        if materials_count >= total_materials * 0.5:  # 50% or more materials use this
            normalization_opportunities.append({
                'type': 'category_standardization',
                'property_type': property_type,
                'materials_count': materials_count,
                'total_materials': total_materials,
                'coverage_percentage': (materials_count / total_materials) * 100,
                'properties': analysis['properties_list'],
                'description': f"Standardize {property_type} structure at category level"
            })
    
    # 2. Check for inconsistent property structures
    for property_type, analysis in property_field_analysis.items():
        inconsistent_props = [prop for prop, data in analysis['structural_consistency'].items() 
                            if not data['is_consistent']]
        
        if inconsistent_props:
            normalization_opportunities.append({
                'type': 'structure_consistency',
                'property_type': property_type,
                'inconsistent_properties': inconsistent_props,
                'description': f"Normalize inconsistent structures in {property_type}"
            })
    
    # 3. Check for common property values that could be defaults
    common_values_opportunities = []
    for field_pattern, value_counts in property_value_patterns.items():
        # Look for values that appear frequently
        total_occurrences = sum(value_counts.values())
        if total_occurrences > 1:
            most_common_value, most_common_count = value_counts.most_common(1)[0]
            if most_common_count >= total_occurrences * 0.7:  # 70% or more use same value
                common_values_opportunities.append({
                    'field': field_pattern,
                    'common_value': most_common_value,
                    'frequency': most_common_count,
                    'total_occurrences': total_occurrences,
                    'percentage': (most_common_count / total_occurrences) * 100
                })
    
    if common_values_opportunities:
        normalization_opportunities.append({
            'type': 'common_value_defaults',
            'opportunities': common_values_opportunities,
            'description': 'Create category-level defaults for frequently repeated values'
        })
    
    # Display normalization opportunities
    if normalization_opportunities:
        print(f"   🎯 Found {len(normalization_opportunities)} normalization opportunities:")
        
        for i, opportunity in enumerate(normalization_opportunities, 1):
            print(f"\n   {i}. {opportunity['type'].upper()}: {opportunity['description']}")
            
            if opportunity['type'] == 'category_standardization':
                coverage = opportunity['coverage_percentage']
                props_count = len(opportunity['properties'])
                print(f"      📊 Coverage: {coverage:.1f}% ({opportunity['materials_count']}/{opportunity['total_materials']} materials)")
                print(f"      📋 Properties to standardize: {props_count}")
                
            elif opportunity['type'] == 'structure_consistency':
                inconsistent_count = len(opportunity['inconsistent_properties'])
                print(f"      ⚠️  Inconsistent properties: {inconsistent_count}")
                for prop in opportunity['inconsistent_properties'][:3]:
                    print(f"         • {prop}")
                
            elif opportunity['type'] == 'common_value_defaults':
                defaults_count = len(opportunity['opportunities'])
                print(f"      📈 Potential defaults: {defaults_count}")
                
                top_defaults = sorted(opportunity['opportunities'], 
                                    key=lambda x: x['percentage'], reverse=True)[:3]
                for default in top_defaults:
                    print(f"         • {default['field']}: '{default['common_value']}' ({default['percentage']:.1f}%)")
    else:
        print(f"   ✅ No significant normalization opportunities found")
        print(f"   🎉 Properties appear well-structured!")
    
    # Generate consolidation recommendation
    total_estimated_savings = 0
    for opp in normalization_opportunities:
        if opp['type'] == 'category_standardization':
            # Estimate entries that could be moved to category level
            properties_count = len(opp['properties'])
            materials_affected = opp['materials_count']
            estimated_savings = properties_count * materials_affected * 0.7  # Conservative estimate
            total_estimated_savings += estimated_savings
        elif opp['type'] == 'common_value_defaults':
            # Estimate redundant values that could be defaults
            for common_val in opp['opportunities']:
                if common_val['percentage'] > 70:
                    total_estimated_savings += common_val['frequency'] - 1  # Keep one, eliminate rest
    
    print(f"\n🏆 CONSOLIDATION POTENTIAL:")
    if total_estimated_savings > 0:
        print(f"   🎯 Estimated consolidatable entries: {int(total_estimated_savings)}")
        print(f"   📊 Potential normalization approach: Category-level property templates + defaults")
        print(f"   🔧 Implementation: Enhance materialPropertiesDefinitions with inheritance")
    else:
        print(f"   🎉 Properties are already well-normalized!")
        print(f"   ✨ No significant consolidation needed")
    
    # Save analysis results
    analysis_results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "property_patterns": dict(property_patterns),
        "property_field_analysis": property_field_analysis,
        "normalization_opportunities": normalization_opportunities,
        "estimated_consolidation_savings": int(total_estimated_savings),
        "category_property_templates": category_property_templates,
        "materials_analyzed": len(actual_materials)
    }
    
    report_file = "properties_normalization_analysis.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Properties analysis saved to: {report_file}")
    
    return analysis_results

if __name__ == "__main__":
    analyze_properties_normalization()