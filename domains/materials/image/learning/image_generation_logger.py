#!/usr/bin/env python3
"""
Image Generation Learning Logger

Tracks all image generation attempts to identify failure patterns
and optimize generation parameters.

Captures:
- Generation parameters (prompt length, guidance scale, patterns)
- Validation results (scores, issues, red flags)
- Success/failure patterns by material category
- Feedback effectiveness (A/B testing)

Database: SQLite (lightweight, no infrastructure)
Location: domains/materials/image/learning/generation_history.db

Author: AI Assistant
Date: November 25, 2025
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ImageGenerationLogger:
    """
    Logs image generation attempts for learning and optimization.
    
    Features:
    - Automatic schema creation
    - Tracks generation and validation metadata
    - Identifies failure patterns
    - Measures feedback effectiveness
    - Provides analytics queries
    
    Example:
        logger = ImageGenerationLogger()
        
        # Log generation attempt
        attempt_id = logger.log_attempt(
            material="Birch",
            category="wood_hardwood",
            generation_params=dict(),
            validation_results=dict()
        )
        
        # Get analytics
        stats = logger.get_category_stats("wood_hardwood")
        physics_issues = logger.get_common_physics_violations()
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize logger with database.
        
        Args:
            db_path: Optional path to database file
                    (defaults to learning/generation_history.db)
        """
        if db_path is None:
            db_path = Path(__file__).parent / "generation_history.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_database()
        
        logger.info(f"✅ Image generation logger initialized: {self.db_path}")
    
    def _init_database(self):
        """Create database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main attempts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_attempts (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                material TEXT NOT NULL,
                category TEXT NOT NULL,
                
                -- Generation parameters
                gen_prompt_length INTEGER,
                guidance_scale REAL,
                contamination_uniformity INTEGER,
                view_mode TEXT,
                patterns_used TEXT,  -- JSON array
                feedback_applied BOOLEAN,
                feedback_text TEXT,  -- User feedback content
                feedback_category TEXT,  -- physics, aesthetics, contamination, etc.
                feedback_source TEXT,  -- user, automated, system
                
                -- Validation results
                val_prompt_length INTEGER,
                val_truncated BOOLEAN,
                realism_score INTEGER,
                passed BOOLEAN,
                physics_issues TEXT,  -- JSON array
                red_flags TEXT,  -- JSON array
                
                -- Outcome
                failure_category TEXT,
                retry_count INTEGER,
                final_success BOOLEAN,
                
                -- Image metadata
                image_path TEXT,
                image_size_kb REAL,
                
                -- Notes
                notes TEXT
            )
        """)
        
        # Index for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON generation_attempts(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON generation_attempts(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_passed 
            ON generation_attempts(passed)
        """)
        
        conn.commit()
        conn.close()
        
        logger.debug("✅ Database schema initialized")
    
    def log_attempt(
        self,
        material: str,
        category: str,
        generation_params: Dict,
        validation_results: Dict,
        outcome: Dict,
        image_metadata: Optional[Dict] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Log a generation attempt.
        
        Args:
            material: Material name (e.g., "Birch")
            category: Material category (e.g., "wood_hardwood")
            generation_params: Dict with:
                - prompt_length: int
                - guidance_scale: float
                - contamination_uniformity: int (1-5)
                - view_mode: str
                - patterns_used: List[str]
                - feedback_applied: bool
                - feedback_text: Optional[str] (actual feedback content)
                - feedback_category: Optional[str] (physics, aesthetics, etc.)
                - feedback_source: Optional[str] (user, automated, system)
            validation_results: Dict with:
                - prompt_length: int
                - truncated: bool
                - realism_score: int (0-100)
                - passed: bool
                - physics_issues: List[str]
                - red_flags: List[str]
            outcome: Dict with:
                - failure_category: Optional[str]
                - retry_count: int
                - final_success: bool
            image_metadata: Optional dict with:
                - path: str
                - size_kb: float
            notes: Optional notes about the attempt
            
        Returns:
            Attempt ID (UUID)
        """
        import uuid
        
        attempt_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO generation_attempts (
                id, timestamp, material, category,
                gen_prompt_length, guidance_scale, contamination_uniformity,
                view_mode, patterns_used, feedback_applied,
                feedback_text, feedback_category, feedback_source,
                val_prompt_length, val_truncated, realism_score, passed,
                physics_issues, red_flags,
                failure_category, retry_count, final_success,
                image_path, image_size_kb, notes
            ) VALUES (
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?
            )
        """, (
            attempt_id,
            timestamp,
            material,
            category,
            
            # Generation
            generation_params.get('prompt_length'),
            generation_params.get('guidance_scale'),
            generation_params.get('contamination_uniformity'),
            generation_params.get('view_mode'),
            json.dumps(generation_params.get('patterns_used', [])),
            generation_params.get('feedback_applied', False),
            generation_params.get('feedback_text'),
            generation_params.get('feedback_category'),
            generation_params.get('feedback_source', 'user' if generation_params.get('feedback_text') else None),
            
            # Validation
            validation_results.get('prompt_length'),
            validation_results.get('truncated', False),
            validation_results.get('realism_score'),
            validation_results.get('passed', False),
            json.dumps(validation_results.get('physics_issues', [])),
            json.dumps(validation_results.get('red_flags', [])),
            
            # Outcome
            outcome.get('failure_category'),
            outcome.get('retry_count', 0),
            outcome.get('final_success', False),
            
            # Image
            image_metadata.get('path') if image_metadata else None,
            image_metadata.get('size_kb') if image_metadata else None,
            
            notes
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(
            f"📊 Logged attempt: {material} ({category}) - "
            f"Score: {validation_results.get('realism_score')}/100, "
            f"Passed: {validation_results.get('passed')}"
        )
        
        return attempt_id
    
    def get_category_stats(self, category: str) -> Dict:
        """
        Get success statistics for a material category.
        
        Args:
            category: Material category (e.g., "wood_hardwood")
            
        Returns:
            Dict with success rate, avg score, common issues
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed,
                AVG(realism_score) as avg_score,
                AVG(gen_prompt_length) as avg_gen_prompt,
                AVG(val_prompt_length) as avg_val_prompt
            FROM generation_attempts
            WHERE category = ?
        """, (category,))
        
        row = cursor.fetchone()
        total, passed, avg_score, avg_gen, avg_val = row
        
        stats = {
            'category': category,
            'total_attempts': total or 0,
            'passed': passed or 0,
            'failed': (total or 0) - (passed or 0),
            'success_rate': (passed / total * 100) if total else 0,
            'avg_realism_score': round(avg_score, 1) if avg_score else 0,
            'avg_gen_prompt_length': int(avg_gen) if avg_gen else 0,
            'avg_val_prompt_length': int(avg_val) if avg_val else 0
        }
        
        # Physics issues
        cursor.execute("""
            SELECT physics_issues
            FROM generation_attempts
            WHERE category = ? AND physics_issues != '[]'
        """, (category,))
        
        all_issues = []
        for row in cursor.fetchall():
            issues = json.loads(row[0])
            all_issues.extend(issues)
        
        # Count issue frequency
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # Sort by frequency
        common_issues = sorted(
            issue_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        stats['common_physics_issues'] = [
            {'issue': issue, 'count': count}
            for issue, count in common_issues
        ]
        
        conn.close()
        
        return stats
    
    def get_common_physics_violations(self, limit: int = 10) -> List[Dict]:
        """
        Get most common physics violations across all materials.
        
        Args:
            limit: Max number of violations to return
            
        Returns:
            List of dicts with issue and count
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT physics_issues
            FROM generation_attempts
            WHERE physics_issues != '[]'
        """)
        
        all_issues = []
        for row in cursor.fetchall():
            issues = json.loads(row[0])
            all_issues.extend(issues)
        
        conn.close()
        
        # Count frequency
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # Sort and limit
        top_issues = sorted(
            issue_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {'issue': issue, 'count': count, 'percentage': count / len(all_issues) * 100}
            for issue, count in top_issues
        ]
    
    def get_feedback_effectiveness(self) -> Dict:
        """
        Compare success rates before and after feedback applied.
        
        Returns:
            Dict with before/after stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Before feedback
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed,
                AVG(realism_score) as avg_score
            FROM generation_attempts
            WHERE feedback_applied = 0
        """)
        
        before_total, before_passed, before_avg = cursor.fetchone()
        
        # After feedback
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed,
                AVG(realism_score) as avg_score
            FROM generation_attempts
            WHERE feedback_applied = 1
        """)
        
        after_total, after_passed, after_avg = cursor.fetchone()
        
        conn.close()
        
        return {
            'before_feedback': {
                'total': before_total or 0,
                'passed': before_passed or 0,
                'success_rate': (before_passed / before_total * 100) if before_total else 0,
                'avg_score': round(before_avg, 1) if before_avg else 0
            },
            'after_feedback': {
                'total': after_total or 0,
                'passed': after_passed or 0,
                'success_rate': (after_passed / after_total * 100) if after_total else 0,
                'avg_score': round(after_avg, 1) if after_avg else 0
            },
            'improvement': {
                'success_rate_delta': (
                    (after_passed / after_total * 100 if after_total else 0) -
                    (before_passed / before_total * 100 if before_total else 0)
                ),
                'avg_score_delta': (
                    (after_avg if after_avg else 0) -
                    (before_avg if before_avg else 0)
                )
            }
        }
    
    def get_prompt_truncation_impact(self) -> Dict:
        """
        Analyze impact of prompt truncation on success rate.
        
        Returns:
            Dict comparing truncated vs non-truncated attempts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Non-truncated
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed,
                AVG(realism_score) as avg_score
            FROM generation_attempts
            WHERE val_truncated = 0
        """)
        
        normal_total, normal_passed, normal_avg = cursor.fetchone()
        
        # Truncated
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed,
                AVG(realism_score) as avg_score
            FROM generation_attempts
            WHERE val_truncated = 1
        """)
        
        trunc_total, trunc_passed, trunc_avg = cursor.fetchone()
        
        conn.close()
        
        return {
            'non_truncated': {
                'total': normal_total or 0,
                'passed': normal_passed or 0,
                'success_rate': (normal_passed / normal_total * 100) if normal_total else 0,
                'avg_score': round(normal_avg, 1) if normal_avg else 0
            },
            'truncated': {
                'total': trunc_total or 0,
                'passed': trunc_passed or 0,
                'success_rate': (trunc_passed / trunc_total * 100) if trunc_total else 0,
                'avg_score': round(trunc_avg, 1) if trunc_avg else 0
            }
        }
    
    def get_recent_attempts(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent generation attempts.
        
        Args:
            limit: Number of attempts to return
            
        Returns:
            List of attempt dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                material, category, timestamp, 
                realism_score, passed, 
                physics_issues, failure_category
            FROM generation_attempts
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        attempts = []
        for row in cursor.fetchall():
            material, category, timestamp, score, passed, issues, fail_cat = row
            attempts.append({
                'material': material,
                'category': category,
                'timestamp': timestamp,
                'realism_score': score,
                'passed': bool(passed),
                'physics_issues': json.loads(issues) if issues else [],
                'failure_category': fail_cat
            })
        
        conn.close()
        
        return attempts
    
    def get_feedback_patterns(self, limit: int = 10) -> List[Dict]:
        """
        Analyze which feedback categories are most effective.
        
        Args:
            limit: Number of top feedback types to return
            
        Returns:
            List of dicts with feedback category, usage, effectiveness
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                feedback_category,
                COUNT(*) as usage_count,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as successes,
                AVG(realism_score) as avg_score
            FROM generation_attempts
            WHERE feedback_applied = 1 AND feedback_category IS NOT NULL
            GROUP BY feedback_category
            ORDER BY usage_count DESC
            LIMIT ?
        """, (limit,))
        
        patterns = []
        for row in cursor.fetchall():
            category, count, successes, avg_score = row
            patterns.append({
                'category': category,
                'usage_count': count,
                'success_rate': (successes / count * 100) if count else 0,
                'avg_score': round(avg_score, 1) if avg_score else 0
            })
        
        conn.close()
        
        return patterns
    
    def search_feedback(self, search_term: str) -> List[Dict]:
        """
        Search feedback text for specific keywords or patterns.
        
        Args:
            search_term: Text to search for (e.g., "contamination", "physics")
            
        Returns:
            List of attempts with matching feedback
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                material, feedback_text, feedback_category,
                realism_score, passed, timestamp
            FROM generation_attempts
            WHERE feedback_text LIKE ?
            ORDER BY timestamp DESC
        """, (f'%{search_term}%',))
        
        results = []
        for row in cursor.fetchall():
            material, feedback, category, score, passed, timestamp = row
            results.append({
                'material': material,
                'feedback_text': feedback,
                'feedback_category': category,
                'realism_score': score,
                'passed': bool(passed),
                'timestamp': timestamp
            })
        
        conn.close()
        
        return results
    
    def get_best_feedback_examples(self, category: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """
        Get examples of feedback that led to successful generations.
        
        Args:
            category: Optional feedback category to filter by
            limit: Number of examples to return
            
        Returns:
            List of successful attempts with feedback
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT 
                    material, feedback_text, feedback_category,
                    realism_score, timestamp
                FROM generation_attempts
                WHERE passed = 1 
                    AND feedback_applied = 1 
                    AND feedback_text IS NOT NULL
                    AND feedback_category = ?
                ORDER BY realism_score DESC
                LIMIT ?
            """, (category, limit))
        else:
            cursor.execute("""
                SELECT 
                    material, feedback_text, feedback_category,
                    realism_score, timestamp
                FROM generation_attempts
                WHERE passed = 1 
                    AND feedback_applied = 1 
                    AND feedback_text IS NOT NULL
                ORDER BY realism_score DESC
                LIMIT ?
            """, (limit,))
        
        examples = []
        for row in cursor.fetchall():
            material, feedback, category, score, timestamp = row
            examples.append({
                'material': material,
                'feedback_text': feedback,
                'feedback_category': category,
                'realism_score': score,
                'timestamp': timestamp
            })
        
        conn.close()
        
        return examples
    
    def print_analytics_report(self):
        """Print comprehensive analytics report."""
        print("\n" + "=" * 70)
        print("📊 IMAGE GENERATION ANALYTICS REPORT")
        print("=" * 70)
        
        # Overall stats
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM generation_attempts")
        total = cursor.fetchone()[0]
        
        if total == 0:
            print("\nNo generation attempts logged yet.")
            conn.close()
            return
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END),
                AVG(realism_score)
            FROM generation_attempts
        """)
        passed, avg_score = cursor.fetchone()
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   • Total attempts: {total}")
        print(f"   • Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"   • Failed: {total-passed} ({(total-passed)/total*100:.1f}%)")
        print(f"   • Average score: {avg_score:.1f}/100")
        
        # By category
        cursor.execute("""
            SELECT category, COUNT(*), 
                   SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END),
                   AVG(realism_score)
            FROM generation_attempts
            GROUP BY category
        """)
        
        print(f"\n📊 BY CATEGORY:")
        for row in cursor.fetchall():
            cat, count, cat_passed, cat_avg = row
            print(f"   • {cat}: {count} attempts, "
                  f"{cat_passed/count*100:.1f}% pass rate, "
                  f"{cat_avg:.1f} avg score")
        
        conn.close()
        
        # Physics violations
        physics = self.get_common_physics_violations(5)
        if physics:
            print(f"\n🚨 TOP PHYSICS VIOLATIONS:")
            for item in physics:
                print(f"   • {item['issue']}: {item['count']} times ({item['percentage']:.1f}%)")
        
        # Feedback effectiveness
        feedback_stats = self.get_feedback_effectiveness()
        if feedback_stats['before_feedback']['total'] > 0 and feedback_stats['after_feedback']['total'] > 0:
            print(f"\n📈 FEEDBACK EFFECTIVENESS:")
            print(f"   Before: {feedback_stats['before_feedback']['success_rate']:.1f}% pass rate")
            print(f"   After:  {feedback_stats['after_feedback']['success_rate']:.1f}% pass rate")
            print(f"   Improvement: {feedback_stats['improvement']['success_rate_delta']:+.1f}%")
        
        # Truncation impact
        trunc_stats = self.get_prompt_truncation_impact()
        if trunc_stats['truncated']['total'] > 0:
            print("\n⚠️  PROMPT TRUNCATION IMPACT:")
            print(f"   Non-truncated: {trunc_stats['non_truncated']['success_rate']:.1f}% pass rate")
            print(f"   Truncated: {trunc_stats['truncated']['success_rate']:.1f}% pass rate")
        
        # Feedback patterns
        feedback_patterns = self.get_feedback_patterns(5)
        if feedback_patterns:
            print("\n💡 FEEDBACK EFFECTIVENESS BY TYPE:")
            for pattern in feedback_patterns:
                print(f"   • {pattern['category']}: "
                      f"{pattern['usage_count']} uses, "
                      f"{pattern['success_rate']:.1f}% success, "
                      f"{pattern['avg_score']:.1f} avg score")
            
            # Best examples
            best_examples = self.get_best_feedback_examples(limit=3)
            if best_examples:
                print("\n🌟 TOP PERFORMING FEEDBACK:")
                for ex in best_examples:
                    print(f"   • {ex['material']} ({ex['realism_score']}/100) - {ex['feedback_category']}")
                    print(f"     \"{ex['feedback_text'][:100]}...\"" if len(ex['feedback_text']) > 100 else f"     \"{ex['feedback_text']}\"")
        
        print("\n" + "=" * 70)


def create_logger(db_path: Optional[Path] = None) -> ImageGenerationLogger:
    """Factory function to create image generation logger."""
    return ImageGenerationLogger(db_path=db_path)
