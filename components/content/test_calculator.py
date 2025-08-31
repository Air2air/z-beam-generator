#!/usr/bin/env python3
"""
Content Calculator Test Suite
Comprehensive testing for the author-driven content calculator.
"""

import sys
import tempfile
import os
import yaml
from pathlib import Path

# Add the project root to Python path before importing project modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from components.content.generator import (
    ContentCalculator,
    load_frontmatter_data,
    load_authors_data,
    load_persona_prompt,
    calculate_content_for_material
)

def test_author_data_loading():
    """Test 1: Author data loading functionality"""
    print("🧪 TEST 1: Author Data Loading")
    print("=" * 40)
    
    try:
        authors = load_authors_data()
        assert len(authors) == 4, f"Expected 4 authors, got {len(authors)}"
        
        # Verify all expected authors are present
        author_ids = [author['id'] for author in authors]
        expected_ids = [1, 2, 3, 4]
        assert set(author_ids) == set(expected_ids), "Missing expected author IDs"
        
        # Verify author details
        author_names = [author['name'] for author in authors]
        expected_names = ['Yi-Chun Lin', 'Alessandro Moretti', 'Ikmanda Roswati', 'Todd Dunning']
        for name in expected_names:
            assert name in author_names, f"Missing author: {name}"
        
        print(f"✅ Loaded {len(authors)} authors successfully")
        print(f"✅ All expected authors present: {', '.join(expected_names)}")
        print("✅ Author data loading working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_content_generation_all_authors():
    """Test 2: Content generation for all 4 authors"""
    print("\n🧪 TEST 2: Content Generation for All Authors")
    print("=" * 40)
    
    try:
        frontmatter_file = 'content/components/frontmatter/aluminum-laser-cleaning.md'
        
        # Test each author
        for author_id in [1, 2, 3, 4]:
            calculator = ContentCalculator(load_frontmatter_data(frontmatter_file), author_id)
            content = calculator.calculate_content_for_material()
            
            # Basic validation
            assert len(content) > 500, f"Content too short for author {author_id}"
            assert 'aluminum' in content.lower(), f"Material missing from content for author {author_id}"
            assert '##' in content or '#' in content, f"No sections found for author {author_id}"
            
            # Author-specific validation
            author_name = calculator.author_info['name'] if calculator.author_info else 'Unknown'
            assert author_name in content, f"Author name missing for author {author_id}"
            
            word_count = len(content.split())
            print(f"   ✅ Author {author_id} ({author_name}): {word_count} words")
        
        print("✅ All 4 authors generate content successfully")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_author_persona_differences():
    """Test 3: Verify distinct author personas"""
    print("\n🧪 TEST 3: Author Persona Differences")
    print("=" * 40)
    
    try:
        frontmatter_file = 'content/components/frontmatter/aluminum-laser-cleaning.md'
        frontmatter_data = load_frontmatter_data(frontmatter_file)
        
        contents = {}
        for author_id in [1, 2, 3, 4]:
            calculator = ContentCalculator(frontmatter_data, author_id)
            content = calculator.calculate_content_for_material()
            contents[author_id] = content
        
        # Check for distinct differences
        personas = {
            1: 'Taiwan',  # Yi-Chun Lin - precise, methodical
            2: 'Italy',   # Alessandro Moretti - passionate, expressive  
            3: 'Indonesia', # Ikmanda Roswati - analytical, repetitive
            4: 'California' # Todd Dunning - conversational, optimistic
        }
        
        for author_id, country in personas.items():
            content = contents[author_id]
            assert country in content, f"Country reference missing for author {author_id}"
        
        # Check specific persona elements
        assert 'systematic' in contents[1] or 'methodical' in contents[1], "Taiwan precision missing"
        assert 'masterpiece' in contents[2] or 'artistic' in contents[2], "Italian passion missing"  
        assert 'important' in contents[3] and 'very important' in contents[3], "Indonesian repetition missing"
        assert "let's" in contents[4] or "you're" in contents[4], "USA conversational missing"
        
        print("✅ Taiwan persona: Precise and methodical language detected")
        print("✅ Italy persona: Passionate and expressive language detected")
        print("✅ Indonesia persona: Analytical and repetitive language detected")
        print("✅ USA persona: Conversational and optimistic language detected")
        print("✅ All personas show distinct characteristics")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_frontmatter_integration():
    """Test 4: Frontmatter data integration"""
    print("\n🧪 TEST 4: Frontmatter Data Integration")
    print("=" * 40)
    
    try:
        frontmatter_file = 'content/components/frontmatter/aluminum-laser-cleaning.md'
        
        # Test with real frontmatter
        calculator = ContentCalculator(load_frontmatter_data(frontmatter_file), 2)
        result = calculator.generate_complete_content()
        
        # Validate frontmatter integration
        assert result['material'] == 'Aluminum', "Material extraction failed"
        assert result['author_id'] == 2, "Author ID mismatch"
        assert result['author_name'] == 'Alessandro Moretti', "Author name extraction failed"
        assert result['word_count'] > 300, "Word count too low"
        assert result['persona_optimized'], "Persona optimization flag missing"
        
        print(f"✅ Material: {result['material']}")
        print(f"✅ Author: {result['author_name']} (ID: {result['author_id']})")
        print(f"✅ Word count: {result['word_count']}")
        print(f"✅ Sections: {result['sections']}")
        print("✅ Frontmatter integration working correctly")
        
        # Test with mock frontmatter
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
subject: Test Material
category: metal
properties:
  chemicalFormula: "TestO₂"
---
Test content""")
            temp_file = f.name
        
        try:
            calculator = ContentCalculator(load_frontmatter_data(temp_file), 1)
            content = calculator.calculate_content_for_material()
            assert 'Test Material' in content, "Mock material missing"
            assert 'TestO₂' in content, "Mock formula missing"
            print("✅ Mock frontmatter integration working")
        finally:
            os.unlink(temp_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_chemical_formula_extraction():
    """Test 5: Chemical formula extraction"""
    print("\n🧪 TEST 5: Chemical Formula Extraction")
    print("=" * 40)
    
    try:
        # Test with different materials
        test_cases = [
            ({'subject': 'Aluminum', 'properties': {'chemicalFormula': 'Al₂O₃'}}, 'Al₂O₃'),
            ({'subject': 'Steel', 'properties': {}}, 'Fe₂O₃'),  # Fallback
            ({'subject': 'Copper', 'properties': {}}, 'Cu₂O'),  # Fallback
            ({'subject': 'Unknown Material', 'properties': {}}, 'Unknown MaterialₓOᵧ')  # Generic fallback
        ]
        
        for frontmatter_data, expected_formula in test_cases:
            calculator = ContentCalculator(frontmatter_data, 2)
            assert calculator.material_formula == expected_formula, f"Formula mismatch: expected {expected_formula}, got {calculator.material_formula}"
            
            # Verify formula appears in content
            content = calculator.calculate_content_for_material()
            assert expected_formula in content, f"Formula {expected_formula} missing from content"
            
            print(f"✅ {frontmatter_data['subject']}: {expected_formula}")
        
        print("✅ Chemical formula extraction working correctly")
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
        frontmatter_file = 'content/components/frontmatter/aluminum-laser-cleaning.md'
        frontmatter_data = load_frontmatter_data(frontmatter_file)
        
        # Test generation speed for each author
        for author_id in [1, 2, 3, 4]:
            start_time = time.time()
            iterations = 5
            
            for _ in range(iterations):
                calculator = ContentCalculator(frontmatter_data, author_id)
                content = calculator.calculate_content_for_material()
                result = calculator.generate_complete_content()
            
            end_time = time.time()
            avg_time = (end_time - start_time) / iterations
            
            # Performance assertions
            assert avg_time < 0.1, f"Generation too slow for author {author_id}: {avg_time:.4f}s"
            assert len(content) > 200, f"Content too short for author {author_id}"
            assert result['word_count'] > 100, f"Word count too low for author {author_id}"
            
            author_name = calculator.author_info['name'] if calculator.author_info else f"Author {author_id}"
            print(f"✅ {author_name}: {avg_time:.4f}s average")
        
        print("✅ All authors meet performance targets (<0.1s per generation)")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_frontmatter_author_extraction():
    """Test 6: Author extraction from frontmatter"""
    print("\n🧪 TEST 6: Author Extraction from Frontmatter")
    print("=" * 40)
    
    try:
        authors = load_authors_data()
        
        for author in authors:
            # Create test frontmatter with this author
            test_frontmatter = {
                'name': 'Steel',
                'author': author['name'],
                'formula': 'Fe₂O₃',
                'properties': {
                    'density': '7.87 g/cm³'
                }
            }
            
            # Write temporary frontmatter file
            import yaml
            temp_content = f"---\n{yaml.dump(test_frontmatter)}\n---\n\nTest content"
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(temp_content)
                temp_file = f.name
            
            try:
                # Generate content (should automatically use author from frontmatter)
                content = calculate_content_for_material(temp_file)
                
                # Verify content was generated
                assert len(content) > 100, f"Content too short for {author['name']}"
                
                # Verify author-specific characteristics
                if author['country'] == 'Taiwan':
                    assert any(word in content.lower() for word in ['methodical', 'systematic', 'approach']), "Taiwan style not detected"
                elif author['country'] == 'Italy':
                    assert any(word in content.lower() for word in ['passion', 'art', 'masterpiece']), "Italy style not detected"
                elif author['country'] == 'Indonesia':
                    assert 'analysis' in content.lower() and 'important' in content.lower(), "Indonesia style not detected"
                elif 'United States' in author['country']:
                    assert any(word in content.lower()[:200] for word in ['let', "we're", 'imagine']), "USA style not detected"
                
                print(f"✅ {author['name']} ({author['country']}) - Style verified")
                
            finally:
                os.unlink(temp_file)
        
        # Test missing author fallback
        test_frontmatter_no_author = {
            'name': 'Copper',
            'formula': 'Cu₂O'
        }
        
        temp_content = f"---\n{yaml.dump(test_frontmatter_no_author)}\n---\n\nTest content"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(temp_content)
            temp_file = f.name
        
        try:
            content = calculate_content_for_material(temp_file)
            # Should fallback to Alessandro Moretti (passionate style)
            assert any(word in content.lower() for word in ['passion', 'art', 'masterpiece']), "Fallback to Alessandro not working"
            print("✅ Missing author fallback verified")
        finally:
            os.unlink(temp_file)
        
        print("✅ Author extraction from frontmatter working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 CONTENT CALCULATOR TEST SUITE")
    print("=" * 50)
    print("📅 Test Date: August 30, 2025")
    print("🎯 Testing: Author-driven content generation functionality")
    
    # Run all tests
    tests = [
        test_author_data_loading,
        test_content_generation_all_authors,
        test_author_persona_differences,
        test_frontmatter_integration,
        test_chemical_formula_extraction,
        test_performance,
        test_frontmatter_author_extraction
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
        print("🎉 ALL TESTS PASSED! Content calculator is ready for production.")
        print("📝 4 distinct author personas successfully implemented")
        print("🌍 Global authorship: Taiwan, Italy, Indonesia, USA")
    else:
        print("⚠️ Some tests failed. Please review the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
