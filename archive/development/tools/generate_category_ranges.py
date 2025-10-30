#!/usr/bin/env python3
"""
Generate category ranges for properties based on actual material values.

For each property that doesn't have category ranges:
1. Collect all values from materials in that category
2. Calculate min/max across all materials
3. Add to Categories.yaml category_ranges
"""

import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
MATERIALS_FILE = ROOT_DIR / "data" / "materials.yaml"
CATEGORIES_FILE = ROOT_DIR / "data" / "Categories.yaml"
BACKUP_FILE = ROOT_DIR / "data" / "Categories.backup.yaml"


def load_yaml(file_path: Path) -> Dict:
    """Load YAML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml(file_path: Path, data: Dict):
    """Save YAML file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def extract_numeric_value(value: Any) -> float:
    """Extract numeric value from various formats."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Try to extract first number from string
        import re
        match = re.search(r'[-+]?\d*\.?\d+', value)
        if match:
            return float(match.group())
    return None


def collect_property_ranges(materials_data: Dict) -> Dict[str, Dict[str, Dict]]:
    """
    Collect min/max ranges for each property by category.
    
    Returns: {category: {property_name: {min, max, unit, sample_count}}}
    """
    category_props = defaultdict(lambda: defaultdict(lambda: {
        'values': [],
        'unit': None,
        'descriptions': []
    }))
    
    for mat_name, mat_data in materials_data['materials'].items():
        category = mat_data.get('category', '').lower()
        if not category:
            continue
        
        properties = mat_data.get('properties', {})
        for prop_name, prop_data in properties.items():
            if not isinstance(prop_data, dict):
                continue
            
            value = prop_data.get('value')
            if value is None:
                continue
            
            numeric_value = extract_numeric_value(value)
            if numeric_value is None:
                continue
            
            # Collect data
            category_props[category][prop_name]['values'].append(numeric_value)
            
            if not category_props[category][prop_name]['unit']:
                category_props[category][prop_name]['unit'] = prop_data.get('unit', '')
            
            desc = prop_data.get('description', '')
            if desc and desc not in category_props[category][prop_name]['descriptions']:
                category_props[category][prop_name]['descriptions'].append(desc)
    
    # Calculate ranges
    ranges = {}
    for category, props in category_props.items():
        ranges[category] = {}
        for prop_name, prop_info in props.items():
            values = prop_info['values']
            if len(values) < 2:  # Need at least 2 materials
                continue
            
            ranges[category][prop_name] = {
                'min': min(values),
                'max': max(values),
                'unit': prop_info['unit'],
                'sample_count': len(values),
                'description': prop_info['descriptions'][0] if prop_info['descriptions'] else ''
            }
    
    return ranges


def update_categories_with_ranges(categories_data: Dict, new_ranges: Dict) -> Dict:
    """Add new ranges to Categories.yaml category_ranges."""
    
    stats = {
        'categories_updated': 0,
        'properties_added': 0,
        'properties_skipped': 0
    }
    
    for category_name, category_data in categories_data['categories'].items():
        if category_name not in new_ranges:
            continue
        
        if 'category_ranges' not in category_data:
            category_data['category_ranges'] = {}
        
        existing_ranges = category_data['category_ranges']
        new_cat_ranges = new_ranges[category_name]
        
        for prop_name, range_data in new_cat_ranges.items():
            # Skip if already has ranges
            if prop_name in existing_ranges:
                stats['properties_skipped'] += 1
                continue
            
            # Add new range
            existing_ranges[prop_name] = {
                'min': range_data['min'],
                'max': range_data['max'],
                'unit': range_data['unit'],
                'description': range_data['description'],
                'sample_count': range_data['sample_count'],
                'auto_generated': True,
                'generated_date': '2025-10-16'
            }
            
            stats['properties_added'] += 1
        
        if category_name in new_ranges and new_ranges[category_name]:
            stats['categories_updated'] += 1
    
    return categories_data, stats


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate category ranges from material values',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes)
  python3 scripts/tools/generate_category_ranges.py --dry-run
  
  # Generate and add ranges
  python3 scripts/tools/generate_category_ranges.py
  
  # Show detailed report
  python3 scripts/tools/generate_category_ranges.py --verbose
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed property information')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    
    args = parser.parse_args()
    
    print(f"\n{'=' * 70}")
    print(f"Generate Category Ranges from Material Values")
    print(f"{'=' * 70}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE UPDATE'}")
    print(f"Backup: {'Disabled' if args.no_backup else 'Enabled'}")
    print(f"{'=' * 70}\n")
    
    # Load data
    print("📂 Loading data files...")
    materials_data = load_yaml(MATERIALS_FILE)
    categories_data = load_yaml(CATEGORIES_FILE)
    print(f"  ✅ Loaded {len(materials_data['materials'])} materials")
    print(f"  ✅ Loaded {len(categories_data['categories'])} categories\n")
    
    # Collect ranges
    print("🔍 Analyzing material properties by category...")
    new_ranges = collect_property_ranges(materials_data)
    
    # Report findings
    print(f"\n{'=' * 70}")
    print(f"Properties Found (by category)")
    print(f"{'=' * 70}\n")
    
    total_new_props = 0
    for category, props in sorted(new_ranges.items()):
        existing_count = len(categories_data['categories'][category].get('category_ranges', {}))
        new_count = len(props)
        print(f"{category}:")
        print(f"  Existing ranges: {existing_count}")
        print(f"  New ranges found: {new_count}")
        total_new_props += new_count
        
        if args.verbose:
            for prop_name, range_data in sorted(props.items()):
                # Check if already exists
                existing = categories_data['categories'][category].get('category_ranges', {})
                status = "⏭️ EXISTS" if prop_name in existing else "✅ NEW"
                print(f"    {status} {prop_name}: [{range_data['min']:.2f} - {range_data['max']:.2f}] {range_data['unit']} (n={range_data['sample_count']})")
        print()
    
    print(f"Total new properties: {total_new_props}\n")
    
    # Update categories
    if not args.dry_run:
        # Backup
        if not args.no_backup:
            print("💾 Creating backup...")
            save_yaml(BACKUP_FILE, categories_data)
            print(f"  ✅ Backup saved: {BACKUP_FILE}\n")
        
        print("📝 Updating Categories.yaml...")
        updated_data, stats = update_categories_with_ranges(categories_data, new_ranges)
        
        # Save
        save_yaml(CATEGORIES_FILE, updated_data)
        
        print(f"\n{'=' * 70}")
        print(f"Update Summary")
        print(f"{'=' * 70}")
        print(f"Categories updated:   {stats['categories_updated']}")
        print(f"Properties added:     {stats['properties_added']} ✅")
        print(f"Properties skipped:   {stats['properties_skipped']} ⏭️")
        print(f"{'=' * 70}\n")
        print(f"✅ Categories.yaml updated successfully")
    else:
        print("⚠️  DRY RUN - No files were modified")
        print(f"   Would add {total_new_props} new property ranges")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
