#!/usr/bin/env python3
"""
Remove material-specific ranges that should be null (no category range defined).

This script reverts the incorrect backfill that added material-specific ranges
when only category-wide ranges should be used.
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, List


def load_categories_ranges() -> Dict[str, Dict]:
    """Load category ranges from Categories.yaml"""
    with open('data/Categories.yaml', 'r', encoding='utf-8') as f:
        cat_data = yaml.safe_load(f)
    
    category_ranges = {}
    if 'categories' in cat_data:
        for cat_name, cat_info in cat_data['categories'].items():
            if 'category_ranges' in cat_info:
                category_ranges[cat_name] = cat_info['category_ranges']
    
    return category_ranges


def should_property_have_null_ranges(
    prop_name: str,
    material_category: str,
    category_ranges: Dict[str, Dict]
) -> bool:
    """Check if a property should have null ranges (not in category ranges)"""
    if material_category not in category_ranges:
        return True
    
    return prop_name not in category_ranges[material_category]


def clean_frontmatter_ranges(
    fm_data: Dict[str, Any],
    material_category: str,
    category_ranges: Dict[str, Dict]
) -> Tuple[int, List[str]]:
    """
    Set ranges to null for properties that don't have category ranges defined.
    
    Returns:
        Tuple of (properties cleaned, list of cleaned property names)
    """
    cleaned_count = 0
    cleaned_props = []
    
    if 'materialProperties' not in fm_data:
        return 0, []
    
    for category_name, category_data in fm_data['materialProperties'].items():
        if not isinstance(category_data, dict) or 'properties' not in category_data:
            continue
        
        for prop_name, prop_data in category_data['properties'].items():
            if not isinstance(prop_data, dict):
                continue
            
            # Check if this property should have null ranges
            if should_property_have_null_ranges(prop_name, material_category, category_ranges):
                # Check if it currently has ranges
                if prop_data.get('min') is not None or prop_data.get('max') is not None:
                    prop_data['min'] = None
                    prop_data['max'] = None
                    cleaned_count += 1
                    cleaned_props.append(f"{category_name}.{prop_name}")
    
    return cleaned_count, cleaned_props


def main():
    """Main execution"""
    print("🧹 Clean Incorrect Material-Specific Ranges")
    print("=" * 80)
    print("Removing material-specific ranges where only category ranges should exist")
    print("=" * 80)
    
    # Load category ranges
    try:
        category_ranges = load_categories_ranges()
        print(f"\n✅ Loaded category ranges for {len(category_ranges)} categories")
        for cat_name, ranges in category_ranges.items():
            print(f"   {cat_name}: {len(ranges)} properties with category ranges")
    except Exception as e:
        print(f"❌ Failed to load Categories.yaml: {e}")
        return 1
    
    # Process all frontmatter files
    frontmatter_dir = Path('content/components/frontmatter')
    fm_files = list(frontmatter_dir.glob('*laser-cleaning.yaml'))
    
    print(f"\n📁 Found {len(fm_files)} frontmatter files")
    print("\nProcessing...")
    print("-" * 80)
    
    total_cleaned = 0
    files_updated = 0
    
    for fm_file in fm_files:
        try:
            with open(fm_file, 'r', encoding='utf-8') as f:
                fm_data = yaml.safe_load(f)
            
            material_category = fm_data.get('category', '').lower()
            if not material_category:
                continue
            
            cleaned_count, cleaned_props = clean_frontmatter_ranges(
                fm_data,
                material_category,
                category_ranges
            )
            
            if cleaned_count > 0:
                # Write back
                with open(fm_file, 'w', encoding='utf-8') as f:
                    yaml.dump(fm_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
                files_updated += 1
                total_cleaned += cleaned_count
                print(f"✅ {fm_file.stem:50s} - Cleaned {cleaned_count} properties")
        
        except Exception as e:
            print(f"❌ {fm_file.stem:50s} - Error: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Files processed:      {len(fm_files)}")
    print(f"Files updated:        {files_updated}")
    print(f"Properties cleaned:   {total_cleaned}")
    print()
    print("✅ Properties now correctly show:")
    print("   - Category ranges where defined in Categories.yaml")
    print("   - Null ranges where no category range exists")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
