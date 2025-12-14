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
from shared.voice.enhanced_ai_detector import EnhancedAIDetector

logger = logging.getLogger(__name__)


class QualityAnalyzer:
    """
    Unified quality analysis combining AI detection and voice compliance.
    
    Consolidates functionality from:
    - AIDetector (ai_detection.py) - AI pattern detection
    - VoicePostProcessor (post_processor.py) - Voice validation methods
    
    Provides single interface for all text quality assessment.
    """
    
    def __init__(self, api_client=None, strict_mode: bool = True, learning_db_path: str = 'z-beam.db'):
        """
        Initialize quality analyzer.
        
        Args:
            api_client: Optional API client (Winston + voice enhancement)
            strict_mode: Use STRICT thresholds for AI detection (DEFAULT: True)
            learning_db_path: Path to learning database for benchmarks
        """
        # PRIORITY 1: Enhanced AI Detection (strict mode DEFAULT TRUE)
        self.enhanced_ai_detector = EnhancedAIDetector(
            winston_client=api_client,  # Winston API for external validation
            strict_mode=strict_mode
        )
        
        # Legacy AI detector (backup only)
        self.ai_detector = AIDetector(strict_mode=strict_mode)
        
        self.strict_mode = strict_mode
        
        # Voice validation requires API client (optional)
        self.voice_validator = VoicePostProcessor(api_client) if api_client else None
        
        # Load patterns for analysis
        self.patterns = load_patterns()
        
        # Learning database for benchmarks
        self.learning_db_path = learning_db_path
        
        logger.info(f"QualityAnalyzer initialized (ENHANCED AI DETECTION, strict_mode={strict_mode})")
    
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
        
        # 0. MINIMUM LENGTH CHECK - Note: AI and voice tests still run, only structural skipped
        MIN_CONTENT_LENGTH = 150  # Minimum chars for meaningful structural analysis
        content_too_short = len(text) < MIN_CONTENT_LENGTH
        
        # 1. ENHANCED AI DETECTION (TOP PRIORITY - ALWAYS RUN)
        enhanced_ai_result = self.enhanced_ai_detector.analyze(text)
        
        # INSTANT REJECTION if enhanced detector flags as AI
        if enhanced_ai_result['is_ai']:
            logger.warning(f"ENHANCED AI DETECTOR: {enhanced_ai_result['recommendation']}")
            # Return early with FAIL grade
            return {
                'overall_score': 0.0,  # INSTANT FAIL
                'ai_patterns': {
                    'score': 0.0,
                    'is_ai_like': True,
                    'issues': enhanced_ai_result['violations'],
                    'details': enhanced_ai_result['scores'],
                    'winston_score': enhanced_ai_result.get('winston_score'),
                    'confidence': enhanced_ai_result['confidence']
                },
                'voice_authenticity': {'score': None, 'language': 'unknown', 'linguistic_patterns': {}, 'issues': []},
                'structural_quality': {'sentence_variation': 0.0, 'rhythm_score': 0.0, 'complexity_variation': 0.0},
                'recommendations': [enhanced_ai_result['recommendation']],
                'enhanced_detection': enhanced_ai_result  # Full details for debugging
            }
        
        # 2. Legacy AI Pattern Detection (secondary validation)
        ai_result = self.ai_detector.detect_ai_patterns(text)
        
        # 3. Voice Authenticity (ALWAYS RUN if author provided, regardless of length)
        # 3. Voice Authenticity (ALWAYS RUN if author provided, regardless of length)
        voice_result = None
        if author and self.voice_validator:
            voice_result = self._analyze_voice_authenticity(text, author)
        
        # 4. Structural Quality (skip if too short)
        if content_too_short:
            structural_result = {
                'sentence_variation': 50.0,  # Baseline for single sentence
                'rhythm_score': 50.0,
                'complexity_variation': 50.0,
                'sentence_count': len([s for s in text.split('.') if s.strip()])
            }
        else:
            structural_result = self._analyze_structural_quality(text)
        
        # 5. Calculate overall score (ENHANCED AI DETECTION WEIGHTED HEAVILY)
        overall_score = self._calculate_overall_score_enhanced(
            enhanced_ai_result, ai_result, voice_result, structural_result
        )
        
        # 6. Generate recommendations
        recommendations = []
        if include_recommendations:
            recommendations = self._generate_recommendations_enhanced(
                enhanced_ai_result, ai_result, voice_result, structural_result
            )
        
        return {
            'overall_score': overall_score,
            'ai_patterns': {
                'score': (1.0 - enhanced_ai_result['confidence']) * 100,  # Invert confidence
                'is_ai_like': enhanced_ai_result['is_ai'],
                'issues': enhanced_ai_result['violations'],
                'details': enhanced_ai_result['scores'],
                'winston_score': enhanced_ai_result.get('winston_score'),
                'confidence': enhanced_ai_result['confidence'],
                'legacy_detection': {
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
            'recommendations': recommendations,
            'enhanced_detection': enhanced_ai_result  # Full enhanced detection details
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
        
        # Single-sentence content (like material_description) gets baseline score
        # Don't penalize appropriately concise content for lack of variation
        if len(sentences) < 2:
            return {
                'sentence_variation': 50,  # Neutral baseline (can't vary single sentence)
                'rhythm_score': 50,         # Neutral baseline (can't have rhythm with one sentence)
                'complexity_variation': 50, # Neutral baseline (can't mix complexity types)
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
    
    def analyze_technical_accuracy(
        self,
        text: str,
        item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze technical accuracy and specificity of content.
        
        Checks if content accurately reflects the material/item properties
        and uses specific technical language rather than generic descriptions.
        
        Args:
            text: Content to analyze
            item_data: Material/item data dict with category, properties, etc.
            
        Returns:
            {
                'score': float (0-100),
                'checks': Dict of individual check results,
                'issues': List of problems found
            }
        """
        text_lower = text.lower()
        words = text.split()
        
        checks = {}
        issues = []
        
        # Check 1: Mentions category
        category = item_data.get('category', '').lower()
        if category:
            checks['mentions_category'] = category in text_lower
            if not checks['mentions_category']:
                issues.append(f"Does not mention category '{category}'")
        
        # Check 2: Mentions key technical properties
        property_keywords = ['thermal', 'density', 'hardness', 'reflectivity', 'conductivity', 
                            'strength', 'temperature', 'resistance', 'absorption', 'wavelength']
        mentions_properties = any(prop in text_lower for prop in property_keywords)
        checks['mentions_key_property'] = mentions_properties
        if not mentions_properties:
            issues.append("Lacks specific technical property mentions")
        
        # Check 3: Specific vs generic language (ratio of long technical words)
        long_words = [w for w in words if len(w) > 8]
        specificity_ratio = len(long_words) / len(words) if words else 0
        checks['specific_vs_generic'] = specificity_ratio > 0.15
        if specificity_ratio <= 0.15:
            issues.append(f"Too generic - only {specificity_ratio:.1%} technical terms")
        
        # Check 4: Technical precision (avoid vague qualifiers)
        vague_terms = ['very', 'quite', 'somewhat', 'fairly', 'relatively', 'rather']
        vague_count = sum(1 for term in vague_terms if term in text_lower)
        checks['technical_precision'] = vague_count == 0
        if vague_count > 0:
            issues.append(f"Contains {vague_count} vague qualifier(s)")
        
        # Check 5: Quantitative data (numbers, units, specific values)
        has_numbers = bool(re.search(r'\d+', text))
        checks['includes_quantitative_data'] = has_numbers
        if not has_numbers:
            issues.append("No quantitative data (numbers, measurements)")
        
        # Calculate overall technical accuracy score
        score = (sum(checks.values()) / len(checks)) * 100 if checks else 0
        
        return {
            'score': score,
            'checks': checks,
            'issues': issues
        }
    
    def get_category_benchmark(self, category: str, domain: str = 'materials') -> Optional[float]:
        """
        Get 90th percentile quality score for category from learning database.
        
        Args:
            category: Material/item category
            domain: Domain name (materials, contaminants, settings)
            
        Returns:
            Float score (0-100) or None if insufficient data
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            # Query for quality scores in this category
            cursor.execute('''
                SELECT overall_score FROM quality_evaluations
                WHERE category = ? AND domain = ?
                ORDER BY overall_score DESC
            ''', (category, domain))
            
            scores = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if len(scores) < 10:  # Need at least 10 samples
                return None
            
            # Calculate 90th percentile
            scores.sort()
            index = int(len(scores) * 0.9)
            return scores[index]
            
        except Exception as e:
            logger.warning(f"Could not get category benchmark: {e}")
            return None
    
    def analyze_consistency_with_category(
        self,
        text: str,
        category: str,
        domain: str = 'materials'
    ) -> Dict[str, Any]:
        """
        Analyze if content style is consistent with other items in same category.
        
        Extracts style features and compares against category norms.
        
        Args:
            text: Content to analyze
            category: Material/item category
            domain: Domain name
            
        Returns:
            {
                'consistency_score': float (0-100),
                'style_features': Dict,
                'deviations': List[str]
            }
        """
        # Extract style features from this text
        features = self._extract_style_features(text)
        
        # Get category average features from database
        category_features = self._get_category_style_features(category, domain)
        
        if not category_features:
            return {
                'consistency_score': None,
                'style_features': features,
                'deviations': ['Insufficient category data for comparison']
            }
        
        # Compare features
        deviations = []
        feature_scores = []
        
        # Average sentence length deviation
        if 'avg_sentence_length' in category_features:
            deviation = abs(features['avg_sentence_length'] - category_features['avg_sentence_length'])
            deviation_pct = deviation / category_features['avg_sentence_length']
            feature_scores.append(100 - min(100, deviation_pct * 100))
            if deviation_pct > 0.3:  # More than 30% different
                deviations.append(f"Sentence length deviates {deviation_pct:.0%} from category norm")
        
        # Formality level deviation
        if 'formality_level' in category_features:
            deviation = abs(features['formality_level'] - category_features['formality_level'])
            feature_scores.append(100 - min(100, deviation * 50))
            if deviation > 0.4:
                deviations.append(f"Formality level inconsistent with category")
        
        # Technical density deviation
        if 'technical_density' in category_features:
            deviation = abs(features['technical_density'] - category_features['technical_density'])
            feature_scores.append(100 - min(100, deviation * 100))
            if deviation > 0.2:
                deviations.append(f"Technical density deviates from category norm")
        
        consistency_score = sum(feature_scores) / len(feature_scores) if feature_scores else 50
        
        return {
            'consistency_score': consistency_score,
            'style_features': features,
            'category_features': category_features,
            'deviations': deviations
        }
    
    def _extract_style_features(self, text: str) -> Dict[str, float]:
        """Extract stylistic features from text for comparison"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = text.split()
        
        # Average sentence length
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Formality level (ratio of long words)
        long_words = [w for w in words if len(w) > 7]
        formality_level = len(long_words) / len(words) if words else 0
        
        # Technical density (technical terms per sentence)
        technical_terms = sum(1 for w in words if len(w) > 8)
        technical_density = technical_terms / len(sentences) if sentences else 0
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'formality_level': formality_level,
            'technical_density': technical_density
        }
    
    def _get_category_style_features(self, category: str, domain: str) -> Optional[Dict[str, float]]:
        """Get average style features for category from database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT avg_sentence_length, formality_level, technical_density
                FROM category_style_norms
                WHERE category = ? AND domain = ?
            ''', (category, domain))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'avg_sentence_length': row[0],
                    'formality_level': row[1],
                    'technical_density': row[2]
                }
            return None
            
        except Exception as e:
            logger.debug(f"Category style features not available: {e}")
            return None
    
    def _calculate_overall_score_enhanced(
        self,
        enhanced_ai_result: Dict,
        ai_result: Dict,
        voice_result: Optional[Dict],
        structural_result: Dict
    ) -> float:
        """
        Calculate composite score with ENHANCED AI DETECTION weighted heavily.
        
        Weights (STRICT MODE):
        - Enhanced AI Detection: 50% (TOP PRIORITY)
        - Voice Authenticity: 25% (if available)
        - Structural Quality: 15%
        - Legacy AI Detection: 10%
        """
        # Enhanced AI confidence (inverted: 0 = AI, 1 = human)
        enhanced_ai_score = (1.0 - enhanced_ai_result['confidence']) * 100
        
        # Legacy AI score (inverted: 100 - ai_score)
        legacy_ai_score = 100 - ai_result['ai_score']
        
        # Voice score (if available)
        voice_score = voice_result['score'] if voice_result else None
        
        # Structural score (average of three metrics)
        structural_score = (
            structural_result['sentence_variation'] +
            structural_result['rhythm_score'] +
            structural_result['complexity_variation']
        ) / 3
        
        # Calculate weighted average with ENHANCED AI weighted heavily
        if voice_score is not None:
            overall = (
                enhanced_ai_score * 0.50 +    # TOP PRIORITY
                voice_score * 0.25 +
                structural_score * 0.15 +
                legacy_ai_score * 0.10
            )
        else:
            # Without voice score, reweight (enhanced AI still 50%)
            overall = (
                enhanced_ai_score * 0.50 +    # TOP PRIORITY
                structural_score * 0.30 +
                legacy_ai_score * 0.20
            )
        
        return round(overall, 1)
    
    def _generate_recommendations_enhanced(
        self,
        enhanced_ai_result: Dict,
        ai_result: Dict,
        voice_result: Optional[Dict],
        structural_result: Dict
    ) -> list:
        """Generate recommendations with enhanced AI detection insights"""
        recommendations = []
        
        # Enhanced AI violations (TOP PRIORITY)
        for violation in enhanced_ai_result['violations']:
            recommendations.append(f"🚨 CRITICAL: {violation}")
        
        # Detailed enhanced AI issues
        if enhanced_ai_result['details']['telltale_count'] > 0:
            recommendations.append(
                "Remove AI telltale phrases. These are instant rejection markers."
            )
        
        for issue in enhanced_ai_result['details']['structural_issues']:
            recommendations.append(f"Structural: {issue}")
        
        for issue in enhanced_ai_result['details']['statistical_issues']:
            recommendations.append(f"Statistical: {issue}")
        
        for issue in enhanced_ai_result['details']['linguistic_issues']:
            recommendations.append(f"Linguistic: {issue}")
        
        # Legacy AI pattern recommendations
        if ai_result['ai_score'] > 60:
            recommendations.append(
                "Legacy detection: High AI pattern score. Reduce formulaic phrasing."
            )
        
        # Voice authenticity recommendations
        if voice_result and voice_result['language'] != 'english':
            recommendations.append(
                f"Voice: Non-English content detected ({voice_result['language']})"
            )
        
        # Structural recommendations
        if structural_result['sentence_variation'] < 40:
            recommendations.append(
                "Structural: Low sentence variation. Vary sentence lengths more."
            )
        
        return recommendations


