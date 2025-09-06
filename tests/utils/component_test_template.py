#!/usr/bin/env python3
"""
Component Test Template
Standardized testing template for all Z-Beam generator components.

This template provides a consistent testing structure for:
- Component generation validation
- Error handling and fail-fast behavior
- API client dependency testing
- Material data validation
- Author information validation
- Output format verification

Usage:
1. Copy this template for each component
2. Replace COMPONENT_NAME with the actual component name
3. Update test data and assertions as needed
4. Ensure proper imports for the specific component
"""

import sys
from pathlib import Path
from typing import Dict

from components.COMPONENT_NAME.generator import COMPONENT_NAMEComponentGenerator

from generators.component_generators import ComponentResult

except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Test fixtures
_test_generator = None

def get_generator():
    """Lazy initialization of component generator."""
    global _test_generator
    if _test_generator is None:
        _test_generator = COMPONENT_NAMEComponentGenerator()
    return _test_generator

def test_COMPONENT_NAME_generation_success():
    """Test successful COMPONENT_NAME generation with valid inputs."""
    print(f"🧪 Testing COMPONENT_NAME Generation Success")
    print("-" * 60)

    generator = get_generator()

    # Test with mock/real API client (depending on availability)
    # This test assumes an API client is available
    # In CI/CD, this would use a mock client

    result = generator.generate(
        material_name="Aluminum",
        material_data={
            "name": "Aluminum",
            "subject": "Aluminum",
            "category": "metal",
            "data": {"formula": "Al"},
            "properties": {"chemicalFormula": "Al"}
        },
        api_client=None,  # Replace with actual client in integration tests
        author_info={"id": 1, "name": "Test Author", "country": "Test Country"}
    )

    # Verify result structure
    assert isinstance(result, ComponentResult)
    assert result.component_type == "COMPONENT_NAME"
    assert isinstance(result.success, bool)
    assert isinstance(result.content, str)
    assert isinstance(result.metadata, dict)

    if result.success:
        # Additional validation for successful generation
        assert len(result.content.strip()) > 0, "Generated content should not be empty"
        # Add component-specific validations here

    print(f"✅ COMPONENT_NAME generation test completed")

def test_COMPONENT_NAME_fail_fast_no_api_client():
    """Test fail-fast behavior when no API client is provided."""
    print(f"⚡ Testing COMPONENT_NAME Fail-Fast (No API Client)")
    print("-" * 60)

    generator = get_generator()

    result = generator.generate(
        material_name="Test Material",
        material_data={
            "name": "Test Material",
            "subject": "Test",
            "category": "test",
            "data": {"formula": "T"},
            "properties": {"chemicalFormula": "T"}
        },
        api_client=None,  # Should trigger fail-fast
        author_info={"id": 1, "name": "Test Author", "country": "Test"}
    )

    # Verify fail-fast behavior
    assert isinstance(result, ComponentResult)
    assert not result.success, "Should fail without API client"
    assert "API client" in result.error_message.lower() or "required" in result.error_message.lower()

    print(f"✅ Fail-fast test passed: {result.error_message}")

def test_COMPONENT_NAME_material_data_validation():
    """Test material data validation and error handling."""
    print(f"📊 Testing COMPONENT_NAME Material Data Validation")
    print("-" * 60)

    generator = get_generator()

    # Test with invalid material data
    result = generator.generate(
        material_name="",
        material_data={},  # Empty data should cause validation error
        api_client=None,
        author_info={"id": 1, "name": "Test Author", "country": "Test"}
    )

    # Should fail with invalid data
    assert isinstance(result, ComponentResult)
    assert not result.success, "Should fail with invalid material data"

    print(f"✅ Material data validation test passed")

def test_COMPONENT_NAME_author_info_validation():
    """Test author information validation."""
    print(f"👤 Testing COMPONENT_NAME Author Info Validation")
    print("-" * 60)

    generator = get_generator()

    # Test with invalid author info
    result = generator.generate(
        material_name="Test Material",
        material_data={
            "name": "Test Material",
            "subject": "Test",
            "category": "test",
            "data": {"formula": "T"},
            "properties": {"chemicalFormula": "T"}
        },
        api_client=None,
        author_info={}  # Empty author info
    )

    # Should handle gracefully
    assert isinstance(result, ComponentResult)
    # Note: Some components may not require author info, so this might succeed

    print(f"✅ Author info validation test passed")

def test_COMPONENT_NAME_output_format():
    """Test output format and structure."""
    print(f"📝 Testing COMPONENT_NAME Output Format")
    print("-" * 60)

    generator = get_generator()

    # This test would be more meaningful with a mock API client
    # For now, test the fail-fast path and verify error format

    result = generator.generate(
        material_name="Test Material",
        material_data={
            "name": "Test Material",
            "subject": "Test",
            "category": "test",
            "data": {"formula": "T"},
            "properties": {"chemicalFormula": "T"}
        },
        api_client=None,
        author_info={"id": 1, "name": "Test Author", "country": "Test"}
    )

    # Verify result has proper structure even on failure
    assert hasattr(result, 'component_type')
    assert hasattr(result, 'success')
    assert hasattr(result, 'content')
    assert hasattr(result, 'error_message')
    assert hasattr(result, 'metadata')

    print(f"✅ Output format test passed")

# Component-specific tests can be added below
# def test_COMPONENT_NAME_specific_feature():
#     """Test component-specific features."""
#     pass
