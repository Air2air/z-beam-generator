"""Simplified orchestrator - SCHEMA-DRIVEN ONLY."""

import logging
from typing import Dict, Any, Optional
from metadata.generator import MetadataGenerator
from jsonld.generator import JsonLdGenerator
from tags.generator import TagsGenerator
from utils.output_formatter import assemble_markdown

logger = logging.getLogger(__name__)


class ArticleOrchestrator:
    """Schema-driven orchestrator - NO FALLBACKS."""

    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider

        # Validate required context fields - NO FALLBACKS
        required_fields = ["subject", "article_type"]
        for field in required_fields:
            if field not in context:
                raise ValueError(f"Required context field '{field}' not provided")

        # Validate schema is not empty - NO FALLBACKS
        if not schema:
            raise ValueError("Schema cannot be empty")

        logger.info(f"Orchestrator initialized for {context['article_type']}: {context['subject']}")

    def generate_article(self) -> Optional[str]:
        """Generate complete article - FAIL if any component fails."""
        try:
            logger.info("Starting article generation process")

            # Initialize generators
            metadata_gen = MetadataGenerator(self.context, self.schema, self.ai_provider)
            jsonld_gen = JsonLdGenerator(self.context, self.schema, self.ai_provider)
            tags_gen = TagsGenerator(self.context, self.schema, self.ai_provider)

            # Generate metadata
            logger.info("Generating metadata...")
            metadata = metadata_gen.generate()
            if not metadata:
                logger.error("Metadata generation failed")
                return None

            # Generate tags
            logger.info("Generating tags...")
            tags = tags_gen.generate()
            if not tags:
                logger.error("Tags generation failed")
                return None

            # Generate JSON-LD
            logger.info("Generating JSON-LD...")
            jsonld = jsonld_gen.generate()
            if not jsonld:
                logger.error("JSON-LD generation failed")
                return None

            # Assemble final output
            logger.info("Assembling final output...")
            output = assemble_markdown(metadata, tags, jsonld)

            if not output:
                logger.error("Output assembly failed")
                return None

            logger.info("Article generated successfully")
            return output

        except Exception as e:
            logger.error(f"Article generation failed: {e}", exc_info=True)
            return None

    def save_article(self, output: str) -> Optional[str]:
        """Save article to file - FAIL if subject not provided."""
        try:
            subject = self.context["subject"]  # Will fail if not provided
            filename = f"{subject.lower().replace(' ', '_')}_laser_cleaning.md"
            filepath = f"output/{filename}"

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(output)

            logger.info(f"Article saved to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save article: {e}", exc_info=True)
            return None