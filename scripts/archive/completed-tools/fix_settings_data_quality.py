#!/usr/bin/env python3
"""
Fix data quality issues in Settings.yaml:
1. Add missing 'value' fields (use midpoint of min/max)
2. Fix unrealistic ranges (adjust max to accommodate value)
"""

import yaml
from pathlib import Path

def fix_settings_data():
    """Fix data quality issues in Settings.yaml"""
    
    settings_path = Path('data/settings/Settings.yaml')
    
    with open(settings_path, 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data['settings']
    
    # Track fixes
    missing_values_fixed = []
    unrealistic_ranges_fixed = []
    
    # Fix 1: Add missing 'value' fields
    for name, mat in materials.items():
        if 'machine_settings' not in mat:
            continue
            
        for param_name, param_data in mat['machine_settings'].items():
            # Add missing 'value' field
            if 'value' not in param_data and 'min' in param_data and 'max' in param_data:
                # Use midpoint as value
                midpoint = (param_data['min'] + param_data['max']) / 2
                param_data['value'] = round(midpoint, 2) if midpoint < 100 else int(midpoint)
                missing_values_fixed.append(f"{name}.{param_name}")
            
            # Fix unrealistic ranges
            if all(k in param_data for k in ['min', 'max', 'value']):
                min_val = param_data['min']
                max_val = param_data['max']
                value = param_data['value']
                
                if value > max_val:
                    # Increase max to accommodate value + 20% buffer
                    new_max = value * 1.2
                    param_data['max'] = round(new_max, 2) if new_max < 100 else int(new_max)
                    unrealistic_ranges_fixed.append(f"{name}.{param_name}: max {max_val} → {param_data['max']}")
                
                elif value < min_val:
                    # Decrease min to accommodate value - 20% buffer
                    new_min = value * 0.8
                    param_data['min'] = round(new_min, 2) if new_min < 100 else int(new_min)
                    unrealistic_ranges_fixed.append(f"{name}.{param_name}: min {min_val} → {param_data['min']}")
    
    # Save updated data
    with open(settings_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Fixed {len(missing_values_fixed)} missing value fields:")
    for item in missing_values_fixed:
        print(f"   • {item}")
    
    print(f"\n✅ Fixed {len(unrealistic_ranges_fixed)} unrealistic ranges:")
    for item in unrealistic_ranges_fixed:
        print(f"   • {item}")
    
    print(f"\n💾 Updated Settings.yaml")

if __name__ == '__main__':
    fix_settings_data()
