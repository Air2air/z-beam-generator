#!/usr/bin/env python3
"""
Remove duplicate thermalDestructionPoint from non-wood materials.

Since we've added category-specific thermal fields (sinteringPoint, softeningPoint, etc.),
we need to remove the old generic thermalDestructionPoint from materials that aren't wood.

Wood materials keep thermalDestructionPoint as their category-specific field.
All other categories should only have their category-specific field + meltingPoint.
"""

import yaml
from pathlib import Path

root = Path(__file__).parent.parent
frontmatter_dir = root / 'content' / 'components' / 'frontmatter'

# Categories that should keep thermalDestructionPoint
KEEP_THERMAL_DESTRUCTION = ['wood']

stats = {
    'checked': 0,
    'removed': 0,
    'kept': 0,
    'errors': 0
}

print('=' * 80)
print('REMOVING DUPLICATE thermalDestructionPoint FROM NON-WOOD MATERIALS')
print('=' * 80)

for filepath in sorted(frontmatter_dir.glob('*.yaml')):
    try:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        stats['checked'] += 1
        name = data.get('name', filepath.stem)
        category = data.get('category', '').lower()
        props = data.get('materialProperties', {})
        
        # Check if material has thermalDestructionPoint
        if 'thermalDestructionPoint' not in props:
            continue
        
        # Keep for wood materials
        if category in KEEP_THERMAL_DESTRUCTION:
            stats['kept'] += 1
            continue
        
        # Remove for all other categories
        del props['thermalDestructionPoint']
        
        # Write back
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        print(f'✓ Removed thermalDestructionPoint from {name} ({category})')
        stats['removed'] += 1
        
    except Exception as e:
        print(f'❌ Error processing {filepath.name}: {e}')
        stats['errors'] += 1

print(f'\n' + '=' * 80)
print('SUMMARY')
print('=' * 80)
print(f'Total checked: {stats["checked"]}')
print(f'Removed thermalDestructionPoint: {stats["removed"]}')
print(f'Kept thermalDestructionPoint (wood): {stats["kept"]}')
print(f'Errors: {stats["errors"]}')
print('=' * 80)
