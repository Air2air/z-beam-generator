#!/usr/bin/env python3
"""
Fix thermalDestruction Structure in Categories.yaml

The thermalDestruction ranges were stored with a flat structure:
  thermalDestruction:
    min: 1000
    max: 1700
    unit: 'K'

But should have a nested structure to match Materials.yaml:
  thermalDestruction:
    point:
      min: 1000
      max: 1700
      unit: 'K'

This script fixes the thermalDestruction ranges in Categories.yaml.
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime

def fix_thermal_destruction_ranges():
    """Fix thermalDestruction ranges in Categories.yaml"""
    
    categories_file = Path("data/Categories.yaml")
    if not categories_file.exists():
        print("❌ Categories.yaml not found")
        return False
    
    # Create backup
    backup_file = categories_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
    
    print(f"📁 Loading {categories_file}")
    with open(categories_file, 'r') as f:
        categories = yaml.safe_load(f)
    
    # Create backup
    print(f"💾 Creating backup: {backup_file}")
    with open(backup_file, 'w') as f:
        yaml.dump(categories, f, default_flow_style=False, sort_keys=False, indent=2)
    
    # Track changes
    fixed_count = 0
    
    # Fix structure for all categories
    for cat_name, cat_data in categories['categories'].items():
        ranges = cat_data.get('category_ranges', {})
        
        if 'thermalDestruction' in ranges:
            thermal = ranges['thermalDestruction']
            
            # Check if it has flat structure (min/max directly under thermalDestruction)
            if isinstance(thermal, dict) and 'min' in thermal and 'point' not in thermal:
                print(f"🔧 Fixing {cat_name}: flat → nested structure")
                
                # Convert flat structure to nested structure
                new_thermal = {
                    'point': {
                        'min': thermal['min'],
                        'max': thermal['max'],
                        'unit': thermal.get('unit', '°C')
                    },
                    'type': thermal.get('type', 'melting')
                }
                
                # Preserve additional metadata if present
                for key in ['research_basis', 'confidence', 'description']:
                    if key in thermal:
                        new_thermal[key] = thermal[key]
                
                # Update the structure
                ranges['thermalDestruction'] = new_thermal
                fixed_count += 1
            
            elif isinstance(thermal, dict) and 'point' in thermal:
                print(f"✅ {cat_name}: already has correct nested structure")
            
            else:
                print(f"⚠️  {cat_name}: unexpected thermalDestruction structure: {type(thermal)}")
    
    if fixed_count > 0:
        # Save updated categories
        print(f"\n💾 Saving updated Categories.yaml with {fixed_count} fixes")
        with open(categories_file, 'w') as f:
            yaml.dump(categories, f, default_flow_style=False, sort_keys=False, indent=2)
        
        print(f"✅ Fixed {fixed_count} thermalDestruction range structures")
        print(f"📁 Backup saved: {backup_file}")
        
        return True
    else:
        print("✅ No fixes needed - all structures are correct")
        backup_file.unlink()  # Remove backup if no changes made
        return True

if __name__ == '__main__':
    success = fix_thermal_destruction_ranges()
    sys.exit(0 if success else 1)