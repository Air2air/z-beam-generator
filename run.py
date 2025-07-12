#!/usr/bin/env python3
"""Z-Beam Generator - Main entry point for schema-driven article generation."""

import os
from pathlib import Path

# Load environment variables manually
def load_env_file():
    """Load .env file manually without python-dotenv."""
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load environment variables first
load_env_file()

import click
import json
import logging
import sys
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler

from orchestrator import ArticleOrchestrator

console = Console()

# AI Provider selection (no default - must be set here)
AI_PROVIDER = "openai"  # Change to: "xai", "gemini", "deepseek", or "openai"

@click.command()
@click.option('--article-type', 
              type=click.Choice(['material', 'application', 'region', 'thesaurus']), 
              required=True,
              help='Type of article to generate')
@click.option('--subject', 
              required=True, 
              help='The subject to generate content for')
@click.option('--author-id', 
              help='Author ID for the article')
@click.option('--verbose', '-v', 
              is_flag=True, 
              help='Enable verbose logging')
def main(article_type, subject, author_id, verbose):
    """Generate schema-driven laser cleaning articles."""
    
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    logger = logging.getLogger(__name__)
    
    console.print(f"🚀 Starting Z-Beam Generator", style="bold green")
    console.print(f"Article Type: {article_type}")
    console.print(f"Subject: {subject}")
    console.print(f"AI Provider: {AI_PROVIDER}")
    
    try:
        # Create context
        context_data = {
            "article_type": article_type,
            "subject": subject,
            "author_id": author_id,
            "ai_provider": AI_PROVIDER
        }
        
        # Load schema
        schema_path = Path(f"schemas/definitions/{article_type}_schema_definition.json")
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
            
        with open(schema_path, 'r') as f:
            schema = json.load(f)
            
        logger.info(f"Schema loaded from {schema_path}")
        
        # Generate article
        console.print("🔄 Generating article...", style="yellow")
        
        orchestrator = ArticleOrchestrator(context_data, schema)
        output_file = orchestrator.generate_article()
        
        if output_file:
            console.print("✅ Article generated successfully!", style="bold green")
            console.print(f"📄 Output saved to: {output_file}")
        else:
            console.print("❌ Article generation failed", style="bold red")
            return 1
            
    except FileNotFoundError as e:
        console.print(f"❌ File error: {e}", style="bold red")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        console.print(f"❌ Unexpected error: {e}", style="bold red")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
