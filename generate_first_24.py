#!/usr/bin/env python3
"""
Generate Content for First 24 Materials
Uses the fail_fast_generator to create content for the first 24 materials with REAL API (no mocks)
"""

import sys
import yaml
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from components.content.generators.fail_fast_generator import create_fail_fast_generator
from api.client_manager import create_api_client

def load_materials():
    """Load materials from the YAML file"""
    materials_file = project_root / "data" / "materials.yaml"
    with open(materials_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # Flatten all materials from all categories
    all_materials = []
    for category_name, category_data in data['materials'].items():
        for material in category_data['items']:
            material['category_name'] = category_name
            all_materials.append(material)
    
    return all_materials

def generate_content_for_material(generator, api_client, material, author_id=1):
    """Generate content for a single material"""
    print(f"🔧 Generating content for {material['name']}...")
    
    # Map author IDs to author info
    authors = {
        1: {'id': 1, 'name': 'Dr. Li Wei', 'country': 'Taiwan'},
        2: {'id': 2, 'name': 'Dr. Marco Rossi', 'country': 'Italy'},
        3: {'id': 3, 'name': 'Dr. Sari Dewi', 'country': 'Indonesia'},
        4: {'id': 4, 'name': 'Dr. Sarah Johnson', 'country': 'United States (California)'}
    }
    
    author_info = authors.get(author_id, authors[1])
    
    # Use the material's preferred author if specified
    if 'author_id' in material:
        author_info = authors.get(material['author_id'], authors[1])
    
    # Prepare material data
    material_data = {
        'name': material['name'],
        'category': material['category_name'],
        'formula': material.get('formula', ''),
        'complexity': material.get('complexity', 'medium'),
        'applications': material.get('applications', []),
        'laser_parameters': material.get('laser_parameters', {}),
        'surface_treatments': material.get('surface_treatments', []),
        'industry_tags': material.get('industry_tags', [])
    }
    
    try:
        result = generator.generate(
            material_name=material['name'],
            material_data=material_data,
            api_client=api_client,
            author_info=author_info,
            frontmatter_data={
                'title': f'Laser Cleaning of {material["name"]}',
                'description': f'Technical analysis of {material["name"]} for laser cleaning applications',
                'category': material['category_name']
            }
        )
        
        if result.success:
            # Save the content to file
            filename = material['name'].lower().replace(' ', '-').replace('(', '').replace(')', '').replace(',', '')
            output_file = project_root / "content" / "components" / "content" / f"{filename}-laser-cleaning.md"
            
            with open(output_file, 'w') as f:
                f.write(result.content)
            
            print(f"✅ Success: Saved {len(result.content)} chars to {output_file.name}")
            
            if result.quality_score:
                print(f"   📊 Overall Score: {result.quality_score.overall_score:.1f}/100")
                print(f"   👤 Human Believability: {result.quality_score.human_believability:.1f}/100")
            
            return True
        else:
            print(f"❌ Failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def main():
    """Generate content for the first 24 materials"""
    print("🚀 GENERATING CONTENT FOR FIRST 24 MATERIALS")
    print("=" * 60)
    
    # Load materials
    materials = load_materials()
    first_24 = materials[:24]
    
    print(f"📋 Loaded {len(materials)} total materials")
    print("🎯 Generating content for first 24 materials:")
    for i, material in enumerate(first_24, 1):
        print(f"   {i:2d}. {material['name']} ({material['category_name']})")
    print()
    
    # Initialize generator with scoring enabled
    generator = create_fail_fast_generator(
        max_retries=2,
        retry_delay=1.0,
        enable_scoring=True,
        human_threshold=70.0
    )
    
    # Use real API client (no mocks) - requires GROK_API_KEY environment variable
    try:
        api_client = create_api_client('grok')
        print("✅ Real Grok API client created successfully")
    except Exception as e:
        print(f"❌ Failed to create API client: {e}")
        print("💡 Make sure GROK_API_KEY environment variable is set")
        return
    
    successful = 0
    failed = 0
    
    for i, material in enumerate(first_24, 1):
        print(f"\n📍 Material {i}/24: {material['name']}")
        print("-" * 50)
        
        success = generate_content_for_material(generator, api_client, material)
        
        if success:
            successful += 1
        else:
            failed += 1
        
        print()
    
    print("=" * 60)
    print("📊 GENERATION SUMMARY")
    print(f"✅ Successful: {successful}/24")
    print(f"❌ Failed: {failed}/24") 
    print(f"📈 Success Rate: {successful/24*100:.1f}%")
    
    if successful > 0:
        print("\n🎉 Generated content files are in: content/components/content/")

if __name__ == "__main__":
    main()
