# generator/modules/page_generator.py
"""
Refactored page generator with better separation of concerns and error handling.
"""

import json
import os
import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from config.global_config import get_config
import yaml

from generator.config.settings import AppConfig, GenerationConfig
from generator.modules.logger import get_logger
from generator.exceptions import GenerationError, FileOperationError
from generator.modules import content_generator
from generator.modules.metadata_generator import generate_metadata
from generator.modules.prompt_loader import PromptLoader
from generator.modules.prompt_manager import PromptManager
from generator.modules.file_handler import save_file, read_cache, write_cache
from generator.modules.prompt_repository_adapter import PromptRepositoryAdapter
from generator.modules.mdx_validator import validate_mdx_output

# NEW: Import DI container and modern services
from generator.core.container import get_container
from generator.core.application import configure_services
from generator.core.interfaces.services import IContentGenerator, IPromptRepository
from generator.core.domain.models import (
    GenerationRequest,
    SectionConfig,
    GenerationContext,
    ProviderType,
    SectionType,
)


@dataclass
class ArticleData:
    """Structured representation of article data."""

    metadata: Dict[str, Any]
    sections: Dict[str, str]
    material_details: Optional[Dict[str, Any]] = None

    def to_mdx(self) -> str:
        """Convert article data to MDX format."""
        # If metadata is already a YAML string, just use it
        if isinstance(self.metadata, str) and self.metadata.startswith("---"):
            mdx_content = self.metadata + "\n\n"
        else:
            mdx_content = "---\n"
            for key, value in self.metadata.items():
                if isinstance(value, (list, dict)):
                    mdx_content += f"{key}: {json.dumps(value)}\n"
                else:
                    mdx_content += f"{key}: {value}\n"
            mdx_content += "---\n\n"

        # Write sections in the order specified in config
        section_order = [
            "introduction",
            "comparison",
            "chart",
            "contaminants",
            "substrates",
            "table",
        ]
        for section_name in section_order:
            if section_name in self.sections:
                title = section_name.replace("_", " ").title()
                mdx_content += f"## {title}\n{self.sections[section_name]}\n\n"
        # Write any remaining sections not in the order list
        for section_name, content in self.sections.items():
            if section_name not in section_order:
                title = section_name.replace("_", " ").title()
                mdx_content += f"## {title}\n{content}\n\n"

        return mdx_content


