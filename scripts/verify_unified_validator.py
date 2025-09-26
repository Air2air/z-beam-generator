#!/usr/bin/env python3
"""
Unified Validator Verification Script

Comprehensive testing to ensure the unified validator properly consolidates
all existing validation functionality without breaking existing code.

Tests:
1. Basic validation functionality
2. Enhanced validation with quality scoring
3. Research-grade validation requirements
4. Backward compatibility with all legacy interfaces
5. Schema hierarchy and fallback behavior
6. CLI interface functionality
"""

import sys
import json
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_unified_validator_basic():
    """Test basic unified validator functionality"""
    
    logger.info("🧪 Testing UnifiedSchemaValidator basic functionality...")
    
    try:
        from validation.unified_schema_validator import UnifiedSchemaValidator, ValidationMode
        
        # Test basic mode
        validator = UnifiedSchemaValidator(validation_mode="basic")
        
        # Test with valid data
        valid_data = {
            "name": "aluminum_6061",
            "category": "metal",
            "title": "Aluminum 6061-T6",
            "description": "High-strength aluminum alloy for aerospace applications",
            "properties": {
                "density": {
                    "value": 2.70,
                    "unit": "g/cm³",
                    "confidence_score": 0.95
                }
            }
        }
        
        result = validator.validate(valid_data, "aluminum_6061")
        
        # Verify result structure
        assert hasattr(result, 'is_valid'), "Missing is_valid attribute"
        assert hasattr(result, 'quality_score'), "Missing quality_score attribute"
        assert hasattr(result, 'errors'), "Missing errors attribute"
        assert hasattr(result, 'warnings'), "Missing warnings attribute"
        
        # Verify backward compatibility properties
        assert hasattr(result, 'valid'), "Missing backward compatibility 'valid' property"
        assert hasattr(result, 'error_count'), "Missing backward compatibility 'error_count' property"
        assert hasattr(result, 'error_messages'), "Missing backward compatibility 'error_messages' property"
        
        logger.info("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic functionality test failed: {e}")
        return False


def test_validation_modes():
    """Test different validation modes"""
    
    logger.info("🧪 Testing validation modes...")
    
    try:
        from validation.unified_schema_validator import UnifiedSchemaValidator
        
        test_data = {
            "name": "steel_304",
            "category": "metal",
            "title": "Stainless Steel 304",
            "description": "Austenitic stainless steel",
            "properties": {
                "density": {
                    "value": 8.0,
                    "unit": "g/cm³",
                    "confidence_score": 0.90,
                    "validation": {
                        "confidence_score": 0.90,
                        "sources_validated": 3,
                        "peer_reviewed": True
                    }
                }
            },
            "machineSettings": {
                "power": {
                    "value": 1000,
                    "unit": "W",
                    "confidence_score": 0.85,
                    "validation": {
                        "confidence_score": 0.85,
                        "sources_validated": 2,
                        "peer_reviewed": True
                    }
                }
            }
        }
        
        # Test basic mode
        basic_validator = UnifiedSchemaValidator(validation_mode="basic")
        basic_result = basic_validator.validate(test_data, "steel_304")
        
        # Test enhanced mode
        enhanced_validator = UnifiedSchemaValidator(validation_mode="enhanced")
        enhanced_result = enhanced_validator.validate(test_data, "steel_304")
        
        # Test research grade mode
        research_validator = UnifiedSchemaValidator(validation_mode="research_grade")
        research_result = research_validator.validate(test_data, "steel_304")
        
        # Verify mode differences
        assert enhanced_result.quality_score > 0, "Enhanced mode should have quality score"
        assert research_result.research_validation_coverage >= 0, "Research mode should have coverage metric"
        
        logger.info("✅ Validation modes test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Validation modes test failed: {e}")
        return False


def test_backward_compatibility():
    """Test backward compatibility with legacy interfaces"""
    
    logger.info("🧪 Testing backward compatibility...")
    
    try:
        from validation.unified_schema_validator import UnifiedSchemaValidator
        
        validator = UnifiedSchemaValidator(validation_mode="basic")
        
        test_data = {
            "name": "titanium_grade2",
            "category": "metal",
            "title": "Titanium Grade 2",
            "description": "Commercially pure titanium"
        }
        
        # Test legacy validate_frontmatter interface
        is_valid, error_messages = validator.validate_frontmatter(test_data, "titanium_grade2")
        
        assert isinstance(is_valid, bool), "validate_frontmatter should return bool"
        assert isinstance(error_messages, list), "validate_frontmatter should return list of strings"
        
        # Test legacy detailed report interface
        report = validator.validate_with_detailed_report(test_data, "titanium_grade2")
        
        assert isinstance(report, str), "validate_with_detailed_report should return string"
        assert "VALIDATION REPORT" in report, "Report should contain validation header"
        
        logger.info("✅ Backward compatibility test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Backward compatibility test failed: {e}")
        return False


def test_schema_hierarchy():
    """Test schema detection and fallback hierarchy"""
    
    logger.info("🧪 Testing schema hierarchy...")
    
    try:
        from validation.unified_schema_validator import SchemaManager
        
        schema_manager = SchemaManager(project_root)
        schema_path, schema_data = schema_manager.get_primary_schema()
        
        assert isinstance(schema_data, dict), "Schema should be loaded as dict"
        assert "properties" in schema_data, "Schema should have properties section"
        
        logger.info(f"✅ Schema hierarchy test passed - Using: {schema_path.name if schema_path else 'minimal schema'}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema hierarchy test failed: {e}")
        return False


