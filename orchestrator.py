"""Simplified orchestrator - SCHEMA-DRIVEN ONLY."""

import logging
from typing import Dict, Any, Optional
from frontmatter.generator import FrontmatterGenerator
from jsonld.generator import JsonLdGenerator
from tags.generator import TagsGenerator
from utils.output_formatter import format_output, force_write_output
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

    def generate_article(self) -> bool:
        """Generate complete article - FAIL if any component fails."""
        try:
            logger.info("Starting article generation process")

            # Generate frontmatter first
            frontmatter_gen = FrontmatterGenerator(self.context, self.schema, self.ai_provider)
            frontmatter = frontmatter_gen.generate()
            if not frontmatter:
                logger.error("Frontmatter generation failed")
                return False

            # Parse frontmatter string to dict for table generation
            frontmatter_dict = yaml.safe_load(frontmatter)

            # Generate table
            table_gen = TableGenerator(self.context, self.schema, frontmatter_dict)
            markdown_table = table_gen.generate()

            # Create a frontmatter summary for tags
            frontmatter_summary = self._summarize_frontmatter(frontmatter)
            tags_gen = TagsGenerator(self.context, self.schema, self.ai_provider, frontmatter=frontmatter, frontmatter_summary=frontmatter_summary)
            tags = tags_gen.generate()
            if not tags:
                logger.error("Tags generation failed")
                return False
                
            # Continue with jsonld...
            jsonld_gen = JsonLdGenerator(self.context, self.schema, self.ai_provider)
            jsonld = jsonld_gen.generate()
            if not jsonld:
                logger.error("JSON-LD generation failed")
                return False


            # Assemble final output
            logger.info("Assembling final output...")
            output = format_output(frontmatter, tags, jsonld, markdown_table)

            if not output:
                logger.error("Output assembly failed")
                return False

            # Save the article to file
            success = self.save_article(output)
            if not success:
                logger.error("Failed to save article")
                return False

            logger.info("Article generated successfully")
            return True

        except Exception as e:
            logger.error(f"Article generation failed: {e}", exc_info=True)
            return False

    def save_article(self, output: str) -> bool:
        """Save article to file with standardized dash-based naming."""
        try:
            # Use the slug that was already generated
            filename = f"{self.context['slug']}.md"
            output_dir = self.context["output_dir"]
            
            # Print detailed debug info
            print(f"\n📄 Saving article to:")
            print(f"   - Directory: {output_dir}")
            print(f"   - Filename: {filename}")
            print(f"   - Content length: {len(output)} characters")
            
            # Make directory if it doesn't exist
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            # Write file directly
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(output)
                
            # Verify file was written
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print(f"   ✅ File successfully written ({os.path.getsize(filepath)} bytes)")
                return True
            else:
                print(f"   ❌ File verification failed")
                return False

        except Exception as e:
            logger.error(f"Failed to save article: {e}", exc_info=True)
            return False

    def _summarize_frontmatter(self, frontmatter: str) -> str:
        # Example: extract facility names, technologies, standards, and unique uses
        # You can use regex or yaml parsing for structured frontmatter
        summary_lines = []
        # Extract manufacturing centers
        centers = re.findall(r'name:\s*"([^"]+)"', frontmatter)
        if centers:
            summary_lines.append("Facilities: " + ", ".join(centers))
        # Extract regulatory standards
        standards = re.findall(r'regulatoryStandards:\s*\n((?:\s*-\s*".*?"\n)+)', frontmatter)
        if standards:
            summary_lines.append("Regulatory Standards: " + ", ".join(re.findall(r'"([^"]+)"', standards[0])))
        # Extract keywords
        keywords = re.findall(r'keywords:\s*\n((?:\s*-\s*".*?"\n)+)', frontmatter)
        if keywords:
            summary_lines.append("Keywords: " + ", ".join(re.findall(r'"([^"]+)"', keywords[0])))
        # Add more as needed
        return "\n".join(summary_lines)

    def _generate_table(self, metadata_dict):
        """Generate a table using the table generator."""
        
        # Log the available metadata for debugging
        logger.debug(f"Available metadata keys: {list(metadata_dict.keys())}")
        
        # Create and configure the table generator
        table_gen = TableGenerator(self.context, self.schema, metadata_dict)
        
        # Generate the table
        table = table_gen.generate()
        
        # Validate table output
        if table and "|" in table:
            logger.info("Generated table successfully")
        else:
            logger.warning("Table generation produced empty or invalid output")
        
        return table