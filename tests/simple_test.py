#!/usr/bin/env python3
"""
Simplified anti-bloat test for core functionality.
Single test file following DEVELOPMENT.md rules.
"""

def test_imports():
    """Test that all core modules import correctly."""
    try:
        # Test core imports
        import main
        from config.global_config import GlobalConfigManager
        from modules import content_generator, api_client, ai_detector
        from modules import prompt_manager, logger, file_handler
        print("✅ All modules import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_config_manager():
    """Test GlobalConfigManager basic functionality."""
    try:
        # Test singleton pattern
        config1 = GlobalConfigManager()
        config2 = GlobalConfigManager()
        assert config1 is config2, "GlobalConfigManager should be singleton"
        
        # Test basic config access (without initialization for now)
        print("✅ GlobalConfigManager singleton works")
        return True
    except Exception as e:
        print(f"❌ Config manager error: {e}")
        return False


def test_mdx_validation():
    """Test basic MDX validation patterns."""
    try:
        from modules.content_generator import validate_mdx_output
        
        # Test basic content
        test_content = """---
title: "Test Article"
tags: ["bronze", "laser"]
---

# Test Article

This is a test article about bronze laser cleaning.
"""
        
        result = validate_mdx_output(test_content)
        assert result is not None, "MDX validation should return content"
        print("✅ MDX validation works")
        return True
    except Exception as e:
        print(f"❌ MDX validation error: {e}")
        return False


def test_prompt_manager():
    """Test prompt loading functionality."""
    try:
        from modules.content_generator import PromptManager
        
        # Test basic prompt manager instantiation
        pm = PromptManager()
        assert pm is not None, "PromptManager should instantiate"
        print("✅ PromptManager works")
        return True
    except Exception as e:
        print(f"❌ PromptManager error: {e}")
        return False


def test_project_guide_compliance():
    """Test PROJECT_GUIDE.md compliance before any operations."""
    try:
        from audit_violations import ClaudeComplianceValidator
        validator = ClaudeComplianceValidator(".")
        
        # Test project guide compliance
        assert validator.validate_project_guide(), "PROJECT_GUIDE.md compliance failed"
        assert validator.validate_documentation_count(), "Unauthorized documentation detected"
        
        print("✅ PROJECT_GUIDE.md compliance verified")
        return True
    except Exception as e:
        print(f"❌ PROJECT_GUIDE.md compliance error: {e}")
        return False


def run_all_tests():
    """Run all simplified tests."""
    print("🧪 Running simplified anti-bloat tests...\n")
    
    tests = [
        test_project_guide_compliance,  # Run compliance first
        test_imports,
        test_config_manager,
        test_mdx_validation,
        test_prompt_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! System meets anti-bloat requirements.")
        return True
    else:
        print("⚠️ Some tests failed. Check system integrity.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
