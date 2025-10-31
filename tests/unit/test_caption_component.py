#!/usr/bin/env python3
"""
Test Caption Component

Tests for the caption component generator.
"""

from unittest.mock import Mock

import pytest

from materials.caption.generators.generator import CaptionComponentGenerator, CaptionGenerator

def get_mock_api_client():
    """Create a mock API client for testing."""
    mock_api_client = Mock()
    
    # Create a mock response object with the expected structure and format
    mock_response = Mock()
    mock_response.success = True
    mock_response.content = """**BEFORE_TEXT:**
This comprehensive analysis examines the application of laser cleaning technology for industrial surface treatment processes. The non-contact laser ablation method provides precise control over material removal while maintaining substrate integrity. Advanced pulse parameters including wavelength optimization, power density modulation, and scan velocity control enable effective contaminant removal across diverse material categories. The technique demonstrates superior performance in removing oxidation, paint layers, and surface contaminants without mechanical damage.

**AFTER_TEXT:**
Following laser cleaning treatment, surfaces exhibit enhanced quality with minimal thermal stress and zero mechanical damage. The non-destructive process preserves dimensional accuracy while achieving superior cleanliness levels required for advanced manufacturing applications.
"""
    mock_response.error = None
    
    mock_api_client.generate_simple.return_value = mock_response
    return mock_api_client

def get_caption_generator():
    """Lazy initialization of caption generator."""
    global _test_generator
    if "_test_generator" not in globals():
        global _test_generator
        _test_generator = CaptionComponentGenerator()
    return _test_generator

def test_caption_generation_success():
    """Test successful caption generation with valid inputs."""
    generator = get_caption_generator()

    # Create mock API client
    mock_api_client = get_mock_api_client()
    
    # Provide minimal frontmatter data
    frontmatter_data = {
        "title": "Aluminum Laser Cleaning",
        "author": {"name": "Test Author"},
        "category": "metal"
    }

    result = generator.generate(material_name="aluminum", material_data={}, api_client=mock_api_client, frontmatter_data=frontmatter_data)
    assert result.success, f"Caption generation should succeed: {result.error_message}"
    assert result.component_type == "caption"
    assert result.content, "Content should not be empty"
    assert "before_text" in result.content
    assert "after_text" in result.content

def test_caption_material_data_validation():
    """Test caption generation with valid material data."""
    generator = get_caption_generator()

    # Create mock API client with proper response object
    mock_api_client = Mock()
    mock_response = Mock()
    mock_response.success = True
    mock_response.content = """**BEFORE_TEXT:**
Mock caption content for aluminum laser cleaning applications showing surface contaminants and oxidation layers. This comprehensive analysis demonstrates the effectiveness of laser ablation technology for removing unwanted surface deposits while preserving the underlying substrate integrity.

**AFTER_TEXT:**
Clean aluminum surface after laser treatment with enhanced properties and improved surface quality for industrial applications."""
    mock_response.error = None
    mock_api_client.generate_simple.return_value = mock_response

    material_data = {
        "name": "Aluminum",
        "subject": "Aluminum",
        "category": "metal",
        "data": {"formula": "Al"},
        "materialProperties": {"chemicalFormula": "Al"}
    }

    # Provide required frontmatter_data for fail-fast architecture
    frontmatter_data = {
        "title": "Aluminum Laser Cleaning",
        "author": {"name": "Test Author"},
        "category": "metal"
    }

    result = generator.generate(
        material_name="Aluminum",
        material_data=material_data,
        api_client=mock_api_client,
        frontmatter_data=frontmatter_data
    )

    assert result.success
    assert result.component_type == "caption"
    assert len(result.content) > 0
    # Check for YAML content structure
    assert "before_text:" in result.content
    assert "after_text:" in result.content
    # Check for material in metadata footer (case-insensitive)
    assert "Material:" in result.content or "material:" in result.content
    # Caption generator is working correctly and producing valid YAML

def test_caption_output_format():
    """Test caption component output format and structure."""
    generator = get_caption_generator()
    mock_api_client = get_mock_api_client()

    frontmatter_data = {
        "title": "Aluminum Laser Cleaning",
        "author": {"name": "Test Author"},
        "category": "metal"
    }

    result = generator.generate(
        material_name="Aluminum",
        material_data={},
        api_client=mock_api_client,
        frontmatter_data=frontmatter_data
    )

    # Verify successful generation
    assert result.success, f"Should succeed with valid data: {result.error_message}"
    assert result.component_type == "caption"
    assert result.content, "Content should not be empty"

def test_caption_with_minimal_data():
    """Test caption generation with minimal material data."""
    generator = get_caption_generator()
    mock_api_client = get_mock_api_client()

    minimal_data = {
        "name": "Steel",
        "category": "metal"
    }

    frontmatter_data = {
        "title": "Steel Laser Cleaning",
        "author": {"name": "Test Author"},
        "category": "metal"
    }

    result = generator.generate(
        material_name="Steel",
        material_data=minimal_data,
        api_client=mock_api_client,
        frontmatter_data=frontmatter_data
    )

    # Verify successful generation with minimal data
    assert result.success, f"Should succeed with minimal data: {result.error_message}"
    assert result.component_type == "caption"
    assert result.content, "Content should not be empty"

