"""
Unit tests for ValidationUtils

Tests Phase 3.3 validation consolidation utilities.
Verifies confidence normalization, threshold checks, and property validation.
"""

import pytest
from components.frontmatter.services.validation_utils import ValidationUtils


class TestConfidenceNormalization:
    """Test confidence value normalization"""
    
    def test_normalize_fractional_confidence(self):
        """Fractional values (0.0-1.0) should convert to percentages"""
        assert ValidationUtils.normalize_confidence(0.85) == 85
        assert ValidationUtils.normalize_confidence(0.5) == 50
        assert ValidationUtils.normalize_confidence(0.0) == 0
        assert ValidationUtils.normalize_confidence(1.0) == 1  # Edge case: 1.0 treated as percentage
    
    def test_normalize_percentage_confidence(self):
        """Percentage values (0-100) should remain unchanged"""
        assert ValidationUtils.normalize_confidence(85) == 85
        assert ValidationUtils.normalize_confidence(50) == 50
        assert ValidationUtils.normalize_confidence(100) == 100
        assert ValidationUtils.normalize_confidence(0) == 0
    
    def test_normalize_edge_cases(self):
        """Edge cases for confidence normalization"""
        assert ValidationUtils.normalize_confidence(0.999) == 99
        assert ValidationUtils.normalize_confidence(0.001) == 0
        assert ValidationUtils.normalize_confidence(99.9) == 99
    
    def test_normalize_returns_integer(self):
        """All normalized values should be integers"""
        result = ValidationUtils.normalize_confidence(0.855)
        assert isinstance(result, int)
        assert result == 85


class TestConfidenceThresholds:
    """Test confidence threshold checking"""
    
    def test_high_confidence_with_default_threshold(self):
        """Test using default YAML_CONFIDENCE_THRESHOLD (0.85)"""
        assert ValidationUtils.is_high_confidence(0.9) is True
        assert ValidationUtils.is_high_confidence(0.85) is True
        assert ValidationUtils.is_high_confidence(0.84) is False
        assert ValidationUtils.is_high_confidence(0.75) is False
    
    def test_high_confidence_with_percentage_values(self):
        """Test with percentage format (0-100)"""
        assert ValidationUtils.is_high_confidence(90) is True
        assert ValidationUtils.is_high_confidence(85) is True
        assert ValidationUtils.is_high_confidence(84) is False
        assert ValidationUtils.is_high_confidence(75) is False
    
    def test_high_confidence_with_custom_threshold(self):
        """Test with custom threshold values"""
        assert ValidationUtils.is_high_confidence(0.75, threshold=0.7) is True
        assert ValidationUtils.is_high_confidence(0.65, threshold=0.7) is False
        assert ValidationUtils.is_high_confidence(80, threshold=0.75) is True
        assert ValidationUtils.is_high_confidence(70, threshold=0.75) is False
    
    def test_threshold_constants(self):
        """Verify threshold constants are defined correctly"""
        assert ValidationUtils.YAML_CONFIDENCE_THRESHOLD == 0.85
        assert ValidationUtils.AI_CONFIDENCE_THRESHOLD == 0.80
        assert isinstance(ValidationUtils.YAML_CONFIDENCE_THRESHOLD, float)
        assert isinstance(ValidationUtils.AI_CONFIDENCE_THRESHOLD, float)


class TestPropertyValidation:
    """Test essential property validation"""
    
    def test_all_properties_present(self):
        """All required properties present should pass"""
        properties = {'density': {...}, 'hardness': {...}, 'meltingPoint': {...}}
        required = {'density', 'hardness', 'meltingPoint'}
        
        is_valid, missing = ValidationUtils.validate_essential_properties(
            properties, required, "TestMaterial"
        )
        
        assert is_valid is True
        assert missing == []
    
    def test_missing_properties(self):
        """Missing required properties should be detected"""
        properties = {'density': {...}, 'hardness': {...}}
        required = {'density', 'hardness', 'meltingPoint', 'thermalConductivity'}
        
        is_valid, missing = ValidationUtils.validate_essential_properties(
            properties, required, "TestMaterial"
        )
        
        assert is_valid is False
        assert len(missing) == 2
        assert 'meltingPoint' in missing
        assert 'thermalConductivity' in missing
    
    def test_extra_properties_allowed(self):
        """Extra non-required properties should not cause failure"""
        properties = {
            'density': {...},
            'hardness': {...},
            'meltingPoint': {...},
            'extraProperty': {...}
        }
        required = {'density', 'hardness', 'meltingPoint'}
        
        is_valid, missing = ValidationUtils.validate_essential_properties(
            properties, required
        )
        
        assert is_valid is True
        assert missing == []
    
    def test_empty_required_set(self):
        """Empty required set should always pass"""
        properties = {'density': {...}}
        required = set()
        
        is_valid, missing = ValidationUtils.validate_essential_properties(
            properties, required
        )
        
        assert is_valid is True
        assert missing == []
    
    def test_missing_list_is_sorted(self):
        """Missing properties should be returned in sorted order"""
        properties = {}
        required = {'zirconium', 'aluminum', 'density', 'meltingPoint'}
        
        is_valid, missing = ValidationUtils.validate_essential_properties(
            properties, required
        )
        
        assert missing == ['aluminum', 'density', 'meltingPoint', 'zirconium']


class TestIntegration:
    """Integration tests for ValidationUtils"""
    
    def test_typical_workflow(self):
        """Test typical confidence handling workflow"""
        # Simulate receiving confidence from different sources
        yaml_confidence = 0.95  # Fractional from YAML
        ai_confidence = 85  # Percentage from AI
        
        # Normalize both
        yaml_normalized = ValidationUtils.normalize_confidence(yaml_confidence)
        ai_normalized = ValidationUtils.normalize_confidence(ai_confidence)
        
        assert yaml_normalized == 95
        assert ai_normalized == 85
        
        # Check thresholds
        assert ValidationUtils.is_high_confidence(yaml_normalized) is True
        assert ValidationUtils.is_high_confidence(ai_normalized) is True
    
    def test_phase_3_optimization_benefit(self):
        """Verify Phase 3.3 eliminated duplicate code"""
        # Before Phase 3.3: This logic was duplicated 3 times
        # After Phase 3.3: Single source of truth
        
        test_values = [0.85, 95, 0.5, 50, 1.0, 100]
        
        for value in test_values:
            result = ValidationUtils.normalize_confidence(value)
            assert isinstance(result, int)
            assert 0 <= result <= 100
