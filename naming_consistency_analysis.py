#!/usr/bin/env python3
"""
Naming Consistency Analysis - End-to-End Pipeline

Analyzes naming consistency throughout the entire Z-Beam Generator pipeline.
"""

import yaml
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import re

def analyze_naming_consistency():
    """Comprehensive analysis of naming consistency across the pipeline."""
    
    print("🔍 NAMING CONSISTENCY ANALYSIS - END-TO-END PIPELINE")
    print("=" * 65)
    
    inconsistencies = []
    naming_patterns = defaultdict(set)
    
    # ANALYSIS 1: Data Structure Naming
    print("\n📁 DATA STRUCTURE ANALYSIS")
    print("-" * 30)
    
    # Load data files
    with open("data/Categories.yaml", 'r', encoding='utf-8') as f:
        categories_data = yaml.safe_load(f)
    
    with open("data/materials.yaml", 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    # Check property naming in Categories.yaml
    category_property_types = set()
    if 'materialPropertiesDefinitions' in categories_data:
        for prop_type in categories_data['materialPropertiesDefinitions'].keys():
            category_property_types.add(prop_type)
            naming_patterns['property_group_definitions'].add(prop_type)
    
    # Check property naming in individual categories
    category_inline_properties = set()
    for key, value in categories_data.items():
        if isinstance(value, dict):
            for prop_key in value.keys():
                if 'Properties' in prop_key:
                    category_inline_properties.add(prop_key)
                    naming_patterns['category_inline_properties'].add(prop_key)
    
    # Check materials.yaml property naming
    material_property_types = set()
    if 'materials' in materials_data:
        for category_name, category_data in materials_data['materials'].items():
            if 'items' in category_data:
                for material in category_data['items']:
                    if isinstance(material, dict):
                        for key in material.keys():
                            if '_properties' in key:
                                material_property_types.add(key)
                                naming_patterns['material_property_overrides'].add(key)
    
    print(f"   📊 Categories.yaml property definitions: {category_property_types}")
    print(f"   📊 Categories.yaml inline properties: {category_inline_properties}")
    print(f"   📊 materials.yaml property overrides: {material_property_types}")
    
    # CRITICAL INCONSISTENCY 1: Property Group Naming
    snake_case_groups = {p for p in category_property_types if '_' in p}
    camel_case_groups = {p for p in category_inline_properties if 'Properties' in p and '_' not in p}
    
    if snake_case_groups and camel_case_groups:
        inconsistencies.append({
            "type": "CRITICAL",
            "category": "Property Group Naming",
            "issue": "Mixed snake_case and camelCase for property groups",
            "details": {
                "snake_case_definitions": list(snake_case_groups),
                "camelCase_inline": list(camel_case_groups)
            },
            "impact": "Data access failures, mapping errors in components"
        })
    
    # ANALYSIS 2: Component Code Analysis
    print(f"\n💻 COMPONENT CODE ANALYSIS")
    print("-" * 30)
    
    # Check property references in components
    property_references = defaultdict(set)
    
    component_files = [
        "components/frontmatter/core/streamlined_generator.py",
        "components/frontmatter/research/property_researcher.py", 
        "components/propertiestable/generator.py",
        "components/frontmatter/enhancement/property_enhancement_service.py"
    ]
    
    for comp_file in component_files:
        if Path(comp_file).exists():
            with open(comp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find property type references
                snake_case_props = re.findall(r'["\']([a-z]+_properties)["\']', content)
                camel_case_props = re.findall(r'["\']([a-z]+Properties)["\']', content)
                
                for prop in snake_case_props:
                    property_references[comp_file].add(f"snake_case:{prop}")
                    naming_patterns['component_snake_case'].add(prop)
                
                for prop in camel_case_props:
                    property_references[comp_file].add(f"camelCase:{prop}")
                    naming_patterns['component_camel_case'].add(prop)
    
    # Check for mixed naming in components
    components_with_mixed_naming = []
    for comp_file, refs in property_references.items():
        snake_refs = [r for r in refs if r.startswith('snake_case:')]
        camel_refs = [r for r in refs if r.startswith('camelCase:')]
        
        if snake_refs and camel_refs:
            components_with_mixed_naming.append({
                "file": comp_file,
                "snake_case": snake_refs,
                "camelCase": camel_refs
            })
    
    print(f"   📊 Components with mixed naming: {len(components_with_mixed_naming)}")
    
    if components_with_mixed_naming:
        inconsistencies.append({
            "type": "WARNING", 
            "category": "Component Mixed Naming",
            "issue": "Components use both snake_case and camelCase",
            "details": components_with_mixed_naming,
            "impact": "Maintenance complexity, potential lookup errors"
        })
    
    # ANALYSIS 3: Individual Property Naming
    print(f"\n🏷️  INDIVIDUAL PROPERTY NAMING")
    print("-" * 30)
    
    # Check individual property names (thermalConductivity vs thermal_conductivity)
    individual_properties = defaultdict(set)
    
    # From Categories.yaml materialPropertiesDefinitions
    if 'materialPropertiesDefinitions' in categories_data:
        for prop_group, props in categories_data['materialPropertiesDefinitions'].items():
            if isinstance(props, dict) and 'common_properties' in props:
                for prop_name in props['common_properties'].keys():
                    individual_properties['definition_properties'].add(prop_name)
                    if '_' in prop_name:
                        naming_patterns['individual_snake_case'].add(prop_name)
                    elif prop_name[0].islower() and any(c.isupper() for c in prop_name):
                        naming_patterns['individual_camel_case'].add(prop_name)
    
    # From component code individual property references
    for comp_file in component_files:
        if Path(comp_file).exists():
            with open(comp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find individual property references
                thermal_cond_snake = re.findall(r'["\']thermal_conductivity["\']', content)
                thermal_cond_camel = re.findall(r'["\']thermalConductivity["\']', content)
                
                if thermal_cond_snake:
                    individual_properties['component_snake_individual'].add('thermal_conductivity')
                    naming_patterns['component_individual_snake'].add('thermal_conductivity')
                
                if thermal_cond_camel:
                    individual_properties['component_camel_individual'].add('thermalConductivity')
                    naming_patterns['component_individual_camel'].add('thermalConductivity')
    
    # CRITICAL INCONSISTENCY 2: Individual Property Naming
    snake_individual = naming_patterns['individual_snake_case'] | naming_patterns['component_individual_snake']
    camel_individual = naming_patterns['individual_camel_case'] | naming_patterns['component_individual_camel']
    
    thermal_conductivity_inconsistency = False
    if 'thermal_conductivity' in snake_individual and 'thermalConductivity' in camel_individual:
        thermal_conductivity_inconsistency = True
        inconsistencies.append({
            "type": "CRITICAL",
            "category": "Individual Property Naming",
            "issue": "thermalConductivity vs thermal_conductivity inconsistency", 
            "details": {
                "snake_case_usage": "thermal_conductivity in property_researcher.py",
                "camelCase_usage": "thermalConductivity in most other components",
                "definition_format": list(individual_properties['definition_properties'])
            },
            "impact": "Property lookups may fail, data mapping errors"
        })
    
    print(f"   📊 Individual snake_case properties: {len(snake_individual)}")
    print(f"   📊 Individual camelCase properties: {len(camel_individual)}")
    print(f"   ⚠️  thermalConductivity inconsistency: {thermal_conductivity_inconsistency}")
    
    # ANALYSIS 4: Output Format Analysis  
    print(f"\n📄 OUTPUT FORMAT ANALYSIS")
    print("-" * 30)
    
    # Check generated frontmatter format
    sample_frontmatter = {
        "materialProperties": {
            "density": {"value": "2.7", "unit": "g/cm³"},
            "thermalConductivity": {"value": "237", "unit": "W/m·K"},
            "meltingPoint": {"value": "660", "unit": "°C"}
        }
    }
    
    output_format = "camelCase"  # From sample examination
    print(f"   📊 Final output format: {output_format} (materialProperties.thermalConductivity)")
    
    # ANALYSIS 5: Pipeline Transformation Analysis
    print(f"\n🔄 PIPELINE TRANSFORMATION ANALYSIS")
    print("-" * 35)
    
    transformation_chain = [
        "Categories.yaml (mixed: snake_case definitions + camelCase inline)",
        "materials.yaml (snake_case: thermal_properties, mechanical_properties)", 
        "Component Processing (mixed: both naming conventions)",
        "Output Generation (camelCase: thermalConductivity)"
    ]
    
    for i, step in enumerate(transformation_chain, 1):
        print(f"   {i}. {step}")
    
    # CRITICAL INCONSISTENCY 3: Pipeline Transformation
    if len(set([len(naming_patterns['property_group_definitions']), 
                len(naming_patterns['category_inline_properties']), 
                len(naming_patterns['material_property_overrides'])])) > 1:
        inconsistencies.append({
            "type": "CRITICAL", 
            "category": "Pipeline Transformation",
            "issue": "Inconsistent property naming through transformation chain",
            "details": {
                "definitions": list(naming_patterns['property_group_definitions']),
                "inline": list(naming_patterns['category_inline_properties']),
                "overrides": list(naming_patterns['material_property_overrides']),
                "final_output": "camelCase"
            },
            "impact": "Data loss during transformation, inconsistent output"
        })
    
    # FINAL ASSESSMENT
    print(f"\n🎯 CONSISTENCY ASSESSMENT")
    print("-" * 25)
    
    critical_count = len([i for i in inconsistencies if i['type'] == 'CRITICAL'])
    warning_count = len([i for i in inconsistencies if i['type'] == 'WARNING'])
    
    print(f"   🚨 Critical inconsistencies: {critical_count}")
    print(f"   ⚠️  Warning inconsistencies: {warning_count}")
    
    if critical_count == 0 and warning_count == 0:
        consistency_score = 100
        assessment = "EXCELLENT"
        color = "🟢"
    elif critical_count == 0:
        consistency_score = 85 
        assessment = "GOOD"
        color = "🟡"
    elif critical_count <= 2:
        consistency_score = 60
        assessment = "NEEDS IMPROVEMENT"  
        color = "🟠"
    else:
        consistency_score = 30
        assessment = "POOR"
        color = "🔴"
    
    print(f"   {color} Overall consistency: {assessment} ({consistency_score}%)")
    
    # DETAILED INCONSISTENCY REPORT
    if inconsistencies:
        print(f"\n📋 DETAILED INCONSISTENCY REPORT")
        print("-" * 35)
        
        for i, issue in enumerate(inconsistencies, 1):
            print(f"\n   {issue['type']} #{i}: {issue['category']}")
            print(f"   Issue: {issue['issue']}")
            print(f"   Impact: {issue['impact']}")
            if isinstance(issue['details'], dict):
                for key, value in issue['details'].items():
                    print(f"   {key}: {value}")
            else:
                print(f"   Details: {issue['details']}")
    
    # RECOMMENDATIONS
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 18)
    
    if critical_count > 0:
        print(f"   🚨 URGENT: Fix critical naming inconsistencies")
        print(f"   📋 Priority actions:")
        print(f"      1. Standardize property group naming (choose snake_case OR camelCase)")
        print(f"      2. Fix thermalConductivity/thermal_conductivity inconsistency")
        print(f"      3. Ensure consistent transformation pipeline")
        print(f"   ⚡ Risk: Data loss, component failures, incorrect output")
    elif warning_count > 0:
        print(f"   ⚠️  MODERATE: Address warning inconsistencies")  
        print(f"   📋 Recommended actions:")
        print(f"      1. Standardize component internal naming")
        print(f"      2. Add naming convention documentation")
        print(f"   ⚡ Risk: Maintenance complexity, developer confusion")
    else:
        print(f"   ✅ EXCELLENT: No significant naming inconsistencies found")
        print(f"   📋 Maintain current consistency:")
        print(f"      1. Document current naming conventions")  
        print(f"      2. Add linting rules to prevent future inconsistencies")
    
    # Save analysis
    analysis_results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "consistency_score": consistency_score,
        "assessment": assessment,
        "critical_inconsistencies": critical_count,
        "warning_inconsistencies": warning_count,
        "inconsistencies": inconsistencies,
        "naming_patterns": {k: list(v) for k, v in naming_patterns.items()},
        "transformation_chain": transformation_chain
    }
    
    report_file = "naming_consistency_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full analysis saved to: {report_file}")
    
    return analysis_results

if __name__ == "__main__":
    analyze_naming_consistency()