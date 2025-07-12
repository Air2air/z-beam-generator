#!/usr/bin/env python3
"""Main run script - SCHEMA-DRIVEN ONLY."""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Manual environment loading (no python-dotenv fallback)
def load_env_file():
    """Load .env file manually."""
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env_file()

from orchestrator import ArticleOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_schema(article_type: str) -> Optional[Dict[str, Any]]:
    """Load schema for article type - NO FALLBACKS."""
    schema_path = f"schemas/definitions/{article_type}_schema_definition.json"
    
    if not Path(schema_path).exists():
        logger.error(f"Schema file not found: {schema_path}")
        return None
    
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        if not schema:
            logger.error(f"Empty schema file: {schema_path}")
            return None
        
        logger.info(f"Schema loaded from {schema_path}")
        return schema
        
    except Exception as e:
        logger.error(f"Failed to load schema: {e}")
        return None

def main():
    """Main execution function - FAIL FAST approach."""
    
    # Get required arguments - NO FALLBACKS
    if len(sys.argv) < 5:
        logger.error("Usage: python run.py --article-type <type> --subject <subject>")
        sys.exit(1)
    
    article_type = None
    subject = None
    
    for i, arg in enumerate(sys.argv):
        if arg == "--article-type" and i + 1 < len(sys.argv):
            article_type = sys.argv[i + 1]
        elif arg == "--subject" and i + 1 < len(sys.argv):
            subject = sys.argv[i + 1]
    
    if not article_type or not subject:
        logger.error("Both --article-type and --subject are required")
        sys.exit(1)
    
    # Validate article type - NO FALLBACKS
    valid_types = ["material", "application", "region", "thesaurus"]
    if article_type not in valid_types:
        logger.error(f"Invalid article type. Must be one of: {valid_types}")
        sys.exit(1)
    
    # Load schema - NO FALLBACKS
    schema = load_schema(article_type)
    if not schema:
        logger.error("Failed to load schema")
        sys.exit(1)
    
    # Get AI provider - DEFAULT TO DEEPSEEK
    ai_provider = os.getenv("AI_PROVIDER", "deepseek")
    
    # Validate AI provider
    valid_providers = ["openai", "xai", "gemini", "deepseek"]
    if ai_provider not in valid_providers:
        logger.error(f"Invalid AI provider: {ai_provider}. Must be one of: {valid_providers}")
        sys.exit(1)
    
    # Create context - NO DEFAULTS
    context = {
        "article_type": article_type,
        "subject": subject,
        "publishedAt": "2024-01-15T10:00:00Z",
        "lastUpdated": "2024-01-15T10:00:00Z"
    }
    
    print(f"🚀 Starting Z-Beam Generator")
    print(f"Article Type: {article_type}")
    print(f"Subject: {subject}")
    print(f"AI Provider: {ai_provider}")
    
    try:
        # Initialize orchestrator
        orchestrator = ArticleOrchestrator(context, schema, ai_provider)
        
        # Generate article
        print("🔄 Generating article...")
        output = orchestrator.generate_article()
        
        if not output:
            logger.error("Article generation failed")
            sys.exit(1)
        
        # Save article
        filepath = orchestrator.save_article(output)
        
        if not filepath:
            logger.error("Failed to save article")
            sys.exit(1)
        
        print("✅ Article generated successfully!")
        print(f"📄 Output saved to: {filepath}")
        
    except Exception as e:
        logger.error(f"Application failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
