"""
Unified Parameter Provider - Consolidated Parameter Resolution

Simplifies parameter resolution by consolidating 5 different sources into a single interface:
- DynamicConfig (base temperature, penalties)
- SweetSpotAnalyzer (learned parameters)
- WeightLearner (quality weights)
- ValidationWinstonCorrelator (quality insights)
- Component config (base settings)

BEFORE (5 separate calls):
    base_params = dynamic_config.calculate_temperature(component_type)
    learned_params = sweet_spot_analyzer.get_learned_parameters()
    learned_weights = weight_learner.get_learned_quality_weights()
    insights = validation_correlator.get_top_issues(lookback_days=7)
    # Complex merging logic...

AFTER (1 unified call):
    params = unified_provider.get_parameters(component_type)
    # All parameters with learning integrated, ready to use

Created: January 20, 2026
Purpose: Simplify generation pipeline by reducing parameter resolution complexity
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class GenerationParameters:
    """Unified container for all generation parameters"""
    # Core API parameters
    temperature: float
    frequency_penalty: float
    presence_penalty: float
    max_tokens: int
    
    # Quality weights (for evaluation)
    quality_weights: Dict[str, float]
    
    # Quality insights (for context)
    recent_issues: List[Dict[str, any]]
    
    # Learning context
    learned_from_samples: int
    confidence_score: float


class UnifiedParameterProvider:
    """
    Consolidated parameter provider integrating all learning sources.
    
    Replaces the complex multi-source parameter resolution pattern with
    a single unified interface that internally queries and merges all sources.
    
    Architecture:
        1. Load base parameters from DynamicConfig
        2. Query learning databases (sweet spot, weights, correlations)
        3. Merge with learned precedence rules
        4. Return unified GenerationParameters object
    """
    
    def __init__(self, db_path: str = 'z-beam.db'):
        """
        Initialize unified parameter provider.
        
        Args:
            db_path: Path to SQLite learning database
        """
        self.db_path = Path(db_path)
        
        # Initialize base config
        from generation.config.dynamic_config import DynamicConfig
        self.dynamic_config = DynamicConfig()
        
        # Initialize learning modules (lazy - only if database exists)
        self._sweet_spot_analyzer = None
        self._weight_learner = None
        self._validation_correlator = None
        
        if self.db_path.exists():
            try:
                from learning.sweet_spot_analyzer import SweetSpotAnalyzer
                from learning.validation_winston_correlator import ValidationWinstonCorrelator
                from learning.weight_learner import WeightLearner
                
                self._sweet_spot_analyzer = SweetSpotAnalyzer(db_path=str(self.db_path))
                self._weight_learner = WeightLearner(db_path=self.db_path)
                self._validation_correlator = ValidationWinstonCorrelator(db_path=str(self.db_path))
                
                logger.info(f"✅ Learning systems initialized from {db_path}")
            except Exception as e:
                logger.warning(f"⚠️  Learning systems unavailable: {e}")
        else:
            logger.info(f"Learning database not found: {db_path} (using base config only)")
    
    def get_parameters(
        self,
        component_type: str,
        target_words: Optional[int] = None
    ) -> GenerationParameters:
        """
        Get unified parameters with all learning integrated.
        
        Args:
            component_type: Type of component (micro, description, faq)
            target_words: Target word count for optimal max_tokens calculation
            
        Returns:
            GenerationParameters with all learning sources merged
        """
        logger.debug(f"Resolving parameters for {component_type}")
        
        # 1. Get base parameters from DynamicConfig
        base_temp = self.dynamic_config.calculate_temperature(component_type)
        base_penalties = self.dynamic_config.calculate_penalties(component_type)
        
        # 2. Apply learned parameters if available
        learned_temp = base_temp
        learned_penalties = base_penalties
        learned_samples = 0
        confidence = 0.0
        
        if self._sweet_spot_analyzer:
            try:
                learned_params = self._sweet_spot_analyzer.get_learned_parameters(component_type)
                if learned_params and 'temperature' in learned_params:
                    learned_temp = learned_params['temperature']
                    learned_samples = learned_params.get('sample_count', 0)
                    confidence = learned_params.get('confidence', 0.0)
                    logger.debug(f"Applied learned temperature: {learned_temp:.3f} (from {learned_samples} samples)")
            except Exception as e:
                logger.debug(f"Could not load learned parameters: {e}")
        
        # 3. Get quality weights
        quality_weights = self._get_quality_weights()
        
        # 4. Get recent quality insights
        recent_issues = self._get_recent_issues()
        
        # 5. Calculate optimal max_tokens
        if target_words:
            # Allow 2.5x target for natural completion + safety margin
            # 1 token ≈ 0.75 words, so words * 1.33 ≈ tokens
            max_tokens = int(target_words * 2.5 * 1.33)
            max_tokens = max(200, min(max_tokens, 4096))  # Clamp 200-4096
        else:
            max_tokens = 2000  # Reasonable default
        
        return GenerationParameters(
            temperature=learned_temp,
            frequency_penalty=learned_penalties.get('frequency_penalty', 0.0),
            presence_penalty=learned_penalties.get('presence_penalty', 0.0),
            max_tokens=max_tokens,
            quality_weights=quality_weights,
            recent_issues=recent_issues,
            learned_from_samples=learned_samples,
            confidence_score=confidence
        )
    
    def _get_quality_weights(self) -> Dict[str, float]:
        """Get learned quality weights or defaults"""
        default_weights = {
            'winston_ai': 0.4,
            'realism': 0.6,
            'voice_authenticity': 0.3,
            'structural_quality': 0.2,
            'ai_patterns': 0.3
        }
        
        if self._weight_learner:
            try:
                learned_weights = self._weight_learner.get_learned_quality_weights()
                if learned_weights:
                    return learned_weights
            except Exception as e:
                logger.debug(f"Could not load learned weights: {e}")
        
        return default_weights
    
    def _get_recent_issues(self) -> List[Dict[str, any]]:
        """Get recent quality issues from correlation analysis"""
        if self._validation_correlator:
            try:
                insights = self._validation_correlator.get_top_issues(lookback_days=7, limit=3)
                return insights or []
            except Exception as e:
                logger.debug(f"Could not load quality insights: {e}")
        
        return []
    
    def display_insights(self, params: GenerationParameters) -> None:
        """
        Display parameter insights for user visibility.
        
        Args:
            params: GenerationParameters to display
        """
        print(f"🌡️  Generation Parameters:")
        print(f"   • temperature: {params.temperature:.3f}")
        print(f"   • frequency_penalty: {params.frequency_penalty:.2f}")
        print(f"   • presence_penalty: {params.presence_penalty:.2f}")
        print(f"   • max_tokens: {params.max_tokens}")
        
        if params.learned_from_samples > 0:
            print(f"   • Learned from {params.learned_from_samples} samples (confidence: {params.confidence_score:.1%})")
        
        if params.recent_issues:
            print(f"\n💡 Recent Quality Insights:")
            for insight in params.recent_issues:
                print(f"   ⚠️  {insight['issue']}: {insight['impact']:+.1f} impact on Winston")