def test_error_handling():
    """Test error handling and validation reporting"""
    
    logger.info("🧪 Testing error handling...")
    
    try:
        from validation.unified_schema_validator import UnifiedSchemaValidator
        
        validator = UnifiedSchemaValidator(validation_mode="enhanced")
        
        # Test with invalid data
        invalid_data = {
            "name": "",  # Empty name should fail
            "category": "invalid_category",
            # Missing required fields
        }
        
        result = validator.validate(invalid_data, "invalid_material")
        
        # Should have validation errors
        assert not result.is_valid, "Invalid data should fail validation"
        assert len(result.errors) > 0, "Invalid data should have errors"
        assert len(result.error_messages) > 0, "Should have error messages for compatibility"
        
        # Test error structure
        for error in result.errors:
            assert hasattr(error, 'field_path'), "Error should have field_path"
            assert hasattr(error, 'message'), "Error should have message"
            assert hasattr(error, 'error_type'), "Error should have error_type"
        
        logger.info("✅ Error handling test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False


def test_datametric_validation():
    """Test DataMetric structure validation"""
    
    logger.info("🧪 Testing DataMetric validation...")
    
    try:
        from validation.unified_schema_validator import UnifiedSchemaValidator
        
        validator = UnifiedSchemaValidator(validation_mode="enhanced")
        
        # Test with proper DataMetric structure
        datametric_data = {
            "name": "copper_c101",
            "category": "metal",
            "title": "Copper C101",
            "description": "High conductivity copper",
            "properties": {
                "density": {
                    "value": 8.96,
                    "unit": "g/cm³", 
                    "confidence_score": 0.95,
                    "validation": {
                        "confidence_score": 0.95,
                        "sources_validated": 4,
                        "peer_reviewed": True
                    }
                },
                "thermal_conductivity": {
                    "value": 401,
                    "unit": "W/(m·K)",
                    "confidence_score": 0.92
                }
            },
            "machineSettings": {
                "power": {
                    "value": 800,
                    "unit": "W",
                    "confidence_score": 0.88
                }
            }
        }
        
        result = validator.validate(datametric_data, "copper_c101")
        
        # Should pass validation with good quality score
        assert result.quality_score > 70, "DataMetric structure should score well"
        assert result.confidence_coverage > 0.5, "Should have confidence coverage"
        
        logger.info(f"✅ DataMetric validation test passed - Quality: {result.quality_score:.1f}%")
        return True
        
    except Exception as e:
        logger.error(f"❌ DataMetric validation test failed: {e}")
        return False


def test_cli_interface():
    """Test CLI interface functionality"""
    
    logger.info("🧪 Testing CLI interface...")
    
    try:
        # Create test data file
        test_data = {
            "name": "test_cli_material",
            "category": "metal",
            "title": "CLI Test Material", 
            "description": "Material for CLI testing"
        }
        
        test_file = project_root / "test_cli_data.json"
        with open(test_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        # Test CLI import
        from validation.unified_schema_validator import main
        
        logger.info("✅ CLI interface test passed - Main function available")
        
        # Cleanup
        test_file.unlink()
        return True
        
    except Exception as e:
        logger.error(f"❌ CLI interface test failed: {e}")
        return False


def run_comprehensive_verification():
    """Run all verification tests"""
    
    logger.info("🚀 Starting comprehensive unified validator verification...")
    
    tests = [
        ("Basic Functionality", test_unified_validator_basic),
        ("Validation Modes", test_validation_modes), 
        ("Backward Compatibility", test_backward_compatibility),
        ("Schema Hierarchy", test_schema_hierarchy),
        ("Error Handling", test_error_handling),
        ("DataMetric Validation", test_datametric_validation),
        ("CLI Interface", test_cli_interface)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"Running: {test_name}")
        logger.info('='*60)
        
        success = test_func()
        results.append((test_name, success))
        
        if success:
            logger.info(f"✅ {test_name}: PASSED")
        else:
            logger.error(f"❌ {test_name}: FAILED")
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("VERIFICATION SUMMARY")
    logger.info('='*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{test_name:<25} {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED - Unified validator ready for deployment!")
        return True
    else:
        logger.error("⚠️ SOME TESTS FAILED - Address issues before deployment")
        return False


def main():
    """Main verification interface"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify unified schema validator functionality")
    parser.add_argument("--test", choices=[
        "basic", "modes", "compatibility", "schema", "errors", "datametric", "cli"
    ], help="Run specific test only")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.test:
        # Run specific test
        test_map = {
            "basic": test_unified_validator_basic,
            "modes": test_validation_modes,
            "compatibility": test_backward_compatibility, 
            "schema": test_schema_hierarchy,
            "errors": test_error_handling,
            "datametric": test_datametric_validation,
            "cli": test_cli_interface
        }
        
        test_func = test_map[args.test]
        success = test_func()
        return 0 if success else 1
    else:
        # Run comprehensive verification
        success = run_comprehensive_verification()
        return 0 if success else 1


if __name__ == "__main__":
    exit(main())