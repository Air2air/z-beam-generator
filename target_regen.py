#!/usr/bin/env python3
"""
Targeted regeneration for just the 5 content files
"""
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Add project root to Python path  
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after path setup
from components.component_generator_factory import ComponentGeneratorFactory
from z_beam_generator import DynamicSchemaGenerator

def main():
    """Generate content for just the 5 files we want"""
    print("🔧 Regenerating 5 content files...")
    
    # Initialize the dynamic generator
    generator = DynamicSchemaGenerator()
    materials_data = generator.load_materials()
    
    # Materials we want to regenerate
    target_materials = ["alumina", "silicon_nitride", "stoneware", "zirconia", "silicon"]
    
    # Find the materials in the data
    for material_data in materials_data:
        material_name = material_data.get('name', '').lower().replace(' ', '_')
        material_slug = material_data.get('slug', '').lower().replace('-', '_')
        
        # Check if this is one of our target materials
        is_target = False
        for target in target_materials:
            if target in [material_name, material_slug] or material_name == target or material_slug == target:
                is_target = True
                break
        
        if not is_target:
            continue
            
        print(f"\n🔧 Processing {material_data.get('name')}...")
        
        try:
            # Create content generator
            content_generator = ComponentGeneratorFactory.create_generator("content")
            
            # Generate content
            result = content_generator.generate(material_data)
            
            if result.success:
                print(f"✅ Content generated: {len(result.content)} characters")
            else:
                print(f"❌ Content failed: {result.error}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
