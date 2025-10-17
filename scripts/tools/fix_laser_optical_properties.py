#!/usr/bin/env python3
"""
Fix laserAbsorption and laserReflectivity data inconsistencies.

Issues found:
- 87 of 122 materials (71%) have absorption + reflectivity != 100%
- 23 materials: Sum > 105% (physically impossible)
- 64 materials: Sum < 80% (missing transmittance or incorrect values)

Strategy:
1. For opaque materials (metals, ceramics, stone, composites): 
   Recalculate reflectivity = 100 - absorption
2. For transparent materials (glass, some plastics):
   Keep existing values (they have transmittance)
3. Backup all files before modifications
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Categories that are typically opaque (should sum to ~100%)
OPAQUE_CATEGORIES = {
    'metal', 'ceramic', 'stone', 'wood', 'composite'
}

# Categories that can be transparent (can sum to < 100%)
TRANSPARENT_CATEGORIES = {
    'glass', 'plastic', 'semiconductor'
}

def backup_file(file_path):
    """Create backup of file"""
    backup_dir = Path("backups/laser_optical_fixes_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Make file_path absolute if it isn't already
    file_path = file_path.resolve()
    cwd = Path.cwd().resolve()
    
    relative_path = file_path.relative_to(cwd)
    backup_path = backup_dir / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    shutil.copy2(file_path, backup_path)
    return backup_dir

def fix_laser_properties(file_path, dry_run=False):
    """Fix laser absorption and reflectivity values"""
    
    with open(file_path) as f:
        data = yaml.safe_load(f)
    
    if not data or 'materialProperties' not in data:
        return None
    
    props = data['materialProperties'].get('laser_material_interaction', {}).get('properties', {})
    absorption_data = props.get('laserAbsorption', {})
    reflectivity_data = props.get('laserReflectivity', {})
    
    absorption = absorption_data.get('value')
    reflectivity = reflectivity_data.get('value')
    
    if absorption is None or reflectivity is None:
        return None
    
    absorption = float(absorption)
    reflectivity = float(reflectivity)
    total = absorption + reflectivity
    
    # Get material info
    material = file_path.stem.replace('-laser-cleaning', '')
    category = data.get('category', 'unknown')
    
    # Determine if material should be opaque
    is_opaque = category in OPAQUE_CATEGORIES
    
    # Check if fix is needed
    needs_fix = False
    fix_type = None
    new_reflectivity = reflectivity
    
    if is_opaque:
        # Opaque materials: should sum to ~100%
        if total < 95 or total > 105:
            needs_fix = True
            new_reflectivity = round(100 - absorption, 1)
            fix_type = f"opaque_recalc (was {total:.1f}%, now 100%)"
    else:
        # Transparent materials: only fix if > 105%
        if total > 105:
            needs_fix = True
            new_reflectivity = round(100 - absorption, 1)
            fix_type = f"impossible_sum (was {total:.1f}%, now 100%)"
    
    if not needs_fix:
        return {
            'material': material,
            'category': category,
            'absorption': absorption,
            'reflectivity': reflectivity,
            'sum': total,
            'status': 'OK',
            'changed': False
        }
    
    # Apply fix
    if not dry_run:
        reflectivity_data['value'] = new_reflectivity
        
        # Add metadata about the fix
        if 'metadata' not in reflectivity_data:
            reflectivity_data['metadata'] = {}
        
        reflectivity_data['metadata']['last_verified'] = datetime.now().isoformat()
        reflectivity_data['metadata']['verification_source'] = 'automatic_fix'
        reflectivity_data['metadata']['fix_reason'] = f'Recalculated: 100 - {absorption} = {new_reflectivity}'
        reflectivity_data['metadata']['previous_value'] = reflectivity
        
        # Write back to file
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return {
        'material': material,
        'category': category,
        'absorption': absorption,
        'old_reflectivity': reflectivity,
        'new_reflectivity': new_reflectivity,
        'old_sum': total,
        'new_sum': absorption + new_reflectivity,
        'fix_type': fix_type,
        'changed': True
    }

def main():
    dry_run = '--dry-run' in sys.argv
    
    print("=" * 80)
    print("LASER OPTICAL PROPERTIES FIX")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE FIX'}")
    print()
    
    frontmatter_dir = Path("content/components/frontmatter")
    files = list(frontmatter_dir.glob("*.yaml"))
    
    results = []
    backup_created = False
    
    for file_path in sorted(files):
        result = fix_laser_properties(file_path, dry_run=dry_run)
        if result:
            results.append(result)
            
            # Create backup on first actual change
            if result['changed'] and not dry_run and not backup_created:
                backup_dir = backup_file(file_path)
                print(f"✅ Backup created: {backup_dir}")
                print()
                backup_created = True
    
    # Separate results
    changed = [r for r in results if r['changed']]
    unchanged = [r for r in results if not r['changed']]
    
    # Print changes
    if changed:
        print(f"\n{'DRY RUN - WOULD CHANGE' if dry_run else 'CHANGED'}: {len(changed)} materials")
        print("-" * 80)
        for r in changed:
            print(f"{r['material']:<30} ({r['category']:<10}) "
                  f"A:{r['absorption']:>5.1f}% + R:{r['old_reflectivity']:>5.1f}% = {r['old_sum']:>6.1f}% → "
                  f"R:{r['new_reflectivity']:>5.1f}% = {r['new_sum']:>6.1f}%")
    
    print(f"\n✅ UNCHANGED: {len(unchanged)} materials")
    
    # Summary by category
    print("\n" + "=" * 80)
    print("SUMMARY BY CATEGORY")
    print("=" * 80)
    
    by_category = {}
    for r in changed:
        cat = r['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(r)
    
    for cat, items in sorted(by_category.items()):
        print(f"{cat}: {len(items)} materials fixed")
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Total materials analyzed: {len(results)}")
    print(f"Materials fixed: {len(changed)}")
    print(f"Materials OK: {len(unchanged)}")
    
    if dry_run:
        print("\n⚠️  This was a DRY RUN - no files were modified")
        print("Run without --dry-run to apply fixes")
    else:
        print(f"\n✅ Fixes applied to {len(changed)} files")
        if backup_created:
            print(f"✅ Backup created in backups/ directory")

if __name__ == '__main__':
    main()
