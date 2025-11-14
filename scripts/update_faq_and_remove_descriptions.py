#!/usr/bin/env python3
"""
Update Materials.yaml to:
1. Change faq.questions[] to faq[] (simplified structure)
2. Remove all 'description' fields throughout
"""

import yaml
from pathlib import Path
from datetime import datetime


def update_faq_structure(material_data):
    """Convert faq.questions[] to faq[]"""
    if 'faq' in material_data and isinstance(material_data['faq'], dict):
        if 'questions' in material_data['faq']:
            # Convert faq.questions[] to faq[]
            material_data['faq'] = material_data['faq']['questions']
            return True
    return False


def remove_description_fields(obj, path=""):
    """
    Recursively remove 'description' fields from nested dicts.
    EXCEPTION: Preserve 'description' in regulatoryStandards items.
    """
    removed_count = 0
    
    if isinstance(obj, dict):
        # Check if we're in regulatoryStandards context
        in_regulatory_standards = 'regulatoryStandards' in path
        
        # Remove description UNLESS we're in regulatoryStandards
        if 'description' in obj and not in_regulatory_standards:
            del obj['description']
            removed_count += 1
        
        # Recurse into nested structures
        for key, value in list(obj.items()):
            removed_count += remove_description_fields(value, f"{path}.{key}")
    
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            removed_count += remove_description_fields(item, f"{path}[{i}]")
    
    return removed_count


def main():
    print("=" * 60)
    print("UPDATE FAQ STRUCTURE & REMOVE DESCRIPTIONS")
    print("=" * 60)
    print()
    
    # Load Materials.yaml
    materials_file = Path('data/materials/Materials.yaml')
    print(f"Loading {materials_file}...")
    
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    print(f"✅ Loaded {len(materials)} materials\n")
    
    # Track changes
    faq_updated = 0
    descriptions_removed = 0
    materials_modified = []
    
    # Update each material
    for mat_name, mat_data in materials.items():
        if not isinstance(mat_data, dict):
            continue
        
        modified = False
        
        # 1. Update FAQ structure
        if update_faq_structure(mat_data):
            faq_updated += 1
            modified = True
        
        # 2. Remove description fields
        removed = remove_description_fields(mat_data)
        if removed > 0:
            descriptions_removed += removed
            modified = True
        
        if modified:
            materials_modified.append(mat_name)
    
    # Print summary
    print("Changes Summary:")
    print("=" * 60)
    print(f"  FAQ structure updated:        {faq_updated:3d} materials")
    print(f"  Description fields removed:   {descriptions_removed:3d} instances")
    print(f"  Total materials modified:     {len(materials_modified):3d}/{len(materials)}")
    print("=" * 60)
    print()
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = Path(f'data/materials/backups/materials_backup_{timestamp}.yaml')
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(materials_file, 'r') as f:
        backup_content = f.read()
    with open(backup_file, 'w') as f:
        f.write(backup_content)
    print(f'✅ Backup created: {backup_file}')
    
    # Save updated data
    with open(materials_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    print(f'✅ Saved: {materials_file}')
    
    print()
    print('✅ Update complete!')
    print(f'   - FAQ structure simplified for {faq_updated} materials')
    print(f'   - Removed {descriptions_removed} description field instances')


if __name__ == '__main__':
    main()
