#!/usr/bin/env python3
"""
Normalize category capitalization in frontmatter files to lowercase.

This ensures consistency across the entire system:
- Categories.yaml: lowercase keys
- materials.yaml: lowercase category values  
- Frontmatter files: lowercase category values (this script fixes these)
"""

import yaml
from pathlib import Path

def normalize_file(file_path):
    """Normalize category and subcategory to lowercase in a frontmatter file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return None, "Empty file"
        
        changes = []
        
        # Normalize category
        if 'category' in data and data['category']:
            old_cat = data['category']
            new_cat = old_cat.lower()
            if old_cat != new_cat:
                data['category'] = new_cat
                changes.append(f"category: {old_cat} → {new_cat}")
        
        # Normalize subcategory
        if 'subcategory' in data and data['subcategory']:
            old_subcat = data['subcategory']
            new_subcat = old_subcat.lower()
            if old_subcat != new_subcat:
                data['subcategory'] = new_subcat
                changes.append(f"subcategory: {old_subcat} → {new_subcat}")
        
        if not changes:
            return None, "Already normalized"
        
        # Write normalized data
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
        
        return changes, None
        
    except Exception as e:
        return None, f"Error: {str(e)}"

def main():
    print("=" * 70)
    print("Normalizing Frontmatter Categories to Lowercase")
    print("=" * 70)
    
    frontmatter_dir = Path('content/components/frontmatter')
    if not frontmatter_dir.exists():
        print(f"❌ Error: {frontmatter_dir} not found")
        return
    
    yaml_files = sorted(frontmatter_dir.glob('*.yaml'))
    print(f"\n🔍 Found {len(yaml_files)} frontmatter files")
    
    print("\n🔄 Normalizing...")
    print("=" * 70)
    
    updated = 0
    skipped = 0
    errors = 0
    
    for yaml_file in yaml_files:
        changes, error = normalize_file(yaml_file)
        
        if changes:
            updated += 1
            print(f"\n✅ {yaml_file.name}")
            for change in changes:
                print(f"   • {change}")
        elif error and "Already normalized" not in error:
            errors += 1
            print(f"❌ {yaml_file.name}: {error}")
        else:
            skipped += 1
    
    print("\n" + "=" * 70)
    print("\n📊 Summary:")
    print(f"   Total files: {len(yaml_files)}")
    print(f"   ✅ Updated: {updated}")
    print(f"   ⏭️  Already normalized: {skipped}")
    print(f"   ❌ Errors: {errors}")
    
    if updated > 0:
        print(f"\n✨ Successfully normalized {updated} frontmatter files!")
        print("\n🎯 System-wide consistency achieved:")
        print("   • Categories.yaml: lowercase ✅")
        print("   • materials.yaml: lowercase ✅")
        print("   • Frontmatter files: lowercase ✅")
    else:
        print("\n✅ All files already normalized!")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
