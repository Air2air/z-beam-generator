#!/usr/bin/env python3
"""
Show complete text field content for review
"""

import sys
from pathlib import Path
import yaml

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data.materials import get_material_by_name_cached

def show_complete_fields(material_name: str):
    """Show complete content of all AI-researched text fields"""
    
    print(f"📋 Complete Text Field Content for {material_name}")
    print("=" * 60)
    
    material_data = get_material_by_name_cached(material_name)
    
    if not material_data:
        print(f"❌ Material '{material_name}' not found")
        return
    
    ai_text_fields = material_data.get('ai_text_fields', {})
    
    if not ai_text_fields:
        print("ℹ️  No AI-researched text fields found")
        return
    
    # Show each field with complete content
    for field_name, field_data in ai_text_fields.items():
        print(f"\n🏷️  {field_name.upper()}")
        print("-" * 40)
        
        if isinstance(field_data, dict) and 'content' in field_data:
            content = field_data['content']
            word_count = field_data.get('word_count', len(content.split()))
            
            print(f"📝 Content ({word_count} words):")
            print(f'"{content}"')
            
            # Show metadata
            print(f"\n📊 Metadata:")
            print(f"   • Source: {field_data.get('source', 'unknown')}")
            print(f"   • Research Date: {field_data.get('research_date', 'unknown')[:10]}")
            print(f"   • Word Count: {word_count}")
            print(f"   • Character Count: {field_data.get('character_count', len(content))}")
            
        else:
            print(f"📝 Content: {field_data}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        material_name = sys.argv[1]
    else:
        material_name = "Aluminum"
    
    show_complete_fields(material_name)