#!/usr/bin/env python3
"""
Add _section metadata to components.micro for all materials.

MANDATORY FIELDS (Jan 15, 2026):
- ALL sections MUST have _section with sectionTitle and sectionDescription
- This includes components.micro (before/after microscopic analysis)

This script:
1. Finds all materials with components.micro (before/after text)
2. Wraps them in proper _section structure with required metadata
3. Preserves existing before/after content
"""

import yaml
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def add_micro_section_metadata():
    """Add _section metadata to components.micro for all materials"""
    
    materials_file = project_root / 'data' / 'materials' / 'Materials.yaml'
    
    # Load Materials.yaml
    print(f"Loading {materials_file}...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    print(f"Found {len(materials)} materials\n")
    
    updated_count = 0
    skipped_count = 0
    already_has_section = 0
    
    for material_key, material_data in materials.items():
        # Check if components.micro exists
        if 'components' not in material_data:
            continue
            
        components = material_data['components']
        if 'micro' not in components:
            continue
        
        micro = components['micro']
        
        # Skip if already has _section with required fields
        if isinstance(micro, dict) and '_section' in micro:
            section = micro['_section']
            if 'sectionTitle' in section and 'sectionDescription' in section:
                already_has_section += 1
                continue
        
        # Get material name for metadata
        material_name = material_data.get('name', material_key.replace('-laser-cleaning', '').title())
        
        # Handle different micro formats
        if isinstance(micro, str):
            # Simple string - convert to structured format
            print(f"  ⚠️  {material_key}: micro is a simple string, skipping (needs manual review)")
            skipped_count += 1
            continue
        elif isinstance(micro, dict):
            # Dictionary format
            if 'before' in micro or 'after' in micro:
                # Has before/after but no _section - add it
                if '_section' not in micro:
                    micro['_section'] = {}
                
                section = micro['_section']
                section['sectionTitle'] = 'Microscopic Analysis'
                section['sectionDescription'] = f'High-magnification comparison of {material_name} surface before and after laser cleaning treatment'
                section['icon'] = 'microscope'
                section['order'] = 5
                section['variant'] = 'default'
                
                print(f"  ✅ Updated {material_key}")
                updated_count += 1
            else:
                print(f"  ⚠️  {material_key}: micro dict has unexpected structure, skipping")
                skipped_count += 1
        else:
            print(f"  ⚠️  {material_key}: micro is unexpected type {type(micro)}, skipping")
            skipped_count += 1
    
    # Summary
    print(f"\n{'='*80}")
    print(f"Summary:")
    print(f"  Already had complete _section: {already_has_section}")
    print(f"  Updated with _section: {updated_count}")
    print(f"  Skipped (needs review): {skipped_count}")
    print(f"{'='*80}\n")
    
    # Save updated data
    if updated_count > 0:
        print(f"Saving {updated_count} updates to {materials_file}...")
        with open(materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
        
        print(f"✅ Successfully updated {updated_count} materials")
    else:
        print(f"✅ No updates needed - {already_has_section} materials already have complete metadata")
    
    return updated_count

if __name__ == '__main__':
    try:
        updated = add_micro_section_metadata()
        sys.exit(0 if updated >= 0 else 1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
