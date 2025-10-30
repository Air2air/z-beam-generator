#!/usr/bin/env python3
"""
Quality Validation for Generated Content

Implements inline validation for FAQ, Caption, and Subtitle content
with strict quality enforcement and auto-regeneration support.

Part of the validation pipeline integration (Phase 1).
"""

import re
import logging
from typing import Dict, List, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when content fails quality validation in strict mode."""
    pass


class ContentValidator:
    """
    Validates generated content for quality, repetition, and variation.
    
    Supports two modes:
    - strict_mode=True: Raises ValidationError on quality failures (fail-fast)
    - strict_mode=False: Logs warnings but allows content through (dev mode)
    """
    
    # Common voice markers to track for repetition
    VOICE_MARKERS = [
        'systematic', 'precisely', 'methodology', 'framework', 'comprehensive',  # Taiwan
        'meticulous', 'precision', 'finesse', 'artisan', 'craftsmanship',  # Italy
        'innovative', 'performance', 'advanced', 'cutting-edge', 'breakthrough',  # USA
        'sustainable', 'heritage', 'wisdom', 'harmony', 'balance'  # Indonesia
    ]
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator.
        
        Args:
            strict_mode: If True, raises ValidationError on quality failures
        """
        self.strict_mode = strict_mode
    
    def validate_faq(
        self,
        faq_items: List[Dict],
        word_count_range: Tuple[int, int]
    ) -> Dict:
        """
        Validate FAQ content for quality.
        
        Args:
            faq_items: List of FAQ dictionaries with 'question' and 'answer' keys
            word_count_range: (min_words, max_words) tuple
            
        Returns:
            Dictionary with validation results:
            {
                'valid': bool,
                'quality_score': int (0-100),
                'errors': List[str],
                'warnings': List[str],
                'repetition_analysis': Dict[str, float],
                'variation_score': float
            }
        """
        min_words, max_words = word_count_range
        errors = []
        warnings = []
        quality_score = 100
        
        # Check word counts
        for i, item in enumerate(faq_items):
            answer = item.get('answer', '')
            word_count = len(answer.split())
            
            if word_count < min_words:
                errors.append(f"Q{i+1} answer too short: {word_count} words (min: {min_words})")
                quality_score -= 10
            elif word_count > max_words:
                errors.append(f"Q{i+1} answer too long: {word_count} words (max: {max_words})")
                quality_score -= 10
        
        # ABSOLUTE RULE: Check for cross-contamination between questions and answers
        cross_contamination = self._check_cross_contamination(faq_items)
        for issue in cross_contamination:
            errors.append(issue)
            quality_score -= 25  # Severe penalty - this is an absolute rule violation
        
        # Analyze repetition
        repetition_analysis = self._analyze_repetition(faq_items)
        
        for word, percentage in repetition_analysis.items():
            if percentage >= 100:
                errors.append(f"CRITICAL: '{word}' appears in 100% of answers (robotic)")
                quality_score -= 20
            elif percentage >= 80:
                errors.append(f"EXCESSIVE: '{word}' appears in {percentage:.0f}% of answers")
                quality_score -= 10
            elif percentage >= 60:
                warnings.append(f"HIGH: '{word}' appears in {percentage:.0f}% of answers")
                quality_score -= 5
        
        # Analyze variation
        variation_score = self._analyze_variation(faq_items)
        
        if variation_score < 0.2:
            errors.append(f"LOW VARIATION: Only {variation_score:.1%} unique sentence structures")
            quality_score -= 15
        elif variation_score < 0.4:
            warnings.append(f"MODERATE VARIATION: {variation_score:.1%} unique sentence structures (target: >40%)")
            quality_score -= 5
        
        # Detect repeated phrases
        repeated_phrases = self._detect_repeated_phrases(faq_items)
        
        for phrase, count in repeated_phrases.items():
            if count >= 4:
                errors.append(f"REPEATED PHRASE: '{phrase}' appears {count} times")
                quality_score -= 10
            elif count >= 3:
                warnings.append(f"Repeated phrase: '{phrase}' appears {count} times")
                quality_score -= 5
        
        # Cap quality score
        quality_score = max(0, quality_score)
        
        return {
            'valid': len(errors) == 0,
            'quality_score': quality_score,
            'errors': errors,
            'warnings': warnings,
            'repetition_analysis': repetition_analysis,
            'variation_score': variation_score,
            'repeated_phrases': repeated_phrases
        }
    
    def _analyze_repetition(self, faq_items: List[Dict]) -> Dict[str, float]:
        """
        Analyze word repetition across FAQ answers.
        
        Returns:
            Dictionary mapping words to their repetition percentage (0-100)
        """
        if not faq_items:
            return {}
        
        total_answers = len(faq_items)
        word_counts = Counter()
        
        for item in faq_items:
            answer = item.get('answer', '').lower()
            words_in_answer = set()
            
            for word in self.VOICE_MARKERS:
                if word in answer:
                    words_in_answer.add(word)
            
            for word in words_in_answer:
                word_counts[word] += 1
        
        # Convert to percentages
        repetition_analysis = {}
        for word, count in word_counts.items():
            percentage = (count / total_answers) * 100
            if percentage >= 60:  # Only report significant repetition
                repetition_analysis[word] = percentage
        
        return repetition_analysis
    
    def _analyze_variation(self, faq_items: List[Dict]) -> float:
        """
        Analyze sentence structure variation.
        
        Returns:
            Variation score (0.0-1.0) representing uniqueness ratio
        """
        if not faq_items:
            return 0.0
        
        # Extract sentence openings (first 3 words of each sentence)
        openings = []
        
        for item in faq_items:
            answer = item.get('answer', '')
            sentences = re.split(r'[.!?]+', answer)
            
            for sentence in sentences:
                words = sentence.strip().split()
                if len(words) >= 3:
                    opening = ' '.join(words[:3]).lower()
                    openings.append(opening)
        
        if not openings:
            return 0.0
        
        # Calculate uniqueness ratio
        unique_openings = len(set(openings))
        total_openings = len(openings)
        
        return unique_openings / total_openings
    
    def _detect_repeated_phrases(self, faq_items: List[Dict]) -> Dict[str, int]:
        """
        Detect multi-word phrases that appear multiple times.
        
        Returns:
            Dictionary mapping phrases to occurrence count (only 2+ occurrences)
        """
        # Extract 2-3 word phrases
        phrase_counts = Counter()
        
        for item in faq_items:
            answer = item.get('answer', '').lower()
            words = re.findall(r'\b\w+\b', answer)
            
            # 2-word phrases
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}"
                if len(phrase) > 6:  # Skip very short phrases
                    phrase_counts[phrase] += 1
            
            # 3-word phrases
            for i in range(len(words) - 2):
                phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                if len(phrase) > 10:
                    phrase_counts[phrase] += 1
        
        # Return only phrases appearing 2+ times
        return {phrase: count for phrase, count in phrase_counts.items() if count >= 2}
    
    def _check_cross_contamination(self, faq_items: List[Dict]) -> List[str]:
        """
        ABSOLUTE RULE: Check for word/phrase repetition between questions and answers.
        
        This is a critical quality violation - questions and answers must be distinct.
        No significant words or phrases from questions should appear in their answers.
        
        Returns:
            List of error messages for cross-contamination violations
        """
        errors = []
        
        # Common words to ignore (articles, prepositions, etc.)
        stopwords = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'of', 'in', 'on', 'at', 'to',
            'for', 'with', 'from', 'by', 'about', 'as', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'what',
            'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'them', 'their', 'our', 'my', 'your',
            'laser', 'cleaning', 'material', 'surface', 'method', 'process'  # Domain-specific common words
        }
        
        for i, item in enumerate(faq_items):
            question = item.get('question', '').lower()
            answer = item.get('answer', '').lower()
            
            if not question or not answer:
                continue
            
            # Extract meaningful words from question (3+ chars, not stopwords)
            question_words = set()
            for word in re.findall(r'\b\w+\b', question):
                if len(word) >= 3 and word not in stopwords:
                    question_words.add(word)
            
            # Extract words from answer
            answer_words = set()
            for word in re.findall(r'\b\w+\b', answer):
                if len(word) >= 3 and word not in stopwords:
                    answer_words.add(word)
            
            # Check for overlap
            overlap = question_words & answer_words
            
            if overlap:
                overlap_ratio = len(overlap) / len(question_words) if question_words else 0
                
                # Critical violation: >30% of question words appear in answer
                if overlap_ratio > 0.3:
                    overlapping_words = sorted(list(overlap))[:5]  # Show first 5
                    errors.append(
                        f"Q{i+1} CROSS-CONTAMINATION: {overlap_ratio:.0%} of question words appear in answer "
                        f"({', '.join(overlapping_words)}{'...' if len(overlap) > 5 else ''})"
                    )
                # Moderate violation: 2-3 specific shared words
                elif len(overlap) >= 2:
                    overlapping_words = sorted(list(overlap))[:3]
                    errors.append(
                        f"Q{i+1} Word repetition: Question and answer share '{', '.join(overlapping_words)}'"
                    )
            
            # Check for repeated 2-3 word phrases between question and answer
            question_phrases = self._extract_phrases(question)
            answer_phrases = self._extract_phrases(answer)
            
            phrase_overlap = question_phrases & answer_phrases
            if phrase_overlap:
                for phrase in list(phrase_overlap)[:2]:  # Show first 2
                    errors.append(
                        f"Q{i+1} PHRASE REPETITION: '{phrase}' appears in both question and answer"
                    )
        
        return errors
    
    def _extract_phrases(self, text: str) -> set:
        """
        Extract 2-3 word phrases from text.
        
        Returns:
            Set of lowercase phrases
        """
        phrases = set()
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 2-word phrases
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 6:  # Skip very short
                phrases.add(phrase)
        
        # 3-word phrases
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(phrase) > 10:
                phrases.add(phrase)
        
        return phrases
    
    def validate_subtitle(
        self,
        subtitle: str,
        word_count_range: Tuple[int, int]
    ) -> Dict:
        """
        Validate subtitle content.
        
        Args:
            subtitle: The subtitle text
            word_count_range: (min_words, max_words) tuple
            
        Returns:
            Dictionary with validation results
        """
        min_words, max_words = word_count_range
        errors = []
        warnings = []
        quality_score = 100
        
        word_count = len(subtitle.split())
        
        if word_count < min_words:
            errors.append(f"Subtitle too short: {word_count} words (min: {min_words})")
            quality_score -= 20
        elif word_count > max_words:
            errors.append(f"Subtitle too long: {word_count} words (max: {max_words})")
            quality_score -= 20
        
        # Check for required elements
        if not re.search(r'[A-Z]', subtitle):
            errors.append("Subtitle missing capitalization")
            quality_score -= 10
        
        # Check for clichés
        cliches = ['revolutionary', 'game-changing', 'world-class', 'state-of-the-art']
        for cliche in cliches:
            if cliche.lower() in subtitle.lower():
                warnings.append(f"Cliché detected: '{cliche}'")
                quality_score -= 5
        
        quality_score = max(0, quality_score)
        
        return {
            'valid': len(errors) == 0,
            'quality_score': quality_score,
            'errors': errors,
            'warnings': warnings,
            'word_count': word_count
        }


class ValidationReporter:
    """Formats validation reports for human readability."""
    
    @staticmethod
    def format_report(validation_result: Dict) -> str:
        """
        Format validation result as readable string.
        
        Args:
            validation_result: Result from ContentValidator.validate_faq()
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("VALIDATION REPORT")
        lines.append("=" * 70)
        lines.append(f"Valid: {validation_result['valid']}")
        lines.append(f"Quality Score: {validation_result['quality_score']}/100")
        lines.append("")
        
        if validation_result.get('errors'):
            lines.append("ERRORS:")
            for error in validation_result['errors']:
                lines.append(f"  ❌ {error}")
            lines.append("")
        
        if validation_result.get('warnings'):
            lines.append("WARNINGS:")
            for warning in validation_result['warnings']:
                lines.append(f"  ⚠️  {warning}")
            lines.append("")
        
        if validation_result.get('repetition_analysis'):
            lines.append("REPETITION ANALYSIS:")
            for word, pct in sorted(validation_result['repetition_analysis'].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  • '{word}': {pct:.0f}%")
            lines.append("")
        
        if 'variation_score' in validation_result:
            lines.append(f"Variation Score: {validation_result['variation_score']:.1%}")
            lines.append("")
        
        return "\n".join(lines)
