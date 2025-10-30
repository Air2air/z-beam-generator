#!/usr/bin/env python3
"""
Update all frontmatter files with latest category ranges from Categories.yaml.

This script:
1. Loads category ranges from Categories.yaml
2. Updates each frontmatter file's materialProperties min/max ranges
3. Preserves existing property values and units
4. Adds missing category ranges for properties
5. Creates backup before modifications
"""

import sys
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

def load_category_ranges(categories_path):
    """Load category ranges from Categories.yaml."""
    print(f"\n{'='*80}")
    print("Loading category ranges from Categories.yaml")
    print(f"{'='*80}\n")
    
    with open(categories_path, 'r', encoding='utf-8') as f:
        categories_data = yaml.safe_load(f)
    
    # Extract category ranges from categories section
    category_ranges = {}
    
    # Get the categories section
    categories = categories_data.get('categories', {})
    
    for category_name, category_data in categories.items():
        if not isinstance(category_data, dict):
            continue
        
        # Check for category_ranges or properties section
        ranges_data = category_data.get('category_ranges') or category_data.get('properties')
        
        if not ranges_data or not isinstance(ranges_data, dict):
            continue
        
        category_ranges[category_name] = {}
        
        # Extract min/max from each property
        for prop_name, prop_data in ranges_data.items():
            if isinstance(prop_data, dict):
                if 'min' in prop_data and 'max' in prop_data:
                    category_ranges[category_name][prop_name] = {
                        'min': prop_data['min'],
                        'max': prop_data['max']
                    }
    
    print(f"  ✅ Loaded ranges for {len(category_ranges)} categories")
    for cat_name, props in sorted(category_ranges.items()):
        print(f"    • {cat_name}: {len(props)} properties")
    
    return category_ranges

def update_frontmatter_file(file_path, category_ranges):
    """Update a single frontmatter file with category ranges."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data:
        return False, 0
    
    # Get material category
    material_category = data.get('category')
    if not material_category:
        return False, 0
    
    # Get category ranges for this material
    cat_ranges = category_ranges.get(material_category, {})
    
    if not cat_ranges:
        return False, 0
    
    modified = False
    updates_count = 0
    
    # Update materialProperties
    mat_props = data.get('materialProperties', {})
    
    for category_name in ['laser_material_interaction', 'material_characteristics']:
        if category_name not in mat_props:
            continue
        
        category_data = mat_props[category_name]
        if 'properties' not in category_data:
            continue
        
        properties = category_data['properties']
        
        # Update each property with category ranges
        for prop_name, prop_data in properties.items():
            if not isinstance(prop_data, dict):
                continue
            
            # Check if this property has a category range
            if prop_name in cat_ranges:
                range_info = cat_ranges[prop_name]
                
                # Update min/max if they exist or add them
                current_min = prop_data.get('min')
                current_max = prop_data.get('max')
                
                new_min = range_info['min']
                new_max = range_info['max']
                
                # Only update if different
                if current_min != new_min or current_max != new_max:
                    prop_data['min'] = new_min
                    prop_data['max'] = new_max
                    modified = True
                    updates_count += 1
    
    if modified:
        # Save updated file
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return modified, updates_count

def update_all_frontmatter(frontmatter_dir, category_ranges):
    """Update all frontmatter files with category ranges."""
    print(f"\n{'='*80}")
    print("Updating frontmatter files")
    print(f"{'='*80}\n")
    
    frontmatter_files = list(frontmatter_dir.glob('*.yaml'))
    
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'total_updates': 0,
        'by_category': defaultdict(lambda: {'files': 0, 'updates': 0})
    }
    
    for file_path in sorted(frontmatter_files):
        stats['files_processed'] += 1
        
        # Load to get category
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        material_category = data.get('category') if data else None
        
        # Update file
        modified, updates = update_frontmatter_file(file_path, category_ranges)
        
        if modified:
            stats['files_modified'] += 1
            stats['total_updates'] += updates
            
            if material_category:
                stats['by_category'][material_category]['files'] += 1
                stats['by_category'][material_category]['updates'] += updates
            
            print(f"  ✅ {file_path.name}: {updates} properties updated")
    
    return stats

def verify_updates(frontmatter_dir, category_ranges):
    """Verify that all properties have appropriate ranges."""
    print(f"\n{'='*80}")
    print("Verifying range updates")
    print(f"{'='*80}\n")
    
    frontmatter_files = list(frontmatter_dir.glob('*.yaml'))
    
    issues = []
    success_count = 0
    
    for file_path in frontmatter_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            continue
        
        material_category = data.get('category')
        cat_ranges = category_ranges.get(material_category, {})
        
        mat_props = data.get('materialProperties', {})
        
        # Check each property
        for category_name in ['laser_material_interaction', 'material_characteristics']:
            if category_name not in mat_props:
                continue
            
            category_data = mat_props[category_name]
            if 'properties' not in category_data:
                continue
            
            properties = category_data['properties']
            
            for prop_name, prop_data in properties.items():
                if not isinstance(prop_data, dict):
                    continue
                
                # If category range exists, property should have min/max
                if prop_name in cat_ranges:
                    if 'min' not in prop_data or 'max' not in prop_data:
                        issues.append(f"{file_path.name}: {prop_name} missing min/max")
                    else:
                        success_count += 1
    
    if issues:
        print(f"⚠️  Issues found ({len(issues)}):")
        for issue in issues[:10]:
            print(f"  • {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
        return False
    else:
        print(f"✅ All properties have appropriate ranges ({success_count} verified)")
        return True

def backup_files(files_to_backup, backup_dir):
    """Create backup of files before modification."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in files_to_backup:
        if file_path.exists():
            relative_path = file_path.relative_to(project_root)
            backup_path = backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)

