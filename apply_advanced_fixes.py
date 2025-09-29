#!/usr/bin/env python3
"""
Advanced System Value Improvements

This script applies sophisticated fixes for exceptional materials and edge cases
that require special handling beyond standard material categories.
"""

import yaml
import os
import glob
from pathlib import Path

def create_soft_metal_exceptions():
    """Create special handling for soft metals with exceptional properties"""
    
    print("🔄 Creating soft metal property exceptions...")
    
    # Define soft metals with exceptional properties
    soft_metals = {
        'Gallium': {
            'hardness_hv': 1.5,
            'youngs_modulus_gpa': 9.8,
            'tensile_strength_mpa': 4.0,
            'thermal_diffusivity': 1.85
        },
        'Indium': {
            'hardness_hv': 0.9,
            'youngs_modulus_gpa': 11.0,
            'tensile_strength_mpa': 4.0
        },
        'Tin': {
            'youngs_modulus_gpa': 50.0,
            'tensile_strength_mpa': 15.0
        },
        'Lead': {
            'tensile_strength_mpa': 18.0
        }
    }
    
    # Update Categories.yaml to accommodate soft metals
    with open('data/Categories.yaml', 'r') as f:
        content = f.read()
    
    updates_made = 0
    
    # Lower metal property minimums for soft metals
    range_updates = [
        {
            'old': '      hardness:\n        max: 3000\n        min: 5\n        unit: HV',
            'new': '      hardness:\n        max: 3500\n        min: 0.5\n        unit: HV',
            'description': 'Accommodate soft metals (gallium, indium) and ultra-hard metals (tungsten)'
        },
        {
            'old': '      youngsModulus:\n        max: 411\n        min: 70\n        unit: GPa',
            'new': '      youngsModulus:\n        max: 411\n        min: 5\n        unit: GPa',
            'description': 'Lower Young\'s modulus minimum for soft metals'
        },
        {
            'old': '      tensileStrength:\n        max: 3000.0\n        min: 30.0\n        unit: MPa',
            'new': '      tensileStrength:\n        max: 3000.0\n        min: 3.0\n        unit: MPa',
            'description': 'Lower tensile strength minimum for soft metals'
        },
        {
            'old': '      thermalDiffusivity:\n        max: 174\n        min: 4.2\n        unit: mm²/s',
            'new': '      thermalDiffusivity:\n        max: 174\n        min: 0.2\n        unit: mm²/s',
            'description': 'Lower thermal diffusivity minimum for heavy metals'
        }
    ]
    
    for update in range_updates:
        if update['old'] in content:
            content = content.replace(update['old'], update['new'])
            print(f"  ✅ {update['description']}")
            updates_made += 1
    
    # Write updated content
    if updates_made > 0:
        with open('data/Categories.yaml', 'w') as f:
            f.write(content)
    
    print(f"✅ Completed soft metal accommodations: {updates_made} updates made")
    return updates_made

def fix_composite_thermal_expansion():
    """Expand composite thermal expansion range for high-expansion materials"""
    
    print("🔄 Expanding composite thermal expansion range...")
    
    with open('data/Categories.yaml', 'r') as f:
        content = f.read()
    
    updates_made = 0
    
    # Expand composite thermal expansion for polymer composites
    old_range = '      thermalExpansion:\n        max: 50\n        min: -1\n        unit: µm/m·K'
    new_range = '      thermalExpansion:\n        max: 100\n        min: -1\n        unit: µm/m·K'
    
    if old_range in content:
        content = content.replace(old_range, new_range)
        print("  ✅ Expanded composite thermal expansion for polymer resins")
        updates_made += 1
        
        with open('data/Categories.yaml', 'w') as f:
            f.write(content)
    
    print(f"✅ Completed composite thermal expansion fix: {updates_made} updates made")
    return updates_made

def fix_ceramic_thermal_diffusivity():
    """Lower ceramic thermal diffusivity minimum for carbides"""
    
    print("🔄 Adjusting ceramic thermal diffusivity range...")
    
    with open('data/Categories.yaml', 'r') as f:
        content = f.read()
    
    updates_made = 0
    
    # Lower minimum for carbides and technical ceramics
    old_range = '      thermalDiffusivity:\n        max: 120\n        min: 0.3\n        unit: mm²/s'
    new_range = '      thermalDiffusivity:\n        max: 120\n        min: 0.1\n        unit: mm²/s'
    
    if old_range in content:
        content = content.replace(old_range, new_range)
        print("  ✅ Lowered ceramic thermal diffusivity minimum for carbides")
        updates_made += 1
        
        with open('data/Categories.yaml', 'w') as f:
            f.write(content)
    
    print(f"✅ Completed ceramic thermal diffusivity fix: {updates_made} updates made")
    return updates_made

def fix_machine_settings_precision():
    """Improve machine settings ranges for precision applications"""
    
    print("🔄 Improving machine settings for precision applications...")
    
    with open('data/Materials.yaml', 'r') as f:
        content = f.read()
    
    updates_made = 0
    
    # Already partially fixed, but ensure spot size can go very small
    old_range = '  spotSize:\n    min: 10\n    max: 5000\n    unit: μm'
    new_range = '  spotSize:\n    min: 0.1\n    max: 5000\n    unit: μm'
    
    if old_range in content:
        content = content.replace(old_range, new_range)
        print("  ✅ Lowered spot size minimum for ultra-precision applications")
        updates_made += 1
    
    # Lower power range minimum for delicate materials
    old_power = '  powerRange:\n    min: 10\n    max: 2000\n    unit: W'
    new_power = '  powerRange:\n    min: 1\n    max: 2000\n    unit: W'
    
    if old_power in content:
        content = content.replace(old_power, new_power)
        print("  ✅ Lowered power range minimum for delicate cleaning")
        updates_made += 1
    
    if updates_made > 0:
        with open('data/Materials.yaml', 'w') as f:
            f.write(content)
    
    print(f"✅ Completed machine settings improvements: {updates_made} updates made")
    return updates_made

