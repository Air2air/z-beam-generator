#!/usr/bin/env python3
"""Z-Beam Generator - Simple version without Rich dependency."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import click
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

# Simple console output instead of Rich
def print_info(message):
    print(f"ℹ️  {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

# Pydantic model for context validation
class ArticleContext(BaseModel):
    article_type: str = Field(..., description="Type of article to generate")
    subject: str = Field(..., description="Main subject of the article")
    author_id: Optional[str] = Field(None, description="Author identifier")
    generation_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        extra = "forbid"

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
    
    # Setup simple logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    print_info(f"🚀 Starting Z-Beam Generator")
    print_info(f"Article Type: {article_type}")
    print_info(f"Subject: {subject}")
    print_info(f"AI Provider: {AI_PROVIDER}")
    
    try:
        # Create and validate context
        context_data = {
            "article_type": article_type,
            "subject": subject,
            "author_id": author_id
        }
        
        context = ArticleContext(**context_data)
        logger.info(f"Context validated successfully")
        
        # Load schema
        schema_path = Path(f"schemas/definitions/{article_type}_schema_definition.json")
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
            
        with open(schema_path, 'r') as f:
            schema = json.load(f)
            
        logger.info(f"Schema loaded from {schema_path}")
        
        # For now, just print success - we'll add the orchestrator later
        print_success("Schema loaded successfully!")
        print_info(f"Schema contains {len(schema)} sections")
        
        # Show what we found
        for key in schema.keys():
            print_info(f"  - {key}")
        
        print_success("Setup validation complete!")
        return 0
            
    except ValidationError as e:
        print_error(f"Context validation error: {e}")
        return 1
    except FileNotFoundError as e:
        print_error(f"File error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print_error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())