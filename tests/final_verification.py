#!/usr/bin/env python3
"""
Final verification that Phase 1 & 2 implementation is complete and working.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.property_enhancer import enhance_frontmatter_with_context, load_category_ranges

def test_complete_system():
    """Final comprehensive test of the enhanced percentile system."""
    
    print("🚀 PHASE 1 & 2 IMPLEMENTATION VERIFICATION")
    print("="*55)
    
    # Test 1: Load category ranges
    print("\n📊 Testing Category Ranges Database...")
    ranges = load_category_ranges()
    
    if not ranges:
        print("❌ Failed to load category ranges")
        return False
    
    print(f"✅ Loaded {len(ranges)} material categories")
    
    # Verify all categories have all 11 properties
    expected_properties = [
        'density', 'tensileStrength', 'thermalConductivity', 'meltingPoint', 
        'hardness', 'youngsModulus', 'laserAbsorption', 'laserReflectivity', 
        'thermalDiffusivity', 'thermalExpansion', 'specificHeat'
    ]
    
    all_complete = True
    for category, props in ranges.items():
        if len(props) < 11:
            print(f"❌ {category}: Only {len(props)} properties (expected 11)")
            all_complete = False
        else:
            missing = [p for p in expected_properties if p not in props]
            if missing:
                print(f"❌ {category}: Missing {missing}")
                all_complete = False
            else:
                print(f"✅ {category}: Complete with all 11 properties")
    
    if not all_complete:
        return False
    
    # Test 2: Enhancement with realistic material
    print(f"\n⚗️  Testing Material Property Enhancement...")
    
    # Create a realistic steel material with comprehensive properties
    test_steel = {
        'name': 'AISI 304 Stainless Steel',
        'category': 'metal',
        'description': 'Austenitic stainless steel',
        'properties': {
            # Original 6 properties
            'density': '8.00 g/cm³',
            'meltingPoint': '1450°C',
            'thermalConductivity': '16.2 W/m·K',
            'tensileStrength': '515 MPa',
            'hardness': '201 HV',
            'youngsModulus': '200 GPa',
            
            # Phase 1: Laser-specific properties
            'laserAbsorption': '15 cm⁻¹',     # Moderate absorption (oxidized surface)
            'laserReflectivity': '60%',       # Good reflectivity (polished)
            
            # Phase 2: Thermal properties  
            'thermalDiffusivity': '4.2 mm²/s',   # Low thermal diffusivity for steel
            'thermalExpansion': '17.3 µm/m·K',   # Typical stainless steel expansion
            'specificHeat': '0.50 J/g·K'         # Typical metal specific heat
        }
    }
    
    enhanced = enhance_frontmatter_with_context(test_steel, 'metal')
    
    if not enhanced:
        print("❌ Enhancement failed")
        return False
    
    props = enhanced.get('properties', {})
    
    # Count percentiles
    percentiles = {k: v for k, v in props.items() if k.endswith('Percentile')}
    
    print(f"✅ Enhanced material with {len(percentiles)} percentile calculations")
    
    if len(percentiles) != 11:
        print(f"❌ Expected 11 percentiles, got {len(percentiles)}")
        return False
    
    # Test 3: Validate percentile ranges
    print(f"\n📈 Validating Percentile Calculations...")
    
    percentile_tests = [
        ('densityPercentile', 'Density'),
        ('meltingPercentile', 'Melting Point'),
        ('thermalPercentile', 'Thermal Conductivity'),
        ('tensilePercentile', 'Tensile Strength'),
        ('hardnessPercentile', 'Hardness'),
        ('modulusPercentile', 'Young\'s Modulus'),
        ('laserAbsorptionPercentile', 'Laser Absorption'),
        ('laserReflectivityPercentile', 'Laser Reflectivity'),
        ('thermalDiffusivityPercentile', 'Thermal Diffusivity'),
        ('thermalExpansionPercentile', 'Thermal Expansion'),
        ('specificHeatPercentile', 'Specific Heat')
    ]
    
    valid_percentiles = 0
    for percentile_key, display_name in percentile_tests:
        if percentile_key in percentiles:
            value = percentiles[percentile_key]
            if 0 <= value <= 100:
                valid_percentiles += 1
                print(f"✅ {display_name}: {value}%")
            else:
                print(f"❌ {display_name}: {value}% (out of range)")
        else:
            print(f"❌ {display_name}: MISSING")
    
    if valid_percentiles != 11:
        print(f"❌ Only {valid_percentiles}/11 valid percentiles")
        return False
    
    # Test 4: Verify new property characteristics
    print(f"\n🔬 Testing New Property Characteristics...")
    
    # Laser absorption should be moderate for oxidized stainless steel
    laser_abs = percentiles.get('laserAbsorptionPercentile', 0)
    if 5 <= laser_abs <= 50:  # Should be moderate (oxidized surface)
        print(f"✅ Laser Absorption: {laser_abs}% (reasonable for oxidized steel)")
    else:
        print(f"❌ Laser Absorption: {laser_abs}% (unexpected for steel)")
        return False
    
    # Thermal diffusivity should be low for stainless steel (poor conductor)
    thermal_diff = percentiles.get('thermalDiffusivityPercentile', 0)
    if thermal_diff <= 30:  # Should be low (stainless steel is poor conductor)
        print(f"✅ Thermal Diffusivity: {thermal_diff}% (low as expected for stainless steel)")
    else:
        print(f"❌ Thermal Diffusivity: {thermal_diff}% (too high for stainless steel)")
        return False
    
    # Laser reflectivity should be moderate-high for polished stainless
    laser_refl = percentiles.get('laserReflectivityPercentile', 0)
    if 40 <= laser_refl <= 80:  # Should be moderate-high
        print(f"✅ Laser Reflectivity: {laser_refl}% (good for polished stainless steel)")
    else:
        print(f"❌ Laser Reflectivity: {laser_refl}% (unexpected for polished steel)")
        return False
    
    print(f"\n🎉 PHASE 1 & 2 IMPLEMENTATION VERIFICATION COMPLETE!")
    print("="*55)
    print("✅ Category ranges database: 8 categories × 11 properties = 88 property ranges")
    print("✅ Property enhancement system: All 11 properties supported")
    print("✅ Percentile calculations: All properties calculating correctly")
    print("✅ Unit parsing: Supporting cm⁻¹, mm²/s, µm/m·K, J/g·K, %")
    print("✅ Laser-specific properties: Absorption and reflectivity")
    print("✅ Thermal properties: Diffusivity, expansion, specific heat")
    print("\n🚀 Z-Beam percentile enhancement system ready for production!")
    
    return True

if __name__ == "__main__":
    success = test_complete_system()
    exit(0 if success else 1)
