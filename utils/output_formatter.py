"""Output formatter for assembling final markdown files."""

import yaml
import json
import logging
from typing import Dict, Any, Union, List

logger = logging.getLogger(__name__)

def assemble_markdown(metadata: Union[str, Dict], tags: Union[str, List], jsonld: Union[str, Dict]) -> str:
    """Assemble the final markdown output with proper error handling."""
    
    # Parse metadata
    if isinstance(metadata, str):
        metadata_dict = safe_yaml_parse(metadata)
    else:
        metadata_dict = metadata or {}
    
    # Parse tags
    if isinstance(tags, str):
        try:
            tags_dict = safe_yaml_parse(tags)
            if isinstance(tags_dict, dict) and 'tags' in tags_dict:
                tags_list = tags_dict['tags']
            else:
                tags_list = []
        except:
            tags_list = []
    else:
        tags_list = tags or []
    
    # Parse JSON-LD
    if isinstance(jsonld, str):
        jsonld_dict = safe_json_parse(jsonld)
    else:
        jsonld_dict = jsonld or {}
    
    # Format frontmatter
    try:
        frontmatter = yaml.dump(metadata_dict, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        logger.error(f"Failed to format metadata as YAML: {e}")
        frontmatter = "# Error formatting metadata\n"
    
    # Format tags section
    if tags_list:
        tags_section = f"Tags: {', '.join(tags_list)}\n"
    else:
        tags_section = ""
    
    # Format JSON-LD
    if jsonld_dict:
        try:
            jsonld_block = f'<script type="application/ld+json">\n{json.dumps(jsonld_dict, indent=2, ensure_ascii=False)}\n</script>\n'
        except Exception as e:
            logger.error(f"Failed to format JSON-LD: {e}")
            jsonld_block = "<!-- Error formatting JSON-LD -->\n"
    else:
        jsonld_block = ""
    
    # Assemble final markdown
    markdown_content = f"""---
{frontmatter}---

{tags_section}
{jsonld_block}
"""
    
    return markdown_content.strip() + "\n"

def safe_yaml_parse(content: str) -> Dict[str, Any]:
    """Safely parse YAML content with error handling."""
    try:
        return yaml.safe_load(content) or {}
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML: {e}")
        return {}

def safe_json_parse(content: str) -> Dict[str, Any]:
    """Safely parse JSON content with error handling."""
    try:
        return json.loads(content) if isinstance(content, str) else content
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return {}