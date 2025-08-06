"""
Validation script to test the refactored base components.

This script performs basic validation to ensure that functionality has not been lost.
"""

import os
import sys
import logging

# Add project root directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_material_service():
    """Test that the material service can load and retrieve formulas."""
    from components.base.services.material_service import formula_service
    
    # Test formula retrieval
    logger.info("Testing material formula service...")
    formula = formula_service.get_formula("Aluminum", "metal")
    symbol = formula_service.get_symbol("Aluminum", "metal")
    
    if formula == "Al" and symbol == "Al":
        logger.info("✅ Material formula service works correctly")
    else:
        logger.error(f"❌ Material formula service failed: formula={formula}, symbol={symbol}")
        return False
        
    # Test category detection
    material_type = formula_service.get_material_type("Aluminum")
    if material_type == "metal":
        logger.info("✅ Material type detection works correctly")
    else:
        logger.error(f"❌ Material type detection failed: type={material_type}")
        return False
        
    return True

def test_validation_utils():
    """Test that validation utilities work correctly."""
    from components.base.utils.validation import (
        validate_non_empty, validate_length, validate_category_consistency
    )
    
    logger.info("Testing validation utilities...")
    
    # Test validate_non_empty
    try:
        result = validate_non_empty("test content")
        if result == "test content":
            logger.info("✅ validate_non_empty works correctly")
        else:
            logger.error(f"❌ validate_non_empty returned unexpected result: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ validate_non_empty raised exception: {e}")
        return False
        
    # Test validate_length
    try:
        result = validate_length("test content", min_length=5, max_length=15)
        if result == "test content":
            logger.info("✅ validate_length works correctly")
        else:
            logger.error(f"❌ validate_length returned unexpected result: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ validate_length raised exception: {e}")
        return False
        
    # Test validate_category_consistency
    try:
        frontmatter = """---
category: metal
article_type: material
subject: Aluminum
---
Test content
"""
        result = validate_category_consistency(frontmatter, "metal", "material", "Aluminum")
        if result:
            logger.info("✅ validate_category_consistency works correctly")
        else:
            logger.error(f"❌ validate_category_consistency returned unexpected result: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ validate_category_consistency raised exception: {e}")
        return False
        
    return True

def test_formatting_utils():
    """Test that formatting utilities work correctly."""
    from components.base.utils.formatting import format_frontmatter_with_comment
    
    logger.info("Testing formatting utilities...")
    
    # Test format_frontmatter_with_comment
    try:
        yaml_content = """
title: Test Title
description: Test Description
"""
        result = format_frontmatter_with_comment(yaml_content, "metal", "material", "Aluminum")
        
        if "category: metal" in result and "article_type: material" in result and "subject: Aluminum" in result and "<!--" not in result:
            logger.info("✅ format_frontmatter_with_comment works correctly (no HTML comments)")
        else:
            logger.error(f"❌ format_frontmatter_with_comment returned unexpected result: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ format_frontmatter_with_comment raised exception: {e}")
        return False
        
    return True

def main():
    """Run all validation tests."""
    logger.info("Starting validation of refactored base components...")
    
    tests = [
        test_material_service,
        test_validation_utils,
        test_formatting_utils
    ]
    
    success = True
    for test in tests:
        if not test():
            success = False
            
    if success:
        logger.info("✅ All validation tests passed! The refactoring has preserved functionality.")
    else:
        logger.error("❌ Some validation tests failed. The refactoring may have issues.")
        
if __name__ == "__main__":
    main()
