"""
Technical layout template for articles with more structured organization.
"""

from typing import Dict, Any
import logging
import re
import yaml

logger = logging.getLogger(__name__)

def apply_template(components: Dict[str, str], context: Dict[str, Any]) -> str:
    """Apply technical template to arrange components."""
    # Start with frontmatter
    content = components.get("frontmatter", "")
    
    # Get material name and capitalize it
    material_name = context.get("subject", "Unknown").capitalize()
    
    # Add title
    content += f"# {material_name} Laser Cleaning Guide\n\n"
    
    # Add overview section with safe handling
    if "content" in components and components["content"]:
        content += "## Overview\n\n" + components["content"]
    else:
        content += f"## Overview\n\nInformation about {material_name} is not available."
    
    # Add bullet points if available
    if "bullets" in components and components["bullets"]:
        content += "\n\n" + components["bullets"]
    
    # Add table if available
    if "table" in components and components["table"]:
        content += "\n\n" + components["table"]
    
    # Add images section if available (placeholder)
    if "images" in components and components["images"]:
        content += "\n\n## Images\n\n" + components["images"]
    
    # Add tags section with type checking
    if "tags" in components:
        tags_content = components["tags"]
        # Handle case where tags is a list
        if isinstance(tags_content, list):
            tags_content = "\n".join(f"- {tag}" for tag in tags_content)
        if tags_content:
            content += "\n\n## Tags\n" + tags_content
    
    # Add JSON-LD with safe handling
    if "jsonld" in components and components["jsonld"]:
        content += "\n\n" + components["jsonld"]
    
    return content