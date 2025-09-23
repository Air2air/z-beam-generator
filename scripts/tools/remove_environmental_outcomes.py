#!/usr/bin/env python3
"""
Remove Environmental Impact and Outcomes Fields
Removes environmental_impact and outcomes fields from all materials in materials.yaml
"""

import yaml
from pathlib import Path
from datetime import datetime


def remove_environmental_and_outcomes_fields():
    """Remove environmental_impact and outcomes fields from all materials."""
    
    print("🗑️  REMOVING ENVIRONMENTAL IMPACT AND OUTCOMES FIELDS")
    print("=" * 60)
    print("Cleaning up generic environmental impact and outcomes data...")
    print()
    
    # Load current data
    materials_file = Path('data/materials.yaml')
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f'backups/remove_fields_{timestamp}')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    backup_file = backup_dir / 'materials.yaml'
    with open(backup_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Backup created: {backup_file}")
    
    materials_processed = 0
    fields_removed = 0
    
    # Process each material
    for category_name, category_data in data['materials'].items():
        items = category_data.get('items', [])
        
        print(f"\n📁 Processing {category_name} category ({len(items)} materials)...")
        
        for material in items:
            material_name = material.get('name', 'Unknown')
            
            # Remove environmental_impact field if it exists
            if 'environmental_impact' in material:
                del material['environmental_impact']
                fields_removed += 1
                print(f"   ❌ Removed environmental_impact from {material_name}")
            
            # Remove outcomes field if it exists
            if 'outcomes' in material:
                del material['outcomes']
                fields_removed += 1
                print(f"   ❌ Removed outcomes from {material_name}")
            
            materials_processed += 1
    
    # Save updated materials.yaml
    with open(materials_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"\n✅ Processed {materials_processed} materials")
    print(f"🗑️  Removed {fields_removed} fields total")
    print("📁 Updated materials.yaml")
    
    return True


if __name__ == "__main__":
    print("🗑️  ENVIRONMENTAL IMPACT & OUTCOMES FIELD REMOVAL")
    print("=" * 70)
    print("Removing generic environmental_impact and outcomes fields from all materials")
    print()
    
    success = remove_environmental_and_outcomes_fields()
    
    if success:
        print("\n🎉 FIELD REMOVAL COMPLETED!")
        print("=" * 50)
        print("✅ All environmental_impact fields removed")
        print("✅ All outcomes fields removed")
        print("✅ Materials.yaml structure cleaned up")
        print("\n🔍 Run tests to verify structure is still valid")
    else:
        print("\n❌ Field removal encountered errors")
        print("Check the logs for details")
