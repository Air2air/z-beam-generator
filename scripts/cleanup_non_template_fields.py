#!/usr/bin/env python3
"""
Remove fields from Materials.yaml that are not in frontmatter_template.yaml

FIELDS TO REMOVE:
- voice_enhanced
- industryTags
- ranges
- material_metadata
- subtitle_metadata
- environmentalImpact
- outcomeMetrics
- materialCharacteristics
- applications (removed from template by user)

These fields are not part of the canonical template and should not be
included in material data or frontmatter exports.
"""

import yaml
from pathlib import Path
from datetime import datetime

# Fields to remove (not in template)
FIELDS_TO_REMOVE = [
    'voice_enhanced',
    'industryTags',
    'ranges',
    'material_metadata',
    'subtitle_metadata',
    'environmentalImpact',
    'outcomeMetrics',
    'materialCharacteristics',
    'applications',  # Removed from template
]

# Template fields (canonical reference)
TEMPLATE_FIELDS = [
    'name',
    'category',
    'subcategory',
    'title',
    'subtitle',
    'description',
    'author',
    'images',
    'caption',
    'regulatoryStandards',
    'materialProperties',
    'machineSettings',
    'faq',  # Added to template
]


def load_materials():
    """Load Materials.yaml"""
    materials_file = Path('materials/data/Materials.yaml')
    with open(materials_file, 'r') as f:
        return yaml.safe_load(f)


def clean_material(mat_data):
    """Remove non-template fields from a material"""
    removed_fields = []
    for field in FIELDS_TO_REMOVE:
        if field in mat_data:
            del mat_data[field]
            removed_fields.append(field)
    return removed_fields


def save_materials(data, backup=True):
    """Save Materials.yaml with optional backup"""
    materials_file = Path('materials/data/Materials.yaml')
    
    if backup:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = Path(f'materials/data/backups/materials_backup_{timestamp}.yaml')
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy current file to backup
        with open(materials_file, 'r') as f:
            backup_content = f.read()
        with open(backup_file, 'w') as f:
            f.write(backup_content)
        print(f'✅ Backup created: {backup_file}')
    
    # Save cleaned data
    with open(materials_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(f'✅ Saved: {materials_file}')


def main():
    print('Loading Materials.yaml...')
    data = load_materials()
    materials = data.get('materials', {})
    
    print(f'Total materials: {len(materials)}\n')
    
    # Track removals
    removal_stats = {field: 0 for field in FIELDS_TO_REMOVE}
    materials_modified = []
    
    # Clean each material
    for mat_name, mat_data in materials.items():
        removed = clean_material(mat_data)
        if removed:
            materials_modified.append(mat_name)
            for field in removed:
                removal_stats[field] += 1
    
    # Print summary
    print('Removal Summary:')
    print('=' * 60)
    for field, count in removal_stats.items():
        if count > 0:
            print(f'  {field:30s}: {count:3d} materials')
    print('=' * 60)
    print(f'\nTotal materials modified: {len(materials_modified)}/{len(materials)}')
    print(f'Materials unchanged: {len(materials) - len(materials_modified)}/{len(materials)}')
    
    # Show materials that would remain unchanged
    if len(materials_modified) < len(materials):
        unchanged = [m for m in materials.keys() if m not in materials_modified]
        print(f'\nMaterials already clean: {len(unchanged)}')
        if len(unchanged) <= 10:
            for m in unchanged:
                print(f'  - {m}')
    
    # Save changes
    print('\nSaving cleaned Materials.yaml...')
    save_materials(data, backup=True)
    
    print('\n✅ Cleanup complete!')
    print(f'   Removed {sum(removal_stats.values())} field instances across {len(materials_modified)} materials')


if __name__ == '__main__':
    main()
