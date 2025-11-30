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
                severity TEXT,  -- light, moderate, heavy (contamination coverage)
                shape_override TEXT,  -- User-specified shape if any
                
                -- Context parameters (for learning)
                context TEXT,  -- indoor/outdoor/industrial/marine/architectural
                aging_weight REAL,  -- Context weight for aging patterns
                contamination_weight REAL,  -- Context weight for contamination patterns
                background TEXT,  -- Environment background description
                pattern_scores TEXT,  -- JSON: {pattern_name: relevance_score}
                
                -- Optimization metrics
                prompt_chars_before_opt INTEGER,
                prompt_chars_after_opt INTEGER,
                pre_validation_passed BOOLEAN,
                pre_validation_errors INTEGER,
                pre_validation_warnings INTEGER
                
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
        
        # Add new columns if they don't exist (migration for existing DBs)
        try:
            cursor.execute("ALTER TABLE generation_attempts ADD COLUMN severity TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE generation_attempts ADD COLUMN shape_override TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Phase 1 Learning Enhancement columns (Nov 29, 2025)
        new_columns = [
            ("context", "TEXT"),
            ("aging_weight", "REAL"),
            ("contamination_weight", "REAL"),
            ("background", "TEXT"),
            ("pattern_scores", "TEXT"),
            ("prompt_chars_before_opt", "INTEGER"),
            ("prompt_chars_after_opt", "INTEGER"),
            ("pre_validation_passed", "BOOLEAN"),
            ("pre_validation_errors", "INTEGER"),
            ("pre_validation_warnings", "INTEGER")
        ]
        for col_name, col_type in new_columns:
            try:
                cursor.execute(f"ALTER TABLE generation_attempts ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass  # Column already exists
        
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
        
        # ================================================================
        # PHASE 2: Learning Tables (Nov 29, 2025)
        # Single source of truth for all learnable parameters
        # ================================================================
        
        # Learned defaults per category+context combination
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_defaults (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                context TEXT DEFAULT 'outdoor',
                
                -- Generation parameters (learned from successful attempts)
                guidance_scale REAL,
                contamination_uniformity INTEGER,
                view_mode TEXT DEFAULT 'Contextual',
                pass_threshold REAL,
                
                -- Context weights (learned optimal values)
                aging_weight REAL,
                contamination_weight REAL,
                
                -- Statistics
                sample_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                avg_score REAL,
                last_updated TEXT,
                
                UNIQUE(category, context)
            )
        """)
        
        # Add view_mode column if missing (migration for existing databases)
        try:
            cursor.execute("ALTER TABLE learned_defaults ADD COLUMN view_mode TEXT DEFAULT 'Contextual'")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Pattern effectiveness tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_effectiveness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                category TEXT NOT NULL,
                context TEXT DEFAULT 'outdoor',
                
                -- Effectiveness metrics
                total_uses INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                avg_score REAL DEFAULT 0,
                
                -- Score distribution
                score_sum REAL DEFAULT 0,
                
                last_updated TEXT,
                
                UNIQUE(pattern_id, category, context)
            )
        """)
        
        # Prompt template versions with effectiveness
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                content TEXT,
                
                -- Effectiveness tracking
                usage_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                avg_score REAL DEFAULT 0,
                
                created_at TEXT,
                last_used TEXT,
                
                UNIQUE(template_name, version)
            )
        """)
        
        # Index for learned_defaults queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_learned_defaults_cat_ctx
            ON learned_defaults(category, context)
        """)
        
        # Index for pattern_effectiveness queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pattern_eff_cat_ctx
            ON pattern_effectiveness(category, context)
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
                - severity: str (light, moderate, heavy)
                - shape_override: Optional[str]
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
                severity, shape_override,
                context, aging_weight, contamination_weight,
                background, pattern_scores,
                prompt_chars_before_opt, prompt_chars_after_opt,
                pre_validation_passed, pre_validation_errors, pre_validation_warnings,
                val_prompt_length, val_truncated, realism_score, passed,
                physics_issues, red_flags,
                failure_category, retry_count, final_success,
                image_path, image_size_kb, notes
            ) VALUES (
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?,
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
            generation_params.get('severity', 'moderate'),
            generation_params.get('shape_override'),
            
            # Context parameters (for learning)
            generation_params.get('context', 'outdoor'),
            generation_params.get('aging_weight'),
            generation_params.get('contamination_weight'),
            generation_params.get('background'),
            json.dumps(generation_params.get('pattern_scores', {})),
            
            # Optimization metrics
            generation_params.get('prompt_chars_before_opt'),
            generation_params.get('prompt_chars_after_opt'),
            generation_params.get('pre_validation_passed'),
            generation_params.get('pre_validation_errors'),
            generation_params.get('pre_validation_warnings'),
            
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
    
    def get_severity_stats(self) -> Dict:
        """
        Get success statistics by contamination severity level.
        
        Returns:
            Dict with stats for each severity level (light, moderate, heavy)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        for severity in ['light', 'moderate', 'heavy']:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed,
                    AVG(realism_score) as avg_score
                FROM generation_attempts
                WHERE severity = ?
            """, (severity,))
            
            total, passed, avg_score = cursor.fetchone()
            stats[severity] = {
                'total': total or 0,
                'passed': passed or 0,
                'success_rate': (passed / total * 100) if total else 0,
                'avg_score': round(avg_score, 1) if avg_score else 0
            }
        
        conn.close()
        return stats
    
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
    
    def get_category_feedback(self, material_category: str, limit: int = 10) -> str:
        """
        Get accumulated feedback for a specific material category PLUS global feedback.
        
        Retrieves feedback from:
        1. Failed attempts in the same category (category-specific learning)
        2. Global feedback (category='all_categories') that applies to ALL materials
        
        Args:
            material_category: Material category (e.g., "metal_ferrous", "wood_hardwood")
            limit: Maximum number of feedback items to retrieve
            
        Returns:
            Formatted feedback string to add to prompts (empty if no feedback)
            
        Example:
            feedback = logger.get_category_feedback("metal_ferrous")
            # Returns: "LEARNED FROM PREVIOUS ATTEMPTS:
            #          [GLOBAL] Generic oil contamination is unrealistic
            #          - Clean side contaminated - must be visibly clean
            #          - Rust not visible enough - needs higher contrast"
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get feedback from BOTH category-specific AND global sources
        cursor.execute("""
            SELECT DISTINCT feedback_text, COUNT(*) as occurrences,
                   CASE WHEN category = 'all_categories' THEN 1 ELSE 0 END as is_global
            FROM generation_attempts
            WHERE (category = ? OR category = 'all_categories')
                AND passed = 0
                AND feedback_text IS NOT NULL
                AND feedback_text != ''
            GROUP BY feedback_text
            ORDER BY is_global DESC, occurrences DESC, timestamp DESC
            LIMIT ?
        """, (material_category, limit))
        
        feedback_items = []
        for row in cursor.fetchall():
            feedback_text, count, is_global = row
            # Clean up feedback text (remove numbers, clean formatting)
            lines = [line.strip() for line in feedback_text.split('\n') if line.strip()]
            prefix = "[GLOBAL] " if is_global else ""
            for line in lines:
                # Remove leading numbers and dashes
                clean_line = line.lstrip('0123456789.-) ')
                if clean_line and clean_line not in feedback_items:
                    feedback_items.append(f"{prefix}{clean_line}")
        
        conn.close()
        
        if not feedback_items:
            return ""
        
        # Format for prompt inclusion
        feedback_str = "LEARNED FROM PREVIOUS ATTEMPTS (category-specific + global):\n"
        for item in feedback_items[:limit]:
            feedback_str += f"- {item}\n"
        
        return feedback_str.strip()
    
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
        
        # NEW: Context effectiveness analysis
        context_stats = self.get_context_effectiveness()
        if any(s['total'] > 0 for s in context_stats.values()):
            print("\n🌍 CONTEXT EFFECTIVENESS:")
            for ctx, stats in context_stats.items():
                if stats['total'] > 0:
                    print(f"   • {ctx}: {stats['success_rate']:.1f}% pass rate, "
                          f"{stats['avg_score']:.1f} avg score ({stats['total']} attempts)")
        
        # NEW: Category-context combinations
        cat_ctx_stats = self.get_category_context_stats()
        if cat_ctx_stats:
            print("\n📊 BEST CATEGORY-CONTEXT COMBINATIONS:")
            for item in cat_ctx_stats[:5]:
                print(f"   • {item['category']} + {item['context']}: "
                      f"{item['success_rate']:.1f}% ({item['avg_score']:.1f} avg, {item['total']} attempts)")
        
        print("\n" + "=" * 70)
    
    def get_context_effectiveness(self) -> Dict[str, Dict]:
        """
        Analyze which contexts produce best results.
        
        Returns:
            Dict mapping context -> {total, passed, success_rate, avg_score}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        for context in ['indoor', 'outdoor', 'industrial', 'marine', 'architectural']:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed,
                    AVG(realism_score) as avg_score,
                    AVG(aging_weight) as avg_aging_weight,
                    AVG(contamination_weight) as avg_contam_weight
                FROM generation_attempts
                WHERE context = ?
            """, (context,))
            
            row = cursor.fetchone()
            total, passed, avg_score, avg_aging, avg_contam = row
            stats[context] = {
                'total': total or 0,
                'passed': passed or 0,
                'success_rate': (passed / total * 100) if total else 0,
                'avg_score': round(avg_score, 1) if avg_score else 0,
                'avg_aging_weight': round(avg_aging, 2) if avg_aging else None,
                'avg_contamination_weight': round(avg_contam, 2) if avg_contam else None
            }
        
        conn.close()
        return stats
    
    def get_category_context_stats(self, limit: int = 10) -> List[Dict]:
        """
        Get success rates for category+context combinations.
        
        Identifies which material categories work best with which contexts.
        
        Returns:
            List of dicts sorted by success rate
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                category, context,
                COUNT(*) as total,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed,
                AVG(realism_score) as avg_score
            FROM generation_attempts
            WHERE context IS NOT NULL
            GROUP BY category, context
            HAVING total >= 2
            ORDER BY (passed * 1.0 / total) DESC, avg_score DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            cat, ctx, total, passed, avg_score = row
            results.append({
                'category': cat,
                'context': ctx,
                'total': total,
                'passed': passed,
                'success_rate': (passed / total * 100) if total else 0,
                'avg_score': round(avg_score, 1) if avg_score else 0
            })
        
        conn.close()
        return results
    
    def get_optimal_guidance_scale(self, category: str) -> Optional[float]:
        """
        Suggest optimal guidance_scale based on historical success.
        
        Returns the average guidance_scale of successful attempts for the category.
        
        Args:
            category: Material category
            
        Returns:
            Suggested guidance_scale or None if insufficient data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT AVG(guidance_scale), COUNT(*)
            FROM generation_attempts
            WHERE category = ? AND passed = 1 AND guidance_scale IS NOT NULL
        """, (category,))
        
        avg_scale, count = cursor.fetchone()
        conn.close()
        
        if count and count >= 3:  # Require at least 3 successes
            return round(avg_scale, 1)
        return None
    
    def get_pattern_effectiveness(self, limit: int = 15) -> List[Dict]:
        """
        Analyze which contamination patterns lead to best results.
        
        Returns:
            List of patterns with success metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT patterns_used, passed, realism_score
            FROM generation_attempts
            WHERE patterns_used IS NOT NULL AND patterns_used != '[]'
        """)
        
        pattern_stats = {}
        for row in cursor.fetchall():
            patterns_json, passed, score = row
            patterns = json.loads(patterns_json)
            for pattern in patterns:
                if pattern not in pattern_stats:
                    pattern_stats[pattern] = {'total': 0, 'passed': 0, 'scores': []}
                pattern_stats[pattern]['total'] += 1
                if passed:
                    pattern_stats[pattern]['passed'] += 1
                if score:
                    pattern_stats[pattern]['scores'].append(score)
        
        conn.close()
        
        # Calculate metrics and sort
        results = []
        for pattern, stats in pattern_stats.items():
            if stats['total'] >= 2:  # Minimum 2 uses
                results.append({
                    'pattern': pattern,
                    'total': stats['total'],
                    'passed': stats['passed'],
                    'success_rate': (stats['passed'] / stats['total'] * 100),
                    'avg_score': sum(stats['scores']) / len(stats['scores']) if stats['scores'] else 0
                })
        
        results.sort(key=lambda x: (x['success_rate'], x['avg_score']), reverse=True)
        return results[:limit]
    
    # ================================================================
    # PHASE 2: Learned Defaults System
    # Single source of truth for all learnable parameters
    # ================================================================
    
    def seed_defaults_from_config(self, category_defaults: Dict[str, Dict], force_update: bool = False) -> int:
        """
        Seed learned_defaults table from hardcoded CATEGORY_DEFAULTS.
        
        This migrates hardcoded defaults to SQLite as the single source of truth.
        
        Args:
            category_defaults: Dict mapping category -> {guidance_scale, contamination_uniformity, view_mode}
            force_update: If True, update existing rows with new values (preserves learned stats)
            
        Returns:
            Number of rows inserted or updated
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        modified = 0
        timestamp = datetime.utcnow().isoformat()
        
        for category, defaults in category_defaults.items():
            # Check if already exists
            cursor.execute(
                "SELECT COUNT(*) FROM learned_defaults WHERE category = ?",
                (category,)
            )
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                # Insert new row
                cursor.execute("""
                    INSERT INTO learned_defaults 
                    (category, context, guidance_scale, contamination_uniformity, 
                     view_mode, pass_threshold, sample_count, last_updated)
                    VALUES (?, 'outdoor', ?, ?, ?, 75.0, 0, ?)
                """, (
                    category,
                    defaults.get('guidance_scale', 15.0),
                    defaults.get('contamination_uniformity', 3),
                    defaults.get('view_mode', 'Contextual'),
                    timestamp
                ))
                modified += 1
            elif force_update:
                # Update existing row (preserve sample_count, success_count, avg_score)
                cursor.execute("""
                    UPDATE learned_defaults 
                    SET guidance_scale = ?, contamination_uniformity = ?, 
                        view_mode = ?, last_updated = ?
                    WHERE category = ? AND context = 'outdoor'
                """, (
                    defaults.get('guidance_scale', 15.0),
                    defaults.get('contamination_uniformity', 3),
                    defaults.get('view_mode', 'Contextual'),
                    timestamp,
                    category
                ))
                modified += 1
        
        conn.commit()
        conn.close()
        
        if modified > 0:
            action = "seeded/updated" if force_update else "seeded"
            logger.info(f"📊 {action.capitalize()} {modified} category defaults in learning database")
        
        return modified
    
    def get_learned_defaults(self, category: str, context: str = 'outdoor') -> Optional[Dict]:
        """
        Get learned optimal parameters for a category+context combination.
        
        Returns None if no learned data exists (caller should use fallback or fail).
        
        Args:
            category: Material category (e.g., 'metals_ferrous')
            context: Environment context (e.g., 'outdoor')
            
        Returns:
            Dict with guidance_scale, contamination_uniformity, pass_threshold, etc.
            or None if no data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT guidance_scale, contamination_uniformity, pass_threshold,
                   aging_weight, contamination_weight, avg_score, sample_count, view_mode
            FROM learned_defaults
            WHERE category = ? AND context = ?
        """, (category, context))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'guidance_scale': row[0],
            'contamination_uniformity': row[1],
            'pass_threshold': row[2],
            'aging_weight': row[3],
            'contamination_weight': row[4],
            'avg_score': row[5],
            'sample_count': row[6],
            'view_mode': row[7] or 'Contextual',
            'source': 'learned'
        }
    
    def update_learned_defaults_from_success(
        self,
        category: str,
        context: str,
        guidance_scale: float,
        realism_score: float,
        aging_weight: Optional[float] = None,
        contamination_weight: Optional[float] = None
    ):
        """
        Update learned defaults when a generation succeeds.
        
        Uses exponential moving average (EMA) to incorporate new successful params.
        
        Args:
            category: Material category
            context: Environment context
            guidance_scale: Guidance scale that worked
            realism_score: Score achieved
            aging_weight: Weight used (if applicable)
            contamination_weight: Weight used (if applicable)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        
        # EMA alpha (0.1 = slow adaptation, 0.3 = faster)
        alpha = 0.15
        
        # Get current values
        cursor.execute("""
            SELECT guidance_scale, avg_score, sample_count, success_count,
                   aging_weight, contamination_weight
            FROM learned_defaults
            WHERE category = ? AND context = ?
        """, (category, context))
        
        row = cursor.fetchone()
        
        if row:
            # Update existing with EMA
            old_guidance = row[0] or guidance_scale
            old_score = row[1] or realism_score
            sample_count = (row[2] or 0) + 1
            success_count = (row[3] or 0) + 1
            old_aging = row[4]
            old_contam = row[5]
            
            new_guidance = old_guidance * (1 - alpha) + guidance_scale * alpha
            new_score = old_score * (1 - alpha) + realism_score * alpha
            new_aging = old_aging * (1 - alpha) + aging_weight * alpha if aging_weight and old_aging else aging_weight
            new_contam = old_contam * (1 - alpha) + contamination_weight * alpha if contamination_weight and old_contam else contamination_weight
            
            cursor.execute("""
                UPDATE learned_defaults
                SET guidance_scale = ?,
                    avg_score = ?,
                    sample_count = ?,
                    success_count = ?,
                    aging_weight = ?,
                    contamination_weight = ?,
                    last_updated = ?
                WHERE category = ? AND context = ?
            """, (new_guidance, new_score, sample_count, success_count,
                  new_aging, new_contam, timestamp, category, context))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO learned_defaults
                (category, context, guidance_scale, avg_score, sample_count, success_count,
                 aging_weight, contamination_weight, pass_threshold, last_updated)
                VALUES (?, ?, ?, ?, 1, 1, ?, ?, 75.0, ?)
            """, (category, context, guidance_scale, realism_score,
                  aging_weight, contamination_weight, timestamp))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"📈 Updated learned defaults for {category}/{context}")
    
    def update_pattern_effectiveness(
        self,
        patterns_used: List[str],
        category: str,
        context: str,
        passed: bool,
        realism_score: float
    ):
        """
        Update pattern effectiveness based on generation outcome.
        
        Args:
            patterns_used: List of pattern IDs used
            category: Material category
            context: Environment context  
            passed: Whether generation passed validation
            realism_score: Score achieved
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        
        for pattern_id in patterns_used:
            # Check if exists
            cursor.execute("""
                SELECT total_uses, success_count, score_sum
                FROM pattern_effectiveness
                WHERE pattern_id = ? AND category = ? AND context = ?
            """, (pattern_id, category, context))
            
            row = cursor.fetchone()
            
            if row:
                total = row[0] + 1
                successes = row[1] + (1 if passed else 0)
                score_sum = row[2] + (realism_score or 0)
                avg_score = score_sum / total
                
                cursor.execute("""
                    UPDATE pattern_effectiveness
                    SET total_uses = ?,
                        success_count = ?,
                        score_sum = ?,
                        avg_score = ?,
                        last_updated = ?
                    WHERE pattern_id = ? AND category = ? AND context = ?
                """, (total, successes, score_sum, avg_score, timestamp,
                      pattern_id, category, context))
            else:
                cursor.execute("""
                    INSERT INTO pattern_effectiveness
                    (pattern_id, category, context, total_uses, success_count, 
                     score_sum, avg_score, last_updated)
                    VALUES (?, ?, ?, 1, ?, ?, ?, ?)
                """, (pattern_id, category, context, 
                      1 if passed else 0, realism_score or 0, realism_score or 0, 
                      timestamp))
        
        conn.commit()
        conn.close()
    
    def get_best_patterns_for_category(
        self,
        category: str,
        context: str = 'outdoor',
        limit: int = 5,
        min_uses: int = 2
    ) -> List[Dict]:
        """
        Get most effective patterns for a category+context based on learning data.
        
        Args:
            category: Material category
            context: Environment context
            limit: Max patterns to return
            min_uses: Minimum uses to be considered
            
        Returns:
            List of pattern dicts sorted by effectiveness
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_id, total_uses, success_count, avg_score,
                   (success_count * 1.0 / total_uses) as success_rate
            FROM pattern_effectiveness
            WHERE category = ? AND context = ? AND total_uses >= ?
            ORDER BY success_rate DESC, avg_score DESC
            LIMIT ?
        """, (category, context, min_uses, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'pattern_id': row[0],
                'total_uses': row[1],
                'success_count': row[2],
                'avg_score': round(row[3], 1) if row[3] else 0,
                'success_rate': round(row[4] * 100, 1) if row[4] else 0
            })
        
        conn.close()
        return results
    
    def get_suggested_threshold(self, category: str, context: str = 'outdoor') -> float:
        """
        Get suggested pass threshold based on what's achievable for this combination.
        
        Uses 25th percentile of successful scores (conservative) or default 75.0.
        
        Args:
            category: Material category
            context: Environment context
            
        Returns:
            Suggested threshold (default 75.0 if insufficient data)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get scores from passed attempts
        cursor.execute("""
            SELECT realism_score
            FROM generation_attempts
            WHERE category = ? AND context = ? AND passed = 1
            ORDER BY realism_score ASC
        """, (category, context))
        
        scores = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        
        if len(scores) >= 5:
            # Use 25th percentile as threshold (achievable but quality)
            idx = len(scores) // 4
            return max(scores[idx], 60.0)  # Floor at 60
        
        return 75.0  # Default
    
    def print_learned_defaults_report(self):
        """Print report of learned defaults."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("\n" + "=" * 80)
        print("📊 LEARNED DEFAULTS REPORT (Single Source of Truth)")
        print("=" * 80)
        
        cursor.execute("""
            SELECT category, context, guidance_scale, contamination_uniformity, 
                   view_mode, pass_threshold, avg_score, sample_count, success_count
            FROM learned_defaults
            ORDER BY category, context
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("\n⚠️  No learned defaults yet. Run --seed-defaults or generate images.")
        else:
            print(f"\n{'Category':<28} {'Ctx':<8} {'G.Scl':<6} {'Unif':<5} {'ViewMode':<12} {'Samples':<8}")
            print("-" * 80)
            for row in rows:
                cat, ctx, gs, unif, vm, thresh, avg, samples, successes = row
                success_rate = (successes / samples * 100) if samples else 0
                vm_short = (vm or 'Contextual')[:11]
                print(f"{cat:<28} {ctx:<8} {gs or 15.0:<6.1f} {unif or 3:<5} {vm_short:<12} {samples or 0:<8} ({success_rate:.0f}%)")
        
        conn.close()
        print("\n" + "=" * 80)


def create_logger(db_path: Optional[Path] = None) -> ImageGenerationLogger:
    """Factory function to create image generation logger."""
    return ImageGenerationLogger(db_path=db_path)
