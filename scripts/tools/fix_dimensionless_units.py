#!/usr/bin/env python3
"""
Fix Dimensionless Units in Materials.yaml

Problem: Properties like laserAbsorption, laserReflectivity use "unit: dimensionless"
Solution: Replace with empty string "" (standard for dimensionless quantities)

Affected properties:
- laserAbsorption (absorptivity, 0-1 scale)
- laserReflectivity (reflectance, 0-1 scale)
- corrosionResistance (index, 0-1 scale)
- oxidationResistance (index, 0-1 scale)
- absorptivity (coefficient, 0-1 scale)
- reflectivity (coefficient, 0-1 scale)
- porosity (fraction, 0-1 scale)
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime

# Backup file
MATERIALS_FILE = Path("materials/data/Materials.yaml")
BACKUP_FILE = Path(f"materials/data/Materials.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml")

def fix_dimensionless_units():
    """Replace 'dimensionless' with empty string for unit field"""
    
    print("="*80)
    print("FIXING DIMENSIONLESS UNITS")
    print("="*80)
    print()
    
    # Load Materials.yaml
    print(f"📂 Loading {MATERIALS_FILE}...")
    with open(MATERIALS_FILE) as f:
        data = yaml.safe_load(f)
    
    # Create backup
    print(f"💾 Creating backup: {BACKUP_FILE}...")
    with open(BACKUP_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Track changes
    fixed_count = 0
    materials_affected = set()
    properties_affected = set()
    
    # Fix dimensionless units
    print(f"🔧 Fixing dimensionless units...")
    print()
    
    for mat_name, mat_data in data['materials'].items():
        props = mat_data.get('materialProperties', {})
        
        for cat in ['material_characteristics', 'laser_material_interaction']:
            if cat in props:
                for prop_name, prop_data in props[cat].items():
                    if isinstance(prop_data, dict) and 'unit' in prop_data:
                        unit = prop_data['unit']
                        
                        # Check if unit contains "dimensionless"
                        if isinstance(unit, str) and 'dimensionless' in unit.lower():
                            # Replace with empty string
                            prop_data['unit'] = ""
                            fixed_count += 1
                            materials_affected.add(mat_name)
                            properties_affected.add(prop_name)
                            
                            if fixed_count <= 5:  # Show first 5 examples
                                print(f"   ✅ {mat_name}.{prop_name}: '{unit}' → ''")
    
    print()
    print(f"📊 Summary:")
    print(f"   Properties fixed: {fixed_count}")
    print(f"   Materials affected: {len(materials_affected)}")
    print(f"   Unique properties: {len(properties_affected)}")
    print()
    print(f"   Properties affected:")
    for prop in sorted(properties_affected):
        print(f"      - {prop}")
    
    # Save updated data
    print()
    print(f"💾 Saving updated {MATERIALS_FILE}...")
    with open(MATERIALS_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print()
    print("="*80)
    print("✅ DIMENSIONLESS UNITS FIXED")
    print("="*80)
    print()
    print("📋 Next Steps:")
    print("   1. Verify the fix:")
    print(f"      grep -c 'unit: dimensionless' {MATERIALS_FILE}")
    print("      (should return 0)")
    print()
    print("   2. Check empty units are correct:")
    print(f"      grep -A 1 'laserAbsorption:' {MATERIALS_FILE} | grep 'unit:' | head -5")
    print()
    print(f"   3. Rollback if needed:")
    print(f"      cp {BACKUP_FILE} {MATERIALS_FILE}")
    print()
    
    return fixed_count

if __name__ == "__main__":
    try:
        fixed = fix_dimensionless_units()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
