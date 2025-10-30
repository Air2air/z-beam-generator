#!/usr/bin/env python3
"""
Fix Confidence Values in Materials.yaml

Converts confidence values from percentage format (0-100) to decimal format (0-1).
This script identifies properties with confidence values > 1 and converts them to proper decimal format.

Usage:
    python3 scripts/tools/fix_confidence_values.py [--dry-run] [--backup]

Options:
    --dry-run    Show what would be changed without making changes
    --backup     Create a backup before making changes (default: True)
"""

import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime
import shutil


def fix_confidence_values(materials_file: Path, dry_run: bool = False, create_backup: bool = True):
    """
    Fix confidence values in Materials.yaml by converting percentages to decimals.
    
    Args:
        materials_file: Path to Materials.yaml
        dry_run: If True, only report changes without applying them
        create_backup: If True, create backup before modifying file
        
    Returns:
        Tuple of (total_fixed, materials_affected)
    """
    print("🔧 Confidence Value Fixer")
    print("=" * 80)
    print(f"File: {materials_file}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 80)
    print()
    
    # Load Materials.yaml
    print("📂 Loading Materials.yaml...")
    with open(materials_file, 'r') as f:
        materials_data = yaml.safe_load(f)
    
    materials_section = materials_data.get('materials', {})
    
    # Track fixes
    total_fixed = 0
    materials_affected = set()
    fixes_by_material = {}
    
    # Scan for confidence values > 1
    print("🔍 Scanning for confidence values > 1.0...")
    print()
    
    for material_name, material_data in materials_section.items():
        if not isinstance(material_data, dict):
            continue
        
        properties = material_data.get('properties', {})
        material_fixes = []
        
        for prop_name, prop_data in properties.items():
            if isinstance(prop_data, dict):
                confidence = prop_data.get('confidence')
                
                # Check if confidence needs fixing (> 1.0)
                if confidence is not None and confidence > 1.0:
                    old_value = confidence
                    new_value = confidence / 100.0
                    
                    material_fixes.append({
                        'property': prop_name,
                        'old_confidence': old_value,
                        'new_confidence': new_value
                    })
                    
                    total_fixed += 1
                    materials_affected.add(material_name)
        
        if material_fixes:
            fixes_by_material[material_name] = material_fixes
    
    # Report findings
    if total_fixed == 0:
        print("✅ No confidence values need fixing!")
        print("   All confidence values are already in decimal format (0-1)")
        return 0, 0
    
    print(f"📊 Found {total_fixed} confidence values to fix across {len(materials_affected)} materials")
    print()
    
    # Show detailed fixes
    print("🔧 Confidence Values to Fix:")
    print("-" * 80)
    
    for material_name in sorted(fixes_by_material.keys()):
        fixes = fixes_by_material[material_name]
        print(f"\n{material_name} ({len(fixes)} properties):")
        for fix in fixes:
            print(f"  • {fix['property']}: {fix['old_confidence']:.1f} → {fix['new_confidence']:.2f}")
    
    print()
    print("-" * 80)
    
    if dry_run:
        print()
        print("🏁 DRY RUN COMPLETE")
        print(f"   Would fix {total_fixed} confidence values")
        print(f"   Run without --dry-run to apply changes")
        return total_fixed, len(materials_affected)
    
    # Apply fixes
    print()
    print("💾 Applying fixes to Materials.yaml...")
    
    # Create backup if requested
    if create_backup:
        backup_file = materials_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')
        shutil.copy2(materials_file, backup_file)
        print(f"   ✅ Backup created: {backup_file.name}")
    
    # Apply confidence fixes
    for material_name, fixes in fixes_by_material.items():
        properties = materials_section[material_name]['properties']
        
        for fix in fixes:
            prop_name = fix['property']
            if prop_name in properties and isinstance(properties[prop_name], dict):
                properties[prop_name]['confidence'] = fix['new_confidence']
    
    # Save updated file
    with open(materials_file, 'w') as f:
        yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"   ✅ Fixed {total_fixed} confidence values")
    print(f"   ✅ Updated {len(materials_affected)} materials")
    print()
    
    print("🎉 CONFIDENCE VALUES FIXED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Verify changes: grep -A2 'confidence:' data/Materials.yaml | head -20")
    print("  2. Test generation: python3 run.py --material \"Aluminum\"")
    print("  3. Run validation: python3 run.py --validate")
    print()
    
    return total_fixed, len(materials_affected)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Fix confidence values in Materials.yaml (percentage → decimal)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would change
  python3 scripts/tools/fix_confidence_values.py --dry-run
  
  # Apply fixes with backup (default)
  python3 scripts/tools/fix_confidence_values.py
  
  # Apply fixes without backup
  python3 scripts/tools/fix_confidence_values.py --no-backup
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    
    parser.add_argument(
        '--no-backup',
        dest='backup',
        action='store_false',
        default=True,
        help='Do not create backup before making changes'
    )
    
    parser.add_argument(
        '--materials-file',
        type=Path,
        default=Path('data/Materials.yaml'),
        help='Path to Materials.yaml (default: data/Materials.yaml)'
    )
    
    args = parser.parse_args()
    
    # Validate materials file exists
    if not args.materials_file.exists():
        print(f"❌ Error: Materials.yaml not found at {args.materials_file}")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Expected path: {args.materials_file.absolute()}")
        sys.exit(1)
    
    try:
        # Run the fixer
        total_fixed, materials_affected = fix_confidence_values(
            args.materials_file,
            dry_run=args.dry_run,
            create_backup=args.backup
        )
        
        # Exit with appropriate code
        if args.dry_run and total_fixed > 0:
            sys.exit(2)  # Changes needed
        elif total_fixed == 0:
            sys.exit(0)  # No changes needed
        else:
            sys.exit(0)  # Changes applied successfully
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
