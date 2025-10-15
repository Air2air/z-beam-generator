#!/usr/bin/env python3
"""
Restructure materials.yaml to use nested thermalDestruction structure.

Changes:
1. Combine thermalDestructionPoint and thermalDestructionType into nested thermalDestruction
2. Remove meltingPoint (redundant with thermalDestruction when type=melting)
3. Assign appropriate destruction type based on material category
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime

# Category to destruction type mapping from Categories.yaml
CATEGORY_DESTRUCTION_TYPES = {
    'ceramic': 'thermal_shock',
    'composite': 'decomposition',
    'glass': 'melting',
    'masonry': 'spalling',
    'metal': 'melting',
    'plastic': 'decomposition',
    'semiconductor': 'melting',
    'stone': 'thermal_shock',
    'wood': 'carbonization'
}

def restructure_material(material_name, material_data):
    """Restructure a single material's thermal properties"""
    changes_made = []
    
    if 'properties' not in material_data:
        return changes_made
    
    props = material_data['properties']
    category = material_data.get('category', 'unknown')
    
    # Get the appropriate destruction type for this category
    destruction_type = CATEGORY_DESTRUCTION_TYPES.get(category, 'melting')
    
    # Check if we have the old structure
    has_tdp = 'thermalDestructionPoint' in props
    has_tdt = 'thermalDestructionType' in props
    has_melting = 'meltingPoint' in props
    has_nested = 'thermalDestruction' in props
    
    # Skip if already has nested structure
    if has_nested and isinstance(props['thermalDestruction'], dict):
        if 'point' in props['thermalDestruction']:
            changes_made.append(f"Already has nested thermalDestruction structure")
            # Still remove old properties if they exist
            if has_tdp:
                del props['thermalDestructionPoint']
                changes_made.append("Removed redundant thermalDestructionPoint")
            if has_tdt:
                del props['thermalDestructionType']
                changes_made.append("Removed redundant thermalDestructionType")
            if has_melting:
                del props['meltingPoint']
                changes_made.append("Removed redundant meltingPoint")
            return changes_made
    
    # Build nested thermalDestruction from available data
    thermal_destruction = None
    
    if has_tdp:
        tdp_data = props['thermalDestructionPoint']
        if isinstance(tdp_data, dict):
            thermal_destruction = {
                'point': {
                    'value': tdp_data.get('value'),
                    'unit': tdp_data.get('unit', '°C'),
                    'min': tdp_data.get('min'),
                    'max': tdp_data.get('max'),
                    'confidence': tdp_data.get('confidence'),
                    'research_basis': tdp_data.get('research_basis'),
                    'research_date': tdp_data.get('research_date'),
                    'source': tdp_data.get('source'),
                    'validation_method': tdp_data.get('validation_method'),
                    'ai_verified': tdp_data.get('ai_verified'),
                    'verification_date': tdp_data.get('verification_date'),
                    'verification_variance': tdp_data.get('verification_variance'),
                    'verification_confidence': tdp_data.get('verification_confidence')
                },
                'type': destruction_type
            }
            # Remove None values
            thermal_destruction['point'] = {k: v for k, v in thermal_destruction['point'].items() if v is not None}
            
            changes_made.append(f"Created nested thermalDestruction from thermalDestructionPoint")
            changes_made.append(f"Set destruction type to '{destruction_type}' for category '{category}'")
    
    elif has_melting:
        # Use meltingPoint data if no thermalDestructionPoint exists
        mp_data = props['meltingPoint']
        if isinstance(mp_data, dict):
            thermal_destruction = {
                'point': {
                    'value': mp_data.get('value'),
                    'unit': mp_data.get('unit', '°C'),
                    'min': mp_data.get('min'),
                    'max': mp_data.get('max'),
                    'confidence': mp_data.get('confidence'),
                    'research_basis': mp_data.get('research_basis'),
                    'research_date': mp_data.get('research_date'),
                    'source': mp_data.get('source'),
                    'validation_method': mp_data.get('validation_method'),
                    'ai_verified': mp_data.get('ai_verified'),
                    'verification_date': mp_data.get('verification_date'),
                    'verification_variance': mp_data.get('verification_variance'),
                    'verification_confidence': mp_data.get('verification_confidence')
                },
                'type': destruction_type
            }
            # Remove None values
            thermal_destruction['point'] = {k: v for k, v in thermal_destruction['point'].items() if v is not None}
            
            changes_made.append(f"Created nested thermalDestruction from meltingPoint")
            changes_made.append(f"Set destruction type to '{destruction_type}' for category '{category}'")
    
    # Apply the new nested structure
    if thermal_destruction:
        props['thermalDestruction'] = thermal_destruction
        
        # Remove old properties
        if has_tdp:
            del props['thermalDestructionPoint']
            changes_made.append("Removed old thermalDestructionPoint")
        if has_tdt:
            del props['thermalDestructionType']
            changes_made.append("Removed old thermalDestructionType")
        if has_melting:
            del props['meltingPoint']
            changes_made.append("Removed old meltingPoint")
    
    return changes_made

def main():
    materials_file = Path('data/materials.yaml')
    
    if not materials_file.exists():
        print(f"❌ Error: {materials_file} not found")
        sys.exit(1)
    
    print(f"📖 Loading {materials_file}...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data:
        print("❌ Error: materials.yaml is empty or invalid")
        sys.exit(1)
    
    # Get materials dict (they're nested under 'materials' key)
    if 'materials' not in data:
        print("❌ Error: No 'materials' key found in materials.yaml")
        sys.exit(1)
    
    materials = data['materials']
    
    # Create backup
    backup_file = materials_file.with_suffix(f'.yaml.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    print(f"💾 Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Process each material
    total_materials = 0
    materials_changed = 0
    total_changes = 0
    
    print(f"\n🔄 Processing materials...")
    print("=" * 80)
    
    for material_name, material_data in materials.items():
        if not isinstance(material_data, dict):
            continue
        
        total_materials += 1
        changes = restructure_material(material_name, material_data)
        
        if changes:
            materials_changed += 1
            total_changes += len(changes)
            print(f"\n✅ {material_name}:")
            for change in changes:
                print(f"   • {change}")
    
    print("\n" + "=" * 80)
    print(f"\n📊 Summary:")
    print(f"   Total materials processed: {total_materials}")
    print(f"   Materials changed: {materials_changed}")
    print(f"   Total changes made: {total_changes}")
    
    if materials_changed > 0:
        print(f"\n💾 Writing updated materials.yaml...")
        with open(materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
        print(f"✅ Successfully updated {materials_file}")
        print(f"📁 Backup saved to {backup_file}")
    else:
        print(f"\n✅ No changes needed - all materials already have correct structure")
    
    print(f"\n✨ Done!")

if __name__ == '__main__':
    main()
