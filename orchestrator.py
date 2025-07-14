"""Simplified orchestrator - SCHEMA-DRIVEN ONLY."""

import logging
from typing import Dict, Any, Optional
from metadata.generator import MetadataGenerator
from jsonld.generator import JsonLdGenerator
from tags.generator import TagsGenerator
from utils.output_formatter import format_output
from table.generator import TableGenerator
import re
import yaml

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

            # Parse metadata string to dict for table generation
            metadata_dict = yaml.safe_load(metadata)

            # Generate table
            table_gen = TableGenerator(self.context, self.schema, metadata_dict)
            markdown_table = table_gen.generate()

            # Create a metadata summary for tags
            metadata_summary = self._summarize_metadata(metadata)
            tags_gen = TagsGenerator(self.context, self.schema, self.ai_provider, metadata=metadata, metadata_summary=metadata_summary)
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
            output = format_output(metadata, tags, jsonld, markdown_table)

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

    def _summarize_metadata(self, metadata: str) -> str:
        # Example: extract facility names, technologies, standards, and unique uses
        # You can use regex or yaml parsing for structured metadata
        summary_lines = []
        # Extract manufacturing centers
        centers = re.findall(r'name:\s*"([^"]+)"', metadata)
        if centers:
            summary_lines.append("Facilities: " + ", ".join(centers))
        # Extract regulatory standards
        standards = re.findall(r'regulatoryStandards:\s*\n((?:\s*-\s*".*?"\n)+)', metadata)
        if standards:
            summary_lines.append("Regulatory Standards: " + ", ".join(re.findall(r'"([^"]+)"', standards[0])))
        # Extract keywords
        keywords = re.findall(r'keywords:\s*\n((?:\s*-\s*".*?"\n)+)', metadata)
        if keywords:
            summary_lines.append("Keywords: " + ", ".join(re.findall(r'"([^"]+)"', keywords[0])))
        # Add more as needed
        return "\n".join(summary_lines)