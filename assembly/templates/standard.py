"""
Standard layout template for articles.
"""

from typing import Dict, Any
import logging
import yaml
import re

logger = logging.getLogger(__name__)

def apply_template(component_outputs, context):
    """
    Apply standard template to arrange components into final article.
    
    Args:
        component_outputs: Dictionary of generated component outputs
        context: Article context
        
    Returns:
        Assembled article
    """
    content = ""
    
    # Extract frontmatter data but don't include raw YAML in output
    frontmatter_content = component_outputs.get("frontmatter", "")
    frontmatter_match = re.search(r'---\s*(.*?)\s*---', frontmatter_content, re.DOTALL)
    frontmatter_data = {}
    if frontmatter_match:
        try:
            frontmatter_data = yaml.safe_load(frontmatter_match.group(1)) or {}
        except Exception:
            pass
    
    # Start with content
    if "content" in component_outputs:
        content += component_outputs["content"]
    
    # Add bullets if available
    if "bullets" in component_outputs:
        content += "\n\n" + component_outputs["bullets"]
    
    # Add table if available
    if "table" in component_outputs:
        content += "\n\n" + component_outputs["table"]
    
    # Add tags if available
    if "tags" in component_outputs:
        content += "\n\n## Tags\n" + component_outputs["tags"]
    
    # Add JSON-LD if available
    if "jsonld" in component_outputs:
        content += "\n\n" + component_outputs["jsonld"]
    
    return content