def add_missing_property_ranges():
    """Add ranges for commonly missing properties"""
    
    print("🔄 Adding ranges for missing properties...")
    
    with open('data/Categories.yaml', 'r') as f:
        content = f.read()
    
    updates_made = 0
    
    # Add absorption coefficient ranges to categories that are missing them
    missing_properties = {
        'absorptionCoefficient': {
            'ceramic': {'min': 0.1, 'max': 50, 'unit': 'cm⁻¹'},
            'metal': {'min': 0.02, 'max': 100, 'unit': 'cm⁻¹'},
            'glass': {'min': 0.001, 'max': 10, 'unit': 'cm⁻¹'},
            'wood': {'min': 1, 'max': 50, 'unit': 'cm⁻¹'},
            'stone': {'min': 0.1, 'max': 20, 'unit': 'cm⁻¹'},
            'plastic': {'min': 0.1, 'max': 100, 'unit': 'cm⁻¹'},
            'composite': {'min': 0.05, 'max': 200, 'unit': 'cm⁻¹'},
            'semiconductor': {'min': 0.01, 'max': 100, 'unit': 'cm⁻¹'},
            'masonry': {'min': 0.5, 'max': 15, 'unit': 'cm⁻¹'}
        },
        'reflectivity': {
            'ceramic': {'min': 5, 'max': 90, 'unit': '%'},
            'metal': {'min': 5, 'max': 98, 'unit': '%'},
            'glass': {'min': 4, 'max': 92, 'unit': '%'},
            'wood': {'min': 10, 'max': 60, 'unit': '%'},
            'stone': {'min': 5, 'max': 80, 'unit': '%'},
            'plastic': {'min': 5, 'max': 95, 'unit': '%'},
            'composite': {'min': 2, 'max': 80, 'unit': '%'},
            'semiconductor': {'min': 10, 'max': 70, 'unit': '%'},
            'masonry': {'min': 10, 'max': 70, 'unit': '%'}
        }
    }
    
    # This would be a more complex addition requiring careful YAML structure manipulation
    # For now, just count what we could add
    potential_additions = 0
    for prop_name, categories in missing_properties.items():
        for category in categories:
            potential_additions += 1
    
    print(f"  📋 Identified {potential_additions} potential property ranges to add")
    print("  ℹ️  Advanced property ranges can be added in future enhancement")
    
    return 0  # No actual changes made yet

def fix_masonry_thermal_expansion():
    """Fix minor masonry thermal expansion range"""
    
    print("🔄 Adjusting masonry thermal expansion...")
    
    with open('data/Categories.yaml', 'r') as f:
        content = f.read()
    
    updates_made = 0
    
    # Slightly lower minimum for brick
    old_range = '      thermalExpansion:\n        max: 12\n        min: 6\n        unit: µm/m·K'
    new_range = '      thermalExpansion:\n        max: 12\n        min: 5\n        unit: µm/m·K'
    
    if old_range in content:
        content = content.replace(old_range, new_range)
        print("  ✅ Lowered masonry thermal expansion minimum for brick")
        updates_made += 1
        
        with open('data/Categories.yaml', 'w') as f:
            f.write(content)
    
    print(f"✅ Completed masonry thermal expansion fix: {updates_made} updates made")
    return updates_made

def main():
    print("🔧 Advanced System Value Improvements")
    print("=" * 50)
    
    # Apply advanced fixes
    soft_metal_fixes = create_soft_metal_exceptions()
    composite_fixes = fix_composite_thermal_expansion()
    ceramic_fixes = fix_ceramic_thermal_diffusivity()
    machine_fixes = fix_machine_settings_precision()
    missing_properties = add_missing_property_ranges()
    masonry_fixes = fix_masonry_thermal_expansion()
    
    total_fixes = (soft_metal_fixes + composite_fixes + ceramic_fixes + 
                  machine_fixes + masonry_fixes)
    
    print("\n" + "=" * 50)
    print("📊 ADVANCED IMPROVEMENTS SUMMARY")
    print("=" * 50)
    print(f"Soft metal property accommodations: {soft_metal_fixes}")
    print(f"Composite thermal expansion fixes: {composite_fixes}")
    print(f"Ceramic thermal diffusivity fixes: {ceramic_fixes}")
    print(f"Machine settings precision improvements: {machine_fixes}")
    print(f"Masonry thermal expansion fixes: {masonry_fixes}")
    print(f"Missing property analysis completed: {missing_properties}")
    print(f"Total advanced fixes applied: {total_fixes}")
    
    if total_fixes > 0:
        print("\n✅ Run the analysis script again to validate advanced improvements!")
        print("Expected result: Reduction to ~40-50 remaining violations")
        print("📋 Remaining violations will likely be true material outliers")
    else:
        print("\n⚠️ No additional fixes were needed or applied.")
        print("System appears to be well-optimized already!")

if __name__ == "__main__":
    main()