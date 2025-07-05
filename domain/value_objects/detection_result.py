"""
Value objects for detection results in the Z-Beam domain.
These represent the outcomes of AI and human-like content detection.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class DetectionStatus(Enum):
    """Enumeration of detection statuses."""
    PASSED = "passed"           # Content passed all thresholds
    FAILED = "failed"           # Content failed thresholds
    INCONCLUSIVE = "inconclusive"  # Results were unclear
    ERROR = "error"             # Detection process failed


class ContentQuality(Enum):
    """Enumeration of content quality levels."""
    EXCELLENT = "excellent"     # High human-like, low AI scores
    GOOD = "good"              # Acceptable scores within thresholds
    MARGINAL = "marginal"      # Close to threshold boundaries
    POOR = "poor"              # Failed thresholds significantly


@dataclass(frozen=True)
class DetectionScore:
    """Value object representing a single detection score."""
    
    score: float  # 0-100 scale
    confidence: float  # 0-1 scale
    model_used: str
    timestamp: datetime
    
    def __post_init__(self):
        """Validate detection score."""
        if not 0 <= self.score <= 100:
            raise ValueError("Score must be between 0 and 100")
        
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        
        if not self.model_used or not self.model_used.strip():
            raise ValueError("Model used cannot be empty")
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if the detection score has high confidence."""
        return self.confidence >= threshold
    
    def get_score_category(self) -> str:
        """Get a categorical representation of the score."""
        if self.score <= 20:
            return "very_low"
        elif self.score <= 40:
            return "low"
        elif self.score <= 60:
            return "medium"
        elif self.score <= 80:
            return "high"
        else:
            return "very_high"


