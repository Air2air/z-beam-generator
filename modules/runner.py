from config.settings import AppConfig, GenerationConfig
from modules.page_generator import ArticleGenerator
from exceptions import ConfigurationError, GenerationError
from core.domain.models import TemperatureConfig
from dataclasses import dataclass
from typing import Optional
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from modules.logger import get_logger


@dataclass
class RunConfiguration:
    """Configuration for a single run of the article generator."""

    material: str
    category: str
    file_name: str  # Renamed from filename
    generator_provider: str
    model: str  # <-- Add this line
    author: str  # Just a string filename
    temperature: float  # Maintained for backward compatibility
    force_regenerate: bool
    ai_detection_threshold: int
    human_detection_threshold: int  # Add human threshold
    generator_model_settings: dict  # <-- Add this line
    iterations_per_section: int = None  # Will be set from config
    detection_provider: str = None
    detection_model_settings: dict = None
    max_article_words: int = None  # Will be set from config
    api_timeout: int = None  # Will be set from config
    detection_temperature: float = None  # Will be set from config
    temperature_config: Optional[TemperatureConfig] = None

    def __post_init__(self):
        # Import here to avoid circular imports
        from config.global_config import get_config
        
        # Set defaults from configuration if not provided
        if self.iterations_per_section is None:
            self.iterations_per_section = get_config().get_iterations_per_section()
        if self.max_article_words is None:
            self.max_article_words = get_config().get_max_article_words()
        if self.api_timeout is None:
            self.api_timeout = get_config().get_api_timeout()
        if self.detection_temperature is None:
            self.detection_temperature = get_config().get_detection_temperature()
            
        missing = []
        for field_name in [
            "material",
            "category",
            "file_name",
            "generator_provider",
            "model",
            "author",
            "temperature",
            "force_regenerate",
            "ai_detection_threshold",
            "human_detection_threshold",
            "generator_model_settings",
        ]:
            if getattr(self, field_name, None) is None:
                missing.append(field_name)

        # Create temperature_config if not provided (from legacy fields)
        if self.temperature_config is None:
            self.temperature_config = TemperatureConfig.from_legacy_config(
                content_temp=self.temperature, detection_temp=self.detection_temperature
            )
        if missing:
            raise ConfigurationError(
                f"Missing required configuration fields: {', '.join(missing)}"
            )

    def validate(self) -> None:
        """Validate the run configuration."""
        if not self.material:
            raise ConfigurationError("Material cannot be empty")
        if not self.file_name:
            raise ConfigurationError("file_name cannot be empty")
        
        # Validate provider against run.py configuration instead of hardcoded list
        try:
            import sys, os, importlib.util
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            run_path = os.path.join(project_root, "run.py")
            spec = importlib.util.spec_from_file_location("run_module", run_path)
            run_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(run_module)
            supported_providers = list(getattr(run_module, "PROVIDER_MODELS", {}).keys())
            
            if self.generator_provider.upper() not in [p.upper() for p in supported_providers]:
                raise ConfigurationError(
                    f"Unsupported generator_provider: {self.generator_provider}. "
                    f"Supported providers: {supported_providers}"
                )
        except Exception:
            # If we can't load run.py, just skip provider validation
            pass


class ApplicationRunner:
    """Handles the application lifecycle and orchestrates article generation."""

    def __init__(self):
        self.logger = get_logger("app_runner")
        self.app_config = AppConfig()

    def setup_environment(self) -> None:
        """Setup the application environment."""
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        load_dotenv()

    def create_generation_config(
        self, run_config: RunConfiguration
    ) -> GenerationConfig:
        api_keys = {
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
            "XAI_API_KEY": os.getenv("XAI_API_KEY"),
            "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
        }
        required_key = f"{run_config.generator_provider.upper()}_API_KEY"
        if not api_keys.get(required_key):
            self.logger.warning(
                f"No API key found for generator_provider '{run_config.generator_provider}'. "
                f"Please ensure {required_key} is set in your .env file."
            )
        return GenerationConfig(
            material=run_config.material,
            article_category=run_config.category,
            file_name=run_config.file_name,
            generator_provider=run_config.generator_provider,
            model=run_config.model,  # Use model from run_config, not from AppConfig
            author=run_config.author,
            temperature=run_config.temperature,  # Legacy field - kept for backward compatibility
            force_regenerate=run_config.force_regenerate,
            api_keys=api_keys,
            ai_detection_threshold=run_config.ai_detection_threshold,
            human_detection_threshold=run_config.human_detection_threshold,
            generator_model_settings=run_config.generator_model_settings,
            iterations_per_section=run_config.iterations_per_section,
            detection_provider=getattr(run_config, "detection_provider", None),
            detection_model_settings=getattr(
                run_config, "detection_model_settings", None
            ),
            max_article_words=run_config.max_article_words,
            temperature_config=run_config.temperature_config,  # Pass the temperature_config
        )

    def run(self, run_config: RunConfiguration) -> bool:
        try:
            run_config.validate()
            self.setup_environment()
            gen_config = self.create_generation_config(run_config)
            generator = ArticleGenerator(self.app_config)
            generator.generate_article(gen_config)
            self.logger.info("Article generation completed successfully")
            return True
        except (ConfigurationError, GenerationError) as e:
            self.logger.error(f"Generation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during generation: {e}", exc_info=True)
            return False
