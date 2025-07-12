"""Tags prompt builder for schema-driven generation."""

import json
from typing import Dict, Any

def build_tags_prompt(context: Dict[str, Any], schema: Dict[str, Any]) -> str:
    """Build tags generation prompt using schema structure."""
    article_type = context.get("article_type")
    subject = context.get("subject")
    
    # Map context subject to schema placeholder
    placeholder_map = {
        "material": "materialName",
        "application": "applicationName", 
        "region": "regionName",
        "thesaurus": "term"
    }
    
    placeholder = placeholder_map.get(article_type, "subject")
    
    # Find tags section in schema (flexible naming)
    tags_section = None
    for key, value in schema.items():
        if "tags" in key.lower():
            tags_section = value
            break
    
    if not tags_section:
        raise ValueError(f"No tags section found in schema for {article_type}")
    
    # Replace system placeholders in schema
    schema_with_system = json.dumps(tags_section, indent=2)
    for sys_key, sys_value in context.items():
        if sys_key in ["generation_timestamp", "model_used", "lastUpdated", "publishedAt"]:
            schema_with_system = schema_with_system.replace(f"{{{{{sys_key}}}}}", str(sys_value))
    
    prompt = f"""You are an expert technical writer creating tags for a laser cleaning article.

Subject: {subject}
Article Type: {article_type}

Generate tags following this exact schema structure:
{schema_with_system}

CRITICAL REQUIREMENTS:
- Replace ALL instances of {{{{{placeholder}}}}} with "{subject}"
- Use the subject "{subject}" appropriately in all tag fields
- Include ALL fields from the schema - no omissions
- Follow the schema data types and formats exactly
- Return ONLY valid YAML format
- Do NOT include any explanatory text or markdown formatting
- Ensure every field has meaningful content (no empty arrays)

Generate the tags now:"""
    
    return prompt