#!/usr/bin/env python3
"""
Property Normalization Checker

Verifies:
1. All material properties have corresponding category min/max ranges
2. Property values are consistently structured across all materials
3. Property fields are normalized (value, unit, confidence, source present)
"""

import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Tuple

def load_materials() -> dict:
    """Load Materials.yaml"""
    materials_file = Path('materials/data/Materials.yaml')
    with open(materials_file, 'r') as f:
        return yaml.safe_load(f)

def load_category_ranges() -> dict:
    """Load MaterialProperties.yaml for category ranges"""
    properties_file = Path('materials/data/MaterialProperties.yaml')
    with open(properties_file, 'r') as f:
        return yaml.safe_load(f)

def check_normalization():
    """Main normalization check"""
    print("=" * 80)
    print("PROPERTY NORMALIZATION CHECK")
    print("=" * 80)
    print()
    
    # Load data
    materials_data = load_materials()
    properties_data = load_category_ranges()
    
    materials = materials_data.get('materials', {})
    # MaterialProperties.yaml has category ranges under 'categoryRanges' key
    category_ranges_data = properties_data.get('categoryRanges', {})
    
    # Track all properties used across materials by category
    properties_by_category = defaultdict(set)
    property_structure_issues = []
    
    # Track materials by category
    materials_by_category = defaultdict(list)
    
    print(f"📊 Loaded {len(materials)} materials, {len(category_ranges_data)} categories")
    print()
    
    # Analyze material properties
    for material_name, material_data in materials.items():
        category = material_data.get('category', 'unknown')
        materials_by_category[category].append(material_name)
        
        if 'materialProperties' not in material_data:
            continue
        
        mat_props = material_data['materialProperties']
        
        # Check both property groups
        for group_name in ['material_characteristics', 'laser_material_interaction']:
            if group_name not in mat_props:
                continue
            
            group = mat_props[group_name]
            
            # Skip metadata fields
            metadata_fields = {'label', 'description', 'percentage'}
            
            for prop_name, prop_value in group.items():
                if prop_name in metadata_fields:
                    continue
                
                # Track this property for this category
                properties_by_category[category].add(prop_name)
                
                # Check property structure
                if not isinstance(prop_value, dict):
                    property_structure_issues.append({
                        'material': material_name,
                        'category': category,
                        'property': prop_name,
                        'issue': f'Not a dict: {type(prop_value)}'
                    })
                    continue
                
                # Check required fields
                required_fields = ['value', 'unit', 'confidence', 'source']
                missing_fields = [f for f in required_fields if f not in prop_value]
                
                if missing_fields:
                    property_structure_issues.append({
                        'material': material_name,
                        'category': category,
                        'property': prop_name,
                        'issue': f'Missing fields: {", ".join(missing_fields)}'
                    })
    
    # Check category ranges
    print("=" * 80)
    print("CATEGORY RANGE COVERAGE")
    print("=" * 80)
    print()
    
    missing_ranges = []
    
    for category, properties in sorted(properties_by_category.items()):
        print(f"\n{category.upper()}")
        print("-" * 80)
        
        # Category names in Materials.yaml might have different case/format
        # (e.g., "rare-earth" vs "RARE-EARTH")
        category_key = category.lower().replace('_', '-')
        
        if category_key not in category_ranges_data:
            print(f"  ⚠️  Category '{category_key}' not found in MaterialProperties.yaml")
            continue
        
        category_data = category_ranges_data[category_key]
        category_ranges = category_data.get('ranges', {})
        
        # MaterialProperties.yaml has ranges directly under category
        # Each property has min/max/unit structure
        all_range_properties = set()
        for prop_name in category_ranges.keys():
            # Skip metadata fields
            if prop_name not in ['name', 'description', 'label', 'percentage']:
                all_range_properties.add(prop_name)
        
        print(f"  Materials using this category: {len(materials_by_category[category])}")
        print(f"  Unique properties in materials: {len(properties)}")
        print(f"  Properties with category ranges: {len(all_range_properties)}")
        print()
        
        # Check for missing ranges
        missing = properties - all_range_properties
        if missing:
            print(f"  ⚠️  Properties WITHOUT category ranges ({len(missing)}):")
            for prop in sorted(missing):
                print(f"     - {prop}")
                missing_ranges.append({
                    'category': category,
                    'property': prop,
                    'materials_affected': len([m for m in materials_by_category[category]])
                })
        else:
            print(f"  ✅ All properties have category ranges")
        
        # Check for unused ranges
        unused = all_range_properties - properties
        if unused:
            print(f"  ℹ️  Category ranges NOT used by any material ({len(unused)}):")
            for prop in sorted(unused):
                print(f"     - {prop}")
    
    # Report property structure issues
    print("\n" + "=" * 80)
    print("PROPERTY STRUCTURE ISSUES")
    print("=" * 80)
    print()
    
    if property_structure_issues:
        print(f"⚠️  Found {len(property_structure_issues)} structure issues:\n")
        
        # Group by issue type
        by_issue = defaultdict(list)
        for issue in property_structure_issues:
            by_issue[issue['issue']].append(issue)
        
        for issue_type, issues in sorted(by_issue.items()):
            print(f"  {issue_type} ({len(issues)} occurrences):")
            for issue in issues[:5]:  # Show first 5
                print(f"    - {issue['material']}: {issue['property']}")
            if len(issues) > 5:
                print(f"    ... and {len(issues) - 5} more")
            print()
    else:
        print("✅ All properties have correct structure (value, unit, confidence, source)")
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Categories analyzed: {len(properties_by_category)}")
    print(f"Total unique properties across all materials: {len(set().union(*properties_by_category.values()))}")
    print(f"Properties missing category ranges: {len(missing_ranges)}")
    print(f"Property structure issues: {len(property_structure_issues)}")
    print()
    
    if missing_ranges:
        print("=" * 80)
        print("MISSING CATEGORY RANGES DETAILS")
        print("=" * 80)
        print()
        for item in missing_ranges:
            print(f"  {item['category']}.{item['property']}")
            print(f"    Affects {item['materials_affected']} materials")
        print()
    
    return len(missing_ranges) == 0 and len(property_structure_issues) == 0

if __name__ == '__main__':
    import sys
    success = check_normalization()
    sys.exit(0 if success else 1)
