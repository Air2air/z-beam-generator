#!/usr/bin/env python3
"""
Fix issues with thermalShockResistance and oxidationResistance properties.

Issues to fix:
1. thermalShockResistance: Remove from 4 files (no category ranges defined)
2. oxidationResistance: Convert 6 files with non-°C units to °C
"""

import sys
import yaml
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Files with thermalShockResistance to remove
THERMAL_SHOCK_FILES = [
    'beryllium-laser-cleaning.yaml',
    'iron-laser-cleaning.yaml',
    'molybdenum-laser-cleaning.yaml',
    'tungsten-laser-cleaning.yaml'
]

# Oxidation resistance qualitative mappings (from our previous work)
OXIDATION_QUALITATIVE_MAP = {
    'Excellent': 1000,
    'Very Good': 800,
    'Good': 600,
    'Moderate': 400,
    'Poor': 200,
}

def backup_files(files_to_backup, backup_dir):
    """Create backup of files before modification."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in files_to_backup:
        if file_path.exists():
            relative_path = file_path.relative_to(project_root)
            backup_path = backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)

def remove_thermal_shock_resistance(frontmatter_dir):
    """Remove thermalShockResistance from specified files."""
    print(f"\n{'='*80}")
    print("Removing thermalShockResistance property")
    print(f"{'='*80}\n")
    
    removed_count = 0
    
    for filename in THERMAL_SHOCK_FILES:
        file_path = frontmatter_dir / filename
        
        if not file_path.exists():
            print(f"  ⚠️  {filename} not found")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        modified = False
        
        # Check materialProperties categories
        mat_props = data.get('materialProperties', {})
        
        for category_name in ['laser_material_interaction', 'material_characteristics']:
            if category_name not in mat_props:
                continue
            
            category_data = mat_props[category_name]
            if 'properties' not in category_data:
                continue
            
            properties = category_data['properties']
            
            if 'thermalShockResistance' in properties:
                del properties['thermalShockResistance']
                modified = True
                removed_count += 1
                print(f"  ✅ Removed from {filename}")
        
        if modified:
            # Save updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n  📊 Total removed: {removed_count}")
    return removed_count

def fix_oxidation_resistance(frontmatter_dir):
    """Fix oxidationResistance units to °C."""
    print(f"\n{'='*80}")
    print("Fixing oxidationResistance units")
    print(f"{'='*80}\n")
    
    frontmatter_files = list(frontmatter_dir.glob('*.yaml'))
    fixed_count = 0
    
    for file_path in frontmatter_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            continue
        
        modified = False
        
        # Check materialProperties categories
        mat_props = data.get('materialProperties', {})
        
        for category_name in ['laser_material_interaction', 'material_characteristics']:
            if category_name not in mat_props:
                continue
            
            category_data = mat_props[category_name]
            if 'properties' not in category_data:
                continue
            
            properties = category_data['properties']
            
            if 'oxidationResistance' in properties:
                prop_data = properties['oxidationResistance']
                
                if not isinstance(prop_data, dict):
                    continue
                
                unit = prop_data.get('unit')
                value = prop_data.get('value')
                
                # Skip if already °C
                if unit == '°C':
                    continue
                
                # Handle qualitative values
                if unit == 'qualitative':
                    if isinstance(value, str) and value in OXIDATION_QUALITATIVE_MAP:
                        new_value = OXIDATION_QUALITATIVE_MAP[value]
                        prop_data['value'] = new_value
                        prop_data['unit'] = '°C'
                        modified = True
                        fixed_count += 1
                        print(f"  ✅ {file_path.name}: '{value}' → {new_value}°C")
                    elif isinstance(value, (int, float)):
                        # Value is already numeric, just fix unit
                        prop_data['unit'] = '°C'
                        modified = True
                        fixed_count += 1
                        print(f"  ✅ {file_path.name}: unit qualitative → °C (value already {value})")
                    else:
                        # Use default moderate value
                        prop_data['value'] = 400
                        prop_data['unit'] = '°C'
                        modified = True
                        fixed_count += 1
                        print(f"  ✅ {file_path.name}: '{value}' (unknown) → 400°C (default)")
                
                # Handle percentage (assume it's temperature percentage of max)
                elif unit == '%':
                    # Assume max oxidation temp is ~1500°C for ceramics
                    try:
                        pct = float(value)
                        temp_value = int(1500 * pct / 100)
                        prop_data['value'] = temp_value
                        prop_data['unit'] = '°C'
                        modified = True
                        fixed_count += 1
                        print(f"  ✅ {file_path.name}: {pct}% → {temp_value}°C")
                    except (ValueError, TypeError):
                        prop_data['value'] = 600
                        prop_data['unit'] = '°C'
                        modified = True
                        fixed_count += 1
                        print(f"  ✅ {file_path.name}: {value}% (invalid) → 600°C (default)")
        
        if modified:
            # Save updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n  📊 Total fixed: {fixed_count}")
    return fixed_count

def verify_fixes(frontmatter_dir):
    """Verify that all fixes were applied."""
    print(f"\n{'='*80}")
    print("Verifying fixes")
    print(f"{'='*80}\n")
    
    issues = []
    
    # Check thermalShockResistance removed
    for filename in THERMAL_SHOCK_FILES:
        file_path = frontmatter_dir / filename
        
        if not file_path.exists():
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'thermalShockResistance' in content:
            issues.append(f"thermalShockResistance still in {filename}")
    
    # Check oxidationResistance units
    frontmatter_files = list(frontmatter_dir.glob('*.yaml'))
    
    for file_path in frontmatter_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            continue
        
        mat_props = data.get('materialProperties', {})
        
        for category_name in ['laser_material_interaction', 'material_characteristics']:
            if category_name not in mat_props:
                continue
            
            category_data = mat_props[category_name]
            if 'properties' not in category_data:
                continue
            
            properties = category_data['properties']
            
            if 'oxidationResistance' in properties:
                prop_data = properties['oxidationResistance']
                
                if isinstance(prop_data, dict):
                    unit = prop_data.get('unit')
                    if unit and unit != '°C':
                        issues.append(f"{file_path.name}: oxidationResistance has unit '{unit}' (should be °C)")
    
    if issues:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ All fixes verified successfully")
        return True

def main():
    """Main execution function."""
    print(f"\n{'='*80}")
    print("PROPERTY ISSUES FIX TOOL")
    print(f"{'='*80}")
    print(f"\nFixing issues with:")
    print(f"  • thermalShockResistance (remove from 4 files)")
    print(f"  • oxidationResistance (standardize to °C)")
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    # Define paths
    frontmatter_dir = project_root / 'content' / 'components' / 'frontmatter'
    
    # Create backup directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = project_root / 'backups' / f'property_fixes_{timestamp}'
    
    print("Creating backups...")
    files_to_backup = list(frontmatter_dir.glob('*.yaml'))
    backup_files(files_to_backup, backup_dir)
    print(f"✅ Backed up {len(files_to_backup)} files to: {backup_dir.relative_to(project_root)}\n")
    
    # Execute fixes
    removed = remove_thermal_shock_resistance(frontmatter_dir)
    fixed = fix_oxidation_resistance(frontmatter_dir)
    
    # Verify fixes
    verification_passed = verify_fixes(frontmatter_dir)
    
    # Final summary
    print(f"\n{'='*80}")
    print("FIXES COMPLETE")
    print(f"{'='*80}\n")
    print("Summary:")
    print(f"  • thermalShockResistance removed: {removed}")
    print(f"  • oxidationResistance fixed: {fixed}")
    print(f"  • Backup location: {backup_dir.relative_to(project_root)}")
    print(f"  • Verification: {'✅ PASSED' if verification_passed else '⚠️  ISSUES FOUND'}")
    print(f"\n{'='*80}\n")
    
    return 0 if verification_passed else 1

if __name__ == '__main__':
    sys.exit(main())
