"""Quality Results Dataclass"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class QualityResults:
    """Results from quality assessment pass"""
    
    # Winston detection
    winston_ai_score: float
    winston_human_score: float
    
    # Realism evaluation
    realism_score: float
    
    # Readability
    readability_passes: bool = False
    
    # Subjective language
    subjective_violations: int = 0
    
    # Composite scoring
    composite_score: float = 0.0
    
    # Optional detailed results
    winston_sentence_scores: Optional[List[Dict]] = None
    realism_voice_authenticity: Optional[float] = None
    realism_tonal_consistency: Optional[float] = None
    realism_ai_tendencies: Optional[List[str]] = None
    readability_details: Optional[Dict] = None
    subjective_details: Optional[List[str]] = None
    subjective_full_result: Optional[Dict] = None
    
    def __post_init__(self):
        # Calculate composite if not provided
        if self.composite_score == 0.0:
            self.composite_score = (
                self.winston_human_score * 0.6 +
                self.realism_score * 10 * 0.4  # Convert 0-10 to 0-100
            )
