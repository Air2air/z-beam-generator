#!/usr/bin/env python3
"""
Quick Consistency Check

A lightweight version of the full consistency tests for rapid feedback during development.
Focuses on the most critical checks to prevent silent failures.
"""

import sys
from pathlib import Path

# Add project root to path  
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def quick_consistency_check():
    """Run critical consistency checks quickly"""
    try:
        print("🏃‍♂️ Running Quick Consistency Check...")
        
        # Test 1: Categories.yaml loading
        try:
            import yaml
            categories_path = Path(__file__).resolve().parent.parent / "data" / "Categories.yaml"
            with open(categories_path, 'r', encoding='utf-8') as file:
                categories_data = yaml.safe_load(file)
            print("   ✅ Categories.yaml loads successfully")
        except Exception as e:
            print(f"   ❌ Categories.yaml loading failed: {e}")
            return False
        
        # Test 2: Materials data loading
        try:
            from domains.materials.materials_cache import load_materials_cached as load_materials
            materials_data = load_materials()
            print("   ✅ Materials data loads successfully")
        except Exception as e:
            print(f"   ❌ Materials data loading failed: {e}")
            return False
        
        # Test 3: Generator unit extraction (critical test)
        try:
            # Set up test environment
            test_materials_data = materials_data.copy()
            test_materials_data['machine_settingsRanges'] = {
                'powerRange': {'min': 10, 'max': 1000, 'unit': 'W'}
            }
            
            import data.materials.materials
            original_load = data.materials.load_materials
            data.materials.load_materials = lambda: test_materials_data
            
            try:
                from export.core.streamlined_generator import StreamlinedFrontmatterGenerator
                from shared.api.client_factory import create_api_client
                
                # Test without API client first (faster)
                generator = StreamlinedFrontmatterGenerator()
                
                # Test critical unit extractions that previously failed
                critical_machine_settings = ['powerRange', 'wavelength', 'spotSize']
                failed_extractions = []
                
                for setting in critical_machine_settings:
                    unit = generator._get_category_unit('metal', setting)
                    if not unit:
                        failed_extractions.append(setting)
                
                if failed_extractions:
                    print(f"   ❌ Unit extraction failed for: {failed_extractions}")
                    return False
                else:
                    print("   ✅ Critical unit extractions working")
                    
            finally:
                data.materials.load_materials = original_load
                
        except Exception as e:
            print(f"   ❌ Generator unit extraction test failed: {e}")
            return False
        
        # Test 4: Required sections present
        try:
            required_sections = ['machine_settingsDescriptions', 'categories']
            missing = [s for s in required_sections if s not in categories_data]
            if missing:
                print(f"   ❌ Missing required sections: {missing}")
                return False
            else:
                print("   ✅ Required Categories.yaml sections present")
        except Exception as e:
            print(f"   ❌ Section check failed: {e}")
            return False
        
        print("✅ Quick consistency check passed!")
        return True
        
    except Exception as e:
        print(f"❌ Quick consistency check failed: {e}")
        return False

def main():
    """Main function"""
    success = quick_consistency_check()
    if success:
        print("\\n🎉 All critical consistency checks passed!")
        print("💡 Run full tests with: python3 tests/test_frontmatter_consistency.py")
    else:
        print("\\n⚠️  Consistency issues detected!")
        print("🔧 Run full tests for details: python3 tests/test_frontmatter_consistency.py --verbose")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()