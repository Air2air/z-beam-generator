#!/usr/bin/env python3
"""
Update all tests to use flattened materialProperties structure.
Removes .get('properties', {}) calls and accesses properties directly.
"""

import re
from pathlib import Path


def update_test_file(filepath: Path) -> tuple[bool, int]:
    """Update a single test file. Returns (modified, replacement_count)."""
    content = filepath.read_text()
    original_content = content
    replacement_count = 0
    
    # Pattern 1: .get('laser_material_interaction', {}).get('properties', {})
    # Replace with: .get('laser_material_interaction', {})
    pattern1 = r"\.get\('(laser_material_interaction|material_characteristics|other)', \{\}\)\.get\('properties', \{\}\)"
    replacement1 = r".get('\1', {})"
    content, count1 = re.subn(pattern1, replacement1, content)
    replacement_count += count1
    
    # Pattern 2: ['properties'] after category access
    # Example: updated['material_characteristics']['properties']
    # Replace with: updated['material_characteristics']
    pattern2 = r"\['(laser_material_interaction|material_characteristics|other)'\]\['properties'\]"
    replacement2 = r"['\1']"
    content, count2 = re.subn(pattern2, replacement2, content)
    replacement_count += count2
    
    # Pattern 3: section_data['properties']
    # This is trickier - need context. Only replace if it's clearly category data
    # Look for: props = section_data['properties']
    pattern3 = r"(\s+)props = section_data\['properties'\]"
    replacement3 = r"\1props = {k: v for k, v in section_data.items() if k not in ['label', 'description', 'percentage']}"
    content, count3 = re.subn(pattern3, replacement3, content)
    replacement_count += count3
    
    # Pattern 4: category_data.get('properties', {})
    # Replace with: {k: v for k, v in category_data.items() if k not in ['label', 'description', 'percentage']}
    pattern4 = r"category_data\.get\('properties', \{\}\)"
    replacement4 = r"{k: v for k, v in category_data.items() if k not in ['label', 'description', 'percentage']}"
    content, count4 = re.subn(pattern4, replacement4, content)
    replacement_count += count4
    
    # Pattern 5: material_data.get('properties', {}) - generic case
    # This might be for other uses, so be careful
    # Only replace if clearly in materialProperties context
    
    modified = content != original_content
    if modified:
        filepath.write_text(content)
    
    return modified, replacement_count


def main():
    """Main execution."""
    print("=" * 70)
    print("UPDATING TESTS FOR FLATTENED STRUCTURE")
    print("=" * 70)
    print()
    
    test_files = [
        'tests/test_data_completeness.py',
        'tests/test_category_range_compliance.py',
        'tests/test_two_category_compliance.py',
        'tests/test_property_categorizer.py',
        'tests/test_data_storage_policy.py',
    ]
    
    total_modified = 0
    total_replacements = 0
    
    for filepath_str in test_files:
        filepath = Path(filepath_str)
        if not filepath.exists():
            print(f"⚠️  Skipped: {filepath} (not found)")
            continue
        
        modified, count = update_test_file(filepath)
        if modified:
            print(f"✅ Updated: {filepath} ({count} replacements)")
            total_modified += 1
            total_replacements += count
        else:
            print(f"⏭️  Skipped: {filepath} (no changes needed)")
    
    print()
    print("=" * 70)
    print(f"✅ Updated {total_modified}/{len(test_files)} test files")
    print(f"📊 Total replacements: {total_replacements}")
    print("=" * 70)
    print()
    print("Next: Run tests to verify:")
    print("  python3 -m pytest tests/ -v")


if __name__ == "__main__":
    main()