class ArticleGenerator:
    """Main article generation orchestrator."""

    def __init__(self, app_config: AppConfig):
        self.config = app_config
        self.logger = get_logger("page_generator")

        # Initialize components
        self.prompt_loader = PromptLoader(
            os.path.join(os.path.dirname(__file__), "../prompts/sections")
        )
        self.prompt_manager = PromptManager(
            os.path.join(os.path.dirname(__file__), "../prompts")
        )

        # NEW: Initialize DI container and modern services
        self.container = get_container()
        configure_services(self.container)
        self.content_generator = (
            None  # Will be initialized with max_article_words in generate_article
        )

        # Initialize prompt repository for fallback section generation
        from generator.infrastructure.storage.enhanced_json_prompt_repository import (
            EnhancedJsonPromptRepository,
        )
        from pathlib import Path

        prompts_dir = Path(__file__).parent.parent / "prompts"
        self.prompt_repository = EnhancedJsonPromptRepository(prompts_dir)

    def _initialize_efficient_content_service(
        self, gen_config: GenerationConfig
    ) -> None:
        """Initialize the EfficientContentGenerationService with word budget."""
        from generator.core.services.efficient_content_service import (
            EfficientContentGenerationService,
        )
        from generator.core.interfaces.services import (
            IAPIClient,
            IPromptRepository,
        )
        from generator.core.services.detection_service import DetectionService
        from generator.infrastructure.api.client import APIClient

        # Create provider-specific API client based on user config
        provider = gen_config.generator_provider.upper()
        api_key_name = f"{provider}_API_KEY"
        api_key = gen_config.api_keys.get(api_key_name)

        if not api_key:
            self.logger.warning(
                f"No API key found for {provider}. Using container default."
            )
            api_client = self.container.get(IAPIClient)
        else:
            # Create provider-specific API client
            api_client = APIClient(provider, api_key)
            self.logger.info(f"Created {provider} API client for content generation")

        # Get other services from container
        prompt_repository = self.container.get(IPromptRepository)

        # Create detection service with the same provider as generation
        detection_api_client = api_client  # Use the same API client for consistency
        detection_service = DetectionService(detection_api_client, prompt_repository)

        # Initialize efficient content service with word budget
        max_article_words = getattr(gen_config, "max_article_words", None)
        if max_article_words is None:
            max_article_words = get_config().get_max_article_words()
        self.content_generator = EfficientContentGenerationService(
            api_client=api_client,
            detection_service=detection_service,
            prompt_repository=prompt_repository,
            max_article_words=max_article_words,
        )

        self.logger.info(
            f"Initialized EfficientContentGenerationService with {max_article_words} word budget using {provider}"
        )

    def generate_article(self, gen_config: GenerationConfig) -> None:
        """
        Generate a complete article based on the given configuration.

        Args:
            gen_config: Configuration for the generation process

        Raises:
            GenerationError: If the generation process fails
        """
        self.logger.info(
            f"Starting article generation for material: '{gen_config.material}', "
            f"provider: '{gen_config.generator_provider}', model: '{gen_config.model}'"
        )

        try:
            # NEW: Initialize efficient content service with word budget
            self._initialize_efficient_content_service(gen_config)

            # Load required data
            prompt_templates = self._load_prompt_templates()
            sections_config = self._load_sections_config()

            # Research material configuration
            material_config = self._research_material_config(
                gen_config, prompt_templates
            )

            # Initialize article data
            article_data = self._initialize_article_data(gen_config, material_config)

            # Load cache if not forcing regeneration
            cache_data = self._load_cache_data(gen_config)

            # Generate content for each section
            self._generate_sections(
                article_data,
                sections_config,
                gen_config,
                prompt_templates,
                cache_data,
                gen_config.ai_detection_threshold,  # Strict: always use the value from run.py, no fallback
                gen_config.human_detection_threshold,  # Pass human threshold
            )

            # Save the final article
            self._save_article(article_data, gen_config, cache_data)

            # NEW: Display efficiency summary
            self._display_generation_summary(gen_config)

            self.logger.info("Article generation completed successfully")
            print(
                f"[PROGRESS] Article generation completed successfully for: {gen_config.file_name}"
            )

        except Exception as e:
            self.logger.error(f"Article generation failed: {e}", exc_info=True)
            raise GenerationError(f"Failed to generate article: {e}") from e

    def _display_generation_summary(self, gen_config: GenerationConfig) -> None:
        """Display a summary of the generation process including efficiency metrics."""
        max_words = getattr(gen_config, "max_article_words", None)
        if max_words is None:
            max_words = get_config().get_max_article_words()
        budget_manager = self.content_generator.word_budget_manager

        print(f"\n{'=' * 60}")
        print("📊 GENERATION SUMMARY")
        print(f"{'=' * 60}")
        print(f"🎯 Target Word Budget: {max_words} words")
        print(f"📝 Material: {gen_config.material}")
        print(f"🤖 Provider: {gen_config.generator_provider}")
        print(f"⚙️  Max Iterations per Section: {gen_config.iterations_per_section}")
        print(f"🧠 AI Threshold: ≤{gen_config.ai_detection_threshold}%")
        print(f"👤 Human Threshold: ≤{gen_config.human_detection_threshold}%")

        # Show word budget allocation
        print("\n📏 WORD BUDGET ALLOCATION:")
        for section_name, budget in budget_manager.section_budgets.items():
            print(
                f"   {section_name}: {budget.target_words} words ({budget.percentage * 100:.1f}%)"
            )

        print(f"{'=' * 60}")
        self.logger.info(
            "✅ Article generation completed with efficient word budget management"
        )

    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates from JSON repository with fallback to text files."""
        try:
            # First try using the JSON repository adapter
            try:
                # Get repository from container
                repository = self.container.get(IPromptRepository)
                adapter = PromptRepositoryAdapter(repository)
                templates = adapter.get_section_templates()

                if templates:
                    self.logger.info(
                        f"Loaded {len(templates)} prompt templates from JSON repository"
                    )
                    return templates

            except Exception as json_error:
                self.logger.warning(
                    f"Failed to load from JSON repository: {json_error}, falling back to text files"
                )

            # Fallback to legacy text file loading
            templates = self.prompt_loader.load_all_templates()
            if not templates:
                raise GenerationError("No prompt templates loaded from any source")
            return templates

        except Exception as e:
            raise GenerationError(f"Failed to load prompt templates: {e}") from e

    def _load_sections_config(self) -> Dict[str, Dict[str, Any]]:
        """Load sections configuration."""
        return self.config.load_sections_config()

    def _research_material_config(
        self, gen_config: GenerationConfig, prompt_templates: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """Research material configuration using AI."""
        try:
            material_config = content_generator.research_material_config(
                gen_config.material,
                gen_config.generator_provider,
                gen_config.model,
                gen_config.api_keys,
                prompt_templates,
                gen_config.generator_model_settings,  # Pass the model settings
            )

            if material_config:
                self.logger.info(
                    f"Successfully researched material config for '{gen_config.material}'"
                )
                return material_config
            else:
                self.logger.warning(
                    f"Failed to research material config for '{gen_config.material}'"
                )
                return None

        except Exception as e:
            self.logger.error(f"Material research failed: {e}")
            raise GenerationError(f"Failed to research material config: {e}") from e

    def _initialize_article_data(
        self,
        gen_config: GenerationConfig,
        material_config: Optional[Dict[str, Any]],
    ) -> ArticleData:
        """Initialize the article data structure with author metadata."""
        # Only log metadata once per run
        if not hasattr(self, "_metadata_logged"):
            self._metadata_logged = True
            self.logger.info(
                f"[METADATA] Article metadata: material={gen_config.material}, file={gen_config.file_name}, provider={gen_config.generator_provider}, author={gen_config.author}, temperature={gen_config.temperature}"
            )
        # Normalize author key (strip .mdx, lowercase, underscores)
        author_key = (
            os.path.splitext(gen_config.author)[0]
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )
        author_metadata = self._load_author_metadata(author_key)
        # Compose article_config dict for metadata
        article_config = {
            "author": gen_config.author,
            "temperature": gen_config.temperature,
            "model": getattr(gen_config, "model", None),
        }
        ai_scores = {}  # You may want to pass actual scores if available
        article_category = getattr(gen_config, "category", None) or "material"
        metadata_yaml = generate_metadata(
            gen_config.material,
            material_config or {},
            article_config,
            author_metadata,
            ai_scores,
            article_category,
        )
        return ArticleData(
            metadata=metadata_yaml, sections={}, material_details=material_config
        )

    def _load_cache_data(self, gen_config: GenerationConfig) -> Dict[str, Any]:
        """Load cache data if available and not forcing regeneration."""
        if gen_config.force_regenerate:
            self.logger.info("Force regeneration is active. Ignoring cache.")
            return {}

        try:
            cache_file = gen_config.file_name.replace(".mdx", ".cache.json")
            cache_data = read_cache(cache_file)

            if cache_data:
                self.logger.info(f"Loaded existing cache from {cache_file}")
                return cache_data
            else:
                self.logger.info("No cache found, using fresh generation")
                return {}

        except Exception as e:
            self.logger.warning(f"Failed to load cache: {e}")
            return {}

    def _generate_sections(
        self,
        article_data: ArticleData,
        sections_config: Dict[str, Dict[str, Any]],
        gen_config: GenerationConfig,
        prompt_templates: Dict[str, str],
        cache_data: Dict[str, Any],
        ai_detection_threshold: int,  # Pass threshold through pipeline
        human_detection_threshold: int,  # Pass human threshold through pipeline
    ) -> None:
        """Generate content for all sections using coordinated budget allocation."""
        sorted_sections = sorted(
            sections_config.items(), key=lambda item: item[1].get("order", 999)
        )

        # Filter out sections that should not be generated
        sections_to_generate = []
        for section_name, section_config in sorted_sections:
            if section_name == "ai_detection_prompt":
                continue  # Skip ai_detection_prompt as a section
            if not section_config.get("generate", True):
                continue
            # Add all sections - ai_detect flag controls detection, not generation
            sections_to_generate.append((section_name, section_config))

        if not sections_to_generate:
            self.logger.warning("No sections to generate")
            return

        # Use coordinated generation for efficient word budget allocation
        try:
            self._generate_sections_coordinated(
                article_data,
                sections_to_generate,
                gen_config,
                prompt_templates,
                cache_data,
                ai_detection_threshold,
                human_detection_threshold,
            )
        except Exception as e:
            self.logger.error(f"Coordinated generation failed: {e}")
            self.logger.info("Falling back to individual section generation")
            # Fallback to individual generation
            for section_name, section_config in sections_to_generate:
                self._generate_single_section(
                    section_name,
                    section_config,
                    article_data,
                    gen_config,
                    prompt_templates,
                    cache_data,
                    ai_detection_threshold,
                    human_detection_threshold,
                )

        if not article_data.sections:
            raise GenerationError("No sections were successfully generated")

    def _generate_sections_coordinated(
        self,
        article_data: ArticleData,
        sections_to_generate: List[Tuple[str, Dict[str, Any]]],
        gen_config: GenerationConfig,
        prompt_templates: Dict[str, str],
        cache_data: Dict[str, Any],
        ai_detection_threshold: int,
        human_detection_threshold: int,
    ) -> None:
        """Generate all sections using coordinated word budget allocation."""
        self.logger.info(
            f"🎯 Generating {len(sections_to_generate)} sections with coordinated budget allocation"
        )

        # Create GenerationRequest for all sections
        section_names = [name for name, _ in sections_to_generate]
        request = GenerationRequest(
            material=gen_config.material,
            sections=section_names,
            provider=ProviderType(gen_config.generator_provider),
            model=gen_config.model,
            ai_detection_threshold=ai_detection_threshold,
            human_detection_threshold=human_detection_threshold,
            iterations_per_section=gen_config.iterations_per_section,
            temperature=gen_config.temperature,
            max_tokens=get_config().get_max_improvement_tokens(),  # Will be managed by budget
            force_regenerate=gen_config.force_regenerate,
        )

        # Create SectionConfig objects for all sections
        section_configs = []
        for section_name, section_config in sections_to_generate:
            ai_detect = section_config.get("ai_detect", True)

            section_config_obj = SectionConfig(
                name=section_name,
                ai_detect=ai_detect,
                prompt_file=section_name,  # Use section name directly for JSON lookup
                section_type=SectionType.TEXT,
                generate=True,
                order=section_config.get("order", 1),
            )
            section_configs.append(section_config_obj)

        # Create GenerationContext
        section_variables = {
            "material": gen_config.material,
            "temperature": gen_config.temperature,
        }
        context = GenerationContext(
            material=gen_config.material,
            content_type="article",
            variables=section_variables,
        )

        # Generate all sections with coordinated budget allocation
        self.logger.info(
            "📊 Using EfficientContentGenerationService.generate_article_sections for coordinated budget management"
        )
        results = self.content_generator.generate_article_sections(
            request=request, section_configs=section_configs, context=context
        )

        # Process results and store in article_data
        for section_name, _ in sections_to_generate:
            result = results.get(section_name)
            if result and result.content:
                article_data.sections[section_name] = result.content

                ai_likelihood = result.ai_score.score if result.ai_score else None
                threshold_met = result.threshold_met

                if threshold_met:
                    self.logger.info(
                        f"✅ Successfully generated content for section: {section_name} "
                        f"(AI: {ai_likelihood}%, target: ≤{ai_detection_threshold}%)"
                    )
                else:
                    self.logger.warning(
                        f"⚠️ Section '{section_name}' generated but did NOT meet thresholds. "
                        f"AI: {ai_likelihood}%, target: ≤{ai_detection_threshold}%"
                    )
            else:
                self.logger.error(
                    f"❌ Failed to generate content for section: {section_name}"
                )

        self.logger.info(
            f"🎉 Coordinated generation completed for {len(results)} sections"
        )

    def _generate_single_section(
        self,
        section_name: str,
        section_config: Dict[str, Any],
        article_data: ArticleData,
        gen_config: GenerationConfig,
        prompt_templates: Dict[str, str],
        cache_data: Dict[str, Any],
        ai_detection_threshold: int,  # Accept threshold
        human_detection_threshold: int,  # Accept human threshold
    ) -> None:
        """Generate content for a single section."""
        # NEW: Use JSON repository to get prompt instead of legacy prompt files
        try:
            prompt_template = self.prompt_repository.get_prompt(
                section_name, "sections"
            )
            if not prompt_template:
                self.logger.warning(
                    f"No prompt found for section '{section_name}' in JSON repository. Skipping."
                )
                return
        except Exception as e:
            self.logger.error(
                f"Failed to load prompt for section '{section_name}': {e}"
            )
            return

        # Prepare section variables (word budget will be managed by EfficientContentGenerationService)
        section_variables = {
            **gen_config.__dict__,
            **(article_data.material_details or {}),
            "content_type": section_name,
            "temperature": gen_config.temperature,
            "iterations_per_section": gen_config.iterations_per_section,
        }
        ai_detect = section_config.get("ai_detect", True)

        self.logger.info(f"Generating content for section: {section_name}")

        # Use cached section content if available and not forcing regeneration
        if not gen_config.force_regenerate and section_name in cache_data.get(
            "sections", {}
        ):
            cached_content = cache_data["sections"][section_name]
            article_data.sections[section_name] = cached_content
            self.logger.info(f"Loaded cached content for section: {section_name}")
            return

        try:
            # NEW: Use EfficientContentGenerationService instead of legacy function
            # Create GenerationRequest
            request = GenerationRequest(
                material=gen_config.material,
                sections=[section_name],
                provider=ProviderType(gen_config.generator_provider.upper()),
                model=gen_config.model,
                ai_detection_threshold=ai_detection_threshold,
                human_detection_threshold=human_detection_threshold,
                iterations_per_section=gen_config.iterations_per_section,
                temperature=gen_config.temperature,
                max_tokens=get_config().get_max_improvement_tokens(),  # Will be managed by word budget
                force_regenerate=gen_config.force_regenerate,
            )

            # Create SectionConfig
            section_config_obj = SectionConfig(
                name=section_name,
                ai_detect=ai_detect,
                prompt_file=section_name,  # Use section name as identifier
                section_type=SectionType.TEXT,
                generate=True,
                order=1,
            )

            # Create GenerationContext
            context = GenerationContext(
                material=gen_config.material,
                content_type=section_name,
                variables=section_variables,
            )

            # Use efficient content generation service
            result = self.content_generator.generate_section(
                request=request, section_config=section_config_obj, context=context
            )

            # Extract results
            content = result.content
            ai_likelihood = result.ai_score.score if result.ai_score else None
            threshold_met = result.threshold_met

            if content:
                article_data.sections[section_name] = content
                if threshold_met:
                    self.logger.info(
                        f"✅ Successfully generated content for section: {section_name} "
                        f"(AI: {ai_likelihood}%, target: ≤{ai_detection_threshold}%)"
                    )
                else:
                    self.logger.warning(
                        f"⚠️ Section '{section_name}' generated but did NOT meet thresholds. "
                        f"AI: {ai_likelihood}%, target: ≤{ai_detection_threshold}%"
                    )
            else:
                self.logger.error(
                    f"❌ No content generated for section: {section_name}"
                )

        except Exception as e:
            self.logger.error(
                f"❌ Error generating content for section '{section_name}': {e}",
                exc_info=True,
            )

    def _save_article(
        self,
        article_data: ArticleData,
        gen_config: GenerationConfig,
        cache_data: Dict[str, Any],
    ) -> None:
        """Save the generated article and cache."""
        try:
            print(f"[PROGRESS] Saving article to file: {gen_config.file_name}")
            # Save the article
            output_dir = os.path.join("app", "(materials)", "posts")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, gen_config.file_name)
            mdx_content = article_data.to_mdx()

            # Validate and fix MDX content for Next.js compatibility
            validated_content, validation_issues = validate_mdx_output(mdx_content)
            if validation_issues:
                self.logger.info(
                    f"MDX validation fixed {len(validation_issues)} issues:"
                )
                for issue in validation_issues:
                    self.logger.info(f"  - {issue}")

            save_file(output_path, validated_content)
            self.logger.info(f"Article saved to: {output_path}")

            # Save the cache
            cache_file = gen_config.file_name.replace(".mdx", ".cache.json")
            cache_path = os.path.join(output_dir, cache_file)
            cache_data.update(
                {
                    "metadata": article_data.metadata,
                    "material_details": article_data.material_details,
                }
            )
            write_cache(cache_path, cache_data)
            self.logger.info(f"Cache saved to: {cache_path}")
            print(
                f"[PROGRESS] Finished saving article and cache for: {gen_config.file_name}"
            )

        except Exception as e:
            raise FileOperationError(f"Failed to save article or cache: {e}") from e

    def _load_author_metadata(self, author_filename: str) -> Dict[str, Any]:
        """Load metadata for a single author from .mdx file (YAML frontmatter)."""
        author_dir = self.config.directories.author_dir
        file_path = os.path.join(author_dir, author_filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            match = re.match(r"---\s*\n(.*?)\n---", content, re.DOTALL)
            if not match:
                return {}
            metadata = yaml.safe_load(match.group(1))
            return metadata if isinstance(metadata, dict) else {}
        except Exception:
            return {}


# Legacy function for backward compatibility
def main(*args, **kwargs):
    """Legacy main function for backward compatibility."""
    from generator.config.settings import AppConfig

    # Convert old-style arguments to new configuration
    gen_config = GenerationConfig(
        material=kwargs.get("material"),
        article_category=kwargs.get("article_category"),
        file_name=kwargs.get("file_name"),
        provider=kwargs.get("provider"),
        model=kwargs.get("model"),
        authors=kwargs.get(
            "authors", []
        ),  # Kept for legacy, but not used in new pipeline
        force_regenerate=kwargs["force_regenerate"],
        api_keys=kwargs.get("api_keys", {}),
        temperature=kwargs["temperature"],
    )

    app_config = AppConfig()
    generator = ArticleGenerator(app_config)
    generator.generate_article(gen_config)
