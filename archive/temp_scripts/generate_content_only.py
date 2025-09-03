#!/usr/bin/env python3
"""
Generate content for just the 5 specific files we need
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up API key environment variable
import api.env_loader

# Import the content generator
from components.content.generators.fail_fast_generator import FailFastContentGenerator

def generate_single_content(material_name, file_suffix):
    """Generate content for a single material"""
    print(f"\n🔧 Generating content for {material_name}...")
    
    # Create generator
    generator = FailFastContentGenerator()
    
    # Create basic material data structure
    material_data = {
        "name": material_name,
        "slug": f"{file_suffix}-laser-cleaning",
        "data": {
            "formula": f"{material_name}_formula",  # Basic placeholder
            "properties": {}
        }
    }
    
    try:
        # Generate content
        result = generator.generate(material_name, material_data)
        
        if result.success:
            print(f"✅ Successfully generated {len(result.content)} characters")
            
            # Save to file
            output_path = f"content/components/content/{file_suffix}-laser-cleaning.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.content)
            print(f"✅ Saved to {output_path}")
        else:
            print(f"❌ Failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def main():
    """Generate all 5 content files"""
    materials = [
        ("Silicon", "silicon"),
        ("Stoneware", "stoneware"), 
        ("Alumina", "alumina"),
        ("Zirconia", "zirconia"),
        ("Silicon Nitride", "silicon-nitride")
    ]
    
    for material_name, file_suffix in materials:
        generate_single_content(material_name, file_suffix)

if __name__ == "__main__":
    main()
