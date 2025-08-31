#!/usr/bin/env python3
"""
Metatags Calculator Test Suite
Tests comprehensive meta tag generation and validates best practice standards.
"""

import sys
import time
from pathlib import Path
import yaml

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.metatags.calculator import (
    generate_yaml_metatags_for_material,
    MetatagsCalculator
)

def test_comprehensive_meta_generation():
    """Test 1: Comprehensive meta tag generation"""
    print("🧪 TEST 1: Comprehensive Meta Tag Generation")
    print("=" * 50)
    
    frontmatter_file = 'content/components/frontmatter/aluminum-laser-cleaning.md'
    
    try:
        yaml_content = generate_yaml_metatags_for_material(frontmatter_file)
        
        # Parse YAML to validate structure
        content_lines = yaml_content.strip().split('\n')
        if content_lines[0] == '---' and content_lines[-1] == '---':
            yaml_data = yaml.safe_load('\n'.join(content_lines[1:-1]))
        else:
            yaml_data = yaml.safe_load(yaml_content)
        
        # Validate core structure
        required_fields = ['title', 'meta_tags', 'opengraph', 'twitter']
        for field in required_fields:
            assert field in yaml_data, f"Missing required field: {field}"
        
        # Validate meta tags count
        meta_tags = yaml_data['meta_tags']
        assert len(meta_tags) >= 10, f"Expected 10+ meta tags, got {len(meta_tags)}"
        
        # Validate OpenGraph completeness
        opengraph = yaml_data['opengraph']
        assert len(opengraph) >= 10, f"Expected 10+ OpenGraph properties, got {len(opengraph)}"
        
        # Validate Twitter cards
        twitter = yaml_data['twitter']
        assert len(twitter) >= 5, f"Expected 5+ Twitter properties, got {len(twitter)}"
        
        print("✅ YAML structure valid")
        print(f"✅ Meta tags count: {len(meta_tags)}")
        print(f"✅ OpenGraph properties: {len(opengraph)}")
        print(f"✅ Twitter card properties: {len(twitter)}")
        print(f"✅ Total character count: {len(yaml_content)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_seo_optimization():
    """Test 2: SEO optimization features"""
    print("\n🧪 TEST 2: SEO Optimization Features")
    print("=" * 50)
    
    try:
        # Test with sample data
        sample_data = {
            "subject": "Steel",
            "category": "metal",
            "author": "Dr. Test Engineer",
            "properties": {"density": "7.8 g/cm³"},
            "technicalSpecifications": {"wavelength": "1064nm"}
        }
        
        calculator = MetatagsCalculator(sample_data)
        
        # Test title optimization
        title = calculator.calculate_meta_title()
        assert 45 <= len(title) <= 65, f"Title length {len(title)} not optimal (45-65 chars)"
        
        # Test description optimization  
        description = calculator.calculate_meta_description()
        assert 120 <= len(description) <= 165, f"Description length {len(description)} not optimal (120-165 chars)"
        
        # Test keyword generation
        keywords = calculator.generate_seo_keywords()
        assert len(keywords) >= 10, f"Expected 10+ keywords, got {len(keywords)}"
        assert 'steel' in [k.lower() for k in keywords], "Material name missing from keywords"
        
        # Test technical data integration
        assert "7.8 g/cm³" in description, "Density not integrated in description"
        assert "1064nm" in description, "Wavelength not integrated in description"
        
        print(f"✅ Title length: {len(title)} chars (optimal)")
        print(f"✅ Description length: {len(description)} chars (optimal)")
        print(f"✅ Keywords generated: {len(keywords)}")
        print("✅ Technical data integrated")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_social_media_optimization():
    """Test 3: Social media optimization"""
    print("\n🧪 TEST 3: Social Media Optimization")
    print("=" * 50)
    
    try:
        sample_data = {
            "subject": "Titanium",
            "category": "metal",
            "author": "Dr. Expert"
        }
        
        calculator = MetatagsCalculator(sample_data)
        
        # Test OpenGraph generation
        og_data = calculator.generate_opengraph_data()
        required_og_props = ['og:title', 'og:description', 'og:image', 'og:type']
        og_props = [item['property'] for item in og_data]
        
        for prop in required_og_props:
            assert prop in og_props, f"Missing OpenGraph property: {prop}"
        
        # Test Twitter card generation
        twitter_data = calculator.generate_twitter_card_data()
        required_twitter = ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']
        twitter_names = [item['name'] for item in twitter_data]
        
        for name in required_twitter:
            assert name in twitter_names, f"Missing Twitter card property: {name}"
        
        # Test image optimization
        og_image_items = [item for item in og_data if item['property'] == 'og:image:width']
        assert len(og_image_items) > 0, "Missing image width specification"
        
        print(f"✅ OpenGraph properties: {len(og_data)}")
        print(f"✅ Twitter card properties: {len(twitter_data)}")
        print("✅ Image optimization included")
        print("✅ Required properties present")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_technical_precision():
    """Test 4: Technical precision and data integration"""
    print("\n🧪 TEST 4: Technical Precision")
    print("=" * 50)
    
    try:
        sample_data = {
            "subject": "Aluminum",
            "category": "metal",
            "properties": {"density": "2.7 g/cm³"},
            "technicalSpecifications": {"wavelength": "1064nm"},
            "applications": [
                {"industry": "aerospace", "detail": "aircraft cleaning"}
            ]
        }
        
        calculator = MetatagsCalculator(sample_data)
        
        # Test density extraction
        density = calculator._extract_density()
        assert density == "2.7 g/cm³", f"Expected '2.7 g/cm³', got '{density}'"
        
        # Test wavelength extraction
        wavelength = calculator._extract_wavelength()
        assert "1064nm" in wavelength, f"Expected wavelength containing '1064nm', got '{wavelength}'"
        
        # Test application integration
        applications = calculator._extract_primary_applications()
        assert "aerospace" in applications.lower(), f"Expected aerospace application, got '{applications}'"
        
        # Test complete integration
        complete_data = calculator.generate_complete_metatags()
        meta_tags = complete_data['meta_tags']
        
        # Find density and wavelength in meta tags
        density_found = any("2.7 g/cm³" in tag.get('content', '') for tag in meta_tags)
        wavelength_found = any("1064nm" in tag.get('content', '') for tag in meta_tags)
        
        assert density_found, "Density not found in meta tags"
        assert wavelength_found, "Wavelength not found in meta tags"
        
        print(f"✅ Density extraction: {density}")
        print(f"✅ Wavelength extraction: {wavelength}")
        print(f"✅ Application integration: {applications}")
        print("✅ Complete data integration verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_best_practice_compliance():
    """Test 5: Best practice standards compliance"""
    print("\n🧪 TEST 5: Best Practice Standards Compliance")
    print("=" * 50)
    
    frontmatter_file = 'content/components/frontmatter/aluminum-laser-cleaning.md'
    
    try:
        yaml_content = generate_yaml_metatags_for_material(frontmatter_file)
        
        # Parse the generated content
        content_lines = yaml_content.strip().split('\n')
        yaml_data = yaml.safe_load('\n'.join(content_lines[1:-1]))
        
        # Check advanced robots directives
        meta_tags = yaml_data['meta_tags']
        robots_tag = next((tag for tag in meta_tags if tag['name'] == 'robots'), None)
        assert robots_tag is not None, "Robots meta tag missing"
        assert "max-snippet:-1" in robots_tag['content'], "Advanced robots directive missing"
        
        # Check theme and color scheme support
        theme_tag = next((tag for tag in meta_tags if tag['name'] == 'theme-color'), None)
        color_scheme_tag = next((tag for tag in meta_tags if tag['name'] == 'color-scheme'), None)
        assert theme_tag is not None, "Theme color missing"
        assert color_scheme_tag is not None, "Color scheme support missing"
        
        # Check technical metadata
        material_density = next((tag for tag in meta_tags if tag['name'] == 'material:density'), None)
        laser_wavelength = next((tag for tag in meta_tags if tag['name'] == 'laser:wavelength'), None)
        assert material_density is not None, "Material density metadata missing"
        assert laser_wavelength is not None, "Laser wavelength metadata missing"
        
        # Check canonical URL structure
        canonical = yaml_data.get('canonical', '')
        assert canonical.startswith('https://z-beam.com/') and canonical.endswith('-laser-cleaning'), "Canonical URL structure incorrect"
        
        print("✅ Advanced robots directives present")
        print("✅ Theme and color scheme support")
        print("✅ Technical metadata included")
        print("✅ Canonical URL structure correct")
        print("✅ Modern SEO standards compliant")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def run_performance_comparison():
    """Performance comparison with previous version"""
    print("\n⚡ PERFORMANCE COMPARISON")
    print("=" * 50)
    
    frontmatter_file = 'content/components/frontmatter/aluminum-laser-cleaning.md'
    
    # Time the comprehensive generation
    start = time.time()
    yaml_result = generate_yaml_metatags_for_material(frontmatter_file)
    generation_time = time.time() - start
    
    # Count features
    yaml_data = yaml.safe_load(yaml_result.split('---')[1])
    feature_count = (
        len(yaml_data.get('meta_tags', [])) +
        len(yaml_data.get('opengraph', [])) +
        len(yaml_data.get('twitter', []))
    )
    
    print(f"📊 Generation time: {generation_time:.4f}s")
    print(f"📊 Total features: {feature_count}")
    print(f"📊 Character count: {len(yaml_result)}")
    print(f"📊 Features per second: {feature_count/generation_time:.1f}")

def main():
    """Run all tests"""
    print("🚀 METATAGS CALCULATOR TEST SUITE")
    print("=" * 60)
    print("📅 Test Date: August 30, 2025")
    print("🎯 Testing: Comprehensive best practice standards")
    
    # Run all tests
    tests = [
        test_comprehensive_meta_generation,
        test_seo_optimization,
        test_social_media_optimization,
        test_technical_precision,
        test_best_practice_compliance
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Performance comparison
    run_performance_comparison()
    
    # Summary
    print("\n📈 TEST SUMMARY")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"✅ Tests passed: {passed}/{total}")
    print(f"📊 Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Metatags calculator meets best practice standards.")
    else:
        print("⚠️ Some tests failed. Please review the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
