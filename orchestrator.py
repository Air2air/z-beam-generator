"""Simplified orchestrator - SCHEMA-DRIVEN ONLY."""

import logging
import os
from typing import Dict, Any, Optional
from frontmatter.generator import FrontmatterGenerator
from jsonld.generator import JsonLdGenerator
from tags.generator import TagsGenerator
from utils.markdown_formatter import MarkdownFormatter, format_output, force_write_output
from table.generator import TableGenerator
from content.generator import ContentGenerator
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
        """Generate complete article based on configured components and layout."""
        try:
            logger.info("Starting article generation process")
            
            # Get component configuration (with defaults if not provided)
            component_config = self.context.get("component_config", {})
            layout_template = self.context.get("layout_template", "standard")
            
            logger.info(f"Using layout template: {layout_template}")
            
            # Track which components to generate based on configuration
            generate_components = {
                "frontmatter": True,  # Frontmatter is always required
                "tags": component_config.get("tags", {}).get("enabled", True),
                "jsonld": component_config.get("jsonld", {}).get("enabled", True),
                "table": component_config.get("table", {}).get("enabled", True),
                "content": component_config.get("content", {}).get("enabled", True)  # NEW: Content component
            }
            
            # Log enabled components
            enabled_components = [c for c, enabled in generate_components.items() if enabled]
            logger.info(f"Components enabled: {', '.join(enabled_components)}")
            
            # Generated component content
            generated_content = {}

            # Generate frontmatter first
            frontmatter_gen = FrontmatterGenerator(self.context, self.schema, self.ai_provider)
            frontmatter = frontmatter_gen.generate()
            if not frontmatter:
                logger.error("Frontmatter generation failed")
                return False

            # Parse frontmatter string to dict for table generation
            frontmatter_dict = {}  # Initialize to avoid potential reference errors
            try:
                # Extract just the first YAML document if there are multiple documents
                def extract_yaml_content(text):
                    """Extract the YAML content between or before --- markers."""
                    if text.startswith('---'):
                        parts = text.split('---', 2)
                        if len(parts) >= 2:
                            return parts[1].strip()
                    return text

                # Preprocess to handle multiple YAML documents
                yaml_content = extract_yaml_content(frontmatter)
                
                # Try to parse the YAML content
                frontmatter_dict = yaml.safe_load(yaml_content)
                
            except Exception as e:
                logger.error(f"Failed to parse frontmatter: {e}")
                # Last resort fallback - try parsing with load_all
                try:
                    docs = list(yaml.safe_load_all(frontmatter))
                    if docs:
                        frontmatter_dict = docs[0]
                        logger.info("Successfully parsed frontmatter using safe_load_all")
                    else:
                        logger.error("No valid YAML documents found in frontmatter")
                        return False
                except Exception as e2:
                    logger.error(f"All frontmatter parsing attempts failed: {e2}")
                    return False

            # Generate table if enabled - FIXED INDENTATION HERE
            markdown_table = ""
            if generate_components["table"]:
                table_options = component_config.get("table", {})
                table_gen = TableGenerator(self.context, self.schema, frontmatter_dict)
                
                # Pass component-specific options if we implement set_options in TableGenerator
                if table_options and hasattr(table_gen, 'set_options'):
                    table_gen.set_options(table_options)
                    
                markdown_table = table_gen.generate()
            else:
                logger.info("Table component disabled, skipping generation")

            # Generate content if enabled
            main_content = ""
            if generate_components["content"]:
                content_options = component_config.get("content", {})
                content_gen = ContentGenerator(self.context, self.schema, self.ai_provider)
                
                # Pass frontmatter_dict to ContentGenerator
                content_gen.set_frontmatter(frontmatter_dict)
                
                # Pass component-specific options
                if content_options:
                    content_gen.set_options(content_options)
                    
                main_content = content_gen.generate()
                if not main_content:
                    logger.warning("Content generation produced empty result")
            else:
                logger.info("Content component disabled, skipping generation")

            # Generate tags if enabled
            tags = ""
            if generate_components["tags"]:
                tags_gen = TagsGenerator(self.context, self.schema, frontmatter_dict)
                tags = tags_gen.generate()
                if not tags:
                    logger.error("Tags generation failed")
                    return False
            else:
                logger.info("Tags component disabled, skipping generation")
            
            # Generate JSON-LD if enabled
            jsonld = ""
            if generate_components["jsonld"]:
                jsonld_gen = JsonLdGenerator(self.context, self.schema, self.ai_provider)
                jsonld = jsonld_gen.generate()
                if not jsonld:
                    logger.error("JSON-LD generation failed")
                    return False
            else:
                logger.info("JSON-LD component disabled, skipping generation")

            # Assemble final output based on layout template
            logger.info("Assembling final output...")
            output = format_output(frontmatter, tags, jsonld, markdown_table, main_content)

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
            logger.error(f"Unexpected error during article generation: {e}", exc_info=True)
            return False

    def save_article(self, output: str) -> bool:
        """Save article to file with standardized dash-based naming."""
        try:
            filename = f"{self.context['slug']}.md"
            output_dir = self.context["output_dir"]
            filepath = os.path.join(output_dir, filename)
            
            print(f"\n📄 Saving article to:")
            print(f"   - Directory: {output_dir}")
            print(f"   - Filename: {filename}")
            print(f"   - Content length: {len(output)} characters")
            
            # Format and write in one step
            from utils.markdown_formatter import MarkdownFormatter
            formatted_output = MarkdownFormatter.format_output(
                frontmatter=None,  # Let the formatter extract it from the output
                tags=None,
                jsonld=None,
                tables=None,
                content=output  # Pass the entire output
            )
            
            success = MarkdownFormatter.write_markdown(filepath, formatted_output)
            
            if success:
                print(f"   ✅ File successfully written with proper formatting")
                return True
            else:
                print(f"   ❌ File formatting and write failed")
                return False
        except Exception as e:
            logger.error(f"Failed to save article: {e}", exc_info=True)
            return False