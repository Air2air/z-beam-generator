#!/usr/bin/env python3
"""
Data Structure Optimization Analysis

Analyzes Categories.yaml and materials.yaml for frontmatter generation optimization.
"""

import yaml
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def analyze_structure_optimization():
    """Quick analysis of data structure optimization for frontmatter generation."""
    
    print("🔍 DATA STRUCTURE OPTIMIZATION ANALYSIS")
    print("=" * 60)
    
    # Load files
    with open("data/Categories.yaml", 'r', encoding='utf-8') as f:
        categories_data = yaml.safe_load(f)
    
    with open("data/materials.yaml", 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    print(f"📂 Analyzing Categories.yaml and materials.yaml structures")
    
    # ANALYSIS 1: Categories.yaml Structure
    print(f"\n🏗️ CATEGORIES.YAML STRUCTURE:")
    
    global_definitions = 0
    category_definitions = 0
    
    for key, value in categories_data.items():
        if key in ['universal_regulatory_standards', 'machineSettingsDescriptions', 
                   'materialPropertiesDefinitions', 'environmentalImpactTemplates']:
            global_definitions += 1
            print(f"   🌐 {key}: Global definition")
        elif key == 'metadata':
            print(f"   ⚙️  {key}: Configuration metadata")
        elif isinstance(value, dict) and len(value) > 2:
            category_definitions += 1
            print(f"   📁 {key}: Category definition ({len(value)} fields)")
    
    print(f"   📊 Summary: {global_definitions} global definitions, {category_definitions} categories")
    
    # ANALYSIS 2: materials.yaml Structure
    print(f"\n📋 MATERIALS.YAML STRUCTURE:")
    
    total_materials = 0
    materials_with_properties = 0
    clean_materials = 0
    
    if 'materials' in materials_data:
        for category_name, category_data in materials_data['materials'].items():
            if isinstance(category_data, dict) and 'items' in category_data:
                materials_list = category_data['items']
                category_materials = len(materials_list)
                total_materials += category_materials
                
                category_with_props = 0
                category_clean = 0
                
                for material in materials_list:
                    if isinstance(material, dict):
                        has_properties = any(key.endswith('_properties') for key in material.keys())
                        if has_properties:
                            materials_with_properties += 1
                            category_with_props += 1
                        else:
                            clean_materials += 1
                            category_clean += 1
                
                print(f"   📁 {category_name}: {category_materials} materials ({category_clean} clean, {category_with_props} with properties)")
    
    optimization_rate = (clean_materials / total_materials) * 100 if total_materials > 0 else 0
    print(f"   📊 Total: {total_materials} materials, {optimization_rate:.1f}% optimized through inheritance")
    
    # ANALYSIS 3: Frontmatter Generation Efficiency
    print(f"\n🚀 FRONTMATTER GENERATION EFFICIENCY:")
    
    efficiency_score = 0
    max_score = 10
    
    # Check global definitions
    if global_definitions >= 4:
        efficiency_score += 3
        print(f"   ✅ Comprehensive global definitions (+3)")
    elif global_definitions >= 2:
        efficiency_score += 2
        print(f"   👍 Good global definitions (+2)")
    
    # Check property inheritance
    if 'materialPropertiesDefinitions' in categories_data:
        efficiency_score += 2
        print(f"   ✅ Property inheritance system (+2)")
    
    # Check optimization rate
    if optimization_rate >= 50:
        efficiency_score += 2
        print(f"   ✅ Good inheritance optimization ({optimization_rate:.1f}%) (+2)")
    elif optimization_rate >= 30:
        efficiency_score += 1
        print(f"   👍 Moderate inheritance optimization (+1)")
    
    # Check structure depth
    nesting_levels = 3  # materials -> category -> items -> material
    if nesting_levels <= 3:
        efficiency_score += 1
        print(f"   ✅ Reasonable nesting depth (+1)")
    
    # Check for dual inheritance (industry + properties)
    has_industry_tags = any(isinstance(v, dict) and 'industryTags' in v 
                           for v in categories_data.values() if isinstance(v, dict))
    if has_industry_tags:
        efficiency_score += 2
        print(f"   ✅ Dual inheritance system (industry + properties) (+2)")
    
    efficiency_percentage = (efficiency_score / max_score) * 100
    
    # ANALYSIS 4: Optimization Recommendations
    print(f"\n💡 OPTIMIZATION ASSESSMENT:")
    print(f"   📊 Current efficiency: {efficiency_score}/{max_score} ({efficiency_percentage:.1f}%)")
    
    if efficiency_percentage >= 80:
        print(f"   🎉 EXCELLENT: Structure is highly optimized for frontmatter generation")
        print(f"   ✨ Current architecture is near-optimal")
        recommendation = "maintain_current"
    elif efficiency_percentage >= 70:
        print(f"   👍 VERY GOOD: Structure is well-optimized with minor opportunities")
        print(f"   🔧 Consider small refinements only")
        recommendation = "minor_refinements"
    elif efficiency_percentage >= 60:
        print(f"   📊 GOOD: Structure is adequately optimized")
        print(f"   🔄 Some normalization opportunities exist")
        recommendation = "moderate_improvements"
    else:
        print(f"   ⚠️  NEEDS IMPROVEMENT: Structure has optimization potential")
        print(f"   🏗️  Consider structural enhancements")
        recommendation = "significant_improvements"
    
    # Specific recommendations
    print(f"\n🎯 SPECIFIC RECOMMENDATIONS:")
    
    normalization_opportunities = []
    
    # Check for redundant definitions
    if 'property_groups' in materials_data and 'materialPropertiesDefinitions' in categories_data:
        normalization_opportunities.append("Consolidate property_groups with materialPropertiesDefinitions")
    
    # Check material_index necessity
    if 'material_index' in materials_data:
        normalization_opportunities.append("Consider auto-generating material_index from materials structure")
    
    # Check for missing frontmatter templates
    frontmatter_sections = ['machineSettingsDescriptions', 'materialPropertiesDefinitions', 
                           'environmentalImpactTemplates', 'applicationTypes']
    missing_sections = [section for section in frontmatter_sections 
                       if section not in categories_data]
    
    if missing_sections:
        normalization_opportunities.append(f"Add missing frontmatter templates: {', '.join(missing_sections)}")
    
    if recommendation == "maintain_current":
        print(f"   ✅ Current structure is optimal - maintain dual inheritance architecture")
        print(f"   📋 Focus on data quality and consistency")
        if normalization_opportunities:
            print(f"   🔧 Minor cleanup opportunities:")
            for opp in normalization_opportunities[:2]:
                print(f"      • {opp}")
    
    elif recommendation in ["minor_refinements", "moderate_improvements"]:
        print(f"   🔧 Recommended optimizations:")
        for opp in normalization_opportunities:
            print(f"      • {opp}")
        print(f"   ⚡ Consider performance optimizations for large-scale generation")
    
    else:
        print(f"   🏗️  Major structural improvements needed:")
        print(f"      • Implement comprehensive inheritance system")
        print(f"      • Add missing global definition templates")
        print(f"      • Optimize data access patterns")
    
    # Overall assessment for frontmatter generation
    print(f"\n🏆 FRONTMATTER GENERATION READINESS:")
    
    readiness_factors = []
    
    if global_definitions >= 3:
        readiness_factors.append("✅ Rich template definitions available")
    
    if optimization_rate >= 50:
        readiness_factors.append("✅ Efficient inheritance reduces data duplication")
    
    if has_industry_tags and 'materialPropertiesDefinitions' in categories_data:
        readiness_factors.append("✅ Dual inheritance system supports comprehensive generation")
    
    if len(readiness_factors) >= 3:
        print(f"   🎉 EXCELLENT: Structure is highly optimized for frontmatter generation")
        print(f"   🚀 Ready for high-performance content generation")
    elif len(readiness_factors) >= 2:
        print(f"   👍 GOOD: Structure supports effective frontmatter generation")
        print(f"   📈 Minor optimizations could enhance performance")
    else:
        print(f"   ⚠️  NEEDS WORK: Structure requires optimization for efficient generation")
    
    for factor in readiness_factors:
        print(f"   {factor}")
    
    # Save analysis
    analysis_results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "efficiency_score": efficiency_score,
        "max_score": max_score,
        "efficiency_percentage": efficiency_percentage,
        "optimization_rate": optimization_rate,
        "total_materials": total_materials,
        "global_definitions": global_definitions,
        "recommendation": recommendation,
        "normalization_opportunities": normalization_opportunities,
        "readiness_factors": readiness_factors
    }
    
    report_file = "data_structure_optimization_analysis.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Analysis saved to: {report_file}")
    
    return analysis_results

if __name__ == "__main__":
    analyze_structure_optimization()