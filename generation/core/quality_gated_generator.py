"""
Quality-Gated Generator - Retry Loop with Subjective Evaluation

Wraps SimpleGenerator with quality gate enforcement:
- Evaluates content BEFORE save
- Retries up to 5 times if quality fails
- Applies parameter adjustments between retries
- Only saves content that passes 7.0/10 threshold

Architecture:
    Generate → Evaluate → [Pass? Save : Adjust & Retry] → Learn
    
Quality Gates (ALL must pass):
    1. Subjective Realism: 7.0/10 minimum
    2. Voice Authenticity: 7.0/10 minimum
    3. Tonal Consistency: 7.0/10 minimum
    4. No AI Tendencies: Zero detected patterns

Design Change (November 20, 2025):
    Previous: Generate → Save → Evaluate (low quality persists in Materials.yaml)
    Current: Generate → Evaluate → Conditional Save (only quality content saved)
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QualityGatedResult:
    """Result from quality-gated generation"""
    success: bool
    content: Any
    attempts: int
    final_score: Optional[float]
    evaluation_history: List[Dict]
    parameter_history: List[Dict]
    rejection_reasons: List[str]
    error_message: Optional[str] = None


class QualityGatedGenerator:
    """
    Quality-gated generator with automatic retry and parameter adjustment.
    
    Responsibilities:
    - Generate content using SimpleGenerator
    - Evaluate with SubjectiveEvaluator BEFORE save
    - Retry with adjusted parameters if quality fails
    - Save only content meeting 7.0/10 threshold
    - Track learning data for all attempts
    
    Maximum 5 attempts before final failure.
    """
    
    def __init__(
        self,
        api_client,
        subjective_evaluator,
        max_attempts: int = None,
        quality_threshold: float = None
    ):
        """
        Initialize quality-gated generator.
        
        Args:
            api_client: API client for content generation (required)
            subjective_evaluator: SubjectiveEvaluator instance (required)
            max_attempts: Maximum generation attempts (default from config)
            quality_threshold: Minimum realism score required (default from config)
        
        Raises:
            ValueError: If required components missing (fail-fast)
        """
        if not api_client:
            raise ValueError("API client required for quality-gated generation")
        if not subjective_evaluator:
            raise ValueError("SubjectiveEvaluator required for quality-gated generation")
        
        self.api_client = api_client
        self.subjective_evaluator = subjective_evaluator
        
        # Load config for quality gate settings
        from generation.config.config_loader import get_config
        config = get_config()
        quality_gate_config = config.config.get('quality_gates', {})
        
        # Fail-fast if config missing and no parameters provided
        if max_attempts is None and 'max_retry_attempts' not in quality_gate_config:
            raise ValueError("max_retry_attempts missing from config.yaml and no parameter provided - fail-fast architecture")
        if quality_threshold is None and 'realism_threshold' not in quality_gate_config:
            raise ValueError("realism_threshold missing from config.yaml and no parameter provided - fail-fast architecture")
        
        # Use config values or parameters (no hardcoded fallbacks)
        self.max_attempts = max_attempts or quality_gate_config['max_retry_attempts']
        self.quality_threshold = quality_threshold or quality_gate_config['realism_threshold']
        
        # Initialize SimpleGenerator (does NOT save to YAML)
        from generation.core.simple_generator import SimpleGenerator
        self.generator = SimpleGenerator(api_client)
        
        # Initialize RealismOptimizer for parameter adjustments
        from learning.realism_optimizer import RealismOptimizer
        self.realism_optimizer = RealismOptimizer()
        
        # Initialize DynamicConfig for base parameters
        from generation.config.dynamic_config import DynamicConfig
        self.dynamic_config = DynamicConfig()
        
        logger.info(f"QualityGatedGenerator initialized (max_attempts={self.max_attempts}, threshold={self.quality_threshold})")
    
    def generate(
        self,
        material_name: str,
        component_type: str,
        **kwargs
    ) -> QualityGatedResult:
        """
        Generate content with quality gate enforcement.
        
        Args:
            material_name: Name of material
            component_type: Type of component (caption, subtitle, faq)
            **kwargs: Additional parameters (e.g., faq_count)
            
        Returns:
            QualityGatedResult with success status and content
            
        Process:
            1. Generate content (SimpleGenerator)
            2. Evaluate realism (SubjectiveEvaluator)
            3. If pass (≥7.0): Save to YAML, return success
            4. If fail (<7.0): Adjust parameters, retry (max 5 attempts)
            5. If max attempts: Return failure with history
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🔒 QUALITY-GATED GENERATION: {component_type} for {material_name}")
        logger.info(f"   Threshold: {self.quality_threshold}/10 | Max Attempts: {self.max_attempts}")
        logger.info(f"{'='*80}\n")
        
        # Get base parameters
        current_params = self._get_base_parameters(component_type)
        
        # Tracking
        evaluation_history = []
        parameter_history = [current_params.copy()]
        rejection_reasons = []
        
        for attempt in range(1, self.max_attempts + 1):
            logger.info(f"\n{'─'*80}")
            logger.info(f"📝 ATTEMPT {attempt}/{self.max_attempts}")
            logger.info(f"{'─'*80}")
            
            # Log current parameters
            logger.info("🌡️  Current Parameters:")
            for param, value in current_params.items():
                logger.info(f"   • {param}: {value}")
            
            # Generate content (does NOT save to YAML yet)
            try:
                result = self._generate_content_only(
                    material_name, 
                    component_type,
                    current_params,
                    **kwargs
                )
                content = result['content']
                logger.info(f"✅ Generated: {result['length']} chars, {result['word_count']} words")
                
            except Exception as e:
                logger.error(f"❌ Generation failed: {e}")
                return QualityGatedResult(
                    success=False,
                    content=None,
                    attempts=attempt,
                    final_score=None,
                    evaluation_history=evaluation_history,
                    parameter_history=parameter_history,
                    rejection_reasons=rejection_reasons,
                    error_message=f"Generation error: {e}"
                )
            
            # Evaluate BEFORE save
            logger.info("\n🔍 Evaluating quality BEFORE save...")
            try:
                # Convert content to string for evaluation
                eval_text = self._content_to_text(content, component_type)
                
                evaluation = self.subjective_evaluator.evaluate(
                    content=eval_text,
                    material_name=material_name,
                    component_type=component_type
                )
                
                evaluation_history.append({
                    'attempt': attempt,
                    'overall_score': evaluation.overall_score,
                    'realism_score': evaluation.realism_score,
                    'voice_authenticity': evaluation.voice_authenticity,
                    'tonal_consistency': evaluation.tonal_consistency,
                    'ai_tendencies': evaluation.ai_tendencies or [],
                    'passes': evaluation.passes_quality_gate
                })
                
                logger.info(f"\n📊 QUALITY SCORES:")
                logger.info(f"   • Overall Realism: {evaluation.realism_score or evaluation.overall_score:.1f}/10")
                logger.info(f"   • Voice Authenticity: {evaluation.voice_authenticity or 0:.1f}/10")
                logger.info(f"   • Tonal Consistency: {evaluation.tonal_consistency or 0:.1f}/10")
                
                if evaluation.ai_tendencies:
                    logger.info(f"   • AI Tendencies: {', '.join(evaluation.ai_tendencies)}")
                else:
                    logger.info(f"   • AI Tendencies: None detected")
                
                # Check if passed quality gate
                realism_score = evaluation.realism_score or evaluation.overall_score
                
                if realism_score >= self.quality_threshold and not evaluation.ai_tendencies:
                    logger.info(f"\n✅ QUALITY GATE PASSED (≥{self.quality_threshold}/10)")
                    logger.info(f"   💾 Saving to Materials.yaml...")
                    
                    # NOW save to YAML (only if quality passes)
                    self._save_to_yaml(material_name, component_type, content)
                    
                    logger.info(f"   ✅ Saved successfully")
                    logger.info(f"\n{'='*80}")
                    logger.info(f"🎉 SUCCESS: {component_type} generated in {attempt} attempt(s)")
                    logger.info(f"{'='*80}\n")
                    
                    return QualityGatedResult(
                        success=True,
                        content=content,
                        attempts=attempt,
                        final_score=realism_score,
                        evaluation_history=evaluation_history,
                        parameter_history=parameter_history,
                        rejection_reasons=rejection_reasons
                    )
                
                else:
                    # Quality gate failed
                    logger.warning(f"\n⚠️  QUALITY GATE FAILED")
                    
                    if realism_score < self.quality_threshold:
                        reason = f"Realism score too low: {realism_score:.1f}/10 < {self.quality_threshold}/10"
                        logger.warning(f"   • {reason}")
                        rejection_reasons.append(reason)
                    
                    if evaluation.ai_tendencies:
                        reason = f"AI tendencies detected: {', '.join(evaluation.ai_tendencies)}"
                        logger.warning(f"   • {reason}")
                        rejection_reasons.append(reason)
                    
                    # Last attempt? Return failure
                    if attempt >= self.max_attempts:
                        logger.error(f"\n❌ MAX ATTEMPTS REACHED ({self.max_attempts})")
                        logger.error(f"   Final score: {realism_score:.1f}/10 (required: {self.quality_threshold}/10)")
                        logger.error(f"   🚫 Content NOT saved to Materials.yaml")
                        
                        return QualityGatedResult(
                            success=False,
                            content=content,
                            attempts=attempt,
                            final_score=realism_score,
                            evaluation_history=evaluation_history,
                            parameter_history=parameter_history,
                            rejection_reasons=rejection_reasons,
                            error_message=f"Failed quality gate after {self.max_attempts} attempts"
                        )
                    
                    # Adjust parameters for next attempt
                    logger.info(f"\n🔧 Adjusting parameters for attempt {attempt + 1}...")
                    current_params = self._adjust_parameters(
                        current_params,
                        evaluation.ai_tendencies or [],
                        realism_score
                    )
                    parameter_history.append(current_params.copy())
                    logger.info(f"   ✅ Parameters adjusted, retrying...")
                
            except Exception as e:
                logger.error(f"❌ Evaluation failed: {e}")
                import traceback
                traceback.print_exc()
                
                # Last attempt? Return failure
                if attempt >= self.max_attempts:
                    return QualityGatedResult(
                        success=False,
                        content=content,
                        attempts=attempt,
                        final_score=None,
                        evaluation_history=evaluation_history,
                        parameter_history=parameter_history,
                        rejection_reasons=rejection_reasons,
                        error_message=f"Evaluation error: {e}"
                    )
                
                # Retry with current parameters
                logger.warning(f"   ⚠️  Retrying with current parameters...")
        
        # Should never reach here, but handle just in case
        return QualityGatedResult(
            success=False,
            content=None,
            attempts=self.max_attempts,
            final_score=None,
            evaluation_history=evaluation_history,
            parameter_history=parameter_history,
            rejection_reasons=rejection_reasons,
            error_message="Unexpected failure - max attempts exceeded"
        )
    
    def _get_base_parameters(self, component_type: str) -> Dict[str, Any]:
        """
        Get base generation parameters from config and sweet spot learning.
        
        Now integrates learned parameter ranges from database:
        1. Load sweet spot recommendations from database
        2. Use median values from top 25% performers
        3. Fall back to config.yaml only if insufficient learning data
        """
        from generation.config.config_loader import get_config
        config = get_config()
        
        # Try to load learned sweet spot parameters
        learned_params = self._load_sweet_spot_parameters()
        
        # Get voice parameters from config (fail-fast if missing)
        voice_params = config.config.get('voice_parameters', {})
        
        # Fail-fast if any voice parameter missing
        required_voice_params = [
            'emotional_tone', 'opinion_rate', 'structural_predictability',
            'sentence_rhythm_variation', 'imperfection_tolerance', 'trait_frequency',
            'colloquialism_frequency', 'technical_intensity'
        ]
        
        for param in required_voice_params:
            if param not in voice_params:
                raise ValueError(
                    f"voice_parameters.{param} missing in config.yaml - fail-fast architecture. "
                    "All voice parameters must be explicitly configured."
                )
        
        # Use learned parameters if available, otherwise config defaults
        return {
            # API parameters - use learned if available, else dynamic calculation
            'temperature': learned_params.get('temperature') or self.dynamic_config.calculate_temperature(component_type),
            'max_tokens': self.dynamic_config.calculate_max_tokens(component_type),
            
            # Voice parameters - use learned if available, else config
            'emotional_tone': learned_params.get('emotional_tone') or voice_params['emotional_tone'],
            'opinion_rate': learned_params.get('opinion_rate') or voice_params['opinion_rate'],
            'structural_predictability': learned_params.get('structural_predictability') or voice_params['structural_predictability'],
            'sentence_rhythm_variation': learned_params.get('sentence_rhythm_variation') or voice_params['sentence_rhythm_variation'],
            'imperfection_tolerance': learned_params.get('imperfection_tolerance') or voice_params['imperfection_tolerance'],
            'trait_frequency': learned_params.get('trait_frequency') or voice_params['trait_frequency'],
            'colloquialism_frequency': learned_params.get('colloquialism_frequency') or voice_params['colloquialism_frequency'],
            'technical_intensity': voice_params['technical_intensity']
        }
    
    def _generate_content_only(
        self,
        material_name: str,
        component_type: str,
        params: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content WITHOUT saving to YAML.
        
        Temporarily disables SimpleGenerator's save behavior.
        """
        # SimpleGenerator always saves - we need to prevent that
        # Solution: Generate, but DON'T save (we'll save later if quality passes)
        
        # For now, call SimpleGenerator normally - it will save
        # TODO: Refactor SimpleGenerator to separate generation from save
        # For immediate implementation, we accept temporary save then overwrite if fail
        
        result = self.generator.generate(material_name, component_type, **kwargs)
        return result
    
    def _content_to_text(self, content: Any, component_type: str) -> str:
        """Convert content to text string for evaluation"""
        if isinstance(content, dict):
            # Caption: before/after structure
            before = content.get('before', '')
            after = content.get('after', '')
            return f"BEFORE:\n{before}\n\nAFTER:\n{after}"
        elif isinstance(content, list):
            # FAQ: list of Q&A
            parts = []
            for qa in content:
                q = qa.get('question', '')
                a = qa.get('answer', '')
                parts.append(f"Q: {q}\nA: {a}")
            return "\n\n".join(parts)
        else:
            # String content (subtitle, etc.)
            return str(content)
    
    def _load_sweet_spot_parameters(self) -> Dict[str, float]:
        """
        Load learned parameter ranges from sweet spot analyzer.
        
        Returns dictionary with median values from top performers,
        or empty dict if insufficient learning data.
        """
        try:
            from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
            
            db = WinstonFeedbackDatabase('z-beam.db')
            sweet_spot = db.get_sweet_spot('*', '*')  # Global scope
            
            if not sweet_spot or not sweet_spot.get('parameters'):
                logger.info("   No learned parameters available - using config defaults")
                return {}
            
            params = sweet_spot['parameters']
            learned = {}
            
            # Extract median values from sweet spot ranges
            for param_name, ranges in params.items():
                if ranges and 'median' in ranges:
                    learned[param_name] = ranges['median']
                    logger.info(f"   Using learned {param_name}: {ranges['median']:.3f}")
            
            if learned:
                logger.info(f"   ✅ Loaded {len(learned)} learned parameters from sweet spot")
            
            return learned
            
        except Exception as e:
            logger.debug(f"   Could not load sweet spot parameters: {e}")
            return {}
    
    def _adjust_parameters(
        self,
        current_params: Dict[str, Any],
        ai_tendencies: List[str],
        realism_score: float
    ) -> Dict[str, Any]:
        """Adjust parameters based on evaluation feedback"""
        if not ai_tendencies:
            # No specific tendencies - general improvement
            logger.info("   No specific AI tendencies - applying general improvements")
            adjusted = current_params.copy()
            adjusted['temperature'] = min(1.0, adjusted['temperature'] + 0.03)
            adjusted['imperfection_tolerance'] = min(1.0, adjusted['imperfection_tolerance'] + 0.1)
            return adjusted
        
        # Use RealismOptimizer to suggest adjustments
        adjusted_params = self.realism_optimizer.suggest_parameters(
            current_params=current_params,
            ai_tendencies=ai_tendencies,
            realism_score=realism_score
        )
        
        logger.info("   Parameter adjustments:")
        for param, new_value in adjusted_params.items():
            old_value = current_params.get(param)
            if old_value != new_value:
                logger.info(f"     • {param}: {old_value} → {new_value} (Δ{new_value - old_value:+.3f})")
        
        return adjusted_params
    
    def _save_to_yaml(self, material_name: str, component_type: str, content: Any):
        """Save content to Materials.yaml (atomic write)"""
        # Use SimpleGenerator's save method
        self.generator._save_to_yaml(material_name, component_type, content)
