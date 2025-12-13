"""
Unified Quality Analyzer - Consolidated Quality Assessment

Combines AI Detection and Voice Compliance into single analysis system.
Eliminates duplication between AIDetector and VoicePostProcessor validation.

Architecture:
    Single entry point → Multiple quality dimensions → Unified score
    
Quality Dimensions:
    1. AI Patterns (grammar, phrasing, repetition, statistical)
    2. Voice Authenticity (nationality markers, linguistic patterns)
    3. Language Detection (English vs translations)
    4. Translation Artifacts (reduplication, code-switching)
    5. Structural Quality (sentence variation, rhythm)

Usage:
    from shared.voice.quality_analyzer import QualityAnalyzer
    
    analyzer = QualityAnalyzer()
    result = analyzer.analyze(text, author={'name': 'Todd', 'country': 'United States'})
    
    print(f"Overall Quality: {result['overall_score']}/100")
    print(f"AI Pattern Score: {result['ai_patterns']['score']}/100")
    print(f"Voice Authenticity: {result['voice_authenticity']['score']}/100")
    
Design Principles:
    - Single responsibility: Quality assessment only
    - No side effects: Pure analysis, no modifications
    - Comprehensive: All quality dimensions in one place
    - Efficient: Shared text analysis across dimensions
"""

from typing import Dict, Any, Optional
import logging
import re
import statistics

# Import existing detection modules
from shared.voice.ai_detection import AIDetector, load_patterns
from shared.voice.post_processor import VoicePostProcessor

logger = logging.getLogger(__name__)


