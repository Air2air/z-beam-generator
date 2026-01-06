#!/usr/bin/env python3
"""
Normalize industry_applications items to simple {id, name} format.
Fixes 21 materials that have enriched {title, description, metadata} format.

COMPLIANCE: docs/INDUSTRY_APPLICATIONS_MIGRATION_JAN5_2026.md
Run: python3 scripts/migrations/normalize_industry_applications_format.py
"""

import yaml
from pathlib import Path
import shutil
import re

def slugify(text):
    """Convert display name to slug ID."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def normalize_materials_yaml():
    """Normalize industry_applications items to {id, name} format."""
    
    source_file = Path('data/materials/Materials.yaml')
    backup_file = Path('data/materials/Materials.yaml.backup-normalize-format')
    
    # Create backup
    shutil.copy2(source_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # Load source data
    with open(source_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    normalized_count = 0
    skipped_count = 0
    
    # Process each material
    for material_name, material_data in data['materials'].items():
        if 'relationships' not in material_data:
            continue
        
        if 'operational' not in material_data['relationships']:
            continue
        
        industry_apps = material_data['relationships']['operational'].get('industry_applications')
        
        # Check if it's the relationship structure format
        if not isinstance(industry_apps, dict) or 'items' not in industry_apps:
            skipped_count += 1
            continue
        
        # Check if items have the enriched format (title, description, metadata)
        needs_normalization = False
        for item in industry_apps['items']:
            if 'title' in item or 'description' in item or 'metadata' in item:
                needs_normalization = True
                break
        
        if not needs_normalization:
            skipped_count += 1
            continue
        
        # Normalize to {id, name} format
        normalized_items = []
        for item in industry_apps['items']:
            # Extract the display name from title field
            if 'title' in item:
                name = item['title']
                # Remove common suffixes like " Manufacturing" if doubled
                name = name.replace(' Manufacturing industry applications and manufacturing requirements for laser cleaning.', '')
                # Keep the clean title
                item_id = slugify(name)
                normalized_items.append({'id': item_id, 'name': name})
            elif 'name' in item and 'id' in item:
                # Already has correct format
                normalized_items.append({'id': item['id'], 'name': item['name']})
            elif 'name' in item:
                # Has name but no id
                normalized_items.append({'id': slugify(item['name']), 'name': item['name']})
            else:
                print(f"⚠️  {material_name}: Unknown item format: {item}")
        
        if normalized_items:
            industry_apps['items'] = normalized_items
            print(f"✅ Normalized: {material_name} ({len(normalized_items)} items)")
            normalized_count += 1
    
    # Write back to source
    with open(source_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n📊 Normalization Summary:")
    print(f"   ✅ Normalized: {normalized_count} materials")
    print(f"   ⏭️  Skipped: {skipped_count} materials")
    print(f"   📁 Total: {normalized_count + skipped_count} materials")
    print(f"\n💾 Backup: {backup_file}")
    print(f"📝 Source updated: {source_file}")
    print(f"\n⚠️  NEXT STEP: Re-export materials to regenerate frontmatter")
    print(f"   Command: python3 run.py --export --domain materials")

def main():
    print("🔧 Industry Applications: Normalize Item Format")
    print("=" * 60)
    print("Converting enriched items to simple {id, name} format")
    print("Target: 21 materials with {title, description, metadata}")
    print("=" * 60)
    print()
    
    normalize_materials_yaml()
    
    print("\n✅ Normalization Complete!")

if __name__ == '__main__':
    main()
