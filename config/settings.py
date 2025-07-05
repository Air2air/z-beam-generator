# generator/config/settings.py
"""
Centralized configuration management for the article generation system.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import yaml

from generator.exceptions import ConfigurationError


# --- Directory and Path Configuration ---
@dataclass
class DirectoryConfig:
    """Configuration for directory paths."""

    def __post_init__(self):
        self.generator_dir = Path(__file__).parent.parent
        self.project_root = self.generator_dir.parent
        self.author_dir = self.generator_dir / "authors"
        self.sections_dir = self.generator_dir / "sections"
        self.output_dir = self.project_root / "app" / "(materials)" / "posts"


# --- API Provider Configuration ---
@dataclass
class APIProviderConfig:
    """Configuration for a specific API generator_provider."""

    model: str
    url_template: str
    default_temperature: float  # Remove default
    default_max_tokens: int = 1000


# --- Content and Section Configuration ---
@dataclass
class ContentConfig:
    """Configuration for content generation."""

    ai_detection_fallback_prompts: list[str] = field(
        default_factory=lambda: [
            "Evaluate text for AI traits. Return percentage (0-100) and summary (1-2 sentences): {content}",
            "Analyze text for AI-generated style. Return percentage (0-100) and summary (string): {content}",
        ]
    )
    default_content_lengths: Dict[str, str] = field(
        default_factory=lambda: {
            "introduction": "150-200",
            "contaminants": "70-100",
            "table": "60-90",
            "chart": "60-90",
            "comparison": "60-90",
            "substrates": "100-150",
        }
    )
    section_type_mapping: Dict[str, str] = field(
        default_factory=lambda: {
            "introduction": "paragraph",
            "contaminants": "list",
            "table": "table",
            "chart": "chart",
            "comparison": "comparison_chart",
        }
    )
    section_order: list[str] = field(
        default_factory=lambda: [
            "introduction",
            "contaminants",
            "table",
            "chart",
            "comparison",
            "substrates",
        ]
    )


class AppConfig:
    """Main application configuration manager."""

    def __init__(self):
        self.directories = DirectoryConfig()
        self.content = ContentConfig()
        self._setup_providers()

    def _setup_providers(self):
        """Setup API provider configurations."""
        # REMOVE all hardcoded provider configs from here. All API/model config must come from run.py only.
        self.providers = {}

    def get_provider_config(self, provider: str) -> APIProviderConfig:
        provider_key = provider.upper()
        if provider_key not in self.providers:
            raise ConfigurationError(f"Unknown provider: {provider}")
        return self.providers[provider_key]

    def get_model_for_provider(self, provider: str) -> str:
        return self.get_provider_config(provider).model

    def get_api_url(self, provider: str) -> str:
        return self.get_provider_config(provider).url_template

    def load_sections_config(self) -> Dict[str, Dict[str, Any]]:
        """Load sections configuration from JSON repository or fallback to text files."""
        sections_config = {}

        # Try to load from JSON repository first
        try:
            from generator.infrastructure.storage.enhanced_json_prompt_repository import (
                EnhancedJsonPromptRepository,
            )

            # Initialize repository
            prompts_dir = self.directories.generator_dir / "prompts"
            repository = EnhancedJsonPromptRepository(prompts_dir)

            # Get all section metadata
            section_metadata = repository.get_all_prompt_metadata("sections")

            # Convert to the format expected by the application
            for name, data in section_metadata.items():
                sections_config[name] = {
                    "ai_detect": data.get("ai_detect", True),
                    "order": data.get("order", 999),
                    "section_type": data.get("section_type", "TEXT"),
                    "title": data.get("title", name.title()),
                    "generate": True,  # All sections from JSON should be generated
                }

            if sections_config:
                return sections_config

        except Exception as e:
            print(f"Warning: Failed to load sections from JSON repository: {e}")
            print("Falling back to text file loading...")

        # Fallback to legacy text file loading
        sections_dir = self.directories.generator_dir / "prompts" / "sections"
        if not sections_dir.exists():
            return sections_config
        for file_path in sections_dir.glob("*.txt"):
            section_key = file_path.stem
            ai_detect = True  # Default
            # Parse ai_detect from YAML frontmatter or # ai_detect: ... comment
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                # Check for YAML frontmatter
                if lines and lines[0].strip() == "---":
                    end = next(
                        (
                            i
                            for i, line in enumerate(lines[1:], 1)
                            if line.strip() == "---"
                        ),
                        None,
                    )
                    if end is not None:
                        yaml_block = "".join(lines[1:end])
                        meta = yaml.safe_load(yaml_block)
                        if isinstance(meta, dict) and "ai_detect" in meta:
                            ai_detect = bool(meta["ai_detect"])
                # Check for # ai_detect: ... in first 10 lines
                for line in lines[:10]:
                    if line.strip().lower().startswith("# ai_detect:"):
                        val = line.split(":", 1)[1].strip().lower()
                        if val in ("false", "no", "0"):
                            ai_detect = False
                        elif val in ("true", "yes", "1"):
                            ai_detect = True
                        break
            except Exception:
                pass
            sections_config[section_key] = {
                "prompt_file": file_path.name,
                "type": self.content.section_type_mapping.get(section_key, "text"),
                "generate": True,
                "order": len(sections_config),
                "ai_detect": ai_detect,
            }
        return sections_config


# --- Generation Request Configuration ---
@dataclass
class GenerationConfig:
    material: str
    article_category: str
    file_name: str
    generator_provider: str
    model: str
    author: str
    temperature: float  # Legacy field, maintained for backward compatibility
    force_regenerate: bool
    ai_detection_threshold: int  # <-- moved up, before any default fields
    human_detection_threshold: int  # Add human threshold
    generator_model_settings: dict = None  # <-- Add this line
    detection_provider: str = None
    detection_model_settings: dict = None
    temperature_config: Any = None  # Use Any to avoid circular imports
    iterations_per_section: int = 3
    max_article_words: int = 1200  # Total word budget for article
    api_keys: dict = None
    title: Optional[str] = None
    keywords: list[str] = field(default_factory=list)

    def __post_init__(self):
        # Strict required fields check
        required_fields = [
            "material",
            "article_category",
            "file_name",
            "generator_provider",
            "model",
            "author",
            "temperature",
            "force_regenerate",
            "api_keys",
            "ai_detection_threshold",
            "human_detection_threshold",
            "iterations_per_section",
        ]
        missing = [f for f in required_fields if getattr(self, f, None) is None]
        if missing:
            raise ConfigurationError(
                f"Missing required GenerationConfig fields: {', '.join(missing)}"
            )
        if not self.title:
            self.title = f"Laser Cleaning {self.material}"

    def validate(self):
        # Reuse the strict required fields check from __post_init__
        required_fields = [
            "material",
            "article_category",
            "file_name",
            "generator_provider",
            "model",
            "author",
            "temperature",
            "force_regenerate",
            "api_keys",
            "ai_detection_threshold",
            "human_detection_threshold",
            "iterations_per_section",
        ]
        missing = [f for f in required_fields if getattr(self, f, None) is None]
        if missing:
            raise ConfigurationError(
                f"Missing required GenerationConfig fields: {', '.join(missing)}"
            )


# --- Legacy constants for backward compatibility ---
def get_legacy_constants():
    config = AppConfig()
    return {
        "GENERATOR_DIR": config.directories.generator_dir,
        "PROJECT_ROOT": config.directories.project_root,
        "AUTHOR_DIR": config.directories.author_dir,
        "SECTIONS_DIR": config.directories.sections_dir,
        "OUTPUT_DIR": config.directories.output_dir,
        "DEFAULT_MODELS": {k: v.model for k, v in config.providers.items()},
        "API_URLS": {k: v.url_template for k, v in config.providers.items()},
        "AI_DETECTION_THRESHOLD": None,  # Removed from config, now set in run.py only
        "SECTION_TYPE_MAPPING": config.content.section_type_mapping,
        "BASE_SECTIONS_CONFIG": {"sections": config.load_sections_config()},
        "BASE_ARTICLE_CONFIG": {
            "authors": [],
            "voice": "professional",
            "authority": "expert",
            "content_length": config.content.default_content_lengths,
            "variety": "Technical details and industry applications with subtle imperfections, specific examples, and technical terminology to ensure human-like style.",
            "articleType": "Material",
            "articleCategory": "Material",
            "section_order": config.content.section_order,
        },
    }
