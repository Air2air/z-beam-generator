#!/usr/bin/env python3
"""
E2E Processing System Evaluation
==================================

Comprehensive evaluation across 5 dimensions:
1. Human-readable text & AI detection passing
2. Self-learning and knowledge storage  
3. Self-diagnosis capabilities
4. Feedback collection best practices
5. Codebase simplicity, organization, robustness
"""

import sys
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class E2EEvaluator:
    """Comprehensive system evaluation"""
    
    def __init__(self):
        self.db_path = Path("data/winston_feedback.db")
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'evaluations': {}
        }
    
    def run_all_evaluations(self) -> Dict[str, Any]:
        """Run all evaluation dimensions"""
        
        print("=" * 80)
        print("E2E PROCESSING SYSTEM EVALUATION")
        print("=" * 80)
        print()
        
        self.evaluate_generation_quality()
        self.evaluate_learning_systems()
        self.evaluate_self_diagnosis()
        self.evaluate_feedback_practices()
        self.evaluate_codebase_quality()
        
        return self.results
    
    def evaluate_generation_quality(self):
        """Dimension 1: Human-readable text & AI detection"""
        print("📝 DIMENSION 1: Generation Quality & AI Detection")
        print("-" * 80)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                AVG(human_score) as avg_human,
                AVG(ai_score) as avg_ai,
                MIN(human_score) as min_human,
                MAX(human_score) as max_human,
                AVG(CASE WHEN success = 1 THEN human_score END) as avg_success_human
            FROM detection_results
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        
        stats = cursor.fetchone()
        
        eval_result = {
            'total_attempts': stats[0],
            'success_rate': (stats[1] / stats[0] * 100) if stats[0] > 0 else 0,
            'avg_human_score': stats[2] if stats[2] else 0,
            'avg_ai_score': stats[3] if stats[3] else 0,
            'human_score_range': f"{stats[4] if stats[4] else 0:.1f}% - {stats[5] if stats[5] else 0:.1f}%",
            'avg_success_human_score': stats[6] if stats[6] else 0
        }
        
        print(f"  Total Attempts (7 days): {eval_result['total_attempts']}")
        print(f"  Success Rate: {eval_result['success_rate']:.1f}%")
        print(f"  Avg Human Score: {eval_result['avg_human_score']:.1f}%")
        print(f"  Avg AI Score: {eval_result['avg_ai_score']:.3f}")
        print(f"  Human Score Range: {eval_result['human_score_range']}")
        print(f"  Avg Successful Human Score: {eval_result['avg_success_human_score']:.1f}%")
        
        # Grading
        grade = self._grade_generation_quality(eval_result)
        eval_result['grade'] = grade
        
        print(f"\n  Grade: {grade['letter']} ({grade['score']}/100)")
        print(f"  Assessment: {grade['assessment']}")
        
        # Check dynamic penalties impact
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN p.frequency_penalty = 0.0 THEN 'Hardcoded (0.0)'
                    ELSE 'Dynamic (>0.0)'
                END as penalty_type,
                AVG(d.human_score) as avg_human,
                COUNT(*) as samples,
                SUM(CASE WHEN d.success = 1 THEN 1 ELSE 0 END) as successes
            FROM generation_parameters p
            JOIN detection_results d ON p.detection_result_id = d.id
            GROUP BY penalty_type
        ''')
        
        penalty_impact = cursor.fetchall()
        if penalty_impact:
            print(f"\n  Dynamic Penalties Impact:")
            for row in penalty_impact:
                success_rate = (row[3] / row[2] * 100) if row[2] > 0 else 0
                print(f"    {row[0]}: {row[1]:.1f}% human, {success_rate:.1f}% success (n={row[2]})")
        
        self.results['evaluations']['generation_quality'] = eval_result
        conn.close()
        print()
    
    def evaluate_learning_systems(self):
        """Dimension 2: Self-learning capabilities"""
        print("🧠 DIMENSION 2: Self-Learning & Knowledge Storage")
        print("-" * 80)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        eval_result = {}
        
        # Parameter logging
        cursor.execute('SELECT COUNT(*), COUNT(DISTINCT param_hash) FROM generation_parameters')
        params = cursor.fetchone()
        eval_result['param_sets_logged'] = params[0]
        eval_result['unique_param_sets'] = params[1]
        print(f"  Parameter Sets: {params[0]} logged, {params[1]} unique")
        
        # AI patterns learned
        cursor.execute('SELECT COUNT(*) FROM ai_patterns')
        patterns = cursor.fetchone()
        eval_result['ai_patterns_learned'] = patterns[0]
        print(f"  AI Patterns Learned: {patterns[0]}")
        
        # Sentence analysis
        cursor.execute('SELECT COUNT(*), AVG(human_score) FROM sentence_analysis')
        sentences = cursor.fetchone()
        eval_result['sentences_analyzed'] = sentences[0]
        eval_result['avg_sentence_human'] = sentences[1] if sentences[1] else 0
        print(f"  Sentences Analyzed: {sentences[0]} (avg {sentences[1] if sentences[1] else 0:.1f}% human)")
        
        # Subjective evaluations
        cursor.execute('''
            SELECT COUNT(*), AVG(overall_score), 
                   SUM(CASE WHEN passes_quality_gate = 1 THEN 1 ELSE 0 END)
            FROM subjective_evaluations
        ''')
        claude = cursor.fetchone()
        eval_result['subjective_evaluations'] = claude[0]
        eval_result['avg_claude_score'] = claude[1] if claude[1] else 0
        eval_result['claude_pass_rate'] = (claude[2] / claude[0] * 100) if claude[0] > 0 else 0
        print(f"  Subjective Evaluations: {claude[0]} (avg {claude[1] if claude[1] else 0:.1f}/10)")
        print(f"  Claude Pass Rate: {eval_result['claude_pass_rate']:.1f}%")
        
        # Learning trend (last 7 days vs previous 7 days)
        cursor.execute('''
            SELECT 
                AVG(CASE WHEN timestamp > datetime('now', '-7 days') THEN human_score END) as recent,
                AVG(CASE WHEN timestamp BETWEEN datetime('now', '-14 days') AND datetime('now', '-7 days') THEN human_score END) as previous
            FROM detection_results
        ''')
        trend = cursor.fetchone()
        if trend[0] and trend[1]:
            improvement = trend[0] - trend[1]
            eval_result['learning_trend'] = f"{'+' if improvement > 0 else ''}{improvement:.1f}%"
            print(f"  Learning Trend: {eval_result['learning_trend']} (week over week)")
        
        grade = self._grade_learning_systems(eval_result)
        eval_result['grade'] = grade
        
        print(f"\n  Grade: {grade['letter']} ({grade['score']}/100)")
        print(f"  Assessment: {grade['assessment']}")
        
        self.results['evaluations']['learning_systems'] = eval_result
        conn.close()
        print()
    
    def evaluate_self_diagnosis(self):
        """Dimension 3: Self-diagnosis capabilities"""
        print("🔍 DIMENSION 3: Self-Diagnosis & Error Detection")
        print("-" * 80)
        
        try:
            from generation.integrity.integrity_checker import IntegrityChecker
            import time
            
            checker = IntegrityChecker()
            start = time.time()
            results = checker.run_all_checks()
            duration = time.time() - start
            
            passed = sum(1 for r in results if r.status.value == 'PASS')
            failed = sum(1 for r in results if r.status.value == 'FAIL')
            warned = sum(1 for r in results if r.status.value == 'WARN')
            
            eval_result = {
                'total_checks': len(results),
                'passed': passed,
                'failed': failed,
                'warned': warned,
                'duration_ms': duration * 1000,
                'checks': []
            }
            
            print(f"  Total Checks: {len(results)}")
            print(f"  Passed: {passed}")
            print(f"  Failed: {failed}")
            print(f"  Warned: {warned}")
            print(f"  Duration: {duration*1000:.1f}ms")
            
            # List failures
            if failed > 0:
                print(f"\n  Failures:")
                for r in results:
                    if r.status.value == 'FAIL':
                        print(f"    ❌ {r.check_name}: {r.message[:60]}...")
                        eval_result['checks'].append({
                            'name': r.check_name,
                            'status': 'FAIL',
                            'message': r.message
                        })
            
            grade = self._grade_self_diagnosis(eval_result)
            eval_result['grade'] = grade
            
            print(f"\n  Grade: {grade['letter']} ({grade['score']}/100)")
            print(f"  Assessment: {grade['assessment']}")
            
            self.results['evaluations']['self_diagnosis'] = eval_result
            
        except Exception as e:
            print(f"  ❌ Failed to run integrity checks: {e}")
            self.results['evaluations']['self_diagnosis'] = {
                'grade': {'letter': 'F', 'score': 0, 'assessment': f'System error: {e}'}
            }
        
        print()
    
    def evaluate_feedback_practices(self):
        """Dimension 4: Feedback collection"""
        print("📊 DIMENSION 4: Feedback Collection & Analytics")
        print("-" * 80)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        eval_result = {}
        
        # Check all feedback mechanisms
        cursor.execute('SELECT COUNT(*) FROM detection_results')
        eval_result['winston_detections'] = cursor.fetchone()[0]
        print(f"  Winston Detections: {eval_result['winston_detections']}")
        
        cursor.execute('SELECT COUNT(*) FROM corrections')
        eval_result['corrections_logged'] = cursor.fetchone()[0]
        print(f"  Manual Corrections: {eval_result['corrections_logged']}")
        
        cursor.execute('SELECT COUNT(*) FROM subjective_evaluations')
        eval_result['claude_evals'] = cursor.fetchone()[0]
        print(f"  Subjective Evaluations: {eval_result['claude_evals']}")
        
        cursor.execute('SELECT COUNT(*) FROM sentence_analysis')
        eval_result['sentence_analyses'] = cursor.fetchone()[0]
        print(f"  Sentence Analyses: {eval_result['sentence_analyses']}")
        
        # Check feedback loop effectiveness
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT material) as materials,
                COUNT(DISTINCT component_type) as components
            FROM detection_results
        ''')
        coverage = cursor.fetchone()
        eval_result['material_coverage'] = coverage[0]
        eval_result['component_coverage'] = coverage[1]
        print(f"  Material Coverage: {coverage[0]} materials")
        print(f"  Component Coverage: {coverage[1]} component types")
        
        # Data completeness
        cursor.execute('''
            SELECT 
                COUNT(*) as with_params
            FROM detection_results d
            WHERE EXISTS (
                SELECT 1 FROM generation_parameters p 
                WHERE p.detection_result_id = d.id
            )
        ''')
        with_params = cursor.fetchone()[0]
        param_coverage = (with_params / eval_result['winston_detections'] * 100) if eval_result['winston_detections'] > 0 else 0
        eval_result['parameter_logging_coverage'] = param_coverage
        print(f"  Parameter Logging Coverage: {param_coverage:.1f}%")
        
        grade = self._grade_feedback_practices(eval_result)
        eval_result['grade'] = grade
        
        print(f"\n  Grade: {grade['letter']} ({grade['score']}/100)")
        print(f"  Assessment: {grade['assessment']}")
        
        self.results['evaluations']['feedback_practices'] = eval_result
        conn.close()
        print()
    
    def evaluate_codebase_quality(self):
        """Dimension 5: Code quality & organization"""
        print("🏗️  DIMENSION 5: Codebase Quality & Robustness")
        print("-" * 80)
        
        eval_result = {}
        
        # Count files and LOC
        project_root = Path(__file__).parent.parent
        processing_dir = project_root / "processing"
        
        py_files = list(processing_dir.rglob("*.py"))
        eval_result['processing_files'] = len(py_files)
        
        total_loc = 0
        for f in py_files:
            try:
                with open(f) as file:
                    total_loc += len(file.readlines())
            except:
                pass
        
        eval_result['total_loc'] = total_loc
        print(f"  Processing Files: {len(py_files)}")
        print(f"  Total LOC: {total_loc:,}")
        
        # Check documentation
        doc_files = list(Path(project_root / "docs").rglob("*.md"))
        eval_result['documentation_files'] = len(doc_files)
        print(f"  Documentation Files: {len(doc_files)}")
        
        # Check tests
        test_files = list(Path(project_root / "tests").rglob("test_*.py"))
        eval_result['test_files'] = len(test_files)
        print(f"  Test Files: {len(test_files)}")
        
        # Check for key architectural patterns
        patterns_found = []
        
        # Factory pattern
        if (project_root / "shared/api/client_factory.py").exists():
            patterns_found.append("Factory Pattern")
        
        # Database abstraction
        if (project_root / "generation/learning/winston_feedback_db.py").exists():
            patterns_found.append("Database Abstraction")
        
        # Configuration management
        if (project_root / "generation/config/dynamic_config.py").exists():
            patterns_found.append("Dynamic Configuration")
        
        # Integrity checking
        if (project_root / "generation/integrity/integrity_checker.py").exists():
            patterns_found.append("Integrity Validation")
        
        eval_result['architectural_patterns'] = patterns_found
        print(f"  Architectural Patterns: {', '.join(patterns_found)}")
        
        # Check error handling sophistication
        error_handling_score = self._assess_error_handling(processing_dir)
        eval_result['error_handling_score'] = error_handling_score
        print(f"  Error Handling Score: {error_handling_score}/10")
        
        grade = self._grade_codebase_quality(eval_result)
        eval_result['grade'] = grade
        
        print(f"\n  Grade: {grade['letter']} ({grade['score']}/100)")
        print(f"  Assessment: {grade['assessment']}")
        
        self.results['evaluations']['codebase_quality'] = eval_result
        print()
    
    def _grade_generation_quality(self, data: Dict) -> Dict[str, Any]:
        """Grade generation quality"""
        score = 0
        
        # Success rate (30 points)
        if data['success_rate'] >= 80:
            score += 30
        elif data['success_rate'] >= 60:
            score += 25
        elif data['success_rate'] >= 40:
            score += 20
        elif data['success_rate'] >= 20:
            score += 10
        
        # Human score quality (40 points)
        if data['avg_success_human_score'] >= 80:
            score += 40
        elif data['avg_success_human_score'] >= 60:
            score += 30
        elif data['avg_success_human_score'] >= 40:
            score += 20
        elif data['avg_success_human_score'] >= 20:
            score += 10
        
        # AI score (lower is better) (20 points)
        if data['avg_ai_score'] <= 0.3:
            score += 20
        elif data['avg_ai_score'] <= 0.5:
            score += 15
        elif data['avg_ai_score'] <= 0.7:
            score += 10
        elif data['avg_ai_score'] <= 0.9:
            score += 5
        
        # Consistency (10 points)
        if data['total_attempts'] >= 50:
            score += 10
        elif data['total_attempts'] >= 20:
            score += 5
        
        # Letter grade
        if score >= 90:
            letter = 'A'
            assessment = "Excellent: Consistently produces human-like content"
        elif score >= 80:
            letter = 'B'
            assessment = "Good: Reliably passes AI detection"
        elif score >= 70:
            letter = 'C'
            assessment = "Acceptable: Some AI detection issues"
        elif score >= 60:
            letter = 'D'
            assessment = "Poor: Frequent AI detection failures"
        else:
            letter = 'F'
            assessment = "Failing: Unable to produce human-like content"
        
        return {'letter': letter, 'score': score, 'assessment': assessment}
    
    def _grade_learning_systems(self, data: Dict) -> Dict[str, Any]:
        """Grade learning systems"""
        score = 0
        
        # Parameter logging (30 points)
        if data['param_sets_logged'] >= 50:
            score += 30
        elif data['param_sets_logged'] >= 20:
            score += 20
        elif data['param_sets_logged'] >= 5:
            score += 10
        
        # Pattern learning (25 points)
        if data['ai_patterns_learned'] >= 20:
            score += 25
        elif data['ai_patterns_learned'] >= 10:
            score += 15
        elif data['ai_patterns_learned'] >= 5:
            score += 10
        
        # Subjective evaluations (25 points)
        if data['subjective_evaluations'] >= 20:
            score += 25
        elif data['subjective_evaluations'] >= 10:
            score += 15
        elif data['subjective_evaluations'] >= 5:
            score += 10
        
        # Sentence analysis (20 points)
        if data['sentences_analyzed'] >= 200:
            score += 20
        elif data['sentences_analyzed'] >= 100:
            score += 15
        elif data['sentences_analyzed'] >= 50:
            score += 10
        
        if score >= 90:
            letter = 'A'
            assessment = "Excellent: Comprehensive learning infrastructure"
        elif score >= 80:
            letter = 'B'
            assessment = "Good: Active learning with good coverage"
        elif score >= 70:
            letter = 'C'
            assessment = "Acceptable: Basic learning capabilities"
        elif score >= 60:
            letter = 'D'
            assessment = "Poor: Limited learning data"
        else:
            letter = 'F'
            assessment = "Failing: Insufficient learning infrastructure"
        
        return {'letter': letter, 'score': score, 'assessment': assessment}
    
    def _grade_self_diagnosis(self, data: Dict) -> Dict[str, Any]:
        """Grade self-diagnosis"""
        score = 0
        
        # Number of checks (20 points)
        if data['total_checks'] >= 15:
            score += 20
        elif data['total_checks'] >= 10:
            score += 15
        elif data['total_checks'] >= 5:
            score += 10
        
        # Pass rate (60 points)
        pass_rate = (data['passed'] / data['total_checks'] * 100) if data['total_checks'] > 0 else 0
        if pass_rate >= 90:
            score += 60
        elif pass_rate >= 75:
            score += 45
        elif pass_rate >= 50:
            score += 30
        elif pass_rate >= 25:
            score += 15
        
        # Performance (10 points)
        if data['duration_ms'] < 100:
            score += 10
        elif data['duration_ms'] < 300:
            score += 7
        elif data['duration_ms'] < 500:
            score += 5
        
        # Failure detection (10 points)
        if data['failed'] > 0:
            score += 10  # Finding issues is good!
        
        if score >= 90:
            letter = 'A'
            assessment = "Excellent: Comprehensive health monitoring"
        elif score >= 80:
            letter = 'B'
            assessment = "Good: Effective issue detection"
        elif score >= 70:
            letter = 'C'
            assessment = "Acceptable: Basic health checks"
        elif score >= 60:
            letter = 'D'
            assessment = "Poor: Limited diagnostic capability"
        else:
            letter = 'F'
            assessment = "Failing: No effective diagnostics"
        
        return {'letter': letter, 'score': score, 'assessment': assessment}
    
    def _grade_feedback_practices(self, data: Dict) -> Dict[str, Any]:
        """Grade feedback practices"""
        score = 0
        
        # Detection coverage (30 points)
        if data['winston_detections'] >= 50:
            score += 30
        elif data['winston_detections'] >= 20:
            score += 20
        elif data['winston_detections'] >= 10:
            score += 10
        
        # Multiple feedback sources (30 points)
        sources = 0
        if data['winston_detections'] > 0:
            sources += 1
        if data['claude_evals'] > 0:
            sources += 1
        if data['sentence_analyses'] > 0:
            sources += 1
        if data['corrections_logged'] > 0:
            sources += 1
        
        score += sources * 7.5
        
        # Material/component coverage (20 points)
        if data['material_coverage'] >= 10:
            score += 10
        elif data['material_coverage'] >= 5:
            score += 7
        elif data['material_coverage'] >= 2:
            score += 5
        
        if data['component_coverage'] >= 3:
            score += 10
        elif data['component_coverage'] >= 2:
            score += 7
        elif data['component_coverage'] >= 1:
            score += 5
        
        # Data completeness (20 points)
        if data['parameter_logging_coverage'] >= 90:
            score += 20
        elif data['parameter_logging_coverage'] >= 70:
            score += 15
        elif data['parameter_logging_coverage'] >= 50:
            score += 10
        elif data['parameter_logging_coverage'] >= 25:
            score += 5
        
        if score >= 90:
            letter = 'A'
            assessment = "Excellent: Comprehensive feedback loops"
        elif score >= 80:
            letter = 'B'
            assessment = "Good: Multi-source feedback collection"
        elif score >= 70:
            letter = 'C'
            assessment = "Acceptable: Basic feedback mechanisms"
        elif score >= 60:
            letter = 'D'
            assessment = "Poor: Limited feedback data"
        else:
            letter = 'F'
            assessment = "Failing: No effective feedback"
        
        return {'letter': letter, 'score': score, 'assessment': assessment}
    
    def _grade_codebase_quality(self, data: Dict) -> Dict[str, Any]:
        """Grade codebase quality"""
        score = 0
        
        # Size/complexity (20 points)
        if data['total_loc'] < 15000:
            score += 20
        elif data['total_loc'] < 25000:
            score += 15
        elif data['total_loc'] < 40000:
            score += 10
        else:
            score += 5
        
        # Documentation (25 points)
        if data['documentation_files'] >= 30:
            score += 25
        elif data['documentation_files'] >= 20:
            score += 20
        elif data['documentation_files'] >= 10:
            score += 15
        elif data['documentation_files'] >= 5:
            score += 10
        
        # Tests (25 points)
        if data['test_files'] >= 20:
            score += 25
        elif data['test_files'] >= 10:
            score += 20
        elif data['test_files'] >= 5:
            score += 15
        elif data['test_files'] >= 2:
            score += 10
        
        # Architectural patterns (20 points)
        score += len(data['architectural_patterns']) * 5
        
        # Error handling (10 points)
        score += data['error_handling_score']
        
        if score >= 90:
            letter = 'A'
            assessment = "Excellent: Clean, well-organized codebase"
        elif score >= 80:
            letter = 'B'
            assessment = "Good: Solid architecture with good practices"
        elif score >= 70:
            letter = 'C'
            assessment = "Acceptable: Functional but needs improvement"
        elif score >= 60:
            letter = 'D'
            assessment = "Poor: Significant technical debt"
        else:
            letter = 'F'
            assessment = "Failing: Major architectural issues"
        
        return {'letter': letter, 'score': score, 'assessment': assessment}
    
    def _assess_error_handling(self, processing_dir: Path) -> int:
        """Assess error handling sophistication (0-10)"""
        score = 0
        
        # Check for try/except usage
        try_count = 0
        specific_exceptions = 0
        logged_errors = 0
        
        for py_file in processing_dir.rglob("*.py"):
            try:
                with open(py_file) as f:
                    content = f.read()
                    try_count += content.count('try:')
                    specific_exceptions += content.count('except ') - content.count('except:')
                    logged_errors += content.count('logger.error') + content.count('logger.exception')
            except:
                pass
        
        # Scoring
        if try_count >= 50:
            score += 3
        elif try_count >= 20:
            score += 2
        elif try_count >= 10:
            score += 1
        
        if specific_exceptions >= 40:
            score += 3
        elif specific_exceptions >= 20:
            score += 2
        elif specific_exceptions >= 10:
            score += 1
        
        if logged_errors >= 30:
            score += 4
        elif logged_errors >= 15:
            score += 3
        elif logged_errors >= 5:
            score += 2
        
        return min(score, 10)
    
    def print_summary(self):
        """Print overall summary"""
        print("=" * 80)
        print("OVERALL SYSTEM ASSESSMENT")
        print("=" * 80)
        print()
        
        evaluations = self.results['evaluations']
        overall_score = 0
        letter_grades = []
        
        dimensions = [
            ('Generation Quality', 'generation_quality', 25),
            ('Learning Systems', 'learning_systems', 20),
            ('Self-Diagnosis', 'self_diagnosis', 20),
            ('Feedback Practices', 'feedback_practices', 20),
            ('Codebase Quality', 'codebase_quality', 15)
        ]
        
        for name, key, weight in dimensions:
            if key in evaluations and 'grade' in evaluations[key]:
                grade = evaluations[key]['grade']
                weighted_score = grade['score'] * weight / 100
                overall_score += weighted_score
                letter_grades.append(grade['letter'])
                print(f"  {name:25s}: {grade['letter']:2s} ({int(grade['score']):3d}/100) [weight: {weight}%]")
        
        print()
        print(f"  Overall Score: {overall_score:.1f}/100")
        
        # Overall letter grade
        if overall_score >= 90:
            overall_letter = 'A'
            status = "🎉 EXCELLENT"
            recommendation = "System performing at production-ready level"
        elif overall_score >= 80:
            overall_letter = 'B'
            status = "✅ GOOD"
            recommendation = "System functional with minor improvements needed"
        elif overall_score >= 70:
            overall_letter = 'C'
            status = "⚠️  ACCEPTABLE"
            recommendation = "System works but requires attention"
        elif overall_score >= 60:
            overall_letter = 'D'
            status = "❌ POOR"
            recommendation = "Significant issues need addressing"
        else:
            overall_letter = 'F'
            status = "🚨 FAILING"
            recommendation = "Critical issues blocking production use"
        
        print(f"  Overall Grade: {overall_letter}")
        print(f"  Status: {status}")
        print(f"  Recommendation: {recommendation}")
        print()
        
        # Save results
        output_file = Path("E2E_EVALUATION_REPORT.json")
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"  📄 Full report saved to: {output_file}")
        print()


if __name__ == '__main__':
    evaluator = E2EEvaluator()
    evaluator.run_all_evaluations()
    evaluator.print_summary()
