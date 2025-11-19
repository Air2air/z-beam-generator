#!/usr/bin/env python3
"""
Comprehensive test suite for Winston AI Learning System

Tests all 4 learning modules:
- PatternLearner: N-gram pattern extraction and risk scoring
- TemperatureAdvisor: Statistical temperature optimization
- PromptOptimizer: Dynamic prompt enhancement
- SuccessPredictor: Multi-model success prediction
"""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

# Import learning modules
from processing.learning.pattern_learner import PatternLearner
from processing.learning.temperature_advisor import TemperatureAdvisor
from processing.learning.prompt_optimizer import PromptOptimizer
from processing.learning.success_predictor import SuccessPredictor
from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
from shared.api.client import APIClient


class TestWinstonLearningSystem(unittest.TestCase):
    """Test suite for Winston AI learning system"""

    def setUp(self):
        """Set up test fixtures with temporary database"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Initialize database with schema
        self.feedback_db = WinstonFeedbackDatabase(self.db_path)
        
        # Initialize learning modules
        self.pattern_learner = PatternLearner(self.db_path)
        self.temperature_advisor = TemperatureAdvisor(self.db_path)
        self.prompt_optimizer = PromptOptimizer(self.db_path)
        self.success_predictor = SuccessPredictor(self.db_path)
        
        # Create mock Winston API client (no real API calls in tests)
        mock_config = Mock()
        mock_config.base_url = "https://api.gowinston.ai"
        mock_config.api_key = "test_key"
        mock_config.model = "winston"
        mock_config.get = lambda key: getattr(mock_config, key, None)
        self.winston_client = APIClient(config=mock_config)

    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    # ========================================================================
    # PATTERN LEARNER TESTS
    # ========================================================================

    def test_pattern_learner_empty_database(self):
        """Test PatternLearner handles empty database gracefully"""
        result = self.pattern_learner.learn_patterns()
        
        self.assertIsInstance(result, dict)
        # Should have low sample count
        self.assertEqual(result.get('sample_size', 0), 0)

    def test_pattern_learner_with_data(self):
        """Test PatternLearner learns patterns from sample data"""
        # Add sample detection results
        self._add_sample_data()

        # Learn patterns
        result = self.pattern_learner.learn_patterns()

        self.assertIsInstance(result, dict)
        self.assertIn('risky_patterns', result)
        self.assertIn('safe_patterns', result)
        self.assertIn('stats', result)
        self.assertGreater(result['stats']['total_samples'], 0)

    def test_pattern_learner_material_filtering(self):
        """Test PatternLearner filters by material"""
        self._add_sample_data()

        # Learn patterns for specific material
        result = self.pattern_learner.learn_patterns(material="Aluminum")

        self.assertIsInstance(result, dict)
        # Method returns risky_patterns, safe_patterns, stats - not 'material' key
        self.assertIn('risky_patterns', result)
        self.assertIn('safe_patterns', result)
        self.assertIn('stats', result)

    def test_pattern_learner_dynamic_blacklist(self):
        """Test PatternLearner generates dynamic blacklist"""
        self._add_sample_data()

        # Get blacklist (patterns that fail >80%)
        blacklist = self.pattern_learner.get_dynamic_blacklist(threshold=0.8)

        self.assertIsInstance(blacklist, list)
        # Blacklist may be empty if no patterns exceed threshold
        for pattern in blacklist:
            self.assertIsInstance(pattern, str)

    def test_pattern_learner_check_text(self):
        """Test PatternLearner checks text for risky patterns"""
        self._add_sample_data()

        # Check sample text
        text = "This demonstrates clear evidence of laser cleaning effectiveness."
        result = self.pattern_learner.check_text_for_patterns(text, threshold=0.7)

        self.assertIsInstance(result, dict)
        self.assertIn('has_risky_patterns', result)
        self.assertIn('detected_patterns', result)  # Fixed: actual return key
        self.assertIsInstance(result['has_risky_patterns'], bool)

    # ========================================================================
    # TEMPERATURE ADVISOR TESTS
    # ========================================================================

    def test_temperature_advisor_empty_database(self):
        """Test TemperatureAdvisor handles empty database gracefully"""
        result = self.temperature_advisor.get_optimal_temperature(
            material="Aluminum",
            component_type="caption"
        )

        self.assertIsInstance(result, dict)
        # Should return default or indicate insufficient data
        self.assertIn('confidence', result)
        self.assertEqual(result.get('sample_size', 0), 0)

    def test_temperature_advisor_with_data(self):
        """Test TemperatureAdvisor finds optimal temperature"""
        self._add_sample_data()

        result = self.temperature_advisor.get_optimal_temperature(
            material="Aluminum",
            component_type="caption"
        )

        self.assertIsInstance(result, dict)
        if result.get('optimal_temperature') is not None:
            self.assertGreater(result['optimal_temperature'], 0.0)
            self.assertLessEqual(result['optimal_temperature'], 1.0)

    def test_temperature_advisor_comparison(self):
        """Test TemperatureAdvisor compares temperature buckets"""
        self._add_sample_data()

        comparison = self.temperature_advisor.compare_temperatures(
            temps=[0.6, 0.7, 0.8, 0.9]
        )

        self.assertIsInstance(comparison, dict)
        self.assertIn('results', comparison)
        self.assertIsInstance(comparison['results'], dict)

    def test_temperature_advisor_adjustment_suggestion(self):
        """Test TemperatureAdvisor suggests adjustments"""
        self._add_sample_data()

        suggestion = self.temperature_advisor.get_adjustment_suggestion(
            current_temp=0.7,
            recent_failures=2,
            material="Aluminum",
            component_type="caption"
        )

        self.assertIsInstance(suggestion, dict)
        self.assertIn('action', suggestion)
        self.assertIn(suggestion['action'], ['adjust', 'explore', 'keep'])

    # ========================================================================
    # PROMPT OPTIMIZER TESTS
    # ========================================================================

    def test_prompt_optimizer_empty_database(self):
        """Test PromptOptimizer handles empty database gracefully"""
        base_prompt = "Generate a caption for {material}."
        
        result = self.prompt_optimizer.optimize_prompt(
            base_prompt,
            material="Aluminum",
            component_type="caption"
        )

        self.assertIsInstance(result, dict)
        self.assertIn('optimized_prompt', result)
        # Should return base prompt if no data
        self.assertIn(base_prompt, result['optimized_prompt'])

    def test_prompt_optimizer_with_data(self):
        """Test PromptOptimizer enhances prompts"""
        self._add_sample_data()

        base_prompt = "Generate a caption for {material}."
        
        result = self.prompt_optimizer.optimize_prompt(
            base_prompt,
            material="Aluminum",
            component_type="caption"
        )

        self.assertIsInstance(result, dict)
        self.assertIn('optimized_prompt', result)
        self.assertIn('patterns_analyzed', result)
        self.assertIsInstance(result['optimized_prompt'], str)

    def test_prompt_optimizer_generate_variants(self):
        """Test PromptOptimizer generates prompt variants"""
        self._add_sample_data()

        base_prompt = "Generate a caption for {material}."
        
        variants = self.prompt_optimizer.generate_variants(
            base_prompt,
            num_variants=3
        )

        self.assertIsInstance(variants, list)
        self.assertLessEqual(len(variants), 3)
        for variant in variants:
            self.assertIsInstance(variant, dict)
            self.assertIn('prompt', variant)
            self.assertIn('strategy', variant)

    def test_prompt_optimizer_effectiveness_report(self):
        """Test PromptOptimizer generates effectiveness report"""
        self._add_sample_data()

        report = self.prompt_optimizer.get_prompt_effectiveness_report()

        self.assertIsInstance(report, dict)
        # Method returns 'status' key - either 'insufficient_data' or 'analyzed'
        self.assertIn('status', report)

    # ========================================================================
    # SUCCESS PREDICTOR TESTS
    # ========================================================================

    def test_success_predictor_empty_database(self):
        """Test SuccessPredictor handles empty database gracefully"""
        result = self.success_predictor.predict_success(
            material="Aluminum",
            component_type="caption",
            temperature=0.7,
            attempt_number=1
        )

        self.assertIsInstance(result, dict)
        self.assertIn('success_probability', result)
        self.assertIn('confidence', result)
        # Should have low confidence with no data
        self.assertEqual(result.get('sample_size', 0), 0)

    def test_success_predictor_with_data(self):
        """Test SuccessPredictor predicts success probability"""
        self._add_sample_data()

        result = self.success_predictor.predict_success(
            material="Aluminum",
            component_type="caption",
            temperature=0.7,
            attempt_number=1
        )

        self.assertIsInstance(result, dict)
        self.assertIn('success_probability', result)
        self.assertIn('confidence', result)
        # Confidence is string not float
        self.assertIn(result['confidence'], ['high', 'medium', 'low', 'none'])

    def test_success_predictor_risk_assessment(self):
        """Test SuccessPredictor generates risk assessment"""
        self._add_sample_data()

        assessment = self.success_predictor.get_risk_assessment(
            material="Aluminum",
            component_type="caption"
        )

        self.assertIsInstance(assessment, dict)
        self.assertIn('risk_level', assessment)
        self.assertIn(assessment['risk_level'], ['low', 'medium', 'high', 'unknown'])

    def test_success_predictor_multi_model(self):
        """Test SuccessPredictor uses multiple models"""
        self._add_sample_data()

        result = self.success_predictor.predict_success(
            material="Steel",
            component_type="subtitle",
            temperature=0.8,
            attempt_number=2
        )

        self.assertIsInstance(result, dict)
        # Should have success_probability even with sparse data
        self.assertIn('success_probability', result)

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_end_to_end_learning_workflow(self):
        """Test complete learning workflow from detection to optimization"""
        # 1. Add detection results
        self._add_sample_data()

        # 2. Learn patterns
        patterns = self.pattern_learner.learn_patterns()
        self.assertGreater(patterns['stats']['total_samples'], 0)

        # 3. Get optimal temperature
        temp_result = self.temperature_advisor.get_optimal_temperature(
            material="Aluminum",
            component_type="caption"
        )
        self.assertIsInstance(temp_result, dict)

        # 4. Optimize prompt
        base_prompt = "Generate content for {material}."
        optimized = self.prompt_optimizer.optimize_prompt(
            base_prompt,
            material="Aluminum",
            component_type="caption"
        )
        self.assertIn('optimized_prompt', optimized)

        # 5. Predict success
        prediction = self.success_predictor.predict_success(
            material="Aluminum",
            component_type="caption",
            temperature=0.7,
            attempt_number=1
        )
        self.assertIn('success_probability', prediction)

    def test_database_persistence(self):
        """Test learning modules read from persistent database"""
        # Add data
        self._add_sample_data()

        # Create new module instances (simulating restart)
        new_learner = PatternLearner(self.db_path)
        result = new_learner.learn_patterns()

        # Should still have data
        self.assertIn('stats', result)
        self.assertGreater(result['stats']['total_samples'], 0)

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _add_sample_data(self):
        """Add sample detection results to database"""
        samples = [
            {
                'material': 'Aluminum',
                'component_type': 'caption',
                'temperature': 0.7,
                'attempt': 1,
                'content': 'This demonstrates clear evidence of laser cleaning on aluminum surfaces.',
                'human_score': 45.0,
                'passed': False
            },
            {
                'material': 'Aluminum',
                'component_type': 'caption',
                'temperature': 0.7,
                'attempt': 2,
                'content': 'Laser cleaning removes surface contaminants from aluminum without damage.',
                'human_score': 75.0,
                'passed': True
            },
            {
                'material': 'Steel',
                'component_type': 'subtitle',
                'temperature': 0.8,
                'attempt': 1,
                'content': 'Industrial laser cleaning for steel surfaces.',
                'human_score': 65.0,
                'passed': True
            },
            {
                'material': 'Steel',
                'component_type': 'caption',
                'temperature': 0.6,
                'attempt': 1,
                'content': 'This reveals that laser cleaning is effective for steel.',
                'human_score': 40.0,
                'passed': False
            },
            {
                'material': 'Copper',
                'component_type': 'caption',
                'temperature': 0.7,
                'attempt': 1,
                'content': 'Copper surfaces benefit from precise laser cleaning technology.',
                'human_score': 80.0,
                'passed': True
            }
        ]

        for sample in samples:
            winston_result = {
                'overall_score': sample['human_score'],
                'classification': 'human' if sample['passed'] else 'ai',
                'analysis': {
                    'sentences': [
                        {
                            'text': sample['content'],
                            'ai_probability': 100 - sample['human_score']
                        }
                    ]
                }
            }

            self.feedback_db.log_detection(
                material=sample['material'],
                component_type=sample['component_type'],
                generated_text=sample['content'],
                winston_result=winston_result,
                temperature=sample['temperature'],
                attempt=sample['attempt'],
                success=sample['passed'],
                failure_analysis={'failure_type': 'low_human_score'} if not sample['passed'] else None
            )


class TestWinstonFeedbackDB(unittest.TestCase):
    """Test suite for Winston feedback database"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.feedback_db = WinstonFeedbackDatabase(self.db_path)

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_database_initialization(self):
        """Test database creates all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check for all required tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        expected_tables = {
            'detection_results',
            'sentence_analysis',
            'ai_patterns',
            'corrections',
            'learning_insights'
        }

        self.assertTrue(expected_tables.issubset(tables))
        conn.close()

    def test_log_detection(self):
        """Test logging detection results"""
        winston_result = {
            'overall_score': 75.0,
            'classification': 'human',
            'analysis': {'sentences': []}
        }

        detection_id = self.feedback_db.log_detection(
            material="Aluminum",
            component_type="caption",
            generated_text="Test content",
            winston_result=winston_result,
            temperature=0.7,
            attempt=1,
            success=True
        )

        self.assertIsInstance(detection_id, int)
        self.assertGreater(detection_id, 0)

    def test_add_correction(self):
        """Test adding manual correction"""
        # First log a detection
        winston_result = {
            'overall_score': 45.0,
            'classification': 'ai',
            'analysis': {'sentences': []}
        }

        detection_id = self.feedback_db.log_detection(
            material="Aluminum",
            component_type="caption",
            generated_text="Test content",
            winston_result=winston_result,
            temperature=0.7,
            attempt=1,
            success=False
        )

        # Add correction
        correction_id = self.feedback_db.add_correction(
            detection_result_id=detection_id,
            original_text="Test content",
            corrected_text="Corrected test content",
            correction_type="phrasing",
            notes="Fixed AI detection patterns"
        )

        self.assertIsInstance(correction_id, int)
        self.assertGreater(correction_id, 0)

    def test_get_stats(self):
        """Test getting database statistics"""
        # Add some data
        for i in range(5):
            winston_result = {
                'overall_score': 60.0 + i * 10,
                'classification': 'human' if i % 2 == 0 else 'ai',
                'analysis': {'sentences': []}
            }
            self.feedback_db.log_detection(
                material="Aluminum",
                component_type="caption",
                generated_text=f"Test content {i}",
                winston_result=winston_result,
                temperature=0.7,
                attempt=1,
                success=i % 2 == 0
            )

        stats = self.feedback_db.get_stats()

        self.assertIsInstance(stats, dict)
        self.assertIn('total_detections', stats)
        self.assertEqual(stats['total_detections'], 5)


if __name__ == '__main__':
    unittest.main()
