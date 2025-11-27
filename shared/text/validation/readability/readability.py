"""
Readability Validation

Ensures generated content meets readability standards.
Prevents over-optimization that degrades clarity.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ReadabilityValidator:
    """
    Validates text readability using Flesch-Kincaid scoring.
    
    Ensures content remains accessible while avoiding AI detection.
    """
    
    def __init__(self, min_score: float = 60.0, max_score: float = 100.0):
        """
        Initialize validator.
        
        Args:
            min_score: Minimum acceptable Flesch Reading Ease score
            max_score: Maximum acceptable score (to prevent oversimplification)
        """
        self.min_score = min_score
        self.max_score = max_score
        
        # Try to import textstat
        try:
            import textstat
            self.textstat = textstat
            logger.info("Readability validation enabled")
        except ImportError:
            logger.warning("textstat not installed - readability validation disabled")
            self.textstat = None
    
    def validate(self, text: str) -> Dict:
        """
        Validate text readability.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with:
            - flesch_score: Flesch Reading Ease score
            - grade_level: Flesch-Kincaid Grade Level
            - is_readable: Boolean check against thresholds
            - status: 'pass', 'too_hard', 'too_easy', or 'disabled'
        """
        if not self.textstat:
            return {
                'flesch_score': None,
                'grade_level': None,
                'is_readable': True,  # Pass by default if disabled
                'status': 'disabled'
            }
        
        try:
            flesch = self.textstat.flesch_reading_ease(text)
            grade = self.textstat.flesch_kincaid_grade(text)
            
            # Determine status
            if flesch < self.min_score:
                status = 'too_hard'
                is_readable = False
            elif flesch > self.max_score:
                status = 'too_easy'
                is_readable = False
            else:
                status = 'pass'
                is_readable = True
            
            return {
                'flesch_score': round(flesch, 1),
                'grade_level': round(grade, 1),
                'is_readable': is_readable,
                'status': status
            }
        except Exception as e:
            logger.error(f"Readability validation failed: {e}")
            return {
                'flesch_score': None,
                'grade_level': None,
                'is_readable': True,  # Pass on error
                'status': 'error'
            }
    
    def suggest_improvement(self, readability: Dict) -> str:
        """
        Suggest improvements based on readability score.
        
        Args:
            readability: Result from validate()
            
        Returns:
            Improvement suggestion string
        """
        status = readability['status']
        
        if status == 'too_hard':
            return ("Text is too complex. Simplify: "
                   "use shorter sentences, simpler words, active voice.")
        elif status == 'too_easy':
            return ("Text is too simple. Add technical depth: "
                   "include specific terms, expand details.")
        elif status == 'pass':
            return "Readability is good."
        else:
            return "Readability check unavailable."
