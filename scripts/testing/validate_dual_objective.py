#!/usr/bin/env python3
"""
Pre-Flight Validation for Dual-Objective Optimization System

Runs comprehensive checks before allowing production generation.
Fails fast with clear error messages if any component is missing or broken.
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ValidationResult:
    """Result of a validation check."""
    
    def __init__(self, name: str, passed: bool, message: str, critical: bool = True):
        self.name = name
        self.passed = passed
        self.message = message
        self.critical = critical
    
    def __str__(self):
        icon = "✅" if self.passed else ("❌" if self.critical else "⚠️")
        return f"{icon} {self.name}: {self.message}"


class DualObjectiveValidator:
    """Validates dual-objective optimization system integrity."""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("=" * 80)
        print("🔍 DUAL-OBJECTIVE OPTIMIZATION PRE-FLIGHT VALIDATION")
        print("=" * 80)
        print()
        
        # Component existence checks
        self.check_realism_optimizer_exists()
        self.check_database_schema()
        self.check_subjective_evaluator_fields()
        self.check_generator_integration()
        
        # Logic validation checks
        self.check_realism_optimizer_logic()
        self.check_tendency_mappings()
        self.check_combined_scoring()
        
        # Integration checks
        self.check_retry_loop_integration()
        self.check_database_logging()
        self.check_batch_test_display()
        
        # Print results
        print("\n" + "=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)
        
        passed_count = sum(1 for r in self.results if r.passed)
        critical_failed = [r for r in self.results if not r.passed and r.critical]
        warnings = [r for r in self.results if not r.passed and not r.critical]
        
        for result in self.results:
            print(result)
        
        print()
        print(f"Passed: {passed_count}/{len(self.results)}")
        
        if critical_failed:
            print(f"\n❌ CRITICAL FAILURES: {len(critical_failed)}")
            print("System is NOT ready for production use!")
            print("\nFailed checks:")
            for r in critical_failed:
                print(f"  - {r.name}")
            return False
        
        if warnings:
            print(f"\n⚠️  WARNINGS: {len(warnings)}")
            for r in warnings:
                print(f"  - {r.name}: {r.message}")
        
        print("\n✅ ALL CRITICAL CHECKS PASSED - System ready for production!")
        return True
    
    def check_realism_optimizer_exists(self):
        """Check RealismOptimizer class exists and is importable."""
        try:
            from learning.realism_optimizer import RealismOptimizer
            optimizer = RealismOptimizer()
            
            # Check required methods
            required_methods = [
                'analyze_ai_tendencies',
                'suggest_parameters',
                'calculate_combined_score',
                'should_retry'
            ]
            
            missing = [m for m in required_methods if not hasattr(optimizer, m)]
            
            if missing:
                self.results.append(ValidationResult(
                    "RealismOptimizer Methods",
                    False,
                    f"Missing methods: {', '.join(missing)}",
                    critical=True
                ))
            else:
                self.results.append(ValidationResult(
                    "RealismOptimizer Class",
                    True,
                    "Class exists with all required methods"
                ))
        except Exception as e:
            self.results.append(ValidationResult(
                "RealismOptimizer Import",
                False,
                f"Failed to import: {e}",
                critical=True
            ))
    
    def check_database_schema(self):
        """Check realism_learning table exists in database."""
        try:
            from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
            import tempfile
            import sqlite3
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
                db_path = f.name
            
            try:
                db = WinstonFeedbackDatabase(db_path)
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='realism_learning'
                """)
                
                if not cursor.fetchone():
                    self.results.append(ValidationResult(
                        "Realism Learning Table",
                        False,
                        "Table 'realism_learning' not found in database schema",
                        critical=True
                    ))
                else:
                    # Check required columns
                    cursor.execute("PRAGMA table_info(realism_learning)")
                    columns = {row[1] for row in cursor.fetchall()}
                    
                    required_columns = {
                        'id', 'timestamp', 'material', 'component_type',
                        'original_realism_score', 'detected_ai_tendencies',
                        'original_parameters', 'parameter_adjustments',
                        'adjustment_rationale', 'new_realism_score',
                        'improvement', 'success'
                    }
                    
                    missing_columns = required_columns - columns
                    
                    if missing_columns:
                        self.results.append(ValidationResult(
                            "Realism Learning Schema",
                            False,
                            f"Missing columns: {', '.join(missing_columns)}",
                            critical=True
                        ))
                    else:
                        self.results.append(ValidationResult(
                            "Realism Learning Table",
                            True,
                            "Table exists with all required columns"
                        ))
                
                conn.close()
            finally:
                if os.path.exists(db_path):
                    os.unlink(db_path)
        except Exception as e:
            self.results.append(ValidationResult(
                "Database Schema Check",
                False,
                f"Failed: {e}",
                critical=True
            ))
    
    def check_subjective_evaluator_fields(self):
        """Check SubjectiveEvaluationResult has realism fields."""
        try:
            from postprocessing.evaluation.evaluator import SubjectiveEvaluationResult
            import inspect
            
            sig = inspect.signature(SubjectiveEvaluationResult)
            params = set(sig.parameters.keys())
            
            required_fields = {
                'realism_score',
                'voice_authenticity',
                'tonal_consistency',
                'ai_tendencies'
            }
            
            missing = required_fields - params
            
            if missing:
                self.results.append(ValidationResult(
                    "SubjectiveEvaluationResult Fields",
                    False,
                    f"Missing fields: {', '.join(missing)}",
                    critical=True
                ))
            else:
                self.results.append(ValidationResult(
                    "SubjectiveEvaluationResult Fields",
                    True,
                    "All realism fields present"
                ))
        except Exception as e:
            self.results.append(ValidationResult(
                "SubjectiveEvaluationResult Check",
                False,
                f"Failed: {e}",
                critical=True
            ))
    
    def check_generator_integration(self):
        """Check DynamicGenerator initializes RealismOptimizer."""
        try:
            from generation.core.legacy.generator import DynamicGenerator
            import inspect
            
            source = inspect.getsource(DynamicGenerator._init_components)
            
            if 'RealismOptimizer' not in source:
                self.results.append(ValidationResult(
                    "Generator RealismOptimizer Init",
                    False,
                    "DynamicGenerator doesn't import/initialize RealismOptimizer",
                    critical=True
                ))
            elif 'self.realism_optimizer' not in source:
                self.results.append(ValidationResult(
                    "Generator RealismOptimizer Init",
                    False,
                    "DynamicGenerator doesn't set self.realism_optimizer",
                    critical=True
                ))
            else:
                self.results.append(ValidationResult(
                    "Generator RealismOptimizer Init",
                    True,
                    "RealismOptimizer properly initialized in generator"
                ))
        except Exception as e:
            self.results.append(ValidationResult(
                "Generator Integration Check",
                False,
                f"Failed: {e}",
                critical=True
            ))
    
    def check_realism_optimizer_logic(self):
        """Test RealismOptimizer produces valid adjustments."""
        try:
            from learning.realism_optimizer import RealismOptimizer
            
            optimizer = RealismOptimizer()
            
            # Test tendency analysis
            tendencies = ['formulaic_phrasing', 'mechanical_tone']
            current_params = {
                'temperature': 0.7,
                'trait_frequency': 0.5
            }
            
            adjustments = optimizer.analyze_ai_tendencies(tendencies, current_params)
            
            if not adjustments:
                self.results.append(ValidationResult(
                    "RealismOptimizer Logic",
                    False,
                    "No adjustments generated for known AI tendencies",
                    critical=True
                ))
            else:
                self.results.append(ValidationResult(
                    "RealismOptimizer Logic",
                    True,
                    f"Generated {len(adjustments)} parameter adjustments"
                ))
        except Exception as e:
            self.results.append(ValidationResult(
                "RealismOptimizer Logic Test",
                False,
                f"Failed: {e}",
                critical=True
            ))
    
    def check_tendency_mappings(self):
        """Verify AI tendency mappings are comprehensive."""
        try:
            from learning.realism_optimizer import RealismOptimizer
            
            optimizer = RealismOptimizer()
            
            expected_tendencies = [
                'formulaic_phrasing',
                'unnatural_transitions',
                'excessive_enthusiasm',
                'rigid_structure',
                'overly_polished',
                'mechanical_tone',
                'repetitive_patterns',
                'forced_transitions',
                'artificial_symmetry',
                'generic_language'
            ]
            
            missing = []
            for tendency in expected_tendencies:
                if tendency not in optimizer.TENDENCY_MAPPINGS:
                    missing.append(tendency)
            
            if missing:
                self.results.append(ValidationResult(
                    "AI Tendency Mappings",
                    False,
                    f"Missing mappings: {', '.join(missing)}",
                    critical=False  # Warning only
                ))
            else:
                self.results.append(ValidationResult(
                    "AI Tendency Mappings",
                    True,
                    f"All {len(expected_tendencies)} tendencies mapped"
                ))
        except Exception as e:
            self.results.append(ValidationResult(
                "Tendency Mappings Check",
                False,
                f"Failed: {e}",
                critical=True
            ))
    
    def check_combined_scoring(self):
        """Test combined score calculation logic."""
        try:
            from learning.realism_optimizer import RealismOptimizer
            
            optimizer = RealismOptimizer()
            
            # Test case: High Winston, low realism
            score = optimizer.calculate_combined_score(90.0, 5.0)
            expected = (90 * 0.4) + (50 * 0.6)  # 36 + 30 = 66
            
            if abs(score - expected) > 0.1:
                self.results.append(ValidationResult(
                    "Combined Score Calculation",
                    False,
                    f"Incorrect calculation: got {score}, expected {expected}",
                    critical=True
                ))
            else:
                self.results.append(ValidationResult(
                    "Combined Score Calculation",
                    True,
                    "40/60 weighting calculation correct"
                ))
        except Exception as e:
            self.results.append(ValidationResult(
                "Combined Scoring Test",
                False,
                f"Failed: {e}",
                critical=True
            ))
    
    def check_retry_loop_integration(self):
        """Verify realism evaluation is integrated in retry loop."""
        try:
            from generation.core.legacy.generator import DynamicGenerator
            import inspect
            
            source = inspect.getsource(DynamicGenerator.generate)
            
            required_elements = [
                ('SubjectiveEvaluator', 'Realism evaluator import'),
                ('realism_score', 'Realism score tracking'),
                ('ai_tendencies', 'AI tendencies tracking'),
                ('combined_score', 'Combined score calculation'),
                ('realism_optimizer', 'RealismOptimizer usage')
            ]
            
            missing = []
            for element, description in required_elements:
                if element not in source:
                    missing.append(description)
            
            if missing:
                self.results.append(ValidationResult(
                    "Retry Loop Integration",
                    False,
                    f"Missing: {', '.join(missing)}",
                    critical=True
                ))
            else:
                self.results.append(ValidationResult(
                    "Retry Loop Integration",
                    True,
                    "Realism evaluation fully integrated in retry loop"
                ))
        except Exception as e:
            self.results.append(ValidationResult(
                "Retry Loop Check",
                False,
                f"Failed: {e}",
                critical=True
            ))
    
    def check_database_logging(self):
        """Verify generator logs realism learning data."""
        try:
            from generation.core.legacy.generator import DynamicGenerator
            from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
            import inspect
            
            # Check generator calls log_realism_learning
            gen_source = inspect.getsource(DynamicGenerator.generate)
            
            if 'log_realism_learning' not in gen_source:
                self.results.append(ValidationResult(
                    "Database Logging",
                    False,
                    "Generator doesn't call log_realism_learning",
                    critical=True
                ))
            else:
                # Check method exists
                if not hasattr(WinstonFeedbackDatabase, 'log_realism_learning'):
                    self.results.append(ValidationResult(
                        "Database Logging",
                        False,
                        "log_realism_learning method missing from database",
                        critical=True
                    ))
                else:
                    self.results.append(ValidationResult(
                        "Database Logging",
                        True,
                        "Realism learning data logged to database"
                    ))
        except Exception as e:
            self.results.append(ValidationResult(
                "Database Logging Check",
                False,
                f"Failed: {e}",
                critical=True
            ))
    
    def check_batch_test_display(self):
        """Verify batch test displays realism metrics."""
        try:
            batch_test_path = Path('scripts/batch_caption_test.py')
            
            if not batch_test_path.exists():
                self.results.append(ValidationResult(
                    "Batch Test Display",
                    False,
                    "Batch test script not found",
                    critical=False
                ))
                return
            
            with open(batch_test_path, 'r') as f:
                source = f.read()
            
            required_metrics = [
                'realism_score',
                'voice_authenticity',
                'tonal_consistency',
                'ai_tendencies'
            ]
            
            missing = [m for m in required_metrics if m not in source]
            
            if missing:
                self.results.append(ValidationResult(
                    "Batch Test Display",
                    False,
                    f"Doesn't display: {', '.join(missing)}",
                    critical=False  # Warning only
                ))
            else:
                self.results.append(ValidationResult(
                    "Batch Test Display",
                    True,
                    "All realism metrics displayed in reports"
                ))
        except Exception as e:
            self.results.append(ValidationResult(
                "Batch Test Check",
                False,
                f"Failed: {e}",
                critical=False
            ))


def main():
    """Run validation and exit with appropriate code."""
    validator = DualObjectiveValidator()
    
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
