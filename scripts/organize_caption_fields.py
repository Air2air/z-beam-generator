#!/usr/bin/env python3
"""
Caption Field Organization Script
Reorganizes scattered caption-related fields         if dry_run:
            print("   📋 Would create caption structure with:")
            try:
                print(f"      • beforeText: {len(updated_data['caption']['beforeText'])} chars")
                print(f"      • afterText: {len(updated_data['caption']['afterText'])} chars") 
                print(f"      • description: {len(updated_data['caption']['description'])} chars")
                print(f"      • alt: {len(updated_data['caption']['alt'])} chars")
                print(f"      • imageUrl: {updated_data['caption']['imageUrl']}")
                if 'images' in updated_data:
                    hero_info = updated_data['images'].get('hero', {})
                    hero_url = hero_info.get('url', 'none') if isinstance(hero_info, dict) else 'none'
                    print(f"      • images.hero preserved: {hero_url}")
                else:
                    print("      • images section removed (no hero image)")
            except Exception as e:
                print(f"      ❌ Error in dry_run output: {e}")
                print(f"      Debug - updated_data keys: {list(updated_data.keys())}")
                if 'caption' in updated_data:
                    print(f"      Debug - caption keys: {list(updated_data['caption'].keys())}")
            return True dedicated 'caption' key in frontmatter files.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any
import argparse

def reorganize_caption_fields(frontmatter_data: Dict[str, Any], material_name: str) -> Dict[str, Any]:
    """
    Reorganize caption-related fields under a dedicated 'caption' key.
    
    Args:
        frontmatter_data: The frontmatter dictionary
        material_name: Name of the material for generating descriptions
    
    Returns:
        Updated frontmatter data with organized caption structure
    """
    
    try:
        # Extract current image alt texts
        images = frontmatter_data.get('images', {})
        micro_data = images.get('micro', {})
        hero_data = images.get('hero', {})
        
        micro_alt = micro_data.get('alt', '') if isinstance(micro_data, dict) else ''
        micro_url = micro_data.get('url', '') if isinstance(micro_data, dict) else ''
        hero_url = hero_data.get('url', '') if isinstance(hero_data, dict) else ''
        
        # Create enhanced caption structure using only micro image
        frontmatter_data['caption'] = {
            'beforeText': f"{material_name} surface before laser cleaning treatment showing contamination and surface irregularities",
            'afterText': f"Microscopic view of clean {material_name} surface after precise laser cleaning treatment with restored surface integrity",
            'imageUrl': micro_url,
            'description': micro_alt or f"Microscopic view of {material_name} surface after laser cleaning showing detailed surface structure",
            'alt': micro_alt or f"Microscopic view of {material_name} surface after laser cleaning showing detailed surface structure",
            'technicalAnalysis': {
                'focus': 'surface_cleaning_effectiveness',
                'characteristics': [
                    'contamination_removal',
                    'surface_integrity_preservation', 
                    'precision_cleaning_control'
                ],
                'process': 'laser_ablation_cleaning',
                'microscopyType': 'scanning_electron_microscopy',
                'magnification': '1000x',
                'fieldOfView': '200_micrometers'
            }
        }
        
        # Update images structure to contain only hero (remove micro since it's now in caption)
        if 'images' in frontmatter_data and hero_url:
            frontmatter_data['images'] = {
                'hero': {'url': hero_url}
            }
        elif 'images' in frontmatter_data:
            # If no hero URL, remove images section entirely since micro is now in caption
            del frontmatter_data['images']
        
        return frontmatter_data
        
    except Exception as e:
        print(f"Debug - Error in reorganize_caption_fields: {e}")
        print(f"Debug - Images structure: {frontmatter_data.get('images', 'NOT FOUND')}")
        raise

def process_frontmatter_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Process a single frontmatter file to reorganize caption fields.
    
    Args:
        file_path: Path to the frontmatter file
        dry_run: If True, don't write changes, just show what would be done
    
    Returns:
        True if processing was successful, False otherwise
    """
    
    try:
        # Load the frontmatter file
        with open(file_path, 'r', encoding='utf-8') as f:
            frontmatter_data = yaml.safe_load(f)
        
        if not frontmatter_data:
            print(f"⚠️  Empty or invalid YAML: {file_path.name}")
            return False
        
        # Extract material name
        material_name = frontmatter_data.get('name', file_path.stem.replace('-laser-cleaning', ''))
        
        # Check if caption key already exists
        if 'caption' in frontmatter_data:
            print(f"⏭️  Already has caption key: {file_path.name}")
            return True
        
        # Check if images exist to reorganize
        images = frontmatter_data.get('images', {})
        if not images or not any('alt' in img_data for img_data in images.values() if isinstance(img_data, dict)):
            print(f"⚠️  No image alt texts to reorganize: {file_path.name}")
            return False
        
        print(f"🔄 Processing: {file_path.name}")
        
        # Reorganize caption fields
        updated_data = reorganize_caption_fields(frontmatter_data, material_name)
        
        if dry_run:
            print("   📋 Would create caption structure with:")
            try:
                print(f"      • beforeText: {len(updated_data['caption']['beforeText'])} chars")
                print(f"      • afterText: {len(updated_data['caption']['afterText'])} chars") 
                print(f"      • description: {len(updated_data['caption']['description'])} chars")
                print(f"      • alt: {len(updated_data['caption']['alt'])} chars")
                print(f"      • imageUrl: {updated_data['caption']['imageUrl']}")
                if 'images' in updated_data:
                    hero_info = updated_data['images'].get('hero', {})
                    hero_url = hero_info.get('url', 'none') if isinstance(hero_info, dict) else 'none'
                    print(f"      • images.hero preserved: {hero_url}")
                else:
                    print("      • images section removed (no hero image)")
            except Exception as e:
                print(f"      ❌ Error in dry_run output: {e}")
                print(f"      Debug - updated_data keys: {list(updated_data.keys())}")
                if 'caption' in updated_data:
                    print(f"      Debug - caption keys: {list(updated_data['caption'].keys())}")
            return True
        
        # Write updated frontmatter
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(updated_data, f, default_flow_style=False, sort_keys=False, 
                     allow_unicode=True, width=120, indent=2)
        
        print(f"   ✅ Caption structure organized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to process all frontmatter files."""
    
    parser = argparse.ArgumentParser(
        description="Reorganize caption-related fields in frontmatter files"
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        '--material',
        type=str,
        help="Process only a specific material (e.g., 'aluminum')"
    )
    
    args = parser.parse_args()
    
    print("🎯 CAPTION FIELD ORGANIZATION")
    print("=" * 50)
    print("📋 Moving scattered caption fields under dedicated 'caption' key")
    print()
    
    # Define frontmatter directory
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return 1
    
    # Get files to process
    if args.material:
        pattern = f"{args.material}*laser-cleaning.yaml"
        files = list(frontmatter_dir.glob(pattern))
        if not files:
            print(f"❌ No frontmatter file found for material: {args.material}")
            return 1
    else:
        files = list(frontmatter_dir.glob("*-laser-cleaning.yaml"))
    
    if not files:
        print(f"❌ No frontmatter files found in {frontmatter_dir}")
        return 1
    
    print(f"📁 Found {len(files)} frontmatter files to process")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    print()
    
    # Process files
    successful = 0
    skipped = 0
    failed = 0
    
    for file_path in sorted(files):
        result = process_frontmatter_file(file_path, dry_run=args.dry_run)
        
        if result is True:
            successful += 1
        elif result is False:
            failed += 1
        else:
            skipped += 1
    
    # Summary
    print()
    print("📊 PROCESSING SUMMARY")
    print("-" * 30)
    print(f"✅ Successful: {successful}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Total: {len(files)}")
    
    if args.dry_run:
        print()
        print("💡 Run without --dry-run to apply changes")
    elif successful > 0:
        print()
        print("🎉 Caption field organization completed!")
        print("   All caption-related fields are now organized under the 'caption' key")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())