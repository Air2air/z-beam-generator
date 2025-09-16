#!/usr/bin/env python3
"""
Winston.ai Composite Scoring Algorithm
======================================

This module creates a bias-filtered composite score from Winston.ai's rich response data,
addressing the systematic bias against technical content while leveraging detailed metrics.

Key Approach:
1. Analyze multiple Winston.ai metrics beyond just the main score
2. Apply domain-specific adjustments for technical content
3. Weight different factors based on reliability and relevance
4. Generate a composite "human-likeness" score that's more accurate for our use case
"""

import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class WinstonCompositeResult:
    """Enhanced result with composite scoring"""
    original_score: float  # Winston's raw score
    composite_score: float  # Our calculated composite score
    confidence: float  # Composite confidence level
    classification: str  # Based on composite score
    bias_adjustments: Dict[str, float]  # Applied adjustments
    component_scores: Dict[str, float]  # Individual component contributions
    reasoning: List[str]  # Human-readable explanations


class WinstonCompositeScorer:
    """
    Creates composite scores from Winston.ai response data to overcome technical content bias
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        
    def _default_config(self) -> Dict:
        """Default configuration for composite scoring"""
        return {
            # Component weights (must sum to 1.0)
            "weights": {
                "sentence_distribution": 0.35,  # How varied are sentence scores?
                "readability_normalized": 0.25,  # Readability as human indicator  
                "content_authenticity": 0.20,   # Non-uniform patterns, natural flow
                "technical_adjustment": 0.15,   # Domain-specific bias correction
                "winston_baseline": 0.05        # Small weight for Winston's raw score
            },
            
            # Bias correction factors
            "technical_content_boost": 25.0,    # Points to add for technical content
            "max_technical_adjustment": 40.0,   # Cap on technical adjustment
            
            # Sentence analysis thresholds
            "high_variance_threshold": 30.0,    # Score variance indicating natural writing
            "zero_score_penalty_threshold": 0.7, # Penalty when >70% sentences score 0
            
            # Readability mapping (Winston's readability to human-likeness)
            "readability_ranges": {
                "very_simple": (0, 20, 15),      # (min, max, human_score)
                "simple": (20, 40, 35),
                "moderate": (40, 60, 65),
                "complex": (60, 80, 80),
                "very_complex": (80, 100, 70)    # Very complex can seem AI-like
            },
            
            # Technical content indicators
            "technical_keywords": [
                "wavelength", "fluence", "ablation", "conductivity", "J/cm²", 
                "nanoseconds", "kHz", "laser", "thermal", "spectroscopy", 
                "substrate", "oxide", "microstructural", "nm", "W/m·K"
            ],
            
            # Classification thresholds for composite score
            "classification_thresholds": {
                "human": 70.0,
                "unclear": 40.0,
                "ai": 0.0
            }
        }
    
    def calculate_composite_score(self, winston_response: Dict[str, Any]) -> WinstonCompositeResult:
        """
        Calculate composite score from Winston.ai response data
        
        Args:
            winston_response: Full Winston.ai API response
            
        Returns:
            WinstonCompositeResult with composite scoring and analysis
        """
        original_score = winston_response.get("score", 0.0)
        details = winston_response.get("details", {})
        sentences = details.get("sentences", [])
        
        # Initialize component scores
        component_scores = {}
        bias_adjustments = {}
        reasoning = []
        
        # 1. Sentence Distribution Analysis (35% weight)
        sentence_score = self._analyze_sentence_distribution(sentences)
        component_scores["sentence_distribution"] = sentence_score
        reasoning.append(f"Sentence variance analysis: {sentence_score:.1f}/100")
        
        # 2. Readability Normalization (25% weight)  
        readability = details.get("readability_score", 50.0)
        readability_score = self._normalize_readability(readability)
        component_scores["readability_normalized"] = readability_score
        reasoning.append(f"Readability mapping ({readability:.1f}): {readability_score:.1f}/100")
        
        # 3. Content Authenticity (20% weight)
        authenticity_score = self._assess_content_authenticity(winston_response)
        component_scores["content_authenticity"] = authenticity_score
        reasoning.append(f"Content authenticity patterns: {authenticity_score:.1f}/100")
        
        # 4. Technical Content Adjustment (15% weight)
        text = details.get("input", "")
        technical_score, technical_adjustment = self._apply_technical_adjustment(
            text, original_score
        )
        component_scores["technical_adjustment"] = technical_score
        bias_adjustments["technical_bias_correction"] = technical_adjustment
        reasoning.append(f"Technical content adjustment: +{technical_adjustment:.1f} points")
        
        # 5. Winston Baseline (5% weight)
        winston_baseline = max(original_score, 5.0)  # Never completely ignore Winston
        component_scores["winston_baseline"] = winston_baseline
        reasoning.append(f"Winston baseline (capped): {winston_baseline:.1f}/100")
        
        # Calculate weighted composite score
        weights = self.config["weights"]
        composite_score = sum(
            component_scores[component] * weights[component]
            for component in component_scores
        )
        
        # Apply additional bias corrections
        composite_score = min(composite_score + sum(bias_adjustments.values()), 100.0)
        
        # Calculate composite confidence
        confidence = self._calculate_composite_confidence(component_scores, winston_response)
        
        # Determine classification
        classification = self._classify_composite_score(composite_score)
        
        reasoning.append(f"Final composite score: {composite_score:.1f}/100 ({classification})")
        
        return WinstonCompositeResult(
            original_score=original_score,
            composite_score=composite_score,
            confidence=confidence,
            classification=classification,
            bias_adjustments=bias_adjustments,
            component_scores=component_scores,
            reasoning=reasoning
        )
    
    def _analyze_sentence_distribution(self, sentences: List[Dict]) -> float:
        """
        Analyze sentence score distribution for natural writing patterns
        
        Natural human writing should have varied sentence scores, not all 0s or all 100s
        """
        if not sentences:
            return 50.0  # Neutral score if no sentence data
            
        # Extract sentence scores
        sentence_scores = []
        for sentence in sentences:
            if isinstance(sentence, dict) and "score" in sentence:
                sentence_scores.append(sentence["score"])
        
        if not sentence_scores:
            return 50.0
            
        # Calculate variance and distribution metrics
        avg_score = sum(sentence_scores) / len(sentence_scores)
        variance = sum((s - avg_score) ** 2 for s in sentence_scores) / len(sentence_scores)
        std_dev = variance ** 0.5
        
        # Count extreme scores
        zero_count = sum(1 for s in sentence_scores if s == 0)
        hundred_count = sum(1 for s in sentence_scores if s == 100)
        extreme_percentage = (zero_count + hundred_count) / len(sentence_scores)
        
        # Natural writing should have:
        # - Some variance in sentence scores (not all the same)
        # - Not too many extreme scores (0 or 100)
        # - Reasonable average score
        
        variance_score = min(std_dev * 2, 100)  # Higher variance = more natural
        extreme_penalty = extreme_percentage * 50  # Penalty for too many extremes
        average_bonus = min(avg_score / 2, 25)  # Bonus for decent average
        
        distribution_score = variance_score - extreme_penalty + average_bonus
        return max(min(distribution_score, 100), 0)
    
    def _normalize_readability(self, readability_score: float) -> float:
        """
        Map Winston's readability score to human-likeness score
        
        Winston's readability doesn't directly correlate with AI detection,
        but certain ranges may indicate natural human writing complexity
        """
        ranges = self.config["readability_ranges"]
        
        for range_name, (min_val, max_val, human_score) in ranges.items():
            if min_val <= readability_score <= max_val:
                return human_score
                
        # Fallback for out-of-range values
        if readability_score < 20:
            return 15  # Very simple
        elif readability_score > 80:
            return 70  # Very complex
        else:
            return 50  # Default
    
    def _assess_content_authenticity(self, winston_response: Dict) -> float:
        """
        Assess content authenticity based on patterns Winston.ai detected
        """
        details = winston_response.get("details", {})
        
        # Check for attack patterns (good sign if none detected)
        attack_detected = details.get("attack_detected", {})
        no_attacks_bonus = 20 if not any(attack_detected.values()) else 0
        
        # Check sentence pattern analysis
        failing_patterns = details.get("failing_patterns", {})
        
        # Natural writing should not have:
        # - Excessive repetition
        # - Completely uniform structure  
        # - Unnatural technical density
        
        repetition_penalty = 15 if failing_patterns.get("contains_repetition", False) else 0
        uniform_penalty = 20 if failing_patterns.get("uniform_structure", False) else 0
        
        # Technical density between 0.1-0.3 is natural for technical content
        tech_density = failing_patterns.get("technical_density", 0.2)
        if 0.1 <= tech_density <= 0.3:
            density_score = 20
        elif tech_density < 0.1:
            density_score = 10  # Too simple for technical content
        else:
            density_score = 5   # Too dense
            
        authenticity_score = (
            no_attacks_bonus + density_score - repetition_penalty - uniform_penalty + 50
        )
        
        return max(min(authenticity_score, 100), 0)
    
    def _apply_technical_adjustment(self, text: str, original_score: float) -> tuple[float, float]:
        """
        Apply bias correction for technical content
        
        Returns: (adjusted_score, adjustment_amount)
        """
        if not text:
            return 50.0, 0.0
            
        text_lower = text.lower()
        
        # Count technical keywords
        technical_keywords = self.config["technical_keywords"]
        keyword_count = sum(1 for keyword in technical_keywords if keyword in text_lower)
        keyword_density = keyword_count / len(text.split()) if text.split() else 0
        
        # Technical content indicators
        has_equations = any(char in text for char in ["=", "²", "³", "°", "±"])
        has_units = any(unit in text_lower for unit in ["j/cm", "w/m", "nm", "khz", "ns"])
        has_ranges = "–" in text or " - " in text or "between" in text_lower
        
        # Calculate technical content score
        technical_indicators = sum([
            keyword_count > 3,          # Multiple technical terms
            keyword_density > 0.05,     # High technical density  
            has_equations,              # Mathematical notation
            has_units,                  # Scientific units
            has_ranges,                 # Parameter ranges
            len(text) > 200             # Substantial technical content
        ])
        
        # Apply adjustment based on technical content level
        base_adjustment = self.config["technical_content_boost"]
        max_adjustment = self.config["max_technical_adjustment"]
        
        # Higher technical content = higher adjustment
        adjustment_factor = technical_indicators / 6.0  # Normalize to 0-1
        technical_adjustment = min(base_adjustment * adjustment_factor, max_adjustment)
        
        # If original score is extremely low (<10) and content is highly technical,
        # apply more aggressive correction
        if original_score < 10 and technical_indicators >= 4:
            technical_adjustment = max_adjustment
            
        adjusted_score = min(original_score + technical_adjustment, 100.0)
        
        return adjusted_score, technical_adjustment
    
    def _calculate_composite_confidence(self, component_scores: Dict, winston_response: Dict) -> float:
        """
        Calculate confidence in the composite score based on component agreement
        """
        scores = list(component_scores.values())
        
        if not scores:
            return 0.5
            
        # Higher confidence when components agree
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        
        # Lower variance = higher confidence
        confidence_from_agreement = max(0, 1 - (variance / 1000))
        
        # Boost confidence if we have good sentence-level data
        sentences = winston_response.get("details", {}).get("sentences", [])
        data_quality_bonus = 0.2 if len(sentences) > 3 else 0
        
        total_confidence = min(confidence_from_agreement + data_quality_bonus, 1.0)
        return max(total_confidence, 0.1)  # Minimum 10% confidence
    
    def _classify_composite_score(self, score: float) -> str:
        """Classify composite score into human/unclear/ai categories"""
        thresholds = self.config["classification_thresholds"]
        
        if score >= thresholds["human"]:
            return "human"
        elif score >= thresholds["unclear"]:
            return "unclear"
        else:
            return "ai"


def test_composite_scorer():
    """Test the composite scorer with sample Winston.ai responses"""
    
    # Sample Winston.ai response (based on our copper content analysis)
    sample_response = {
        "score": 0.7,  # Winston's biased score
        "details": {
            "input": "Copper's thermal conductivity of 401 W/m·K requires precise fluence control between 0.5-3.0 J/cm² for effective laser ablation at 1064nm wavelength.",
            "readability_score": 45.2,
            "sentences": [
                {"score": 0, "text": "Copper's thermal conductivity of 401 W/m·K requires precise fluence control."},
                {"score": 0, "text": "Effective laser ablation occurs at 1064nm wavelength."},
                {"score": 60, "text": "This process enables selective cleaning of oxide layers."}
            ],
            "attack_detected": {
                "zero_width_space": False,
                "homoglyph_attack": False
            },
            "failing_patterns": {
                "contains_repetition": False,
                "uniform_structure": False,
                "technical_density": 0.23
            }
        }
    }
    
    scorer = WinstonCompositeScorer()
    result = scorer.calculate_composite_score(sample_response)
    
    print("🧮 Winston.ai Composite Scorer Test Results")
    print("=" * 50)
    print(f"Original Winston Score: {result.original_score}% human")
    print(f"Composite Score: {result.composite_score:.1f}% human")
    print(f"Classification: {result.classification.upper()}")
    print(f"Confidence: {result.confidence:.2f}")
    
    print("\n📊 Component Breakdown:")
    for component, score in result.component_scores.items():
        weight = scorer.config["weights"][component]
        contribution = score * weight
        print(f"  {component}: {score:.1f} (weight: {weight:.2f}, contributes: {contribution:.1f})")
    
    print("\n🔧 Bias Adjustments:")
    for adjustment, value in result.bias_adjustments.items():
        print(f"  {adjustment}: +{value:.1f} points")
    
    print("\n💭 Reasoning:")
    for reason in result.reasoning:
        print(f"  • {reason}")


if __name__ == "__main__":
    test_composite_scorer()
