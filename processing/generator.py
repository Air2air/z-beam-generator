"""
Unified Dynamic Content Generator

Single robust generator with fully dynamic parameters that learn from Winston scores.
Replaces both UnifiedMaterialsGenerator and Orchestrator with integrated learning.

ARCHITECTURE:
- All generation flows through this single class
- Starts from /prompts/*.txt templates
- Uses processing/config.yaml as initial parameter baseline
- Parameters (temperature, voice, enrichment) adapt based on Winston feedback
- Integrates existing learning modules (PatternLearner, TemperatureAdvisor, etc.)

WORKFLOW:
1. Load prompt template from /prompts/{component_type}.txt
2. Get initial parameters from config.yaml
3. Enrich with real facts
4. Build unified prompt with dynamic parameters
5. Generate content via API
6. Validate with Winston AI detection
7. Learn from feedback and adjust parameters
8. Retry with adapted parameters on failure
9. Write successful content to Materials.yaml

NO FALLBACKS - Fails explicitly with clear error messages
"""

import logging
import random
import re
import sqlite3
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

# Paths
MATERIALS_DATA_PATH = Path("data/materials/Materials.yaml")
PROMPTS_DIR = Path("prompts")


class DynamicGenerator:
    """
    Single unified generator for all content types with parameter learning.
    
    Responsibilities:
    - Load prompt templates from /prompts/*.txt
    - Get baseline parameters from processing/config.yaml
    - Enrich content with real facts
    - Generate with dynamic parameters
    - Validate with Winston AI detection
    - Learn from feedback and adapt parameters
    - Write successful content to Materials.yaml
    
    Parameter Learning:
    - Temperature: Adjusts based on success/failure patterns
    - Voice params: Refines based on Winston sentence scores
    - Enrichment params: Adapts technical intensity
    - All learning persists to database for cross-session improvement
    """
    
    def __init__(self, api_client):
        """
        Initialize dynamic generator.
        
        Args:
            api_client: API client for content generation (required)
        """
        if not api_client:
            raise ValueError("API client required for content generation")
        
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._init_components()
        
        self.logger.info("DynamicGenerator initialized with learning capabilities")
    
    def _init_components(self):
        """Initialize all required components with fail-fast validation"""
        # Data enricher for real facts
        from processing.enrichment.data_enricher import DataEnricher
        self.enricher = DataEnricher()
        
        # Dynamic config for parameter baseline
        from processing.config.dynamic_config import DynamicConfig
        self.dynamic_config = DynamicConfig()
        
        # Load personas from prompts/personas/ (GROK_INSTRUCTIONS.md Rule 6 compliance)
        self.personas = self._load_all_personas()
        
        # Prompt builder
        from processing.generation.prompt_builder import PromptBuilder
        self.prompt_builder = PromptBuilder
        
        # Winston AI detector
        winston_client = None
        try:
            from shared.api.client_factory import create_api_client
            winston_client = create_api_client('winston')
            self.logger.info("Winston API client initialized")
        except Exception as e:
            raise ValueError(f"Winston API client required but unavailable: {e}")
        
        from processing.detection.ensemble import AIDetectorEnsemble
        self.detector = AIDetectorEnsemble(use_ml=False, winston_client=winston_client)
        
        # Readability validator
        from processing.validation.readability import ReadabilityValidator
        readability_thresholds = self.dynamic_config.calculate_readability_thresholds()
        self.validator = ReadabilityValidator(min_score=readability_thresholds['min'])
        
        # Subjective language validator (November 16, 2025 - catch violations during generation)
        from processing.subjective import SubjectiveValidator
        self.subjective_validator = SubjectiveValidator()
        
        # Winston feedback database and analyzer
        try:
            from processing.config.config_loader import get_config
            config = get_config()
            db_path = config.config.get('winston_feedback_db_path')
            if not db_path:
                raise ValueError("winston_feedback_db_path not configured")
            
            from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
            from processing.detection.winston_analyzer import WinstonFeedbackAnalyzer
            
            self.feedback_db = WinstonFeedbackDatabase(db_path)
            self.analyzer = WinstonFeedbackAnalyzer()
            
            self.logger.info(f"Winston feedback database initialized at {db_path}")
        except Exception as e:
            raise ValueError(f"Winston feedback database required but unavailable: {e}")
        
        # Learning modules for parameter adaptation (pass db_path string, not db object)
        from processing.learning.pattern_learner import PatternLearner
        from processing.learning.temperature_advisor import TemperatureAdvisor
        from processing.learning.prompt_optimizer import PromptOptimizer
        from processing.learning.success_predictor import SuccessPredictor
        from processing.learning.fix_strategy_manager import FixStrategyManager
        from processing.learning.realism_optimizer import RealismOptimizer
        
        self.pattern_learner = PatternLearner(db_path)
        self.temperature_advisor = TemperatureAdvisor(db_path)
        self.prompt_optimizer = PromptOptimizer(db_path)
        self.success_predictor = SuccessPredictor(db_path)
        self.fix_manager = FixStrategyManager(self.feedback_db)
        self.realism_optimizer = RealismOptimizer()  # NEW: Dual-objective optimization
        
        # AI detection threshold (base - will adapt based on learning phase)
        self.base_ai_threshold = self.dynamic_config.calculate_detection_threshold() / 100.0
        self.ai_threshold = self.base_ai_threshold
        
        self.logger.info(f"Base AI detection threshold: {self.base_ai_threshold:.3f}")
    
    def _load_prompt_template(self, component_type: str) -> str:
        """
        Load prompt template from /prompts/{component_type}.txt
        
        Args:
            component_type: Type of content (caption, faq, subtitle, etc.)
            
        Returns:
            Prompt template string
            
        Raises:
            ValueError: If template file doesn't exist
        """
        template_path = PROMPTS_DIR / f"{component_type}.txt"
        if not template_path.exists():
            raise ValueError(f"Prompt template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        self.logger.debug(f"Loaded prompt template: {template_path}")
        return template
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml"""
        from data.materials import load_materials_data
        return load_materials_data()
    
    def _load_all_personas(self) -> Dict[int, Dict]:
        """
        Load all persona YAML files from prompts/personas/ directory.
        Maps author IDs to persona configurations.
        
        Returns:
            Dict mapping author_id to persona configuration
        """
        personas_dir = Path("prompts/personas")
        if not personas_dir.exists():
            raise ValueError(f"Personas directory not found: {personas_dir}")
        
        # Map persona files to author IDs (matches old AuthorVoiceStore mapping)
        author_id_map = {
            1: "indonesia",
            2: "united_states", 
            3: "taiwan",
            4: "italy"
        }
        
        personas = {}
        for author_id, filename in author_id_map.items():
            yaml_path = personas_dir / f"{filename}.yaml"
            if not yaml_path.exists():
                self.logger.warning(f"Persona file not found: {yaml_path}, skipping author_id {author_id}")
                continue
            
            try:
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    persona_config = yaml.safe_load(f)
                    personas[author_id] = persona_config
                    self.logger.debug(f"Loaded persona for author_id {author_id}: {persona_config.get('name', 'Unknown')}")
            except Exception as e:
                self.logger.error(f"Failed to load persona from {yaml_path}: {e}")
        
        if not personas:
            raise ValueError("No personas loaded from prompts/personas/ directory")
        
        self.logger.info(f"Loaded {len(personas)} personas from prompts/personas/")
        return personas
    
    def _get_persona_by_author_id(self, author_id: int) -> Dict:
        """
        Get persona configuration by author ID.
        
        Args:
            author_id: Author identifier (1-4)
            
        Returns:
            Persona configuration dictionary
            
        Raises:
            ValueError: If author_id not found
        """
        if author_id not in self.personas:
            available = list(self.personas.keys())
            raise ValueError(f"Author ID {author_id} not found. Available: {available}")
        
        return self.personas[author_id]
    
    def _build_context(self, material_data: Dict) -> str:
        """Build context string from material data"""
        context_parts = []
        
        if 'category' in material_data:
            context_parts.append(f"Category: {material_data['category']}")
        
        if 'description' in material_data:
            context_parts.append(f"Description: {material_data['description'][:300]}")
        
        properties = material_data.get('materialProperties', {})
        key_props = []
        for prop in ['hardness', 'thermalConductivity', 'density', 'meltingPoint']:
            if prop in properties:
                key_props.append(f"{prop}: {properties[prop]}")
        
        if key_props:
            context_parts.append("Properties: " + ", ".join(key_props[:5]))
        
        return "\n".join(context_parts)
    
    def _get_adaptive_quality_threshold(self, material_name: str, component_type: str) -> float:
        """
        Calculate adaptive quality threshold based on historical success rate.
        
        Uses curriculum learning approach:
        - Learning phase (low success): Accept 60% AI (0.40 threshold)
        - Improvement phase (medium success): Accept 70% AI (0.30 threshold)  
        - Mature phase (high success): Strict 80% human (0.20 threshold)
        
        Args:
            material_name: Material being generated for
            component_type: Component type
            
        Returns:
            Adaptive AI score threshold (lower = stricter)
        """
        try:
            # Query database for recent success rate
            conn = sqlite3.connect(self.feedback_db.db_path)
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes
                FROM detection_results
                WHERE material = ? 
                  AND component_type = ?
                  AND timestamp > datetime('now', '-30 days')
            """, (material_name, component_type))
            
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
                    f"📊 Quality threshold: {threshold:.2f} "
                    f"[{phase}] (success rate: {success_rate:.1%}, samples: {total_samples})"
                )
                return threshold
            
        except Exception as e:
            self.logger.warning(f"Failed to calculate adaptive threshold: {e}")
        
        # Default to base threshold
        return self.base_ai_threshold
    
    def _get_adaptive_parameters(
        self, 
        material_name: str, 
        component_type: str,
        attempt: int = 1,
        last_winston_result: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get generation parameters with multi-dimensional learning-based adaptation.
        
        INDUSTRY BEST PRACTICES IMPLEMENTED:
        - ✅ Cross-session learning from database (TemperatureAdvisor)
        - ✅ Failure-type-specific retry strategies (uniform/borderline/partial)
        - ✅ 15% exploration rate for parameter discovery
        - ✅ Multi-parameter adaptation (temperature + voice + enrichment)
        - ✅ Adaptive adjustments based on Winston sentence analysis
        
        Args:
            material_name: Material being generated for
            component_type: Component type
            attempt: Current attempt number
            last_winston_result: Previous Winston feedback (if any)
            
        Returns:
            Dict with adapted parameters:
            - temperature: Adapted temperature
            - voice_params: Adapted voice parameters  
            - enrichment_params: Adapted enrichment parameters
            - max_tokens: Token limit
        """
        # Get baseline parameters from config
        base_params = self.dynamic_config.get_all_generation_params(component_type)
        voice_params = base_params['voice_params'].copy()
        enrichment_params = base_params['enrichment_params'].copy()
        
        # Extract base temperature from config
        base_temperature = self.dynamic_config.calculate_temperature(component_type)
        
        # BEST PRACTICE 1: Cross-session learning from historical data
        try:
            learned_temp = self.temperature_advisor.recommend_temperature(
                material=material_name,
                component_type=component_type,
                attempt=attempt,
                fallback_temp=base_temperature
            )
            
            if learned_temp != base_temperature:
                self.logger.info(f"📊 Learned temperature: {learned_temp:.3f} (base: {base_temperature:.3f})")
                base_temperature = learned_temp
        except Exception as e:
            self.logger.warning(f"Failed to get learned temperature: {e}")
        
        # BEST PRACTICE 2: Use standardized fix strategy system
        if last_winston_result and attempt > 1:
            failure_analysis = self.analyzer.analyze_failure(last_winston_result)
            
            # Get fix strategy from standardized system
            fix_strategy = self.fix_manager.get_fix_strategy(
                failure_analysis=failure_analysis,
                attempt=attempt,
                material=material_name,
                component_type=component_type,
                previous_strategy_id=getattr(self, '_last_strategy_id', None)
            )
            
            # NEW: Incorporate realism feedback if available from last attempt
            if hasattr(self, '_last_realism_score') and hasattr(self, '_last_ai_tendencies'):
                try:
                    from processing.learning.realism_optimizer import RealismOptimizer
                    optimizer = RealismOptimizer()
                    
                    current_params = {
                        'temperature': base_temperature,
                        'frequency_penalty': 0.0,  # Will be calculated by dynamic_config
                        'presence_penalty': 0.0,
                        'voice_params': voice_params
                    }
                    
                    # Get realism-based adjustments
                    realism_adjustments = optimizer.suggest_parameter_adjustments(
                        ai_tendencies=self._last_ai_tendencies,
                        current_params=current_params
                    )
                    
                    # Blend Winston-based and Realism-based adjustments (60% realism, 40% winston)
                    if 'temperature' in realism_adjustments:
                        realism_temp_adj = realism_adjustments['temperature'] - base_temperature
                        winston_temp_adj = fix_strategy['temperature_adjustment']
                        blended_temp_adj = (realism_temp_adj * 0.6) + (winston_temp_adj * 0.4)
                        base_temperature = min(1.0, base_temperature + blended_temp_adj)
                        self.logger.info(f"🎯 Blended adjustment: Winston {winston_temp_adj:.3f} + Realism {realism_temp_adj:.3f} = {blended_temp_adj:.3f}")
                    
                    # Apply realism voice adjustments
                    if 'voice_params' in realism_adjustments:
                        for param, value in realism_adjustments['voice_params'].items():
                            if param in voice_params:
                                # Blend: 60% realism suggestion, 40% current
                                blended_value = (value * 0.6) + (voice_params[param] * 0.4)
                                voice_params[param] = max(0.0, min(1.0, blended_value))
                
                except Exception as e:
                    self.logger.warning(f"Failed to apply realism adjustments: {e}")
            
            # Apply temperature adjustment (may have been modified by realism feedback above)
            if 'temperature_adjustment' in fix_strategy and not hasattr(self, '_last_realism_score'):
                base_temperature = min(1.0, base_temperature + fix_strategy['temperature_adjustment'])
            
            # Apply voice adjustments
            for param, adjustment in fix_strategy['voice_adjustments'].items():
                current_value = voice_params.get(param, 0.5)
                voice_params[param] = max(0.0, min(1.0, current_value + adjustment))
            
            # Apply enrichment adjustments
            for param, adjustment in fix_strategy['enrichment_adjustments'].items():
                current_value = enrichment_params.get(param, 0.5)
                enrichment_params[param] = max(0.0, min(1.0, current_value + adjustment))
            
            # Log fix attempt to database
            if hasattr(self, '_last_detection_id'):
                fix_attempt_id = self.fix_manager.log_fix_attempt(
                    detection_id=self._last_detection_id,
                    attempt_number=attempt,
                    strategy=fix_strategy,
                    material=material_name,
                    component_type=component_type
                )
                self._last_fix_attempt_id = fix_attempt_id
            
            # Remember strategy for next attempt
            self._last_strategy_id = fix_strategy['strategy_id']
            
            self.logger.info(
                f"🌡️  {fix_strategy['strategy_name']}: "
                f"temp={base_temperature:.2f}"
            )
        
        # BEST PRACTICE 3: Exploration rate (15% of time, try random variations)
        if attempt > 1 and random.random() < 0.15:
            self.logger.info("🔍 EXPLORATION MODE: Trying random parameter variation")
            base_temperature += random.uniform(-0.10, 0.10)
            base_temperature = max(0.3, min(1.0, base_temperature))
            
            # Randomly adjust one voice parameter
            param_to_adjust = random.choice(['imperfection_tolerance', 'sentence_rhythm_variation', 'emotional_tone'])
            if param_to_adjust in voice_params:
                voice_params[param_to_adjust] += random.uniform(-0.15, 0.15)
                voice_params[param_to_adjust] = max(0.0, min(1.0, voice_params[param_to_adjust]))
                self.logger.info(f"   Adjusted {param_to_adjust} to {voice_params[param_to_adjust]:.2f}")
        
        # Build final params dict with adapted multi-parameter values
        # Extract API penalties from base_params - FAIL FAST if missing
        # NOTE: Grok doesn't support penalties, but we calculate and log them for:
        #   1. Learning system (parameter correlation analysis)
        #   2. Future provider switching (OpenAI, Anthropic support penalties)
        #   3. Research (understanding what would work with penalty-capable models)
        if 'api_params' not in base_params:
            raise ValueError("Missing 'api_params' in base_params - configuration error")
        if 'penalties' not in base_params['api_params']:
            raise ValueError("Missing 'penalties' in api_params - configuration error")
        
        api_penalties = base_params['api_params']['penalties']
        
        return {
            'temperature': base_temperature,
            'voice_params': voice_params,
            'enrichment_params': enrichment_params,
            'max_tokens': self.dynamic_config.calculate_max_tokens(component_type),
            'api_penalties': api_penalties  # Logged but not sent to Grok (filtered in API client)
        }
    
    def _write_to_materials_yaml(self, material_name: str, component_type: str, content_data: Any):
        """
        Write generated content to Materials.yaml atomically.
        
        Args:
            material_name: Name of material
            component_type: Type of content
            content_data: Content data to write
        """
        materials_data = self._load_materials_data()
        
        if material_name not in materials_data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        materials_data['materials'][material_name][component_type] = content_data
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=MATERIALS_DATA_PATH.parent,
            delete=False,
            suffix='.yaml'
        ) as temp_f:
            yaml.dump(materials_data, temp_f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            temp_path = temp_f.name
        
        Path(temp_path).replace(MATERIALS_DATA_PATH)
        self.logger.info(f"✅ {component_type} written to Materials.yaml → materials.{material_name}.{component_type}")
    
    def generate(
        self,
        material_name: str,
        component_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content with dynamic learning-based parameters.
        
        Args:
            material_name: Name of material
            component_type: Type of content (caption, faq, subtitle, etc.)
            **kwargs: Additional parameters (e.g., faq_count)
            
        Returns:
            Dict with:
            - success: bool
            - content: Generated content (if successful)
            - attempts: Number of attempts
            - ai_score: Final AI detection score
            - reason: Failure reason (if failed)
        """
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Generating {component_type} for {material_name}")
        self.logger.info(f"{'='*60}")
        
        # Load material data
        materials_data = self._load_materials_data()
        if material_name not in materials_data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        material_data = materials_data['materials'][material_name]
        
        # Get author ID and load corresponding persona
        author_id = material_data.get('author', {}).get('id', 2)
        voice = self._get_persona_by_author_id(author_id)
        
        # Enrich with real facts
        facts = self.enricher.fetch_real_facts(material_name)
        context = self._build_context(material_data)
        
        # Determine length
        from processing.generation.component_specs import ComponentRegistry
        spec = ComponentRegistry.get_spec(component_type)
        length = random.randint(spec.min_length, spec.max_length)
        self.logger.info(f"🎲 Target length: {length} words (range: {spec.min_length}-{spec.max_length})")
        
        # Set adaptive quality threshold based on historical success (curriculum learning)
        self.ai_threshold = self._get_adaptive_quality_threshold(material_name, component_type)
        
        # Generation loop with learning
        max_attempts = 5  # Increased for learning phase to gather more training data
        attempt = 1
        last_winston_result = None
        last_realism_result = None  # NEW: Track realism evaluation results
        regeneration_triggered = False  # Track if we've already done a fresh regeneration
        improvement_history = []  # Track human score improvements to detect stuck patterns
        realism_history = []  # NEW: Track realism score improvements
        
        while attempt <= max_attempts:
            self.logger.info(f"\nAttempt {attempt}/{max_attempts}")
            
            # Get adaptive parameters (learns from feedback)
            params = self._get_adaptive_parameters(
                material_name, 
                component_type, 
                attempt,
                last_winston_result
            )
            
            # Format facts string
            facts_str = self.enricher.format_facts_for_prompt(
                facts, 
                enrichment_params=params['enrichment_params'],
                voice_params=params['voice_params']
            )
            
            # Build prompt with dynamic parameters
            import time
            variation_seed = int(time.time() * 1000) + attempt
            
            prompt = self.prompt_builder.build_unified_prompt(
                topic=material_name,
                voice=voice,
                length=length,
                facts=facts_str,
                context=context,
                component_type=component_type,
                domain='materials',
                voice_params=params['voice_params'],
                enrichment_params=params['enrichment_params'],
                variation_seed=variation_seed
            )
            
            # SELF-LEARNING: Optimize prompt with learned patterns from Winston feedback
            # Run on EVERY attempt to continuously learn and adapt
            if self.prompt_optimizer:
                optimization_result = self.prompt_optimizer.optimize_prompt(
                    base_prompt=prompt,
                    material=material_name,
                    component_type=component_type,
                    include_patterns=True,
                    include_recommendations=True
                )
                
                if optimization_result['confidence'] != 'none':
                    prompt = optimization_result['optimized_prompt']
                    self.logger.info(f"🧠 Attempt {attempt}: Prompt optimized with learned patterns:")
                    self.logger.info(f"   Confidence: {optimization_result['confidence']}")
                    self.logger.info(f"   Patterns analyzed: {optimization_result.get('patterns_analyzed', 0)}")
                    self.logger.info(f"   Expected improvement: {optimization_result['expected_improvement']*100:.1f}%")
                    for addition in optimization_result['additions']:
                        self.logger.info(f"   + {addition}")
                else:
                    self.logger.info(f"🧠 Attempt {attempt}: Prompt optimizer: {optimization_result.get('reason', 'Insufficient data')}")
            
            # ADDITIONAL adjustment on retry (stacks with prompt optimizer)
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
                    params['temperature'],
                    params['max_tokens'],
                    params['enrichment_params'],
                    params.get('api_penalties', {})  # NEW: Pass API penalties
                )
            except Exception as e:
                self.logger.error(f"API call failed: {e}")
                if attempt >= max_attempts:
                    return {
                        'success': False,
                        'reason': f'API error: {e}',
                        'attempts': attempt
                    }
                attempt += 1
                continue
            
            # Validate with Winston
            detection = self.detector.detect(text)
            ai_score = detection['ai_score']
            last_winston_result = detection
            
            self.logger.info(f"AI score: {ai_score:.3f} (threshold: {self.ai_threshold:.3f})")
            
            # Check for subjective language violations (November 16, 2025 integration)
            # Pass Winston human score for dynamic threshold calculation
            human_score = detection.get('human_score', 0)
            subjective_valid, subjective_details = self.subjective_validator.validate(text, winston_score=human_score)
            if not subjective_valid:
                violation_summary = self.subjective_validator.get_violation_summary(subjective_details)
                self.logger.warning(f"❌ Subjective language violations detected:\n{violation_summary}")
            else:
                self.logger.info(f"✅ No subjective language violations (thresholds: {subjective_details.get('applied_thresholds', {})})")
            
            # Check readability
            readability = self.validator.validate(text)
            self.logger.info(f"Readability: {readability['status']}")
            
            # Per-iteration realism evaluation for learning (runs on EVERY iteration)
            # Even failures provide valuable training data for parameter optimization
            realism_score = None
            voice_authenticity = None
            tonal_consistency = None
            ai_tendencies = None
            
            try:
                from processing.subjective import SubjectiveEvaluator
                from shared.api.client_factory import create_api_client
                
                # Create Grok client for realism evaluation
                grok_client = create_api_client('grok')
                realism_evaluator = SubjectiveEvaluator(
                    api_client=grok_client,
                    quality_threshold=7.0,
                    verbose=False
                )
                
                # Run realism evaluation (parallel with Winston conceptually)
                realism_result = realism_evaluator.evaluate(
                    content=text,
                    material_name=material_name,
                    component_type=component_type
                )
                
                if realism_result:
                    realism_score = realism_result.overall_score
                    
                    # Extract dimension scores for detailed feedback
                    voice_authenticity = None
                    tonal_consistency = None
                    for dim_score in realism_result.dimension_scores:
                        if dim_score.dimension.value == 'voice_authenticity':
                            voice_authenticity = dim_score.score
                        elif dim_score.dimension.value == 'tonal_consistency':
                            tonal_consistency = dim_score.score
                    
                    # Calculate AI tendencies for learning
                    ai_tendencies = {}
                    for dim_score in realism_result.dimension_scores:
                        dim = dim_score.dimension.value
                        # Higher score = more human, lower = more AI tendency
                        tendency_strength = max(0, 7.0 - dim_score.score) / 7.0
                        if dim == 'voice_authenticity':
                            ai_tendencies['generic_language'] = tendency_strength
                        elif dim == 'tonal_consistency':
                            ai_tendencies['unnatural_transitions'] = tendency_strength
                        elif dim == 'human_likeness':
                            ai_tendencies['ai_patterns'] = tendency_strength
                    
                    # Store for next iteration's parameter adjustments
                    self._last_realism_score = realism_score
                    self._last_ai_tendencies = ai_tendencies
                    
                    self.logger.info(f"🤖 Realism Score: {realism_score:.1f}/10")
                    if voice_authenticity:
                        self.logger.info(f"   Voice Authenticity: {voice_authenticity:.1f}/10")
                    if tonal_consistency:
                        self.logger.info(f"   Tonal Consistency: {tonal_consistency:.1f}/10")
                    if ai_tendencies:
                        self.logger.info(f"📊 AI Tendencies: {ai_tendencies}")
                    
                    # Update learned patterns from evaluation result
                    # This happens IMMEDIATELY after evaluation to capture learnings
                    try:
                        from processing.learning.subjective_pattern_learner import SubjectivePatternLearner
                        from pathlib import Path
                        
                        learner = SubjectivePatternLearner(
                            patterns_file=Path('prompts/evaluation/learned_patterns.yaml')
                        )
                        
                        # Update patterns based on this evaluation
                        learner.update_from_evaluation(
                            evaluation_result={
                                'overall_score': realism_score,
                                'dimension_scores': {
                                    'voice_authenticity': voice_authenticity,
                                    'tonal_consistency': tonal_consistency
                                },
                                'ai_tendencies': list(ai_tendencies.keys()) if ai_tendencies else [],
                                'violations': []  # Extract from realism_result if available
                            },
                            content=text,
                            accepted=False,  # Will update to True later if accepted
                            component_type=component_type,
                            material_name=material_name
                        )
                        
                        self.logger.info("📚 [LEARNING] Updated subjective evaluation patterns")
                    except Exception as learn_error:
                        self.logger.warning(f"Failed to update learned patterns: {learn_error}")
                        
            except Exception as e:
                self.logger.warning(f"Realism evaluation unavailable: {e}")
                # Continue without realism - Winston still works
            
            # Calculate composite quality score (Winston + Subjective + Readability)
            composite_score = None
            try:
                from processing.evaluation.composite_scorer import CompositeScorer
                scorer = CompositeScorer()  # Uses learned weights
                
                composite_result = scorer.calculate(
                    winston_human_score=human_score,
                    subjective_overall_score=realism_score,  # 0-10 scale
                    readability_score=readability.get('score')  # 0-100 scale
                )
                composite_score = composite_result['composite_score']
                
                self.logger.info(
                    f"📊 Composite Quality: {composite_score:.1f}/100 "
                    f"(Winston: {composite_result['winston_contribution']:.1f}, "
                    f"Subjective: {composite_result.get('subjective_contribution', 0):.1f}, "
                    f"Readability: {composite_result.get('readability_contribution', 0):.1f})"
                )
                self.logger.info(f"   Weights: {composite_result['weights_source']}")
            except Exception as e:
                self.logger.warning(f"Composite scoring failed: {e}, using Winston only")
                composite_score = human_score  # Fallback to Winston score
            
            # Log to feedback database for learning
            try:
                failure_analysis = self.analyzer.analyze_failure(detection)
                detection_id = self.feedback_db.log_detection(
                    material=material_name,
                    component_type=component_type,
                    generated_text=text,
                    winston_result=detection,
                    temperature=params['temperature'],
                    attempt=attempt,
                    success=(ai_score <= self.ai_threshold and readability['is_readable'] and subjective_valid),
                    failure_analysis=failure_analysis,
                    composite_quality_score=composite_score  # NEW: Store composite score
                )
                self.logger.info(f"📊 Logged result to database (ID: {detection_id})")
                
                # Track detection ID for fix outcome logging
                self._last_detection_id = detection_id
                
                # If we had a previous fix attempt, log the outcome
                if hasattr(self, '_last_fix_attempt_id') and hasattr(self, '_previous_human_score'):
                    self.fix_manager.log_fix_outcome(
                        fix_attempt_id=self._last_fix_attempt_id,
                        next_detection_id=detection_id,
                        success=(ai_score <= self.ai_threshold and readability['is_readable']),
                        human_score_before=self._previous_human_score,
                        human_score_after=detection.get('human_score', 0.0),
                        material=material_name,
                        component_type=component_type
                    )
                
                # Store human score for next iteration
                self._previous_human_score = detection.get('human_score', 0.0)
                
                # Log generation parameters for machine learning
                try:
                    # Restructure params to match expected format
                    structured_params = {
                        'material_name': material_name,
                        'component_type': component_type,
                        'attempt': attempt,
                        'api': {
                            'temperature': params['temperature'],
                            'max_tokens': params['max_tokens'],
                            'frequency_penalty': params.get('api_penalties', {}).get('frequency_penalty', 0.0),
                            'presence_penalty': params.get('api_penalties', {}).get('presence_penalty', 0.0)
                        },
                        'voice': params.get('voice_params', {}),
                        'enrichment': params.get('enrichment_params', {}),
                        'validation': {
                            'detection_threshold': self.ai_threshold,
                            'readability_min': 0.0,
                            'readability_max': 100.0,
                            'grammar_strictness': 0.8,
                            'confidence_high': 0.9,
                            'confidence_medium': 0.7
                        },
                        'retry': {
                            'max_attempts': max_attempts,
                            'retry_temperature_increase': 0.05
                        }
                    }
                    param_id = self.feedback_db.log_generation_parameters(detection_id, structured_params)
                    self.logger.info(f"📊 Logged parameters #{param_id} for detection #{detection_id}")
                except Exception as param_error:
                    self.logger.error(f"❌ Failed to log generation parameters: {param_error}")
                    import traceback
                    self.logger.error(traceback.format_exc())
            except Exception as e:
                self.logger.warning(f"Failed to log to database: {e}")
            
            # Dual-objective decision: Winston (40%) + Realism (60%)
            # Both contribute to learning on EVERY iteration (success or failure)
            human_score = detection.get('human_score', 0)
            learning_target = self.dynamic_config.base_config.get_learning_target()
            
            # Combined scoring: Winston detection + Realism evaluation
            if realism_score is not None:
                # Normalize Winston to 0-10 scale, combine with realism
                winston_normalized = human_score / 10.0  # 0-100 -> 0-10
                combined_score = (winston_normalized * 0.4) + (realism_score * 0.6)
                combined_score_percent = combined_score * 10  # Back to 0-100 scale
                self.logger.info(f"📊 Combined Score: {combined_score:.1f}/10 (Winston: {human_score:.1f}%, Realism: {realism_score:.1f}/10)")
            else:
                # Fallback to Winston-only if realism unavailable
                combined_score = human_score / 10.0
                combined_score_percent = human_score
                self.logger.info(f"📊 Winston Score: {human_score:.1f}% (target: {learning_target:.1f}%)")
            
            # CRITICAL: Realism score must pass quality gate (7.0/10 minimum)
            passes_realism_gate = True  # Default if no realism evaluation
            if realism_score is not None:
                realism_threshold = 7.0  # Minimum quality threshold
                passes_realism_gate = realism_score >= realism_threshold
                if not passes_realism_gate:
                    self.logger.warning(
                        f"❌ Realism score below threshold: {realism_score:.1f}/10 < {realism_threshold}/10"
                    )
            
            passes_acceptance = (
                ai_score <= self.ai_threshold and 
                readability['is_readable'] and 
                subjective_valid and
                passes_realism_gate  # NEW: Realism is now a quality gate
            )
            # Use combined score (Winston + Realism) for quality target decision
            meets_quality_target = combined_score_percent >= learning_target
            
            # Check if successful for BOTH acceptance and quality target
            if passes_acceptance and meets_quality_target:
                self.logger.info(
                    f"✅ Success on attempt {attempt} "
                    f"(Combined: {combined_score_percent:.1f}%, target: {learning_target:.1f}%)"
                )
                
                # Extract component-specific content
                content_data = self._extract_content(text, component_type)
                
                # Write to Materials.yaml
                self._write_to_materials_yaml(material_name, component_type, content_data)
                
                # Log realism-based learning for future parameter optimization
                # This happens on SUCCESS to capture what worked
                if realism_score is not None and ai_tendencies:
                    try:
                        from processing.learning.realism_optimizer import RealismOptimizer
                        optimizer = RealismOptimizer()
                        
                        # Get suggested parameter adjustments
                        current_params = {
                            'temperature': params['temperature'],
                            'frequency_penalty': params.get('api_penalties', {}).get('frequency_penalty', 0.0),
                            'presence_penalty': params.get('api_penalties', {}).get('presence_penalty', 0.0),
                            'voice_params': params.get('voice_params', {})
                        }
                        
                        suggested = optimizer.suggest_parameter_adjustments(
                            ai_tendencies=ai_tendencies,
                            current_params=current_params
                        )
                        
                        # Log to realism_learning table for future generations
                        self.feedback_db.log_realism_learning(
                            topic=material_name,
                            component_type=component_type,
                            ai_tendencies=ai_tendencies,
                            suggested_params=suggested,
                            realism_score=realism_score
                        )
                        
                        self.logger.info(f"📚 [LEARNING] Realism data logged for successful iteration {attempt}")
                    except Exception as learn_error:
                        self.logger.warning(f"Failed to log realism learning: {learn_error}")
                
                # Update learned patterns to mark as accepted (success patterns)
                if realism_score is not None:
                    try:
                        from processing.learning.subjective_pattern_learner import SubjectivePatternLearner
                        from pathlib import Path
                        
                        learner = SubjectivePatternLearner(
                            patterns_file=Path('prompts/evaluation/learned_patterns.yaml')
                        )
                        
                        # Update patterns with successful acceptance
                        learner.update_from_evaluation(
                            evaluation_result={
                                'overall_score': realism_score,
                                'dimension_scores': {
                                    'voice_authenticity': voice_authenticity,
                                    'tonal_consistency': tonal_consistency
                                },
                                'ai_tendencies': list(ai_tendencies.keys()) if ai_tendencies else [],
                                'violations': []
                            },
                            content=text,
                            accepted=True,  # Mark as accepted for success pattern learning
                            component_type=component_type,
                            material_name=material_name
                        )
                        
                        self.logger.info("📚 [LEARNING] Updated patterns with successful acceptance")
                    except Exception as learn_error:
                        self.logger.warning(f"Failed to update learned patterns on success: {learn_error}")
                
                return {
                    'success': True,
                    'content': content_data,
                    'text': text,
                    'attempts': attempt,
                    'ai_score': ai_score,
                    'human_score': human_score,
                    'realism_score': realism_score,
                    'combined_score': combined_score,
                    'readability': readability
                }
            
            # Passes acceptance but needs quality improvement
            if passes_acceptance and not meets_quality_target:
                self.logger.warning(
                    f"⚠️  Passes acceptance but below quality target "
                    f"(Winston: {combined_score:.1f}% < {learning_target:.1f}%)"
                )
                # Continue to retry logic with parameter adjustments
            
            # Log failure reasons with specific guidance
            failure_reasons = []
            if ai_score > self.ai_threshold:
                failure_reasons.append(f"AI score too high: {ai_score:.3f} > {self.ai_threshold:.3f}")
            if not readability['is_readable']:
                failure_reasons.append("Readability check failed")
            if not subjective_valid:
                failure_reasons.append("Subjective language violations detected")
            if not passes_realism_gate:
                failure_reasons.append(f"Realism score too low: {realism_score:.1f}/10 < 7.0/10")
            if not meets_quality_target:
                failure_reasons.append(f"Quality target not met: {combined_score_percent:.1f}% < {learning_target}%")
            
            if failure_reasons:
                self.logger.warning(f"❌ Attempt {attempt} failed: {', '.join(failure_reasons)}")
            if not readability['is_readable']:
                self.logger.warning(f"❌ Readability failed: {readability['status']}")
            if not subjective_valid:
                self.logger.warning(f"❌ Subjective validation failed: {subjective_details['total_violations']} violations")
            
            # Log realism learning even for FAILURES - they provide valuable training data
            # Knowing what NOT to do is as important as knowing what works
            if realism_score is not None and ai_tendencies:
                try:
                    from processing.learning.realism_optimizer import RealismOptimizer
                    optimizer = RealismOptimizer()
                    
                    # Get suggested parameter adjustments based on what failed
                    current_params = {
                        'temperature': params['temperature'],
                        'frequency_penalty': params.get('api_penalties', {}).get('frequency_penalty', 0.0),
                        'presence_penalty': params.get('api_penalties', {}).get('presence_penalty', 0.0),
                        'voice_params': params.get('voice_params', {})
                    }
                    
                    suggested = optimizer.suggest_parameter_adjustments(
                        ai_tendencies=ai_tendencies,
                        current_params=current_params
                    )
                    
                    # Log to realism_learning table - mark as failure for learning
                    self.feedback_db.log_realism_learning(
                        topic=material_name,
                        component_type=component_type,
                        ai_tendencies=ai_tendencies,
                        suggested_params=suggested,
                        realism_score=realism_score,
                        success=False  # This iteration failed
                    )
                    
                    self.logger.info(f"📚 [LEARNING] Failure pattern logged for iteration {attempt} (builds training data)")
                except Exception as learn_error:
                    self.logger.warning(f"Failed to log failure learning: {learn_error}")
            
            # SMART REGENERATION: Track improvement to detect stuck patterns
            improvement_history.append(human_score)
            
            # If we have 3+ attempts and zero improvement detected, trigger fresh regeneration
            if attempt >= 3 and not regeneration_triggered:
                # Check if stuck (no improvement across last 3 attempts)
                if len(improvement_history) >= 3:
                    recent_improvements = [
                        improvement_history[i] - improvement_history[i-1] 
                        for i in range(len(improvement_history)-2, len(improvement_history))
                    ]
                    
                    # All improvements are 0 or negative = stuck
                    if all(improvement <= 0.0 for improvement in recent_improvements):
                        self.logger.warning(
                            f"🔄 STUCK PATTERN DETECTED: Zero improvement across {len(recent_improvements)} attempts "
                            f"({improvement_history[-3]:.1f}% → {improvement_history[-2]:.1f}% → {improvement_history[-1]:.1f}%)"
                        )
                        
                        if attempt < max_attempts:
                            self.logger.info("🆕 Triggering FRESH REGENERATION with new random seed...")
                            regeneration_triggered = True
                            last_winston_result = None  # Reset to trigger new generation path
                            improvement_history = []  # Reset tracking
                            # Continue to next attempt with fresh start
                        else:
                            self.logger.error("❌ Cannot trigger regeneration - already at max attempts")
            
            # SAFETY: If regeneration was triggered and still failing, stop immediately
            if regeneration_triggered and attempt >= max_attempts:
                self.logger.error(
                    f"❌ REGENERATION FAILED: Fresh generation attempt also failed after {attempt} total attempts"
                )
                raise ValueError(
                    f"{component_type.capitalize()} generation failed after fresh regeneration. "
                    f"Last AI score: {ai_score:.3f}, Human score: {human_score:.1f}%. "
                    f"Both original and regenerated content failed quality checks. "
                    f"This material may require manual review or prompt adjustments."
                )
            
            attempt += 1
        
        # Max attempts reached
        raise ValueError(
            f"{component_type.capitalize()} generation failed after {max_attempts} attempts. "
            f"Last AI score: {ai_score:.3f}. "
            f"This is a quality check failure - parameters need adjustment."
        )
    
    def _call_api(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        enrichment_params: Dict,
        api_penalties: Dict = None
    ) -> str:
        """
        Call AI API with dynamic parameters.
        
        NOTE: Penalties are calculated and logged for research/learning but NOT sent to Grok.
        Grok API rejects frequency_penalty/presence_penalty (returns 400 error).
        API client automatically filters these parameters for Grok models.
        
        Args:
            prompt: Prompt to send
            temperature: Generation temperature
            max_tokens: Token limit
            enrichment_params: Enrichment parameters for system prompt
            api_penalties: Frequency/presence penalties (logged but not sent to Grok)
            
        Returns:
            Generated text
        """
        # Build system prompt
        system_prompt = "You are a professional technical writer creating concise, clear content."
        
        tech_intensity = enrichment_params.get('technical_intensity', 0.22)  # 0.0-1.0 normalized
        if tech_intensity < 0.15:  # Very low (slider 1-2)
            system_prompt = (
                "You are a professional technical writer creating concise, clear content. "
                "CRITICAL RULE: Write ONLY in qualitative, conceptual terms. "
                "ABSOLUTELY FORBIDDEN: Any numbers, measurements, units, or technical specifications. "
                "Use ONLY descriptive words: 'strong', 'heat-resistant', 'conductive', 'durable'."
            )
        
        # Extract penalties - FAIL FAST if missing
        if not api_penalties:
            raise ValueError("Missing api_penalties parameter - configuration error")
        if 'frequency_penalty' not in api_penalties:
            raise ValueError("Missing 'frequency_penalty' in api_penalties - configuration error")
        if 'presence_penalty' not in api_penalties:
            raise ValueError("Missing 'presence_penalty' in api_penalties - configuration error")
            
        frequency_penalty = api_penalties['frequency_penalty']
        presence_penalty = api_penalties['presence_penalty']
        
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
    
    def _extract_content(self, text: str, component_type: str) -> Any:
        """
        Extract component-specific content from generated text.
        
        Args:
            text: Generated text
            component_type: Component type
            
        Returns:
            Extracted content in appropriate format
        """
        # Delegate all extraction to domain adapter
        # This keeps the generator fully generic and reusable
        return self.adapter.extract_content(text, component_type)
    
    def _extract_caption_DEPRECATED(self, text: str) -> Dict[str, str]:
        """
        DEPRECATED: Moved to materials_adapter._extract_before_after()
        Extract caption from generated text.
        
        The prompt asks for BEFORE and AFTER descriptions. We need to parse
        the generated text to extract both parts.
        
        Expected formats:
        1. Single caption (treat as 'before', leave 'after' empty)
        2. Two sentences/paragraphs (first = before, second = after)
        3. Explicit markers like "Before:" or "After:"
        
        Returns:
            Dict with 'before' and 'after' keys
        """
        # Clean up the text
        cleaned = text.strip()
        
        # Remove any markdown or formatting markers
        cleaned = re.sub(r'\*\*(?:BEFORE_TEXT|AFTER_TEXT|Before|After):\*\*\s*', '', cleaned).strip()
        
        # Strategy 1: Look for explicit "Before:" and "After:" markers
        before_match = re.search(r'(?:^|\n)(?:Before|BEFORE):\s*(.+?)(?=\n(?:After|AFTER):|$)', cleaned, re.DOTALL | re.IGNORECASE)
        after_match = re.search(r'(?:^|\n)(?:After|AFTER):\s*(.+?)$', cleaned, re.DOTALL | re.IGNORECASE)
        
        if before_match and after_match:
            return {
                'before': before_match.group(1).strip(),
                'after': after_match.group(1).strip()
            }
        
        # Remove line-start markers that weren't caught by regex
        cleaned = re.sub(r'^(?:BEFORE|AFTER|Before|After):\s*', '', cleaned, flags=re.MULTILINE).strip()
        
        # Strategy 2: Split by double newline or period followed by newline (two paragraphs/sentences)
        # Look for natural breaks that might separate before/after
        
        # First try: Double newline (proper paragraph break)
        if '\n\n' in cleaned:
            parts = cleaned.split('\n\n', 1)
            before = parts[0].strip()
            after = parts[1].strip()
            
            # Ensure proper period endings
            if before and not before.endswith('.'):
                before += '.'
            if after and not after.endswith('.'):
                after += '.'
            
            return {
                'before': before,
                'after': after
            }
        
        # Second try: Look for explicit "After" keyword marking the transition
        # Common patterns: "After laser cleaning", "After the cleaning", "After cleaning"
        after_split = re.split(r'\.\s+(After (?:laser )?cleaning[^.]*,?\s+)', cleaned, maxsplit=1, flags=re.IGNORECASE)
        
        if len(after_split) == 3:
            # Found "After cleaning" marker
            before = after_split[0].strip()
            after = after_split[1].strip() + after_split[2].strip()
            
            # Ensure proper period endings
            if before and not before.endswith('.'):
                before += '.'
            if after and not after.endswith('.'):
                after += '.'
            
            return {
                'before': before,
                'after': after
            }
        
        # Third try: Split at sentence boundary if we have 2+ sentences
        parts = re.split(r'\.\s+(?=[A-Z])', cleaned, maxsplit=1)
        
        if len(parts) == 2:
            # Two distinct parts - likely before and after
            before = parts[0].strip()
            after = parts[1].strip()
            
            # Ensure 'before' ends with period
            if before and not before.endswith('.'):
                before += '.'
            
            # Ensure 'after' ends with period  
            if after and not after.endswith('.'):
                after += '.'
            
            return {
                'before': before,
                'after': after
            }
        
        # Strategy 3: Single caption - use as 'before', leave 'after' empty
        # This handles cases where only one caption is generated
        return {
            'before': cleaned if cleaned.endswith('.') else cleaned + '.',
            'after': ''
        }
    
    def _extract_faq_DEPRECATED(self, text: str) -> list:
        """DEPRECATED: Moved to materials_adapter._extract_json_list()"""
        import json
        
        faq_pattern = r'\{\s*"faq"\s*:\s*\[(.*?)\]\s*\}'
        matches = list(re.finditer(faq_pattern, text, re.DOTALL))
        
        if not matches:
            raise ValueError("Could not find FAQ JSON in response")
        
        json_str = matches[-1].group(0)
        data = json.loads(json_str)
        faq_list = data.get('faq', [])
        
        if not faq_list:
            raise ValueError("FAQ list is empty")
        
        return faq_list
