#!/usr/bin/env python3
"""
Fix field ordering in Settings.yaml to comply with BACKEND_FRONTMATTER_FIELD_ORDER_JAN6_2026.md

CRITICAL ISSUE: category and subcategory appear at lines 300+ instead of lines 4-5,
causing 404 routing errors in frontend.

FIELD ORDER REQUIRED:
Section 1: Core Identity (Lines 1-10)
- id, name, displayName, category, subcategory, hazard_class
- datePublished, dateModified, contentType, schemaVersion

Section 2: Navigation & SEO (Lines 11-30)
- fullPath, breadcrumb, pageTitle, pageDescription, metaDescription

Section 3: Technical Properties (Lines 31+)
- machine_settings, relatedMaterial, etc.

Section 4: Content Fields (After technical)
- component_summary, etc.

Section 5: Media Assets (After content)
- images

Section 6: Relationships (After images)
- relationships

Section 7: Complex Objects (End)
- author, card
"""

import yaml
from pathlib import Path
from collections import OrderedDict
import shutil
from datetime import datetime


# Field ordering per BACKEND_FRONTMATTER_FIELD_ORDER_JAN6_2026.md
FIELD_ORDER = [
    # Priority 1: Critical routing (MUST be first 10 lines)
    'id',
    'name',
    'displayName',
    'category',
    'subcategory',
    'hazard_class',
    'datePublished',
    'dateModified',
    'contentType',
    'schemaVersion',
    
    # Priority 2: Navigation & SEO (Lines 11-30)
    'fullPath',
    'breadcrumb',
    'pageTitle',
    'pageDescription',
    'metaDescription',
    
    # Priority 3: Technical Properties
    'relatedMaterial',
    'machine_settings',
    'power_range',
    'frequency_range',
    'pulse_duration',
    'spot_size',
    
    # Priority 4: Content Fields
    'component_summary',
    'micro',
    'description',
    'subtitle',
    
    # Priority 5: Media Assets
    'images',
    
    # Priority 6: Relationships
    'relationships',
    
    # Priority 7: Complex Objects (End)
    'author',
    'card',
]


def reorder_fields(data: dict) -> OrderedDict:
    """Reorder fields according to FIELD_ORDER."""
    ordered = OrderedDict()
    
    # Add fields in specified order
    for key in FIELD_ORDER:
        if key in data:
            ordered[key] = data[key]
    
    # Add any remaining fields not in FIELD_ORDER (at end)
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value
    
    return ordered


def fix_settings_field_order():
    """Fix field ordering in Settings.yaml source data."""
    settings_file = Path('data/settings/Settings.yaml')
    
    if not settings_file.exists():
        print(f"❌ ERROR: {settings_file} not found")
        return False
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = settings_file.with_suffix(f'.backup-field-order-{timestamp}.yaml')
    shutil.copy(settings_file, backup_file)
    print(f"✅ Created backup: {backup_file.name}")
    
    # Load settings
    print(f"📖 Loading {settings_file}...")
    with open(settings_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if 'settings' not in data:
        print("❌ ERROR: 'settings' key not found in data")
        return False
    
    total_settings = len(data['settings'])
    print(f"📊 Found {total_settings} settings entries")
    
    # Fix field order for each setting
    fixed_count = 0
    for setting_id, setting_data in data['settings'].items():
        # Check if category/subcategory exist and are out of order
        if 'category' in setting_data or 'subcategory' in setting_data:
            # Get original key order
            original_keys = list(setting_data.keys())
            
            # Reorder fields
            ordered_data = reorder_fields(setting_data)
            
            # Replace with ordered version
            data['settings'][setting_id] = dict(ordered_data)
            
            # Check if order actually changed
            new_keys = list(ordered_data.keys())
            if original_keys != new_keys:
                fixed_count += 1
                
                # Show first few entries as examples
                if fixed_count <= 3:
                    print(f"\n📝 Example: {setting_id}")
                    print(f"   Original order (first 5): {original_keys[:5]}")
                    print(f"   New order (first 5): {new_keys[:5]}")
    
    # Save reordered data
    print(f"\n💾 Saving reordered data to {settings_file}...")
    with open(settings_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, 
                  default_flow_style=False,
                  allow_unicode=True,
                  sort_keys=False,  # CRITICAL: Preserve our ordering!
                  width=1000,
                  indent=2)
    
    print(f"\n✅ COMPLETE: Fixed field order for {fixed_count}/{total_settings} settings")
    print(f"✅ category/subcategory now in first 10 lines (after id, name)")
    print(f"✅ Backup saved: {backup_file.name}")
    
    return True


if __name__ == '__main__':
    print("=" * 80)
    print("FIX SETTINGS FIELD ORDER")
    print("=" * 80)
    print("\nCOMPLIANCE: docs/BACKEND_FRONTMATTER_FIELD_ORDER_JAN6_2026.md")
    print("\nCRITICAL ISSUE:")
    print("- category/subcategory at line 300+ instead of line 4-5")
    print("- Causes 404 routing errors in frontend")
    print("- Must fix in SOURCE DATA (Settings.yaml)")
    print()
    
    success = fix_settings_field_order()
    
    if success:
        print("\n" + "=" * 80)
        print("✅ Settings.yaml field order FIXED")
        print("=" * 80)
        print("\nNEXT STEPS:")
        print("1. Re-export settings domain:")
        print("   python3 run.py --export --domain settings")
        print("\n2. Verify frontmatter has correct field order")
        print("\n3. Test routing (no more 404 errors)")
    else:
        print("\n" + "=" * 80)
        print("❌ FAILED to fix field order")
        print("=" * 80)
