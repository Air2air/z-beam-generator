#!/usr/bin/env python3
"""
Demo script to display AI-generated caption fields for Materials.yaml entries

NOTE: ai_text_fields is now LIMITED to caption fields only per system policy.
Other text fields are handled through the frontmatter generation pipeline.
"""

import yaml
from pathlib import Path

def load_materials():
    """Load materials data"""
    materials_path = Path("data/materials.yaml")
    with open(materials_path, 'r') as f:
        data = yaml.safe_load(f)
        # Materials are under the 'materials' key
        return data.get('materials', {})

def display_ai_text_fields(material_name):
    """Display caption fields for a material - ai_text_fields is CAPTION-ONLY"""
    materials = load_materials()
    
    if material_name not in materials:
        print(f"❌ Material '{material_name}' not found")
        return
    
    material = materials[material_name]
    ai_fields = material.get('ai_text_fields', {})
    
    if not ai_fields:
        print(f"❌ No ai_text_fields found for {material_name}")
        print(f"ℹ️  ai_text_fields is now LIMITED to caption fields only")
        return
    
    print(f"\n🎯 Caption Fields for {material_name}")
    print("=" * 60)
    print(f"ℹ️  ai_text_fields contains ONLY caption data")
    print(f"ℹ️  Other text fields use frontmatter generation pipeline")
    print("=" * 60)
    
    # Caption fields ONLY - ai_text_fields is LIMITED per system policy
    caption_fields = [
        'caption_beforeText', 'caption_afterText'
    ]
    
    # Display Caption Fields
    print("\n📋 Caption Fields (ai_text_fields):")
    print("-" * 40)
    for field in caption_fields:
        if field in ai_fields:
            data = ai_fields[field]
            content = data.get('content', 'N/A')
            word_count = data.get('word_count', 0)
            char_count = data.get('character_count', 0)
            
            # Truncate content for display
            if len(content) > 100:
                content_preview = content[:100] + "..."
            else:
                content_preview = content
            
            print(f"\n✅ {field}:")
            print(f"   Content: {content_preview}")
            print(f"   Stats: {word_count} words, {char_count} chars")
        else:
            print(f"\n❌ {field}: Not found")
    
    # Summary
    total_fields = len([f for f in ai_fields if f in caption_fields])
    print(f"\n📈 Summary: {total_fields} caption fields in ai_text_fields")
    print("ℹ️  Configuration: Caption-only ai_text_fields per system policy")
    print("ℹ️  Other text fields: Generated via frontmatter pipeline")

if __name__ == "__main__":
    display_ai_text_fields("Aluminum")