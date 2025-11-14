"""
AI Detection Ensemble

Combines multiple detectors for robust AI content identification.
Composite scoring reduces false positives/negatives.
"""

import logging
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)


class AIDetectorEnsemble:
    """
    Ensemble of AI detection methods.
    
    Combines:
    1. Pattern-based detection (fast, rule-based)
    2. Optional: Hugging Face model (accurate, ML-based)
    
    Composite score = weighted average of all detectors.
    """
    
    def __init__(self, patterns_file: str = None, use_ml: bool = False):
        """
        Initialize ensemble.
        
        Args:
            patterns_file: Path to AI detection patterns
            use_ml: Whether to use ML model (requires transformers)
        """
        self.patterns_file = patterns_file or self._default_patterns_file()
        self.use_ml = use_ml
        self._patterns = self._load_patterns()
        self._model = None
        
        if use_ml:
            self._load_ml_model()
    
    def _default_patterns_file(self) -> str:
        """Get default patterns file path"""
        return str(Path(__file__).parent.parent.parent / "shared" / "voice" / "ai_detection_patterns.txt")
    
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
            - is_ai_like: Boolean threshold check (>0.3)
            - pattern_score: Pattern-based score
            - ml_score: ML model score (if enabled)
            - detected_patterns: List of matched patterns
        """
        # Pattern-based detection
        pattern_result = self._pattern_detection(text)
        
        # ML detection (if enabled)
        ml_score = 0.0
        if self.use_ml and self._model:
            ml_score = self._ml_detection(text)
        
        # Composite score (weighted average)
        if self.use_ml:
            ai_score = (0.4 * pattern_result['score']) + (0.6 * ml_score)
        else:
            ai_score = pattern_result['score']
        
        return {
            'ai_score': round(ai_score, 3),
            'is_ai_like': ai_score > 0.3,
            'pattern_score': pattern_result['score'],
            'ml_score': ml_score,
            'detected_patterns': pattern_result['patterns'],
            'method': 'ensemble' if self.use_ml else 'pattern_only'
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
