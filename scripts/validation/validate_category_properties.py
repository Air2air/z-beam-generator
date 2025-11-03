#!/usr/bin/env python3
"""
Validate Material Properties Against Category Definitions

This script checks all materials in Materials.yaml to ensure they only have
properties that are defined in their category's category_ranges in Categories.yaml.

Enforces the VITAL PROPERTY VALIDATION RULE from DATA_ARCHITECTURE.md:
"If a property is NOT defined in Categories.yaml for a given category, it MUST NOT
be added to any material in that category in Materials.yaml."

Author: GitHub Copilot
Date: October 17, 2025
"""

import yaml
from pathlib import Path
from collections import defaultdict
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from materials.utils.category_property_cache import CategoryPropertyCache


def validate_material_properties():
    """Validate all material properties against category definitions."""
    
    print("="*80)
    print("MATERIAL PROPERTY VALIDATION")
    print("="*80)
    print()
    print("Enforcing: VITAL PROPERTY VALIDATION RULE")
    print("Rule: Properties must be defined in category_ranges to exist in materials")
    print()
    
    # Load category property cache
    cache = CategoryPropertyCache()
    valid_properties_by_category = cache.load()
    
    print(f"✅ Loaded property definitions for {len(valid_properties_by_category)} categories:")
    for cat_name, props in sorted(valid_properties_by_category.items()):
        print(f"   {cat_name:15s}: {len(props)} properties")
    print()
    
    # Load materials
    materials_file = Path("data/Materials.yaml")
    with open(materials_file) as f:
        materials_data = yaml.safe_load(f)
    
    materials_section = materials_data.get('materials', {})
    print(f"📊 Analyzing {len(materials_section)} materials...")
    print()
    
    # Validate each material
    violations = []
    valid_materials = 0
    
    for material_name, material_data in materials_section.items():
        if not isinstance(material_data, dict):
            continue
        
        category = material_data.get('category', 'unknown')
        valid_props = valid_properties_by_category.get(category, set())
        
        if not valid_props:
            violations.append({
                'material': material_name,
                'category': category,
                'error': f"Unknown category '{category}'",
                'invalid_properties': set()
            })
            continue
        
        material_props = set(material_data.get('materialProperties', {}).keys())
        invalid_props = material_props - valid_props
        
        if invalid_props:
            violations.append({
                'material': material_name,
                'category': category,
                'invalid_properties': invalid_props,
                'error': None
            })
        else:
            valid_materials += 1
    
    # Report results
    print("="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    print()
    
    if not violations:
        print("✅ SUCCESS: All materials have valid properties for their categories!")
        print(f"   {valid_materials} materials validated")
        print()
        return True
    
    # Show violations
    print(f"❌ FAILED: Found {len(violations)} materials with invalid properties")
    print()
    
    # Group by violation type
    unknown_categories = [v for v in violations if v['error']]
    invalid_properties = [v for v in violations if not v['error']]
    
    if unknown_categories:
        print(f"Unknown Categories ({len(unknown_categories)} materials):")
        print("-"*80)
        for v in unknown_categories:
            print(f"  {v['material']:30s} → category '{v['category']}' not found")
        print()
    
    if invalid_properties:
        print(f"Invalid Properties ({len(invalid_properties)} materials):")
        print("-"*80)
        
        # Show detailed violations
        for v in sorted(invalid_properties, key=lambda x: len(x['invalid_properties']), reverse=True)[:20]:
            print(f"\n  {v['material']} ({v['category']}):")
            print(f"    Invalid properties: {', '.join(sorted(v['invalid_properties']))}")
            
            # Show what properties ARE valid for this category
            valid_for_cat = valid_properties_by_category.get(v['category'], set())
            print(f"    Valid for {v['category']}: {len(valid_for_cat)} properties")
        
        if len(invalid_properties) > 20:
            print(f"\n  ... and {len(invalid_properties) - 20} more materials with violations")
        print()
    
    # Show statistics
    print("="*80)
    print("STATISTICS")
    print("="*80)
    
    # Count violations by property
    property_violation_counts = defaultdict(int)
    for v in invalid_properties:
        for prop in v['invalid_properties']:
            property_violation_counts[prop] += 1
    
    if property_violation_counts:
        print()
        print("Most Common Invalid Properties:")
        print("-"*80)
        for prop, count in sorted(property_violation_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {prop:30s}: {count:3d} materials")
    
    # Count violations by category
    category_violation_counts = defaultdict(int)
    for v in invalid_properties:
        category_violation_counts[v['category']] += 1
    
    if category_violation_counts:
        print()
        print("Violations by Category:")
        print("-"*80)
        for cat, count in sorted(category_violation_counts.items(), key=lambda x: x[1], reverse=True):
            total_in_cat = sum(1 for m in materials_section.values() 
                              if isinstance(m, dict) and m.get('category') == cat)
            pct = (count / total_in_cat * 100) if total_in_cat > 0 else 0
            print(f"  {cat:15s}: {count:3d}/{total_in_cat:3d} materials ({pct:5.1f}%)")
    
    print()
    print("="*80)
    print("RECOMMENDED ACTIONS")
    print("="*80)
    print()
    print("1. Review invalid properties - may indicate:")
    print("   • Properties that should be added to Categories.yaml")
    print("   • Properties that are incorrectly assigned to materials")
    print("   • Materials with incorrect category assignments")
    print()
    print("2. For properties that should exist:")
    print("   • Add category_ranges to Categories.yaml for the relevant categories")
    print("   • Re-run this validation")
    print()
    print("3. For incorrect properties:")
    print("   • Remove from Materials.yaml")
    print("   • Update material category if misclassified")
    print()
    
    return False


if __name__ == "__main__":
    success = validate_material_properties()
    sys.exit(0 if success else 1)
