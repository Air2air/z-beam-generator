#!/usr/bin/env python3
"""
Fix wood material thermal property descriptions.

Updates thermalDestructionPoint descriptions from generic 
"thermalDestructionPoint from Materials.yaml" to proper scientific
"Temperature where pyrolysis (thermal decomposition) begins"
"""

import yaml
from pathlib import Path

CORRECT_DESCRIPTION = "Temperature where pyrolysis (thermal decomposition) begins"

wood_materials = [
    'ash', 'bamboo', 'beech', 'birch', 'cedar', 'cherry', 'fir', 'hickory',
    'mahogany', 'maple', 'mdf', 'oak', 'pine', 'plywood', 'poplar', 
    'redwood', 'rosewood', 'teak', 'walnut', 'willow'
]

root = Path(__file__).parent.parent
frontmatter_dir = root / 'content' / 'components' / 'frontmatter'

updated = 0
already_correct = 0

for material in wood_materials:
    filepath = frontmatter_dir / f'{material}-laser-cleaning.yaml'
    
    if not filepath.exists():
        print(f'⚠️  File not found: {filepath.name}')
        continue
    
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    props = data.get('materialProperties', {})
    thermal = props.get('thermalDestructionPoint')
    
    if not thermal or not isinstance(thermal, dict):
        print(f'⚠️  {material}: No thermalDestructionPoint field')
        continue
    
    current_desc = thermal.get('description', '')
    
    if current_desc == CORRECT_DESCRIPTION:
        already_correct += 1
        continue
    
    # Update description
    thermal['description'] = CORRECT_DESCRIPTION
    
    # Write back
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f'✓ Updated {material}')
    updated += 1

print(f'\n{"=" * 60}')
print(f'Updated: {updated}')
print(f'Already correct: {already_correct}')
print(f'Total processed: {updated + already_correct}')
