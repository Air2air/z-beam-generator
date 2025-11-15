"""
Winston AI Feedback Database

SQLite-based database for logging Winston API results and human corrections.
Enables learning from past failures and tracking improvement over time.

Compliant with fail-fast architecture - no fallbacks, clear error signaling.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Database configuration error."""
    pass


class WinstonFeedbackDatabase:
    """
    Manage Winston feedback and corrections database using SQLite.
    
    Database runs on SQLite - a lightweight, serverless SQL database that:
    - No installation needed (built into Python)
    - Single file database
    - Zero configuration
    - Cross-platform
    
    Fail-fast design:
    - Requires explicit database path
    - No fallbacks or defaults
    - Throws specific exceptions on failures
    """
    
    def __init__(self, db_path: str):
        """
        Initialize database connection.
        
        Args:
            db_path: Absolute or relative path to SQLite database file
            
        Raises:
            ConfigurationError: If db_path not provided or invalid
        """
        if not db_path:
            raise ConfigurationError("Winston feedback database path required")
        
        self.db_path = Path(db_path)
        
        # Create parent directories if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_database()
        
        logger.info(f"✅ [WINSTON DB] Initialized at {db_path}")
    
    def _init_database(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create all tables
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS detection_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    material TEXT NOT NULL,
                    component_type TEXT NOT NULL,
                    generated_text TEXT NOT NULL,
                    human_score REAL NOT NULL,
                    ai_score REAL NOT NULL,
                    readability_score REAL,
                    credits_used INTEGER,
                    attempt_number INTEGER,
                    temperature REAL,
                    success BOOLEAN NOT NULL,
                    failure_type TEXT
                );
                
                CREATE TABLE IF NOT EXISTS sentence_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detection_result_id INTEGER NOT NULL,
                    sentence_number INTEGER NOT NULL,
                    sentence_text TEXT NOT NULL,
                    human_score REAL NOT NULL,
                    FOREIGN KEY (detection_result_id) REFERENCES detection_results(id)
                );
                
                CREATE TABLE IF NOT EXISTS ai_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detection_result_id INTEGER NOT NULL,
                    pattern TEXT NOT NULL,
                    context TEXT NOT NULL,
                    FOREIGN KEY (detection_result_id) REFERENCES detection_results(id)
                );
                
                CREATE TABLE IF NOT EXISTS corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detection_result_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    original_text TEXT NOT NULL,
                    corrected_text TEXT NOT NULL,
                    correction_type TEXT NOT NULL,
                    notes TEXT,
                    corrected_by TEXT,
                    approved BOOLEAN DEFAULT 0,
                    FOREIGN KEY (detection_result_id) REFERENCES detection_results(id)
                );
                
                CREATE TABLE IF NOT EXISTS learning_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    success_rate REAL,
                    last_seen TEXT NOT NULL,
                    material_specific BOOLEAN DEFAULT 0,
                    materials TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_material ON detection_results(material);
                CREATE INDEX IF NOT EXISTS idx_component ON detection_results(component_type);
                CREATE INDEX IF NOT EXISTS idx_success ON detection_results(success);
                CREATE INDEX IF NOT EXISTS idx_timestamp ON detection_results(timestamp);
            """)
            
            conn.commit()
    
    def log_detection(
        self,
        material: str,
        component_type: str,
        generated_text: str,
        winston_result: Dict[str, Any],
        temperature: float,
        attempt: int,
        success: bool,
        failure_analysis: Optional[Dict] = None
    ) -> int:
        """
        Log a Winston detection result.
        
        Args:
            material: Material name (e.g., "Steel")
            component_type: Component type (e.g., "caption", "subtitle")
            generated_text: The text that was analyzed
            winston_result: Full Winston API response with sentence data
            temperature: Generation temperature used
            attempt: Attempt number
            success: Whether it passed AI detection threshold
            failure_analysis: Optional WinstonFeedbackAnalyzer results
            
        Returns:
            detection_result_id for linking corrections
        """
        timestamp = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert main detection result
            cursor.execute("""
                INSERT INTO detection_results 
                (timestamp, material, component_type, generated_text, 
                 human_score, ai_score, readability_score, credits_used,
                 attempt_number, temperature, success, failure_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                material,
                component_type,
                generated_text,
                winston_result.get('human_score', 0),
                winston_result.get('ai_score', 1.0),
                winston_result.get('readability_score'),
                winston_result.get('credits_used'),
                attempt,
                temperature,
                success,
                failure_analysis.get('failure_type') if failure_analysis else None
            ))
            
            result_id = cursor.lastrowid
            
            # Insert sentence-level data
            sentences = winston_result.get('sentences', [])
            for idx, sentence in enumerate(sentences, 1):
                cursor.execute("""
                    INSERT INTO sentence_analysis
                    (detection_result_id, sentence_number, sentence_text, human_score)
                    VALUES (?, ?, ?, ?)
                """, (
                    result_id,
                    idx,
                    sentence.get('text', ''),
                    sentence.get('score', 0)
                ))
            
            # Insert detected AI patterns
            if failure_analysis:
                patterns = failure_analysis.get('patterns', [])
                for pattern in patterns:
                    cursor.execute("""
                        INSERT INTO ai_patterns
                        (detection_result_id, pattern, context)
                        VALUES (?, ?, ?)
                    """, (
                        result_id,
                        pattern[:50],  # Pattern description
                        pattern        # Full context
                    ))
            
            conn.commit()
        
        logger.info(f"📝 [WINSTON DB] Logged detection result #{result_id}")
        return result_id
    
    def add_correction(
        self,
        detection_result_id: int,
        original_text: str,
        corrected_text: str,
        correction_type: str,
        notes: str = None,
        corrected_by: str = "user"
    ) -> int:
        """
        Add a human correction for a detection result.
        
        This is the CORE learning function - captures what humans changed.
        
        Args:
            detection_result_id: ID from log_detection()
            original_text: Original AI-generated text
            corrected_text: Human-corrected version
            correction_type: Type of correction ('word_choice', 'structure', 'phrasing', 'technical_accuracy')
            notes: Optional explanation of why correction was made
            corrected_by: Who made the correction
            
        Returns:
            correction_id
        """
        timestamp = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO corrections
                (detection_result_id, timestamp, original_text, corrected_text,
                 correction_type, notes, corrected_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                detection_result_id,
                timestamp,
                original_text,
                corrected_text,
                correction_type,
                notes,
                corrected_by
            ))
            
            correction_id = cursor.lastrowid
            conn.commit()
        
        logger.info(f"✏️  [WINSTON DB] Added correction #{correction_id}")
        return correction_id
    
    def get_problematic_patterns(
        self,
        material: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get most frequent AI patterns that cause failures.
        
        Useful for prompt engineering and avoidance lists.
        
        Args:
            material: Optional filter by material name
            limit: Maximum number of patterns to return
            
        Returns:
            List of pattern dicts with frequency and scores
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT p.pattern, COUNT(*) as frequency, 
                       AVG(d.human_score) as avg_score,
                       GROUP_CONCAT(DISTINCT d.material) as materials
                FROM ai_patterns p
                JOIN detection_results d ON p.detection_result_id = d.id
                WHERE d.success = 0
            """
            
            if material:
                query += " AND d.material = ?"
                params = (material, limit)
            else:
                params = (limit,)
            
            query += """
                GROUP BY p.pattern
                ORDER BY frequency DESC
                LIMIT ?
            """
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'pattern': row[0],
                    'frequency': row[1],
                    'avg_score': row[2],
                    'materials': row[3].split(',') if row[3] else []
                })
            
            return results
    
    def get_successful_corrections(
        self,
        material: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get corrections that worked (human-approved).
        
        These can be used as examples in prompts.
        
        Args:
            material: Optional filter by material name
            limit: Maximum number of corrections to return
            
        Returns:
            List of correction dicts with original/corrected text
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT c.original_text, c.corrected_text, 
                       c.correction_type, c.notes,
                       d.material, d.component_type
                FROM corrections c
                JOIN detection_results d ON c.detection_result_id = d.id
                WHERE c.approved = 1
            """
            
            if material:
                query += " AND d.material = ?"
                params = (material, limit)
            else:
                params = (limit,)
            
            query += " ORDER BY c.timestamp DESC LIMIT ?"
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'original': row[0],
                    'corrected': row[1],
                    'type': row[2],
                    'notes': row[3],
                    'material': row[4],
                    'component': row[5]
                })
            
            return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total detections
            cursor.execute("SELECT COUNT(*) FROM detection_results")
            total_detections = cursor.fetchone()[0]
            
            # Success rate
            cursor.execute("SELECT COUNT(*) FROM detection_results WHERE success = 1")
            successful = cursor.fetchone()[0]
            
            # Total corrections
            cursor.execute("SELECT COUNT(*) FROM corrections")
            total_corrections = cursor.fetchone()[0]
            
            # Approved corrections
            cursor.execute("SELECT COUNT(*) FROM corrections WHERE approved = 1")
            approved_corrections = cursor.fetchone()[0]
            
            # Average human score
            cursor.execute("SELECT AVG(human_score) FROM detection_results")
            avg_human_score = cursor.fetchone()[0] or 0
            
            return {
                'total_detections': total_detections,
                'successful_detections': successful,
                'success_rate': (successful / total_detections * 100) if total_detections > 0 else 0,
                'total_corrections': total_corrections,
                'approved_corrections': approved_corrections,
                'avg_human_score': avg_human_score
            }
