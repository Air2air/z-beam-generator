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
                    failure_type TEXT,
                    composite_quality_score REAL,
                    subjective_evaluation_id INTEGER,
                    FOREIGN KEY (subjective_evaluation_id) REFERENCES subjective_evaluations(id)
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
                
                CREATE TABLE IF NOT EXISTS subjective_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    component_type TEXT NOT NULL,
                    domain TEXT DEFAULT 'materials',
                    generated_text TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    clarity_score REAL NOT NULL,
                    professionalism_score REAL NOT NULL,
                    technical_accuracy_score REAL NOT NULL,
                    human_likeness_score REAL NOT NULL,
                    engagement_score REAL NOT NULL,
                    jargon_free_score REAL NOT NULL,
                    passes_quality_gate BOOLEAN NOT NULL,
                    quality_threshold REAL NOT NULL,
                    evaluation_time_ms REAL,
                    strengths TEXT,
                    weaknesses TEXT,
                    recommendations TEXT,
                    narrative_assessment TEXT,
                    realism_score REAL,
                    voice_authenticity REAL,
                    tonal_consistency REAL,
                    ai_tendencies TEXT,
                    author_id INTEGER,
                    attempt_number INTEGER,
                    has_claude_api BOOLEAN DEFAULT 0,
                    generation_parameters_id INTEGER,
                    FOREIGN KEY (generation_parameters_id) REFERENCES generation_parameters(id)
                );
                
                CREATE TABLE IF NOT EXISTS generation_parameters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detection_result_id INTEGER UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    material TEXT NOT NULL,
                    component_type TEXT NOT NULL,
                    attempt_number INTEGER NOT NULL,
                    
                    -- API Parameters
                    temperature REAL NOT NULL,
                    max_tokens INTEGER NOT NULL,
                    frequency_penalty REAL NOT NULL,
                    presence_penalty REAL NOT NULL,
                    
                    -- Voice Parameters (0.0-1.0 range)
                    trait_frequency REAL NOT NULL,
                    opinion_rate REAL NOT NULL,
                    reader_address_rate REAL NOT NULL,
                    colloquialism_frequency REAL NOT NULL,
                    structural_predictability REAL NOT NULL,
                    emotional_tone REAL NOT NULL,
                    imperfection_tolerance REAL,
                    sentence_rhythm_variation REAL,
                    
                    -- Enrichment Parameters (1-3 scale)
                    technical_intensity INTEGER NOT NULL,
                    context_detail_level INTEGER NOT NULL,
                    fact_formatting_style TEXT NOT NULL,
                    engagement_level INTEGER NOT NULL,
                    
                    -- Validation Parameters
                    detection_threshold REAL NOT NULL,
                    readability_min REAL NOT NULL,
                    readability_max REAL NOT NULL,
                    grammar_strictness REAL NOT NULL,
                    confidence_high REAL NOT NULL,
                    confidence_medium REAL NOT NULL,
                    
                    -- Retry Behavior
                    max_attempts INTEGER NOT NULL,
                    retry_temperature_increase REAL NOT NULL,
                    
                    -- Full JSON snapshot
                    full_params_json TEXT NOT NULL,
                    param_hash TEXT NOT NULL,
                    
                    FOREIGN KEY (detection_result_id) REFERENCES detection_results(id) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS sweet_spot_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    material TEXT NOT NULL,
                    component_type TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    
                    -- Sweet spot parameter ranges (NULL if insufficient data)
                    temperature_min REAL,
                    temperature_max REAL,
                    temperature_median REAL,
                    frequency_penalty_min REAL,
                    frequency_penalty_max REAL,
                    frequency_penalty_median REAL,
                    presence_penalty_min REAL,
                    presence_penalty_max REAL,
                    presence_penalty_median REAL,
                    trait_frequency_min REAL,
                    trait_frequency_max REAL,
                    trait_frequency_median REAL,
                    technical_intensity_min INTEGER,
                    technical_intensity_max INTEGER,
                    technical_intensity_median INTEGER,
                    imperfection_tolerance_min REAL,
                    imperfection_tolerance_max REAL,
                    imperfection_tolerance_median REAL,
                    sentence_rhythm_variation_min REAL,
                    sentence_rhythm_variation_max REAL,
                    sentence_rhythm_variation_median REAL,
                    
                    -- Statistics
                    sample_count INTEGER NOT NULL,
                    max_human_score REAL NOT NULL,
                    avg_human_score REAL NOT NULL,
                    confidence_level TEXT NOT NULL,  -- 'high', 'medium', 'low'
                    
                    -- Top correlations (JSON array)
                    parameter_correlations TEXT,
                    
                    -- Recommendations (JSON array)
                    recommendations TEXT,
                    
                    UNIQUE(material, component_type)
                );
                
                CREATE TABLE IF NOT EXISTS realism_learning (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    material TEXT NOT NULL,
                    component_type TEXT NOT NULL,
                    domain TEXT DEFAULT 'materials',
                    
                    -- Original state
                    original_realism_score REAL,
                    original_voice_authenticity REAL,
                    original_tonal_consistency REAL,
                    detected_ai_tendencies TEXT,  -- JSON array
                    original_parameters TEXT,  -- JSON object
                    
                    -- Adjustment made
                    parameter_adjustments TEXT,  -- JSON array of RealismAdjustment objects
                    adjustment_rationale TEXT,
                    
                    -- Outcome (after retry)
                    new_realism_score REAL,
                    new_voice_authenticity REAL,
                    new_tonal_consistency REAL,
                    improvement REAL,  -- new_realism_score - original_realism_score
                    success BOOLEAN,  -- improvement > 0
                    
                    -- Combined scores
                    original_winston_score REAL,
                    new_winston_score REAL,
                    original_combined_score REAL,
                    new_combined_score REAL,
                    
                    -- Metadata
                    subjective_evaluation_id INTEGER,
                    attempt_number INTEGER,
                    FOREIGN KEY (subjective_evaluation_id) REFERENCES subjective_evaluations(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_realism_material ON realism_learning(material);
                CREATE INDEX IF NOT EXISTS idx_realism_component ON realism_learning(component_type);
                CREATE INDEX IF NOT EXISTS idx_realism_success ON realism_learning(success);
                CREATE INDEX IF NOT EXISTS idx_realism_timestamp ON realism_learning(timestamp);
                
                CREATE INDEX IF NOT EXISTS idx_material ON detection_results(material);
                CREATE INDEX IF NOT EXISTS idx_component ON detection_results(component_type);
                CREATE INDEX IF NOT EXISTS idx_success ON detection_results(success);
                CREATE INDEX IF NOT EXISTS idx_timestamp ON detection_results(timestamp);
                CREATE INDEX IF NOT EXISTS idx_detection_composite ON detection_results(composite_quality_score);
                CREATE INDEX IF NOT EXISTS idx_detection_subjective ON detection_results(subjective_evaluation_id);
                CREATE INDEX IF NOT EXISTS idx_claude_topic ON subjective_evaluations(topic);
                CREATE INDEX IF NOT EXISTS idx_claude_component ON subjective_evaluations(component_type);
                CREATE INDEX IF NOT EXISTS idx_claude_quality ON subjective_evaluations(passes_quality_gate);
                CREATE INDEX IF NOT EXISTS idx_claude_timestamp ON subjective_evaluations(timestamp);
                CREATE INDEX IF NOT EXISTS idx_subjective_eval_params ON subjective_evaluations(generation_parameters_id);
                CREATE INDEX IF NOT EXISTS idx_params_material ON generation_parameters(material);
                CREATE INDEX IF NOT EXISTS idx_params_component ON generation_parameters(component_type);
                CREATE INDEX IF NOT EXISTS idx_params_temperature ON generation_parameters(temperature);
                CREATE INDEX IF NOT EXISTS idx_params_penalties ON generation_parameters(frequency_penalty, presence_penalty);
                CREATE INDEX IF NOT EXISTS idx_params_hash ON generation_parameters(param_hash);
                CREATE INDEX IF NOT EXISTS idx_params_timestamp ON generation_parameters(timestamp);
                CREATE INDEX IF NOT EXISTS idx_sweet_spot_lookup ON sweet_spot_recommendations(material, component_type);
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
        failure_analysis: Optional[Dict] = None,
        composite_quality_score: Optional[float] = None
    ) -> int:
        """
        Log a Winston detection result.
        
        Args:
            material: Material name (e.g., "Steel")
            component_type: Component type (defined in prompts/{type}.txt)
            generated_text: The text that was analyzed
            winston_result: Full Winston API response with sentence data
            temperature: Generation temperature used
            attempt: Attempt number
            success: Whether it passed AI detection threshold
            failure_analysis: Optional WinstonFeedbackAnalyzer results
            composite_quality_score: Composite score (Winston + Subjective + Readability)
            
        Returns:
            detection_result_id for linking corrections
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Validate scores are 0-1.0 normalized (fail-fast on invalid data)
        human_score = winston_result.get('human_score', 0)
        ai_score = winston_result.get('ai_score', 1.0)
        readability_score = winston_result.get('readability_score')
        
        if not 0.0 <= human_score <= 1.0:
            raise ValueError(
                f"human_score must be 0-1.0 normalized, got {human_score}. "
                f"Winston API should return normalized scores."
            )
        if not 0.0 <= ai_score <= 1.0:
            raise ValueError(
                f"ai_score must be 0-1.0 normalized, got {ai_score}"
            )
        if readability_score is not None and not 0.0 <= readability_score <= 1.0:
            raise ValueError(
                f"readability_score must be 0-1.0 normalized, got {readability_score}"
            )
        if composite_quality_score is not None and not 0.0 <= composite_quality_score <= 1.0:
            raise ValueError(
                f"composite_quality_score must be 0-1.0 normalized, got {composite_quality_score}"
            )
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert main detection result (ALL scores normalized to 0-1.0)
            cursor.execute("""
                INSERT INTO detection_results 
                (timestamp, material, component_type, generated_text, 
                 human_score, ai_score, readability_score, credits_used,
                 attempt_number, temperature, success, failure_type, composite_quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                material,
                component_type,
                generated_text,
                human_score,
                ai_score,
                readability_score,
                winston_result.get('credits_used'),
                attempt,
                temperature,
                success,
                failure_analysis.get('failure_type') if failure_analysis else None,
                composite_quality_score
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
    
    def log_subjective_evaluation(
        self,
        topic: str,
        component_type: str,
        generated_text: str,
        evaluation_result,
        domain: str = "materials",
        author_id: Optional[int] = None,
        attempt_number: Optional[int] = None
    ) -> int:
        """
        Log subjective content evaluation to learning database.
        
        Args:
            topic: Subject matter (material name, historical event, etc.)
            component_type: Content type (from prompts/)
            generated_text: The generated text that was evaluated
            evaluation_result: SubjectiveEvaluationResult object
            domain: Content domain (materials, history, recipes, etc.)
            author_id: Optional author ID (1-4)
            attempt_number: Optional attempt number
            
        Returns:
            evaluation_id for reference
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Extract dimension scores
        dimension_scores = {
            score.dimension.value: score.score 
            for score in evaluation_result.dimension_scores
        }
        
        # Convert lists to JSON strings
        strengths_json = json.dumps(evaluation_result.strengths)
        weaknesses_json = json.dumps(evaluation_result.weaknesses)
        recommendations_json = json.dumps(evaluation_result.recommendations)
        
        # DEBUG: Log narrative before database insert
        if evaluation_result.narrative_assessment:
            logger.info(f"🔍 [DEBUG] DATABASE: About to insert narrative ({len(evaluation_result.narrative_assessment)} chars): {evaluation_result.narrative_assessment[:100]}...")
        else:
            logger.warning(f"⚠️ [DEBUG] DATABASE: evaluation_result.narrative_assessment is None/empty")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO subjective_evaluations
                (timestamp, topic, component_type, domain, generated_text,
                 overall_score, clarity_score, professionalism_score,
                 technical_accuracy_score, human_likeness_score,
                 engagement_score, jargon_free_score,
                 passes_quality_gate, quality_threshold, evaluation_time_ms,
                 strengths, weaknesses, recommendations,
                 author_id, attempt_number, has_claude_api, narrative_assessment,
                 realism_score, voice_authenticity, tonal_consistency, ai_tendencies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                topic,
                component_type,
                domain,
                generated_text,
                evaluation_result.overall_score,
                dimension_scores.get('clarity', 0.0),
                dimension_scores.get('professionalism', 0.0),
                dimension_scores.get('technical_accuracy', 0.0),
                dimension_scores.get('human_likeness', 0.0),
                dimension_scores.get('engagement', 0.0),
                dimension_scores.get('jargon_free', 0.0),
                evaluation_result.passes_quality_gate,
                7.0,  # Default threshold (can be parameterized)
                evaluation_result.evaluation_time_ms,
                strengths_json,
                weaknesses_json,
                recommendations_json,
                author_id,
                attempt_number,
                evaluation_result.raw_response is not None,  # Has Claude API if raw response exists
                evaluation_result.narrative_assessment,  # Paragraph-form evaluation
                evaluation_result.realism_score,
                evaluation_result.voice_authenticity,
                evaluation_result.tonal_consistency,
                json.dumps(evaluation_result.ai_tendencies) if evaluation_result.ai_tendencies else None
            ))
            
            evaluation_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"✅ [CLAUDE EVAL] Logged evaluation #{evaluation_id} for {topic}/{component_type}")
            
            return evaluation_id
    
    def log_realism_learning(
        self,
        material: str,
        component_type: str,
        original_realism_score: Optional[float],
        original_voice_authenticity: Optional[float],
        original_tonal_consistency: Optional[float],
        detected_ai_tendencies: Optional[List[str]],
        original_parameters: Dict,
        parameter_adjustments: List,
        adjustment_rationale: str,
        new_realism_score: Optional[float] = None,
        new_voice_authenticity: Optional[float] = None,
        new_tonal_consistency: Optional[float] = None,
        original_winston_score: Optional[float] = None,
        new_winston_score: Optional[float] = None,
        subjective_evaluation_id: Optional[int] = None,
        attempt_number: int = 1,
        domain: str = 'materials'
    ) -> int:
        """
        Log realism learning data for parameter optimization analysis.
        
        Args:
            material: Material name
            component_type: Content type (caption, subtitle, etc.)
            original_realism_score: Initial realism score (0-10)
            original_voice_authenticity: Initial voice authenticity (0-10)
            original_tonal_consistency: Initial tonal consistency (0-10)
            detected_ai_tendencies: List of AI tendency identifiers
            original_parameters: Original generation parameters dict
            parameter_adjustments: List of RealismAdjustment objects (will be serialized)
            adjustment_rationale: Human-readable explanation of adjustments
            new_realism_score: Realism score after adjustment (None if not yet retried)
            new_voice_authenticity: Voice authenticity after adjustment
            new_tonal_consistency: Tonal consistency after adjustment
            original_winston_score: Winston score before adjustment
            new_winston_score: Winston score after adjustment
            subjective_evaluation_id: Reference to subjective_evaluations table
            attempt_number: Retry attempt number
            domain: Content domain
            
        Returns:
            ID of logged realism learning entry
        """
        import json
        from datetime import datetime
        
        timestamp = datetime.now().isoformat()
        
        # Calculate improvement and success (if new scores available)
        improvement = None
        success = None
        if new_realism_score is not None and original_realism_score is not None:
            improvement = new_realism_score - original_realism_score
            success = improvement > 0
        
        # Calculate combined scores (Winston 40% + Realism 60%)
        original_combined = None
        new_combined = None
        if original_winston_score is not None and original_realism_score is not None:
            original_combined = (original_winston_score * 0.4) + (original_realism_score * 10 * 0.6)
        if new_winston_score is not None and new_realism_score is not None:
            new_combined = (new_winston_score * 0.4) + (new_realism_score * 10 * 0.6)
        
        # Serialize complex objects
        tendencies_json = json.dumps(detected_ai_tendencies) if detected_ai_tendencies else None
        params_json = json.dumps(original_parameters)
        
        # Convert RealismAdjustment objects to dicts for JSON serialization
        adjustments_dicts = []
        for adj in parameter_adjustments:
            if hasattr(adj, '__dict__'):
                adjustments_dicts.append(adj.__dict__)
            else:
                adjustments_dicts.append(adj)
        adjustments_json = json.dumps(adjustments_dicts)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO realism_learning
                (timestamp, material, component_type, domain,
                 original_realism_score, original_voice_authenticity, original_tonal_consistency,
                 detected_ai_tendencies, original_parameters,
                 parameter_adjustments, adjustment_rationale,
                 new_realism_score, new_voice_authenticity, new_tonal_consistency,
                 improvement, success,
                 original_winston_score, new_winston_score,
                 original_combined_score, new_combined_score,
                 subjective_evaluation_id, attempt_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, material, component_type, domain,
                original_realism_score, original_voice_authenticity, original_tonal_consistency,
                tendencies_json, params_json,
                adjustments_json, adjustment_rationale,
                new_realism_score, new_voice_authenticity, new_tonal_consistency,
                improvement, success,
                original_winston_score, new_winston_score,
                original_combined, new_combined,
                subjective_evaluation_id, attempt_number
            ))
            
            learning_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"✅ [REALISM LEARNING] Logged learning #{learning_id} for {material}/{component_type}")
            if success is not None:
                status = "SUCCESS" if success else "FAILED"
                logger.info(f"   Improvement: {improvement:+.2f} ({status})")
            
            return learning_id
    
    def get_latest_subjective_evaluation(
        self,
        topic: str,
        component_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent subjective evaluation for a topic/component.
        
        Args:
            topic: Subject matter (material name, etc.)
            component_type: Content type (caption, subtitle, etc.)
            
        Returns:
            Dict with evaluation data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM subjective_evaluations
                WHERE topic = ? AND component_type = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (topic, component_type))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Parse JSON fields
            import json
            try:
                strengths = json.loads(row['strengths']) if row['strengths'] else []
                weaknesses = json.loads(row['weaknesses']) if row['weaknesses'] else []
                recommendations = json.loads(row['recommendations']) if row['recommendations'] else []
            except Exception:
                strengths = []
                weaknesses = []
                recommendations = []
            
            return {
                'evaluation_id': row['id'],
                'timestamp': row['timestamp'],
                'overall_score': row['overall_score'],
                'clarity_score': row['clarity_score'],
                'professionalism_score': row['professionalism_score'],
                'technical_accuracy_score': row['technical_accuracy_score'],
                'human_likeness_score': row['human_likeness_score'],
                'engagement_score': row['engagement_score'],
                'jargon_free_score': row['jargon_free_score'],
                'passes_quality_gate': bool(row['passes_quality_gate']),
                'strengths': strengths,
                'weaknesses': weaknesses,
                'recommendations': recommendations,
                'evaluation_time_ms': row['evaluation_time_ms'],
                'narrative_assessment': row['narrative_assessment'] if 'narrative_assessment' in row.keys() else None
            }
    
    def should_update_sweet_spot(self, material: str = '*', component_type: str = '*', min_samples: int = 5) -> bool:
        """Check if global sweet spot should be updated based on sample count.
        
        GENERIC LEARNING: Always checks global scope (material='*', component_type='*').
        
        Args:
            material: Ignored (kept for backward compatibility)
            component_type: Ignored (kept for backward compatibility)
            min_samples: Minimum samples needed before calculating sweet spot
            
        Returns:
            True if enough samples exist and sweet spot should be updated
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if global sweet spot already exists
            cursor.execute("""
                SELECT last_updated, sample_count FROM sweet_spot_recommendations
                WHERE material = '*' AND component_type = '*'
            """)
            
            existing = cursor.fetchone()
            
            # Check current total sample count across ALL materials/components
            cursor.execute("""
                SELECT COUNT(*) FROM detection_results
                WHERE success = 1
            """)
            
            current_samples = cursor.fetchone()[0]
            
            # Update if: no existing sweet spot, or new samples since last update
            if not existing:
                return current_samples >= min_samples
            else:
                last_sample_count = existing[1] or 0
                return current_samples > last_sample_count and current_samples >= min_samples
    
    def get_subjective_evaluation_stats(
        self,
        topic: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Subjective evaluation statistics.
        
        Args:
            topic: Optional filter by topic
            component_type: Optional filter by component type
            
        Returns:
            Statistics dict with averages and trends
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build query with filters
            base_query = "SELECT COUNT(*), AVG(overall_score), AVG(passes_quality_gate) FROM subjective_evaluations"
            filters = []
            params = []
            
            if topic:
                filters.append("topic = ?")
                params.append(topic)
            
            if component_type:
                filters.append("component_type = ?")
                params.append(component_type)
            
            if filters:
                base_query += " WHERE " + " AND ".join(filters)
            
            cursor.execute(base_query, params)
            row = cursor.fetchone()
            
            total_evals = row[0] or 0
            avg_score = row[1] or 0.0
            pass_rate = (row[2] or 0.0) * 100
            
            # Get dimension averages
            dim_query = """
                SELECT 
                    AVG(clarity_score),
                    AVG(professionalism_score),
                    AVG(technical_accuracy_score),
                    AVG(human_likeness_score),
                    AVG(engagement_score),
                    AVG(jargon_free_score)
                FROM subjective_evaluations
            """
            
            if filters:
                dim_query += " WHERE " + " AND ".join(filters)
            
            cursor.execute(dim_query, params)
            dim_row = cursor.fetchone()
            
            return {
                'total_evaluations': total_evals,
                'avg_overall_score': avg_score,
                'quality_gate_pass_rate': pass_rate,
                'dimension_averages': {
                    'clarity': dim_row[0] or 0.0,
                    'professionalism': dim_row[1] or 0.0,
                    'technical_accuracy': dim_row[2] or 0.0,
                    'human_likeness': dim_row[3] or 0.0,
                    'engagement': dim_row[4] or 0.0,
                    'jargon_free': dim_row[5] or 0.0
                }
            }
    
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
            
            # Subjective evaluation stats
            cursor.execute("SELECT COUNT(*) FROM subjective_evaluations")
            total_claude_evals = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(overall_score) FROM subjective_evaluations")
            avg_claude_score = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM subjective_evaluations WHERE passes_quality_gate = 1")
            claude_passes = cursor.fetchone()[0]
            
            # Generation parameters stats
            cursor.execute("SELECT COUNT(*) FROM generation_parameters")
            total_params = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(temperature), AVG(frequency_penalty), AVG(presence_penalty) FROM generation_parameters")
            param_avgs = cursor.fetchone()
            avg_temperature = param_avgs[0] or 0
            avg_freq_penalty = param_avgs[1] or 0
            avg_pres_penalty = param_avgs[2] or 0
            
            return {
                'total_detections': total_detections,
                'successful_detections': successful,
                'success_rate': (successful / total_detections * 100) if total_detections > 0 else 0,
                'total_corrections': total_corrections,
                'approved_corrections': approved_corrections,
                'avg_human_score': avg_human_score,
                'total_subjective_evaluations': total_claude_evals,
                'avg_claude_score': avg_claude_score,
                'claude_pass_rate': (claude_passes / total_claude_evals * 100) if total_claude_evals > 0 else 0,
                'total_generation_parameters': total_params,
                'avg_temperature': avg_temperature,
                'avg_frequency_penalty': avg_freq_penalty,
                'avg_presence_penalty': avg_pres_penalty
            }
    
    def log_generation_parameters(
        self,
        detection_result_id: int,
        params: Dict[str, Any]
    ) -> int:
        """
        Log complete parameter set used for generation.
        
        Links parameters to detection result for analysis and learning.
        Enables queries like "what temperature works best?" and
        "does increasing penalties improve human scores?"
        
        Args:
            detection_result_id: ID from detection_results table
            params: Parameters dict with structure:
                {
                    'material_name': str,
                    'component_type': str,
                    'attempt': int,
                    'api': {
                        'temperature': float,
                        'max_tokens': int,
                        'frequency_penalty': float,
                        'presence_penalty': float
                    },
                    'voice': {
                        'trait_frequency': float,
                        'opinion_rate': float,
                        'reader_address_rate': float,
                        'colloquialism_frequency': float,
                        'structural_predictability': float,
                        'emotional_tone': float,
                        'imperfection_tolerance': float (optional),
                        'sentence_rhythm_variation': float (optional)
                    },
                    'enrichment': {
                        'technical_intensity': int,
                        'context_detail_level': int,
                        'fact_formatting_style': str,
                        'engagement_level': int
                    },
                    'validation': {
                        'detection_threshold': float,
                        'readability_min': float,
                        'readability_max': float,
                        'grammar_strictness': float,
                        'confidence_high': float,
                        'confidence_medium': float
                    },
                    'retry': {
                        'max_attempts': int,
                        'retry_temperature_increase': float
                    }
                }
            
        Returns:
            Row ID of inserted parameters
            
        Raises:
            KeyError: If required parameter fields are missing
        """
        import hashlib
        
        # Calculate hash for deduplication and tracking
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO generation_parameters (
                    detection_result_id,
                    timestamp,
                    material,
                    component_type,
                    attempt_number,
                    temperature,
                    max_tokens,
                    frequency_penalty,
                    presence_penalty,
                    trait_frequency,
                    opinion_rate,
                    reader_address_rate,
                    colloquialism_frequency,
                    structural_predictability,
                    emotional_tone,
                    imperfection_tolerance,
                    sentence_rhythm_variation,
                    technical_intensity,
                    context_detail_level,
                    fact_formatting_style,
                    engagement_level,
                    detection_threshold,
                    readability_min,
                    readability_max,
                    grammar_strictness,
                    confidence_high,
                    confidence_medium,
                    max_attempts,
                    retry_temperature_increase,
                    full_params_json,
                    param_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                detection_result_id,
                datetime.now().isoformat(),
                params['material_name'],
                params['component_type'],
                params['attempt'],
                params['api']['temperature'],
                params['api']['max_tokens'],
                params['api']['frequency_penalty'],
                params['api']['presence_penalty'],
                params['voice']['trait_frequency'],
                params['voice']['opinion_rate'],
                params['voice']['reader_address_rate'],
                params['voice']['colloquialism_frequency'],
                params['voice']['structural_predictability'],
                params['voice']['emotional_tone'],
                params['voice'].get('imperfection_tolerance'),
                params['voice'].get('sentence_rhythm_variation'),
                params['enrichment']['technical_intensity'],
                params['enrichment']['context_detail_level'],
                params['enrichment']['fact_formatting_style'],
                params['enrichment']['engagement_level'],
                params['validation']['detection_threshold'],
                params['validation']['readability_min'],
                params['validation']['readability_max'],
                params['validation']['grammar_strictness'],
                params['validation']['confidence_high'],
                params['validation']['confidence_medium'],
                params['retry']['max_attempts'],
                params['retry']['retry_temperature_increase'],
                json.dumps(params),
                param_hash
            ))
            conn.commit()
            
            row_id = cursor.lastrowid
            logger.info(f"📊 [WINSTON DB] Logged generation parameters #{row_id} for detection result #{detection_result_id}")
            
            return row_id
    
    def get_best_parameters_for_material(
        self,
        material: str,
        component_type: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get best-performing parameter sets for a material/component.
        
        Useful for learning what parameter combinations work best.
        
        Args:
            material: Material name (e.g., "Aluminum")
            component_type: Component type (e.g., "caption")
            limit: Number of top results to return
            
        Returns:
            List of parameter dicts ordered by human_score DESC
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    p.full_params_json,
                    d.human_score,
                    d.ai_score,
                    d.timestamp
                FROM generation_parameters p
                JOIN detection_results d ON p.detection_result_id = d.id
                WHERE d.material = ?
                  AND d.component_type = ?
                  AND d.success = 1
                ORDER BY d.human_score DESC
                LIMIT ?
            """, (material, component_type, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'params': json.loads(row[0]),
                    'human_score': row[1],
                    'ai_score': row[2],
                    'timestamp': row[3]
                })
            
            return results
    
    def get_parameter_correlation(
        self,
        parameter_path: str,
        component_type: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze correlation between a parameter and success.
        
        Args:
            parameter_path: Parameter to analyze (e.g., "temperature", "frequency_penalty")
            component_type: Optional filter by component type
            days: Number of days to look back
            
        Returns:
            Dict with correlation analysis
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = f"""
                SELECT 
                    p.{parameter_path},
                    AVG(d.human_score) as avg_human_score,
                    AVG(d.ai_score) as avg_ai_score,
                    COUNT(*) as samples,
                    SUM(CASE WHEN d.success = 1 THEN 1 ELSE 0 END) as successes
                FROM generation_parameters p
                JOIN detection_results d ON p.detection_result_id = d.id
                WHERE d.timestamp > datetime('now', '-{days} days')
            """
            
            if component_type:
                query += f" AND d.component_type = '{component_type}'"
            
            query += f"""
                GROUP BY ROUND(p.{parameter_path}, 2)
                HAVING samples >= 2
                ORDER BY avg_human_score DESC
            """
            
            cursor.execute(query)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'value': row[0],
                    'avg_human_score': row[1],
                    'avg_ai_score': row[2],
                    'samples': row[3],
                    'success_rate': (row[4] / row[3] * 100) if row[3] > 0 else 0
                })
            
            return {
                'parameter': parameter_path,
                'component_type': component_type or 'all',
                'days_analyzed': days,
                'data_points': results
            }
    
    def upsert_sweet_spot(
        self,
        material: str,
        component_type: str,
        sweet_spots: Dict[str, Any],
        correlations: List[Dict],
        max_human_score: float,
        avg_human_score: float,
        sample_count: int,
        confidence: str,
        recommendations: List[str]
    ) -> int:
        """
        Insert or update sweet spot recommendations for a material/component.
        
        Args:
            material: Material name
            component_type: Component type
            sweet_spots: Dict of {parameter_name: SweetSpot}
            correlations: List of parameter correlations
            max_human_score: Best human score achieved
            avg_human_score: Average human score
            sample_count: Number of samples analyzed
            confidence: 'high', 'medium', or 'low'
            recommendations: List of recommendation strings
            
        Returns:
            Row ID of the upserted record
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Extract parameter ranges from sweet_spots dict
            def get_param(name: str, field: str) -> Optional[float]:
                spot = sweet_spots.get(name)
                if spot:
                    return getattr(spot, field, None)
                return None
            
            cursor.execute("""
                INSERT INTO sweet_spot_recommendations (
                    material,
                    component_type,
                    last_updated,
                    temperature_min,
                    temperature_max,
                    temperature_median,
                    frequency_penalty_min,
                    frequency_penalty_max,
                    frequency_penalty_median,
                    presence_penalty_min,
                    presence_penalty_max,
                    presence_penalty_median,
                    trait_frequency_min,
                    trait_frequency_max,
                    trait_frequency_median,
                    technical_intensity_min,
                    technical_intensity_max,
                    technical_intensity_median,
                    imperfection_tolerance_min,
                    imperfection_tolerance_max,
                    imperfection_tolerance_median,
                    sentence_rhythm_variation_min,
                    sentence_rhythm_variation_max,
                    sentence_rhythm_variation_median,
                    sample_count,
                    max_human_score,
                    avg_human_score,
                    confidence_level,
                    parameter_correlations,
                    recommendations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(material, component_type) DO UPDATE SET
                    last_updated = excluded.last_updated,
                    temperature_min = excluded.temperature_min,
                    temperature_max = excluded.temperature_max,
                    temperature_median = excluded.temperature_median,
                    frequency_penalty_min = excluded.frequency_penalty_min,
                    frequency_penalty_max = excluded.frequency_penalty_max,
                    frequency_penalty_median = excluded.frequency_penalty_median,
                    presence_penalty_min = excluded.presence_penalty_min,
                    presence_penalty_max = excluded.presence_penalty_max,
                    presence_penalty_median = excluded.presence_penalty_median,
                    trait_frequency_min = excluded.trait_frequency_min,
                    trait_frequency_max = excluded.trait_frequency_max,
                    trait_frequency_median = excluded.trait_frequency_median,
                    technical_intensity_min = excluded.technical_intensity_min,
                    technical_intensity_max = excluded.technical_intensity_max,
                    technical_intensity_median = excluded.technical_intensity_median,
                    imperfection_tolerance_min = excluded.imperfection_tolerance_min,
                    imperfection_tolerance_max = excluded.imperfection_tolerance_max,
                    imperfection_tolerance_median = excluded.imperfection_tolerance_median,
                    sentence_rhythm_variation_min = excluded.sentence_rhythm_variation_min,
                    sentence_rhythm_variation_max = excluded.sentence_rhythm_variation_max,
                    sentence_rhythm_variation_median = excluded.sentence_rhythm_variation_median,
                    sample_count = excluded.sample_count,
                    max_human_score = excluded.max_human_score,
                    avg_human_score = excluded.avg_human_score,
                    confidence_level = excluded.confidence_level,
                    parameter_correlations = excluded.parameter_correlations,
                    recommendations = excluded.recommendations
            """, (
                material,
                component_type,
                datetime.now().isoformat(),
                get_param('temperature', 'optimal_min'),
                get_param('temperature', 'optimal_max'),
                get_param('temperature', 'optimal_median'),
                get_param('frequency_penalty', 'optimal_min'),
                get_param('frequency_penalty', 'optimal_max'),
                get_param('frequency_penalty', 'optimal_median'),
                get_param('presence_penalty', 'optimal_min'),
                get_param('presence_penalty', 'optimal_max'),
                get_param('presence_penalty', 'optimal_median'),
                get_param('trait_frequency', 'optimal_min'),
                get_param('trait_frequency', 'optimal_max'),
                get_param('trait_frequency', 'optimal_median'),
                get_param('technical_intensity', 'optimal_min'),
                get_param('technical_intensity', 'optimal_max'),
                get_param('technical_intensity', 'optimal_median'),
                get_param('imperfection_tolerance', 'optimal_min'),
                get_param('imperfection_tolerance', 'optimal_max'),
                get_param('imperfection_tolerance', 'optimal_median'),
                get_param('sentence_rhythm_variation', 'optimal_min'),
                get_param('sentence_rhythm_variation', 'optimal_max'),
                get_param('sentence_rhythm_variation', 'optimal_median'),
                sample_count,
                max_human_score,
                avg_human_score,
                confidence,
                json.dumps(correlations),
                json.dumps(recommendations)
            ))
            
            return cursor.lastrowid
    
    def get_sweet_spot(
        self,
        material: str,
        component_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve sweet spot recommendations - GENERIC LEARNING (params ignored).
        
        Returns:
            Dict with sweet spot data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM sweet_spot_recommendations
                ORDER BY max_human_score DESC, last_updated DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'material': row['material'],
                'component_type': row['component_type'],
                'last_updated': row['last_updated'],
                'parameters': {
                    'temperature': {
                        'min': row['temperature_min'],
                        'max': row['temperature_max'],
                        'median': row['temperature_median']
                    } if row['temperature_min'] is not None else None,
                    'frequency_penalty': {
                        'min': row['frequency_penalty_min'],
                        'max': row['frequency_penalty_max'],
                        'median': row['frequency_penalty_median']
                    } if row['frequency_penalty_min'] is not None else None,
                    'presence_penalty': {
                        'min': row['presence_penalty_min'],
                        'max': row['presence_penalty_max'],
                        'median': row['presence_penalty_median']
                    } if row['presence_penalty_min'] is not None else None,
                    'trait_frequency': {
                        'min': row['trait_frequency_min'],
                        'max': row['trait_frequency_max'],
                        'median': row['trait_frequency_median']
                    } if row['trait_frequency_min'] is not None else None,
                    'technical_intensity': {
                        'min': row['technical_intensity_min'],
                        'max': row['technical_intensity_max'],
                        'median': row['technical_intensity_median']
                    } if row['technical_intensity_min'] is not None else None,
                    'imperfection_tolerance': {
                        'min': row['imperfection_tolerance_min'],
                        'max': row['imperfection_tolerance_max'],
                        'median': row['imperfection_tolerance_median']
                    } if row['imperfection_tolerance_min'] is not None else None,
                    'sentence_rhythm_variation': {
                        'min': row['sentence_rhythm_variation_min'],
                        'max': row['sentence_rhythm_variation_max'],
                        'median': row['sentence_rhythm_variation_median']
                    } if row['sentence_rhythm_variation_min'] is not None else None,
                },
                'statistics': {
                    'sample_count': row['sample_count'],
                    'max_human_score': row['max_human_score'],
                    'avg_human_score': row['avg_human_score'],
                    'confidence_level': row['confidence_level']
                },
                'correlations': json.loads(row['parameter_correlations']) if row['parameter_correlations'] else [],
                'recommendations': json.loads(row['recommendations']) if row['recommendations'] else []
            }
    
    def get_passing_sample_patterns(self) -> Dict[str, Any]:
        """
        Analyze passing Winston samples to extract humanness patterns.
        
        Extracts conversational markers, number usage patterns, and sentence structures
        from content that successfully passed Winston AI detection (success=1).
        
        Returns:
            Dictionary with extracted patterns:
            {
                'sample_count': int,
                'best_score': float (lowest AI score),
                'average_score': float,
                'sample_excerpts': List[str],
                'conversational_markers': List[str],
                'number_patterns': List[str]
            }
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Query passing samples (success=1) ordered by best (lowest) AI score
            cursor.execute("""
                SELECT 
                    generated_text,
                    ai_score,
                    human_score,
                    material,
                    component_type
                FROM detection_results
                WHERE success = 1
                ORDER BY ai_score ASC
                LIMIT 20
            """)
            
            rows = cursor.fetchall()
            
            if not rows:
                # No passing samples yet - return empty patterns
                return {
                    'sample_count': 0,
                    'best_score': 1.0,
                    'average_score': 1.0,
                    'sample_excerpts': [],
                    'conversational_markers': [],
                    'number_patterns': []
                }
            
            # Extract patterns from passing samples
            sample_count = len(rows)
            ai_scores = [row['ai_score'] for row in rows]
            best_score = min(ai_scores)
            average_score = sum(ai_scores) / len(ai_scores)
            
            # Get sample excerpts (first 150 chars of best samples)
            sample_excerpts = []
            for row in rows[:3]:  # Top 3 best samples
                text = row['generated_text']
                excerpt = text[:150] if len(text) > 150 else text
                sample_excerpts.append(excerpt)
            
            # Extract conversational markers from all passing samples
            conversational_markers = set()
            number_patterns = set()
            
            for row in rows:
                text = row['generated_text'].lower()
                
                # Common conversational markers that appear in human-like text
                markers = [
                    'we use', 'around', 'roughly', 'about', 'typically',
                    'generally', 'usually', 'often', 'sometimes', 'tends to',
                    'stays near', 'close to', 'approximately', 'nearly'
                ]
                
                for marker in markers:
                    if marker in text:
                        conversational_markers.add(marker)
                
                # Extract number patterns (number + unit combinations)
                # Examples: "100 W", "8.8 g/cm³", "0.5%"
                import re
                number_unit_pattern = r'\d+\.?\d*\s*[A-Za-z/%³²°]+/?[A-Za-z]*³?'
                matches = re.findall(number_unit_pattern, row['generated_text'])
                for match in matches[:3]:  # Top 3 from each sample
                    if len(match) < 20:  # Reasonable length
                        number_patterns.add(match.strip())
            
            return {
                'sample_count': sample_count,
                'best_score': best_score,
                'average_score': average_score,
                'sample_excerpts': sample_excerpts,
                'conversational_markers': sorted(list(conversational_markers)),
                'number_patterns': sorted(list(number_patterns))[:10]  # Top 10 patterns
            }


