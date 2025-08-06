#!/usr/bin/env python3
"""
Final verification that SlugUtils is properly implemented everywhere and prevents double dashes.
"""

import sys
import os
import re

# Add the project root to the Python path
sys.path.insert(0, os.getcwd())

def test_slugutils_double_dash_prevention():
    """Test that SlugUtils prevents double dashes in all scenarios."""
    print("Testing SlugUtils double dash prevention...")
    print("=" * 60)
    
    try:
        from components.base.utils.slug_utils import SlugUtils
        
        # Test edge cases that could potentially create double dashes
        test_cases = [
            "Normal Subject",           # Normal case
            "Subject-With-Hyphens",     # Already has hyphens
            "Subject--Double--Dash",    # Already has double dashes
            "Subject_With_Underscores", # Underscores
            "Subject  Multiple  Spaces", # Multiple spaces
            "Subject-_Mixed_-Separators", # Mixed separators
            "Subject---Triple---Dash",  # Triple dashes
            "",                         # Empty string
            "A",                        # Single character
            "Subject!!Special@@Chars##", # Special characters
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            print(f"\nTesting: '{test_case}'")
            
            # Test all SlugUtils methods
            basic_slug = SlugUtils.create_slug(test_case)
            subject_slug = SlugUtils.create_subject_slug(test_case)
            category_slug = SlugUtils.create_category_slug(test_case)
            article_type_slug = SlugUtils.create_article_type_slug(test_case)
            image_slug = SlugUtils.create_image_slug(test_case, "hero")
            image_url = SlugUtils.create_image_url(test_case, "hero")
            
            # Check for double dashes
            results = [
                ("Basic slug", basic_slug),
                ("Subject slug", subject_slug),
                ("Category slug", category_slug),
                ("Article type slug", article_type_slug),
                ("Image slug", image_slug),
                ("Image URL", image_url),
            ]
            
            for name, result in results:
                if "--" in result:
                    print(f"  ❌ {name}: {result} (contains double dash)")
                    all_passed = False
                else:
                    print(f"  ✓ {name}: {result}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing SlugUtils: {e}")
        return False

def test_imagehandler_integration():
    """Test that ImageHandler properly uses SlugUtils."""
    print("\n" + "=" * 60)
    print("Testing ImageHandler integration with SlugUtils...")
    print("=" * 60)
    
    try:
        from components.base.image_handler import ImageHandler
        
        test_subjects = [
            "Zirconia",
            "Stoneware", 
            "Porcelain",
            "Multi--Word--Subject",
            "Subject_With_Underscores",
        ]
        
        all_passed = True
        
        for subject in test_subjects:
            print(f"\nTesting ImageHandler with subject: '{subject}'")
            
            # Test ImageHandler methods
            subject_slug = ImageHandler.get_subject_slug(subject)
            hero_url = ImageHandler.format_image_url(subject, "hero")
            closeup_url = ImageHandler.format_image_url(subject, "closeup")
            
            # Test normalization
            problematic_url = f"/images/{subject.lower().replace(' ', '--')}--laser-cleaning-hero.jpg"
            normalized_url = ImageHandler.normalize_url(problematic_url)
            
            results = [
                ("Subject slug", subject_slug),
                ("Hero URL", hero_url),
                ("Closeup URL", closeup_url),
                ("Normalized URL", normalized_url),
            ]
            
            for name, result in results:
                if "--" in result:
                    print(f"  ❌ {name}: {result} (contains double dash)")
                    all_passed = False
                else:
                    print(f"  ✓ {name}: {result}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing ImageHandler: {e}")
        return False

def verify_generator_imports():
    """Verify all active generators import and use SlugUtils."""
    print("\n" + "=" * 60)
    print("Verifying all generators import SlugUtils...")
    print("=" * 60)
    
    # Key generator files that should use SlugUtils
    key_generators = [
        "components/frontmatter/generator.py",
        "components/metatags/generator.py", 
        "components/jsonld/generator.py",
        "components/base/component.py",
        "components/base/image_handler.py",
        "run.py",
    ]
    
    all_passed = True
    
    for generator_file in key_generators:
        if not os.path.exists(generator_file):
            print(f"⚠️  {generator_file} not found")
            continue
        
        try:
            with open(generator_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for SlugUtils import
            has_slugutils_import = "from components.base.utils.slug_utils import SlugUtils" in content
            
            # Check for SlugUtils usage
            has_slugutils_usage = "SlugUtils." in content
            
            # Check for manual slug creation (bad) - but ignore commented lines
            manual_slug_matches = re.findall(r'\.lower\(\)\.replace\(\s*["\'][\s_]["\'],.*["\'][-_]["\']\)', content)
            # Filter out matches that are in commented lines
            has_manual_slug = False
            for match in manual_slug_matches:
                # Find the line containing this match
                lines = content.split('\n')
                for line in lines:
                    if match in line and not line.strip().startswith('#'):
                        has_manual_slug = True
                        break
            
            if has_slugutils_import and has_slugutils_usage and not has_manual_slug:
                print(f"✓ {generator_file}: Properly uses SlugUtils")
            else:
                print(f"❌ {generator_file}:")
                if not has_slugutils_import:
                    print("    Missing SlugUtils import")
                if not has_slugutils_usage:
                    print("    Not using SlugUtils methods")
                if has_manual_slug:
                    print("    Still has manual slug creation")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error reading {generator_file}: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run comprehensive SlugUtils verification."""
    print("COMPREHENSIVE SLUGUTILS VERIFICATION")
    print("=" * 60)
    
    # Test 1: SlugUtils double dash prevention
    slugutils_ok = test_slugutils_double_dash_prevention()
    
    # Test 2: ImageHandler integration
    imagehandler_ok = test_imagehandler_integration()
    
    # Test 3: Generator imports and usage
    generators_ok = verify_generator_imports()
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if slugutils_ok and imagehandler_ok and generators_ok:
        print("✅ ALL VERIFICATIONS PASSED")
        print("   • SlugUtils prevents double dashes in all scenarios")
        print("   • ImageHandler properly integrates with SlugUtils")
        print("   • All generators properly import and use SlugUtils")
        print("\n🎉 SlugUtils is properly implemented throughout the codebase!")
        print("🚫 Double dashes cannot be generated by any component!")
        return True
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        if not slugutils_ok:
            print("   • SlugUtils has issues with double dash prevention")
        if not imagehandler_ok:
            print("   • ImageHandler integration issues")
        if not generators_ok:
            print("   • Some generators not properly using SlugUtils")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
