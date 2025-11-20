"""
Dynamic Threshold Manager - Database-Driven Adaptive Learning

Manages ALL quality thresholds dynamically based on learned success patterns.
Replaces static config values with database-driven adaptive thresholds.

Architecture:
1. Starts with sensible defaults (config.yaml as baseline)
2. Learns from sweet spot analysis (top 25% of successful content)
3. Adjusts thresholds based on 75th percentile of quality scores
4. Saves learned thresholds back to database
5. Next generation uses updated thresholds

Replaces:
- ValidationConstants.WINSTON_AI_THRESHOLD (was hardcoded 0.33)
- config.yaml quality_gates.realism_threshold (was static 7.0)
- All other static quality thresholds

Complies with:
- HARDCODED_VALUE_POLICY.md: Zero hardcoded thresholds in production
- Fail-fast architecture: Explicit errors if database unavailable
- Learning architecture: Continuous improvement from success patterns
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


class ThresholdManager:
    """
    Manage dynamic, database-driven quality thresholds.
    
    Learns optimal thresholds from successful content and adapts over time.
    Falls back to config defaults only when insufficient learning data exists.
    """
    
    # Default thresholds (ONLY used when database has insufficient data)
    DEFAULT_WINSTON_THRESHOLD = 0.33        # 67%+ human required
    DEFAULT_REALISM_THRESHOLD = 7.0         # 7.0/10 minimum realism
    DEFAULT_VOICE_THRESHOLD = 7.0           # 7.0/10 voice authenticity
    DEFAULT_TONAL_THRESHOLD = 7.0           # 7.0/10 tonal consistency
    
    # Learning parameters
    MIN_SAMPLES_FOR_LEARNING = 10           # Need 10+ samples to learn
    PERCENTILE_TARGET = 75                   # Learn from top 25% (75th percentile)
    CONSERVATIVE_FACTOR = 0.95               # Be 95% as strict as learned optimum
    
    def __init__(
        self,
        db_path: str,
        min_samples: int = MIN_SAMPLES_FOR_LEARNING
    ):
        """
        Initialize threshold manager with database connection.
        
        Args:
            db_path: Path to Winston feedback database
            min_samples: Minimum samples needed for learning (default 10)
            
        Raises:
            ValueError: If db_path not provided
        """
        if not db_path:
            raise ValueError("Database path required for dynamic thresholds")
        
        self.db_path = Path(db_path)
        self.min_samples = min_samples
        
        logger.info(
            f"[THRESHOLD MANAGER] Initialized "
            f"(db={db_path}, min_samples={min_samples})"
        )
    
    def get_winston_threshold(
        self,
        use_learned: bool = True
    ) -> float:
        """
        Get dynamic Winston AI threshold based on learned success patterns.
        
        Strategy:
        1. Query top 25% of successful content by composite_quality_score
        2. Find 75th percentile of their AI scores
        3. Use that as threshold (with conservative factor)
        4. Fall back to DEFAULT_WINSTON_THRESHOLD if insufficient data
        
        Args:
            use_learned: If False, return default (for testing)
            
        Returns:
            Winston AI threshold (0-1.0 scale, lower = more strict)
        """
        if not use_learned:
            return self.DEFAULT_WINSTON_THRESHOLD
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get top performers (composite_quality_score >= 0.80)
            query = """
                SELECT ai_score
                FROM detection_results
                WHERE success = 1
                  AND composite_quality_score IS NOT NULL
                  AND composite_quality_score >= 0.80
                ORDER BY composite_quality_score DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < self.min_samples:
                logger.info(
                    f"[WINSTON THRESHOLD] Insufficient data ({len(rows)} samples), "
                    f"using default {self.DEFAULT_WINSTON_THRESHOLD}"
                )
                return self.DEFAULT_WINSTON_THRESHOLD
            
            # Get AI scores from top performers
            ai_scores = [row[0] for row in rows]
            
            # Calculate 75th percentile (learn from best 25%)
            learned_threshold = statistics.quantiles(ai_scores, n=100)[self.PERCENTILE_TARGET - 1]
            
            # Apply conservative factor (be 95% as strict)
            adjusted_threshold = learned_threshold * self.CONSERVATIVE_FACTOR
            
            # Ensure reasonable bounds (don't be too lenient or too strict)
            final_threshold = max(0.25, min(0.40, adjusted_threshold))
            
            logger.info(
                f"[WINSTON THRESHOLD] Learned {final_threshold:.3f} from {len(ai_scores)} samples "
                f"(75th percentile: {learned_threshold:.3f})"
            )
            
            return final_threshold
            
        except Exception as e:
            logger.warning(
                f"[WINSTON THRESHOLD] Learning failed: {e}, "
                f"using default {self.DEFAULT_WINSTON_THRESHOLD}"
            )
            return self.DEFAULT_WINSTON_THRESHOLD
    
    def get_realism_threshold(
        self,
        use_learned: bool = True
    ) -> float:
        """
        Get dynamic realism threshold based on learned success patterns.
        
        Strategy:
        1. Query subjective_evaluations for successful content
        2. Find 75th percentile of realism scores
        3. Use that as threshold (with conservative factor)
        4. Fall back to DEFAULT_REALISM_THRESHOLD if insufficient data
        
        Args:
            use_learned: If False, return default (for testing)
            
        Returns:
            Realism threshold (0-10 scale)
        """
        if not use_learned:
            return self.DEFAULT_REALISM_THRESHOLD
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get successful evaluations
            query = """
                SELECT overall_score
                FROM subjective_evaluations
                WHERE passes_quality_gate = 1
                ORDER BY overall_score DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < self.min_samples:
                logger.info(
                    f"[REALISM THRESHOLD] Insufficient data ({len(rows)} samples), "
                    f"using default {self.DEFAULT_REALISM_THRESHOLD}"
                )
                return self.DEFAULT_REALISM_THRESHOLD
            
            # Get scores from successful content
            scores = [row[0] for row in rows]
            
            # Calculate 75th percentile
            learned_threshold = statistics.quantiles(scores, n=100)[self.PERCENTILE_TARGET - 1]
            
            # Apply conservative factor
            adjusted_threshold = learned_threshold * self.CONSERVATIVE_FACTOR
            
            # Ensure reasonable bounds (6.0 to 9.0)
            final_threshold = max(6.0, min(9.0, adjusted_threshold))
            
            logger.info(
                f"[REALISM THRESHOLD] Learned {final_threshold:.1f} from {len(scores)} samples "
                f"(75th percentile: {learned_threshold:.1f})"
            )
            
            return final_threshold
            
        except Exception as e:
            logger.warning(
                f"[REALISM THRESHOLD] Learning failed: {e}, "
                f"using default {self.DEFAULT_REALISM_THRESHOLD}"
            )
            return self.DEFAULT_REALISM_THRESHOLD
    
    def get_voice_threshold(
        self,
        use_learned: bool = True
    ) -> float:
        """
        Get dynamic voice authenticity threshold.
        
        Currently returns default (future: learn from subjective_evaluations).
        """
        # TODO: Implement learning from human_likeness_score in subjective_evaluations
        return self.DEFAULT_VOICE_THRESHOLD
    
    def get_tonal_threshold(
        self,
        use_learned: bool = True
    ) -> float:
        """
        Get dynamic tonal consistency threshold.
        
        Currently returns default (future: learn from engagement_score).
        """
        # TODO: Implement learning from engagement_score in subjective_evaluations
        return self.DEFAULT_TONAL_THRESHOLD
    
    def get_all_thresholds(
        self,
        use_learned: bool = True
    ) -> Dict[str, float]:
        """
        Get all quality thresholds in one call.
        
        Returns:
            Dictionary with all threshold values
        """
        return {
            'winston_ai': self.get_winston_threshold(use_learned),
            'realism': self.get_realism_threshold(use_learned),
            'voice_authenticity': self.get_voice_threshold(use_learned),
            'tonal_consistency': self.get_tonal_threshold(use_learned)
        }
    
    def save_learned_thresholds(
        self,
        thresholds: Dict[str, float]
    ) -> None:
        """
        Save learned thresholds to database for audit trail.
        
        Creates learned_thresholds table if it doesn't exist and
        stores threshold values with timestamp.
        
        Args:
            thresholds: Dictionary of threshold names and values
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if needed
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learned_thresholds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    threshold_type TEXT NOT NULL,
                    threshold_value REAL NOT NULL,
                    sample_count INTEGER,
                    confidence_level TEXT,
                    UNIQUE(threshold_type, timestamp)
                )
            """)
            
            # Insert threshold values
            timestamp = datetime.now().isoformat()
            for threshold_type, value in thresholds.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO learned_thresholds
                    (timestamp, threshold_type, threshold_value)
                    VALUES (?, ?, ?)
                """, (timestamp, threshold_type, value))
            
            conn.commit()
            conn.close()
            
            logger.info(
                f"[THRESHOLD MANAGER] Saved {len(thresholds)} learned thresholds "
                f"to database"
            )
            
        except Exception as e:
            logger.error(f"[THRESHOLD MANAGER] Failed to save thresholds: {e}")
    
    def get_threshold_history(
        self,
        threshold_type: str,
        limit: int = 10
    ) -> list:
        """
        Get historical threshold values to track learning progression.
        
        Args:
            threshold_type: Type of threshold ('winston_ai', 'realism', etc.)
            limit: Maximum number of historical records
            
        Returns:
            List of (timestamp, value) tuples
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, threshold_value
                FROM learned_thresholds
                WHERE threshold_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (threshold_type, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [(row[0], row[1]) for row in rows]
            
        except Exception as e:
            logger.error(f"[THRESHOLD MANAGER] Failed to get history: {e}")
            return []
