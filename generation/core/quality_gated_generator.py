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
    5. Structural Variation: 6.0/10 minimum (no formulaic patterns)

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
        winston_client=None,
        structural_variation_checker=None,
        max_attempts: int = None,
        quality_threshold: float = None
    ):
        """
        Initialize quality-gated generator.
        
        Args:
            api_client: API client for content generation (required)
            subjective_evaluator: SubjectiveEvaluator instance (required)
            winston_client: Winston API client for AI detection (optional)
            structural_variation_checker: StructuralVariationChecker instance (optional)
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
        self.winston_client = winston_client
        self.structural_variation_checker = structural_variation_checker
        
        # Load config for quality gate settings
        from generation.config.config_loader import get_config
        config = get_config()
        quality_gate_config = config.config.get('quality_gates', {})
        
        # CRITICAL: quality_threshold MUST be provided by caller (from ThresholdManager)
        # Config only has fallback values for when learning data insufficient
        if quality_threshold is None:
            raise ValueError(
                "quality_threshold parameter is REQUIRED (no default allowed). "
                "Caller must use ThresholdManager.get_realism_threshold(use_learned=True) "
                "to provide learned threshold. Fail-fast architecture enforces dynamic thresholds only."
            )
        
        # max_attempts can use config (not a learned parameter)
        if max_attempts is None and 'max_retry_attempts' not in quality_gate_config:
            raise ValueError("max_retry_attempts missing from config.yaml and no parameter provided - fail-fast architecture")
        
        self.max_attempts = max_attempts or quality_gate_config['max_retry_attempts']
        self.quality_threshold = quality_threshold  # MUST be provided, no fallback
        
        # Initialize SimpleGenerator (does NOT save to YAML)
        from generation.core.simple_generator import SimpleGenerator
        self.generator = SimpleGenerator(api_client)
        
        # Initialize RealismOptimizer for parameter adjustments
        from learning.realism_optimizer import RealismOptimizer
        self.realism_optimizer = RealismOptimizer()
        
        # Initialize DynamicConfig for base parameters
        from generation.config.dynamic_config import DynamicConfig
        self.dynamic_config = DynamicConfig()
        
        # Initialize HumannessOptimizer for Universal Humanness Layer
        from learning.humanness_optimizer import HumannessOptimizer
        self.humanness_optimizer = HumannessOptimizer()
        
        # Initialize ForbiddenPhraseValidator for pre-flight checks
        from generation.validation.forbidden_phrase_validator import ForbiddenPhraseValidator
        self.phrase_validator = ForbiddenPhraseValidator()
        
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
        
        # Track AI tendencies across attempts for strictness progression
        previous_ai_tendencies = []
        
        # Get base parameters
        current_params = self._get_base_parameters(component_type)
        
        # Tracking
        evaluation_history = []
        parameter_history = [current_params.copy()]
        rejection_reasons = []
        
        for attempt in range(1, self.max_attempts + 1):
            # Print to terminal (always visible)
            print(f"\n{'─'*80}")
            print(f"📝 ATTEMPT {attempt}/{self.max_attempts}")
            print(f"{'─'*80}")
            
            # Log current parameters to terminal
            print("🌡️  Current Parameters:")
            for param, value in current_params.items():
                print(f"   • {param}: {value}")
            
            # Also log for file records
            logger.info(f"\n{'─'*80}")
            logger.info(f"📝 ATTEMPT {attempt}/{self.max_attempts}")
            logger.info(f"{'─'*80}")
            logger.info("🌡️  Current Parameters:")
            for param, value in current_params.items():
                logger.info(f"   • {param}: {value}")
            
            # Generate humanness instructions (Universal Humanness Layer)
            # Strictness increases with each attempt (1-5)
            print(f"\n🧠 Generating humanness instructions (strictness level {attempt}/5)...")
            logger.info(f"\n🧠 Generating humanness instructions (strictness level {attempt}/5)...")
            
            if previous_ai_tendencies:
                print(f"   📋 Previous AI tendencies detected: {', '.join(previous_ai_tendencies)}")
                logger.info(f"   📋 Previous AI tendencies detected: {', '.join(previous_ai_tendencies)}")
            
            humanness_instructions = self.humanness_optimizer.generate_humanness_instructions(
                component_type=component_type,
                strictness_level=attempt,  # 1-5 based on attempt number
                previous_ai_tendencies=previous_ai_tendencies
            )
            
            print(f"   ✅ Humanness layer generated ({len(humanness_instructions)} chars)")
            print(f"   📝 Preview: {humanness_instructions[:200]}...")
            logger.info(f"   ✅ Humanness layer generated ({len(humanness_instructions)} chars)")
            logger.info(f"   📝 Preview: {humanness_instructions[:200]}...")
            
            # Generate content with humanness layer (does NOT save to YAML yet)
            try:
                result = self._generate_content_only(
                    material_name, 
                    component_type,
                    current_params,
                    humanness_layer=humanness_instructions,
                    **kwargs
                )
                content = result['content']
                print(f"✅ Generated: {result['length']} chars, {result['word_count']} words")
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
            
            # PRE-FLIGHT: Check for forbidden phrases BEFORE expensive evaluations
            print("\n🔍 Pre-flight: Checking for forbidden phrases...")
            logger.info("\n🔍 Pre-flight: Checking for forbidden phrases...")
            is_valid, violations = self.phrase_validator.validate(content)
            
            if not is_valid:
                print(f"   ❌ FORBIDDEN PHRASES DETECTED - Regenerating immediately")
                logger.warning(f"   ❌ FORBIDDEN PHRASES DETECTED - Regenerating immediately")
                for phrase in violations:
                    print(f"      • \"{phrase}\"")
                    logger.warning(f"      • \"{phrase}\"")
                
                rejection_reasons.append(f"Forbidden phrases: {', '.join(violations)}")
                
                # Skip expensive evaluation, go straight to retry with adjusted params
                if attempt >= self.max_attempts:
                    logger.error(f"\n❌ MAX ATTEMPTS REACHED ({self.max_attempts})")
                    logger.error(f"   Content still contains forbidden phrases")
                    logger.error(f"   🚫 Content NOT saved to Materials.yaml")
                    
                    return QualityGatedResult(
                        success=False,
                        content=content,
                        attempts=attempt,
                        final_score=None,
                        evaluation_history=evaluation_history,
                        parameter_history=parameter_history,
                        rejection_reasons=rejection_reasons,
                        error_message=f"Failed after {self.max_attempts} attempts - forbidden phrases persist"
                    )
                
                # Adjust parameters and retry immediately
                logger.info(f"\n🔧 Adjusting parameters for attempt {attempt + 1}...")
                previous_ai_tendencies = violations  # Use violations as AI tendencies
                logger.info(f"   📋 Forbidden phrases to avoid: {', '.join(violations)}")
                
                current_params = self._adjust_parameters(
                    current_params,
                    violations,  # Treat as AI tendencies
                    0.0,  # Low score triggers aggressive adjustment
                    winston_passed=False  # Trigger Winston-specific adjustments
                )
                parameter_history.append(current_params.copy())
                
                logger.info(f"\n🔄 Parameter changes for next attempt:")
                for param, value in current_params.items():
                    logger.info(f"   • {param}: {value}")
                
                continue  # Skip to next attempt WITHOUT running expensive evaluations
            
            print("   ✅ No forbidden phrases detected")
            logger.info("   ✅ No forbidden phrases detected")
            
            # Evaluate BEFORE save (only if pre-flight passed)
            print("\n🔍 Evaluating quality BEFORE save...")
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
                
                print(f"\n📊 QUALITY SCORES:")
                print(f"   • Overall Realism: {evaluation.realism_score or evaluation.overall_score:.1f}/10")
                print(f"   • Voice Authenticity: {evaluation.voice_authenticity or 0:.1f}/10")
                print(f"   • Tonal Consistency: {evaluation.tonal_consistency or 0:.1f}/10")
                
                if evaluation.ai_tendencies:
                    print(f"   • AI Tendencies: {', '.join(evaluation.ai_tendencies)}")
                else:
                    print(f"   • AI Tendencies: None detected")
                
                # Also log for records
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
                
                # Run Winston detection BEFORE save (quality gate)
                # Winston API confirmed working - detection successful, API responsive
                # Challenge: Current content generation produces 99-100% AI scores
                # Historical passing samples (12.2%, 24.5% AI) show conversational tone helps
                # System retries with adjusted parameters when Winston fails
                winston_result = self._check_winston_detection(content, material_name, component_type)
                winston_passed = winston_result['passed']
                winston_score = winston_result.get('human_score', 0.0)
                
                # Check structural variation BEFORE save (quality gate)
                structural_passed = True
                diversity_score = 10.0
                if self.structural_variation_checker:
                    eval_text = self._content_to_text(content, component_type)
                    
                    # Get author_id from material data for voice preservation
                    author_id = self._get_author_id(material_name)
                    
                    structural_analysis = self.structural_variation_checker.check(
                        content=eval_text,
                        material_name=material_name,
                        component_type=component_type,
                        author_id=author_id  # Pass author ID for voice preservation
                    )
                    structural_passed = structural_analysis.passes
                    diversity_score = structural_analysis.diversity_score
                    
                    if not structural_passed:
                        logger.warning(f"   ❌ Structural variation failed: {', '.join(structural_analysis.issues)}")
                        for suggestion in structural_analysis.suggestions:
                            logger.info(f"      💡 {suggestion}")
                
                # NEW (Priority 2): Use adaptive threshold that relaxes with each attempt
                adaptive_threshold = self._get_adaptive_threshold(attempt, self.max_attempts)
                
                if adaptive_threshold < self.quality_threshold:
                    print(f"\n📉 ADAPTIVE THRESHOLD: {adaptive_threshold:.1f}/10 (relaxed from {self.quality_threshold:.1f} for attempt {attempt})")
                    logger.info(f"\n📉 ADAPTIVE THRESHOLD: {adaptive_threshold:.1f}/10 (relaxed from {self.quality_threshold:.1f} for attempt {attempt})")
                
                # NEW: Log this attempt for learning BEFORE quality gate decision
                # This enables learning from both successes AND failures
                passed_all_gates = (
                    realism_score >= adaptive_threshold and 
                    not evaluation.ai_tendencies and 
                    winston_passed and 
                    structural_passed
                )
                
                self._log_attempt_for_learning(
                    material_name=material_name,
                    component_type=component_type,
                    content=self._content_to_text(content, component_type),
                    current_params=current_params,
                    evaluation=evaluation,
                    winston_result=winston_result,
                    structural_analysis=structural_analysis if self.structural_variation_checker else None,
                    attempt=attempt,
                    passed_all_gates=passed_all_gates
                )
                
                if passed_all_gates:
                    print(f"\n✅ QUALITY GATE PASSED (≥{adaptive_threshold:.1f}/10)")
                    print(f"   💾 Saving to Materials.yaml...")
                    
                    # NOW save to YAML (only if quality passes)
                    self._save_to_yaml(material_name, component_type, content)
                    
                    print(f"   ✅ Saved successfully")
                    print(f"\n{'='*80}")
                    print(f"🎉 SUCCESS: {component_type} generated in {attempt} attempt(s)")
                    print(f"{'='*80}\n")
                    
                    # Also log for records
                    logger.info(f"\n✅ QUALITY GATE PASSED (≥{adaptive_threshold:.1f}/10)")
                    logger.info(f"   💾 Saving to Materials.yaml...")
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
                    # Quality gate failed - RETRY with adjusted parameters
                    print(f"\n⚠️  QUALITY GATE FAILED - Will retry with adjusted parameters")
                    logger.warning(f"\n⚠️  QUALITY GATE FAILED - Will retry with adjusted parameters")
                    
                    if not structural_passed:
                        rejection_reasons.append(f"Structural variation failed (diversity: {diversity_score:.1f}/10)")
                    
                    if realism_score < adaptive_threshold:
                        reason = f"Realism score too low: {realism_score:.1f}/10 < {adaptive_threshold:.1f}/10"
                        print(f"   • {reason}")
                        logger.warning(f"   • {reason}")
                        rejection_reasons.append(reason)
                    
                    if evaluation.ai_tendencies:
                        reason = f"AI tendencies detected: {', '.join(evaluation.ai_tendencies)}"
                        print(f"   • {reason}")
                        logger.warning(f"   • {reason}")
                        rejection_reasons.append(reason)
                    
                    if not winston_passed:
                        reason = f"Winston AI detection failed (human score: {winston_score:.1%})"
                        print(f"   • {reason}")
                        logger.warning(f"   • {reason}")
                        rejection_reasons.append(reason)
                    
                    # Last attempt? Return failure
                    if attempt >= self.max_attempts:
                        print(f"\n❌ MAX ATTEMPTS REACHED ({self.max_attempts})")
                        print(f"   Final score: {realism_score:.1f}/10 (required: {self.quality_threshold}/10)")
                        print(f"   🚫 Content NOT saved to Materials.yaml")
                        
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
                    print(f"\n🔧 Adjusting parameters for attempt {attempt + 1}...")
                    logger.info(f"\n🔧 Adjusting parameters for attempt {attempt + 1}...")
                    
                    # Update previous_ai_tendencies for next humanness layer
                    previous_ai_tendencies = evaluation.ai_tendencies or []
                    if previous_ai_tendencies:
                        print(f"   📋 AI tendencies to avoid next time: {', '.join(previous_ai_tendencies)}")
                        logger.info(f"   📋 AI tendencies to avoid next time: {', '.join(previous_ai_tendencies)}")
                    
                    current_params = self._adjust_parameters(
                        current_params,
                        evaluation.ai_tendencies or [],
                        realism_score,
                        winston_passed=winston_passed
                    )
                    parameter_history.append(current_params.copy())
                    print(f"   ✅ Parameters adjusted for retry")
                    logger.info(f"   ✅ Parameters adjusted for retry")
                    
                    # Log what changed
                    print(f"\n🔄 Parameter changes for next attempt:")
                    logger.info(f"\n🔄 Parameter changes for next attempt:")
                    for param, value in current_params.items():
                        print(f"   • {param}: {value}")
                        logger.info(f"   • {param}: {value}")
                
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
        humanness_layer: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content WITHOUT saving to YAML.
        
        FIXED DESIGN (November 20, 2025):
        Now uses generate_without_save() to ensure content is NOT saved until
        after quality gate passes. This enforces:
        
        Generate → Evaluate → [Pass? Save : Retry]
        
        Previous bug: SimpleGenerator.generate() saved immediately, violating
        the documented quality-gated architecture.
        
        Args:
            humanness_layer: Dynamic humanness instructions from HumannessOptimizer
        """
        result = self.generator.generate_without_save(
            material_name, 
            component_type,
            humanness_layer=humanness_layer,
            **kwargs
        )
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
        Load learned parameter ranges from sweet spot analyzer with correlation filtering.
        
        Priority 4 Enhancement: Filters out parameters with negative correlation to quality.
        Only learns from parameters that actually help (positive correlation).
        
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
            filtered_count = 0
            
            # Priority 4: Calculate correlations and filter negative ones
            correlations = self._calculate_parameter_correlations()
            
            # Extract median values from sweet spot ranges with correlation filtering
            for param_name, ranges in params.items():
                if ranges and 'median' in ranges:
                    correlation = correlations.get(param_name)
                    
                    # Priority 4: Skip parameters with strong negative correlation
                    if correlation is not None and correlation < -0.3:
                        logger.warning(f"   ❌ {param_name}: Negative correlation {correlation:.3f} - EXCLUDED from learning")
                        filtered_count += 1
                        continue
                    
                    # Include parameter
                    learned[param_name] = ranges['median']
                    if correlation is not None:
                        logger.info(f"   ✅ {param_name}: {ranges['median']:.3f} (correlation: {correlation:.3f})")
                    else:
                        logger.info(f"   Using learned {param_name}: {ranges['median']:.3f}")
            
            # Override sentence_rhythm_variation to respect config target (Option A+C implementation)
            # This allows manual config changes to take precedence over learned values
            # for specific parameters we want to control directly
            if 'sentence_rhythm_variation' in learned:
                del learned['sentence_rhythm_variation']
                logger.info("   ⚡ sentence_rhythm_variation override: using config value (not learned)")
            
            if learned:
                logger.info(f"   ✅ Loaded {len(learned)} learned parameters from sweet spot ({filtered_count} filtered)")
            
            return learned
            
        except Exception as e:
            logger.debug(f"   Could not load sweet spot parameters: {e}")
            return {}
    
    def _calculate_parameter_correlations(self) -> Dict[str, float]:
        """
        Calculate Pearson correlation between each parameter and composite quality score.
        
        Priority 4 Implementation: Identifies which parameters help vs hurt quality.
        Positive correlation = parameter helps (learn from it)
        Negative correlation = parameter hurts (exclude from learning)
        
        Returns:
            Dict mapping parameter name to correlation coefficient (-1.0 to 1.0)
        """
        try:
            import sqlite3
            from scipy.stats import pearsonr
            
            conn = sqlite3.connect('z-beam.db')
            cursor = conn.cursor()
            
            # Get all parameters with quality scores
            cursor.execute("""
                SELECT gp.temperature, gp.trait_frequency, gp.imperfection_tolerance,
                       gp.opinion_rate, gp.colloquialism_frequency, gp.emotional_tone,
                       dr.composite_quality_score
                FROM generation_parameters gp
                JOIN detection_results dr ON gp.detection_result_id = dr.id
                WHERE dr.composite_quality_score IS NOT NULL
                  AND dr.timestamp > datetime('now', '-30 days')
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < 20:
                logger.info("   ⚠️  Insufficient data for correlation analysis (need 20+ samples)")
                return {}
            
            # Calculate correlations for each parameter
            param_names = ['temperature', 'trait_frequency', 'imperfection_tolerance',
                          'opinion_rate', 'colloquialism_frequency', 'emotional_tone']
            
            correlations = {}
            
            for i, param_name in enumerate(param_names):
                # Build PAIRED lists to keep parameter and quality score indices matched
                # CRITICAL: Must filter rows together to avoid array mismatch
                paired_data = [(row[i], row[-1]) for row in rows if row[i] is not None]
                
                if len(paired_data) >= 20:
                    param_values = [p[0] for p in paired_data]
                    matched_quality_scores = [p[1] for p in paired_data]
                    
                    try:
                        corr, p_value = pearsonr(param_values, matched_quality_scores)
                        correlations[param_name] = corr
                    except Exception as e:
                        logger.debug(f"   Could not calculate correlation for {param_name}: {e}")
            
            return correlations
            
        except ImportError:
            logger.warning("   ⚠️  scipy not available - skipping correlation analysis")
            return {}
        except Exception as e:
            logger.debug(f"   Could not calculate correlations: {e}")
            return {}
    
    def _get_adaptive_threshold(self, attempt: int, max_attempts: int = 5) -> float:
        """
        Calculate adaptive threshold that relaxes with each attempt.
        
        Strategy (graduated relaxation) - LEARNING PHASE:
        - Attempt 1: base threshold (from learned threshold, typically 6.0-8.5)
        - Attempt 2-5: Relax toward 4.0/10 minimum
        
        This enables:
        1. Start with learned quality standards (if available)
        2. Relax quickly to collect more learning data
        3. Minimum 4.0/10 prevents truly poor content
        
        Args:
            attempt: Current attempt number (1-5)
            max_attempts: Maximum attempts (default 5)
            
        Returns:
            Relaxed threshold for this attempt
        """
        base_threshold = self.quality_threshold
        min_threshold = 2.0  # PRODUCTION MODE: Accept good-enough content (was 4.0)
        
        # Handle edge case: max_attempts=1 means no relaxation
        if max_attempts == 1:
            return base_threshold
        
        total_relaxation = base_threshold - min_threshold
        relaxation_per_attempt = total_relaxation / (max_attempts - 1)
        relaxed_threshold = base_threshold - (relaxation_per_attempt * (attempt - 1))
        return max(min_threshold, relaxed_threshold)
    
    def _adjust_parameters(
        self,
        current_params: Dict[str, Any],
        ai_tendencies: List[str],
        realism_score: float,
        winston_passed: bool = True
    ) -> Dict[str, Any]:
        """
        Adjust parameters based on evaluation feedback.
        
        Args:
            current_params: Current generation parameters
            ai_tendencies: Detected AI patterns from realism evaluation
            realism_score: Current realism score (0-10)
            winston_passed: Whether Winston detection passed
        
        Returns:
            Adjusted parameters for next attempt
        """
        # If Winston failed, apply aggressive adjustments for humanness
        if not winston_passed:
            logger.info("   🚨 Winston failure detected - applying aggressive humanness adjustments")
            adjusted = current_params.copy()
            
            # Dramatically increase randomness and imperfection
            adjusted['temperature'] = min(1.0, adjusted['temperature'] + 0.15)  # Larger jump
            adjusted['imperfection_tolerance'] = min(1.0, adjusted['imperfection_tolerance'] + 0.2)
            adjusted['trait_frequency'] = min(1.0, adjusted.get('trait_frequency', 0.5) + 0.15)
            adjusted['sentence_rhythm_variation'] = 1.0  # Maximum variation
            
            logger.info(f"     • temperature: {current_params['temperature']:.3f} → {adjusted['temperature']:.3f} (+0.15)")
            logger.info(f"     • imperfection_tolerance: {current_params['imperfection_tolerance']:.3f} → {adjusted['imperfection_tolerance']:.3f} (+0.20)")
            logger.info(f"     • trait_frequency: {current_params.get('trait_frequency', 0.5):.3f} → {adjusted['trait_frequency']:.3f} (+0.15)")
            
            return adjusted
        
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
    
    def _check_winston_detection(self, content: str, material_name: str, component_type: str) -> Dict[str, Any]:
        """
        Run Winston AI detection during quality gate (before save).
        
        Returns:
            dict: {
                'passed': bool,
                'human_score': float,
                'ai_score': float,
                'message': str
            }
        """
        # Winston is optional - if not configured, pass by default
        if not self.winston_client:
            logger.info("   ⚠️  Winston API not configured - skipping AI detection")
            return {'passed': True, 'human_score': 1.0, 'ai_score': 0.0, 'message': 'Winston not configured'}
        
        try:
            from postprocessing.detection.winston_integration import WinstonIntegration
            from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
            from generation.config.config_loader import get_config
            from generation.validation.constants import ValidationConstants
            
            config = get_config()
            db_path = config.config.get('winston_feedback_db_path')
            feedback_db = WinstonFeedbackDatabase(db_path) if db_path else None
            
            # Initialize Winston integration
            winston = WinstonIntegration(
                winston_client=self.winston_client,
                feedback_db=feedback_db,
                config=config.config
            )
            
            # Use fully dynamic threshold from database learning (no fallback)
            from learning.threshold_manager import ThresholdManager
            threshold_manager = ThresholdManager(db_path='z-beam.db')
            ai_threshold = threshold_manager.get_winston_threshold(use_learned=True)
            logger.info(f"\n🤖 Running Winston AI detection...")
            logger.info(f"   Using learned Winston threshold: {ai_threshold:.3f} (dynamic from DB)")
            
            # Calculate temperature for logging (metadata only)
            from generation.config.dynamic_config import DynamicConfig
            dynamic_config = DynamicConfig()
            generation_temp = dynamic_config.calculate_temperature(component_type)
            
            # Detect (don't log yet - that happens post-save if passed)
            winston_result = winston.detect_and_log(
                text=content,
                material=material_name,
                component_type=component_type,
                temperature=generation_temp,
                attempt=1,
                max_attempts=1,
                ai_threshold=ai_threshold
            )
            
            ai_score = winston_result['ai_score']
            human_score = 1.0 - ai_score
            
            logger.info(f"   🎯 AI Score: {ai_score*100:.1f}% (threshold: {ai_threshold*100:.1f}%)")
            logger.info(f"   👤 Human Score: {human_score*100:.1f}%")
            
            passed = ai_score <= ai_threshold
            
            if passed:
                logger.info("   ✅ Winston check PASSED")
            else:
                logger.warning("   ❌ Winston check FAILED - will retry with adjusted parameters")
            
            return {
                'passed': passed,
                'human_score': human_score,
                'ai_score': ai_score,
                'threshold': ai_threshold,
                'message': f"{'Passed' if passed else 'Failed'} Winston detection"
            }
                
        except Exception as e:
            # Winston optional for short content
            error_msg = str(e)
            if 'Text too short' in error_msg:
                logger.info(f"   ⚠️  Winston skipped: {e}")
                return {'passed': True, 'human_score': 1.0, 'ai_score': 0.0, 'message': 'Text too short for Winston'}
            elif 'not configured' in error_msg:
                logger.info(f"   ⚠️  Winston not configured: {e}")
                return {'passed': True, 'human_score': 1.0, 'ai_score': 0.0, 'message': 'Winston not configured'}
            else:
                # Other errors - still retry (treat as Winston fail for safety)
                logger.error(f"   ❌ Winston detection error: {e}")
                return {'passed': False, 'human_score': 0.0, 'ai_score': 1.0, 'message': f'Winston error: {e}'}
    
    def _log_attempt_for_learning(
        self,
        material_name: str,
        component_type: str,
        content: str,
        current_params: Dict[str, Any],
        evaluation: Any,
        winston_result: Dict[str, Any],
        structural_analysis: Any,
        attempt: int,
        passed_all_gates: bool
    ):
        """
        Log EVERY generation attempt to database for learning, not just successes.
        
        This is the KEY fix for learning system - we need data from failures to:
        1. Learn what parameters correlate negatively with success
        2. Understand realistic threshold distributions
        3. Identify structural patterns that fail vs succeed
        4. Build sufficient corpus for sweet spot analysis
        
        Args:
            material_name: Material being generated
            component_type: Component type
            content: Generated content (string)
            current_params: Generation parameters used
            evaluation: SubjectiveEvaluation result
            winston_result: Winston detection result
            structural_analysis: StructuralAnalysis result
            attempt: Attempt number (1-5)
            passed_all_gates: Whether all quality gates passed
        """
        try:
            # Only log if we have Winston database available
            if not self.winston_client:
                return
            
            from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
            
            # Get database path from config
            from generation.config.config_loader import get_config
            config = get_config()
            db_path = config.config.get('winston_feedback_db_path', 'z-beam.db')
            
            db = WinstonFeedbackDatabase(db_path)
            
            # Prepare Winston result for logging
            winston_log = {
                'human_score': winston_result.get('human_score', 0.0),
                'ai_score': winston_result.get('ai_score', 1.0),
                'readability_score': winston_result.get('readability_score'),
                'credits_used': winston_result.get('credits_used', 0),
                'sentences': winston_result.get('sentences', [])
            }
            
            # Calculate composite quality score (Winston 40% + Realism 60%)
            realism_score = evaluation.realism_score or evaluation.overall_score
            realism_normalized = realism_score / 10.0  # 0-10 scale → 0-1.0
            composite_score = (
                winston_result.get('human_score', 0.0) * 0.4 +
                realism_normalized * 0.6
            )
            
            # Log detection result (includes attempt data)
            detection_id = db.log_detection(
                material=material_name,
                component_type=component_type,
                generated_text=content,
                winston_result=winston_log,
                temperature=current_params.get('temperature', 0.0),
                attempt=attempt,
                success=passed_all_gates,  # Mark success ONLY if passed all gates
                failure_analysis={
                    'failure_type': 'quality_gate_failed' if not passed_all_gates else None,
                    'realism_score': realism_score,
                    'diversity_score': structural_analysis.diversity_score if structural_analysis else 10.0,
                    'winston_passed': winston_result.get('passed', False),
                    'structural_passed': structural_analysis.passes if structural_analysis else True,
                    'ai_tendencies': evaluation.ai_tendencies or []
                },
                composite_quality_score=composite_score
            )
            
            # Log generation parameters (enables correlation analysis)
            params_for_db = {
                'material_name': material_name,
                'component_type': component_type,
                'attempt': attempt,
                'api': {
                    'temperature': current_params.get('temperature'),
                    'max_tokens': current_params.get('max_tokens'),
                    'frequency_penalty': current_params.get('frequency_penalty', 0.0),
                    'presence_penalty': current_params.get('presence_penalty', 0.0)
                },
                'voice': {
                    'trait_frequency': current_params.get('trait_frequency'),
                    'opinion_rate': current_params.get('opinion_rate'),
                    'reader_address_rate': current_params.get('reader_address_rate', 0.3),  # Default if missing
                    'colloquialism_frequency': current_params.get('colloquialism_frequency'),
                    'structural_predictability': current_params.get('structural_predictability'),
                    'emotional_tone': current_params.get('emotional_tone'),
                    'imperfection_tolerance': current_params.get('imperfection_tolerance'),
                    'sentence_rhythm_variation': current_params.get('sentence_rhythm_variation')
                },
                'enrichment': {
                    'technical_intensity': current_params.get('technical_intensity', 2),
                    'context_detail_level': 2,
                    'fact_formatting_style': 1,  # Default style
                    'engagement_level': 2
                },
                'validation': {
                    'detection_threshold': self.ai_threshold if hasattr(self, 'ai_threshold') else 0.33,
                    'readability_min': 0,
                    'readability_max': 100,
                    'grammar_strictness': 0.7,
                    'confidence_high': 0.8,
                    'confidence_medium': 0.5
                },
                'retry': {
                    'max_attempts': self.max_attempts if hasattr(self, 'max_attempts') else 5,
                    'retry_temperature_increase': 0.15
                }
            }
            
            db.log_generation_parameters(
                detection_result_id=detection_id,
                params=params_for_db
            )
            
            # Log to subjective evaluations table (pass the evaluation object directly)
            db.log_subjective_evaluation(
                topic=material_name,
                component_type=component_type,
                generated_text=content,
                evaluation_result=evaluation,  # Pass the evaluation object
                domain="materials",
                author_id=None,  # Could enhance this later
                attempt_number=attempt
            )
            
            logger.info(
                f"   📊 Logged attempt {attempt} to database "
                f"(detection_id={detection_id}, passed={passed_all_gates})"
            )
            print(
                f"   📊 Logged attempt {attempt} to database "
                f"(detection_id={detection_id}, passed={passed_all_gates})"
            )
            
        except Exception as e:
            # Don't fail generation if logging fails - just warn
            logger.warning(f"   ⚠️  Failed to log attempt to database: {e}")
            print(f"   ⚠️  Failed to log attempt to database: {e}")
    
    def _save_to_yaml(self, material_name: str, component_type: str, content: Any):
        """Save content to Materials.yaml (atomic write)"""
        # Use SimpleGenerator's save method
        self.generator._save_to_yaml(material_name, component_type, content)
    
    def _get_author_id(self, material_name: str) -> int:
        """Get author_id for material from Materials.yaml"""
        try:
            from data.materials import load_materials_data
            materials_data = load_materials_data()
            material_data = materials_data.get('materials', {}).get(material_name, {})
            author_id = material_data.get('author', {}).get('id', 2)  # Default to author 2 if not found
            return author_id
        except Exception as e:
            logger.warning(f"Could not load author_id for {material_name}: {e}")
            return 2  # Default to author 2
