"""
Application services implementing business use cases.
"""

from datetime import datetime

from domain.entities import Content
from domain.value_objects import ContentSpecs, GenerationSettings, ThresholdSettings, DetectionResult
from domain.simple_repositories import ISimplePromptRepository, ISimpleContentService, ISimpleDetectionService
from core.interfaces.services import IAPIClient
from infrastructure.configuration import ConfigProvider


class ContentService(ISimpleContentService):
    """Application service for content generation."""
    
    def __init__(
        self,
        api_client: IAPIClient,
        prompt_repository: ISimplePromptRepository,
        config_provider: ConfigProvider
    ):
        self._api_client = api_client
        self._prompt_repository = prompt_repository
        self._config = config_provider
    
    async def generate_content(
        self,
        material: str,
        category: str,
        specs: ContentSpecs,
        settings: GenerationSettings
    ) -> Content:
        """Generate content using AI API."""
        # Get content generation prompt
        prompt = await self._prompt_repository.get_content_prompt(
            material=material,
            category=category,
            specs=specs
        )
        
        # Call AI API for content generation
        response = await self._call_api_with_settings(
            prompt=prompt,
            settings=settings,
            operation_type="content_generation"
        )
        
        # Create content entity
        content = Content(
            id=self._generate_content_id(),
            body=response,
            material=material,
            category=category,
            created_at=datetime.utcnow(),
            specs=specs
        )
        
        return content
    
    async def improve_content(
        self,
        content: Content,
        improvement_prompt: str,
        temperature: float
    ) -> Content:
        """Improve existing content."""
        # Combine content with improvement instructions
        full_prompt = f"{improvement_prompt}\n\nOriginal Content:\n{content.body}"
        
        # Generate improved content
        response = self._api_client.call_api(
            prompt=full_prompt,
            model=self._get_model(),
            temperature=temperature,
            max_tokens=self._config.get_config().get_max_improvement_tokens(),
            timeout=self._config.get_config().get_api_timeout()
        )
        
        # Return updated content
        return Content(
            id=content.id,
            body=response,
            material=content.material,
            category=content.category,
            created_at=content.created_at,
            specs=content.specs,
            version=content.version + 1 if hasattr(content, 'version') else 2
        )
    
    async def _call_api_with_settings(
        self,
        prompt: str,
        settings: GenerationSettings,
        operation_type: str
    ) -> str:
        """Call API with appropriate settings for operation type."""
        # Get temperature based on operation type
        if operation_type == "content_generation":
            temperature = settings.temperature_settings.content_generation
            max_tokens = self._config.get_config().get_max_content_tokens()
        elif operation_type == "improvement":
            temperature = settings.temperature_settings.improvement
            max_tokens = self._config.get_config().get_max_improvement_tokens()
        else:
            temperature = settings.temperature_settings.content_generation
            max_tokens = self._config.get_config().get_max_api_tokens()
        
        return self._api_client.call_api(
            prompt=prompt,
            model=self._get_model(),
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=settings.api_settings.timeout_seconds
        )
    
    def _get_model(self) -> str:
        """Get the model to use for content generation."""
        provider = self._config.get_config().get_generator_provider()
        return self._config.get_config().get_provider_model(provider)
    
    def _generate_content_id(self) -> str:
        """Generate unique content ID."""
        return f"content_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"


