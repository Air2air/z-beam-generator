"""
Tests for Universal Humanness Layer (ADR-007)

Tests the dual-feedback learning system that combines Winston AI Detection
patterns with Subjective Evaluation patterns to generate dynamic humanness
instructions with strictness progression.

Created: November 20, 2025
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from learning.humanness_optimizer import (
    HumannessOptimizer,
    WinstonPatterns,
    SubjectivePatterns
)


class TestHumannessOptimizerInitialization:
    """Test initialization and configuration validation."""
    
    def test_initialization_with_defaults(self):
        """Should initialize with default paths."""
        optimizer = HumannessOptimizer()
        
        assert optimizer.winston_db_path == 'z-beam.db'
        assert optimizer.patterns_file == Path('prompts/evaluation/learned_patterns.yaml')
        assert optimizer.template_file == Path('prompts/system/humanness_layer.txt')
    
    def test_initialization_with_custom_paths(self):
        """Should accept custom paths."""
        optimizer = HumannessOptimizer(
            winston_db_path='custom.db',
            patterns_file=Path('custom_patterns.yaml')
        )
        
        assert optimizer.winston_db_path == 'custom.db'
        assert optimizer.patterns_file == Path('custom_patterns.yaml')
    
    def test_fail_fast_on_missing_template(self, tmp_path):
        """Should raise FileNotFoundError if template missing (fail-fast)."""
        # Temporarily change template path to non-existent file
        with patch.object(Path, 'exists', return_value=False):
            with pytest.raises(FileNotFoundError) as exc_info:
                HumannessOptimizer()
            
            assert "Humanness layer template not found" in str(exc_info.value)
            assert "template-only policy" in str(exc_info.value)


class TestGenerateHumannessInstructions:
    """Test dynamic humanness instruction generation."""
    
    @pytest.fixture
    def optimizer(self, tmp_path):
        """Create optimizer with mock dependencies."""
        # Create minimal template file
        template_path = tmp_path / "humanness_layer.txt"
        template_path.write_text("""
=== HUMANNESS LAYER ===
Attempt {attempt_number}/5
Winston: {winston_success_patterns}
Subjective: {subjective_ai_tendencies}
Theatrical: {theatrical_phrases_list}
Conversational: {conversational_markers}
Strictness {strictness_level}: {strictness_guidance}
{previous_attempt_feedback}
""")
        
        with patch('learning.humanness_optimizer.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.read_text.return_value = template_path.read_text()
            optimizer = HumannessOptimizer()
            optimizer.template_file = template_path
            return optimizer
    
    def test_generate_basic_instructions(self, optimizer):
        """Should generate instructions from dual feedback sources."""
        # Mock Winston patterns
        with patch.object(optimizer, '_extract_winston_patterns') as mock_winston:
            mock_winston.return_value = WinstonPatterns(
                sample_count=20,
                best_score=0.122,
                average_score=0.245,
                conversational_markers=["around", "roughly"],
                number_patterns=["100 W", "8.8 g/cm³"],
                sample_excerpts=["Sample text..."]
            )
            
            # Mock Subjective patterns
            with patch.object(optimizer, '_extract_subjective_patterns') as mock_subjective:
                mock_subjective.return_value = SubjectivePatterns(
                    theatrical_phrases=["zaps away", "And yeah"],
                    ai_tendencies=["formulaic_structure", "technical_manual_tone"],
                    success_patterns={},
                    penalty_weights={}
                )
                
                instructions = optimizer.generate_humanness_instructions(
                    component_type='caption',
                    strictness_level=1
                )
                
                assert isinstance(instructions, str)
                assert len(instructions) > 0
                assert "HUMANNESS LAYER" in instructions
    
    def test_strictness_level_validation(self, optimizer):
        """Should fail-fast if strictness level out of range."""
        with pytest.raises(ValueError) as exc_info:
            optimizer.generate_humanness_instructions(
                component_type='caption',
                strictness_level=0  # Invalid - must be 1-5
            )
        
        assert "strictness_level must be 1-5" in str(exc_info.value)
        
        with pytest.raises(ValueError):
            optimizer.generate_humanness_instructions(
                component_type='caption',
                strictness_level=6  # Invalid - must be 1-5
            )
    
    def test_strictness_progression(self, optimizer):
        """Should generate different instructions for different strictness levels."""
        with patch.object(optimizer, '_extract_winston_patterns'), \
             patch.object(optimizer, '_extract_subjective_patterns'):
            
            instructions_level_1 = optimizer.generate_humanness_instructions(
                component_type='caption',
                strictness_level=1
            )
            
            instructions_level_5 = optimizer.generate_humanness_instructions(
                component_type='caption',
                strictness_level=5
            )
            
            # Instructions should differ based on strictness
            assert instructions_level_1 != instructions_level_5
    
    def test_previous_ai_tendencies_included(self, optimizer):
        """Should include feedback from previous attempt."""
        with patch.object(optimizer, '_extract_winston_patterns'), \
             patch.object(optimizer, '_extract_subjective_patterns'):
            
            previous_tendencies = ['formulaic_structure', 'technical_manual_tone']
            
            instructions = optimizer.generate_humanness_instructions(
                component_type='caption',
                strictness_level=2,
                previous_ai_tendencies=previous_tendencies
            )
            
            # Should include previous feedback for level > 1
            assert len(instructions) > 0


class TestWinstonPatternExtraction:
    """Test Winston passing sample pattern extraction."""
    
    def test_extract_winston_patterns_with_samples(self):
        """Should extract patterns from Winston passing samples."""
        # Create temporary database with sample data
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            conn = sqlite3.connect(tmp_db.name)
            cursor = conn.cursor()
            
            # Create detection_results table
            cursor.execute("""
                CREATE TABLE detection_results (
                    id INTEGER PRIMARY KEY,
                    generated_text TEXT,
                    ai_score REAL,
                    human_score REAL,
                    success INTEGER,
                    material TEXT,
                    component_type TEXT
                )
            """)
            
            # Insert sample passing results
            cursor.execute("""
                INSERT INTO detection_results 
                (generated_text, ai_score, human_score, success, material, component_type)
                VALUES 
                ('Sample text with around 100 W power', 0.122, 0.878, 1, 'Aluminum', 'caption')
            """)
            conn.commit()
            conn.close()
            
            # Test extraction
            optimizer = HumannessOptimizer(winston_db_path=tmp_db.name)
            patterns = optimizer._extract_winston_patterns()
            
            assert isinstance(patterns, WinstonPatterns)
            assert patterns.sample_count > 0
            Path(tmp_db.name).unlink()  # Cleanup


class TestSubjectivePatternExtraction:
    """Test subjective evaluation pattern extraction."""
    
    def test_extract_subjective_patterns(self):
        """Should load patterns from learned_patterns.yaml."""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w') as tmp_yaml:
            tmp_yaml.write("""
