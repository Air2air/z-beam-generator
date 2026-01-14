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

import logging
import re
import statistics
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# Import existing detection modules
from shared.voice.ai_detection import AIDetector, load_patterns
from shared.voice.enhanced_ai_detector import EnhancedAIDetector
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
    
    def __init__(
        self, 
        api_client=None, 
        strict_mode: bool = True, 
        learning_db_path: str = 'z-beam.db',
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize quality analyzer.
        
        Args:
            api_client: Optional API client (Winston + voice enhancement)
            strict_mode: Use STRICT thresholds for AI detection (DEFAULT: True)
            learning_db_path: Path to learning database for benchmarks
            weights: Optional learned weights for quality scoring (winston, subjective, readability)
        """
        # PRIORITY 1: Enhanced AI Detection (strict mode DEFAULT TRUE)
        self.enhanced_ai_detector = EnhancedAIDetector(
            winston_client=api_client,  # Winston API for external validation
            strict_mode=strict_mode
        )
        
        # Legacy AI detector (backup only)
        self.ai_detector = AIDetector(strict_mode=strict_mode)
        
        self.strict_mode = strict_mode
        
        # Store learned weights (if provided)
        self.learned_weights = weights
        if weights:
            logger.info(f"Using learned weights: {weights}")
        
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
        include_recommendations: bool = True,
        component_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive quality analysis of text.
        
        Args:
            text: Text content to analyze
            author: Optional author dict with 'name' and 'country' keys
            include_recommendations: Include improvement recommendations
            component_type: Optional component type for context-aware validation
                          (instructional components allow direct address)
            
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
        
        # MODERATE REJECTION THRESHOLD - Allow for improvement
        if enhanced_ai_result['is_ai'] and enhanced_ai_result['confidence'] > 0.8:
            logger.warning(f"ENHANCED AI DETECTOR (HIGH CONFIDENCE): {enhanced_ai_result['recommendation']}")
            # Return early with FAIL grade only for high confidence AI detection
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
        elif enhanced_ai_result['is_ai']:
            # Low confidence AI detection - allow to proceed but note issue
            logger.info(f"ENHANCED AI DETECTOR (LOW CONFIDENCE): {enhanced_ai_result['recommendation']}")
        
        # 2. Legacy AI Pattern Detection (secondary validation)
        ai_result = self.ai_detector.detect_ai_patterns(text)
        
        # 3. Voice Authenticity (ALWAYS RUN if author provided, regardless of length)
        voice_result = None
        if author and self.voice_validator:
            voice_result = self._analyze_voice_authenticity(text, author, component_type)
        
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
            'overall_score': abs(overall_score),  # Ensure non-negative
            'ai_patterns': {
                'score': abs((1.0 - enhanced_ai_result['confidence'])),  # Invert confidence (0-1 range)
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
        author: Dict[str, str],
        component_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze voice authenticity and linguistic patterns.
        
        Uses VoicePostProcessor validation methods + pattern compliance check.
        Also checks for forbidden phrases that indicate AI generation.
        
        Args:
            text: Content to analyze
            author: Author metadata (name, country, id)
            component_type: Optional component type for context-aware validation
                           (instructional components allow direct address)
        """
        # Check for forbidden phrases FIRST (instant rejection)
        # BUT: Skip direct_address check for instructional components
        forbidden_check = self._check_forbidden_phrases(text, author, component_type)
        if forbidden_check['has_forbidden']:
            return {
                'score': 0.0,  # INSTANT FAIL for forbidden phrases
                'language': 'english',
                'linguistic_patterns': {},
                'pattern_compliance': {'authentic': False, 'found_patterns': [], 'found_count': 0},
                'forbidden_violations': forbidden_check['violations'],
                'issues': [f"FORBIDDEN: {v}" for v in forbidden_check['violations']]
            }
        
        # Language detection
        language_check = self.voice_validator.detect_language(text)
        
        # Linguistic pattern detection
        linguistic_patterns = self.voice_validator.detect_linguistic_patterns(
            text, author
        )
        
        # NEW: Check for author-specific pattern compliance
        pattern_compliance = self._check_pattern_compliance(text, author)
        
        # Calculate voice authenticity score (0-100)
        voice_score = self._calculate_voice_score(
            language_check, linguistic_patterns, pattern_compliance
        )
        
        # Identify issues (LENIENT: only fail on high-confidence non-English)
        issues = []
        # Only fail if both:
        # 1. Language is definitely not English (not 'english' or 'unknown')
        # 2. Confidence is high (> 0.7)
        # This avoids false positives from technical terminology
        if (language_check['language'] not in ['english', 'unknown', 'unknown_non_english'] 
            and language_check.get('confidence', 0) > 0.7):
            issues.append(f"Non-English content detected: {language_check['language']}")
        
        if linguistic_patterns.get('translation_artifacts'):
            issues.append("Translation artifacts detected")
        
        if linguistic_patterns.get('wrong_nationality_markers'):
            issues.append("Incorrect nationality linguistic patterns")
        
        # NEW: Add pattern compliance issues
        if pattern_compliance['found_count'] < 2:
            issues.append(
                f"Missing author-specific patterns: found {pattern_compliance['found_count']}/2 required "
                f"({', '.join(pattern_compliance['found_patterns']) if pattern_compliance['found_patterns'] else 'none'})"
            )
        
        return {
            'score': voice_score,
            'language': language_check['language'],
            'confidence': language_check.get('confidence', 0),
            'linguistic_patterns': linguistic_patterns,
            'pattern_compliance': pattern_compliance,
            'issues': issues
        }
    
    def _check_forbidden_phrases(
        self, 
        text: str, 
        author: Dict[str, str],
        component_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check for forbidden phrases in persona files.
        These are instant rejection markers (theatrical, abstract, direct address).
        
        Context-aware: Instructional components (section_description, prevention)
        are allowed to use direct address ("you", "your") for technical instruction.
        Formal components (description, caption) maintain strict formality.
        
        Args:
            text: Content to check
            author: Author metadata
            component_type: Optional component type (not used, kept for compatibility)
        
        Returns:
            {
                'has_forbidden': bool,
                'violations': [list of found forbidden phrases]
            }
        """
        violations = []
        text_lower = text.lower()
        country = author.get('country', '').lower().replace(' ', '_')
        
        # Load persona file for this author
        persona_path = Path(__file__).parent / 'profiles' / f'{country}.yaml'
        if not persona_path.exists():
            return {'has_forbidden': False, 'violations': []}
        
        try:
            with open(persona_path, 'r') as f:
                persona = yaml.safe_load(f)
                forbidden = persona.get('forbidden', {})
                
                # Check forbidden categories but SKIP direct_address (allow "we", "you", etc.)
                for category, phrases in forbidden.items():
                    # Skip direct_address blocking (user requested this)
                    if category == 'direct_address':
                        continue
                        
                    for phrase in phrases:
                        if phrase.lower() in text_lower:
                            violations.append(f"{category}: '{phrase}'")
        except Exception as e:
            logger.warning(f"Error loading forbidden phrases from {persona_path}: {e}")
            return {'has_forbidden': False, 'violations': []}
        
        return {
            'has_forbidden': len(violations) > 0,
            'violations': violations
        }
    
    def _check_pattern_compliance(self, text: str, author: Dict[str, str]) -> Dict[str, Any]:
        """
        Check if text uses author-specific linguistic patterns.
        
        Validates that the author's voice instructions were actually followed.
        Returns dict with found patterns and compliance score.
        """
        country = author.get('country', '').lower()
        author_id = author.get('id', 0)
        
        # Define author-specific patterns to check
        # Based on persona files: taiwan.yaml, italy.yaml, indonesia.yaml, united_states.yaml
        patterns = {
            'united states': {
                'phrasal_verbs': [
                    r'\bline up\b', r'\bdial in\b', r'\brun through\b', r'\bwork out\b',
                    r'\bramp up\b', r'\bset up\b', r'\bwrap up\b', r'\bhold up\b',
                    r'\bback up\b', r'\bcut down\b', r'\bturns out\b'
                ],
                'quantified_outcomes': [r'\d+%', r'by \d+%', r'\d+% (over|under|better|faster)'],
                'practical_transitions': [
                    r'\bturns out\b', r'\bin practice\b', r'\boverall\b', 
                    r'\bthe key point\b', r'\bin the field\b'
                ],
            },
            'taiwan': {
                'topic_comment': [r'\w+, it \w+', r'\w+ of \w+, it \w+'],
                'article_omission': [
                    r'\b(Process|Surface|Method|Treatment|Control|Layer|System) (yields|shows|exhibits|demonstrates|holds)\b'
                ],
                'temporal_markers': [
                    r'\bAfter (treatment|adjustment|process|cleaning)\b',
                    r'\bFollowing \w+\b',
                    r'\b(already|still|just) \w+\b'
                ],
            },
            'italy': {
                'cleft_structures': [r'\w+, it (persists|resists|adheres|leads|demonstrates|manifests)'],
                'subjunctive_hedging': [r'\bIt seems that\b', r'\bIt appears\b', r'\bIt would seem\b'],
                'romance_cognates': [
                    r'\btenaciously\b', r'\bmanifests\b', r'\bpersists\b', r'\bexhibits\b',
                    r'\bdemonstrates\b', r'\bdependent from\b', r'\binfluenced from\b'
                ],
            },
            'indonesia': {
                'reduplication': [r'\b(\w+)-\1\b'],  # Partial reduplication patterns
                'aspectual_markers': [r'\balready\b', r'\bstill\b', r'\bjust now\b', r'\blater on\b'],
                'topic_prominence': [r'\w+, (it|this|that) \w+'],
            }
        }
        
        # Get patterns for this author's country
        author_patterns = patterns.get(country, {})
        
        if not author_patterns:
            # Unknown country - can't validate patterns
            return {
                'country': country,
                'found_patterns': [],
                'found_count': 0,
                'total_patterns': 0,
                'authentic': False,
                'note': f'No pattern definitions for country: {country}'
            }
        
        # Check which patterns are present
        found_patterns = []
        for pattern_type, pattern_list in author_patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text, re.IGNORECASE):
                    found_patterns.append(f"{pattern_type}: {pattern}")
                    break  # Count each pattern_type only once
        
        # Calculate compliance
        total_pattern_types = len(author_patterns)
        found_count = len(found_patterns)
        
        # Require at least 2 pattern types present for authenticity
        authentic = found_count >= 2
        
        return {
            'country': country,
            'found_patterns': found_patterns,
            'found_count': found_count,
            'total_patterns': total_pattern_types,
            'authentic': authentic,
            'score': (found_count / total_pattern_types * 100) if total_pattern_types > 0 else 0
        }
    
    def _calculate_voice_score(
        self,
        language_check: Dict,
        linguistic_patterns: Dict,
        pattern_compliance: Dict
    ) -> float:
        """
        Calculate voice authenticity score (0-100).
        
        Now includes pattern compliance in calculation.
        """
        score = 100.0
        
        # Deduct for non-English (but only if high confidence)
        if (language_check['language'] not in ['english', 'unknown', 'unknown_non_english']
            and language_check.get('confidence', 0) > 0.7):
            score -= 50
        
        # Deduct for translation artifacts
        if linguistic_patterns.get('translation_artifacts'):
            score -= 20
        
        # Deduct for wrong nationality markers
        if linguistic_patterns.get('wrong_nationality_markers'):
            score -= 15
        
        # NEW: Deduct for missing author-specific patterns
        if not pattern_compliance['authentic']:
            deduction = (2 - pattern_compliance['found_count']) * 15  # 15 points per missing pattern
            score -= deduction
        
        return max(0, score)
    
    def _analyze_structural_quality(self, text: str) -> Dict[str, Any]:
        """
        Analyze structural quality: sentence variation, rhythm, complexity.
        """
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Single-sentence content (like description) gets baseline score
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
        
        INSTANT REJECTION:
        - Forbidden phrases detected → 0 score (forces regeneration)
        """
        # Check for forbidden phrases - INSTANT FAIL
        if voice_result and 'forbidden_violations' in voice_result and voice_result['forbidden_violations']:
            logger.warning(f"🚨 FORBIDDEN PHRASES DETECTED - Score set to 0")
            for violation in voice_result['forbidden_violations']:
                logger.warning(f"   • {violation}")
            return 0.0  # INSTANT FAIL - will trigger regeneration
        
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
        
        # Forbidden phrase violations (CRITICAL)
        if voice_result and 'forbidden_violations' in voice_result and voice_result['forbidden_violations']:
            recommendations.append("🚨 FORBIDDEN PHRASES DETECTED - Content must be regenerated:")
            for violation in voice_result['forbidden_violations']:
                recommendations.append(f"   • {violation}")
        
        # Structural recommendations
        if structural_result['sentence_variation'] < 40:
            recommendations.append(
                "Structural: Low sentence variation. Vary sentence lengths more."
            )
        
        return recommendations


