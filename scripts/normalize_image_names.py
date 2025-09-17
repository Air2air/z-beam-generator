#!/usr/bin/env python3
"""
Normalize image naming convention in Next.js public/images directory.
Standardizes all images to {material-name}-laser-cleaning-{hero|micro}.jpg format.
"""
import os
import shutil
from pathlib import Path

def get_material_mapping():
    """Define mapping from current names to normalized names."""
    return {
        # Category-prefixed images that need normalization
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
        'carbon-steel': 'steel',
        'cast-iron': 'iron',
        'cobalt-chromium': 'cobalt',  # Keep cobalt as primary
        'galvanized-steel': 'steel',  # Note: This might conflict with steel
        'tool-steel': 'steel',       # Note: This might conflict with steel
        'concrete-block': 'concrete',
        'terra-cotta': 'terracotta',  # Normalize hyphenation
        'indium-glass': 'indium',     # Keep indium as primary
    }

def analyze_images_directory(images_dir):
    """Analyze current naming patterns and propose normalizations."""
    images_path = Path(images_dir)
    if not images_path.exists():
        print(f"❌ Images directory not found: {images_dir}")
        return {}
    
    material_mapping = get_material_mapping()
    rename_operations = []
    conflicts = []
    
    # Get all hero/micro images
    hero_micro_images = list(images_path.glob("*-hero.jpg")) + list(images_path.glob("*-micro.jpg"))
    
    for img_file in hero_micro_images:
        filename = img_file.name
        
        # Extract components
        if '-hero.jpg' in filename:
            prefix = filename.replace('-laser-cleaning-hero.jpg', '').replace('-hero.jpg', '')
            image_type = 'hero'
        elif '-micro.jpg' in filename:
            prefix = filename.replace('-laser-cleaning-micro.jpg', '').replace('-micro.jpg', '')
            image_type = 'micro'
        else:
            continue
        
        # Check if normalization is needed
        normalized_material = material_mapping.get(prefix, prefix)
        
        # Standard normalized filename
        normalized_filename = f"{normalized_material}-laser-cleaning-{image_type}.jpg"
        
        if filename != normalized_filename:
            # Check if target already exists
            target_path = images_path / normalized_filename
            if target_path.exists():
                conflicts.append((filename, normalized_filename, "Target already exists"))
            else:
                rename_operations.append((filename, normalized_filename))
    
    return rename_operations, conflicts

def preview_normalization(images_dir):
    """Preview what the normalization would do."""
    print("🔍 ANALYZING IMAGE NORMALIZATION NEEDS")
    print("="*60)
    
    rename_ops, conflicts = analyze_images_directory(images_dir)
    
    if rename_ops:
        print(f"\n✅ PROPOSED RENAMES ({len(rename_ops)}):")
        for old_name, new_name in sorted(rename_ops):
            print(f"   {old_name}")
            print(f"   → {new_name}")
            print()
    
    if conflicts:
        print(f"\n⚠️  CONFLICTS FOUND ({len(conflicts)}):")
        for old_name, new_name, reason in conflicts:
            print(f"   {old_name} → {new_name}")
            print(f"   ⚠️  {reason}")
            print()
    
    if not rename_ops and not conflicts:
        print("✅ All images already follow the normalized naming convention!")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Files to rename: {len(rename_ops)}")
    print(f"   Conflicts: {len(conflicts)}")
    
    return rename_ops, conflicts

def apply_normalization(images_dir, rename_operations, dry_run=True):
    """Apply the normalization renames."""
    images_path = Path(images_dir)
    
    if dry_run:
        print("\n🧪 DRY RUN - No files will be modified")
        print("="*40)
    else:
        print("\n🔧 APPLYING NORMALIZATIONS")
        print("="*40)
    
    success_count = 0
    error_count = 0
    
    for old_name, new_name in rename_operations:
        old_path = images_path / old_name
        new_path = images_path / new_name
        
        try:
            if dry_run:
                print(f"Would rename: {old_name} → {new_name}")
            else:
                old_path.rename(new_path)
                print(f"✅ Renamed: {old_name} → {new_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error renaming {old_name}: {e}")
            error_count += 1
    
    print(f"\n📊 OPERATION SUMMARY:")
    print(f"   Successful: {success_count}")
    print(f"   Errors: {error_count}")
    
    return success_count, error_count

def main():
    """Main normalization workflow."""
    images_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/public/images"
    
    print("🎯 IMAGE NAMING NORMALIZATION TOOL")
    print("="*50)
    print(f"Target directory: {images_dir}")
    print("\nStandard format: {material-name}-laser-cleaning-{hero|micro}.jpg")
    
    # Preview what would be done
    rename_ops, conflicts = preview_normalization(images_dir)
    
    if conflicts:
        print(f"\n⚠️  Please resolve conflicts before proceeding.")
        return
    
    if rename_ops:
        print(f"\n🤔 Apply these {len(rename_ops)} renames? (y/n): ", end="")
        # For script execution, we'll do a dry run first
        print("Running dry run first...")
        
        # Dry run
        apply_normalization(images_dir, rename_ops, dry_run=True)
        
        print(f"\n🔧 To apply changes, run with --apply flag")
    else:
        print(f"\n🎉 No normalization needed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--apply":
        # Actually apply the changes
        images_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/public/images"
        rename_ops, conflicts = analyze_images_directory(images_dir)
        
        if conflicts:
            print("❌ Cannot apply - conflicts exist")
            for old_name, new_name, reason in conflicts:
                print(f"   {old_name} → {new_name}: {reason}")
        elif rename_ops:
            apply_normalization(images_dir, rename_ops, dry_run=False)
        else:
            print("✅ No changes needed")
    else:
        main()
