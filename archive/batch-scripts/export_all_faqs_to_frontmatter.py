#!/usr/bin/env python3
"""
Export all FAQs from Materials.yaml to frontmatter files
"""
import yaml
from pathlib import Path
import sys

def export_all_faqs():
    print("="*80)
    print("📤 EXPORTING ALL FAQs TO FRONTMATTER")
    print("="*80)
    print()
    
    # Load Materials.yaml
    materials_path = Path("data/Materials.yaml")
    if not materials_path.exists():
        print(f"❌ File not found: {materials_path}")
        sys.exit(1)
    
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    total = len(materials)
    
    print(f"📊 Found {total} materials in Materials.yaml")
    print()
    
    # Check FAQ coverage
    with_faq = [name for name, mat in materials.items() if 'faq' in mat and mat['faq']]
    print(f"✅ Materials with FAQs: {len(with_faq)}/{total} ({len(with_faq)/total*100:.1f}%)")
    
    if len(with_faq) < total:
        print(f"⚠️  Warning: {total - len(with_faq)} materials missing FAQs")
        response = input("\nContinue export anyway? (y/N): ")
        if response.lower() != 'y':
            print("Export cancelled")
            return
    
    print()
    print("="*80)
    print("Starting export...")
    print("="*80)
    print()
    
    # Ensure frontmatter directory exists
    frontmatter_dir = Path("content/frontmatter")
    frontmatter_dir.mkdir(parents=True, exist_ok=True)
    
    exported = 0
    skipped = 0
    created = 0
    updated = 0
    
    for material_name in sorted(with_faq):
        material = materials[material_name]
        
        # Create filename
        filename = material_name.lower().replace(' ', '-') + '-laser-cleaning.yaml'
        frontmatter_path = frontmatter_dir / filename
        
        # Load existing frontmatter or create new
        if frontmatter_path.exists():
            try:
                with open(frontmatter_path, 'r', encoding='utf-8') as f:
                    frontmatter_data = yaml.safe_load(f) or {}
                action = "Updated"
                updated += 1
            except Exception as e:
                print(f"⚠️  {material_name}: Error loading existing file: {e}")
                frontmatter_data = {}
                action = "Created"
                created += 1
        else:
            frontmatter_data = {
                'title': f"{material_name} Laser Cleaning",
                'material': material_name
            }
            action = "Created"
            created += 1
        
        # Update FAQ section
        frontmatter_data['faq'] = material['faq']
        
        # Write back
        try:
            with open(frontmatter_path, 'w', encoding='utf-8') as f:
                yaml.dump(frontmatter_data, f, 
                         default_flow_style=False, 
                         allow_unicode=True, 
                         sort_keys=False,
                         width=120)
            
            faq_count = len(material['faq']) if isinstance(material['faq'], list) else 0
            print(f"✅ {action}: {material_name} ({faq_count} FAQs) → {filename}")
            exported += 1
            
        except Exception as e:
            print(f"❌ {material_name}: Export failed: {e}")
            skipped += 1
    
    print()
    print("="*80)
    print("📊 EXPORT SUMMARY")
    print("="*80)
    print(f"✅ Successfully exported: {exported}/{len(with_faq)}")
    print(f"   - Created new files: {created}")
    print(f"   - Updated existing: {updated}")
    if skipped > 0:
        print(f"⚠️  Skipped (errors): {skipped}")
    print()
    print(f"📁 Frontmatter directory: {frontmatter_dir.absolute()}")
    print("="*80)

if __name__ == "__main__":
    export_all_faqs()
