"""Main article generation functionality."""

import os
import sys
import time
from pathlib import Path

# Initialize environment and logging first
from utils.logging_config import setup_logging
from utils.env_loader import load_env_file

# Set up logging
logger = setup_logging()

# Load environment variables
load_env_file()

# Import remaining modules
from utils.schema_loader import load_schema
from utils.author_loader import load_author
from utils.connectivity import check_api_connectivity
from utils.slug_generator import generate_slug
from orchestrator import ArticleOrchestrator

OUTPUT_FORMAT = "markdown"  # Options: "markdown", "tables", "both"

def ensure_output_directory(directory):
    """Ensure output directory exists and is writeable."""
    if not directory:
        directory = "output"  # Default if none provided
        
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Test if directory is writable
        test_file = os.path.join(directory, '.write_test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.info(f"✅ Output directory created/verified: {directory}")
            logger.info("✅ Write permissions confirmed")
            return directory
        except PermissionError:
            logger.error(f"No write permission for output directory: {directory}")
            return False
    except Exception as e:
        logger.error(f"Failed to create output directory: {e}")
        return False

def generate_article(context):
    """Generate an article based on the provided context."""
    # Start timing
    start_time = time.time()
    
    # Run connectivity diagnostics for the selected provider
    logger.info("Running API connectivity diagnostics...")
    connectivity_results = check_api_connectivity(context["ai_provider"])
    
    # Generate slug from subject
    if "slug" in context:
        # Use the slug already in the context
        slug = context["slug"]
    else:
        # Generate slug from subject
        slug = generate_slug(context["subject"])
    
    # Load schema and author data
    schema = load_schema(context["article_type"])
    author = load_author(str(context["author_id"]))
    
    if not schema:
        print("❌ Failed to load schema")
        sys.exit(1)
    
    # Create full context with loaded data
    full_context = {
        "article_type": context["article_type"],
        "subject": context["subject"],
        "output_dir": context["output_dir"],
        "author": author,
        "slug": slug
    }
    
    # Ensure output directory exists and is writable
    if not ensure_output_directory(context["output_dir"]):
        # If absolute path fails, try relative path as fallback
        if context["output_dir"].startswith('/'):
            fallback_dir = context["output_dir"][1:]  # Remove leading slash
            logger.warning(f"Falling back to relative path: {fallback_dir}")
            if ensure_output_directory(fallback_dir):
                full_context["output_dir"] = fallback_dir
            else:
                fallback_dir = "output"
                logger.warning(f"Falling back to default directory: {fallback_dir}")
                ensure_output_directory(fallback_dir)
                full_context["output_dir"] = fallback_dir
    
    # Log important details
    logger.info(f"Article Type: {context['article_type']}")
    logger.info(f"Subject: {context['subject']}")
    logger.info(f"AI Provider: {context['ai_provider']}")
    logger.info(f"Output Directory: {full_context['output_dir']}")
    logger.info(f"Slug: {slug}")
    
    # Generate article
    print(f"\nGenerating article about {context['subject']}...")
    try:
        orchestrator = ArticleOrchestrator(
            context=full_context,
            schema=schema,
            ai_provider=context["ai_provider"]
        )
        
        success = orchestrator.generate_article()
        
        if success:
            elapsed = time.time() - start_time
            print(f"\n✅ Article generation completed successfully in {elapsed:.1f} seconds")
            output_path = os.path.join(full_context["output_dir"], f"{slug}.md")
            print(f"📄 Article saved to: {output_path}")
            return True
        else:
            print("\n❌ Article generation failed")
            sys.exit(1)
            
    except Exception as e:
        logger.exception("Unhandled exception during article generation")
        print(f"\n❌ Error generating article: {str(e)}")
        print(f"📝 Check api_diagnostics.log for more details")
        sys.exit(1)

def generate_content(subject, frontmatter, schema_parser):
    # Create list to hold content sections
    content_parts = []
    
    # Always include YAML frontmatter
    content_parts.append(f"```yaml\n{yaml.dump(frontmatter)}\n```")
    
    # Include content based on selected format
    if OUTPUT_FORMAT in ["markdown", "both"]:
        # Add bullet-point style content
        markdown_content = generate_markdown_sections(frontmatter)
        content_parts.append(markdown_content)
        
        # Add tags section
        tags_content = generate_tags_section(frontmatter)
        content_parts.append(tags_content)
        
        # Add JSON-LD
        jsonld_content = generate_jsonld(frontmatter)
        content_parts.append(jsonld_content)
    
    if OUTPUT_FORMAT in ["tables", "both"]:
        # Add table-formatted content
        from utils.markdown_formatter import MarkdownFormatter
        formatter = MarkdownFormatter(schema_parser)
        table_content = formatter.format_frontmatter_as_markdown(frontmatter)
        content_parts.append(table_content)
    
    # Join all parts and return
    return "\n\n".join(content_parts)