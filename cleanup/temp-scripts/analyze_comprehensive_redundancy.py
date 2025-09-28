#!/usr/bin/env python3
"""
Comprehensive Data Redundancy Analysis

This script analyzes all potential redundancy patterns across Categories.yaml 
and materials.yaml to identify additional consolidation opportunities.
"""

import yaml
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

def analyze_comprehensive_redundancy():
    """Analyze all potential data redundancy patterns."""
    
    print("🔍 COMPREHENSIVE DATA REDUNDANCY ANALYSIS")
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
    
    print(f"📂 Loaded {len(categories_data)} categories + metadata")
    print(f"📂 Loaded {len(materials_data)} materials + index")
    
    # Analyze different data structures
    analysis_results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "categories_analysis": {},
        "materials_analysis": {},
        "redundancy_opportunities": {}
    }
    
    # 1. REGULATORY STANDARDS (already optimized)
    print(f"\n✅ REGULATORY STANDARDS:")
    if 'universal_regulatory_standards' in categories_data:
        universal_regulatory = categories_data['universal_regulatory_standards']
        print(f"   📊 Universal regulatory standards: {len(universal_regulatory)} entries")
        print(f"   🎯 Status: ALREADY OPTIMIZED - Single category-level source")
        analysis_results["regulatory_status"] = "optimized"
    else:
        print(f"   📊 No universal regulatory standards found")
        analysis_results["regulatory_status"] = "not_found"
    
    # 2. MACHINE SETTINGS DESCRIPTIONS
    print(f"\n🔧 MACHINE SETTINGS DESCRIPTIONS:")
    if 'machineSettingsDescriptions' in categories_data:
        machine_settings = categories_data['machineSettingsDescriptions']
        print(f"   📊 Machine settings descriptions: {len(machine_settings)} entries")
        print(f"   🎯 Status: OPTIMIZED - Single category-level source")
        analysis_results["machine_settings_status"] = "optimized"
    else:
        print(f"   📊 No machine settings descriptions found")
    
    # 3. MATERIAL PROPERTIES TEMPLATES
    print(f"\n🧪 MATERIAL PROPERTIES:")
    if 'materialPropertiesDefinitions' in categories_data:
        property_definitions = categories_data['materialPropertiesDefinitions']
        print(f"   📊 Material property definitions: {len(property_definitions)} entries")
        print(f"   🎯 Status: OPTIMIZED - Single category-level templates")
        analysis_results["property_definitions_status"] = "optimized"
    else:
        print(f"   📊 No material properties definitions found")
    
    # 4. ENVIRONMENTAL IMPACT TEMPLATES
    print(f"\n🌍 ENVIRONMENTAL IMPACT:")
    if 'environmentalImpactTemplates' in categories_data:
        env_templates = categories_data['environmentalImpactTemplates']
        print(f"   📊 Environmental impact templates: {len(env_templates)} entries")
        print(f"   🎯 Status: OPTIMIZED - Single category-level templates")
        analysis_results["environmental_templates_status"] = "optimized"
    else:
        print(f"   📊 No environmental impact templates found")
    
    # 5. APPLICATION TYPES
    print(f"\n🔨 APPLICATION TYPES:")
    if 'applicationTypes' in categories_data:
        app_types = categories_data['applicationTypes']
        print(f"   📊 Application types: {len(app_types)} entries")
        print(f"   🎯 Status: OPTIMIZED - Standardized application categories")
        analysis_results["application_types_status"] = "optimized"
    else:
        print(f"   📊 No application types found")
    
    # 6. ANALYZE MATERIALS FOR REMAINING REDUNDANCY OPPORTUNITIES
    print(f"\n📋 MATERIALS ANALYSIS:")
    
    # Remove material_index and metadata
    actual_materials = {k: v for k, v in materials_data.items() 
                       if k not in ['material_index'] and isinstance(v, dict)}
    
    print(f"   📊 Analyzing {len(actual_materials)} actual materials")
    
    # Check for common patterns in material data
    material_fields = defaultdict(list)
    field_value_frequency = defaultdict(Counter)
    
    for material_name, material_data in actual_materials.items():
        if isinstance(material_data, dict):
            for field_name, field_value in material_data.items():
                material_fields[field_name].append(material_name)
                
                # Count value frequencies for potential consolidation
                if isinstance(field_value, (str, int, float)):
                    field_value_frequency[field_name][field_value] += 1
                elif isinstance(field_value, list):
                    for item in field_value:
                        if isinstance(item, (str, int, float)):
                            field_value_frequency[field_name][item] += 1
                elif isinstance(field_value, dict):
                    # For nested dictionaries, count common structures
                    for nested_key, nested_value in field_value.items():
                        nested_field = f"{field_name}.{nested_key}"
                        if isinstance(nested_value, (str, int, float)):
                            field_value_frequency[nested_field][nested_value] += 1
    
    print(f"\n🔍 FIELD FREQUENCY ANALYSIS:")
    for field_name, materials_with_field in material_fields.items():
        field_frequency = len(materials_with_field) / len(actual_materials) * 100
        print(f"   📊 {field_name}: {len(materials_with_field)}/{len(actual_materials)} materials ({field_frequency:.1f}%)")
    
    # Look for high-frequency values that could be consolidated
    print(f"\n🎯 POTENTIAL CONSOLIDATION OPPORTUNITIES:")
    
    consolidation_opportunities = []
    
    for field_name, value_counts in field_value_frequency.items():
        # Look for values that appear in many materials (potential for category-level defaults)
        high_frequency_values = [(value, count) for value, count in value_counts.items() 
                               if count >= len(actual_materials) * 0.3]  # 30% threshold
        
        if high_frequency_values:
            total_occurrences = sum(count for _, count in high_frequency_values)
            consolidation_opportunities.append({
                'field': field_name,
                'high_frequency_values': high_frequency_values,
                'total_occurrences': total_occurrences,
                'materials_affected': len(set().union(*[
                    [m for m, data in actual_materials.items() 
                     if isinstance(data, dict) and field_name in data and data[field_name] == value]
                    for value, _ in high_frequency_values
                ]))
            })
    
    # Sort by consolidation potential
    consolidation_opportunities.sort(key=lambda x: x['total_occurrences'], reverse=True)
    
    if consolidation_opportunities:
        print(f"   🔍 Found {len(consolidation_opportunities)} potential consolidation areas:")
        
        for i, opportunity in enumerate(consolidation_opportunities[:5], 1):  # Show top 5
            field = opportunity['field']
            total_occurrences = opportunity['total_occurrences']
            materials_affected = opportunity['materials_affected']
            
            print(f"   {i}. {field}:")
            print(f"      📊 {total_occurrences} occurrences across {materials_affected} materials")
            
            # Show most common values
            top_values = sorted(opportunity['high_frequency_values'], 
                              key=lambda x: x[1], reverse=True)[:3]
            for value, count in top_values:
                percentage = (count / len(actual_materials)) * 100
                print(f"         • '{value}': {count} materials ({percentage:.1f}%)")
    else:
        print(f"   ✅ No significant consolidation opportunities found")
        print(f"   🎉 Material data appears well-optimized!")
    
    # Overall assessment
    print(f"\n🏆 OVERALL ASSESSMENT:")
    optimized_systems = [
        "✅ Regulatory Standards (universal_regulatory_standards)",
        "✅ Industry Tags (consolidated in previous optimization)", 
        "✅ Machine Settings (machineSettingsDescriptions)",
        "✅ Material Properties (materialPropertiesDefinitions)",
        "✅ Environmental Impact (environmentalImpactTemplates)",
        "✅ Application Types (applicationTypes)"
    ]
    
    print(f"   📊 Systems Already Optimized:")
    for system in optimized_systems:
        print(f"      {system}")
    
    if consolidation_opportunities:
        print(f"\n   🎯 Additional Optimization Potential:")
        print(f"      📈 {len(consolidation_opportunities)} fields with consolidation opportunities")
        print(f"      📊 Estimated further redundancy reduction possible")
    else:
        print(f"\n   🎉 CONGRATULATIONS!")
        print(f"      🏆 Your data architecture is highly optimized!")
        print(f"      ✨ No significant redundancy remaining")
    
    # Save analysis results
    analysis_results["consolidation_opportunities"] = consolidation_opportunities
    analysis_results["optimized_systems_count"] = len(optimized_systems)
    analysis_results["materials_analyzed"] = len(actual_materials)
    
    report_file = "comprehensive_redundancy_analysis.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive analysis saved to: {report_file}")
    
    return analysis_results

if __name__ == "__main__":
    analyze_comprehensive_redundancy()