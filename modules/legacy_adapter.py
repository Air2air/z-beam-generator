"""
Backward compatibility adapter for the legacy content generator.
This allows the existing system to use the new architecture gradually.
"""

from typing import Dict, Any, Optional, List
from generator.core.application import get_app
from generator.core.domain.models import (
    GenerationRequest,
    GenerationContext,
    SectionConfig,
    ProviderType,
    SectionType,
)
from generator.core.exceptions import ContentGenerationError
from generator.modules.logger import get_logger

logger = get_logger("legacy_adapter")


class LegacyContentGeneratorAdapter:
    """Adapter to bridge legacy API with new architecture."""

    def __init__(self):
        self._app = get_app()

    def generate_content(
        self,
        section_name: str,
        prompt_template: str,
        section_variables: Dict[str, Any],
        article_data: Dict[str, Any],
        cache_data: Dict[str, Any],
        generator_provider: str,
        model: str,
        force_regenerate: bool,
        api_keys: Dict[str, str],
        prompt_templates_dict: Dict[str, str],
        prompt_file_name: str,
        ai_detection_threshold: int,
        human_detection_threshold: int,
        ai_detect: bool = True,
        iterations_per_section: int = 3,
        generator_model_settings: Optional[Dict] = None,
        detection_provider: Optional[str] = None,
        detection_model_settings: Optional[Dict] = None,
    ) -> tuple[str, Optional[int], bool]:
        """
        Legacy interface for content generation.
        Returns: (content, ai_score, threshold_met)
        """
        try:
            logger.info(
                f"Legacy adapter generating content for section: {section_name}"
            )

            # Convert legacy parameters to new domain models
            request = self._create_generation_request(
                section_variables.get("material", "unknown"),
                [section_name],
                generator_provider,
                model,
                ai_detection_threshold,
                human_detection_threshold,
                iterations_per_section,
                section_variables.get("temperature", 1.0),
            )

            section_config = self._create_section_config(
                section_name, ai_detect, prompt_file_name
            )

            context = self._create_generation_context(
                section_variables, article_data, cache_data
            )

            # Get the appropriate API key
            api_key = api_keys.get(f"{generator_provider.upper()}_API_KEY")
            if not api_key:
                # Fallback to just the provider name
                api_key = api_keys.get(generator_provider.upper())
            if not api_key:
                raise ContentGenerationError(
                    f"No API key found for provider: {generator_provider}",
                    section=section_name,
                )

            # Get content generator with provider-specific configuration
            content_generator = self._app.get_content_generator(
                generator_provider.upper(), api_key
            )

            # Generate content using new architecture
            result = content_generator.generate_section(
                request, section_config, context
            )

            # Convert result back to legacy format
            ai_score = result.final_ai_score
            threshold_met = result.threshold_met

            logger.info(f"Legacy adapter completed generation for {section_name}")

            return result.content, ai_score, threshold_met

        except Exception as e:
            logger.error(f"Legacy adapter failed for {section_name}: {str(e)}")
            raise ContentGenerationError(
                f"Legacy content generation failed: {str(e)}", section=section_name
            ) from e

    def _create_generation_request(
        self,
        material: str,
        sections: List[str],
        provider: str,
        model: str,
        ai_threshold: int,
        human_threshold: int,
        iterations: int,
        temperature: float,
    ) -> GenerationRequest:
        """Create a GenerationRequest from legacy parameters."""
        try:
            provider_enum = ProviderType(provider.upper())
        except ValueError:
            logger.error(f"Unknown provider {provider}, no fallback configured")
            raise ValueError(f"Provider {provider} is not supported. Check your run.py configuration.")

        return GenerationRequest(
            material=material,
            sections=sections,
            provider=provider_enum,
            model=model,
            ai_detection_threshold=ai_threshold,
            human_detection_threshold=human_threshold,
            iterations_per_section=iterations,
            temperature=temperature,
        )

    def _create_section_config(
        self, section_name: str, ai_detect: bool, prompt_file: str
    ) -> SectionConfig:
        """Create a SectionConfig from legacy parameters."""
        # Map section names to types (basic mapping)
        section_type_mapping = {
            "table": SectionType.TABLE,
            "chart": SectionType.CHART,
            "list": SectionType.LIST,
            "comparison": SectionType.COMPARISON,
        }

        section_type = section_type_mapping.get(section_name, SectionType.TEXT)

        return SectionConfig(
            name=section_name,
            ai_detect=ai_detect,
            prompt_file=prompt_file,
            section_type=section_type,
        )

    def _create_generation_context(
        self,
        section_variables: Dict[str, Any],
        article_data: Dict[str, Any],
        cache_data: Dict[str, Any],
    ) -> GenerationContext:
        """Create a GenerationContext from legacy parameters."""
        material = section_variables.get("material", "unknown")
        content_type = section_variables.get("content_type", "article")

        return GenerationContext(
            material=material,
            content_type=content_type,
            variables=section_variables,
            material_details=article_data.get("material_details"),
            article_data=article_data,
            cache_data=cache_data,
        )


# Legacy function for backward compatibility
def generate_content(*args, **kwargs):
    """Legacy function that uses the new architecture under the hood."""
    adapter = LegacyContentGeneratorAdapter()
    return adapter.generate_content(*args, **kwargs)