def test_caption_yaml_parsing():
    """Test that generated caption content is valid YAML."""
    import yaml
    
    generator = get_caption_generator()
    mock_api_client = get_mock_api_client()

    frontmatter_data = {
        "title": "Steel Laser Cleaning",
        "author": {"name": "Test Author"},
        "category": "metal"
    }

    result = generator.generate(
        material_name="Steel",
        material_data={"name": "Steel"},
        api_client=mock_api_client,
        frontmatter_data=frontmatter_data
    )

    assert result.success
    content = result.content
    
    # Extract YAML content (before the metadata footer)
    yaml_content = content.split('\n---\n')[0]
    
    try:
        # Parse YAML to ensure it's valid
        parsed = yaml.safe_load(yaml_content)
        
        # Validate required fields (content uses "before_text" and "after_text")
        assert "before_text" in parsed or "before" in parsed
        assert "after_text" in parsed or "after" in parsed
        # Note: material is in metadata footer, not in YAML body
        assert "author" in parsed
        assert "generation" in parsed
        
        # Validate data types
        assert isinstance(parsed["author"], str)
        # Check for before/after content (could be "before_text" or "before")
        before_key = "before_text" if "before_text" in parsed else "before"
        after_key = "after_text" if "after_text" in parsed else "after"
        assert isinstance(parsed[before_key], str)
        assert isinstance(parsed[after_key], str)
        assert len(parsed[before_key]) > 0
        assert len(parsed[after_key]) > 0
        
    except yaml.YAMLError as e:
        pytest.fail(f"Generated content is not valid YAML: {e}")

def test_caption_randomization():
    """Test that captions are randomized for variety."""
    generator = get_caption_generator()
    mock_api_client = get_mock_api_client()

    frontmatter_data = {
        "title": "Steel Laser Cleaning",
        "author": {"name": "Test Author"},
        "category": "metal"
    }

    # Generate multiple captions to check randomization
    captions = []
    for _ in range(10):
        result = generator.generate(
            material_name="Steel",
            material_data={"name": "Steel"},
            api_client=mock_api_client,
            frontmatter_data=frontmatter_data
        )
        assert result.success
        captions.append(result.content)

    # Check that we get some variation (not all identical)
    unique_captions = set(captions)
    assert len(unique_captions) > 1, "Captions should be randomized"

def test_caption_legacy_generator():
    """Test CaptionGenerator with proper parameters."""
    generator = CaptionGenerator()
    mock_api_client = get_mock_api_client()

    # Use the correct signature for caption generator
    result = generator.generate(
        material="brass",
        material_data={
            "name": "Brass", 
            "category": "metal",
            "formula": "CuZn"  # Provide required chemical data
        },
        api_client=mock_api_client
    )

    assert isinstance(result, str)
    assert len(result) > 0
    # Check for YAML content structure
    assert "brass" in result.lower()  # Material name appears somewhere
    assert "before" in result.lower() or "before_text:" in result

def test_caption_component_info():
    """Test component information retrieval."""
    generator = CaptionGenerator()

    # CaptionGenerator is a simple class without get_component_info method
    # Test that it can be instantiated and has expected attributes
    assert hasattr(generator, 'generate')
    assert callable(generator.generate)

def test_caption_error_handling():
    """Test error handling in caption generation."""
    generator = get_caption_generator()
    mock_api_client = get_mock_api_client()

    frontmatter_data = {
        "title": "Test Material Laser Cleaning",
        "author": {"name": "Test Author"},
        "category": "metal"
    }

    # Test with None material_data - should still work with fail-fast architecture
    result = generator.generate(
        material_name="Test",
        material_data=None,
        api_client=mock_api_client,
        frontmatter_data=frontmatter_data
    )

    # Should succeed with required parameters provided
    assert result.success

def test_caption_content_structure():
    """Test caption content has proper YAML structure."""
    generator = get_caption_generator()
    mock_api_client = get_mock_api_client()

    frontmatter_data = {
        "title": "Silicon Laser Cleaning",
        "author": {"name": "Test Author"},
        "category": "semiconductor"
    }

    result = generator.generate(
        material_name="Silicon",
        material_data={"name": "Silicon"},
        api_client=mock_api_client,
        frontmatter_data=frontmatter_data
    )

    assert result.success
    content = result.content

    # Check for YAML structure (current format uses before_text/after_text)
    assert "before_text:" in content or "before:" in content
    assert "after_text:" in content or "after:" in content
    
    # Check for required sections
    assert "generation:" in content
    assert "author:" in content

    # Check for contamination description in before field
    contamination_keywords = [
        "contaminants", "oxide", "particulate", "residues",
        "deposits", "contamination", "buildup", "staining"
    ]
    assert any(keyword in content.lower() for keyword in contamination_keywords)

    # Check for result description in after field
    result_keywords = [
        "removal", "cleaning", "modification", "ablation",
        "restoration", "decontamination", "elimination"
    ]
    assert any(keyword in content.lower() for keyword in result_keywords)

    # Check YAML metadata structure (Component Metadata section exists)
    assert "Component Metadata" in content or "Component:" in content
    assert "generated:" in content or "Generated:" in content
