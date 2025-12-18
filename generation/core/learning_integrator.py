"""
Learning Integrator for Generation Results

🔄 REUSABILITY: Single learning system for ALL domains
🎯 SEPARATION: ONLY handles learning database operations
🚀 ADAPTABILITY: Log ANY field without changing core schema

This module integrates generation results with the learning system by:
- Logging all generation attempts to learning database
- Tracking quality metrics and parameter correlations
- Updating sweet spot parameters for optimization
- Supporting any domain/component type through flexible context
"""

from typing import Dict, Any, Optional
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class LearningIntegrator:
    """
    🔄 REUSABLE: Single learning system for ALL domains
    🎯 SEPARATION: ONLY handles learning database operations
    🚀 ADAPTABLE: Log ANY field without changing core schema
    
    Integrates generation results with learning system.
    Logs attempts, updates parameters, tracks quality trends.
    
    Usage:
        >>> integrator = LearningIntegrator('learning/detection_results.db')
        >>> 
        >>> detection_id = integrator.log_generation(
        ...     content="Aluminum is lightweight.",
        ...     quality_scores={'winston': 0.85, 'realism': 7.5},
        ...     parameters={'temperature': 0.7, 'frequency_penalty': 0.3},
        ...     context={
        ...         'domain': 'materials',
        ...         'item_name': 'Aluminum',
        ...         'component_type': 'description',
        ...         'author_id': 'todd'
        ...     }
        ... )
    """
    
    def __init__(self, learning_database_path: str):
        """
        Initialize learning integrator.
        
        Args:
            learning_database_path: Path to SQLite learning database
        """
        self.db_path = learning_database_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self) -> None:
        """Ensure database file and tables exist"""
        db_file = Path(self.db_path)
        if not db_file.parent.exists():
            db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Tables created by existing learning system
        # This integrator just uses existing schema
        logger.debug(f"Learning database: {self.db_path}")
    
    def log_generation(
        self, 
        content: str, 
        quality_scores: Dict[str, Any], 
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> int:
        """
        🔄 REUSABLE: Works for materials, settings, contaminants, compounds
        🚀 ADAPTABLE: 'context' dict accepts ANY fields
        
        Log generation attempt to learning database.
        
        Args:
            content: Generated text (ANY domain)
            quality_scores: From QualityOrchestrator (domain-agnostic)
                Expected keys: 'winston', 'subjective', 'structural', 'overall_quality'
            parameters: Generation params (temperature, penalties, etc.)
            context: Flexible context dict with ANY fields:
                Required:
                - 'domain': 'materials' | 'settings' | 'contaminants' | 'compounds'
                - 'item_name': Name of item (material, setting, etc.)
                - 'component_type': Type of content generated
                Optional:
                - 'author_id': Author persona ID
                - 'custom_field': Any additional field
                - ... any other fields
        
        Returns:
            Detection ID (for tracking)
        """
        # Extract standard fields
        domain = context.get('domain', 'materials')
        item_name = context.get('item_name', 'Unknown')
        component_type = context.get('component_type', 'text')
        author_id = context.get('author_id', 'unknown')
        
        # Extract quality scores
        winston_score = self._extract_winston_score(quality_scores)
        subjective_score = self._extract_subjective_score(quality_scores)
        overall_quality = quality_scores.get('overall_quality', 0.0)
        passed = quality_scores.get('passed', False)
        
        # Log to database
        detection_id = self._insert_to_database(
            content=content,
            winston_human_score=winston_score,
            subjective_score=subjective_score,
            overall_quality=overall_quality,
            passed=passed,
            parameters=parameters,
            domain=domain,
            item_name=item_name,
            component_type=component_type,
            author_id=author_id,
            extra_context=context
        )
        
        logger.info(
            f"Logged generation to learning database: "
            f"id={detection_id}, domain={domain}, item={item_name}, "
            f"quality={overall_quality:.2f}"
        )
        
        # Update sweet_spot_samples if quality high
        if overall_quality > 0.8:
            self._update_sweet_spot(detection_id, parameters, component_type, domain)
        
        return detection_id
    
    def _extract_winston_score(self, quality_scores: Dict) -> float:
        """Extract Winston human score from quality results"""
        if 'winston' in quality_scores:
            winston_result = quality_scores['winston']
            if isinstance(winston_result, dict):
                return winston_result.get('human_score', 0.0)
        return 0.0
    
    def _extract_subjective_score(self, quality_scores: Dict) -> float:
        """Extract subjective realism score from quality results"""
        if 'subjective' in quality_scores:
            subjective_result = quality_scores['subjective']
            if isinstance(subjective_result, dict):
                return subjective_result.get('overall_realism', 0.0)
        return 0.0
    
    def _insert_to_database(
        self,
        content: str,
        winston_human_score: float,
        subjective_score: float,
        overall_quality: float,
        passed: bool,
        parameters: Dict[str, Any],
        domain: str,
        item_name: str,
        component_type: str,
        author_id: str,
        extra_context: Dict[str, Any]
    ) -> int:
        """
        Insert generation attempt to detection_results table.
        
        Returns:
            Detection ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Serialize parameters and context
            params_json = json.dumps(parameters)
            context_json = json.dumps(extra_context)
            
            cursor.execute("""
                INSERT INTO detection_results (
                    content,
                    winston_human_score,
                    subjective_realism_score,
                    overall_quality,
                    passed,
                    parameters,
                    domain,
                    item_name,
                    component_type,
                    author_id,
                    extra_context,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content,
                winston_human_score,
                subjective_score,
                overall_quality,
                1 if passed else 0,
                params_json,
                domain,
                item_name,
                component_type,
                author_id,
                context_json,
                datetime.now().isoformat()
            ))
            
            detection_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return detection_id
            
        except sqlite3.OperationalError as e:
            # Table might not exist - create it
            logger.warning(f"Database table missing, creating: {e}")
            self._create_tables()
            # Retry insert
            return self._insert_to_database(
                content, winston_human_score, subjective_score,
                overall_quality, passed, parameters, domain,
                item_name, component_type, author_id, extra_context
            )
        except Exception as e:
            logger.error(f"Failed to insert to learning database: {e}")
            return -1
    
    def _create_tables(self) -> None:
        """Create learning database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # detection_results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detection_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                winston_human_score REAL,
                subjective_realism_score REAL,
                overall_quality REAL,
                passed INTEGER,
                parameters TEXT,
                domain TEXT,
                item_name TEXT,
                component_type TEXT,
                author_id TEXT,
                extra_context TEXT,
                timestamp TEXT
            )
        """)
        
        # sweet_spot_samples table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sweet_spot_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_id INTEGER,
                component_type TEXT,
                domain TEXT,
                temperature REAL,
                frequency_penalty REAL,
                presence_penalty REAL,
                overall_quality REAL,
                timestamp TEXT,
                FOREIGN KEY (detection_id) REFERENCES detection_results(id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Created learning database tables")
    
    def _update_sweet_spot(
        self, 
        detection_id: int, 
        parameters: Dict[str, Any], 
        component_type: str,
        domain: str
    ) -> None:
        """
        Update sweet spot samples with high-quality generation.
        
        Args:
            detection_id: ID of detection result
            parameters: Generation parameters used
            component_type: Type of content
            domain: Domain of content
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get overall_quality from detection_results
            cursor.execute(
                "SELECT overall_quality FROM detection_results WHERE id = ?",
                (detection_id,)
            )
            row = cursor.fetchone()
            overall_quality = row[0] if row else 0.0
            
            # Insert into sweet_spot_samples
            cursor.execute("""
                INSERT INTO sweet_spot_samples (
                    detection_id,
                    component_type,
                    domain,
                    temperature,
                    frequency_penalty,
                    presence_penalty,
                    overall_quality,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                detection_id,
                component_type,
                domain,
                parameters.get('temperature', 0.7),
                parameters.get('frequency_penalty', 0.0),
                parameters.get('presence_penalty', 0.0),
                overall_quality,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(
                f"Updated sweet spot: component={component_type}, "
                f"domain={domain}, quality={overall_quality:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Failed to update sweet spot: {e}")
    
    def get_optimized_parameters(
        self, 
        component_type: str, 
        domain: str = 'materials',
        min_quality: float = 0.8,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        🔄 REUSABLE: Get optimal parameters for ANY domain + component
        
        Query sweet spot samples and calculate optimal parameters.
        
        Args:
            component_type: Type of content (description, micro, etc.)
            domain: Domain (materials, settings, contaminants, compounds)
            min_quality: Minimum quality threshold for samples
            limit: Maximum number of samples to analyze
        
        Returns:
            Dict with optimized parameters:
            {
                'temperature': float,
                'frequency_penalty': float,
                'presence_penalty': float,
                'sample_count': int
            }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get top performing samples
            cursor.execute("""
                SELECT temperature, frequency_penalty, presence_penalty, overall_quality
                FROM sweet_spot_samples
                WHERE component_type = ? 
                  AND domain = ?
                  AND overall_quality >= ?
                ORDER BY overall_quality DESC
                LIMIT ?
            """, (component_type, domain, min_quality, limit))
            
            samples = cursor.fetchall()
            conn.close()
            
            if not samples:
                logger.warning(
                    f"No sweet spot samples found for {domain}/{component_type}"
                )
                return {
                    'temperature': 0.7,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0,
                    'sample_count': 0
                }
            
            # Calculate average of top performers
            avg_temp = sum(s[0] for s in samples) / len(samples)
            avg_freq = sum(s[1] for s in samples) / len(samples)
            avg_pres = sum(s[2] for s in samples) / len(samples)
            
            logger.info(
                f"Optimized parameters from {len(samples)} samples: "
                f"temp={avg_temp:.3f}, freq_pen={avg_freq:.3f}"
            )
            
            return {
                'temperature': round(avg_temp, 3),
                'frequency_penalty': round(avg_freq, 3),
                'presence_penalty': round(avg_pres, 3),
                'sample_count': len(samples)
            }
            
        except Exception as e:
            logger.error(f"Failed to get optimized parameters: {e}")
            return {
                'temperature': 0.7,
                'frequency_penalty': 0.0,
                'presence_penalty': 0.0,
                'sample_count': 0
            }
    
    def get_quality_statistics(
        self,
        domain: Optional[str] = None,
        component_type: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get quality statistics for learning analysis.
        
        Args:
            domain: Filter by domain (None = all domains)
            component_type: Filter by component type (None = all types)
            days: Number of days to analyze
        
        Returns:
            Dict with statistics:
            {
                'total_attempts': int,
                'passed_attempts': int,
                'avg_winston_score': float,
                'avg_subjective_score': float,
                'avg_overall_quality': float
            }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query with optional filters
            query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(passed) as passed,
                    AVG(winston_human_score) as avg_winston,
                    AVG(subjective_realism_score) as avg_subjective,
                    AVG(overall_quality) as avg_quality
                FROM detection_results
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
            """
            params = [days]
            
            if domain:
                query += " AND domain = ?"
                params.append(domain)
            
            if component_type:
                query += " AND component_type = ?"
                params.append(component_type)
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            conn.close()
            
            return {
                'total_attempts': row[0] or 0,
                'passed_attempts': row[1] or 0,
                'avg_winston_score': round(row[2] or 0.0, 3),
                'avg_subjective_score': round(row[3] or 0.0, 3),
                'avg_overall_quality': round(row[4] or 0.0, 3)
            }
            
        except Exception as e:
            logger.error(f"Failed to get quality statistics: {e}")
            return {
                'total_attempts': 0,
                'passed_attempts': 0,
                'avg_winston_score': 0.0,
                'avg_subjective_score': 0.0,
                'avg_overall_quality': 0.0
            }
