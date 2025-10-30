#!/usr/bin/env python3
"""
Property Categorizer Usage Examples

Demonstrates practical applications of the property categorization system.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.core.property_categorizer import get_property_categorizer


def example_1_basic_lookup():
    """Example 1: Basic property category lookup"""
    print("=" * 60)
    print("Example 1: Basic Property Lookup")
    print("=" * 60)
    
    categorizer = get_property_categorizer()
    
    properties = [
        'thermalConductivity',
        'hardness',
        'laserAbsorption',
        'density'
    ]
    
    for prop in properties:
        category = categorizer.get_category(prop)
        tier = categorizer.get_usage_tier(prop)
        cat_info = categorizer.get_category_info(category)
        label = cat_info['label'] if cat_info else category
        print(f"  {prop:25s} → {label:30s} [{tier}]")
    
    print()


def example_2_material_analysis():
    """Example 2: Analyze material property distribution"""
    print("=" * 60)
    print("Example 2: Material Property Distribution")
    print("=" * 60)
    
    categorizer = get_property_categorizer()
    
    # Simulate material properties
    material_properties = {
        'density': 7.85,
        'thermalConductivity': 50.2,
        'specificHeat': 460,
        'hardness': 200,
        'tensileStrength': 400,
        'youngsModulus': 210,
        'laserAbsorption': 0.4,
        'reflectivity': 0.6,
        'electricalResistivity': 1.7e-7
    }
    
    # Categorize properties
    categorized = categorizer.categorize_properties(list(material_properties.keys()))
    
    print("\nProperty Distribution by Category:")
    for category_id, props in sorted(categorized.items()):
        cat_info = categorizer.get_category_info(category_id)
        if cat_info:
            label = cat_info['label']
            print(f"\n  {label}:")
            for prop in props:
                tier = categorizer.get_usage_tier(prop)
                print(f"    - {prop:25s} [{tier}]")
        else:
            print(f"\n  {category_id}:")
            for prop in props:
                print(f"    - {prop}")
    
    print()


def example_3_validate_coverage():
    """Example 3: Validate core property coverage"""
    print("=" * 60)
    print("Example 3: Core Property Coverage Validation")
    print("=" * 60)
    
    categorizer = get_property_categorizer()
    
    # Simulate incomplete material properties
    incomplete_material = {
        'density': 7.85,
        'hardness': 200,
        'laserAbsorption': 0.4
    }
    
    # Get all core properties
    core_props = []
    for category_id in categorizer.get_all_categories():
        props = categorizer.get_properties_by_category(category_id)
        for prop in props:
            if categorizer.get_usage_tier(prop) == 'core':
                core_props.append(prop)
    
    # Check coverage
    missing_core = [p for p in core_props if p not in incomplete_material]
    
    print(f"\nTotal core properties: {len(core_props)}")
    print(f"Properties in material: {len(incomplete_material)}")
    print(f"Missing core properties: {len(missing_core)}")
    
    if missing_core:
        print("\n⚠️  Missing Core Properties:")
        for prop in missing_core[:10]:  # Show first 10
            category = categorizer.get_category(prop)
            cat_info = categorizer.get_category_info(category)
            label = cat_info['label'] if cat_info else category
            print(f"  - {prop:25s} ({label})")
        if len(missing_core) > 10:
            print(f"  ... and {len(missing_core) - 10} more")
    else:
        print("\n✅ All core properties present!")
    
    print()


def example_4_category_statistics():
    """Example 4: Display category statistics"""
    print("=" * 60)
    print("Example 4: Category Statistics")
    print("=" * 60)
    
    categorizer = get_property_categorizer()
    metadata = categorizer.get_metadata()
    
    print(f"\nTaxonomy Version: {metadata['version']}")
    print(f"Last Updated: {metadata['last_updated']}")
    print(f"Total Categories: {metadata['total_categories']}")
    print(f"Total Properties: {metadata['total_properties']}")
    
    print("\nCategory Breakdown:")
    for category_id in categorizer.get_all_categories():
        cat_info = categorizer.get_category_info(category_id)
        if cat_info:
            props = cat_info['properties']
            percentage = cat_info.get('percentage', 0)
            print(f"  {cat_info['label']:30s}: {len(props):2d} properties ({percentage:.1f}%)")
    
    print("\nUsage Tier Distribution:")
    for tier in ['core', 'common', 'specialized']:
        # Count properties in this tier
        count = 0
        for category_id in categorizer.get_all_categories():
            props = categorizer.get_properties_by_category(category_id)
            for prop in props:
                if categorizer.get_usage_tier(prop) == tier:
                    count += 1
        print(f"  {tier.title():12s}: {count:2d} properties")
    
    print()


def example_5_category_listing():
    """Example 5: List all properties by category"""
    print("=" * 60)
    print("Example 5: Complete Property Listing by Category")
    print("=" * 60)
    
    categorizer = get_property_categorizer()
    
    # Pick one category to show in detail
    category_id = 'thermal'
    cat_info = categorizer.get_category_info(category_id)
    
    if cat_info:
        print(f"\nCategory: {cat_info['label']}")
        print(f"Description: {cat_info['description']}")
        print(f"Properties ({len(cat_info['properties'])}):")
        
        for prop in cat_info['properties']:
            tier = categorizer.get_usage_tier(prop)
            tier_badge = '⭐' if tier == 'core' else '◆' if tier == 'common' else '○'
            print(f"  {tier_badge} {prop}")
        
        print(f"\nLegend: ⭐ Core | ◆ Common | ○ Specialized")
    
    print()


if __name__ == '__main__':
    print("\n🔬 Property Categorizer Usage Examples\n")
    
    try:
        example_1_basic_lookup()
        example_2_material_analysis()
        example_3_validate_coverage()
        example_4_category_statistics()
        example_5_category_listing()
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
