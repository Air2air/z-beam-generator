#!/usr/bin/env python3
"""
Winston.ai Enhanced Provider with Composite Scoring
==================================================

This module extends the existing Winston.ai provider to include composite scoring
that corrects for technical content bias while maintaining compatibility with
the existing AI detection framework.
"""

import logging
from typing import Dict, Any, Optional
from ai_detection.providers.winston import WinstonProvider
from ai_detection.service import AIDetectionResult
from winston_composite_scorer import WinstonCompositeScorer

logger = logging.getLogger(__name__)


class WinstonEnhancedProvider(WinstonProvider):
    """
    Enhanced Winston.ai provider with bias-corrected composite scoring
    
    This provider maintains full compatibility with the existing AI detection system
    while providing improved accuracy for technical content through composite scoring.
    """
    
    def __init__(self, config, use_composite_scoring: bool = True):
        super().__init__(config)
        self.use_composite_scoring = use_composite_scoring
        self.composite_scorer = WinstonCompositeScorer() if use_composite_scoring else None
        
    def analyze_text(self, text: str, options: Optional[Dict] = None) -> AIDetectionResult:
        """
        Analyze text with optional composite scoring for bias correction
        
        Returns enhanced AIDetectionResult with both raw and composite scores
        """
        # Get standard Winston.ai analysis
        raw_result = super().analyze_text(text, options)
        
        if not self.use_composite_scoring:
            return raw_result
            
        try:
            # Prepare Winston response data for composite scoring
            winston_response = {
                "score": raw_result.score,
                "details": raw_result.details
            }
            
            # Calculate composite score
            composite_result = self.composite_scorer.calculate_composite_score(winston_response)
            
            # Create enhanced result with composite data
            enhanced_details = raw_result.details.copy()
            enhanced_details.update({
                "composite_scoring": {
                    "enabled": True,
                    "original_score": raw_result.score,
                    "composite_score": composite_result.composite_score,
                    "improvement": composite_result.composite_score - raw_result.score,
                    "component_scores": composite_result.component_scores,
                    "bias_adjustments": composite_result.bias_adjustments,
                    "composite_confidence": composite_result.confidence,
                    "reasoning": composite_result.reasoning
                }
            })
            
            # Determine which score and classification to use
            final_score = composite_result.composite_score
            final_classification = composite_result.classification
            
            # Enhanced confidence calculation (blend original and composite)
            original_confidence = raw_result.confidence
            composite_confidence = composite_result.confidence
            
            # Weight composite confidence higher for technical content
            text_lower = text.lower()
            technical_keywords = ["laser", "wavelength", "fluence", "thermal", "conductivity"]
            is_technical = any(keyword in text_lower for keyword in technical_keywords)
            
            if is_technical:
                final_confidence = (0.3 * original_confidence) + (0.7 * composite_confidence)
            else:
                final_confidence = (0.7 * original_confidence) + (0.3 * composite_confidence)
                
            # Log the enhancement
            improvement = final_score - raw_result.score
            logger.info(
                f"🧮 Composite scoring applied: {raw_result.score:.1f}% → {final_score:.1f}% "
                f"({improvement:+.1f} points, technical={is_technical})"
            )
            
            return AIDetectionResult(
                score=final_score,
                confidence=final_confidence,
                classification=final_classification,
                details=enhanced_details,
                processing_time=raw_result.processing_time,
                provider="winston-enhanced"
            )
            
        except Exception as e:
            logger.warning(f"Composite scoring failed, using raw Winston.ai result: {e}")
            # Fall back to raw result if composite scoring fails
            return raw_result


def create_enhanced_winston_provider(config, enable_composite: bool = True) -> WinstonEnhancedProvider:
    """
    Factory function to create enhanced Winston.ai provider
    
    Args:
        config: AI detection configuration
        enable_composite: Whether to enable composite scoring (default: True)
        
    Returns:
        WinstonEnhancedProvider instance
    """
    return WinstonEnhancedProvider(config, use_composite_scoring=enable_composite)


# Configuration for easy integration
ENHANCED_WINSTON_CONFIG = {
    "provider_class": WinstonEnhancedProvider,
    "composite_scoring": True,
    "technical_content_boost": 25.0,
    "fallback_on_error": True,
    "logging_enabled": True
}


def test_enhanced_provider():
    """Test the enhanced provider with sample content"""
    from ai_detection.service import AIDetectionConfig
    
    config = AIDetectionConfig(timeout=30)
    provider = WinstonEnhancedProvider(config, use_composite_scoring=True)
    
    # Test with technical content that typically scores poorly
    technical_text = """
    Copper's thermal conductivity of 401 W/m·K presents unique challenges for laser cleaning applications. 
    The optimal fluence range of 0.5-3.0 J/cm² must be carefully controlled to achieve effective ablation 
    of surface oxides while preserving substrate integrity. A 1064nm wavelength provides superior absorption 
    characteristics for contaminant removal without damaging the underlying copper matrix.
    """
    
    print("🧪 Testing Enhanced Winston.ai Provider")
    print("=" * 60)
    
    try:
        result = provider.analyze_text(technical_text.strip())
        
        print(f"📊 Final Score: {result.score:.1f}% human")
        print(f"🎯 Classification: {result.classification.upper()}")
        print(f"🔒 Confidence: {result.confidence:.3f}")
        print(f"⏱️  Processing Time: {result.processing_time:.2f}s")
        print(f"🔧 Provider: {result.provider}")
        
        # Show composite scoring details if available
        composite_data = result.details.get("composite_scoring", {})
        if composite_data.get("enabled"):
            print(f"\n🧮 Composite Scoring Details:")
            print(f"   Original Score: {composite_data['original_score']:.1f}%")
            print(f"   Composite Score: {composite_data['composite_score']:.1f}%") 
            print(f"   Improvement: {composite_data['improvement']:+.1f} points")
            
            print(f"\n🔧 Bias Adjustments:")
            for adj, value in composite_data.get("bias_adjustments", {}).items():
                print(f"   • {adj}: {value:+.1f}")
                
            print(f"\n💭 Key Reasoning:")
            for reason in composite_data.get("reasoning", [])[:3]:  # Show first 3
                print(f"   • {reason}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_enhanced_provider()
