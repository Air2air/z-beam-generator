"""
Content Generation Orchestrator

Main workflow coordinator for AI-resistant content generation.

Flow:
1. Enrich material data with real facts
2. Build unified prompt (voice + facts + anti-AI)
3. Generate content via API (with dynamic settings from config sliders)
4. Validate with ensemble detection (dynamic thresholds)
5. Check readability (dynamic thresholds)
6. Retry with adjusted prompt on failure
7. Output to frontmatter

All technical parameters calculated dynamically from 10 user-facing sliders.
"""

import logging
from typing import Dict
import yaml
from pathlib import Path

from processing.enrichment.data_enricher import DataEnricher
from processing.generation.prompt_builder import PromptBuilder
from processing.detection.ensemble import AIDetectorEnsemble
from processing.validation.readability import ReadabilityValidator
from processing.config.dynamic_config import DynamicConfig

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main workflow orchestrator for content generation.
    
    Uses DynamicConfig to calculate all parameters from user-facing sliders.
    NO hardcoded technical values - everything adapts to slider changes.
    """
    
    def __init__(
        self,
        api_client,
        dynamic_config: DynamicConfig = None
    ):
        """
        Initialize orchestrator with dynamic configuration.
        
        Args:
            api_client: AI API client (e.g., GrokClient)
            dynamic_config: Optional DynamicConfig instance (creates new if None)
        """
        self.api_client = api_client
        self.dynamic_config = dynamic_config if dynamic_config else DynamicConfig()
        
        # Calculate parameters dynamically from sliders
        readability_thresholds = self.dynamic_config.calculate_readability_thresholds()
        detection_threshold = self.dynamic_config.calculate_detection_threshold()
        
        # Initialize components with dynamic parameters
        self.enricher = DataEnricher()
        self.personas = self._load_all_personas()
        
        # Initialize Winston client for AI detection
        winston_client = None
        try:
            from shared.api.client_factory import create_api_client
            winston_client = create_api_client('winston')
            logger.info("Winston API client initialized for AI detection")
        except Exception as e:
            logger.warning(f"Winston API client not available: {e} - using pattern-based detection only")
        
        # Initialize detector with Winston client
        self.detector = AIDetectorEnsemble(use_ml=False, winston_client=winston_client)
        self.validator = ReadabilityValidator(min_score=readability_thresholds['min'])
        
        # Store dynamically calculated values
        self.ai_threshold = detection_threshold / 100.0  # Convert to 0-1 scale
        
        # Initialize Winston feedback database if configured
        self.feedback_db = None
        self.prompt_optimizer = None  # Will be initialized if feedback_db available
        try:
            from processing.config.config_loader import get_config
            config = get_config()
            db_path = config.config.get('winston_feedback_db_path')
            if db_path:
                from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
                self.feedback_db = WinstonFeedbackDatabase(db_path)
                logger.info(f"Winston feedback database initialized at {db_path}")
                
                # Initialize PromptOptimizer for self-learning prompt enhancement
                from processing.learning.prompt_optimizer import PromptOptimizer
                self.prompt_optimizer = PromptOptimizer(db_path)
                logger.info("🧠 PromptOptimizer enabled - dynamic prompt learning active")
        except Exception as e:
            logger.warning(f"Winston feedback database unavailable: {e}")
        
        logger.info("Orchestrator initialized with dynamic config")
        logger.info(f"  AI threshold: {self.ai_threshold:.3f} (calculated from sliders)")
        logger.info(f"  Readability min: {readability_thresholds['min']:.1f} (calculated)")
    
    def _load_all_personas(self) -> Dict[int, Dict]:
        """
        Load all persona YAML files from prompts/personas/ directory.
        Maps author IDs to persona configurations.
        
        Returns:
            Dict mapping author_id to persona configuration
        """
        import yaml
        from pathlib import Path
        
        personas_dir = Path("prompts/personas")
        if not personas_dir.exists():
            raise ValueError(f"Personas directory not found: {personas_dir}")
        
        # Map persona files to author IDs
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
                logger.warning(f"Persona file not found: {yaml_path}, skipping author_id {author_id}")
                continue
            
            try:
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    persona_config = yaml.safe_load(f)
                    personas[author_id] = persona_config
                    logger.debug(f"Loaded persona for author_id {author_id}: {persona_config.get('name', 'Unknown')}")
            except Exception as e:
                logger.error(f"Failed to load persona from {yaml_path}: {e}")
        
        if not personas:
            raise ValueError("No personas loaded from prompts/personas/ directory")
        
        logger.info(f"Loaded {len(personas)} personas from prompts/personas/")
        return personas
    
    def _load_prompt_template(self, template_name: str) -> str:
        """
        Load prompt template from /prompts/system/{template_name}
        
        Args:
            template_name: Name of template file (e.g., 'base.txt', 'low_technical.txt')
            
        Returns:
            Prompt template string
            
        Raises:
            ValueError: If template file doesn't exist
        """
        from pathlib import Path
        template_path = Path("prompts/system") / template_name
        if not template_path.exists():
            raise ValueError(f"System prompt template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read().strip()
        
        logger.debug(f"Loaded system prompt template: {template_path}")
        return template
    
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
    
    def generate(
        self,
        topic: str,  # Renamed from 'material' for generality (backward compatible via kwargs)
        component_type: str,
        author_id: int,
        length: int = None,
        context: str = "",
        domain: str = "materials",
        **kwargs  # Backward compatibility: accepts 'material' as alias for 'topic'
    ) -> Dict:
        """
        Generate AI-resistant content.
        
        Args:
            topic: Subject matter (material name, historical event, etc.)
            component_type: Content type (subtitle, caption, description, etc.)
            author_id: Author ID (1-4)
            length: Target word count (uses component default if None)
            context: Additional context
            domain: Content domain (materials, history, recipes, etc.)
            **kwargs: Backward compatibility (accepts 'material' as alias for 'topic')
            
        Returns:
            Dict with:
            - success: bool
            - text: Generated text (if successful)
            - attempts: Number of attempts taken
            - ai_score: Final AI detection score
            - readability: Readability metrics
            - reason: Failure reason (if failed)
        """
        # Backward compatibility: accept 'material' as alias for 'topic'
        if 'material' in kwargs:
            topic = kwargs['material']
        
        # Randomize length within component's range for dramatic variation
        if length is None:
            from processing.generation.component_specs import ComponentRegistry
            import random
            spec = ComponentRegistry.get_spec(component_type)
            # Pick random length within the full range (e.g., 12-48 for subtitles with ±60%)
            length = random.randint(spec.min_length, spec.max_length)
            logger.info(f"🎲 Randomized length: {length} words (range: {spec.min_length}-{spec.max_length})")
        
        # Step 1: Enrich with real facts
        facts = self.enricher.fetch_real_facts(topic)
        
        # Phase 2: Get all parameters from dynamic config (includes voice_params)
        all_params = self.dynamic_config.get_all_generation_params(component_type)
        voice_params = all_params['voice_params']
        enrichment_params = all_params['enrichment_params']  # Phase 3A
        
        logger.info(f"📋 Retrieved enrichment_params: {enrichment_params}")
        
        facts_str = self.enricher.format_facts_for_prompt(facts, enrichment_params=enrichment_params, voice_params=voice_params)
        
        # Step 2: Get voice profile
        # Load persona for author
        voice = self._get_persona_by_author_id(author_id)
        
        # Step 3: Determine max attempts based on Winston mode
        # Adaptive retry can extend this dynamically based on feedback
        max_attempts = self._get_max_attempts_for_mode()
        absolute_max = 3  # Safety limit for adaptive retry
        
        # Track Winston feedback for adaptive decisions
        last_winston_result = None
        
        # Step 4: Generation loop with adaptive retry
        attempt = 1
        while attempt <= max_attempts and attempt <= absolute_max:
            logger.info(f"Attempt {attempt}/{max_attempts} for {topic} {component_type}")
            
            # Generate variation seed using timestamp to defeat caching
            import time
            variation_seed = int(time.time() * 1000) + attempt
            
            # Build prompt with voice parameters (Phase 2: personality control)
            prompt = PromptBuilder.build_unified_prompt(
                topic=topic,
                voice=voice,
                length=length,
                facts=facts_str,
                context=context,
                component_type=component_type,
                domain=domain,
                voice_params=voice_params,  # NEW: Pass voice parameters
                enrichment_params=enrichment_params,  # Phase 3+: Pass technical intensity
                variation_seed=variation_seed
            )
            
            # SELF-LEARNING: Optimize prompt with learned patterns from Winston feedback
            if self.prompt_optimizer and attempt == 1:
                # Only optimize on first attempt (retry uses adjust_on_failure)
                optimization_result = self.prompt_optimizer.optimize_prompt(
                    base_prompt=prompt,
                    material=topic,
                    component_type=component_type,
                    include_patterns=True,
                    include_recommendations=True
                )
                
                if optimization_result['confidence'] != 'none':
                    prompt = optimization_result['optimized_prompt']
                    logger.info(f"🧠 Prompt optimized with learned patterns:")
                    logger.info(f"   Confidence: {optimization_result['confidence']}")
                    logger.info(f"   Patterns analyzed: {optimization_result.get('patterns_analyzed', 0)}")
                    logger.info(f"   Expected improvement: {optimization_result['expected_improvement']*100:.1f}%")
                    for addition in optimization_result['additions']:
                        logger.info(f"   + {addition}")
                else:
                    logger.info(f"🧠 Prompt optimizer: {optimization_result.get('reason', 'Insufficient data')}")
            
            # Adjust prompt on retry
            if attempt > 1:
                prompt = PromptBuilder.adjust_on_failure(
                    prompt,
                    failure_reason=f"AI score too high (attempt {attempt})",
                    attempt=attempt
                )
            
            # Generate content with adaptive temperature
            try:
                # Use adaptive temperature if we have Winston feedback
                base_temp = self.dynamic_config.calculate_temperature(component_type)
                if attempt > 1 and last_winston_result:
                    temperature = self._calculate_adaptive_temperature(
                        base_temp, attempt, last_winston_result
                    )
                    # Override the temperature in _call_api by passing it explicitly
                    # For now, let _call_api handle it with feedback awareness
                
                text = self._call_api(
                    prompt, 
                    attempt=attempt, 
                    component_type=component_type,
                    winston_feedback=last_winston_result
                )
            except Exception as e:
                logger.error(f"API call failed: {e}")
                if attempt >= absolute_max:
                    return {
                        'success': False,
                        'reason': f'API error: {e}',
                        'attempts': attempt
                    }
                attempt += 1
                continue
            
            # Step 4.5: Check for technical specs violation at very low technical_intensity
            # Use enrichment_params from line 113 (already calculated)
            tech_intensity = enrichment_params.get('technical_intensity', 0.22)  # 0.0-1.0 normalized
            
            logger.info(f"🔍 Checking technical specs (technical_intensity={tech_intensity:.3f})")
            logger.info(f"🔍 Enrichment params: {enrichment_params}")
            
            if tech_intensity < 0.15:  # Very low (slider 1-2)
                # Detect numbers with units (technical specs)
                import re
                spec_patterns = [
                    r'\d+\.?\d*\s*(?:GPa|MPa|kPa|Pa|K|°C|°F|g/cm³|kg/m³|W/\(m·K\)|S/m|MS/m|nm|μm|mm|cm|m|Hz|kHz|MHz|GHz|J|kJ|MJ|W|kW|MW|V|A|Ω|%)',
                    r'\d+\.?\d*\s*(?:GPa|MPa|K|g/cm³|W|Hz|nm|V)',  # Common ones
                ]
                
                has_specs = any(re.search(pattern, text, re.IGNORECASE) for pattern in spec_patterns)
                
                logger.info(f"🔍 Text: {text[:100]}...")
                logger.info(f"🔍 Has specs: {has_specs}")
                
                if has_specs:
                    logger.warning(f"❌ Attempt {attempt}: Contains technical specs (forbidden at technical_intensity < 0.15)")
                    if attempt < absolute_max:
                        # Retry with same prompt - low_technical.txt template already emphasizes no specs
                        attempt += 1
                        continue
                    else:
                        logger.error("⚠️ Final attempt still contains specs - accepting anyway")
                else:
                    logger.info("✅ No technical specs found - content is qualitative only")
            
            # Step 5: AI detection with smart Winston usage
            # Smart mode: Use patterns for early attempts, Winston for later/final
            use_winston = self._should_use_winston(attempt, max_attempts)
            
            if use_winston:
                detection = self.detector.detect(text)
                # Store Winston result for adaptive decisions
                if 'sentences' in detection:
                    last_winston_result = detection
                    
                    # Log Winston result to database for learning
                    if self.feedback_db:
                        try:
                            from processing.detection.winston_analyzer import WinstonFeedbackAnalyzer
                            analyzer = WinstonFeedbackAnalyzer()
                            failure_analysis = analyzer.analyze_failure(detection)
                            
                            detection_id = self.feedback_db.log_detection(
                                material=topic,
                                component_type=component_type,
                                generated_text=text,
                                winston_result=detection,
                                temperature=self.dynamic_config.calculate_temperature(component_type),
                                attempt=attempt,
                                success=(detection['ai_score'] <= self.ai_threshold),
                                failure_analysis=failure_analysis
                            )
                            logger.info(f"📊 Logged Winston result to database (ID: {detection_id})")
                        except Exception as e:
                            logger.warning(f"Failed to log Winston result: {e}")
            else:
                # Pattern-based only for cost savings
                logger.info(f"💰 [COST CONTROL] Using pattern-based detection (attempt {attempt}/{max_attempts})")
                from processing.detection.ai_detection import AIDetector
                pattern_detector = AIDetector(strict_mode=False)
                pattern_result = pattern_detector.detect(text)
                detection = {
                    'ai_score': pattern_result['ai_score'],
                    'method': 'pattern_only',
                    'details': pattern_result['details']
                }
            
            ai_score = detection['ai_score']
            
            logger.info(f"AI score: {ai_score:.3f} (threshold: {self.ai_threshold:.3f}) [method: {detection.get('method', 'unknown')}]")
            
            # Step 6: Readability check with dynamic threshold
            readability = self.validator.validate(text)
            
            logger.info(f"Readability: {readability['status']} (Flesch: {readability.get('flesch_score', 'N/A')})")
            
            # Check if acceptable
            if ai_score <= self.ai_threshold and readability['is_readable']:
                logger.info(f"✅ Success on attempt {attempt}")
                return {
                    'success': True,
                    'text': text,
                    'attempts': attempt,
                    'ai_score': ai_score,
                    'readability': readability,
                    'detection': detection
                }
            
            # Log failure reason
            if ai_score > self.ai_threshold:
                logger.warning(f"❌ AI score too high: {ai_score:.3f} > {self.ai_threshold}")
                
                # Check if we should extend attempts based on Winston feedback
                # Do this BEFORE checking if we're at max_attempts
                if last_winston_result and attempt >= max_attempts and attempt < absolute_max:
                    if self._should_extend_attempts_adaptive(attempt, last_winston_result):
                        max_attempts += 1
                        logger.info(f"📈 [ADAPTIVE] Extended max_attempts to {max_attempts} (attempt {attempt}/{absolute_max})")
                        
            if not readability['is_readable']:
                logger.warning(f"❌ Readability failed: {readability['status']}")
            
            attempt += 1
        
        # Max attempts reached
        logger.error(f"Failed after {max_attempts} attempts")
        return {
            'success': False,
            'reason': f'Max attempts reached. Last AI score: {ai_score:.3f}',
            'attempts': max_attempts,
            'last_text': text,
            'last_ai_score': ai_score,
            'last_readability': readability
        }
    
    def _should_use_winston(self, attempt: int, max_attempts: int) -> bool:
        """
        Determine if Winston API should be used for this attempt.
        
        Args:
            attempt: Current attempt number (1-based)
            max_attempts: Maximum attempts allowed
            
        Returns:
            True if Winston should be used, False for pattern-only
        """
        # Get Winston usage mode from config
        try:
            from processing.config.config_loader import get_config
            config = get_config()
            mode = config.config.get('winston_usage_mode', 'smart')
        except Exception:
            mode = 'smart'  # Default to smart mode
        
        if mode == 'disabled':
            return False
        elif mode == 'always':
            return True
        elif mode == 'final_only':
            return attempt == max_attempts
        elif mode == 'smart':
            # Smart: pattern-based for attempts 1-2, Winston for 3+ and final
            return attempt >= 3 or attempt == max_attempts
        else:
            logger.warning(f"Unknown winston_usage_mode '{mode}', defaulting to smart")
            return attempt >= 3 or attempt == max_attempts
    
    def _get_max_attempts_for_mode(self) -> int:
        """Get max attempts based on Winston usage mode."""
        try:
            from processing.config.config_loader import get_config
            config = get_config()
            mode = config.config.get('winston_usage_mode', 'smart')
            
            # In 'always' mode, start with 1 attempt (can extend based on feedback)
            if mode == 'always':
                return 1
            
            # Default for other modes
            return 3
        except Exception:
            return 3
    
    def _should_extend_attempts_adaptive(self, attempt: int, winston_result: Dict) -> bool:
        """Check if attempts should be extended based on Winston feedback."""
        try:
            from processing.config.config_loader import get_config
            from processing.detection.winston_analyzer import WinstonFeedbackAnalyzer
            
            config = get_config()
            
            # Check if adaptive retry is enabled
            if not config.config.get('winston_adaptive_retry', True):
                return False
            
            # Only in 'always' mode
            mode = config.config.get('winston_usage_mode', 'smart')
            if mode != 'always':
                return False
            
            # Get configuration
            max_extensions = config.config.get('winston_max_extensions', 2)
            absolute_max = 3  # Safety limit
            
            # Use analyzer to decide
            analyzer = WinstonFeedbackAnalyzer()
            should_extend = analyzer.should_extend_attempts(
                current_attempt=attempt,
                winston_result=winston_result,
                max_extensions=max_extensions,
                absolute_max=absolute_max
            )
            
            if should_extend:
                analysis = analyzer.analyze_failure(winston_result)
                logger.info(f"🔄 [ADAPTIVE RETRY] Extending attempts based on feedback")
                logger.info(f"   Type: {analysis['failure_type']}")
                logger.info(f"   Guidance: {analysis['guidance']}")
            
            return should_extend
            
        except Exception as e:
            logger.warning(f"[ADAPTIVE RETRY] Failed to analyze: {e}")
            return False
    
    def _calculate_adaptive_temperature(
        self, 
        base_temp: float, 
        attempt: int, 
        winston_feedback: Dict = None
    ) -> float:
        """Calculate temperature with Winston feedback adaptation."""
        try:
            from processing.detection.winston_analyzer import WinstonFeedbackAnalyzer
            
            # No feedback? Use normal progression
            if not winston_feedback:
                retry_config = self.dynamic_config.calculate_retry_behavior()
                retry_temp_increase = retry_config['retry_temperature_increase']
                return min(1.0, base_temp + (attempt - 1) * retry_temp_increase)
            
            # Analyze feedback
            analyzer = WinstonFeedbackAnalyzer()
            analysis = analyzer.analyze_failure(winston_feedback)
            failure_type = analysis['failure_type']
            
            if failure_type == 'uniform':
                # All sentences bad: INCREASE temperature significantly
                # Need more creative variation
                temp = base_temp + 0.15
                logger.info(f"🌡️  [ADAPTIVE] Uniform failure → High temp ({temp:.2f}) for variation")
                return min(1.0, temp)
                
            elif failure_type == 'borderline':
                # Close to passing: DECREASE temperature slightly
                # Need more control/consistency
                temp = base_temp - 0.05
                logger.info(f"🌡️  [ADAPTIVE] Borderline → Lower temp ({temp:.2f}) for control")
                return max(0.5, temp)
                
            else:  # partial or other
                # Mixed results: Normal progression
                retry_config = self.dynamic_config.calculate_retry_behavior()
                retry_temp_increase = retry_config['retry_temperature_increase']
                temp = base_temp + (attempt - 1) * retry_temp_increase
                logger.info(f"🌡️  [ADAPTIVE] {failure_type} → Normal progression ({temp:.2f})")
                return min(1.0, temp)
                
        except Exception as e:
            logger.warning(f"[ADAPTIVE] Temperature calculation failed: {e}")
            # Fallback to normal progression
            retry_config = self.dynamic_config.calculate_retry_behavior()
            retry_temp_increase = retry_config['retry_temperature_increase']
            return min(1.0, base_temp + (attempt - 1) * retry_temp_increase)
    
    def _call_api(
        self, 
        prompt: str, 
        attempt: int = 1, 
        component_type: str = 'subtitle',
        winston_feedback: Dict = None
    ) -> str:
        """
        Call AI API with error handling and dynamic temperature.
        
        Args:
            prompt: Prompt to send
            attempt: Attempt number (affects temperature for variation)
            component_type: Component type for max_tokens lookup
            winston_feedback: Optional Winston feedback for adaptive temperature
            
        Returns:
            Generated text
        """
        # Calculate dynamic temperature from sliders OR adaptive from Winston feedback
        base_temperature = self.dynamic_config.calculate_temperature(component_type)
        max_tokens = self.dynamic_config.calculate_max_tokens(component_type)
        
        # Use adaptive temperature if we have Winston feedback
        if winston_feedback:
            temperature = self._calculate_adaptive_temperature(base_temperature, attempt, winston_feedback)
        else:
            # Normal temperature progression
            retry_config = self.dynamic_config.calculate_retry_behavior()
            retry_temp_increase = retry_config['retry_temperature_increase']
            temperature = min(1.0, base_temperature + (attempt - 1) * retry_temp_increase)
            logger.info(f"🌡️  Temperature: {temperature:.2f} (base: {base_temperature:.2f}, +{retry_temp_increase:.2f}/attempt)")
        logger.info(f"🎯  Max tokens: {max_tokens} (calculated from sliders)")
        
        # Load system prompt from template based on technical_intensity
        enrichment_params = self.dynamic_config.calculate_enrichment_params()
        tech_intensity = enrichment_params.get('technical_intensity', 0.22)  # 0.0-1.0 normalized
        
        if tech_intensity < 0.15:  # Very low (slider 1-2)
            # Use low_technical template with CRITICAL override
            system_prompt = self._load_prompt_template('low_technical.txt')
        else:
            # Use standard base template
            system_prompt = self._load_prompt_template('base.txt')
        
        # Use the standard API client interface: generate_simple()
        response = self.api_client.generate_simple(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Handle APIResponse object
        if not response.success:
            raise RuntimeError(f"API call failed: {response.error}")
        
        return response.content.strip()
    
    def batch_generate(
        self,
        materials: list,
        component_type: str,
        author_id: int,
        length: int
    ) -> Dict[str, Dict]:
        """
        Generate content for multiple materials.
        
        Args:
            materials: List of material names
            component_type: Content type
            author_id: Author ID
            length: Target word count
            
        Returns:
            Dict mapping material name to result
        """
        results = {}
        
        for material in materials:
            logger.info(f"\n{'='*60}")
            logger.info(f"Generating {component_type} for {material}")
            logger.info(f"{'='*60}")
            
            result = self.generate(
                material=material,
                component_type=component_type,
                author_id=author_id,
                length=length
            )
            
            results[material] = result
        
        # Summary
        successful = sum(1 for r in results.values() if r['success'])
        logger.info(f"\n✅ Success: {successful}/{len(materials)}")
        
        return results
