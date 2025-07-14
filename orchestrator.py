"""Simplified orchestrator - SCHEMA-DRIVEN ONLY."""

import logging
from typing import Dict, Any, Optional
from metadata.generator import MetadataGenerator
from jsonld.generator import JsonLdGenerator
from tags.generator import TagsGenerator
from utils.output_formatter import format_output
import re

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

            # Generate metadata first
            metadata_gen = MetadataGenerator(self.context, self.schema, self.ai_provider)
            metadata = metadata_gen.generate()
            if not metadata:
                logger.error("Metadata generation failed")
                return None
            
            # Pass metadata to tags generator
            tags_gen = TagsGenerator(self.context, self.schema, self.ai_provider, metadata=metadata)
            tags = tags_gen.generate()
            if not tags:
                logger.error("Tags generation failed")
                return None
                
            # Continue with jsonld...
            jsonld_gen = JsonLdGenerator(self.context, self.schema, self.ai_provider)
            jsonld = jsonld_gen.generate()
            if not jsonld:
                logger.error("JSON-LD generation failed")
                return None

            # Assemble final output
            logger.info("Assembling final output...")
            output = format_output(metadata, tags, jsonld)

            if not output:
                logger.error("Output assembly failed")
                return None

            logger.info("Article generated successfully")
            return output

        except Exception as e:
            logger.error(f"Article generation failed: {e}", exc_info=True)
            return None

    def save_article(self, output: str) -> Optional[str]:
        """Save article to file with standardized dash-based naming."""
        try:
            subject = self.context["subject"]  # Will fail if not provided
            
            # Enhanced filename normalization
            normalized = subject.lower()
            # Remove special characters and punctuation
            normalized = re.sub(r'[,\'"!@#$%^&*()+=]', '', normalized)
            # Replace spaces and underscores with dashes
            normalized = re.sub(r'[\s_]+', '-', normalized)
            # Remove any extra dashes
            normalized = re.sub(r'-+', '-', normalized)
            
            filename = f"{normalized}-laser-cleaning.md"
            filepath = f"output/{filename}"

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(output)

            logger.info(f"Article saved to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save article: {e}", exc_info=True)
            return None