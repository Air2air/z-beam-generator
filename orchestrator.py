"""Article generation orchestrator - coordinates metadata, tags, and JSON-LD generation."""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from metadata.generator import MetadataGenerator
from tags.generator import TagsGenerator
from jsonld.generator import JsonLdGenerator
from utils.output_formatter import assemble_markdown

logger = logging.getLogger(__name__)


class ArticleOrchestrator:
    """Orchestrates the generation of complete articles from schema definitions."""

    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any]):
        self.context = context
        self.schema = schema
        self.article_type = context.get("article_type")
        self.subject = context.get("subject")
        self.ai_provider = context.get("ai_provider", "openai")

        # Add system placeholders
        self.context["generation_timestamp"] = datetime.now().isoformat()
        self.context["model_used"] = self._get_model_name()
        self.context["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
        self.context["publishedAt"] = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"Orchestrator initialized for {self.article_type}: {self.subject}")

    def _get_model_name(self) -> str:
        """Get model name based on AI provider."""
        models = {
            "openai": "gpt-4",
            "xai": "grok-beta",
            "gemini": "gemini-pro",
            "deepseek": "deepseek-chat",
        }
        return models.get(self.ai_provider, "unknown")

    def _get_output_filename(self) -> str:
        """Generate output filename based on article type and subject."""
        # Convert subject to lowercase and replace spaces with underscores
        subject_clean = self.subject.lower().replace(" ", "_")

        filename_patterns = {
            "material": f"{subject_clean}_laser_cleaning.md",
            "application": f"{subject_clean}_laser_cleaning.md",
            "region": f"{subject_clean}_laser_cleaning.md",
            "thesaurus": f"{subject_clean}.md",
        }

        return filename_patterns.get(self.article_type, f"{subject_clean}_article.md")

    def generate_article(self) -> Optional[str]:
        """Generate complete article with metadata, tags, and JSON-LD."""
        try:
            logger.info("Starting article generation process")

            # Initialize generators
            metadata_gen = MetadataGenerator(self.context, self.schema, self.ai_provider)
            tags_gen = TagsGenerator(self.context, self.schema, self.ai_provider)
            jsonld_gen = JsonLdGenerator(self.context, self.schema, self.ai_provider)

            # Generate each component
            logger.info("Generating metadata...")
            metadata = metadata_gen.generate()
            if not metadata:
                logger.error("Metadata generation failed")
                return None

            logger.info("Generating tags...")
            tags = tags_gen.generate()
            if not tags:
                logger.error("Tags generation failed")
                return None

            logger.info("Generating JSON-LD...")
            jsonld = jsonld_gen.generate()
            if not jsonld:
                logger.error("JSON-LD generation failed")
                return None

            # Assemble markdown
            logger.info("Assembling final output...")
            markdown_content = assemble_markdown(metadata, tags, jsonld)

            # Save output
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            filename = self._get_output_filename()
            output_path = output_dir / filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            logger.info(f"Article saved to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Article generation failed: {e}", exc_info=True)
            return None