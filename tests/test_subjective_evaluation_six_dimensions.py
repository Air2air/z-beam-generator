"""
Test Six-Dimension Comprehensive Human Realism Evaluation

Verifies that subjective evaluation checks all 6 comprehensive dimensions
for human realism and properly detects technical jargon, formulaic structures,
and other AI patterns.

Created: November 22, 2025
Policy: docs/06-ai-systems/SUBJECTIVE_EVALUATION_POLICY.md (to be created)
"""

import pytest
from unittest.mock import Mock
from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator


class TestSixDimensionEvaluation:
    """Test comprehensive 6-dimension human realism evaluation"""
    
    def test_six_dimensions_parsed_from_response(self):
        """Verify all 6 dimensions are parsed from evaluation response"""
        mock_api = Mock()
        
        # Mock API response with all 6 dimensions
        mock_response = Mock()
        mock_response.success = True
        mock_response.content = """
**Overall Realism (0-10)**: 8.5
**Voice Authenticity (0-10)**: 8.0
**Tonal Consistency (0-10)**: 7.5
**Technical Accessibility (0-10)**: 9.0
**Natural Imperfection (0-10)**: 8.5
**Conversational Flow (0-10)**: 8.0

**Reasoning**: This content demonstrates strong human characteristics with natural 
flow and practical guidance. Technical accessibility is excellent with minimal jargon.

**Technical Jargon Issues**: none
**AI Patterns Found**: none
**Theatrical Phrases Found**: none
**Formulaic Structures**: none

**Pass/Fail**: PASS
"""
        mock_api.generate.return_value = mock_response
        
        evaluator = SubjectiveEvaluator(
            api_client=mock_api,
            quality_threshold=7.0
        )
        
        result = evaluator.evaluate(
            content="Test content",
            material_name="Aluminum",
            component_type="description"
        )
        
        # Verify all 6 dimensions present
        assert result.realism_score == 8.5, "Overall Realism score missing"
        assert result.voice_authenticity == 8.0, "Voice Authenticity score missing"
        assert result.tonal_consistency == 7.5, "Tonal Consistency score missing"
        assert result.technical_accessibility == 9.0, "Technical Accessibility score missing"
        assert result.natural_imperfection == 8.5, "Natural Imperfection score missing"
        assert result.conversational_flow == 8.0, "Conversational Flow score missing"
        
        # Verify pass status
        assert result.passes_quality_gate is True
    
    def test_technical_jargon_detection(self):
        """Verify technical jargon issues are detected and parsed"""
        mock_api = Mock()
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.content = """
**Overall Realism (0-10)**: 4.0
**Voice Authenticity (0-10)**: 5.0
**Tonal Consistency (0-10)**: 5.0
**Technical Accessibility (0-10)**: 2.0
**Natural Imperfection (0-10)**: 4.0
**Conversational Flow (0-10)**: 4.0

**Reasoning**: Content reads like a physics paper with excessive technical precision.
Multiple decimal places and wavelength citations without practical context.

**Technical Jargon Issues**: Multiple decimal places (0.95, 0.06, 933.47), wavelength citation (1064 nm), temperature in Kelvin (933.47 K)
**AI Patterns Found**: Scientific paper language
**Theatrical Phrases Found**: presents a primary challenge
**Formulaic Structures**: Property bombardment without application

**Pass/Fail**: FAIL
"""
        mock_api.generate.return_value = mock_response
        
        evaluator = SubjectiveEvaluator(
            api_client=mock_api,
            quality_threshold=7.0
        )
        
        result = evaluator.evaluate(
            content="Aluminum's high reflectivity of 0.95 and low laser absorption of 0.06 at 1064 nm present a primary challenge for laser cleaning. Its low melting point of 933.47 K requires precise control.",
            material_name="Aluminum",
            component_type="description"
        )
        
        # Verify technical jargon detected
        assert result.technical_jargon_issues is not None, "Technical jargon issues not parsed"
        assert len(result.technical_jargon_issues) >= 3, f"Expected at least 3 jargon issues, got {len(result.technical_jargon_issues)}"
        
        # Verify specific issues detected (parser may split on commas)
        jargon_text = ' '.join(result.technical_jargon_issues)
        assert 'decimal' in jargon_text.lower() or '0.95' in jargon_text, "Decimal places issue not detected"
        assert '1064' in jargon_text or 'nm' in jargon_text, "Wavelength citation not detected"
        assert 'Kelvin' in jargon_text or '933.47 K' in jargon_text, "Kelvin temperature not detected"
        
        # Verify low technical accessibility score
        assert result.technical_accessibility == 2.0, "Technical accessibility should be low"
        
        # Verify failure
        assert result.passes_quality_gate is False
    
    def test_formulaic_structures_detection(self):
        """Verify formulaic structures are detected and parsed"""
        mock_api = Mock()
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.content = """
**Overall Realism (0-10)**: 5.0
**Voice Authenticity (0-10)**: 6.0
**Tonal Consistency (0-10)**: 5.0
**Technical Accessibility (0-10)**: 7.0
**Natural Imperfection (0-10)**: 3.0
**Conversational Flow (0-10)**: 4.0

**Reasoning**: Content shows formulaic patterns with perfect parallel structures
and suspiciously balanced sentence lengths indicating algorithmic generation.

**Technical Jargon Issues**: none
**AI Patterns Found**: Perfect parallel structures, balanced sentence lengths
**Theatrical Phrases Found**: none
**Formulaic Structures**: Three items in identical format, symmetry obsession

**Pass/Fail**: FAIL
"""
        mock_api.generate.return_value = mock_response
        
        evaluator = SubjectiveEvaluator(
            api_client=mock_api,
            quality_threshold=7.0
        )
        
        result = evaluator.evaluate(
            content="Test content with formulaic patterns",
            material_name="Steel",
            component_type="description"
        )
        
        # Verify formulaic structures detected
        assert result.formulaic_structures is not None, "Formulaic structures not parsed"
        assert len(result.formulaic_structures) == 2, f"Expected 2 formulaic patterns, got {len(result.formulaic_structures)}"
        
        # Verify specific patterns detected
        formulaic_text = ', '.join(result.formulaic_structures)
        assert 'identical format' in formulaic_text.lower(), "Identical format pattern not detected"
        assert 'symmetry' in formulaic_text.lower(), "Symmetry obsession not detected"
        
        # Verify low natural imperfection score
        assert result.natural_imperfection == 3.0, "Natural imperfection should be low"
        
        # Verify low conversational flow score
        assert result.conversational_flow == 4.0, "Conversational flow should be low"
        
        # Verify failure
        assert result.passes_quality_gate is False
    
    def test_all_detection_categories_present(self):
        """Verify all 4 detection categories are parsed"""
        mock_api = Mock()
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.content = """
**Overall Realism (0-10)**: 3.0
**Voice Authenticity (0-10)**: 4.0
**Tonal Consistency (0-10)**: 4.0
**Technical Accessibility (0-10)**: 2.0
**Natural Imperfection (0-10)**: 3.0
**Conversational Flow (0-10)**: 3.0

**Reasoning**: Multiple issues detected across all categories indicating AI generation.

**Technical Jargon Issues**: Excessive decimals (0.95), wavelength (1064 nm)
**AI Patterns Found**: Hedge words, balanced structures
**Theatrical Phrases Found**: presents a unique challenge, critical pitfall
**Formulaic Structures**: Template-driven organization

**Pass/Fail**: FAIL
"""
        mock_api.generate.return_value = mock_response
        
        evaluator = SubjectiveEvaluator(
            api_client=mock_api,
            quality_threshold=7.0
        )
        
        result = evaluator.evaluate(
            content="Test content with all issues",
            material_name="Copper",
            component_type="description"
        )
        
        # Verify all 4 detection categories present
        assert result.technical_jargon_issues is not None, "Technical jargon missing"
        assert result.ai_tendencies is not None, "AI patterns missing"
        assert result.formulaic_structures is not None, "Formulaic structures missing"
        
        # Verify counts
        assert len(result.technical_jargon_issues) == 2, "Should have 2 jargon issues"
        assert len(result.ai_tendencies) == 2, "Should have 2 AI patterns"
        assert len(result.formulaic_structures) == 1, "Should have 1 formulaic structure"
        
        # Verify comprehensive failure
        assert result.passes_quality_gate is False
        assert result.overall_score < 5.0, "Overall score should be very low"
    
    def test_clean_content_passes_all_dimensions(self):
        """Verify clean human-like content passes all 6 dimensions"""
        mock_api = Mock()
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.content = """
**Overall Realism (0-10)**: 9.0
**Voice Authenticity (0-10)**: 9.0
**Tonal Consistency (0-10)**: 8.5
**Technical Accessibility (0-10)**: 9.5
**Natural Imperfection (0-10)**: 9.0
**Conversational Flow (0-10)**: 9.0

**Reasoning**: Excellent natural human voice with practical guidance and genuine
stylistic quirks. No jargon overload, flows naturally like expert explaining.

**Technical Jargon Issues**: none
**AI Patterns Found**: none
**Theatrical Phrases Found**: none
**Formulaic Structures**: none

**Pass/Fail**: PASS
"""
        mock_api.generate.return_value = mock_response
        
        evaluator = SubjectiveEvaluator(
            api_client=mock_api,
            quality_threshold=7.0
        )
        
        result = evaluator.evaluate(
            content="Copper tends to heat up fast, so you'll want to dial back the power a bit. Start around 80W and watch how it responds - the surface should clean up nicely without any discoloration.",
            material_name="Copper",
            component_type="description"
        )
        
        # Verify all dimensions high
        assert result.realism_score >= 9.0, "Overall Realism should be excellent"
        assert result.voice_authenticity >= 9.0, "Voice Authenticity should be excellent"
        assert result.tonal_consistency >= 8.0, "Tonal Consistency should be high"
        assert result.technical_accessibility >= 9.0, "Technical Accessibility should be excellent"
        assert result.natural_imperfection >= 9.0, "Natural Imperfection should be excellent"
        assert result.conversational_flow >= 9.0, "Conversational Flow should be excellent"
        
        # Verify no issues detected
        assert result.technical_jargon_issues is None or len(result.technical_jargon_issues) == 0
        assert result.ai_tendencies is None or len(result.ai_tendencies) == 0
        assert result.formulaic_structures is None or len(result.formulaic_structures) == 0
        
        # Verify pass
        assert result.passes_quality_gate is True
    
    def test_technical_accessibility_dimension_critical(self):
        """Verify Technical Accessibility dimension catches academic tone"""
        mock_api = Mock()
        
        # Response with low technical accessibility but other dimensions OK
        mock_response = Mock()
        mock_response.success = True
        mock_response.content = """
**Overall Realism (0-10)**: 6.0
**Voice Authenticity (0-10)**: 7.0
**Tonal Consistency (0-10)**: 7.0
**Technical Accessibility (0-10)**: 3.0
**Natural Imperfection (0-10)**: 7.0
**Conversational Flow (0-10)**: 6.0

**Reasoning**: Voice is authentic but content reads like academic documentation
rather than practical guidance. Too much technical precision without context.

**Technical Jargon Issues**: Physics textbook language, property bombardment
**AI Patterns Found**: none
**Theatrical Phrases Found**: none
**Formulaic Structures**: none

**Pass/Fail**: FAIL
"""
        mock_api.generate.return_value = mock_response
        
        evaluator = SubjectiveEvaluator(
            api_client=mock_api,
            quality_threshold=7.0
        )
        
        result = evaluator.evaluate(
            content="The material exhibits a reflectivity coefficient of 0.95 at the standard wavelength.",
            material_name="Aluminum",
            component_type="description"
        )
        
        # Verify technical accessibility is the problem
        assert result.technical_accessibility == 3.0, "Technical accessibility should be very low"
        assert result.voice_authenticity >= 7.0, "Voice authenticity should be acceptable"
        
        # Verify failure despite some good scores
        assert result.passes_quality_gate is False
        assert result.overall_score < 7.0


