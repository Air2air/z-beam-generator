#!/usr/bin/env python3
"""
Fix Young's Modulus errors.

Issues found:
1. All wood materials have E = 2502.5 GPa (should be ~25 GPa - 100x too high)
2. Many stone/masonry materials have very high E/TS ratios (> 1000)

Strategy:
1. Divide wood E values by 100 (2502.5 → 25.0 GPa)
2. Review and adjust stone/masonry values based on geological data
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
import shutil

def backup_files(files_to_backup):
    """Create backup of files"""
    if not files_to_backup:
        return None
        
    backup_dir = Path("backups/youngs_modulus_fixes_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in files_to_backup:
        file_path = file_path.resolve()
        cwd = Path.cwd().resolve()
        
        relative_path = file_path.relative_to(cwd)
        backup_path = backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(file_path, backup_path)
    
    return backup_dir

def fix_youngs_modulus(file_path, dry_run=False):
    """Fix Young's Modulus if value is unrealistic"""
    
    with open(file_path) as f:
        data = yaml.safe_load(f)
    
    if not data or 'materialProperties' not in data:
        return None
    
    props = data['materialProperties'].get('material_characteristics', {}).get('properties', {})
    youngs_data = props.get('youngsModulus', {})
    
    E = youngs_data.get('value')
    if E is None:
        return None
    
    E_val = float(E)
    material = file_path.stem.replace('-laser-cleaning', '')
    category = data.get('category', 'unknown')
    
    # Determine fix needed
    needs_fix = False
    new_value = E_val
    fix_reason = None
    
    # Wood: divide by 100 if E > 100
    if category.lower() == 'wood' and E_val > 100:
        needs_fix = True
        new_value = round(E_val / 100, 1)
        fix_reason = f'Wood E was 100x too high: {E_val} → {new_value} GPa'
    
    if not needs_fix:
        return {
            'material': material,
            'category': category,
            'old_E': E_val,
            'new_E': E_val,
            'changed': False
        }
    
    # Apply fix
    if not dry_run:
        youngs_data['value'] = new_value
        
        # Add metadata
        if 'metadata' not in youngs_data:
            youngs_data['metadata'] = {}
        
        youngs_data['metadata']['last_verified'] = datetime.now().isoformat()
        youngs_data['metadata']['verification_source'] = 'automatic_fix'
        youngs_data['metadata']['fix_reason'] = fix_reason
        youngs_data['metadata']['previous_value'] = E_val
        
        # Write back
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return {
        'material': material,
        'category': category,
        'old_E': E_val,
        'new_E': new_value,
        'changed': True,
        'fix_reason': fix_reason
    }

def main():
    dry_run = '--dry-run' in sys.argv
    
    print("=" * 80)
    print("YOUNG'S MODULUS FIX")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE FIX'}")
    print()
    
    frontmatter_dir = Path("content/components/frontmatter")
    files = list(frontmatter_dir.glob("*.yaml"))
    
    results = []
    files_to_backup = []
    
    for file_path in sorted(files):
        result = fix_youngs_modulus(file_path, dry_run=dry_run)
        if result:
            results.append(result)
            if result['changed']:
                files_to_backup.append(file_path)
    
    # Create backup
    if files_to_backup and not dry_run:
        backup_dir = backup_files(files_to_backup)
        print(f"✅ Backup created: {backup_dir}")
        print()
    
    # Separate results
    changed = [r for r in results if r['changed']]
    unchanged = [r for r in results if not r['changed']]
    
    # Print changes
    if changed:
        print(f"\n{'DRY RUN - WOULD CHANGE' if dry_run else 'CHANGED'}: {len(changed)} materials")
        print("-" * 80)
        for r in changed:
            print(f"{r['material']:<30} ({r['category']:<10}) "
                  f"{r['old_E']:>8.1f} GPa → {r['new_E']:>6.1f} GPa")
    
    print(f"\n✅ UNCHANGED: {len(unchanged)} materials")
    
    # Summary by category
    if changed:
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
        if files_to_backup:
            print("✅ Backup created in backups/ directory")

if __name__ == '__main__':
    main()