@dataclass(frozen=True)
class DetectionResult:
    """Value object representing the complete detection result for content."""
    
    ai_score: float  # 0-100, lower is better (less AI-like)
    human_score: float  # 0-100, higher is better (more human-like)
    ai_confidence: float  # 0-1
    human_confidence: float  # 0-1
    status: DetectionStatus
    quality: ContentQuality
    iteration: int
    timestamp: datetime
    detailed_scores: Optional[Dict[str, DetectionScore]] = None
    analysis_notes: Optional[List[str]] = None
    processing_time_ms: Optional[float] = None
    
    def __post_init__(self):
        """Validate detection result."""
        if not 0 <= self.ai_score <= 100:
            raise ValueError("AI score must be between 0 and 100")
        
        if not 0 <= self.human_score <= 100:
            raise ValueError("Human score must be between 0 and 100")
        
        if not 0 <= self.ai_confidence <= 1:
            raise ValueError("AI confidence must be between 0 and 1")
        
        if not 0 <= self.human_confidence <= 1:
            raise ValueError("Human confidence must be between 0 and 1")
        
        if self.iteration <= 0:
            raise ValueError("Iteration must be positive")
    
    def passes_thresholds(self, ai_threshold: float, human_threshold: float) -> bool:
        """Check if the result passes the specified thresholds."""
        return self.ai_score <= ai_threshold and self.human_score >= human_threshold
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if both confidence scores are high."""
        return self.ai_confidence >= threshold and self.human_confidence >= threshold
    
    def get_overall_confidence(self) -> float:
        """Calculate overall confidence as average of both scores."""
        return (self.ai_confidence + self.human_confidence) / 2
    
    def get_quality_score(self) -> float:
        """Calculate a quality score (0-100) based on AI and human scores."""
        # Lower AI score is better, higher human score is better
        ai_quality = 100 - self.ai_score  # Invert AI score
        human_quality = self.human_score
        return (ai_quality + human_quality) / 2
    
    def has_detailed_analysis(self) -> bool:
        """Check if detailed analysis information is available."""
        return bool(self.detailed_scores and self.analysis_notes)
    
    def get_detailed_score(self, detector_name: str) -> Optional[DetectionScore]:
        """Get detailed score for a specific detector."""
        if not self.detailed_scores:
            return None
        return self.detailed_scores.get(detector_name)
    
    def add_analysis_note(self, note: str) -> 'DetectionResult':
        """Create a new instance with an additional analysis note."""
        current_notes = list(self.analysis_notes) if self.analysis_notes else []
        new_notes = current_notes + [note]
        
        return DetectionResult(
            ai_score=self.ai_score,
            human_score=self.human_score,
            ai_confidence=self.ai_confidence,
            human_confidence=self.human_confidence,
            status=self.status,
            quality=self.quality,
            iteration=self.iteration,
            timestamp=self.timestamp,
            detailed_scores=self.detailed_scores,
            analysis_notes=new_notes,
            processing_time_ms=self.processing_time_ms
        )
    
    @classmethod
    def create_passed(
        cls,
        ai_score: float,
        human_score: float,
        ai_confidence: float,
        human_confidence: float,
        iteration: int
    ) -> 'DetectionResult':
        """Create a detection result that passed thresholds."""
        quality = cls._determine_quality(ai_score, human_score)
        
        return cls(
            ai_score=ai_score,
            human_score=human_score,
            ai_confidence=ai_confidence,
            human_confidence=human_confidence,
            status=DetectionStatus.PASSED,
            quality=quality,
            iteration=iteration,
            timestamp=datetime.now()
        )
    
    @classmethod
    def create_failed(
        cls,
        ai_score: float,
        human_score: float,
        ai_confidence: float,
        human_confidence: float,
        iteration: int,
        reason: str = None
    ) -> 'DetectionResult':
        """Create a detection result that failed thresholds."""
        quality = ContentQuality.POOR
        analysis_notes = [reason] if reason else None
        
        return cls(
            ai_score=ai_score,
            human_score=human_score,
            ai_confidence=ai_confidence,
            human_confidence=human_confidence,
            status=DetectionStatus.FAILED,
            quality=quality,
            iteration=iteration,
            timestamp=datetime.now(),
            analysis_notes=analysis_notes
        )
    
    @classmethod
    def create_error(cls, iteration: int, error_message: str) -> 'DetectionResult':
        """Create a detection result for an error condition."""
        return cls(
            ai_score=0.0,
            human_score=0.0,
            ai_confidence=0.0,
            human_confidence=0.0,
            status=DetectionStatus.ERROR,
            quality=ContentQuality.POOR,
            iteration=iteration,
            timestamp=datetime.now(),
            analysis_notes=[f"Error: {error_message}"]
        )
    
    @staticmethod
    def _determine_quality(ai_score: float, human_score: float) -> ContentQuality:
        """Determine content quality based on scores."""
        quality_score = (100 - ai_score + human_score) / 2
        
        if quality_score >= 80:
            return ContentQuality.EXCELLENT
        elif quality_score >= 65:
            return ContentQuality.GOOD
        elif quality_score >= 50:
            return ContentQuality.MARGINAL
        else:
            return ContentQuality.POOR


@dataclass(frozen=True)
class AggregateDetectionResult:
    """Value object representing aggregated detection results across multiple sections."""
    
    section_results: Dict[str, DetectionResult]
    overall_ai_score: float
    overall_human_score: float
    overall_status: DetectionStatus
    overall_quality: ContentQuality
    total_iterations: int
    timestamp: datetime
    
    def __post_init__(self):
        """Validate aggregate detection result."""
        if not self.section_results:
            raise ValueError("Section results cannot be empty")
        
        if not 0 <= self.overall_ai_score <= 100:
            raise ValueError("Overall AI score must be between 0 and 100")
        
        if not 0 <= self.overall_human_score <= 100:
            raise ValueError("Overall human score must be between 0 and 100")
    
    def get_section_count(self) -> int:
        """Get the number of sections analyzed."""
        return len(self.section_results)
    
    def get_passed_sections(self, ai_threshold: float, human_threshold: float) -> List[str]:
        """Get list of sections that passed the thresholds."""
        return [
            section for section, result in self.section_results.items()
            if result.passes_thresholds(ai_threshold, human_threshold)
        ]
    
    def get_failed_sections(self, ai_threshold: float, human_threshold: float) -> List[str]:
        """Get list of sections that failed the thresholds."""
        return [
            section for section, result in self.section_results.items()
            if not result.passes_thresholds(ai_threshold, human_threshold)
        ]
    
    def get_pass_rate(self, ai_threshold: float, human_threshold: float) -> float:
        """Calculate the percentage of sections that passed."""
        passed_count = len(self.get_passed_sections(ai_threshold, human_threshold))
        return (passed_count / self.get_section_count()) * 100
    
    def get_average_quality_score(self) -> float:
        """Calculate average quality score across all sections."""
        if not self.section_results:
            return 0.0
        
        total_quality = sum(result.get_quality_score() for result in self.section_results.values())
        return total_quality / len(self.section_results)
    
    @classmethod
    def create_from_sections(cls, section_results: Dict[str, DetectionResult]) -> 'AggregateDetectionResult':
        """Create aggregate result from individual section results."""
        if not section_results:
            raise ValueError("Section results cannot be empty")
        
        # Calculate overall scores as averages
        ai_scores = [result.ai_score for result in section_results.values()]
        human_scores = [result.human_score for result in section_results.values()]
        
        overall_ai_score = sum(ai_scores) / len(ai_scores)
        overall_human_score = sum(human_scores) / len(human_scores)
        
        # Determine overall status
        statuses = [result.status for result in section_results.values()]
        if all(status == DetectionStatus.PASSED for status in statuses):
            overall_status = DetectionStatus.PASSED
        elif any(status == DetectionStatus.ERROR for status in statuses):
            overall_status = DetectionStatus.ERROR
        elif any(status == DetectionStatus.INCONCLUSIVE for status in statuses):
            overall_status = DetectionStatus.INCONCLUSIVE
        else:
            overall_status = DetectionStatus.FAILED
        
        # Determine overall quality
        overall_quality = DetectionResult._determine_quality(overall_ai_score, overall_human_score)
        
        # Calculate total iterations
        total_iterations = sum(result.iteration for result in section_results.values())
        
        return cls(
            section_results=section_results,
            overall_ai_score=overall_ai_score,
            overall_human_score=overall_human_score,
            overall_status=overall_status,
            overall_quality=overall_quality,
            total_iterations=total_iterations,
            timestamp=datetime.now()
        )
