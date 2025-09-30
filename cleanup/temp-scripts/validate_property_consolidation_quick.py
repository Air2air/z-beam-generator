#!/usr/bin/env python3
"""
Property Consolidation Validation Test

Quick validation to ensure property consolidation worked correctly.
"""

import yaml
import json
from pathlib import Path

def quick_validate_consolidation():
    """Quick validation of property consolidation results."""
    
    print("🔍 PROPERTY CONSOLIDATION VALIDATION")
    print("=" * 50)
    
    # Load data files
    with open("data/Categories.yaml", 'r', encoding='utf-8') as f:
        categories_data = yaml.safe_load(f)
    
    with open("data/materials.yaml", 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    # Check materialPropertiesDefinitions
    print("\n✅ CHECKING MATERIAL PROPERTIES DEFINITIONS:")
    if 'materialPropertiesDefinitions' in categories_data:
        prop_defs = categories_data['materialPropertiesDefinitions']
        print(f"   📊 Found {len(prop_defs)} property type definitions")
        for prop_type in prop_defs.keys():
            print(f"      • {prop_type}")
    else:
        print("   ❌ materialPropertiesDefinitions not found")
    
    # Check version update
    print("\n✅ CHECKING VERSION UPDATE:")
    metadata = categories_data.get('metadata', {})
    version = metadata.get('version', 'unknown')
    print(f"   📊 Version: {version}")
    
    # Check materials optimization
    print("\n✅ CHECKING MATERIALS OPTIMIZATION:")
    materials = materials_data.get('materials', {})
    
    total_materials = 0
    clean_materials = 0
    materials_with_properties = 0
    
    for category_name, category_data in materials.items():
        if isinstance(category_data, dict) and 'items' in category_data:
            category_materials = category_data['items']
            print(f"   📁 {category_name}: {len(category_materials)} materials")
            
            category_clean = 0
            category_with_props = 0
            
            for material in category_materials:
                if isinstance(material, dict):
                    total_materials += 1
                    
                    # Check for property sections
                    has_properties = any(key.endswith('_properties') for key in material.keys())
                    
                    if has_properties:
                        materials_with_properties += 1
                        category_with_props += 1
                    else:
                        clean_materials += 1
                        category_clean += 1
            
            clean_pct = (category_clean / len(category_materials)) * 100 if category_materials else 0
            print(f"      📊 Clean (inherited): {category_clean}/{len(category_materials)} ({clean_pct:.1f}%)")
            print(f"      📊 With overrides: {category_with_props}/{len(category_materials)}")
    
    optimization_rate = (clean_materials / total_materials) * 100 if total_materials > 0 else 0
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Total materials: {total_materials}")
    print(f"   Clean materials (inherit from category): {clean_materials}")
    print(f"   Materials with property overrides: {materials_with_properties}")
    print(f"   Optimization rate: {optimization_rate:.1f}%")
    
    # Check consolidation report
    print(f"\n✅ CHECKING CONSOLIDATION REPORT:")
    report_files = list(Path(".").glob("property_consolidation_report_*.json"))
    if report_files:
        latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
        with open(latest_report, 'r') as f:
            report = json.load(f)
        
        eliminated = report.get('implementation_results', {}).get('properties_eliminated', 0)
        print(f"   📊 Properties eliminated: {eliminated}")
        print(f"   📊 Report file: {latest_report.name}")
    else:
        print(f"   ⚠️  No consolidation report found")
    
    # Overall assessment
    print(f"\n🏆 VALIDATION RESULT:")
    
    checks_passed = 0
    total_checks = 4
    
    if 'materialPropertiesDefinitions' in categories_data:
        checks_passed += 1
        print(f"   ✅ Property definitions added")
    
    if version.startswith('2.5'):
        checks_passed += 1
        print(f"   ✅ Version updated correctly")
    
    if optimization_rate >= 30:  # At least 30% optimization
        checks_passed += 1
        print(f"   ✅ Good optimization achieved ({optimization_rate:.1f}%)")
    
    if report_files:
        checks_passed += 1
        print(f"   ✅ Consolidation report generated")
    
    success_rate = (checks_passed / total_checks) * 100
    
    if success_rate >= 75:
        print(f"\n🎉 PROPERTY CONSOLIDATION: SUCCESS! ({checks_passed}/{total_checks} checks passed)")
        print(f"✨ Major consolidation objectives achieved")
    else:
        print(f"\n⚠️  PROPERTY CONSOLIDATION: PARTIAL SUCCESS ({checks_passed}/{total_checks} checks passed)")
    
    return {
        'total_materials': total_materials,
        'clean_materials': clean_materials,
        'optimization_rate': optimization_rate,
        'checks_passed': checks_passed,
        'success_rate': success_rate
    }

if __name__ == "__main__":
    quick_validate_consolidation()