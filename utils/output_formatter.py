import logging
import yaml

logger = logging.getLogger("zbeam.output_formatter")

def assemble_markdown(metadata, tags, jsonld):
    logger.info("Assembling Markdown output...")
    # Metadata as YAML frontmatter
    yaml_frontmatter = yaml.dump(metadata, default_flow_style=False)
    # Tags as a YAML list
    tags_section = yaml.dump({"tags": tags}, default_flow_style=False)
    # JSON-LD as a script block
    jsonld_block = f'<script type="application/ld+json">\n{jsonld}\n</script>'
    markdown = f"---\n{yaml_frontmatter}{tags_section}---\n\n{jsonld_block}\n"
    logger.info("Markdown assembled.")
    return markdown