def main():
    """Main execution function."""
    print(f"\n{'='*80}")
    print("FRONTMATTER RANGE UPDATE TOOL")
    print(f"{'='*80}")
    print(f"\nUpdating frontmatter files with category ranges")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    # Define paths
    categories_path = project_root / 'data' / 'Categories.yaml'
    frontmatter_dir = project_root / 'content' / 'components' / 'frontmatter'
    
    # Create backup directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = project_root / 'backups' / f'frontmatter_update_{timestamp}'
    
    print("Creating backups...")
    files_to_backup = list(frontmatter_dir.glob('*.yaml'))
    backup_files(files_to_backup, backup_dir)
    print(f"✅ Backed up {len(files_to_backup)} files to: {backup_dir.relative_to(project_root)}\n")
    
    # Load category ranges
    category_ranges = load_category_ranges(categories_path)
    
    if not category_ranges:
        print("\n❌ No category ranges found in Categories.yaml")
        return 1
    
    # Update frontmatter files
    stats = update_all_frontmatter(frontmatter_dir, category_ranges)
    
    # Verify updates
    verification_passed = verify_updates(frontmatter_dir, category_ranges)
    
    # Final summary
    print(f"\n{'='*80}")
    print("UPDATE COMPLETE")
    print(f"{'='*80}\n")
    print("Summary:")
    print(f"  • Files processed: {stats['files_processed']}")
    print(f"  • Files modified: {stats['files_modified']}")
    print(f"  • Total property updates: {stats['total_updates']}")
    print(f"  • Backup location: {backup_dir.relative_to(project_root)}")
    print(f"  • Verification: {'✅ PASSED' if verification_passed else '⚠️  ISSUES FOUND'}")
    
    if stats['by_category']:
        print("\nUpdates by category:")
        for cat_name, cat_stats in sorted(stats['by_category'].items()):
            print(f"  • {cat_name}:")
            print(f"    - Files: {cat_stats['files']}")
            print(f"    - Updates: {cat_stats['updates']}")
    
    print(f"\n{'='*80}\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
