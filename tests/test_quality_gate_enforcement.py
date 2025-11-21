#!/usr/bin/env python3
"""
Test Quality Gate Enforcement

Verifies that content is evaluated BEFORE save and only saved if passing.
Tests the fix implemented on November 20, 2025.
"""

import pytest
from unittest.mock import Mock, patch
from generation.core.simple_generator import SimpleGenerator
from generation.core.quality_gated_generator import QualityGatedGenerator


class TestSimpleGeneratorSaveBehavior:
    """Test SimpleGenerator save/no-save behavior"""
    
    def test_generate_without_save_does_not_save(self):
        """Test that generate_without_save does NOT save to YAML"""
        mock_client = Mock()
        mock_client.generate.return_value = Mock(
            success=True,
            content="Test content for verification"
        )
        
        generator = SimpleGenerator(mock_client)
        
        with patch.object(generator, '_save_to_yaml') as mock_save:
            result = generator.generate_without_save('Aluminum', 'subtitle')
            
            # Verify save was NOT called
            mock_save.assert_not_called()
            
            # Verify result indicates not saved
            assert result['saved'] is False
            assert 'content' in result
            assert 'length' in result
            assert 'word_count' in result
    
    def test_generate_calls_save(self):
        """Test that generate() DOES save to YAML"""
        mock_client = Mock()
        mock_client.generate.return_value = Mock(
            success=True,
            content="Test content for verification"
        )
        
        generator = SimpleGenerator(mock_client)
        
        with patch.object(generator, '_save_to_yaml') as mock_save:
            with patch.object(generator, 'generate_without_save') as mock_gen:
                mock_gen.return_value = {
                    'content': 'test',
                    'length': 4,
                    'word_count': 1,
                    'saved': False,
                    'temperature': 0.7
                }
                
                result = generator.generate('Aluminum', 'subtitle')
                
                # Verify save WAS called
                mock_save.assert_called_once()
                
                # Verify result indicates saved
                assert result['saved'] is True


class TestQualityGateEnforcement:
    """Test that QualityGatedGenerator enforces evaluate-before-save"""
    
    def test_failed_quality_gate_does_not_save(self):
        """Test that content failing quality gate is NOT saved"""
        mock_client = Mock()
        mock_evaluator = Mock()
        
        # Mock evaluation to fail (score < 5.5)
        mock_eval_result = Mock(
            overall_score=4.0,
            realism_score=4.0,
            voice_authenticity=4.0,
            tonal_consistency=4.0,
            ai_tendencies=[],
            passes_quality_gate=False
        )
        mock_evaluator.evaluate.return_value = mock_eval_result
        
        generator = QualityGatedGenerator(
            api_client=mock_client,
            subjective_evaluator=mock_evaluator,
            max_attempts=1,  # Only 1 attempt for test
            quality_threshold=5.5
        )
        
        with patch.object(generator, '_generate_content_only') as mock_gen:
            mock_gen.return_value = {
                'content': 'test content',
                'length': 12,
                'word_count': 2,
                'saved': False
            }
            
            with patch.object(generator, '_save_to_yaml') as mock_save:
                result = generator.generate('Aluminum', 'subtitle')
                
                # Verify save was NOT called (quality failed)
                mock_save.assert_not_called()
                
                # Verify result indicates failure
                assert result.success is False
                assert result.attempts == 1
    
    def test_passed_quality_gate_saves_content(self):
        """Test that content passing quality gate IS saved"""
        mock_client = Mock()
        mock_evaluator = Mock()
        
        # Mock evaluation to pass (score >= 5.5)
        mock_eval_result = Mock(
            overall_score=8.0,
            realism_score=8.0,
            voice_authenticity=8.0,
            tonal_consistency=8.0,
            ai_tendencies=[],
            passes_quality_gate=True
        )
        mock_evaluator.evaluate.return_value = mock_eval_result
        
        generator = QualityGatedGenerator(
            api_client=mock_client,
            subjective_evaluator=mock_evaluator,
            max_attempts=5,
            quality_threshold=5.5
        )
        
        with patch.object(generator, '_generate_content_only') as mock_gen:
            mock_gen.return_value = {
                'content': 'test content',
                'length': 12,
                'word_count': 2,
                'saved': False
            }
            
            with patch.object(generator, '_save_to_yaml') as mock_save:
                result = generator.generate('Aluminum', 'subtitle')
                
                # Verify save WAS called (quality passed)
                mock_save.assert_called_once_with('Aluminum', 'subtitle', 'test content')
                
                # Verify result indicates success
                assert result.success is True
                assert result.attempts == 1
                assert result.final_score == 8.0
    
    def test_multiple_attempts_only_last_saved(self):
        """Test that only the final passing attempt is saved"""
        mock_client = Mock()
        mock_evaluator = Mock()
        
        # Mock evaluation: fail twice, pass third time
        eval_results = [
            Mock(overall_score=4.0, realism_score=4.0, voice_authenticity=4.0, 
                 tonal_consistency=4.0, ai_tendencies=[], passes_quality_gate=False),
            Mock(overall_score=5.0, realism_score=5.0, voice_authenticity=5.0,
                 tonal_consistency=5.0, ai_tendencies=[], passes_quality_gate=False),
            Mock(overall_score=7.0, realism_score=7.0, voice_authenticity=7.0,
                 tonal_consistency=7.0, ai_tendencies=[], passes_quality_gate=True),
        ]
        mock_evaluator.evaluate.side_effect = eval_results
        
        generator = QualityGatedGenerator(
            api_client=mock_client,
            subjective_evaluator=mock_evaluator,
            max_attempts=3,
            quality_threshold=5.5
        )
        
        with patch.object(generator, '_generate_content_only') as mock_gen:
            mock_gen.return_value = {
                'content': 'test content',
                'length': 12,
                'word_count': 2,
                'saved': False
            }
            
            with patch.object(generator, '_save_to_yaml') as mock_save:
                result = generator.generate('Aluminum', 'subtitle')
                
                # Verify save called exactly ONCE (only for passing attempt)
                assert mock_save.call_count == 1
                mock_save.assert_called_once_with('Aluminum', 'subtitle', 'test content')
                
                # Verify result shows 3 attempts
                assert result.success is True
                assert result.attempts == 3
                assert result.final_score == 7.0


class TestArchitectureCompliance:
    """Test system architecture compliance"""
    
    def test_no_double_save_pattern(self):
        """Test that content is not saved multiple times"""
        mock_client = Mock()
        mock_evaluator = Mock()
        
        # Pass on first attempt
        mock_eval_result = Mock(
            overall_score=8.0,
            realism_score=8.0,
            voice_authenticity=8.0,
            tonal_consistency=8.0,
            ai_tendencies=[],
            passes_quality_gate=True
        )
        mock_evaluator.evaluate.return_value = mock_eval_result
        
        generator = QualityGatedGenerator(
            api_client=mock_client,
            subjective_evaluator=mock_evaluator,
            max_attempts=5,
            quality_threshold=5.5
        )
        
        with patch.object(generator, '_generate_content_only') as mock_gen:
            mock_gen.return_value = {
                'content': 'test content',
                'length': 12,
                'word_count': 2,
                'saved': False  # Key: indicates not saved yet
            }
            
            with patch.object(generator, '_save_to_yaml') as mock_save:
                generator.generate('Aluminum', 'subtitle')
                
                # CRITICAL: Verify save called exactly once (no double-save)
                assert mock_save.call_count == 1
                
                # Verify generate_content_only returned saved=False
                generated_result = mock_gen.return_value
                assert generated_result['saved'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
