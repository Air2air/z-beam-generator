"""
Consolidated Learning System - Unified Learning Database

Simplifies learning integration by consolidating 3 separate systems into one:
- SweetSpotAnalyzer (parameter learning)
- WeightLearner (quality weight learning)
- ValidationWinstonCorrelator (correlation analysis)

BEFORE (3 separate databases, 3 write operations):
    sweet_spot_analyzer.log_generation(...)
    weight_learner.update_weights(...)
    validation_correlator.log_correlation(...)

AFTER (1 database, 1 write operation):
    learning_system.log_generation(result)
    # All learning data logged in single transaction

Created: January 20, 2026
Purpose: Reduce learning complexity from 3 systems to 1 unified interface
"""

import logging
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Complete generation result for learning"""
    material_name: str
    component_type: str
    content: str
    
    # Quality scores
    winston_score: float
    realism_score: float
    voice_authenticity_score: float
    structural_quality_score: float
    ai_pattern_score: float
    
    # Generation parameters
    temperature: float
    frequency_penalty: float
    presence_penalty: float
    
    # Metadata
    word_count: int
    char_count: int
    author_id: int
    timestamp: datetime


class ConsolidatedLearningSystem:
    """
    Unified learning system consolidating all learning functionality.
    
    Replaces 3 separate systems with single database and unified interface:
    - Parameter optimization (sweet spot analysis)
    - Quality weight learning
    - Correlation analysis (validation → Winston)
    
    Architecture:
        1. Single SQLite database with optimized schema
        2. Unified logging method for all generation data
        3. Consolidated query methods for learned insights
        4. Automatic database migrations and cleanup
    """
    
    def __init__(self, db_path: str = 'z-beam.db'):
        """
        Initialize consolidated learning system.
        
        Args:
            db_path: Path to SQLite learning database
        """
        self.db_path = Path(db_path)
        self._init_database()
        
        logger.info(f"✅ Consolidated learning system initialized: {db_path}")
    
    def _init_database(self) -> None:
        """Initialize consolidated database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Single unified generations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    material_name TEXT NOT NULL,
                    component_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    
                    -- Quality scores
                    winston_score REAL,
                    realism_score REAL,
                    voice_authenticity_score REAL,
                    structural_quality_score REAL,
                    ai_pattern_score REAL,
                    overall_quality_score REAL,
                    
                    -- Generation parameters
                    temperature REAL NOT NULL,
                    frequency_penalty REAL NOT NULL,
                    presence_penalty REAL NOT NULL,
                    
                    -- Metadata
                    word_count INTEGER,
                    char_count INTEGER,
                    author_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes separately (SQLite doesn't allow inline INDEX with CREATE TABLE)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_component_type ON generations (component_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_scores ON generations (overall_quality_score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON generations (timestamp)")
            
            # Quality weights learning table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_weights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component_type TEXT NOT NULL,
                    winston_weight REAL DEFAULT 0.4,
                    realism_weight REAL DEFAULT 0.6,
                    voice_weight REAL DEFAULT 0.3,
                    structural_weight REAL DEFAULT 0.2,
                    ai_pattern_weight REAL DEFAULT 0.3,
                    sample_count INTEGER DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    UNIQUE(component_type)
                )
            """)
            
            # Correlation insights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    impact_on_winston REAL,
                    occurrence_count INTEGER DEFAULT 1,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes separately for quality_insights
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_impact ON quality_insights (impact_on_winston)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_seen ON quality_insights (last_seen)")

            # Grok evaluator feedback table (additive; linked to generations.id)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grok_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    generation_id INTEGER NOT NULL,
                    schema_version TEXT NOT NULL,
                    prompt_version TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    model TEXT NOT NULL,

                    weighted_score REAL NOT NULL,
                    confidence REAL NOT NULL,
                    score_band TEXT NOT NULL,
                    pass_gate INTEGER NOT NULL,

                    overall_min REAL NOT NULL,
                    confidence_min REAL NOT NULL,

                    fail_reasons_json TEXT,
                    actions_json TEXT,
                    raw_payload_json TEXT NOT NULL,

                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (generation_id) REFERENCES generations(id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_grok_eval_generation ON grok_evaluations(generation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_grok_eval_score ON grok_evaluations(weighted_score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_grok_eval_pass ON grok_evaluations(pass_gate)")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grok_evaluation_criteria (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    grok_evaluation_id INTEGER NOT NULL,
                    criterion_key TEXT NOT NULL,
                    score REAL NOT NULL,
                    weight REAL NOT NULL,
                    min_score REAL NOT NULL,
                    evidence_json TEXT,
                    issues_json TEXT,

                    FOREIGN KEY (grok_evaluation_id) REFERENCES grok_evaluations(id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_grok_eval_criterion ON grok_evaluation_criteria(criterion_key, score)")
            
            conn.commit()
    
    def log_generation(self, result: GenerationResult) -> int:
        """
        Log complete generation result for learning.
        
        Single method replaces 3 separate logging operations.
        
        Args:
            result: GenerationResult with all quality scores and parameters
            
        Returns:
            Generation ID for reference
        """
        # Calculate overall quality score (weighted average)
        overall_score = (
            result.winston_score * 0.4 +
            result.realism_score * 0.6 +
            result.voice_authenticity_score * 0.3 +
            result.structural_quality_score * 0.2 +
            result.ai_pattern_score * 0.3
        ) / 2.3  # Normalize to 0-100 scale
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO generations (
                    material_name, component_type, content,
                    winston_score, realism_score, voice_authenticity_score,
                    structural_quality_score, ai_pattern_score, overall_quality_score,
                    temperature, frequency_penalty, presence_penalty,
                    word_count, char_count, author_id, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.material_name, result.component_type, result.content,
                result.winston_score, result.realism_score, result.voice_authenticity_score,
                result.structural_quality_score, result.ai_pattern_score, overall_score,
                result.temperature, result.frequency_penalty, result.presence_penalty,
                result.word_count, result.char_count, result.author_id,
                result.timestamp.isoformat()
            ))
            
            generation_id = cursor.lastrowid
            conn.commit()
            
            logger.debug(f"Logged generation {generation_id} for {result.material_name}/{result.component_type}")
            return generation_id
    
    def get_optimal_parameters(self, component_type: str) -> Optional[Dict]:
        """
        Get optimal parameters learned from high-quality generations.
        
        Replaces SweetSpotAnalyzer.get_learned_parameters()
        
        Args:
            component_type: Type of component
            
        Returns:
            Dict with optimal temperature, penalties, and confidence metrics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get top 25% of generations by quality score
            # Calculate 75th percentile using portable SQL (ORDER BY + LIMIT)
            cursor.execute("""
                WITH ranked_scores AS (
                    SELECT overall_quality_score
                    FROM generations
                    WHERE component_type = ?
                      AND overall_quality_score IS NOT NULL
                      AND timestamp > datetime('now', '-30 days')
                    ORDER BY overall_quality_score DESC
                ),
                percentile_75 AS (
                    SELECT overall_quality_score as p75_score
                    FROM ranked_scores
                    LIMIT 1 OFFSET (SELECT COUNT(*) / 4 FROM ranked_scores)
                )
                SELECT temperature, frequency_penalty, presence_penalty,
                       overall_quality_score, COUNT(*) as sample_count
                FROM generations
                WHERE component_type = ?
                  AND overall_quality_score IS NOT NULL
                  AND timestamp > datetime('now', '-30 days')
                  AND overall_quality_score >= (SELECT p75_score FROM percentile_75)
                GROUP BY temperature, frequency_penalty, presence_penalty
                ORDER BY AVG(overall_quality_score) DESC
                LIMIT 1
            """, (component_type, component_type))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'temperature': row[0],
                    'frequency_penalty': row[1],
                    'presence_penalty': row[2],
                    'quality_score': row[3],
                    'sample_count': row[4],
                    'confidence': min(row[4] / 10.0, 1.0)  # Confidence increases with samples
                }
            
            return None
    
    def get_quality_weights(self, component_type: str = 'default') -> Dict[str, float]:
        """
        Get learned quality weights for evaluation.
        
        Replaces WeightLearner.get_learned_quality_weights()
        
        Args:
            component_type: Type of component (or 'default')
            
        Returns:
            Dict with quality dimension weights
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT winston_weight, realism_weight, voice_weight,
                       structural_weight, ai_pattern_weight
                FROM quality_weights
                WHERE component_type = ?
            """, (component_type,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'winston_ai': row[0],
                    'realism': row[1],
                    'voice_authenticity': row[2],
                    'structural_quality': row[3],
                    'ai_patterns': row[4]
                }

            raise RuntimeError(
                f"No learned quality weights found for component_type='{component_type}'"
            )
    
    def get_recent_insights(self, lookback_days: int = 7, limit: int = 3) -> List[Dict]:
        """
        Get recent quality insights and correlation patterns.
        
        Replaces ValidationWinstonCorrelator.get_top_issues()
        
        Args:
            lookback_days: Number of days to look back
            limit: Maximum number of insights to return
            
        Returns:
            List of quality insights with impact scores
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT issue_type, description, impact_on_winston, occurrence_count
                FROM quality_insights
                WHERE last_seen > datetime('now', '-' || ? || ' days')
                ORDER BY ABS(impact_on_winston) DESC
                LIMIT ?
            """, (lookback_days, limit))
            
            insights = []
            for row in cursor.fetchall():
                insights.append({
                    'issue': row[0],
                    'description': row[1],
                    'impact': row[2],
                    'occurrences': row[3]
                })
            
            return insights
    
    def update_quality_weights(
        self,
        component_type: str,
        weights: Dict[str, float],
        sample_count: int
    ) -> None:
        """
        Update learned quality weights based on correlation analysis.
        
        Args:
            component_type: Type of component
            weights: New quality dimension weights
            sample_count: Number of samples used for learning
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            required_keys = [
                'winston_ai',
                'realism',
                'voice_authenticity',
                'structural_quality',
                'ai_patterns',
            ]
            missing = [key for key in required_keys if key not in weights]
            if missing:
                raise KeyError(
                    f"weights missing required keys: {', '.join(missing)}"
                )
            
            cursor.execute("""
                INSERT OR REPLACE INTO quality_weights (
                    component_type, winston_weight, realism_weight, voice_weight,
                    structural_weight, ai_pattern_weight, sample_count, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                component_type,
                weights['winston_ai'],
                weights['realism'],
                weights['voice_authenticity'],
                weights['structural_quality'],
                weights['ai_patterns'],
                sample_count
            ))
            
            conn.commit()
            logger.debug(f"Updated quality weights for {component_type}")
    
    def log_quality_insight(
        self,
        issue_type: str,
        description: str,
        impact_on_winston: float
    ) -> None:
        """
        Log a quality insight from correlation analysis.
        
        Args:
            issue_type: Type of quality issue
            description: Human-readable description
            impact_on_winston: Impact on Winston AI score (-100 to +100)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update or insert insight
            cursor.execute("""
                INSERT INTO quality_insights (issue_type, description, impact_on_winston, occurrence_count, last_seen)
                VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(issue_type) DO UPDATE SET
                    occurrence_count = occurrence_count + 1,
                    last_seen = CURRENT_TIMESTAMP
            """, (issue_type, description, impact_on_winston))
            
            conn.commit()

    def log_grok_evaluation(self, generation_id: int, evaluation_payload: Dict[str, Any]) -> int:
        """
        Persist Grok humanness evaluation payload linked to a generation.

        Args:
            generation_id: Foreign key to generations.id
            evaluation_payload: Schema-validated Grok evaluation JSON payload

        Returns:
            Inserted grok_evaluations.id
        """
        if not isinstance(generation_id, int):
            raise TypeError("generation_id must be an integer")

        required_top_keys = [
            'schemaVersion',
            'evaluator',
            'scores',
            'aggregation',
            'gates',
            'actions',
        ]
        missing_top_keys = [key for key in required_top_keys if key not in evaluation_payload]
        if missing_top_keys:
            raise KeyError(f"evaluation_payload missing required keys: {', '.join(missing_top_keys)}")

        evaluator = evaluation_payload['evaluator']
        aggregation = evaluation_payload['aggregation']
        gates = evaluation_payload['gates']
        thresholds = gates['thresholds']
        scores = evaluation_payload['scores']
        weights = aggregation['weights']
        criterion_mins = thresholds['criterionMins']

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO grok_evaluations (
                    generation_id,
                    schema_version,
                    prompt_version,
                    mode,
                    model,
                    weighted_score,
                    confidence,
                    score_band,
                    pass_gate,
                    overall_min,
                    confidence_min,
                    fail_reasons_json,
                    actions_json,
                    raw_payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                generation_id,
                evaluation_payload['schemaVersion'],
                evaluator['promptVersion'],
                evaluator['mode'],
                evaluator['model'],
                aggregation['weightedScore'],
                aggregation['confidence'],
                aggregation['scoreBand'],
                int(bool(gates['pass'])),
                thresholds['overallMin'],
                thresholds['confidenceMin'],
                json.dumps(gates['failReasons']),
                json.dumps(evaluation_payload['actions']),
                json.dumps(evaluation_payload),
            ))

            grok_evaluation_id = cursor.lastrowid

            for criterion_key, score_obj in scores.items():
                cursor.execute("""
                    INSERT INTO grok_evaluation_criteria (
                        grok_evaluation_id,
                        criterion_key,
                        score,
                        weight,
                        min_score,
                        evidence_json,
                        issues_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    grok_evaluation_id,
                    criterion_key,
                    score_obj['score'],
                    weights[criterion_key],
                    criterion_mins[criterion_key],
                    json.dumps(score_obj['evidence']),
                    json.dumps(score_obj['issues']),
                ))

            conn.commit()

        logger.debug(
            f"Logged Grok evaluation {grok_evaluation_id} for generation_id={generation_id}"
        )
        return grok_evaluation_id