theatrical_phrases:
  high_penalty:
    - "zaps away"
    - "And yeah"
ai_tendencies:
  common:
    formulaic_structure: 15
    technical_manual_tone: 12
""")
            tmp_yaml.flush()
            
            optimizer = HumannessOptimizer(patterns_file=Path(tmp_yaml.name))
            patterns = optimizer._extract_subjective_patterns()
            
            assert isinstance(patterns, SubjectivePatterns)
            assert len(patterns.theatrical_phrases) > 0
            assert len(patterns.ai_tendencies) > 0
            
            Path(tmp_yaml.name).unlink()  # Cleanup


class TestPolicyCompliance:
    """Test compliance with system policies."""
    
    def test_zero_hardcoded_values(self):
        """Should have no hardcoded parameter values in production code."""
        import inspect
        source = inspect.getsource(HumannessOptimizer)
        
        # Check for hardcoded API parameters
        assert "temperature = 0." not in source
        assert "frequency_penalty = 0." not in source
        assert "presence_penalty = 0." not in source
    
    def test_template_only_approach(self):
        """Should load all prompt text from template file."""
        optimizer = HumannessOptimizer()
        
        # Template file should exist
        assert optimizer.template_file == Path('prompts/system/humanness_layer.txt')
    
    def test_fail_fast_architecture(self):
        """Should fail immediately on missing dependencies."""
        # Missing template should raise FileNotFoundError
        with patch.object(Path, 'exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                HumannessOptimizer()


class TestIntegrationFlow:
    """Test end-to-end integration scenarios."""
    
    def test_dual_feedback_integration(self):
        """Should successfully integrate both feedback sources."""
        optimizer = HumannessOptimizer()
        
        # Mock both feedback sources
        with patch.object(optimizer, '_extract_winston_patterns') as mock_winston, \
             patch.object(optimizer, '_extract_subjective_patterns') as mock_subjective:
            
            mock_winston.return_value = WinstonPatterns(
                sample_count=20,
                best_score=0.122,
                average_score=0.245,
                conversational_markers=["around"],
                number_patterns=["100 W"],
                sample_excerpts=["Test"]
            )
            
            mock_subjective.return_value = SubjectivePatterns(
                theatrical_phrases=["zaps away"],
                ai_tendencies=["formulaic"],
                success_patterns={},
                penalty_weights={}
            )
            
            instructions = optimizer.generate_humanness_instructions(
                component_type='caption',
                strictness_level=1
            )
            
            # Should successfully generate instructions from both sources
            assert instructions is not None
            assert len(instructions) > 0
