"""
Tests for Dynamic Threshold Learning System

Verifies that thresholds adapt based on database learning patterns
and fall back to defaults when insufficient data exists.
"""

import pytest
import sqlite3
from pathlib import Path
import tempfile
from datetime import datetime


class TestThresholdManager:
    """Test ThresholdManager dynamic threshold calculation."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database with test data."""
        db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_path = db_file.name
        db_file.close()
        
        # Create schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.executescript("""
            CREATE TABLE detection_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                material TEXT NOT NULL,
                component_type TEXT NOT NULL,
                generated_text TEXT NOT NULL,
                human_score REAL NOT NULL,
                ai_score REAL NOT NULL,
                success BOOLEAN NOT NULL,
                composite_quality_score REAL
            );
            
            CREATE TABLE subjective_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                topic TEXT NOT NULL,
                component_type TEXT NOT NULL,
                generated_text TEXT NOT NULL,
                overall_score REAL NOT NULL,
                passes_quality_gate BOOLEAN NOT NULL
            );
            
            CREATE TABLE learned_thresholds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                threshold_type TEXT NOT NULL,
                threshold_value REAL NOT NULL,
                sample_count INTEGER,
                confidence_level TEXT
            );
        """)
        
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink()
    
    def test_winston_threshold_with_insufficient_data(self, temp_db):
        """Should return default threshold when <10 samples."""
        from learning.threshold_manager import ThresholdManager
        
        manager = ThresholdManager(temp_db, min_samples=10)
        threshold = manager.get_winston_threshold(use_learned=True)
        
        assert threshold == 0.33  # Default
    
    def test_winston_threshold_with_sufficient_data(self, temp_db):
        """Should calculate learned threshold from 75th percentile."""
        from learning.threshold_manager import ThresholdManager
        
        # Insert 15 successful results with varying AI scores
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        ai_scores = [0.25, 0.28, 0.30, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.38, 0.40, 0.42, 0.45, 0.48, 0.50]
        for i, ai_score in enumerate(ai_scores):
            cursor.execute("""
                INSERT INTO detection_results 
                (timestamp, material, component_type, generated_text, human_score, ai_score, success, composite_quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), f"Material{i}", "caption", "test text", 1.0 - ai_score, ai_score, True, 0.85))
        
        conn.commit()
        conn.close()
        
        manager = ThresholdManager(temp_db, min_samples=10)
        threshold = manager.get_winston_threshold(use_learned=True)
        
        # Should be learned value (75th percentile * 0.95), not default
        assert threshold != 0.33
        assert 0.25 <= threshold <= 0.40  # Reasonable range
    
    def test_realism_threshold_with_insufficient_data(self, temp_db):
        """Should return default realism threshold when <10 samples."""
        from learning.threshold_manager import ThresholdManager
        
        manager = ThresholdManager(temp_db, min_samples=10)
        threshold = manager.get_realism_threshold(use_learned=True)
        
        assert threshold == 7.0  # Default
    
    def test_realism_threshold_with_sufficient_data(self, temp_db):
        """Should calculate learned threshold from 75th percentile."""
        from learning.threshold_manager import ThresholdManager
        
        # Insert 15 successful evaluations
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        scores = [7.0, 7.2, 7.4, 7.5, 7.6, 7.8, 8.0, 8.2, 8.4, 8.5, 8.6, 8.8, 9.0, 9.2, 9.5]
        for i, score in enumerate(scores):
            cursor.execute("""
                INSERT INTO subjective_evaluations
                (timestamp, topic, component_type, generated_text, overall_score, passes_quality_gate)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), f"Topic{i}", "caption", "test text", score, True))
        
        conn.commit()
        conn.close()
        
        manager = ThresholdManager(temp_db, min_samples=10)
        threshold = manager.get_realism_threshold(use_learned=True)
        
        # Should be learned value (75th percentile * 0.95), not default
        assert threshold != 7.0
        assert 6.0 <= threshold <= 9.0  # Reasonable range
    
    def test_use_learned_false_returns_defaults(self, temp_db):
        """Should return defaults when use_learned=False."""
        from learning.threshold_manager import ThresholdManager
        
        manager = ThresholdManager(temp_db)
        
        winston = manager.get_winston_threshold(use_learned=False)
        realism = manager.get_realism_threshold(use_learned=False)
        
        assert winston == 0.33
        assert realism == 7.0
    
    def test_get_all_thresholds(self, temp_db):
        """Should return dictionary with all thresholds."""
        from learning.threshold_manager import ThresholdManager
        
        manager = ThresholdManager(temp_db)
        thresholds = manager.get_all_thresholds(use_learned=False)
        
        assert 'winston_ai' in thresholds
        assert 'realism' in thresholds
        assert 'voice_authenticity' in thresholds
        assert 'tonal_consistency' in thresholds
        
        assert thresholds['winston_ai'] == 0.33
        assert thresholds['realism'] == 7.0
    
    def test_save_learned_thresholds(self, temp_db):
        """Should save learned thresholds to database."""
        from learning.threshold_manager import ThresholdManager
        
        manager = ThresholdManager(temp_db)
        thresholds = {
            'winston_ai': 0.305,
            'realism': 7.2
        }
        
        manager.save_learned_thresholds(thresholds)
        
        # Verify saved
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM learned_thresholds")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 2
    
    def test_get_threshold_history(self, temp_db):
        """Should retrieve historical threshold values."""
        from learning.threshold_manager import ThresholdManager
        
        manager = ThresholdManager(temp_db)
        
        # Save some historical values
        thresholds = {'winston_ai': 0.32}
        manager.save_learned_thresholds(thresholds)
        
        thresholds = {'winston_ai': 0.30}
        manager.save_learned_thresholds(thresholds)
        
        history = manager.get_threshold_history('winston_ai', limit=5)
        
        assert len(history) == 2
        assert all(isinstance(item, tuple) for item in history)
        assert all(len(item) == 2 for item in history)  # (timestamp, value)


class TestValidationConstantsDynamic:
    """Test ValidationConstants integration with dynamic thresholds."""
    
    def test_get_winston_threshold_method(self):
        """Should have get_winston_threshold method."""
        from generation.validation.constants import ValidationConstants
        
        threshold = ValidationConstants.get_winston_threshold(use_learned=False)
        assert threshold == 0.33
    
    def test_passes_winston_uses_dynamic_threshold(self):
        """Should use dynamic threshold in passes_winston."""
        from generation.validation.constants import ValidationConstants
        
        # With learned=False, should use default 0.33
        assert ValidationConstants.passes_winston(0.25, use_learned=False) == True  # 0.25 < 0.33
        assert ValidationConstants.passes_winston(0.35, use_learned=False) == False  # 0.35 > 0.33
    
    def test_deprecated_constant_still_works(self):
        """Deprecated WINSTON_AI_THRESHOLD should still return value."""
        from generation.validation.constants import ValidationConstants
        
        constants = ValidationConstants()
        # Should work but log deprecation warning
        threshold = constants.WINSTON_AI_THRESHOLD
        assert threshold == 0.33


class TestSweetSpotParameterIntegration:
    """Test that sweet spot parameters feed into generation."""
    
    @pytest.fixture
    def temp_db_with_sweet_spot(self):
        """Create database with sweet spot data."""
        db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_path = db_file.name
        db_file.close()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE sweet_spot_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material TEXT NOT NULL,
                component_type TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                temperature_min REAL,
                temperature_max REAL,
                temperature_median REAL,
                frequency_penalty_min REAL,
                frequency_penalty_max REAL,
                frequency_penalty_median REAL,
                presence_penalty_min REAL,
                presence_penalty_max REAL,
                presence_penalty_median REAL,
                trait_frequency_min REAL,
                trait_frequency_max REAL,
                trait_frequency_median REAL,
                technical_intensity_min INTEGER,
                technical_intensity_max INTEGER,
                technical_intensity_median INTEGER,
                imperfection_tolerance_min REAL,
                imperfection_tolerance_max REAL,
                imperfection_tolerance_median REAL,
                sentence_rhythm_variation_min REAL,
                sentence_rhythm_variation_max REAL,
                sentence_rhythm_variation_median REAL,
                sample_count INTEGER NOT NULL,
                max_human_score REAL NOT NULL,
                avg_human_score REAL NOT NULL,
                confidence_level TEXT NOT NULL,
                parameter_correlations TEXT,
                recommendations TEXT,
                UNIQUE(material, component_type)
            )
        """)
        
        # Insert sweet spot data
        cursor.execute("""
            INSERT INTO sweet_spot_recommendations
            (material, component_type, last_updated, temperature_min, temperature_max, temperature_median,
             sample_count, max_human_score, avg_human_score, confidence_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('*', '*', datetime.now().isoformat(), 0.7, 0.85, 0.78, 20, 0.95, 0.88, 'high'))
        
        conn.commit()
        conn.close()
        
        yield db_path
        
        Path(db_path).unlink()
    
    def test_load_sweet_spot_parameters(self, temp_db_with_sweet_spot):
        """Should load learned parameters from sweet spot."""
        from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
        
        db = WinstonFeedbackDatabase(temp_db_with_sweet_spot)
        sweet_spot = db.get_sweet_spot('*', '*')
        
        assert sweet_spot is not None
        assert 'parameters' in sweet_spot
        assert 'temperature' in sweet_spot['parameters']
        assert sweet_spot['parameters']['temperature']['median'] == 0.78


class TestEndToEndLearning:
    """Test complete learning cycle."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for E2E test."""
        db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_path = db_file.name
        db_file.close()
        yield db_path
        Path(db_path).unlink()
    
    def test_learning_cycle_closes_loop(self, temp_db):
        """Verify that learned data influences next generation."""
        from learning.threshold_manager import ThresholdManager
        
        # 1. Start with defaults (insufficient data)
        manager = ThresholdManager(temp_db, min_samples=5)
        initial_threshold = manager.get_winston_threshold(use_learned=True)
        assert initial_threshold == 0.33  # Default
        
        # 2. Add successful generation data
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Create schema
        cursor.execute("""
            CREATE TABLE detection_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, material TEXT, component_type TEXT,
                generated_text TEXT, human_score REAL, ai_score REAL,
                success BOOLEAN, composite_quality_score REAL
            )
        """)
        
        # Add 10 samples with lower AI scores (better quality)
        for i in range(10):
            cursor.execute("""
                INSERT INTO detection_results 
                (timestamp, material, component_type, generated_text, human_score, ai_score, success, composite_quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), "Test", "caption", "text", 0.75, 0.25, True, 0.85))
        
        conn.commit()
        conn.close()
        
        # 3. Threshold should now learn from data
        learned_threshold = manager.get_winston_threshold(use_learned=True)
        
        # Should be different from default and lower (more strict)
        assert learned_threshold != initial_threshold
        assert learned_threshold < initial_threshold  # Stricter based on good results


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
