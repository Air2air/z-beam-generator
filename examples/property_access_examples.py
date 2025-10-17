#!/usr/bin/env python3
"""
Property Access Examples

Demonstrates how to work with different property patterns in Materials.yaml
using the PropertyAccessor helper methods.

Usage:
    python3 examples/property_access_examples.py
"""

import sys
from pathlib import Path
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.property_helpers import PropertyAccessor, CategoryHelper


def load_data():
    """Load Materials.yaml and Categories.yaml"""
    materials_path = project_root / 'data' / 'Materials.yaml'
    categories_path = project_root / 'data' / 'Categories.yaml'
    
    with open(materials_path, 'r') as f:
        materials_data = yaml.safe_load(f)
    
    with open(categories_path, 'r') as f:
        categories_data = yaml.safe_load(f)
    
    return materials_data, categories_data


def example_1_simple_property():
    """Example 1: Access simple property value"""
    print("\n" + "="*70)
    print("Example 1: Simple Property Access")
    print("="*70)
    
    materials_data, _ = load_data()
    materials = materials_data.get('materials', materials_data)
    
    # Get Copper material
    copper = materials.get('Copper')
    if not copper:
        print("❌ Copper not found in materials")
        return
    
    # Direct access (verbose way)
    density_data = copper['properties']['density']
    density_value = density_data['value']
    density_unit = density_data['unit']
    print(f"\n📊 Direct access:")
    print(f"   Copper density: {density_value} {density_unit}")
    
    # Using helper (simple way)
    density = PropertyAccessor.get_value(copper['properties']['density'])
    print(f"\n✨ Using helper:")
    print(f"   Copper density: {density} g/cm³")


def example_2_nested_property():
    """Example 2: Access nested thermalDestruction property"""
    print("\n" + "="*70)
    print("Example 2: Nested Property Access (thermalDestruction)")
    print("="*70)
    
    materials_data, _ = load_data()
    materials = materials_data.get('materials', materials_data)
    
    copper = materials.get('Copper')
    if not copper or 'thermalDestruction' not in copper['properties']:
        print("❌ Copper thermal destruction data not found")
        return
    
    # Direct access (very verbose)
    try:
        thermal_dest = copper['properties']['thermalDestruction']
        temp = thermal_dest['point']['value']
        unit = thermal_dest['point']['unit']
        dtype = thermal_dest['type']
        print(f"\n📊 Direct access:")
        print(f"   Copper melting point: {temp} {unit}")
        print(f"   Destruction type: {dtype}")
    except KeyError as e:
        print(f"❌ Direct access failed: {e}")
    
    # Using helper (much simpler)
    temp = PropertyAccessor.get_thermal_destruction_point(copper)
    dtype = PropertyAccessor.get_thermal_destruction_type(copper)
    print(f"\n✨ Using helper:")
    print(f"   Copper melting point: {temp} K")
    print(f"   Destruction type: {dtype}")


def example_3_pulse_specific():
    """Example 3: Access pulse-specific ablation threshold"""
    print("\n" + "="*70)
    print("Example 3: Pulse-Specific Property (ablationThreshold)")
    print("="*70)
    
    materials_data, _ = load_data()
    materials = materials_data.get('materials', materials_data)
    
    # Find a material with pulse-specific ablation data
    material_with_ablation = None
    material_name = None
    
    for name, mat_data in materials.items():
        ablation = mat_data.get('properties', {}).get('ablationThreshold')
        if ablation and 'nanosecond' in ablation:
            material_with_ablation = mat_data
            material_name = name
            break
    
    if not material_with_ablation:
        print("ℹ️  No materials found with pulse-specific ablation data")
        return
    
    print(f"\n📌 Material: {material_name}")
    
    # Access different pulse durations
    for pulse_type in ['nanosecond', 'picosecond', 'femtosecond']:
        threshold = PropertyAccessor.get_ablation_threshold(
            material_with_ablation,
            pulse_type=pulse_type
        )
        if threshold:
            print(f"   {pulse_type.capitalize():12} ablation: {threshold:.2f} J/cm²")
    
    # Get as range
    ns_range = PropertyAccessor.get_ablation_threshold(
        material_with_ablation,
        pulse_type='nanosecond',
        return_range=True
    )
    if ns_range:
        print(f"\n✨ Nanosecond range: {ns_range[0]}-{ns_range[1]} J/cm²")


def example_4_wavelength_specific():
    """Example 4: Access wavelength-specific reflectivity"""
    print("\n" + "="*70)
    print("Example 4: Wavelength-Specific Property (reflectivity)")
    print("="*70)
    
    materials_data, _ = load_data()
    materials = materials_data.get('materials', materials_data)
    
    # Find a material with wavelength-specific reflectivity
    material_with_refl = None
    material_name = None
    
    for name, mat_data in materials.items():
        refl = mat_data.get('properties', {}).get('reflectivity')
        if refl and 'at_1064nm' in refl:
            material_with_refl = mat_data
            material_name = name
            break
    
    if not material_with_refl:
        print("ℹ️  No materials found with wavelength-specific reflectivity")
        return
    
    print(f"\n📌 Material: {material_name}")
    
    # Access different wavelengths
    wavelengths = [
        ('1064nm', 'Nd:YAG/Fiber'),
        ('532nm', 'Green doubled Nd:YAG'),
        ('355nm', 'UV tripled Nd:YAG'),
        ('10640nm', 'CO2 laser')
    ]
    
    for wl, laser_type in wavelengths:
        refl = PropertyAccessor.get_reflectivity(
            material_with_refl,
            wavelength=wl
        )
        if refl:
            print(f"   {wl:8} ({laser_type:20}): {refl:.1f}%")


