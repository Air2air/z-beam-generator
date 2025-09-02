#!/usr/bin/env python3
"""
Z-Beam Testing Coordinator

This script provides a unified interface for running all Z-Beam tests including:
- Original dynamic system tests
- New component-local architecture tests  
- Integration tests
- Mock generator        parser.add_argument(
        '--no-mocks', 
        action='store_true',
        help='Run only no mocks/fallbacks test'
    )s

Usage:
    python3 tests/run_all_tests.py                    # Run all tests
    python3 tests/run_all_tests.py --component-local  # Run only component-local tests
    python3 tests/run_all_tests.py --enhanced         # Run enhanced dynamic system tests
    python3 tests/run_all_tests.py --quick            # Run quick smoke tests only
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_no_mocks_fallbacks_test():
    """Run no mocks or fallbacks test"""
    print("\n🚫 RUNNING NO MOCKS/FALLBACKS TEST")
    print("=" * 60)
    
    try:
        from tests.test_no_mocks_fallbacks import main as test_no_mocks_fallbacks
        return test_no_mocks_fallbacks()
    except ImportError as e:
        print(f"❌ Failed to import no mocks/fallbacks test: {e}")
        return False
    except Exception as e:
        print(f"❌ No mocks/fallbacks test failed: {e}")
        return False

def run_component_local_tests():
    """Run component-local architecture tests"""
    print("🏗️  RUNNING COMPONENT-LOCAL ARCHITECTURE TESTS")
    print("=" * 60)
    
    try:
        from tests.test_component_local_architecture import main as test_component_local
        return test_component_local()
    except ImportError as e:
        print(f"❌ Failed to import component-local tests: {e}")
        return False
    except Exception as e:
        print(f"❌ Component-local tests failed: {e}")
        return False

def run_enhanced_dynamic_tests():
    """Run enhanced dynamic system tests"""
    print("\n🚀 RUNNING ENHANCED DYNAMIC SYSTEM TESTS")
    print("=" * 60)
    
    try:
        from tests.test_enhanced_dynamic_system import main as test_enhanced_dynamic
        return test_enhanced_dynamic()
    except ImportError as e:
        print(f"❌ Failed to import enhanced dynamic tests: {e}")
        return False
    except Exception as e:
        print(f"❌ Enhanced dynamic tests failed: {e}")
        return False

def run_original_dynamic_tests():
    """Run original dynamic system tests"""
    print("\n🔄 RUNNING ORIGINAL DYNAMIC SYSTEM TESTS")
    print("=" * 60)
    
    try:
        from tests.test_dynamic_system import main as test_original_dynamic
        return test_original_dynamic()
    except ImportError as e:
        print(f"❌ Failed to import original dynamic tests: {e}")
        return False
    except Exception as e:
        print(f"❌ Original dynamic tests failed: {e}")
        return False

def run_quick_smoke_tests():
    """Run quick smoke tests to verify basic functionality"""
    print("💨 RUNNING QUICK SMOKE TESTS")
    print("=" * 60)
    
    success_count = 0
    total_tests = 5
    
    # Test 1: Basic imports
    print("\n🔍 Test 1: Basic System Imports...")
    try:
        from generators.dynamic_generator import DynamicGenerator
        print("  ✅ Core system imports successful")
        success_count += 1
    except Exception as e:
        print(f"  ❌ Core system imports failed: {e}")
    
    # Test 2: Component-local imports
    print("\n🔍 Test 2: Component-Local Module Imports...")
    try:
        from components.frontmatter.validator import validate_frontmatter_content
        print("  ✅ Component-local imports successful")
        success_count += 1
    except Exception as e:
        print(f"  ❌ Component-local imports failed: {e}")
    
    # Test 3: Dynamic generator initialization
    print("\n🔍 Test 3: Dynamic Generator Initialization...")
    try:
        generator = DynamicGenerator()
        materials = generator.get_available_materials()
        components = generator.get_available_components()
        if len(materials) > 50 and len(components) > 5:
            print(f"  ✅ Generator initialized ({len(materials)} materials, {len(components)} components)")
            success_count += 1
        else:
            print(f"  ❌ Generator data insufficient ({len(materials)} materials, {len(components)} components)")
    except Exception as e:
        print(f"  ❌ Generator initialization failed: {e}")
    
    # Test 4: Centralized validator
    print("\n🔍 Test 4: Centralized Validator...")
    try:
        from validators.centralized_validator import CentralizedValidator
        CentralizedValidator()
        print("  ✅ Centralized validator initialized")
        success_count += 1
    except Exception as e:
        print(f"  ❌ Centralized validator failed: {e}")
    
    # Test 5: API client
    print("\n🔍 Test 5: API Client...")
    try:
        from api.client import MockAPIClient
        client = MockAPIClient()
        response = client.generate_simple("test prompt")
        if response.success:
            print("  ✅ API client functional")
            success_count += 1
        else:
            print("  ❌ API client response failed")
    except Exception as e:
        print(f"  ❌ API client failed: {e}")
    
    # Summary
    print(f"\n📊 SMOKE TEST RESULTS: {success_count}/{total_tests} passed")
    if success_count == total_tests:
        print("✅ All smoke tests passed - system appears functional")
    else:
        print(f"⚠️  {total_tests - success_count} smoke tests failed")
    
    return success_count == total_tests

def run_all_tests():
    """Run all test suites"""
    print("🧪 Z-BEAM COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print("Running all available test suites...")
    print("=" * 70)
    
    results = {}
    
    # Run no mocks/fallbacks test first (critical for fail-fast architecture)
    print("🚫 PRIORITY: No Mocks/Fallbacks Test (Fail-Fast Architecture)")
    results['no_mocks_fallbacks'] = run_no_mocks_fallbacks_test()
    
    # Only continue with other tests if no mocks/fallbacks test passes
    if not results['no_mocks_fallbacks']:
        print("\n❌ CRITICAL FAILURE: Mock/fallback violations detected!")
        print("🛑 Stopping test suite - fail-fast architecture violated")
        print("🔧 Fix mock/fallback violations before running other tests")
        
        # Summary for critical failure
        print("\n" + "=" * 70)
        print("📊 CRITICAL TEST FAILURE - FAIL-FAST ARCHITECTURE VIOLATED")
        print("=" * 70)
        print("   No Mocks/Fallbacks: ❌ FAILED")
        print("   Other Tests: ⏸️  SKIPPED (fix violations first)")
        print("\n❌ SYSTEM DOES NOT FOLLOW FAIL-FAST ARCHITECTURE")
        print("🔧 Manual cleanup required to remove mocks and fallbacks")
        return False
    
    print("\n✅ No mocks/fallbacks test passed - continuing with other tests...")
    
    # Run component-local tests
    results['component_local'] = run_component_local_tests()
    
    # Run enhanced dynamic tests
    results['enhanced_dynamic'] = run_enhanced_dynamic_tests()
    
    # Run original dynamic tests
    results['original_dynamic'] = run_original_dynamic_tests()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE TEST SUITE RESULTS")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print("\n🎯 OVERALL RESULTS:")
    print(f"   Test Suites: {passed}/{total} passed")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TEST SUITES PASSED!")
        print("✅ Z-Beam system with fail-fast architecture is fully functional")
        
        print("\n📋 VERIFIED SYSTEM CAPABILITIES:")
        print("   ✅ Fail-fast architecture enforced (no mocks/fallbacks)")
        print("   ✅ Component-local architecture complete")
        print("   ✅ Enhanced dynamic generation system")
        print("   ✅ Original functionality preserved")
        print("   ✅ Integration between systems working")
        
        print("\n🚀 SYSTEM READY FOR:")
        print("   • Full content generation workflows")
        print("   • Production deployment")
        print("   • Component-specific development")
        print("   • Strict fail-fast validation")
        
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed")
        print("🔧 Review individual test results for specific issues")
    
    return passed == total

def main():
    """Main entry point for test coordinator"""
    parser = argparse.ArgumentParser(
        description="Z-Beam Testing Coordinator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 tests/run_all_tests.py                    # Run all tests (no-mocks first)
  python3 tests/run_all_tests.py --no-mocks         # No mocks/fallbacks test only  
  python3 tests/run_all_tests.py --component-local  # Component-local tests only
  python3 tests/run_all_tests.py --enhanced         # Enhanced dynamic tests only
  python3 tests/run_all_tests.py --quick            # Quick smoke tests only
  python3 tests/run_all_tests.py --original         # Original dynamic tests only
        """
    )
    
    parser.add_argument(
        '--component-local', 
        action='store_true',
        help='Run only component-local architecture tests'
    )
    parser.add_argument(
        '--enhanced', 
        action='store_true',
        help='Run only enhanced dynamic system tests'
    )
    parser.add_argument(
        '--original', 
        action='store_true',
        help='Run only original dynamic system tests'
    )
    parser.add_argument(
        '--no-mocks', 
        action='store_true',
        help='Run only no mocks/fallbacks test (default priority)'
    )
    parser.add_argument(
        '--quick', 
        action='store_true',
        help='Run only quick smoke tests'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Determine which tests to run
    if args.component_local:
        success = run_component_local_tests()
    elif args.enhanced:
        success = run_enhanced_dynamic_tests()
    elif args.original:
        success = run_original_dynamic_tests()
    elif args.quick:
        success = run_quick_smoke_tests()
    elif args.no_mocks:
        success = run_no_mocks_fallbacks_test()
    else:
        # Run all tests by default
        success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
