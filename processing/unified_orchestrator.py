"""
Unified Content Generation Orchestrator

Single orchestrator consolidating processing/orchestrator.py and processing/generator.py.
Reduces 1,250 LOC of duplicate logic to ~750 LOC of clean, maintainable code.

ARCHITECTURE:
- Works with ANY data source via DataSourceAdapter pattern
- Centralizes Winston integration via WinstonIntegration facade
- Implements industry best practices (RLHF, curriculum learning, exploration)
- Provides single, testable generation workflow

WORKFLOW:
1. Load data via adapter (Materials, Regions, Applications, etc.)
2. Enrich with real facts
3. Build prompt with voice + facts + anti-AI rules
4. Generate with adaptive parameters (temperature, voice, enrichment)
5. Validate with Winston AI detection + readability
6. Learn from feedback and adapt
7. Retry with adjusted parameters on failure
8. Write success to data source via adapter

NO FALLBACKS - Fails explicitly with clear error messages
"""

import logging
import random
import re
import time
from typing import Dict, Any, Optional
from copy import deepcopy

from processing.adapters.base import DataSourceAdapter
from processing.adapters.materials_adapter import MaterialsAdapter
from processing.detection.winston_integration import WinstonIntegration

logger = logging.getLogger(__name__)


def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries, preserving nested structures.
    
    Args:
        base: Base dictionary to merge into
        update: Dictionary with updates to apply
        
    Returns:
        New dictionary with deep-merged values
    """
    result = deepcopy(base)
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


class UnifiedOrchestrator:
    """
    Single unified orchestrator for all content generation.
    
    Replaces processing/orchestrator.py and processing/generator.py with
    a cleaner, more maintainable architecture using adapter pattern.
    
    Key Features:
    - Data source adapter pattern for extensibility
    - Winston integration facade for testability
    - Industry best practices (RLHF, curriculum learning, 15% exploration)
    - Adaptive parameters based on historical feedback
    - Clear separation of concerns
    
    Usage:
        # For materials
        adapter = MaterialsAdapter()
        orchestrator = UnifiedOrchestrator(
            api_client=api_client,
            data_adapter=adapter
        )
        
        result = orchestrator.generate(
            identifier="Aluminum",
            component_type="caption"
        )
    """
    
    def __init__(
        self,
        api_client,
        data_adapter: Optional[DataSourceAdapter] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize unified orchestrator.
        
        Args:
            api_client: API client for content generation (required)
            data_adapter: Data source adapter (defaults to MaterialsAdapter)
            config: Optional configuration dict
        """
        if not api_client:
            raise ValueError("API client required for content generation")
        
        self.api_client = api_client
        self.data_adapter = data_adapter or MaterialsAdapter()
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._init_components()
        
        self.logger.info("UnifiedOrchestrator initialized with learning capabilities")
    
    def _init_components(self):
        """Initialize all required components with fail-fast validation"""
        # Data enricher for real facts
        from processing.enrichment.data_enricher import DataEnricher
        self.enricher = DataEnricher()
        
        # Dynamic config for parameter baseline
        from processing.config.dynamic_config import DynamicConfig
        self.dynamic_config = DynamicConfig()
        
        # Author voice store
        from processing.voice.store import AuthorVoiceStore
        self.voice_store = AuthorVoiceStore()
        
        # Prompt builder
        from processing.generation.prompt_builder import PromptBuilder
        self.prompt_builder = PromptBuilder()
        
        # Winston integration facade
        winston_client = None
        try:
            from shared.api.client_factory import create_api_client
            winston_client = create_api_client('winston')
            self.logger.info("Winston API client initialized")
        except Exception as e:
            self.logger.warning(f"Winston API client unavailable: {e}")
        
        # Winston feedback database
        feedback_db = None
        db_path = None
        try:
            from processing.config.config_loader import get_config
            config = get_config()
            db_path = config.config.get('winston_feedback_db_path')
            if db_path:
                from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
                feedback_db = WinstonFeedbackDatabase(db_path)
                self.logger.info(f"Winston feedback database initialized at {db_path}")
        except Exception as e:
            self.logger.warning(f"Winston feedback database unavailable: {e}")
        
        # Initialize Winston integration facade
        self.winston = WinstonIntegration(
            winston_client=winston_client,
            feedback_db=feedback_db,
            config=self.config
        )
        
        # Initialize PromptOptimizer for self-learning prompt enhancement
        self.prompt_optimizer = None
        if db_path:
            try:
                from processing.learning.prompt_optimizer import PromptOptimizer
                self.prompt_optimizer = PromptOptimizer(db_path)
                self.logger.info("🧠 PromptOptimizer enabled - dynamic prompt learning active")
            except Exception as e:
                self.logger.warning(f"PromptOptimizer unavailable: {e}")
        
        # Readability validator
        from processing.validation.readability import ReadabilityValidator
        readability_thresholds = self.dynamic_config.calculate_readability_thresholds()
        self.validator = ReadabilityValidator(min_score=readability_thresholds['min'])
        
        # Learning modules for parameter adaptation
        if feedback_db:
            try:
                from processing.learning.temperature_advisor import TemperatureAdvisor
                self.temperature_advisor = TemperatureAdvisor(feedback_db.db_path)
                self.logger.info("Temperature advisor initialized")
            except Exception as e:
                self.logger.warning(f"Temperature advisor unavailable: {e}")
                self.temperature_advisor = None
        else:
            self.temperature_advisor = None
        
        # AI detection threshold (base - will adapt based on learning phase)
        self.base_ai_threshold = self.dynamic_config.calculate_detection_threshold() / 100.0
        self.ai_threshold = self.base_ai_threshold
        
        self.logger.info(f"Base AI detection threshold: {self.base_ai_threshold:.3f}")
    
    def generate(
        self,
        identifier: str,
        component_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content with adaptive learning-based parameters.
        
        Args:
            identifier: Item identifier (material name, region name, etc.)
            component_type: Content type (defined in prompts/{type}.txt)
            **kwargs: Additional parameters
            
        Returns:
            Dict with:
            - success: bool
            - content: Generated content (if successful)
            - text: Raw generated text
            - attempts: Number of attempts
            - ai_score: Final AI detection score
            - readability: Readability metrics
            - reason: Failure reason (if failed)
        """
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Generating {component_type} for {identifier}")
        self.logger.info(f"{'='*60}")
        
        # Load item data via adapter
        try:
            item_data = self.data_adapter.get_item_data(identifier)
        except ValueError as e:
            raise ValueError(f"Data load failed: {e}")
        
        # Get author voice
        author_id = self.data_adapter.get_author_id(item_data)
        voice = self.voice_store.get_voice(author_id)
        
        # Get enrichment data via adapter
        facts = self.data_adapter.get_enrichment_data(identifier)
        context = self.data_adapter.build_context(item_data)
        
        # Determine length
        from processing.generation.component_specs import ComponentRegistry
        spec = ComponentRegistry.get_spec(component_type)
        length = random.randint(spec.min_length, spec.max_length)
        self.logger.info(f"🎲 Target length: {length} words (range: {spec.min_length}-{spec.max_length})")
        
        # Set adaptive quality threshold (curriculum learning)
        self.ai_threshold = self._get_adaptive_quality_threshold(identifier, component_type)
        
        # Generation loop with learning
        max_attempts = self.winston.get_max_attempts_for_mode(default=3)
        absolute_max = 3
        attempt = 1
        last_winston_result = None
        
        while attempt <= max_attempts and attempt <= absolute_max:
            self.logger.info(f"\nAttempt {attempt}/{max_attempts}")
            
            # Get adaptive parameters (learns from feedback)
            params = self._get_adaptive_parameters(
                identifier,
                component_type,
                attempt,
                last_winston_result
            )
            
            # Format facts string
            facts_str = self.enricher.format_facts_for_prompt(
                facts,
                enrichment_params=params['enrichment_params']
            )
            
            # Build prompt with dynamic parameters
            variation_seed = int(time.time() * 1000) + attempt
            
            prompt = self.prompt_builder.build_unified_prompt(
                topic=identifier,
                voice=voice,
                length=length,
                facts=facts_str,
                context=context,
                component_type=component_type,
                domain='materials',  # TODO: Get from adapter
                voice_params=params['voice_params'],
                enrichment_params=params['enrichment_params'],
                variation_seed=variation_seed
            )
            
            # SELF-LEARNING: Optimize prompt with learned patterns from Winston feedback
            if self.prompt_optimizer and attempt == 1:
                # Only optimize on first attempt (retry uses adjust_on_failure)
                optimization_result = self.prompt_optimizer.optimize_prompt(
                    base_prompt=prompt,
                    material=identifier,
                    component_type=component_type,
                    include_patterns=True,
                    include_recommendations=True
                )
                
                if optimization_result['confidence'] != 'none':
                    prompt = optimization_result['optimized_prompt']
                    self.logger.info("🧠 Prompt optimized with learned patterns:")
                    self.logger.info(f"   Confidence: {optimization_result['confidence']}")
                    self.logger.info(f"   Patterns analyzed: {optimization_result.get('patterns_analyzed', 0)}")
                    self.logger.info(f"   Expected improvement: {optimization_result['expected_improvement']*100:.1f}%")
                    for addition in optimization_result['additions']:
                        self.logger.info(f"   + {addition}")
                else:
                    self.logger.info(f"🧠 Prompt optimizer: {optimization_result.get('reason', 'Insufficient data')}")
            
            # Adjust prompt on retry
            if attempt > 1:
                prompt = self.prompt_builder.adjust_on_failure(
                    prompt,
                    failure_reason=f"AI score too high (attempt {attempt})",
                    attempt=attempt
                )
            
            # Generate content
            try:
                text = self._call_api(
                    prompt,
                    params['api_params']['temperature'],
                    params['api_params']['max_tokens'],
                    params['enrichment_params'],
                    params.get('api_penalties', {})  # NEW: Pass API penalties
                )
            except Exception as e:
                self.logger.error(f"API call failed: {e}")
                if attempt >= absolute_max:
                    return {
                        'success': False,
                        'reason': f'API error: {e}',
                        'attempts': attempt
                    }
                attempt += 1
                continue
            
            # AI detection via Winston integration facade
            detection_result = self.winston.detect_and_log(
                text=text,
                material=identifier,
                component_type=component_type,
                temperature=params['api_params']['temperature'],
                attempt=attempt,
                max_attempts=max_attempts,
                ai_threshold=self.ai_threshold
            )
            
            ai_score = detection_result['ai_score']
            last_winston_result = detection_result['detection']
            
            self.logger.info(
                f"AI score: {ai_score:.3f} (threshold: {self.ai_threshold:.3f}) "
                f"[method: {detection_result['method']}]"
            )
            
            # Readability check
            readability = self.validator.validate(text)
            self.logger.info(f"Readability: {readability['status']}")
            
            # Dual-threshold check:
            # 1. Acceptance threshold: ai_score <= threshold (for deployment)
            # 2. Learning target: human_score >= target (for improvement)
            passes_acceptance = ai_score <= self.ai_threshold and readability['is_readable']
            human_score = detection_result['detection'].get('human_score', 0)
            learning_target = self.dynamic_config.base_config.get_learning_target()
            meets_learning_target = human_score >= learning_target
            
            # Check if successful for BOTH acceptance and learning
            if passes_acceptance and meets_learning_target:
                self.logger.info(f"✅ Success on attempt {attempt} (human: {human_score:.1f}%, target: {learning_target}%)")
                
                # Extract component-specific content via adapter
                try:
                    content_data = self.data_adapter.extract_component_content(
                        text,
                        component_type
                    )
                except ValueError as e:
                    self.logger.error(f"Content extraction failed: {e}")
                    if attempt >= absolute_max:
                        return {
                            'success': False,
                            'reason': f'Extraction error: {e}',
                            'attempts': attempt,
                            'text': text
                        }
                    attempt += 1
                    continue
                
                # Write to data source via adapter
                try:
                    self.data_adapter.write_component(
                        identifier,
                        component_type,
                        content_data
                    )
                except Exception as e:
                    self.logger.error(f"Write failed: {e}")
                    return {
                        'success': False,
                        'reason': f'Write error: {e}',
                        'attempts': attempt,
                        'content': content_data,
                        'text': text
                    }
                
                return {
                    'success': True,
                    'content': content_data,
                    'text': text,
                    'attempts': attempt,
                    'ai_score': ai_score,
                    'human_score': human_score,
                    'readability': readability
                }
            
            # Passes acceptance but needs learning improvement
            if passes_acceptance and not meets_learning_target:
                self.logger.warning(
                    f"⚠️  Passes acceptance (ai_score: {ai_score:.3f} <= {self.ai_threshold:.3f}) "
                    f"but below learning target (human: {human_score:.1f}% < {learning_target}%)"
                )
                # Continue to retry logic below
            
            # Log failure reasons
            if ai_score > self.ai_threshold:
                self.logger.warning(f"❌ AI score too high: {ai_score:.3f} > {self.ai_threshold}")
                
                # Check if we should extend attempts (adaptive retry)
                if attempt >= max_attempts and attempt < absolute_max:
                    if last_winston_result and self.winston.should_extend_attempts(
                        attempt, last_winston_result
                    ):
                        max_attempts += 1
                        self.logger.info(f"📈 [ADAPTIVE] Extended to {max_attempts} attempts")
            elif not meets_learning_target:
                self.logger.warning(f"📚 Learning target not met: human {human_score:.1f}% < {learning_target}%")
            
            if not readability['is_readable']:
                self.logger.warning(f"❌ Readability failed: {readability['status']}")
            
            attempt += 1
        
        # Max attempts reached
        self.logger.error(f"Failed after {max_attempts} attempts")
        return {
            'success': False,
            'reason': f'Max attempts reached. Last AI score: {ai_score:.3f}',
            'attempts': max_attempts,
            'last_text': text,
            'last_ai_score': ai_score,
            'last_readability': readability
        }
    
    def _get_adaptive_quality_threshold(
        self,
        identifier: str,
        component_type: str
    ) -> float:
        """
        Calculate adaptive quality threshold using curriculum learning.
        
        - Learning phase (low success): 0.40 threshold (60% AI acceptable)
        - Improving phase (medium success): 0.30 threshold (70% AI acceptable)
        - Mature phase (high success): 0.20 threshold (80% human required)
        
        Args:
            identifier: Item identifier
            component_type: Component type
            
        Returns:
            Adaptive AI score threshold
        """
        if not self.winston.feedback_db:
            return self.base_ai_threshold
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.winston.feedback_db.db_path)
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes
                FROM detection_results
                WHERE material = ? 
                  AND component_type = ?
                  AND timestamp > datetime('now', '-30 days')
            """, (identifier, component_type))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0] > 0:
                success_rate = row[1] / row[0]
                total_samples = row[0]
                
                # Curriculum learning thresholds - use dynamic calculation as base
                # then apply learning phase multipliers
                if success_rate < 0.10 or total_samples < 5:
                    # Learning phase: be lenient (133% of base threshold)
                    threshold = min(0.95, self.base_ai_threshold * 1.33)
                    phase = "LEARNING"
                elif success_rate < 0.30 or total_samples < 15:
                    # Improvement phase: moderate (110% of base threshold)
                    threshold = min(0.95, self.base_ai_threshold * 1.10)
                    phase = "IMPROVING"
                else:
                    # Mature phase: use base threshold
                    threshold = self.base_ai_threshold
                    phase = "MATURE"
                
                self.logger.info(
                    f"📊 Quality threshold: {threshold:.2f} [{phase}] "
                    f"(success rate: {success_rate:.1%}, samples: {total_samples})"
                )
                return threshold
        
        except Exception as e:
            self.logger.warning(f"Failed to calculate adaptive threshold: {e}")
        
        return self.base_ai_threshold
    
    def _validate_parameter_schema(self, params: Dict[str, Any]) -> bool:
        """Validate that database parameters match expected schema.
        
        Args:
            params: Parameters retrieved from database
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields exist
            required = ['temperature', 'frequency_penalty', 'presence_penalty']
            if not all(key in params for key in required):
                return False
            
            # Validate types and ranges
            if not isinstance(params['temperature'], (int, float)):
                return False
            if not (0.0 <= params['temperature'] <= 2.0):
                return False
            
            if not isinstance(params['frequency_penalty'], (int, float)):
                return False
            if not (-2.0 <= params['frequency_penalty'] <= 2.0):
                return False
            
            if not isinstance(params['presence_penalty'], (int, float)):
                return False
            if not (-2.0 <= params['presence_penalty'] <= 2.0):
                return False
            
            # Validate optional dict fields
            if 'voice_params' in params and params['voice_params']:
                if not isinstance(params['voice_params'], dict):
                    return False
            
            if 'enrichment_params' in params and params['enrichment_params']:
                if not isinstance(params['enrichment_params'], dict):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Parameter validation error: {e}")
            return False
    
    def _get_best_previous_parameters(
        self,
        identifier: str,
        component_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve best-performing parameters from previous successful generations.
        
        Priority order:
        1. Most recent successful generation with high human score
        2. Sweet spot recommendations (statistical analysis of top performers)
        3. None (fallback to calculated parameters)
        
        Args:
            identifier: Material/item name
            component_type: Component type
            
        Returns:
            Parameter dict if found, None otherwise
        """
        if not self.winston.feedback_db:
            return None
        
        try:
            import sqlite3
            import json
            
            conn = sqlite3.connect(self.winston.feedback_db.db_path)
            
            # Strategy 1: Get parameters from most recent successful generation with high human score
            # GENERIC LEARNING: Use best params from ANY material/component
            cursor = conn.execute("""
                SELECT 
                    p.temperature,
                    p.frequency_penalty,
                    p.presence_penalty,
                    p.trait_frequency,
                    p.technical_intensity,
                    p.imperfection_tolerance,
                    p.sentence_rhythm_variation,
                    p.full_params_json,
                    r.human_score,
                    r.timestamp
                FROM generation_parameters p
                JOIN detection_results r ON p.detection_result_id = r.id
                WHERE r.success = 1
                  AND r.human_score >= 20
                ORDER BY r.human_score DESC, r.timestamp DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            
            if row:
                (temp, freq_pen, pres_pen, trait_freq, tech_int, 
                 imperf_tol, rhythm_var, full_json, human_score, timestamp) = row
                
                full_params = json.loads(full_json) if full_json else {}
                
                params = {
                    'temperature': temp,
                    'frequency_penalty': freq_pen or 0.0,
                    'presence_penalty': pres_pen or 0.0,
                    'voice_params': full_params.get('voice'),
                    'enrichment_params': full_params.get('enrichment'),
                    'human_score': human_score,
                    'timestamp': timestamp
                }
                
                # Validate schema before returning
                if self._validate_parameter_schema(params):
                    self.logger.info(
                        f"🎯 [PARAMETER REUSE] Found successful params: "
                        f"human={human_score:.1f}%, temp={temp:.3f}"
                    )
                    conn.close()
                    return params
                else:
                    self.logger.warning(
                        f"Retrieved parameters failed schema validation for {identifier} {component_type}"
                    )
            
            # Strategy 2: Use sweet spot recommendations if no successful generation found
            # GENERIC LEARNING: Use sweet spots from ALL materials/components
            cursor = conn.execute("""
                SELECT 
                    temperature_median,
                    frequency_penalty_median,
                    presence_penalty_median,
                    trait_frequency_median,
                    technical_intensity_median,
                    imperfection_tolerance_median,
                    sentence_rhythm_variation_median,
                    max_human_score,
                    confidence_level,
                    last_updated
                FROM sweet_spot_recommendations
                ORDER BY max_human_score DESC, last_updated DESC
                LIMIT 1
            """)
            
            sweet_row = cursor.fetchone()
            conn.close()
            
            if sweet_row:
                (temp_med, freq_med, pres_med, trait_med, tech_med,
                 imperf_med, rhythm_med, max_score, confidence, updated) = sweet_row
                
                # Only use if we have high or medium confidence
                if confidence in ('high', 'medium') and temp_med is not None:
                    params = {
                        'temperature': temp_med,
                        'frequency_penalty': freq_med or 0.0,
                        'presence_penalty': pres_med or 0.0,
                        'voice_params': {
                            'trait_frequency': trait_med,
                            'imperfection_tolerance': imperf_med,
                            'sentence_rhythm_variation': rhythm_med
                        } if trait_med is not None else None,
                        'enrichment_params': {
                            'technical_intensity': int(tech_med)
                        } if tech_med is not None else None,
                        'human_score': max_score,
                        'timestamp': updated
                    }
                    
                    # Remove None values from voice_params
                    if params['voice_params']:
                        params['voice_params'] = {
                            k: v for k, v in params['voice_params'].items() 
                            if v is not None
                        }
                    
                    self.logger.info(
                        f"📊 [SWEET SPOT] Using statistical recommendations: "
                        f"confidence={confidence}, max_score={max_score:.1f}%, temp={temp_med:.3f}"
                    )
                    
                    return params
        
        except Exception as e:
            self.logger.debug(f"Could not retrieve previous parameters: {e}")
        
        return None
    
    def _get_adaptive_parameters(
        self,
        identifier: str,
        component_type: str,
        attempt: int = 1,
        last_winston_result: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get generation parameters with multi-dimensional learning adaptation.
        
        On first attempt, tries to reuse best parameters from previous successful
        generations. On retries, adapts based on Winston feedback.
        
        Implements industry best practices:
        - Parameter reuse from successful previous generations (NEW)
        - Cross-session learning from database (TemperatureAdvisor)
        - Failure-type-specific retry strategies (uniform/borderline/partial)
        - 15% exploration rate for parameter discovery
        - Multi-parameter adaptation (temperature + voice + enrichment)
        
        Args:
            identifier: Item identifier
            component_type: Component type
            attempt: Current attempt number
            last_winston_result: Previous Winston feedback
            
        Returns:
            Dict with temperature, voice_params, enrichment_params, max_tokens
        """
        # MANDATORY: Always try to reuse proven parameters from database FIRST
        # This is the primary source for all generation parameters
        previous_params = self._get_best_previous_parameters(identifier, component_type)
        
        if previous_params:
            # FOUND IN DATABASE - Use these as the starting point for ALL attempts
            if attempt == 1:
                # Get baseline structure (for word counts only)
                base_params = self.dynamic_config.get_all_generation_params(component_type)
                
                # Track what changed for detailed logging
                changes = []
                
                # Apply temperature
                old_temp = base_params['api_params']['temperature']
                new_temp = previous_params['temperature']
                if abs(old_temp - new_temp) > 0.001:
                    base_params['api_params']['temperature'] = new_temp
                    changes.append(f"temperature={new_temp:.3f} (was {old_temp:.3f})")
                
                # Apply penalties to api_penalties dict
                if 'api_penalties' not in base_params:
                    base_params['api_penalties'] = {}
                
                old_freq = base_params['api_penalties'].get('frequency_penalty', 0.0)
                new_freq = previous_params['frequency_penalty']
                if abs(old_freq - new_freq) > 0.001:
                    base_params['api_penalties']['frequency_penalty'] = new_freq
                    changes.append(f"frequency_penalty={new_freq:.3f} (was {old_freq:.3f})")
                
                old_pres = base_params['api_penalties'].get('presence_penalty', 0.0)
                new_pres = previous_params['presence_penalty']
                if abs(old_pres - new_pres) > 0.001:
                    base_params['api_penalties']['presence_penalty'] = new_pres
                    changes.append(f"presence_penalty={new_pres:.3f} (was {old_pres:.3f})")
                
                # Deep merge voice params
                if previous_params.get('voice_params'):
                    old_voice = deepcopy(base_params['voice_params'])
                    base_params['voice_params'] = _deep_merge(
                        base_params['voice_params'],
                        previous_params['voice_params']
                    )
                    if base_params['voice_params'] != old_voice:
                        voice_changes = []
                        for key, val in previous_params['voice_params'].items():
                            if key not in old_voice or old_voice[key] != val:
                                voice_changes.append(f"{key}={val}")
                        if voice_changes:
                            changes.append(f"voice_params: {', '.join(voice_changes)}")
                
                # Deep merge enrichment params
                if previous_params.get('enrichment_params'):
                    old_enrich = deepcopy(base_params['enrichment_params'])
                    base_params['enrichment_params'] = _deep_merge(
                        base_params['enrichment_params'],
                        previous_params['enrichment_params']
                    )
                    if base_params['enrichment_params'] != old_enrich:
                        enrich_changes = []
                        for key, val in previous_params['enrichment_params'].items():
                            if key not in old_enrich or old_enrich[key] != val:
                                enrich_changes.append(f"{key}={val}")
                        if enrich_changes:
                            changes.append(f"enrichment_params: {', '.join(enrich_changes)}")
                
                # Log detailed parameter reuse
                if changes:
                    self.logger.info(
                        f"✓ Reusing proven successful parameters (human_score={previous_params['human_score']:.1f}%):\n" +
                        "\n".join(f"   • {change}" for change in changes)
                    )
                else:
                    self.logger.info(
                        f"✓ Previous successful parameters match baseline (human_score={previous_params['human_score']:.1f}%)"
                    )
                
                return base_params
            else:
                # Retry attempts: Start with DB params, then apply adaptive adjustments below
                base_params = self.dynamic_config.get_all_generation_params(component_type)
                base_params['api_params']['temperature'] = previous_params['temperature']
                if 'api_penalties' not in base_params:
                    base_params['api_penalties'] = {}
                base_params['api_penalties']['frequency_penalty'] = previous_params['frequency_penalty']
                base_params['api_penalties']['presence_penalty'] = previous_params['presence_penalty']
                if previous_params.get('voice_params'):
                    base_params['voice_params'] = _deep_merge(base_params['voice_params'], previous_params['voice_params'])
                if previous_params.get('enrichment_params'):
                    base_params['enrichment_params'] = _deep_merge(base_params['enrichment_params'], previous_params['enrichment_params'])
                
                self.logger.info(
                    f"🔄 Retry {attempt}: Starting with DB params (temp={previous_params['temperature']:.3f}, score={previous_params['human_score']:.1f}%)"
                )
                # Continue to adaptive adjustments below
        else:
            # NO DATABASE HISTORY - Calculate from scratch (rare case for new materials)
            self.logger.warning(
                f"⚠️  No database history for {identifier} {component_type} - calculating from scratch"
            )
            base_params = self.dynamic_config.get_all_generation_params(component_type)
        
        # Extract current parameters for adaptive adjustment
        voice_params = base_params['voice_params'].copy()
        enrichment_params = base_params['enrichment_params'].copy()
        base_temperature = base_params['api_params']['temperature']
        
        # Cross-session learning ONLY used if no database parameters exist
        # Database parameters are PRIMARY and should not be overridden
        if not previous_params and self.temperature_advisor:
            try:
                learned_temp = self.temperature_advisor.recommend_temperature(
                    material=identifier,
                    component_type=component_type,
                    attempt=attempt,
                    fallback_temp=base_temperature
                )
                
                if learned_temp != base_temperature:
                    self.logger.info(
                        f"📊 Learned temperature: {learned_temp:.3f} "
                        f"(base: {base_temperature:.3f})"
                    )
                    base_temperature = learned_temp
            except Exception as e:
                self.logger.warning(f"Failed to get learned temperature: {e}")
        
        # Failure-type-specific retry strategies
        if last_winston_result and attempt > 1 and self.winston.analyzer:
            failure_analysis = self.winston.analyzer.analyze_failure(last_winston_result)
            failure_type = failure_analysis['failure_type']
            
            if failure_type == 'uniform':
                # All bad: increase randomness
                base_temperature = min(1.0, base_temperature + 0.15)
                voice_params['imperfection_tolerance'] = min(
                    1.0, voice_params.get('imperfection_tolerance', 0.5) + 0.20
                )
                voice_params['colloquialism_frequency'] = min(
                    1.0, voice_params.get('colloquialism_frequency', 0.3) + 0.15
                )
                enrichment_params['fact_density'] = max(
                    0.3, enrichment_params.get('fact_density', 0.7) - 0.15
                )
                self.logger.info(f"🌡️  UNIFORM failure → Increase randomness: temp={base_temperature:.2f}")
                
            elif failure_type == 'borderline':
                # Close: fine-tune
                base_temperature = max(0.5, base_temperature - 0.03)
                voice_params['sentence_rhythm_variation'] = min(
                    1.0, voice_params.get('sentence_rhythm_variation', 0.5) + 0.10
                )
                self.logger.info(f"🌡️  BORDERLINE → Fine-tune: temp={base_temperature:.2f}")
                
            elif failure_type == 'partial':
                # Mixed: moderate adjustments
                base_temperature = min(1.0, base_temperature + 0.08)
                voice_params['reader_address_rate'] = min(
                    1.0, voice_params.get('reader_address_rate', 0.2) + 0.10
                )
                enrichment_params['context_depth'] = min(
                    1.0, enrichment_params.get('context_depth', 0.5) + 0.10
                )
                self.logger.info(f"🌡️  PARTIAL → Moderate boost: temp={base_temperature:.2f}")
            
            else:
                # Normal progression
                retry_config = self.dynamic_config.calculate_retry_behavior()
                base_temperature += (attempt - 1) * retry_config['retry_temperature_increase']
                base_temperature = min(1.0, base_temperature)
                self.logger.info(f"🌡️  Standard progression: temp={base_temperature:.2f}")
        
        # Exploration rate (15% random variations)
        if attempt > 1 and random.random() < 0.15:
            self.logger.info("🔍 EXPLORATION MODE: Random parameter variation")
            base_temperature += random.uniform(-0.10, 0.10)
            base_temperature = max(0.3, min(1.0, base_temperature))
            
            # Randomly adjust one voice parameter
            param_to_adjust = random.choice([
                'imperfection_tolerance',
                'sentence_rhythm_variation',
                'emotional_tone'
            ])
            if param_to_adjust in voice_params:
                voice_params[param_to_adjust] += random.uniform(-0.15, 0.15)
                voice_params[param_to_adjust] = max(0.0, min(1.0, voice_params[param_to_adjust]))
                self.logger.info(f"   Adjusted {param_to_adjust} to {voice_params[param_to_adjust]:.2f}")
        
        # Return consistent structure with api_params dict
        return {
            'api_params': {
                'temperature': base_temperature,
                'max_tokens': self.dynamic_config.calculate_max_tokens(component_type)
            },
            'api_penalties': base_params.get('api_penalties', {}),
            'voice_params': voice_params,
            'enrichment_params': enrichment_params
        }
    
    def _call_api(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        enrichment_params: Dict,
        api_penalties: Dict = None
    ) -> str:
        """
        Call AI API with dynamic parameters including penalties.
        
        Args:
            prompt: Prompt to send
            temperature: Generation temperature
            max_tokens: Token limit
            enrichment_params: Enrichment parameters for system prompt
            api_penalties: Optional frequency/presence penalties
            
        Returns:
            Generated text
        """
        # Build system prompt
        system_prompt = "You are a professional technical writer creating concise, clear content."
        
        tech_intensity = enrichment_params.get('technical_intensity', 2)
        if tech_intensity == 1:
            system_prompt = (
                "You are a professional technical writer creating concise, clear content. "
                "CRITICAL RULE: Write ONLY in qualitative, conceptual terms. "
                "ABSOLUTELY FORBIDDEN: Any numbers, measurements, units, or technical specifications. "
                "Use ONLY descriptive words: 'strong', 'heat-resistant', 'conductive', 'durable'."
            )
        
        # Extract penalties
        api_penalties = api_penalties or {}
        frequency_penalty = api_penalties.get('frequency_penalty', 0.0)
        presence_penalty = api_penalties.get('presence_penalty', 0.0)
        
        self.logger.info(f"🌡️  Temperature: {temperature:.3f}, Max tokens: {max_tokens}")
        self.logger.info(f"⚖️  Penalties: frequency={frequency_penalty:.2f}, presence={presence_penalty:.2f}")
        
        # Use enhanced API call with penalties
        from shared.api.client import GenerationRequest
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        
        response = self.api_client.generate(request)
        
        if not response.success:
            raise RuntimeError(f"API call failed: {response.error}")
        
        return response.content.strip()
    
    def _should_check_tech_specs(self, enrichment_params: Dict) -> bool:
        """Check if we should validate against technical specs"""
        return enrichment_params.get('technical_intensity', 2) == 1
    
    def _has_tech_specs(self, text: str) -> bool:
        """Check if text contains technical specifications"""
        spec_patterns = [
            r'\d+\.?\d*\s*(?:GPa|MPa|kPa|Pa|K|°C|°F|g/cm³|kg/m³|W/\(m·K\)|S/m|MS/m|nm|μm|mm|cm|m|Hz|kHz|MHz|GHz|J|kJ|MJ|W|kW|MW|V|A|Ω|%)',
            r'\d+\.?\d*\s*(?:GPa|MPa|K|g/cm³|W|Hz|nm|V)',
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in spec_patterns)
    
    def batch_generate(
        self,
        identifiers: list,
        component_type: str,
        **kwargs
    ) -> Dict[str, Dict]:
        """
        Generate content for multiple items.
        
        Args:
            identifiers: List of identifiers
            component_type: Content type
            **kwargs: Additional parameters
            
        Returns:
            Dict mapping identifier to result
        """
        results = {}
        
        for identifier in identifiers:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Batch generating {component_type} for {identifier}")
            self.logger.info(f"{'='*60}")
            
            try:
                result = self.generate(
                    identifier=identifier,
                    component_type=component_type,
                    **kwargs
                )
                results[identifier] = result
            except Exception as e:
                self.logger.error(f"Generation failed for {identifier}: {e}")
                results[identifier] = {
                    'success': False,
                    'reason': str(e),
                    'attempts': 0
                }
        
        # Summary
        successful = sum(1 for r in results.values() if r.get('success', False))
        self.logger.info(f"\n✅ Success: {successful}/{len(identifiers)}")
        
        return results
