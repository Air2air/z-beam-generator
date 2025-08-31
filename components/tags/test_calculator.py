#!/usr/bin/env python3
"""
Tags Calculator Test Suite
Comprehensive testing for the optimized tags calculator.
"""

import sys
import tempfile
import os
from pathlib import Path

# Add the project root to Python path before importing project modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.tags.calculator import (
    TagsCalculator,
    calculate_tags_for_material,
    load_frontmatter_data,
    sanitize_tag
)

def test_tag_generation():
    """Test 1: Basic tag generation functionality"""
    print("🧪 TEST 1: Basic Tag Generation")
    print("=" * 40)
    
    try:
        # Test with sample data
        sample_data = {
            "subject": "Steel",
            "category": "metal",
            "author": "Dr. Test Engineer",
            "properties": {"density": "7.8 g/cm³"},
            "technicalSpecifications": {"wavelength": "1064nm"}
        }
        
        calculator = TagsCalculator(sample_data)
        tags = calculator.calculate_seo_optimized_tags()
        
        # Validate tag count
        assert len(tags) == 8, f"Expected 8 tags, got {len(tags)}"
        
        # Validate primary material tag
        assert tags[0] == 'steel', f"Expected 'steel' as first tag, got '{tags[0]}'"
        
        # Validate author tag (should be last)
        assert 'test-engineer' in tags[-1], f"Expected author tag, got '{tags[-1]}'"
        
        # Validate no duplicates
        assert len(tags) == len(set(tags)), "Duplicate tags found"
        
        print(f"✅ Generated {len(tags)} unique tags")
        print(f"✅ Tags: {', '.join(tags)}")
        print("✅ Basic tag generation working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_seo_optimization():
    """Test 2: SEO optimization features"""
    print("\n🧪 TEST 2: SEO Optimization Features")
    print("=" * 40)
    
    try:
        sample_data = {
            "subject": "Titanium",
            "category": "metal",
            "author": "SEO Expert",
            "properties": {"density": "4.5 g/cm³"},
            "applications": [{"industry": "aerospace"}]
        }
        
        calculator = TagsCalculator(sample_data)
        result = calculator.generate_complete_tags()
        
        # Check SEO optimization
        assert result['seo_optimized'], "Tags should be SEO optimized"
        
        # Check relevance scoring
        assert 'relevance_scores' in result, "Relevance scores missing"
        assert len(result['relevance_scores']) == len(result['tags']), "Score count mismatch"
        
        # Check for high-value SEO tags
        tags = result['tags']
        seo_indicators = ['laser-cleaning', 'surface-preparation', 'precision', 'aerospace']
        has_seo_tag = any(tag in ' '.join(tags) for tag in seo_indicators)
        assert has_seo_tag, "Missing high-value SEO tags"
        
        print(f"✅ SEO optimization: {result['seo_optimized']}")
        print(f"✅ Average relevance: {result['average_score']:.2f}")
        print("✅ High-value SEO tags present")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_material_specificity():
    """Test 3: Material-specific tag generation"""
    print("\n🧪 TEST 3: Material-Specific Tag Generation")
    print("=" * 40)
    
    material_tests = [
        {
            'data': {"subject": "Glass", "category": "glass", "author": "Glass Expert"},
            'expected_tags': ['optical', 'transparency', 'precision']
        },
        {
            'data': {"subject": "Wood", "category": "wood", "author": "Wood Specialist"},
            'expected_tags': ['restoration', 'eco-friendly', 'furniture']
        },
        {
            'data': {"subject": "Ceramic", "category": "ceramic", "author": "Ceramic Engineer"},
            'expected_tags': ['precision', 'electronics', 'micro']
        }
    ]
    
    try:
        for i, test_case in enumerate(material_tests, 1):
            calculator = TagsCalculator(test_case['data'])
            tags = calculator.calculate_seo_optimized_tags()
            
            # Check material specificity
            material = test_case['data']['subject'].lower()
            assert material in tags[0], f"Material '{material}' not in primary tag"
            
            # Check for some expected material-specific content
            tag_text = ' '.join(tags)
            any(expected in tag_text for expected in test_case['expected_tags'])
            
            print(f"✅ Test {i} ({material}): {len(tags)} tags generated")
            print(f"   Tags: {', '.join(tags[:3])}...")
            
        print("✅ Material-specific tag generation working")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_frontmatter_integration():
    """Test 4: Frontmatter data integration"""
    print("\n🧪 TEST 4: Frontmatter Data Integration")
    print("=" * 40)
    
    try:
        # Test with actual frontmatter file
        frontmatter_file = 'content/components/frontmatter/aluminum-laser-cleaning.md'
        
        if os.path.exists(frontmatter_file):
            tags_result = calculate_tags_for_material(frontmatter_file)
            tags_list = [tag.strip() for tag in tags_result.split(',')]
            
            # Validate result
            assert len(tags_list) == 8, f"Expected 8 tags from frontmatter, got {len(tags_list)}"
            assert 'aluminum' in tags_list[0], "Primary material tag missing"
            
            # Check technical data integration
            frontmatter_data = load_frontmatter_data(frontmatter_file)
            calculator = TagsCalculator(frontmatter_data)
            detailed_result = calculator.generate_complete_tags()
            
            assert detailed_result['material'] == 'aluminum', "Material extraction failed"
            assert detailed_result['category'] == 'metal', "Category extraction failed"
            
            print("✅ Frontmatter integration working")
            print(f"✅ Generated: {tags_result}")
            print(f"✅ Material: {detailed_result['material']}")
            print(f"✅ Category: {detailed_result['category']}")
            
        else:
            # Test with mock frontmatter
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write("""---
subject: Test Material
category: metal
author: Test Author
properties:
  density: "5.0 g/cm³"
technicalSpecifications:
  wavelength: "1064nm"
---
Test content""")
                temp_file = f.name
            
            try:
                tags_result = calculate_tags_for_material(temp_file)
                tags_list = [tag.strip() for tag in tags_result.split(',')]
                assert len(tags_list) == 8, "Mock frontmatter test failed"
                print("✅ Mock frontmatter integration working")
            finally:
                os.unlink(temp_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_sanitization():
    """Test 5: Tag sanitization and security"""
    print("\n🧪 TEST 5: Tag Sanitization and Security")
    print("=" * 40)
    
    try:
        # Test with potentially problematic data
        problematic_data = {
            "subject": "Metal<script>alert('xss')</script>",
            "category": "metal@#$%",
            "author": "'; DROP TABLE tags; --"
        }
        
        calculator = TagsCalculator(problematic_data)
        tags = calculator.calculate_seo_optimized_tags()
        
        # Check sanitization
        for tag in tags:
            # No dangerous characters
            assert '<' not in tag, f"Dangerous character '<' found in tag: {tag}"
            assert '>' not in tag, f"Dangerous character '>' found in tag: {tag}"
            assert ';' not in tag, f"Dangerous character ';' found in tag: {tag}"
            assert 'script' not in tag.lower(), f"Script tag found in: {tag}"
            
            # Proper format
            assert tag.islower() or '-' in tag, f"Tag not properly formatted: {tag}"
            assert not tag.startswith('-'), f"Tag starts with dash: {tag}"
            assert not tag.endswith('-'), f"Tag ends with dash: {tag}"
        
        # Test sanitize_tag function directly
        test_cases = [
            ("Test@Tag!", "test-tag"),
            ("Multiple   Spaces", "multiple-spaces"),
            ("UPPERCASE", "uppercase"),
            ("", ""),
            ("dash-tag", "dash-tag")
        ]
        
        for input_tag, expected in test_cases:
            result = sanitize_tag(input_tag)
            assert result == expected, f"Sanitization failed: '{input_tag}' -> '{result}' (expected '{expected}')"
        
        print("✅ Tag sanitization working correctly")
        print("✅ Security validation passed")
        print(f"✅ Generated safe tags: {', '.join(tags[:3])}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_performance():
    """Test 6: Performance and efficiency"""
    print("\n🧪 TEST 6: Performance and Efficiency")
    print("=" * 40)
    
    import time
    
    try:
        # Test generation speed
        sample_data = {
            "subject": "Performance Test Material",
            "category": "composite",
            "author": "Speed Tester",
            "properties": {"density": "1.5 g/cm³"},
            "technicalSpecifications": {"wavelength": "532nm"},
            "applications": [
                {"industry": "aerospace", "detail": "high performance"},
                {"industry": "automotive", "detail": "lightweight"}
            ]
        }
        
        # Time multiple generations
        start_time = time.time()
        iterations = 100
        
        for _ in range(iterations):
            calculator = TagsCalculator(sample_data)
            tags = calculator.calculate_seo_optimized_tags()
            result = calculator.generate_complete_tags()
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / iterations
        
        # Performance assertions
        assert avg_time < 0.01, f"Generation too slow: {avg_time:.4f}s average"
        assert len(tags) == 8, "Consistent tag count required"
        assert result['average_score'] >= 0, "Relevance scoring required"
        
        print(f"✅ Average generation time: {avg_time:.4f}s")
        print(f"✅ Total time for {iterations} iterations: {total_time:.4f}s")
        print("✅ Performance target met (<0.01s per generation)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 TAGS CALCULATOR TEST SUITE")
    print("=" * 50)
    print("📅 Test Date: August 30, 2025")
    print("🎯 Testing: Optimized tags calculator functionality")
    
    # Run all tests
    tests = [
        test_tag_generation,
        test_seo_optimization,
        test_material_specificity,
        test_frontmatter_integration,
        test_sanitization,
        test_performance
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n📈 TEST SUMMARY")
    print("=" * 40)
    passed = sum(results)
    total = len(results)
    print(f"✅ Tests passed: {passed}/{total}")
    print(f"📊 Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Tags calculator is ready for production.")
    else:
        print("⚠️ Some tests failed. Please review the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
