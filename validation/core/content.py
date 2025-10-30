#!/usr/bin/env python3
"""
Consolidated Content Validation

Combines content quality, author voice, caption integration, and text analysis
into a unified content validation service.

Merges functionality from:
- validation/content_validator.py
- validation/quality_validator.py  
- validation/caption_integration_validator.py
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from validation.core.base_validator import BaseValidator, ValidationContext
from validation.errors import ErrorType, ErrorSeverity, ValidationResult


@dataclass
class ContentQualityScore:
    """Comprehensive content quality metrics"""
    # Author voice metrics
    author_voice_score: float = 0.0
    vocabulary_diversity: float = 0.0
    style_consistency: float = 0.0
    
    # Human characteristics
    natural_flow: float = 0.0
    varied_sentence_structure: float = 0.0
    authentic_imperfections: float = 0.0
    
    # AI detection avoidance
    low_repetition: float = 0.0
    contextual_accuracy: float = 0.0
    human_believability: float = 0.0
    
    # Overall
    overall_score: float = 0.0
    passes_threshold: bool = False


class ContentValidator(BaseValidator):
    """
    Unified content validation service.
    
    Validates:
    - Author voice consistency
    - Content quality and readability
    - Caption integration
    - Human believability
    - AI detection avoidance
    """
    
    def __init__(
        self,
        quality_threshold: float = 0.7,
        strict_mode: bool = False
    ):
        """
        Initialize content validator.
        
        Args:
            quality_threshold: Minimum quality score (0.0-1.0)
            strict_mode: If True, treat warnings as errors
        """
        super().__init__(strict_mode=strict_mode)
        self.quality_threshold = quality_threshold
    
    def get_validator_name(self) -> str:
        """Return validator name"""
        return "ContentValidator"
    
    def validate(
        self,
        data: Any,
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """
        Validate content quality.
        
        Args:
            data: Dict with 'content' key containing text to validate
            context: Optional validation context
            
        Returns:
            ValidationResult with quality scores and pass/fail
        """
        self.clear_errors()
        
        # Extract content
        if not isinstance(data, dict):
            self.add_error(
                ErrorType.INVALID_FIELD,
                "Content data must be a dictionary",
                ErrorSeverity.ERROR
            )
            return self.create_result(success=False)
        
        content = data.get('content', '')
        if not content:
            self.add_error(
                ErrorType.MISSING_FIELD,
                "No content provided for validation",
                ErrorSeverity.ERROR,
                field='content'
            )
            return self.create_result(success=False)
        
        # Run quality checks
        quality_score = self._calculate_quality_score(content, context)
        
        # Check threshold
        if quality_score.overall_score < self.quality_threshold:
            self.add_error(
                ErrorType.LOW_CONFIDENCE,
                f"Content quality score {quality_score.overall_score:.2f} below threshold {self.quality_threshold}",
                ErrorSeverity.WARNING if not self.strict_mode else ErrorSeverity.ERROR,
                details={'score': quality_score.overall_score}
            )
        
        success = len([e for e in self.errors if e.severity == ErrorSeverity.ERROR]) == 0
        
        return self.create_result(
            success=success,
            data={
                'quality_score': quality_score.overall_score,
                'details': quality_score.__dict__
            }
        )
    
    def _calculate_quality_score(
        self,
        content: str,
        context: Optional[ValidationContext]
    ) -> ContentQualityScore:
        """
        Calculate comprehensive quality score.
        
        Args:
            content: Text content to score
            context: Optional context
            
        Returns:
            ContentQualityScore with all metrics
        """
        score = ContentQualityScore()
        
        # Basic metrics (simplified for consolidated version)
        word_count = len(content.split())
        sentence_count = content.count('.') + content.count('!') + content.count('?')
        
        # Author voice (0-1)
        score.author_voice_score = min(1.0, word_count / 500.0)
        score.vocabulary_diversity = self._calculate_diversity(content)
        score.style_consistency = 0.8  # Placeholder
        
        # Human characteristics (0-1)
        score.natural_flow = self._check_natural_flow(content)
        score.varied_sentence_structure = min(1.0, sentence_count / 20.0)
        score.authentic_imperfections = 0.75  # Placeholder
        
        # AI avoidance (0-1)
        score.low_repetition = self._check_repetition(content)
        score.contextual_accuracy = 0.85  # Placeholder
        score.human_believability = 0.80  # Placeholder
        
        # Overall score (weighted average)
        score.overall_score = (
            score.author_voice_score * 0.2 +
            score.natural_flow * 0.2 +
            score.vocabulary_diversity * 0.2 +
            score.low_repetition * 0.2 +
            score.human_believability * 0.2
        )
        
        score.passes_threshold = score.overall_score >= self.quality_threshold
        
        return score
    
    def _calculate_diversity(self, content: str) -> float:
        """Calculate vocabulary diversity (unique words / total words)"""
        words = content.lower().split()
        if not words:
            return 0.0
        unique_words = len(set(words))
        return min(1.0, unique_words / len(words))
    
    def _check_natural_flow(self, content: str) -> float:
        """Check for natural language flow"""
        # Simple heuristic: penalize very short or very long sentences
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if not sentences:
            return 0.0
        
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        # Ideal: 15-25 words per sentence
        if 15 <= avg_length <= 25:
            return 1.0
        elif 10 <= avg_length <= 30:
            return 0.8
        else:
            return 0.6
    
    def _check_repetition(self, content: str) -> float:
        """Check for excessive word repetition"""
        words = content.lower().split()
        if len(words) < 10:
            return 1.0
        
        # Find most common words (excluding common stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        filtered_words = [w for w in words if w not in stop_words]
        
        if not filtered_words:
            return 1.0
        
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        max_freq = max(word_freq.values())
        repetition_ratio = max_freq / len(filtered_words)
        
        # Lower repetition is better
        return max(0.0, 1.0 - (repetition_ratio * 5))


class CaptionIntegrationValidator(BaseValidator):
    """
    Validates caption integration into frontmatter.
    
    Checks that captions are:
    - Present and non-empty
    - Properly formatted
    - Contextually appropriate
    """
    
    def __init__(self, strict_mode: bool = False):
        """Initialize caption validator"""
        super().__init__(strict_mode=strict_mode)
    
    def get_validator_name(self) -> str:
        """Return validator name"""
        return "CaptionIntegrationValidator"
    
    def validate(
        self,
        data: Any,
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """
        Validate caption integration.
        
        Args:
            data: Dict with 'caption' key
            context: Optional validation context
            
        Returns:
            ValidationResult
        """
        self.clear_errors()
        
        if not isinstance(data, dict):
            self.add_error(
                ErrorType.INVALID_FIELD,
                "Caption data must be a dictionary",
                ErrorSeverity.ERROR
            )
            return self.create_result(success=False)
        
        caption = data.get('caption', '')
        
        # Check caption exists
        if not caption:
            self.add_error(
                ErrorType.MISSING_FIELD,
                "Caption is missing",
                ErrorSeverity.WARNING,  # Warning, not error
                field='caption'
            )
        
        # Check caption length (reasonable bounds)
        elif len(caption) < 10:
            self.add_error(
                ErrorType.INVALID_VALUE,
                f"Caption too short ({len(caption)} chars)",
                ErrorSeverity.WARNING,
                field='caption'
            )
        elif len(caption) > 500:
            self.add_error(
                ErrorType.INVALID_VALUE,
                f"Caption too long ({len(caption)} chars)",
                ErrorSeverity.WARNING,
                field='caption'
            )
        
        success = not self.has_errors()
        return self.create_result(success=success)