class TestEvaluationResponseFormat:
    """Test evaluation response format with 6 dimensions"""
    
    def test_response_format_includes_all_required_fields(self):
        """Verify evaluation prompt expects all required response fields"""
        from pathlib import Path
        
        template_file = Path('prompts/evaluation/subjective_quality.txt')
        assert template_file.exists(), "Evaluation template not found"
        
        template_content = template_file.read_text()
        
        # Verify 6 dimension headers in response format
        assert '**Overall Realism (0-10)**:' in template_content
        assert '**Voice Authenticity (0-10)**:' in template_content
        assert '**Tonal Consistency (0-10)**:' in template_content
        assert '**Technical Accessibility (0-10)**:' in template_content
        assert '**Natural Imperfection (0-10)**:' in template_content
        assert '**Conversational Flow (0-10)**:' in template_content
        
        # Verify 4 detection categories in response format
        assert '**Technical Jargon Issues**:' in template_content
        assert '**AI Patterns Found**:' in template_content
        assert '**Theatrical Phrases Found**:' in template_content
        assert '**Formulaic Structures**:' in template_content
        
        # Verify pass/fail field
        assert '**Pass/Fail**:' in template_content
    
    def test_evaluation_criteria_includes_jargon_detection(self):
        """Verify evaluation prompt includes technical jargon detection criteria"""
        from pathlib import Path
        
        template_file = Path('prompts/evaluation/subjective_quality.txt')
        template_content = template_file.read_text()
        
        # Verify technical jargon section exists
        assert 'TECHNICAL JARGON OVERLOAD' in template_content, "Technical jargon section missing"
        
        # Verify specific jargon criteria
        assert 'decimal places' in template_content.lower(), "Decimal places criterion missing"
        assert 'wavelength' in template_content.lower(), "Wavelength criterion missing"
        assert 'Kelvin' in template_content, "Kelvin temperature criterion missing"
        assert 'physics textbook' in template_content.lower() or 'scientific paper' in template_content.lower(), "Academic tone criterion missing"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
