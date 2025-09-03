#!/usr/bin/env python3
"""
Content Component Test Suite Runner

Orchestrates all content generation tests following CLAUDE_INSTRUCTIONS.md principles.
Fail-fast architecture with comprehensive validation and no mocks in production.
"""

import sys
import logging
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('content_test_results.log')
    ]
)
logger = logging.getLogger(__name__)


def run_content_test_suite():
    """Run complete content component test suite"""
    logger.info("🚀 Z-BEAM CONTENT COMPONENT TEST SUITE")
    logger.info("=" * 80)
    logger.info("Following CLAUDE_INSTRUCTIONS.md principles:")
    logger.info("  ✅ Fail-fast architecture")
    logger.info("  ✅ No mocks or fallbacks")
    logger.info("  ✅ Real API integration testing")
    logger.info("  ✅ Comprehensive validation")
    logger.info("=" * 80)
    
    start_time = time.time()
    
    # Test execution results
    test_results = {}
    
    # 1. Calculator Tests - Removed (no production calculator code exists)
    logger.info("\n📊 TEST SUITE 1: CALCULATOR TESTS - REMOVED")
    logger.info("-" * 60)
    logger.info("❌ Calculator module removed - no fallbacks or mocks allowed")
    # No test_results entry - let the test fail if calculator is expected
    
    # 2. Run Persona Validation Tests (new)
    logger.info("\n🎭 TEST SUITE 2: PERSONA VALIDATION TESTS")
    logger.info("-" * 60)
    try:
        from components.content.testing.test_persona_validation import run_persona_validation_tests
        success = run_persona_validation_tests()
        test_results['persona_validation'] = success
        if success:
            logger.info("✅ Persona validation tests PASSED")
        else:
            logger.error("❌ Persona validation tests FAILED")
    except Exception as e:
        logger.error(f"❌ Persona validation tests ERROR: {e}")
        test_results['persona_validation'] = False
    
    # 3. Run Technical Content Validation Tests (new)
    logger.info("\n🔬 TEST SUITE 3: TECHNICAL CONTENT VALIDATION TESTS")
    logger.info("-" * 60)
    logger.info("⚠️  WARNING: This suite makes real API calls to Grok")
    logger.info("   - Tests new technical-only content requirements")
    logger.info("   - Validates emotive language elimination")
    logger.info("   - Checks header standardization and paragraph structure")
    
    try:
        from components.content.testing.test_technical_content_validation import run_technical_content_validation_tests
        success = run_technical_content_validation_tests()
        test_results['technical_validation'] = success
        if success:
            logger.info("✅ Technical content validation tests PASSED")
        else:
            logger.error("❌ Technical content validation tests FAILED")
    except Exception as e:
        logger.error(f"❌ Technical content validation tests ERROR: {e}")
        test_results['technical_validation'] = False
    
    # 4. Run End-to-End Tests (existing, with API calls)
    logger.info("\n🌐 TEST SUITE 4: END-TO-END INTEGRATION TESTS")
    logger.info("-" * 60)
    logger.info("⚠️  WARNING: This suite makes real API calls to Grok")
    logger.info("   - Tests are limited to minimize API usage")
    logger.info("   - May take several minutes to complete")
    
    try:
        from components.content.testing.test_content_end_to_end_updated import run_updated_end_to_end_tests
        success = run_updated_end_to_end_tests()
        test_results['end_to_end'] = success
        if success:
            logger.info("✅ End-to-end tests PASSED")
        else:
            logger.error("❌ End-to-end tests FAILED")
    except Exception as e:
        logger.error(f"❌ End-to-end tests ERROR: {e}")
        test_results['end_to_end'] = False
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Final Summary
    logger.info("\n" + "=" * 80)
    logger.info("📋 FINAL TEST SUITE SUMMARY")
    logger.info("=" * 80)
    
    total_suites = len(test_results)
    passed_suites = sum(test_results.values())
    
    logger.info(f"Total test suites: {total_suites}")
    logger.info(f"Passed suites: {passed_suites}")
    logger.info(f"Failed suites: {total_suites - passed_suites}")
    logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")
    
    logger.info("\nDetailed Results:")
    for suite_name, success in test_results.items():
        status = "PASSED" if success else "FAILED"
        emoji = "✅" if success else "❌"
        logger.info(f"  {emoji} {suite_name}: {status}")
    
    # Overall success determination
    overall_success = all(test_results.values())
    
    if overall_success:
        logger.info("\n🎉 ALL CONTENT COMPONENT TESTS PASSED!")
        logger.info("Content generation system is validated and ready for production.")
    else:
        logger.error("\n❌ SOME CONTENT COMPONENT TESTS FAILED!")
        logger.error("Review failed tests before deploying content generation system.")
    
    logger.info("\n📄 Detailed logs saved to: content_test_results.log")
    logger.info("=" * 80)
    
    return overall_success


def main():
    """Main entry point"""
    try:
        success = run_content_test_suite()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Test suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"🔥 Critical error in test suite: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
