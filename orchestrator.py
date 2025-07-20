"""Bridge between legacy systems and new assembler architecture."""

import logging
import os
from typing import Dict, Any, Optional
from assembly.assembler import ArticleAssembler
from frontmatter.generator import FrontmatterGenerator
from jsonld.generator import JsonLdGenerator
from tags.generator import TagsGenerator
from utils.markdown_formatter import MarkdownFormatter, format_output, force_write_output
from table.generator import TableGenerator
from content.generator import ContentGenerator

logger = logging.getLogger(__name__)

OUTPUT_FORMAT = "content"  # Options: "content" (bullet points), "table" (tables), or "both"

def generate_article(context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str) -> Optional[str]:
    """
    Generate an article using the assembler system.
    
    Args:
        context: Article context dictionary
        schema: Schema dictionary
        ai_provider: AI provider name
        
    Returns:
        Path to generated article or None if generation failed
    """
    # Update context with required fields
    full_context = {
        **context,
        "schema": schema,
        "ai_provider": ai_provider
    }
    
    # Log generation start
    logger.info(f"Starting article generation for {context.get('subject')} using {ai_provider}")
    
    # Create assembler and generate article
    assembler = ArticleAssembler(full_context)
    success, output_path = assembler.assemble_article()
    
    if success:
        logger.info(f"Article successfully generated at {output_path}")
        return output_path
    else:
        logger.error("Article generation failed")
        return None

class ArticleOrchestrator:
    """Legacy wrapper around the new assembler system."""

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
        """Generate article using the assembler system."""
        # Prepare full context for assembler
        full_context = {
            **self.context,
            "schema": self.schema,
            "ai_provider": self.ai_provider,
            # Map the OUTPUT_FORMAT to component config
            "component_config": {
                **self.context.get("component_config", {}),
                "table": {"enabled": OUTPUT_FORMAT in ["table", "both"]},
                "content": {"enabled": OUTPUT_FORMAT in ["content", "both"]}
            }
        }
        
        # Use assembler to generate article
        assembler = ArticleAssembler(full_context)
        success, _ = assembler.assemble_article()
        return success
        
    def save_article(self, output: str) -> bool:
        """Legacy method kept for backwards compatibility."""
        # This functionality is now handled by the assembler
        logger.warning("save_article is deprecated, use assembler directly")
        return False