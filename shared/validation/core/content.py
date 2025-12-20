#!/usr/bin/env python3
"""
Consolidated Content Validation

Combines content quality, author voice, micro integration, and text analysis
into a unified content validation service.

Merges functionality from:
- validation/content_validator.py
- validation/quality_validator.py  
- validation/micro_integration_validator.py
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from shared.validation.core.base_validator import BaseValidator, ValidationContext
from shared.validation.errors import ErrorSeverity, ErrorType, ValidationResult


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
    - Micro integration
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


class MicroIntegrationValidator(BaseValidator):
    """
    Validates micro integration into frontmatter.
    
    Checks that micros are:
    - Present and non-empty
    - Properly formatted
    - Contextually appropriate
    """
    
    def __init__(self, strict_mode: bool = False):
        """Initialize micro validator"""
        super().__init__(strict_mode=strict_mode)
    
    def get_validator_name(self) -> str:
        """Return validator name"""
        return "MicroIntegrationValidator"
    
    def validate(
        self,
        data: Any,
        context: Optional[ValidationContext] = None
    ) -> ValidationResult:
        """
        Validate micro integration.
        
        Args:
            data: Dict with 'micro' key
            context: Optional validation context
            
        Returns:
            ValidationResult
        """
        self.clear_errors()
        
        if not isinstance(data, dict):
            self.add_error(
                ErrorType.INVALID_FIELD,
                "Micro data must be a dictionary",
                ErrorSeverity.ERROR
            )
            return self.create_result(success=False)
        
        caption = data.get('micro', '')
        
        # Check micro exists
        if not micro:
            self.add_error(
                ErrorType.MISSING_FIELD,
                "Micro is missing",
                ErrorSeverity.WARNING,  # Warning, not error
                field='micro'
            )
        
        # Check micro length (reasonable bounds)
        elif len(caption) < 10:
            self.add_error(
                ErrorType.INVALID_VALUE,
                f"Micro too short ({len(caption)} chars)",
                ErrorSeverity.WARNING,
                field='micro'
            )
        elif len(caption) > 500:
            self.add_error(
                ErrorType.INVALID_VALUE,
                f"Micro too long ({len(caption)} chars)",
                ErrorSeverity.WARNING,
                field='micro'
            )
        
        success = not self.has_errors()
        return self.create_result(success=success)


# ============================================================================
# Word Count & Text Structure Validation (Consolidated - Dec 19, 2025)
# ============================================================================

import re


def validate_word_count(
    text: str,
    min_words: Optional[int] = None,
    max_words: Optional[int] = None,
    component_type: str = "content"
) -> Dict:
    """
    Validate word count against min/max bounds.
    
    Consolidates word count validation from:
    - scripts/validation/validate_faq_output.py
    - Multiple generation validators
    
    Args:
        text: Content to validate
        min_words: Minimum word count (optional)
        max_words: Maximum word count (optional)
        component_type: Type of content for error messages
    
    Returns:
        Dict with keys:
            - valid: bool
            - word_count: int
            - errors: List[str]
            - warnings: List[str]
    
    Example:
        >>> result = validate_word_count("This is a test.", min_words=3, max_words=10)
        >>> result['valid']
        True
        >>> result['word_count']
        4
    """
    errors = []
    warnings = []
    
    # Count words (split on whitespace)
    words = text.split()
    word_count = len(words)
    
    # Check minimum
    if min_words is not None and word_count < min_words:
        errors.append(
            f"{component_type} too short: {word_count} words "
            f"(minimum: {min_words})"
        )
    
    # Check maximum
    if max_words is not None and word_count > max_words:
        errors.append(
            f"{component_type} too long: {word_count} words "
            f"(maximum: {max_words})"
        )
    
    # Warning for very short content
    if word_count < 3:
        warnings.append(f"{component_type} is very short ({word_count} words)")
    
    return {
        'valid': len(errors) == 0,
        'word_count': word_count,
        'errors': errors,
        'warnings': warnings
    }


def validate_sentence_count(
    text: str,
    min_sentences: Optional[int] = None,
    max_sentences: Optional[int] = None
) -> Dict:
    """
    Validate sentence count in text.
    
    Args:
        text: Content to validate
        min_sentences: Minimum sentence count (optional)
        max_sentences: Maximum sentence count (optional)
    
    Returns:
        Dict with validation results
    """
    errors = []
    warnings = []
    
    # Count sentences (split on . ! ?)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)
    
    if min_sentences is not None and sentence_count < min_sentences:
        errors.append(
            f"Too few sentences: {sentence_count} (minimum: {min_sentences})"
        )
    
    if max_sentences is not None and sentence_count > max_sentences:
        errors.append(
            f"Too many sentences: {sentence_count} (maximum: {max_sentences})"
        )
    
    return {
        'valid': len(errors) == 0,
        'sentence_count': sentence_count,
        'errors': errors,
        'warnings': warnings
    }


def validate_character_count(
    text: str,
    min_chars: Optional[int] = None,
    max_chars: Optional[int] = None,
    component_type: str = "content"
) -> Dict:
    """
    Validate character count against bounds.
    
    Args:
        text: Content to validate
        min_chars: Minimum character count (optional)
        max_chars: Maximum character count (optional)
        component_type: Type of content for error messages
    
    Returns:
        Dict with validation results
    """
    errors = []
    warnings = []
    
    char_count = len(text)
    
    if min_chars is not None and char_count < min_chars:
        errors.append(
            f"{component_type} too short: {char_count} chars "
            f"(minimum: {min_chars})"
        )
    
    if max_chars is not None and char_count > max_chars:
        errors.append(
            f"{component_type} too long: {char_count} chars "
            f"(maximum: {max_chars})"
        )
    
    return {
        'valid': len(errors) == 0,
        'character_count': char_count,
        'errors': errors,
        'warnings': warnings
    }


def validate_text_structure(
    text: str,
    require_punctuation: bool = True,
    require_capitalization: bool = True
) -> Dict:
    """
    Validate basic text structure and formatting.
    
    Args:
        text: Content to validate
        require_punctuation: Check for ending punctuation
        require_capitalization: Check for proper capitalization
    
    Returns:
        Dict with validation results
    """
    errors = []
    warnings = []
    
    if not text or not text.strip():
        errors.append("Text is empty")
        return {'valid': False, 'errors': errors, 'warnings': warnings}
    
    text = text.strip()
    
    # Check ending punctuation
    if require_punctuation:
        if not text[-1] in '.!?':
            warnings.append("Text does not end with punctuation")
    
    # Check capitalization
    if require_capitalization:
        if not text[0].isupper():
            warnings.append("Text does not start with capital letter")
    
    # Check for all caps (likely error)
    if text.isupper() and len(text) > 10:
        warnings.append("Text is all uppercase")
    
    # Check for excessive whitespace
    if '  ' in text:
        warnings.append("Text contains excessive whitespace")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def validate_content_completeness(
    text: str,
    forbidden_phrases: Optional[List[str]] = None
) -> Dict:
    """
    Validate content is complete and not placeholder text.
    
    Args:
        text: Content to validate
        forbidden_phrases: List of phrases indicating incomplete content
    
    Returns:
        Dict with validation results
    """
    errors = []
    warnings = []
    
    # Default forbidden phrases
    if forbidden_phrases is None:
        forbidden_phrases = [
            'todo', 'tbd', 'coming soon', 'placeholder',
            '[insert', 'xxx', 'lorem ipsum'
        ]
    
    text_lower = text.lower()
    
    found_phrases = []
    for phrase in forbidden_phrases:
        if phrase.lower() in text_lower:
            found_phrases.append(phrase)
    
    if found_phrases:
        errors.append(
            f"Content contains placeholder phrases: {', '.join(found_phrases)}"
        )
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'found_placeholders': found_phrases
    }
