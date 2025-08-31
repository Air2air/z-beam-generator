#!/usr/bin/env python3
"""
Test the enhanced percentile system with Phase 1 & 2 properties.
Tests the complete pipeline: material data -> percentile enhancement -> validation.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.property_enhancer import enhance_frontmatter_with_context
from utils.percentile_calculator import extract_numeric_value


def test_enhanced_material():
    """Test enhanced system with a comprehensive material including all new properties."""
    
    print("=== Enhanced Percentile System Test ===")
    print("Testing material with Phase 1 & 2 properties (laser-specific and thermal)")
    
    # Create a comprehensive test material with all 11 properties
    test_material = {
        'name': 'Aluminum 6061',
        'category': 'metal',
        'description': 'Versatile aluminum alloy with excellent machinability',
        'properties': {
            # Original 6 properties
            'density': '2.70 g/cm³',
            'meltingPoint': '660°C',
            'thermalConductivity': '167 W/m·K',
            'tensileStrength': '310 MPa',
            'hardness': '95 HB',
            'youngsModulus': '69 GPa',
            
            # Phase 1 & 2: New laser-specific and thermal properties
            'laserAbsorption': '0.1 cm⁻¹',     # Low absorption (highly reflective)
            'laserReflectivity': '90%',         # High reflectivity (typical for polished aluminum)
            'thermalDiffusivity': '97 mm²/s',   # High thermal diffusivity
            'thermalExpansion': '23.6 µm/m·K',  # Moderate thermal expansion
            'specificHeat': '0.90 J/g·K'       # High specific heat capacity
        }
    }
    
    print(f"\nTesting material: {test_material['name']}")
    print(f"Category: {test_material['category']}")
    
    # Enhance the material with percentile calculations
    enhanced = enhance_frontmatter_with_context(test_material, 'metal')
    
    if not enhanced:
        print("❌ Enhancement failed!")
        return False
    
    properties = enhanced.get('properties', {})
    
    print("\n=== Property Analysis ===")
    
    # Define expected property mappings for validation
    property_tests = [
        ('density', 'Density', 'g/cm³'),
        ('meltingPoint', 'Melting Point', '°C'),
        ('thermalConductivity', 'Thermal Conductivity', 'W/m·K'),
        ('tensileStrength', 'Tensile Strength', 'MPa'),
        ('hardness', 'Hardness', 'HB'),
        ('youngsModulus', 'Young\'s Modulus', 'GPa'),
        ('laserAbsorption', 'Laser Absorption', 'cm⁻¹'),
        ('laserReflectivity', 'Laser Reflectivity', '%'),
        ('thermalDiffusivity', 'Thermal Diffusivity', 'mm²/s'),
        ('thermalExpansion', 'Thermal Expansion', 'µm/m·K'),
        ('specificHeat', 'Specific Heat', 'J/g·K')
    ]
    
    all_passed = True
    percentile_count = 0
    
    for prop_key, display_name, unit in property_tests:
        if prop_key in properties:
            value = properties[prop_key]
            percentile_key = prop_key + 'Percentile'
            
            if percentile_key in properties:
                percentile = properties[percentile_key]
                percentile_count += 1
                
                # Validate percentile is reasonable (0-100)
                if 0 <= percentile <= 100:
                    status = "✅"
                else:
                    status = "❌"
                    all_passed = False
                
                print(f"{status} {display_name}: {value} ({percentile}% within category)")
            else:
                print(f"❌ {display_name}: {value} (NO PERCENTILE)")
                all_passed = False
        else:
            print(f"❌ {display_name}: MISSING")
            all_passed = False
    
    print("\n=== Results Summary ===")
    print(f"Properties tested: {len(property_tests)}")
    print(f"Percentiles calculated: {percentile_count}")
    print(f"Enhanced properties total: {len(properties)}")
    
    # Test specific new property calculations
    print("\n=== New Property Validation ===")
    
    # Test laser absorption percentile (aluminum should be low - highly reflective)
    laser_absorption_percentile = properties.get('laserAbsorptionPercentile', 0)
    if laser_absorption_percentile < 20:  # Should be low for reflective aluminum
        print(f"✅ Laser Absorption percentile correct: {laser_absorption_percentile}% (low for reflective metal)")
    else:
        print(f"❌ Laser Absorption percentile unexpected: {laser_absorption_percentile}%")
        all_passed = False
    
    # Test laser reflectivity percentile (aluminum should be high)
    laser_reflectivity_percentile = properties.get('laserReflectivityPercentile', 0)
    if laser_reflectivity_percentile > 80:  # Should be high for polished aluminum
        print(f"✅ Laser Reflectivity percentile correct: {laser_reflectivity_percentile}% (high for polished metal)")
    else:
        print(f"❌ Laser Reflectivity percentile unexpected: {laser_reflectivity_percentile}%")
        all_passed = False
    
    # Test thermal diffusivity (aluminum should be high)
    thermal_diffusivity_percentile = properties.get('thermalDiffusivityPercentile', 0)
    if thermal_diffusivity_percentile > 50:  # Should be moderate-high for aluminum
        print(f"✅ Thermal Diffusivity percentile correct: {thermal_diffusivity_percentile}% (good conductor)")
    else:
        print(f"❌ Thermal Diffusivity percentile unexpected: {thermal_diffusivity_percentile}%")
        all_passed = False
    
    print("\n=== Unit Parsing Test ===")
    
    # Test that our new units parse correctly
    unit_tests = [
        ("0.1 cm⁻¹", 0.1),
        ("90%", 90.0),
        ("97 mm²/s", 97.0),
        ("23.6 µm/m·K", 23.6),
        ("0.90 J/g·K", 0.90),
        ("1.5e-2 cm⁻¹", 0.015)
    ]
    
    for test_value, expected in unit_tests:
        result = extract_numeric_value(test_value)
        if abs(result - expected) < 0.001:
            print(f"✅ Unit parsing: '{test_value}' -> {result}")
        else:
            print(f"❌ Unit parsing: '{test_value}' -> {result} (expected {expected})")
            all_passed = False
    
    print("\n=== Final Assessment ===")
    if all_passed and percentile_count == 11:
        print("🎉 ALL TESTS PASSED! Enhanced percentile system working correctly.")
        print("✅ Phase 1 & 2 implementation complete:")
        print("   - Laser-specific properties (absorption, reflectivity)")
        print("   - Thermal properties (diffusivity, expansion, specific heat)")
        print("   - Unit parsing for specialized units")
        print("   - Percentile calculations for all 11 properties")
        return True
    else:
        print("❌ Some tests failed. System needs debugging.")
        return False


def test_category_coverage():
    """Test that all categories have the new properties."""
    
    print("\n=== Category Coverage Test ===")
    
    from utils.property_enhancer import load_category_ranges
    
    ranges = load_category_ranges()
    
    expected_properties = [
        'density', 'tensileStrength', 'thermalConductivity', 'meltingPoint', 
        'hardness', 'youngsModulus', 'laserAbsorption', 'laserReflectivity', 
        'thermalDiffusivity', 'thermalExpansion', 'specificHeat'
    ]
    
    all_categories_complete = True
    
    for category, props in ranges.items():
        missing_props = []
        for expected_prop in expected_properties:
            if expected_prop not in props:
                missing_props.append(expected_prop)
        
        if missing_props:
            print(f"❌ {category}: Missing {missing_props}")
            all_categories_complete = False
        else:
            print(f"✅ {category}: All {len(expected_properties)} properties present")
    
    if all_categories_complete:
        print("🎉 All categories have complete property sets!")
    else:
        print("❌ Some categories are missing properties.")
    
    return all_categories_complete


if __name__ == "__main__":
    print("Starting Enhanced Percentile System Validation...\n")
    
    # Test 1: Enhanced material processing
    test1_passed = test_enhanced_material()
    
    # Test 2: Category coverage
    test2_passed = test_category_coverage()
    
    print(f"\n{'='*50}")
    print("FINAL VALIDATION RESULTS:")
    print(f"Enhanced Material Test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"Category Coverage Test: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🚀 PHASE 1 & 2 IMPLEMENTATION COMPLETE!")
        print("The Z-Beam percentile system now supports:")
        print("• 11 material properties (6 original + 5 new)")
        print("• Laser-specific properties for cleaning optimization")
        print("• Thermal properties for safety and processing")
        print("• All 8 material categories fully supported")
        print("• Advanced unit parsing (cm⁻¹, mm²/s, µm/m·K, J/g·K, %)")
    else:
        print("\n⚠️  System validation incomplete. Please review errors above.")
    
    print(f"{'='*50}")
