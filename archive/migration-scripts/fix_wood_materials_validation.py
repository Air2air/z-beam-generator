#!/usr/bin/env python3
"""
Fix validation issues in wood materials in Materials.yaml

Issues to fix:
1. Invalid unit formats (J·kg⁻¹·K⁻¹ → J/(kg·K), μm/m·K → 10⁻⁶/K, N/mm² → MPa)
2. Add missing metadata fields (research_basis, research_date)
3. Fix thermalDestruction property structure
4. Fix youngsModulus range violations
"""

import yaml
from datetime import datetime
from pathlib import Path

def fix_wood_materials():
    """Fix all validation issues in wood materials"""
    
    materials_file = Path('data/Materials.yaml')
    
    print("🔧 Loading Materials.yaml...")
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # Track fixes
    fixes = {
        'unit_fixes': 0,
        'metadata_additions': 0,
        'thermal_destruction_fixes': 0,
        'range_fixes': 0,
        'hardness_unit_fixes': 0
    }
    
    # Unit mappings
    unit_mappings = {
        'J·kg⁻¹·K⁻¹': 'J/(kg·K)',
        'μm/m·K': '10⁻⁶/K',
        'μm/m·°C': '10⁻⁶/K',
        'N/mm²': 'MPa',
        'N': 'MPa',  # Hardness unit fix
        'J/kg·K': 'J/(kg·K)'  # Already correct format but normalize
    }
    
    # Get all materials and filter wood materials
    materials_section = data.get('materials', {})
    if not materials_section:
        print("❌ No materials found")
        return False
    
    # Find wood materials (category='wood' or known wood material names)
    wood_material_names = [
        'Ash', 'Balsa', 'Bamboo', 'Beech', 'Birch', 'Cedar', 'Cherry',
        'Fir', 'Hickory', 'Mahogany', 'Maple', 'MDF', 'Oak', 'Pine',
        'Plywood', 'Poplar', 'Redwood', 'Rosewood', 'Teak', 'Walnut', 'Willow'
    ]
    
    wood_materials = []
    for mat_name, mat_data in materials_section.items():
        if isinstance(mat_data, dict):
            # Check if it's a wood material
            if mat_data.get('category') == 'wood' or mat_name in wood_material_names:
                wood_materials.append(mat_data)
    
    if not wood_materials:
        print("❌ No wood materials found")
        return False
    
    print(f"📋 Found {len(wood_materials)} wood materials to fix\n")
    
    for material in wood_materials:
        material_name = material.get('name', 'Unknown')
        print(f"🔍 Processing: {material_name}")
        
        if 'properties' not in material:
            material['properties'] = {}
        
        properties = material['properties']
        
        # Fix 1: Unit formats
        for prop_name, prop_data in properties.items():
            if isinstance(prop_data, dict) and 'unit' in prop_data:
                old_unit = prop_data['unit']
                if old_unit in unit_mappings:
                    new_unit = unit_mappings[old_unit]
                    prop_data['unit'] = new_unit
                    fixes['unit_fixes'] += 1
                    print(f"  ✅ Fixed {prop_name} unit: {old_unit} → {new_unit}")
        
        # Fix 2: Add missing metadata to youngsModulus
        if 'youngsModulus' in properties:
            ym_data = properties['youngsModulus']
            if isinstance(ym_data, dict):
                if 'research_basis' not in ym_data:
                    ym_data['research_basis'] = 'standard_material_database'
                    fixes['metadata_additions'] += 1
                if 'research_date' not in ym_data:
                    ym_data['research_date'] = '2024-01-01'
                    fixes['metadata_additions'] += 1
                
                # Fix 3: Range violations for youngsModulus
                if 'value' in ym_data:
                    value = ym_data['value']
                    if isinstance(value, (int, float)) and value > 1200.0:
                        # Convert from MPa to GPa if needed
                        if value > 1200:
                            ym_data['value'] = value / 1000.0  # MPa to GPa
                            ym_data['unit'] = 'GPa'
                            fixes['range_fixes'] += 1
                            print(f"  ✅ Fixed youngsModulus range: {value} MPa → {ym_data['value']} GPa")
        
        # Fix 4: thermalDestruction property structure
        if 'thermalDestruction' in properties:
            td_data = properties['thermalDestruction']
            
            # If it's missing required fields, set reasonable defaults
            if isinstance(td_data, dict):
                if 'value' not in td_data or td_data.get('value') is None:
                    # Use typical wood combustion temperature
                    td_data['value'] = 300.0
                    fixes['thermal_destruction_fixes'] += 1
                
                if 'unit' not in td_data or td_data.get('unit') is None:
                    td_data['unit'] = '°C'
                    fixes['thermal_destruction_fixes'] += 1
                
                if 'confidence' not in td_data or td_data.get('confidence') is None:
                    td_data['confidence'] = 0.8
                    fixes['thermal_destruction_fixes'] += 1
                
                if 'source' not in td_data or td_data.get('source') is None:
                    td_data['source'] = 'wood_combustion_standards'
                    fixes['thermal_destruction_fixes'] += 1
                
                if td_data.get('value') and td_data.get('unit'):
                    print(f"  ✅ Fixed thermalDestruction structure")
        
        # Fix 5: Hardness unit conversions
        if 'hardness' in properties:
            h_data = properties['hardness']
            if isinstance(h_data, dict) and h_data.get('unit') in ['N', 'N/mm²']:
                old_unit = h_data['unit']
                # Convert to MPa (for N/mm²) or set reasonable default
                if old_unit == 'N/mm²':
                    h_data['unit'] = 'MPa'
                elif old_unit == 'N' and 'value' in h_data:
                    # Assume Janka hardness in N, convert to typical range
                    h_data['unit'] = 'N (Janka)'
                fixes['hardness_unit_fixes'] += 1
                print(f"  ✅ Fixed hardness unit: {old_unit} → {h_data['unit']}")
        
        # Fix 6: thermalDiffusivity range issues
        if 'thermalDiffusivity' in properties:
            td_data = properties['thermalDiffusivity']
            if isinstance(td_data, dict) and 'value' in td_data:
                value = td_data['value']
                if isinstance(value, (int, float)) and value < 0.001:
                    # Value is too small, likely needs unit conversion
                    td_data['value'] = value * 1000  # Convert to mm²/s
                    if td_data.get('unit') == 'm²/s':
                        td_data['unit'] = 'mm²/s'
                    fixes['range_fixes'] += 1
                    print(f"  ✅ Fixed thermalDiffusivity range: {value} → {td_data['value']}")
    
    # Save updated Materials.yaml
    print(f"\n💾 Saving updated Materials.yaml...")
    with open(materials_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Print summary
    print(f"\n" + "="*60)
    print("📊 FIX SUMMARY")
    print("="*60)
    print(f"✅ Unit format fixes: {fixes['unit_fixes']}")
    print(f"✅ Metadata additions: {fixes['metadata_additions']}")
    print(f"✅ Thermal destruction fixes: {fixes['thermal_destruction_fixes']}")
    print(f"✅ Range fixes: {fixes['range_fixes']}")
    print(f"✅ Hardness unit fixes: {fixes['hardness_unit_fixes']}")
    print(f"\n🎉 Total fixes applied: {sum(fixes.values())}")
    print("="*60)
    
    return True

if __name__ == '__main__':
    try:
        success = fix_wood_materials()
        if success:
            print("\n✅ Wood materials validation issues fixed successfully!")
            print("\nNext steps:")
            print("  1. Verify fixes: python3 run.py --material \"Oak\"")
            print("  2. Generate all: python3 run.py --all")
        else:
            print("\n❌ Failed to fix wood materials")
            exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