def example_5_category_ranges():
    """Example 5: Access category ranges"""
    print("\n" + "="*70)
    print("Example 5: Category Range Access")
    print("="*70)
    
    _, categories_data = load_data()
    
    # Get metal category density range
    density_range = PropertyAccessor.get_category_range(
        categories_data,
        'metal',
        'density'
    )
    
    if density_range:
        print(f"\n📊 Metal density range:")
        print(f"   Min: {density_range['min']} {density_range['unit']}")
        print(f"   Max: {density_range['max']} {density_range['unit']}")
        print(f"   Range: Lithium ({density_range['min']}) to Osmium ({density_range['max']})")
    
    # Get thermal destruction range for metals (nested structure)
    thermal_range = PropertyAccessor.get_category_range(
        categories_data,
        'metal',
        'thermalDestruction'
    )
    
    if thermal_range:
        print(f"\n🔥 Metal thermal destruction range:")
        print(f"   Min: {thermal_range['min']} {thermal_range['unit']}")
        print(f"   Max: {thermal_range['max']} {thermal_range['unit']}")
        print(f"   Range: Mercury ({thermal_range['min']}) to Tungsten ({thermal_range['max']})")


def example_6_validation():
    """Example 6: Validate property values against category ranges"""
    print("\n" + "="*70)
    print("Example 6: Property Validation")
    print("="*70)
    
    materials_data, categories_data = load_data()
    materials = materials_data.get('materials', materials_data)
    
    # Check Copper density
    copper = materials.get('Copper')
    if not copper:
        return
    
    copper_density = PropertyAccessor.get_value(copper['properties']['density'])
    density_range = PropertyAccessor.get_category_range(
        categories_data,
        'metal',
        'density'
    )
    
    if copper_density and density_range:
        in_range = CategoryHelper.is_value_in_range(
            copper_density,
            density_range['min'],
            density_range['max']
        )
        
        print(f"\n✓ Copper density: {copper_density} g/cm³")
        print(f"  Category range: {density_range['min']}-{density_range['max']} g/cm³")
        print(f"  Status: {'✅ VALID' if in_range else '❌ OUT OF RANGE'}")


def example_7_pattern_detection():
    """Example 7: Detect property patterns"""
    print("\n" + "="*70)
    print("Example 7: Pattern Detection")
    print("="*70)
    
    materials_data, _ = load_data()
    materials = materials_data.get('materials', materials_data)
    
    # Get first material with properties
    for material_name, material_data in list(materials.items())[:3]:
        print(f"\n📌 {material_name}:")
        
        properties = material_data.get('properties', {})
        for prop_name, prop_data in list(properties.items())[:5]:
            pattern = PropertyAccessor.detect_property_pattern(prop_data)
            value = PropertyAccessor.get_value(prop_data)
            
            print(f"   {prop_name:20} → {pattern:20} (value: {value})")


def example_8_get_all_properties():
    """Example 8: Get all properties as flat dictionary"""
    print("\n" + "="*70)
    print("Example 8: Get All Property Values")
    print("="*70)
    
    materials_data, _ = load_data()
    materials = materials_data.get('materials', materials_data)
    
    copper = materials.get('Copper')
    if not copper:
        return
    
    # Get all property values as flat dict
    all_values = PropertyAccessor.get_all_property_values(copper)
    
    print(f"\n📊 All Copper properties:")
    for prop_name, value in sorted(all_values.items()):
        print(f"   {prop_name:25} = {value}")


def example_9_category_helpers():
    """Example 9: Category helper methods"""
    print("\n" + "="*70)
    print("Example 9: Category Helpers")
    print("="*70)
    
    _, categories_data = load_data()
    
    # List all categories
    categories = CategoryHelper.get_all_categories(categories_data)
    print(f"\n📋 All categories ({len(categories)}):")
    for cat in categories:
        print(f"   • {cat}")
    
    # List all properties in metal category
    metal_props = CategoryHelper.get_all_properties_in_category(
        categories_data,
        'metal'
    )
    print(f"\n🔧 Metal category properties ({len(metal_props)}):")
    for prop in sorted(metal_props):
        print(f"   • {prop}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("🎯 Property Access Helper Examples")
    print("="*70)
    print("\nThese examples demonstrate how to use PropertyAccessor helpers")
    print("to simplify working with Materials.yaml and Categories.yaml data.")
    
    try:
        example_1_simple_property()
        example_2_nested_property()
        example_3_pulse_specific()
        example_4_wavelength_specific()
        example_5_category_ranges()
        example_6_validation()
        example_7_pattern_detection()
        example_8_get_all_properties()
        example_9_category_helpers()
        
        print("\n" + "="*70)
        print("✅ All examples completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
