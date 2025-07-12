#!/usr/bin/env python3
"""
Z-Beam Generator Runner
Command-line interface to generate articles
"""

from utils.setup_logging import setup_logging
setup_logging()
import logging
logger = logging.getLogger("zbeam")

import json
import os
from orchestrator import ArticleOrchestrator
from utils.output_formatter import assemble_markdown
from utils.tag_formatter import format_tags

ARTICLE_CONTEXT = {
    "subject": "hafnium",
    "author_id": 2,
    "article_type": "material"
}

logger.info("Starting Z-Beam Generator")
logger.info("Loaded context: %s", ARTICLE_CONTEXT)

def main():
    schema_path = f"schemas/definitions/{ARTICLE_CONTEXT['article_type']}_schema_definition.md"
    logger.info("Loading schema from: %s", schema_path)
    with open(schema_path, "r") as f:
        schema = json.loads(f.read())
    orchestrator = ArticleOrchestrator(ARTICLE_CONTEXT, schema)
    output = orchestrator.run()
    if output:
        # Format tags before output
        output["tags"] = format_tags(output["tags"])
        markdown = assemble_markdown(output["metadata"], output["tags"], output["jsonld"])
        output_path = f"output/{ARTICLE_CONTEXT['article_type']}_{ARTICLE_CONTEXT['subject']}.md"
        logger.info("Writing output to: %s", output_path)
        with open(output_path, "w") as out_file:
            out_file.write(markdown)
        logger.info("Article generation complete.")
        return 0
    else:
        logger.error("Article generation failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
