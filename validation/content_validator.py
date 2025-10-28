#!/usr/bin/env python3
"""
Centralized Content Validation Service

Unified validation system for all generated content with multi-dimensional scoring:
- Author voice authenticity and consistency
- Content variation and naturalness  
- Human writing characteristics
- AI detection avoidance

Consolidates and normalizes:
- utils/validation/quality_validator.py (persona thresholds, circuit breakers)
- validation/services/post_generation_service.py (quality scoring)
- scripts/tools/quality_analyzer.py (advanced quality metrics)
- Scattered validation logic across components

STRICT FAIL-FAST ARCHITECTURE - ZERO TOLERANCE for mocks/fallbacks
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AuthorVoiceScore:
    """Author voice authenticity scoring"""
    overall_score: float  # 0-100
    linguistic_match: float  # Linguistic characteristics match
    phrase_authenticity: float  # Signature phrases usage
    tone_consistency: float  # Tone and style consistency
    technical_balance: float  # Technical vs conversational balance
    issues: List[str] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """Check if score meets minimum threshold"""
        return self.overall_score >= 70.0


@dataclass
class VariationScore:
    """Content variation and naturalness scoring"""
    overall_score: float  # 0-100
    length_variation: float  # Word count variation across items
    structure_variation: float  # Sentence/paragraph structure variety
    vocabulary_diversity: float  # Lexical diversity
    pattern_avoidance: float  # Avoids repetitive patterns
    issues: List[str] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """Check if variation meets minimum threshold"""
        return self.overall_score >= 65.0


@dataclass
class HumanCharacteristicsScore:
    """Human writing characteristics scoring"""
    overall_score: float  # 0-100
    imperfection_score: float  # Natural imperfections (not errors)
    flow_naturalness: float  # Natural flow and transitions
    personality_presence: float  # Author personality evident
    spontaneity_score: float  # Spontaneous, not formulaic
    issues: List[str] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """Check if human characteristics meet threshold"""
        return self.overall_score >= 60.0


@dataclass
class AIDetectionAvoidanceScore:
    """AI detection avoidance scoring"""
    overall_score: float  # 0-100 (higher = more human-like)
    pattern_breaking: float  # Breaks AI-typical patterns
    unpredictability: float  # Unpredictable elements
    contextual_depth: float  # Deep contextual understanding
    authenticity: float  # Genuine human touch
    issues: List[str] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """Check if AI avoidance meets threshold"""
        return self.overall_score >= 70.0


@dataclass
class ContentValidationResult:
    """Comprehensive validation result for generated content"""
    success: bool
    component_type: str  # 'faq', 'caption', 'subtitle'
    material_name: str
    author_name: str
    author_country: str
    
    # Multi-dimensional scores
    author_voice: AuthorVoiceScore
    variation: VariationScore
    human_characteristics: HumanCharacteristicsScore
    ai_avoidance: AIDetectionAvoidanceScore
    
    # Overall metrics
    overall_score: float  # 0-100 weighted average
    grade: str  # A, B, C, D, F
    
    # Issues and recommendations
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def all_passed(self) -> bool:
        """Check if all dimension scores passed"""
        return (
            self.author_voice.passed and
            self.variation.passed and
            self.human_characteristics.passed and
            self.ai_avoidance.passed
        )


# ============================================================================
# PERSONA THRESHOLDS (from quality_validator.py)
# ============================================================================

PERSONA_THRESHOLDS = {
    "Taiwan": {"min_score": 70, "target_score": 80, "precision_weight": 1.2},
    "Italy": {"min_score": 75, "target_score": 85, "expressiveness_weight": 1.3},
    "Indonesia": {"min_score": 65, "target_score": 75, "accessibility_weight": 1.1},
    "United States": {"min_score": 72, "target_score": 82, "innovation_weight": 1.2},
    "United States (California)": {"min_score": 72, "target_score": 82, "innovation_weight": 1.2},
}


# ============================================================================
# CENTRALIZED CONTENT VALIDATION SERVICE
# ============================================================================

class ContentValidationService:
    """
    Centralized validation service for all generated content.
    
    Provides unified, multi-dimensional validation with:
    - Author voice authenticity scoring
    - Content variation analysis
    - Human characteristic detection
    - AI detection avoidance validation
    
    Replaces scattered validation logic and normalizes across components.
    """
    
    def __init__(self):
        """Initialize content validation service"""
        logger.info("✅ ContentValidationService initialized")
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    def validate_content(
        self,
        content: Dict[str, Any],
        component_type: str,
        material_name: str,
        author_name: str,
        author_country: str,
        voice_profile: Optional[Dict[str, Any]] = None
    ) -> ContentValidationResult:
        """
        Validate generated content with multi-dimensional scoring.
        
        Args:
            content: Generated content (structure varies by component)
            component_type: 'faq', 'caption', 'subtitle'
            material_name: Material name for context
            author_name: Author name
            author_country: Author country
            voice_profile: Optional voice profile for enhanced validation
            
        Returns:
            ContentValidationResult with all dimension scores
        """
        logger.info(f"🔍 Validating {component_type} for {material_name} ({author_name} - {author_country})")
        
        # Extract text from content based on component type
        texts = self._extract_texts(content, component_type)
        
        if not texts:
            return self._create_failure_result(
                component_type, material_name, author_name, author_country,
                "No text content found to validate"
            )
        
        # Score each dimension
        author_voice_score = self._score_author_voice(texts, author_country, voice_profile)
        variation_score = self._score_variation(texts, component_type)
        human_score = self._score_human_characteristics(texts)
        ai_avoidance_score = self._score_ai_avoidance(texts, author_country)
        
        # Calculate weighted overall score
        overall_score = self._calculate_overall_score(
            author_voice_score, variation_score, human_score, ai_avoidance_score
        )
        
        # Determine grade
        grade = self._score_to_grade(overall_score)
        
        # Collect issues and recommendations
        critical_issues, warnings, recommendations = self._collect_feedback(
            author_voice_score, variation_score, human_score, ai_avoidance_score,
            author_country
        )
        
        # Check success
        success = overall_score >= PERSONA_THRESHOLDS.get(author_country, {}).get('min_score', 70)
        
        return ContentValidationResult(
            success=success,
            component_type=component_type,
            material_name=material_name,
            author_name=author_name,
            author_country=author_country,
            author_voice=author_voice_score,
            variation=variation_score,
            human_characteristics=human_score,
            ai_avoidance=ai_avoidance_score,
            overall_score=overall_score,
            grade=grade,
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations
        )
    
    # ========================================================================
    # TEXT EXTRACTION
    # ========================================================================
    
    def _extract_texts(self, content: Dict[str, Any], component_type: str) -> List[str]:
        """Extract text strings from content based on component type"""
        texts = []
        
        if component_type == 'faq':
            # FAQ: extract questions and answers
            questions = content.get('questions', [])
            for q in questions:
                if isinstance(q, dict):
                    texts.append(q.get('question', ''))
                    texts.append(q.get('answer', ''))
        
        elif component_type == 'caption':
            # Caption: extract beforeText and afterText
            texts.append(content.get('beforeText', ''))
            texts.append(content.get('afterText', ''))
        
        elif component_type == 'subtitle':
            # Subtitle: single text string
            if isinstance(content, str):
                texts.append(content)
            else:
                texts.append(content.get('subtitle', ''))
        
        # Filter out empty strings
        return [t.strip() for t in texts if t and t.strip()]
    
    # ========================================================================
    # AUTHOR VOICE SCORING
    # ========================================================================
    
    def _score_author_voice(
        self,
        texts: List[str],
        author_country: str,
        voice_profile: Optional[Dict[str, Any]]
    ) -> AuthorVoiceScore:
        """Score author voice authenticity"""
        issues = []
        
        # 1. Linguistic characteristics match (40%)
        linguistic_score = self._check_linguistic_characteristics(texts, author_country, voice_profile)
        
        # 2. Signature phrases usage (20%)
        phrase_score = self._check_signature_phrases(texts, author_country, voice_profile)
        
        # 3. Tone consistency (25%)
        tone_score = self._check_tone_consistency(texts, author_country)
        
        # 4. Technical balance (15%)
        technical_score = self._check_technical_balance(texts, author_country)
        
        # Calculate weighted overall score
        overall = (
            linguistic_score * 0.40 +
            phrase_score * 0.20 +
            tone_score * 0.25 +
            technical_score * 0.15
        )
        
        # Collect issues
        if linguistic_score < 70:
            issues.append(f"Linguistic characteristics weak (score: {linguistic_score:.1f})")
        if phrase_score < 60:
            issues.append(f"Signature phrases underutilized (score: {phrase_score:.1f})")
        if tone_score < 70:
            issues.append(f"Tone inconsistency detected (score: {tone_score:.1f})")
        
        return AuthorVoiceScore(
            overall_score=overall,
            linguistic_match=linguistic_score,
            phrase_authenticity=phrase_score,
            tone_consistency=tone_score,
            technical_balance=technical_score,
            issues=issues
        )
    
    def _check_linguistic_characteristics(
        self,
        texts: List[str],
        author_country: str,
        voice_profile: Optional[Dict]
    ) -> float:
        """Check linguistic characteristics match author's country"""
        score = 75.0  # Base score
        
        if not voice_profile:
            return score
        
        linguistic = voice_profile.get('linguistic_characteristics', {})
        
        # Check sentence length patterns
        avg_sentence_length = self._calculate_avg_sentence_length(texts)
        
        # Country-specific expectations
        if author_country == "Taiwan":
            # Taiwanese: shorter, precise sentences
            if 10 <= avg_sentence_length <= 18:
                score += 15
            elif avg_sentence_length > 22:
                score -= 10
        
        elif author_country == "Italy":
            # Italian: longer, flowing sentences
            if 18 <= avg_sentence_length <= 28:
                score += 15
            elif avg_sentence_length < 14:
                score -= 10
        
        elif author_country == "Indonesia":
            # Indonesian: moderate, balanced
            if 14 <= avg_sentence_length <= 22:
                score += 15
        
        elif "United States" in author_country:
            # American: varied, conversational
            if 12 <= avg_sentence_length <= 20:
                score += 15
        
        return min(100.0, max(0.0, score))
    
    def _check_signature_phrases(
        self,
        texts: List[str],
        author_country: str,
        voice_profile: Optional[Dict]
    ) -> float:
        """Check for signature phrase usage"""
        if not voice_profile:
            return 70.0
        
        signature_phrases = voice_profile.get('signature_phrases', {})
        if not signature_phrases:
            return 70.0
        
        # Count phrase usage
        full_text = ' '.join(texts).lower()
        phrases_found = 0
        total_phrases = 0
        
        for category, phrases in signature_phrases.items():
            if isinstance(phrases, list):
                total_phrases += len(phrases)
                for phrase in phrases:
                    if phrase.lower() in full_text:
                        phrases_found += 1
        
        if total_phrases == 0:
            return 70.0
        
        # Score based on usage percentage
        usage_percent = (phrases_found / total_phrases) * 100
        
        # Don't penalize too heavily - phrases are guidance, not requirements
        if usage_percent >= 15:
            return 90.0
        elif usage_percent >= 10:
            return 80.0
        elif usage_percent >= 5:
            return 70.0
        else:
            return 60.0
    
    def _check_tone_consistency(self, texts: List[str], author_country: str) -> float:
        """Check tone consistency across texts"""
        if len(texts) < 2:
            return 85.0  # Single text, assume consistent
        
        # Analyze tone markers in each text
        tones = [self._analyze_tone(text) for text in texts]
        
        # Calculate consistency (variance in tone scores)
        if not tones:
            return 70.0
        
        avg_formality = sum(t['formality'] for t in tones) / len(tones)
        avg_technicality = sum(t['technicality'] for t in tones) / len(tones)
        
        # Check variance
        formality_variance = sum(abs(t['formality'] - avg_formality) for t in tones) / len(tones)
        technical_variance = sum(abs(t['technicality'] - avg_technicality) for t in tones) / len(tones)
        
        # Lower variance = higher consistency = higher score
        consistency_score = 100 - (formality_variance * 2 + technical_variance * 2)
        
        return min(100.0, max(50.0, consistency_score))
    
    def _analyze_tone(self, text: str) -> Dict[str, float]:
        """Analyze tone of a single text"""
        # Simple heuristic-based tone analysis
        words = text.lower().split()
        
        # Formality indicators
        formal_words = ['therefore', 'consequently', 'furthermore', 'moreover', 'thus']
        informal_words = ["let's", "you'll", "we'll", "can't", "don't"]
        
        formal_count = sum(1 for w in words if any(fw in w for fw in formal_words))
        informal_count = sum(1 for w in words if any(iw in w for iw in informal_words))
        
        formality = (formal_count / max(len(words), 1)) * 100
        
        # Technical indicators
        technical_terms = ['precision', 'parameter', 'specification', 'wavelength', 'ablation']
        technical_count = sum(1 for w in words if any(tt in w for tt in technical_terms))
        
        technicality = (technical_count / max(len(words), 1)) * 100
        
        return {
            'formality': min(100, formality * 10),
            'technicality': min(100, technicality * 10)
        }
    
    def _check_technical_balance(self, texts: List[str], author_country: str) -> float:
        """Check technical vs conversational balance"""
        full_text = ' '.join(texts)
        words = full_text.lower().split()
        
        # Technical term density
        technical_terms = [
            'laser', 'wavelength', 'ablation', 'precision', 'parameter',
            'substrate', 'oxide', 'coating', 'contaminant', 'reflectivity'
        ]
        
        technical_count = sum(1 for w in words if any(tt in w for tt in technical_terms))
        technical_density = (technical_count / max(len(words), 1)) * 100
        
        # Country-specific expectations
        if author_country == "Taiwan":
            # Higher technical density expected
            if 3 <= technical_density <= 8:
                return 90.0
            elif technical_density < 2:
                return 60.0
        
        elif author_country == "Italy":
            # More balanced, expressive
            if 2 <= technical_density <= 6:
                return 90.0
        
        # Default scoring
        if 2 <= technical_density <= 7:
            return 85.0
        elif technical_density > 10:
            return 70.0  # Too technical
        elif technical_density < 1:
            return 65.0  # Too conversational
        else:
            return 75.0
    
    # ========================================================================
    # VARIATION SCORING
    # ========================================================================
    
    def _score_variation(self, texts: List[str], component_type: str) -> VariationScore:
        """Score content variation and naturalness"""
        issues = []
        
        # 1. Length variation (30%)
        length_score = self._check_length_variation(texts, component_type)
        
        # 2. Structure variation (30%)
        structure_score = self._check_structure_variation(texts)
        
        # 3. Vocabulary diversity (25%)
        vocab_score = self._check_vocabulary_diversity(texts)
        
        # 4. Pattern avoidance (15%)
        pattern_score = self._check_pattern_avoidance(texts)
        
        # Calculate weighted overall score
        overall = (
            length_score * 0.30 +
            structure_score * 0.30 +
            vocab_score * 0.25 +
            pattern_score * 0.15
        )
        
        # Collect issues
        if length_score < 60:
            issues.append(f"Length variation insufficient (score: {length_score:.1f})")
        if vocab_score < 65:
            issues.append(f"Vocabulary diversity low (score: {vocab_score:.1f})")
        if pattern_score < 70:
            issues.append(f"Repetitive patterns detected (score: {pattern_score:.1f})")
        
        return VariationScore(
            overall_score=overall,
            length_variation=length_score,
            structure_variation=structure_score,
            vocabulary_diversity=vocab_score,
            pattern_avoidance=pattern_score,
            issues=issues
        )
    
    def _check_length_variation(self, texts: List[str], component_type: str) -> float:
        """Check word count variation across texts"""
        if len(texts) < 2:
            return 75.0  # Single text, can't measure variation
        
        word_counts = [len(text.split()) for text in texts]
        avg_length = sum(word_counts) / len(word_counts)
        
        if avg_length == 0:
            return 50.0
        
        # Calculate coefficient of variation (CV)
        variance = sum((wc - avg_length) ** 2 for wc in word_counts) / len(word_counts)
        std_dev = variance ** 0.5
        cv = (std_dev / avg_length) * 100
        
        # Score based on CV (expect 15-35% variation)
        if component_type == 'faq':
            # FAQ answers should vary more
            if 20 <= cv <= 40:
                return 95.0
            elif 15 <= cv <= 50:
                return 85.0
            elif cv < 10:
                return 60.0  # Too uniform
            else:
                return 70.0
        
        else:
            # Caption/subtitle - less variation expected
            if 10 <= cv <= 30:
                return 90.0
            elif cv < 5:
                return 65.0
            else:
                return 75.0
    
    def _check_structure_variation(self, texts: List[str]) -> float:
        """Check sentence structure variation"""
        if len(texts) < 2:
            return 75.0
        
        # Analyze sentence patterns (simple vs complex)
        patterns = []
        for text in texts:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Count commas (proxy for complexity)
            comma_density = sum(s.count(',') for s in sentences) / max(len(sentences), 1)
            patterns.append(comma_density)
        
        # Variation in complexity
        avg_complexity = sum(patterns) / len(patterns)
        variance = sum((p - avg_complexity) ** 2 for p in patterns) / len(patterns)
        
        # Higher variance = more varied structure
        if variance > 0.5:
            return 90.0
        elif variance > 0.2:
            return 75.0
        else:
            return 60.0
    
    def _check_vocabulary_diversity(self, texts: List[str]) -> float:
        """Check lexical diversity (Type-Token Ratio)"""
        full_text = ' '.join(texts).lower()
        words = re.findall(r'\b\w+\b', full_text)
        
        if not words:
            return 50.0
        
        unique_words = set(words)
        ttr = len(unique_words) / len(words)
        
        # Score based on TTR (0.5-0.8 is good)
        if 0.5 <= ttr <= 0.8:
            return 90.0
        elif 0.4 <= ttr < 0.5:
            return 75.0
        elif ttr > 0.8:
            return 85.0  # Very diverse
        else:
            return 60.0  # Too repetitive
    
    def _check_pattern_avoidance(self, texts: List[str]) -> float:
        """Check for AI-typical repetitive patterns"""
        full_text = ' '.join(texts).lower()
        
        # Common AI patterns to avoid
        ai_patterns = [
            r'\b(it is important to|it is crucial to|it is essential to)\b',
            r'\b(furthermore|moreover|additionally|in addition)\b',
            r'\b(in conclusion|to conclude|in summary)\b',
            r'\b(one of the (most|best|key))\b',
        ]
        
        pattern_count = sum(len(re.findall(pattern, full_text)) for pattern in ai_patterns)
        
        # Lower count = better score
        if pattern_count == 0:
            return 100.0
        elif pattern_count <= 2:
            return 85.0
        elif pattern_count <= 4:
            return 70.0
        else:
            return 55.0
    
    # ========================================================================
    # HUMAN CHARACTERISTICS SCORING
    # ========================================================================
    
    def _score_human_characteristics(self, texts: List[str]) -> HumanCharacteristicsScore:
        """Score human writing characteristics"""
        issues = []
        
        # 1. Imperfection score (natural, not errors) (25%)
        imperfection_score = self._check_natural_imperfections(texts)
        
        # 2. Flow naturalness (30%)
        flow_score = self._check_natural_flow(texts)
        
        # 3. Personality presence (25%)
        personality_score = self._check_personality_presence(texts)
        
        # 4. Spontaneity (20%)
        spontaneity_score = self._check_spontaneity(texts)
        
        # Calculate weighted overall score
        overall = (
            imperfection_score * 0.25 +
            flow_score * 0.30 +
            personality_score * 0.25 +
            spontaneity_score * 0.20
        )
        
        # Collect issues
        if flow_score < 60:
            issues.append(f"Flow appears mechanical (score: {flow_score:.1f})")
        if personality_score < 55:
            issues.append(f"Lacks personality/voice (score: {personality_score:.1f})")
        if spontaneity_score < 60:
            issues.append(f"Appears too formulaic (score: {spontaneity_score:.1f})")
        
        return HumanCharacteristicsScore(
            overall_score=overall,
            imperfection_score=imperfection_score,
            flow_naturalness=flow_score,
            personality_presence=personality_score,
            spontaneity_score=spontaneity_score,
            issues=issues
        )
    
    def _check_natural_imperfections(self, texts: List[str]) -> float:
        """Check for natural human imperfections (not errors)"""
        # Human writing has natural variety, not perfect uniformity
        # This is about style variation, not mistakes
        
        full_text = ' '.join(texts)
        sentences = re.split(r'[.!?]+', full_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 70.0
        
        # Check for perfect uniformity (AI tendency)
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        
        # Higher variance = more natural
        if variance > 20:
            return 85.0
        elif variance > 10:
            return 75.0
        else:
            return 65.0  # Too uniform
    
    def _check_natural_flow(self, texts: List[str]) -> float:
        """Check for natural flow and transitions"""
        score = 75.0  # Base score
        
        full_text = ' '.join(texts)
        
        # Check for overly formal transitions (AI tendency)
        formal_transitions = ['furthermore', 'moreover', 'additionally', 'consequently']
        formal_count = sum(full_text.lower().count(t) for t in formal_transitions)
        
        if formal_count > 3:
            score -= 15  # Too formal
        elif formal_count == 0:
            score += 10  # More natural
        
        # Check for conversational elements
        conversational = ["let's", "you'll", "we'll", "that's", "here's"]
        conv_count = sum(full_text.lower().count(c) for c in conversational)
        
        if conv_count > 0:
            score += 10
        
        return min(100.0, max(50.0, score))
    
    def _check_personality_presence(self, texts: List[str]) -> float:
        """Check for author personality presence"""
        full_text = ' '.join(texts).lower()
        
        # Indicators of personality
        personality_markers = [
            # Opinion/perspective
            ('perspective', 2),
            ('consider', 2),
            ('recommend', 2),
            # Expertise
            ('experience', 3),
            ('practice', 2),
            # Engagement
            ('note', 2),
            ('observe', 2),
        ]
        
        score = 60.0
        for marker, weight in personality_markers:
            if marker in full_text:
                score += weight
        
        return min(95.0, score)
    
    def _check_spontaneity(self, texts: List[str]) -> float:
        """Check for spontaneity vs formulaic writing"""
        full_text = ' '.join(texts)
        
        # Formulaic patterns (AI tendency)
        formulaic_patterns = [
            r'^(In order to|To ensure|For optimal)',
            r'(is crucial|is essential|is vital|is key)',
            r'(it is important to note|it should be noted)',
        ]
        
        formula_count = sum(len(re.findall(p, full_text, re.IGNORECASE)) for p in formulaic_patterns)
        
        # Lower count = more spontaneous
        if formula_count == 0:
            return 90.0
        elif formula_count <= 2:
            return 75.0
        elif formula_count <= 4:
            return 60.0
        else:
            return 50.0
    
    # ========================================================================
    # AI DETECTION AVOIDANCE SCORING
    # ========================================================================
    
    def _score_ai_avoidance(self, texts: List[str], author_country: str) -> AIDetectionAvoidanceScore:
        """Score AI detection avoidance (higher = more human-like)"""
        issues = []
        
        # 1. Pattern breaking (30%)
        pattern_score = self._check_pattern_breaking(texts)
        
        # 2. Unpredictability (25%)
        unpredictability_score = self._check_unpredictability(texts)
        
        # 3. Contextual depth (25%)
        context_score = self._check_contextual_depth(texts)
        
        # 4. Authenticity (20%)
        authenticity_score = self._check_authenticity(texts, author_country)
        
        # Calculate weighted overall score
        overall = (
            pattern_score * 0.30 +
            unpredictability_score * 0.25 +
            context_score * 0.25 +
            authenticity_score * 0.20
        )
        
        # Collect issues
        if pattern_score < 65:
            issues.append(f"AI-typical patterns detected (score: {pattern_score:.1f})")
        if unpredictability_score < 60:
            issues.append(f"Content too predictable (score: {unpredictability_score:.1f})")
        if context_score < 65:
            issues.append(f"Lacks contextual depth (score: {context_score:.1f})")
        
        return AIDetectionAvoidanceScore(
            overall_score=overall,
            pattern_breaking=pattern_score,
            unpredictability=unpredictability_score,
            contextual_depth=context_score,
            authenticity=authenticity_score,
            issues=issues
        )
    
    def _check_pattern_breaking(self, texts: List[str]) -> float:
        """Check for breaking AI-typical patterns"""
        # This is inverse of pattern detection
        full_text = ' '.join(texts).lower()
        
        # AI typical patterns
        ai_patterns = [
            r'\b(leverage|utilize|implement|facilitate)\b',
            r'\b(comprehensive|robust|seamless|innovative)\b',
            r'\b(it is worth noting|it is important to|one must)\b',
        ]
        
        pattern_hits = sum(len(re.findall(p, full_text)) for p in ai_patterns)
        
        # Fewer hits = better score
        if pattern_hits == 0:
            return 100.0
        elif pattern_hits <= 2:
            return 85.0
        elif pattern_hits <= 4:
            return 70.0
        else:
            return 55.0
    
    def _check_unpredictability(self, texts: List[str]) -> float:
        """Check for unpredictable elements"""
        # Measure entropy/surprise in word choice
        full_text = ' '.join(texts).lower()
        words = re.findall(r'\b\w+\b', full_text)
        
        if not words:
            return 70.0
        
        # Check for unexpected word combinations
        # Simple heuristic: unique bigrams
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        unique_bigrams = len(set(bigrams))
        total_bigrams = len(bigrams)
        
        if total_bigrams == 0:
            return 70.0
        
        uniqueness_ratio = unique_bigrams / total_bigrams
        
        # Higher uniqueness = more unpredictable
        if uniqueness_ratio > 0.8:
            return 90.0
        elif uniqueness_ratio > 0.6:
            return 75.0
        else:
            return 65.0
    
    def _check_contextual_depth(self, texts: List[str]) -> float:
        """Check for deep contextual understanding"""
        full_text = ' '.join(texts)
        
        # Indicators of contextual depth
        depth_indicators = [
            # Specific technical details
            r'\b\d+\s*(nm|µm|mm|J/cm²|W|MHz)\b',
            # Material-specific references
            r'\b(oxide layer|substrate|coating|contamination)\b',
            # Process-specific
            r'\b(ablation|absorption|reflection|thermal)\b',
        ]
        
        depth_score = 60.0
        for pattern in depth_indicators:
            matches = len(re.findall(pattern, full_text, re.IGNORECASE))
            depth_score += min(matches * 5, 15)
        
        return min(95.0, depth_score)
    
    def _check_authenticity(self, texts: List[str], author_country: str) -> float:
        """Check for genuine human touch"""
        full_text = ' '.join(texts)
        
        # Authentic human markers
        authentic_markers = [
            # Personal observations
            ('note that', 2),
            ('observe', 2),
            ('find that', 2),
            # Real-world context
            ('practice', 3),
            ('application', 2),
            ('industry', 2),
        ]
        
        score = 65.0
        for marker, weight in authentic_markers:
            if marker in full_text.lower():
                score += weight
        
        return min(90.0, score)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _calculate_avg_sentence_length(self, texts: List[str]) -> float:
        """Calculate average sentence length across texts"""
        full_text = ' '.join(texts)
        sentences = re.split(r'[.!?]+', full_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        word_counts = [len(s.split()) for s in sentences]
        return sum(word_counts) / len(word_counts)
    
    def _calculate_overall_score(
        self,
        author_voice: AuthorVoiceScore,
        variation: VariationScore,
        human: HumanCharacteristicsScore,
        ai_avoidance: AIDetectionAvoidanceScore
    ) -> float:
        """Calculate weighted overall score"""
        # Weights: voice (40%), variation (25%), human (20%), AI avoidance (15%)
        overall = (
            author_voice.overall_score * 0.40 +
            variation.overall_score * 0.25 +
            human.overall_score * 0.20 +
            ai_avoidance.overall_score * 0.15
        )
        return round(overall, 2)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _collect_feedback(
        self,
        author_voice: AuthorVoiceScore,
        variation: VariationScore,
        human: HumanCharacteristicsScore,
        ai_avoidance: AIDetectionAvoidanceScore,
        author_country: str
    ) -> Tuple[List[str], List[str], List[str]]:
        """Collect critical issues, warnings, and recommendations"""
        critical_issues = []
        warnings = []
        recommendations = []
        
        # Critical issues (score < 60)
        if author_voice.overall_score < 60:
            critical_issues.append("Author voice authenticity critically low")
        if variation.overall_score < 55:
            critical_issues.append("Content variation critically insufficient")
        
        # Warnings (score < 70)
        if author_voice.overall_score < 70:
            warnings.extend(author_voice.issues)
        if variation.overall_score < 65:
            warnings.extend(variation.issues)
        if human.overall_score < 60:
            warnings.extend(human.issues)
        if ai_avoidance.overall_score < 70:
            warnings.extend(ai_avoidance.issues)
        
        # Recommendations based on country and scores
        thresholds = PERSONA_THRESHOLDS.get(author_country, {})
        target = thresholds.get('target_score', 80)
        
        overall = self._calculate_overall_score(author_voice, variation, human, ai_avoidance)
        
        if overall < target:
            gap = target - overall
            if gap > 10:
                recommendations.append("Consider regenerating content - significant improvement needed")
            elif gap > 5:
                recommendations.append("Moderate improvements recommended for optimal quality")
            
            # Specific recommendations
            if author_voice.overall_score < target:
                if author_country == "Taiwan":
                    recommendations.append("Strengthen systematic approach and technical precision")
                elif author_country == "Italy":
                    recommendations.append("Enhance expressive language and engineering passion")
                elif author_country == "Indonesia":
                    recommendations.append("Improve analytical clarity and balanced presentation")
                elif "United States" in author_country:
                    recommendations.append("Boost innovative language and conversational tone")
        
        return critical_issues, warnings, recommendations
    
    def _create_failure_result(
        self,
        component_type: str,
        material_name: str,
        author_name: str,
        author_country: str,
        error_message: str
    ) -> ContentValidationResult:
        """Create a failure result"""
        zero_score = lambda: 0.0
        
        return ContentValidationResult(
            success=False,
            component_type=component_type,
            material_name=material_name,
            author_name=author_name,
            author_country=author_country,
            author_voice=AuthorVoiceScore(0, 0, 0, 0, 0, [error_message]),
            variation=VariationScore(0, 0, 0, 0, 0, []),
            human_characteristics=HumanCharacteristicsScore(0, 0, 0, 0, 0, []),
            ai_avoidance=AIDetectionAvoidanceScore(0, 0, 0, 0, 0, []),
            overall_score=0.0,
            grade="F",
            critical_issues=[error_message],
            warnings=[],
            recommendations=["Fix validation errors and regenerate content"]
        )
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def generate_validation_report(self, result: ContentValidationResult) -> str:
        """Generate human-readable validation report"""
        lines = []
        lines.append("=" * 80)
        lines.append("📊 CONTENT VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append(f"\nComponent: {result.component_type.upper()}")
        lines.append(f"Material: {result.material_name}")
        lines.append(f"Author: {result.author_name} ({result.author_country})")
        lines.append(f"Timestamp: {result.timestamp}")
        lines.append("")
        
        # Overall score
        status = "✅ PASSED" if result.success else "❌ FAILED"
        lines.append(f"Overall Score: {result.overall_score:.1f}/100 (Grade: {result.grade}) {status}")
        lines.append("")
        
        # Dimension scores
        lines.append("DIMENSION SCORES:")
        lines.append("-" * 80)
        
        dimensions = [
            ("Author Voice", result.author_voice, 0.40),
            ("Content Variation", result.variation, 0.25),
            ("Human Characteristics", result.human_characteristics, 0.20),
            ("AI Detection Avoidance", result.ai_avoidance, 0.15),
        ]
        
        for name, score_obj, weight in dimensions:
            status_icon = "✅" if score_obj.passed else "⚠️"
            lines.append(f"{status_icon} {name}: {score_obj.overall_score:.1f}/100 (weight: {weight*100:.0f}%)")
            
            # Sub-scores
            if hasattr(score_obj, 'linguistic_match'):
                lines.append(f"   - Linguistic Match: {score_obj.linguistic_match:.1f}")
                lines.append(f"   - Phrase Authenticity: {score_obj.phrase_authenticity:.1f}")
                lines.append(f"   - Tone Consistency: {score_obj.tone_consistency:.1f}")
                lines.append(f"   - Technical Balance: {score_obj.technical_balance:.1f}")
            elif hasattr(score_obj, 'length_variation'):
                lines.append(f"   - Length Variation: {score_obj.length_variation:.1f}")
                lines.append(f"   - Structure Variation: {score_obj.structure_variation:.1f}")
                lines.append(f"   - Vocabulary Diversity: {score_obj.vocabulary_diversity:.1f}")
                lines.append(f"   - Pattern Avoidance: {score_obj.pattern_avoidance:.1f}")
            elif hasattr(score_obj, 'imperfection_score'):
                lines.append(f"   - Natural Imperfections: {score_obj.imperfection_score:.1f}")
                lines.append(f"   - Flow Naturalness: {score_obj.flow_naturalness:.1f}")
                lines.append(f"   - Personality Presence: {score_obj.personality_presence:.1f}")
                lines.append(f"   - Spontaneity: {score_obj.spontaneity_score:.1f}")
            elif hasattr(score_obj, 'pattern_breaking'):
                lines.append(f"   - Pattern Breaking: {score_obj.pattern_breaking:.1f}")
                lines.append(f"   - Unpredictability: {score_obj.unpredictability:.1f}")
                lines.append(f"   - Contextual Depth: {score_obj.contextual_depth:.1f}")
                lines.append(f"   - Authenticity: {score_obj.authenticity:.1f}")
            
            if score_obj.issues:
                for issue in score_obj.issues:
                    lines.append(f"   ⚠️  {issue}")
            lines.append("")
        
        # Critical issues
        if result.critical_issues:
            lines.append("🚨 CRITICAL ISSUES:")
            for issue in result.critical_issues:
                lines.append(f"   - {issue}")
            lines.append("")
        
        # Warnings
        if result.warnings:
            lines.append("⚠️  WARNINGS:")
            for warning in result.warnings:
                lines.append(f"   - {warning}")
            lines.append("")
        
        # Recommendations
        if result.recommendations:
            lines.append("💡 RECOMMENDATIONS:")
            for rec in result.recommendations:
                lines.append(f"   - {rec}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return '\n'.join(lines)