class QualityAnalyzer:
    """
    Unified quality analysis combining AI detection and voice compliance.
    
    Consolidates functionality from:
    - AIDetector (ai_detection.py) - AI pattern detection
    - VoicePostProcessor (post_processor.py) - Voice validation methods
    
    Provides single interface for all text quality assessment.
    """
    
    def __init__(self, api_client=None, strict_mode: bool = False):
        """
        Initialize quality analyzer.
        
        Args:
            api_client: Optional API client (only needed for voice enhancement)
            strict_mode: Use stricter thresholds for AI detection
        """
        # Initialize detection components
        self.ai_detector = AIDetector(strict_mode=strict_mode)
        self.strict_mode = strict_mode
        
        # Voice validation requires API client (optional)
        self.voice_validator = VoicePostProcessor(api_client) if api_client else None
        
        # Load patterns for analysis
        self.patterns = load_patterns()
        
        logger.info(f"QualityAnalyzer initialized (strict_mode={strict_mode})")
    
    def analyze(
        self,
        text: str,
        author: Optional[Dict[str, str]] = None,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive quality analysis of text.
        
        Args:
            text: Text content to analyze
            author: Optional author dict with 'name' and 'country' keys
            include_recommendations: Include improvement recommendations
            
        Returns:
            {
                'overall_score': float,  # 0-100 composite quality score
                'ai_patterns': {
                    'score': float,  # 0-100 (lower = more AI-like)
                    'is_ai_like': bool,
                    'issues': List[str],
                    'details': Dict
                },
                'voice_authenticity': {
                    'score': float,  # 0-100 (higher = more authentic)
                    'language': str,  # 'english', 'indonesian', etc.
                    'linguistic_patterns': Dict,
                    'issues': List[str]
                },
                'structural_quality': {
                    'sentence_variation': float,
                    'rhythm_score': float,
                    'complexity_variation': float
                },
                'recommendations': List[str]  # If include_recommendations=True
            }
        """
        logger.debug(f"Analyzing text quality ({len(text)} chars)")
        
        # 0. MINIMUM LENGTH CHECK - Content too short to evaluate properly
        MIN_CONTENT_LENGTH = 150  # Minimum chars for meaningful content
        if len(text) < MIN_CONTENT_LENGTH:
            return {
                'overall_score': 0.0,  # Auto-fail short content
                'ai_patterns': {
                    'score': 0.0,
                    'is_ai_like': False,
                    'issues': [f'Content too short: {len(text)} chars < {MIN_CONTENT_LENGTH} minimum'],
                    'details': {}
                },
                'voice_authenticity': {
                    'score': 0.0,
                    'language': 'unknown',
                    'linguistic_patterns': {},
                    'issues': ['Content too short for voice analysis']
                },
                'structural_quality': {
                    'sentence_variation': 0.0,
                    'rhythm_score': 0.0,
                    'complexity_variation': 0.0,
                    'sentence_count': len([s for s in text.split('.') if s.strip()])
                },
                'recommendations': [
                    f'Content is only {len(text)} characters (minimum: {MIN_CONTENT_LENGTH})',
                    'Generate proper material_description content',
                    'Content appears to be placeholder or title text'
                ]
            }
        
        # 1. AI Pattern Detection
        ai_result = self.ai_detector.detect_ai_patterns(text)
        
        # 2. Voice Authenticity (if author provided and validator available)
        voice_result = None
        if author and self.voice_validator:
            voice_result = self._analyze_voice_authenticity(text, author)
        
        # 3. Structural Quality
        structural_result = self._analyze_structural_quality(text)
        
        # 4. Calculate overall score
        overall_score = self._calculate_overall_score(
            ai_result, voice_result, structural_result
        )
        
        # 5. Generate recommendations
        recommendations = []
        if include_recommendations:
            recommendations = self._generate_recommendations(
                ai_result, voice_result, structural_result
            )
        
        return {
            'overall_score': overall_score,
            'ai_patterns': {
                'score': 100 - ai_result['ai_score'],  # Invert: higher is better
                'is_ai_like': ai_result['is_ai_like'],
                'issues': ai_result.get('issues', []),
                'details': {
                    'grammar_score': ai_result.get('grammar_score', 0),
                    'phrasing_score': ai_result.get('phrasing_score', 0),
                    'repetition_score': ai_result.get('repetition_score', 0),
                    'linguistic_score': ai_result.get('linguistic_score', 0)
                }
            },
            'voice_authenticity': voice_result or {
                'score': None,
                'language': 'unknown',
                'linguistic_patterns': {},
                'issues': []
            },
            'structural_quality': structural_result,
            'recommendations': recommendations
        }
    
    def _analyze_voice_authenticity(
        self,
        text: str,
        author: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Analyze voice authenticity and linguistic patterns.
        
        Uses VoicePostProcessor validation methods.
        """
        # Language detection
        language_check = self.voice_validator.detect_language(text)
        
        # Linguistic pattern detection
        linguistic_patterns = self.voice_validator.detect_linguistic_patterns(
            text, author
        )
        
        # Calculate voice authenticity score (0-100)
        voice_score = self._calculate_voice_score(
            language_check, linguistic_patterns
        )
        
        # Identify issues
        issues = []
        if language_check['language'] != 'english':
            issues.append(f"Non-English content detected: {language_check['language']}")
        
        if linguistic_patterns.get('translation_artifacts'):
            issues.append("Translation artifacts detected")
        
        if linguistic_patterns.get('wrong_nationality_markers'):
            issues.append("Incorrect nationality linguistic patterns")
        
        return {
            'score': voice_score,
            'language': language_check['language'],
            'confidence': language_check.get('confidence', 0),
            'linguistic_patterns': linguistic_patterns,
            'issues': issues
        }
    
    def _analyze_structural_quality(self, text: str) -> Dict[str, Any]:
        """
        Analyze structural quality: sentence variation, rhythm, complexity.
        """
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if len(sentences) < 2:
            return {
                'sentence_variation': 0,
                'rhythm_score': 0,
                'complexity_variation': 0,
                'sentence_count': len(sentences)
            }
        
        # Sentence length variation
        lengths = [len(s.split()) for s in sentences]
        length_stdev = statistics.stdev(lengths) if len(lengths) > 1 else 0
        length_mean = statistics.mean(lengths)
        
        # Coefficient of variation (higher = more variation)
        length_cv = (length_stdev / length_mean) if length_mean > 0 else 0
        
        # Sentence variation score (0-100)
        # Target CV: 0.4-0.6 (40-60% variation is natural)
        sentence_variation = min(100, (length_cv / 0.6) * 100)
        
        # Rhythm score based on pattern diversity
        # Count sentence starter patterns
        starters = [s.split()[0] for s in sentences if s.split()]
        starter_diversity = len(set(starters)) / len(starters) if starters else 0
        rhythm_score = starter_diversity * 100
        
        # Complexity variation (mix of simple and complex sentences)
        # Simple: < 15 words, Medium: 15-25, Complex: > 25
        simple = sum(1 for length in lengths if length < 15)
        medium = sum(1 for length in lengths if 15 <= length <= 25)
        complex_count = sum(1 for length in lengths if length > 25)
        
        # Ideal: mix of all three types
        has_all_types = (simple > 0 and medium > 0 and complex_count > 0)
        complexity_variation = 100 if has_all_types else 50
        
        return {
            'sentence_variation': sentence_variation,
            'rhythm_score': rhythm_score,
            'complexity_variation': complexity_variation,
            'sentence_count': len(sentences),
            'avg_sentence_length': length_mean,
            'sentence_length_stdev': length_stdev
        }
    
    def _calculate_voice_score(
        self,
        language_check: Dict,
        linguistic_patterns: Dict
    ) -> float:
        """Calculate voice authenticity score (0-100)"""
        score = 100.0
        
        # Deduct for wrong language
        if language_check['language'] != 'english':
            score -= 50 * language_check.get('confidence', 0.5)
        
        # Deduct for translation artifacts
        if linguistic_patterns.get('translation_artifacts'):
            artifact_count = len(linguistic_patterns['translation_artifacts'])
            score -= min(30, artifact_count * 10)
        
        # Deduct for wrong nationality markers
        if linguistic_patterns.get('wrong_nationality_markers'):
            marker_count = len(linguistic_patterns['wrong_nationality_markers'])
            score -= min(20, marker_count * 5)
        
        return max(0, score)
    
    def _calculate_overall_score(
        self,
        ai_result: Dict,
        voice_result: Optional[Dict],
        structural_result: Dict
    ) -> float:
        """
        Calculate composite overall quality score (0-100).
        
        Weights:
        - AI Patterns: 40%
        - Voice Authenticity: 30% (if available)
        - Structural Quality: 30%
        """
        # AI score (inverted: 100 - ai_score)
        ai_score = 100 - ai_result['ai_score']
        
        # Voice score (if available)
        voice_score = voice_result['score'] if voice_result else None
        
        # Structural score (average of three metrics)
        structural_score = (
            structural_result['sentence_variation'] +
            structural_result['rhythm_score'] +
            structural_result['complexity_variation']
        ) / 3
        
        # Calculate weighted average
        if voice_score is not None:
            overall = (
                ai_score * 0.40 +
                voice_score * 0.30 +
                structural_score * 0.30
            )
        else:
            # Without voice score, reweight
            overall = (
                ai_score * 0.60 +
                structural_score * 0.40
            )
        
        return round(overall, 1)
    
    def _generate_recommendations(
        self,
        ai_result: Dict,
        voice_result: Optional[Dict],
        structural_result: Dict
    ) -> list:
        """Generate actionable improvement recommendations"""
        recommendations = []
        
        # AI pattern recommendations
        if ai_result['ai_score'] > 60:
            recommendations.append(
                "High AI pattern score detected. Increase sentence variation and reduce formulaic phrasing."
            )
        
        if ai_result.get('repetition_score', 0) > 50:
            recommendations.append(
                "Excessive repetition detected. Use more diverse vocabulary and sentence structures."
            )
        
        # Voice authenticity recommendations
        if voice_result and voice_result['language'] != 'english':
            recommendations.append(
                f"Non-English content detected ({voice_result['language']}). "
                "Ensure all content is written in English."
            )
        
        if voice_result and voice_result.get('issues'):
            for issue in voice_result['issues']:
                recommendations.append(f"Voice issue: {issue}")
        
        # Structural recommendations
        if structural_result['sentence_variation'] < 40:
            recommendations.append(
                "Low sentence variation. Mix short (< 15 words), "
                "medium (15-25 words), and long (> 25 words) sentences."
            )
        
        if structural_result['rhythm_score'] < 50:
            recommendations.append(
                "Repetitive sentence starters detected. Vary how sentences begin."
            )
        
        if structural_result['complexity_variation'] < 80:
            recommendations.append(
                "Limited sentence complexity variation. Include mix of simple, "
                "compound, and complex sentences."
            )
        
        return recommendations
    
    def quick_check(self, text: str) -> Dict[str, Any]:
        """
        Fast quality check with minimal analysis.
        
        Returns:
            {
                'is_acceptable': bool,
                'overall_score': float,
                'primary_issue': str or None
            }
        """
        # Quick AI detection
        ai_result = self.ai_detector.detect_ai_patterns(text)
        
        # Quick structural check
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        lengths = [len(s.split()) for s in sentences]
        
        has_variation = False
        if len(lengths) > 1:
            length_stdev = statistics.stdev(lengths)
            has_variation = length_stdev > 3
        
        # Determine if acceptable
        is_acceptable = (
            ai_result['ai_score'] < 70 and  # Not too AI-like
            has_variation  # Has sentence variation
        )
        
        # Identify primary issue
        primary_issue = None
        if ai_result['ai_score'] >= 70:
            primary_issue = "High AI pattern score"
        elif not has_variation:
            primary_issue = "Insufficient sentence variation"
        
        return {
            'is_acceptable': is_acceptable,
            'overall_score': 100 - ai_result['ai_score'],
            'primary_issue': primary_issue
        }
