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
    from postprocessing.detection.ai_detection import AIDetector
    ADVANCED_DETECTOR_AVAILABLE = True
except ImportError:
    ADVANCED_DETECTOR_AVAILABLE = False
    logger.warning("Advanced AI detector not available")


class AIDetectorEnsemble:
    """
    Simplified Winston-only AI detection.
    
    Uses Winston API exclusively for accurate AI content detection.
    Fails fast if Winston unavailable - no fallback methods.
    """
    
    def __init__(self, winston_client=None):
        """
        Initialize detector with Winston API client.
        
        Args:
            winston_client: Winston API client (required)
        """
        if not winston_client:
            raise ValueError("Winston API client required - no fallback detection methods")
        
        self._winston_client = winston_client
        logger.info("Winston API client initialized for AI detection")
    
    def detect(self, text: str) -> Dict:
        """
        Run Winston API detection on text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with:
            - ai_score: Winston AI score (0-1, higher = more AI-like)
            - human_score: Human-written percentage (0-100)
            - is_ai_like: Boolean threshold check (>0.3)
            - sentences: Per-sentence analysis from Winston
            - method: Always 'winston_api'
        """
        try:
            winston_result = self._winston_client.detect_ai_content(text)
            
            if not winston_result.get('success'):
                error_msg = winston_result.get('error', 'Unknown error')
                logger.error(f"Winston API failed: {error_msg}")
                raise RuntimeError(f"Winston API detection failed: {error_msg}")
            
            ai_score = winston_result['ai_score']
            human_score = winston_result.get('human_score', (1.0 - ai_score) * 100)
            
            logger.info(f"Winston API detection: AI={ai_score:.3f}, Human={human_score:.1f}%")
            
            return {
                'ai_score': round(ai_score, 3),
                'human_score': round(human_score, 1),
                'is_ai_like': ai_score > 0.3,
                'sentences': winston_result.get('sentences', []),
                'method': 'winston_api'
            }
            
        except Exception as e:
            logger.error(f"Winston API exception: {e}")
            raise RuntimeError(f"Winston API detection failed: {e}")
    
    def batch_detect(self, texts: List[str]) -> List[Dict]:
        """
        Detect AI in batch.
        
        Args:
            texts: List of texts
            
        Returns:
            List of detection results
        """
        return [self.detect(text) for text in texts]
