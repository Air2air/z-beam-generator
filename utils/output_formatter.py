"""Output formatter - SCHEMA-DRIVEN ONLY."""

import logging
import json
import yaml
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def assemble_markdown(metadata: Dict[str, Any], tags: List[str], jsonld: Dict[str, Any]) -> str:
    """Assemble final markdown output - NO FALLBACKS."""
    
    if not metadata:
        logger.error("Metadata is required for output assembly")
        return None
    
    if not tags:
        logger.error("Tags are required for output assembly")
        return None
    
    if not jsonld:
        logger.error("JSON-LD is required for output assembly")
        return None
    
    try:
        output_parts = []
        
        # Add YAML frontmatter
        output_parts.append("---")
        output_parts.append(yaml.dump(metadata, default_flow_style=False, sort_keys=False))
        output_parts.append("---")
        output_parts.append("")
        
        # Add tags section (separate from frontmatter for compatibility)
        output_parts.append(f"Tags: {', '.join(tags)}")
        output_parts.append("")
        
        # Add JSON-LD structured data
        output_parts.append('<script type="application/ld+json">')
        output_parts.append(json.dumps(jsonld, indent=2))
        output_parts.append('</script>')
        
        return "\n".join(output_parts)
        
    except Exception as e:
        logger.error(f"Failed to assemble markdown: {e}", exc_info=True)
        return None