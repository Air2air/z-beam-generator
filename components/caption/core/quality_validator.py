#!/usr/bin/env python3
"""
Quality Validator - Integrated quality validation during generation

Provides streaming quality validation during caption generation process,
eliminating the need for separate grading steps.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityResult:
    """Quality validation result"""
    overall_score: int
    passed: bool
    issues: List[str]
    recommendations: List[str]
    voice_score: int = 0
    ai_score: int = 0
    technical_score: int = 0


class QualityValidator:
    """Integrated quality validation - no separate grading step needed"""
    
    def __init__(self):
        self.voice_adapter = None  # Will be injected to avoid circular imports
    
    def set_voice_adapter(self, voice_adapter):
        """Inject voice adapter to avoid circular imports"""
        self.voice_adapter = voice_adapter
    
    def validate_during_generation(self, content: Dict[str, Any], 
                                 author_config: Dict[str, Any]) -> QualityResult:
        """Validate quality during generation process"""
        
        try:
            before_text = content.get('beforeText', '')
            after_text = content.get('afterText', '')
            combined_text = before_text + ' ' + after_text
            country = author_config.get('country', 'usa')
            
            # Assess different quality dimensions
            voice_score = self._assess_voice_authenticity(before_text, after_text, country)
            ai_score = self._assess_ai_detectability(combined_text)
            technical_score = self._assess_technical_accuracy(before_text, after_text)
            
            # Calculate weighted overall score
            overall_score = self._calculate_weighted_score(voice_score, ai_score, technical_score)
            
            # Check if meets thresholds
            thresholds = self._get_quality_thresholds(country)
            passed = self._meets_thresholds(voice_score, ai_score, technical_score, thresholds)
            
            # Generate issues and recommendations
            issues = self._identify_issues(voice_score, ai_score, technical_score, thresholds)
            recommendations = self._generate_recommendations(voice_score, ai_score, technical_score)
            
            return QualityResult(
                overall_score=overall_score,
                passed=passed,
                issues=issues,
                recommendations=recommendations,
                voice_score=voice_score,
                ai_score=ai_score,
                technical_score=technical_score
            )
            
        except Exception as e:
            logger.error(f"Quality validation failed: {e}")
            return QualityResult(
                overall_score=0,
                passed=False,
                issues=[f"Quality validation error: {e}"],
                recommendations=["Review content and retry generation"]
            )
    
    def _assess_voice_authenticity(self, before_text: str, after_text: str, country: str) -> int:
        """Assess voice authenticity against country expectations"""
        
        combined_text = (before_text + ' ' + after_text).lower()
        score = 70  # Base score
        
        # Country-specific voice markers (simplified from CopilotQualityGrader)
        voice_markers = {
            'united_states': ['bottom line', 'here\'s what', 'works out', 'roughly', 'around'],
            'usa': ['bottom line', 'here\'s what', 'works out', 'roughly', 'around'],
            'taiwan': ['systematic', 'analysis shows', 'appears to', 'suggests', 'indicates'],
            'italy': ['examining this', 'one cannot', 'what strikes', 'elegant', 'beautiful'],
            'indonesia': ['practical', 'community', 'environmental', 'very-very', 'this surface']
        }
        
        markers = voice_markers.get(country.lower(), [])
        
        # Check for voice markers
        marker_count = sum(1 for marker in markers if marker in combined_text)
        if marker_count > 0:
            score += min(marker_count * 5, 20)  # Up to 20 bonus points
        
        # Check for formulaic phrases (penalty)
        formulaic_phrases = ['surface analysis reveals', 'microscopic examination shows', 
                           'examination reveals', 'analysis demonstrates']
        formulaic_count = sum(1 for phrase in formulaic_phrases if phrase in combined_text)
        if formulaic_count > 1:
            score -= formulaic_count * 10
        
        return max(0, min(100, score))
    
    def _assess_ai_detectability(self, text: str) -> int:
        """Assess AI detectability (higher score = more human-like)"""
        
        score = 70  # Base score
        
        # Check sentence length variation
        sentences = [s.strip() for s in text.replace('.', '.|').replace('!', '!|').replace('?', '?|').split('|') if s.strip()]
        if len(sentences) > 3:
            lengths = [len(s.split()) for s in sentences]
            if len(set(lengths)) > len(lengths) * 0.6:  # Good variation
                score += 10
            
            # Check for very short and very long sentences
            short_sentences = sum(1 for length in lengths if length < 8)
            long_sentences = sum(1 for length in lengths if length > 20)
            if short_sentences > 0 and long_sentences > 0:
                score += 10
        
        # Check for natural imperfections
        imperfection_markers = ['approximately', 'roughly', 'about', '—', 'perhaps', 'seems to']
        imperfection_count = sum(1 for marker in imperfection_markers if marker.lower() in text.lower())
        if imperfection_count > 0:
            score += min(imperfection_count * 3, 15)
        
        # Check for parenthetical asides
        if '(' in text and ')' in text:
            score += 5
        
        # Penalty for overly perfect measurements
        if text.count('.0 ') > 2:  # Too many perfect decimals
            score -= 10
        
        return max(0, min(100, score))
    
    def _assess_technical_accuracy(self, before_text: str, after_text: str) -> int:
        """Assess technical accuracy and plausibility"""
        
        score = 80  # Base score (assume technically sound)
        
        combined_text = (before_text + ' ' + after_text).lower()
        
        # Check for measurement units
        units = ['µm', 'micrometers', 'nm', 'mm', '%', 'degrees']
        unit_count = sum(1 for unit in units if unit in combined_text)
        if unit_count > 0:
            score += min(unit_count * 2, 10)
        
        # Check for technical terms
        technical_terms = ['contamination', 'surface', 'cleaning', 'laser', 'analysis', 
                          'microscopic', 'thickness', 'roughness']
        tech_count = sum(1 for term in technical_terms if term in combined_text)
        if tech_count >= 5:
            score += 10
        
        # Check for before/after comparison
        comparison_words = ['improved', 'reduced', 'increased', 'enhanced', 'better', 'cleaner']
        if any(word in after_text.lower() for word in comparison_words):
            score += 5
        
        return max(0, min(100, score))
    
    def _calculate_weighted_score(self, voice_score: int, ai_score: int, technical_score: int) -> int:
        """Calculate weighted overall score"""
        # Weights: voice authenticity 30%, AI human-likeness 40%, technical accuracy 30%
        return int(voice_score * 0.3 + ai_score * 0.4 + technical_score * 0.3)
    
    def _get_quality_thresholds(self, country: str) -> Dict[str, float]:
        """Get quality thresholds for country"""
        if self.voice_adapter:
            try:
                return self.voice_adapter.get_quality_thresholds(country)
            except Exception:
                pass
        
        # Fallback thresholds
        return {
            'min_voice_authenticity': 60.0,
            'min_ai_human_likeness': 65.0,
            'min_technical_accuracy': 70.0,
            'min_overall_score': 65.0
        }
    
    def _meets_thresholds(self, voice_score: int, ai_score: int, technical_score: int, 
                         thresholds: Dict[str, float]) -> bool:
        """Check if scores meet minimum thresholds"""
        return (voice_score >= thresholds.get('min_voice_authenticity', 60) and
                ai_score >= thresholds.get('min_ai_human_likeness', 65) and 
                technical_score >= thresholds.get('min_technical_accuracy', 70))
    
    def _identify_issues(self, voice_score: int, ai_score: int, technical_score: int,
                        thresholds: Dict[str, float]) -> List[str]:
        """Identify specific quality issues"""
        issues = []
        
        if voice_score < thresholds.get('min_voice_authenticity', 60):
            issues.append(f"Voice authenticity below threshold: {voice_score} < {thresholds.get('min_voice_authenticity', 60)}")
        
        if ai_score < thresholds.get('min_ai_human_likeness', 65):
            issues.append(f"AI human-likeness below threshold: {ai_score} < {thresholds.get('min_ai_human_likeness', 65)}")
        
        if technical_score < thresholds.get('min_technical_accuracy', 70):
            issues.append(f"Technical accuracy below threshold: {technical_score} < {thresholds.get('min_technical_accuracy', 70)}")
        
        return issues
    
    def _generate_recommendations(self, voice_score: int, ai_score: int, technical_score: int) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if voice_score < 70:
            recommendations.append("Increase country-specific voice markers and reduce formulaic phrases")
        
        if ai_score < 70:
            recommendations.append("Add more sentence length variation and natural imperfections")
        
        if technical_score < 75:
            recommendations.append("Include more technical measurements and terminology")
        
        return recommendations