class DetectionService(ISimpleDetectionService):
    """Application service for AI content detection."""
    
    def __init__(
        self,
        api_client: IAPIClient,
        prompt_repository: ISimplePromptRepository,
        config_provider: ConfigProvider
    ):
        self._api_client = api_client
        self._prompt_repository = prompt_repository
        self._config = config_provider
    
    async def detect_ai_content(
        self,
        content: str,
        thresholds: ThresholdSettings
    ) -> DetectionResult:
        """Detect AI characteristics in content."""
        # Get AI detection prompt
        ai_prompt = await self._prompt_repository.get_ai_detection_prompt(content)
        
        # Call AI API for detection
        ai_response = await self._call_detection_api(ai_prompt, "ai_detection")
        ai_score = self._parse_score(ai_response)
        
        # Get human voice detection prompt
        human_prompt = await self._prompt_repository.get_human_detection_prompt(content)
        
        # Call AI API for human detection
        human_response = await self._call_detection_api(human_prompt, "human_detection")
        human_score = self._parse_score(human_response)
        
        # Calculate confidence based on consistency
        confidence = self._calculate_confidence(ai_score, human_score)
        
        from datetime import datetime
        from domain.value_objects.detection_result import DetectionStatus, ContentQuality
        
        # Determine status based on scores and thresholds
        status = DetectionStatus.PASSED
        if ai_score > thresholds.ai_threshold or human_score < thresholds.human_threshold:
            status = DetectionStatus.FAILED
        
        # Create quality level using our helper function
        quality = ContentQuality.GOOD
        if human_score >= 80:
            quality = ContentQuality.EXCELLENT
        elif human_score >= 60:
            quality = ContentQuality.GOOD
        elif human_score >= 40:
            quality = ContentQuality.MARGINAL
        else:
            quality = ContentQuality.POOR
        
        return DetectionResult(
            ai_score=ai_score,
            human_score=human_score,
            ai_confidence=confidence,
            human_confidence=confidence,
            status=status,
            quality=quality,
            iteration=1,
            timestamp=datetime.utcnow(),
            analysis_notes=["Test detection run"],
            detailed_scores=None,
            processing_time_ms=100.0
        )
    
    async def _call_detection_api(self, prompt: str, detection_type: str) -> str:
        """Call API for detection with appropriate settings."""
        if detection_type == "ai_detection":
            temperature = self._config.get_config().get_detection_temperature()
            max_tokens = self._config.get_config().get_max_detection_tokens()
        else:  # human_detection
            temperature = self._config.get_config().get_detection_temperature()
            max_tokens = self._config.get_config().get_max_large_response_tokens()
        
        provider = self._config.get_config().get_detection_provider()
        model = self._config.get_config().get_provider_model(provider)
        
        return self._api_client.call_api(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self._config.get_config().get_api_timeout()
        )
    
    def _parse_score(self, response: str) -> float:
        """Parse score from AI response."""
        # Look for numbers in the response
        import re
        
        # Try to find percentage (e.g., "25%", "25.5%")
        percentage_match = re.search(r'(\d+(?:\.\d+)?)\s*%', response)
        if percentage_match:
            return float(percentage_match.group(1))
        
        # Try to find score out of 100 (e.g., "25/100", "25 out of 100")
        score_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:/100|out of 100)', response)
        if score_match:
            return float(score_match.group(1))
        
        # Try to find any number between 0-100
        number_match = re.search(r'\b(\d+(?:\.\d+)?)\b', response)
        if number_match:
            score = float(number_match.group(1))
            if 0 <= score <= 100:
                return score
            elif 0 <= score <= 1:  # Convert from 0-1 scale to 0-100
                return score * 100
        
        # Default fallback - estimate based on response content
        response_lower = response.lower()
        if any(word in response_lower for word in ['high', 'very', 'significant', 'obvious']):
            return 75.0
        elif any(word in response_lower for word in ['medium', 'moderate', 'some']):
            return 50.0
        elif any(word in response_lower for word in ['low', 'minimal', 'slight']):
            return 25.0
        else:
            return 50.0  # Default middle value
    
    def _calculate_confidence(self, ai_score: float, human_score: float) -> float:
        """Calculate confidence score based on detection consistency."""
        # High confidence when scores are consistent (ai_score + human_score ≈ 100)
        total_score = ai_score + human_score
        
        # Ideal total is around 100, deviation reduces confidence
        deviation = abs(100 - total_score)
        
        # Convert deviation to confidence (0-1 scale)
        confidence = max(0.1, 1.0 - (deviation / 100.0))
        
        return min(1.0, confidence)
