"""
Content Generation Orchestrator

Main workflow coordinator for AI-resistant content generation.

Flow:
1. Enrich material data with real facts
2. Build unified prompt (voice + facts + anti-AI)
3. Generate content via API
4. Validate with ensemble detection
5. Check readability
6. Retry with adjusted prompt on failure
7. Output to frontmatter
"""

import logging
from typing import Dict

from processing.enrichment.data_enricher import DataEnricher
from processing.generation.prompt_builder import PromptBuilder
from processing.detection.ensemble import AIDetectorEnsemble
from processing.validation.readability import ReadabilityValidator
from processing.voice.store import AuthorVoiceStore

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main workflow orchestrator for content generation.
    
    Coordinates all processing steps with retry logic and
    dynamic prompt adjustment.
    """
    
    def __init__(
        self,
        api_client,
        max_attempts: int = 5,
        ai_threshold: float = 0.3,
        readability_min: float = 60.0,
        use_ml_detection: bool = False
    ):
        """
        Initialize orchestrator.
        
        Args:
            api_client: AI API client (e.g., GrokClient)
            max_attempts: Maximum retry attempts
            ai_threshold: AI score threshold (reject if above)
            readability_min: Minimum readability score
            use_ml_detection: Whether to use ML-based detection
        """
        self.api_client = api_client
        self.max_attempts = max_attempts
        self.ai_threshold = ai_threshold
        self.readability_min = readability_min
        
        # Initialize components
        self.enricher = DataEnricher()
        self.voice_store = AuthorVoiceStore()
        self.detector = AIDetectorEnsemble(use_ml=use_ml_detection)
        self.validator = ReadabilityValidator(min_score=readability_min)
        
        logger.info("Orchestrator initialized")
    
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
        
        # Step 1: Enrich with real facts
        facts = self.enricher.fetch_real_facts(topic)
        facts_str = self.enricher.format_facts_for_prompt(facts)
        
        # Step 2: Get voice profile
        voice = self.voice_store.get_voice(author_id)
        
        # Step 3: Generation loop with retry
        for attempt in range(1, self.max_attempts + 1):
            logger.info(f"Attempt {attempt}/{self.max_attempts} for {topic} {component_type}")
            
            # Generate variation seed using timestamp to defeat caching
            import time
            variation_seed = int(time.time() * 1000) + attempt
            
            # Build prompt
            prompt = PromptBuilder.build_unified_prompt(
                topic=topic,
                voice=voice,
                length=length,
                facts=facts_str,
                context=context,
                component_type=component_type,
                domain=domain,
                variation_seed=variation_seed
            )
            
            # Adjust prompt on retry
            if attempt > 1:
                prompt = PromptBuilder.adjust_on_failure(
                    prompt,
                    failure_reason=f"AI score too high (attempt {attempt})",
                    attempt=attempt
                )
            
            # Generate content with increasing temperature for variation
            try:
                text = self._call_api(prompt, attempt=attempt)
            except Exception as e:
                logger.error(f"API call failed: {e}")
                if attempt == self.max_attempts:
                    return {
                        'success': False,
                        'reason': f'API error: {e}',
                        'attempts': attempt
                    }
                continue
            
            # Step 4: AI detection
            detection = self.detector.detect(text)
            ai_score = detection['ai_score']
            
            logger.info(f"AI score: {ai_score:.3f} (threshold: {self.ai_threshold})")
            
            # Step 5: Readability check
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
        logger.error(f"Failed after {self.max_attempts} attempts")
        return {
            'success': False,
            'reason': f'Max attempts reached. Last AI score: {ai_score:.3f}',
            'attempts': self.max_attempts,
            'last_text': text,
            'last_ai_score': ai_score,
            'last_readability': readability
        }
    
    def _call_api(self, prompt: str, attempt: int = 1) -> str:
        """
        Call AI API with error handling and dynamic temperature.
        
        Args:
            prompt: Prompt to send
            attempt: Attempt number (affects temperature for variation)
            
        Returns:
            Generated text
        """
        # Increase temperature with each attempt for more variation
        # Attempt 1: 0.8 (higher than before for more creativity)
        # Attempt 2: 0.9 (more variation)
        # Attempt 3+: 1.0 (maximum variation)
        base_temperature = 0.8
        temperature = min(1.0, base_temperature + (attempt - 1) * 0.1)
        
        logger.info(f"🌡️  Temperature: {temperature:.1f} (attempt {attempt})")
        
        # Use the standard API client interface: generate_simple()
        # which requires max_tokens and temperature
        response = self.api_client.generate_simple(
            prompt=prompt,
            system_prompt="You are a professional technical writer creating concise, clear content.",
            max_tokens=200,  # Subtitles are short
            temperature=temperature  # Dynamic temperature for variation
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
