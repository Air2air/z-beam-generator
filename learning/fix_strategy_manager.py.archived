"""
Fix Strategy Manager

Standardizes and tracks fix strategies for different failure patterns.
Learns which fixes work over time, similar to Winston detection learning.

Architecture:
- Analyzes failure patterns (from WinstonFeedbackAnalyzer)
- Selects appropriate fix strategy (from fix_strategies.py)
- Tracks fix effectiveness in database
- Learns optimal adjustments over time

Similar to WinstonFeedbackAnalyzer but for parameter adjustments instead of detection.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from learning.fix_strategies import (
    get_strategies_for_failure_type,
    get_strategy_by_id,
    get_alternative_strategies,
    DEFAULT_STRATEGY_ORDER
)

logger = logging.getLogger(__name__)


class FixStrategyManager:
    """
    Manages fix strategies and learns from their success/failure.
    
    Key capabilities:
    1. Select appropriate fix based on failure analysis
    2. Track which fixes were applied
    3. Log outcomes (success/failure)
    4. Learn which fixes work best for each failure type
    5. Automatically switch to better strategies
    
    Similar to WinstonFeedbackAnalyzer pattern.
    """
    
    def __init__(self, feedback_db):
        """
        Initialize fix strategy manager.
        
        Args:
            feedback_db: WinstonFeedbackDatabase instance for logging
        """
        self.db = feedback_db
        self.current_fix_attempt = None  # Track current fix for logging
        
        # Ensure fix tracking tables exist
        self._initialize_tables()
    
    def _initialize_tables(self):
        """
        Create fix tracking tables in database if they don't exist.
        
        Tables:
        - fix_attempts: Every fix application
        - fix_outcomes: Success/failure results
        - fix_statistics: Aggregated learning data
        """
        try:
            import sqlite3
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Track every fix attempt
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS fix_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        detection_id INTEGER,
                        attempt_number INTEGER,
                        failure_type TEXT,
                        strategy_id TEXT,
                        strategy_name TEXT,
                        temperature_adjustment REAL,
                        voice_adjustments TEXT,  -- JSON
                        enrichment_adjustments TEXT,  -- JSON
                        rationale TEXT,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (detection_id) REFERENCES detection_results(id)
                    )
                """)
                
                # Track fix outcomes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS fix_outcomes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fix_attempt_id INTEGER,
                        next_detection_id INTEGER,
                        success BOOLEAN,
                        human_score_before REAL,
                        human_score_after REAL,
                        improvement REAL,
                        effective BOOLEAN,
                        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (fix_attempt_id) REFERENCES fix_attempts(id),
                        FOREIGN KEY (next_detection_id) REFERENCES detection_results(id)
                    )
                """)
                
                # Aggregate learning statistics
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS fix_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        failure_type TEXT,
                        material TEXT,
                        component_type TEXT,
                        strategy_id TEXT,
                        strategy_name TEXT,
                        success_count INTEGER DEFAULT 0,
                        failure_count INTEGER DEFAULT 0,
                        success_rate REAL,
                        avg_improvement REAL,
                        times_used INTEGER DEFAULT 0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(failure_type, material, component_type, strategy_id)
                    )
                """)
                
                conn.commit()
            
            logger.info("✅ [FIX STRATEGY] Database tables initialized")
            
        except Exception as e:
            logger.error(f"❌ [FIX STRATEGY] Failed to initialize tables: {e}")
    
    def get_fix_strategy(
        self,
        failure_analysis: Dict[str, Any],
        attempt: int,
        material: str,
        component_type: str,
        previous_strategy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get appropriate fix strategy based on failure analysis.
        
        Args:
            failure_analysis: Output from WinstonFeedbackAnalyzer.analyze_failure()
            attempt: Current attempt number (1-based)
            material: Material name
            component_type: Component type (caption, subtitle, etc.)
            previous_strategy_id: Strategy used in previous attempt (if any)
            
        Returns:
            Dict with strategy details and adjustments to apply
        """
        failure_type = failure_analysis.get('failure_type', 'unknown')
        
        logger.info(f"🔧 [FIX STRATEGY] Selecting strategy for {failure_type} failure (attempt {attempt})")
        
        # Step 1: Check if we have learned data for this specific case
        learned_strategy = self._get_learned_strategy(failure_type, material, component_type)
        
        if learned_strategy:
            logger.info(f"📊 [FIX STRATEGY] Using learned strategy: {learned_strategy['strategy_name']}")
            logger.info(f"   Success rate: {learned_strategy['success_rate']*100:.1f}%")
            logger.info(f"   Avg improvement: {learned_strategy['avg_improvement']:.1f}%")
            return self._build_strategy_response(learned_strategy, failure_analysis)
        
        # Step 2: Get applicable strategies for this failure type
        strategies = get_strategies_for_failure_type(failure_type, attempt)
        
        if not strategies:
            logger.warning(f"⚠️  [FIX STRATEGY] No strategies found for {failure_type}, using standard progression")
            return self._build_default_strategy(failure_analysis)
        
        # Step 3: If previous strategy failed, try alternative
        if previous_strategy_id and attempt > 3:
            alternatives = get_alternative_strategies(previous_strategy_id, attempt)
            if alternatives:
                strategy = alternatives[0]
                logger.info(f"🔄 [FIX STRATEGY] Switching to alternative: {strategy['name']}")
            else:
                strategy = strategies[0]
        else:
            # Use primary strategy
            strategy = strategies[0]
        
        logger.info(f"✅ [FIX STRATEGY] Selected: {strategy['name']}")
        logger.info(f"   Rationale: {strategy['rationale']}")
        logger.info(f"   Temperature: {strategy['temperature_adjustment']:+.2f}")
        
        return self._build_strategy_response(strategy, failure_analysis)
    
    def _get_learned_strategy(
        self,
        failure_type: str,
        material: str,
        component_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Query historical data for most effective strategy.
        
        Similar to winston_feedback_db.get_sweet_spot()
        
        Returns:
            Best strategy dict or None if insufficient data
        """
        try:
            import sqlite3
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Query: Best strategy for this specific material/component/failure
                cursor.execute("""
                SELECT 
                    strategy_id,
                    strategy_name,
                    success_rate,
                    avg_improvement,
                    times_used
                FROM fix_statistics
                WHERE failure_type = ?
                    AND material = ?
                    AND component_type = ?
                    AND times_used >= 3
                ORDER BY success_rate DESC, avg_improvement DESC
                LIMIT 1
            """, (failure_type, material, component_type))
            
            row = cursor.fetchone()
            
            if row:
                strategy_id, strategy_name, success_rate, avg_improvement, times_used = row
                strategy = get_strategy_by_id(strategy_id)
                
                if strategy:
                    return {
                        **strategy,
                        'strategy_name': strategy.get('name', strategy_name),  # Ensure strategy_name key exists
                        'success_rate': success_rate,
                        'avg_improvement': avg_improvement,
                        'times_used': times_used,
                        'source': 'learned'
                    }
                
                # Fallback: Best strategy for this failure type across all materials
                cursor.execute("""
                SELECT 
                    strategy_id,
                    strategy_name,
                    AVG(success_rate) as avg_success_rate,
                    AVG(avg_improvement) as avg_improvement,
                    SUM(times_used) as total_uses
                FROM fix_statistics
                WHERE failure_type = ?
                    AND times_used >= 3
                GROUP BY strategy_id, strategy_name
                ORDER BY avg_success_rate DESC, avg_improvement DESC
                LIMIT 1
            """, (failure_type,))
            
            row = cursor.fetchone()
            
            if row:
                strategy_id, strategy_name, avg_success_rate, avg_improvement, total_uses = row
                strategy = get_strategy_by_id(strategy_id)
                
                if strategy:
                    return {
                        **strategy,
                        'success_rate': avg_success_rate,
                        'avg_improvement': avg_improvement,
                        'times_used': total_uses,
                        'source': 'learned_generic'
                    }
                
                return None
            
        except Exception as e:
            logger.warning(f"⚠️  [FIX STRATEGY] Failed to query learned strategies: {e}")
            return None
    
    def _build_strategy_response(
        self,
        strategy: Dict[str, Any],
        failure_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build standardized strategy response.
        
        Returns:
            Dict with all information needed to apply fix
        """
        return {
            'strategy_id': strategy['id'],
            'strategy_name': strategy['name'],
            'temperature_adjustment': strategy['temperature_adjustment'],
            'voice_adjustments': strategy.get('voice_adjustments', {}),
            'enrichment_adjustments': strategy.get('enrichment_adjustments', {}),
            'rationale': strategy['rationale'],
            'confidence': 'high' if strategy.get('success_rate', 0) > 0.7 else 'medium',
            'expected_success_rate': strategy.get('success_rate', 0.0),
            'source': strategy.get('source', 'predefined'),
            'failure_analysis': failure_analysis
        }
    
    def _build_default_strategy(self, failure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build default strategy when no specific strategy found.
        
        Returns:
            Basic temperature increase strategy
        """
        return {
            'strategy_id': 'default_progression',
            'strategy_name': 'Standard Temperature Progression',
            'temperature_adjustment': +0.05,
            'voice_adjustments': {},
            'enrichment_adjustments': {},
            'rationale': 'No specific strategy available, using standard progression',
            'confidence': 'low',
            'expected_success_rate': 0.0,
            'source': 'default',
            'failure_analysis': failure_analysis
        }
    
    def log_fix_attempt(
        self,
        detection_id: int,
        attempt_number: int,
        strategy: Dict[str, Any],
        material: str,
        component_type: str
    ) -> int:
        """
        Log a fix attempt to database.
        
        Args:
            detection_id: ID of detection result that triggered this fix
            attempt_number: Attempt number (1-based)
            strategy: Strategy dict from get_fix_strategy()
            material: Material name
            component_type: Component type
            
        Returns:
            Fix attempt ID
        """
        try:
            import sqlite3
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO fix_attempts (
                    detection_id,
                    attempt_number,
                    failure_type,
                    strategy_id,
                    strategy_name,
                    temperature_adjustment,
                    voice_adjustments,
                    enrichment_adjustments,
                    rationale
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                detection_id,
                attempt_number,
                strategy['failure_analysis'].get('failure_type', 'unknown'),
                strategy['strategy_id'],
                strategy['strategy_name'],
                strategy['temperature_adjustment'],
                json.dumps(strategy['voice_adjustments']),
                json.dumps(strategy['enrichment_adjustments']),
                strategy['rationale']
                ))
                
                conn.commit()
                fix_attempt_id = cursor.lastrowid
            
            self.current_fix_attempt = {
                'id': fix_attempt_id,
                'detection_id': detection_id,
                'strategy': strategy,
                'material': material,
                'component_type': component_type
            }
            
            logger.info(f"📝 [FIX STRATEGY] Logged fix attempt #{fix_attempt_id}")
            
            return fix_attempt_id
            
        except Exception as e:
            logger.error(f"❌ [FIX STRATEGY] Failed to log fix attempt: {e}")
            return -1
    
    def log_fix_outcome(
        self,
        fix_attempt_id: int,
        next_detection_id: int,
        success: bool,
        human_score_before: float,
        human_score_after: float,
        material: str,
        component_type: str
    ):
        """
        Log the outcome of a fix attempt.
        
        Args:
            fix_attempt_id: ID of fix attempt
            next_detection_id: ID of detection result after fix
            success: Whether generation passed after fix
            human_score_before: Human score before fix
            human_score_after: Human score after fix
            material: Material name
            component_type: Component type
        """
        try:
            improvement = human_score_after - human_score_before
            effective = improvement > 0  # Any improvement is effective
            
            import sqlite3
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Log outcome
                cursor.execute("""
                INSERT INTO fix_outcomes (
                    fix_attempt_id,
                    next_detection_id,
                    success,
                    human_score_before,
                    human_score_after,
                    improvement,
                    effective
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                fix_attempt_id,
                next_detection_id,
                success,
                human_score_before,
                human_score_after,
                improvement,
                effective
                ))
                
                conn.commit()
            
            # Update statistics
            self._update_statistics(
                fix_attempt_id,
                success,
                improvement,
                material,
                component_type
            )
            
            status = "SUCCESS" if success else "FAILURE"
            logger.info(f"✅ [FIX STRATEGY] Logged outcome: {status} ({improvement:+.1f}% improvement)")
            
        except Exception as e:
            logger.error(f"❌ [FIX STRATEGY] Failed to log fix outcome: {e}")
    
    def _update_statistics(
        self,
        fix_attempt_id: int,
        success: bool,
        improvement: float,
        material: str,
        component_type: str
    ):
        """
        Update aggregated statistics for this fix strategy.
        
        Args:
            fix_attempt_id: Fix attempt ID
            success: Whether it worked
            improvement: Score improvement
            material: Material name
            component_type: Component type
        """
        try:
            import sqlite3
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Get fix attempt details
                cursor.execute("""
                SELECT failure_type, strategy_id, strategy_name
                FROM fix_attempts
                WHERE id = ?
            """, (fix_attempt_id,))
            
            row = cursor.fetchone()
            if not row:
                return
            
            failure_type, strategy_id, strategy_name = row
            
            # Insert or update statistics
            cursor.execute("""
                INSERT INTO fix_statistics (
                    failure_type,
                    material,
                    component_type,
                    strategy_id,
                    strategy_name,
                    success_count,
                    failure_count,
                    success_rate,
                    avg_improvement,
                    times_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(failure_type, material, component_type, strategy_id) DO UPDATE SET
                    success_count = success_count + ?,
                    failure_count = failure_count + ?,
                    times_used = times_used + 1,
                    success_rate = CAST(success_count AS REAL) / times_used,
                    avg_improvement = (avg_improvement * (times_used - 1) + ?) / times_used,
                    last_updated = CURRENT_TIMESTAMP
            """, (
                failure_type,
                material,
                component_type,
                strategy_id,
                strategy_name,
                1 if success else 0,
                0 if success else 1,
                1.0 if success else 0.0,
                improvement,
                1,
                1 if success else 0,
                0 if success else 1,
                improvement
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ [FIX STRATEGY] Failed to update statistics: {e}")
    
    def get_fix_effectiveness_report(
        self,
        material: Optional[str] = None,
        failure_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate fix effectiveness report.
        
        Args:
            material: Optional material filter
            failure_type: Optional failure type filter
            
        Returns:
            Report dict with statistics and insights
        """
        try:
            import sqlite3
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with optional filters
            where_clauses = []
            params = []
            
            if material:
                where_clauses.append("material = ?")
                params.append(material)
            
            if failure_type:
                where_clauses.append("failure_type = ?")
                params.append(failure_type)
            
            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
            
            # Get overall statistics
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_fixes,
                    SUM(success_count) as total_successes,
                    SUM(failure_count) as total_failures,
                    AVG(success_rate) as avg_success_rate,
                    AVG(avg_improvement) as avg_improvement
                FROM fix_statistics
                {where_sql}
            """, params)
            
            row = cursor.fetchone()
            total_fixes, total_successes, total_failures, avg_success_rate, avg_improvement = row or (0, 0, 0, 0.0, 0.0)
            
            # Get top strategies
            cursor.execute(f"""
                SELECT 
                    strategy_name,
                    failure_type,
                    success_rate,
                    avg_improvement,
                    times_used
                FROM fix_statistics
                {where_sql}
                ORDER BY success_rate DESC, avg_improvement DESC
                LIMIT 10
            """, params)
            
            top_strategies = [
                {
                    'name': row[0],
                    'failure_type': row[1],
                    'success_rate': row[2],
                    'avg_improvement': row[3],
                    'times_used': row[4]
                }
                for row in cursor.fetchall()
            ]
            
            return {
                'overall': {
                    'total_fixes': total_fixes or 0,
                    'total_successes': total_successes or 0,
                    'total_failures': total_failures or 0,
                    'avg_success_rate': avg_success_rate or 0.0,
                    'avg_improvement': avg_improvement or 0.0
                },
                'top_strategies': top_strategies
            }
            
        except Exception as e:
            logger.error(f"❌ [FIX STRATEGY] Failed to generate report: {e}")
            return {
                'overall': {},
                'top_strategies': [],
                'error': str(e)
            }
