#!/usr/bin/env python3
"""
One-Command Material Addition System
Usage: python3 scripts/add_material.py "Material Name" category subcategory [author_id]

Examples:
    python3 scripts/add_material.py "Hafnium" metal refractory 1
    python3 scripts/add_material.py "Silicon Carbide" ceramic technical 2
    python3 scripts/add_material.py "Neodymium" rare-earth lanthanide 3
"""

import sys
import os
import yaml

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.tools.universal_material_template import UniversalMaterialTemplate

def add_material_with_generation(material_name: str, category: str, subcategory: str, author_id: int = 1):
    """
    Complete material addition with immediate frontmatter generation.
    """
    
    print(f"🚀 Adding {material_name} to Z-Beam Generator...")
    print(f"   Category: {category}")
    print(f"   Subcategory: {subcategory}")
    print(f"   Author ID: {author_id}")
    print()
    
    # Step 1: Add to Materials.yaml
    print("📝 Step 1: Adding to Materials.yaml...")
    template_generator = UniversalMaterialTemplate()
    
    try:
        # Load existing materials
        materials_file = "data/Materials.yaml"
        with open(materials_file, 'r', encoding='utf-8') as f:
            materials_data = yaml.safe_load(f)
        
        # Create comprehensive template
        material_template = template_generator.create_material_template(
            material_name, category, subcategory, author_id
        )
        
        # Add to materials
        if 'metadata' not in materials_data:
            materials_data['metadata'] = {}
        
        materials_data['metadata'][material_name] = material_template
        
        # Update material index
        if 'material_index' not in materials_data:
            materials_data['material_index'] = {}
        
        materials_data['material_index'][material_name] = category
        
        # Save updated materials
        with open(materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"   ✅ Added {material_name} to Materials.yaml")
        
    except Exception as e:
        print(f"   ❌ Error adding to Materials.yaml: {e}")
        return False
    
    # Step 2: Update Categories.yaml if needed
    print("📝 Step 2: Checking Categories.yaml...")
    try:
        categories_file = "data/Categories.yaml"
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories_data = yaml.safe_load(f)
        
        # Check if category exists
        if category not in categories_data:
            print(f"   ⚠️  Category '{category}' not found in Categories.yaml")
            print("   📝 You may need to add this category manually")
        else:
            print(f"   ✅ Category '{category}' exists in Categories.yaml")
            
    except Exception as e:
        print(f"   ❌ Error checking Categories.yaml: {e}")
    
    # Step 3: Generate frontend content
    print("📝 Step 3: Generating frontmatter content...")
    
    try:
        import subprocess
        result = subprocess.run([
            'python3', 'run.py', '--material', material_name
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print(f"   ✅ Generated frontmatter for {material_name}")
            print("   📄 Check content/frontmatter/ for new files")
        else:
            print("   ⚠️  Frontmatter generation had issues:")
            print(f"   {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Error generating frontmatter: {e}")
    
    # Step 4: Validation
    print("📝 Step 4: Running validation...")
    
    try:
        # Check file existence
        frontmatter_path = f"content/frontmatter/{material_name.lower().replace(' ', '-')}.md"
        if os.path.exists(frontmatter_path):
            with open(frontmatter_path, 'r') as f:
                content = f.read()
                line_count = len(content.split('\n'))
                print(f"   ✅ Frontmatter file created: {line_count} lines")
        else:
            print(f"   ⚠️  Frontmatter file not found at {frontmatter_path}")
            
    except Exception as e:
        print(f"   ❌ Error in validation: {e}")
    
    print()
    print("🎯 Material addition complete!")
    print(f"   🔬 Material: {material_name}")
    print("   📊 Database: Updated with comprehensive properties")
    print("   📄 Content: Ready for laser cleaning documentation")
    print()
    print("Next steps:")
    print("   • Review generated frontmatter content")
    print("   • Customize properties if needed in Materials.yaml")
    print("   • Generate additional content types with run.py")
    
    return True

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 scripts/add_material.py \"Material Name\" category subcategory [author_id]")
        print()
        print("Examples:")
        print("  python3 scripts/add_material.py \"Hafnium\" metal refractory 1")
        print("  python3 scripts/add_material.py \"Silicon Carbide\" ceramic technical 2")
        print("  python3 scripts/add_material.py \"Neodymium\" rare-earth lanthanide 3")
        print()
        print("Available categories: metal, ceramic, polymer, composite, rare-earth")
        print("Author IDs: 1=Taiwan, 2=Italy, 3=Indonesia, 4=USA")
        sys.exit(1)
    
    material_name = sys.argv[1]
    category = sys.argv[2]
    subcategory = sys.argv[3]
    author_id = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    
    success = add_material_with_generation(material_name, category, subcategory, author_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()