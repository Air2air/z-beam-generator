#!/usr/bin/env python3
"""
Remove Orphan Settings Files
=============================

Remove settings files that have no matching material files.

Part of Export Architecture Improvement Plan (Dec 16, 2025)
Priority 1: Fix orphan settings (30 min)

Usage:
    python3 scripts/data/remove_orphan_settings.py
"""

from pathlib import Path
import sys

ORPHAN_SLUGS = [
    'abs', 'carbide', 'carbon-steel', 'chrome-plated-steel',
    'copper-beryllium-alloy', 'galvanized-steel', 'hss', 'paper',
    'pcb', 'pvc', 'quartz', 'silicon-wafers', 'teflon', 'tile',
    'wrought-iron', 'zinc-alloy'
]

def verify_orphans():
    """Verify which orphan files actually exist"""
    materials_dir = Path('frontmatter/materials')
    settings_dir = Path('frontmatter/settings')
    
    # Get material base names
    material_bases = set(
        f.stem.replace('-laser-cleaning', '') 
        for f in materials_dir.glob('*.yaml')
    )
    
    # Get settings base names
    settings_bases = set(
        f.stem.replace('-settings', '') 
        for f in settings_dir.glob('*.yaml')
    )
    
    # Find actual orphans
    actual_orphans = sorted(settings_bases - material_bases)
    
    print(f"📊 Verification:")
    print(f"   Materials: {len(material_bases)} files")
    print(f"   Settings: {len(settings_bases)} files")
    print(f"   Orphans found: {len(actual_orphans)}")
    
    if actual_orphans != sorted(ORPHAN_SLUGS):
        print("\n⚠️  WARNING: Orphan list mismatch!")
        print(f"   Expected: {sorted(ORPHAN_SLUGS)}")
        print(f"   Found: {actual_orphans}")
        return False
    
    return True

def remove_orphan_settings(dry_run=False):
    """
    Remove settings files with no matching material
    
    Args:
        dry_run: If True, only show what would be removed
    """
    print("\n" + "="*80)
    print("🗑️  REMOVING ORPHAN SETTINGS FILES")
    print("="*80)
    
    removed = []
    not_found = []
    
    for slug in ORPHAN_SLUGS:
        settings_file = Path(f"frontmatter/settings/{slug}-settings.yaml")
        
        if settings_file.exists():
            if dry_run:
                print(f"[DRY RUN] Would remove: {settings_file}")
            else:
                settings_file.unlink()
                print(f"✅ Removed: {settings_file}")
            removed.append(slug)
        else:
            print(f"⚠️  Not found: {settings_file}")
            not_found.append(slug)
    
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"✅ Removed: {len(removed)}/{len(ORPHAN_SLUGS)} orphan settings")
    
    if not_found:
        print(f"⚠️  Not found: {len(not_found)} files")
        print(f"   Files: {not_found}")
    
    if not dry_run:
        print(f"\n🔍 Verify:")
        print(f"   ls frontmatter/settings/*.yaml | wc -l  # Should be 153")

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Remove orphan settings files')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be removed without removing')
    parser.add_argument('--skip-verify', action='store_true',
                       help='Skip verification step')
    
    args = parser.parse_args()
    
    # Verify orphans match expectations
    if not args.skip_verify:
        if not verify_orphans():
            print("\n❌ Verification failed. Use --skip-verify to proceed anyway.")
            sys.exit(1)
    
    # Remove orphans
    remove_orphan_settings(dry_run=args.dry_run)
    
    if args.dry_run:
        print("\n💡 Run without --dry-run to actually remove files")
    else:
        print("\n✅ Orphan removal complete!")

if __name__ == '__main__':
    main()
