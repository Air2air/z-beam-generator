#!/usr/bin/env python3
"""
Advanced image naming normalization with conflict resolution.
Handles conflicts between category-prefixed images and base material names.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

def get_frontmatter_materials():
    """Get list of materials that have frontmatter files."""
    frontmatter_dir = Path('content/components/frontmatter')
    if not frontmatter_dir.exists():
        return set()
    
    materials = set()
    for md_file in frontmatter_dir.glob('*.md'):
        material_name = md_file.stem.replace('-laser-cleaning', '')
        materials.add(material_name)
    
    return materials

def analyze_conflicts(images_dir):
    """Analyze all potential naming conflicts."""
    images_path = Path(images_dir)
    frontmatter_materials = get_frontmatter_materials()
    
    # Define conflict resolution strategies
    conflict_strategies = {
        # STRATEGY 1: Preserve More Specific Material
        # Keep the more specific variant, rename generic to avoid conflict
        'carbon-steel': {
            'action': 'rename_generic',
            'generic': 'steel',
            'specific': 'carbon-steel',
            'new_generic_name': 'plain-steel',
            'reason': 'Carbon steel is more specific than generic steel'
        },
        
        'cast-iron': {
            'action': 'rename_generic', 
            'generic': 'iron',
            'specific': 'cast-iron',
            'new_generic_name': 'wrought-iron',
            'reason': 'Cast iron is more specific than generic iron'
        },
        
        'stainless-steel': {
            'action': 'keep_both',
            'reason': 'Both stainless steel and steel are distinct materials in frontmatter'
        },
        
        # STRATEGY 2: Merge Into Base Material
        # Use the category-prefixed image as the base material image
        'galvanized-steel': {
            'action': 'use_as_base',
            'target': 'steel',
            'reason': 'Galvanized steel can represent general steel cleaning'
        },
        
        'tool-steel': {
            'action': 'use_as_base',
            'target': 'steel', 
            'reason': 'Tool steel can represent general steel cleaning'
        },
        
        # STRATEGY 3: Keep Original Names
        # Maintain category prefix for specialized materials
        'concrete-block': {
            'action': 'keep_prefixed',
            'reason': 'Concrete block is distinct from regular concrete'
        },
        
        'cobalt-chromium': {
            'action': 'keep_prefixed',
            'reason': 'Cobalt-chromium is a specific alloy, distinct from pure cobalt'
        }
    }
    
    return conflict_strategies

def create_resolution_plan(images_dir):
    """Create a comprehensive resolution plan for all conflicts."""
    images_path = Path(images_dir)
    frontmatter_materials = get_frontmatter_materials()
    conflict_strategies = analyze_conflicts(images_dir)
    
    resolution_plan = {
        'renames': [],           # (old_name, new_name, reason)
        'conflicts': [],         # Unresolved conflicts
        'keep_as_is': [],       # Files that don't need changes
        'backup_needed': []      # Files that will be overwritten
    }
    
    # Get all hero/micro images
    all_images = list(images_path.glob("*-hero.jpg")) + list(images_path.glob("*-micro.jpg"))
    
    for img_file in all_images:
        filename = img_file.name
        
        # Extract material name and image type
        if '-laser-cleaning-hero.jpg' in filename:
            material = filename.replace('-laser-cleaning-hero.jpg', '')
            image_type = 'hero'
        elif '-laser-cleaning-micro.jpg' in filename:
            material = filename.replace('-laser-cleaning-micro.jpg', '')
            image_type = 'micro'
        elif '-hero.jpg' in filename:
            material = filename.replace('-hero.jpg', '')
            image_type = 'hero'
        elif '-micro.jpg' in filename:
            material = filename.replace('-micro.jpg', '')
            image_type = 'micro'
        else:
            continue
        
        # Check if this material has a conflict strategy
        if material in conflict_strategies:
            strategy = conflict_strategies[material]
            
            if strategy['action'] == 'rename_generic':
                # This is the specific material, keep as base
                new_name = f"{strategy['generic']}-laser-cleaning-{image_type}.jpg"
                
                # Check if target exists
                target_path = images_path / new_name
                if target_path.exists():
                    resolution_plan['backup_needed'].append((target_path.name, f"backup-{target_path.name}"))
                
                resolution_plan['renames'].append((filename, new_name, f"Use {material} as {strategy['generic']}"))
                
            elif strategy['action'] == 'use_as_base':
                # Use this categorized material as the base material
                target_material = strategy['target']
                new_name = f"{target_material}-laser-cleaning-{image_type}.jpg"
                
                target_path = images_path / new_name
                if target_path.exists():
                    resolution_plan['backup_needed'].append((target_path.name, f"backup-{target_path.name}"))
                
                resolution_plan['renames'].append((filename, new_name, strategy['reason']))
                
            elif strategy['action'] == 'keep_prefixed':
                # Keep the current name (no change needed)
                resolution_plan['keep_as_is'].append((filename, strategy['reason']))
                
            elif strategy['action'] == 'keep_both':
                # Both materials exist in frontmatter, no conflict
                resolution_plan['keep_as_is'].append((filename, strategy['reason']))
        
        else:
            # Check if this needs standard normalization (remove wood- prefix etc.)
            normalized_material = normalize_material_name(material)
            if normalized_material != material:
                new_name = f"{normalized_material}-laser-cleaning-{image_type}.jpg"
                
                target_path = images_path / new_name
                if target_path.exists():
                    resolution_plan['conflicts'].append((filename, new_name, "Target already exists"))
                else:
                    resolution_plan['renames'].append((filename, new_name, "Remove category prefix"))
            else:
                # Already normalized
                resolution_plan['keep_as_is'].append((filename, "Already normalized"))
    
    return resolution_plan

def normalize_material_name(material):
    """Normalize material name by removing category prefixes."""
    prefixes_to_remove = [
        'wood-', 'ceramic-', 'glass-', 'metal-', 'composite-',
        'polymer-', 'fiber-', 'resin-', 'reinforced-'
    ]
    
    # Special mappings
    special_mappings = {
        'wood-walnut': 'walnut',
        'wood-ash': 'ash',
        'wood-beech': 'beech',
        'wood-birch': 'birch', 
        'wood-cedar': 'cedar',
        'wood-cherry': 'cherry',
        'wood-hickory': 'hickory',
        'wood-mahogany': 'mahogany',
        'wood-maple': 'maple',
        'wood-oak': 'oak',
        'wood-pine': 'pine',
        'wood-poplar': 'poplar',
        'wood-rosewood': 'rosewood',
        'wood-spruce': 'spruce',
        'wood-teak': 'teak',
        'terra-cotta': 'terracotta',
        'indium-glass': 'indium'
    }
    
    if material in special_mappings:
        return special_mappings[material]
    
    # Remove standard prefixes
    for prefix in prefixes_to_remove:
        if material.startswith(prefix):
            return material[len(prefix):]
    
    return material

def preview_resolution_plan(images_dir):
    """Preview the complete resolution plan."""
    print("🎯 COMPREHENSIVE IMAGE NAMING RESOLUTION PLAN")
    print("="*60)
    
    plan = create_resolution_plan(images_dir)
    
    if plan['backup_needed']:
        print(f"\n⚠️  BACKUPS NEEDED ({len(plan['backup_needed'])}):")
        for original, backup in plan['backup_needed']:
            print(f"   {original} → {backup}")
    
    if plan['renames']:
        print(f"\n✅ PLANNED RENAMES ({len(plan['renames'])}):")
        for old_name, new_name, reason in plan['renames']:
            print(f"   {old_name}")
            print(f"   → {new_name}")
            print(f"   📝 {reason}")
            print()
    
    if plan['conflicts']:
        print(f"\n❌ UNRESOLVED CONFLICTS ({len(plan['conflicts'])}):")
        for old_name, new_name, reason in plan['conflicts']:
            print(f"   {old_name} → {new_name}")
            print(f"   ⚠️  {reason}")
    
    if plan['keep_as_is']:
        print(f"\n✅ NO CHANGES NEEDED ({len(plan['keep_as_is'])}):")
        for filename, reason in plan['keep_as_is'][:10]:  # Show first 10
            print(f"   {filename} - {reason}")
        if len(plan['keep_as_is']) > 10:
            print(f"   ... and {len(plan['keep_as_is']) - 10} more")
    
    print(f"\n📊 RESOLUTION SUMMARY:")
    print(f"   Backups needed: {len(plan['backup_needed'])}")
    print(f"   Files to rename: {len(plan['renames'])}")
    print(f"   Unresolved conflicts: {len(plan['conflicts'])}")
    print(f"   No changes needed: {len(plan['keep_as_is'])}")
    
    return plan

def apply_resolution_plan(images_dir, plan, dry_run=True):
    """Apply the resolution plan."""
    images_path = Path(images_dir)
    
    if dry_run:
        print("\n🧪 DRY RUN - No files will be modified")
    else:
        print("\n🔧 APPLYING RESOLUTION PLAN")
        
        # Create backup directory
        backup_dir = images_path / f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)
        print(f"📁 Created backup directory: {backup_dir}")
    
    print("="*50)
    
    success_count = 0
    error_count = 0
    
    # First, backup files that will be overwritten
    for original, backup in plan['backup_needed']:
        original_path = images_path / original
        if dry_run:
            print(f"Would backup: {original} → backup/{backup}")
        else:
            try:
                backup_path = backup_dir / backup
                shutil.copy2(original_path, backup_path)
                print(f"📦 Backed up: {original}")
            except Exception as e:
                print(f"❌ Backup error for {original}: {e}")
                error_count += 1
    
    # Apply renames
    for old_name, new_name, reason in plan['renames']:
        old_path = images_path / old_name
        new_path = images_path / new_name
        
        if dry_run:
            print(f"Would rename: {old_name} → {new_name}")
            print(f"   📝 {reason}")
        else:
            try:
                old_path.rename(new_path)
                print(f"✅ Renamed: {old_name} → {new_name}")
                success_count += 1
            except Exception as e:
                print(f"❌ Error renaming {old_name}: {e}")
                error_count += 1
    
    if not dry_run:
        print(f"\n📊 OPERATION RESULTS:")
        print(f"   Successful renames: {success_count}")
        print(f"   Errors: {error_count}")
        print(f"   Backups created: {len(plan['backup_needed'])}")
    
    return success_count, error_count

def main():
    """Main workflow."""
    images_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/public/images"
    
    print("🎯 ADVANCED IMAGE NAMING NORMALIZATION")
    print("="*50)
    print(f"Target directory: {images_dir}")
    
    # Preview the resolution plan
    plan = preview_resolution_plan(images_dir)
    
    if plan['conflicts']:
        print(f"\n⚠️  Please resolve conflicts before proceeding.")
        return plan
    
    # Show dry run
    apply_resolution_plan(images_dir, plan, dry_run=True)
    
    print(f"\n🔧 To apply changes, run with --apply flag")
    return plan

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--apply":
        images_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/public/images"
        plan = create_resolution_plan(images_dir)
        
        if plan['conflicts']:
            print("❌ Cannot apply - unresolved conflicts exist")
            for old_name, new_name, reason in plan['conflicts']:
                print(f"   {old_name} → {new_name}: {reason}")
        else:
            apply_resolution_plan(images_dir, plan, dry_run=False)
    else:
        main()
