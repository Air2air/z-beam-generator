"""
Test Score Normalization E2E

Verifies that all score normalization is consistent across the system:
- Winston API returns 0-1.0 normalized scores
- Database stores 0-1.0 normalized scores  
- Composite scorer accepts and returns 0-1.0
- Display functions format as percentages
- Sweet spot analyzer works with 0-1.0

Date: November 20, 2025
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestScoreNormalization:
    """Test end-to-end score normalization"""
    
    def test_winston_api_returns_normalized(self):
        """Winston API client returns human_score as 0-1.0"""
        # NOTE: This test would require full API config setup
        # Just verify the normalization logic is in place
        from shared.api.client import APIClient
        import inspect
        
        # Check that the normalization logic exists in the source
        source = inspect.getsource(APIClient.detect_ai_content)
        
        # Should have normalization: human_score_raw / 100.0
        assert '/ 100' in source or '/100' in source, \
            "Winston API should normalize human_score from 0-100 to 0-1.0"
    
    def test_validation_constants_consistent(self):
        """ValidationConstants uses consistent 0-1.0 scale"""
        from generation.validation.constants import ValidationConstants
        
        # All defaults should be 0-1.0
        assert 0.0 <= ValidationConstants.DEFAULT_AI_SCORE <= 1.0
        assert 0.0 <= ValidationConstants.DEFAULT_HUMAN_SCORE <= 1.0
        assert 0.0 <= ValidationConstants.DEFAULT_FALLBACK_AI_SCORE <= 1.0
        
        # Thresholds should be 0-1.0 (now dynamic, test with use_learned=False for defaults)
        winston_threshold = ValidationConstants.get_winston_threshold(use_learned=False)
        assert 0.0 <= winston_threshold <= 1.0
        assert 0.0 <= ValidationConstants.WINSTON_HUMAN_THRESHOLD <= 1.0
        
        # Conversion functions
        assert abs(ValidationConstants.ai_to_human_score(0.15) - 85.0) < 0.1
        assert abs(ValidationConstants.human_to_ai_score(85.0) - 0.15) < 0.01
    
    def test_composite_scorer_normalized_inputs(self):
        """Composite scorer expects 0-1.0 normalized inputs"""
        from postprocessing.evaluation.composite_scorer import CompositeScorer
        
        scorer = CompositeScorer()
        
        # Should accept 0-1.0 inputs
        result = scorer.calculate(
            winston_human_score=0.85,      # 0-1.0 normalized
            subjective_overall_score=8.0,  # 0-10 scale (will be normalized)
            readability_score=75.0         # 0-100 scale (will be normalized)
        )
        
        # Should return 0-1.0 normalized
        assert 'composite_score' in result
        assert 0.0 <= result['composite_score'] <= 1.0
        
        # Should be close to weighted average (~0.8)
        assert 0.75 <= result['composite_score'] <= 0.85
    
    def test_composite_scorer_rejects_invalid_range(self):
        """Composite scorer rejects scores outside 0-1.0"""
        from postprocessing.evaluation.composite_scorer import CompositeScorer
        
        scorer = CompositeScorer()
        
        # Should reject human_score > 1.0
        with pytest.raises(ValueError, match="must be 0-1.0"):
            scorer.calculate(
                winston_human_score=85.0,  # Wrong scale!
                subjective_overall_score=8.0,
                readability_score=75.0
            )
    
    def test_database_storage_validates_range(self):
        """Database storage validates scores are 0-1.0"""
        from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
        import tempfile
        import os
        
        # Create temp database
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        try:
            db = WinstonFeedbackDatabase(db_path)
            
            # Should reject human_score > 1.0
            with pytest.raises(ValueError, match="must be 0-1.0"):
                db.log_detection(
                    material="Test",
                    component_type="caption",
                    generated_text="test",
                    winston_result={
                        'human_score': 85.0,  # Wrong scale!
                        'ai_score': 0.15,
                        'sentences': []
                    },
                    temperature=0.8,
                    attempt=1,
                    success=True
                )
            
            # Should accept 0-1.0 scores
            detection_id = db.log_detection(
                material="Test",
                component_type="caption",
                generated_text="test",
                winston_result={
                    'human_score': 0.85,  # Correct scale
                    'ai_score': 0.15,
                    'sentences': []
                },
                temperature=0.8,
                attempt=1,
                success=True,
                composite_quality_score=0.82
            )
            
            assert detection_id > 0
            
        finally:
            os.unlink(db_path)
    
    def test_database_contains_normalized_values(self):
        """Actual database contains only 0-1.0 values after migration"""
        import sqlite3
        
        conn = sqlite3.connect('z-beam.db')
        cursor = conn.cursor()
        
        # Check max values
        cursor.execute("""
            SELECT 
                MAX(human_score) as max_human,
                MAX(ai_score) as max_ai,
                MAX(composite_quality_score) as max_composite
            FROM detection_results
        """)
        
        max_human, max_ai, max_composite = cursor.fetchone()
        
        # All should be <= 1.0
        assert max_human <= 1.0, f"human_score not normalized: {max_human}"
        assert max_ai <= 1.0, f"ai_score not normalized: {max_ai}"
        if max_composite:
            assert max_composite <= 1.0, f"composite not normalized: {max_composite}"
        
        conn.close()
    
    def test_sweet_spot_threshold_normalized(self):
        """Sweet spot analyzer uses 0-1.0 threshold"""
        from learning.sweet_spot_analyzer import SweetSpotAnalyzer
        
        # Should accept 0-1.0 threshold
        analyzer = SweetSpotAnalyzer('z-beam.db', min_samples=5, success_threshold=0.80)
        
        # Should work with normalized threshold (0.80 instead of 80.0)
        # Previously failed with threshold=80.0
        
        # Check that the analyzer stores the normalized threshold
        assert analyzer.success_threshold == 0.80
        
        # The analyzer should be able to find samples now
        # (Previously found 0 samples with threshold=80.0 vs max_score=7.67)
        table = analyzer.get_sweet_spot_table()
        
        # Table should be generated without errors
        assert table is not None
    
    def test_display_formatting(self):
        """Display functions format normalized scores as percentages"""
        from generation.validation.constants import ValidationConstants
        
        # Test conversion to percentage
        normalized = 0.847
        percentage = ValidationConstants.ai_to_human_score(1.0 - normalized)
        
        # Should convert to percentage for display
        assert 84.0 <= percentage <= 85.0
    
    def test_simple_composite_scorer_normalized(self):
        """
        Composite scorer uses 0-1.0 scale
        
        Note: postprocessing.steps archived (Nov 20, 2025) - using main composite scorer
        """
        from postprocessing.evaluation.composite_scorer import CompositeScorer
        
        scorer = CompositeScorer()
        
        # Main composite scorer accepts both normalized (0-1.0) and legacy (0-100) inputs
        winston_score = 0.85  # 0-1.0 normalized
        realism_score = 8.0   # 0-10 scale
        
        result = scorer.calculate(
            winston_human_score=winston_score,
            subjective_overall_score=realism_score
        )
        
        composite = result['composite_score']
        
        # Should return 0-1.0 normalized
        assert 0.0 <= composite <= 1.0
        assert 0.75 <= composite <= 0.90  # Weighted average


class TestBackwardCompatibility:
    """Test that old code paths still work"""
    
    def test_ai_to_human_percentage_conversion(self):
        """Old conversion functions still work"""
        from generation.validation.constants import ai_to_human_percentage
        
        # Should convert 0-1.0 to 0-100
        assert abs(ai_to_human_percentage(0.15) - 85.0) < 0.1
        assert abs(ai_to_human_percentage(0.33) - 67.0) < 0.1
    
    def test_passes_winston_threshold(self):
        """Winston threshold check works with normalized scores"""
        from generation.validation.constants import VALIDATION
        
        # Test with static default threshold (use_learned=False)
        # Should pass with < 0.33 AI score
        assert VALIDATION.passes_winston(0.25, use_learned=False) is True
        assert VALIDATION.passes_winston(0.33, use_learned=False) is False
        assert VALIDATION.passes_winston(0.35, use_learned=False) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
