"""
Winston AI Detection Integration Facade

Centralizes all Winston API interaction logic including:
- Detection mode management (always/smart/disabled/final_only)
- API detection with fallback to pattern-based
- Database logging and feedback analysis
- Smart usage decisions for cost control

This facade replaces 8+ scattered Winston integration points throughout
the codebase with a single, testable, well-documented interface.
"""

import logging
import os
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class WinstonIntegration:
    """
    Unified facade for Winston AI detection and feedback.
    
    Responsibilities:
    - Manage Winston usage modes and smart detection decisions
    - Coordinate AI detection with fallback to pattern-based
    - Log detection results to feedback database
    - Analyze failures and provide adaptive guidance
    
    Benefits:
    - Single source of truth for Winston behavior
    - Easy to mock for testing
    - Clear error handling and fallback paths
    - Centralized cost control logic
    """
    
    def __init__(
        self,
        winston_client=None,
        feedback_db=None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Winston integration.
        
        Args:
            winston_client: Winston API client (optional, falls back to patterns)
            feedback_db: WinstonFeedbackDatabase instance (optional)
            config: Configuration dict with winston_usage_mode, etc.
        """
        self.winston_client = winston_client
        self.feedback_db = feedback_db
        self.config = config or {}
        
        # Initialize ensemble detector
        from postprocessing.detection.ensemble import AIDetectorEnsemble
        self.detector = AIDetectorEnsemble(
            winston_client=winston_client
        )
        
        # Initialize analyzer if database available
        self.analyzer = None
        if feedback_db:
            try:
                from postprocessing.detection.winston_analyzer import WinstonFeedbackAnalyzer
                self.analyzer = WinstonFeedbackAnalyzer()
            except Exception as e:
                logger.warning(f"Winston analyzer unavailable: {e}")
        
        # Log availability
        if winston_client:
            logger.info("Winston API client available for detection")
        else:
            logger.warning("Winston API unavailable - pattern-based detection only")
        
        if feedback_db:
            logger.info("Winston feedback database available for learning")
    
    def get_usage_mode(self) -> str:
        """
        Get configured Winston usage mode.
        
        Returns:
            Mode string: 'always', 'smart', 'disabled', 'final_only'
        """
        env_mode = os.getenv('WINSTON_USAGE_MODE', '').strip().lower()
        if env_mode in {'always', 'smart', 'disabled', 'final_only'}:
            return env_mode

        if os.getenv('DISABLE_WINSTON', '').strip().lower() in {'1', 'true', 'yes', 'on'}:
            return 'disabled'

        return 'always'
    
    def should_use_winston(self, attempt: int, max_attempts: int) -> bool:
        """
        Determine if Winston API should be used for this attempt.
        
        Now always returns True to ensure reliable learning data.
        Pattern-only detection was removed due to false positives polluting
        the training database.
        
        Args:
            attempt: Current attempt number (1-based)
            max_attempts: Maximum attempts allowed
            
        Returns:
            Always True (Winston API on every attempt)
        """
        mode = self.get_usage_mode()
        
        if mode == 'disabled':
            logger.warning("Winston disabled mode detected - this may create unreliable learning data")
            return False
        
        # Always use Winston for accurate detection and clean learning data
        return True
    
    def detect_and_log(
        self,
        text: str,
        material: str,
        component_type: str,
        temperature: float,
        attempt: int,
        max_attempts: int,
        ai_threshold: float
    ) -> Dict[str, Any]:
        """
        Detect AI content and log results to database.
        
        This is the primary method for all detection operations.
        Handles mode logic, fallback to patterns, database logging, and analysis.
        
        Args:
            text: Generated text to analyze
            material: Material name
            component_type: Component type
            temperature: Generation temperature
            attempt: Current attempt number
            max_attempts: Maximum attempts
            ai_threshold: AI score threshold for success
            
        Returns:
            Dict with:
            - ai_score: float (0-1)
            - detection: Dict with full detection results
            - detection_id: int (database ID if logged)
            - failure_analysis: Dict (if analyzer available)
            - method: str ('winston' or 'pattern_only')
        """
        mode = self.get_usage_mode()

        if mode == 'disabled':
            logger.warning("⏭️ Winston detection disabled via configuration (temporary mode)")
            return {
                'ai_score': 0.0,
                'detection': {
                    'ai_score': 0.0,
                    'human_score': 1.0,
                    'mode': 'disabled',
                    'reason': 'Winston temporarily disabled via WINSTON_USAGE_MODE/DISABLE_WINSTON'
                },
                'detection_id': None,
                'failure_analysis': None,
                'method': 'disabled'
            }

        # Always use Winston API for reliable detection
        use_winston = self.should_use_winston(attempt, max_attempts)
        
        # Perform detection
        if use_winston and self.winston_client:
            # Winston API detection (sentence-level analysis)
            detection = self.detector.detect(text)
            method = 'winston' if 'sentences' in detection else 'pattern_only'
            logger.info(f"🔍 Detection method: {method}")
        else:
            # No Winston client available - fail fast
            logger.error("❌ Winston API client not available - cannot proceed without reliable detection")
            raise RuntimeError(
                "Winston API client required for generation. "
                "Pattern-only detection has been removed to prevent false positives in learning data."
            )
        
        ai_score = detection['ai_score']
        
        # Analyze failure if Winston result available
        failure_analysis = None
        if self.analyzer and 'sentences' in detection:
            failure_analysis = self.analyzer.analyze_failure(detection)
        
        # Log to database if available
        detection_id = None
        if self.feedback_db and 'sentences' in detection:
            try:
                success = ai_score <= ai_threshold
                detection_id = self.feedback_db.log_detection(
                    material=material,
                    component_type=component_type,
                    generated_text=text,
                    winston_result=detection,
                    temperature=temperature,
                    attempt=attempt,
                    success=success,
                    failure_analysis=failure_analysis
                )
                logger.info(f"📊 Logged detection result to database (ID: {detection_id})")
            except Exception as e:
                logger.warning(f"Failed to log detection result: {e}")
        
        return {
            'ai_score': ai_score,
            'detection': detection,
            'detection_id': detection_id,
            'failure_analysis': failure_analysis,
            'method': method
        }
    
    def should_extend_attempts(
        self,
        current_attempt: int,
        winston_result: Dict,
        max_extensions: int = 2,
        absolute_max: int = 3
    ) -> bool:
        """
        Check if attempts should be extended based on Winston feedback.
        
        Only applicable in 'always' mode with adaptive retry enabled.
        
        Args:
            current_attempt: Current attempt number
            winston_result: Winston detection result
            max_extensions: Maximum extensions allowed
            absolute_max: Absolute maximum attempts
            
        Returns:
            True if attempts should be extended
        """
        # Only in 'always' mode
        mode = self.get_usage_mode()
        if mode != 'always':
            return False
        
        # Must have analyzer
        if not self.analyzer:
            return False
        
        # Use analyzer to decide
        try:
            should_extend = self.analyzer.should_extend_attempts(
                current_attempt=current_attempt,
                winston_result=winston_result,
                max_extensions=max_extensions,
                absolute_max=absolute_max
            )
            
            if should_extend:
                analysis = self.analyzer.analyze_failure(winston_result)
                logger.info(f"🔄 [ADAPTIVE RETRY] Extending attempts based on feedback")
                logger.info(f"   Type: {analysis['failure_type']}")
                logger.info(f"   Guidance: {analysis['guidance']}")
            
            return should_extend
            
        except Exception as e:
            logger.warning(f"[ADAPTIVE RETRY] Failed to analyze: {e}")
            return False
    
    def get_max_attempts_for_mode(self, default: int = 3) -> int:
        """
        Get initial max attempts based on Winston usage mode.
        
        Args:
            default: Default max attempts
            
        Returns:
            Initial max attempts (can be extended adaptively)
        """
        mode = self.get_usage_mode()
        
        # In 'always' mode, start with 1 attempt (can extend based on feedback)
        if mode == 'always':
            return 1
        
        # Default for other modes
        return default
