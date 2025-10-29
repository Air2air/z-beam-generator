#!/usr/bin/env python3
"""
Export 4 materials to frontmatter (one per author).
"""

import yaml
from pathlib import Path

# Materials to export
MATERIALS_TO_EXPORT = ['Alabaster', 'Aluminum', 'Bamboo', 'Breccia']

print("╔════════════════════════════════════════════════════════════════════╗")
print("║         EXPORT 4 MATERIALS TO FRONTMATTER                          ║")
print("╚════════════════════════════════════════════════════════════════════╝")
print()

# Load Materials.yaml
with open('data/Materials.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Create output directory
output_dir = Path('content/materials')
output_dir.mkdir(parents=True, exist_ok=True)

export_results = []

for material_name in MATERIALS_TO_EXPORT:
    if material_name not in data['materials']:
        print(f"⚠️  {material_name}: Not found in Materials.yaml")
        continue
    
    material = data['materials'][material_name]
    author = material.get('author', {})
    
    print(f"📦 {material_name}")
    print(f"   Author: {author.get('name', 'Unknown')} ({author.get('country', 'Unknown')})")
    
    # Create frontmatter structure
    frontmatter = {
        'author': author
    }
    
    # Add FAQ
    if 'faq' in material:
        frontmatter['faq'] = material['faq']
        faq_count = len(material['faq'].get('questions', []))
        print(f"   ✅ FAQ: {faq_count} questions")
    else:
        print(f"   ❌ FAQ: Not found")
    
    # Add Caption
    if 'caption' in material:
        frontmatter['caption'] = material['caption']
        before_words = len(material['caption'].get('before', '').split())
        after_words = len(material['caption'].get('after', '').split())
        print(f"   ✅ Caption: {before_words}w before, {after_words}w after")
    else:
        print(f"   ❌ Caption: Not found")
    
    # Add Subtitle
    if 'subtitle' in material:
        frontmatter['subtitle'] = material['subtitle']
        # Handle both string and dict formats
        if isinstance(material['subtitle'], dict):
            subtitle_text = material['subtitle'].get('text', '')
        else:
            subtitle_text = material['subtitle']
        subtitle_words = len(subtitle_text.split())
        print(f"   ✅ Subtitle: {subtitle_words}w")
    else:
        print("   ❌ Subtitle: Not found")
    
    # Write to file
    filename = f"{material_name.lower().replace(' ', '-')}.md"
    output_path = output_dir / filename
    
    with open(output_path, 'w') as f:
        f.write('---\n')
        yaml.dump(frontmatter, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        f.write('---\n')
    
    file_size = output_path.stat().st_size
    print(f"   💾 Exported: {filename} ({file_size/1024:.1f}KB)")
    
    export_results.append({
        'material': material_name,
        'author': author.get('name', 'Unknown'),
        'country': author.get('country', 'Unknown'),
        'filename': filename,
        'size_kb': file_size / 1024
    })
    
    print()

print("=" * 70)
print()
print("✨ Export Complete!")
print()
print("📊 SUMMARY:")
print()
print(f"{'Material':<12} {'Author':<20} {'Country':<12} {'File':<20} {'Size':<8}")
print("-" * 72)
for result in export_results:
    print(f"{result['material']:<12} {result['author']:<20} {result['country']:<12} "
          f"{result['filename']:<20} {result['size_kb']:.1f}KB")

print()
print(f"📁 Output directory: {output_dir}")
print(f"📄 Files created: {len(export_results)}")
