#!/usr/bin/env python3
"""
Fast EEAT Generator - Direct Materials.yaml modification

Generates EEAT for all materials WITHOUT API calls.
Pure Python - should complete in seconds for all 132 materials.

Usage:
    python3 scripts/batch/generate_eeat_fast.py [--dry-run]
"""

import yaml
import random
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
MATERIALS_FILE = PROJECT_ROOT / "materials" / "data" / "Materials.yaml"


def generate_eeat_data(regulatory_standards: list) -> dict:
    """
    Generate EEAT section from regulatoryStandards.
    
    Pure Python - no API calls needed.
    """
    # Filter to dict entries only
    dict_standards = [
        std for std in regulatory_standards 
        if isinstance(std, dict) and 'description' in std and 'url' in std
    ]
    
    if not dict_standards:
        return None
    
    # Select 1-3 random standards for citations
    num_citations = random.randint(1, min(3, len(dict_standards)))
    citation_standards = random.sample(dict_standards, num_citations)
    
    # Convert to citation strings (just the description)
    citations = [std['description'] for std in citation_standards]
    
    # Select 1 random standard for isBasedOn
    based_on_standard = random.choice(dict_standards)
    is_based_on = {
        'name': based_on_standard['description'],
        'url': based_on_standard['url']
    }
    
    return {
        'reviewedBy': 'Z-Beam Quality Assurance Team',
        'citations': citations,
        'isBasedOn': is_based_on
    }


def main(dry_run: bool = False):
    """Generate EEAT for all materials"""
    print("=" * 70)
    print("FAST EEAT GENERATION (Pure Python - No API)")
    print("=" * 70)
    
    # Load Materials.yaml
    print(f"\n📖 Loading {MATERIALS_FILE.name}...")
    with open(MATERIALS_FILE, 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data['materials']
    print(f"✅ Loaded {len(materials)} materials")
    
    # Check existing EEAT
    with_eeat = [name for name, mat in materials.items() if 'eeat' in mat and mat['eeat']]
    without_eeat = [name for name in materials.keys() if name not in with_eeat]
    
    print(f"\n📊 Status:")
    print(f"   ✅ Already have EEAT: {len(with_eeat)}")
    print(f"   ⏳ Missing EEAT: {len(without_eeat)}")
    
    if not without_eeat:
        print("\n✨ All materials already have EEAT!")
        return True
    
    if dry_run:
        print("\n🔍 DRY-RUN MODE - No changes will be saved")
    
    # Create backup if not dry-run
    if not dry_run:
        backup_path = MATERIALS_FILE.parent / f"Materials.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        print(f"\n📦 Creating backup: {backup_path.name}")
        with open(MATERIALS_FILE, 'r') as f:
            backup_content = f.read()
        with open(backup_path, 'w') as f:
            f.write(backup_content)
    
    # Generate EEAT for each material
    print(f"\n{'🔍' if dry_run else '🚀'} Processing {len(without_eeat)} materials...")
    print()
    
    success = 0
    skipped = 0
    
    for i, material_name in enumerate(without_eeat, 1):
        material_data = materials[material_name]
        
        # Get regulatoryStandards
        reg_standards = material_data.get('regulatoryStandards', [])
        
        # Generate EEAT
        eeat_data = generate_eeat_data(reg_standards)
        
        if eeat_data is None:
            print(f"[{i}/{len(without_eeat)}] ⏭️  {material_name}: No valid regulatoryStandards")
            skipped += 1
            continue
        
        # Add to material data
        if not dry_run:
            material_data['eeat'] = eeat_data
        
        print(f"[{i}/{len(without_eeat)}] ✅ {material_name}: {len(eeat_data['citations'])} citations")
        success += 1
    
    # Save if not dry-run
    if not dry_run and success > 0:
        print(f"\n💾 Saving to {MATERIALS_FILE.name}...")
        with open(MATERIALS_FILE, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print("✅ Saved successfully")
    
    # Summary
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)
    print(f"\n📊 Results:")
    print(f"   ✅ Generated: {success}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   📈 Total with EEAT: {len(with_eeat) + success}/{len(materials)}")
    
    if dry_run:
        print(f"\n🔍 DRY-RUN: No changes saved")
        print(f"   Run without --dry-run to save changes")
    else:
        print(f"\n✅ EEAT generation complete!")
        print(f"\n📋 Next steps:")
        print(f"   1. Verify: Check Materials.yaml for eeat sections")
        print(f"   2. Deploy: python3 run.py --deploy")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fast EEAT generation (no API)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    args = parser.parse_args()
    
    try:
        main(dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
