#!/usr/bin/env python3
"""
Fix Material References in Contaminants.yaml

Updates material references to match exact display names from Materials.yaml
using fuzzy matching. Creates a backup before modifying.
"""

import sys
from pathlib import Path
from difflib import get_close_matches
import shutil
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.utils.yaml_utils import load_yaml, save_yaml

# Manual corrections (when fuzzy match is wrong)
MANUAL_CORRECTIONS = {
    'Carbon Steel': None,  # No match - different from Tool Steel
    'Quartz': None,  # No match - different from Quartzite
    'Steel Pipes': None,  # Too generic
    'Silicon Wafers': None,  # Component, not material
}

# Known exceptions that should NOT be fixed
KNOWN_EXCEPTIONS = {
    'ALL', 'Plastics', 'Metals', 'Woods', 'Stones', 'Ceramics', 'Composites',
    'Painted Metal', 'Thin Sheet Metal', 'Galvanized Metal',
    'Porous Stone', 'Soft Stone', 'Hard Stone',
    'Synthetic Materials', 'Natural Materials',
    'Thin Plastics', 'Soft Materials', 'Porous Surfaces',
    'Soft Substrates', 'Delicate Substrates', 'Flexible Substrates',
    'HSS', 'PCB', 'ABS', 'PVC',
    'Tile', 'Drywall', 'Teflon', 'Cardboard', 'Paper', 'Asphalt', 'Grout',
    'Boilers', 'Machinery', 'Transformer Housings', 'Turbine Blades',
    'Electronics', 'Optical Components',
    'Food Areas', 'Heated Surfaces', 'Unsealed Areas',
    'Plastics (ABS)', 'Porous Wood',
}


def main():
    print("=" * 80)
    print("FIX MATERIAL REFERENCES IN CONTAMINANTS.YAML")
    print("=" * 80)
    
    # Load data
    materials_path = PROJECT_ROOT / 'data' / 'materials' / 'Materials.yaml'
    contaminants_path = PROJECT_ROOT / 'data' / 'contaminants' / 'Contaminants.yaml'
    
    materials_data = load_yaml(materials_path)
    contaminants_data = load_yaml(contaminants_path)
    
    # Get valid material display names
    material_full_slugs = set(materials_data['materials'].keys())
    material_base_slugs = {m.replace('-laser-cleaning', '') for m in material_full_slugs}
    material_display_names = {
        ' '.join(word.capitalize() for word in slug.split('-'))
        for slug in material_base_slugs
    }
    
    print(f"\n📊 Found {len(material_display_names)} valid material display names")
    
    # Find and fix invalid references
    print(f"\n🔍 Analyzing Contaminants.yaml...")
    fixes_needed = {}
    patterns_modified = 0
    
    for pattern_id, pattern in contaminants_data['contamination_patterns'].items():
        if 'valid_materials' not in pattern:
            continue
            
        modified = False
        new_materials = []
        
        for mat in pattern['valid_materials']:
            if mat in material_display_names or mat in KNOWN_EXCEPTIONS:
                # Valid reference, keep as-is
                new_materials.append(mat)
            elif mat in MANUAL_CORRECTIONS:
                # Manual correction specified
                if MANUAL_CORRECTIONS[mat] is None:
                    # Skip this material (remove from list)
                    print(f"   ⚠️  Removing '{mat}' from {pattern_id} (no valid match)")
                    modified = True
                else:
                    new_materials.append(MANUAL_CORRECTIONS[mat])
                    fixes_needed[mat] = MANUAL_CORRECTIONS[mat]
                    modified = True
            else:
                # Try fuzzy matching
                matches = get_close_matches(mat, material_display_names, n=1, cutoff=0.7)
                if matches:
                    fuzzy_match = matches[0]
                    new_materials.append(fuzzy_match)
                    fixes_needed[mat] = fuzzy_match
                    modified = True
                else:
                    # No match, keep original (will be caught by validation)
                    new_materials.append(mat)
        
        if modified:
            pattern['valid_materials'] = new_materials
            patterns_modified += 1
    
    # Summary
    print(f"\n📊 Found {len(fixes_needed)} unique material reference fixes")
    print(f"📝 Modified {patterns_modified} patterns")
    
    if fixes_needed:
        print(f"\n🔧 FIXES APPLIED:")
        for old, new in sorted(fixes_needed.items()):
            if new:
                print(f"   • '{old}' → '{new}'")
            else:
                print(f"   • '{old}' → REMOVED")
    
    if patterns_modified > 0:
        # Create backup
        backup_path = contaminants_path.parent / f"Contaminants_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        shutil.copy2(contaminants_path, backup_path)
        print(f"\n💾 Backup created: {backup_path}")
        
        # Save changes
        save_yaml(contaminants_path, contaminants_data)
        print(f"✅ Updated: {contaminants_path}")
        print(f"\n📊 SUMMARY:")
        print(f"   • {len(fixes_needed)} material references corrected")
        print(f"   • {patterns_modified} patterns modified")
        print(f"   • Backup saved to: {backup_path.name}")
    else:
        print(f"\n✅ No fixes needed - all references are valid!")
    
    print("=" * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
