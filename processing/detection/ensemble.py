"""
AI Detection Ensemble

Combines multiple detectors for robust AI content identification.
Composite scoring reduces false positives/negatives.
"""

import logging
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

# Import the advanced AI detector
try:
    from processing.detection.ai_detection import AIDetector
    ADVANCED_DETECTOR_AVAILABLE = True
except ImportError:
    ADVANCED_DETECTOR_AVAILABLE = False
    logger.warning("Advanced AI detector not available")


class AIDetectorEnsemble:
    """
    Ensemble of AI detection methods.
    
    Combines:
    1. Pattern-based detection (fast, rule-based)
    2. Optional: Hugging Face model (accurate, ML-based)
    
    Composite score = weighted average of all detectors.
    """
    
    def __init__(self, patterns_file: str = None, use_ml: bool = False, use_advanced: bool = True):
        """
        Initialize ensemble.
        
        Args:
            patterns_file: Path to AI detection patterns
            use_ml: Whether to use ML model (requires transformers)
            use_advanced: Whether to use advanced pattern detector (default True)
        """
        self.patterns_file = patterns_file or self._default_patterns_file()
        self.use_ml = use_ml
        self.use_advanced = use_advanced and ADVANCED_DETECTOR_AVAILABLE
        self._patterns = self._load_patterns()
        self._model = None
        self._advanced_detector = None
        
        # Initialize advanced detector if available
        if self.use_advanced and ADVANCED_DETECTOR_AVAILABLE:
            try:
                self._advanced_detector = AIDetector(strict_mode=False)
                logger.info("Advanced AI detector initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize advanced detector: {e}")
                self.use_advanced = False
        
        if use_ml:
            self._load_ml_model()
    
    def _default_patterns_file(self) -> str:
        """Get default patterns file path"""
        return str(Path(__file__).parent.parent.parent / "prompts" / "ai_detection_patterns.txt")
    
    def _load_patterns(self) -> List[str]:
        """Load detection patterns from file"""
        patterns = []
        try:
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line.lower())
            logger.info(f"Loaded {len(patterns)} detection patterns")
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
        
        return patterns
    
    def _load_ml_model(self):
        """Load Hugging Face model for advanced detection"""
        try:
            from transformers import pipeline
            # Use a fine-tuned model for AI text detection
            # Example: "roberta-base-openai-detector" or custom model
            self._model = pipeline("text-classification", model="roberta-base-openai-detector")
            logger.info("Loaded ML detection model")
        except ImportError:
            logger.warning("transformers not installed - ML detection disabled")
            self.use_ml = False
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            self.use_ml = False
    
    def detect(self, text: str) -> Dict:
        """
        Run ensemble detection on text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with:
            - ai_score: Composite score (0-1, higher = more AI-like)
            - is_ai_like: Boolean threshold check
            - pattern_score: Simple pattern score
            - advanced_score: Advanced pattern score (if enabled)
            - ml_score: ML model score (if enabled)
            - detected_patterns: List of matched patterns
            - details: Advanced detector details (if available)
        """
        # Simple pattern-based detection
        pattern_result = self._pattern_detection(text)
        
        # Advanced detection (if enabled)
        advanced_score = 0.0
        advanced_details = None
        if self.use_advanced and self._advanced_detector:
            advanced_result = self._advanced_detector.detect(text)
            advanced_score = advanced_result['ai_score']
            advanced_details = advanced_result.get('details')
        
        # ML detection (if enabled)
        ml_score = 0.0
        if self.use_ml and self._model:
            ml_score = self._ml_detection(text)
        
        # Composite score (weighted average)
        if self.use_advanced and self.use_ml:
            # All three: advanced (50%), ML (30%), simple (20%)
            ai_score = (0.5 * advanced_score) + (0.3 * ml_score) + (0.2 * pattern_result['score'])
        elif self.use_advanced:
            # Advanced + simple: advanced (70%), simple (30%)
            ai_score = (0.7 * advanced_score) + (0.3 * pattern_result['score'])
        elif self.use_ml:
            # ML + simple: ML (60%), simple (40%)
            ai_score = (0.6 * ml_score) + (0.4 * pattern_result['score'])
        else:
            # Simple only
            ai_score = pattern_result['score']
        
        # Determine method
        if self.use_advanced and self.use_ml:
            method = 'ensemble_advanced_ml'
        elif self.use_advanced:
            method = 'ensemble_advanced'
        elif self.use_ml:
            method = 'ensemble_ml'
        else:
            method = 'pattern_only'
        
        return {
            'ai_score': round(ai_score, 3),
            'is_ai_like': ai_score > 0.3,
            'pattern_score': pattern_result['score'],
            'advanced_score': advanced_score,
            'ml_score': ml_score,
            'detected_patterns': pattern_result['patterns'],
            'details': advanced_details,
            'method': method
        }
    
    def _pattern_detection(self, text: str) -> Dict:
        """
        Pattern-based detection.
        
        Returns:
            Dict with score and matched patterns
        """
        text_lower = text.lower()
        matched = []
        
        for pattern in self._patterns:
            if pattern in text_lower:
                matched.append(pattern)
        
        # Score = percentage of patterns matched (capped at 1.0)
        score = min(len(matched) / max(len(self._patterns) * 0.1, 1), 1.0)
        
        return {
            'score': score,
            'patterns': matched
        }
    
    def _ml_detection(self, text: str) -> float:
        """
        ML-based detection using Hugging Face model.
        
        Returns:
            Score (0-1)
        """
        try:
            result = self._model(text)[0]
            # Model returns label + score
            # Assume label "AI" or "LABEL_1" indicates AI-generated
            if result['label'] in ['AI', 'LABEL_1', 'machine-generated']:
                return result['score']
            else:
                return 1.0 - result['score']
        except Exception as e:
            logger.error(f"ML detection failed: {e}")
            return 0.0
    
    def batch_detect(self, texts: List[str]) -> List[Dict]:
        """
        Detect AI in batch.
        
        Args:
            texts: List of texts
            
        Returns:
            List of detection results
        """
        return [self.detect(text) for text in texts]
