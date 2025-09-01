#!/usr/bin/env python3
"""
Test actual content generation with formatting
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from components.content.fail_fast_generator import create_fail_fast_generator
from api.client import MockAPIClient

def test_content_generation():
    """Test content generation with full prompt and formatting integration."""
    print("🔬 TESTING CONTENT GENERATION WITH FORMATTING")
    print("="*60)
    
    # Create generator and API client
    generator = create_fail_fast_generator()
    api_client = MockAPIClient()
    
    # Test material
    material_data = {
        "name": "Stainless Steel 316L",
        "formula": "Fe-18Cr-10Ni-2Mo"
    }
    
    author_info = {
        "id": 1,
        "name": "Yi-Chun Lin", 
        "country": "Taiwan"
    }
    
    print(f"📝 Generating content for: {material_data['name']}")
    print(f"👤 Author: {author_info['name']} ({author_info['country']})")
    print(f"🧪 Formula: {material_data['formula']}")
    
    try:
        result = generator.generate(
            material_name=material_data["name"],
            material_data=material_data,
            api_client=api_client,
            author_info=author_info
        )
        
        if result.success:
            print("\n✅ GENERATION SUCCESSFUL")
            print(f"📊 Length: {len(result.content)} characters")
            print(f"🎯 Method: {result.metadata.get('generation_method', 'unknown')}")
            
            print("\n📄 GENERATED CONTENT:")
            print("-" * 60)
            print(result.content)
            print("-" * 60)
            
            # Analyze the content for formatting features
            analyze_content_features(result.content)
            
        else:
            print(f"❌ Generation failed: {result.error_message}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def analyze_content_features(content):
    """Analyze the generated content for expected formatting and persona features."""
    print("\n🔍 CONTENT ANALYSIS:")
    
    features_found = []
    
    # Check for markdown headers
    if content.count('#') > 0:
        features_found.append("✅ Markdown headers")
    else:
        features_found.append("❌ No markdown headers")
    
    # Check for bold text
    if '**' in content:
        features_found.append("✅ Bold formatting")
    else:
        features_found.append("❌ No bold formatting")
    
    # Check for formula integration
    if "Fe-18Cr-10Ni-2Mo" in content:
        features_found.append("✅ Formula integration")
    else:
        features_found.append("❌ Formula not integrated")
    
    # Check for Taiwan persona elements (systematic, methodical)
    persona_words = ["systematic", "methodical", "careful", "analysis", "step"]
    found_persona = any(word in content.lower() for word in persona_words)
    if found_persona:
        features_found.append("✅ Taiwan persona language")
    else:
        features_found.append("❌ Taiwan persona language not detected")
    
    # Check for technical content
    technical_words = ["laser", "cleaning", "wavelength", "processing", "nm"]
    found_technical = any(word in content.lower() for word in technical_words)
    if found_technical:
        features_found.append("✅ Technical content")
    else:
        features_found.append("❌ Technical content missing")
    
    # Print analysis
    for feature in features_found:
        print(f"  {feature}")
    
    # Count successful features
    successful = len([f for f in features_found if f.startswith("✅")])
    total = len(features_found)
    print(f"\n📊 Content Quality: {successful}/{total} features present ({successful/total*100:.1f}%)")

def test_multiple_authors():
    """Test content generation with different authors to see persona differences."""
    print(f"\n{'='*60}")
    print("🌍 TESTING MULTIPLE AUTHORS")
    print("-"*30)
    
    generator = create_fail_fast_generator()
    api_client = MockAPIClient()
    
    authors = [
        {"id": 1, "name": "Yi-Chun Lin", "country": "Taiwan"},
        {"id": 2, "name": "Alessandro Moretti", "country": "Italy"},
        {"id": 3, "name": "Ikmanda Roswati", "country": "Indonesia"},
        {"id": 4, "name": "Todd Dunning", "country": "United States"}
    ]
    
    material_data = {"name": "Aluminum 6061", "formula": "Al-Mg-Si"}
    
    for author in authors:
        print(f"\n👤 {author['name']} ({author['country']}):")
        
        try:
            result = generator.generate(
                material_name=material_data["name"],
                material_data=material_data,
                api_client=api_client,
                author_info=author
            )
            
            if result.success:
                print(f"  ✅ Generated {len(result.content)} chars")
                # Show first 100 chars as preview
                preview = result.content[:100].replace('\n', ' ')
                print(f"  📝 Preview: {preview}...")
            else:
                print(f"  ❌ Failed: {result.error_message}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    test_content_generation()
    test_multiple_authors()
