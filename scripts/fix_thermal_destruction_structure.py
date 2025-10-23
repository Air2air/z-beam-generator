#!/usr/bin/env python3
"""
Fix thermalDestruction Structure in Materials.yaml

The thermalDestruction properties were populated with a flat structure:
  thermalDestruction:
    value: 423.0
    unit: '°C'
    confidence: 92

But Categories.yaml expects a nested structure:
  thermalDestruction:
    point:
      value: 423.0
      unit: '°C'
      confidence: 92

This script fixes all thermalDestruction properties to use the correct nested structure.
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime

def fix_thermal_destruction_structure():
    """Fix thermalDestruction structure in Materials.yaml"""
    
    materials_file = Path("data/Materials.yaml")
    if not materials_file.exists():
        print("❌ Materials.yaml not found")
        return False
    
    # Create backup
    backup_file = materials_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
    
    print(f"📁 Loading {materials_file}")
    with open(materials_file, 'r') as f:
        materials = yaml.safe_load(f)
    
    # Create backup
    print(f"💾 Creating backup: {backup_file}")
    with open(backup_file, 'w') as f:
        yaml.dump(materials, f, default_flow_style=False, sort_keys=False, indent=2)
    
    # Track changes
    fixed_count = 0
    materials_with_thermal = []
    
    # Fix structure for all materials
    for mat_name, mat_data in materials['materials'].items():
        properties = mat_data.get('properties', {})
        
        if 'thermalDestruction' in properties:
            thermal = properties['thermalDestruction']
            
            # Check if it has flat structure (value directly under thermalDestruction)
            if isinstance(thermal, dict) and 'value' in thermal and 'point' not in thermal:
                print(f"🔧 Fixing {mat_name}: flat → nested structure")
                
                # Convert flat structure to nested structure
                new_thermal = {
                    'point': {
                        'value': thermal['value'],
                        'unit': thermal.get('unit', '°C'),
                        'confidence': thermal.get('confidence', 85)
                    }
                }
                
                # Preserve additional metadata if present
                for key in ['source', 'research_date', 'description']:
                    if key in thermal:
                        new_thermal['point'][key] = thermal[key]
                
                # Update the structure
                properties['thermalDestruction'] = new_thermal
                materials_with_thermal.append(mat_name)
                fixed_count += 1
            
            elif isinstance(thermal, dict) and 'point' in thermal:
                print(f"✅ {mat_name}: already has correct nested structure")
                materials_with_thermal.append(mat_name)
            
            else:
                print(f"⚠️  {mat_name}: unexpected thermalDestruction structure: {type(thermal)}")
    
    if fixed_count > 0:
        # Save updated materials
        print(f"\n💾 Saving updated Materials.yaml with {fixed_count} fixes")
        with open(materials_file, 'w') as f:
            yaml.dump(materials, f, default_flow_style=False, sort_keys=False, indent=2)
        
        print(f"✅ Fixed {fixed_count} thermalDestruction structures")
        print(f"📊 Total materials with thermalDestruction: {len(materials_with_thermal)}")
        print(f"📁 Backup saved: {backup_file}")
        
        return True
    else:
        print("✅ No fixes needed - all structures are correct")
        backup_file.unlink()  # Remove backup if no changes made
        return True

if __name__ == '__main__':
    success = fix_thermal_destruction_structure()
    sys.exit(0 if success else 1)