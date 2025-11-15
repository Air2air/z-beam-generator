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

from processing.enrichment.data_enricher import DataEnricher
from processing.generation.prompt_builder import PromptBuilder
from processing.detection.ensemble import AIDetectorEnsemble
from processing.validation.readability import ReadabilityValidator
from processing.voice.store import AuthorVoiceStore
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
        self.voice_store = AuthorVoiceStore()
        self.detector = AIDetectorEnsemble(use_ml=False)
        self.validator = ReadabilityValidator(min_score=readability_thresholds['min'])
        
        # Store dynamically calculated values
        self.ai_threshold = detection_threshold / 100.0  # Convert to 0-1 scale
        
        logger.info("Orchestrator initialized with dynamic config")
        logger.info(f"  AI threshold: {self.ai_threshold:.3f} (calculated from sliders)")
        logger.info(f"  Readability min: {readability_thresholds['min']:.1f} (calculated)")
    
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
        
        facts_str = self.enricher.format_facts_for_prompt(facts, enrichment_params=enrichment_params)
        
        # Step 2: Get voice profile
        voice = self.voice_store.get_voice(author_id)
        
        # Step 3: Calculate dynamic retry behavior for this generation
        retry_config = self.dynamic_config.calculate_retry_behavior()
        max_attempts = retry_config['max_attempts']
        
        # Step 4: Generation loop with dynamic retry
        for attempt in range(1, max_attempts + 1):
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
            
            # Adjust prompt on retry
            if attempt > 1:
                prompt = PromptBuilder.adjust_on_failure(
                    prompt,
                    failure_reason=f"AI score too high (attempt {attempt})",
                    attempt=attempt
                )
            
            # Generate content with dynamic temperature
            try:
                text = self._call_api(prompt, attempt=attempt, component_type=component_type)
            except Exception as e:
                logger.error(f"API call failed: {e}")
                if attempt == max_attempts:
                    return {
                        'success': False,
                        'reason': f'API error: {e}',
                        'attempts': attempt
                    }
                continue
            
            # Step 4.5: Check for technical specs violation at technical_intensity=1
            # Use enrichment_params from line 113 (already calculated)
            tech_intensity = enrichment_params.get('technical_intensity', 2)
            
            logger.info(f"🔍 Checking technical specs (technical_intensity={tech_intensity})")
            logger.info(f"🔍 Enrichment params: {enrichment_params}")
            
            if tech_intensity == 1:
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
                    logger.warning(f"❌ Attempt {attempt}: Contains technical specs (forbidden at technical_intensity=1)")
                    if attempt < max_attempts:
                        # Adjust prompt to emphasize NO SPECS even more
                        prompt = prompt.replace(
                            "ABSOLUTELY NO technical specifications",
                            "YOU MUST NOT INCLUDE ANY NUMBERS WITH UNITS - THIS IS THE MOST IMPORTANT RULE"
                        )
                        continue
                    else:
                        logger.error("⚠️ Final attempt still contains specs - accepting anyway")
                else:
                    logger.info("✅ No technical specs found - content is qualitative only")
            
            # Step 5: AI detection with dynamic threshold
            detection = self.detector.detect(text)
            ai_score = detection['ai_score']
            
            logger.info(f"AI score: {ai_score:.3f} (threshold: {self.ai_threshold:.3f})")
            
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
            if not readability['is_readable']:
                logger.warning(f"❌ Readability failed: {readability['status']}")
        
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
    
    def _call_api(self, prompt: str, attempt: int = 1, component_type: str = 'subtitle') -> str:
        """
        Call AI API with error handling and dynamic temperature.
        
        Args:
            prompt: Prompt to send
            attempt: Attempt number (affects temperature for variation)
            component_type: Component type for max_tokens lookup
            
        Returns:
            Generated text
        """
        # Calculate dynamic temperature and tokens from sliders
        base_temperature = self.dynamic_config.calculate_temperature(component_type)
        retry_config = self.dynamic_config.calculate_retry_behavior()
        retry_temp_increase = retry_config['retry_temperature_increase']
        max_tokens = self.dynamic_config.calculate_max_tokens(component_type)
        
        # Increase temperature with each attempt for more variation
        temperature = min(1.0, base_temperature + (attempt - 1) * retry_temp_increase)
        
        logger.info(f"🌡️  Temperature: {temperature:.2f} (base: {base_temperature:.2f}, +{retry_temp_increase:.2f}/attempt)")
        logger.info(f"🎯  Max tokens: {max_tokens} (calculated from sliders)")
        
        # Build system prompt with technical language override if needed
        system_prompt = "You are a professional technical writer creating concise, clear content."
        
        # Get enrichment params to check technical_intensity
        enrichment_params = self.dynamic_config.calculate_enrichment_params()
        tech_intensity = enrichment_params.get('technical_intensity', 2)
        
        if tech_intensity == 1:
            # Level 1: Add CRITICAL override to system prompt (highest authority)
            system_prompt = (
                "You are a professional technical writer creating concise, clear content. "
                "CRITICAL RULE: Write ONLY in qualitative, conceptual terms. "
                "ABSOLUTELY FORBIDDEN: Any numbers, measurements, units, or technical specifications (NO '110 GPa', NO '1941 K', NO '400 MPa', NO '41,000,000 S/m'). "
                "Use ONLY descriptive words: 'strong', 'heat-resistant', 'conductive', 'durable'."
            )
        
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
