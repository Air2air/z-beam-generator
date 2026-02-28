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
    5. Grok Humanness Detection: Logged for human-score trends
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
    quality_scores: Dict  # Grok humanness, realism, structural scores for reference
    evaluation_logged: bool  # Whether learning data was logged
    error_message: Optional[str] = None


class QualityEvaluatedGenerator:
    """
    Single-pass generator with quality evaluation for learning.
    
    Responsibilities:
    - Generate content using Generator (single-pass)
    - Save immediately to domain data file
    - Evaluate with SubjectiveEvaluator AFTER save
    - Log learning data (Grok humanness, Realism, Structural)
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
        Initialize quality-evaluated generator with SIMPLIFIED architecture.
        
        Args:
            api_client: API client for content generation (required)
            subjective_evaluator: SubjectiveEvaluator instance (required)
            winston_client: Deprecated and ignored (backward compatibility only)
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
        
        # ✅ SIMPLIFIED: Unified parameter provider (replaces 5 separate sources)
        from generation.config.unified_parameter_provider import UnifiedParameterProvider
        self.parameter_provider = UnifiedParameterProvider(db_path='z-beam.db')
        
        # Initialize HumannessOptimizer for Universal Humanness Layer
        from learning.humanness_optimizer import HumannessOptimizer
        self.humanness_optimizer = HumannessOptimizer()
        
        # ✅ SIMPLIFIED: Consolidated learning system (replaces 3 separate systems)
        from learning.consolidated_learning_system import ConsolidatedLearningSystem
        self.learning_system = ConsolidatedLearningSystem(db_path='z-beam.db')
        self.grok_humanness_evaluator = None
        
        logger.info(f"QualityEvaluatedGenerator initialized (SIMPLIFIED ARCHITECTURE)")
        logger.info(f"   ✅ Unified parameter provider (1 interface)")
        logger.info(f"   ✅ Consolidated learning system (1 database)")

    
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

        # Runtime controls for orchestration callers (e.g., postprocess retries)
        # Pop here so control flags are NOT forwarded into prompt item_data.
        skip_learning_evaluation = bool(kwargs.pop('skip_learning_evaluation', False))
        
        # ✅ SIMPLIFIED: Get all parameters from unified provider (was 5 separate calls)
        params = self.parameter_provider.get_parameters(component_type, target_words=kwargs.get('target_words'))
        
        # Display parameters with insights
        self.parameter_provider.display_insights(params)
        
        # Generate humanness layer (learning-optimized, structural variation only)
        # Retry speed mode: keep COMPACT humanness for variation without prompt bloat.
        if skip_learning_evaluation:
            print(f"\n⚡ Retry speed mode: using compact humanness layer")
            humanness_instructions = self.humanness_optimizer.generate_humanness_instructions(
                component_type=component_type,
                length_target=kwargs.get('target_words')
            )
            print(f"   ✅ Compact humanness generated ({len(humanness_instructions)} chars)")
        else:
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
                params,  # ✅ SIMPLIFIED: Pass unified params object
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
                raise RuntimeError(f"Could not load config.yaml: {e}") from e

            if not isinstance(config_data, dict):
                raise TypeError("config.yaml must parse to a dictionary")
            if 'length_control' not in config_data:
                raise KeyError("config.yaml missing required key: 'length_control'")
            length_control_config = config_data['length_control']
            if not isinstance(length_control_config, dict):
                raise TypeError("config.yaml key 'length_control' must be a dictionary")
            if 'enable_smart_truncation' not in length_control_config:
                raise KeyError("length_control missing required key: 'enable_smart_truncation'")

            if length_control_config['enable_smart_truncation']:
                skip_components = self._get_domain_generation_list('length_control', 'skip_components')
                if component_type in skip_components:
                    print("\n✂️  Skipping smart length truncation (per domain config)")
                else:
                    from shared.text.utils.length_control import apply_length_control
                    default_target_words = length_control_config.get('default_target_words')
                    if default_target_words is None:
                        raise ValueError(
                            "length_control.default_target_words is required when smart truncation is enabled"
                        )

                    # Get the original prompt for word count extraction
                    final_prompt = getattr(result, 'prompt_used', '') or str(getattr(params, 'prompt', ''))

                    runtime_target_words = kwargs.get('target_words')
                    fallback_target_words = runtime_target_words if isinstance(runtime_target_words, int) and runtime_target_words > 0 else default_target_words

                    print(f"\n✂️  Applying smart length control...")
                    control_result = apply_length_control(
                        content=self._content_to_text(content, component_type),
                        prompt=final_prompt,
                        fallback_target=fallback_target_words
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
                
                # ✅ SIMPLIFIED: Get learned weights from consolidated learning system
                from shared.voice.quality_analyzer import QualityAnalyzer
                learned_weights = self.learning_system.get_quality_weights(component_type)
                
                analyzer = QualityAnalyzer(
                    self.api_client, 
                    strict_mode=False,
                    weights=learned_weights  # Use learned weights from consolidated system
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
            'grok_human_score': None,
            'grok_ai_score': None,
            'diversity_score': None,
            'voice_compliance': voice_compliance,  # Voice compliance data
            'ai_pattern_detection': ai_pattern_detection  # Legacy AI detection with pattern variation
        }
        evaluation_logged = False
        
        # Run quality evaluations (for learning, not gating)
        # NOTE: Keep synchronous for deterministic behavior and crash-free logging.
        eval_text = self._content_to_text(content, component_type)
        evaluation = None

        if skip_learning_evaluation:
            print(f"\n⏩ Skipping subjective learning evaluation (retry speed mode)")
        else:
            print(f"\n🔍 Running quality evaluations (for learning)...")
            try:
                evaluation = self.subjective_evaluator.evaluate(
                    content=eval_text,
                    material_name=material_name,
                    component_type=component_type
                )

                realism_score = evaluation.realism_score
                if realism_score is None:
                    realism_score = evaluation.overall_score
                if realism_score is None:
                    raise ValueError("Subjective evaluation missing both realism_score and overall_score")

                quality_scores['realism_score'] = realism_score
                quality_scores['voice_authenticity'] = evaluation.voice_authenticity
                quality_scores['tonal_consistency'] = evaluation.tonal_consistency
                if evaluation.ai_tendencies is None:
                    raise ValueError("Subjective evaluation missing required ai_tendencies")
                if not isinstance(evaluation.ai_tendencies, list):
                    raise TypeError("Subjective evaluation ai_tendencies must be a list")
                quality_scores['ai_tendencies'] = evaluation.ai_tendencies

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
        
        # Grok humanness detection
        grok_result = self._check_grok_detection(eval_text, material_name, component_type)
        quality_scores['grok_human_score'] = grok_result.get('human_score')
        quality_scores['grok_ai_score'] = grok_result.get('ai_score')
        
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
                    current_params=params,
                    evaluation=evaluation,
                    grok_result=grok_result,
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
    
    # OBSOLETE METHODS - Replaced by simplified systems
    # These methods kept for reference but should not be used
    # Use self.parameter_provider.get_parameters() instead of _get_base_parameters()
    # Use self.learning_system.get_quality_weights() instead of _get_learned_quality_weights()
    
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
            if 'correlations' not in analysis:
                raise KeyError("Sweet spot analysis missing required key: 'correlations'")
            correlations_data = analysis['correlations']
            if not isinstance(correlations_data, list):
                raise TypeError("Sweet spot analysis key 'correlations' must be a list")
            correlations = {param: corr for param, corr in correlations_data}
            
            learned = {}
            filtered_count = 0
            
            for param_name, sweet_spot in sweet_spots.items():
                if param_name not in correlations:
                    raise KeyError(
                        f"Missing correlation for sweet spot parameter '{param_name}'"
                    )
                correlation = correlations[param_name]
                
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
            if 'before' not in content or 'after' not in content:
                try:
                    import yaml

                    yaml_text = yaml.safe_dump(
                        content,
                        sort_keys=False,
                        default_flow_style=False
                    )
                    return yaml_text.strip()
                except Exception:
                    return str(content)
            before = content['before']
            after = content['after']
            return f"BEFORE:\n{before}\n\nAFTER:\n{after}"
        elif isinstance(content, list):
            # FAQ: list of Q&A
            parts = []
            for qa in content:
                if not isinstance(qa, dict):
                    raise TypeError("FAQ content entries must be dictionaries")
                if 'question' not in qa or 'answer' not in qa:
                    raise KeyError("FAQ entry missing required keys: 'question' and 'answer'")
                q = qa['question']
                a = qa['answer']
                parts.append(f"Q: {q}\nA: {a}")
            return "\n\n".join(parts)
        else:
            # String content (description, etc.)
            return str(content)

    def _get_domain_generation_list(self, *path_parts: str) -> list:
        if not self.generator:
            raise RuntimeError("Generator not initialized; cannot read domain config")

        from generation.config.config_loader import get_config

        config = get_config().config
        domain_generation = config.get('domain_generation')
        if not isinstance(domain_generation, dict):
            raise KeyError("Missing required config block: domain_generation")
        if self.generator.domain not in domain_generation:
            raise KeyError(
                f"Missing domain_generation config for domain '{self.generator.domain}'"
            )

        node: Any = domain_generation[self.generator.domain]
        for part in path_parts:
            if not isinstance(node, dict) or part not in node:
                raise KeyError(
                    f"Missing required config key: domain_generation.{self.generator.domain}.{'.'.join(path_parts)}"
                )
            node = node[part]

        if not isinstance(node, list):
            raise TypeError(
                f"domain_generation.{self.generator.domain}.{'.'.join(path_parts)} must be a list"
            )
        return node
    
    def _load_sweet_spot_parameters(self) -> Dict[str, float]:
        """
        Legacy compatibility shim.

        Winston feedback DB has been removed from active runtime. Parameter
        learning now flows through unified providers and consolidated learning.
        Keep this method returning an empty dict to avoid stale call-sites.
        """
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
    
    def _check_grok_detection(self, content: str, material_name: str, component_type: str) -> Dict[str, Any]:
        """
        Run Grok-only humanness detection.
        
        Returns:
            dict: {
                'passed': bool,
                'human_score': float,
                'ai_score': float,
                'message': str
            }
        """
        try:
            logger.info("\n🧠 Running Grok-only humanness detection...")

            if self.grok_humanness_evaluator is None:
                from learning.grok_humanness_runtime import GrokHumannessRuntimeEvaluator
                self.grok_humanness_evaluator = GrokHumannessRuntimeEvaluator()

            author_id = self._get_author_id(material_name)
            grok_payload = self.grok_humanness_evaluator.evaluate(
                candidate_text=content,
                domain=self.domain,
                item_id=material_name,
                component_type=component_type,
                author_id=author_id,
                generation_id=None,
                retry_session_id=None,
                attempt=1,
            )

            aggregation = grok_payload['aggregation']
            weighted_score = float(aggregation['weightedScore'])
            human_score = weighted_score / 100.0
            ai_score = 1.0 - human_score
            passed = bool(grok_payload['gates']['pass'])

            logger.info(f"   👤 Grok Human Score: {human_score*100:.1f}%")
            logger.info(f"   🤖 Grok AI-Likeness Score: {ai_score*100:.1f}%")

            if passed:
                logger.info("   ✅ Grok humanness check PASSED")
            else:
                logger.warning("   ❌ Grok humanness check FAILED - will retry with adjusted parameters")

            return {
                'passed': passed,
                'human_score': human_score,
                'ai_score': ai_score,
                'threshold': None,
                'message': f"{'Passed' if passed else 'Failed'} Grok humanness detection"
            }
                
        except Exception as e:
            raise RuntimeError(f"Grok humanness detection failed: {e}") from e
    
    def _log_attempt_for_learning(
        self,
        material_name: str,
        component_type: str,
        content: str,
        current_params: Dict[str, Any],
        evaluation: Any,
        grok_result: Dict[str, Any],
        structural_analysis: Any,
        attempt: int,
        passed_all_gates: bool,
        retry_session_id: Optional[str] = None,
        is_retry: bool = False
    ):
        """
        Log generation attempt to unified learning system.
        
        SIMPLIFIED VERSION: Uses ConsolidatedLearningSystem for single-write logging.
        
        Tracks:
        - Generation parameters and quality scores
        - Success/failure patterns for learning
        - Retry session tracking for effectiveness analysis
        
        Args:
            material_name: Material being generated
            component_type: Component type
            content: Generated content (string)
            current_params: Generation parameters used
            evaluation: SubjectiveEvaluation result
            grok_result: Grok humanness detection result
            structural_analysis: StructuralAnalysis result
            attempt: Attempt number (1-5)
            passed_all_gates: Whether all quality gates passed
            retry_session_id: Session ID grouping retry attempts together
            is_retry: Whether this is a retry (not first generation)
        """
        try:
            from learning.consolidated_learning_system import GenerationResult
            from datetime import datetime
            
            # Calculate quality scores
            realism_score = evaluation.realism_score
            if realism_score is None:
                realism_score = evaluation.overall_score
            if realism_score is None:
                raise ValueError("Learning log missing both realism_score and overall_score")
            realism_normalized = realism_score / 10.0  # 0-10 scale → 0-1.0
            if 'human_score' not in grok_result:
                raise KeyError("Grok result missing required key: 'human_score'")
            grok_human_score = grok_result['human_score']
            if grok_human_score is None:
                raise ValueError("Grok human_score must not be None")
            
            # Composite score: Grok 40% + Realism 60%
            overall_quality_score = (grok_human_score * 0.4) + (realism_normalized * 0.6)

            # Normalize structural score to 0-100 scale expected by learning system
            structural_score = 50.0
            if structural_analysis and getattr(structural_analysis, 'diversity_score', None) is not None:
                structural_score = float(structural_analysis.diversity_score) * 10.0

            if evaluation.ai_tendencies is None:
                raise ValueError("Learning log missing required ai_tendencies")
            if not isinstance(evaluation.ai_tendencies, list):
                raise TypeError("Learning ai_tendencies must be a list")
            ai_tendencies = evaluation.ai_tendencies
            ai_pattern_score = max(0.0, 100.0 - (len(ai_tendencies) * 20.0))

            author_id = self._get_author_id(material_name)
            word_count = len(content.split())
            char_count = len(content)
            
            # Create unified generation result object
            result = GenerationResult(
                material_name=material_name,
                component_type=component_type,
                content=content,
                winston_score=grok_human_score,
                realism_score=realism_score,
                voice_authenticity_score=evaluation.voice_authenticity or 0.0,
                structural_quality_score=structural_score,
                ai_pattern_score=ai_pattern_score,
                temperature=current_params.temperature,
                frequency_penalty=current_params.frequency_penalty,
                presence_penalty=current_params.presence_penalty,
                word_count=word_count,
                char_count=char_count,
                author_id=author_id,
                timestamp=datetime.now()
            )
            
            # Single unified logging call (replaces 3 separate database writes)
            generation_id = self.learning_system.log_generation(result)

            # Criterion-level Grok humanness evaluation (additive learning signal)
            if self.grok_humanness_evaluator is None:
                from learning.grok_humanness_runtime import GrokHumannessRuntimeEvaluator
                self.grok_humanness_evaluator = GrokHumannessRuntimeEvaluator()

            grok_payload = self.grok_humanness_evaluator.evaluate(
                candidate_text=content,
                domain=self.domain,
                item_id=material_name,
                component_type=component_type,
                author_id=author_id,
                generation_id=generation_id,
                retry_session_id=retry_session_id,
                attempt=attempt,
            )
            grok_evaluation_id = self.learning_system.log_grok_evaluation(generation_id, grok_payload)
            
            logger.info(
                f"   📊 Logged attempt {attempt} to learning system "
                f"(generation_id={generation_id}, quality={overall_quality_score:.2f})"
            )
            print(
                f"   📊 Logged attempt {attempt} to learning system "
                f"(generation_id={generation_id}, quality={overall_quality_score:.2f})"
            )
            logger.info(
                f"   🧠 Logged Grok humanness evaluation "
                f"(grok_evaluation_id={grok_evaluation_id}, generation_id={generation_id})"
            )
            print(
                f"   🧠 Logged Grok humanness evaluation "
                f"(grok_evaluation_id={grok_evaluation_id}, generation_id={generation_id})"
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
        from data.authors.registry import get_author

        # Use generator's domain adapter to load data
        all_data = self.generator.adapter.load_all_data()
        data_root_key = self.generator.adapter.data_root_key
        domain = self.generator.domain
        
        if data_root_key not in all_data:
            raise KeyError(
                f"Domain data missing required root key '{data_root_key}' for domain '{domain}'"
            )
        root_data = all_data[data_root_key]
        if not isinstance(root_data, dict):
            raise TypeError(
                f"Domain data root '{data_root_key}' must be a dictionary, got {type(root_data).__name__}"
            )
        item_data = root_data[material_name] if material_name in root_data else None
        
        if not item_data:
            raise ValueError(f"Item '{material_name}' not found in {domain} data")
        
        # FAIL-FAST: author key is canonical — integer reference (source data) or nested object (frontmatter).
        author_id = None
        author_field = item_data.get('author')
        if isinstance(author_field, dict):
            if 'id' not in author_field:
                raise KeyError(f"Item '{material_name}' author object missing required key: 'id'")
            author_id = author_field['id']
        elif isinstance(author_field, int):
            author_id = author_field  # source data format: author: 4

        if author_id is None:
            raise ValueError(
                f"Item '{material_name}' missing author identity. "
                f"Expected 'author' integer or 'author.id' nested object in {domain} data."
            )

        if not isinstance(author_id, int):
            raise ValueError(
                f"Item '{material_name}' author id must be integer, "
                f"got {type(author_id).__name__}"
            )

        # Validate author exists in registry (raises KeyError if invalid)
        get_author(author_id)
        return author_id
    
    def _get_author_data(self, material_name: str) -> Dict[str, Any]:
        """
        Get complete author data for voice compliance validation.
        
        Returns dict with 'name' and 'country' keys required by VoicePostProcessor.
        """
        from data.authors.registry import get_author

        # Use generator's domain adapter to load data
        all_data = self.generator.adapter.load_all_data()
        data_root_key = self.generator.adapter.data_root_key
        domain = self.generator.domain
        
        if data_root_key not in all_data:
            raise KeyError(
                f"Domain data missing required root key '{data_root_key}' for domain '{domain}'"
            )
        root_data = all_data[data_root_key]
        if not isinstance(root_data, dict):
            raise TypeError(
                f"Domain data root '{data_root_key}' must be a dictionary, got {type(root_data).__name__}"
            )
        item_data = root_data[material_name] if material_name in root_data else None
        
        if not item_data:
            raise ValueError(f"Item '{material_name}' not found in {domain} data")
        
        # Resolve author id with strict validation (author.id or legacy authorId)
        author_id = None
        author_field = item_data['author'] if 'author' in item_data else None
        if isinstance(author_field, dict):
            if 'id' not in author_field:
                raise KeyError(f"Item '{material_name}' author object missing required key: 'id'")
            author_id = author_field['id']
        elif 'authorId' in item_data:
            author_id = item_data['authorId']

        if author_id is None:
            raise ValueError(
                f"Item '{material_name}' missing author identity. "
                f"Expected author.id or authorId in {domain} data."
            )

        if not isinstance(author_id, int):
            raise ValueError(
                f"Item '{material_name}' author id must be integer, "
                f"got {type(author_id).__name__}"
            )

        # Get full author info (raises KeyError if invalid)
        author_info = get_author(author_id)
        
        if 'name' not in author_info:
            raise KeyError(f"Author registry entry missing required key: 'name' for item '{material_name}'")
        if 'country' not in author_info:
            raise KeyError(f"Author registry entry missing required key: 'country' for item '{material_name}'")

        author_name = author_info['name']
        author_country = author_info['country']

        if not author_name:
            raise ValueError(f"Author name missing for '{material_name}'")
        if not author_country:
            raise ValueError(f"Author country missing for '{material_name}'")

        return {
            'name': author_name,
            'country': author_country
        }


# Backward compatibility aliases
QualityGatedGenerator = QualityEvaluatedGenerator
QualityGatedResult = QualityEvaluatedResult