#!/usr/bin/env python3
"""
Fix broken compound references in contaminants.yaml

Updates old compound IDs (with -compound suffix) to new IDs (without suffix).
"""

import yaml
from pathlib import Path
import sys

def main():
    # Mapping of old to new compound IDs
    old_to_new = {
        'carbon-dioxide-compound': 'carbon-dioxide',
        'water-vapor-compound': 'water-vapor',
        'carbon-particulates-compound': 'carbon-particulates',
        'vocs-compound': 'vocs',
        'carbon-ash-compound': 'carbon-ash',
        'nitrogen-oxides-compound': 'nitrogen-oxides',
        'aluminum-oxide-compound': 'aluminum-oxide',
        'carbon-monoxide-compound': 'carbon-monoxide',
        'metal-oxides-mixed-compound': 'metal-oxides-mixed',
        'organic-residues-compound': 'organic-residues',
        'pahs-compound': 'pahs',
        'formaldehyde-compound': 'formaldehyde',
        'benzene-compound': 'benzene',
        'toluene-compound': 'toluene',
        'acetaldehyde-compound': 'acetaldehyde',
        'styrene-compound': 'styrene',
        'acrolein-compound': 'acrolein',
        'iron-oxide-compound': 'iron-oxide',
        'chromium-vi-compound': 'chromium-vi',
        'lead-oxide-compound': 'lead-oxide',
        'cadmium-oxide-compound': 'cadmium-oxide',
        'zinc-oxide-compound': 'zinc-oxide',
        'copper-oxide-compound': 'copper-oxide',
        'tin-oxide-compound': 'tin-oxide',
        'metal-vapors-mixed-compound': 'metal-vapors-mixed',
        'nanoparticulates-compound': 'nanoparticulates',
        'silicon-dioxide-compound': 'silicon-dioxide',
        'calcium-oxide-compound': 'calcium-oxide',
        'sulfur-dioxide-compound': 'sulfur-dioxide',
        'hydrogen-chloride-compound': 'hydrogen-chloride',
        'hydrogen-cyanide-compound': 'hydrogen-cyanide',
        'phosgene-compound': 'phosgene',
        'ammonia-compound': 'ammonia',
        'benzoapyrene-compound': 'benzoapyrene',
    }
    
    # Load contaminants
    contaminants_path = Path('data/contaminants/contaminants.yaml')
    print(f"Loading {contaminants_path}...")
    
    with open(contaminants_path) as f:
        data = yaml.safe_load(f)
    
    patterns = data['contamination_patterns']
    
    # Track changes
    updates_count = 0
    updated_patterns = []
    
    # Update compound references
    for pattern_id, pattern_data in patterns.items():
        if 'produces_compounds' in pattern_data:
            compounds = pattern_data['produces_compounds']
            if compounds:  # Skip empty lists
                pattern_updated = False
                for compound in compounds:
                    old_id = compound.get('id')
                    if old_id in old_to_new:
                        new_id = old_to_new[old_id]
                        compound['id'] = new_id
                        updates_count += 1
                        pattern_updated = True
                        print(f"  ✓ {pattern_id}: {old_id} → {new_id}")
                
                if pattern_updated:
                    updated_patterns.append(pattern_id)
    
    if updates_count == 0:
        print("\n✅ No updates needed - all references already correct!")
        return 0
    
    # Save updated data
    print(f"\n📝 Saving changes to {contaminants_path}...")
    with open(contaminants_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n✅ Fixed {updates_count} compound references across {len(updated_patterns)} patterns")
    return 0

if __name__ == '__main__':
    sys.exit(main())
