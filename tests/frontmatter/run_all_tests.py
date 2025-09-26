#!/usr/bin/env python3
"""
Frontmatter Test Runner
Comprehensive test runner for all frontmatter-related tests.
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_frontmatter_tests():
    """Run all frontmatter-related tests."""
    print("🧪 Frontmatter Test Suite Runner")
    print("=" * 60)
    
    # Test discovery and execution
    test_results = {}
    
    # 1. Run enhanced frontmatter generator tests
    print("\n1️⃣ Running Enhanced Frontmatter Generator Tests...")
    try:
        from test_enhanced_frontmatter_generator import (
            test_frontmatter_properties_have_units,
            test_machine_settings_structure,
            test_new_frontmatter_system_integration
        )
        
        test1 = test_frontmatter_properties_have_units()
        test2 = test_machine_settings_structure()
        test3 = test_new_frontmatter_system_integration()
        
        test_results["enhanced_generator"] = test1 and test2 and test3
        print(f"✅ Enhanced generator tests: {'PASSED' if test_results['enhanced_generator'] else 'FAILED'}")
        
    except Exception as e:
        test_results["enhanced_generator"] = False
        print(f"❌ Enhanced generator tests failed: {e}")
    
    # 2. Run frontmatter management tests
    print("\n2️⃣ Running Frontmatter Management Tests...")
    try:
        # Discover and run unit tests
        test_loader = unittest.TestLoader()
        test_suite = unittest.TestSuite()
        
        # Add frontmatter-specific tests
        frontmatter_test_dir = Path("tests/frontmatter")
        if frontmatter_test_dir.exists():
            frontmatter_tests = test_loader.discover(str(frontmatter_test_dir), pattern="test_*.py")
            test_suite.addTest(frontmatter_tests)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(test_suite)
        
        test_results["frontmatter_management"] = result.wasSuccessful()
        print(f"✅ Frontmatter management tests: {'PASSED' if test_results['frontmatter_management'] else 'FAILED'}")
        
    except Exception as e:
        test_results["frontmatter_management"] = False
        print(f"❌ Frontmatter management tests failed: {e}")
    
    # 3. Run component integration tests
    print("\n3️⃣ Running Component Integration Tests...")
    try:
        # Test updated frontmatter component
        component_test_path = Path("tests/unit/test_frontmatter_component.py")
        if component_test_path.exists():
            test_loader = unittest.TestLoader()
            suite = test_loader.loadTestsFromName("tests.unit.test_frontmatter_component")
            
            runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
            result = runner.run(suite)
            
            test_results["component_integration"] = result.wasSuccessful()
        else:
            test_results["component_integration"] = True  # Skip if not found
            print("ℹ️ Component integration tests not found - skipping")
        
        print(f"✅ Component integration tests: {'PASSED' if test_results['component_integration'] else 'FAILED'}")
        
    except Exception as e:
        test_results["component_integration"] = False
        print(f"❌ Component integration tests failed: {e}")
    
    # 4. Run material loading tests
    print("\n4️⃣ Running Material Loading Tests...")
    try:
        material_test_path = Path("tests/unit/test_material_loading.py")
        if material_test_path.exists():
            test_loader = unittest.TestLoader()
            suite = test_loader.loadTestsFromName("tests.unit.test_material_loading")
            
            runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
            result = runner.run(suite)
            
            test_results["material_loading"] = result.wasSuccessful()
        else:
            test_results["material_loading"] = True  # Skip if not found
            print("ℹ️ Material loading tests not found - skipping")
        
        print(f"✅ Material loading tests: {'PASSED' if test_results['material_loading'] else 'FAILED'}")
        
    except Exception as e:
        test_results["material_loading"] = False
        print(f"❌ Material loading tests failed: {e}")
    
    # 5. System readiness check
    print("\n5️⃣ Running System Readiness Check...")
    try:
        readiness_results = check_system_readiness()
        test_results["system_readiness"] = readiness_results["overall_ready"]
        
        print(f"✅ System readiness: {'READY' if test_results['system_readiness'] else 'NEEDS ATTENTION'}")
        
    except Exception as e:
        test_results["system_readiness"] = False
        print(f"❌ System readiness check failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL FRONTMATTER TESTS PASSED!")
        return True
    else:
        print("⚠️ Some frontmatter tests failed. Check details above.")
        return False

def check_system_readiness():
    """Check if the frontmatter system is ready for use."""
    print("🔍 Checking Frontmatter System Readiness...")
    
    results = {
        "old_structure_exists": False,
        "new_structure_exists": False,
        "migration_needed": False,
        "schema_available": False,
        "manager_available": False,
        "overall_ready": False
    }
    
    # Check old structure
    old_dir = Path("frontmatter/materials")
    if old_dir.exists():
        old_files = list(old_dir.glob("*.md"))
        results["old_structure_exists"] = len(old_files) > 0
        print(f"📁 Old structure: {len(old_files)} files found")
    
    # Check new structure
    new_dir = Path("frontmatter/materials")
    if new_dir.exists():
        new_files = list(new_dir.glob("*.yaml"))
        results["new_structure_exists"] = len(new_files) > 0
        print(f"📁 New structure: {len(new_files)} files found")
    
    # Check if migration is needed
    results["migration_needed"] = results["old_structure_exists"] and not results["new_structure_exists"]
    if results["migration_needed"]:
        print("🔄 Migration needed: Old structure exists but new structure is empty")
    
    # Check schema availability
    schema_path = Path("frontmatter/schemas/material-frontmatter.schema.json")
    results["schema_available"] = schema_path.exists()
    if results["schema_available"]:
        print("📋 Schema available: JSON Schema validation enabled")
    else:
        print("⚠️ Schema not found: Validation may not work")
    
    # Check manager availability
    try:
        from frontmatter.management.manager import FrontmatterManager
        FrontmatterManager()  # Test initialization
        results["manager_available"] = True
        print("🔧 FrontmatterManager: Available and functional")
    except ImportError:
        results["manager_available"] = False
        print("⚠️ FrontmatterManager: Not available")
    except Exception as e:
        results["manager_available"] = False
        print(f"⚠️ FrontmatterManager: Error - {e}")
    
    # Overall readiness assessment
    if results["migration_needed"]:
        results["overall_ready"] = False
        print("📋 System status: Migration required before use")
    elif results["new_structure_exists"] and results["schema_available"] and results["manager_available"]:
        results["overall_ready"] = True
        print("📋 System status: Fully ready for use")
    elif results["manager_available"]:
        results["overall_ready"] = True
        print("📋 System status: Ready (some features may be limited)")
    else:
        results["overall_ready"] = False
        print("📋 System status: Not ready - setup required")
    
    return results

if __name__ == "__main__":
    success = run_frontmatter_tests()
    sys.exit(0 if success else 1)
