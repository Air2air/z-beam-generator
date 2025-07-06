"""
Application command handlers for content generation.
"""

from typing import Optional
from dataclasses import dataclass

from domain.entities import Content, ContentMetadata
from domain.value_objects import ContentSpecs, GenerationSettings, DetectionResult
from domain.simple_repositories import ISimpleContentRepository, ISimplePromptRepository, ISimpleContentService, ISimpleDetectionService
from infrastructure.configuration import ConfigProvider


@dataclass
class GenerateContentCommand:
    """Command to generate content."""
    material: str
    category: str
    author: str
    specs: Optional[ContentSpecs] = None
    settings: Optional[GenerationSettings] = None


@dataclass
class GenerateContentResult:
    """Result of content generation."""
    content: Content
    detection_result: DetectionResult
    metadata: ContentMetadata
    success: bool
    message: str


class ContentGenerationHandler:
    """Handles content generation commands using clean architecture."""
    
    def __init__(
        self,
        content_service: ISimpleContentService,
        detection_service: ISimpleDetectionService,
        content_repository: ISimpleContentRepository,
        prompt_repository: ISimplePromptRepository,
        config_provider: ConfigProvider
    ):
        self._content_service = content_service
        self._detection_service = detection_service
        self._content_repository = content_repository
        self._prompt_repository = prompt_repository
        self._config = config_provider
    
    async def handle(self, command: GenerateContentCommand) -> GenerateContentResult:
        """Handle content generation command."""
        try:
            # Get generation settings from config if not provided
            settings = command.settings or self._get_default_settings()
            
            # Create content specs if not provided
            specs = command.specs or ContentSpecs.create_for_material(
                material=command.material,
                category=command.category,
                max_words=self._config.get_config().get_max_article_words()
            )
            
            # Generate initial content
            content = await self._content_service.generate_content(
                material=command.material,
                category=command.category,
                specs=specs,
                settings=settings
            )
            
            # Detect AI characteristics
            detection_result = await self._detection_service.detect_ai_content(
                content.body,
                settings.threshold_settings
            )
            
            # Improve content if detection scores are too high
            if self._needs_improvement(detection_result, settings):
                content = await self._improve_content(content, detection_result, settings)
                # Re-detect after improvement
                detection_result = await self._detection_service.detect_ai_content(
                    content.body,
                    settings.threshold_settings
                )
            
            # Generate metadata
            metadata = await self._generate_metadata(content, command)
            
            # Store content
            await self._content_repository.save(content)
            
            return GenerateContentResult(
                content=content,
                detection_result=detection_result,
                metadata=metadata,
                success=True,
                message="Content generated successfully"
            )
            
        except Exception as e:
            return GenerateContentResult(
                content=None,
                detection_result=None,
                metadata=None,
                success=False,
                message=f"Content generation failed: {str(e)}"
            )
    
    def _get_default_settings(self) -> GenerationSettings:
        """Get default generation settings from configuration."""
        from domain.value_objects.generation_settings import GenerationSettings, Provider
        
        provider_name = self._config.get_config().get_generator_provider()
        
        # Try to match by name or by value
        if provider_name in Provider.__members__:
            provider = Provider[provider_name]
        else:
            # Try to match by value (case-insensitive)
            found = False
            for member in Provider:
                if member.value.upper() == provider_name.lower():
                    provider = member
                    found = True
                    break
            
            if not found:
                provider = Provider.TEST if "TEST" in provider_name else Provider.GEMINI
        
        return GenerationSettings.create_default(provider)
    
    def _needs_improvement(self, detection_result: DetectionResult, settings: GenerationSettings) -> bool:
        """Check if content needs improvement based on detection results."""
        return (
            detection_result.ai_score > settings.threshold_settings.ai_threshold or
            detection_result.human_score < settings.threshold_settings.human_threshold
        )
    
    async def _improve_content(
        self, 
        content: Content, 
        detection_result: DetectionResult, 
        settings: GenerationSettings
    ) -> Content:
        """Improve content to reduce AI detection scores."""
        max_iterations = settings.max_iterations_per_section
        
        for iteration in range(max_iterations):
            # Get improvement suggestions
            improvement_prompt = await self._prompt_repository.get_improvement_prompt(
                content.body,
                detection_result
            )
            
            # Apply improvements
            improved_content = await self._content_service.improve_content(
                content,
                improvement_prompt,
                settings.temperature_settings.improvement
            )
            
            # Check if improvement is sufficient
            new_detection = await self._detection_service.detect_ai_content(
                improved_content.body,
                settings.threshold_settings
            )
            
            if not self._needs_improvement(new_detection, settings):
                return improved_content
            
            content = improved_content
            detection_result = new_detection
        
        return content
    
    async def _generate_metadata(self, content: Content, command: GenerateContentCommand) -> ContentMetadata:
        """Generate metadata for the content."""
        return ContentMetadata(
            title=await self._extract_title(content.body),
            description=await self._generate_description(content.body),
            author=command.author,
            category=command.category,
            material=command.material,
            word_count=len(content.body.split()),
            tags=await self._generate_tags(content.body, command.material)
        )
    
    async def _extract_title(self, content_body: str) -> str:
        """Extract title from content."""
        lines = content_body.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove markdown headers
                title = line.lstrip('# ').strip()
                return title[:100]  # Truncate if too long
        return "Generated Content"
    
    async def _generate_description(self, content_body: str) -> str:
        """Generate description from content."""
        # Take first paragraph that's not a header
        lines = content_body.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 50:
                return line[:200] + "..." if len(line) > 200 else line
        return "Generated content description"
    
    async def _generate_tags(self, content_body: str, material: str) -> list[str]:
        """Generate tags for content."""
        tags = [material.lower()]
        
        # Add common tags based on content analysis
        content_lower = content_body.lower()
        
        if 'laser' in content_lower:
            tags.append('laser')
        if 'cleaning' in content_lower:
            tags.append('cleaning')
        if 'industrial' in content_lower:
            tags.append('industrial')
        if 'surface' in content_lower:
            tags.append('surface-treatment')
        if 'metal' in content_lower:
            tags.append('metal')
        
        return list(set(tags))  # Remove duplicates
