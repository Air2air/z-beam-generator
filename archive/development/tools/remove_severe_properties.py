#!/usr/bin/env python3
"""
Remove SEVERE data quality issue properties from the system.

Properties to remove:
1. chemicalStability - 13 units, mixing qualitative and quantitative
2. crystallineStructure - 7 units, qualitative non-numeric property

Removes from:
- data/Categories.yaml (propertyCategories definitions)
- content/components/frontmatter/*.yaml (all material files)
"""

import os
import sys
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from collections import Counter

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

PROPERTIES_TO_REMOVE = ['chemicalStability', 'crystallineStructure']

def backup_files(files_to_backup, backup_dir):
    """Create backup of files before modification."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in files_to_backup:
        if file_path.exists():
            relative_path = file_path.relative_to(project_root)
            backup_path = backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            print(f"  ✅ Backed up: {relative_path}")

def remove_from_categories(categories_path):
    """Remove properties from Categories.yaml propertyCategories."""
    print(f"\n{'='*80}")
    print("STEP 1: Remove from Categories.yaml")
    print(f"{'='*80}\n")
    
    with open(categories_path, 'r', encoding='utf-8') as f:
        categories = yaml.safe_load(f)
    
    removed_count = 0
    
    # Remove from property lists in propertyCategories.categories
    prop_categories = categories.get('propertyCategories', {})
    if 'categories' in prop_categories:
        for category_name, category_data in prop_categories['categories'].items():
            properties_list = category_data.get('properties', [])
            
            # Check if properties is a list
            if isinstance(properties_list, list):
                original_length = len(properties_list)
                # Remove properties from the list
                properties_list[:] = [prop for prop in properties_list if prop not in PROPERTIES_TO_REMOVE]
                new_length = len(properties_list)
                
                if new_length < original_length:
                    removed = original_length - new_length
                    removed_count += removed
                    print(f"  ✅ Removed {removed} property(ies) from {category_name}")
    
    # Save updated Categories.yaml
    with open(categories_path, 'w', encoding='utf-8') as f:
        yaml.dump(categories, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n  📊 Total properties removed from Categories.yaml: {removed_count}")
    
    return removed_count

def remove_from_frontmatter(frontmatter_dir):
    """Remove properties from all frontmatter YAML files."""
    print(f"\n{'='*80}")
    print("STEP 2: Remove from frontmatter files")
    print(f"{'='*80}\n")
    
    frontmatter_files = list(frontmatter_dir.glob('*.yaml'))
    total_removed = 0
    files_modified = 0
    
    removal_stats = {prop: 0 for prop in PROPERTIES_TO_REMOVE}
    
    for file_path in frontmatter_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        modified = False
        
        # Check materialProperties categories
        mat_props = data.get('materialProperties', {})
        
        for category_name in ['laser_material_interaction', 'material_characteristics']:
            if category_name in mat_props:
                category_data = mat_props[category_name]
                
                # Properties are nested under 'properties' key
                if 'properties' in category_data:
                    category_props = category_data['properties']
                    
                    for prop in PROPERTIES_TO_REMOVE:
                        if prop in category_props:
                            del category_props[prop]
                            modified = True
                            total_removed += 1
                            removal_stats[prop] += 1
        
        if modified:
            files_modified += 1
            
            # Save updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("\n  📊 Removal Statistics:")
    for prop, count in removal_stats.items():
        print(f"    • {prop}: {count} instances removed")
    
    print("\n  📊 Total Summary:")
    print(f"    • Files modified: {files_modified}")
    print(f"    • Property instances removed: {total_removed}")
    
    return files_modified, total_removed, removal_stats

def verify_removal(categories_path, frontmatter_dir):
    """Verify that properties were completely removed."""
    print(f"\n{'='*80}")
    print("STEP 3: Verify complete removal")
    print(f"{'='*80}\n")
    
    issues_found = []
    
    # Check Categories.yaml
    with open(categories_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for prop in PROPERTIES_TO_REMOVE:
        if prop in content:
            issues_found.append(f"❌ {prop} still found in Categories.yaml")
    
    # Check frontmatter files
    frontmatter_files = list(frontmatter_dir.glob('*.yaml'))
    
    for file_path in frontmatter_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for prop in PROPERTIES_TO_REMOVE:
            if prop in content:
                issues_found.append(f"❌ {prop} still found in {file_path.name}")
    
    if issues_found:
        print("  ⚠️  Issues found during verification:")
        for issue in issues_found[:10]:  # Show first 10
            print(f"    {issue}")
        if len(issues_found) > 10:
            print(f"    ... and {len(issues_found) - 10} more issues")
        return False
    else:
        print("  ✅ Verification successful - all properties completely removed")
        return True

def main():
    """Main execution function."""
    print(f"\n{'='*80}")
    print("SEVERE PROPERTY REMOVAL TOOL")
    print(f"{'='*80}")
    print(f"\nRemoving properties with SEVERE data quality issues:")
    for prop in PROPERTIES_TO_REMOVE:
        print(f"  • {prop}")
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    # Define paths
    categories_path = project_root / 'data' / 'Categories.yaml'
    frontmatter_dir = project_root / 'content' / 'components' / 'frontmatter'
    
    # Create backup directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = project_root / 'backups' / f'remove_severe_properties_{timestamp}'
    
    print("Creating backups...")
    files_to_backup = [categories_path] + list(frontmatter_dir.glob('*.yaml'))
    backup_files(files_to_backup, backup_dir)
    print(f"\n✅ Backed up {len(files_to_backup)} files to: {backup_dir.relative_to(project_root)}\n")
    
    # Execute removal
    categories_removed = remove_from_categories(categories_path)
    files_modified, total_removed, removal_stats = remove_from_frontmatter(frontmatter_dir)
    
    # Verify removal
    verification_passed = verify_removal(categories_path, frontmatter_dir)
    
    # Final summary
    print(f"\n{'='*80}")
    print("REMOVAL COMPLETE")
    print(f"{'='*80}\n")
    print(f"Summary:")
    print(f"  • Properties removed: {len(PROPERTIES_TO_REMOVE)}")
    print(f"  • Categories.yaml instances: {categories_removed}")
    print(f"  • Frontmatter files modified: {files_modified}")
    print(f"  • Total property instances removed: {total_removed}")
    print(f"  • Backup location: {backup_dir.relative_to(project_root)}")
    print(f"  • Verification: {'✅ PASSED' if verification_passed else '❌ FAILED'}")
    
    print("\nDetailed removal statistics:")
    for prop, count in removal_stats.items():
        print(f"  • {prop}: {count} instances")
    
    print(f"\n{'='*80}\n")
    
    if not verification_passed:
        print("⚠️  WARNING: Verification failed. Check output above for details.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
