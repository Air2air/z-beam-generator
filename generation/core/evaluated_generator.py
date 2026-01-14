"""
Quality-Evaluated Generator - Single-Pass with Learning

Single-pass content generation with post-save quality evaluation and learning.
NO gating, NO retries - generate once, save, evaluate for learning only.

Architecture:
    Generate → Save → Evaluate → Log for Learning → Done
    
Quality Evaluation (for learning, NOT blocking):
    1. Subjective Realism: Score logged for learning analysis
    2. Voice Authenticity: Logged for pattern analysis
    3. Tonal Consistency: Logged for quality trends
    4. AI Tendencies: Logged to identify problematic patterns
    5. Winston AI Detection: Logged for human-score trends
    6. Structural Variation: Logged for diversity analysis

Design: Single-pass approach - generate once, save immediately, then evaluate.
        Evaluation data feeds learning system for continuous improvement.
        100% completion rate, fast generation, quality improvement over time.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Import voice compliance validator
try:
    from shared.voice.post_processor import VoicePostProcessor
    VOICE_VALIDATION_AVAILABLE = True
except ImportError:
    VOICE_VALIDATION_AVAILABLE = False
    logger.warning("VoicePostProcessor not available - voice compliance validation disabled")


@dataclass
class QualityEvaluatedResult:
    """Result from quality-evaluated generation (single-pass)"""
    success: bool  # Always True unless generation error
    content: Any
    quality_scores: Dict  # Winston, Realism, Structural scores for reference
    evaluation_logged: bool  # Whether learning data was logged
    error_message: Optional[str] = None


class QualityEvaluatedGenerator:
    """
    Single-pass generator with quality evaluation for learning.
    
    Responsibilities:
    - Generate content using Generator (single-pass)
    - Save immediately to domain data file
    - Evaluate with SubjectiveEvaluator AFTER save
    - Log learning data (Winston, Realism, Structural)
    - Return success with quality scores
    
    NO retry logic, NO gating - evaluation is purely for learning.
    """
    
    def __init__(
        self,
        api_client,
        subjective_evaluator,
        winston_client=None,
        structural_variation_checker=None,
        domain='materials'
    ):
        """
        Initialize quality-evaluated generator.
        
        Args:
            api_client: API client for content generation (required)
            subjective_evaluator: SubjectiveEvaluator instance (required)
            winston_client: Winston API client for AI detection (optional)
            structural_variation_checker: StructuralVariationChecker instance (optional)
            domain: Domain name (e.g., 'materials', 'compounds', 'settings')
        
        Raises:
            ValueError: If required components missing (fail-fast)
        """
        if not api_client:
            raise ValueError("API client required for quality-evaluated generation")
        if not subjective_evaluator:
            raise ValueError("SubjectiveEvaluator required for quality-evaluated generation")
        
        self.api_client = api_client
        self.subjective_evaluator = subjective_evaluator
        self.winston_client = winston_client
        self.structural_variation_checker = structural_variation_checker
        self.domain = domain
        
        # Initialize Generator (single-pass) with domain
        from generation.core.generator import Generator
        self.generator = Generator(api_client, domain=domain)
        
        # Initialize DynamicConfig for parameters
        from generation.config.dynamic_config import DynamicConfig
        self.dynamic_config = DynamicConfig()
        
        # Initialize HumannessOptimizer for Universal Humanness Layer
        from learning.humanness_optimizer import HumannessOptimizer
        self.humanness_optimizer = HumannessOptimizer()
        
        # Initialize learning modules for continuous improvement
        from pathlib import Path

        from learning.sweet_spot_analyzer import SweetSpotAnalyzer
        from learning.validation_winston_correlator import ValidationWinstonCorrelator
        from learning.weight_learner import WeightLearner
        
        db_path = Path('z-beam.db')
        self.sweet_spot_analyzer = SweetSpotAnalyzer(db_path=str(db_path))
        self.weight_learner = WeightLearner(db_path=db_path)
        self.validation_correlator = ValidationWinstonCorrelator(db_path=str(db_path))
        
        logger.info(f"QualityEvaluatedGenerator initialized (single-pass with learning)")
        logger.info(f"   - Learning modules: SweetSpot, WeightLearner, ValidationCorrelator")

    
    def generate(
        self,
        material_name: str,
        component_type: str,
        retry_session_id: Optional[str] = None,
        is_retry: bool = False,
        **kwargs
    ) -> QualityEvaluatedResult:
        """
        Generate content with single-pass and post-save evaluation.
        
        Args:
            material_name: Name of material
            component_type: Type of component (micro, description, faq)
            retry_session_id: Optional session ID to group retry attempts together
            is_retry: Whether this is a retry attempt (enables proper learning tracking)
            **kwargs: Additional parameters (e.g., faq_count)
            
        Returns:
            QualityEvaluatedResult with content and quality scores
            
        Process (single-pass, no gating):
            1. Generate content with humanness layer
            2. Save to YAML immediately
            3. Run quality evaluations (for learning only)
            4. Log all data to learning database (with retry context if provided)
            5. Return success with quality scores
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"📝 SINGLE-PASS GENERATION: {component_type} for {material_name}")
        logger.info(f"{'='*80}\n")
        
        print(f"\n{'='*80}")
        print(f"📝 SINGLE-PASS GENERATION: {component_type} for {material_name}")
        print(f"{'='*80}\n")
        
        # Get base parameters with sweet spot learning
        current_params = self._get_base_parameters(component_type)
        
        # Log parameters
        print("🌡️  Generation Parameters:")
        for param, value in current_params.items():
            print(f"   • {param}: {value}")
        
        # Check for learned insights from validation-winston correlation
        try:
            insights = self.validation_correlator.get_top_issues(lookback_days=7, limit=3)
            if insights:
                print(f"\n💡 Recent Quality Insights:")
                for insight in insights:
                    print(f"   ⚠️  {insight['issue']}: {insight['impact']:+.1f} impact on Winston")
        except Exception as e:
            logger.debug(f"Could not load validation insights: {e}")
        
        # Generate humanness layer (learning-optimized, structural variation only)
        print(f"\n🧠 Generating humanness instructions...")
        humanness_instructions = self.humanness_optimizer.generate_humanness_instructions(
            component_type=component_type
        )
        print(f"   ✅ Humanness layer generated ({len(humanness_instructions)} chars)")
        
        # Generate content
        try:
            result = self._generate_content_only(
                material_name, 
                component_type,
                current_params,
                humanness_layer=humanness_instructions,
                **kwargs
            )
            content = result['content']
            print(f"\n✅ Generated: {result['length']} chars, {result['word_count']} words")
            
            # Apply smart truncation if enabled
            length_controlled = False
            
            # Load generation config to check length control settings
            import yaml
            from pathlib import Path
            config_path = Path(__file__).parent.parent / 'config.yaml'
            
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️  Could not load config.yaml: {e}")
                config_data = {}
            
            if config_data.get('length_control', {}).get('enable_smart_truncation', True):
                from shared.text.utils.length_control import apply_length_control
                
                # Get the original prompt for word count extraction
                final_prompt = getattr(result, 'prompt_used', '') or str(current_params.get('prompt', ''))
                
                print(f"\n✂️  Applying smart length control...")
                control_result = apply_length_control(
                    content=self._content_to_text(content, component_type),
                    prompt=final_prompt,
                    fallback_target=config_data.get('length_control', {}).get('default_target_words', 50)
                )
                
                # Update content if truncation occurred
                if control_result['truncated']:
                    controlled_content = control_result['content']
                    result['content'] = controlled_content
                    content = controlled_content
                    length_controlled = True
                    
                    print(f"📏 Length Control: {control_result['original_words']} → {control_result['final_words']} words")
                    print(f"🎯 Target: {control_result['target_words']}, Accuracy: {100-control_result['compliance']['variance_percent']:.1f}%")
                    print(f"✂️  Truncated: {control_result['reduction']} words removed")
                    
                    # Update result metrics
                    result['length'] = len(controlled_content)
                    result['word_count'] = control_result['final_words']
                    result['length_controlled'] = True
                    result['original_words'] = control_result['original_words']
                    result['truncated'] = True
                else:
                    print(f"📏 Length Control: {control_result['final_words']} words (no truncation needed)")
                    result['length_controlled'] = False
                    result['truncated'] = False
            
            # Display content preview
            content_text = self._content_to_text(content, component_type)
            print(f"\n{'─'*80}")
            print(f"📄 GENERATED CONTENT{' (LENGTH CONTROLLED)' if length_controlled else ''}:")
            print(f"{'─'*80}")
            print(content_text[:500] + ("..." if len(content_text) > 500 else ""))
            print(f"{'─'*80}\n")
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            return QualityEvaluatedResult(
                success=False,
                content=None,
                quality_scores={},
                evaluation_logged=False,
                error_message=f"Generation error: {e}"
            )
        
        # UNIFIED QUALITY ANALYSIS (post-generation, pre-save) 🔥 CONSOLIDATED
        quality_analysis = None
        
        if VOICE_VALIDATION_AVAILABLE:
            try:
                print(f"\n🎭 Analyzing quality (unified system)...")
                author_data = self._get_author_data(material_name)
                print(f"📝 MATERIAL: {material_name}")
                print(f"👤 ASSIGNED AUTHOR: {author_data['name']} ({author_data['country']})")
                print(f"🎯 AUTHOR ID: {self._get_author_id(material_name)}")
                
                # Use unified quality analyzer with learned weights
                from shared.voice.quality_analyzer import QualityAnalyzer

                # Get learned weights from weight_learner
                learned_weights = self._get_learned_quality_weights()
                
                analyzer = QualityAnalyzer(
                    self.api_client, 
                    strict_mode=False,
                    weights=learned_weights  # Use learned weights if available
                )
                
                # Single comprehensive analysis
                quality_analysis = analyzer.analyze(
                    text=content_text,
                    author=author_data,
                    include_recommendations=True,
                    component_type=component_type  # Context-aware forbidden phrases
                )
                
                print(f"   ✅ Quality Analysis Complete:")
                print(f"      • Overall Score: {quality_analysis['overall_score']}/100")
                print(f"      • AI Patterns: {quality_analysis['ai_patterns']['score']}/100")
                print(f"      • Voice Authenticity: {quality_analysis['voice_authenticity']['score']}/100")
                print(f"      • Structural Quality: {quality_analysis['structural_quality']['sentence_variation']:.1f}/100")
                
                # Legacy compatibility: extract voice_compliance and ai_pattern_detection
                voice_compliance = quality_analysis['voice_authenticity']
                ai_pattern_detection = {
                    'ai_score': quality_analysis['ai_patterns']['score'],
                    'is_ai_like': quality_analysis['ai_patterns']['is_ai_like'],
                    'issues': quality_analysis['ai_patterns']['issues'],
                    'details': quality_analysis['ai_patterns']['details']
                }
                
                # Show recommendations if any
                if quality_analysis.get('recommendations'):
                    print(f"\n   📋 Quality Recommendations:")
                    for rec in quality_analysis['recommendations'][:3]:  # Show top 3
                        print(f"      • {rec}")
                
                # Check for critical issues (LENIENT: allow 'unknown' for technical jargon)
                detected_lang = quality_analysis['voice_authenticity']['language']
                if detected_lang not in ['english', 'unknown', 'unknown_non_english']:
                    # Only fail if specific non-English language detected
                    logger.error(f"❌ Content not in English: {detected_lang}")
                    print(f"\n❌ VOICE COMPLIANCE FAILED: Non-English content detected")
                
                if quality_analysis['ai_patterns']['is_ai_like']:
                    logger.warning(f"⚠️  High AI pattern score detected")
                    print(f"   ⚠️  Warning: High AI likelihood")
                
            except Exception as e:
                logger.warning(f"   ⚠️  Quality analysis failed: {e}")
                voice_compliance = {'error': str(e)}
                ai_pattern_detection = None
                
                # Fallback to legacy AI detection only
                try:
                    from shared.voice.ai_detection import AIDetector
                    print(f"\n🤖 Checking AI patterns (fallback)...")
                    
                    detector = AIDetector(strict_mode=False)
                    ai_check = detector.detect_ai_patterns(content_text)
                    
                    ai_pattern_detection = {
                        'ai_score': 100 - ai_check['ai_score'],  # Invert for consistency
                        'is_ai_like': ai_check['is_ai_like'],
                        'issues': ai_check['issues'][:5] if 'issues' in ai_check else []
                    }
                    
                    print(f"   • AI Pattern Score: {ai_pattern_detection['ai_score']:.1f}/100")
                    print(f"   • AI-like: {'Yes' if ai_check['is_ai_like'] else 'No'}")
                    
                except Exception as e2:
                    logger.warning(f"   ⚠️  Fallback AI detection also failed: {e2}")
                    ai_pattern_detection = {'error': str(e2)}
        else:
            logger.debug("Quality analysis skipped - VoicePostProcessor not available")
        
        # SAVE IMMEDIATELY (no gating - voice validation for logging only)
        print(f"\n💾 Saving to {self.generator.domain} data...")
        self._save(material_name, component_type, content)
        print(f"   ✅ Saved successfully")
        
        # Initialize quality scores
        quality_scores = {
            'realism_score': None,
            'voice_authenticity': None,
            'tonal_consistency': None,
            'ai_tendencies': [],
            'winston_human_score': None,
            'winston_ai_score': None,
            'diversity_score': None,
            'voice_compliance': voice_compliance,  # Voice compliance data
            'ai_pattern_detection': ai_pattern_detection  # Legacy AI detection with pattern variation
        }
        evaluation_logged = False
        
        # Run quality evaluations (for learning, not gating)
        # Made async to avoid blocking generation pipeline (saves 22-25s per field)
        print(f"\n🔍 Running quality evaluations (for learning)...")
        print(f"   ⚡ Running in background to avoid blocking...")
        
        import threading
        evaluation = None
        
        def run_quality_evaluation():
            """Background thread for quality evaluation (non-blocking)"""
            nonlocal evaluation
            try:
                # Subjective evaluation
                eval_text = self._content_to_text(content, component_type)
                evaluation = self.subjective_evaluator.evaluate(
                    content=eval_text,
                    material_name=material_name,
                    component_type=component_type
                )
                
                quality_scores['realism_score'] = evaluation.realism_score or evaluation.overall_score
                quality_scores['voice_authenticity'] = evaluation.voice_authenticity
                quality_scores['tonal_consistency'] = evaluation.tonal_consistency
                quality_scores['ai_tendencies'] = evaluation.ai_tendencies or []
                
                print(f"\n📊 QUALITY SCORES (for learning):")
                print(f"   • Realism: {quality_scores['realism_score']:.1f}/10")
                print(f"   • Voice Authenticity: {quality_scores['voice_authenticity'] or 0:.1f}/10")
                print(f"   • Tonal Consistency: {quality_scores['tonal_consistency'] or 0:.1f}/10")
                if quality_scores['ai_tendencies']:
                    print(f"   • AI Tendencies: {', '.join(quality_scores['ai_tendencies'])}")
                else:
                    print(f"   • AI Tendencies: None detected")
            except Exception as e:
                logger.warning(f"   ⚠️  Subjective evaluation failed: {e}")
        
        # Start evaluation in background
        eval_thread = threading.Thread(target=run_quality_evaluation, daemon=True)
        eval_thread.start()
        
        # Don't wait - continue immediately with pipeline
        
        # Winston detection (also run in background for consistency)
        winston_result = self._check_winston_detection(content, material_name, component_type)
        quality_scores['winston_human_score'] = winston_result.get('human_score')
        quality_scores['winston_ai_score'] = winston_result.get('ai_score')
        
        # Log Winston client type for debugging
        if self.winston_client:
            client_type = type(self.winston_client).__name__
            if 'Cached' in client_type:
                logger.warning(f"Winston using {client_type} - may not have proper check_text support")
            else:
                logger.info(f"Winston using {client_type} - full API support available")
        
        # Structural variation
        structural_analysis = None
        if self.structural_variation_checker:
            try:
                author_id = self._get_author_id(material_name)
                structural_analysis = self.structural_variation_checker.check(
                    content=eval_text,
                    material_name=material_name,
                    component_type=component_type,
                    author_id=author_id
                )
                quality_scores['diversity_score'] = structural_analysis.diversity_score
                print(f"   • Diversity: {quality_scores['diversity_score']:.1f}/10")
            except Exception as e:
                logger.warning(f"   ⚠️  Structural check failed: {e}")
        
        # Log to learning database
        if evaluation:
            try:
                self._log_attempt_for_learning(
                    material_name=material_name,
                    component_type=component_type,
                    content=eval_text,
                    current_params=current_params,
                    evaluation=evaluation,
                    winston_result=winston_result,
                    structural_analysis=structural_analysis,
                    attempt=1,
                    passed_all_gates=True,  # Always "passed" - no gating
                    retry_session_id=retry_session_id,
                    is_retry=is_retry
                )
                evaluation_logged = True
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to log learning data: {e}")
        
        print(f"\n{'='*80}")
        print(f"✨ COMPLETE: {component_type} for {material_name}")
        print(f"{'='*80}\n")
        
        return QualityEvaluatedResult(
            success=True,
            content=content,
            quality_scores=quality_scores,
            evaluation_logged=evaluation_logged
        )
    
    def _get_base_parameters(self, component_type: str) -> Dict[str, Any]:
        """
        Get base generation parameters from config and sweet spot learning.
        
        Now integrates learned parameter ranges from database:
        1. Load sweet spot recommendations from SweetSpotAnalyzer
        2. Use median values from top 25% performers
        3. Filter out negatively correlated parameters
        4. Fall back to config.yaml only if insufficient learning data
        """
        from generation.config.config_loader import get_config
        config = get_config()
        
        # Try to load learned sweet spot parameters with correlation filtering
        learned_params = self._load_sweet_spot_parameters_with_filtering()
        
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
    
    def _get_learned_quality_weights(self) -> Optional[Dict[str, float]]:
        """
        Get learned quality metric weights from WeightLearner.
        
        Returns learned weights if sufficient data exists, otherwise None
        to fall back to QualityAnalyzer defaults.
        """
        try:
            weights = self.weight_learner.get_optimal_weights()
            if weights and weights.sample_count >= self.weight_learner.MIN_GLOBAL_SAMPLES:
                logger.info(f"   Using learned weights: W={weights.winston_weight:.2f}, S={weights.subjective_weight:.2f}, R={weights.readability_weight:.2f}")
                return {
                    'winston': weights.winston_weight,
                    'subjective': weights.subjective_weight,
                    'readability': weights.readability_weight
                }
            else:
                logger.debug(f"Insufficient data for learned weights ({weights.sample_count if weights else 0} samples)")
                return None
        except Exception as e:
            logger.debug(f"Could not load learned weights: {e}")
            return None
    
    def _load_sweet_spot_parameters_with_filtering(self) -> Dict[str, float]:
        """
        Load sweet spot parameters using integrated SweetSpotAnalyzer.
        Filters out parameters with negative correlation to quality.
        
        Returns:
            Dict of parameter_name -> optimal_value, or empty dict if insufficient data
        """
        try:
            # Get sweet spot analysis
            analysis = self.sweet_spot_analyzer.get_sweet_spot_table(save_to_db=False)
            
            if not analysis or not analysis.get('sweet_spots'):
                logger.debug("No sweet spot data available - using config defaults")
                return {}
            
            sweet_spots = analysis['sweet_spots']
            correlations = {param: corr for param, corr in analysis.get('correlations', [])}
            
            learned = {}
            filtered_count = 0
            
            for param_name, sweet_spot in sweet_spots.items():
                correlation = correlations.get(param_name, 0)
                
                # Filter out negatively correlated parameters
                if correlation < -0.3:
                    logger.debug(f"   ❌ {param_name}: Negative correlation {correlation:.3f} - excluded")
                    filtered_count += 1
                    continue
                
                # Use median value from sweet spot
                learned[param_name] = sweet_spot.optimal_median
                logger.debug(f"   ✅ {param_name}: {sweet_spot.optimal_median:.3f} (correlation: {correlation:+.3f})")
            
            if filtered_count > 0:
                logger.info(f"   Filtered {filtered_count} negatively correlated parameters from learning")
            
            return learned
            
        except Exception as e:
            logger.debug(f"Could not load sweet spot parameters: {e}")
            return {}
    
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
            # Micro: before/after structure
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
            # String content (description, etc.)
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
            from postprocessing.detection.winston_feedback_db import (
                WinstonFeedbackDatabase,
            )
            
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
    
    def _check_winston_detection(self, content: str, material_name: str, component_type: str) -> Dict[str, Any]:
        """
        Run Winston AI detection (for learning data collection).
        
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
            from generation.config.config_loader import get_config
            from postprocessing.detection.winston_feedback_db import (
                WinstonFeedbackDatabase,
            )
            from postprocessing.detection.winston_integration import WinstonIntegration
            from shared.text.validation.constants import ValidationConstants
            
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
        passed_all_gates: bool,
        retry_session_id: Optional[str] = None,
        is_retry: bool = False
    ):
        """
        Log EVERY generation attempt to database for learning, not just successes.
        
        NOW WITH RETRY TRACKING: Groups retry attempts together via retry_session_id
        to enable retry-specific learning analysis:
        - Parameter drift across attempts
        - Quality progression patterns  
        - Success rate by attempt number
        - Optimal retry strategies
        
        This is the KEY fix for learning system - we need data from ALL attempts to:
        1. Learn what parameters correlate negatively with success
        2. Understand realistic threshold distributions
        3. Identify structural patterns that fail vs succeed
        4. Build sufficient corpus for sweet spot analysis
        5. **NEW**: Analyze retry effectiveness and parameter adjustments
        
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
            retry_session_id: Session ID grouping retry attempts together
            is_retry: Whether this is a retry (not first generation)
        """
        try:
            # Only log if we have Winston database available
            if not self.winston_client:
                return
            
            # Get database path from config
            from generation.config.config_loader import get_config
            from postprocessing.detection.winston_feedback_db import (
                WinstonFeedbackDatabase,
            )
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
                composite_quality_score=composite_score,
                retry_session_id=retry_session_id,
                is_retry=is_retry
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
    
    def _save(self, material_name: str, component_type: str, content: str):
        """Save content to domain data file (atomic write)"""
        # Use Generator's save method (domain-aware)
        self.generator._save_to_yaml(material_name, component_type, content)
    
    def _get_author_id(self, material_name: str) -> int:
        """Get author_id for item from domain data file - FAIL-FAST if missing"""
        from data.authors.registry import resolve_author_for_generation

        # Use generator's domain adapter to load data
        all_data = self.generator.adapter.load_all_data()
        data_root_key = self.generator.adapter.data_root_key
        domain = self.generator.domain
        
        item_data = all_data.get(data_root_key, {}).get(material_name)
        
        if not item_data:
            raise ValueError(f"Item '{material_name}' not found in {domain} data")
        
        # FAIL-FAST: No fallbacks - item must have valid author.id
        author_info = resolve_author_for_generation(item_data)
        return author_info['id']
    
    def _get_author_data(self, material_name: str) -> Dict[str, Any]:
        """
        Get complete author data for voice compliance validation.
        
        Returns dict with 'name' and 'country' keys required by VoicePostProcessor.
        """
        from data.authors.registry import resolve_author_for_generation

        # Use generator's domain adapter to load data
        all_data = self.generator.adapter.load_all_data()
        data_root_key = self.generator.adapter.data_root_key
        domain = self.generator.domain
        
        item_data = all_data.get(data_root_key, {}).get(material_name)
        
        if not item_data:
            raise ValueError(f"Item '{material_name}' not found in {domain} data")
        
        # Get full author info
        author_info = resolve_author_for_generation(item_data)
        
        return {
            'name': author_info.get('name', 'Unknown'),
            'country': author_info.get('country', 'United States')
        }


# Backward compatibility aliases
QualityGatedGenerator = QualityEvaluatedGenerator
QualityGatedResult = QualityEvaluatedResult