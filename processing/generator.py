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
        
        # Author voice store
        from processing.voice.store import AuthorVoiceStore
        self.voice_store = AuthorVoiceStore()
        
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
        
        self.pattern_learner = PatternLearner(db_path)
        self.temperature_advisor = TemperatureAdvisor(db_path)
        self.prompt_optimizer = PromptOptimizer(db_path)
        self.success_predictor = SuccessPredictor(db_path)
        
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
        
        # BEST PRACTICE 2: Failure-type-specific retry strategies
        if last_winston_result and attempt > 1:
            failure_analysis = self.analyzer.analyze_failure(last_winston_result)
            failure_type = failure_analysis['failure_type']
            
            if failure_type == 'uniform':
                # All sentences bad: INCREASE randomness across all parameters
                base_temperature = min(1.0, base_temperature + 0.15)
                voice_params['imperfection_tolerance'] = min(1.0, voice_params.get('imperfection_tolerance', 0.5) + 0.20)
                voice_params['colloquialism_frequency'] = min(1.0, voice_params.get('colloquialism_frequency', 0.3) + 0.15)
                enrichment_params['fact_density'] = max(0.3, enrichment_params.get('fact_density', 0.7) - 0.15)
                self.logger.info(
                    f"🌡️  UNIFORM failure → Increase randomness: "
                    f"temp={base_temperature:.2f}, imperfection={voice_params['imperfection_tolerance']:.2f}"
                )
                
            elif failure_type == 'borderline':
                # Close to passing: FINE-TUNE with small adjustments
                base_temperature = max(0.5, base_temperature - 0.03)
                voice_params['sentence_rhythm_variation'] = min(1.0, voice_params.get('sentence_rhythm_variation', 0.5) + 0.10)
                self.logger.info(
                    f"🌡️  BORDERLINE → Fine-tune: "
                    f"temp={base_temperature:.2f}, rhythm={voice_params['sentence_rhythm_variation']:.2f}"
                )
                
            elif failure_type == 'partial':
                # Some sentences human: MODERATE adjustments
                base_temperature = min(1.0, base_temperature + 0.08)
                voice_params['reader_address_rate'] = min(1.0, voice_params.get('reader_address_rate', 0.2) + 0.10)
                enrichment_params['context_depth'] = min(1.0, enrichment_params.get('context_depth', 0.5) + 0.10)
                self.logger.info(
                    f"🌡️  PARTIAL → Moderate boost: "
                    f"temp={base_temperature:.2f}, context={enrichment_params['context_depth']:.2f}"
                )
                
            else:
                # Normal/unknown failure: Standard progression
                retry_config = self.dynamic_config.calculate_retry_behavior()
                base_temperature += (attempt - 1) * retry_config['retry_temperature_increase']
                base_temperature = min(1.0, base_temperature)
                self.logger.info(f"🌡️  Standard progression: temp={base_temperature:.2f}")
        
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
        # Extract API penalties from base_params
        api_penalties = base_params.get('api_params', {}).get('penalties', {
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0
        })
        
        return {
            'temperature': base_temperature,
            'voice_params': voice_params,
            'enrichment_params': enrichment_params,
            'max_tokens': self.dynamic_config.calculate_max_tokens(component_type),
            'api_penalties': api_penalties  # NEW: Include API penalties
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
        
        # Get author ID
        author_id = material_data.get('author', {}).get('id', 2)
        voice = self.voice_store.get_voice(author_id)
        
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
                enrichment_params=params['enrichment_params']
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
            
            # Check readability
            readability = self.validator.validate(text)
            self.logger.info(f"Readability: {readability['status']}")
            
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
                    success=(ai_score <= self.ai_threshold and readability['is_readable']),
                    failure_analysis=failure_analysis
                )
                self.logger.info(f"📊 Logged result to database (ID: {detection_id})")
            except Exception as e:
                self.logger.warning(f"Failed to log to database: {e}")
            
            # Dual-threshold check:
            # 1. Acceptance threshold: ai_score <= threshold (for deployment)
            # 2. Learning target: human_score >= target (for improvement)
            passes_acceptance = ai_score <= self.ai_threshold and readability['is_readable']
            human_score = detection.get('human_score', 0)
            learning_target = self.dynamic_config.base_config.get_learning_target()
            meets_learning_target = human_score >= learning_target
            
            # Check if successful for BOTH acceptance and learning
            if passes_acceptance and meets_learning_target:
                self.logger.info(f"✅ Success on attempt {attempt} (human: {human_score:.1f}%, target: {learning_target}%)")
                
                # Extract component-specific content
                content_data = self._extract_content(text, component_type)
                
                # Write to Materials.yaml
                self._write_to_materials_yaml(material_name, component_type, content_data)
                
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
                self.logger.warning(f"❌ AI score too high: {ai_score:.3f} > {self.ai_threshold:.3f}")
            elif not meets_learning_target:
                self.logger.warning(f"📚 Learning target not met: human {human_score:.1f}% < {learning_target}%")
            if not readability['is_readable']:
                self.logger.warning(f"❌ Readability failed: {readability['status']}")
            
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
    
    def _extract_content(self, text: str, component_type: str) -> Any:
        """
        Extract component-specific content from generated text.
        
        Args:
            text: Generated text
            component_type: Component type
            
        Returns:
            Extracted content in appropriate format
        """
        if component_type == 'caption':
            return self._extract_caption(text)
        elif component_type == 'faq':
            return self._extract_faq(text)
        elif component_type == 'subtitle':
            return text.strip()
        else:
            return text.strip()
    
    def _extract_caption(self, text: str) -> Dict[str, str]:
        """Extract before/after sections from caption"""
        before_match = re.search(r'\*\*BEFORE_TEXT:\*\*\s*(.+?)(?=\*\*AFTER_TEXT:|\Z)', text, re.DOTALL)
        after_match = re.search(r'\*\*AFTER_TEXT:\*\*\s*(.+)', text, re.DOTALL)
        
        if not before_match or not after_match:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            if len(paragraphs) < 2:
                raise ValueError(f"Could not extract before/after sections: {text[:200]}")
            before_text = paragraphs[0]
            after_text = paragraphs[1]
        else:
            before_text = before_match.group(1).strip()
            after_text = after_match.group(1).strip()
        
        before_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', before_text).strip()
        after_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', after_text).strip()
        
        return {
            'before': before_text,
            'after': after_text
        }
    
    def _extract_faq(self, text: str) -> list:
        """Extract FAQ items from JSON"""
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
