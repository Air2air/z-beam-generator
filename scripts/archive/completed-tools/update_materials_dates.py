#!/usr/bin/env python3
"""
Update datePublished and dateModified fields in Materials.yaml based on Git history.

This script:
1. Reads Materials.yaml
2. For each material, gets first commit date (published) and last commit date (modified)
3. Adds datePublished and dateModified fields in ISO 8601 format
4. Saves the updated Materials.yaml

Usage:
    python3 scripts/tools/update_materials_dates.py [--dry-run] [--material MaterialName]
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def get_file_first_commit_date(file_path: Path) -> str:
    """
    Get the first commit date of Materials.yaml file.
    This will be used as datePublished for ALL materials.
    
    Returns:
        str: ISO 8601 formatted date string
    """
    try:
        cmd = [
            'git', 'log',
            '--follow',
            '--format=%aI',
            '--reverse',
            '--', str(file_path)
        ]
        
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        
        dates = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        
        if not dates:
            # Fallback to current date
            now = datetime.now().isoformat()
            print(f"   ⚠️  No git history found, using current date: {now}")
            return now
        
        return dates[0]
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Git command failed: {e}")
        # Fallback to current date
        return datetime.now().isoformat()


def get_material_last_modified_date(material_name: str, file_path: Path) -> str:
    """
    Get the last commit date for a specific material in Materials.yaml.
    
    Returns:
        str: ISO 8601 formatted date string
    """
    try:
        # Search git log for commits that mention this material
        # Use -G to search for lines that were added/modified/deleted
        pattern = f"^  {material_name}:"
        
        # Get all commit dates for this material (newest first)
        cmd = [
            'git', 'log',
            '--follow',
            '--format=%aI',
            '-G', pattern,
            '--', str(file_path)
        ]
        
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        
        dates = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        
        if not dates:
            # If no material-specific commits found, use file's last commit date
            cmd_file = [
                'git', 'log',
                '--follow',
                '--format=%aI',
                '-1',
                '--', str(file_path)
            ]
            
            result_file = subprocess.run(
                cmd_file,
                cwd=project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            file_dates = [line.strip() for line in result_file.stdout.strip().split('\n') if line.strip()]
            
            if not file_dates:
                # Ultimate fallback: use current date
                return datetime.now().isoformat()
            
            return file_dates[0]
        
        # Return most recent commit date (first in list)
        return dates[0]
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Git command failed for {material_name}: {e}")
        # Fallback to current date
        return datetime.now().isoformat()


def update_materials_yaml(dry_run: bool = False, specific_material: str = None):
    """
    Update Materials.yaml with datePublished and dateModified fields.
    
    Args:
        dry_run: If True, show what would be changed without modifying the file
        specific_material: If provided, only update this specific material
    """
    materials_file = project_root / 'materials' / 'data' / 'Materials.yaml'
    
    print("\n" + "="*80)
    print("UPDATE MATERIALS.YAML WITH GIT DATES")
    print("="*80)
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be saved\n")
    
    # Load Materials.yaml
    print(f"📂 Loading {materials_file.relative_to(project_root)}...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Create backup before modifying
    if not dry_run:
        backup_file = materials_file.parent / f"Materials.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        print(f"💾 Creating backup: {backup_file.name}...")
        with open(backup_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Get the materials section
    if 'materials' in data and isinstance(data['materials'], dict):
        # Materials are nested under 'materials' key
        materials_section = data['materials']
    else:
        # Fallback: materials are at root level (exclude metadata sections)
        excluded_keys = {'category_metadata', 'material_index', 'materials', 'metadata', '_extraction_metadata'}
        materials_section = {k: v for k, v in data.items() 
                            if k not in excluded_keys
                            and isinstance(v, dict)
                            and 'name' in v}  # Materials have a 'name' field
    
    materials_to_process = (
        {specific_material: materials_section[specific_material]} 
        if specific_material and specific_material in materials_section 
        else materials_section
    )
    
    total_materials = len(materials_to_process)
    updated_count = 0
    skipped_count = 0
    
    # Get the Materials.yaml file's first commit date (used for ALL materials)
    print("\n📅 Getting Materials.yaml first commit date (datePublished for all materials)...")
    date_published = get_file_first_commit_date(materials_file)
    print(f"   ✅ File first commit: {date_published}\n")
    
    print(f"🔧 Processing {total_materials} material{'s' if total_materials != 1 else ''}...\n")
    
    for i, (material_name, material_data) in enumerate(materials_to_process.items(), 1):
        print(f"[{i}/{total_materials}] {material_name}...")
        
        # Check if dates already exist
        has_published = 'datePublished' in material_data
        has_modified = 'dateModified' in material_data
        
        if has_published and has_modified and not dry_run:
            print("   ⏭️  Already has dates, skipping")
            skipped_count += 1
            continue
        
        # Get last modified date for this specific material
        date_modified = get_material_last_modified_date(material_name, materials_file)
        
        # Add dates to material data (after 'name' field for logical ordering)
        if not has_published:
            material_data['datePublished'] = date_published
        if not has_modified:
            material_data['dateModified'] = date_modified
        
        # Show what was added/updated
        if dry_run or not (has_published and has_modified):
            print(f"   ✅ datePublished: {date_published}")
            print(f"   ✅ dateModified:  {date_modified}")
            updated_count += 1
    
    # Save updated file
    if not dry_run:
        print("\n💾 Saving updated Materials.yaml...")
        with open(materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print("✅ File saved successfully")
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"   Materials processed: {total_materials}")
    print(f"   Updated: {updated_count}")
    print(f"   Skipped: {skipped_count}")
    
    if dry_run:
        print("\n💡 Run without --dry-run to apply these changes")
    else:
        print("\n✅ Materials.yaml updated successfully!")
    
    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Update Materials.yaml with datePublished and dateModified from Git history'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying the file'
    )
    parser.add_argument(
        '--material',
        type=str,
        help='Process only this specific material (e.g., "Aluminum")'
    )
    
    args = parser.parse_args()
    
    update_materials_yaml(dry_run=args.dry_run, specific_material=args.material)


if __name__ == '__main__':
    main()
