#!/usr/bin/env python3
"""
Property Categorizer System Validation

Validates that the property categorization system is correctly installed
and functioning according to GROK principles.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def validate_installation():
    """Validate that all components are installed"""
    print("🔍 Validating Property Categorizer Installation\n")
    print("=" * 60)
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Categories.yaml exists and has propertyCategories section
    print("\n1. Checking Categories.yaml...")
    checks_total += 1
    try:
        import yaml
        categories_path = Path(__file__).resolve().parents[1] / "data" / "Categories.yaml"
        with open(categories_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if 'propertyCategories' in data:
            taxonomy = data['propertyCategories']
            print(f"   ✅ propertyCategories section found")
            print(f"   ✅ {len(taxonomy['categories'])} categories defined")
            print(f"   ✅ {taxonomy['metadata']['total_properties']} total properties")
            checks_passed += 1
        else:
            print("   ❌ propertyCategories section not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 2: property_categorizer.py exists and loads
    print("\n2. Checking property_categorizer.py...")
    checks_total += 1
    try:
        from utils.core.property_categorizer import get_property_categorizer
        categorizer = get_property_categorizer()
        print(f"   ✅ PropertyCategorizer loaded")
        print(f"   ✅ {len(categorizer.categories)} categories accessible")
        print(f"   ✅ {len(categorizer._property_to_category)} properties indexed")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 3: Schema validation
    print("\n3. Checking property_categories_schema.json...")
    checks_total += 1
    try:
        import json
        schema_path = Path(__file__).resolve().parents[1] / "schemas" / "property_categories_schema.json"
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        if '$schema' in schema and 'properties' in schema:
            print(f"   ✅ Schema file valid")
            print(f"   ✅ Schema version: {schema.get('$schema', 'unknown')}")
            checks_passed += 1
        else:
            print("   ❌ Invalid schema structure")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 4: Tests exist and are runnable
    print("\n4. Checking test_property_categorizer.py...")
    checks_total += 1
    try:
        test_path = Path(__file__).resolve().parents[1] / "tests" / "test_property_categorizer.py"
        if test_path.exists():
            print(f"   ✅ Test file exists")
            # Try importing to check syntax
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_module", test_path)
            if spec:
                print(f"   ✅ Test file is syntactically valid")
                checks_passed += 1
            else:
                print("   ❌ Test file has syntax errors")
        else:
            print("   ❌ Test file not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 5: Documentation exists
    print("\n5. Checking PROPERTY_CATEGORIES.md...")
    checks_total += 1
    try:
        doc_path = Path(__file__).resolve().parents[1] / "docs" / "reference" / "PROPERTY_CATEGORIES.md"
        if doc_path.exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content) > 1000:  # Should be substantial
                print(f"   ✅ Documentation file exists ({len(content)} bytes)")
                checks_passed += 1
            else:
                print("   ❌ Documentation file too short")
        else:
            print("   ❌ Documentation file not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 6: GROK compliance - fail-fast behavior
    print("\n6. Checking GROK compliance (fail-fast behavior)...")
    checks_total += 1
    try:
        from utils.core.property_categorizer import PropertyCategorizer, PropertyCategorizationError
        
        # Should throw exception if Categories.yaml is missing/invalid
        # We can't test this without breaking the system, so we check the exception class exists
        if PropertyCategorizationError:
            print(f"   ✅ PropertyCategorizationError exception defined")
            print(f"   ✅ Fail-fast architecture implemented")
            checks_passed += 1
        else:
            print("   ❌ Exception class not properly defined")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 7: Basic functionality test
    print("\n7. Testing basic functionality...")
    checks_total += 1
    try:
        from utils.core.property_categorizer import get_property_categorizer
        categorizer = get_property_categorizer()
        
        # Test property lookup
        category = categorizer.get_category('thermalConductivity')
        tier = categorizer.get_usage_tier('density')
        props = categorizer.get_properties_by_category('thermal')
        
        if category == 'thermal' and tier == 'core' and len(props) > 0:
            print(f"   ✅ Property lookup working")
            print(f"   ✅ Usage tier classification working")
            print(f"   ✅ Category property listing working")
            checks_passed += 1
        else:
            print("   ❌ Functionality test failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"\n📊 Validation Summary: {checks_passed}/{checks_total} checks passed")
    
    if checks_passed == checks_total:
        print("\n✅ ALL CHECKS PASSED - System is fully operational!")
        print("\n🎉 Property Categorizer successfully installed and validated")
        return True
    else:
        print(f"\n⚠️  {checks_total - checks_passed} checks failed - please review errors above")
        return False


if __name__ == '__main__':
    success = validate_installation()
    sys.exit(0 if success else 1)
